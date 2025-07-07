#!/bin/bash

# Prepare UPID CLI Release Files
# Creates release files in the standard kubectl pattern

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Preparing UPID CLI Release Files${NC}"
echo "======================================"

# Create releases directory
mkdir -p releases

# Get current version
VERSION="1.0.0"
echo -e "${YELLOW}Version: $VERSION${NC}"

# Copy binary to releases with proper naming
if [ -f "./dist/upid-darwin-arm64" ]; then
    echo -e "${YELLOW}Preparing macOS ARM64 binary...${NC}"
    cp ./dist/upid-darwin-arm64 ./releases/upid-darwin-arm64
    chmod +x ./releases/upid-darwin-arm64
    
    # Create tar.gz for macOS
    tar -czf ./releases/upid-darwin-arm64.tar.gz -C ./releases upid-darwin-arm64
    echo -e "${GREEN}✅ Created upid-darwin-arm64.tar.gz${NC}"
else
    echo -e "${RED}❌ Binary not found at ./dist/upid-darwin-arm64${NC}"
    echo "Please build the binary first: python build_binary_fixed.py"
    exit 1
fi

# Create placeholder files for other platforms (for GitHub Actions to fill)
echo -e "${YELLOW}Creating placeholder files for other platforms...${NC}"

# Linux x86_64 placeholder
echo "#!/bin/bash" > ./releases/upid-linux-x86_64
echo "echo 'Linux x86_64 binary - build with GitHub Actions'" >> ./releases/upid-linux-x86_64
chmod +x ./releases/upid-linux-x86_64
tar -czf ./releases/upid-linux-x86_64.tar.gz -C ./releases upid-linux-x86_64

# Linux ARM64 placeholder
echo "#!/bin/bash" > ./releases/upid-linux-arm64
echo "echo 'Linux ARM64 binary - build with GitHub Actions'" >> ./releases/upid-linux-arm64
chmod +x ./releases/upid-linux-arm64
tar -czf ./releases/upid-linux-arm64.tar.gz -C ./releases upid-linux-arm64

# Windows x86_64 placeholder
echo "@echo off" > ./releases/upid-windows-x86_64.exe
echo "echo Windows x86_64 binary - build with GitHub Actions" >> ./releases/upid-windows-x86_64.exe
zip -j ./releases/upid-windows-x86_64.zip ./releases/upid-windows-x86_64.exe

echo -e "${GREEN}✅ Created placeholder files for all platforms${NC}"

# Update README with correct installation instructions
echo -e "${YELLOW}Updating README with installation instructions...${NC}"

# Create a simple installation guide
cat > ./releases/INSTALL.md << 'EOF'
# UPID CLI Installation

## Quick Install

### Linux/macOS
```bash
# Download and install
curl -LO https://github.com/vellankikoti/upid-cli/releases/latest/download/upid-linux.tar.gz
tar -xzf upid-linux.tar.gz
sudo mv upid /usr/local/bin/
chmod +x /usr/local/bin/upid

# Or use the installer
curl -sSL https://raw.githubusercontent.com/vellankikoti/upid-cli/main/install.sh | bash
```

### Windows
```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/vellankikoti/upid-cli/releases/latest/download/upid-windows.zip" -OutFile "upid-windows.zip"
Expand-Archive -Path "upid-windows.zip" -DestinationPath "."
# Add to PATH manually
```

## Test Installation
```bash
upid --help
upid status
upid demo
```

## Platform-Specific Downloads

- **Linux x86_64**: [upid-linux-x86_64.tar.gz](https://github.com/vellankikoti/upid-cli/releases/latest/download/upid-linux-x86_64.tar.gz)
- **Linux ARM64**: [upid-linux-arm64.tar.gz](https://github.com/vellankikoti/upid-cli/releases/latest/download/upid-linux-arm64.tar.gz)
- **macOS ARM64**: [upid-darwin-arm64.tar.gz](https://github.com/vellankikoti/upid-cli/releases/latest/download/upid-darwin-arm64.tar.gz)
- **Windows x86_64**: [upid-windows-x86_64.zip](https://github.com/vellankikoti/upid-cli/releases/latest/download/upid-windows-x86_64.zip)
EOF

echo -e "${GREEN}✅ Created INSTALL.md${NC}"

# Show what was created
echo -e "\n${BLUE}📦 Release Files Created:${NC}"
echo "=========================="
ls -la ./releases/

echo -e "\n${GREEN}🎉 Release preparation complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Create GitHub release with these files"
echo "2. Upload the files to the release"
echo "3. Update install.sh with the correct URLs"
echo "4. Test the installation process" 