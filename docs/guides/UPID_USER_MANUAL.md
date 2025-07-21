# UPID CLI User Manual

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Authentication](#authentication)
5. [Core Commands](#core-commands)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

UPID CLI is a comprehensive Kubernetes intelligence and optimization platform that provides real-time analytics, machine learning insights, and automated optimization recommendations for your Kubernetes clusters.

### Key Features
- **Real-time Analytics**: Live monitoring of cluster performance and resource usage
- **Machine Learning**: Predictive analytics for resource planning and cost optimization
- **Business Intelligence**: KPI tracking and ROI analysis
- **Security**: Enterprise-grade authentication with MFA support
- **Multi-cloud Support**: AWS, GCP, and Azure integration

## Installation

### Prerequisites
- Python 3.9 or higher
- kubectl configured and connected to your cluster
- Access to your Kubernetes cluster

### Installation Methods

#### Method 1: Direct Installation
```bash
# Clone the repository
git clone https://github.com/your-org/upid-cli.git
cd upid-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install UPID CLI
pip install -e .
```

#### Method 2: Using Pre-built Binaries
```bash
# Download the appropriate binary for your platform
# Linux
wget https://github.com/your-org/upid-cli/releases/latest/download/upid-linux-x86_64
chmod +x upid-linux-x86_64
sudo mv upid-linux-x86_64 /usr/local/bin/upid

# macOS
wget https://github.com/your-org/upid-cli/releases/latest/download/upid-darwin-arm64
chmod +x upid-darwin-arm64
sudo mv upid-darwin-arm64 /usr/local/bin/upid

# Windows
# Download upid-windows-x86_64.exe and add to PATH
```

## Quick Start

1. **Initialize UPID CLI**
```bash
upid init
```

2. **Authenticate**
```bash
upid auth login
# Enter your credentials when prompted
```

3. **Analyze your cluster**
```bash
upid analyze cluster
```

4. **View executive dashboard**
```bash
upid dashboard
```

## Authentication

UPID CLI supports multiple authentication methods:

### Default Authentication
```bash
upid auth login
# Username: admin
# Password: admin123
```

### MFA Authentication
If MFA is enabled:
```bash
upid auth login
# Enter username and password
# Enter MFA code when prompted
```

### Enterprise Authentication
```bash
# OIDC
upid auth oidc --provider-url https://your-oidc-provider.com

# SAML
upid auth saml --metadata-url https://your-saml-provider.com/metadata

# LDAP
upid auth ldap --server ldap://your-ldap-server.com
```

## Core Commands

### Authentication Commands

#### Login
```bash
upid auth login [--username USERNAME] [--password PASSWORD]
```

#### Logout
```bash
upid auth logout
```

#### Check Status
```bash
upid auth status
```

### Analysis Commands

#### Cluster Analysis
```bash
# Comprehensive cluster analysis
upid analyze cluster [--namespace NAMESPACE] [--time-range 1h|6h|24h|7d]

# Quick analysis
upid analyze quick

# Detailed analysis with custom parameters
upid analyze detailed --cpu-threshold 80 --memory-threshold 85
```

#### Pod Analysis
```bash
# Analyze specific pod
upid analyze pod POD_NAME --namespace NAMESPACE

# Analyze all pods in namespace
upid analyze pods --namespace NAMESPACE
```

#### Resource Analysis
```bash
# CPU analysis
upid analyze cpu [--time-range 24h]

# Memory analysis
upid analyze memory [--time-range 24h]

# Network analysis
upid analyze network [--time-range 24h]
```

### Optimization Commands

#### Resource Optimization
```bash
# Get optimization recommendations
upid optimize resources

# Apply optimizations
upid optimize apply --recommendation-id RECOMMENDATION_ID

# Preview optimizations
upid optimize preview
```

#### Cost Optimization
```bash
# Analyze costs
upid optimize cost --time-range 30d

# Get cost savings recommendations
upid optimize cost-savings

# Apply cost optimizations
upid optimize apply-cost --recommendation-id RECOMMENDATION_ID
```

### Reporting Commands

#### Generate Reports
```bash
# Executive summary
upid report executive --time-range 7d

# Technical report
upid report technical --time-range 24h

# Cost report
upid report cost --time-range 30d

# Security report
upid report security --time-range 7d
```

#### Export Reports
```bash
# Export to PDF
upid report export --format pdf --output report.pdf

# Export to JSON
upid report export --format json --output report.json

# Export to CSV
upid report export --format csv --output report.csv
```

### Dashboard Commands

#### Executive Dashboard
```bash
# Launch web dashboard
upid dashboard

# View specific metrics
upid dashboard --metric cpu --time-range 24h

# Custom dashboard
upid dashboard --custom-config dashboard-config.yaml
```

### Storage Commands

#### Data Management
```bash
# Backup data
upid storage backup --output backup.tar.gz

# Restore data
upid storage restore --input backup.tar.gz

# Clear old data
upid storage cleanup --older-than 30d
```

## Advanced Features

### Machine Learning

#### Resource Prediction
```bash
# Predict resource usage
upid ml predict --resource cpu --horizon 7d

# Train prediction model
upid ml train --model resource-prediction --data training-data.json
```

#### Anomaly Detection
```bash
# Detect anomalies
upid ml anomalies --severity high

# Configure anomaly detection
upid ml configure-anomalies --threshold 0.8
```

### Business Intelligence

#### KPI Tracking
```bash
# View KPIs
upid bi kpis --time-range 30d

# Set KPI targets
upid bi set-targets --kpi cost-savings --target 25
```

#### ROI Analysis
```bash
# Calculate ROI
upid bi roi --time-range 90d

# Generate business report
upid bi report --type executive-summary
```

### Cloud Integration

#### AWS Integration
```bash
# Configure AWS billing
upid cloud aws configure --access-key ACCESS_KEY --secret-key SECRET_KEY

# Analyze AWS costs
upid cloud aws costs --time-range 30d
```

#### GCP Integration
```bash
# Configure GCP billing
upid cloud gcp configure --project-id PROJECT_ID --key-file key.json

# Analyze GCP costs
upid cloud gcp costs --time-range 30d
```

#### Azure Integration
```bash
# Configure Azure billing
upid cloud azure configure --subscription-id SUBSCRIPTION_ID --tenant-id TENANT_ID

# Analyze Azure costs
upid cloud azure costs --time-range 30d
```

## Troubleshooting

### Common Issues

#### Authentication Problems
```bash
# Reset authentication
upid auth reset

# Check authentication status
upid auth status --verbose
```

#### Connection Issues
```bash
# Test cluster connection
upid test connection

# Check kubectl configuration
kubectl cluster-info
```

#### Performance Issues
```bash
# Check system resources
upid system status

# Optimize performance
upid system optimize
```

### Debug Mode
```bash
# Enable debug logging
upid --debug analyze cluster

# View detailed logs
upid logs --level debug
```

### Support Commands
```bash
# Generate support bundle
upid support bundle --output support-bundle.tar.gz

# Check system health
upid support health-check

# Validate configuration
upid support validate-config
```

## Best Practices

### Security
1. **Use strong passwords** and enable MFA
2. **Regularly rotate credentials**
3. **Use role-based access control**
4. **Monitor authentication logs**

### Performance
1. **Run analysis during off-peak hours**
2. **Use appropriate time ranges for analysis**
3. **Regularly backup data**
4. **Monitor resource usage**

### Data Management
1. **Regular data cleanup** to prevent storage bloat
2. **Backup important reports** and configurations
3. **Use version control** for custom configurations
4. **Monitor storage usage**

### Integration
1. **Configure cloud billing** for accurate cost analysis
2. **Set up monitoring alerts** for critical metrics
3. **Integrate with existing tools** and workflows
4. **Regular updates** to latest versions

### Reporting
1. **Schedule regular reports** for stakeholders
2. **Customize reports** for different audiences
3. **Track trends** over time
4. **Share insights** with team members

## Configuration

### Environment Variables
```bash
export UPID_JWT_SECRET="your-secret-key"
export UPID_REDIS_HOST="localhost"
export UPID_REDIS_PORT="6379"
export UPID_DB_PATH="/path/to/upid.db"
```

### Configuration File
Create `~/.upid/config.yaml`:
```yaml
auth:
  default_provider: "local"
  mfa_required: true
  
storage:
  database_path: "/path/to/upid.db"
  backup_enabled: true
  
monitoring:
  metrics_interval: 60
  alert_threshold: 0.8
  
cloud:
  aws:
    enabled: true
    region: "us-west-2"
  gcp:
    enabled: false
  azure:
    enabled: false
```

## API Reference

### REST API
The UPID CLI also provides a REST API for integration:

```bash
# Start API server
upid api start --port 8080

# API endpoints
GET /api/v1/analysis/cluster
POST /api/v1/auth/login
GET /api/v1/dashboard/metrics
```

### Webhook Integration
```bash
# Configure webhooks
upid webhook configure --url https://your-webhook-url.com --events alerts,reports
```

## Support

### Getting Help
```bash
# Show help
upid --help

# Command-specific help
upid analyze --help

# Show version
upid --version
```

### Documentation
- **Online Documentation**: https://docs.upid.io
- **API Reference**: https://api.upid.io
- **Community Forum**: https://community.upid.io

### Support Channels
- **Email**: support@upid.io
- **Slack**: #upid-support
- **GitHub Issues**: https://github.com/your-org/upid-cli/issues

---

**UPID CLI v2.0** - Production Ready Kubernetes Intelligence Platform 