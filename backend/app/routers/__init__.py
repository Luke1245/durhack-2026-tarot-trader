from fastapi import APIRouter

from .health import router as health_router
from .readings import router as readings_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(readings_router)
