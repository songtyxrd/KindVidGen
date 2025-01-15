import subprocess
import os
import tempfile
from typing import List


class AudioConcatenator:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize the AudioConcatenator class.

        :param ffmpeg_path: Path to the ffmpeg executable. Default is "ffmpeg".
        """
        self.ffmpeg_path = ffmpeg_path

    def concatenate_audio(
        self, audio_files: List[str], output_path: str = "output_audio.mp3"
    ) -> str:
        """
        Concatenate multiple audio files into one.

        :param audio_files: List of paths to audio files to be concatenated.
        :param output_path: Path to save the concatenated audio file.
        :return: Path to the concatenated audio file.
        """
        if not audio_files or len(audio_files) < 2:
            return audio_files[0]

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Use a temporary file for the list of audio files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_list = os.path.join(temp_dir, "file_list.txt")
            with open(temp_file_list, "w") as file_list:
                for audio in audio_files:
                    file_list.write(f"file '{audio}'\n")

            try:
                # Run the ffmpeg command to concatenate audio files
                command = [
                    self.ffmpeg_path,
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    temp_file_list,
                    "-c",
                    "copy",
                    output_path,
                ]
                subprocess.run(command, check=True)

            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error during audio concatenation: {e}")

        return output_path
