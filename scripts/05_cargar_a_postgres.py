# -*- coding: utf-8 -*-
"""
PASO 4: Cargar los JSON generados por el parser a PostgreSQL.

ORDEN DE CARGA (por FKs):
  1. secciones   2. divisiones   3. grupos   4. clases
  5. subclases   6. actividades  7. exclusiones

Validación FINAL mediante vw_conteos_jerarquia.

Python 3.8+ compatible.

Uso:  python scripts/05_cargar_a_postgres.py
Antes:  python scripts/03_aplicar_schema.py && python scripts/04_parser_ciiu.py
Autor: Diego Vallejo
"""

from __future__ import print_function, unicode_literals

import os
import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import psycopg2
    from psycopg2.extras import execute_batch
    from dotenv import load_dotenv
except ImportError as e:
    print("[ERROR] Falta dependencia: %s" % e)
    print("Instala con:  pip install psycopg2-binary python-dotenv")
    sys.exit(1)

load_dotenv(str(BASE_DIR / ".env"))
load_dotenv(str(BASE_DIR / ".env.example"), override=False)

PARSED_DIR = BASE_DIR / "data" / "parsed"


def get_env(name, default=None):
    # type: (str, Any) -> str
    v = os.getenv(name) or os.getenv(name.upper())
    if not v and default is None:
        print("[ERROR] Falta variable de entorno: %s" % name)
        sys.exit(1)
    return v if v else (default if default else "")


def cargar_json(path):
    # type: (Path) -> Any
    if not path.exists():
        print("[ERROR] No existe: %s" % path)
        print("        Ejecuta primero:  python scripts/04_parser_ciiu.py")
        sys.exit(1)
    with open(str(path), encoding="utf-8") as f:
        return json.load(f)


def get_conn():
    host    = get_env("DB_HOST", "localhost")
    port    = int(get_env("DB_PORT", "5432"))
    user    = get_env("DB_USER", "postgres")
    passwd  = get_env("DB_PASSWORD", "")
    dbname  = get_env("DB_NAME", "ciiu_inec")
    return psycopg2.connect(host=host, port=port, user=user, password=passwd, dbname=dbname)


SECCIONES_CIIU_4_0 = {
    "A": u"Agricultura, ganadería, caza y silvicultura",
    "B": u"Pesca y acuicultura",
    "C": u"Explotación de minas y canteras",
    "D": u"Industrias manufactureras",
    "E": u"Suministro de electricidad, gas, vapor y aire acondicionado",
    "F": u"Distribución de agua; evacuación y tratamiento de aguas residuales, gestión de desechos y actividades de saneamiento ambiental",
    "G": u"Construcción",
    "H": u"Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas",
    "I": u"Transporte y almacenamiento",
    "J": u"Actividades de alojamiento y de servicio de comidas y bebidas",
    "K": u"Información y comunicaciones",
    "L": u"Actividades financieras y de seguros",
    "M": u"Actividades inmobiliarias",
    "N": u"Actividades profesionales, científicas y técnicas",
    "O": u"Actividades administrativas y servicios de apoyo",
    "P": u"Administración pública y defensa; planes de seguridad social de afiliación obligatoria",
    "Q": u"Enseñanza",
    "R": u"Actividades de salud humana y de asistencia social",
    "S": u"Actividades artísticas, de entretenimiento y recreación",
    "T": u"Otras actividades de servicios",
    "U": u"Actividades de los hogares como empleadores domésticos; actividades no diferenciadas de los hogares en la producción de bienes y servicios para uso propio",
}


