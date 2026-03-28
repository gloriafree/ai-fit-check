"""
Step 5: Lighting Harmonization using IC-Light
===============================================
Unifies lighting across the three try-on views so they look
like they were taken under the same conditions.
"""

import logging
from pathlib import Path
from typing import Optional, Dict

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


class LightingHarmonizer:
    """Harmonizes lighting across multiple try-on views using IC-Light."""

    def __init__(self, config: dict):
        self.config = config.get("ic_light", {})
        self.device = self.config.get("device", "cpu")
        self.prompt = self.config.get("prompt", "soft studio lighting, even illumination")
        self.strength = self.config.get("strength", 0.6)
        self.model = None

    def load_model(self):
        """Load IC-Light model."""
        if self.model is not None:
            return

        logger.info("Loading IC-Light model...")

        try:
            from diffusers import StableDiffusionImg2ImgPipeline

            self.model = StableDiffusionImg2ImgPipeline.from_pretrained(
                "lllyasviel/ic-light-fbc-sd15",
                torch_dtype=__import__("torch").float16 if self.device == "cuda" else __import__("torch").float32,
                safety_checker=None,
            )
            self.model = self.model.to(self.device)
            self.model_type = "ic_light"
            logger.info("IC-Light model loaded successfully.")

        except Exception as e:
            logger.warning(f"IC-Light not available: {e}. Using histogram-based fallback.")
            self.model_type = "fallback"

    def harmonize(
        self,
        images: Dict[str, Image.Image],
        reference_view: str = "front",
        save_dir: Optional[str] = None,
    ) -> Dict[str, Image.Image]:
        """
        Harmonize lighting across multiple views.

        Args:
            images: Dict of {view_name: PIL Image}
            reference_view: Which view to use as the lighting reference
            save_dir: Optional save directory

        Returns:
            Dict of harmonized images
        """
        if self.model is None:
            self.load_model()

        if reference_view not in images:
            reference_view = list(images.keys())[0]

        reference_img = images[reference_view]
        logger.info(f"Harmonizing lighting with reference: {reference_view}")

        results = {}
        for view_name, img in images.items():
            if view_name == reference_view:
                results[view_name] = img
                continue

            if self.model_type == "ic_light":
                results[view_name] = self._harmonize_ic_light(img, reference_img)
            else:
                results[view_name] = self._harmonize_histogram(img, reference_img)

            logger.info(f"Harmonized: {view_name}")

        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            for view_name, img in results.items():
                save_path = Path(save_dir) / f"harmonized_{view_name}.png"
                img.save(save_path)
                logger.info(f"Saved harmonized {view_name} to: {save_path}")

        return results

    def _harmonize_ic_light(self, image: Image.Image, reference: Image.Image) -> Image.Image:
        """Harmonize using IC-Light model."""
        # IC-Light takes the image and relights it based on prompt
        result = self.model(
            prompt=self.prompt,
            image=image,
            strength=self.strength,
            num_inference_steps=20,
            guidance_scale=2.0,
        ).images[0]

        return result

    def _harmonize_histogram(self, image: Image.Image, reference: Image.Image) -> Image.Image:
        """
        Fallback: Histogram-based color/brightness matching.
        Matches the brightness, contrast, and color balance of the target
        to the reference image.
        """
        image_rgb = image.convert("RGB")
        reference_rgb = reference.convert("RGB")

        img_array = np.array(image_rgb, dtype=np.float32)
        ref_array = np.array(reference_rgb, dtype=np.float32)

        # Match mean and std for each channel
        for c in range(3):
            img_mean = img_array[:, :, c].mean()
            img_std = img_array[:, :, c].std()
            ref_mean = ref_array[:, :, c].mean()
            ref_std = ref_array[:, :, c].std()

            if img_std > 0:
                img_array[:, :, c] = (img_array[:, :, c] - img_mean) * (ref_std / img_std) + ref_mean

        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        result = Image.fromarray(img_array)

        # Apply slight blur to smooth any harsh transitions
        result = result.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Match overall brightness
        ref_brightness = np.mean(ref_array)
        result_brightness = np.mean(np.array(result, dtype=np.float32))
        if result_brightness > 0:
            brightness_factor = ref_brightness / result_brightness
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(brightness_factor)

        return result
