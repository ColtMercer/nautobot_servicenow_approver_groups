# Containerized Installation Guide

## Overview

This guide provides detailed instructions for installing and running the ServiceNow Groups Nautobot app in containerized environments using Docker and Kubernetes.

## Prerequisites

### Docker Installation
- Docker Engine 20.10+ or Docker Desktop 4.0+
- Docker Compose 2.0+
- At least 4GB RAM and 10GB disk space

### Kubernetes Installation (Optional)
- Kubernetes cluster 1.20+
- kubectl 1.20+
- Helm 3.0+ (for Helm chart installation)

## Quick Start with Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/nautobot-servicenow-groups.git
cd nautobot-servicenow-groups
```

### 2. Configure Environment

Create a `.env` file with your configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the environment variables
nano .env
```

Example `.env` file:

```bash
# Nautobot Configuration
NAUTOBOT_SECRET_KEY=your-super-secret-key-here
NAUTOBOT_ALLOWED_HOSTS=localhost,127.0.0.1,nautobot.local
NAUTOBOT_DEBUG=false

# Database Configuration
NAUTOBOT_DB_HOST=postgres
NAUTOBOT_DB_NAME=nautobot
NAUTOBOT_DB_USER=nautobot
NAUTOBOT_DB_PASSWORD=nautobot
NAUTOBOT_DB_PORT=5432

# Redis Configuration
NAUTOBOT_REDIS_HOST=redis
NAUTOBOT_REDIS_PORT=6379
NAUTOBOT_REDIS_PASSWORD=
NAUTOBOT_REDIS_SSL=false

# ServiceNow Groups Plugin Configuration
SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING=true
SERVICENOW_GROUPS_ENABLE_GRAPHQL=true
SERVICENOW_GROUPS_ENABLE_ADMIN=true
SERVICENOW_GROUPS_DEFAULT_PREFIX=SN_
SERVICENOW_GROUPS_MAX_GROUPS_PER_DEVICE=10
SERVICENOW_GROUPS_CACHE_TIMEOUT=300

# Docker Configuration
COMPOSE_PROJECT_NAME=nautobot-servicenow-groups
```

### 3. Start the Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f nautobot
```

### 4. Initialize the Database

```bash
# Run database migrations
docker-compose exec nautobot nautobot-server migrate

# Create a superuser
docker-compose exec nautobot nautobot-server createsuperuser

# Collect static files
docker-compose exec nautobot nautobot-server collectstatic --noinput
```

### 5. Access the Application

- **Nautobot UI**: http://localhost:8080
- **Admin Interface**: http://localhost:8080/admin/
- **API Documentation**: http://localhost:8080/api/docs/

## Docker Compose Configuration

### Service Overview

The `docker-compose.yml` file includes the following services:

```yaml
services:
  postgres:      # PostgreSQL database
  redis:         # Redis cache and message broker
  nautobot:      # Main Nautobot application
  nautobot-worker:    # Background task worker
  nautobot-scheduler: # Task scheduler
```

### Customizing the Configuration

#### Database Configuration

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: nautobot
      POSTGRES_USER: nautobot
      POSTGRES_PASSWORD: nautobot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nautobot"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### Redis Configuration

```yaml
services:
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### Nautobot Configuration

```yaml
services:
  nautobot:
    build: .
    environment:
      NAUTOBOT_DB_HOST: postgres
      NAUTOBOT_DB_NAME: nautobot
      NAUTOBOT_DB_USER: nautobot
      NAUTOBOT_DB_PASSWORD: nautobot
      NAUTOBOT_REDIS_HOST: redis
      NAUTOBOT_REDIS_PORT: 6379
      NAUTOBOT_SECRET_KEY: your-secret-key-here
      NAUTOBOT_ALLOWED_HOSTS: localhost,127.0.0.1
      PLUGINS: service_now_groups
    volumes:
      - ./nautobot_config.py:/app/nautobot_config.py:ro
      - ./media:/app/media
      - ./static:/app/static
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```

## Docker Image Building

### Building the Image

```bash
# Build the image locally
docker build -t nautobot-servicenow-groups:latest .

# Build with specific tag
docker build -t nautobot-servicenow-groups:v1.0.0 .

# Build with build arguments
docker build \
  --build-arg NAUTOBOT_VERSION=1.6.0 \
  --build-arg PYTHON_VERSION=3.9 \
  -t nautobot-servicenow-groups:latest .
```

### Multi-Stage Build

The Dockerfile uses multi-stage builds for optimization:

```dockerfile
# Build stage
FROM python:3.9-slim as builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "nautobot==${NAUTOBOT_VERSION}" && \
    pip install --no-cache-dir -e .

# Production stage
FROM python:3.9-slim

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# ... rest of production configuration
```

