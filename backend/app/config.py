# -*- coding: utf-8 -*-
"""Backend settings (Python 3.8+ compatible)."""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache
from typing import List, Optional

try:
    from urllib.parse import quote_plus
except ImportError:  # Python 2 guard — nunca pasará pero por si acaso
    from urllib import quote_plus  # type: ignore

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _PYDANTIC_V2 = True
except ImportError:
    _PYDANTIC_V2 = False

    class BaseSettings(object):  # type: ignore
        def __init__(self, **kwargs):
            env_files = kwargs.pop("__env_files__", ())
            for f in env_files:
                p = Path(f)
                if p.exists():
                    try:
                        for line in p.read_text(encoding="utf-8").splitlines():
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip().upper(), v.strip().strip('"').strip("'"))
                    except Exception:
                        pass
            for key in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
                        "DATABASE_URL", "POSTGRES_URL", "APP_ENV", "APP_SECRET_KEY",
                        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
                        "CORS_ORIGINS"):
                if key in os.environ and key.lower() not in kwargs:
                    kwargs[key.lower()] = os.environ[key]
            for k, v in kwargs.items():
                setattr(self, k, v)

    class SettingsConfigDict(dict):  # type: ignore
        pass


BASE_DIR = Path(__file__).resolve().parent.parent


if _PYDANTIC_V2:
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=(str(BASE_DIR.parent / ".env"), str(BASE_DIR.parent / ".env.example")),
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

        db_host: str = "localhost"
        db_port: int = 5432
        db_name: str = "ciiu_inec"
        db_user: str = "postgres"
        db_password: str = ""

        database_url: Optional[str] = None
        postgres_url: Optional[str] = None

        app_env: str = "development"
        app_secret_key: str = "dev-secret-key-change-me"

        openai_api_key: Optional[str] = None
        anthropic_api_key: Optional[str] = None
        gemini_api_key: Optional[str] = None

        cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

        @property
        def sqlalchemy_database_uri(self):
            # type: () -> str
            candidate = self.database_url or self.postgres_url
            if candidate:
                if candidate.startswith("postgres://"):
                    return "postgresql://" + candidate[len("postgres://"):]
                return candidate
            # URL-encodeamos user/pass por si tienen caracteres especiales
            # (ej: "@", ":", "/", etc. romperían la URI si no se escapan)
            u = quote_plus(str(self.db_user or ""))
            p = quote_plus(str(self.db_password or ""))
            return "postgresql://%s:%s@%s:%d/%s" % (
                u, p, self.db_host, int(self.db_port), self.db_name,
            )
else:
    class Settings(BaseSettings):  # type: ignore
        def __init__(self, **kwargs):
            env_files = (
                str(BASE_DIR.parent / ".env"),
                str(BASE_DIR.parent / ".env.example"),
            )
            kwargs["__env_files__"] = env_files
            super(Settings, self).__init__(**kwargs)
            self.db_host = getattr(self, "db_host", os.environ.get("DB_HOST", "localhost"))
            self.db_port = int(getattr(self, "db_port", os.environ.get("DB_PORT", "5432")))
            self.db_name = getattr(self, "db_name", os.environ.get("DB_NAME", "ciiu_inec"))
            self.db_user = getattr(self, "db_user", os.environ.get("DB_USER", "postgres"))
            self.db_password = getattr(self, "db_password", os.environ.get("DB_PASSWORD", ""))
            self.database_url = getattr(self, "database_url", os.environ.get("DATABASE_URL"))
            self.postgres_url = getattr(self, "postgres_url", os.environ.get("POSTGRES_URL"))
            self.app_env = getattr(self, "app_env", os.environ.get("APP_ENV", "development"))
            self.app_secret_key = getattr(
                self, "app_secret_key",
                os.environ.get("APP_SECRET_KEY", "dev-secret-key-change-me"),
            )
            self.openai_api_key = getattr(self, "openai_api_key", os.environ.get("OPENAI_API_KEY"))
            self.anthropic_api_key = getattr(self, "anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY"))
            self.gemini_api_key = getattr(self, "gemini_api_key", os.environ.get("GEMINI_API_KEY"))
            raw_cors = os.environ.get("CORS_ORIGINS")
            if raw_cors:
                try:
                    self.cors_origins = [s.strip() for s in raw_cors.split(",") if s.strip()]
                except Exception:
                    self.cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
            else:
                self.cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

        @property
        def sqlalchemy_database_uri(self):
            candidate = self.database_url or self.postgres_url
            if candidate:
                if candidate.startswith("postgres://"):
                    return "postgresql://" + candidate[len("postgres://"):]
                return candidate
            u = quote_plus(str(self.db_user or ""))
            p = quote_plus(str(self.db_password or ""))
            return "postgresql://%s:%s@%s:%d/%s" % (
                u, p, self.db_host, int(self.db_port), self.db_name,
            )


@lru_cache(maxsize=1)
def get_settings():
    # type: () -> Settings
    return Settings()
