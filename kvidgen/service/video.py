import os
import tempfile

from kvidgen.core.audio.audio_mixer import FfmpegAudioMixer
from kvidgen.core.audio.audio_video import FfmpegAudioVideoMerger
from kvidgen.core.video.video_generator import SlideshowVideoGenerator
from kvidgen.schemas.fundraising import FundraisingRequest
from loguru import logger

from kvidgen.utils.oss_client import AliyunOssClient
from kvidgen.utils.tts_client import TTSClient


async def generate_video(param: FundraisingRequest) -> str:
    logger.info(f"start generate video {param.patient_info.patient_name}")
    with tempfile.TemporaryDirectory() as tmp_dir:
        # todo use multi agent generate fundraising_text by SongTianYe
        tts: TTSClient = TTSClient()
        logger.info(f"create tmp dir: {tmp_dir}")
        # generate tts audio
        tts_filepath = await tts.synthesize(
            param.fundraising_text, os.path.join(tmp_dir, "tts.mp3")
        )
        # mix background music
        mix_filepath = FfmpegAudioMixer().mix_audio(
            tts_filepath,
            "/Users/songtianye/workspace/python/github/myself/KindVidGen/kvidgen/service/background_music/default.mp3",
            os.path.join(tmp_dir, "mix.m4a"),
        )
        # generate slideshow video
        # todo vl model choose effect by SongTianYe
        # todo download images from oss
        # demo
        images = [
            "/Users/songtianye/Documents/视频生成图片素材/1.jpeg",
            "/Users/songtianye/Documents/视频生成图片素材/2.jpeg",
            "/Users/songtianye/Documents/视频生成图片素材/3.jpeg",
            "/Users/songtianye/Documents/视频生成图片素材/4.jpeg",
            "/Users/songtianye/Documents/视频生成图片素材/5.jpeg",
        ]
        slideshow_video = SlideshowVideoGenerator(
            images=images,
            output_path=os.path.join(tmp_dir, "slideshow.mp4"),
            total_duration=30,
        ).create_video()
        # merge audio and video
        result_path = FfmpegAudioVideoMerger().merge(
            slideshow_video, mix_filepath, os.path.join(tmp_dir, "result.mp4")
        )

        logger.info(f"finish generate video {param.patient_info.patient_name}")

        # upload to oss
        oss_client = AliyunOssClient()
        object_key = f"tmp/video/{param.patient_info.patient_name}.mp4"
        await oss_client.upload_file(result_path, object_key)

        return await oss_client.generate_signed_url(object_key=object_key)
