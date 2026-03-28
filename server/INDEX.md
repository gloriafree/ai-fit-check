# AI Fit Check Backend - File Index

Complete guide to all files in the server directory.

## Core Application Files

### `main.py` (Main Entry Point)
**Size:** ~600 lines | **Type:** Python
**Purpose:** FastAPI application with all REST API endpoints

**Key Components:**
- FastAPI app initialization
- CORS middleware setup
- 7 API endpoints (person, tryon, wardrobe management)
- Error handlers
- Utility functions for image encoding/decoding
- Health check endpoint

**Entry Point:** `if __name__ == "__main__": uvicorn.run(app, ...)`

**Usage:**
```bash
python main.py  # Runs on http://localhost:8000
```

---

### `config.py` (Configuration Management)
**Size:** ~150 lines | **Type:** Python
**Purpose:** Centralized configuration from environment, .env, and YAML

**Key Components:**
- `Config` class with all settings
- Server config (host, port, debug)
- Fashn.ai API configuration
- File path definitions
- CORS settings
- Validation methods

**Usage:**
```python
from config import Config
Config.load()  # Load from all sources
Config.validate()  # Verify settings
```

---

### `health.py` (Health Monitoring)
**Size:** ~150 lines | **Type:** Python
**Purpose:** Server health checks and system monitoring

**Key Components:**
- `HealthMonitor` class
- Uptime tracking
- Dependency verification
- Request/error statistics
- System information gathering

**Usage:**
```python
from health import monitor, get_health_report
status = monitor.get_status()
report = get_health_report()
```

---

## Configuration & Environment

### `.env.example` (Environment Template)
**Size:** ~20 lines | **Type:** Configuration
**Purpose:** Template for environment variables

**Content:**
- Fashn.ai API key placeholder
- Python configuration
- Server settings
- Device configuration
- Log level setting

**Usage:**
```bash
cp .env.example .env
nano .env  # Edit with your values
```

---

### `requirements.txt` (Python Dependencies)
**Size:** ~10 lines | **Type:** Requirements
**Purpose:** Python package dependencies for pip

**Packages:**
- fastapi (0.104.1)
- uvicorn (0.24.0)
- python-multipart (0.0.6)
- aiofiles (23.2.1)
- Pillow (10.1.0)
- pyyaml (6.0.1)
- requests (2.31.0)

**Usage:**
```bash
pip install -r requirements.txt
```

---

## Docker & Container Files

### `Dockerfile` (Container Image)
**Size:** ~50 lines | **Type:** Docker
**Purpose:** Multi-stage Docker build configuration

**Stages:**
1. Base image setup (Python 3.11-slim + system deps)
2. Builder stage (install Python packages)
3. Runtime stage (minimal final image)

**Features:**
- Multi-stage build for smaller image
- System dependencies for image processing
- Health check configuration
- Proper signal handling

**Usage:**
```bash
docker build -t ai-fit-check-backend .
docker run -p 8000:8000 ai-fit-check-backend
```

---

### `docker-compose.yml` (Container Orchestration)
**Size:** ~40 lines | **Type:** Docker Compose
**Purpose:** Define and run multi-container application

**Services:**
- `ai-fit-check-backend`: Main application service
- Optional: nginx reverse proxy (commented)

**Features:**
- Volume mounts for data persistence
- Environment variable configuration
- Health checks
- Auto-restart policy

**Usage:**
```bash
docker-compose up -d      # Start services
docker-compose logs -f    # View logs
docker-compose down       # Stop services
```

---

## Scripts & Utilities

### `start.sh` (Startup Script)
**Size:** ~70 lines | **Type:** Bash
**Purpose:** Convenient startup script for local development

**Features:**
- Checks for .env file
- Creates virtual environment
- Installs dependencies
- Creates data directories
- Validates configuration
- Starts server with informative output

**Usage:**
```bash
chmod +x start.sh
./start.sh
```

---

### `api_client_example.py` (Python Client Example)
**Size:** ~300 lines | **Type:** Python
**Purpose:** Complete example of how to use the API from Python

