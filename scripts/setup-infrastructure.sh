#!/bin/bash

# TheTally Infrastructure Setup Script
# This script sets up the complete infrastructure on Google Cloud Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Please authenticate with gcloud first: gcloud auth login"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Set up project variables
setup_variables() {
    print_status "Setting up project variables..."
    
    # Use your existing project ID
    export PROJECT_ID="jamesbr-thetally"
    export REGION="us-central1"
    export ZONE="us-central1-a"
    
    print_status "Project ID: $PROJECT_ID"
    print_status "Region: $REGION"
    print_status "Zone: $ZONE"
    
    # Save variables to file for later use
    cat > .env.infrastructure << EOF
PROJECT_ID=$PROJECT_ID
REGION=$REGION
ZONE=$ZONE
EOF
    
    print_success "Project variables set"
}

# Set up existing GCP project
setup_project() {
    print_status "Setting up existing GCP project..."
    
    # Set as active project
    gcloud config set project $PROJECT_ID
    
    # Check if project exists and is accessible
    if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
        print_error "Project $PROJECT_ID not found or not accessible"
        print_error "Please check the project ID and your permissions"
        exit 1
    fi
    
    print_success "Project configured: $PROJECT_ID"
    print_warning "Please ensure billing is enabled for this project"
    print_warning "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."
    
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        compute.googleapis.com \
        storage.googleapis.com \
        secretmanager.googleapis.com \
        artifactregistry.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com
    
    print_success "APIs enabled"
}

# Create service accounts
create_service_accounts() {
    print_status "Creating service accounts..."
    
    # Create service accounts
    gcloud iam service-accounts create thetally-app \
        --display-name="TheTally Application" \
        --description="Service account for TheTally application" || true
    
    gcloud iam service-accounts create thetally-cicd \
        --display-name="TheTally CI/CD" \
        --description="Service account for CI/CD pipeline" || true
    
    gcloud iam service-accounts create thetally-db \
        --display-name="TheTally Database" \
        --description="Service account for database access" || true
    
    print_success "Service accounts created"
}

# Configure IAM roles
configure_iam() {
    print_status "Configuring IAM roles..."
    
    # Grant roles to application service account
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:thetally-app@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/storage.objectAdmin" || true
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:thetally-app@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" || true
    
    # Grant roles to CI/CD service account
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/run.admin" || true
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/artifactregistry.admin" || true
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="roles/iam.serviceAccountUser" || true
    
    print_success "IAM roles configured"
}

# Create Artifact Registry
create_artifact_registry() {
    print_status "Creating Artifact Registry..."
    
    gcloud artifacts repositories create thetally-repo \
        --repository-format=docker \
        --location=$REGION \
        --description="TheTally Docker images" || true
    
    # Configure Docker authentication
    gcloud auth configure-docker $REGION-docker.pkg.dev || true
    
    print_success "Artifact Registry created"
}

# Create database instance
create_database() {
    print_status "Creating database instance..."
    
    # Create database instance
    gcloud compute instances create thetally-db \
        --zone=$ZONE \
        --machine-type=e2-medium \
        --image-family=ubuntu-2004-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=20GB \
        --boot-disk-type=pd-standard \
        --tags=postgresql-server \
        --service-account=thetally-db@$PROJECT_ID.iam.gserviceaccount.com || true
    
    # Create firewall rule for PostgreSQL
    gcloud compute firewall-rules create allow-postgresql \
        --allow tcp:5432 \
        --source-ranges 0.0.0.0/0 \
        --target-tags postgresql-server \
        --description="Allow PostgreSQL access" || true
    
    # Get external IP
    DB_EXTERNAL_IP=$(gcloud compute instances describe thetally-db \
        --zone=$ZONE \
        --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
    
    echo "DB_EXTERNAL_IP=$DB_EXTERNAL_IP" >> .env.infrastructure
    
    print_success "Database instance created with IP: $DB_EXTERNAL_IP"
}

# Install PostgreSQL
install_postgresql() {
    print_status "Installing PostgreSQL..."
    
    # Wait for instance to be ready
    print_status "Waiting for instance to be ready..."
    sleep 30
    
    # Install PostgreSQL
    gcloud compute ssh thetally-db --zone=$ZONE --command="
        sudo apt update && \
        sudo apt install -y postgresql postgresql-contrib && \
        sudo systemctl start postgresql && \
        sudo systemctl enable postgresql
    " || {
        print_error "Failed to install PostgreSQL"
        exit 1
    }
    
    # Configure PostgreSQL
    gcloud compute ssh thetally-db --zone=$ZONE --command="
        sudo -u postgres psql -c \"CREATE DATABASE thetally;\"
        sudo -u postgres psql -c \"CREATE USER thetally_user WITH PASSWORD 'secure_password_123';\"
        sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE thetally TO thetally_user;\"
        sudo -u postgres psql -c \"ALTER USER thetally_user CREATEDB;\"
    " || {
        print_error "Failed to configure PostgreSQL"
        exit 1
    }
    
    # Configure PostgreSQL for external connections
    gcloud compute ssh thetally-db --zone=$ZONE --command="
        sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" /etc/postgresql/*/main/postgresql.conf && \
        echo \"host all all 0.0.0.0/0 md5\" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf && \
        sudo systemctl restart postgresql
    " || {
        print_error "Failed to configure PostgreSQL for external connections"
        exit 1
    }
    
    print_success "PostgreSQL installed and configured"
}

