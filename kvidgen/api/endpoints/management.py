from fastapi import APIRouter
from loguru import logger

from kvidgen.models.http import HttpResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HttpResponse,
    name="health",
)
async def get_health():
    logger.info("health check")
    return HttpResponse.ok([])