def construir_listas_planas_desde_arbol(arbol):
    # type: (Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]
    secciones, divisiones, grupos, clases, subclases, actividades = [], [], [], [], [], []
    for s_cod in sorted(arbol.keys()):
        s = arbol[s_cod]
        secciones.append({"codigo": s["codigo"], "descripcion": s["descripcion"],
                          "notas": s.get("notas") or ""})
        for d in s.get("divisiones", []) or []:
            divisiones.append({"codigo": d["codigo"], "codigo_numerico": d["codigo_numerico"],
                               "seccion_codigo": s["codigo"],
                               "descripcion": d.get("descripcion") or "",
                               "notas": d.get("notas") or ""})
            for g in d.get("grupos", []) or []:
                grupos.append({"codigo": g["codigo"], "codigo_numerico": g["codigo_numerico"],
                               "division_codigo": d["codigo"],
                               "descripcion": g.get("descripcion") or "",
                               "notas": g.get("notas") or ""})
                for c in g.get("clases", []) or []:
                    clases.append({"codigo": c["codigo"], "codigo_numerico": c["codigo_numerico"],
                                   "grupo_codigo": g["codigo"],
                                   "descripcion": c["descripcion"],
                                   "notas_comprende": c.get("notas_comprende") or "",
                                   "notas_adicionales": c.get("notas_adicionales") or ""})
                    for sc in c.get("subclases", []) or []:
                        subclases.append({"codigo": sc["codigo"], "codigo_numerico": sc["codigo_numerico"],
                                          "clase_codigo": c["codigo"],
                                          "descripcion": sc["descripcion"],
                                          "notas": sc.get("notas") or ""})
                    for a in c.get("actividades", []) or []:
                        actividades.append(dict(a))
    return {
        "secciones": secciones, "divisiones": divisiones, "grupos": grupos,
        "clases": clases, "subclases": subclases, "actividades": actividades,
    }


def _inferir_codigos_clase(cod):
    # type: (str) -> Tuple[str, str, str]
    """Dado un código de CLASE (p.ej. K6419), devuelve (seccion, division, grupo)."""
    if not cod:
        return "A", "A00", "A000"
    letra = cod[0]
    divi = (cod[:3] if len(cod) >= 3 else letra + "00")
    grup = (cod[:4] if len(cod) >= 4 else (divi + "0"))
    return letra, divi, grup


def _inferir_codigos_actividad(cod):
    # type: (str) -> Tuple[str, str, str, str]
    """Dado un código de ACTIVIDAD (p.ej. A0111.11, E3700.00), devuelve (seccion, division, grupo, clase)."""
    if not cod:
        return "A", "A00", "A000", "A0000"
    letra = cod[0]
    # Si hay punto, la clase es la parte entera sin el primer char+digit+digit+digit+digit.
    # Sencillo: todo lo que esté ANTES del punto, si lo hay.
    if "." in cod:
        clase_cod = cod.split(".", 1)[0]
    else:
        clase_cod = cod[:5] if len(cod) >= 5 else cod
    _, divi, grup = _inferir_codigos_clase(clase_cod)
    return letra, divi, grup, clase_cod


