"""
Backend FastAPI — CIIU Clasificador INEC
========================================

Autor: Diego Vallejo

Endpoints disponibles:
  GET  /api/health
  GET  /api/estadisticas          -> conteos del catálogo
  GET  /api/secciones             -> listar secciones (A..U)
  GET  /api/actividades/:codigo   -> detalle de una actividad por código
  GET  /api/actividades           -> búsqueda paginada + FTS en PostgreSQL
  POST /api/predecir              -> CLASIFICACIÓN POR IA (el endpoint principal)
  GET  /docs   /redoc             -> documentación automática OpenAPI

Para correr localmente:
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import time
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from .config import get_settings
from .database import get_db, engine, Base, SessionLocal
from . import models, schemas
from .classifier import obtener_clasificador

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicialización al arrancar:
      - (intento) crear tablas faltantes con SQLAlchemy
      - (intento) pre-cargar / entrenar el clasificador

    El backend NUNCA debe crashear por fallos de BD al startup (UX amigable
    en desarrollo cuando el usuario todavía no corrió los scripts 03→05).
    Si hay error, se loguea y el endpoint /health muestra estado != ok.
    """
    # 1. Validar tablas (usamos SessionLocal como en /health que SÍ funciona;
    #    engine.connect() a veces da OperationalError benigno en la primera
    #    conexión con algunos pares SQLAlchemy + psycopg2).
    _tablas_ya_existen = False
    _bd_accesible = False
    try:
        _tmp = SessionLocal()
        try:
            # El ORM query simple funciona siempre si la BD está arriba (como
            # demuestra /health en las pruebas del usuario).
            from sqlalchemy import text as _t
            _res = _tmp.execute(_t(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'secciones'"
            )).scalar()
            _tablas_ya_existen = int(_res or 0) > 0
            _bd_accesible = True
        finally:
            _tmp.close()
    except Exception as _e:
        # Si ni siquiera un SELECT 1 funciona, asumimos que la BD no está
        # lista ahora (no mostramos spam, solo una línea).
        _msg = str(_e).splitlines()
        _msg = _msg[0] if _msg else str(_e)
        _bd_accesible = False
        print("[STARTUP][INFO] Base de datos no accesible en startup: %s" % _msg)
        print("               (se re-intentará en el 1er request a /api/*)")

    if _bd_accesible:
        if _tablas_ya_existen:
            print("[STARTUP] Tablas ya existen (schema OK) — SKIP create_all.")
        else:
            try:
                Base.metadata.create_all(bind=engine)
                print("[STARTUP] Base.metadata.create_all() ejecutado.")
            except Exception as _e2:
                _m2 = str(_e2).splitlines()
                print("[STARTUP][INFO] create_all() falló (no crítico): %s" % (
                    _m2[0] if _m2 else str(_e2)
                ))
                print("               Si no has corrido scripts/03_aplicar_schema.py, hacelo ahora.")

    # 2. Clasificador (si no hay datos en DB, no falla — solo re-entrena luego en el 1er request)
    if _bd_accesible:
        try:
            clf = obtener_clasificador()
            if not clf.entrenado:
                clf.entrenar(forzar=False)
            print("[STARTUP] Clasificador cargado/entrenado: %s" % (
                "OK" if clf.entrenado else "SIN DATOS (se entrenará en el 1er request)"
            ))
        except Exception as _e3:
            _m3 = str(_e3).splitlines()
            print("[STARTUP][INFO] Clasificador no se pudo inicializar ahora: %s" % (
                _m3[0] if _m3 else str(_e3)
            ))
            print("               Se re-intentará en el 1er request a /api/predecir.")
    else:
        print("[STARTUP] Clasificador diferido (BD no accesible en startup).")
    yield


app = FastAPI(
    title="CIIU Clasificador INEC API",
    description=(
        "API de clasificación automática de actividades económicas "
        "según el catálogo oficial CIIU 4.0 del INEC (Ecuador). "
        "Devuelve la actividad detallada (6 dígitos) más probable."
    ),
    version="1.0.0",
    author="Diego Vallejo",
    lifespan=lifespan,
)

