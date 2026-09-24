# Configuración de Cloud Run

La imagen del `Dockerfile` escucha en `0.0.0.0` y usa el `PORT` que Cloud Run entrega al contenedor. Tiene `ENVIRONMENT=production` y `APP_RELOAD=false`. No se debe subir ni copiar `.env` al contenedor.

## Variables del servicio

| Variable | Valor o fuente | Uso |
| --- | --- | --- |
| `S2_DB_HOST` | Hostname o IP de MySQL | Necesaria para consultar `db-mega-reporte`. |
| `S2_DB_PORT` | `3306`, salvo que MySQL use otro puerto | Puerto TCP. |
| `S2_DB_NAME` | `db-mega-reporte` | Nombre de la base. |
| `S2_DB_USER` | Usuario MySQL con permiso `SELECT` | Credencial; preferir Secret Manager. |
| `S2_DB_PASSWORD` | Contraseña del usuario MySQL | Secreto de Secret Manager. |
| `S2_DB_SSL_CA` | Ruta absoluta del certificado CA montado, por ejemplo `/secrets/mysql/ca.pem` | Obligatoria cuando `ENVIRONMENT=production`. La CA debe estar montada como archivo. |
| `API_KEYS` | Pares `consumer_id:secret`, separados por comas | Autentica el header `X-API-Key`. Guardar el valor en Secret Manager. |

`APP_NAME`, `APP_DESCRIPTION` y `APP_VERSION` son opcionales. `S2_DB_CONNECT_TIMEOUT_SECONDS` usa `5` por defecto; `DOCS_ENABLED` usa `true` y puede cambiarse a `false`. `HOST`, `APP_RELOAD` y `ENVIRONMENT` ya tienen valores adecuados en la imagen. Cloud Run inyecta `PORT`; no hace falta fijarlo manualmente.

La cuenta MySQL debe poder llegar a `S2_DB_HOST:S2_DB_PORT` desde Cloud Run. Si la base usa una dirección privada, el administrador debe configurar salida a la VPC y las reglas de red necesarias. Esta aplicación usa conexión TCP a MySQL; no tiene configurado un socket Unix de Cloud SQL.

El servicio responde `GET /api/v1/health` sin consultar MySQL. La verificación real de base se hace con `POST /api/v1/segundometro/creditos` y un cuerpo como `{"id_credito":"1008"}`, enviando `X-API-Key`.

Documentación oficial: [variables y puerto de Cloud Run](https://docs.cloud.google.com/run/docs/configuring), [secretos como variables o archivos](https://docs.cloud.google.com/run/docs/configuring/services/secrets), [conexión a VPC](https://docs.cloud.google.com/run/docs/configuring/vpc-connectors).
