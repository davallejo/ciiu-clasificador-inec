# -*- coding: utf-8 -*-
"""
Clasificador CIIU híbrido (TF-IDF + Cosine + RapidFuzz) — Python 3.8+ compatible.

NO ALUCINA: score 100% transparente, basado en el catálogo oficial.
"""

from __future__ import print_function, unicode_literals

import re
import os
import pickle
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import scipy.sparse  # noqa: F401
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from rapidfuzz import fuzz  # type: ignore
    HAS_FUZZ = True
except ImportError:
    HAS_FUZZ = False

try:
    from sqlalchemy import text as _sa_text
except ImportError:  # pragma: no cover - sqlalchemy siempre está disponible
    _sa_text = None

from .database import SessionLocal

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _resolver_modelo_dir():
    # type: () -> Path
    """
    Resuelve el directorio para guardar la caché del clasificador
    (TF-IDF + dataset). Prioridad:
      1. Variable de entorno `CIIU_MODELO_DIR` (útil en Vercel / Lambda: /tmp)
      2. Variable de entorno `MODELO_DIR` (alternativa corta)
      3. Por defecto: `<project_root>/models`
    Además intenta crear el directorio; si falla (FS read-only como Vercel
    sin usar /tmp), devuelve None y el clasificador re-entrena cada vez.
    """
    for key in ("CIIU_MODELO_DIR", "MODELO_DIR"):
        raw = os.environ.get(key)
        if raw:
            p = Path(raw).expanduser()
            try:
                p.mkdir(exist_ok=True, parents=True)
                return p
            except OSError:
                # No se puede escribir — devolver la ruta de todos modos;
                # el clasificador capturará los errores y seguirá sin cache.
                return p
    fallback = BASE_DIR / "models"
    try:
        fallback.mkdir(exist_ok=True, parents=True)
    except OSError:
        pass
    return fallback


MODELO_DIR = _resolver_modelo_dir()
TFIDF_PATH = MODELO_DIR / "tfidf_vectorizer.pkl"
MATRIX_PATH = MODELO_DIR / "tfidf_matrix.npz"
DATASET_PATH = MODELO_DIR / "dataset_actividades.pkl"

STOPWORDS_ES = set("""
a al algo algunas algunos alguna alguno ante antes como con contra cual
cuando de del desde donde durante e el ella ellas ellos en entre era eras
eramos eran es esa esas ese eso esta estaba estado estais estamos estan
estar estas este esto estos estoy fin fue fuera fui fuimos hacen hasta
incluso la las le les lo los mas me mi mia mias mientras mio mios mis
mucho muy nada ni no nos nosotras nosotros nuestra nuestras nuestro nuestros
o os otra otras otro otros para pero por porque que quien quienes se
según ser si sin sino sois sobre su sus suya suyas suyo suyos también tanto
te tiene tenemos tienen tengo toda todas todo todos tu tus tuya tuyas tuyo
tuyos un una unas uno unos usted ustedes va vamos van voy y ya yo
del al es son fue era eran hay ha han he hemos hace hacen haciendo
solo muy ya mas si no todo nada muy poco bastante demasiado demasiado
casi solo solamente incluso además también tampoco igual mismo misma
mismos mismas tanto tan como así bien mal mejor peor mayor menor
""".split())

NORMALIZAR_RE = re.compile(r'[^a-z0-9áéíóúñü\s]')


class ActividadDataset(object):
    __slots__ = (
        "id", "codigo", "descripcion", "texto_busqueda",
        "clase_codigo", "clase_descripcion",
        "grupo_codigo", "grupo_descripcion",
        "division_codigo", "division_descripcion",
        "seccion_codigo", "seccion_descripcion",
        "subclase_codigo", "subclase_descripcion",
        "pagina_pdf",
    )

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def normalizar_texto(t):
    # type: (Optional[str]) -> str
    if not t:
        return ""
    t = t.lower()
    t = NORMALIZAR_RE.sub(" ", t)
    t = re.sub(r'\s+', ' ', t).strip()
    palabras = [p for p in t.split() if p not in STOPWORDS_ES and len(p) > 1]
    return " ".join(palabras)