# CORS: en local permite :3000, en producción usa la lista de settings
# o "*" si el usuario lo deja abierto. Nunca bloquear explícitamente.
if settings.app_env == "development":
    _cors_origins = list(set(settings.cors_origins + [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]))
else:
    _cors_origins = settings.cors_origins if settings.cors_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins if _cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH
# ============================================================
@app.get("/api/health", response_model=schemas.HealthResponse, tags=["General"])
def health(db: Session = Depends(get_db)):
    try:
        total = db.query(func.count(models.Actividad.id)).scalar() or 0
    except Exception:
        total = 0
    clf = obtener_clasificador()
    return schemas.HealthResponse(
        status="ok",
        ambiente=settings.app_env,
        actividades_cargadas=total,
        modelo_entrenado=clf.entrenado,
    )


# ============================================================
# ESTADÍSTICAS
# ============================================================
@app.get("/api/estadisticas", tags=["General"])
def estadisticas(db: Session = Depends(get_db)):
    """Conteos por nivel jerárquico (vista vw_conteos_jerarquia)."""
    try:
        rows = db.execute(text("SELECT nivel, total FROM vw_conteos_jerarquia ORDER BY nivel"))
        return {r.nivel: r.total for r in rows}
    except Exception as e:
        raise HTTPException(500, "No se pudo consultar estadísticas: %s" % e)


# ============================================================
# SECCIONES
# ============================================================
@app.get("/api/secciones", response_model=List[schemas.SeccionOut], tags=["Catálogo"])
def listar_secciones(db: Session = Depends(get_db)):
    secciones = db.query(models.Seccion).order_by(models.Seccion.codigo).all()
    return secciones


# ============================================================
# JERARQUÍA: dada una sección, devuelve divisiones / grupos / clases / subclases
# ============================================================
@app.get("/api/secciones/{codigo}/divisiones", response_model=List[schemas.DivisionOut], tags=["Catálogo"])
def divisiones_por_seccion(codigo: str, db: Session = Depends(get_db)):
    sec = db.query(models.Seccion).filter(models.Seccion.codigo == codigo.upper()).first()
    if not sec:
        raise HTTPException(404, "Sección %s no encontrada" % codigo)
    return sorted(sec.divisiones, key=lambda d: d.codigo)


@app.get("/api/divisiones/{codigo}/grupos", response_model=List[schemas.GrupoOut], tags=["Catálogo"])
def grupos_por_division(codigo: str, db: Session = Depends(get_db)):
    div = db.query(models.Division).filter(models.Division.codigo == codigo.upper()).first()
    if not div:
        raise HTTPException(404, "División %s no encontrada" % codigo)
    return sorted(div.grupos, key=lambda d: d.codigo)


@app.get("/api/grupos/{codigo}/clases", response_model=List[schemas.ClaseOut], tags=["Catálogo"])
def clases_por_grupo(codigo: str, db: Session = Depends(get_db)):
    gpo = db.query(models.Grupo).filter(models.Grupo.codigo == codigo.upper()).first()
    if not gpo:
        raise HTTPException(404, "Grupo %s no encontrado" % codigo)
    return sorted(gpo.clases, key=lambda d: d.codigo)


# ============================================================
# ACTIVIDADES (BÚSQUEDA + DETALLE)
# ============================================================
@app.get("/api/actividades/{codigo}", response_model=schemas.ActividadOut, tags=["Catálogo"])
def detalle_actividad(codigo: str, db: Session = Depends(get_db)):
    act = db.query(models.Actividad).filter(models.Actividad.codigo == codigo.upper()).first()
    if not act:
        raise HTTPException(404, "Actividad %s no encontrada" % codigo)
    return act


