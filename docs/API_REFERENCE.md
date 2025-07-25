# UPID CLI API Reference

## Overview

UPID CLI provides a comprehensive REST API for Kubernetes cost optimization and resource management. The API is designed for enterprise integration and supports authentication, real-time analysis, and automated optimization.

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Authentication**: JWT Bearer tokens  

---

## Authentication Endpoints

### POST /api/v1/auth/login
**Purpose**: Authenticate users and obtain access tokens  
**Value**: Secure access to all UPID features with role-based permissions

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "username": "admin",
    "role": "admin",
    "permissions": ["read", "write", "admin"]
  },
  "expires": "2025-12-31T23:59:59Z"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### POST /api/v1/auth/logout
**Purpose**: Invalidate user session and tokens  
**Value**: Secure session termination for compliance

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### GET /api/v1/auth/status
**Purpose**: Check authentication status and token validity  
**Value**: Session validation for client applications

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "authenticated": true,
  "user": "admin",
  "role": "admin",
  "expires": "2025-12-31T23:59:59Z",
  "permissions": ["read", "write", "admin"]
}
```

---

## Analysis Endpoints

### POST /api/v1/analyze/cluster
**Purpose**: Comprehensive cluster analysis with cost optimization insights  
**Value**: Identify $50k-$500k+ annual savings through intelligent resource analysis

**Request Body**:
```json
{
  "namespace": "production",
  "time_range": "24h",
  "include_idle": true,
  "confidence_threshold": 0.85
}
```

**Response**:
```json
{
  "analysis": {
    "cluster_name": "production-cluster",
    "namespace": "production",
    "total_pods": 45,
    "running_pods": 42,
    "idle_pods": 13,
    "cost_per_month": 3200.00,
    "potential_savings": 1400.00,
    "efficiency_score": 0.62,
    "health_check_traffic_filtered": 2847,
    "real_business_requests": 142,
    "recommendations": [
      {
        "type": "zero_pod_scaling",
        "workloads": ["legacy-api-v1", "batch-processor"],
        "monthly_savings": 1205.00,
        "confidence": 0.96
      },
      {
        "type": "resource_rightsizing", 
        "pods": ["web-server-1", "web-server-2"],
        "cpu_optimization": "50% reduction",
        "memory_optimization": "30% reduction",
        "monthly_savings": 195.00
      }
    ],
    "risk_assessment": {
      "safety_score": "HIGH",
      "rollback_plan": "Available",
      "estimated_downtime": "0 minutes"
    }
  },
  "timestamp": "2025-07-25T23:00:00Z"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze/cluster \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"namespace":"production","time_range":"24h"}'
