from dataclasses import dataclass, field


@dataclass(slots=True)
class ApiProblem(Exception):
    status_code: int
    code: str
    title: str
    detail: str
    errors: list[dict[str, str]] = field(default_factory=list)


class Unauthorized(ApiProblem):
    def __init__(self) -> None:
        super().__init__(401, "UNAUTHORIZED", "No autorizado", "La API key no es válida o no fue proporcionada.")


class CreditNotFound(ApiProblem):
    def __init__(self) -> None:
        super().__init__(404, "CREDIT_NOT_FOUND", "Crédito no encontrado", "No hay registros para el id_credito solicitado.")


class DatabaseUnavailable(ApiProblem):
    def __init__(self) -> None:
        super().__init__(503, "DATABASE_UNAVAILABLE", "Base de datos no disponible", "No fue posible consultar db-mega-reporte.tbl_segundometro_semana.")
