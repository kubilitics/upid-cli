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
- **Production Data System**: Real Kubernetes cluster integration with unified data ingestion
- **Real-time Analytics**: Live monitoring of cluster performance and resource usage
- **Cost Optimization**: Real-time cost analysis and optimization recommendations
- **Business Intelligence**: KPI tracking and ROI analysis with production data
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

2. **Connect to your Kubernetes cluster**
```bash
# Ensure kubectl is configured
kubectl cluster-info

# UPID CLI will automatically detect your cluster
```

3. **Authenticate**
```bash
upid auth login
# Enter your credentials when prompted
```

4. **Analyze your cluster with production data**
```bash
upid analyze cluster
```

5. **View cost analysis and optimizations**
```bash
upid optimize resources
upid optimize cost
```

6. **View executive dashboard**
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

## Production Data System

UPID CLI v2.0 includes a production-ready data system that provides real-time integration with your Kubernetes clusters.

### Data System Features
- **Real Kubernetes Integration**: Direct connection to your cluster via kubectl
- **Unified Data Ingestion**: Single interface for cluster, node, pod, and metrics data
- **Cost Analysis**: Real-time cost calculation and waste identification
- **Optimization Engine**: Automated resource optimization recommendations
- **Business Intelligence**: KPI tracking and ROI analysis
- **Caching System**: Performance optimization with intelligent caching

### Data Sources
- **Cluster Information**: Version, nodes, namespaces, capacity
- **Node Metrics**: CPU, memory, network, storage usage
- **Pod Analytics**: Resource requests, limits, actual usage
- **Cost Data**: Monthly costs, waste analysis, potential savings
- **Optimization Data**: Resource efficiency, idle workload detection
- **Business Intelligence**: KPIs, trends, alerts, ROI metrics

### Data System Commands
```bash
# Get comprehensive cluster data
upid data cluster

# View cost analysis
upid data cost

# Get optimization recommendations
upid data optimize

# View business intelligence
upid data bi

# Get system metrics
upid data metrics
```

### Mock API System
UPID CLI includes a production-ready mock API system for demonstrations and testing.

#### Mock API Features
- **Realistic Responses**: All API endpoints return realistic data
- **Multiple Scenarios**: Production, staging, and development environments
- **Authentication**: Valid credential validation (admin@upid.io/admin123)
- **Error Handling**: Proper error responses for invalid requests
- **Response Times**: Realistic 100-500ms response times

#### Mock API Endpoints
```bash
# Authentication
POST /api/v1/auth/login

# Cluster Management
GET /api/v1/clusters
GET /api/v1/clusters/{cluster_id}

# Analysis
POST /api/v1/analyze/cluster/{cluster_id}
POST /api/v1/analyze/idle/{cluster_id}
POST /api/v1/analyze/costs/{cluster_id}

# Optimization
GET /api/v1/optimize/strategies/{cluster_id}
POST /api/v1/optimize/simulate/{cluster_id}
POST /api/v1/optimize/apply/{cluster_id}

# Metrics & Reports
GET /api/v1/metrics/{cluster_id}
POST /api/v1/reports/{cluster_id}
GET /api/v1/ai/insights/{cluster_id}
```

#### Using Mock API
```bash
# Enable mock mode
export UPID_MOCK_MODE=true

# Run CLI commands (will use mock API)
upid analyze cluster
upid optimize resources
upid dashboard
```

### Enhanced Authentication System
UPID provides a comprehensive authentication system with OIDC integration and RBAC authorization.

#### Authentication Methods
```bash
# Standard login
upid auth login --email user@example.com --password password

# OIDC login (Google, GitHub, Azure)
upid auth login --provider google
upid auth login --provider github
upid auth login --provider azure

# Token-based login
upid auth login --token your-jwt-token

# SSO login
upid auth sso --provider google
```

#### RBAC Roles and Permissions
- **Viewer**: Read-only access to clusters, analysis, and reports
- **Operator**: Read/write access to clusters and analysis, read-only optimization
- **Admin**: Full access to all features including user management
- **Super Admin**: Enterprise-wide administration capabilities

#### Permission System
```bash
# Check user permissions
upid auth permissions

# Check specific permission
upid auth check-permission --permission read:clusters

# Check role
upid auth check-role --role admin
```

