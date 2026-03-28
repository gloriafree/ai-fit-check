"""
Step 2: Super Resolution using Real-ESRGAN
===========================================
Upscales clothing images to enhance texture detail before try-on.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class SuperResolver:
    """Upscales images using Real-ESRGAN for better texture detail."""

    def __init__(self, config: dict):
        self.config = config.get("super_resolution", {})
        self.scale = self.config.get("scale", 4)
        self.target_size = self.config.get("target_size", 1024)
        self.device = self.config.get("device", "cpu")
        self.model = None

        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
        except ImportError:
            pass

    def load_model(self):
        """Load Real-ESRGAN model."""
        if self.model is not None:
            return

        logger.info("Loading Real-ESRGAN model...")

        try:
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet

            # RealESRGAN_x4plus model architecture
            rrdb_model = RRDBNet(
                num_in_ch=3, num_out_ch=3, num_feat=64,
                num_block=23, num_grow_ch=32, scale=4
            )

            model_path = self._get_model_path("RealESRGAN_x4plus.pth")

            # Auto-download if model doesn't exist
            if not Path(model_path).exists():
                logger.info("Model not found locally, will auto-download...")
                model_path = None  # RealESRGANer will auto-download

            self.model = RealESRGANer(
                scale=self.scale,
                model_path=model_path,
                model=rrdb_model,
                tile=400,  # Tile size to avoid OOM
                tile_pad=10,
                pre_pad=0,
                half=True if self.device == "cuda" else False,
                device=self.device,
            )

            logger.info("Real-ESRGAN model loaded successfully.")

        except ImportError:
            logger.warning("Real-ESRGAN not installed. Using Pillow LANCZOS upscaling as fallback.")
            self._use_fallback = True

    def upscale(self, image: Image.Image, save_dir: Optional[str] = None, filename: str = "upscaled") -> Image.Image:
        """
        Upscale an image to enhance texture detail.

        Args:
            image: Input PIL Image (can be RGBA with transparency)
            save_dir: Optional directory to save result
            filename: Base filename for saving

        Returns:
            Upscaled PIL Image
        """
        if self.model is None and not hasattr(self, '_use_fallback'):
            self.load_model()

        original_size = image.size
        logger.info(f"Upscaling image from {original_size}...")

        # Check if upscaling is needed
        max_dim = max(image.size)
        if max_dim >= self.target_size:
            logger.info(f"Image already large enough ({max_dim}px), skipping upscale. Resizing to target.")
            return self._resize_to_target(image)

        if hasattr(self, '_use_fallback') and self._use_fallback:
            result = self._upscale_fallback(image)
        else:
            result = self._upscale_realesrgan(image)

        # Resize to target size while maintaining aspect ratio
        result = self._resize_to_target(result)

        logger.info(f"Upscaled: {original_size} → {result.size}")

        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            save_path = Path(save_dir) / f"{filename}.png"
            result.save(save_path)
            logger.info(f"Saved upscaled image to: {save_path}")

        return result

    def _upscale_realesrgan(self, image: Image.Image) -> Image.Image:
        """Upscale using Real-ESRGAN model."""
        has_alpha = image.mode == "RGBA"

        if has_alpha:
            # Handle transparency: upscale RGB and alpha separately
            rgb = image.convert("RGB")
            alpha = image.split()[3]

            # Upscale RGB
            rgb_np = np.array(rgb)[:, :, ::-1]  # RGB to BGR for OpenCV
            output_bgr, _ = self.model.enhance(rgb_np, outscale=self.scale)
            output_rgb = output_bgr[:, :, ::-1]  # BGR back to RGB

            # Upscale alpha channel
            alpha_np = np.array(alpha)
            alpha_3ch = np.stack([alpha_np] * 3, axis=-1)
            alpha_up, _ = self.model.enhance(alpha_3ch, outscale=self.scale)
            alpha_up = alpha_up[:, :, 0]

            # Combine
            result = Image.fromarray(output_rgb).convert("RGBA")
            result.putalpha(Image.fromarray(alpha_up))
        else:
            rgb_np = np.array(image.convert("RGB"))[:, :, ::-1]
            output_bgr, _ = self.model.enhance(rgb_np, outscale=self.scale)
            result = Image.fromarray(output_bgr[:, :, ::-1])

        return result

    def _upscale_fallback(self, image: Image.Image) -> Image.Image:
        """Fallback: use Pillow LANCZOS upscaling."""
        new_size = (image.size[0] * self.scale, image.size[1] * self.scale)
        return image.resize(new_size, Image.LANCZOS)

    def _resize_to_target(self, image: Image.Image) -> Image.Image:
        """Resize image so the longest side equals target_size."""
        w, h = image.size
        max_dim = max(w, h)
        if max_dim <= self.target_size:
            return image

        ratio = self.target_size / max_dim
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        return image.resize((new_w, new_h), Image.LANCZOS)

    def _get_model_path(self, filename: str) -> str:
        return str(Path(__file__).parent.parent / "models" / filename)
