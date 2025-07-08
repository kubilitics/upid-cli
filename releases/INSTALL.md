# UPID CLI Installation

## Quick Install

### Linux/macOS
```bash
# Download and install
curl -LO https://github.com/kubilitics/upid-cli/releases/latest/download/upid-linux.tar.gz
tar -xzf upid-linux.tar.gz
sudo mv upid /usr/local/bin/
chmod +x /usr/local/bin/upid

# Or use the installer
curl -sSL https://raw.githubusercontent.com/vellankikoti/upid-cli/main/install.sh | bash
```

### Windows
```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/kubilitics/upid-cli/releases/latest/download/upid-windows.zip" -OutFile "upid-windows.zip"
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

- **Linux x86_64**: [upid-linux-x86_64.tar.gz](https://github.com/kubilitics/upid-cli/releases/latest/download/upid-linux-x86_64.tar.gz)
- **Linux ARM64**: [upid-linux-arm64.tar.gz](https://github.com/kubilitics/upid-cli/releases/latest/download/upid-linux-arm64.tar.gz)
- **macOS ARM64**: [upid-darwin-arm64.tar.gz](https://github.com/kubilitics/upid-cli/releases/latest/download/upid-darwin-arm64.tar.gz)
- **Windows x86_64**: [upid-windows-x86_64.zip](https://github.com/kubilitics/upid-cli/releases/latest/download/upid-windows-x86_64.zip)
