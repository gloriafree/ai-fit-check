# Deployment Guide

Complete guide for deploying the AI Fit Check backend to production.

## Pre-Deployment Checklist

- [ ] Fashn.ai API key obtained and validated
- [ ] Python 3.11+ available
- [ ] Docker installed (for containerized deployment)
- [ ] Domain name configured (for HTTPS)
- [ ] SSL/TLS certificates ready
- [ ] Cloud hosting account (AWS, GCP, Azure, etc.)
- [ ] Database planned (PostgreSQL recommended)
- [ ] Monitoring tools configured

## Deployment Options

### Option 1: Heroku (Simplest for Small-Scale)

#### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository

#### Steps

1. **Create Procfile**
```bash
echo "web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server.main:app" > Procfile
```

2. **Create Heroku App**
```bash
heroku create your-app-name
```

3. **Set Environment Variables**
```bash
heroku config:set FASHN_API_KEY="your-key"
heroku config:set DEBUG="False"
```

4. **Deploy**
```bash
git push heroku main
```

5. **View Logs**
```bash
heroku logs --tail
```

### Option 2: Docker + AWS EC2 (Good for Medium-Scale)

#### Prerequisites
- AWS account with EC2 access
- EC2 instance running Ubuntu 20.04 LTS or newer
- SSH access to instance

#### Steps

1. **Connect to EC2 Instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

3. **Clone Repository**
```bash
git clone https://github.com/your-org/ai-fit-check.git
cd ai-fit-check/server
```

4. **Configure Environment**
```bash
cp .env.example .env
nano .env  # Edit with your configuration
```

5. **Build and Run**
```bash
docker build -t ai-fit-check:latest .
docker run -d \
  --name ai-fit-check \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/server/data \
  ai-fit-check:latest
```

6. **Set Up Nginx Reverse Proxy**
```bash
sudo apt-get update
sudo apt-get install nginx
sudo systemctl start nginx
```

Create `/etc/nginx/sites-available/ai-fit-check`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/ai-fit-check /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Set Up HTTPS with Let's Encrypt**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 3: Kubernetes (Enterprise-Scale)

#### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS)
- kubectl installed
- Docker image pushed to registry

#### Steps

