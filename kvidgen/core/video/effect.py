from typing import Dict, Callable

import cv2
import numpy as np


class EffectBase:
    """特效基类，所有特效需继承并实现 apply 方法。"""

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        raise NotImplementedError("特效类需实现 apply 方法。")


class EffectRegistry:
    """特效注册表，用于管理和查找特效。"""

    _registry: Dict[str, Callable[[], EffectBase]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(effect_cls: Callable[[], EffectBase]):
            cls._registry[name] = effect_cls
            return effect_cls

        return decorator

    @classmethod
    def get_effect(cls, name: str) -> EffectBase:
        if name not in cls._registry:
            raise ValueError(f"特效 '{name}' 未注册。")
        return cls._registry[name]()


@EffectRegistry.register("zoom")
class ZoomEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        动态放大效果。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        scale = 1 + 0.1 * (frame_idx / total_frames)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, 0, scale)
        return cv2.warpAffine(image, matrix, (w, h))


@EffectRegistry.register("fade_in")
class FadeInEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        渐入效果。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        alpha = frame_idx / total_frames
        return (image * alpha).astype(np.uint8)


@EffectRegistry.register("slide")
class SlideEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        滑入效果。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        h, w = image.shape[:2]
        offset = int(w * (1 - frame_idx / total_frames))
        canvas = np.zeros_like(image)
        canvas[:, offset:w] = image[:, : w - offset]
        return canvas


@EffectRegistry.register("grayscale")
class GrayscaleEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        黑白效果。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
        alpha = frame_idx / total_frames
        return cv2.addWeighted(image, 1 - alpha, gray_image, alpha, 0)


@EffectRegistry.register("red_bubble")
class RedBubbleEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        红色气泡效果。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        overlay = image.copy()
        alpha = 0.5 + 0.5 * (frame_idx / total_frames)
        h, w = image.shape[:2]
        cv2.circle(overlay, (w // 2, h // 2), min(h, w) // 4, (0, 0, 255), -1)
        return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


@EffectRegistry.register("heartbeat")
class HeartbeatEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        心跳效果，图片进行周期性放大和缩小。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        scale = 1 + 0.05 * np.sin(2 * np.pi * (frame_idx / total_frames) * 4)  # 心跳频率
        matrix = cv2.getRotationMatrix2D(center, 0, scale)
        return cv2.warpAffine(image, matrix, (w, h))


@EffectRegistry.register("highlight_border")
class HighlightBorderEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        高亮边框效果，边框逐渐出现并闪烁。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        overlay = image.copy()
        alpha = (
            (frame_idx / total_frames)
            if frame_idx < total_frames // 2
            else (1 - frame_idx / total_frames)
        )
        thickness = max(2, int(10 * alpha))  # 边框厚度变化
        h, w = image.shape[:2]
        color = (0, 255, 0)  # 高亮绿色边框
        cv2.rectangle(overlay, (0, 0), (w, h), color, thickness=thickness)
        return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


@EffectRegistry.register("spotlight")
class SpotlightEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        聚光灯效果，逐渐突出图片中心。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        radius = int(min(h, w) * (0.1 + 0.4 * (frame_idx / total_frames)))
        center = (w // 2, h // 2)
        cv2.circle(mask, center, radius, 255, -1)
        blurred_mask = cv2.GaussianBlur(mask, (21, 21), 0)
        spotlight = cv2.merge([blurred_mask] * 3)
        return cv2.addWeighted(image, 0.8, spotlight, 0.2, 0)


@EffectRegistry.register("shimmer")
class ShimmerEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        闪烁效果，模拟光线横向滑过图片。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        h, w = image.shape[:2]
        overlay = np.zeros_like(image)
        x_start = int((w + h) * (frame_idx / total_frames)) - h
        x_end = x_start + h // 3
        cv2.rectangle(overlay, (x_start, 0), (x_end, h), (255, 255, 255), -1)
        blurred_overlay = cv2.GaussianBlur(overlay, (51, 51), 0)
        return cv2.addWeighted(image, 1, blurred_overlay, 0.5, 0)
