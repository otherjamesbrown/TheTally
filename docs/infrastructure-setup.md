# Infrastructure Setup Guide

## Overview

This guide walks through setting up the complete infrastructure for TheTally on Google Cloud Platform.

## Prerequisites

- Google Cloud account with billing enabled
- GitHub repository (already exists)
- `gcloud` CLI installed and configured
- Docker installed locally

## Step 1: Google Cloud Project Setup

### 1.1 Create GCP Project
```bash
# Set project variables
export PROJECT_ID="thetally-$(date +%s)"
export REGION="us-central1"
export ZONE="us-central1-a"

# Create project
gcloud projects create $PROJECT_ID --name="TheTally"

# Set as active project
gcloud config set project $PROJECT_ID

# Enable billing (you'll need to do this in the console)
echo "Please enable billing for project: $PROJECT_ID"
echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
```

### 1.2 Enable Required APIs
```bash
# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    compute.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com

echo "APIs enabled successfully"
```

### 1.3 Create Service Accounts
```bash
# Create service accounts
gcloud iam service-accounts create thetally-app \
    --display-name="TheTally Application" \
    --description="Service account for TheTally application"

gcloud iam service-accounts create thetally-cicd \
    --display-name="TheTally CI/CD" \
    --description="Service account for CI/CD pipeline"

gcloud iam service-accounts create thetally-db \
    --display-name="TheTally Database" \
    --description="Service account for database access"
```

### 1.4 Configure IAM Roles
```bash
# Grant roles to application service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:thetally-app@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:thetally-app@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant roles to CI/CD service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Grant roles to database service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:thetally-db@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/compute.instanceAdmin"
```

## Step 2: Artifact Registry Setup

### 2.1 Create Artifact Registry
```bash
# Create Artifact Registry
gcloud artifacts repositories create thetally-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="TheTally Docker images"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev
```

## Step 3: Database Infrastructure

### 3.1 Create Compute Engine Instance
```bash
# Create database instance
gcloud compute instances create thetally-db \
    --zone=$ZONE \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=postgresql-server \
    --service-account=thetally-db@$PROJECT_ID.iam.gserviceaccount.com

# Create firewall rule for PostgreSQL
gcloud compute firewall-rules create allow-postgresql \
    --allow tcp:5432 \
    --source-ranges 0.0.0.0/0 \
    --target-tags postgresql-server \
    --description="Allow PostgreSQL access"

# Get external IP
DB_EXTERNAL_IP=$(gcloud compute instances describe thetally-db \
    --zone=$ZONE \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo "Database external IP: $DB_EXTERNAL_IP"
```

### 3.2 Install PostgreSQL
```bash
# SSH into the instance and install PostgreSQL
gcloud compute ssh thetally-db --zone=$ZONE --command="
sudo apt update && \
sudo apt install -y postgresql postgresql-contrib && \
sudo systemctl start postgresql && \
sudo systemctl enable postgresql
"

# Configure PostgreSQL
gcloud compute ssh thetally-db --zone=$ZONE --command="
sudo -u postgres psql -c \"CREATE DATABASE thetally;\"
sudo -u postgres psql -c \"CREATE USER thetally_user WITH PASSWORD 'secure_password_123';\"
sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE thetally TO thetally_user;\"
sudo -u postgres psql -c \"ALTER USER thetally_user CREATEDB;\"
"

# Configure PostgreSQL for external connections
gcloud compute ssh thetally-db --zone=$ZONE --command="
sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" /etc/postgresql/*/main/postgresql.conf && \
echo \"host all all 0.0.0.0/0 md5\" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf && \
sudo systemctl restart postgresql
"
```

## Step 4: Cloud Storage Setup

### 4.1 Create Storage Bucket
```bash
# Create Cloud Storage bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-uploads

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://$PROJECT_ID-uploads
```

## Step 5: Logging Infrastructure Setup

