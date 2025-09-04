#!/bin/bash

# Install GitHub CLI on macOS
# This script downloads and installs GitHub CLI

set -e

echo "🚀 Installing GitHub CLI..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is for macOS only"
    exit 1
fi

# Check if GitHub CLI is already installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI is already installed"
    gh --version
    exit 0
fi

# Get the latest release URL
echo "📥 Downloading GitHub CLI..."
LATEST_RELEASE=$(curl -s https://api.github.com/repos/cli/cli/releases/latest)

# Use the universal macOS package
DOWNLOAD_URL=$(echo "$LATEST_RELEASE" | grep "browser_download_url.*macOS_universal.pkg" | cut -d '"' -f 4)

VERSION=$(echo "$LATEST_RELEASE" | grep "tag_name" | cut -d '"' -f 4)

echo "📦 Version: $VERSION"
echo "🔗 Download URL: $DOWNLOAD_URL"

# Download the installer
TEMP_DIR=$(mktemp -d)
PKG_FILE="$TEMP_DIR/gh.pkg"

echo "⬇️  Downloading installer..."
curl -L -o "$PKG_FILE" "$DOWNLOAD_URL"

# Install the package
echo "🔧 Installing GitHub CLI..."
sudo installer -pkg "$PKG_FILE" -target /

# Clean up
rm -rf "$TEMP_DIR"

# Verify installation
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI installed successfully!"
    gh --version
    echo ""
    echo "🔐 Next steps:"
    echo "1. Run: gh auth login"
    echo "2. Follow the authentication prompts"
    echo "3. Then I can help you manage GitHub issues and PRs!"
else
    echo "❌ Installation failed. Please try manual installation:"
    echo "1. Go to: https://github.com/cli/cli/releases/latest"
    echo "2. Download the macOS installer (.pkg file)"
    echo "3. Run the installer"
    echo "4. Restart your terminal"
fi
