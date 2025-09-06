#!/bin/bash

# Setup Branching Strategy for TheTally
# This script helps set up the recommended branching strategy

set -e

echo "🌳 Setting up branching strategy for TheTally..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run this from the project root."
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Create develop branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo "🔧 Creating develop branch..."
    git checkout -b develop
    git push -u origin develop
    echo "✅ Develop branch created and pushed"
else
    echo "✅ Develop branch already exists"
    git checkout develop
fi

# Create .github/CODEOWNERS if it doesn't exist
if [ ! -f ".github/CODEOWNERS" ]; then
    echo "🔧 Creating CODEOWNERS file..."
    cat > .github/CODEOWNERS << EOF
# Global owners
* @otherjamesbrown

# Security-related files
.github/workflows/security-scan*.yml @otherjamesbrown
config/environments/production.yaml @otherjamesbrown
.bandit @otherjamesbrown

# Critical files
backend/app/core/config.py @otherjamesbrown
backend/app/services/ @otherjamesbrown
frontend/src/ @otherjamesbrown
EOF
    echo "✅ CODEOWNERS file created"
else
    echo "✅ CODEOWNERS file already exists"
fi

# Create branch protection setup script
cat > scripts/setup-branch-protection.sh << 'EOF'
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
  --field restrictions='{"users":[],"teams":[]}' \
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
  --field restrictions='{"users":[],"teams":[]}' \
  --field allow_force_pushes=true \
  --field allow_deletions=false

echo "✅ Develop branch protection configured"
echo "🎉 Branch protection setup complete!"
EOF

chmod +x scripts/setup-branch-protection.sh
echo "✅ Branch protection setup script created"

# Create feature branch template
cat > .github/ISSUE_TEMPLATE/feature_request.yml << 'EOF'
name: Feature Request
description: Request a new feature for TheTally
title: "[FEATURE] "
labels: ["enhancement", "feature"]
body:
  - type: markdown
    attributes:
      value: |
        ## Feature Request
        Please describe the feature you'd like to see implemented.
  - type: textarea
    id: feature-description
    attributes:
      label: Feature Description
      description: Describe the feature in detail
      placeholder: What would you like to see implemented?
    validations:
      required: true
  - type: textarea
    id: use-case
    attributes:
      label: Use Case
      description: How would this feature be used?
      placeholder: Describe the use case for this feature
    validations:
      required: true
  - type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance Criteria
      description: What needs to be done to consider this feature complete?
      placeholder: |
        - [ ] Criterion 1
        - [ ] Criterion 2
        - [ ] Criterion 3
    validations:
      required: true
  - type: dropdown
    id: priority
    attributes:
      label: Priority
      description: How important is this feature?
      options:
        - Low
        - Medium
        - High
        - Critical
    validations:
      required: true
  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any other context about the feature request
      placeholder: Add any other context or screenshots about the feature request here
EOF

echo "✅ Feature request template created"

# Create hotfix branch template
cat > .github/ISSUE_TEMPLATE/hotfix_request.yml << 'EOF'
name: Hotfix Request
description: Request an urgent fix for a critical issue
title: "[HOTFIX] "
labels: ["bug", "hotfix", "urgent"]
body:
  - type: markdown
    attributes:
      value: |
        ## Hotfix Request
        This is for urgent fixes that need to be deployed immediately.
  - type: textarea
    id: issue-description
    attributes:
      label: Issue Description
      description: Describe the critical issue
      placeholder: What is the problem that needs immediate fixing?
    validations:
      required: true
  - type: textarea
    id: impact
    attributes:
      label: Impact
      description: What is the impact of this issue?
      placeholder: Describe the impact on users or system
    validations:
      required: true
  - type: textarea
    id: steps-to-reproduce
    attributes:
      label: Steps to Reproduce
      description: How can this issue be reproduced?
      placeholder: |
        1. Step 1
        2. Step 2
        3. Step 3
    validations:
      required: true
  - type: dropdown
    id: severity
    attributes:
      label: Severity
      description: How severe is this issue?
      options:
        - Critical - System down
        - High - Major functionality broken
        - Medium - Minor functionality affected
    validations:
      required: true
  - type: textarea
    id: proposed-solution
    attributes:
      label: Proposed Solution
      description: How do you propose to fix this?
      placeholder: Describe your proposed solution
    validations:
      required: true
EOF

echo "✅ Hotfix request template created"

echo ""
echo "🎉 Branching strategy setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run: ./scripts/setup-branch-protection.sh"
echo "2. Create feature branches: git checkout -b feature/your-feature-name"
echo "3. Make changes and create PRs to develop"
echo "4. When ready, create PR from develop to main"
echo ""
echo "🔗 Useful commands:"
echo "  git checkout -b feature/your-feature-name"
echo "  git push -u origin feature/your-feature-name"
echo "  gh pr create --base develop"
echo "  gh pr create --base main"
echo ""
echo "📚 See docs/branching-strategy.md for detailed information"
