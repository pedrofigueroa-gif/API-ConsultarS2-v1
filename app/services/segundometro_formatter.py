"""Agrupa las columnas de segundo metro sin alterar nombres ni valores."""

from __future__ import annotations

import re
from typing import Any


HOURLY_DAYS_MORA = re.compile(
    r"^Dias_mora_(?:Lunes|Martes|Miercoles|Jueves|Viernes|Sabado|Domingo)_\d{2}_\d{2}$"
)


CLIENT_FIELDS = frozenset(
    {
        "id_segundometro_histo",
        "KT",
        "Id_credito",
        "Id_cliente",
        "Nombre_cliente",
        "Fecha_nacimiento",
        "Genero",
        "Estado_civil",
        "Celular",
        "Sucursal",
        "Referencia_stp",
        "Codigo_postal_1",
        "Estado_1",
        "Domicilio_Completo",
        "Coordenada_fat",
        "Direccion_maps",
        "Donde_firma",
    }
)

CLIENT_PREFIXES = (
    "Calle_",
    "Num_exterior_",
    "Num_interior_",
    "Cp_adicional_",
    "Colonia_",
    "Estado_adicional_",
    "Ciudad_",
    "Municipio_",
    "Codigo_postal_",
    "Direccion",
    "D_",
    "Adicionales_colonia",
    "Entidad_",
)

BALANCE_FIELDS = frozenset(
    {
        "Saldo_vencido_inicio",
        "Numero_amortizaciones",
        "Monto_otorgado",
        "Cuota",
        "Num_cuotas_pagadas",
        "Saldo_total_capital",
        "Saldo_para_liquidar_hoy",
        "Abonos_total",
        "Abonos_numero",
        "Monto_otorgado_2",
        "Rango_Monto",
        "pago_acreditado",
        "Dia_pago_moda",
        "Saldo_total_capital_cierre",
        "Saldo_vencido_actualizado",
        "Fecha_ultimo_pago_efectivo",
        "Cuotas_vencidas",
        "Cuotas_devengadas",
        "Monto_abono_efectivo",
    }
)

STATUS_FIELDS = frozenset(
    {
        "Status_credito",
        "Fecha_inicio",
        "Fecha_primer_vencimiento",
        "Fecha_ultimo_vencimiento",
        "Avance_Pago_Plazo",
        "Gestor_Asignado",
        "Jefe_de_Plaza",
        "Zonal",
        "Territorial",
        "Observaciones",
        "Cierre_Actual",
        "Ajuste",
        "Ghost",
        "Tipo_de_contacto",
        "Medio_de_contacto",
        "Gestiones",
        "Ultimo_Dictamen",
        "Promesas_Totales",
        "Promesas_cumplidas",
        "Promesa_Vigente",
        "Promesa_Rota",
        "Dia_de_la_prom",
        "Promesa_de_pago",
        "SEMANA",
        "fecha_hora_insert",
        "reporte_lock",
    }
)

STATUS_PREFIXES = (
    "Dias_mora",
    "Bucket_",
    "bucket_",
    "Delincuencia_",
    "delincuencia_",
    "dias_moda_",
    "Variable_",
)


def group_record(row: dict[str, Any]) -> dict[str, Any]:
    """Agrupa columnas y omite las mediciones horarias de mora solicitadas."""

    groups: dict[str, dict[str, Any]] = {
        "datosCliente": {},
        "estatus": {},
        "saldos": {},
    }
    for column, value in row.items():
        if column == "Dias_mora_cierre_semana" or HOURLY_DAYS_MORA.fullmatch(column):
            continue
        if column in CLIENT_FIELDS or column.startswith(CLIENT_PREFIXES):
            groups["datosCliente"][column] = value
        elif column in BALANCE_FIELDS or column.startswith("fecha_ultimo_abono_efectivo_"):
            groups["saldos"][column] = value
        elif column in STATUS_FIELDS or column.startswith(STATUS_PREFIXES):
            groups["estatus"][column] = value
        else:
            groups.setdefault("otros", {})[column] = value
    return groups
