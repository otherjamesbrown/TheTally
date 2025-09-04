#!/bin/bash

# Setup Google Code Assist (Gemini) for PR Reviews
# This script configures Google Code Assist for automated PR reviews

set -e

echo "🚀 Setting up Google Code Assist for PR reviews..."

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

# Create setup instructions
echo "📋 Creating setup instructions..."
cat > .github/GOOGLE_CODE_ASSIST_SETUP.md << EOF
# Google Code Assist Setup Instructions

## Overview

Google Code Assist (formerly Duet AI) provides AI-powered code reviews directly through GitHub integration. This setup configures Gemini Code Assist to automatically review your pull requests.

## Installation Steps

### 1. Install Google Code Assist for GitHub

1. Go to the [Gemini Code Assist for GitHub app page](https://github.com/apps/gemini-code-assist)
2. Sign in to your GitHub account
3. Click **Install**
4. Select the organization: **$REPO_OWNER**
5. Choose repositories to enable:
   - ✅ **$REPO_NAME** (select this repository)
6. Click **Install** to complete the setup

### 2. Complete Setup in Admin Console

After installation, you'll be redirected to the Gemini Code Assist Admin Console:

1. Login with your GitHub account
2. Select **$REPO_OWNER** from the dropdown
3. Review and accept the Google Terms of Service
4. Accept the Generative AI Prohibited Use Policy
5. Accept the Privacy Policy
6. Click **Complete setup**

### 3. Configure Branch Protection (Required)

To ensure all changes go through PRs:

1. Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/branches
2. Click **Add rule** for the main branch
3. Configure the following settings:
   - ✅ **Require a pull request before merging**
   - ✅ **Require approvals** (set to 1)
   - ✅ **Dismiss stale reviews when new commits are pushed**
   - ✅ **Require review from code owners** (optional)
   - ✅ **Restrict pushes that create files** (optional)
4. Click **Create**

### 4. Verify Configuration

The \`config.yaml\` file in your repository root customizes Gemini's behavior:

- **Severity Threshold**: MEDIUM (adjustable)
- **Max Comments**: 15 per PR
- **Focus Areas**: Security, performance, maintainability, testing
- **Project Context**: TheTally-specific rules and architecture
- **Ignore Patterns**: Documentation, logs, dependencies

## How It Works

### Automatic Reviews
- Gemini Code Assist automatically reviews every new PR
- Reviews include severity levels (Critical, High, Medium, Low)
- Provides code suggestions that can be committed directly
- References your project's style guide and rules

### Manual Commands
You can manually invoke Gemini in PR comments:

- \`/gemini summary\` - Get a summary of changes
- \`/gemini review\` - Get a detailed code review
- \`/gemini help\` - Show available commands
- \`/gemini\` - Ask specific questions about the code

### Review Focus Areas

Gemini will specifically check for:

#### Security 🔒
- JWT authentication implementation
- Input validation and sanitization
- SQL injection prevention
- Multi-tenant data isolation
- 2FA compliance

#### Architecture 🏗️
- Service layer separation
- Database model design
- API endpoint organization
- Error handling patterns
- Logging implementation

#### Code Quality 📝
- Type hints and TypeScript compliance
- Naming conventions
- Function complexity
- Documentation completeness
- Testing coverage

## Testing the Setup

1. Create a test branch: \`git checkout -b test-gemini-review\`
2. Make a small change to any code file
3. Commit and push: \`git push origin test-gemini-review\`
4. Create a PR to main branch
5. Watch for the \`gemini-code-assist[bot]\` to appear as a reviewer
6. Check the PR comments for the AI review

## Customization

Edit \`config.yaml\` to customize:

- **Severity threshold**: Change \`comment_severity_threshold\`
- **Max comments**: Adjust \`max_review_comments\`
- **Focus areas**: Modify \`focus_areas\` list
- **Ignore patterns**: Update \`ignore_patterns\`
- **Project context**: Add more specific rules

## Troubleshooting

### Common Issues

1. **Gemini not reviewing PRs**:
   - Check if the GitHub app is installed
   - Verify repository access in app settings
   - Ensure branch protection is enabled

2. **Reviews not appearing**:
   - Check PR is targeting the main branch
   - Verify the app has necessary permissions
   - Look for error messages in PR comments

3. **Customization not working**:
   - Ensure \`config.yaml\` is in repository root
   - Check YAML syntax is valid
   - Verify configuration keys are correct

### Getting Help

- [Google Code Assist Documentation](https://developers.google.com/gemini-code-assist/docs/review-github-code)
- [Customization Guide](https://developers.google.com/gemini-code-assist/docs/customize-gemini-behavior-github)
- Check GitHub App settings: https://github.com/settings/installations

## Benefits

✅ **No API keys required** - Uses Google's native integration
✅ **Automatic reviews** - Reviews every PR without manual triggers
✅ **Project-aware** - Understands TheTally's architecture and rules
✅ **Interactive** - Can ask questions and get clarifications
✅ **Customizable** - Tailored to your specific needs
✅ **Secure** - Reviews happen within Google's secure environment

EOF

echo "✅ Created setup instructions"

# Create a simple test workflow to verify the setup
cat > .github/workflows/test-gemini-setup.yml << 'EOF'
name: Test Gemini Code Assist Setup

on:
  workflow_dispatch:
  pull_request:
    types: [opened, synchronize]

jobs:
  test-setup:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Verify config.yaml exists
        run: |
          if [ -f "config.yaml" ]; then
            echo "✅ config.yaml found"
            echo "Configuration:"
            head -20 config.yaml
          else
            echo "❌ config.yaml not found"
            exit 1
          fi
      
      - name: Validate YAML syntax
        run: |
          python -c "import yaml; yaml.safe_load(open('config.yaml'))"
          echo "✅ YAML syntax is valid"
      
      - name: Check branch protection
        run: |
          echo "ℹ️  To enable branch protection:"
          echo "1. Go to repository Settings > Branches"
          echo "2. Add rule for main branch"
          echo "3. Enable 'Require a pull request before merging'"
EOF

echo "✅ Created test workflow"

# Make script executable
chmod +x scripts/setup-google-code-assist.sh

echo ""
echo "🎉 Google Code Assist setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Install the GitHub App:"
echo "   https://github.com/apps/gemini-code-assist"
echo ""
echo "2. Select this repository: $REPO_OWNER/$REPO_NAME"
echo ""
echo "3. Complete setup in the Admin Console"
echo ""
echo "4. Enable branch protection for main branch"
echo ""
echo "5. Test with a sample PR"
echo ""
echo "📖 See .github/GOOGLE_CODE_ASSIST_SETUP.md for detailed instructions"
echo ""
echo "🧪 Run the test workflow to verify setup:"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/actions/workflows/test-gemini-setup.yml"
