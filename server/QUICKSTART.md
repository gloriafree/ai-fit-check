# Quick Start Guide - AI Fit Check Backend

Get the backend server running in minutes.

## Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- 4GB+ RAM
- Fashn.ai API key

## Option 1: Local Development (Recommended for Testing)

### Step 1: Navigate to Server Directory
```bash
cd server
```

### Step 2: Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure
Copy the example .env file:
```bash
cp .env.example .env
```

Edit `.env` and set your Fashn.ai API key:
```
FASHN_API_KEY=your-api-key-here
```

### Step 5: Run the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

### Step 6: Verify It's Running
```bash
curl http://localhost:8000/health
```

You should see a JSON response indicating the server is healthy.

## Option 2: Using Docker

### Step 1: Build the Image
```bash
docker build -t ai-fit-check-backend .
```

### Step 2: Run the Container
```bash
docker run -p 8000:8000 \
  -e FASHN_API_KEY="your-api-key-here" \
  -v $(pwd)/data:/app/server/data \
  ai-fit-check-backend
```

## Option 3: Using Docker Compose (Easiest)

### Step 1: Create .env File
```bash
cp .env.example .env
# Edit .env and set FASHN_API_KEY
```

### Step 2: Start Services
```bash
docker-compose up -d
```

### Step 3: View Logs
```bash
docker-compose logs -f ai-fit-check-backend
```

### Step 4: Stop Services
```bash
docker-compose down
```

## Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Upload Person Photo
```bash
curl -X POST http://localhost:8000/api/person \
  -F "file=@/path/to/person.jpg"
```

### 3. Perform Try-On
```bash
curl -X POST http://localhost:8000/api/tryon \
  -F "file=@/path/to/clothing.jpg" \
  -o result.png
```

### 4. View API Documentation
Open your browser to: `http://localhost:8000/docs`

This provides an interactive Swagger UI where you can test all endpoints.

## Troubleshooting

### Connection Refused
- Ensure server is running: `curl http://localhost:8000/health`
- Check port 8000 is not in use: `lsof -i :8000`

### Models Not Initialized
Check the logs for initialization errors. Some models require GPU support.

### Try-On Fails
1. Verify Fashn.ai API key is correct
2. Ensure person image is uploaded first
3. Check image quality and format

### Out of Memory
Reduce image resolution or use CPU mode instead of GPU.

## Next Steps

1. Read the full [README.md](README.md) for detailed API documentation
2. Check [api_client_example.py](api_client_example.py) for Python integration
3. Review [config.py](config.py) for advanced configuration options

## Development

To make changes to the code and restart automatically:

```bash
pip install watchdog
watchmedo auto-restart -d . -p '*.py' -- python main.py
```

## Production Deployment

For production use:

1. Set `DEBUG=False` in environment
2. Restrict CORS origins to your domain
3. Use HTTPS/TLS
4. Set up proper logging and monitoring
5. Use a proper ASGI server like Gunicorn with Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Support

For issues or questions:
1. Check server logs: `docker-compose logs ai-fit-check-backend`
2. Review API documentation: `http://localhost:8000/docs`
3. Check [README.md](README.md) for detailed information
