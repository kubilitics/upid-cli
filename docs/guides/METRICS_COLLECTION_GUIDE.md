# UPID Metrics Collection Guide

## Overview

UPID CLI provides comprehensive metrics collection capabilities that integrate with your existing monitoring stack. This guide shows you how to configure and use UPID with Prometheus, cAdvisor, and custom metrics endpoints.

## Quick Start

### 1. Basic Setup (Kubernetes Only)

If you only want to use UPID with basic Kubernetes metrics:

```bash
# Test your setup
upid intelligence test-connections

# Run analysis
upid intelligence analyze
```

### 2. Full Setup (With Monitoring Stack)

For full intelligence capabilities, configure your monitoring endpoints:

```bash
# Set your monitoring endpoints
export UPID_PROMETHEUS_URL="http://your-prometheus:9090"
export UPID_CADVISOR_URL="http://your-cadvisor:8080"
export UPID_CUSTOM_METRICS_URL="http://your-metrics:8080"

# Test connections
upid intelligence test-connections

# Run comprehensive analysis
upid intelligence analyze
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `UPID_PROMETHEUS_URL` | Prometheus server URL | `http://localhost:9090` | `http://prometheus:9090` |
| `UPID_CADVISOR_URL` | cAdvisor server URL | `http://localhost:8080` | `http://cadvisor:8080` |
| `UPID_CUSTOM_METRICS_URL` | Custom metrics endpoint | `None` | `http://metrics:8080` |
| `UPID_METRICS_TIMEOUT` | Request timeout (seconds) | `10` | `15` |

### Kubernetes Context

UPID automatically uses your current kubectl context. To use a specific context:

```bash
# Use specific context
upid intelligence analyze --cluster my-cluster

# Or set KUBECONFIG
export KUBECONFIG="/path/to/your/kubeconfig"
upid intelligence analyze
```

## Monitoring Stack Integration

### Prometheus Integration

UPID queries Prometheus for advanced metrics including:

- **CPU Usage**: `sum(rate(container_cpu_usage_seconds_total{container!=""}[5m])) * 100`
- **Memory Usage**: `sum(container_memory_usage_bytes{container!=""}) / sum(machine_memory_bytes) * 100`
- **Pod Count**: `count(kube_pod_info)`
- **Error Rate**: `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100`

**Setup:**
```bash
# If Prometheus is running locally
export UPID_PROMETHEUS_URL="http://localhost:9090"

# If Prometheus is in Kubernetes
export UPID_PROMETHEUS_URL="http://prometheus-service:9090"

# If using port-forward
kubectl port-forward svc/prometheus 9090:9090 &
export UPID_PROMETHEUS_URL="http://localhost:9090"
```

### cAdvisor Integration

UPID queries cAdvisor for container-level metrics including:

- Container CPU usage
- Container memory usage
- Container count
- Average metrics per container

**Setup:**
```bash
# If cAdvisor is running locally
export UPID_CADVISOR_URL="http://localhost:8080"

# If cAdvisor is in Kubernetes
export UPID_CADVISOR_URL="http://cadvisor-service:8080"

# If using port-forward
kubectl port-forward svc/cadvisor 8080:8080 &
export UPID_CADVISOR_URL="http://localhost:8080"
```

### Custom Metrics Integration

UPID can query any HTTP endpoint that provides metrics in:

- **JSON format**: `{"metric_name": "value", "value": 123.45}`
- **Prometheus format**: `metric_name{label="value"} 123.45`

**Setup:**
```bash
# Set your custom metrics endpoint
export UPID_CUSTOM_METRICS_URL="http://your-app:8080/metrics"

# UPID will try these endpoints automatically:
# - /metrics
# - /api/metrics
# - /api/v1/metrics
# - /metrics/{metric_name}
# - /api/metrics/{metric_name}
```

## Testing Your Setup

### 1. Test Connections

```bash
# Test all connections
upid intelligence test-connections

# Expected output:
# ✅ KUBECTL: Successfully connected to Kubernetes cluster
# ✅ PROMETHEUS: Successfully connected to Prometheus
# ✅ CADVISOR: Successfully connected to cAdvisor
# ✅ CUSTOM_METRICS: Successfully connected to custom metrics endpoint
```

### 2. Test Individual Components

```bash
# Test business intelligence
upid intelligence business

# Test predictive analytics
upid intelligence predict

# Test optimization
upid intelligence optimize

# Get real-time insights
upid intelligence insights
```

### 3. Run Comprehensive Analysis

```bash
# Run all intelligence engines
upid intelligence analyze

# With specific cluster
upid intelligence analyze --cluster production

# With custom output format
upid intelligence analyze --output json
```

