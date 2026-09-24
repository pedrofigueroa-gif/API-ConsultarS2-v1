from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.problems import DatabaseUnavailable
from app.factory import create_app


class FakeRepository:
    def __init__(self, rows):
        self.rows = rows
        self.received = None

    async def get_by_credit(self, id_credito: str):
        self.received = id_credito
        if isinstance(self.rows, Exception):
            raise self.rows
        return self.rows


def client_for(rows):
    repository = FakeRepository(rows)
    app = create_app(Settings(api_keys=(("local", "secret"),)), repository)
    return TestClient(app), repository


def test_consulta_preserva_id_y_decimales():
    client, repository = client_for([{"Id_credito": "00123", "Nombre_cliente": "Ejemplo", "Status_credito": "Vencido", "Dias_mora": 12, "Bucket_Morosidad": "B2", "Cuota": Decimal("123.45"), "Saldo_vencido_inicio": None}])
    response = client.post("/api/v1/segundometro/creditos", json={"id_credito": "00123"}, headers={"X-API-Key": "secret"})
    assert response.status_code == 200
    assert response.json() == {
        "meta": {"code": 200, "success": True, "idCredito": "00123", "totalRegistros": 1},
        "data": [{
            "datosCliente": {"Id_credito": "00123", "Nombre_cliente": "Ejemplo"},
            "estatus": {"Status_credito": "Vencido", "Dias_mora": 12, "Bucket_Morosidad": "B2"},
            "saldos": {"Cuota": "123.45", "Saldo_vencido_inicio": None},
        }],
    }
    assert repository.received == "00123"
    assert response.headers["X-Request-ID"]


def test_sin_registros_devuelve_404():
    client, _ = client_for([])
    response = client.post("/api/v1/segundometro/creditos", json={"id_credito": "00123"}, headers={"X-API-Key": "secret"})
    assert response.status_code == 404
    assert response.json()["code"] == "CREDIT_NOT_FOUND"


def test_llave_y_validacion_de_string():
    client, repository = client_for([])
    url = "/api/v1/segundometro/creditos"
    assert client.post(url, json={"id_credito": "00123"}).status_code == 401
    for payload in ({"id_credito": 1008}, {"id_credito": "x" * 21}, {"id_credito": "   "}, {}):
        assert client.post(url, json=payload, headers={"X-API-Key": "secret"}).status_code == 422
    assert repository.received is None


def test_error_de_base_no_expone_detalles():
    client, _ = client_for(DatabaseUnavailable())
    response = client.post("/api/v1/segundometro/creditos", json={"id_credito": "00123"}, headers={"X-API-Key": "secret"})
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "DATABASE_UNAVAILABLE"


def test_columna_nueva_no_se_pierde():
    client, _ = client_for([{"Id_credito": "1008", "Campo_nuevo": "valor"}])
    response = client.post("/api/v1/segundometro/creditos", json={"id_credito": "1008"}, headers={"X-API-Key": "secret"})
    assert response.json()["data"][0]["otros"] == {"Campo_nuevo": "valor"}


def test_omite_solo_mora_horaria_y_cierre_semana():
    client, _ = client_for([{
        "Id_credito": "1008",
        "Dias_mora": 1221,
        "Dias_mora_Lunes_07_30": None,
        "Dias_mora_Martes_09_30": 1219,
        "Dias_mora_Domingo_23_50": None,
        "Dias_mora_cierre_semana": None,
        "Dias_mora_cierre": 1220,
        "Bucket_Morosidad": "B1",
    }])
    response = client.post("/api/v1/segundometro/creditos", json={"id_credito": "1008"}, headers={"X-API-Key": "secret"})
    assert response.status_code == 200
    assert response.json()["data"][0]["estatus"] == {
        "Dias_mora": 1221,
        "Dias_mora_cierre": 1220,
        "Bucket_Morosidad": "B1",
    }
