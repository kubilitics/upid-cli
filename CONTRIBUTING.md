# Contributing to UPID CLI

We welcome contributions to UPID CLI! This document provides guidelines for contributing to the project.

## 🤝 **Ways to Contribute**

- 🐛 **Report Bugs**: Found a bug? Let us know!
- 💡 **Feature Requests**: Have an idea? We'd love to hear it!
- 🔧 **Code Contributions**: Submit PRs for improvements
- 📚 **Documentation**: Help improve our docs
- 🧪 **Testing**: Add tests or improve existing ones

## 🚀 **Getting Started**

### Prerequisites
- Python 3.9+
- kubectl configured with cluster access
- Git

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/your-username/upid-cli.git
cd upid-cli
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements-dev.txt
pip install -e .
```

4. **Verify Installation**
```bash
upid --version
```

## 🧪 **Testing**

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests  
pytest tests/integration/

# All tests
pytest tests/
```

### Manual Testing
```bash
# Build binary for testing
python3 build_binary.py

# Run demonstration suite
./scripts/testing/master_demonstration_suite.sh
```

## 📝 **Development Guidelines**

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

### Commit Messages
- Use conventional commit format
- Be descriptive and concise
- Include context about why the change was made

Example:
```
feat: add support for GKE autopilot clusters

- Add GKE autopilot detection in cluster_detector.py
- Update optimization engine for autopilot constraints
- Add tests for autopilot-specific behavior

Fixes #123
```

### Pull Request Process

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
- Write clean, tested code
- Update documentation if needed
- Add tests for new functionality

3. **Test Your Changes**
```bash
pytest tests/
python3 build_binary.py  # Ensure binary builds
```

4. **Submit Pull Request**
- Use the PR template
- Provide clear description of changes
- Link related issues
- Ensure CI passes

## 🐛 **Bug Reports**

When reporting bugs, please include:

- **Environment**: OS, Python version, kubectl version
- **UPID Version**: Output of `upid --version`
- **Kubernetes Environment**: Distribution, version
- **Steps to Reproduce**: Clear, minimal example
- **Expected vs Actual Behavior**
- **Error Messages**: Full error output
- **Additional Context**: Any relevant logs or screenshots

## 💡 **Feature Requests**

For feature requests, please include:

- **Problem Description**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives Considered**: Other approaches you've thought of
- **Use Case**: Real-world scenario where this would help
- **Additional Context**: Any supporting information

## 🏗️ **Architecture Overview**

UPID CLI uses a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    🎯 UPID Intelligence                  │
├─────────────────────────────────────────────────────────┤
│ Layer 5: Executive Intelligence (ROI, Business Metrics) │
│ Layer 4: Safety & Risk Assessment (ML-Powered)          │
│ Layer 3: Optimization Engine (Zero-Pod Scaling)         │
│ Layer 2: Traffic Pattern Analysis (Real vs Health)      │
│ Layer 1: Universal K8s Compatibility (Any Distribution) │
└─────────────────────────────────────────────────────────┘
```

### Key Components

- **CLI Interface** (`upid/cli.py`): Main entry point
- **Commands** (`upid/commands/`): Command implementations
- **Core Engine** (`upid/core/`): Business logic and algorithms
- **Authentication** (`upid/auth/`): Multi-provider auth system
- **API Layer** (`upid/api/`): REST API endpoints
- **ML Models** (`models/`): Pre-trained optimization models

## 📚 **Documentation**

- Keep README.md up to date
- Update docstrings for new functions
- Add examples for new features
- Update user guides in `docs/guides/`

## 🛡️ **Security**

- Follow security best practices
- Never commit secrets or credentials  
- Sanitize user inputs
- Report security issues privately

## 📄 **License**

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🆘 **Getting Help**

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check `docs/` directory

## 🙏 **Recognition**

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Special thanks in documentation

Thank you for helping make UPID CLI better! 🚀