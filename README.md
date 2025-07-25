# UPID CLI - Universal Pod Intelligence Director

<div align="center">

![UPID Logo](https://img.shields.io/badge/UPID-CLI-blue?style=for-the-badge&logo=kubernetes)

**🚧 DEVELOPMENT VERSION - NOT FOR PRODUCTION USE 🚧**

[![Version](https://img.shields.io/badge/version-2.0.0--dev-orange.svg)](https://github.com/your-org/upid-cli/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/your-org/upid-cli/releases)

🔬 **Enterprise Kubernetes Cost Optimization Platform - In Development**

[Installation](#installation) • [Features](#features) • [Development](#development) • [Contributing](#contributing)

</div>

---

## 🚨 **IMPORTANT NOTICE**

**This is a development version and is NOT ready for production use.** 

**Current Status:**
- ✅ CLI interface and Go binaries are functional
- ✅ Database schema and architecture complete  
- ✅ All 7 development phases implemented
- ⚠️ Python dependencies need proper packaging
- ⚠️ API server needs deployment configuration
- ⚠️ Authentication system needs production setup

**For Developers & Contributors Only** - Please see [Development](#development) section below.

---

## 🎯 **Vision: The $1B+ "Health Check Illusion" Solution**

### The Problem We're Solving

Most Kubernetes cost optimization tools suffer from the **Health Check Illusion** - they see constant traffic from health checks and assume workloads are active, missing **60-80% of potential cost savings**.

UPID CLI will solve this with **5-layer intelligent filtering**:
- 🔍 **Health Check Detection**: Filters kube-probe, load balancer health checks
- 📊 **Real Traffic Analysis**: Identifies genuine business requests
- 🤖 **ML-Powered Intelligence**: Predicts actual resource needs
- ⚡ **Zero-Pod Scaling**: Safe automation with rollback guarantees
- 💰 **Executive Insights**: ROI calculations and cost optimization

## ✨ **Planned Features (In Development)**

### 🎯 **Core Capabilities**
- **Real Pod Idle Detection**: Accurate identification beyond health check noise
- **Zero-Pod Scaling**: Safe automation with instant rollback guarantees
- **Universal Compatibility**: "If kubectl works, UPID works" - any K8s distribution
- **60-80% Cost Savings**: On truly idle workloads with proven results

### 🏢 **Enterprise Ready**
- **8 Authentication Providers**: OIDC, SAML, LDAP, AWS IAM, Azure AD, Google IAM
- **Executive Dashboards**: ROI metrics, cost analysis, business intelligence
- **Multi-Cloud Support**: AWS, Azure, GCP cost optimization
- **Audit & Compliance**: Complete logging and security controls

### 🛡️ **Safety First**
- **Read-Only by Default**: Safe analysis without cluster modifications
- **Explicit Confirmation**: All optimizations require user approval
- **Rollback Guaranteed**: All changes can be instantly reverted
- **Risk Assessment**: ML-powered safety scoring for every optimization

## 🛠️ **Development**

### **Prerequisites for Developers**
- Python 3.9+
- Go 1.19+
- kubectl configured
- Access to Kubernetes cluster

### **Setup Development Environment**
```bash
# Clone repository
git clone https://github.com/your-org/upid-cli.git
cd upid-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### **Build Development Binary**
```bash
# Build Go binary for current platform
./build_go_binary.sh

# Test the built binary
./dist/upid-darwin-arm64 --help
```

### **Run Development Tests**
```bash
# Run unit tests
make test-unit

# Run integration tests  
make test-integration

# Run all tests
make test-all
```

## 📋 **Architecture Status**

### ✅ **Completed Components**

#### 1. CLI Interface (Go) - **95% Complete**
- **Location**: `cmd/upid/`, `internal/commands/`
- **Status**: Professional Cobra-based CLI with comprehensive command structure
- **Functionality**: All command hierarchies defined with help text

#### 2. Database System - **90% Complete**
- **Location**: `api_server/database/`
- **Status**: Complete SQLAlchemy models with enterprise schema
- **Functionality**: Users, Clusters, Workloads, OptimizationRuns, etc.

#### 3. Configuration Management - **100% Complete** ✅
- **Location**: `upid_config.py`, `upid_python/core/central_config.py`
- **Status**: Centralized configuration system
- **Functionality**: Single source of truth for all product metadata

#### 4. Build System - **85% Complete**
- **Location**: `build_binary.py`, `build_go_binary.sh`
- **Status**: Multi-platform binary builds working
- **Functionality**: Cross-platform Go and Python binary generation

### 🔶 **In Progress Components**

#### 5. Python Backend Integration - **60% Complete**
- **Location**: `upid_python/core/`, `upid_python/ml/`
- **Status**: Complete code structure, needs dependency management
- **Required**: Proper Python packaging and deployment

#### 6. API Server - **70% Complete**
- **Location**: `api_server/`
- **Status**: FastAPI application with all endpoints
- **Required**: Production deployment configuration

#### 7. Authentication System - **75% Complete**
- **Location**: `upid_python/core/auth.py`
- **Status**: Well-designed auth system
- **Required**: Provider integrations and production setup

### 🔴 **Not Ready for Production**

#### 8. Dependency Management - **30% Complete**
- **Status**: Requirements defined but not packaged
- **Required**: Docker containers or embedded Python runtime

#### 9. Production Deployment - **20% Complete**
- **Status**: Development scripts only
- **Required**: Production-ready deployment configurations

#### 10. End-to-End Integration - **40% Complete**
- **Status**: Components exist but integration needs testing
- **Required**: Full integration testing and validation

## 🧪 **Development Testing**

### **Available Make Commands**
```bash
# Installation
make install          # Install production dependencies
make install-dev      # Install development dependencies

# Testing
make test             # Run all tests
make test-unit        # Run unit tests only
make test-integration # Run integration tests only

# Binary Building
make binary           # Build and install binary
make build-binary     # Build binary for current platform

# Code Quality
make lint             # Run code linting
make type-check       # Run type checking
make security         # Run security checks

# Utilities
make clean            # Clean build artifacts
make help             # Show all available commands
```

### **Current Test Status**
- **Unit Tests**: Comprehensive test suite structure in place
- **Integration Tests**: Framework ready, needs real cluster testing
- **Security Tests**: Security scanning and validation tools configured
- **Performance Tests**: Load testing framework ready

## 📚 **Documentation (In Development)**

### **Available Documentation**
- **[Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)**: Complete development plan
- **[API Reference](docs/architecture/api-refernce.md)**: REST API documentation  
- **[Architecture Guide](docs/architecture/upid_architecture_complete.md)**: System architecture
- **[User Manual](docs/guides/UPID_USER_MANUAL.md)**: User guide (draft)
- **[Installation Guide](docs/guides/UPID_INSTALLATION_GUIDE.md)**: Installation instructions

### **Documentation TODO**
- [ ] Complete API reference with examples
- [ ] Finalize user manual with real examples
- [ ] Create troubleshooting guide
- [ ] Add security configuration guide
- [ ] Write deployment guide

## 🤝 **Contributing**

We welcome contributions! This is an active development project.

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`make install-dev`)
4. Make your changes
5. Run tests (`make test`)
6. Run code quality checks (`make lint type-check`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### **Contribution Areas**
- **Backend Integration**: Help complete Python-Go integration
- **Authentication**: Implement production-ready auth providers
- **Testing**: Add integration tests and real cluster testing
- **Documentation**: Improve user guides and API documentation
- **Deployment**: Create production deployment configurations
- **Security**: Enhance security features and compliance

## 📊 **Current Development Status**

### **Overall Progress: 70% Complete**

| Component | Status | Priority |
|-----------|--------|----------|
| CLI Interface | ✅ 95% | High |
| Configuration System | ✅ 100% | High |
| Database Schema | ✅ 90% | High |
| Build System | ✅ 85% | High |
| Python Backend | 🔶 60% | Critical |
| API Server | 🔶 70% | Critical |
| Authentication | 🔶 75% | High |
| Dependency Management | 🔴 30% | Critical |
| Production Deployment | 🔴 20% | Critical |
| End-to-End Testing | 🔴 40% | High |

### **Next Milestones**
1. **Complete Python Integration** (2-3 weeks)
2. **Production Deployment Configuration** (1-2 weeks)
3. **End-to-End Integration Testing** (1 week)
4. **Security Hardening** (1 week)
5. **Production Release** (Target: 4-6 weeks)

## 🎯 **When Will This Be Production Ready?**

**Estimated Timeline: 4-6 weeks** for production release, pending:

### **Critical Path Items**
1. **Python Dependency Management**: Package Python runtime with binaries
2. **Production Configuration**: Create deployment-ready configurations
3. **Integration Testing**: Test all components working together
4. **Security Hardening**: Production security configurations
5. **Documentation**: Complete user guides and examples

### **Success Criteria for Production Release**
- [ ] All CLI commands work without external dependencies
- [ ] Authentication system fully functional
- [ ] API server starts and responds correctly
- [ ] Database operations work seamlessly
- [ ] End-to-end workflows tested and verified
- [ ] Professional installation experience
- [ ] Complete documentation with examples
- [ ] Security audit passed

## 🆘 **Getting Help**

### **For Developers**
- **Issues**: [GitHub Issues](https://github.com/your-org/upid-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/upid-cli/discussions)
- **Email**: dev@upid.io

### **For Future Users**
- **Documentation**: [docs.upid.io](https://docs.upid.io) (coming soon)
- **Community**: [Slack](https://slack.upid.io) (coming soon)
- **Support**: support@upid.io

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 **Vision Statement**

UPID CLI will be the **industry-leading Kubernetes cost optimization platform** that solves the Health Check Illusion problem and delivers 60-80% cost savings with enterprise-grade security and safety guarantees.

**When complete, UPID CLI will provide:**
- Unmatched accuracy in idle workload detection
- Enterprise-grade security and compliance features  
- Professional installation and user experience
- Comprehensive business intelligence and ROI analysis
- Multi-cloud cost optimization and billing integration
- Safety-first approach with guaranteed rollback capabilities

**Thank you for your interest in UPID CLI development!** 

*This project represents the future of intelligent Kubernetes cost optimization.*

---

**🔬 Development Version 2.0.0-dev** - Not for production use