## Troubleshooting

### Common Issues

#### 1. Prometheus Connection Failed
```bash
# Check if Prometheus is running
curl http://localhost:9090/api/v1/query?query=up

# If using port-forward
kubectl port-forward svc/prometheus 9090:9090
```

#### 2. cAdvisor Connection Failed
```bash
# Check if cAdvisor is running
curl http://localhost:8080/api/v1.3/docker/

# If using port-forward
kubectl port-forward svc/cadvisor 8080:8080
```

#### 3. Custom Metrics Connection Failed
```bash
# Test your metrics endpoint
curl http://your-app:8080/metrics

# Ensure it returns valid metrics format
```

#### 4. Kubernetes Connection Failed
```bash
# Check kubectl configuration
kubectl config current-context

# Test cluster access
kubectl get nodes
```

### Debug Mode

Enable verbose logging to debug connection issues:

```bash
# Enable debug mode
export UPID_DEBUG=1

# Run with verbose output
upid intelligence analyze --verbose
```

## Advanced Configuration

### Custom Prometheus Queries

You can customize Prometheus queries by modifying the metrics collector:

```python
# In upid/core/metrics_collector.py
queries = {
    'cpu_usage': 'your_custom_cpu_query',
    'memory_usage': 'your_custom_memory_query',
    'custom_metric': 'your_custom_query'
}
```

### Custom Metrics Endpoints

UPID supports multiple endpoint formats:

```bash
# JSON format
curl http://your-app/metrics
# Returns: {"cpu_usage": 75.5, "memory_usage": 82.3}

# Prometheus format
curl http://your-app/metrics
# Returns: cpu_usage{instance="app"} 75.5
```

### Timeout Configuration

Adjust timeouts for slow networks:

```bash
# Increase timeout to 30 seconds
export UPID_METRICS_TIMEOUT=30
```

## Production Deployment

### 1. Environment Setup

Create a configuration file:

```bash
# ~/.upid/config
export UPID_PROMETHEUS_URL="http://prometheus-service:9090"
export UPID_CADVISOR_URL="http://cadvisor-service:8080"
export UPID_CUSTOM_METRICS_URL="http://metrics-service:8080"
export UPID_METRICS_TIMEOUT=15
```

### 2. Kubernetes Integration

For Kubernetes deployments, use ConfigMaps:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: upid-config
data:
  UPID_PROMETHEUS_URL: "http://prometheus-service:9090"
  UPID_CADVISOR_URL: "http://cadvisor-service:8080"
  UPID_CUSTOM_METRICS_URL: "http://metrics-service:8080"
  UPID_METRICS_TIMEOUT: "15"
```

### 3. Monitoring Integration

Set up monitoring for UPID itself:

```bash
# Monitor UPID performance
upid intelligence analyze --output json | jq '.summary.key_metrics'

# Set up alerts for connection failures
upid intelligence test-connections | grep "❌"
```

## Examples

### Example 1: Basic Kubernetes Analysis

```bash
# Simple analysis with kubectl metrics only
upid intelligence analyze

# Output includes:
# - CPU and memory usage
# - Pod count and status
# - Basic optimization recommendations
```

### Example 2: Full Stack Analysis

```bash
# Set up monitoring stack
export UPID_PROMETHEUS_URL="http://prometheus:9090"
export UPID_CADVISOR_URL="http://cadvisor:8080"

# Run comprehensive analysis
upid intelligence analyze

# Output includes:
# - Business intelligence correlations
# - Predictive analytics
# - Advanced optimization recommendations
# - Real-time insights
```

### Example 3: Custom Metrics Integration

```bash
# Set up custom metrics
export UPID_CUSTOM_METRICS_URL="http://my-app:8080/metrics"

# Run analysis with custom metrics
upid intelligence analyze

# UPID will include your custom metrics in the analysis
```

## Support

For issues with metrics collection:

1. **Test connections**: `upid intelligence test-connections`
2. **Check logs**: Enable debug mode with `export UPID_DEBUG=1`
3. **Verify endpoints**: Test each endpoint manually with `curl`
4. **Review configuration**: Ensure environment variables are set correctly

## Next Steps

After setting up metrics collection:

1. **Run regular analysis**: Set up cron jobs for automated analysis
2. **Monitor trends**: Use historical data for trend analysis
3. **Optimize resources**: Implement optimization recommendations
4. **Scale monitoring**: Add more custom metrics as needed

---

**UPID CLI** - Kubernetes Resource Optimization Platform  
© 2024 Kubilitics - hello@kubilitics.com 