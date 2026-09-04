# -*- coding: utf-8 -*-
"""
PASO 2: PARSER DEL CATÁLOGO CIIU 4.0 (INEC) — Python 3.8+ compatible
====================================================================

ESTE ES EL ARCHIVO MÁS CRÍTICO DE TODO EL PROYECTO.

Convierte el PDF ciiu.pdf en un dataset estructurado 100% fiel:
  - 21 secciones
  - ~divisiones
  - ~grupos
  - ~417 clases
  - ~subclases
  - ~1.724 actividades detalladas (nivel granular PARA EL MODELO DE IA)
  - ~388 bloques de exclusión ("ESTA CLASE NO COMPRENDE:") — CAPTURADOS APARTE

ESTRATEGIA PARA NO ALUCINAR:
  1. Máquina de estados: primero detectamos el TIPO DE LÍNEA, luego acumulamos.
  2. Descripciones MULTILÍNEA se unen detectando continuación.
  3. TODOS los registros incluyen TRAZABILIDAD: número de página.
  4. Al final, VALIDACIONES AUTOMÁTICAS (conteos, códigos duplicados, FKs).
  5. Salida en JSON + archivo _VALIDACIONES.txt (REVISIÓN HUMANA OBLIGATORIA).

Uso:  python scripts/04_parser_ciiu.py
Autor: Diego Vallejo
"""

from __future__ import print_function, unicode_literals

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] Instala primero:  pip install PyMuPDF")
    sys.exit(1)


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "Insumos" / "ciiu.pdf"
PARSED_DIR = BASE_DIR / "data" / "parsed"
PARSED_DIR.mkdir(parents=True, exist_ok=True)

RE_SECCION = re.compile(r'^([A-U])\s{2,}([A-ZÁÉÍÓÚÑ\s,./()&\-]{5,})')
RE_DIVISION = re.compile(r'^([A-U]\d{2})(?:\s{1,}(.+))?$')
RE_GRUPO = re.compile(r'^([A-U]\d{3})(?:\s{1,}(.+))?$')
RE_CLASE = re.compile(r'^([A-U]\d{4})(?:\s{1,}(.+))?$')
RE_SUBCLASE = re.compile(r'^([A-U]\d{4}\.\d)(?:\s{1,}(.+))?$')
RE_ACTIVIDAD = re.compile(r'^([A-U]\d{4}\.\d{2})(?:\s{1,}(.+))?$')

PATRONES_NOTAS = [
    ("COMPRENDE",    re.compile(r'^(ESTA CLASE COMPRENDE|COMPRENDE)\s*:\s*', re.I)),
    ("NO_COMPRENDE", re.compile(r'^(ESTA CLASE NO COMPRENDE|NO COMPRENDE|NOCOMPRENDE)\s*:\s*', re.I)),
    ("NOTA",         re.compile(r'^(NOTA|OBSERVACI?O?N|NOTAS)\s*[:.]', re.I)),
    ("INCLUYE",      re.compile(r'^INCLUYE\s*:\s*', re.I)),
    ("EXCLUYE",      re.compile(r'^EXCLUYE\s*:\s*', re.I)),
]


def detectar_tipo_linea(linea):
    # type: (str) -> str
    l = linea.strip()
    if not l:
        return "vacia"
    if RE_ACTIVIDAD.match(l):   return "actividad"
    if RE_SUBCLASE.match(l):    return "subclase"
    if RE_CLASE.match(l):       return "clase"
    if RE_GRUPO.match(l):       return "grupo"
    if RE_DIVISION.match(l):    return "division"
    if RE_SECCION.match(l):     return "seccion"
    for tipo, rx in PATRONES_NOTAS:
        if rx.match(l):
            if tipo == "COMPRENDE":    return "nota_comprende"
            if tipo == "NO_COMPRENDE": return "nota_no_comprende"
            return "nota_otra"
    return "continuacion"


