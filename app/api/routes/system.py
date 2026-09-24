from fastapi import APIRouter, Depends, Request

from app.core.security import require_api_key
from app.models.system import ApiKeyValidationResponse, HealthResponse


router = APIRouter(prefix="/api/v1", tags=["Sistema"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(application=settings.app_name, version=settings.app_version)


@router.get("/auth/validar", response_model=ApiKeyValidationResponse)
async def validar_api_key(consumer_id: str = Depends(require_api_key)) -> ApiKeyValidationResponse:
    return ApiKeyValidationResponse(consumerId=consumer_id)
