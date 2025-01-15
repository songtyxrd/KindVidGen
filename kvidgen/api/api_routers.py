from fastapi import APIRouter

from kvidgen.api.endpoints import management, video

api_router = APIRouter()
api_router.include_router(
    management.router,
    prefix="/management",
    tags=["management"],
)

api_router.include_router(
    video.router,
    prefix="/video",
    tags=["video"],
)
