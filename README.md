# API Consultar S2 v1

Servicio FastAPI de solo lectura para consultar `db-mega-reporte.tbl_segundometro_semana` mediante `Id_credito` (`VARCHAR(20)`). Sigue la organización `app/api`, `app/core`, `app/db` y `app/models` de las APIs de Originación y Selección de Oferta. No incluye modo auditoría ni escrituras en la base.

## Preparación en PowerShell

```powershell
cd C:\xampp\htdocs\api-ConsultarS2-v1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Configure `.env` con `S2_DB_HOST`, `S2_DB_USER`, `S2_DB_PASSWORD` y `API_KEYS=consumidor:secreto`. El valor por defecto de `S2_DB_NAME` es `db-mega-reporte`; `S2_DB_SSL_CA` permite verificar TLS y es obligatorio fuera de entornos `local`, `test` y `development`. La cuenta MySQL solo necesita permiso `SELECT` sobre la tabla.

```powershell
python main.py
```

También se puede ejecutar sin activar el entorno: `.\.venv\Scripts\python.exe main.py`.

## Endpoints

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/api/v1/health` | Estado de la aplicación, sin consultar MySQL. |
| GET | `/api/v1/auth/validar` | Valida `X-API-Key`. |
| POST | `/api/v1/segundometro/creditos` | Recibe `id_credito` en JSON y devuelve todas las filas y columnas. |

La ruta de negocio requiere `X-API-Key` y un cuerpo JSON con `id_credito` como string de 1 a 20 caracteres no vacío. Conserva ceros iniciales y otros caracteres válidos de `VARCHAR(20)`. La igualdad sigue el cotejamiento configurado en MySQL. El parámetro de la consulta SQL está enlazado, no interpolado.

Ejemplo:

```powershell
curl.exe -X POST "http://127.0.0.1:8083/api/v1/segundometro/creditos" -H "X-API-Key: secreto" -H "Content-Type: application/json" -d '{"id_credito":"001234"}'
```

Respuesta `200`:

```json
{
  "meta": {
    "code": 200,
    "success": true,
    "idCredito": "001234",
    "totalRegistros": 1
  },
  "data": [{
    "datosCliente": {"Id_credito": "001234", "Id_cliente": "456", "Nombre_cliente": "Ejemplo", "Sucursal": "Sucursal A", "Referencia_stp": "STP123"},
    "estatus": {"Status_credito": "Vencido", "Dias_mora": 30, "Bucket_Morosidad": "B1"},
    "saldos": {"Cuota": "500.00", "Saldo_vencido_inicio": "1000.00"}
  }]
}
```

La respuesta tiene dos secciones: `meta` reúne el resultado de la operación y el crédito consultado; `data` contiene las filas. Cada fila se agrupa en `datosCliente` (identificación, datos personales, domicilio, sucursal y referencia STP), `estatus` (estado, fechas, días de mora, buckets y seguimiento) y `saldos` (montos, cuotas, abonos y pagos). Se omiten de la respuesta las columnas `Dias_mora_<día>_<hora>` y `Dias_mora_cierre_semana`; las demás conservan sus nombres y valores originales. Las columnas nuevas sin clasificar aparecerán en `otros` dentro de la fila. La tabla del ejemplo contiene `Id_cliente`, no `Id_persona`; la API no inventa ese identificador.

Los valores `DECIMAL` se serializan como texto para no perder precisión. Sin registros se devuelve `404`; entrada inválida `422`; API key ausente o incorrecta `401`; conexión o consulta fallida `503`. Los errores usan `application/problem+json` e incluyen `traceId`, que también aparece en `X-Request-ID`.

Swagger: `http://127.0.0.1:8083/docs`.

## Pruebas

```powershell
python -m pytest -q
```

Las pruebas HTTP y de SQL usan dobles locales. La conexión real a `db-mega-reporte` se comprueba al configurar credenciales y ejecutar el endpoint en el entorno de destino.

## Cloud Run

El proyecto incluye `Dockerfile` y `.dockerignore`. Las variables, secretos y requisitos de red están en [docs/CLOUD_RUN.md](docs/CLOUD_RUN.md). El archivo `.env` local queda fuera del repositorio y de la imagen.
