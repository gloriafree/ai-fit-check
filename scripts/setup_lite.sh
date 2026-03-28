#!/bin/bash
# AI Fit Check - Lite Setup (No GPU / No PyTorch)
# =================================================
# Use this on Mac or any machine without NVIDIA GPU.
# Uses Fashn.ai API for try-on + rembg for segmentation.

set -e

echo "🔥 AI Fit Check - Lite Setup (API mode)"
echo "========================================"

# 1. Create virtual environment
echo ""
echo "▶ Step 1: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip
echo ""
echo "▶ Step 2: Upgrading pip..."
pip install --upgrade pip

# 3. Install lite dependencies (no PyTorch!)
echo ""
echo "▶ Step 3: Installing dependencies..."
pip install -r requirements-lite.txt

echo ""
echo "========================================"
echo "✅ Lite setup complete!"
echo ""
echo "To activate:"
echo "  source venv/bin/activate"
echo ""
echo "To test API:"
echo "  python scripts/test_fashn_api.py"
echo ""
echo "To run (front view only, recommended for lite mode):"
echo "  python run.py -c screenshot.png -p my_photo.jpg --skip-multiview"
echo ""
echo "To run full 3-view (multi-view uses placeholder for side/back):"
echo "  python run.py -c screenshot.png -p my_photo.jpg"
