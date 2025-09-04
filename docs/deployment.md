# Deployment Guide

## Overview

TheTally is deployed on Google Cloud Platform (GCP) using a containerized microservices architecture with automated CI/CD pipelines.

## Architecture

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Cloud Run     │    │   Compute Engine│
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (PostgreSQL)  │
│   Auto-scaling  │    │   Auto-scaling  │    │   Self-managed  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cloud Storage │
                       │   (File Uploads)│
                       └─────────────────┘
```

### Staging Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Cloud Run     │    │   Compute Engine│
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (PostgreSQL)  │
│   Staging       │    │   Staging       │    │   Staging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### GCP Setup
1. **Google Cloud Project**: Create a new GCP project
2. **APIs Enabled**: Enable required APIs
   - Cloud Run API
   - Compute Engine API
   - Artifact Registry API
   - Cloud Build API
   - Secret Manager API
   - Cloud Storage API

### Service Accounts
1. **CI/CD Service Account**: For GitHub Actions
2. **Application Service Account**: For Cloud Run services
3. **Database Service Account**: For Compute Engine database access
4. **Storage Service Account**: For Cloud Storage access

### Required Tools
- **Docker**: For containerization
- **gcloud CLI**: For GCP management
- **kubectl**: For Kubernetes management (if needed)

## Environment Configuration

### Environment Variables

#### Backend Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
DATABASE_HOST=your-cloud-sql-host
DATABASE_PORT=5432
DATABASE_NAME=thetally
DATABASE_USER=thetally_user
DATABASE_PASSWORD=secure_password

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 2FA
OTP_ISSUER=TheTally
OTP_SECRET_LENGTH=32

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=csv,ofx,qif

# CORS
CORS_ORIGINS=https://thetally.app,https://staging.thetally.app
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### Frontend Environment Variables
```bash
# API Configuration
REACT_APP_API_URL=https://api.thetally.app
REACT_APP_API_STAGING_URL=https://api-staging.thetally.app

# Authentication
REACT_APP_JWT_STORAGE_KEY=thetally_token
REACT_APP_REFRESH_TOKEN_KEY=thetally_refresh_token

# Feature Flags
REACT_APP_ENABLE_2FA=true
REACT_APP_ENABLE_FILE_UPLOAD=true
REACT_APP_ENABLE_ANALYTICS=false

# Environment
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
```

## Database Setup

### Compute Engine PostgreSQL Configuration
```bash
# Create Compute Engine instance for PostgreSQL
gcloud compute instances create thetally-db \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=postgresql-server

# Create firewall rule for PostgreSQL
gcloud compute firewall-rules create allow-postgresql \
    --allow tcp:5432 \
    --source-ranges 0.0.0.0/0 \
    --target-tags postgresql-server

# SSH into the instance and install PostgreSQL
gcloud compute ssh thetally-db --zone=us-central1-a

# On the instance, run:
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE thetally;
CREATE USER thetally_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE thetally TO thetally_user;
\q
```

### Database Migrations
```bash
# Set database URL for migrations
export DATABASE_URL="postgresql://thetally_user:secure_password@EXTERNAL_IP:5432/thetally"

# Run migrations
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "Initial migration"
```

### Cloud Storage Setup
```bash
# Create Cloud Storage bucket for file uploads
gsutil mb gs://thetally-uploads

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://thetally-uploads
```

## Container Configuration

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PROJECT_ID: thetally-gcp
  REGION: us-central1
  REGISTRY: gcr.io

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      - name: Run frontend tests
        run: |
          cd frontend
          npm run test:ci

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.PROJECT_ID }}
      - name: Configure Docker
        run: gcloud auth configure-docker
      - name: Build and push backend
        run: |
          cd backend
          docker build -t $REGISTRY/$PROJECT_ID/backend:$GITHUB_SHA .
          docker push $REGISTRY/$PROJECT_ID/backend:$GITHUB_SHA
      - name: Build and push frontend
        run: |
          cd frontend
          docker build -t $REGISTRY/$PROJECT_ID/frontend:$GITHUB_SHA .
          docker push $REGISTRY/$PROJECT_ID/frontend:$GITHUB_SHA

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: |
          gcloud run deploy backend-staging \
            --image $REGISTRY/$PROJECT_ID/backend:$GITHUB_SHA \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated
          gcloud run deploy frontend-staging \
            --image $REGISTRY/$PROJECT_ID/frontend:$GITHUB_SHA \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to production
        run: |
          gcloud run deploy backend \
            --image $REGISTRY/$PROJECT_ID/backend:$GITHUB_SHA \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated
          gcloud run deploy frontend \
            --image $REGISTRY/$PROJECT_ID/frontend:$GITHUB_SHA \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated
```

## Deployment Commands

### Manual Deployment
```bash
# Deploy backend
gcloud run deploy backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://thetally_user:secure_password@EXTERNAL_IP:5432/thetally"

# Deploy frontend
gcloud run deploy frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars REACT_APP_API_URL="https://backend-xxx-uc.a.run.app"
```

### Database Migration
```bash
# Run migrations using Cloud Run job
gcloud run jobs create migrate-db \
  --image gcr.io/thetally-gcp/backend:latest \
  --command "alembic" \
  --args "upgrade" "head" \
  --region us-central1 \
  --set-env-vars DATABASE_URL="postgresql://thetally_user:secure_password@EXTERNAL_IP:5432/thetally"

# Execute the migration job
gcloud run jobs execute migrate-db --region us-central1
```

## Monitoring and Logging

### Cloud Monitoring
- **Metrics**: Response time, error rate, throughput
- **Alerts**: High error rate, slow response time
- **Dashboards**: Real-time application metrics

### Cloud Logging
- **Structured Logs**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Retention**: 30 days for application logs

### Health Checks
- **Backend**: `/health` endpoint
- **Frontend**: `/health` endpoint
- **Database**: Connection health check

## Security Configuration

### IAM Roles
- **Cloud Run Service Account**: Minimal required permissions
- **Database Service Account**: Compute Engine database access only
- **Storage Service Account**: Cloud Storage access only
- **CI/CD Service Account**: Build and deploy permissions

### Network Security
- **VPC**: Private network configuration
- **Firewall**: Restrictive firewall rules
- **SSL/TLS**: Automatic certificate management

### Secrets Management
- **Secret Manager**: Store sensitive configuration
- **Environment Variables**: Non-sensitive configuration
- **Key Rotation**: Regular key rotation schedule

## Rollback Strategy

### Automatic Rollback
- **Health Check Failure**: Automatic rollback on health check failure
- **Error Rate Threshold**: Rollback if error rate exceeds 5%
- **Response Time Threshold**: Rollback if response time exceeds 5s

### Manual Rollback
```bash
# Rollback to previous version
gcloud run services update-traffic backend \
  --to-revisions=backend-00001-abc=100 \
  --region us-central1
```

## Disaster Recovery

### Backup Strategy
- **Database**: Daily automated backups to Cloud Storage
- **Application**: Container image backups in Artifact Registry
- **Configuration**: Infrastructure as Code backups
- **File Uploads**: Cloud Storage with versioning enabled

### Recovery Procedures
- **Database Recovery**: Point-in-time recovery
- **Application Recovery**: Container image restoration
- **Configuration Recovery**: Infrastructure redeployment

---

*This deployment guide will be updated as the infrastructure evolves and new deployment requirements emerge.*
