"""
Step 1: Clothing Segmentation using Grounded SAM 2
===================================================
Extracts clothing from a screenshot image, removing background,
price tags, models, and other non-clothing elements.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from PIL import Image

logger = logging.getLogger(__name__)


class ClothingSegmenter:
    """Segments clothing items from screenshots using Grounded SAM 2."""

    def __init__(self, config: dict):
        self.config = config.get("segmentation", {})
        self.device = self.config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
        self.prompt = self.config.get("prompt", "clothing, garment")
        self.box_threshold = self.config.get("box_threshold", 0.3)
        self.text_threshold = self.config.get("text_threshold", 0.25)
        self.model = None
        self.sam_predictor = None

    def load_model(self):
        """Load Grounded SAM 2 models."""
        if self.model is not None:
            logger.info("Segmentation model already loaded, skipping.")
            return

        logger.info("Loading Grounded SAM 2 models...")

        try:
            # Load Grounding DINO for text-guided detection
            from groundingdino.util.inference import load_model as load_gd_model
            from groundingdino.util.inference import predict as gd_predict

            gd_config_path = self._get_model_path("groundingdino_swinb_cogcoor.pth", "config")
            gd_weights_path = self._get_model_path("groundingdino_swinb_cogcoor.pth", "weights")

            self.grounding_model = load_gd_model(gd_config_path, gd_weights_path, device=self.device)
            self.gd_predict = gd_predict

            # Load SAM 2 for segmentation
            from sam2.build_sam import build_sam2
            from sam2.sam2_image_predictor import SAM2ImagePredictor

            sam2_checkpoint = self._get_model_path("sam2.1_hiera_large.pt")
            sam2_config = "sam2.1_hiera_l.yaml"

            sam2_model = build_sam2(sam2_config, sam2_checkpoint, device=self.device)
            self.sam_predictor = SAM2ImagePredictor(sam2_model)

            logger.info("Grounded SAM 2 models loaded successfully.")

        except ImportError as e:
            logger.warning(f"Grounded SAM 2 not available: {e}")
            logger.info("Falling back to U2Net cloth segmentation...")
            self._load_fallback_model()

    def _load_fallback_model(self):
        """Load lightweight U2Net cloth segmentation as fallback."""
        try:
            from transformers import pipeline
            self.model = pipeline(
                "image-segmentation",
                model="mattmdjaga/segformer_b2_clothes",
                device=0 if self.device == "cuda" else -1
            )
            self._use_fallback = True
            logger.info("Fallback segmentation model (SegFormer clothes) loaded.")
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")
            raise

    def segment(self, image_path: str, save_dir: Optional[str] = None) -> Image.Image:
        """
        Segment clothing from an image.

        Args:
            image_path: Path to the input screenshot image
            save_dir: Optional directory to save intermediate results

        Returns:
            PIL Image of the segmented clothing with transparent background
        """
        if self.model is None and self.sam_predictor is None:
            self.load_model()

        image = Image.open(image_path).convert("RGB")
        logger.info(f"Segmenting clothing from: {image_path} ({image.size})")

        if hasattr(self, '_use_fallback') and self._use_fallback:
            result = self._segment_fallback(image)
        else:
            result = self._segment_grounded_sam(image)

        # Save intermediate result if requested
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            save_path = Path(save_dir) / f"segmented_{Path(image_path).stem}.png"
            result.save(save_path)
            logger.info(f"Saved segmented clothing to: {save_path}")

        return result

    def _segment_grounded_sam(self, image: Image.Image) -> Image.Image:
        """Segment using Grounded SAM 2 pipeline."""
        image_np = np.array(image)

        # Step 1: Detect clothing bounding boxes with Grounding DINO
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

        # Step 2: Generate masks with SAM 2
        self.sam_predictor.set_image(image_np)

        # Convert boxes to SAM format
        h, w = image_np.shape[:2]
        boxes_abs = boxes * torch.tensor([w, h, w, h])

        masks, scores, _ = self.sam_predictor.predict(
            box=boxes_abs.numpy(),
            multimask_output=False,
        )

        # Combine all clothing masks
        combined_mask = np.zeros((h, w), dtype=bool)
        for mask in masks:
            if mask.ndim == 3:
                mask = mask[0]
            combined_mask |= mask

        # Apply mask to create RGBA output
        result = Image.new("RGBA", image.size, (0, 0, 0, 0))
        image_rgba = image.convert("RGBA")
        image_data = np.array(image_rgba)
        image_data[~combined_mask, 3] = 0  # Set non-clothing pixels transparent
        result = Image.fromarray(image_data)

        return result

    def _segment_fallback(self, image: Image.Image) -> Image.Image:
        """Segment using SegFormer clothes model (fallback)."""
        results = self.model(image)

        # Clothing labels in the SegFormer clothes model
        clothing_labels = {
            "Upper-clothes", "Skirt", "Pants", "Dress",
            "Belt", "Scarf", "Coat", "Jumpsuits"
        }

        # Combine all clothing masks
        w, h = image.size
        combined_mask = np.zeros((h, w), dtype=bool)

        for result in results:
            if result["label"] in clothing_labels:
                mask = np.array(result["mask"])
                combined_mask |= (mask > 128)
                logger.info(f"  Found: {result['label']} (score: {result['score']:.3f})")

        if not combined_mask.any():
            logger.warning("No clothing segments found. Using full image.")
            return image.convert("RGBA")

        # Apply mask
        image_rgba = image.convert("RGBA")
        image_data = np.array(image_rgba)
        image_data[~combined_mask, 3] = 0
        result = Image.fromarray(image_data)

        # Crop to clothing bounding box with padding
        bbox = result.getbbox()
        if bbox:
            pad = 20
            bbox = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(w, bbox[2] + pad),
                min(h, bbox[3] + pad),
            )
            result = result.crop(bbox)

        return result

    def _get_model_path(self, filename: str, subdir: str = "") -> str:
        """Get path to model file in the models directory."""
        base = Path(__file__).parent.parent / "models"
        if subdir:
            return str(base / subdir / filename)
        return str(base / filename)
