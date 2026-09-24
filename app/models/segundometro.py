from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SegundometroRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"id_credito": "string"}},
    )

    id_credito: str = Field(
        min_length=1,
        max_length=20,
        pattern=r".*\S.*",
        strict=True,
        description="Valor literal de Id_credito (VARCHAR(20))",
    )


class SegundometroMeta(BaseModel):
    code: Literal[200] = 200
    success: Literal[True] = True
    idCredito: str = Field(description="ID de crédito consultado, VARCHAR(20)")
    totalRegistros: int = Field(ge=1)


class SegundometroRecord(BaseModel):
    datosCliente: dict[str, Any] = Field(description="Identificadores, datos personales, domicilio, sucursal y referencia STP")
    estatus: dict[str, Any] = Field(description="Estado del crédito, fechas, mora, buckets y seguimiento")
    saldos: dict[str, Any] = Field(description="Montos, cuotas, pagos y saldos")
    otros: dict[str, Any] | None = Field(default=None, description="Columnas nuevas sin clasificación conocida")


class SegundometroResponse(BaseModel):
    meta: SegundometroMeta
    data: list[SegundometroRecord] = Field(description="Filas agrupadas con los nombres originales de columnas de MySQL")
