#!/bin/bash

# Setup Branch Protection Rules
# Run this script to set up branch protection rules in GitHub

echo "🛡️ Setting up branch protection rules..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Please install it first:"
    echo "   brew install gh"
    echo "   gh auth login"
    exit 1
fi

# Get repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"

# Set up main branch protection
echo "🔒 Setting up main branch protection..."
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Production Security Scan","Deployment Security Gate"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field allow_force_pushes=false \
  --field allow_deletions=false

echo "✅ Main branch protection configured"

# Set up develop branch protection (less strict)
echo "🔒 Setting up develop branch protection..."
gh api repos/$REPO/branches/develop/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Security Scan"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":0,"dismiss_stale_reviews":false,"require_code_owner_reviews":false}' \
  --field allow_force_pushes=true \
  --field allow_deletions=false

echo "✅ Develop branch protection configured"
echo "🎉 Branch protection setup complete!"
