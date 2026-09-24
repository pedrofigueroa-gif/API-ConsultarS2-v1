from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.problems import CreditNotFound
from app.core.security import require_api_key
from app.models.segundometro import SegundometroMeta, SegundometroRequest, SegundometroResponse
from app.services.segundometro_formatter import group_record


router = APIRouter(prefix="/api/v1/segundometro", tags=["Segundo metro"])


@router.post(
    "/creditos",
    response_model=SegundometroResponse,
    summary="Consultar segundo metro semanal por ID de crédito",
    description="Recibe id_credito como string en el cuerpo y devuelve todas las filas de tbl_segundometro_semana.",
    responses={401: {"description": "API key inválida"}, 404: {"description": "Crédito sin registros"}, 422: {"description": "ID de crédito inválido"}, 503: {"description": "Base de datos no disponible"}},
    dependencies=[Depends(require_api_key)],
)
async def consultar_credito(
    request: Request,
    payload: Annotated[
        SegundometroRequest,
        Body(
            openapi_examples={
                "default": {
                    "summary": "Consulta por ID de crédito",
                    "value": {"id_credito": "string"},
                }
            }
        ),
    ],
) -> JSONResponse:
    rows = await request.app.state.segundometro_repository.get_by_credit(payload.id_credito)
    if not rows:
        raise CreditNotFound()
    result = SegundometroResponse(
        meta=SegundometroMeta(idCredito=payload.id_credito, totalRegistros=len(rows)),
        data=[group_record(row) for row in rows],
    )
    content = jsonable_encoder(
        result,
        custom_encoder={Decimal: str, date: lambda value: value.isoformat(), datetime: lambda value: value.isoformat()},
    )
    for record in content["data"]:
        if record["otros"] is None:
            del record["otros"]
    return JSONResponse(content=content)
