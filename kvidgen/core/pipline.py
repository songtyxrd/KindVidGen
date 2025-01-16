import asyncio
import math
from typing import Any
import os
from abc import ABC, abstractmethod

from loguru import logger

from kvidgen.core.agents.editor import Editor, ImageEffectsArtist
from kvidgen.core.audio.audio_concat import AudioConcatenator
from kvidgen.core.audio.audio_mixer import FfmpegAudioMixer
from kvidgen.core.audio.audio_video import FfmpegAudioVideoMerger
from kvidgen.core.video.video_generator import SlideshowVideoGenerator
from kvidgen.utils.common import split_text, get_audio_duration, file_to_base64
from kvidgen.utils.download import download_file, download_image_file
from kvidgen.utils.oss_client import AliyunOssClient
from kvidgen.utils.tts_client import TTSClient


class PipelineStep(ABC):
    """
    抽象管道步骤
    """

    @abstractmethod
    async def process(self, data: Any) -> Any:
        pass


class TextGenerationStep(PipelineStep):
    async def process(self, data: Any) -> Any:
        logger.info(f"Generating fundraising text for {data['patient_name']}")
        text = await Editor().run(
            {
                "fundraiser_info": data["fundraiser_info"],
                "patient_info": data["patient_info"],
                "story": data["story"],
            }
        )
        data["generated_text"] = text
        logger.info(f"Generated text: {text}")
        return data


class TTSSynthesisStep(PipelineStep):
    async def process(self, data: Any) -> Any:
        logger.info("Synthesizing audio from text")
        tts = TTSClient()
        tts_chunks = [
            await tts.synthesize(chunk, os.path.join(data["tmp_dir"], f"tts{i}.mp3"))
            for i, chunk in enumerate(split_text(data["generated_text"]))
        ]
        data["tts_chunks"] = tts_chunks
        return data


class AudioProcessingStep(PipelineStep):
    async def process(self, data: Any) -> Any:
        logger.info("Concatenating and mixing audio")
        tts_concat = AudioConcatenator().concatenate_audio(
            data["tts_chunks"], os.path.join(data["tmp_dir"], "tts_concat.mp3")
        )
        mix_filepath = FfmpegAudioMixer().mix_audio(
            tts_concat,
            await download_file(
                data["background_music_url"], data["tmp_dir"], "background_music.mp3"
            ),
            os.path.join(data["tmp_dir"], "mix.m4a"),
        )
        data["mixed_audio"] = mix_filepath
        return data


class VideoGenerationStep(PipelineStep):
    async def process(self, data: Any) -> Any:
        logger.info("Generating slideshow video")
        images = await download_image_file(data["tmp_dir"], data["image_urls"])
        tasks = [ImageEffectsArtist().run(file_to_base64(image)) for image in images]
        results = await asyncio.gather(*tasks)
        effect_config = {
            images[index]: result[0] for index, result in enumerate(results)
        }
        logger.debug(f"images Effect end, effect_config: {effect_config}")
        slideshow_video = SlideshowVideoGenerator(
            images=images,
            output_path=os.path.join(data["tmp_dir"], "slideshow.mp4"),
            total_duration=math.floor(get_audio_duration(data["mixed_audio"])) + 1,
            effect_config=effect_config,
        ).create_video()
        data["slideshow_video"] = slideshow_video
        return data


class VideoAudioMergeStep(PipelineStep):
    async def process(self, data: Any) -> Any:
        logger.info("Merging audio and video")
        result_path = FfmpegAudioVideoMerger().merge(
            data["slideshow_video"],
            data["mixed_audio"],
            os.path.join(data["tmp_dir"], "result.mp4"),
        )
        data["result_video"] = result_path
        return data


class UploadStep(PipelineStep):
    async def process(self, data: Any) -> Any:
        logger.info("Uploading video to OSS")
        oss_client = AliyunOssClient()
        object_key = f"tmp/video/{data['patient_name']}.mp4"
        await oss_client.upload_file(data["result_video"], object_key)
        data["video_url"] = await oss_client.generate_signed_url(object_key=object_key)
        return data


class VideoGenerationPipeline:
    def __init__(self, steps):
        self.steps = steps

    async def run(self, initial_data: Any) -> Any:
        data = initial_data
        for step in self.steps:
            data = await step.process(data)
        return data
