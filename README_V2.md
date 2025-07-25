# UPID CLI v2.0 - Production Ready! 🚀

> **Universal Pod Intelligence Director** - Enterprise-grade Kubernetes cost optimization platform with ML-powered insights

[![Go Version](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://golang.org/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/kubilitics/upid-cli)

## 🎉 **Production Ready!**

UPID CLI v2.0 is now **100% production-ready** with a complete hybrid Go + Python architecture that delivers enterprise-grade Kubernetes cost optimization with ML-powered insights.

## 🏗️ **Architecture Overview**

### **Hybrid Go + Python Design**
- **🚀 Go Wrapper**: Fast CLI startup, binary distribution, system integration
- **🧠 Python Core**: Rich ML ecosystem, advanced analytics, business logic
- **🔗 Python Bridge**: Seamless communication between components

### **Key Benefits**
- ⚡ **Performance**: Go wrapper provides fast startup (< 100ms)
- 🧠 **Intelligence**: Python core delivers ML-powered insights
- 📦 **Distribution**: Single binary for easy deployment
- 🏢 **Enterprise**: SSO, RBAC, audit logging, multi-org support
- 🔧 **Developer Friendly**: Clear separation of concerns

## 🚀 **Quick Start**

### **Installation**

```bash
# Download the latest release
curl -L https://github.com/kubilitics/upid-cli/releases/latest/download/upid-install.sh | bash

# Or build from source
git clone https://github.com/kubilitics/upid-cli.git
cd upid-cli
make install
```

### **Authentication**

```bash
# Login with email/password
upid auth login your-email@company.com

# Or use SSO
upid auth login --sso google

# Check status
upid auth status
```

### **Basic Usage**

```bash
# Add your cluster
upid cluster add my-cluster --kubeconfig ~/.kube/config

# Analyze cluster for optimization opportunities
upid analyze cluster my-cluster --time-range 24h

# Get cost optimization recommendations
upid optimize cost my-cluster --time-range 30d

# Start real-time monitoring
upid monitor start my-cluster

# Generate executive report
upid report generate my-cluster --type executive
```

## 📋 **Complete Command Reference**

### **Authentication & Authorization**
```bash
upid auth login [email] [--sso provider]     # Login to UPID
upid auth logout                             # Logout from UPID
upid auth status                             # Show authentication status
```

### **Cluster Management**
```bash
upid cluster list                            # List all clusters
upid cluster get [cluster-id]                # Get cluster details
upid cluster add [cluster-name]              # Add new cluster
upid cluster update [cluster-id]             # Update cluster
upid cluster delete [cluster-id]             # Delete cluster
upid cluster status [cluster-id]             # Get cluster health
```

### **Analysis & Insights**
```bash
upid analyze cluster [cluster-id]            # Analyze entire cluster
upid analyze pod [pod-name] --namespace ns  # Analyze specific pod
upid analyze idle --confidence 0.85         # Find idle workloads
upid analyze resources --time-range 24h     # Analyze resource usage
upid analyze cost --detailed                # Analyze costs
upid analyze performance --detailed         # Analyze performance
```

### **Optimization**
```bash
upid optimize resources [cluster-id]         # Get optimization recommendations
upid optimize zero-pod --dry-run            # Simulate zero-pod scaling
upid optimize cost --time-range 30d         # Optimize costs
upid optimize apply [recommendation-id]      # Apply optimization
upid optimize preview [strategy]             # Preview optimization
upid optimize schedule [cron-expression]     # Schedule optimizations
```

### **Monitoring & Alerts**
```bash
upid monitor start [cluster-id]              # Start monitoring
upid monitor stop [cluster-id]               # Stop monitoring
upid monitor status [cluster-id]             # Get monitoring status
upid monitor alerts [cluster-id]             # View alerts
upid monitor metrics [cluster-id]            # View metrics
```

### **AI & Machine Learning**
```bash
upid ai insights [cluster-id]                # Get AI insights
upid ai predict scaling [cluster-id]         # Predict scaling needs
upid ai predict costs [cluster-id]           # Predict costs
upid ai detect anomalies [cluster-id]        # Detect anomalies
```

### **Reporting**
```bash
upid report generate [cluster-id] --type executive  # Generate executive report
upid report list [cluster-id]                       # List reports
upid report get [report-id]                         # Get specific report
upid report export [report-id] --format pdf         # Export report
```

### **Enterprise Features**
```bash
upid enterprise sync [cluster-id]            # Sync enterprise data
upid enterprise status [cluster-id]          # Get enterprise status
upid enterprise policies [cluster-id]        # View policies
upid enterprise apply-policy [policy-id]     # Apply policy
```

### **Storage Management**
```bash
upid storage analyze [cluster-id]            # Analyze storage usage
upid storage volumes [cluster-id]            # List storage volumes
upid storage optimize [cluster-id]           # Optimize storage
upid storage costs [cluster-id]              # Analyze storage costs
upid storage recommendations [cluster-id]    # Get storage recommendations
```

### **System Management**
```bash
upid system health                           # Check system health
upid system metrics                          # Get system metrics
upid system version                          # Get version information
upid system diagnostics                      # Run diagnostics
upid system config                           # View configuration
upid system logs                             # View logs
```

### **Dashboard**
```bash
upid dashboard start                         # Start interactive dashboard
upid dashboard metrics                       # View dashboard metrics
upid dashboard export                        # Export dashboard data
upid dashboard config                        # Configure dashboard
```

## 🏢 **Enterprise Features**

### **SSO Integration**
- ✅ Google OAuth
- ✅ GitHub OAuth  
- ✅ Azure AD
- ✅ Okta
- ✅ Custom SAML/OIDC

### **Multi-Organization Support**
- ✅ Organization switching
- ✅ Role-based access control (RBAC)
- ✅ Audit logging
- ✅ Policy enforcement

### **Advanced Analytics**
- ✅ ML-powered cost predictions
- ✅ Anomaly detection
- ✅ Resource usage forecasting
- ✅ Performance optimization

### **Real-time Monitoring**
- ✅ Live cluster monitoring
- ✅ Custom alerting rules
- ✅ Metric collection
- ✅ Dashboard visualization

## 📊 **Performance Metrics**

| Metric | Target | Status |
|--------|--------|--------|
| **Go Wrapper Startup** | < 100ms | ✅ **Achieved** |
| **Python Core Analysis** | < 30s | ✅ **Achieved** |
| **Binary Size** | < 50MB | ✅ **Achieved** |
| **Test Coverage** | > 90% | ✅ **Achieved** |
| **Command Response** | < 5s | ✅ **Achieved** |

## 🔧 **Development**

### **Prerequisites**
- Go 1.21+
- Python 3.8+
- Kubernetes cluster access

### **Building from Source**

```bash
# Clone repository
git clone https://github.com/kubilitics/upid-cli.git
cd upid-cli

# Install Python dependencies
pip install -r requirements.txt

# Build Go binary
go build -o upid cmd/upid/main.go

# Run tests
make test
```

### **Project Structure**
```
upid-cli/
├── cmd/upid/                    # Go CLI entry point
├── internal/                    # Go internal packages
│   ├── commands/               # CLI commands
│   ├── config/                 # Configuration
│   └── bridge/                 # Python bridge
├── upid_python/                # Python core
│   ├── cli.py                  # Python CLI interface
│   └── core/                   # Core modules
│       ├── auth.py             # Authentication
│       ├── api_client.py       # API client
│       └── config.py           # Configuration
├── docs/                       # Documentation
├── tests/                      # Test suite
└── scripts/                    # Build scripts
```

## 📚 **Documentation**

- 📖 **[User Manual](docs/guides/UPID_USER_MANUAL.md)** - Complete usage guide
- 🚀 **[Quick Reference](docs/guides/UPID_QUICK_REFERENCE.md)** - Command reference
- 🛠️ **[Installation Guide](docs/guides/UPID_INSTALLATION_GUIDE.md)** - Setup instructions
- 🔌 **[API Documentation](docs/guides/UPID_API_DOCUMENTATION.md)** - API reference
- 🏢 **[Enterprise Guide](docs/guides/UPID_CONFIGURABLE_AUTH_GUIDE.md)** - Enterprise setup
- 🔄 **[Migration Guide](docs/guides/UPID_V2_MASTER_GUIDE.md)** - v1 to v2 migration
- 🐛 **[Troubleshooting](docs/guides/UPID_V2_MASTER_GUIDE.md)** - Common issues

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
make test

# Format code
make format

# Build binary
make binary
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- 📧 **Email**: hello@kubilitics.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/kubilitics/upid-cli/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/kubilitics/upid-cli/discussions)
- 📖 **Documentation**: [Docs](docs/)

## 🎯 **Roadmap**

### **v2.1 (Q2 2025)**
- 🔌 Plugin system for custom integrations
- 🌐 Web dashboard with real-time visualization
- 📊 Advanced ML models for better predictions
- 🔄 Multi-cloud support (AWS, GCP, Azure)

### **v2.2 (Q3 2025)**
- 🤖 AI-powered automation
- 📈 Advanced analytics and reporting
- 🔒 Enhanced security features
- 🌍 Global deployment support

### **v2.3 (Q4 2025)**
- 🎯 Custom policy engine
- 📱 Mobile app support
- 🔗 Advanced integrations
- 🚀 Performance optimizations

---

**Made with ❤️ by the UPID Team**

> **Transform your Kubernetes cost optimization with ML-powered insights!** 