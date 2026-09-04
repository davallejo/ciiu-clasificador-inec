# -*- coding: utf-8 -*-
"""
PASO 1: Extraer TODO el texto del PDF ciiu.pdf con PyMuPDF (fitz).
Este script NO hace parsing; solo extrae el texto CRUDO página por página
y lo guarda en un archivo .txt para que el humano pueda REVISAR y CONFIRMAR
que la extracción es 100% fiel al original (sin OCR, usando la capa de texto real).

Además guarda un segundo archivo con la estructura detectada (coordenadas, tamaños de fuente)
para validar patrones de jerarquía (códigos vs títulos vs descripciones).

Python 3.8+ compatible.

Autor: Diego Vallejo
"""

from __future__ import print_function, unicode_literals

import os
import sys
import json
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] PyMuPDF no está instalado. Ejecuta: pip install PyMuPDF")
    sys.exit(1)


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "Insumos" / "ciiu.pdf"
OUTPUT_DIR = BASE_DIR / "data" / "extraidos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TXT_PATH = OUTPUT_DIR / "ciiu_texto_completo.txt"
STRUCT_PATH = OUTPUT_DIR / "ciiu_estructura_paginas.jsonl"


def extraer_texto_y_estructura():
    if not PDF_PATH.exists():
        print("[ERROR] No se encontró el PDF en: %s" % PDF_PATH)
        sys.exit(1)

    print("[INFO] Abriendo PDF: %s" % PDF_PATH)
    doc = fitz.open(str(PDF_PATH))
    total_paginas = len(doc)
    print("[INFO] Total de páginas: %d" % total_paginas)

    texto_acumulado = []

    with open(str(STRUCT_PATH), "w", encoding="utf-8") as f_struct:
        for page_idx in range(total_paginas):
            page = doc[page_idx]
            page_num = page_idx + 1

            # --- Texto crudo (para revisión humana) ---
            texto_pagina = page.get_text("text")
            texto_acumulado.append(
                "\n" + "=" * 100 + "\n"
                + ("PÁGINA %d / %d\n" % (page_num, total_paginas))
                + "=" * 100 + "\n"
                + (texto_pagina or "")
                + "\n"
            )

            # --- Estructura detallada (bloques con fuente y coordenadas) ---
            blocks = page.get_text("dict")["blocks"]
            registros_pagina = []
            for b in blocks:
                if "lines" not in b:
                    continue
                for line in b["lines"]:
                    for span in line["spans"]:
                        texto_span = span["text"].strip()
                        if not texto_span:
                            continue
                        registros_pagina.append({
                            "page": page_num,
                            "text": texto_span,
                            "size": round(span["size"], 2),
                            "font": span["font"],
                            "bold": "Bold" in span["font"] or "bold" in span["font"].lower(),
                            "bbox": [round(v, 1) for v in span["bbox"]],
                        })

            if registros_pagina:
                for r in registros_pagina:
                    f_struct.write(json.dumps(r, ensure_ascii=False) + "\n")

            if page_num % 20 == 0:
                print("  ... procesadas %d/%d páginas" % (page_num, total_paginas))

    # Guardar texto completo
    with open(str(TXT_PATH), "w", encoding="utf-8") as f_txt:
        f_txt.write("".join(texto_acumulado))

    doc.close()

    print("\n[OK] Extracción completada.")
    print("  - Texto completo:   %s" % TXT_PATH)
    print("  - Estructura (JSONL): %s" % STRUCT_PATH)
    print("\n[RECOMENDACIÓN] Abre el TXT y revisa las primeras 50 páginas para")
    print("confirmar que los patrones de códigos (A01, A011, A0113, A0113.2, A0113.22)")
    print("y las descripciones se extrajeron correctamente.")


if __name__ == "__main__":
    extraer_texto_y_estructura()
