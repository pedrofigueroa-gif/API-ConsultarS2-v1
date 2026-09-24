from unittest.mock import patch

from app.core.config import Settings
from app.db.segundometro import MySqlSegundometroRepository


class Cursor:
    def __init__(self):
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchall(self):
        return [{"Id_credito": "0007"}]


class Connection:
    def __init__(self):
        self.cursor_instance = Cursor()
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def close(self):
        self.closed = True


def test_sql_parametrizado_y_conexion_cerrada():
    connection = Connection()
    settings = Settings(s2_db_host="localhost", s2_db_user="reader")
    with patch("app.db.segundometro.pymysql.connect", return_value=connection):
        rows = MySqlSegundometroRepository(settings)._get_by_credit_sync("0007")
    assert rows == [{"Id_credito": "0007"}]
    assert "WHERE `Id_credito` = %s" in connection.cursor_instance.query
    assert connection.cursor_instance.params == ("0007",)
    assert connection.closed