### Image Optimization

```bash
# Build optimized image
docker build \
  --target production \
  --no-cache \
  --compress \
  -t nautobot-servicenow-groups:optimized .

# Check image size
docker images nautobot-servicenow-groups
```

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace nautobot-servicenow-groups
```

### 2. Create ConfigMap

```yaml
# k8s-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nautobot-config
  namespace: nautobot-servicenow-groups
data:
  NAUTOBOT_SECRET_KEY: "your-super-secret-key-here"
  NAUTOBOT_ALLOWED_HOSTS: "nautobot.example.com"
  NAUTOBOT_DEBUG: "false"
  PLUGINS: "service_now_groups"
  SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING: "true"
  SERVICENOW_GROUPS_ENABLE_GRAPHQL: "true"
  SERVICENOW_GROUPS_ENABLE_ADMIN: "true"
  SERVICENOW_GROUPS_DEFAULT_PREFIX: "SN_"
  SERVICENOW_GROUPS_MAX_GROUPS_PER_DEVICE: "10"
  SERVICENOW_GROUPS_CACHE_TIMEOUT: "300"
```

### 3. Create Secret

```yaml
# k8s-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: nautobot-secret
  namespace: nautobot-servicenow-groups
type: Opaque
data:
  NAUTOBOT_DB_PASSWORD: bmF1dG9ib3Q=  # base64 encoded
  NAUTOBOT_REDIS_PASSWORD: ""  # empty for no password
```

### 4. Create Persistent Volume Claims

```yaml
# k8s-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nautobot-media
  namespace: nautobot-servicenow-groups
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nautobot-static
  namespace: nautobot-servicenow-groups
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### 5. Create Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nautobot
  namespace: nautobot-servicenow-groups
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nautobot
  template:
    metadata:
      labels:
        app: nautobot
    spec:
      containers:
      - name: nautobot
        image: nautobot-servicenow-groups:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: nautobot-config
        - secretRef:
            name: nautobot-secret
        env:
        - name: NAUTOBOT_DB_HOST
          value: "postgres-service"
        - name: NAUTOBOT_REDIS_HOST
          value: "redis-service"
        volumeMounts:
        - name: media
          mountPath: /app/media
        - name: static
          mountPath: /app/static
        livenessProbe:
          httpGet:
            path: /health/
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: media
        persistentVolumeClaim:
          claimName: nautobot-media
      - name: static
        persistentVolumeClaim:
          claimName: nautobot-static
```

### 6. Create Services

```yaml
# k8s-services.yaml
apiVersion: v1
kind: Service
metadata:
  name: nautobot-service
  namespace: nautobot-servicenow-groups
spec:
  selector:
    app: nautobot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: nautobot-servicenow-groups
spec:
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: nautobot-servicenow-groups
spec:
  selector:
    app: redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
  type: ClusterIP
```

### 7. Create Ingress

```yaml
# k8s-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nautobot-ingress
  namespace: nautobot-servicenow-groups
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - nautobot.example.com
    secretName: nautobot-tls
  rules:
  - host: nautobot.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nautobot-service
            port:
              number: 80
```

### 8. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s-configmap.yaml
kubectl apply -f k8s-secret.yaml
kubectl apply -f k8s-pvc.yaml
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-services.yaml
kubectl apply -f k8s-ingress.yaml

# Check deployment status
kubectl get pods -n nautobot-servicenow-groups
kubectl get services -n nautobot-servicenow-groups
kubectl get ingress -n nautobot-servicenow-groups
```

## Helm Chart Installation

### 1. Add Helm Repository

```bash
# Add the Helm repository (if available)
helm repo add nautobot-servicenow-groups https://your-org.github.io/nautobot-servicenow-groups
helm repo update
```

### 2. Install with Helm

```bash
# Install with default values
helm install nautobot-servicenow-groups nautobot-servicenow-groups/nautobot-servicenow-groups \
  --namespace nautobot-servicenow-groups \
  --create-namespace

# Install with custom values
helm install nautobot-servicenow-groups nautobot-servicenow-groups/nautobot-servicenow-groups \
  --namespace nautobot-servicenow-groups \
  --create-namespace \
  --values values.yaml
```

### 3. Custom Values File

