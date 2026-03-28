# Server Architecture Documentation

## Overview

The AI Fit Check backend is a FastAPI application that provides REST endpoints for virtual try-on functionality. It orchestrates the pipeline: clothing segmentation → upscaling → virtual try-on via Fashn.ai API.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     iOS App Client                          │
│                   (SwiftUI App)                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                 HTTP/HTTPS (REST API)
                             │
                             ▼
        ┌────────────────────────────────────┐
        │   FastAPI Backend Server           │
        │   (main.py)                        │
        │                                    │
        │  • Person Management               │
        │  • Virtual Try-On Pipeline         │
        │  • Wardrobe/Closet Management      │
        └────────────────┬───────────────────┘
                         │
        ┌────────────────┴───────────────────┐
        │                                    │
        ▼                                    ▼
    ┌───────────────────┐          ┌─────────────────────┐
    │ Local Models      │          │ Fashn.ai API        │
    │                   │          │ (Cloud Service)     │
    │ • Segmentation    │          │                     │
    │   (Grounded SAM)  │          │ Virtual Try-On      │
    │   (rembg)         │          │ Generation          │
    └───────────────────┘          └─────────────────────┘
        │
        ▼
    ┌───────────────────┐
    │ File Storage      │
    │                   │
    │ • Person Images   │
    │ • Try-On Results  │
    │ • Metadata (JSON) │
    └───────────────────┘
```

## Component Details

### 1. Main Application (main.py)

**Responsibilities:**
- FastAPI application setup
- Route definitions and request handling
- Image encoding/decoding (base64)
- CORS middleware configuration
- Error handling and logging

**Key Classes/Functions:**
- `app`: FastAPI application instance
- `upload_person()`: POST /api/person
- `get_person()`: GET /api/person
- `virtual_tryon()`: POST /api/tryon
- `list_wardrobe()`: GET /api/wardrobe
- `save_to_wardrobe()`: POST /api/wardrobe
- `delete_from_wardrobe()`: DELETE /api/wardrobe/{id}

### 2. Configuration (config.py)

**Responsibilities:**
- Centralized configuration management
- Environment variable handling
- YAML configuration loading
- Configuration validation

**Key Class:**
- `Config`: Singleton configuration holder
  - Server settings (host, port, debug)
  - API credentials (Fashn.ai API key)
  - Model configuration
  - Directory paths
  - Timeout and limit settings

### 3. Health Monitoring (health.py)

**Responsibilities:**
- Server health monitoring
- Dependency checking
- Statistics tracking
- Uptime calculation

**Key Class:**
- `HealthMonitor`: Tracks server status
  - Request/error counting
  - Dependency verification
  - Environment information
  - Directory health checks

### 4. External Dependencies

#### AI Fit Check Modules
- `ai_fit_check.segmentation.ClothingSegmenter`
  - Segments clothing from images
  - Supports multiple backends (Grounded SAM, rembg, simple fallback)
  - Removes background with transparency

- `ai_fit_check.tryon.VirtualTryOn`
  - Integrates with Fashn.ai API
  - Converts images to base64
  - Polls API for results
  - Downloads completed try-on images

#### External APIs
- **Fashn.ai**: Virtual try-on generation
  - REST API endpoint: `https://api.fashn.ai/v1`
  - Authentication: Bearer token
  - Operations: `/run` (create), `/status/{id}` (check)

## Data Flow

### Try-On Request Flow

```
1. Client uploads clothing image
        ↓
2. Server receives upload
        ↓
3. Load saved person image from disk
        ↓
4. Segment clothing (remove background)
   - Convert image to PIL
   - Use ClothingSegmenter
   - Get RGBA image with transparency
        ↓
5. Call Fashn.ai API
   - Convert both images to base64
   - POST to /api/v1/run endpoint
   - Get prediction ID
        ↓
6. Poll Fashn.ai for result
   - GET /api/v1/status/{prediction_id}
   - Wait for status == "completed"
   - Handle timeout (120s default)
        ↓
7. Download result image
        ↓
8. Return base64-encoded result to client
```

### Wardrobe Management Flow

```
Upload Try-On Result
        ↓
Generate unique ID (UUID4)
        ↓
Save PNG image to disk
        ↓
Create metadata JSON file
  {
    "id": "uuid",
    "clothing_name": "...",
    "description": "...",
    "saved_at": "2024-03-27T...",
    "image_path": "uuid.png",
    "size": [width, height]
  }
        ↓
Return metadata to client
```

