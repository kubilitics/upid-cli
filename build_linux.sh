#!/bin/bash
# UPID CLI Linux Build Script
# This script helps build UPID CLI binary on Linux systems

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔨 UPID CLI Linux Build Script${NC}"
echo -e "${BLUE}================================${NC}"

# Check if we're on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo -e "${RED}❌ This script is designed for Linux systems${NC}"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo -e "${YELLOW}Please install Python 3 first:${NC}"
    echo -e "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo -e "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo -e "  Amazon Linux: sudo yum install python3 python3-pip"
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    echo -e "${YELLOW}Please install git first:${NC}"
    echo -e "  Ubuntu/Debian: sudo apt install git"
    echo -e "  CentOS/RHEL: sudo yum install git"
    exit 1
fi

echo -e "${GREEN}✅ System requirements met${NC}"

# Clone the repository if not already present
if [ ! -d "upid-cli" ]; then
    echo -e "${YELLOW}Cloning UPID CLI repository...${NC}"
    git clone https://github.com/kubilitics/upid-cli.git
    cd upid-cli
else
    echo -e "${YELLOW}Using existing upid-cli directory${NC}"
    cd upid-cli
fi

# Create virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Build the binary
echo -e "${YELLOW}Building UPID CLI binary...${NC}"
python3 build_binary_fixed.py

# Install the binary
echo -e "${YELLOW}Installing binary to /usr/local/bin/upid...${NC}"
if [ -f "dist/upid-linux-x86_64" ]; then
    sudo cp dist/upid-linux-x86_64 /usr/local/bin/upid
    sudo chmod +x /usr/local/bin/upid
    echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
    
    # Test the installation
    echo -e "${YELLOW}Testing installation...${NC}"
    if upid --help &> /dev/null; then
        echo -e "${GREEN}✅ UPID CLI is working correctly!${NC}"
        echo -e "${YELLOW}Run 'upid --help' to see available commands${NC}"
    else
        echo -e "${RED}❌ Installation test failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Binary not found in dist/ directory${NC}"
    echo -e "${YELLOW}Check the build output above for errors${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 UPID CLI is ready to use!${NC}" 