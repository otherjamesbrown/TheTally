#!/bin/bash

# Setup GitHub PR Workflow with AI Review
# This script configures GitHub repository settings for PR requirements and AI review

set -e

echo "🚀 Setting up GitHub PR workflow with AI review..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository. Please run this from the project root."
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"

# Get repository information
REPO_OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)

echo "📋 Repository: $REPO_OWNER/$REPO_NAME"

# Create .env.example file for required secrets
echo "📝 Creating .env.example file..."
cat > .env.example << EOF
# GitHub Secrets Required for AI PR Review
# Add these to your repository secrets at: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions

# OpenAI API Key for AI code review
OPENAI_API_KEY=your_openai_api_key_here

# GitHub Token (automatically provided by GitHub Actions)
# GITHUB_TOKEN=\${{ secrets.GITHUB_TOKEN }}
EOF

echo "✅ Created .env.example file"

# Create setup instructions
echo "📋 Creating setup instructions..."
cat > .github/PR_SETUP_INSTRUCTIONS.md << EOF
# GitHub PR Workflow Setup Instructions

## Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key for the AI reviewer
   - Get one from: https://platform.openai.com/api-keys
   - Add it to repository secrets as \`OPENAI_API_KEY\`

2. **Repository Secrets**: Add the following secrets to your repository:
   - Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions
   - Add: \`OPENAI_API_KEY\` with your OpenAI API key

## Branch Protection Setup

The repository is configured to require:
- ✅ Pull requests for all changes to main branch
- ✅ AI code review on every PR
- ✅ Passing tests before merge
- ✅ At least 1 approval required

## AI Review Features

The AI reviewer will check:
- 🔒 Security compliance (JWT auth, input validation, SQL injection prevention)
- 📝 Code quality (type hints, error handling, naming conventions)
- 🏗️ Architecture adherence (service layer, modularity, separation of concerns)
- 🧪 Testing requirements (unit tests, integration tests)
- 🏢 Multi-tenant considerations (tenant_id usage)
- 📊 Logging implementation (structured logging with three types)

## Workflow Files

- \`.github/workflows/ai-pr-review.yml\` - AI review workflow
- \`.github/workflows/setup-branch-protection.yml\` - Branch protection setup
- \`.github/scripts/ai_reviewer.py\` - AI review script
- \`.github/CODEOWNERS\` - Code ownership rules

## Testing the Setup

1. Create a test branch: \`git checkout -b test-ai-review\`
2. Make a small change to any file
3. Commit and push: \`git push origin test-ai-review\`
4. Create a PR to main branch
5. Check the Actions tab to see the AI review in action

## Manual Branch Protection Setup

If the automated setup doesn't work, manually enable branch protection:

1. Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/branches
2. Click "Add rule" for the main branch
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Dismiss stale reviews
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
4. Add required status checks: \`ai-review\`, \`test-backend\`, \`test-frontend\`
5. Click "Create"

EOF

echo "✅ Created setup instructions"

# Make scripts executable
chmod +x .github/scripts/ai_reviewer.py
chmod +x scripts/setup-github-pr-workflow.sh

echo "✅ Made scripts executable"

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Add your OpenAI API key to repository secrets:"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
echo ""
echo "2. Run the branch protection setup workflow:"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/actions/workflows/setup-branch-protection.yml"
echo ""
echo "3. Test the setup by creating a test PR"
echo ""
echo "📖 See .github/PR_SETUP_INSTRUCTIONS.md for detailed instructions"
