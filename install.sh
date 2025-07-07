#!/bin/bash
# UPID CLI Installation Script
# Installs UPID CLI like kubectl

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub repository info
GITHUB_REPO="vellankikoti/upid-cli"
RELEASE_URL="https://github.com/$GITHUB_REPO/releases/latest/download"

echo -e "${BLUE}🚀 UPID CLI Installation${NC}"
echo "=========================="

# Detect OS and architecture
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m | tr '[:upper:]' '[:lower:]')"

# Map architecture
case $ARCH in
    x86_64) ARCH="x86_64" ;;
    amd64) ARCH="x86_64" ;;
    arm64) ARCH="arm64" ;;
    aarch64) ARCH="arm64" ;;
    *) echo -e "${RED}Unsupported architecture: $ARCH${NC}" && exit 1 ;;
esac

# Map OS
case $OS in
    darwin) OS="darwin" ;;
    linux) OS="linux" ;;
    *) echo -e "${RED}Unsupported OS: $OS${NC}" && exit 1 ;;
esac

echo -e "${YELLOW}Detected: $OS $ARCH${NC}"

# Determine binary name
BINARY_NAME="upid-$OS-$ARCH"
if [ "$OS" = "windows" ]; then
    BINARY_NAME="${BINARY_NAME}.exe"
fi

# Download URL
DOWNLOAD_URL="$RELEASE_URL/$BINARY_NAME"

echo -e "${YELLOW}Downloading UPID CLI...${NC}"
echo "URL: $DOWNLOAD_URL"

# Download binary
if command -v curl &> /dev/null; then
    curl -L -o /tmp/upid "$DOWNLOAD_URL"
elif command -v wget &> /dev/null; then
    wget -O /tmp/upid "$DOWNLOAD_URL"
else
    echo -e "${RED}Error: Neither curl nor wget is installed${NC}"
    exit 1
fi

# Make executable
chmod +x /tmp/upid

# Install to system path
echo -e "${YELLOW}Installing to /usr/local/bin/upid...${NC}"
sudo mv /tmp/upid /usr/local/bin/upid

# Verify installation
if command -v upid &> /dev/null; then
    echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
    echo -e "${GREEN}Version: $(upid --version 2>/dev/null || echo "1.0.0")${NC}"
    echo -e "${YELLOW}Run 'upid --help' to get started${NC}"
    
    # Test basic functionality
    echo -e "\n${BLUE}Testing installation...${NC}"
    if upid --help &> /dev/null; then
        echo -e "${GREEN}✅ Basic functionality test passed${NC}"
    else
        echo -e "${RED}❌ Basic functionality test failed${NC}"
        exit 1
    fi
    
    echo -e "\n${GREEN}🎉 Installation complete!${NC}"
    echo -e "${BLUE}Quick start:${NC}"
    echo "  upid --help          # Show all commands"
    echo "  upid status          # Check UPID status"
    echo "  upid universal status # Check cluster health"
    echo "  upid demo            # Run demo"
    
else
    echo -e "${RED}❌ Installation failed${NC}"
    exit 1
fi
