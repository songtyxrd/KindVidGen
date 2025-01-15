import cv2
import numpy as np
from typing import List, Tuple, Dict

from loguru import logger

from kvidgen.core.video.effect import EffectRegistry


class SlideshowVideoGenerator:
    def __init__(
        self,
        images: List[str],
        output_path: str,
        frame_size: Tuple[int, int] = None,
        fps: int = 30,
        total_duration: int = 10,
        effect_config: Dict[str, str] = None,
    ):
        """
        初始化图片轮播视频生成器。
        :param images: 图片路径列表。
        :param output_path: 输出视频路径。
        :param frame_size: 视频帧大小 (宽度, 高度)，如果未提供，将根据图片动态调整。
        :param fps: 视频帧率。
        :param total_duration: 视频总时长（秒）。
        :param effect_config: 每张图片对应的特效名称映射。
        """
        self.images = images
        self.output_path = output_path
        self.frame_size = frame_size
        self.fps = fps
        self.total_duration = total_duration
        self.effect_config = effect_config or {}
        self.validate_inputs()
        if self.frame_size is None:
            self.frame_size = self.calculate_dynamic_frame_size()

    def validate_inputs(self):
        """校验输入参数。"""
        if not self.images:
            raise ValueError("图片列表不能为空。")
        if self.total_duration <= 0:
            raise ValueError("总时长必须为正数。")
        if self.fps <= 0:
            raise ValueError("帧率必须为正数。")

    def calculate_dynamic_frame_size(self) -> Tuple[int, int]:
        """
        根据图片的宽高比例动态计算视频帧大小。
        :return: 动态调整的帧大小 (宽度, 高度)
        """
        aspect_ratios = []
        for image_path in self.images:
            img = cv2.imread(image_path)
            if img is not None:
                h, w = img.shape[:2]
                aspect_ratios.append(w / h)

        if not aspect_ratios:
            raise ValueError("无法读取任何图片，无法计算动态帧大小。")

        avg_aspect_ratio = sum(aspect_ratios) / len(aspect_ratios)
        base_height = 1080  # 设定基准高度
        frame_width = int(base_height * avg_aspect_ratio)
        return frame_width, base_height

    def create_video(self):
        """生成图片轮播视频。"""
        num_frames = self.fps * self.total_duration
        frames_per_image = num_frames // len(self.images)

        # 创建视频写入对象
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 使用 mp4v 编码
        video_writer = cv2.VideoWriter(
            self.output_path, fourcc, self.fps, self.frame_size
        )

        for image_path in self.images:
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"警告: 无法读取图片 {image_path}，跳过。")
                continue
            # 调整图片大小以适应动态帧大小
            img_resized = self.resize_with_padding(img, self.frame_size)

            # 应用特效
            effect_name = self.effect_config.get(image_path)
            if effect_name:
                effect = EffectRegistry.get_effect(effect_name)
                for frame_idx in range(frames_per_image):
                    frame = effect.apply(img_resized, frame_idx, frames_per_image)
                    video_writer.write(frame)
            else:
                for _ in range(frames_per_image):
                    video_writer.write(img_resized)

        # 如果图片总帧数不足，补齐最后一张图片
        remaining_frames = num_frames - frames_per_image * len(self.images)
        if remaining_frames > 0 and self.images:
            last_image = cv2.imread(self.images[-1])
            last_image_resized = self.resize_with_padding(last_image, self.frame_size)
            for _ in range(remaining_frames):
                video_writer.write(last_image_resized)

        video_writer.release()
        return self.output_path

    def resize_with_padding(
        self, img: np.ndarray, target_size: Tuple[int, int]
    ) -> np.ndarray:
        """
        调整图片大小并添加填充以适应目标尺寸，保持原始图片比例。
        :param img: 输入图片。
        :param target_size: 目标帧大小 (宽度, 高度)。
        :return: 调整后的图片。
        """
        h, w = img.shape[:2]
        target_w, target_h = target_size

        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized_img = cv2.resize(img, (new_w, new_h))

        # 创建带填充的背景
        top = (target_h - new_h) // 2
        bottom = target_h - new_h - top
        left = (target_w - new_w) // 2
        right = target_w - new_w - left

        return cv2.copyMakeBorder(
            resized_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
