#!/bin/bash
# UPID CLI Installation Script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 UPID CLI Installation${NC}"
echo -e "${BLUE}==========================${NC}"

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

# Check if binary exists locally first
BINARY_PATH="./dist/upid-$OS-$ARCH"
if [ -f "$BINARY_PATH" ]; then
    echo -e "${YELLOW}Using local binary: $BINARY_PATH${NC}"
    sudo cp "$BINARY_PATH" /usr/local/bin/upid
    sudo chmod +x /usr/local/bin/upid
else
    echo -e "${YELLOW}Downloading UPID CLI...${NC}"
    
    # Download from GitHub releases
    BINARY_NAME="upid-$OS-$ARCH"
    if [ "$OS" = "windows" ]; then
        BINARY_NAME="${BINARY_NAME}.exe"
    fi
    
    DOWNLOAD_URL="https://github.com/vellankikoti/upid-cli/releases/latest/download/$BINARY_NAME"
    echo -e "${YELLOW}URL: $DOWNLOAD_URL${NC}"
    
    # Download the binary
    if curl -L -o "/tmp/$BINARY_NAME" "$DOWNLOAD_URL"; then
        # Check if downloaded file is actually a binary (not a placeholder)
        if [ -s "/tmp/$BINARY_NAME" ]; then
            file_size=$(stat -f%z "/tmp/$BINARY_NAME" 2>/dev/null || stat -c%s "/tmp/$BINARY_NAME" 2>/dev/null || echo 0)
            if [ "$file_size" -lt 1000 ]; then
                echo -e "${RED}❌ Downloaded file is too small (${file_size} bytes) - likely a placeholder${NC}"
                echo -e "${YELLOW}This platform binary is not yet available.${NC}"
                echo -e "${BLUE}Available options:${NC}"
                echo -e "1. Build from source: git clone https://github.com/vellankikoti/upid-cli.git && cd upid-cli && python3 build_binary_fixed.py"
                echo -e "2. Use Docker: docker pull vellankikoti/upid-cli:latest"
                echo -e "3. Install via pip: pip install upid-cli"
                exit 1
            fi
        fi
        
        echo -e "${YELLOW}Installing to /usr/local/bin/upid...${NC}"
        sudo cp "/tmp/$BINARY_NAME" /usr/local/bin/upid
        sudo chmod +x /usr/local/bin/upid
        rm "/tmp/$BINARY_NAME"
    else
        echo -e "${RED}❌ Failed to download binary${NC}"
        echo -e "${YELLOW}Please check your internet connection and try again${NC}"
        exit 1
    fi
fi

# Verify installation
if command -v upid &> /dev/null; then
    echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
    
    # Test basic functionality
    echo -e "${YELLOW}Testing installation...${NC}"
    if upid --help &> /dev/null; then
        echo -e "${GREEN}✅ Basic functionality test passed${NC}"
        echo -e "${GREEN}Version: $(upid --version 2>/dev/null || echo '1.0.0')${NC}"
        echo -e "${YELLOW}Run 'upid --help' to get started${NC}"
    else
        echo -e "${RED}❌ Basic functionality test failed${NC}"
        echo -e "${YELLOW}The binary was installed but may not be working correctly${NC}"
    fi
else
    echo -e "${RED}❌ Installation failed${NC}"
    exit 1
fi