def extraer_lineas_con_paginas():
    # type: () -> List[Dict[str, Any]]
    if not PDF_PATH.exists():
        print("[ERROR] No existe: %s" % PDF_PATH)
        sys.exit(1)
    doc = fitz.open(str(PDF_PATH))
    lineas = []  # type: List[Dict[str, Any]]
    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]
        txt = page.get_text("text")
        for raw_line in txt.split("\n"):
            s = raw_line.rstrip()
            if s.strip():
                lineas.append({"page": page_num, "text": s})
    doc.close()
    print("[FASE 1] Extraídas %d líneas de texto con trazabilidad de página." % len(lineas))
    return lineas


class EstadoParser(object):
    def __init__(self):
        self.secciones = {}   # type: Dict[str, Dict[str, Any]]
        self.divisiones = {}  # type: Dict[str, Dict[str, Any]]
        self.grupos = {}      # type: Dict[str, Dict[str, Any]]
        self.clases = {}      # type: Dict[str, Dict[str, Any]]
        self.subclases = {}   # type: Dict[str, Dict[str, Any]]
        self.actividades = {} # type: Dict[str, Dict[str, Any]]
        self.exclusiones = [] # type: List[Dict[str, Any]]

        self.cur_seccion = None    # type: Optional[str]
        self.cur_division = None   # type: Optional[str]
        self.cur_grupo = None      # type: Optional[str]
        self.cur_clase = None      # type: Optional[str]
        self.cur_subclase = None   # type: Optional[str]
        self.cur_actividad = None  # type: Optional[str]

        self.en_nota_comprende = False
        self.en_nota_no_comprende = False
        self.buf_nota = []    # type: List[str]
        self.buf_nota_pagina = None  # type: Optional[int]


def unir_siguiente_linea_descripcion(lineas, idx):
    # type: (List[Dict[str, Any]], int) -> Tuple[str, int]
    primera = lineas[idx]["text"]
    for rx in [RE_ACTIVIDAD, RE_SUBCLASE, RE_CLASE, RE_GRUPO, RE_DIVISION]:
        m = rx.match(primera.strip())
        if m:
            resto = m.group(2) or ""
            partes = [resto.strip()] if resto else []
            j = idx + 1
            while j < len(lineas):
                tipo = detectar_tipo_linea(lineas[j]["text"])
                if tipo == "continuacion":
                    partes.append(lineas[j]["text"].strip())
                    j += 1
                else:
                    break
            descripcion = " ".join(partes).strip()
            descripcion = re.sub(r'\s{2,}', ' ', descripcion)
            return descripcion, j - 1
    m = RE_SECCION.match(primera.strip())
    if m:
        resto = m.group(2) or ""
        partes = [resto.strip()]
        j = idx + 1
        while j < len(lineas):
            tipo = detectar_tipo_linea(lineas[j]["text"])
            if tipo == "continuacion":
                partes.append(lineas[j]["text"].strip())
                j += 1
            else:
                break
        descripcion = " ".join(partes).strip()
        descripcion = re.sub(r'\s{2,}', ' ', descripcion)
        return descripcion, j - 1
    return primera.strip(), idx


def flush_notas(estado):
    # type: (EstadoParser) -> None
    if not estado.buf_nota:
        estado.en_nota_comprende = estado.en_nota_no_comprende = False
        return
    texto = "\n".join(estado.buf_nota).strip()
    texto = re.sub(r'\s{2,}', ' ', texto)

    if estado.en_nota_comprende and estado.cur_clase:
        estado.clases[estado.cur_clase]["notas_comprende"] = texto

    elif estado.en_nota_no_comprende:
        rx_codigo_en_linea = re.compile(r'\b([A-U]\d{4}(?:\.\d{1,2})?)\b')
        for linea_nota in texto.split("\n"):
            linea_nota = linea_nota.strip().strip("-").strip("•").strip()
            if not linea_nota:
                continue
            codigo_destino = None
            m = rx_codigo_en_linea.search(linea_nota)
            if m:
                codigo_destino = m.group(1)
            descripcion_destino = None
            if codigo_destino:
                if codigo_destino in estado.clases:
                    descripcion_destino = estado.clases[codigo_destino]["descripcion"]
                elif codigo_destino in estado.actividades:
                    descripcion_destino = estado.actividades[codigo_destino]["descripcion"]
                elif codigo_destino in estado.subclases:
                    descripcion_destino = estado.subclases[codigo_destino]["descripcion"]
            estado.exclusiones.append({
                "clase_codigo": estado.cur_clase,
                "descripcion_texto": linea_nota,
                "codigo_clase_destino": codigo_destino,
                "descripcion_destino": descripcion_destino,
                "pagina": estado.buf_nota_pagina,
            })

    estado.buf_nota = []
    estado.en_nota_comprende = estado.en_nota_no_comprende = False
    estado.buf_nota_pagina = None