@app.get("/api/actividades", tags=["Catálogo"])
def buscar_actividades(
    q: str = Query("", description="Texto para búsqueda (FTS sobre descripción en español)"),
    seccion: Optional[str] = Query(None, description="Filtrar por letra de sección, ej. A"),
    clase: Optional[str] = Query(None, description="Filtrar por código de clase, ej. A0113"),
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Búsqueda paginada de actividades (usa índice FTS PostgreSQL cuando hay query)."""
    query = db.query(models.Actividad)

    if q and q.strip():
        # FTS: to_tsquery con comodín al final.
        # Usa SQL text() para evitar incompatibilidades entre versiones
        # de SQLAlchemy con el operador `@@` (Full Text Search).
        term = " & ".join(p for p in q.lower().split() if p)
        if term:
            from sqlalchemy import text as _sql_text
            tsvector = func.to_tsvector(
                "spanish",
                func.coalesce(models.Actividad.descripcion, "")
                + " " + func.coalesce(models.Actividad.descripcion_larga, ""),
            )
            tsquery = func.to_tsquery("spanish", func.concat(term, ":*"))
            # `op("@@")` retorna un ClauseElement compatible con SQLAlchemy 1.x y 2.x
            query = query.filter(tsvector.op("@@")(tsquery))
    if seccion:
        query = query.join(models.Actividad.clase).join(models.Clase.grupo) \
                     .join(models.Grupo.division).join(models.Division.seccion) \
                     .filter(models.Seccion.codigo == seccion.upper())
    if clase:
        query = query.join(models.Actividad.clase) \
                     .filter(models.Clase.codigo == clase.upper())

    total = query.count()
    offset = max(0, (page - 1) * limit)
    items = query.order_by(models.Actividad.codigo).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "paginas": (total + limit - 1) // limit,
        "items": [
            {"codigo": a.codigo, "descripcion": a.descripcion,
             "clase_codigo": a.clase.codigo if a.clase else None,
             "clase_descripcion": a.clase.descripcion if a.clase else None,
             "pagina_pdf": a.pagina_pdf}
            for a in items
        ],
    }


# ============================================================
# ENDPOINT PRINCIPAL: PREDICCIÓN POR IA
# ============================================================
@app.post("/api/predecir", response_model=schemas.PredictResponse, tags=["IA"])
def predecir_actividad(req: schemas.PredictRequest):
    """
    Dado un texto libre (lo que escribe el ciudadano / encuestador),
    devuelve el TOP-K de actividades CIIU más probables, con score
    de 0 a 1 (y su porcentaje).

    El frontend debe llamar a este endpoint con un debounce de
    ~400-600ms mientras el usuario escribe, para dar sensación
    de "respuesta en tiempo real".
    """
    texto = (req.texto or "").strip()
    if len(texto) < 2:
        return schemas.PredictResponse(
            texto_ingresado=texto,
            total_coincidencias=0,
            resultados=[],
            modelo_usado="ninguno",
            tiempo_ms=0,
            advertencia="Escribe al menos 2 caracteres para comenzar la predicción.",
        )

    clf = obtener_clasificador()
    if not clf.entrenado and len(clf.dataset) == 0:
        ok = clf.entrenar(forzar=True)
        if not ok:
            raise HTTPException(500, (
                "El clasificador no pudo cargar datos de la base de datos. "
                "Asegúrate de haber ejecutado: python scripts/03_aplicar_schema.py "
                "-> parser -> 05_cargar_a_postgres.py"
            ))

    top_k = max(1, min(req.top_k, 20))
    resultados, modelo, ms = clf.predecir(
        texto=texto, top_k=top_k, umbral=req.umbral_minimo,
    )

    advertencia = None
    if len(resultados) == 0:
        advertencia = (
            "No se encontraron coincidencias con suficiente confianza. "
            "Intenta ser más específico (ej. 'venta de ropa' en vez de solo 'ropa')."
        )
    elif resultados and resultados[0]["score"] < 0.35:
        advertencia = (
            "La coincidencia principal tiene baja confianza. "
            "Revisa las opciones alternativas."
        )

    return schemas.PredictResponse(
        texto_ingresado=texto,
        total_coincidencias=len(resultados),
        resultados=resultados,
        modelo_usado=modelo,
        tiempo_ms=float(ms),
        advertencia=advertencia,
    )


# ============================================================
# Re-entrenar modelo (útil después de una nueva carga de datos)
# ============================================================
@app.post("/api/admin/reentrenar", tags=["Admin"])
def reentrenar_modelo():
    clf = obtener_clasificador()
    ok = clf.entrenar(forzar=True)
    return {
        "ok": ok,
        "actividades_cargadas": len(clf.dataset),
        "modelo_entrenado": clf.entrenado,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