1. **Create Deployment Manifest** (`k8s-deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-fit-check
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-fit-check
  template:
    metadata:
      labels:
        app: ai-fit-check
    spec:
      containers:
      - name: ai-fit-check
        image: your-registry/ai-fit-check:latest
        ports:
        - containerPort: 8000
        env:
        - name: FASHN_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-fit-check-secrets
              key: fashn-api-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: data
          mountPath: /app/server/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ai-fit-check-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ai-fit-check-service
spec:
  type: LoadBalancer
  selector:
    app: ai-fit-check
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-fit-check-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

2. **Create Secret for API Key**
```bash
kubectl create secret generic ai-fit-check-secrets \
  --from-literal=fashn-api-key=your-key
```

3. **Deploy**
```bash
kubectl apply -f k8s-deployment.yaml
kubectl get pods  # Verify deployment
```

4. **Check Status**
```bash
kubectl get svc ai-fit-check-service
kubectl logs -f deployment/ai-fit-check
```

### Option 4: Docker Compose + VPS (Balanced Approach)

#### Prerequisites
- VPS with 8GB RAM, 50GB storage
- Docker and Docker Compose installed
- SSH access

#### Steps

1. **Connect to VPS**
```bash
ssh root@your-vps-ip
```

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Clone and Deploy**
```bash
cd /opt
git clone https://github.com/your-org/ai-fit-check.git
cd ai-fit-check/server
cp .env.example .env
nano .env  # Configure

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

4. **Set Up Monitoring**
```bash
# Add health check to cron
echo "*/5 * * * * curl -f http://localhost:8000/health || docker-compose restart" | crontab -
```

## Production Configuration

### Security Hardening

1. **Environment Variables** (.env)
```
FASHN_API_KEY=your-actual-key
DEBUG=False
LOG_LEVEL=WARNING
HOST=127.0.0.1  # Only listen on localhost, use reverse proxy
```

2. **CORS Configuration** (update in main.py)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

3. **Rate Limiting** (add to requirements.txt and main.py)
```bash
pip install slowapi
```

4. **HTTPS/TLS**
- Always use HTTPS in production
- Use Let's Encrypt for free certificates
- Implement HSTS headers

### Scaling Considerations

1. **Multiple Workers**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

2. **Load Balancing**
- Use Nginx or HAProxy
- Distribute across multiple instances

3. **Database Connection Pooling**
- Use connection pools for PostgreSQL
- Implement caching with Redis

### Monitoring & Logging

1. **Application Monitoring**
```bash
pip install prometheus-client
```

2. **Log Aggregation**
- Use ELK Stack (Elasticsearch, Logstash, Kibana)
- Or Cloud Logging (CloudWatch, Stackdriver)

3. **Error Tracking**
```bash
pip install sentry-sdk
```

4. **Uptime Monitoring**
- Use UptimeRobot or similar
- Monitor `/health` endpoint

## Backup & Recovery

### Data Backup

1. **Wardrobe Data**
```bash
# Backup to S3
aws s3 sync server/data/wardrobe s3://your-bucket/backups/wardrobe/ --delete

# Backup to local
rsync -av user@server:/opt/ai-fit-check/server/data /local/backup/
```

2. **Scheduled Backups**
```bash
# Add to crontab
0 2 * * * aws s3 sync /opt/ai-fit-check/server/data s3://your-bucket/backups/$(date +\%Y-\%m-\%d)/
```

### Recovery Procedure

1. **Restore from Backup**
```bash
aws s3 sync s3://your-bucket/backups/latest /opt/ai-fit-check/server/data/
```

2. **Verify Integrity**
```bash
curl http://localhost:8000/health
```

## Cost Optimization

### Budget-Friendly Options
- **AWS**: t3.medium EC2 instance (~$30/month)
- **Heroku**: Hobby dyno ($7/month)
- **DigitalOcean**: Basic droplet ($6/month)
- **Linode**: Nanode 1GB ($5/month)

### Cost Reduction Strategies
1. Use spot instances for non-critical workloads
2. Implement auto-scaling (scale down during off-hours)
3. Cache API responses
4. Optimize image sizes
5. Use CDN for static assets

## Troubleshooting Deployment

### Common Issues

**Port Already in Use**
```bash
lsof -i :8000
kill -9 <PID>
```

**Permission Denied**
```bash
sudo chown -R $USER:$USER /opt/ai-fit-check
chmod -R 755 /opt/ai-fit-check
```

**Out of Memory**
```bash
# Check memory usage
free -h
top

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Docker Image Build Fails**
```bash
# Clean build
docker build --no-cache -t ai-fit-check:latest .

# Check disk space
docker system df
docker system prune -a  # Warning: removes all images
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and push Docker image
      uses: docker/build-push-action@v2
      with:
        context: ./
        push: true
        tags: your-registry/ai-fit-check:latest
    - name: Deploy to EC2
      run: |
        ssh -i ${{ secrets.EC2_KEY }} ubuntu@${{ secrets.EC2_HOST }} << 'EOF'
        cd /opt/ai-fit-check
        git pull
        docker-compose pull
        docker-compose up -d
        EOF
```

## Rollback Procedure

If something goes wrong:

```bash
# List previous images
docker images

# Rollback to previous version
docker run -d \
  --name ai-fit-check-rollback \
  -p 8001:8000 \
  ai-fit-check:previous-version

# Test on port 8001
curl http://localhost:8001/health

# Switch traffic back if working
# Then remove new broken version
docker stop ai-fit-check
docker rm ai-fit-check
docker run -d --name ai-fit-check ai-fit-check:previous-version
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review health endpoint: `curl http://localhost:8000/health`
3. Consult [README.md](README.md) for API details
4. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
