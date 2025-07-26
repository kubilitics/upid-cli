# 🎯 UPID Demo Scenarios

This directory contains specific demonstration scenarios that showcase different aspects of UPID's capabilities.

## Scenario Categories

### 1. 💰 Cost Optimization Scenarios
- **Over-provisioned Development**: Workloads with 4-10x resource allocation
- **Idle Batch Jobs**: Periodic workloads perfect for zero-pod scaling
- **Abandoned Services**: Unused workloads consuming resources
- **Resource Rightsizing**: Optimizing CPU/memory allocation

### 2. 🤖 ML-Powered Analytics Scenarios
- **Anomaly Detection**: Identifying unusual resource patterns
- **Predictive Analytics**: Forecasting resource needs
- **Usage Optimization**: ML-driven rightsizing recommendations
- **Trend Analysis**: Long-term resource usage patterns

### 3. 🏢 Enterprise Scenarios
- **Multi-Tenant Environments**: Namespace-based cost allocation
- **Compliance Reporting**: Audit trails and governance
- **Executive Dashboards**: Business-focused cost reports
- **Security Integration**: Enterprise authentication and RBAC

### 4. 🔄 Zero-Pod Scaling Scenarios
- **Scheduled Batch Jobs**: ETL, reports, backups
- **Event-Driven Workloads**: ML training, data processing
- **Development Environments**: Non-production workloads
- **Seasonal Applications**: Holiday/peak-time services

## Quick Scenario Selection

Choose scenarios based on your demonstration focus:

| Scenario | Time | Business Value | Technical Complexity |
|----------|------|----------------|---------------------|
| Development Over-provisioning | 5 min | $1,800/month | Low |
| Zero-Pod Scaling | 10 min | $900/month | Medium |
| ML Analytics | 15 min | $1,200/month | High |
| Executive Reporting | 5 min | Business Impact | Low |

## Usage

1. **Quick Demo**: Use `scripts/01-quick-demo.sh` for automated 5-minute overview
2. **Complete Demo**: Follow `docs/COMPLETE_DEMO_GUIDE.md` for comprehensive 45-60 minute demonstration
3. **Custom Scenarios**: Deploy specific workloads from `workloads/` directory
4. **Interactive Exploration**: Use individual kubectl and upid commands

Each scenario is designed to show real business value with quantified cost savings and technical capabilities.