def parsear_lineas(lineas):
    # type: (List[Dict[str, Any]]) -> EstadoParser
    estado = EstadoParser()
    i = 0
    total = len(lineas)

    while i < total:
        linea = lineas[i]["text"]
        pagina = lineas[i]["page"]
        tipo = detectar_tipo_linea(linea)

        if (estado.en_nota_comprende or estado.en_nota_no_comprende) and \
           tipo not in ("continuacion", "nota_comprende", "nota_no_comprende", "nota_otra"):
            flush_notas(estado)

        if tipo == "vacia":
            i += 1
            continue

        elif tipo == "seccion":
            m = RE_SECCION.match(linea.strip())
            codigo = m.group(1)
            descripcion, i = unir_siguiente_linea_descripcion(lineas, i)
            estado.secciones[codigo] = {
                "codigo": codigo,
                "descripcion": descripcion.strip(),
                "pagina": pagina,
            }
            estado.cur_seccion = codigo
            estado.cur_division = estado.cur_grupo = estado.cur_clase = estado.cur_subclase = None
            estado.cur_actividad = None
            flush_notas(estado)

        elif tipo == "division":
            m = RE_DIVISION.match(linea.strip())
            codigo = m.group(1)
            descripcion, i = unir_siguiente_linea_descripcion(lineas, i)
            estado.divisiones[codigo] = {
                "codigo": codigo,
                "codigo_numerico": int(codigo[1:]),
                "descripcion": descripcion.strip(),
                "seccion_codigo": estado.cur_seccion,
                "pagina": pagina,
            }
            estado.cur_division = codigo
            estado.cur_grupo = estado.cur_clase = estado.cur_subclase = None
            estado.cur_actividad = None
            flush_notas(estado)

        elif tipo == "grupo":
            m = RE_GRUPO.match(linea.strip())
            codigo = m.group(1)
            descripcion, i = unir_siguiente_linea_descripcion(lineas, i)
            estado.grupos[codigo] = {
                "codigo": codigo,
                "codigo_numerico": int(codigo[1:]),
                "descripcion": descripcion.strip(),
                "division_codigo": estado.cur_division,
                "seccion_codigo": estado.cur_seccion,
                "pagina": pagina,
            }
            estado.cur_grupo = codigo
            estado.cur_clase = estado.cur_subclase = None
            estado.cur_actividad = None
            flush_notas(estado)

        elif tipo == "clase":
            m = RE_CLASE.match(linea.strip())
            codigo = m.group(1)
            descripcion, i = unir_siguiente_linea_descripcion(lineas, i)
            estado.clases[codigo] = {
                "codigo": codigo,
                "codigo_numerico": int(codigo[1:]),
                "descripcion": descripcion.strip(),
                "grupo_codigo": estado.cur_grupo,
                "division_codigo": estado.cur_division,
                "seccion_codigo": estado.cur_seccion,
                "notas_comprende": "",
                "notas_adicionales": "",
                "pagina": pagina,
            }
            estado.cur_clase = codigo
            estado.cur_subclase = None
            estado.cur_actividad = None
            flush_notas(estado)

        elif tipo == "subclase":
            m = RE_SUBCLASE.match(linea.strip())
            codigo = m.group(1)
            descripcion, i = unir_siguiente_linea_descripcion(lineas, i)
            estado.subclases[codigo] = {
                "codigo": codigo,
                "codigo_numerico": float(codigo[1:]),
                "descripcion": descripcion.strip(),
                "clase_codigo": estado.cur_clase,
                "grupo_codigo": estado.cur_grupo,
                "division_codigo": estado.cur_division,
                "seccion_codigo": estado.cur_seccion,
                "pagina": pagina,
            }
            estado.cur_subclase = codigo
            estado.cur_actividad = None
            flush_notas(estado)

        elif tipo == "actividad":
            m = RE_ACTIVIDAD.match(linea.strip())
            codigo = m.group(1)
            descripcion, i = unir_siguiente_linea_descripcion(lineas, i)
            subclase_codigo = None
            if estado.cur_subclase and codigo.startswith(estado.cur_subclase):
                subclase_codigo = estado.cur_subclase
            else:
                if "." in codigo:
                    base, dec = codigo.split(".")
                    if len(dec) == 2:
                        posible = "%s.%s" % (base, dec[0])
                        if posible in estado.subclases:
                            subclase_codigo = posible
            estado.actividades[codigo] = {
                "codigo": codigo,
                "codigo_numerico": float(codigo[1:]),
                "descripcion": descripcion.strip(),
                "descripcion_larga": "",
                "palabras_clave": [],
                "subclase_codigo": subclase_codigo,
                "clase_codigo": estado.cur_clase,
                "grupo_codigo": estado.cur_grupo,
                "division_codigo": estado.cur_division,
                "seccion_codigo": estado.cur_seccion,
                "pagina": pagina,
            }
            estado.cur_actividad = codigo
            flush_notas(estado)

        elif tipo == "nota_comprende":
            flush_notas(estado)
            estado.en_nota_comprende = True
            estado.buf_nota_pagina = pagina
            for _, rx in PATRONES_NOTAS:
                m2 = rx.match(linea.strip())
                if m2:
                    resto = linea.strip()[m2.end():].strip()
                    if resto:
                        estado.buf_nota.append(resto)
                    break

        elif tipo == "nota_no_comprende":
            flush_notas(estado)
            estado.en_nota_no_comprende = True
            estado.buf_nota_pagina = pagina
            for _, rx in PATRONES_NOTAS:
                m2 = rx.match(linea.strip())
                if m2:
                    resto = linea.strip()[m2.end():].strip()
                    if resto:
                        estado.buf_nota.append(resto)
                    break

        elif tipo == "nota_otra":
            flush_notas(estado)
            if estado.cur_clase:
                txt = linea.strip()
                cur = estado.clases[estado.cur_clase]["notas_adicionales"]
                estado.clases[estado.cur_clase]["notas_adicionales"] = ((cur + "\n" + txt).strip() if cur else txt)

        elif tipo == "continuacion":
            if estado.en_nota_comprende or estado.en_nota_no_comprende:
                estado.buf_nota.append(linea.strip())
            elif estado.cur_actividad:
                act = estado.actividades[estado.cur_actividad]
                dl = act["descripcion_larga"]
                act["descripcion_larga"] = ((dl + " " + linea.strip()).strip() if dl else linea.strip())

        i += 1

    flush_notas(estado)
    return estado


