#!/bin/bash
# UPID CLI Installation Script
# Installs UPID CLI like kubectl

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# GitHub release URL
RELEASE_URL="https://github.com/upid/upid-cli/releases/latest/download"
BINARY_NAME="upid-$OS-$ARCH"

echo -e "${GREEN}Installing UPID CLI...${NC}"
echo -e "${YELLOW}OS: $OS, Architecture: $ARCH${NC}"

# Download binary
echo -e "${YELLOW}Downloading UPID CLI binary...${NC}"
curl -L -o /tmp/upid "$RELEASE_URL/$BINARY_NAME"

# Make executable
chmod +x /tmp/upid

# Install to system path
if [[ "$OS" == "darwin" ]]; then
    sudo mv /tmp/upid /usr/local/bin/upid
else
    sudo mv /tmp/upid /usr/local/bin/upid
fi

# Verify installation
if command -v upid &> /dev/null; then
    echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
    echo -e "${GREEN}Version: $(upid --version)${NC}"
    echo -e "${YELLOW}Run 'upid --help' to get started${NC}"
else
    echo -e "${RED}❌ Installation failed${NC}"
    exit 1
fi
