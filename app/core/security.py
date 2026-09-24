import hmac
from typing import Annotated

from fastapi import Request, Security
from fastapi.security import APIKeyHeader

from app.core.problems import Unauthorized


api_key_header = APIKeyHeader(name="X-API-Key", scheme_name="apiKeyAuth", auto_error=False)


async def require_api_key(
    request: Request,
    api_key: Annotated[str | None, Security(api_key_header)] = None,
) -> str:
    if api_key:
        for consumer_id, secret in request.app.state.settings.api_keys:
            if hmac.compare_digest(api_key, secret):
                request.state.consumer_id = consumer_id
                return consumer_id
    raise Unauthorized()
