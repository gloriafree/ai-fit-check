"""
Step 1: Clothing Segmentation
===============================
Extracts clothing from a screenshot image, removing background,
price tags, models, and other non-clothing elements.

Supports three backends (auto-fallback):
  1. Grounded SAM 2 (best quality, requires PyTorch + GPU)
  2. rembg (good quality, CPU-friendly, no PyTorch)
  3. Simple center-crop (last resort)
"""

import os
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ClothingSegmenter:
    """Segments clothing items from screenshots."""

    def __init__(self, config: dict):
        self.config = config.get("segmentation", {})
        self.device = self.config.get("device", "cpu")
        self.prompt = self.config.get("prompt", "clothing, garment")
        self.box_threshold = self.config.get("box_threshold", 0.3)
        self.text_threshold = self.config.get("text_threshold", 0.25)
        self.model = None
        self.sam_predictor = None
        self._backend = None

        # Try to detect CUDA availability without importing torch
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
        except ImportError:
            self.device = "cpu"

    def load_model(self):
        """Load segmentation model. Tries backends in order of quality."""
        if self._backend is not None:
            return

        # Backend 1: Grounded SAM 2 (requires PyTorch + GPU)
        if self.device == "cuda":
            try:
                self._load_grounded_sam()
                return
            except (ImportError, Exception) as e:
                logger.info(f"Grounded SAM 2 not available: {e}")

        # Backend 2: rembg (lightweight, CPU-friendly)
        try:
            from rembg import remove as rembg_remove
            self._rembg_remove = rembg_remove
            self._backend = "rembg"
            logger.info("Using rembg for clothing segmentation (CPU mode).")
            return
        except ImportError:
            logger.info("rembg not installed.")

        # Backend 3: Simple fallback
        self._backend = "simple"
        logger.warning("No segmentation model available. Using simple center-crop fallback.")

    def _load_grounded_sam(self):
        """Load Grounded SAM 2 models (requires PyTorch)."""
        import torch
        from groundingdino.util.inference import load_model as load_gd_model
        from groundingdino.util.inference import predict as gd_predict
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        gd_config_path = self._get_model_path("groundingdino_swinb_cogcoor.pth", "config")
        gd_weights_path = self._get_model_path("groundingdino_swinb_cogcoor.pth", "weights")
        self.grounding_model = load_gd_model(gd_config_path, gd_weights_path, device=self.device)
        self.gd_predict = gd_predict

        sam2_checkpoint = self._get_model_path("sam2.1_hiera_large.pt")
        sam2_model = build_sam2("sam2.1_hiera_l.yaml", sam2_checkpoint, device=self.device)
        self.sam_predictor = SAM2ImagePredictor(sam2_model)
        self._backend = "grounded_sam"
        logger.info("Grounded SAM 2 loaded successfully.")

    def segment(self, image_path: str, save_dir: Optional[str] = None) -> Image.Image:
        """
        Segment clothing from an image.

        Args:
            image_path: Path to the input screenshot image
            save_dir: Optional directory to save intermediate results

        Returns:
            PIL Image of the segmented clothing with transparent background
        """
        if self._backend is None:
            self.load_model()

        image = Image.open(image_path).convert("RGB")
        logger.info(f"Segmenting clothing from: {image_path} ({image.size}) [backend: {self._backend}]")

        if self._backend == "grounded_sam":
            result = self._segment_grounded_sam(image)
        elif self._backend == "rembg":
            result = self._segment_rembg(image)
        else:
            result = self._segment_simple(image)

        # Save intermediate result if requested
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            save_path = Path(save_dir) / f"segmented_{Path(image_path).stem}.png"
            result.save(save_path)
            logger.info(f"Saved segmented clothing to: {save_path}")

        return result

    def _segment_rembg(self, image: Image.Image) -> Image.Image:
        """Segment using rembg (removes background, keeps foreground clothing)."""
        result = self._rembg_remove(image)

        # Crop to content bounding box with padding
        bbox = result.getbbox()
        if bbox:
            w, h = result.size
            pad = 20
            bbox = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(w, bbox[2] + pad),
                min(h, bbox[3] + pad),
            )
            result = result.crop(bbox)

        return result

    def _segment_grounded_sam(self, image: Image.Image) -> Image.Image:
        """Segment using Grounded SAM 2 pipeline."""
        import torch

        image_np = np.array(image)

        boxes, logits, phrases = self.gd_predict(
            model=self.grounding_model,
            image=image,
            caption=self.prompt,
            box_threshold=self.box_threshold,
            text_threshold=self.text_threshold,
        )

        if len(boxes) == 0:
            logger.warning("No clothing detected. Returning original image.")
            return image

        logger.info(f"Detected {len(boxes)} clothing regions: {phrases}")

        self.sam_predictor.set_image(image_np)

        h, w = image_np.shape[:2]
        boxes_abs = boxes * torch.tensor([w, h, w, h])

        masks, scores, _ = self.sam_predictor.predict(
            box=boxes_abs.numpy(),
            multimask_output=False,
        )

        combined_mask = np.zeros((h, w), dtype=bool)
        for mask in masks:
            if mask.ndim == 3:
                mask = mask[0]
            combined_mask |= mask

        image_rgba = image.convert("RGBA")
        image_data = np.array(image_rgba)
        image_data[~combined_mask, 3] = 0
        return Image.fromarray(image_data)

    def _segment_simple(self, image: Image.Image) -> Image.Image:
        """Simple fallback: center-crop the image (assumes clothing is centered)."""
        w, h = image.size
        # Crop center 70% of image
        margin_x = int(w * 0.15)
        margin_y = int(h * 0.1)
        cropped = image.crop((margin_x, margin_y, w - margin_x, h - margin_y))
        return cropped.convert("RGBA")

    def _get_model_path(self, filename: str, subdir: str = "") -> str:
        base = Path(__file__).parent.parent / "models"
        if subdir:
            return str(base / subdir / filename)
        return str(base / filename)
