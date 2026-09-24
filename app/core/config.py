from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} debe ser true o false")


def _read_int(name: str, default: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} debe ser un entero") from exc
    if not 1 <= value <= maximum:
        raise ValueError(f"{name} debe estar entre 1 y {maximum}")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "api-ConsultarS2-v1"
    app_description: str = "Consulta de segundo metro semanal por ID de crédito"
    app_version: str = "1.0.0"
    environment: str = "local"
    host: str = "127.0.0.1"
    port: int = 8083
    reload: bool = True
    docs_enabled: bool = True
    api_keys: tuple[tuple[str, str], ...] = ()
    s2_db_host: str = ""
    s2_db_port: int = 3306
    s2_db_name: str = "db-mega-reporte"
    s2_db_user: str = ""
    s2_db_password: str = ""
    s2_db_connect_timeout_seconds: int = 5
    s2_db_ssl_ca: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        environment = os.getenv("ENVIRONMENT", "local").strip().lower() or "local"
        database = os.getenv("S2_DB_NAME", "db-mega-reporte").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", database):
            raise ValueError("S2_DB_NAME contiene caracteres no permitidos")
        keys = []
        for item in os.getenv("API_KEYS", "").split(","):
            item = item.strip()
            if not item:
                continue
            consumer, separator, secret = item.partition(":")
            if not separator or not consumer or not secret:
                raise ValueError("API_KEYS debe usar consumer_id:secret")
            keys.append((consumer, secret))
        return cls(
            app_name=os.getenv("APP_NAME", "api-ConsultarS2-v1").strip() or "api-ConsultarS2-v1",
            app_description=os.getenv("APP_DESCRIPTION", "Consulta de segundo metro semanal por ID de crédito").strip() or "Consulta de segundo metro semanal por ID de crédito",
            app_version=os.getenv("APP_VERSION", "1.0.0").strip() or "1.0.0",
            environment=environment,
            host=os.getenv("HOST", "127.0.0.1").strip() or "127.0.0.1",
            port=_read_int("PORT", 8083, 65535),
            reload=_read_bool("APP_RELOAD", environment == "local"),
            docs_enabled=_read_bool("DOCS_ENABLED", True),
            api_keys=tuple(keys),
            s2_db_host=os.getenv("S2_DB_HOST", "").strip(),
            s2_db_port=_read_int("S2_DB_PORT", 3306, 65535),
            s2_db_name=database,
            s2_db_user=os.getenv("S2_DB_USER", "").strip(),
            s2_db_password=os.getenv("S2_DB_PASSWORD", ""),
            s2_db_connect_timeout_seconds=_read_int("S2_DB_CONNECT_TIMEOUT_SECONDS", 5, 120),
            s2_db_ssl_ca=os.getenv("S2_DB_SSL_CA", "").strip() or None,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
