#!/bin/bash

# TheTally Environment Configuration Script
# This script helps configure the environment for different deployment scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [ENVIRONMENT] [ACTION]"
    echo ""
    echo "Environments:"
    echo "  development  - Local development environment"
    echo "  staging      - Staging environment on GCP"
    echo "  production   - Production environment on GCP"
    echo "  local        - Local infrastructure (Docker Compose)"
    echo ""
    echo "Actions:"
    echo "  setup        - Set up the environment"
    echo "  configure    - Configure environment variables"
    echo "  deploy       - Deploy the application"
    echo "  status       - Check environment status"
    echo "  clean        - Clean up the environment"
    echo ""
    echo "Examples:"
    echo "  $0 development setup"
    echo "  $0 production configure"
    echo "  $0 local deploy"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if required tools are installed
    local missing_tools=()
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi
    
    if [ "$1" != "local" ] && ! command -v gcloud &> /dev/null; then
        missing_tools+=("gcloud")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install the missing tools and try again."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup development environment
setup_development() {
    print_status "Setting up development environment..."
    
    # Create development environment file
    cat > .env.development << EOF
# Development Environment Variables
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://thetally_user:password@localhost:5432/thetally_dev
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=thetally_dev
DATABASE_USER=thetally_user
DATABASE_PASSWORD=${DATABASE_PASSWORD:-password}  # nosec B105

# Logging
LOKI_URL=http://localhost:3100
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000

# Application
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000

# Security
JWT_SECRET=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=csv,ofx,qif
UPLOAD_PATH=./uploads

# Redis
REDIS_URL=redis://localhost:6379/0
EOF

    print_success "Development environment configured"
}

# Function to setup production environment
setup_production() {
    print_status "Setting up production environment..."
    
    # Check if gcloud is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Please authenticate with gcloud first: gcloud auth login"
        exit 1
    fi
    
    # Set the project
    gcloud config set project jamesbr-thetally
    
    # Create production environment file
    cat > .env.production << EOF
# Production Environment Variables
ENVIRONMENT=production
DEBUG=false

# Database (will be set by infrastructure setup)
DATABASE_URL=\${DATABASE_URL}
DATABASE_HOST=\${DATABASE_HOST}
DATABASE_PORT=5432
DATABASE_NAME=thetally
DATABASE_USER=thetally_user
DATABASE_PASSWORD=\${DATABASE_PASSWORD}  # nosec B105

# Logging (will be set by infrastructure setup)
LOKI_URL=\${LOKI_URL}
PROMETHEUS_URL=\${PROMETHEUS_URL}
GRAFANA_URL=\${GRAFANA_URL}

# Application
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=80

# Security (will be set by Secret Manager)
JWT_SECRET=\${JWT_SECRET}
CORS_ORIGINS=https://thetally.app,https://staging.thetally.app

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=csv,ofx,qif
STORAGE_BUCKET=\${STORAGE_BUCKET}

# Redis
REDIS_URL=\${REDIS_URL}
EOF

    print_success "Production environment configured"
}

# Function to setup local environment
setup_local() {
    print_status "Setting up local environment..."
    
    # Create local environment file
    cat > .env.local << EOF
# Local Environment Variables
ENVIRONMENT=local
DEBUG=true

# Database
DATABASE_URL=postgresql://thetally_user:password@localhost:5432/thetally_local
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=thetally_local
DATABASE_USER=thetally_user
DATABASE_PASSWORD=${DATABASE_PASSWORD:-password}  # nosec B105

# Logging (using Docker services)
LOKI_URL=http://localhost:3100
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000

# Application
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000

# Security
JWT_SECRET=local-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=csv,ofx,qif
UPLOAD_PATH=./uploads

# Redis
REDIS_URL=redis://localhost:6379/0
EOF

    print_success "Local environment configured"
}

# Function to configure environment variables
configure_environment() {
    local environment=$1
    
    print_status "Configuring environment variables for $environment..."
    
    case $environment in
        "development")
            setup_development
            ;;
        "production")
            setup_production
            ;;
        "local")
            setup_local
            ;;
        *)
            print_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
}

# Function to deploy application
deploy_application() {
    local environment=$1
    
    print_status "Deploying application for $environment..."
    
    case $environment in
        "development")
            print_status "Starting development services..."
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        "production")
            print_status "Deploying to production..."
            ./scripts/setup-infrastructure.sh
            ;;
        "local")
            print_status "Starting local services..."
            docker-compose -f docker-compose.local.yml up -d
            ;;
        *)
            print_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
    
    print_success "Application deployed for $environment"
}

# Function to check environment status
check_status() {
    local environment=$1
    
    print_status "Checking status for $environment..."
    
    case $environment in
        "development"|"local")
            # Check Docker services
            if docker-compose ps | grep -q "Up"; then
                print_success "Services are running"
            else
                print_warning "Some services are not running"
            fi
            ;;
        "production")
            # Check GCP resources
            if gcloud compute instances list --filter="name~thetally" --format="value(name)" | grep -q .; then
                print_success "GCP resources are running"
            else
                print_warning "GCP resources not found"
            fi
            ;;
        *)
            print_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
}

# Function to clean up environment
clean_environment() {
    local environment=$1
    
    print_status "Cleaning up $environment environment..."
    
    case $environment in
        "development"|"local")
            docker-compose down -v
            print_success "Local environment cleaned"
            ;;
        "production")
            print_warning "Production cleanup not implemented for safety"
            ;;
        *)
            print_error "Unknown environment: $environment"
            exit 1
            ;;
    esac
}

# Main function
main() {
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi
    
    local environment=$1
    local action=$2
    
    print_status "Configuring $environment environment for $action..."
    
    check_prerequisites $environment
    
    case $action in
        "setup")
            configure_environment $environment
            ;;
        "configure")
            configure_environment $environment
            ;;
        "deploy")
            deploy_application $environment
            ;;
        "status")
            check_status $environment
            ;;
        "clean")
            clean_environment $environment
            ;;
        *)
            print_error "Unknown action: $action"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
