from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    application: str
    version: str


class ApiKeyValidationResponse(BaseModel):
    valid: bool = True
    consumerId: str
