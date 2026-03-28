"""
Step 4: Virtual Try-On via Fashn.ai API
=========================================
Sends person image + clothing image to Fashn.ai API and retrieves
the try-on result.
"""

import io
import time
import base64
import logging
from pathlib import Path
from typing import Optional, Dict

import requests
from PIL import Image

logger = logging.getLogger(__name__)

FASHN_BASE_URL = "https://api.fashn.ai/v1"


class VirtualTryOn:
    """Virtual try-on using Fashn.ai API."""

    def __init__(self, config: dict):
        fashn_config = config.get("fashn", {})
        self.api_key = fashn_config.get("api_key", "")
        self.base_url = fashn_config.get("base_url", FASHN_BASE_URL)
        self.timeout = fashn_config.get("timeout", 120)
        self.model_id = fashn_config.get("model_id", "viton_hd")

        if not self.api_key:
            raise ValueError("Fashn.ai API key is required. Set it in configs/config.yaml")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def try_on(
        self,
        person_image: Image.Image,
        clothing_image: Image.Image,
        category: str = "auto",
        save_dir: Optional[str] = None,
        view_name: str = "front",
    ) -> Image.Image:
        """
        Perform virtual try-on for a single view.

        Args:
            person_image: PIL Image of the person
            clothing_image: PIL Image of the clothing item (segmented)
            category: Clothing category - "tops", "bottoms", "one-pieces", or "auto"
            save_dir: Optional directory to save result
            view_name: Name of the view (for saving)

        Returns:
            PIL Image with the clothing applied to the person
        """
        logger.info(f"Starting virtual try-on for {view_name} view...")

        # Convert images to base64
        person_b64 = self._image_to_base64(person_image)
        clothing_b64 = self._image_to_base64(clothing_image)

        # Start prediction
        prediction_id = self._create_prediction(person_b64, clothing_b64, category)
        logger.info(f"Prediction created: {prediction_id}")

        # Poll for result
        result_image = self._poll_prediction(prediction_id)
        logger.info(f"Try-on completed for {view_name} view.")

        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            save_path = Path(save_dir) / f"tryon_{view_name}.png"
            result_image.save(save_path)
            logger.info(f"Saved try-on result to: {save_path}")

        return result_image

    def try_on_multiview(
        self,
        person_views: Dict[str, Image.Image],
        clothing_image: Image.Image,
        category: str = "auto",
        save_dir: Optional[str] = None,
    ) -> Dict[str, Image.Image]:
        """
        Perform virtual try-on for multiple views.

        Args:
            person_views: Dict of {view_name: person_image}
            clothing_image: Segmented clothing image
            category: Clothing category
            save_dir: Optional save directory

        Returns:
            Dict of {view_name: try_on_result_image}
        """
        results = {}

        for view_name, person_img in person_views.items():
            logger.info(f"Processing {view_name} view ({list(person_views.keys()).index(view_name) + 1}/{len(person_views)})...")

            try:
                result = self.try_on(
                    person_image=person_img,
                    clothing_image=clothing_image,
                    category=category,
                    save_dir=save_dir,
                    view_name=view_name,
                )
                results[view_name] = result
            except Exception as e:
                logger.error(f"Try-on failed for {view_name} view: {e}")
                results[view_name] = person_img  # Fallback to original

        return results

    def _create_prediction(self, person_b64: str, clothing_b64: str, category: str) -> str:
        """Create a new try-on prediction via Fashn.ai API."""
        payload = {
            "model_image": person_b64,
            "garment_image": clothing_b64,
            "category": category,
        }

        response = requests.post(
            f"{self.base_url}/run",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            error_msg = response.text
            raise RuntimeError(f"Fashn.ai API error ({response.status_code}): {error_msg}")

        data = response.json()
        return data["id"]

    def _poll_prediction(self, prediction_id: str, poll_interval: float = 2.0) -> Image.Image:
        """Poll for prediction result until completed or timeout."""
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            response = requests.get(
                f"{self.base_url}/status/{prediction_id}",
                headers=self.headers,
                timeout=15,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Status check failed: {response.text}")

            data = response.json()
            status = data.get("status", "")

            if status == "completed":
                output_url = data.get("output", [None])[0]
                if output_url:
                    return self._download_image(output_url)
                # If output is base64 instead of URL
                output_b64 = data.get("output_b64")
                if output_b64:
                    return self._base64_to_image(output_b64)
                raise RuntimeError("Prediction completed but no output found")

            elif status == "failed":
                error = data.get("error", "Unknown error")
                raise RuntimeError(f"Prediction failed: {error}")

            logger.debug(f"Status: {status}, elapsed: {time.time() - start_time:.0f}s")
            time.sleep(poll_interval)

        raise TimeoutError(f"Prediction timed out after {self.timeout}s")

    def _download_image(self, url: str) -> Image.Image:
        """Download an image from URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 data URI."""
        # Ensure RGB mode for API
        if image.mode == "RGBA":
            # Composite onto white background
            bg = Image.new("RGB", image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[3])
            image = bg
        elif image.mode != "RGB":
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def _base64_to_image(self, b64_string: str) -> Image.Image:
        """Convert base64 string to PIL Image."""
        if b64_string.startswith("data:"):
            b64_string = b64_string.split(",", 1)[1]
        image_data = base64.b64decode(b64_string)
        return Image.open(io.BytesIO(image_data)).convert("RGB")