**Key Components:**
- `AIFitCheckClient` class
- Methods for all endpoints
- Helper functions for file operations
- Example usage script
- Error handling

**Methods:**
- `health_check()` - GET health
- `upload_person()` - POST person
- `get_person()` - GET person
- `perform_tryon()` - POST tryon
- `list_wardrobe()` - GET wardrobe
- `save_to_wardrobe()` - POST wardrobe
- `delete_from_wardrobe()` - DELETE wardrobe

**Usage:**
```bash
python api_client_example.py
```

---

## Documentation Files

### `README.md` (Full Documentation)
**Size:** ~500 lines | **Type:** Markdown
**Purpose:** Comprehensive documentation for the backend

**Sections:**
- Features overview
- Installation instructions (local, Docker, Compose)
- Configuration guide
- Complete API endpoint documentation with examples
- Data structure and storage layout
- Python usage examples
- cURL command examples
- Performance considerations
- Troubleshooting guide
- Development guidelines
- Testing instructions
- Security notes

**Audience:** Developers, DevOps, API users

---

### `QUICKSTART.md` (Quick Start Guide)
**Size:** ~150 lines | **Type:** Markdown
**Purpose:** Get started in 5 minutes

**Sections:**
- Prerequisites
- Three deployment options (Local, Docker, Docker Compose)
- Testing the API
- Troubleshooting common issues
- Next steps

**Audience:** New users, quick setup

---

### `ARCHITECTURE.md` (System Design)
**Size:** ~400 lines | **Type:** Markdown
**Purpose:** Detailed technical architecture documentation

**Sections:**
- System overview with diagrams
- Component details
- Data flow diagrams
- Directory structure
- API endpoints summary
- Deployment architecture options
- Performance characteristics
- Error handling strategy
- Security considerations
- Monitoring and logging
- Future enhancements
- References

**Audience:** Architects, senior developers, DevOps

---

### `DEPLOYMENT.md` (Production Deployment)
**Size:** ~400 lines | **Type:** Markdown
**Purpose:** Guide for deploying to production

**Sections:**
- Pre-deployment checklist
- Four deployment options:
  1. Heroku (simplest)
  2. Docker + AWS EC2 (medium)
  3. Kubernetes (enterprise)
  4. Docker Compose + VPS (balanced)
- Production configuration
- Scaling considerations
- Monitoring and logging setup
- Backup and recovery procedures
- Cost optimization
- Troubleshooting deployment issues
- CI/CD integration (GitHub Actions example)
- Rollback procedures

**Audience:** DevOps, system administrators, deployment engineers

---

### `INDEX.md` (This File)
**Size:** ~500 lines | **Type:** Markdown
**Purpose:** Complete guide to all files in the server directory

**Sections:**
- File-by-file documentation
- Directory structure
- Usage patterns
- Cross-references

**Audience:** Everyone - start here for orientation

---

## Directory Structure

```
server/
├── main.py                    # FastAPI application (main entry point)
├── config.py                  # Configuration management
├── health.py                  # Health monitoring utilities
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Multi-container orchestration
├── .env.example              # Environment variables template
├── start.sh                  # Local startup script
│
├── api_client_example.py     # Python client example
│
├── README.md                 # Full documentation
├── QUICKSTART.md             # Quick start guide (5 min)
├── ARCHITECTURE.md           # System architecture
├── DEPLOYMENT.md             # Production deployment guide
├── INDEX.md                  # This file
│
└── data/                     # Data storage (created at runtime)
    ├── persons/              # Uploaded person images
    └── wardrobe/             # Saved try-on results + metadata
```

## Quick Reference: Where to Go?

### "I want to..."

**...run the server locally**
→ See [QUICKSTART.md](QUICKSTART.md)

**...deploy to production**
→ See [DEPLOYMENT.md](DEPLOYMENT.md)

**...understand the system architecture**
→ See [ARCHITECTURE.md](ARCHITECTURE.md)

**...use the API from Python**
→ See [api_client_example.py](api_client_example.py) or [README.md](README.md)