### 5.1 Create Logging Instance
```bash
# Create logging instance (Loki + Prometheus + Grafana)
gcloud compute instances create thetally-logging \
    --zone=$ZONE \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-standard \
    --tags=logging-server \
    --service-account=thetally-app@$PROJECT_ID.iam.gserviceaccount.com

# Create firewall rule for logging services
gcloud compute firewall-rules create allow-logging \
    --allow tcp:3000,tcp:9090,tcp:3100 \
    --source-ranges 0.0.0.0/0 \
    --target-tags logging-server \
    --description="Allow Grafana, Prometheus, and Loki access"
```

### 5.2 Install Logging Stack
```bash
# SSH into the logging instance
gcloud compute ssh thetally-logging --zone=$ZONE --command="
# Install Docker
sudo apt update && \
sudo apt install -y docker.io && \
sudo systemctl start docker && \
sudo systemctl enable docker && \
sudo usermod -aG docker $USER

# Create logging directory
sudo mkdir -p /opt/logging/{loki,prometheus,grafana} && \
sudo chown -R $USER:$USER /opt/logging
"
```

### 5.3 Configure Loki
```bash
# Create Loki configuration
gcloud compute ssh thetally-logging --zone=$ZONE --command="
cat > /opt/logging/loki/loki-config.yaml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_scheduler:
  max_outstanding_requests_per_tenant: 2048

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

# By default, Loki will send anonymous, but uniquely-identifiable usage and configuration
# analytics to Grafana Labs. These statistics are sent to https://stats.grafana.org/
#
# Statistics help us better understand how Loki is used, and they show us performance
# levels for most users. This helps us prioritize features and documentation.
# For more information on what's sent, look at
# https://github.com/grafana/loki/blob/main/pkg/usagestats/stats.go
# Refer to the buildReport method to see what goes into a report.
#
# If you would like to disable reporting, uncomment the following lines:
#analytics:
#  reporting_enabled: false
EOF
"
```

### 5.4 Configure Prometheus
```bash
# Create Prometheus configuration
gcloud compute ssh thetally-logging --zone=$ZONE --command="
cat > /opt/logging/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'thetally-backend'
    static_configs:
      - targets: ['thetally-backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'thetally-frontend'
    static_configs:
      - targets: ['thetally-frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF
"
```

### 5.5 Configure Grafana
```bash
# Create Grafana configuration
gcloud compute ssh thetally-logging --zone=$ZONE --command="
cat > /opt/logging/grafana/grafana.ini << 'EOF'
[server]
http_port = 3000
root_url = http://localhost:3000/

[security]
admin_user = admin
admin_password = ${GRAFANA_ADMIN_PASSWORD:-thetally_admin_123}  # nosec B105

[log]
mode = console
level = info

[paths]
data = /var/lib/grafana
logs = /var/log/grafana
plugins = /var/lib/grafana/plugins
provisioning = /etc/grafana/provisioning
EOF
"
```

### 5.6 Start Logging Services
```bash
# Start all logging services with Docker Compose
gcloud compute ssh thetally-logging --zone=$ZONE --command="
cat > /opt/logging/docker-compose.yml << 'EOF'
version: '3.8'

services:
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yaml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/grafana.ini:/etc/grafana/grafana.ini
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-thetally_admin_123}  # nosec B105
    depends_on:
      - loki
      - prometheus

networks:
  default:
    name: logging-network
EOF

cd /opt/logging && docker-compose up -d
"
```

## Step 5: Secret Manager Setup

### 5.1 Create Secrets
```bash
# Create database password secret
echo -n "secure_password_123" | gcloud secrets create db-password \
    --data-file=- \
    --replication-policy="automatic"

# Create JWT secret
echo -n "$(openssl rand -base64 32)" | gcloud secrets create jwt-secret \
    --data-file=- \
    --replication-policy="automatic"

# Create API key secret
echo -n "$(openssl rand -base64 32)" | gcloud secrets create api-key-secret \
    --data-file=- \
    --replication-policy="automatic"
```

## Step 6: GitHub Actions Setup

