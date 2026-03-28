"""
Step 3: Multi-View Person Image Generation
============================================
Generates front, side, and back views of a person from a single
front-facing photo using CharacterGen / Zero123++ / Era3D.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class MultiViewGenerator:
    """Generates multiple viewing angles of a person from a single photo."""

    VIEWS = [
        {"name": "front", "azimuth": 0, "elevation": 0},
        {"name": "side", "azimuth": 90, "elevation": 0},
        {"name": "back", "azimuth": 180, "elevation": 0},
    ]

    def __init__(self, config: dict):
        self.config = config.get("character_gen", {})
        self.device = self.config.get("device", "cpu")
        self.views = self.config.get("views", self.VIEWS)
        self.model = None
        self.model_type = None

        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
        except ImportError:
            pass

    def load_model(self):
        """Load multi-view generation model. Tries multiple backends."""
        if self.model is not None:
            return

        # Try loading in order of preference
        loaders = [
            ("zero123pp", self._load_zero123pp),
            ("era3d", self._load_era3d),
            ("charactergen", self._load_charactergen),
        ]

        for name, loader in loaders:
            try:
                loader()
                self.model_type = name
                logger.info(f"Multi-view model loaded: {name}")
                return
            except (ImportError, Exception) as e:
                logger.debug(f"Could not load {name}: {e}")
                continue

        logger.warning("No multi-view model available. Using pose-guided fallback.")
        self.model_type = "fallback"

    def _load_zero123pp(self):
        """Load Zero123++ for multi-view generation."""
        from diffusers import DiffusionPipeline, EulerAncestralDiscreteScheduler

        pipeline = DiffusionPipeline.from_pretrained(
            "sudo-ai/zero123plus-v1.2",
            custom_pipeline="sudo-ai/zero123plus-pipeline",
            torch_dtype=__import__("torch").float16 if self.device == "cuda" else __import__("torch").float32,
        )
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipeline.scheduler.config, timestep_spacing="trailing"
        )
        pipeline = pipeline.to(self.device)
        self.model = pipeline

    def _load_era3d(self):
        """Load Era3D for consistent multi-view generation."""
        from diffusers import DiffusionPipeline

        pipeline = DiffusionPipeline.from_pretrained(
            "pengHTYX/Era3D_512_6views",
            torch_dtype=__import__("torch").float16 if self.device == "cuda" else __import__("torch").float32,
            trust_remote_code=True,
        )
        pipeline = pipeline.to(self.device)
        self.model = pipeline

    def _load_charactergen(self):
        """Load CharacterGen model."""
        from diffusers import StableDiffusionPipeline

        # CharacterGen uses a finetuned SD pipeline with view conditioning
        pipeline = StableDiffusionPipeline.from_pretrained(
            "fjbeing/CharacterGen",
            torch_dtype=__import__("torch").float16 if self.device == "cuda" else __import__("torch").float32,
            safety_checker=None,
        )
        pipeline = pipeline.to(self.device)
        self.model = pipeline

    def generate_views(
        self,
        person_image_path: str,
        save_dir: Optional[str] = None,
    ) -> Dict[str, Image.Image]:
        """
        Generate front, side, and back views of a person.

        Args:
            person_image_path: Path to the front-facing person photo
            save_dir: Optional directory to save view images

        Returns:
            Dict mapping view name to PIL Image: {"front": img, "side": img, "back": img}
        """
        if self.model is None:
            self.load_model()

        person_img = Image.open(person_image_path).convert("RGB")
        logger.info(f"Generating multi-view from: {person_image_path}")

        if self.model_type == "zero123pp":
            views = self._generate_zero123pp(person_img)
        elif self.model_type == "era3d":
            views = self._generate_era3d(person_img)
        elif self.model_type == "charactergen":
            views = self._generate_charactergen(person_img)
        else:
            views = self._generate_fallback(person_img)

        # Save if requested
        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            for view_name, img in views.items():
                save_path = Path(save_dir) / f"person_{view_name}.png"
                img.save(save_path)
                logger.info(f"Saved {view_name} view to: {save_path}")

        return views

    def _generate_zero123pp(self, person_img: Image.Image) -> Dict[str, Image.Image]:
        """Generate views using Zero123++."""
        # Zero123++ generates 6 views in a single pass as a grid
        result = self.model(
            person_img,
            num_inference_steps=75,
            guidance_scale=4.0,
        ).images[0]

        # Zero123++ outputs a 3x2 grid of views (6 views at fixed angles)
        # Views are: front-right, right, back-right, back-left, left, front-left
        w, h = result.size
        cell_w, cell_h = w // 3, h // 2

        # Extract the most relevant views
        views = {
            "front": person_img.resize((cell_w, cell_h)),  # Use original as front
            "side": result.crop((cell_w, 0, cell_w * 2, cell_h)),  # Right view
            "back": result.crop((cell_w * 2, 0, cell_w * 3, cell_h)),  # Back-right → approximate back
        }

        return views

    def _generate_era3d(self, person_img: Image.Image) -> Dict[str, Image.Image]:
        """Generate views using Era3D (6 consistent views)."""
        result = self.model(
            person_img,
            num_inference_steps=50,
            guidance_scale=3.0,
        )

        # Era3D generates 6 views; map to our 3 views
        generated_views = result.images  # List of 6 PIL Images
        views = {
            "front": person_img,
            "side": generated_views[1] if len(generated_views) > 1 else person_img,
            "back": generated_views[3] if len(generated_views) > 3 else person_img,
        }

        return views

    def _generate_charactergen(self, person_img: Image.Image) -> Dict[str, Image.Image]:
        """Generate views using CharacterGen."""
        views = {}
        view_prompts = {
            "front": "front view of the same person, full body",
            "side": "side view of the same person, full body, 90 degree angle",
            "back": "back view of the same person, full body, from behind",
        }

        for view_name, prompt in view_prompts.items():
            if view_name == "front":
                views[view_name] = person_img
                continue

            result = self.model(
                prompt=prompt,
                image=person_img,
                num_inference_steps=30,
                guidance_scale=7.5,
                strength=0.6,
            ).images[0]
            views[view_name] = result

        return views

    def _generate_fallback(self, person_img: Image.Image) -> Dict[str, Image.Image]:
        """
        Fallback: Return front view as-is and create placeholder side/back views.
        In production, you'd want to use one of the proper models above.
        """
        logger.warning("Using fallback multi-view generation (front only, placeholders for side/back)")

        w, h = person_img.size
        views = {
            "front": person_img,
            "side": Image.new("RGB", (w, h), (200, 200, 200)),  # Placeholder
            "back": Image.new("RGB", (w, h), (200, 200, 200)),  # Placeholder
        }

        # Add text overlay on placeholders
        try:
            from PIL import ImageDraw, ImageFont
            for view_name in ["side", "back"]:
                draw = ImageDraw.Draw(views[view_name])
                text = f"[{view_name.upper()} VIEW]\nRequires GPU model"
                draw.text((w // 4, h // 2), text, fill=(100, 100, 100))
        except Exception:
            pass

        return views
