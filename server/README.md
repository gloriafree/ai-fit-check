# AI Fit Check Backend Server

FastAPI backend service for the AI Fit Check virtual try-on application. Handles virtual try-on operations, person image management, and wardrobe/closet storage.

## Features

- **Virtual Try-On**: Upload clothing images and see them on a saved person model
- **Person Management**: Store and retrieve a full-body person photo for reuse
- **Wardrobe/Closet**: Save and manage try-on results with metadata
- **Segmentation**: Automatic clothing segmentation using Grounded SAM or rembg
- **Fashn.ai Integration**: High-quality virtual try-on via Fashn.ai API
- **CORS Support**: Pre-configured for iOS app communication

## Architecture

```
Input Images
    ↓
Clothing Segmentation (removes background)
    ↓
Fashn.ai Virtual Try-On API
    ↓
Try-On Result Image
    ↓
Store in Wardrobe + Return to Client
```

## Installation

### Local Development

```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The server will start on `http://localhost:8000`

### Docker

```bash
# Build the Docker image
docker build -t ai-fit-check-backend .

# Run the container
docker run -p 8000:8000 \
  -e FASHN_API_KEY="your-api-key-here" \
  -v $(pwd)/data:/app/server/data \
  ai-fit-check-backend
```

### Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f ai-fit-check-backend

# Stop the service
docker-compose down
```

## Configuration

### Environment Variables

- `FASHN_API_KEY`: Fashn.ai API key (required for try-on operations)
- `PYTHONUNBUFFERED`: Set to 1 for real-time logging

### Config File

Main configuration is in `../configs/config.yaml`:

```yaml
fashn:
  api_key: "your-api-key"
  base_url: "https://api.fashn.ai/v1"
  model_id: "viton_hd"
  timeout: 120

segmentation:
  device: "cuda"  # or "cpu"
```

## API Endpoints

### Health Check
```
GET /health
```

Returns server status and model initialization state.

### Person Management

#### Upload/Update Person Photo
```
POST /api/person
Content-Type: multipart/form-data

Parameter: file (binary)
```

Response:
```json
{
  "success": true,
  "message": "Person image uploaded successfully",
  "filename": "person_20240327_120000.png",
  "timestamp": "2024-03-27T12:00:00"
}
```

#### Get Current Person Photo
```
GET /api/person
```

Response:
```json
{
  "success": true,
  "filename": "person_20240327_120000.png",
  "image": "data:image/png;base64,...",
  "size": [1024, 1536],
  "timestamp": "2024-03-27T12:00:00"
}
```

### Virtual Try-On

#### Perform Try-On
```
POST /api/tryon
Content-Type: multipart/form-data

Parameter: file (binary) - clothing image
```

Response:
```json
{
  "success": true,
  "message": "Virtual try-on completed successfully",
  "result": "data:image/png;base64,...",
  "size": [1024, 1536],
  "clothing_filename": "shirt.jpg",
  "timestamp": "2024-03-27T12:00:00"
}
```

### Wardrobe Management

#### List Wardrobe Items
```
GET /api/wardrobe
```

Response:
```json
{
  "success": true,
  "count": 3,
  "items": [
    {
      "id": "uuid-1234-5678",
      "clothing_name": "Blue Shirt",
      "description": "Casual blue shirt",
      "saved_at": "2024-03-27T12:00:00",
      "image_path": "uuid-1234-5678.png",
      "size": [1024, 1536]
    }
  ]
}
```

#### Save Try-On to Wardrobe
```
POST /api/wardrobe
Content-Type: application/json

{
  "tryon_result": "data:image/png;base64,...",
  "clothing_name": "Blue Shirt",
  "description": "Casual blue shirt"
}
```

Response:
```json
{
  "success": true,
  "message": "Item saved to wardrobe",
  "item": {
    "id": "uuid-1234-5678",
    "clothing_name": "Blue Shirt",
    "description": "Casual blue shirt",
    "saved_at": "2024-03-27T12:00:00",
    "image_path": "uuid-1234-5678.png",
    "size": [1024, 1536]
  }
}
```

#### Delete Wardrobe Item
```
DELETE /api/wardrobe/{item_id}
```

Response:
```json
{
  "success": true,
  "message": "Deleted wardrobe item uuid-1234-5678",
  "item_id": "uuid-1234-5678"
}
```

## Data Structure

### Directory Layout

```
server/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── README.md             # This file
└── data/
    ├── persons/          # Stored person images
    │   └── person_20240327_120000.png
    └── wardrobe/         # Wardrobe items and metadata
        ├── uuid-1234.png       # Try-on result image
        ├── uuid-1234.json      # Metadata
        ├── uuid-5678.png
        └── uuid-5678.json