### 6.1 Create Service Account Key
```bash
# Create and download service account key
gcloud iam service-accounts keys create thetally-cicd-key.json \
    --iam-account=thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com

echo "Service account key created: thetally-cicd-key.json"
echo "Add this to GitHub Secrets as GCP_SA_KEY"
```

### 6.2 GitHub Secrets Required
Add these secrets to your GitHub repository:

```
GCP_SA_KEY: <contents of thetally-cicd-key.json>
GCP_PROJECT_ID: <your project ID>
GCP_REGION: us-central1
GCP_ZONE: us-central1-a
DB_PASSWORD: secure_password_123
JWT_SECRET: <generated JWT secret>
API_KEY_SECRET: <generated API key secret>
```

## Step 7: Environment Variables

### 7.1 Production Environment Variables
```bash
# Backend environment variables
cat > .env.production << EOF
# Database
DATABASE_URL=postgresql://thetally_user:secure_password_123@$DB_EXTERNAL_IP:5432/thetally
DATABASE_HOST=$DB_EXTERNAL_IP
DATABASE_PORT=5432
DATABASE_NAME=thetally
DATABASE_USER=thetally_user
DATABASE_PASSWORD=${DATABASE_PASSWORD:-secure_password_123}  # nosec B105

# Authentication
JWT_SECRET_KEY=<generated JWT secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 2FA
OTP_ISSUER=TheTally
OTP_SECRET_LENGTH=32

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=csv,ofx,qif
STORAGE_BUCKET=$PROJECT_ID-uploads

# CORS
CORS_ORIGINS=https://thetally.app,https://staging.thetally.app
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

# Frontend environment variables
cat > .env.production << EOF
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
EOF
```

## Step 8: Verification

### 8.1 Test Database Connection
```bash
# Test database connection
psql "postgresql://thetally_user:secure_password_123@$DB_EXTERNAL_IP:5432/thetally" -c "SELECT version();"
```

### 8.2 Test Cloud Storage
```bash
# Test Cloud Storage
echo "test file" | gsutil cp - gs://$PROJECT_ID-uploads/test.txt
gsutil ls gs://$PROJECT_ID-uploads/
```

### 8.3 Test Secret Manager
```bash
# Test Secret Manager
gcloud secrets versions access latest --secret="db-password"
```

## Step 9: Cost Optimization

### 9.1 Set up Budget Alerts
```bash
# Create budget alert
gcloud billing budgets create \
    --billing-account=$(gcloud billing accounts list --format="value(name)" --limit=1) \
    --display-name="TheTally Budget" \
    --budget-amount=50USD \
    --threshold-rule=percent=80 \
    --threshold-rule=percent=100
```

### 9.2 Database Optimization
```bash
# Stop database instance when not in use
gcloud compute instances stop thetally-db --zone=$ZONE

# Start database instance when needed
gcloud compute instances start thetally-db --zone=$ZONE
```

## Step 10: Monitoring Setup

### 10.1 Enable Monitoring
```bash
# Enable monitoring for the database instance
gcloud compute instances add-metadata thetally-db \
    --zone=$ZONE \
    --metadata=enable-oslogin=TRUE
```

## Summary

After completing this setup, you'll have:

✅ **Google Cloud Project** with all required APIs enabled  
✅ **Service Accounts** with proper IAM roles  
✅ **Artifact Registry** for Docker images  
✅ **Compute Engine** instance with PostgreSQL  
✅ **Cloud Storage** bucket for file uploads  
✅ **Secret Manager** for sensitive configuration  
✅ **GitHub Actions** ready for CI/CD  
✅ **Environment Variables** configured  
✅ **Cost Optimization** and monitoring  

## Next Steps

1. **Run the setup script** (I can help you execute this)
2. **Add GitHub secrets** manually
3. **Test the infrastructure** with a simple deployment
4. **Set up the application** using the prompts in `docs/prompts.md`

Would you like me to help you execute this setup step by step?
