#!/usr/bin/env python3
"""
AI Fit Check - CLI Entry Point
================================
Run the virtual try-on pipeline from the command line.

Usage:
    python run.py --clothing screenshot.png --person my_photo.jpg
    python run.py --clothing screenshot.png --person my_photo.jpg --category tops
    python run.py --clothing screenshot.png --person my_photo.jpg --output my_outfit
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="AI Fit Check - Virtual Try-On Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic try-on
  python run.py --clothing data/input/dress.png --person data/person_images/me.jpg

  # Specify clothing category for better results
  python run.py --clothing screenshot.png --person me.jpg --category tops

  # Custom output name
  python run.py --clothing screenshot.png --person me.jpg --output date_outfit

  # Skip steps for faster iteration
  python run.py --clothing screenshot.png --person me.jpg --skip-multiview

Categories:
  tops        - T-shirts, shirts, blouses, jackets, sweaters
  bottoms     - Pants, skirts, shorts
  one-pieces  - Dresses, jumpsuits, overalls
  auto        - Auto-detect (default)
        """,
    )

    parser.add_argument(
        "--clothing", "-c",
        required=True,
        help="Path to clothing screenshot or image",
    )
    parser.add_argument(
        "--person", "-p",
        required=True,
        help="Path to person's full-body photo",
    )
    parser.add_argument(
        "--category", "-cat",
        default="auto",
        choices=["tops", "bottoms", "one-pieces", "auto"],
        help="Clothing category (default: auto)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output name (default: timestamp)",
    )
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to config file (default: configs/config.yaml)",
    )
    parser.add_argument(
        "--skip-multiview",
        action="store_true",
        help="Skip multi-view generation, only do front view try-on",
    )
    parser.add_argument(
        "--skip-upscale",
        action="store_true",
        help="Skip super-resolution upscaling step",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.clothing).exists():
        print(f"Error: Clothing image not found: {args.clothing}")
        sys.exit(1)
    if not Path(args.person).exists():
        print(f"Error: Person image not found: {args.person}")
        sys.exit(1)
    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)

    # Set log level
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    # Import and run pipeline
    from ai_fit_check.pipeline import FitCheckPipeline

    print("\n🔥 AI Fit Check - Virtual Try-On")
    print("=" * 40)
    print(f"  Clothing: {args.clothing}")
    print(f"  Person:   {args.person}")
    print(f"  Category: {args.category}")
    print("=" * 40 + "\n")

    pipeline = FitCheckPipeline(config_path=args.config)

    if args.skip_multiview:
        # Quick mode: front view only
        print("⚡ Quick mode: front view only (--skip-multiview)")
        _run_front_only(pipeline, args)
    else:
        # Full pipeline
        results = pipeline.run(
            clothing_image_path=args.clothing,
            person_image_path=args.person,
            category=args.category,
            output_name=args.output,
        )

    print("\n✅ Done! Check the output directory for results.")


def _run_front_only(pipeline, args):
    """Run pipeline with front view only (faster)."""
    import os
    from datetime import datetime
    from PIL import Image

    output_name = args.output or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(pipeline.output_dir) / output_name
    os.makedirs(run_dir, exist_ok=True)

    # Step 1: Segment
    print("▶ Step 1: Segmenting clothing...")
    segmented = pipeline.segmenter.segment(args.clothing)

    # Step 2: Upscale (optional)
    if not args.skip_upscale:
        print("▶ Step 2: Upscaling...")
        segmented = pipeline.upscaler.upscale(segmented)
    else:
        print("▶ Step 2: Skipped (--skip-upscale)")

    # Step 3: Try-on (front only)
    print("▶ Step 3: Virtual try-on (front view)...")
    person_img = Image.open(args.person).convert("RGB")
    result = pipeline.tryon.try_on(
        person_image=person_img,
        clothing_image=segmented,
        category=args.category,
        save_dir=str(run_dir),
        view_name="front",
    )

    save_path = run_dir / "front.png"
    result.save(save_path)
    print(f"\n📁 Output: {save_path}")


if __name__ == "__main__":
    main()
