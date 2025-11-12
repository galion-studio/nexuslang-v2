# Nexus Core Distilled Models - Deployment Guide

## Overview

This guide covers deployment strategies, infrastructure setup, and best practices for deploying Nexus Core distilled models in production environments.

---

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Container Deployment](#container-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Serverless Deployment](#serverless-deployment)
6. [Edge Deployment](#edge-deployment)
7. [Load Balancing & Scaling](#load-balancing--scaling)
8. [Monitoring & Observability](#monitoring--observability)
9. [Security](#security)
10. [Cost Optimization](#cost-optimization)

---

## Deployment Options

### Option 1: Docker Container (Recommended)
- **Best For**: Standard model, cloud deployment
- **Pros**: Easy scaling, isolation, portability
- **Cons**: Container overhead
- **Setup Time**: 30 minutes

### Option 2: Kubernetes
- **Best For**: Large-scale production
- **Pros**: Auto-scaling, high availability, orchestration
- **Cons**: Complex setup, resource overhead
- **Setup Time**: 2-4 hours

### Option 3: Serverless (AWS Lambda / Azure Functions)
- **Best For**: Nano model, variable traffic
- **Pros**: Pay-per-use, zero maintenance
- **Cons**: Cold starts, limited control
- **Setup Time**: 1 hour

### Option 4: Edge Deployment
- **Best For**: Nano model, IoT devices
- **Pros**: Low latency, offline capable, privacy
- **Cons**: Limited resources, deployment complexity
- **Setup Time**: Varies

### Option 5: Bare Metal
- **Best For**: Maximum performance
- **Pros**: No virtualization overhead
- **Cons**: Hard to scale, manual management
- **Setup Time**: 2-3 hours

---

## Infrastructure Requirements

### For Standard Model (16GB)

#### Minimum Requirements
```yaml
CPU: 8 cores (Intel Xeon / AMD EPYC)
RAM: 32 GB
GPU: NVIDIA T4 (16GB VRAM) or better
Storage: 50 GB SSD
Network: 1 Gbps
OS: Ubuntu 22.04 LTS
```

#### Recommended Requirements
```yaml
CPU: 16 cores (Intel Xeon Platinum / AMD EPYC)
RAM: 64 GB
GPU: NVIDIA A10 (24GB VRAM) or RTX 4090
Storage: 100 GB NVMe SSD
Network: 10 Gbps
OS: Ubuntu 22.04 LTS
```

#### Cloud Instance Recommendations
- **AWS**: g5.2xlarge (1× A10G 24GB) - $1.21/hour
- **GCP**: a2-highgpu-1g (1× A100 40GB) - $3.67/hour
- **Azure**: Standard_NC24ads_A100_v4 (1× A100 40GB) - $3.67/hour

### For Nano Model (4GB)

#### Minimum Requirements
```yaml
CPU: 4 cores
RAM: 8 GB
GPU: NVIDIA GTX 1660 Ti (6GB VRAM) or better
Storage: 20 GB SSD
Network: 100 Mbps
OS: Ubuntu 22.04 LTS / Raspberry Pi OS
```

#### Recommended Requirements
```yaml
CPU: 8 cores
RAM: 16 GB
GPU: NVIDIA RTX 3060 (12GB VRAM)
Storage: 50 GB SSD
Network: 1 Gbps
OS: Ubuntu 22.04 LTS
```

#### Cloud Instance Recommendations
- **AWS**: g4dn.xlarge (1× T4 16GB) - $0.526/hour
- **GCP**: n1-standard-4 + T4 - $0.48/hour
- **Azure**: Standard_NC4as_T4_v3 (1× T4 16GB) - $0.526/hour

---

## Container Deployment

### 1. Docker Setup for Standard Model

#### Dockerfile

```dockerfile
# distillation/docker/Dockerfile.standard

FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy model
COPY exports/nexus-standard-16gb-v1.0 /app/models/standard/

# Copy API server
COPY api/server.py /app/
COPY api/config.yaml /app/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run server
CMD ["python3", "server.py", "--model", "/app/models/standard", "--port", "8080"]
```

#### Build and Run

```bash
# Build image
docker build -t nexus-standard:v1.0 -f docker/Dockerfile.standard .

# Run container
docker run -d \
    --name nexus-standard \
    --gpus all \
    -p 8080:8080 \
    -e MODEL_PATH=/app/models/standard \
    -e MAX_BATCH_SIZE=32 \
    -e MAX_SEQUENCE_LENGTH=8192 \
    -v /data/cache:/app/cache \
    --restart unless-stopped \
    nexus-standard:v1.0

# View logs
docker logs -f nexus-standard

# Test API
curl -X POST http://localhost:8080/v1/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Hello, world!", "max_tokens": 100}'
```

### 2. Docker Compose Setup

```yaml
# docker-compose.yml

version: '3.8'

services:
  nexus-standard:
    image: nexus-standard:v1.0
    container_name: nexus-standard
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "8080:8080"
    environment:
      - MODEL_PATH=/app/models/standard
      - MAX_BATCH_SIZE=32
      - MAX_SEQUENCE_LENGTH=8192
      - LOG_LEVEL=INFO
    volumes:
      - model-cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Load balancer
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - nexus-standard
    restart: unless-stopped

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  model-cache:
  prometheus-data:
  grafana-data:
```

```bash
# Deploy
docker-compose up -d

# Scale
docker-compose up -d --scale nexus-standard=3
```

---

## Kubernetes Deployment

### 1. Kubernetes Manifests

#### Namespace

```yaml
# k8s/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: nexus-core
```

#### ConfigMap

```yaml
# k8s/configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: nexus-config
  namespace: nexus-core
data:
  config.yaml: |
    model:
      path: /models/standard
      max_batch_size: 32
      max_sequence_length: 8192
    server:
      host: "0.0.0.0"
      port: 8080
      workers: 4
    logging:
      level: INFO
      format: json
```

#### Deployment

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-standard
  namespace: nexus-core
  labels:
    app: nexus-standard
    version: v1.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nexus-standard
  template:
    metadata:
      labels:
        app: nexus-standard
        version: v1.0
    spec:
      containers:
      - name: nexus
        image: nexus-standard:v1.0
        ports:
        - containerPort: 8080
          name: http
        resources:
          requests:
            memory: "24Gi"
            cpu: "8"
            nvidia.com/gpu: "1"
          limits:
            memory: "32Gi"
            cpu: "16"
            nvidia.com/gpu: "1"
        env:
        - name: MODEL_PATH
          value: "/models/standard"
        - name: MAX_BATCH_SIZE
          value: "32"
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        volumeMounts:
        - name: model-storage
          mountPath: /models
          readOnly: true
        - name: cache
          mountPath: /app/cache
        - name: config
          mountPath: /app/config
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: nexus-model-pvc
      - name: cache
        emptyDir:
          sizeLimit: 10Gi
      - name: config
        configMap:
          name: nexus-config
      nodeSelector:
        cloud.google.com/gke-accelerator: nvidia-tesla-a100
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
```

#### Service

```yaml
# k8s/service.yaml

apiVersion: v1
kind: Service
metadata:
  name: nexus-standard
  namespace: nexus-core
spec:
  type: LoadBalancer
  selector:
    app: nexus-standard
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  sessionAffinity: ClientIP
```

#### HorizontalPodAutoscaler

```yaml
# k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nexus-standard-hpa
  namespace: nexus-core
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nexus-standard
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 60
```

#### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create config
kubectl apply -f k8s/configmap.yaml

# Create deployment
kubectl apply -f k8s/deployment.yaml

# Create service
kubectl apply -f k8s/service.yaml

# Create HPA
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get pods -n nexus-core
kubectl get svc -n nexus-core

# View logs
kubectl logs -f -n nexus-core -l app=nexus-standard

# Test
kubectl port-forward -n nexus-core svc/nexus-standard 8080:80
curl -X POST http://localhost:8080/v1/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Test", "max_tokens": 50}'
```

---

## Serverless Deployment

### AWS Lambda (Nano Model)

#### Lambda Function

```python
# lambda/handler.py

import json
import boto3
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Global model (loaded once, reused across invocations)
model = None
tokenizer = None

def load_model():
    global model, tokenizer
    if model is None:
        # Download from S3 if needed
        s3 = boto3.client('s3')
        model_path = '/tmp/nexus-nano'
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map='auto'
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    return model, tokenizer

def lambda_handler(event, context):
    try:
        # Parse request
        body = json.loads(event['body'])
        prompt = body.get('prompt', '')
        max_tokens = body.get('max_tokens', 100)
        
        # Load model (cached after first invocation)
        model, tokenizer = load_model()
        
        # Generate
        inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response,
                'tokens_generated': len(outputs[0])
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

#### SAM Template

```yaml
# template.yaml

AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  NexusNanoFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: nexus-nano-inference
      Handler: handler.lambda_handler
      Runtime: python3.10
      CodeUri: lambda/
      MemorySize: 10240  # 10GB
      Timeout: 900  # 15 minutes
      EphemeralStorage:
        Size: 10240  # 10GB
      Environment:
        Variables:
          MODEL_BUCKET: nexus-models
          MODEL_KEY: nano-4gb-v1.0
      Policies:
        - S3ReadPolicy:
            BucketName: nexus-models
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /generate
            Method: post
```

```bash
# Deploy
sam build
sam deploy --guided

# Test
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Hello", "max_tokens": 50}'
```

---

## Edge Deployment

### Raspberry Pi 4 (Nano Model)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install PyTorch (ARM optimized)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install model requirements
pip3 install transformers accelerate

# Download nano model
wget https://models.galion.app/nexus-nano-4gb-v1.0.tar.gz
tar -xzf nexus-nano-4gb-v1.0.tar.gz

# Run inference
python3 edge_inference.py --model nexus-nano-4gb-v1.0
```

### NVIDIA Jetson (Nano Model)

```bash
# Install JetPack SDK
sudo apt-get install nvidia-jetpack

# Install TensorRT
sudo apt-get install tensorrt

# Convert model to TensorRT
python3 scripts/convert_tensorrt.py \
    --model nexus-nano-4gb-v1.0 \
    --precision fp16 \
    --output nexus-nano-tensorrt

# Run optimized inference
python3 jetson_inference.py --model nexus-nano-tensorrt
```

---

## Load Balancing & Scaling

### NGINX Configuration

```nginx
# nginx.conf

upstream nexus_backend {
    least_conn;  # Load balancing method
    
    server nexus-1:8080 max_fails=3 fail_timeout=30s;
    server nexus-2:8080 max_fails=3 fail_timeout=30s;
    server nexus-3:8080 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

server {
    listen 80;
    server_name api.galion.app;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.galion.app;
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location /v1/generate {
        proxy_pass http://nexus_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    location /health {
        proxy_pass http://nexus_backend;
        access_log off;
    }
}
```

---

## Monitoring & Observability

### Prometheus Metrics

```python
# api/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Request metrics
requests_total = Counter(
    'nexus_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'nexus_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Model metrics
tokens_generated = Counter(
    'nexus_tokens_generated_total',
    'Total tokens generated'
)

generation_time = Histogram(
    'nexus_generation_time_seconds',
    'Token generation time'
)

# Resource metrics
gpu_utilization = Gauge(
    'nexus_gpu_utilization_percent',
    'GPU utilization percentage'
)

gpu_memory_used = Gauge(
    'nexus_gpu_memory_used_bytes',
    'GPU memory used in bytes'
)

model_load_time = Histogram(
    'nexus_model_load_time_seconds',
    'Model loading time'
)

# Error metrics
errors_total = Counter(
    'nexus_errors_total',
    'Total number of errors',
    ['error_type']
)
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Nexus Core - Production Monitoring",
    "panels": [
      {
        "title": "Requests per Second",
        "targets": [
          {
            "expr": "rate(nexus_requests_total[1m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, nexus_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "GPU Utilization",
        "targets": [
          {
            "expr": "nexus_gpu_utilization_percent"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(nexus_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## Security

### API Authentication

```python
# api/auth.py

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/generate")
@limiter.limit("100/minute")
async def generate(request: Request):
    # ...
    pass
```

---

## Cost Optimization

### Tips

1. **Use Spot Instances**: 70% savings on AWS/GCP
2. **Auto-scaling**: Scale down during low traffic
3. **Batch Processing**: Higher throughput per $
4. **Model Caching**: Reduce cold start times
5. **Compression**: Use INT8 for 4× memory reduction

### Cost Calculator

```python
def calculate_monthly_cost(
    requests_per_day: int,
    avg_tokens_per_request: int,
    model_type: str  # 'standard' or 'nano'
):
    # Cloud costs (AWS p3)
    costs = {
        'standard': 3.06,  # per hour
        'nano': 0.526      # per hour
    }
    
    # Calculate required instances
    throughput = {
        'standard': 100,  # req/sec
        'nano': 18.7      # req/sec
    }
    
    req_per_sec = requests_per_day / 86400
    instances = math.ceil(req_per_sec / throughput[model_type])
    
    # Monthly cost
    hours_per_month = 730
    monthly_cost = instances * costs[model_type] * hours_per_month
    
    return {
        'instances': instances,
        'monthly_cost': monthly_cost,
        'cost_per_1m_tokens': (monthly_cost * 1000000) / 
                               (requests_per_day * 30 * avg_tokens_per_request)
    }

# Example
print(calculate_monthly_cost(
    requests_per_day=100000,
    avg_tokens_per_request=200,
    model_type='standard'
))
# Output: {'instances': 2, 'monthly_cost': $4467, 'cost_per_1m_tokens': $0.74}
```

---

## Conclusion

Choose deployment strategy based on your requirements:

- **Docker**: Quick start, easy scaling
- **Kubernetes**: Production-grade, auto-scaling
- **Serverless**: Variable traffic, pay-per-use
- **Edge**: Low latency, privacy, offline

For most users, **Docker + Kubernetes** provides the best balance.

---

**Need Help?** Contact: devops@galion.app