def construir_listas_planas_fallback(clases_json, actividades_json):
    # type: (List[Dict[str, Any]], List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]
    print("[WARN] El árbol arbol_completo.json está incompleto. Usando FALLBACK:")
    print("       Reconstruyendo jerarquía desde clases.json y actividades.json...")

    # 1. Secciones: usar lista oficial CIIU 4.0
    secciones = []  # type: List[Dict[str, Any]]
    for letra in sorted(SECCIONES_CIIU_4_0.keys()):
        secciones.append({
            "codigo": letra,
            "descripcion": SECCIONES_CIIU_4_0[letra],
            "notas": "",
        })

    # 2. Clases: desde clases.json PERO IGNORAMOS grupo/division/seccion del JSON
    #    porque muchos están mal (null o incorrectos). Los inferimos desde el código.
    clases = []  # type: List[Dict[str, Any]]
    clases_cods = set()  # type: set
    for c in clases_json:
        cod = c["codigo"]
        if cod in clases_cods:
            continue
        secc, divi, grup = _inferir_codigos_clase(cod)
        nueva = dict(c)
        nueva["seccion_codigo"] = secc
        nueva["division_codigo"] = divi
        nueva["grupo_codigo"] = grup
        clases.append(nueva)
        clases_cods.add(cod)

    # 3. Actividades: desde actividades.json — IGNORAMOS clase/grupo/division/seccion
    #    del JSON (están mal en E3700.00, F4330.91, R9000.01, etc.). Todo lo inferimos del código.
    actividades = []  # type: List[Dict[str, Any]]
    for a in actividades_json:
        cod = a["codigo"]
        secc, divi, grup, clase_cod = _inferir_codigos_actividad(cod)
        # subclase: si tiene punto, XXXXX.d (de A0111.11 sale A0111.1)
        sub_cod = None
        if "." in cod:
            # Tomamos: todo antes del punto + "." + el PRIMER dígito después
            antes, desp = cod.split(".", 1)
            if len(desp) >= 1:
                sub_cod = "%s.%s" % (antes, desp[0])
        nueva = dict(a)
        nueva["seccion_codigo"] = secc
        nueva["division_codigo"] = divi
        nueva["grupo_codigo"] = grup
        nueva["clase_codigo"] = clase_cod
        if sub_cod:
            nueva["subclase_codigo"] = sub_cod
        actividades.append(nueva)
        # Ahora, si esta actividad referencia una clase no vista, la creamos
        if clase_cod and clase_cod not in clases_cods:
            print("       [INFO] Creando clase faltante inferida: %s" % clase_cod)
            try:
                cc_num = int(clase_cod[1:]) if clase_cod[1:].isdigit() else 0
            except ValueError:
                cc_num = 0
            s2, d2, g2 = _inferir_codigos_clase(clase_cod)
            clases.append({
                "codigo": clase_cod,
                "codigo_numerico": cc_num,
                "descripcion": u"Clase %s (inferida desde actividades)" % clase_cod,
                "grupo_codigo": g2,
                "division_codigo": d2,
                "seccion_codigo": s2,
                "notas_comprende": "",
                "notas_adicionales": "",
                "pagina": a.get("pagina"),
            })
            clases_cods.add(clase_cod)

    # 4. Divisiones: unir las que aparecen en clases (inferidas) + en actividades (inferidas)
    div_cods = set()  # type: set
    divisiones = []  # type: List[Dict[str, Any]]
    todos_los_codigos_div = []  # type: List[str]
    for c in clases:
        dc = c.get("division_codigo")
        if dc:
            todos_los_codigos_div.append(dc)
    for a in actividades:
        dc = a.get("division_codigo")
        if dc:
            todos_los_codigos_div.append(dc)
    for d_cod in todos_los_codigos_div:
        if not d_cod or len(d_cod) < 2:
            continue
        if d_cod in div_cods:
            continue
        div_cods.add(d_cod)
        letra = d_cod[0]
        try:
            num = int(d_cod[1:])
        except ValueError:
            num = 0
        divisiones.append({
            "codigo": d_cod,
            "codigo_numerico": num,
            "seccion_codigo": letra,
            "descripcion": u"División %s" % d_cod,
            "notas": "",
        })

    # 5. Grupos: desde clases.grupo_codigo (inferidos, no null)
    gpo_cods = set()  # type: set
    grupos = []  # type: List[Dict[str, Any]]
    todos_grupos = []  # type: List[str]
    for c in clases:
        gc = c.get("grupo_codigo")
        if gc:
            todos_grupos.append(gc)
    for a in actividades:
        gc = a.get("grupo_codigo")
        if gc:
            todos_grupos.append(gc)
    for g_cod in todos_grupos:
        if not g_cod or len(g_cod) < 3:
            continue
        if g_cod in gpo_cods:
            continue
        gpo_cods.add(g_cod)
        d_cod = g_cod[:3]
        try:
            num = int(g_cod[1:])
        except ValueError:
            num = 0
        if d_cod not in div_cods:
            letra = d_cod[0]
            try:
                d_num = int(d_cod[1:])
            except ValueError:
                d_num = 0
            divisiones.append({
                "codigo": d_cod,
                "codigo_numerico": d_num,
                "seccion_codigo": letra,
                "descripcion": u"División %s" % d_cod,
                "notas": "",
            })
            div_cods.add(d_cod)
        grupos.append({
            "codigo": g_cod,
            "codigo_numerico": num,
            "division_codigo": d_cod,
            "descripcion": u"Grupo %s" % g_cod,
            "notas": "",
        })

    # 6. Subclases: extraer desde actividades.subclase_codigo (ahora todas inferidas y correctas)
    sub_cods = set()  # type: set
    subclases = []  # type: List[Dict[str, Any]]
    for a in actividades:
        sc_cod = a.get("subclase_codigo")
        if not sc_cod:
            continue
        if sc_cod in sub_cods:
            continue
        sub_cods.add(sc_cod)
        if "." in sc_cod:
            base, _ = sc_cod.split(".", 1)
            c_cod_sc = base
        else:
            c_cod_sc = sc_cod[:5] if len(sc_cod) >= 5 else sc_cod
        try:
            num = float(sc_cod[1:])
        except ValueError:
            num = 0.0
        if c_cod_sc not in clases_cods:
            print("       [INFO] Creando clase faltante para subclase: %s" % c_cod_sc)
            letra = c_cod_sc[0] if c_cod_sc else "A"
            try:
                cc_num = int(c_cod_sc[1:]) if c_cod_sc[1:].isdigit() else 0
            except ValueError:
                cc_num = 0
            s2, d2, g2 = _inferir_codigos_clase(c_cod_sc)
            clases.append({
                "codigo": c_cod_sc,
                "codigo_numerico": cc_num,
                "descripcion": u"Clase %s (inferida desde subclases)" % c_cod_sc,
                "grupo_codigo": g2,
                "division_codigo": d2,
                "seccion_codigo": s2,
                "notas_comprende": "",
                "notas_adicionales": "",
                "pagina": None,
            })
            clases_cods.add(c_cod_sc)
        subclases.append({
            "codigo": sc_cod,
            "codigo_numerico": num,
            "clase_codigo": c_cod_sc,
            "descripcion": u"Subclase %s" % sc_cod,
            "notas": "",
        })

    print("       [FALLBACK OK] Secciones=%d Divisiones=%d Grupos=%d Clases=%d Subclases=%d Actividades=%d" % (
        len(secciones), len(divisiones), len(grupos), len(clases), len(subclases), len(actividades),
    ))

    return {
        "secciones": secciones, "divisiones": divisiones, "grupos": grupos,
        "clases": clases, "subclases": subclases, "actividades": actividades,
    }


