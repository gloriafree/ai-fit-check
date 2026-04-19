"""
FastAPI Backend for AI Fit Check Virtual Try-On App
====================================================

Lightweight server that calls Fashn.ai API for virtual try-on.
No PyTorch, no numpy, no heavy ML dependencies required.

Endpoints:
  POST /api/person       - Upload person's full-body photo
  GET  /api/person       - Get current person photo
  POST /api/tryon        - Virtual try-on (clothing image → result)
  GET  /api/wardrobe     - List saved outfits
  POST /api/wardrobe     - Save try-on result
  DELETE /api/wardrobe/{id} - Delete saved outfit
"""

import os
import io
import json
import time
import logging
import base64
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
import requests as http_requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from PIL import Image

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("ai_fit_check")

# ── Paths ────────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "configs" / "config.yaml"
DATA_DIR = Path(__file__).parent / "data"
PERSONS_DIR = DATA_DIR / "persons"
WARDROBE_DIR = DATA_DIR / "wardrobe"
PERSONS_DIR.mkdir(parents=True, exist_ok=True)
WARDROBE_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    try:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config not found at {CONFIG_PATH}, using env vars")
        return {}

config = load_config()
FASHN_API_KEY = config.get("fashn", {}).get("api_key") or os.getenv("FASHN_API_KEY", "")
FASHN_BASE_URL = config.get("fashn", {}).get("base_url") or "https://api.fashn.ai/v1"
FASHN_TIMEOUT = config.get("fashn", {}).get("timeout") or 120

if not FASHN_API_KEY:
    logger.warning("⚠️  No Fashn.ai API key configured! Set it in configs/config.yaml or FASHN_API_KEY env var.")

# ── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(title="AI Fit Check Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helpers ──────────────────────────────────────────────────────────────────

def pil_to_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """PIL Image → base64 data URI."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/{fmt.lower()};base64,{b64}"


def pil_to_raw_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """PIL Image → raw base64 string (no data: prefix)."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode()


def base64_to_pil(b64: str) -> Image.Image:
    """base64 string → PIL Image."""
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")