class ClasificadorCIIU(object):
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.dataset = []  # type: List[ActividadDataset]
        self.entrenado = False

    # ----------------------------------------------------------
    def cargar_desde_db(self):
        # type: () -> int
        db = SessionLocal()
        try:
            SQL = """
                SELECT
                    a.id AS aid, a.codigo AS acod, a.descripcion AS adesc,
                    COALESCE(a.descripcion_larga, '') AS dl,
                    COALESCE(array_to_string(a.palabras_clave, ' '), '') AS kw,
                    s.codigo  AS sec_c,  s.descripcion  AS sec_d,
                    d.codigo  AS div_c,  d.descripcion  AS div_d,
                    g.codigo  AS gpo_c,  g.descripcion  AS gpo_d,
                    c.codigo  AS cla_c,  c.descripcion  AS cla_d,
                    COALESCE(sc.codigo, '')       AS sub_c,
                    COALESCE(sc.descripcion, '')  AS sub_d,
                    COALESCE(c.notas_comprende, '') AS notas_comp,
                    a.pagina_pdf AS pag
                FROM actividades a
                JOIN clases  c  ON c.id  = a.clase_id
                LEFT JOIN subclases sc ON sc.id = a.subclase_id
                JOIN grupos  g  ON g.id  = c.grupo_id
                JOIN divisiones d ON d.id = g.division_id
                JOIN secciones s  ON s.id = d.seccion_id
                ORDER BY a.codigo
            """
            stmt = _sa_text(SQL) if _sa_text is not None else SQL
            rows_raw = db.execute(stmt)
            # SQLAlchemy 2.x: devolver mappings para acceder por nombre de columna
            try:
                rows = rows_raw.mappings().all()
            except Exception:
                # Fallback para SQLAlchemy 1.x
                rows = [dict(zip(rows_raw.keys(), r)) for r in rows_raw.fetchall()]

            self.dataset = []
            for r in rows:
                rdict = dict(r)
                texto_busqueda = " ".join([
                    str(rdict.get("adesc") or ""),
                    str(rdict.get("dl") or ""),
                    str(rdict.get("kw") or ""),
                    str(rdict.get("sub_d") or ""),
                    str(rdict.get("cla_d") or ""),
                    str(rdict.get("gpo_d") or ""),
                    str(rdict.get("div_d") or ""),
                    str(rdict.get("sec_d") or ""),
                    str(rdict.get("notas_comp") or ""),
                ])
                sub_c = rdict.get("sub_c")
                sub_d = rdict.get("sub_d")
                self.dataset.append(ActividadDataset(
                    id=int(rdict["aid"]),
                    codigo=str(rdict["acod"]),
                    descripcion=str(rdict["adesc"]),
                    texto_busqueda=normalizar_texto(texto_busqueda),
                    clase_codigo=str(rdict["cla_c"]),
                    clase_descripcion=str(rdict["cla_d"]),
                    grupo_codigo=str(rdict["gpo_c"]),
                    grupo_descripcion=str(rdict["gpo_d"]),
                    division_codigo=str(rdict["div_c"]),
                    division_descripcion=str(rdict["div_d"]),
                    seccion_codigo=str(rdict["sec_c"]),
                    seccion_descripcion=str(rdict["sec_d"]),
                    subclase_codigo=str(sub_c) if sub_c else None,
                    subclase_descripcion=str(sub_d) if sub_c else None,
                    pagina_pdf=rdict.get("pag"),
                ))
            return len(self.dataset)
        finally:
            db.close()

    # ----------------------------------------------------------
    def _cargar_dataset_solo(self):
        # type: () -> bool
        if DATASET_PATH.exists():
            try:
                with open(str(DATASET_PATH), "rb") as f:
                    self.dataset = pickle.load(f)
                return len(self.dataset) > 0
            except Exception:
                return False
        return False

    def entrenar(self, forzar=False):
        # type: (bool) -> bool
        if not HAS_SKLEARN:
            print("[CLASIFICADOR] sklearn no disponible — modo fuzzy/fts solamente.")
            ok = self._cargar_dataset_solo()
            if not ok:
                ok = self.cargar_desde_db() > 0
            self.entrenado = ok
            return ok

        if self.entrenado and not forzar:
            return True

        if (not forzar) and TFIDF_PATH.exists() and DATASET_PATH.exists() and MATRIX_PATH.exists():
            try:
                import scipy.sparse
                with open(str(TFIDF_PATH), "rb") as f:
                    self.vectorizer = pickle.load(f)
                with open(str(DATASET_PATH), "rb") as f:
                    self.dataset = pickle.load(f)
                npz = np.load(str(MATRIX_PATH), allow_pickle=False)
                self.tfidf_matrix = scipy.sparse.csr_matrix(
                    (npz["data"], npz["indices"], npz["indptr"]), shape=npz["shape"]
                )
                self.entrenado = True
                print("[CLASIFICADOR] Modelo cargado desde disco: %d actividades." % len(self.dataset))
                return True
            except Exception as e:
                print("[CLASIFICADOR] No se pudo cargar modelo guardado (%s); re-entrenando." % str(e))

        if not self.dataset:
            self.cargar_desde_db()
        if not self.dataset:
            print("[CLASIFICADOR] ERROR: No hay actividades en la base de datos.")
            return False

        corpus = [a.texto_busqueda for a in self.dataset]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            analyzer="word",
            lowercase=True,
            sublinear_tf=True,
            max_features=50000,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

        try:
            import scipy.sparse
            with open(str(TFIDF_PATH), "wb") as f:
                pickle.dump(self.vectorizer, f)
            with open(str(DATASET_PATH), "wb") as f:
                pickle.dump(self.dataset, f)
            base_no_ext = str(MATRIX_PATH.with_suffix(""))
            scipy.sparse.save_npz(base_no_ext, self.tfidf_matrix)
            if not MATRIX_PATH.exists():
                alt = Path(base_no_ext + ".npz.npz")
                if alt.exists():
                    try:
                        alt.rename(MATRIX_PATH)
                    except OSError:
                        pass
        except Exception as e:
            print("[CLASIFICADOR] WARN: No se pudo guardar el modelo (%s)." % str(e))

        self.entrenado = True
        print("[CLASIFICADOR] Modelo entrenado: %d actividades." % len(self.dataset))
        return True

    # ----------------------------------------------------------
    def predecir(self, texto, top_k=5, umbral=0.0):
        # type: (str, int, float) -> Tuple[List[Dict[str, Any]], str, int]
        t0 = time.perf_counter()
        texto_norm = normalizar_texto(texto)
        resultados = []  # type: List[Tuple[float, ActividadDataset]]

        if not self.dataset:
            self.cargar_desde_db()
        if not self.dataset:
            return [], "ninguno", 0

        modelo_usado = "hibrido"

        if HAS_SKLEARN and self.vectorizer is not None and self.tfidf_matrix is not None:
            vec = self.vectorizer.transform([texto_norm])
            sims = cosine_similarity(vec, self.tfidf_matrix)[0]
            top_idx = np.argsort(sims)[::-1][:max(top_k * 4, 20)]
            for i in top_idx:
                score_cos = float(sims[i])
                if score_cos <= 0:
                    continue
                item = self.dataset[i]
                score_fuzzy = 0.0
                if HAS_FUZZ:
                    score_fuzzy = (fuzz.token_set_ratio(texto, item.descripcion)
                                   + fuzz.token_sort_ratio(texto, item.descripcion)) / 200.0
                score_final = (score_cos * 0.70) + (score_fuzzy * 0.30)
                resultados.append((score_final, item))
            modelo_usado = "tfidf+coseno+fuzzy"
        else:
            modelo_usado = "fuzzy"
            if HAS_FUZZ:
                for item in self.dataset:
                    score = (fuzz.token_set_ratio(texto, item.descripcion)
                             + fuzz.partial_ratio(texto, item.descripcion)) / 200.0
                    if score > 0.2:
                        resultados.append((score, item))

        vistos = set()  # type: set
        unicos = []  # type: List[Tuple[float, ActividadDataset]]
        for s, it in sorted(resultados, key=lambda x: -x[0]):
            if it.codigo in vistos:
                continue
            vistos.add(it.codigo)
            unicos.append((s, it))

        if umbral > 0:
            unicos = [x for x in unicos if x[0] >= umbral]
        seleccionados = unicos[:top_k]

        salidas = []  # type: List[Dict[str, Any]]
        for score, it in seleccionados:
            salidas.append({
                "score": round(score, 4),
                "score_porcentaje": round(score * 100, 2),
                "actividad_codigo": it.codigo,
                "actividad_descripcion": it.descripcion,
                "clase_codigo": it.clase_codigo,
                "clase_descripcion": it.clase_descripcion,
                "subclase_codigo": it.subclase_codigo,
                "subclase_descripcion": it.subclase_descripcion,
                "grupo_codigo": it.grupo_codigo,
                "grupo_descripcion": it.grupo_descripcion,
                "division_codigo": it.division_codigo,
                "division_descripcion": it.division_descripcion,
                "seccion_codigo": it.seccion_codigo,
                "seccion_descripcion": it.seccion_descripcion,
                "pagina_pdf": it.pagina_pdf,
            })

        ms = int((time.perf_counter() - t0) * 1000)
        return salidas, modelo_usado, ms


_clasificador = None  # type: Optional[ClasificadorCIIU]


def obtener_clasificador():
    # type: () -> ClasificadorCIIU
    global _clasificador
    if _clasificador is None:
        _clasificador = ClasificadorCIIU()
        _clasificador.entrenar(forzar=False)
    return _clasificador
