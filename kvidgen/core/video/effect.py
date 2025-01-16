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


@EffectRegistry.register("spotlight")
class SpotlightEffect(EffectBase):
    """
    聚光灯效果
    聚焦图片中央部分，周围逐渐变暗，突出主体区域，具有更平滑的过渡。
    """

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        max_radius = int(np.sqrt(h**2 + w**2) / 2)
        current_radius = int(max_radius * (frame_idx / total_frames))

        # 创建从中心到边缘的径向渐变掩码
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        mask = 1 - np.clip(
            (dist_from_center - current_radius) / (max_radius - current_radius), 0, 1
        )

        # 使用高斯模糊平滑过渡
        mask = cv2.GaussianBlur(mask, (51, 51), sigmaX=20, sigmaY=20)

        # 将 mask 转换为 3 通道并应用到图像
        spotlight = np.dstack([mask] * 3)
        return (image.astype(np.float32) * spotlight).astype(np.uint8)


@EffectRegistry.register("tear_drop")
class TearDropEffect(EffectBase):
    """
    TearDropEffect（泪滴效果）
    模拟画面逐渐被泪水模糊的效果，突出悲伤的情感。
    """

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        h, w = image.shape[:2]
        blur_intensity = int(1 + 10 * (frame_idx / total_frames))
        blurred_image = cv2.GaussianBlur(
            image, (blur_intensity | 1, blur_intensity | 1), 0
        )
        alpha = frame_idx / total_frames
        return cv2.addWeighted(image, 1 - alpha, blurred_image, alpha, 0)


@EffectRegistry.register("heart_pulse")
class HeartPulseEffect(EffectBase):
    """
    HeartPulseEffect
    模拟心跳节奏的光晕扩散和收缩，带有柔和的渐变效果，增强紧张和急迫感。
    """

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        h, w = image.shape[:2]
        overlay = image.copy().astype(np.float32) / 255.0  # 归一化图像
        base_image = image.astype(np.float32) / 255.0

        # 心跳节奏和强度
        heartbeat_freq = 4  # 每秒4次心跳
        cycle_position = (
            (frame_idx / total_frames) * heartbeat_freq * 2 * np.pi
        )  # 当前周期位置
        pulse_intensity = 0.7 + 0.3 * np.abs(np.sin(cycle_position))  # 动态强度

        # 光圈的动态半径
        max_radius = int(min(h, w) * 0.6)
        radius = int(max_radius * (0.5 + 0.3 * np.sin(cycle_position)))  # 动态半径
        center = (w // 2, h // 2)

        # 创建光圈掩码
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(mask, center, radius, 1.0, -1)  # 主光圈
        mask = cv2.GaussianBlur(mask, (101, 101), 50)  # 增加模糊程度

        # 动态透明渐变光圈
        light_overlay = np.zeros_like(overlay)
        light_overlay[:, :, 0] = mask * pulse_intensity * 0.8  # 蓝色分量
        light_overlay[:, :, 1] = mask * pulse_intensity * 0.8  # 绿色分量
        light_overlay[:, :, 2] = mask * pulse_intensity  # 白光偏冷色

        # 混合光圈和原图
        result = cv2.addWeighted(base_image, 1.0, light_overlay, 0.5, 0)

        # 确保返回结果为 uint8 类型
        return np.clip(result * 255, 0, 255).astype(np.uint8)


@EffectRegistry.register("blur_transition")
class BlurTransitionEffect(EffectBase):
    """

    模糊渐变效果，从清晰逐渐变模糊，表现失去希望或逐渐模糊的记忆。
    """

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        blur_intensity = int(1 + 10 * (frame_idx / total_frames))
        blurred_image = cv2.GaussianBlur(
            image, (blur_intensity | 1, blur_intensity | 1), 0
        )
        alpha = frame_idx / total_frames
        return cv2.addWeighted(image, 1 - alpha, blurred_image, alpha, 0)


@EffectRegistry.register("color_shift")
class ColorShiftEffect(EffectBase):
    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        """
        动态色调转换，从暖色（如橙色）逐渐过渡到冷色（如蓝色），或反向。
        :param image: 输入图片。
        :param frame_idx: 当前帧索引。
        :param total_frames: 总帧数。
        :return: 添加特效后的图片。
        """
        # 计算当前过渡比例
        alpha = frame_idx / total_frames

        # 创建暖色和冷色叠加层
        warm_overlay = np.full(image.shape, (40, 100, 255), dtype=np.uint8)  # 橙色调
        cool_overlay = np.full(image.shape, (255, 150, 60), dtype=np.uint8)  # 蓝色调

        # 动态混合两种颜色
        if alpha <= 0.5:
            transition = cv2.addWeighted(
                image, 1 - alpha * 2, warm_overlay, alpha * 2, 0
            )
        else:
            transition = cv2.addWeighted(
                image, 1 - (alpha - 0.5) * 2, cool_overlay, (alpha - 0.5) * 2, 0
            )

        return transition


@EffectRegistry.register("vignette")
class VignetteEffect(EffectBase):
    """
    四周暗角效果，增强画面中央的情感重点，适合聚焦病人或关键对象
    """

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        max_radius = max(h, w) // 2
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        mask = 1 - np.clip(dist_from_center / max_radius, 0, 1)
        mask = cv2.GaussianBlur(mask, (101, 101), 50)
        vignette = np.dstack([mask] * 3)
        return (image.astype(np.float32) * vignette).astype(np.uint8)


@EffectRegistry.register("light_flicker")
class LightFlickerEffect(EffectBase):

    """
    闪烁的灯光效果，模拟希望逐渐闪现，适合表现筹款目标的可能性
    """

    def apply(self, image: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        alpha = 0.5 + 0.5 * np.sin(2 * np.pi * (frame_idx / total_frames))
        overlay = (image.astype(np.float32) * alpha).astype(np.uint8)
        return cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0)
