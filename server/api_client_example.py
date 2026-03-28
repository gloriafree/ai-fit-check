"""
Example API client for the AI Fit Check backend.
Demonstrates how to interact with all endpoints.
"""

import base64
import json
from pathlib import Path
from typing import Optional, Dict, List

import requests
from PIL import Image


class AIFitCheckClient:
    """Client for interacting with the AI Fit Check backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> Dict:
        """Get server health status."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def upload_person(self, image_path: str) -> Dict:
        """
        Upload a person's full-body photo.

        Args:
            image_path: Path to person image file

        Returns:
            Response with filename and confirmation
        """
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(f"{self.base_url}/api/person", files=files)
        response.raise_for_status()
        return response.json()

    def get_person(self) -> Dict:
        """
        Get the current stored person photo.

        Returns:
            Response with base64 image and metadata
        """
        response = self.session.get(f"{self.base_url}/api/person")
        response.raise_for_status()
        return response.json()

    def save_person_image(self, output_path: str) -> None:
        """
        Get person photo and save to file.

        Args:
            output_path: Path to save the image
        """
        data = self.get_person()
        if not data.get("success"):
            raise RuntimeError("Failed to get person image")

        # Decode base64 image
        img_b64 = data["image"]
        if img_b64.startswith("data:"):
            img_b64 = img_b64.split(",", 1)[1]

        # Save to file
        img_data = base64.b64decode(img_b64)
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"Saved person image to {output_path}")

    def perform_tryon(self, clothing_path: str) -> Dict:
        """
        Perform virtual try-on with uploaded clothing.

        Args:
            clothing_path: Path to clothing image

        Returns:
            Response with base64 try-on result image
        """
        with open(clothing_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(f"{self.base_url}/api/tryon", files=files)
        response.raise_for_status()
        return response.json()

    def save_tryon_result(self, tryon_result: str, output_path: str) -> None:
        """
        Save a try-on result to file.

        Args:
            tryon_result: Base64 image data
            output_path: Path to save the image
        """
        if tryon_result.startswith("data:"):
            tryon_result = tryon_result.split(",", 1)[1]

        img_data = base64.b64decode(tryon_result)
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"Saved try-on result to {output_path}")

    def list_wardrobe(self) -> Dict:
        """
        List all saved wardrobe items.

        Returns:
            Response with wardrobe items
        """
        response = self.session.get(f"{self.base_url}/api/wardrobe")
        response.raise_for_status()
        return response.json()

    def save_to_wardrobe(
        self,
        tryon_result: str,
        clothing_name: str,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Save a try-on result to the wardrobe.

        Args:
            tryon_result: Base64-encoded try-on image
            clothing_name: Name of the clothing item
            description: Optional description

        Returns:
            Response with saved item metadata
        """
        payload = {
            "tryon_result": tryon_result,
            "clothing_name": clothing_name,
            "description": description or "",
        }

        response = self.session.post(
            f"{self.base_url}/api/wardrobe",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def delete_from_wardrobe(self, item_id: str) -> Dict:
        """
        Delete an item from the wardrobe.

        Args:
            item_id: UUID of the wardrobe item

        Returns:
            Response confirming deletion
        """
        response = self.session.delete(f"{self.base_url}/api/wardrobe/{item_id}")
        response.raise_for_status()
        return response.json()

    def get_wardrobe_item(self, item_id: str, output_path: str) -> None:
        """
        Get a wardrobe item image and save to file.

        Args:
            item_id: UUID of the wardrobe item
            output_path: Path to save the image
        """
        items = self.list_wardrobe()
        item = next((i for i in items.get("items", []) if i["id"] == item_id), None)

        if not item:
            raise ValueError(f"Wardrobe item {item_id} not found")

        # In a real implementation, you would download the image from the server
        print(f"Wardrobe item found: {item['clothing_name']}")
        print(f"Image path: {item['image_path']}")


# Example usage
if __name__ == "__main__":
    # Create client
    client = AIFitCheckClient()

    print("=" * 60)
    print("AI Fit Check Backend - Example Client")
    print("=" * 60)

    # Health check
    print("\n1. Health Check")
    print("-" * 60)
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Timestamp: {health['timestamp']}")
        print(f"Models:")
        print(f"  - Segmenter: {health['models']['segmenter']}")
        print(f"  - Try-On: {health['models']['tryon']}")
    except Exception as e:
        print(f"ERROR: {e}")

    # Upload person (if image exists)
    print("\n2. Upload Person Image")
    print("-" * 60)
    test_person_path = "../data/input/person.jpg"
    if Path(test_person_path).exists():
        try:
            result = client.upload_person(test_person_path)
            print(f"SUCCESS: {result['message']}")
            print(f"Filename: {result['filename']}")
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print(f"SKIP: Test image not found at {test_person_path}")

    # Get person
    print("\n3. Get Person Image")
    print("-" * 60)
    try:
        person_data = client.get_person()
        print(f"SUCCESS: {person_data['message']}")
        print(f"Filename: {person_data['filename']}")
        print(f"Size: {person_data['size']}")
        # Save locally
        client.save_person_image("person_downloaded.png")
    except Exception as e:
        print(f"ERROR: {e}")

    # Try-on (if clothing image exists)
    print("\n4. Virtual Try-On")
    print("-" * 60)
    test_clothing_path = "../data/input/clothing.jpg"
    if Path(test_clothing_path).exists():
        try:
            result = client.perform_tryon(test_clothing_path)
            if result.get("success"):
                print(f"SUCCESS: {result['message']}")
                print(f"Result size: {result['size']}")
                # Save result
                client.save_tryon_result(result["result"], "tryon_result.png")
                tryon_result_b64 = result["result"]
            else:
                print(f"ERROR: {result}")
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print(f"SKIP: Test image not found at {test_clothing_path}")

    # Save to wardrobe
    print("\n5. Save to Wardrobe")
    print("-" * 60)
    if 'tryon_result_b64' in locals():
        try:
            result = client.save_to_wardrobe(
                tryon_result=tryon_result_b64,
                clothing_name="Test Clothing Item",
                description="A nice test item",
            )
            if result.get("success"):
                print(f"SUCCESS: {result['message']}")
                item = result["item"]
                print(f"Item ID: {item['id']}")
                print(f"Name: {item['clothing_name']}")
                saved_item_id = item["id"]
            else:
                print(f"ERROR: {result}")
        except Exception as e:
            print(f"ERROR: {e}")

    # List wardrobe
    print("\n6. List Wardrobe")
    print("-" * 60)
    try:
        wardrobe = client.list_wardrobe()
        print(f"Total items: {wardrobe['count']}")
        for item in wardrobe["items"][:3]:  # Show first 3
            print(f"  - {item['clothing_name']} ({item['id'][:8]}...)")
    except Exception as e:
        print(f"ERROR: {e}")

    # Delete from wardrobe
    print("\n7. Delete from Wardrobe")
    print("-" * 60)
    if 'saved_item_id' in locals():
        try:
            result = client.delete_from_wardrobe(saved_item_id)
            if result.get("success"):
                print(f"SUCCESS: {result['message']}")
            else:
                print(f"ERROR: {result}")
        except Exception as e:
            print(f"ERROR: {e}")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
