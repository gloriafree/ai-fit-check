# AI Fit Check

Screenshot a piece of clothing, AI tries it on you, and shows front/side/back views.

The project has three parts: a **ML pipeline** for local virtual try-on, a **FastAPI server** that exposes the pipeline as an API, and an **iOS app** with a Share Extension so you can try on clothes from any app.

## Project Structure

```
ai_fit_check/
├── ai_fit_check/           # ML pipeline package
│   ├── segmentation.py     # Grounded SAM clothing segmentation
│   ├── super_resolution.py # Real-ESRGAN upscaling
│   ├── multiview_gen.py    # Multi-view person generation
│   ├── tryon.py            # Fashn.ai virtual try-on
│   ├── lighting.py         # IC-Light harmonization
│   └── pipeline.py         # Pipeline orchestrator
├── server/                 # FastAPI backend (see server/README.md)
│   ├── main.py             # API server
│   ├── Dockerfile
│   └── docker-compose.yml
├── ios/                    # SwiftUI iOS app (see ios/SETUP_GUIDE.md)
│   ├── AIFitCheck/         # Main app + Share Extension
│   └── AIFitCheck.xcodeproj
├── configs/
│   └── config.yaml         # API keys, model params
├── data/
│   ├── input/              # Clothing screenshots
│   ├── output/             # Results
│   └── person_images/      # Your photos
├── models/                 # Downloaded model weights
├── scripts/
│   ├── setup.sh            # Full setup (GPU + all models)
│   ├── setup_lite.sh       # Lite setup (CPU, smaller download)
│   ├── test_fashn_api.py   # API connectivity test
│   └── download_examples.py
├── run.py                  # CLI entry point
├── requirements.txt        # Full dependencies
└── requirements-lite.txt   # Lite dependencies (CPU only)
```

## Pipeline

```
Screenshot ──→ [Grounded SAM] ──→ [Real-ESRGAN] ──→ [CharacterGen] ──→ [Fashn.ai] ──→ [IC-Light] ──→ 3-view output
 clothing       segmentation       upscale            multi-view          try-on         lighting      front/side/back
```

## Quick Start

### 1. Setup

```bash
cd ai_fit_check

# Full setup (GPU, all models)
bash scripts/setup.sh
source venv/bin/activate

# Or lite setup (CPU only, smaller download)
bash scripts/setup_lite.sh
source venv/bin/activate
```

### 2. Test API Connection

```bash
python scripts/test_fashn_api.py
```

### 3. Prepare Images

- `data/input/` — clothing screenshots
- `data/person_images/` — full-body photos (front-facing, even lighting, natural pose)

### 4. Run Try-On

```bash
# Full pipeline (3 views)
python run.py --clothing data/input/dress.png --person data/person_images/me.jpg

# Quick mode (front view only, faster)
python run.py --clothing data/input/dress.png --person data/person_images/me.jpg --skip-multiview

# Specify clothing category
python run.py --clothing screenshot.png --person me.jpg --category tops
```

### 5. Check Results

Output is saved to `data/output/<timestamp>/`:
- `front.png`, `side.png`, `back.png`
- `combined_3view.png` — all three views side by side

## Server

The FastAPI server wraps the pipeline into a REST API with person management and wardrobe storage. Supports Docker deployment.

```bash
cd server
pip install -r requirements.txt
python main.py
# Server runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

See [server/README.md](server/README.md) for API endpoints, Docker setup, and configuration. Also: [server/QUICKSTART.md](server/QUICKSTART.md), [server/ARCHITECTURE.md](server/ARCHITECTURE.md), [server/DEPLOYMENT.md](server/DEPLOYMENT.md).

## iOS App

SwiftUI app with a Share Extension — share a clothing image from any app (Safari, Instagram, Taobao) to try it on.

- **Home**: Instructions and quick try-on
- **Wardrobe**: Saved try-on results
- **Profile**: Person photo upload and server settings

See [ios/SETUP_GUIDE.md](ios/SETUP_GUIDE.md) and [ios/AIFitCheck/README.md](ios/AIFitCheck/README.md) for Xcode setup and architecture details.

## Configuration

Edit `configs/config.yaml`:

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