CONTEOS_ESPERADOS = {
    "secciones":   (21, 21),
    "clases":      (415, 420),
    "actividades": (1700, 1800),
    "exclusiones": (380, 420),
}


def validar(estado):
    # type: (EstadoParser) -> List[str]
    errores = []   # type: List[str]
    warnings = []  # type: List[str]
    datos = {
        "secciones":   len(estado.secciones),
        "divisiones":  len(estado.divisiones),
        "grupos":      len(estado.grupos),
        "clases":      len(estado.clases),
        "subclases":   len(estado.subclases),
        "actividades": len(estado.actividades),
        "exclusiones": len(estado.exclusiones),
    }
    for nivel, rng in CONTEOS_ESPERADOS.items():
        mn, mx = rng
        cnt = datos[nivel]
        if not (mn <= cnt <= mx):
            errores.append("[CONTEO FUERA DE RANGO] %s: %d registros (esperado entre %d y %d) — REVISA EL PARSER." % (nivel, cnt, mn, mx))
        else:
            warnings.append("[OK CONTEO] %s: %d registros (rango %d-%d) ✓" % (nivel, cnt, mn, mx))

    for nombre, d in [("secciones", estado.secciones), ("divisiones", estado.divisiones),
                      ("grupos", estado.grupos), ("clases", estado.clases),
                      ("subclases", estado.subclases), ("actividades", estado.actividades)]:
        cods = [v["codigo"] for v in d.values()]
        if len(cods) != len(set(cods)):
            errores.append("[DUPLICADOS] %s: hay códigos repetidos!" % nombre)

    for cod, d in estado.divisiones.items():
        if not d.get("seccion_codigo") or d["seccion_codigo"] not in estado.secciones:
            errores.append("[HIJO SIN PADRE] División %s sin sección válida" % cod)
    for cod, d in estado.grupos.items():
        if not d.get("division_codigo") or d["division_codigo"] not in estado.divisiones:
            errores.append("[HIJO SIN PADRE] Grupo %s sin división válida (p. %s)" % (cod, d.get("pagina")))
    for cod, d in estado.clases.items():
        if not d.get("grupo_codigo") or d["grupo_codigo"] not in estado.grupos:
            errores.append("[HIJO SIN PADRE] Clase %s sin grupo válido (p. %s)" % (cod, d.get("pagina")))
    for cod, d in estado.subclases.items():
        if not d.get("clase_codigo") or d["clase_codigo"] not in estado.clases:
            errores.append("[HIJO SIN PADRE] Subclase %s sin clase válida (p. %s)" % (cod, d.get("pagina")))
    for cod, d in estado.actividades.items():
        if not d.get("clase_codigo") or d["clase_codigo"] not in estado.clases:
            errores.append("[HIJO SIN PADRE] Actividad %s sin clase válida (p. %s)" % (cod, d.get("pagina")))

    for cod, d in estado.actividades.items():
        if not d.get("descripcion"):
            errores.append("[SIN DESCRIPCIÓN] Actividad %s (p. %s)" % (cod, d.get("pagina")))

    return warnings + ([] if not errores else ["", "=" * 40, "ERRORES CRÍTICOS:", "=" * 40] + errores)


