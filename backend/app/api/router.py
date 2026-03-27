# Central API router — aggregates all v1 endpoint routers.
from fastapi import APIRouter

from app.api.v1.analysis import router as analysis_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.platforms import router as platforms_router
from app.api.v1.skills import router as skills_router

api_router = APIRouter()
api_router.include_router(jobs_router)
api_router.include_router(platforms_router)
api_router.include_router(skills_router)
api_router.include_router(analysis_router)
