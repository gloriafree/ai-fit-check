#!/bin/bash
# AI Fit Check - Setup Script
# ============================
# Run this on your GPU machine (local or cloud) to set up the environment.

set -e

echo "🔥 AI Fit Check - Environment Setup"
echo "===================================="

# 1. Create virtual environment
echo ""
echo "▶ Step 1: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install PyTorch with CUDA
echo ""
echo "▶ Step 2: Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Install core dependencies
echo ""
echo "▶ Step 3: Installing core dependencies..."
pip install -r requirements.txt

# 4. Install Grounded SAM 2
echo ""
echo "▶ Step 4: Installing Grounded SAM 2..."
pip install segment-anything-2
pip install groundingdino-py

# 5. Install Real-ESRGAN
echo ""
echo "▶ Step 5: Installing Real-ESRGAN..."
pip install realesrgan

# 6. Download model weights
echo ""
echo "▶ Step 6: Downloading model weights..."
mkdir -p models

# SAM 2 weights
echo "  Downloading SAM 2.1 Large..."
wget -q -O models/sam2.1_hiera_large.pt \
    https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt

# Grounding DINO weights
echo "  Downloading Grounding DINO..."
wget -q -O models/groundingdino_swinb_cogcoor.pth \
    https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth

# Real-ESRGAN weights (auto-downloads on first use, but pre-download for speed)
echo "  Downloading Real-ESRGAN x4plus..."
wget -q -O models/RealESRGAN_x4plus.pth \
    https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth

echo ""
echo "===================================="
echo "✅ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run a try-on:"
echo "  python run.py --clothing screenshot.png --person my_photo.jpg"
echo ""
echo "Quick test (front view only, faster):"
echo "  python run.py --clothing screenshot.png --person my_photo.jpg --skip-multiview"
