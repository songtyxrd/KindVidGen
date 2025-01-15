from typing import Optional, TypeVar, Generic

from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import JSONResponse

T = TypeVar("T")


class HttpResponse(BaseModel, Generic[T]):
    code: int
    message: Optional[str]
    data: Optional[T]
    metadata: Optional[dict] = Field(default=None, exclude=True)

    @staticmethod
    def ok(data: T):
        return HttpResponse(code=status.HTTP_200_OK, message="ok", data=data)

    @staticmethod
    def err(
        http_status_code: int,
        business_code: int,
        message: Optional[str] = None,
        detail: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ):
        return JSONResponse(
            status_code=http_status_code,
            content=HttpResponse(
                code=business_code, message=message, detail=detail, metadata=metadata
            ).__dict__,
        )
