#!/bin/bash

# Simple Branch Protection Setup
# This script sets up basic branch protection rules

echo "🛡️ Setting up simple branch protection rules..."

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

echo ""
echo "🔧 Manual setup required. Please follow these steps:"
echo ""
echo "1. Go to: https://github.com/$REPO/settings/branches"
echo ""
echo "2. For the 'main' branch, add a rule with:"
echo "   ✅ Require a pull request before merging"
echo "   ✅ Require approvals: 1"
echo "   ✅ Dismiss stale PR approvals when new commits are pushed"
echo "   ✅ Require review from code owners"
echo "   ✅ Require status checks to pass before merging"
echo "   ✅ Require branches to be up to date before merging"
echo "   ✅ Restrict pushes that create files"
echo ""
echo "3. For the 'develop' branch, add a rule with:"
echo "   ✅ Require a pull request before merging"
echo "   ✅ Require approvals: 0 (optional)"
echo "   ✅ Allow force pushes"
echo ""
echo "4. Add these required status checks for main:"
echo "   - Production Security Scan"
echo "   - Deployment Security Gate"
echo ""
echo "5. Add this required status check for develop:"
echo "   - Security Scan"
echo ""
echo "🎉 Once configured, your branching strategy will be fully operational!"
echo ""
echo "📚 See docs/branching-strategy.md for detailed information"