#### Session Management
```bash
# Create session
upid auth session create

# List active sessions
upid auth session list

# Invalidate session
upid auth session invalidate --session-id session_id
```

### API Client Features
The UPID API client provides comprehensive functionality with both real and mock modes.

#### Mock Mode Configuration
```bash
# Environment variable method
export UPID_MOCK_MODE=true

# Config file method
upid config set mock_mode true

# Direct API URL method
upid config set api_url mock://localhost
```

#### API Client Capabilities
- **Authentication**: Login, logout, token refresh
- **Cluster Management**: List, get, add, update, delete clusters
- **Analysis**: Cluster analysis, idle workload detection, cost analysis
- **Optimization**: Strategies, simulation, application
- **Monitoring**: Metrics collection, alerts, status
- **Reporting**: Report generation, export, history
- **AI/ML**: Insights, predictions, anomaly detection
- **Enterprise**: Multi-cluster, policies, compliance

#### Error Handling
- **Retry Logic**: Automatic retries for transient failures
- **Timeout Management**: Configurable request timeouts
- **Error Classification**: Network, authentication, validation errors
- **Graceful Degradation**: Fallback to mock mode when needed

### Demo Scripts
UPID CLI includes comprehensive demo scripts for different customer scenarios.

#### Available Demo Scripts
```bash
# Executive Demo (5 minutes)
./scripts/demos/enhanced_executive_demo.sh

# Technical Demo (15 minutes)
./scripts/demos/enhanced_technical_demo.sh

# Value Proposition Demo (10 minutes)
./scripts/demos/enhanced_value_demo.sh

# Enterprise Demo (20 minutes)
./scripts/demos/enhanced_enterprise_demo.sh
```

#### Demo Features
- **Real CLI Commands**: All demos use actual UPID CLI commands
- **Mock Mode Integration**: Automatically enables mock mode for demonstrations
- **Professional Presentation**: Color-coded output with clear sections
- **Comprehensive Coverage**: Different scenarios for various customer types
- **Immediate Functionality**: No setup required, works out of the box

#### Running Demos
```bash
# Make scripts executable
chmod +x scripts/demos/enhanced_*.sh

# Run executive demo
./scripts/demos/enhanced_executive_demo.sh

# Run with custom scenario
export UPID_MOCK_SCENARIO="enterprise"
./scripts/demos/enhanced_enterprise_demo.sh
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

## ML Pipeline Features

The UPID CLI includes a comprehensive machine learning pipeline for Kubernetes optimization:

### Model Types

- **Optimization Model**: Identifies resource optimization opportunities using LightGBM
- **Prediction Model**: Forecasts future resource usage with regression analysis
- **Anomaly Model**: Detects unusual resource usage patterns using Isolation Forest

### Features

- **Real-time Inference**: Sub-second prediction latency
- **Batch Processing**: Process multiple workloads efficiently
- **Feature Engineering**: Extract 19 features from Kubernetes metrics
- **Model Versioning**: Track model algorithms and versions
- **Performance Monitoring**: Track accuracy and processing time
- **Automatic Retraining**: Retrain models based on age/performance
- **Mock Models**: Fallback when ML libraries unavailable

### Usage

```bash
# Train all models
upid ml train

# Make predictions for a specific workload
upid ml predict --workload my-app

# Batch predictions for all workloads
upid ml predict --batch

# Get model performance metrics
upid ml metrics

# Check model status
upid ml status

# Retrain models if needed
upid ml retrain
```

### ML Pipeline Components

#### Feature Engineering
The ML pipeline extracts 19 features from Kubernetes metrics:
- **Pod-level**: CPU usage, memory usage, network activity, restart count, age
- **Workload-level**: Workload type, namespace, replica count, resource requests/limits
- **Cluster-level**: CPU/memory utilization, pod density, efficiency score
- **Time-based**: Hour of day, day of week, business hours, weekend

#### Model Training
- **Data Preparation**: Historical metrics converted to training data
- **Automated Training**: Train models with validation
- **Performance Metrics**: Track accuracy, precision, recall
- **Retraining Logic**: Automatic retraining based on age/performance

#### Inference System
- **Real-time Predictions**: Single workload inference
- **Batch Processing**: Multi-workload inference
- **Model Versioning**: Track model algorithms and versions
- **Performance Monitoring**: Processing time and error tracking

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