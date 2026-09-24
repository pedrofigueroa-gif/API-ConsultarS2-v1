from fastapi import APIRouter

from app.api.routes.segundometro import router as segundometro_router
from app.api.routes.system import router as system_router


router = APIRouter()
router.include_router(system_router)
router.include_router(segundometro_router)
