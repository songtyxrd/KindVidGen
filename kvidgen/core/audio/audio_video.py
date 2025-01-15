import subprocess

from loguru import logger


class FfmpegAudioVideoMerger:
    """
    使用 Ffmpeg 合成视频和音频。
    """

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化合成器。
        :param ffmpeg_path: Ffmpeg 可执行文件路径，默认使用系统路径中的 ffmpeg。
        """
        self.ffmpeg_path = ffmpeg_path

    def merge(
        self, video_path: str, audio_path: str, output_path: str, volume: float = 1.0
    ) -> str:
        """
        合成音频和视频。
        :param video_path: 输入视频文件路径。
        :param audio_path: 输入音频文件路径。
        :param output_path: 输出视频文件路径。
        :param volume: 背景音乐音量比例，范围 0.0 - 1.0。
        """
        try:
            command = [
                self.ffmpeg_path,
                "-i",
                video_path,
                "-i",
                audio_path,
                "-filter:a",
                f"volume={volume}",
                "-c:v",
                "copy",
                "-shortest",
                output_path,
            ]
            subprocess.run(command, check=True)
            logger.info(f"视频合成成功，已保存到: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"合成失败: {e}")
            return None
        except FileNotFoundError:
            logger.error("ffmpeg 未安装或路径无效，请确保 ffmpeg 已正确配置。")
            return None


if __name__ == "__main__":
    # 示例使用
    video_path = "docs/slideshow.mp4"  # 输入视频文件路径
    audio_path = "docs/mixed_audio.m4a"  # 输入音频文件路径
    output_path = "docs/final_video_2.mp4"  # 输出视频文件路径
    volume = 1  # 背景音乐音量比例

    merger = FfmpegAudioVideoMerger()
    merger.merge(video_path, audio_path, output_path, volume)