def resize_for_upload(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Resize image so longest side ≤ max_size."""
    w, h = image.size
    if max(w, h) <= max_size:
        return image
    ratio = max_size / max(w, h)
    return image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)


def get_latest_person_path() -> Optional[Path]:
    """Get the most recently uploaded person image."""
    files = sorted(PERSONS_DIR.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0] if files else None


# ── Fashn.ai API Client ─────────────────────────────────────────────────────

def fashn_tryon(person_img: Image.Image, clothing_img: Image.Image, category: str = "auto") -> Image.Image:
    """
    Call Fashn.ai API for virtual try-on.
    Returns the result as a PIL Image.
    """
    if not FASHN_API_KEY:
        raise RuntimeError("Fashn.ai API key not configured")

    headers = {
        "Authorization": f"Bearer {FASHN_API_KEY}",
        "Content-Type": "application/json",
    }

    # Resize before upload to save bandwidth
    person_img = resize_for_upload(person_img)
    clothing_img = resize_for_upload(clothing_img)

    payload = {
        "model_image": pil_to_base64(person_img),
        "garment_image": pil_to_base64(clothing_img),
        "category": category,
    }

    # Step 1: Create prediction
    logger.info("Calling Fashn.ai API...")
    resp = http_requests.post(f"{FASHN_BASE_URL}/run", headers=headers, json=payload, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(f"Fashn.ai API error ({resp.status_code}): {resp.text}")

    prediction_id = resp.json().get("id")
    logger.info(f"Prediction created: {prediction_id}")

    # Step 2: Poll for result
    start = time.time()
    while time.time() - start < FASHN_TIMEOUT:
        status_resp = http_requests.get(
            f"{FASHN_BASE_URL}/status/{prediction_id}",
            headers=headers,
            timeout=15,
        )
        data = status_resp.json()
        status = data.get("status", "")

        if status == "completed":
            output_url = (data.get("output") or [None])[0]
            if output_url:
                img_resp = http_requests.get(output_url, timeout=30)
                img_resp.raise_for_status()
                return Image.open(io.BytesIO(img_resp.content)).convert("RGB")
            raise RuntimeError("Prediction completed but no output found")

        if status == "failed":
            raise RuntimeError(f"Prediction failed: {data.get('error', 'unknown')}")

        logger.debug(f"  status={status}, elapsed={time.time()-start:.0f}s")
        time.sleep(2)

    raise TimeoutError(f"Fashn.ai prediction timed out after {FASHN_TIMEOUT}s")


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "api_key_set": bool(FASHN_API_KEY),
        "person_image_set": get_latest_person_path() is not None,
        "wardrobe_count": len(list(WARDROBE_DIR.glob("*.json"))),
        "timestamp": datetime.now().isoformat(),
    }


# ── Person Image ─────────────────────────────────────────────────────────────

@app.post("/api/person")
async def upload_person(file: UploadFile = File(...)):
    """Upload or update the user's full-body photo."""
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        image = resize_for_upload(image)

        filename = f"person_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = PERSONS_DIR / filename
        image.save(filepath)

        logger.info(f"Person image saved: {filepath} ({image.size})")
        return {"success": True, "filename": filename, "size": list(image.size)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/person")
async def get_person():
    """Get current person photo as base64."""
    path = get_latest_person_path()
    if not path:
        raise HTTPException(status_code=404, detail="No person image found. Upload one first via POST /api/person.")
    image = Image.open(path).convert("RGB")
    return {"success": True, "image": pil_to_raw_base64(image), "size": list(image.size)}


# ── Virtual Try-On ───────────────────────────────────────────────────────────

@app.post("/api/tryon")
async def virtual_tryon(file: UploadFile = File(...), category: str = Form("auto")):
    """
    Virtual try-on: upload clothing image → get try-on result.

    Requires a person image to be uploaded first via POST /api/person.
    """
    # Check person image exists
    person_path = get_latest_person_path()
    if not person_path:
        raise HTTPException(status_code=400, detail="No person image found. Upload one first via POST /api/person.")

    try:
        person_img = Image.open(person_path).convert("RGB")

        clothing_content = await file.read()
        clothing_img = Image.open(io.BytesIO(clothing_content)).convert("RGB")

        logger.info(f"Try-on request: person={person_img.size}, clothing={clothing_img.size}, category={category}")

        # Call Fashn.ai
        result = fashn_tryon(person_img, clothing_img, category=category)

        logger.info(f"Try-on success: result={result.size}")
        return {
            "success": True,
            "result": pil_to_raw_base64(result),
            "size": list(result.size),
            "timestamp": datetime.now().isoformat(),
        }
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"Try-on error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── Wardrobe ─────────────────────────────────────────────────────────────────

@app.get("/api/wardrobe")
async def list_wardrobe():
    """List all saved outfits."""
    items = []
    for meta_file in sorted(WARDROBE_DIR.glob("*.json"), reverse=True):
        try:
            with open(meta_file) as f:
                items.append(json.load(f))
        except Exception:
            pass
    return {"success": True, "count": len(items), "items": items}


@app.post("/api/wardrobe")
async def save_to_wardrobe(
    tryon_result: str = Form(...),
    clothing_name: str = Form("Untitled"),
    description: str = Form(""),
):
    """Save a try-on result to the wardrobe."""
    try:
        item_id = str(uuid.uuid4())
        image = base64_to_pil(tryon_result)
        image.save(WARDROBE_DIR / f"{item_id}.png")

        metadata = {
            "id": item_id,
            "clothing_name": clothing_name,
            "description": description,
            "saved_at": datetime.now().isoformat(),
            "image_file": f"{item_id}.png",
            "size": list(image.size),
        }
        with open(WARDROBE_DIR / f"{item_id}.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return {"success": True, "item": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/wardrobe/{item_id}")
async def delete_from_wardrobe(item_id: str):
    """Delete an outfit from the wardrobe."""
    deleted = 0
    for ext in ("png", "json"):
        p = WARDROBE_DIR / f"{item_id}.{ext}"
        if p.exists():
            p.unlink()
            deleted += 1
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return {"success": True, "deleted": item_id}


@app.get("/api/wardrobe/{item_id}/image")
async def get_wardrobe_image(item_id: str):
    """Get a wardrobe item's try-on result image as base64."""
    path = WARDROBE_DIR / f"{item_id}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    image = Image.open(path).convert("RGB")
    return {"success": True, "image": pil_to_raw_base64(image)}


# ── Root ─────────────────────────────────────────────────────────────────────

@app.get("/api")
async def api_root():
    """JSON endpoint for programmatic access."""
    return {
        "name": "AI Fit Check Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET  /health",
            "POST /api/person",
            "GET  /api/person",
            "POST /api/tryon",
            "GET  /api/wardrobe",
            "POST /api/wardrobe",
            "DELETE /api/wardrobe/{id}",
            "GET  /api/wardrobe/{id}/image",
        ],
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    person_set = get_latest_person_path() is not None
    api_key_set = bool(FASHN_API_KEY)
    wardrobe_count = len(list(WARDROBE_DIR.glob("*.json")))

    def dot(ok: bool) -> str:
        color = "#22c55e" if ok else "#ef4444"
        label = "Ready" if ok else "Not set"
        return f'<span style="color:{color}; font-weight:600;">&#9679; {label}</span>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Fit Check</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #0f172a; color: #e2e8f0; min-height: 100vh;
         display: flex; align-items: center; justify-content: center; }}
  .card {{ background: #1e293b; border-radius: 16px; padding: 48px;
           max-width: 600px; width: 100%; box-shadow: 0 25px 50px rgba(0,0,0,.4); }}
  h1 {{ font-size: 2rem; margin-bottom: 8px; color: #f8fafc; }}
  .subtitle {{ color: #94a3b8; margin-bottom: 32px; }}
  .status {{ background: #0f172a; border-radius: 10px; padding: 20px; margin-bottom: 28px; }}
  .status h2 {{ font-size: .85rem; text-transform: uppercase; letter-spacing: .08em;
                color: #64748b; margin-bottom: 12px; }}
  .status-row {{ display: flex; justify-content: space-between; padding: 6px 0;
                 font-size: .95rem; }}
  .status-label {{ color: #94a3b8; }}
  .endpoints {{ margin-bottom: 28px; }}
  .endpoints h2 {{ font-size: .85rem; text-transform: uppercase; letter-spacing: .08em;
                   color: #64748b; margin-bottom: 12px; }}
  .ep {{ display: flex; gap: 12px; padding: 8px 0; border-bottom: 1px solid #334155;
         font-size: .9rem; }}
  .ep:last-child {{ border-bottom: none; }}
  .method {{ font-weight: 700; min-width: 60px; }}
  .get {{ color: #22d3ee; }}  .post {{ color: #a78bfa; }}  .delete {{ color: #f87171; }}
  .path {{ color: #cbd5e1; }}
  .desc {{ color: #64748b; margin-left: auto; font-size: .85rem; }}
  .links {{ display: flex; gap: 12px; }}
  .links a {{ display: inline-block; padding: 10px 20px; border-radius: 8px;
              text-decoration: none; font-weight: 600; font-size: .9rem; transition: opacity .15s; }}
  .links a:hover {{ opacity: .85; }}
  .btn-primary {{ background: #6366f1; color: #fff; }}
  .btn-secondary {{ background: #334155; color: #e2e8f0; }}
</style>
</head>
<body>
<div class="card">
  <h1>AI Fit Check</h1>
  <p class="subtitle">Virtual try-on powered by Fashn.ai</p>

  <div class="status">
    <h2>Server Status</h2>
    <div class="status-row"><span class="status-label">API Key</span> {dot(api_key_set)}</div>
    <div class="status-row"><span class="status-label">Person Photo</span> {dot(person_set)}</div>
    <div class="status-row"><span class="status-label">Wardrobe</span>
      <span style="color:#e2e8f0; font-weight:600;">{wardrobe_count} item{"s" if wardrobe_count != 1 else ""}</span>
    </div>
  </div>

  <div class="endpoints">
    <h2>API Endpoints</h2>
    <div class="ep"><span class="method get">GET</span>  <span class="path">/health</span>           <span class="desc">Server health</span></div>
    <div class="ep"><span class="method post">POST</span> <span class="path">/api/person</span>      <span class="desc">Upload person photo</span></div>
    <div class="ep"><span class="method get">GET</span>  <span class="path">/api/person</span>       <span class="desc">Get person photo</span></div>
    <div class="ep"><span class="method post">POST</span> <span class="path">/api/tryon</span>       <span class="desc">Virtual try-on</span></div>
    <div class="ep"><span class="method get">GET</span>  <span class="path">/api/wardrobe</span>     <span class="desc">List wardrobe</span></div>
    <div class="ep"><span class="method post">POST</span> <span class="path">/api/wardrobe</span>    <span class="desc">Save outfit</span></div>
    <div class="ep"><span class="method delete">DEL</span> <span class="path">/api/wardrobe/{{id}}</span> <span class="desc">Delete outfit</span></div>
  </div>

  <div class="links">
    <a href="/docs" class="btn-primary">Swagger Docs</a>
    <a href="/api" class="btn-secondary">JSON API</a>
    <a href="/health" class="btn-secondary">Health Check</a>
  </div>
</div>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
