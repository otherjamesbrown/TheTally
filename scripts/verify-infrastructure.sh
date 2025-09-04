#!/bin/bash

# TheTally Infrastructure Verification Script
# This script verifies that the infrastructure is set up correctly

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

# Load infrastructure variables
if [ -f .env.infrastructure ]; then
    source .env.infrastructure
else
    print_error ".env.infrastructure file not found. Please run setup-infrastructure.sh first."
    exit 1
fi

# Test database connection
test_database() {
    print_status "Testing database connection..."
    
    if command -v psql &> /dev/null; then
        if psql "postgresql://thetally_user:secure_password_123@$DB_EXTERNAL_IP:5432/thetally" -c "SELECT version();" &> /dev/null; then
            print_success "Database connection successful"
        else
            print_error "Database connection failed"
            return 1
        fi
    else
        print_warning "psql not installed, skipping database test"
    fi
}

# Test Cloud Storage
test_storage() {
    print_status "Testing Cloud Storage..."
    
    if echo "test file" | gsutil cp - gs://$PROJECT_ID-uploads/test.txt &> /dev/null; then
        print_success "Cloud Storage test successful"
        gsutil rm gs://$PROJECT_ID-uploads/test.txt &> /dev/null
    else
        print_error "Cloud Storage test failed"
        return 1
    fi
}

# Test Secret Manager
test_secrets() {
    print_status "Testing Secret Manager..."
    
    if gcloud secrets versions access latest --secret="db-password" &> /dev/null; then
        print_success "Secret Manager test successful"
    else
        print_error "Secret Manager test failed"
        return 1
    fi
}

# Test Artifact Registry
test_artifact_registry() {
    print_status "Testing Artifact Registry..."
    
    if gcloud artifacts repositories describe thetally-repo --location=$REGION &> /dev/null; then
        print_success "Artifact Registry test successful"
    else
        print_error "Artifact Registry test failed"
        return 1
    fi
}

# Test Compute Engine instance
test_compute_instance() {
    print_status "Testing Compute Engine instance..."
    
    if gcloud compute instances describe thetally-db --zone=$ZONE &> /dev/null; then
        print_success "Compute Engine instance test successful"
    else
        print_error "Compute Engine instance test failed"
        return 1
    fi
}

# Main verification
main() {
    print_status "Starting infrastructure verification..."
    
    local failed_tests=0
    
    test_database || ((failed_tests++))
    test_storage || ((failed_tests++))
    test_secrets || ((failed_tests++))
    test_artifact_registry || ((failed_tests++))
    test_compute_instance || ((failed_tests++))
    
    if [ $failed_tests -eq 0 ]; then
        print_success "All infrastructure tests passed!"
        print_status "Your infrastructure is ready for development."
    else
        print_error "$failed_tests test(s) failed. Please check the setup."
        exit 1
    fi
}

main "$@"
