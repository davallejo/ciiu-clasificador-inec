# -*- coding: utf-8 -*-
"""
PASO 3: Conectar a PostgreSQL, crear la base de datos y aplicar el schema.sql.

Hace tres cosas:
  1. Lee variables de entorno desde .env
  2. Conecta a PostgreSQL (base `postgres` del sistema)
  3. Crea la base de datos `ciiu_inec` si no existe
  4. Cierra esa conexión, se conecta a `ciiu_inec` y ejecuta database/schema.sql

USO:
  python scripts/03_aplicar_schema.py

Requisitos:
  - PostgreSQL corriendo localmente en el puerto 5432
  - Usuario `postgres` con password configurado en .env
  - Dependencias:  pip install psycopg2-binary python-dotenv
  - Python 3.8+ compatible

Autor: Diego Vallejo
"""

from __future__ import print_function, unicode_literals

import os
import sys
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    import psycopg2
    from psycopg2 import sql
    from dotenv import load_dotenv
except ImportError as e:
    print("[ERROR] Falta dependencia: %s" % e)
    print("Instala con:  pip install psycopg2-binary python-dotenv")
    sys.exit(1)

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.example", override=False)  # fallback para valores por defecto

SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_env(name, default=None):
    # type: (str, Optional[str]) -> str
    v = os.getenv(name) or os.getenv(name.upper())
    if not v and default is None:
        print("[ERROR] Falta variable de entorno: %s" % name)
        sys.exit(1)
    return v if v else (default or "")


def main():
    host     = get_env("DB_HOST", "localhost")
    port     = int(get_env("DB_PORT", "5432"))
    db_user  = get_env("DB_USER", "postgres")
    db_pass  = get_env("DB_PASSWORD", "")
    db_name  = get_env("DB_NAME", "ciiu_inec")

    print("=" * 60)
    print("APLICAR SCHEMA CIIU EN POSTGRESQL")
    print("=" * 60)
    print("  Host    : %s:%d" % (host, port))
    print("  Usuario : %s" % db_user)
    print("  DB      : %s" % db_name)
    print()

    # ----- 1. Conectar a la BD de sistema 'postgres' para CREATE DATABASE -----
    try:
        conn_sys = psycopg2.connect(host=host, port=port, user=db_user, password=db_pass, dbname="postgres")
        conn_sys.autocommit = True
    except Exception as e:
        print("[ERROR] No se pudo conectar a PostgreSQL (postgres): %s" % e)
        sys.exit(1)

    try:
        with conn_sys.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                print("[OK] Base de datos '%s' creada." % db_name)
            else:
                print("[INFO] Base de datos '%s' ya existe — NO se recrea." % db_name)
    finally:
        conn_sys.close()

    # ----- 2. Conectar a la BD objetivo y ejecutar schema.sql -----
    if not SCHEMA_PATH.exists():
        print("[ERROR] No se encontró %s" % SCHEMA_PATH)
        sys.exit(1)

    try:
        conn = psycopg2.connect(host=host, port=port, user=db_user, password=db_pass, dbname=db_name)
    except Exception as e:
        print("[ERROR] No se pudo conectar a '%s': %s" % (db_name, e))
        sys.exit(1)

    try:
        sql_text = SCHEMA_PATH.read_text(encoding="utf-8")
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()
        print("[OK] Schema SQL ejecutado desde: %s" % SCHEMA_PATH.name)
    except Exception as e:
        conn.rollback()
        print("[ERROR] Fallo al ejecutar schema.sql: %s" % e)
        sys.exit(1)
    finally:
        conn.close()

    # ----- 3. Verificación: conteos de tablas -----
    try:
        conn = psycopg2.connect(host=host, port=port, user=db_user, password=db_pass, dbname=db_name)
        with conn.cursor() as cur:
            cur.execute("SELECT nivel, total FROM vw_conteos_jerarquia ORDER BY nivel;")
            print("\nConteos por tabla (todas en 0 hasta la carga):")
            for n, t in cur.fetchall():
                print("  %-15s -> %s" % (n, t))
        conn.close()
    except Exception as e:
        print("[WARN] No se pudo consultar vista de conteos: %s" % e)

    print("\n[LISTO] Ahora ejecuta:  python scripts/04_parser_ciiu.py   (si no lo has hecho)")
    print("        y luego:         python scripts/05_cargar_a_postgres.py")


if __name__ == "__main__":
    main()