```yaml
# values.yaml
nautobot:
  replicaCount: 3
  image:
    repository: nautobot-servicenow-groups
    tag: latest
    pullPolicy: IfNotPresent
  
  env:
    NAUTOBOT_SECRET_KEY: "your-super-secret-key-here"
    NAUTOBOT_ALLOWED_HOSTS: "nautobot.example.com"
    PLUGINS: "service_now_groups"
    SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING: "true"
    SERVICENOW_GROUPS_DEFAULT_PREFIX: "SN_"
  
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"
  
  persistence:
    media:
      enabled: true
      size: 10Gi
    static:
      enabled: true
      size: 5Gi

postgresql:
  enabled: true
  postgresqlPassword: "nautobot"
  postgresqlDatabase: "nautobot"
  persistence:
    enabled: true
    size: 8Gi

redis:
  enabled: true
  auth:
    enabled: false
  persistence:
    enabled: true
    size: 5Gi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: nautobot.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: nautobot-tls
      hosts:
        - nautobot.example.com
```

## Production Deployment

### Security Considerations

1. **Secrets Management**:
   ```bash
   # Use Kubernetes secrets or external secret management
   kubectl create secret generic nautobot-secret \
     --from-literal=NAUTOBOT_SECRET_KEY="your-secret-key" \
     --from-literal=NAUTOBOT_DB_PASSWORD="your-db-password"
   ```

2. **Network Security**:
   ```yaml
   # Network policies
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: nautobot-network-policy
   spec:
     podSelector:
       matchLabels:
         app: nautobot
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - namespaceSelector:
           matchLabels:
             name: ingress-nginx
       ports:
       - protocol: TCP
         port: 8080
   ```

3. **Resource Limits**:
   ```yaml
   resources:
     requests:
       memory: "1Gi"
       cpu: "500m"
     limits:
       memory: "2Gi"
       cpu: "1000m"
   ```

### Monitoring and Logging

1. **Health Checks**:
   ```yaml
   livenessProbe:
     httpGet:
       path: /health/
       port: 8080
     initialDelaySeconds: 30
     periodSeconds: 10
     timeoutSeconds: 5
     failureThreshold: 3
   readinessProbe:
     httpGet:
       path: /health/
       port: 8080
     initialDelaySeconds: 5
     periodSeconds: 5
     timeoutSeconds: 3
     failureThreshold: 3
   ```

2. **Logging Configuration**:
   ```yaml
   env:
   - name: LOG_LEVEL
     value: "INFO"
   - name: LOG_FORMAT
     value: "json"
   ```

### Backup and Recovery

1. **Database Backup**:
   ```bash
   # Create backup job
   kubectl create job --from=cronjob/backup-job backup-manual
   
   # Restore from backup
   kubectl exec -it postgres-pod -- pg_restore -d nautobot backup.dump
   ```

2. **Volume Snapshots**:
   ```yaml
   apiVersion: snapshot.storage.k8s.io/v1
   kind: VolumeSnapshot
   metadata:
     name: nautobot-snapshot
   spec:
     source:
       persistentVolumeClaimName: nautobot-media
   ```

## Troubleshooting

### Common Issues

1. **Container Won't Start**:
   ```bash
   # Check container logs
   docker-compose logs nautobot
   kubectl logs -f deployment/nautobot
   
   # Check resource usage
   docker stats
   kubectl top pods
   ```

2. **Database Connection Issues**:
   ```bash
   # Test database connectivity
   docker-compose exec nautobot nautobot-server dbshell
   kubectl exec -it postgres-pod -- psql -U nautobot -d nautobot
   ```

3. **Plugin Not Loading**:
   ```bash
   # Check plugin configuration
   docker-compose exec nautobot nautobot-server shell
   >>> from django.conf import settings
   >>> print(settings.PLUGINS)
   ```

### Performance Tuning

1. **Database Optimization**:
   ```sql
   -- Add indexes for better performance
   CREATE INDEX CONCURRENTLY idx_servicenow_groups_locations 
   ON service_now_groups_servicenowgroup_locations (servicenowgroup_id, location_id);
   ```

2. **Cache Configuration**:
   ```yaml
   env:
   - name: SERVICENOW_GROUPS_CACHE_TIMEOUT
     value: "600"
   - name: SERVICENOW_GROUPS_CACHE_PREFIX
     value: "sng:"
   ```

### Scaling

1. **Horizontal Scaling**:
   ```bash
   # Scale Nautobot deployment
   kubectl scale deployment nautobot --replicas=5
   
   # Scale with HPA
   kubectl autoscale deployment nautobot --cpu-percent=70 --min=3 --max=10
   ```

2. **Database Scaling**:
   ```yaml
   # Use managed database service
   env:
   - name: NAUTOBOT_DB_HOST
     value: "your-managed-postgres-instance"
   ```

## Support

For containerized installation support:

- **Documentation**: [docs.nautobot.com](https://docs.nautobot.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/nautobot-servicenow-groups/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nautobot-servicenow-groups/discussions) 