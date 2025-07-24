#!/bin/bash
# UPID CLI Installation Script - Enterprise Grade
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
UPID_VERSION="1.0.0"
INSTALL_DIR="/usr/local/bin"
BINARY_NAME="upid"

# Platform detection
detect_platform() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case "$OS" in
        darwin)
            case "$ARCH" in
                arm64|aarch64) echo "macos-arm64" ;;
                *) echo "macos-amd64" ;;
            esac
            ;;
        linux)
            case "$ARCH" in
                arm64|aarch64) echo "linux-arm64" ;;
                *) echo "linux-amd64" ;;
            esac
            ;;
        *)
            echo "Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# Main installation function
install_upid() {
    echo -e "${BLUE}🚀 Installing UPID CLI v${UPID_VERSION}${NC}"
    
    PLATFORM=$(detect_platform)
    echo -e "${YELLOW}📋 Detected platform: ${PLATFORM}${NC}"
    
    # Download URL (update this with your GitHub releases URL)
    DOWNLOAD_URL="https://github.com/your-org/upid-cli/releases/download/v${UPID_VERSION}/upid-${UPID_VERSION}-${PLATFORM}"
    
    # Create temporary directory
    TMP_DIR=$(mktemp -d)
    trap "rm -rf $TMP_DIR" EXIT
    
    echo -e "${YELLOW}📥 Downloading UPID CLI...${NC}"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "${DOWNLOAD_URL}" -o "${TMP_DIR}/upid"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "${DOWNLOAD_URL}" -O "${TMP_DIR}/upid"
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one of them.${NC}"
        exit 1
    fi
    
    # Make executable
    chmod +x "${TMP_DIR}/upid"
    
    # Install to system
    echo -e "${YELLOW}📦 Installing to ${INSTALL_DIR}...${NC}"
    if [[ $EUID -eq 0 ]]; then
        mv "${TMP_DIR}/upid" "${INSTALL_DIR}/upid"
    else
        sudo mv "${TMP_DIR}/upid" "${INSTALL_DIR}/upid"
    fi
    
    # Verify installation
    if command -v upid >/dev/null 2>&1; then
        echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
        echo -e "${BLUE}📋 Version: $(upid --version)${NC}"
        echo -e "${YELLOW}🚀 Try: upid --help${NC}"
    else
        echo -e "${RED}❌ Installation failed. Please check your PATH.${NC}"
        exit 1
    fi
}

# Check if running as installer
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_upid
fi
