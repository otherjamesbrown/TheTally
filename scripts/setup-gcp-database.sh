#!/bin/bash

# GCP PostgreSQL Database Setup Script for TheTally
# This script sets up a PostgreSQL database on Google Cloud Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
INSTANCE_NAME="${GCP_DATABASE_INSTANCE:-thetally-postgres}"
DATABASE_NAME="${GCP_DATABASE_NAME:-thetally_prod}"
DATABASE_USER="${GCP_DATABASE_USER:-thetally_user}"
DATABASE_VERSION="${GCP_DATABASE_VERSION:-POSTGRES_15}"
TIER="${GCP_DATABASE_TIER:-db-f1-micro}"

echo -e "${BLUE}🚀 Setting up PostgreSQL database on GCP...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Set project if provided
if [ -n "$PROJECT_ID" ]; then
    echo -e "${BLUE}📋 Setting project to: $PROJECT_ID${NC}"
    gcloud config set project "$PROJECT_ID"
else
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ No project set. Please set GCP_PROJECT_ID or run: gcloud config set project YOUR_PROJECT_ID${NC}"
        exit 1
    fi
    echo -e "${BLUE}📋 Using project: $PROJECT_ID${NC}"
fi

# Enable required APIs
echo -e "${BLUE}🔧 Enabling required APIs...${NC}"
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Check if instance already exists
if gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT_ID" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Instance $INSTANCE_NAME already exists${NC}"
    read -p "Do you want to continue with existing instance? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Setup cancelled${NC}"
        exit 1
    fi
else
    # Create Cloud SQL instance
    echo -e "${BLUE}🗄️  Creating Cloud SQL instance: $INSTANCE_NAME${NC}"
    gcloud sql instances create "$INSTANCE_NAME" \
        --database-version="$DATABASE_VERSION" \
        --tier="$TIER" \
        --region="$REGION" \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --backup-start-time=03:00 \
        --enable-bin-log \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --maintenance-release-channel=production \
        --deletion-protection \
        --project="$PROJECT_ID"
    
    echo -e "${GREEN}✅ Cloud SQL instance created successfully${NC}"
fi

# Set root password
echo -e "${BLUE}🔐 Setting root password...${NC}"
ROOT_PASSWORD=$(openssl rand -base64 32)  # nosec B105
gcloud sql users set-password root \
    --host=% \
    --instance="$INSTANCE_NAME" \
    --password="$ROOT_PASSWORD" \
    --project="$PROJECT_ID"

# Create database
echo -e "${BLUE}📊 Creating database: $DATABASE_NAME${NC}"
gcloud sql databases create "$DATABASE_NAME" \
    --instance="$INSTANCE_NAME" \
    --project="$PROJECT_ID" || echo -e "${YELLOW}⚠️  Database may already exist${NC}"

# Create database user
echo -e "${BLUE}👤 Creating database user: $DATABASE_USER${NC}"
DB_PASSWORD=$(openssl rand -base64 32)  # nosec B105
gcloud sql users create "$DATABASE_USER" \
    --instance="$INSTANCE_NAME" \
    --password="$DB_PASSWORD" \
    --project="$PROJECT_ID" || echo -e "${YELLOW}⚠️  User may already exist${NC}"

# Get instance connection name
CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --format="value(connectionName)")

# Get instance IP
INSTANCE_IP=$(gcloud sql instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --format="value(ipAddresses[0].ipAddress)")

echo -e "${GREEN}✅ Database setup completed successfully!${NC}"
echo
echo -e "${BLUE}📋 Database Information:${NC}"
echo "  Instance Name: $INSTANCE_NAME"
echo "  Connection Name: $CONNECTION_NAME"
echo "  IP Address: $INSTANCE_IP"
echo "  Database: $DATABASE_NAME"
echo "  User: $DATABASE_USER"
echo "  Region: $REGION"
echo
echo -e "${BLUE}🔐 Credentials:${NC}"
echo "  Root Password: $ROOT_PASSWORD"
echo "  User Password: $DB_PASSWORD"
echo
echo -e "${BLUE}🔗 Connection String:${NC}"
echo "  postgresql://$DATABASE_USER:$DB_PASSWORD@$INSTANCE_IP:5432/$DATABASE_NAME?sslmode=require"
echo
echo -e "${BLUE}📝 Environment Variables:${NC}"
echo "  export GCP_PROJECT_ID=$PROJECT_ID"
echo "  export GCP_DATABASE_HOST=$INSTANCE_IP"
echo "  export GCP_DATABASE_NAME=$DATABASE_NAME"
echo "  export GCP_DATABASE_USER=$DATABASE_USER"
echo "  export GCP_DATABASE_PASSWORD=$DB_PASSWORD"
echo
echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
echo "  1. Store these credentials securely (e.g., in Google Secret Manager)"
echo "  2. Never commit passwords to version control"
echo "  3. Use SSL connections in production"
echo "  4. Regularly rotate passwords"
echo
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "  1. Update your .env file with the database credentials"
echo "  2. Run database migrations: alembic upgrade head"
echo "  3. Test the connection: python -c \"from app.db.session import test_database_connection; print(test_database_connection())\""
echo
echo -e "${GREEN}🎉 Setup complete!${NC}"
