# AI Fit Check - Virtual Try-On Pipeline

一键截图衣服 → AI 虚拟试穿 → 三视图展示

## Pipeline Architecture

```
截图/图片 ──→ [1. Grounded SAM] ──→ [2. Real-ESRGAN] ──→ [3. CharacterGen] ──→ [4. Fashn.ai] ──→ [5. IC-Light] ──→ 三视图输出
  衣服图片      衣服分割/抠图         超分辨率增强          多角度人物生成        虚拟试穿API         光影统一          front/side/back
```

## Quick Start

### 1. Setup Environment

```bash
# Clone and enter project
cd ai_fit_check

# Run setup script (installs everything)
chmod +x scripts/setup.sh
bash scripts/setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Test API Connection

```bash
python scripts/test_fashn_api.py
```

### 3. Prepare Your Images

Put your images in the `data/` folder:
- `data/input/` — clothing screenshots
- `data/person_images/` — your full-body photos (front-facing, even lighting, natural pose)

### 4. Run Try-On

```bash
# Full pipeline (3 views)
python run.py --clothing data/input/dress.png --person data/person_images/me.jpg

# Quick mode (front view only, faster)
python run.py --clothing data/input/dress.png --person data/person_images/me.jpg --skip-multiview

# Specify clothing category for better results
python run.py --clothing screenshot.png --person me.jpg --category tops
```

### 5. Check Results

Output is saved to `data/output/<timestamp>/`:
- `front.png` — front view
- `side.png` — side view
- `back.png` — back view
- `combined_3view.png` — all three views side by side

## Project Structure

```
ai_fit_check/
├── ai_fit_check/           # Main package
│   ├── __init__.py
│   ├── segmentation.py     # Step 1: Grounded SAM clothing segmentation
│   ├── super_resolution.py # Step 2: Real-ESRGAN upscaling
│   ├── multiview_gen.py    # Step 3: Multi-view person generation
│   ├── tryon.py            # Step 4: Fashn.ai virtual try-on
│   ├── lighting.py         # Step 5: IC-Light harmonization
│   └── pipeline.py         # Main pipeline orchestrator
├── configs/
│   └── config.yaml         # All configuration (API keys, model params)
├── data/
│   ├── input/              # Clothing screenshots go here
│   ├── output/             # Results saved here
│   └── person_images/      # Your photos go here
├── models/                 # Downloaded model weights
├── scripts/
│   ├── setup.sh            # One-click setup
│   └── test_fashn_api.py   # API connectivity test
├── run.py                  # CLI entry point
└── requirements.txt        # Python dependencies
```

## Configuration

Edit `configs/config.yaml` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `fashn.api_key` | — | Your Fashn.ai API key |
| `segmentation.device` | cuda | GPU device (cuda/cpu) |
| `super_resolution.target_size` | 1024 | Output image size |
| `pipeline.save_intermediate` | true | Save each step's output |

## Hardware Requirements

| Mode | GPU | RAM | Time/run |
|------|-----|-----|----------|
| Full pipeline (3 views) | A6000 48GB+ | 32GB | ~40-60s |
| Front-only (--skip-multiview) | RTX 3090 24GB | 16GB | ~15-20s |
| CPU fallback (slow) | None | 16GB | ~5-10min |

## Clothing Categories

| Category | Use for |
|----------|---------|
| `tops` | T-shirts, shirts, blouses, jackets, sweaters |
| `bottoms` | Pants, skirts, shorts |
| `one-pieces` | Dresses, jumpsuits, overalls |
| `auto` | Let the AI detect (default) |

## Tips for Best Results

**Person photos:**
- Full body, front-facing
- Arms slightly away from body
- Even lighting, plain background
- Natural standing pose

**Clothing screenshots:**
- Clean product images work best
- Avoid heavy watermarks
- Higher resolution = better texture detail
