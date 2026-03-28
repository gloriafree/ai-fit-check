#!/usr/bin/env python3
"""
Download real example images for testing the AI Fit Check pipeline.

Sources:
  - Person photos: Pexels (free license, no attribution required)
  - Clothing images: Pexels (free license)
  - VITON-HD dataset: Academic benchmark (CC BY-NC 4.0)

Usage:
    python scripts/download_examples.py
    python scripts/download_examples.py --viton  # Also download VITON-HD test samples
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests


PERSON_IMAGES = [
    # Full body, front-facing, clean background - ideal for virtual try-on
    {
        "url": "https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "person_woman_casual.jpg",
        "description": "Woman standing, casual outfit, front-facing",
    },
    {
        "url": "https://images.pexels.com/photos/1462637/pexels-photo-1462637.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "person_woman_standing.jpg",
        "description": "Woman full body, standing pose",
    },
    {
        "url": "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "person_man_casual.jpg",
        "description": "Man standing, casual outfit",
    },
    {
        "url": "https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "person_woman_professional.jpg",
        "description": "Woman standing, professional outfit",
    },
]

CLOTHING_IMAGES = [
    # Product shots of clothing items
    {
        "url": "https://images.pexels.com/photos/6311392/pexels-photo-6311392.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "clothing_dress_blue.jpg",
        "description": "Blue dress, product shot",
    },
    {
        "url": "https://images.pexels.com/photos/6311652/pexels-photo-6311652.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "clothing_top_white.jpg",
        "description": "White top, product shot",
    },
    {
        "url": "https://images.pexels.com/photos/6764007/pexels-photo-6764007.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "clothing_jacket.jpg",
        "description": "Jacket, product shot",
    },
    {
        "url": "https://images.pexels.com/photos/4066293/pexels-photo-4066293.jpeg?auto=compress&cs=tinysrgb&w=1024",
        "filename": "clothing_shirt_striped.jpg",
        "description": "Striped shirt, product shot",
    },
]


def download_file(url: str, save_path: str, description: str) -> bool:
    """Download a file from URL."""
    try:
        resp = requests.get(url, timeout=30, stream=True, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        resp.raise_for_status()

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = os.path.getsize(save_path) / 1024
        print(f"  ✅ {description} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  ❌ {description}: {e}")
        return False


def download_pexels_examples():
    """Download example images from Pexels."""
    base_dir = Path(__file__).parent.parent / "data"

    print("\n📸 Downloading person images (Pexels, free license)...")
    person_dir = base_dir / "person_images"
    for img in PERSON_IMAGES:
        download_file(img["url"], str(person_dir / img["filename"]), img["description"])

    print("\n👗 Downloading clothing images (Pexels, free license)...")
    input_dir = base_dir / "input"
    for img in CLOTHING_IMAGES:
        download_file(img["url"], str(input_dir / img["filename"]), img["description"])


def download_viton_hd_samples():
    """Download a few test pairs from VITON-HD dataset (CC BY-NC 4.0)."""
    print("\n📦 VITON-HD Academic Dataset")
    print("  The VITON-HD dataset contains 13,679 person-clothing pairs at 1024x768.")
    print("  License: CC BY-NC 4.0 (non-commercial use)")
    print("")
    print("  To download the full dataset:")
    print("  1. Visit: https://github.com/shadow2496/VITON-HD")
    print("  2. Follow the download instructions in their README")
    print("  3. Place test images in data/viton_hd/")
    print("")
    print("  Alternatively, use the Dress Code dataset (50K+ pairs):")
    print("  https://github.com/aimagelab/dress-code")


def main():
    parser = argparse.ArgumentParser(description="Download example images for AI Fit Check")
    parser.add_argument("--viton", action="store_true", help="Show VITON-HD dataset download info")
    args = parser.parse_args()

    print("🔥 AI Fit Check - Example Image Downloader")
    print("=" * 50)

    download_pexels_examples()

    if args.viton:
        download_viton_hd_samples()

    print("\n" + "=" * 50)
    print("✅ Done! Example images saved to data/")
    print("")
    print("Now you can test the pipeline:")
    print("  python run.py \\")
    print("    --clothing data/input/clothing_dress_blue.jpg \\")
    print("    --person data/person_images/person_woman_casual.jpg \\")
    print("    --skip-multiview")


if __name__ == "__main__":
    main()
