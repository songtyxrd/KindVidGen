import tempfile

from loguru import logger

from kvidgen.core.pipline import (
    VideoGenerationPipeline,
    TextGenerationStep,
    TTSSynthesisStep,
    AudioProcessingStep,
    VideoGenerationStep,
    VideoAudioMergeStep,
    UploadStep,
)
from kvidgen.schemas.fundraising import FundraisingRequest


async def generate_video(param: FundraisingRequest) -> str:
    """
    生成筹款视频

    :param param: 筹款请求参数
    :return: 视频路径
    """
    logger.info(f"Start generating video for {param.patient_info.patient_name}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.info(f"Created temporary directory: {tmp_dir}")

        pipeline = VideoGenerationPipeline(
            [
                TextGenerationStep(),
                TTSSynthesisStep(),
                AudioProcessingStep(),
                VideoGenerationStep(),
                VideoAudioMergeStep(),
                UploadStep(),
            ]
        )

        result = await pipeline.run(
            {
                "tmp_dir": tmp_dir,
                "fundraiser_info": param.patient_info.get_fundraiser_info(),
                "patient_info": param.patient_info.get_patient_info(),
                "story": param.fundraising_text,
                "background_music_url": param.background_music_url,
                "image_urls": param.image_urls,
                "patient_name": param.patient_info.patient_name,
            }
        )

        logger.info(f"Finished generating video for {param.patient_info.patient_name}")
        return result["video_url"]
