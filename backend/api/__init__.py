from fastapi import APIRouter
from backend.api import health, automl, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(automl.router, prefix="/api", tags=["automl"])
api_router.include_router(ui.router, tags=["ui"])