def guardar_salidas(estado):
    # type: (EstadoParser) -> None
    arbol = {}  # type: Dict[str, Any]
    for s_cod, s in estado.secciones.items():
        secc = {"codigo": s["codigo"], "descripcion": s["descripcion"],
                "pagina": s.get("pagina"), "notas": s.get("notas"), "divisiones": []}
        for d_cod in sorted([c for c, v in estado.divisiones.items() if v["seccion_codigo"] == s_cod]):
            d = estado.divisiones[d_cod]
            divi = {k: d.get(k) for k in ("codigo", "codigo_numerico", "descripcion",
                                           "seccion_codigo", "pagina", "notas")}
            divi["grupos"] = []
            for g_cod in sorted([c for c, v in estado.grupos.items() if v["division_codigo"] == d_cod]):
                g = estado.grupos[g_cod]
                grup = {k: g.get(k) for k in ("codigo", "codigo_numerico", "descripcion",
                                               "division_codigo", "pagina", "notas")}
                grup["clases"] = []
                for c_cod in sorted([c for c, v in estado.clases.items() if v["grupo_codigo"] == g_cod]):
                    c = estado.clases[c_cod]
                    clas = {k: c.get(k) for k in ("codigo", "codigo_numerico", "descripcion",
                                                   "grupo_codigo", "notas_comprende",
                                                   "notas_adicionales", "pagina")}
                    clas["subclases"] = []
                    clas["actividades"] = []
                    for sc_cod in sorted([c2 for c2, v in estado.subclases.items() if v["clase_codigo"] == c_cod]):
                        sc = estado.subclases[sc_cod]
                        subcl = {k: sc.get(k) for k in ("codigo", "codigo_numerico", "descripcion",
                                                        "clase_codigo", "pagina", "notas")}
                        subcl["actividades"] = []
                        for a_cod in sorted([c2 for c2, v in estado.actividades.items() if v["subclase_codigo"] == sc_cod]):
                            a = estado.actividades[a_cod]
                            subcl["actividades"].append(dict(a))
                            clas["actividades"].append(dict(a))
                        clas["subclases"].append(subcl)
                    for a_cod in sorted([c2 for c2, v in estado.actividades.items()
                                          if v["clase_codigo"] == c_cod and v.get("subclase_codigo") is None]):
                        a = estado.actividades[a_cod]
                        clas["actividades"].append(dict(a))
                    grup["clases"].append(clas)
                divi["grupos"].append(grup)
            secc["divisiones"].append(divi)
        arbol[s_cod] = secc

    with open(str(PARSED_DIR / "arbol_completo.json"), "w", encoding="utf-8") as f:
        json.dump(arbol, f, ensure_ascii=False, indent=2)

    acts = sorted(estado.actividades.values(), key=lambda x: x["codigo"])
    with open(str(PARSED_DIR / "actividades.json"), "w", encoding="utf-8") as f:
        json.dump(acts, f, ensure_ascii=False, indent=2)

    with open(str(PARSED_DIR / "exclusiones.json"), "w", encoding="utf-8") as f:
        json.dump(estado.exclusiones, f, ensure_ascii=False, indent=2)

    clases_lista = sorted(estado.clases.values(), key=lambda x: x["codigo"])
    with open(str(PARSED_DIR / "clases.json"), "w", encoding="utf-8") as f:
        json.dump(clases_lista, f, ensure_ascii=False, indent=2)

    resumen = validar(estado)
    with open(str(PARSED_DIR / "_VALIDACIONES.txt"), "w", encoding="utf-8") as f:
        f.write("VALIDACIÓN AUTOMÁTICA DEL PARSER CIIU 4.0\n")
        f.write("=" * 60 + "\n")
        f.write("Archivo fuente : %s\n" % PDF_PATH)
        f.write("Secciones       : %d\n" % len(estado.secciones))
        f.write("Divisiones      : %d\n" % len(estado.divisiones))
        f.write("Grupos          : %d\n" % len(estado.grupos))
        f.write("Clases          : %d\n" % len(estado.clases))
        f.write("Subclases       : %d\n" % len(estado.subclases))
        f.write("Actividades     : %d  ← NIVEL PARA IA\n" % len(estado.actividades))
        f.write("Exclusiones     : %d  ← NO son actividades\n" % len(estado.exclusiones))
        f.write("=" * 60 + "\n\n")
        for linea in resumen:
            f.write(linea + "\n")
    print("\n".join(resumen))

    print("\n[OK] Archivos generados en %s/" % PARSED_DIR)
    print("  - arbol_completo.json   (jerarquía anidada completa)")
    print("  - actividades.json      (%d regs — PARA MODELO IA)" % len(acts))
    print("  - clases.json           (%d regs — con notas COMPRENDE)" % len(clases_lista))
    print("  - exclusiones.json      (%d regs — NO son actividades)" % len(estado.exclusiones))
    print("  - _VALIDACIONES.txt     (resumen para revisión humana OBLIGATORIA)")


def main():
    print("=" * 60)
    print("PARSER CIIU 4.0 INEC — Diego Vallejo (Python 3.8+ compatible)")
    print("=" * 60)
    lineas = extraer_lineas_con_paginas()
    print("[FASE 2] Parseando líneas en jerarquía CIIU...")
    estado = parsear_lineas(lineas)
    print("[FASE 3] Validando integridad...")
    print("[FASE 4] Guardando archivos JSON + reporte de validación...")
    guardar_salidas(estado)
    print("\n[LISTO] Revisa data/parsed/_VALIDACIONES.txt para confirmar")
    print("       que no haya errores. Si todo es OK, pasa a:")
    print("       python scripts/05_cargar_a_postgres.py")


if __name__ == "__main__":
    main()
