# -*- coding: utf-8 -*-
"""SQLAlchemy engine + session factory (Python 3.8+ compatible)."""

from __future__ import annotations

from typing import Any, Dict, Generator

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base
except ImportError:
    raise SystemExit("Instala SQLAlchemy: pip install sqlalchemy psycopg2-binary")

try:
    from dotenv import load_dotenv  # type: ignore
    import os as _os
    from pathlib import Path as _Path
    _env = _Path(__file__).resolve().parent.parent.parent / ".env"
    if _env.exists():
        load_dotenv(str(_env), override=False)
except ImportError:  # pragma: no cover - dotenv está en requirements
    pass

from .config import get_settings

settings = get_settings()

uri = settings.sqlalchemy_database_uri
# Detectar conexiones remotas (Vercel Postgres, Supabase, Neon, etc.)
# por el host contenido en la URI. A estas hay que exigirles SSL.
_host_es_remoto = False
_display_host = ""
_display_dbname = ""
try:
    # postgresql://user:pass@host:port/dbname
    if "@" in uri:
        resto = uri.split("@", 1)[1]
        host_port, slash, dbname = resto.partition("/")
        if "?" in dbname:
            dbname = dbname.split("?", 1)[0]
        _display_dbname = dbname or "(vacío)"
        if ":" in host_port:
            _display_host = host_port.rsplit(":", 1)[0]
        else:
            _display_host = host_port
        if _display_host and _display_host not in ("localhost", "127.0.0.1", "0.0.0.0", ""):
            _host_es_remoto = True
    elif uri.startswith("postgresql"):
        _display_host = "localhost"
except Exception:
    pass

connect_args = {}  # type: Dict[str, Any]
_requires_ssl = settings.app_env == "production" or _host_es_remoto

if _requires_ssl:
    # Vercel Postgres y la mayoría de servicios cloud requieren SSL.
    # Aceptamos self-signed (necesario en algunos proveedores).
    connect_args["sslmode"] = "require"

# Print informativo (NUNCA mostrar password)
if _display_host:
    ssl_tag = "  [SSL]" if _requires_ssl else ""
    print("[DB] Conectando a PostgreSQL: %s@%s/%s%s" % (
        settings.db_user or "(usuario)",
        _display_host,
        _display_dbname or "(db)",
        ssl_tag,
    ))
else:
    print("[DB] Conectando a PostgreSQL mediante URI (DATABASE_URL/POSTGRES_URL)%s" % (
        "  [SSL]" if _requires_ssl else "",
    ))

engine = create_engine(
    uri,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    # type: () -> Generator[Any, None, None]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