```

### Wardrobe Metadata (JSON)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "clothing_name": "Blue Shirt",
  "description": "Casual blue shirt from the mall",
  "saved_at": "2024-03-27T12:00:00.123456",
  "image_path": "550e8400-e29b-41d4-a716-446655440000.png",
  "size": [1024, 1536]
}
```

## Usage Example (Python)

```python
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

# Upload person image
with open("person.jpg", "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/api/person",
        files={"file": f}
    )
print(resp.json())

# Perform try-on
with open("clothing.jpg", "rb") as f:
    resp = requests.post(
        f"{BASE_URL}/api/tryon",
        files={"file": f}
    )
result = resp.json()
print(f"Try-on result: {result['result'][:50]}...")

# Save to wardrobe
resp = requests.post(
    f"{BASE_URL}/api/wardrobe",
    json={
        "tryon_result": result["result"],
        "clothing_name": "Blue Shirt",
        "description": "Nice casual shirt"
    }
)
wardrobe_item = resp.json()["item"]
print(f"Saved to wardrobe: {wardrobe_item['id']}")

# List wardrobe
resp = requests.get(f"{BASE_URL}/api/wardrobe")
wardrobe = resp.json()
print(f"Wardrobe items: {wardrobe['count']}")

# Delete from wardrobe
resp = requests.delete(f"{BASE_URL}/api/wardrobe/{wardrobe_item['id']}")
print(resp.json())
```

## Usage Example (cURL)

```bash
# Upload person
curl -X POST http://localhost:8000/api/person \
  -F "file=@person.jpg"

# Perform try-on
curl -X POST http://localhost:8000/api/tryon \
  -F "file=@shirt.jpg" | jq .

# List wardrobe
curl http://localhost:8000/api/wardrobe | jq .

# Delete wardrobe item
curl -X DELETE http://localhost:8000/api/wardrobe/uuid-1234-5678
```

## Performance Considerations

### Virtual Try-On Timing
- Clothing segmentation: 1-5 seconds (Grounded SAM) or instant (rembg)
- Fashn.ai API call: 10-30 seconds (depending on API queue)
- Total: 15-40 seconds per try-on

### Memory Requirements
- Minimum: 4GB RAM (CPU mode with rembg)
- Recommended: 8GB+ RAM with GPU support
- GPU: NVIDIA GPU with CUDA support recommended

### Image Size
- Optimal input: 1024x1536 (portrait orientation)
- Supported: 512x768 to 2048x3072

## Troubleshooting

### Models Not Initialized
Check logs:
```bash
docker-compose logs -f ai-fit-check-backend
```

Common issues:
- Missing FASHN_API_KEY
- Missing model files in `../models/`
- Insufficient GPU memory

### Try-On Failures
1. Verify Fashn.ai API key is valid
2. Check if clothing is clearly visible in image
3. Ensure person image shows full body
4. Try with different image sizes

### Segmentation Issues
If clothing detection fails:
- Ensure good image lighting
- Make sure clothing is centered
- Try with simpler clothing items (solid colors)
- Fall back to manual cropping

## Development

### Adding New Endpoints

```python
@app.post("/api/new-endpoint")
async def new_endpoint(file: UploadFile = File(...)):
    """Documentation here."""
    try:
        # Your implementation
        return JSONResponse({"success": True})
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Logging

All operations are logged to stdout. Adjust log level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # For more verbose output
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit http://localhost:8000/docs (Swagger UI) or http://localhost:8000/redoc (ReDoc)

## Security Notes

- CORS is currently set to allow all origins. In production, restrict to specific domains:
  ```python
  allow_origins=["https://yourdomain.com"]
  ```
- API keys are loaded from environment variables
- File uploads are validated before processing
- Temporary files are cleaned up automatically

## License

Part of the AI Fit Check project.