def _t(s, maxlen):
    # type: (Any, int) -> str
    """Trunca un string a maxlen caracteres (seguro para None y no-strings)."""
    if s is None:
        return ""
    t = str(s)
    if len(t) <= maxlen:
        return t
    return t[:maxlen]


def main():
    print("=" * 60)
    print("CARGAR CIIU A POSTGRESQL (Python 3.8+ compatible)")
    print("=" * 60)

    print("[1/4] Cargando JSONs parseados...")
    arbol = cargar_json(PARSED_DIR / "arbol_completo.json")
    exclusiones = cargar_json(PARSED_DIR / "exclusiones.json")
    planas = construir_listas_planas_desde_arbol(arbol)

    acts_separado = cargar_json(PARSED_DIR / "actividades.json")
    clases_separado = cargar_json(PARSED_DIR / "clases.json")
    acts_por_cod = dict((a["codigo"], a) for a in acts_separado)
    for a in planas["actividades"]:
        extra = acts_por_cod.get(a["codigo"])
        if extra:
            for k, v in extra.items():
                if k not in a or not a[k]:
                    a[k] = v

    # --- FALLBACK: si el árbol está incompleto (0 secciones o <1000 actividades) ---
    if len(planas["secciones"]) < 21 or len(planas["actividades"]) < 1000:
        planas = construir_listas_planas_fallback(clases_separado, acts_separado)

    print("      Secciones:   %d" % len(planas["secciones"]))
    print("      Divisiones:  %d" % len(planas["divisiones"]))
    print("      Grupos:      %d" % len(planas["grupos"]))
    print("      Clases:      %d" % len(planas["clases"]))
    print("      Subclases:   %d" % len(planas["subclases"]))
    print("      Actividades: %d" % len(planas["actividades"]))
    print("      Exclusiones: %d" % len(exclusiones))

    conn = get_conn()
    conn.autocommit = False
    try:
        print("\n[2/4] Conectado a PostgreSQL — limpiando tablas...")
        with conn.cursor() as cur:
            for tabla in ["exclusiones", "actividades", "subclases", "clases",
                          "grupos", "divisiones", "secciones"]:
                cur.execute("TRUNCATE TABLE %s RESTART IDENTITY CASCADE;" % tabla)
        conn.commit()

        print("[3/4] Insertando datos (en orden jerárquico)...")

        # --- Secciones (codigo=CHAR(1), descripcion=VARCHAR(500), notas=TEXT) ---
        with conn.cursor() as cur:
            datos_prep = []
            for s in planas["secciones"]:
                datos_prep.append({
                    "codigo": _t(s["codigo"], 1),
                    "descripcion": _t(s["descripcion"], 500),
                    "notas": s.get("notas") or "",
                })
            execute_batch(cur, """
                INSERT INTO secciones (codigo, descripcion, notas)
                VALUES (%(codigo)s, %(descripcion)s, %(notas)s)
            """, datos_prep)
        print("      ✓ secciones (%d)" % len(planas["secciones"]))
        conn.commit()

        # --- Divisiones (codigo=VARCHAR(3), descripcion=VARCHAR(500)) ---
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, id FROM secciones")
            sec_ids = dict(cur.fetchall())
            datos = []
            for d in planas["divisiones"]:
                if d["seccion_codigo"] not in sec_ids:
                    print("      [WARN] División %s sin sección %s — se omite" % (d["codigo"], d["seccion_codigo"]))
                    continue
                datos.append({
                    "codigo": _t(d["codigo"], 3),
                    "codigo_numerico": d["codigo_numerico"],
                    "descripcion": _t(d.get("descripcion"), 500),
                    "notas": d.get("notas") or "",
                    "seccion_id": sec_ids[d["seccion_codigo"]],
                })
            execute_batch(cur, """
                INSERT INTO divisiones (codigo, codigo_numerico, descripcion, notas, seccion_id)
                VALUES (%(codigo)s, %(codigo_numerico)s, %(descripcion)s, %(notas)s, %(seccion_id)s)
            """, datos)
        print("      ✓ divisiones (%d)" % len(datos))
        conn.commit()

        # --- Grupos (codigo=VARCHAR(4), descripcion=VARCHAR(500)) ---
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, id FROM divisiones")
            div_ids = dict(cur.fetchall())
            datos = []
            for g in planas["grupos"]:
                if g["division_codigo"] not in div_ids:
                    print("      [WARN] Grupo %s sin división %s — se omite" % (g["codigo"], g["division_codigo"]))
                    continue
                datos.append({
                    "codigo": _t(g["codigo"], 4),
                    "codigo_numerico": g["codigo_numerico"],
                    "descripcion": _t(g.get("descripcion"), 500),
                    "notas": g.get("notas") or "",
                    "division_id": div_ids[g["division_codigo"]],
                })
            execute_batch(cur, """
                INSERT INTO grupos (codigo, codigo_numerico, descripcion, notas, division_id)
                VALUES (%(codigo)s, %(codigo_numerico)s, %(descripcion)s, %(notas)s, %(division_id)s)
            """, datos)
        print("      ✓ grupos (%d)" % len(datos))
        conn.commit()

        # --- Clases (codigo=VARCHAR(5), descripcion=VARCHAR(1000)) ---
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, id FROM grupos")
            gpo_ids = dict(cur.fetchall())
            datos = []
            for c in planas["clases"]:
                if c["grupo_codigo"] not in gpo_ids:
                    print("      [WARN] Clase %s sin grupo %s — se omite" % (c["codigo"], c["grupo_codigo"]))
                    continue
                datos.append({
                    "codigo": _t(c["codigo"], 5),
                    "codigo_numerico": c["codigo_numerico"],
                    "descripcion": _t(c.get("descripcion"), 1000),
                    "notas_comprende": c.get("notas_comprende") or "",
                    "notas_adicionales": c.get("notas_adicionales") or "",
                    "grupo_id": gpo_ids[c["grupo_codigo"]],
                })
            execute_batch(cur, """
                INSERT INTO clases (codigo, codigo_numerico, descripcion,
                                    notas_comprende, notas_adicionales, grupo_id)
                VALUES (%(codigo)s, %(codigo_numerico)s, %(descripcion)s,
                        %(notas_comprende)s, %(notas_adicionales)s, %(grupo_id)s)
            """, datos)
        print("      ✓ clases (%d)" % len(datos))
        conn.commit()

        # --- Subclases (codigo=VARCHAR(10), descripcion=VARCHAR(1000)) ---
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, id FROM clases")
            cla_ids = dict(cur.fetchall())
            datos = []
            for sc in planas["subclases"]:
                if sc["clase_codigo"] not in cla_ids:
                    print("      [WARN] Subclase %s sin clase %s — se omite" % (sc["codigo"], sc["clase_codigo"]))
                    continue
                datos.append({
                    "codigo": _t(sc["codigo"], 10),
                    "codigo_numerico": sc["codigo_numerico"],
                    "descripcion": _t(sc.get("descripcion"), 1000),
                    "notas": sc.get("notas") or "",
                    "clase_id": cla_ids[sc["clase_codigo"]],
                })
            execute_batch(cur, """
                INSERT INTO subclases (codigo, codigo_numerico, descripcion, notas, clase_id)
                VALUES (%(codigo)s, %(codigo_numerico)s, %(descripcion)s, %(notas)s, %(clase_id)s)
            """, datos)
        print("      ✓ subclases (%d)" % len(datos))
        conn.commit()

        # --- Actividades (codigo=VARCHAR(10), descripcion=VARCHAR(1500), descripcion_larga=TEXT) ---
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, id FROM subclases")
            sub_ids = dict(cur.fetchall())
            cur.execute("SELECT codigo, id FROM clases")
            cla_ids = dict(cur.fetchall())
            datos = []
            for a in planas["actividades"]:
                if a.get("clase_codigo") not in cla_ids:
                    print("      [WARN] Actividad %s sin clase %s — se omite" % (a["codigo"], a.get("clase_codigo")))
                    continue
                sub_cod = a.get("subclase_codigo")
                datos.append({
                    "codigo": _t(a["codigo"], 10),
                    "codigo_numerico": a["codigo_numerico"],
                    "descripcion": _t(a["descripcion"], 1500),
                    "descripcion_larga": _t(a.get("descripcion_larga"), 20000),
                    "palabras_clave": list(a.get("palabras_clave") or []),
                    "pagina_pdf": a.get("pagina"),
                    "clase_id": cla_ids[a["clase_codigo"]],
                    "subclase_id": sub_ids.get(sub_cod) if sub_cod else None,
                })
            execute_batch(cur, """
                INSERT INTO actividades (
                    codigo, codigo_numerico, descripcion, descripcion_larga,
                    palabras_clave, pagina_pdf, clase_id, subclase_id
                ) VALUES (
                    %(codigo)s, %(codigo_numerico)s, %(descripcion)s, %(descripcion_larga)s,
                    %(palabras_clave)s, %(pagina_pdf)s, %(clase_id)s, %(subclase_id)s
                )
            """, datos)
        print("      ✓ actividades (%d)" % len(datos))
        conn.commit()

        # --- Exclusiones ---
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, id FROM clases")
            cla_ids = dict(cur.fetchall())
            datos = []
            for e in exclusiones:
                c_cod = e.get("clase_codigo")
                cla_id = cla_ids.get(c_cod) if c_cod else None
                if cla_id is None:
                    continue
                datos.append({
                    "clase_id": cla_id,
                    "descripcion_texto": _t(e["descripcion_texto"], 20000),
                    "codigo_clase_destino": _t(e.get("codigo_clase_destino"), 10) if e.get("codigo_clase_destino") else None,
                    "descripcion_destino": _t(e.get("descripcion_destino"), 2000),
                    "pagina_pdf": e.get("pagina"),
                })
            execute_batch(cur, """
                INSERT INTO exclusiones (
                    clase_id, descripcion_texto, codigo_clase_destino,
                    descripcion_destino, pagina_pdf
                ) VALUES (
                    %(clase_id)s, %(descripcion_texto)s, %(codigo_clase_destino)s,
                    %(descripcion_destino)s, %(pagina_pdf)s
                )
            """, datos)
        print("      ✓ exclusiones (%d)" % len(datos))
        conn.commit()

        print("\n[4/4] Validación final consultando vw_conteos_jerarquia:")
        rangos = {
            "secciones":   (21, 21),
            "clases":      (415, 420),
            "actividades": (1700, 1800),
            "exclusiones": (380, 420),
        }
        todo_ok = True
        with conn.cursor() as cur:
            cur.execute("SELECT nivel, total FROM vw_conteos_jerarquia ORDER BY nivel;")
            for nivel, total in cur.fetchall():
                marca = " "
                if nivel in rangos:
                    mn, mx = rangos[nivel]
                    if mn <= total <= mx:
                        marca = "✓"
                    else:
                        marca = "✗ (fuera de rango %d-%d)" % (mn, mx)
                        todo_ok = False
                print("      %s  %-15s -> %5d" % (marca, nivel, total))

        conn.commit()
        conn.close()

        print()
        if todo_ok:
            print("[OK] TODOS LOS CONTEOS ESTÁN DENTRO DE LOS RANGOS ESPERADOS.")
            print("     La base de datos está lista para el modelo de IA.")
        else:
            print("[WARN] Algunos conteos están FUERA de rango. Revisa:")
            print("       %s" % str(PARSED_DIR / "_VALIDACIONES.txt"))

        print("\n[LISTO] Siguiente paso: levantar el backend con:")
        print("       cd backend && pip install -r requirements.txt")
        print("       uvicorn app.main:app --reload")

    except Exception as e:
        conn.rollback()
        conn.close()
        print("\n[ERROR CRÍTICO] Fallo durante la carga: %s" % e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
