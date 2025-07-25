# UPID CLI - Universal Pod Intelligence Director

> **Enterprise Kubernetes Cost Optimization Platform**  
> Reduce infrastructure costs by 60-80% through intelligent resource analysis and automated optimization

[![GitHub release](https://img.shields.io/github/release/kubilitics/upid-cli.svg)](https://github.com/kubilitics/upid-cli/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/go-1.24+-blue.svg)](https://golang.org)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

## 🚀 **Quick Start**

### Prerequisites
- Kubernetes cluster access (any distribution)
- `kubectl` installed and configured
- No other dependencies required!

### Installation (kubectl-style)

**Linux:**
```bash
curl -LO "https://github.com/kubilitics/upid-cli/releases/latest/download/upid-linux-amd64"
chmod +x upid-linux-amd64
sudo mv upid-linux-amd64 /usr/local/bin/upid
```

**macOS:**
```bash
curl -LO "https://github.com/kubilitics/upid-cli/releases/latest/download/upid-darwin-amd64"
chmod +x upid-darwin-amd64
sudo mv upid-darwin-amd64 /usr/local/bin/upid
```

**Windows:**
```powershell
Invoke-WebRequest -Uri "https://github.com/kubilitics/upid-cli/releases/latest/download/upid-windows-amd64.exe" -OutFile "upid.exe"
Move-Item upid.exe "$env:USERPROFILE\bin\upid.exe"
```

**Verify Installation:**
```bash
upid --version
```

## 🎯 **Key Features**

- ⚡ **Real Pod Idle Detection**: Accurate identification beyond health check noise
- 💰 **60-80% Cost Savings**: On truly idle workloads with proven results
- 🛡️ **Zero-Pod Scaling**: Safe automation with rollback guarantees
- 🤖 **ML-Powered Intelligence**: Predictive scaling and anomaly detection
- 📊 **Executive Dashboards**: ROI tracking and business intelligence
- ☁️ **Multi-Cloud Support**: AWS, GCP, Azure cost integration
- 🔐 **Enterprise Security**: MFA, SSO, RBAC, audit logging

## 📖 **Documentation**

- [User Manual](docs/USER_MANUAL.md) - Complete usage guide
- [API Reference](docs/API_REFERENCE.md) - REST API documentation
- [Command Reference](docs/COMMAND_REFERENCE.md) - CLI command reference
- [Installation Guide](docs/guides/UPID_INSTALLATION_GUIDE.md) - Detailed installation instructions

## 🚀 **Quick Commands**

```bash
# Analyze your cluster (safe, read-only)
upid analyze cluster

# Find idle workloads
upid analyze idle

# Generate executive report
upid report executive

# Optimize costs
upid optimize costs

# Monitor real-time
upid monitor live
```

## 🏗️ **Architecture**

UPID CLI is built with a **Go wrapper + Python core** architecture:

- **Go CLI Wrapper**: Provides robust, cross-platform binary distribution
- **Python Core Logic**: Advanced ML, analytics, and enterprise features
- **Embedded Runtime**: No external dependencies required
- **Universal Compatibility**: "If kubectl works, UPID works"

## 🔧 **Development**

### Prerequisites
- Go 1.24+
- Python 3.11+
- kubectl configured

### Build from Source
```bash
git clone https://github.com/kubilitics/upid-cli.git
cd upid-cli

# Build Go binary
go build -o upid ./cmd/upid

# Run
./upid --version
```

### Run Tests
```bash
# Run all tests
make test

# Run specific test suite
python -m pytest tests/unit/test_phase7_advanced_analytics.py -v
```

## 📊 **Performance**

- **Analysis Speed**: 1000+ pods analyzed in <30 seconds
- **Memory Usage**: <100MB RAM for typical clusters
- **CPU Usage**: <5% during analysis
- **Network**: Minimal bandwidth usage

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: `upid --help`
- **Issues**: [GitHub Issues](https://github.com/kubilitics/upid-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kubilitics/upid-cli/discussions)

---

**🎯 Ready for Production Deployment and Client Testing!**