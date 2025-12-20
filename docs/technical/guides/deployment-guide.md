# Brain AI Framework - Deployment Guide

> **Complete guide for deploying Brain AI Framework in production environments**

## 🚀 **Quick Start Demo**

### **Option 1: Automated Setup**
```bash
# Make executable (if permissions allow)
chmod +x start_demo.sh

# Run the demo
./start_demo.sh
```

### **Option 2: Manual Setup**
```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Test functionality
python test_demo.py

# Start demo server
python demo.py
```

### **Demo Access Points**
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Demo Examples**: http://localhost:8000/demo/examples
- **System Status**: http://localhost:8000/status
- **Memory Viewer**: http://localhost:8000/memories

---

## 🏭 **Production Deployment**

### **Prerequisites**

#### **System Requirements**
- **Python**: 3.8 or higher (tested on 3.12)
- **Memory**: 2GB minimum, 8GB recommended
- **Storage**: 10GB for data persistence
- **Network**: HTTPS recommended for production

#### **Dependencies**
```bash
# Core dependencies (required)
pip install fastapi uvicorn pydantic pydantic-settings loguru

# Optional AI dependencies (for full functionality)
pip install openai transformers sentence-transformers
pip install sqlalchemy redis chromadb

# Monitoring (recommended)
pip install prometheus-client
```

### **Environment Configuration**

#### **Production Environment Variables**
```bash
# .env file for production
HOST=0.0.0.0
PORT=8000
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost/brain_ai
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_production_secret_key
API_KEY_REQUIRED=true
LOG_LEVEL=INFO
ENABLE_METRICS=true
METRICS_PORT=9090
```

### **Deployment Options**

#### **Option 1: Docker Deployment**

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt

COPY . .
EXPOSE 8000

CMD ["python", "demo.py"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  brain-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/brain_ai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=brain_ai
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
  
  redis:
    image: redis:7-alpine
```

**Deploy:**
```bash
docker-compose up -d
```

#### **Option 2: Cloud Platform Deployment**

**AWS Deployment:**
```bash
# Using AWS App Runner
aws apprunner create-service \
  --service-name brain-ai-demo \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "your-ecr-repo/brain-ai:latest",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "HOST": "0.0.0.0",
          "PORT": "8000"
        }
      }
    }
  }'
```

**Google Cloud Run:**
```bash
# Deploy to Cloud Run
gcloud run deploy brain-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

**Azure Container Instances:**
```bash
# Deploy to Azure
az container create \
  --resource-group brain-ai-rg \
  --name brain-ai-demo \
  --image your-registry.azurecr.io/brain-ai:latest \
  --ports 8000 \
  --environment-variables \
    HOST=0.0.0.0 \
    PORT=8000
```

#### **Option 3: Kubernetes Deployment**

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brain-ai-demo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brain-ai-demo
  template:
    metadata:
      labels:
        app: brain-ai-demo
    spec:
      containers:
      - name: brain-ai
        image: brain-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: brain-ai-service
spec:
  selector:
    app: brain-ai-demo
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
```

### **Database Setup**

#### **PostgreSQL Configuration**
```sql
-- Create database
CREATE DATABASE brain_ai;

-- Create user
CREATE USER brain_ai_user WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE brain_ai TO brain_ai_user;
```

#### **Redis Configuration**
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### **Security Configuration**

#### **API Security**
```python
# security.py - Add to your app
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_api_key(token: str = Depends(security)):
    # Implement your API key verification
    if token.credentials != os.getenv("VALID_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return token.credentials
```

#### **HTTPS Configuration**
```python
# SSL/TLS setup
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('path/to/cert.pem', 'path/to/key.pem')

uvicorn.run(
    "demo:app",
    host="0.0.0.0",
    port=443,
    ssl_keyfile="path/to/key.pem",
    ssl_certfile="path/to/cert.pem"
)
```

### **Monitoring & Observability**

#### **Prometheus Metrics**
```python
# Add to your application
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter('brain_ai_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('brain_ai_request_duration_seconds', 'Request latency')
ACTIVE_MEMORIES = Gauge('brain_ai_active_memories', 'Number of active memories')

# Use in endpoints
@router.post("/process")
async def process_input(request: ProcessRequest):
    REQUEST_COUNT.inc()
    start_time = time.time()
    
    try:
        result = await brain_system.process_input(request.data)
        return result
    finally:
        REQUEST_LATENCY.observe(time.time() - start_time)
```

#### **Health Checks**
```python
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = brain_system.get_statistics()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "encoder": "healthy",
                "memory_store": "healthy",
                "learning_engine": "healthy",
                "reasoning_engine": "healthy"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### **Performance Optimization**

#### **Production Settings**
```python
# production.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "demo:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Number of worker processes
        worker_class="uvicorn.workers.UvicornWorker",
        max_requests=1000,  # Restart workers after this many requests
        max_requests_jitter=100,  # Add randomness to restart timing
        access_log=True,
        log_level="info"
    )
```

#### **Database Optimization**
```python
# connection pooling
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### **Backup & Recovery**

#### **Data Backup Strategy**
```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/brain_ai"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump brain_ai > $BACKUP_DIR/database_$DATE.sql

# Backup Redis data
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Compress backups
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/database_$DATE.sql $BACKUP_DIR/redis_$DATE.rdb

# Remove old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
```

### **Troubleshooting**

#### **Common Issues**

**Memory Issues:**
```bash
# Monitor memory usage
ps aux | grep python
top -p $(pgrep -f demo.py)

# Increase worker memory
export PYTHONHASHSEED=0
export MALLOC_ARENA_MAX=2
```

**Database Connection Issues:**
```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/brain_ai')
print('Database connection successful')
"
```

**Performance Issues:**
```bash
# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/status"

# curl-format.txt:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#           time_total:  %{time_total}\n
```

### **Support & Maintenance**

#### **Log Monitoring**
```bash
# View logs
tail -f /var/log/brain_ai/app.log

# Monitor errors
grep ERROR /var/log/brain_ai/app.log | tail -20

# Performance monitoring
grep "slow" /var/log/brain_ai/app.log | tail -10
```

#### **Update Process**
```bash
# 1. Backup current deployment
./backup.sh

# 2. Deploy new version
git pull origin main
pip install -r requirements.txt

# 3. Run tests
python -m pytest tests/

# 4. Restart service
systemctl restart brain-ai
```

---

## 📞 **Support & Contact**

### **Documentation**
- **API Reference**: http://localhost:8000/docs
- **Case Studies**: `/docs/case-studies.md`
- **Technical Documentation**: `/docs/`

### **Getting Help**
1. **Demo Issues**: Check `/status` endpoint
2. **Performance**: Monitor `/metrics` endpoint
3. **Logs**: Check application logs for errors
4. **Support**: Contact the development team

### **Production Checklist**
- [ ] Environment variables configured
- [ ] Database connections tested
- [ ] Security measures implemented
- [ ] Monitoring setup complete
- [ ] Backup strategy in place
- [ ] Load testing completed
- [ ] Disaster recovery plan documented

---

*This deployment guide provides a comprehensive approach to deploying Brain AI Framework in production environments. Adapt the configurations based on your specific requirements and infrastructure.*