```

### POST /api/v1/analyze/idle
**Purpose**: Identify idle workloads with ML-powered confidence scoring  
**Value**: Pinpoint exact workloads wasting 60-80% of infrastructure budget

**Request Body**:
```json
{
  "namespace": "production",
  "confidence_threshold": 0.85,
  "time_range": "7d",
  "exclude_system_workloads": true
}
```

**Response**:
```json
{
  "idle_workloads": [
    {
      "name": "legacy-api-v1",
      "namespace": "production",
      "type": "deployment",
      "current_replicas": 3,
      "recommended_replicas": 0,
      "idle_confidence": 0.96,
      "real_traffic_per_minute": 0.2,
      "health_check_traffic_per_minute": 45.3,
      "monthly_cost": 847.00,
      "monthly_savings": 847.00,
      "last_real_request": "2025-07-20T14:30:00Z",
      "safety_analysis": {
        "rollback_time": "30 seconds",
        "dependencies": [],
        "risk_level": "LOW"
      }
    },
    {
      "name": "batch-processor",
      "namespace": "production", 
      "type": "deployment",
      "current_replicas": 5,
      "recommended_replicas": 0,
      "idle_confidence": 0.99,
      "real_traffic_per_minute": 0.0,
      "monthly_cost": 1205.00,
      "monthly_savings": 1205.00,
      "last_real_request": "2025-07-15T09:00:00Z"
    }
  ],
  "summary": {
    "total_idle_workloads": 4,
    "total_monthly_savings": 3109.00,
    "total_annual_savings": 37308.00,
    "average_confidence": 0.94
  },
  "timestamp": "2025-07-25T23:00:00Z"
}
```

### GET /api/v1/analyze/resources
**Purpose**: Real-time resource utilization analysis across cluster  
**Value**: Optimize resource requests/limits for 20-40% efficiency gains

**Query Parameters**:
- `namespace` (optional): Target namespace
- `time_range` (optional): Analysis period (1h, 24h, 7d, 30d)
- `resource_type` (optional): cpu, memory, network, storage

**Response**:
```json
{
  "resource_analysis": {
    "cluster_totals": {
      "cpu_cores_allocated": 120,
      "cpu_cores_used": 45,
      "cpu_utilization": 0.375,
      "memory_gb_allocated": 480,
      "memory_gb_used": 180,
      "memory_utilization": 0.375,
      "storage_gb_allocated": 2000,
      "storage_gb_used": 800,
      "storage_utilization": 0.40
    },
    "optimization_opportunities": [
      {
        "type": "cpu_overprovisioning",
        "affected_pods": 23,
        "current_requests": "8 cores",
        "recommended_requests": "3 cores", 
        "monthly_savings": 450.00
      },
      {
        "type": "memory_overprovisioning",
        "affected_pods": 18,
        "current_requests": "64Gi",
        "recommended_requests": "32Gi",
        "monthly_savings": 320.00
      }
    ],
    "efficiency_score": 0.62,
    "waste_percentage": 0.38
  }
}
```

---

## Optimization Endpoints

### POST /api/v1/optimize/zero-pod
**Purpose**: Safe zero-pod scaling with automated rollback capabilities  
**Value**: Immediate 60-80% cost reduction on idle workloads with zero risk

**Request Body**:
```json
{
  "namespace": "production",
  "workloads": ["legacy-api-v1", "batch-processor"],
  "dry_run": true,
  "safety_checks": true,
  "rollback_plan": true
}
```

**Response**:
```json
{
  "optimization": {
    "namespace": "production",
    "dry_run": true,
    "workloads_optimized": 2,
    "total_monthly_savings": 2052.00,
    "total_annual_savings": 24624.00,
    "actions": [
      {
        "workload": "legacy-api-v1",
        "action": "scale_to_zero",
        "current_replicas": 3,
        "target_replicas": 0,
        "monthly_savings": 847.00,
        "execution_time": "15 seconds",
        "rollback_command": "kubectl scale deployment legacy-api-v1 --replicas=3",
        "rollback_time": "30 seconds"
      },
      {
        "workload": "batch-processor",
        "action": "scale_to_zero",
        "current_replicas": 5, 
        "target_replicas": 0,
        "monthly_savings": 1205.00,
        "execution_time": "20 seconds"
      }
    ],
    "safety_analysis": {
      "safety_score": "HIGH",
      "risk_factors": [],
      "rollback_plan": "Available",
      "estimated_downtime": "0 minutes",
      "dependencies_checked": true,
      "traffic_analysis_completed": true
    },
    "execution_plan": {
      "total_execution_time": "35 seconds",
      "rollback_available": true,
      "monitoring_enabled": true,
      "alerts_configured": true
    }
  },
  "timestamp": "2025-07-25T23:00:00Z"
}
```

**Apply Changes** (set `dry_run: false`):
```bash
curl -X POST http://localhost:8000/api/v1/optimize/zero-pod \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"namespace":"production","workloads":["legacy-api-v1"],"dry_run":false}'
```

### POST /api/v1/optimize/resources
**Purpose**: Right-size resource requests and limits based on actual usage  
**Value**: Optimize resource allocation for 20-40% efficiency improvement

**Request Body**:
```json
{
  "namespace": "production",
  "optimization_type": "rightsizing",
  "target_utilization": 0.70,
  "safety_margin": 0.20
}
```

**Response**:
```json
{
  "resource_optimization": {
    "namespace": "production",
    "optimizations": [
      {
        "workload": "web-server",
        "current_cpu_request": "2000m",
        "recommended_cpu_request": "800m", 
        "current_memory_request": "4Gi",
        "recommended_memory_request": "2Gi",
        "monthly_savings": 280.00,
        "confidence": 0.89
      }
    ],
    "total_monthly_savings": 680.00,
    "efficiency_improvement": 0.25
  }
}
```

---

## Reporting Endpoints

### GET /api/v1/reports/executive
**Purpose**: Executive dashboard with ROI metrics and business intelligence  
**Value**: C-suite reporting with clear ROI justification and savings tracking

**Query Parameters**:
- `time_range`: 7d, 30d, 90d, 1y
- `format`: json, pdf, excel

**Response**:
```json
{
  "executive_report": {
    "period": "30d",
    "generated": "2025-07-25T23:00:00Z",
    "kpis": {
      "total_monthly_cost": 8450.00,
      "potential_monthly_savings": 3250.00,
      "actual_monthly_savings": 2100.00,
      "cost_optimization_percentage": 24.8,
      "resource_efficiency": 0.62,
      "roi_percentage": 1229.0,
      "payback_period_months": 0.98
    },
    "savings_breakdown": {
      "zero_pod_scaling": 1800.00,
      "resource_rightsizing": 450.00,
      "storage_optimization": 320.00,
      "network_optimization": 180.00
    },
    "recommendations": [
      {
        "priority": "HIGH",
        "action": "Implement zero-pod scaling for 6 identified workloads",
        "impact": "$2,400/month savings",
        "effort": "2 hours implementation"
      },
      {
        "priority": "MEDIUM", 
        "action": "Right-size resource requests for over-provisioned pods",
        "impact": "$800/month savings",
        "effort": "4 hours implementation"
      }
    ],
    "trend_analysis": {
      "cost_trend": "decreasing",
      "efficiency_trend": "improving", 
      "optimization_velocity": "accelerating"
    }
  }
}
```

### GET /api/v1/reports/technical
**Purpose**: Detailed technical analysis for DevOps and SRE teams  
**Value**: Actionable technical insights for infrastructure optimization

**Response**:
```json
{
  "technical_report": {
    "cluster_health": {
      "total_nodes": 8,
      "healthy_nodes": 8,
      "total_pods": 156,
      "running_pods": 142,
      "pending_pods": 0,
      "failed_pods": 2
    },
    "resource_utilization": {
      "cpu_utilization": 0.45,
      "memory_utilization": 0.38,
      "storage_utilization": 0.67,
      "network_utilization": 0.23
    },
    "optimization_details": [
      {
        "namespace": "production",
        "workload": "api-server",
        "optimization_type": "cpu_rightsizing",
        "current_request": "2000m",
        "recommended_request": "800m",
        "confidence": 0.92,
        "technical_justification": "95th percentile usage: 600m over 30 days"
      }
    ]
  }
}
```

---

## Cluster Management Endpoints

### GET /api/v1/clusters
**Purpose**: List and manage connected Kubernetes clusters  
**Value**: Multi-cluster visibility and centralized cost management

**Response**:
```json
{
  "clusters": [
    {
      "name": "production-cluster",
      "environment": "production",
      "status": "active",
      "nodes": 8,
      "pods": 156,
      "namespaces": 12,
      "monthly_cost": 4200.00,
      "efficiency_score": 0.68,
      "last_analyzed": "2025-07-25T22:30:00Z",
      "optimization_opportunities": 15
    },
    {
      "name": "staging-cluster",
      "environment": "staging", 
      "status": "active",
      "nodes": 3,
      "pods": 45,
      "monthly_cost": 1200.00,
      "efficiency_score": 0.45
    }
  ],
  "summary": {
    "total_clusters": 2,
    "total_monthly_cost": 5400.00,
    "average_efficiency": 0.57,
    "total_optimization_opportunities": 23
  }
}
```

### POST /api/v1/clusters/register
**Purpose**: Register new Kubernetes cluster for monitoring  
**Value**: Extend cost optimization to additional clusters

**Request Body**:
```json
{
  "name": "development-cluster",
  "environment": "development",
  "kubeconfig": "base64-encoded-kubeconfig",
  "context": "development-context"
}
```

---

## Health and Status Endpoints

### GET /health
**Purpose**: API server health check  
**Value**: Monitoring and alerting integration

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-07-25T23:00:00Z",
  "uptime": "running",
  "dependencies": {
    "database": "healthy",
    "kubernetes": "connected"
  }
}
```

