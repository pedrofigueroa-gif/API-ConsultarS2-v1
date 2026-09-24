from __future__ import annotations

import asyncio
from typing import Any, Protocol

import pymysql
from pymysql.cursors import DictCursor

from app.core.config import Settings
from app.core.problems import DatabaseUnavailable


class SegundometroRepository(Protocol):
    async def get_by_credit(self, id_credito: str) -> list[dict[str, Any]]: ...


class MySqlSegundometroRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_by_credit(self, id_credito: str) -> list[dict[str, Any]]:
        if not self._settings.s2_db_host or not self._settings.s2_db_user:
            raise DatabaseUnavailable()
        return await asyncio.to_thread(self._get_by_credit_sync, id_credito)

    def _get_by_credit_sync(self, id_credito: str) -> list[dict[str, Any]]:
        settings = self._settings
        options: dict[str, Any] = {
            "host": settings.s2_db_host,
            "port": settings.s2_db_port,
            "user": settings.s2_db_user,
            "password": settings.s2_db_password,
            "database": settings.s2_db_name,
            "cursorclass": DictCursor,
            "charset": "utf8mb4",
            "connect_timeout": settings.s2_db_connect_timeout_seconds,
            "read_timeout": settings.s2_db_connect_timeout_seconds,
            "write_timeout": settings.s2_db_connect_timeout_seconds,
            "autocommit": True,
        }
        if settings.s2_db_ssl_ca:
            options["ssl"] = {"ca": settings.s2_db_ssl_ca, "check_hostname": True}
        elif settings.environment not in {"local", "test", "development"}:
            raise DatabaseUnavailable()
        query = (
            f"SELECT * FROM `{settings.s2_db_name}`.`tbl_segundometro_semana` "
            "WHERE `Id_credito` = %s"
        )
        try:
            connection = pymysql.connect(**options)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, (id_credito,))
                    return list(cursor.fetchall())
            finally:
                connection.close()
        except pymysql.MySQLError as exc:
            raise DatabaseUnavailable() from exc
