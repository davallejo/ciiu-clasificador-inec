# -*- coding: utf-8 -*-
"""
Wrapper de entrada para Vercel Python Serverless Functions.

Monta el PYTHONPATH para que se pueda importar `app.main` desde /backend,
aplica el adapter Mangum (convierte ASGI → WSGI serverless), y exporta
`handler` que es lo que Vercel invoca por cada request.

También reubica el directorio de caché del clasificador a /tmp (el único
directorio escribible en entorno serverless de Vercel / AWS Lambda).
"""

from __future__ import print_function, unicode_literals

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# En serverless el FS es read-only salvo /tmp — forzamos MODELO_DIR ahí
os.environ.setdefault("CIIU_MODELO_DIR", "/tmp/ciiu_models")


try:
    from mangum import Mangum
except ImportError:
    raise SystemExit(
        "[SERVERLESS ERROR] mangum no instalado. Asegúrate de ejecutar: "
        "pip install -r requirements.txt (en la raíz del proyecto)."
    )

from app.main import app  # noqa: E402  (import después de PYTHONPATH)


handler = Mangum(app, lifespan="off", api_gateway_base_path="/")
