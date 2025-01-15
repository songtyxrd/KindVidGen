from fastapi import APIRouter

from kvidgen.models.http import HttpResponse
from kvidgen.schemas.fundraising import FundraisingRequest
from kvidgen.service.video import generate_video

router = APIRouter()


@router.post(
    "/generate",
    response_model=HttpResponse,
    description="生成筹款视频",
    name="generate",
)
async def generate(param: FundraisingRequest):
    video: str = await generate_video(param)
    return HttpResponse.ok(video)