### GET /api/v1/status
**Purpose**: Detailed API status and capabilities  
**Value**: Service discovery and feature availability

**Response**:
```json
{
  "api_version": "v1",
  "server_version": "1.0.0",
  "status": "operational",
  "features": [
    "authentication",
    "cluster_analysis",
    "cost_optimization", 
    "reporting",
    "multi_cluster",
    "zero_pod_scaling"
  ],
  "rate_limits": {
    "requests_per_minute": 1000,
    "analysis_requests_per_hour": 100
  },
  "timestamp": "2025-07-25T23:00:00Z"
}
```

---

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": "Valid JWT token must be provided in Authorization header"
  },
  "timestamp": "2025-07-25T23:00:00Z"
}
```

**Common Error Codes**:
- `UNAUTHORIZED` (401): Authentication required or invalid token
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (400): Invalid request parameters
- `INTERNAL_ERROR` (500): Server error
- `RATE_LIMITED` (429): Too many requests

---

## Rate Limiting

**Default Limits**:
- General API calls: 1000 requests/minute
- Analysis operations: 100 requests/hour  
- Authentication: 10 requests/minute

**Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when rate limit resets

---

## SDK Examples

### Python SDK
```python
import requests

# Authenticate
response = requests.post('http://localhost:8000/api/v1/auth/login', 
                        json={'username': 'admin', 'password': 'admin123'})
token = response.json()['token']

# Analyze cluster
headers = {'Authorization': f'Bearer {token}'}
analysis = requests.post('http://localhost:8000/api/v1/analyze/cluster',
                        headers=headers,
                        json={'namespace': 'production'})
print(f"Monthly savings: ${analysis.json()['analysis']['potential_savings']}")
```

### JavaScript SDK
```javascript
// Authenticate
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { token } = await loginResponse.json();

// Get executive report
const reportResponse = await fetch('http://localhost:8000/api/v1/reports/executive?time_range=30d', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const report = await reportResponse.json();
console.log(`ROI: ${report.executive_report.kpis.roi_percentage}%`);
```

---

## API Versioning

UPID API uses URL path versioning:
- Current version: `/api/v1/`
- Future versions: `/api/v2/`, `/api/v3/`

Backward compatibility is maintained for at least 12 months after new version releases.