## Directory Structure

```
server/
├── main.py                 # FastAPI application (main entry point)
├── config.py              # Configuration management
├── health.py              # Health monitoring and diagnostics
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Multi-container orchestration
├── .env.example          # Example environment variables
├── start.sh              # Startup script for local dev
├── api_client_example.py # Python client example
├── README.md             # Full documentation
├── QUICKSTART.md         # Quick start guide
├── ARCHITECTURE.md       # This file
└── data/
    ├── persons/          # User person images
    │   └── person_*.png
    └── wardrobe/         # Saved try-on results
        ├── {uuid}.png    # Image
        └── {uuid}.json   # Metadata
```

## API Endpoints Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Server health and status |
| POST | `/api/person` | Upload person photo |
| GET | `/api/person` | Get current person photo |
| POST | `/api/tryon` | Perform virtual try-on |
| GET | `/api/wardrobe` | List wardrobe items |
| POST | `/api/wardrobe` | Save try-on to wardrobe |
| DELETE | `/api/wardrobe/{id}` | Delete wardrobe item |

## Deployment Architecture

### Local Development
```
Python Process
└── FastAPI + Uvicorn
    ├── Port 8000
    ├── Single worker
    └── Live reload
```

### Docker Container
```
Docker Container
└── Python 3.11 Slim
    ├── FastAPI + Uvicorn
    ├── Port 8000
    ├── Health checks
    └── Volume mounts for data
```

### Production (Recommended)
```
Docker Compose / Kubernetes
├── FastAPI backend (4+ workers)
├── Nginx reverse proxy
├── PostgreSQL (optional, for persistence)
├── Redis (optional, for caching)
└── Persistent volumes
```

## Performance Characteristics

### Try-On Operation
- Segmentation: 1-5s (Grounded SAM) or <100ms (rembg)
- API call setup: <100ms
- Fashn.ai processing: 10-30s (variable, depends on queue)
- Result download: 1-3s
- **Total: 15-40 seconds per try-on**

### Memory Usage
- Model loading: 2-4GB (Grounded SAM) or 500MB (rembg)
- Per request: 100-500MB (depending on image size)
- Runtime overhead: 200MB
- **Total: 2.5-4.5GB recommended**

### Concurrent Requests
- Single worker: ~1 try-on at a time (due to API limits)
- Multiple workers: Scales with Fashn.ai API limits
- Recommended: 4-8 workers for production

## Error Handling

### Graceful Degradation
- Segmentation failure → Use original image
- Model initialization failure → Log warning, continue
- API timeout → Return error to client with context

### Error Responses
```json
{
  "success": false,
  "detail": "Detailed error message",
  "timestamp": "2024-03-27T12:00:00"
}
```

## Security Considerations

1. **API Key Management**
   - Never commit .env files
   - Use environment variables
   - Rotate keys regularly

2. **CORS Configuration**
   - Restrict to specific domains in production
   - Currently allows all origins for development

3. **File Handling**
   - Validate file types
   - Limit file size (10MB default)
   - Clean up temporary files

4. **API Rate Limiting**
   - Implement per-client limiting in production
   - Monitor Fashn.ai API usage

## Monitoring & Logging

### Logging
- FastAPI logs all requests
- Application logs all operations
- Debug level available via LOG_LEVEL environment variable

### Health Checks
```bash
curl http://localhost:8000/health
```

Returns:
- Server status
- Uptime
- Request statistics
- Dependency status
- Model initialization state

### Metrics to Monitor
- API response times
- Error rates
- Segmentation success rate
- Fashn.ai API availability
- Disk usage (for stored images)
- Memory usage
- CPU usage (especially with GPU)

## Future Enhancements

1. **Caching**
   - Cache segmentation results
   - Cache Fashn.ai API responses
   - Redis integration

2. **Authentication**
   - OAuth2 / JWT tokens
   - User sessions
   - API key management

3. **Database**
   - Store user data in PostgreSQL
   - Wardrobe metadata persistence
   - User preferences

4. **Advanced Features**
   - Multi-view try-on (front, side, back)
   - Try-on history
   - Clothing recommendations
   - Social features (sharing)
   - Analytics and insights

5. **Performance**
   - Async processing with Celery
   - Background task queue
   - WebSocket updates
   - Image optimization

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Fashn.ai API Docs](https://api.fashn.ai/)
- [Docker Documentation](https://docs.docker.com/)
- [AI Fit Check Pipeline Modules](../ai_fit_check/)