# Create Cloud Storage bucket
create_storage() {
    print_status "Creating Cloud Storage bucket..."
    
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-uploads || true
    gsutil iam ch allUsers:objectViewer gs://$PROJECT_ID-uploads || true
    
    print_success "Cloud Storage bucket created"
}

# Create logging infrastructure
create_logging() {
    print_status "Creating logging infrastructure..."
    
    # Create logging instance
    gcloud compute instances create thetally-logging \
        --zone=$ZONE \
        --machine-type=e2-medium \
        --image-family=ubuntu-2004-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=50GB \
        --boot-disk-type=pd-standard \
        --tags=logging-server \
        --service-account=thetally-app@$PROJECT_ID.iam.gserviceaccount.com || true
    
    # Create firewall rule for logging services
    gcloud compute firewall-rules create allow-logging \
        --allow tcp:3000,tcp:9090,tcp:3100 \
        --source-ranges 0.0.0.0/0 \
        --target-tags logging-server \
        --description="Allow Grafana, Prometheus, and Loki access" || true
    
    # Get external IP
    LOGGING_EXTERNAL_IP=$(gcloud compute instances describe thetally-logging \
        --zone=$ZONE \
        --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
    
    echo "LOGGING_EXTERNAL_IP=$LOGGING_EXTERNAL_IP" >> .env.infrastructure
    
    print_success "Logging infrastructure created with IP: $LOGGING_EXTERNAL_IP"
}

# Create secrets
create_secrets() {
    print_status "Creating secrets..."
    
    # Create database password secret
    echo -n "secure_password_123" | gcloud secrets create db-password \
        --data-file=- \
        --replication-policy="automatic" || true
    
    # Create JWT secret
    JWT_SECRET=$(openssl rand -base64 32)
    echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret \
        --data-file=- \
        --replication-policy="automatic" || true
    
    # Create API key secret
    API_KEY_SECRET=$(openssl rand -base64 32)
    echo -n "$API_KEY_SECRET" | gcloud secrets create api-key-secret \
        --data-file=- \
        --replication-policy="automatic" || true
    
    echo "JWT_SECRET=$JWT_SECRET" >> .env.infrastructure
    echo "API_KEY_SECRET=$API_KEY_SECRET" >> .env.infrastructure
    
    print_success "Secrets created"
}

# Create service account key
create_service_account_key() {
    print_status "Creating service account key..."
    
    gcloud iam service-accounts keys create thetally-cicd-key.json \
        --iam-account=thetally-cicd@$PROJECT_ID.iam.gserviceaccount.com || true
    
    print_success "Service account key created: thetally-cicd-key.json"
}

# Generate environment files
generate_env_files() {
    print_status "Generating environment files..."
    
    # Load variables
    source .env.infrastructure
    
    # Backend environment variables
    cat > .env.production << EOF
# Database
DATABASE_URL=postgresql://thetally_user:secure_password_123@$DB_EXTERNAL_IP:5432/thetally
DATABASE_HOST=$DB_EXTERNAL_IP
DATABASE_PORT=5432
DATABASE_NAME=thetally
DATABASE_USER=thetally_user
DATABASE_PASSWORD=${DATABASE_PASSWORD:-secure_password_123}

# Authentication
JWT_SECRET_KEY=$JWT_SECRET
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
    cat > frontend/.env.production << EOF
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

    print_success "Environment files generated"
}

# Main execution
main() {
    print_status "Starting TheTally infrastructure setup..."
    
    check_prerequisites
    setup_variables
    setup_project
    enable_apis
    create_service_accounts
    configure_iam
    create_artifact_registry
    create_database
    install_postgresql
    create_storage
    create_logging
    create_secrets
    create_service_account_key
    generate_env_files
    
    print_success "Infrastructure setup completed!"
    
    echo ""
    print_status "Next steps:"
    echo "1. Add thetally-cicd-key.json to GitHub Secrets as GCP_SA_KEY"
    echo "2. Add the following to GitHub Secrets:"
    echo "   - GCP_PROJECT_ID: $PROJECT_ID"
    echo "   - GCP_REGION: $REGION"
    echo "   - GCP_ZONE: $ZONE"
    echo "   - DB_PASSWORD: secure_password_123"
    echo "   - JWT_SECRET: $JWT_SECRET"
    echo "   - API_KEY_SECRET: $API_KEY_SECRET"
    echo "3. Test the database connection"
    echo "4. Start developing using the prompts in docs/prompts.md"
    
    echo ""
    print_status "Infrastructure details saved to .env.infrastructure"
}

# Run main function
main "$@"
