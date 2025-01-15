import subprocess
from loguru import logger

from kvidgen.utils.tts_client import singleton


@singleton
class FfmpegAudioMixer:
    """
    使用 Ffmpeg 合成多个音频文件。
    """

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化音频混合器。
        :param ffmpeg_path: Ffmpeg 可执行文件路径，默认使用系统环境路径中的 ffmpeg。
        """
        self.ffmpeg_path = ffmpeg_path

    def mix_audio(
        self,
        audio_path1: str,
        audio_path2: str,
        output: str,
        audio_volume1: float = 1.0,
        audio_volume2: float = 0.5,
    ) -> str:
        """
        混合两个音频文件。
        :param audio_path1: 解说音频文件路径。
        :param audio_path2: 背景音乐文件路径。
        :param output: 输出音频文件路径。
        :param audio_volume1: 解说音量比例，范围 0.0 - 1.0。
        :param audio_volume2: 背景音乐音量比例，范围 0.0 - 1.0。
        """
        if not (0.0 <= audio_volume1 <= 1.0) or not (0.0 <= audio_volume2 <= 1.0):
            raise ValueError("音量比例必须在 0.0 到 1.0 之间。")

        command = [
            self.ffmpeg_path,
            "-i",
            audio_path1,
            "-i",
            audio_path2,
            "-filter_complex",
            f"[0:a]volume={audio_volume1}[a1];[1:a]volume={audio_volume2}[a2];[a1][a2]amix=inputs=2:duration=first[aout]",
            # noqa
            "-map",
            "[aout]",
            "-c:a",
            "aac",
            output,
        ]

        try:
            subprocess.run(
                command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            logger.info(f"音频混合成功，已保存到: {output}")
            return output
        except FileNotFoundError:
            logger.error("ffmpeg 未安装或路径无效，请确保 ffmpeg 已正确配置。")
        except subprocess.CalledProcessError as e:
            logger.error(f"混合失败，ffmpeg 错误: {e.stderr.decode()}")
        except Exception as e:
            logger.error(f"混合过程中发生未知错误: {e}")

    def is_ffmpeg_installed(self) -> bool:
        """
        检查 ffmpeg 是否已安装并可用。
        :return: 如果 ffmpeg 可用返回 True，否则返回 False。
        """
        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False


if __name__ == "__main__":
    # 示例使用
    audio1_path = "docs/test_submit.mp3"  # 解说音频文件路径
    audio2_path = "docs/background_music.mp3"  # 背景音乐文件路径
    output_path = "docs/mixed_audio.m4a"  # 输出音频文件路径

    # 设置音量比例
    audio1_volume = 1.0  # 解说音频音量比例
    audio2_volume = 0.3  # 背景音乐音量比例

    mixer = FfmpegAudioMixer()

    if not mixer.is_ffmpeg_installed():
        print("请先安装 ffmpeg 并将其添加到系统路径中。")
    else:
        mixer.mix_audio(
            audio1_path, audio2_path, output_path, audio1_volume, audio2_volume
        )
