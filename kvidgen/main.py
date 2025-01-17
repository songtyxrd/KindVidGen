import uvicorn
from fastapi import FastAPI

from kvidgen.api.api_routers import api_router
from kvidgen.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    dependencies=[],
    version=f"{settings.VERSION}",
)
app.include_router(api_router, prefix=settings.API_PREFIX)


def main():
    """主函数入口"""
    uvicorn.run(
        "kvidgen.main:app",
        host=settings.SERVER_NAME,
        port=settings.SERVER_PORT,
        workers=settings.WORKERS,
    )
