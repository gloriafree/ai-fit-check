"""
AI Fit Check - Main Pipeline
==============================
Orchestrates the full virtual try-on pipeline:

  Screenshot → Segment → Upscale → Multi-view → Try-on → Light Harmonize → Output

Usage:
    from ai_fit_check.pipeline import FitCheckPipeline
    pipeline = FitCheckPipeline("configs/config.yaml")
    results = pipeline.run("clothing_screenshot.png", "my_photo.jpg")
"""

import os
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

import yaml
from PIL import Image

from .segmentation import ClothingSegmenter
from .super_resolution import SuperResolver
from .multiview_gen import MultiViewGenerator
from .tryon import VirtualTryOn
from .lighting import LightingHarmonizer

logger = logging.getLogger(__name__)


class FitCheckPipeline:
    """Main pipeline that chains all steps together."""

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize the pipeline with configuration.

        Args:
            config_path: Path to YAML config file
        """
        self.config = self._load_config(config_path)
        self.pipeline_config = self.config.get("pipeline", {})

        # Output settings
        self.output_dir = self.pipeline_config.get("output_dir", "data/output")
        self.save_intermediate = self.pipeline_config.get("save_intermediate", True)

        # Initialize all modules (lazy loading - models loaded on first use)
        self.segmenter = ClothingSegmenter(self.config)
        self.upscaler = SuperResolver(self.config)
        self.multiview = MultiViewGenerator(self.config)
        self.tryon = VirtualTryOn(self.config)
        self.harmonizer = LightingHarmonizer(self.config)

        # Setup logging
        log_level = self.pipeline_config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )

        logger.info("AI Fit Check pipeline initialized.")

    def run(
        self,
        clothing_image_path: str,
        person_image_path: str,
        category: str = "auto",
        output_name: Optional[str] = None,
    ) -> Dict[str, Image.Image]:
        """
        Run the full virtual try-on pipeline.

        Args:
            clothing_image_path: Path to clothing screenshot/image
            person_image_path: Path to person's full-body photo
            category: Clothing category ("tops", "bottoms", "one-pieces", "auto")
            output_name: Optional name for output files (default: timestamp)

        Returns:
            Dict with keys "front", "side", "back" mapping to try-on result images.
            Also saves a combined 3-view image.
        """
        start_time = time.time()

        # Create output directory
        if output_name is None:
            output_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = Path(self.output_dir) / output_name
        os.makedirs(run_dir, exist_ok=True)
        intermediate_dir = str(run_dir / "intermediate") if self.save_intermediate else None
        if intermediate_dir:
            os.makedirs(intermediate_dir, exist_ok=True)

        logger.info("=" * 60)
        logger.info(f"AI Fit Check Pipeline - Run: {output_name}")
        logger.info(f"  Clothing: {clothing_image_path}")
        logger.info(f"  Person:   {person_image_path}")
        logger.info(f"  Category: {category}")
        logger.info("=" * 60)

        # ──────────────────────────────────────────────
        # Step 1: Segment clothing from screenshot
        # ──────────────────────────────────────────────
        logger.info("\n▶ Step 1/5: Segmenting clothing...")
        step_start = time.time()

        segmented_clothing = self.segmenter.segment(
            clothing_image_path,
            save_dir=intermediate_dir,
        )
        logger.info(f"  ✓ Segmentation complete ({time.time() - step_start:.1f}s)")

        # ──────────────────────────────────────────────
        # Step 2: Upscale clothing image
        # ──────────────────────────────────────────────
        logger.info("\n▶ Step 2/5: Upscaling clothing texture...")
        step_start = time.time()

        upscaled_clothing = self.upscaler.upscale(
            segmented_clothing,
            save_dir=intermediate_dir,
            filename="upscaled_clothing",
        )
        logger.info(f"  ✓ Upscaling complete ({time.time() - step_start:.1f}s)")

        # ──────────────────────────────────────────────
        # Step 3: Generate multi-view person images
        # ──────────────────────────────────────────────
        logger.info("\n▶ Step 3/5: Generating multi-view person images...")
        step_start = time.time()

        person_views = self.multiview.generate_views(
            person_image_path,
            save_dir=intermediate_dir,
        )
        logger.info(f"  ✓ Multi-view generation complete ({time.time() - step_start:.1f}s)")
        logger.info(f"    Generated views: {list(person_views.keys())}")

        # ──────────────────────────────────────────────
        # Step 4: Virtual try-on for each view
        # ──────────────────────────────────────────────
        logger.info("\n▶ Step 4/5: Running virtual try-on...")
        step_start = time.time()

        tryon_results = self.tryon.try_on_multiview(
            person_views=person_views,
            clothing_image=upscaled_clothing,
            category=category,
            save_dir=intermediate_dir,
        )
        logger.info(f"  ✓ Virtual try-on complete ({time.time() - step_start:.1f}s)")

        # ──────────────────────────────────────────────
        # Step 5: Harmonize lighting across views
        # ──────────────────────────────────────────────
        logger.info("\n▶ Step 5/5: Harmonizing lighting...")
        step_start = time.time()

        final_results = self.harmonizer.harmonize(
            tryon_results,
            reference_view="front",
            save_dir=intermediate_dir,
        )
        logger.info(f"  ✓ Lighting harmonization complete ({time.time() - step_start:.1f}s)")

        # ──────────────────────────────────────────────
        # Save final outputs
        # ──────────────────────────────────────────────
        logger.info("\nSaving final outputs...")

        # Save individual views
        for view_name, img in final_results.items():
            save_path = run_dir / f"{view_name}.png"
            img.save(save_path, quality=95)

        # Create combined 3-view image
        combined = self._create_combined_view(final_results)
        combined_path = run_dir / "combined_3view.png"
        combined.save(combined_path, quality=95)

        total_time = time.time() - start_time
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Pipeline complete! Total time: {total_time:.1f}s")
        logger.info(f"Output directory: {run_dir}")
        logger.info(f"  - front.png")
        logger.info(f"  - side.png")
        logger.info(f"  - back.png")
        logger.info(f"  - combined_3view.png")
        logger.info(f"{'=' * 60}")

        return final_results

    def _create_combined_view(
        self,
        views: Dict[str, Image.Image],
        padding: int = 20,
        bg_color: tuple = (245, 245, 245),
    ) -> Image.Image:
        """
        Create a side-by-side combined image of all three views.

        Returns a single image with front, side, and back views arranged horizontally
        with labels.
        """
        view_order = ["front", "side", "back"]
        images = [views.get(v) for v in view_order if v in views]

        if not images:
            raise ValueError("No view images to combine")

        # Normalize all images to same height
        target_h = max(img.size[1] for img in images)
        resized = []
        for img in images:
            ratio = target_h / img.size[1]
            new_w = int(img.size[0] * ratio)
            resized.append(img.resize((new_w, target_h), Image.LANCZOS))

        # Calculate canvas size
        total_w = sum(img.size[0] for img in resized) + padding * (len(resized) + 1)
        total_h = target_h + padding * 2 + 40  # Extra space for labels

        # Create canvas
        canvas = Image.new("RGB", (total_w, total_h), bg_color)

        # Paste images and add labels
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(canvas)

            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            except (OSError, IOError):
                font = ImageFont.load_default()

            x_offset = padding
            labels = ["FRONT", "SIDE", "BACK"]

            for i, img in enumerate(resized):
                # Paste image
                y_offset = padding + 30
                canvas.paste(img, (x_offset, y_offset))

                # Draw label
                label = labels[i] if i < len(labels) else ""
                text_w = draw.textlength(label, font=font)
                text_x = x_offset + (img.size[0] - text_w) // 2
                draw.text((text_x, padding + 5), label, fill=(80, 80, 80), font=font)

                x_offset += img.size[0] + padding

        except ImportError:
            # Without PIL draw, just paste images
            x_offset = padding
            for img in resized:
                canvas.paste(img, (x_offset, padding))
                x_offset += img.size[0] + padding

        return canvas

    @staticmethod
    def _load_config(config_path: str) -> dict:
        """Load YAML configuration file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        logger.debug(f"Loaded config from: {config_path}")
        return config
