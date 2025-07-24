# 🚀 UPID CLI Installation Guide

## Quick Installation (Recommended)

### One-Line Install Script
```bash
curl -fsSL https://get.upid.io/install.sh | sh
```

### Manual Installation

#### 1. Download Binary
Choose your platform and download the latest release:

```bash
# macOS (Apple Silicon)
curl -L https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-macos-arm64 -o upid

# macOS (Intel)
curl -L https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-macos-amd64 -o upid

# Linux (x86_64)
curl -L https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-linux-amd64 -o upid

# Linux (ARM64)
curl -L https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-linux-arm64 -o upid
```

#### 2. Make Executable
```bash
chmod +x upid
```

#### 3. Install System-Wide
```bash
# Install to /usr/local/bin (requires sudo)
sudo mv upid /usr/local/bin/

# Or install to user bin (no sudo required)
mkdir -p ~/.local/bin
mv upid ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"  # Add to your shell profile
```

#### 4. Verify Installation
```bash
upid --version
upid --help
```

## Platform-Specific Instructions

### macOS

#### Homebrew (Coming Soon)
```bash
brew install upid-cli
```

#### Manual Installation
```bash
# Download and install
curl -L https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-macos-$(uname -m | sed 's/x86_64/amd64/') -o /usr/local/bin/upid
chmod +x /usr/local/bin/upid

# Verify
upid --version
```

### Linux

#### Package Managers (Coming Soon)
```bash
# Ubuntu/Debian
apt install upid-cli

# CentOS/RHEL/Fedora
yum install upid-cli
```

#### Manual Installation
```bash
# Auto-detect architecture and install
ARCH=$(uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')
curl -L "https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-linux-${ARCH}" -o /usr/local/bin/upid
chmod +x /usr/local/bin/upid

# Verify
upid --version
```

### Windows

#### PowerShell Installation
```powershell
# Download
Invoke-WebRequest -Uri "https://github.com/your-org/upid-cli/releases/latest/download/upid-1.0.0-windows-amd64.exe" -OutFile "upid.exe"

# Move to PATH
Move-Item upid.exe "$env:USERPROFILE\bin\upid.exe"

# Add to PATH (if needed)
$env:PATH += ";$env:USERPROFILE\bin"
```

## Docker Installation

### Run in Container
```bash
docker run --rm -it \\
  -v $HOME/.kube:/root/.kube \\
  upid/cli:latest upid --help
```

### Create Alias
```bash
# Add to your shell profile
alias upid='docker run --rm -it -v $HOME/.kube:/root/.kube upid/cli:latest upid'
```

## Kubernetes Integration

### In-Cluster Installation
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: upid-cli
spec:
  replicas: 1
  selector:
    matchLabels:
      app: upid-cli
  template:
    metadata:
      labels:
        app: upid-cli
    spec:
      serviceAccountName: upid-service-account
      containers:
      - name: upid
        image: upid/cli:latest
        command: ["upid", "api", "start"]
        ports:
        - containerPort: 8080
```

## Prerequisites

### Required
- **kubectl**: Kubernetes command-line tool
  ```bash
  # Install kubectl
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/$(uname -s | tr '[:upper:]' '[:lower:]')/$(uname -m | sed 's/x86_64/amd64/')/kubectl"
  chmod +x kubectl
  sudo mv kubectl /usr/local/bin/
  ```

### Optional
- **Kubernetes cluster access**: For cluster analysis and optimization
- **Cloud CLI tools**: For enhanced cloud cost integration
  - AWS CLI for AWS EKS integration
  - Azure CLI for Azure AKS integration  
  - Google Cloud CLI for GKE integration

## Verification

### Check Installation
```bash
# Verify UPID is installed
upid --version
# Expected: UPID CLI v1.0.0

# Check system prerequisites
upid --check-prereqs
# Expected: ✅ All prerequisites met

# Test basic functionality
upid status
# Expected: UPID system status report
```

### First Run
```bash
# Analyze your cluster (safe, read-only)
upid analyze cluster

# Find idle workloads
upid analyze idle

# Generate executive report
upid report executive
```

## Shell Completion

### Bash
```bash
upid completion bash > /etc/bash_completion.d/upid
```

### Zsh
```bash
upid completion zsh > "${fpath[1]}/_upid"
```

### Fish
```bash
upid completion fish > ~/.config/fish/completions/upid.fish
```

## Updating UPID

### Automatic Update (Coming Soon)
```bash
upid update
```

### Manual Update
```bash
# Re-run installation script
curl -fsSL https://get.upid.io/install.sh | sh

# Or download latest manually
curl -L https://github.com/your-org/upid-cli/releases/latest/download/upid-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m | sed 's/x86_64/amd64/') -o /usr/local/bin/upid
chmod +x /usr/local/bin/upid
```

## Uninstallation

```bash
# Remove binary
sudo rm /usr/local/bin/upid

# Remove configuration (optional)
rm -rf ~/.upid/

# Remove shell completions
rm /etc/bash_completion.d/upid        # Bash
rm "${fpath[1]}/_upid"                # Zsh  
rm ~/.config/fish/completions/upid.fish  # Fish
```

## Troubleshooting

### Common Issues

#### "upid: command not found"
- Verify `/usr/local/bin` is in your PATH: `echo $PATH`
- Add to PATH: `export PATH="/usr/local/bin:$PATH"`
- Add to shell profile: `echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc`

#### "Permission denied"
- Make executable: `chmod +x /usr/local/bin/upid`
- Check ownership: `ls -la /usr/local/bin/upid`

#### "kubectl not found"
- Install kubectl first (see Prerequisites section)
- Verify: `kubectl version --client`

#### Kubernetes connection issues
- Check cluster access: `kubectl cluster-info`
- Verify context: `kubectl config current-context`
- Check permissions: `kubectl auth can-i get pods`

### Getting Help
- **Documentation**: `upid --help`
- **System check**: `upid --check-prereqs`
- **GitHub Issues**: https://github.com/your-org/upid-cli/issues
- **Support**: support@upid.io

---

## 🎉 Success!

Once installed, UPID CLI works exactly like kubectl:

```bash
# Just like kubectl, upid is now available globally
upid --version
upid analyze cluster
upid optimize zero-pod --dry-run
upid report executive

# And follows the same conventions
upid --help
upid <command> --help
upid <command> <subcommand> --help
```

**You're ready to optimize your Kubernetes costs!** 🚀