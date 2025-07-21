# UPID CLI Installation Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Docker Installation](#docker-installation)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Post-Installation Setup](#post-installation-setup)
7. [Verification](#verification)

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (x86_64, ARM64), macOS (x86_64, ARM64), Windows 10/11
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for cloud integrations

### Recommended Requirements
- **CPU**: 4+ cores
- **Memory**: 8GB RAM
- **Storage**: 10GB free space (SSD recommended)
- **Network**: Stable internet connection

## Installation Methods

### Method 1: Pre-built Binaries (Recommended)

#### Linux (x86_64)
```bash
# Download binary
wget https://github.com/your-org/upid-cli/releases/latest/download/upid-linux-x86_64

# Make executable
chmod +x upid-linux-x86_64

# Move to system path
sudo mv upid-linux-x86_64 /usr/local/bin/upid

# Verify installation
upid --version
```

#### Linux (ARM64)
```bash
# Download binary
wget https://github.com/your-org/upid-cli/releases/latest/download/upid-linux-arm64

# Make executable
chmod +x upid-linux-arm64

# Move to system path
sudo mv upid-linux-arm64 /usr/local/bin/upid

# Verify installation
upid --version
```

#### macOS (Intel)
```bash
# Download binary
curl -L -o upid-darwin-x86_64 https://github.com/your-org/upid-cli/releases/latest/download/upid-darwin-x86_64

# Make executable
chmod +x upid-darwin-x86_64

# Move to system path
sudo mv upid-darwin-x86_64 /usr/local/bin/upid

# Verify installation
upid --version
```

#### macOS (Apple Silicon)
```bash
# Download binary
curl -L -o upid-darwin-arm64 https://github.com/your-org/upid-cli/releases/latest/download/upid-darwin-arm64

# Make executable
chmod +x upid-darwin-arm64

# Move to system path
sudo mv upid-darwin-arm64 /usr/local/bin/upid

# Verify installation
upid --version
```

#### Windows
```powershell
# Download binary
Invoke-WebRequest -Uri "https://github.com/your-org/upid-cli/releases/latest/download/upid-windows-x86_64.exe" -OutFile "upid.exe"

# Add to PATH (run as Administrator)
# Copy upid.exe to C:\Windows\System32\ or add directory to PATH

# Verify installation
upid --version
```

### Method 2: Python Package Installation

#### Prerequisites
```bash
# Install Python 3.9+
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip

# CentOS/RHEL
sudo yum install python3.9 python3.9-pip

# macOS
brew install python@3.9

# Windows
# Download from python.org
```

#### Installation
```bash
# Create virtual environment
python3.9 -m venv upid-env
source upid-env/bin/activate  # On Windows: upid-env\Scripts\activate

# Install UPID CLI
pip install upid-cli

# Verify installation
upid --version
```

### Method 3: Source Installation

#### Clone Repository
```bash
# Clone the repository
git clone https://github.com/your-org/upid-cli.git
cd upid-cli

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
upid --version
```

## Platform-Specific Instructions

### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3-pip curl wget

# Install UPID CLI
curl -L https://github.com/your-org/upid-cli/releases/latest/download/install.sh | bash
```

### CentOS/RHEL
```bash
# Install system dependencies
sudo yum install -y python3.9 python3.9-pip curl wget

# Install UPID CLI
curl -L https://github.com/your-org/upid-cli/releases/latest/download/install.sh | bash
```

### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.9 curl wget

# Install UPID CLI
curl -L https://github.com/your-org/upid-cli/releases/latest/download/install.sh | bash
```

### Windows
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python3 curl wget

# Install UPID CLI
Invoke-Expression (Invoke-WebRequest -Uri "https://github.com/your-org/upid-cli/releases/latest/download/install.ps1").Content
```

## Docker Installation

### Using Docker Image
```bash
# Pull the image
docker pull upid/upid-cli:latest

# Run UPID CLI
docker run -it --rm \
  -v ~/.kube:/root/.kube \
  -v ~/.upid:/root/.upid \
  upid/upid-cli:latest upid analyze cluster
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  upid-cli:
    image: upid/upid-cli:latest
    volumes:
      - ~/.kube:/root/.kube
      - ~/.upid:/root/.upid
    environment:
      - UPID_JWT_SECRET=your-secret-key
    ports:
      - "8080:8080"
    command: ["upid", "api", "start", "--port", "8080"]
```

```bash
# Start with Docker Compose
docker-compose up -d
```

## Kubernetes Deployment

### Helm Chart Installation
```bash
# Add Helm repository
helm repo add upid https://charts.upid.io
helm repo update

# Install UPID CLI
helm install upid-cli upid/upid-cli \
  --namespace upid-system \
  --create-namespace \
  --set auth.jwtSecret=your-secret-key \
  --set storage.persistence.enabled=true
```

### Manual Kubernetes Deployment
```yaml
# upid-cli-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: upid-cli
  namespace: upid-system
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
      containers:
      - name: upid-cli
        image: upid/upid-cli:latest
        ports:
        - containerPort: 8080
        env:
        - name: UPID_JWT_SECRET
          value: "your-secret-key"
        volumeMounts:
        - name: upid-data
          mountPath: /root/.upid
      volumes:
      - name: upid-data
        persistentVolumeClaim:
          claimName: upid-data-pvc
```

```bash
# Apply deployment
kubectl apply -f upid-cli-deployment.yaml
```

## Post-Installation Setup

### 1. Initialize Configuration
```bash
# Create configuration directory
mkdir -p ~/.upid

# Initialize configuration
upid init
```

### 2. Configure Authentication
```bash
# Set up default authentication
upid auth configure

# Or configure enterprise authentication
upid auth configure --provider oidc --provider-url https://your-oidc-provider.com
```

### 3. Configure Cloud Integration
```bash
# AWS
upid cloud aws configure --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY

# GCP
upid cloud gcp configure --project-id YOUR_PROJECT_ID --key-file key.json

# Azure
upid cloud azure configure --subscription-id YOUR_SUBSCRIPTION_ID --tenant-id YOUR_TENANT_ID
```

### 4. Set Up Monitoring
```bash
# Configure Prometheus integration
upid monitoring configure --prometheus-url http://prometheus:9090

# Configure alerting
upid monitoring configure-alerts --webhook-url https://your-webhook-url.com
```

## Verification

### 1. Check Installation
```bash
# Verify UPID CLI is installed
upid --version

# Check help
upid --help
```

### 2. Test Authentication
```bash
# Test login
upid auth login

# Check status
upid auth status
```

### 3. Test Cluster Connection
```bash
# Test kubectl connection
kubectl cluster-info

# Test UPID CLI connection
upid test connection
```

### 4. Run Basic Analysis
```bash
# Quick cluster analysis
upid analyze cluster

# Check dashboard
upid dashboard
```

### 5. Verify API
```bash
# Start API server
upid api start --port 8080

# Test API endpoint
curl http://localhost:8080/api/v1/health
```

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Fix binary permissions
chmod +x /usr/local/bin/upid

# Check PATH
echo $PATH
which upid
```

#### Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Kubernetes Connection
```bash
# Check kubectl configuration
kubectl config view

# Test cluster access
kubectl get nodes
```

#### Database Issues
```bash
# Reset database
rm ~/.upid/upid_data.db
upid init
```

### Support
```bash
# Generate support bundle
upid support bundle --output support-bundle.tar.gz

# Check system health
upid support health-check

# View logs
upid logs --level debug
```

## Next Steps

1. **Read the User Manual**: `docs/guides/UPID_USER_MANUAL.md`
2. **Check Quick Reference**: `docs/guides/UPID_QUICK_REFERENCE.md`
3. **Configure your environment** for production use
4. **Set up monitoring and alerting**
5. **Train your team** on UPID CLI usage

---

**UPID CLI v2.0** - Production Ready Kubernetes Intelligence Platform 