**...configure the server**
→ Copy `.env.example` to `.env` and see [README.md](README.md)

**...run with Docker**
→ See [QUICKSTART.md](QUICKSTART.md) Option 3 or [README.md](README.md)

**...troubleshoot issues**
→ See [README.md](README.md) Troubleshooting section

**...understand all endpoints**
→ See [README.md](README.md) API Endpoints section

**...learn about monitoring**
→ See [ARCHITECTURE.md](ARCHITECTURE.md) Monitoring section or [DEPLOYMENT.md](DEPLOYMENT.md)

## File Size Summary

```
Core Application:
  main.py                    ~600 lines (~18 KB)
  config.py                  ~150 lines (~5 KB)
  health.py                  ~150 lines (~5 KB)
  api_client_example.py      ~300 lines (~10 KB)

Configuration:
  requirements.txt           ~10 lines (~0.3 KB)
  .env.example              ~20 lines (~0.5 KB)
  Dockerfile                ~50 lines (~2 KB)
  docker-compose.yml        ~40 lines (~1.5 KB)

Scripts:
  start.sh                  ~70 lines (~2 KB)

Documentation:
  README.md                 ~500 lines (~25 KB)
  QUICKSTART.md             ~150 lines (~7 KB)
  ARCHITECTURE.md           ~400 lines (~20 KB)
  DEPLOYMENT.md             ~400 lines (~20 KB)
  INDEX.md                  ~500 lines (~25 KB)

Total: ~3500 lines, ~140 KB of code and documentation
```

## Python Modules & Imports

### External Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `PIL/Pillow` - Image processing
- `requests` - HTTP client
- `yaml` - YAML parsing
- `python-multipart` - Form data parsing
- `aiofiles` - Async file operations

### Internal Imports
- `ai_fit_check.segmentation.ClothingSegmenter` - Clothing extraction
- `ai_fit_check.tryon.VirtualTryOn` - Try-on pipeline

### Standard Library
- `os`, `sys`, `io` - File and stream operations
- `json` - JSON serialization
- `logging` - Logging
- `uuid` - ID generation
- `datetime` - Time operations
- `pathlib` - Path handling
- `base64` - Encoding/decoding

## Configuration Hierarchy

Settings are loaded in this order (later overrides earlier):

1. **Defaults** in `config.py`
2. **YAML** from `../configs/config.yaml`
3. **Environment variables** (e.g., `FASHN_API_KEY`)
4. **.env file** (if present)

## Development Workflow

### Initial Setup
```bash
git clone <repo>
cd server
cp .env.example .env
# Edit .env with your settings
./start.sh
```

### During Development
```bash
# Modify Python files
# Changes auto-reload via uvicorn --reload
```

### Adding New Endpoints
```python
@app.post("/api/new-endpoint")
async def new_endpoint(...):
    """Documentation."""
    try:
        # Implementation
        return JSONResponse({"success": True})
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing Changes
```bash
# Visit http://localhost:8000/docs
# Or use curl/Python client
```

## Production Checklist

- [ ] `DEBUG=False` in .env
- [ ] CORS origins restricted to your domain
- [ ] HTTPS/TLS enabled
- [ ] Database backups configured
- [ ] Monitoring set up
- [ ] Log rotation configured
- [ ] API key rotated and secured
- [ ] Error tracking (Sentry) configured
- [ ] Rate limiting implemented
- [ ] Load testing completed

## Related Files (Outside server/)

- `../ai_fit_check/segmentation.py` - Clothing segmentation
- `../ai_fit_check/tryon.py` - Virtual try-on pipeline
- `../configs/config.yaml` - Configuration file
- `../ios/` - iOS app client
- `../README.md` - Project overview

## Support & Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- Uvicorn docs: https://www.uvicorn.org/
- Docker docs: https://docs.docker.com/
- Fashn.ai API: https://api.fashn.ai/
- Python requests: https://requests.readthedocs.io/

## Last Updated

- **Version:** 1.0.0
- **Date:** 2024-03-27
- **Python:** 3.11+
- **Status:** Production Ready
