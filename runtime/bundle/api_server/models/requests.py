"""
UPID CLI API Server Request Models
Pydantic models for request validation and documentation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class OptimizationType(str, Enum):
    """Types of optimizations available"""
    ZERO_POD = "zero-pod"
    RESOURCE_LIMITS = "resource-limits"
    COST_OPTIMIZATION = "cost-optimization"
    SCALING = "scaling"


class AnalysisType(str, Enum):
    """Types of analysis available"""
    CLUSTER = "cluster"
    NAMESPACE = "namespace"
    WORKLOAD = "workload"
    IDLE = "idle"
    COST = "cost"


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "on-premise"


# Authentication Models
class LoginRequest(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str = Field(..., description="Valid refresh token")


# Cluster Management Models
class ClusterRegisterRequest(BaseModel):
    """Register a new Kubernetes cluster"""
    name: str = Field(..., min_length=3, max_length=100)
    kubeconfig: Optional[str] = Field(None, description="Base64 encoded kubeconfig")
    endpoint: Optional[str] = Field(None, description="Kubernetes API endpoint")
    cloud_provider: CloudProvider = Field(CloudProvider.ON_PREMISE)
    region: Optional[str] = Field(None, max_length=50)
    tags: Optional[Dict[str, str]] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Cluster name must contain only alphanumeric characters, hyphens, and underscores')
        return v


class ClusterUpdateRequest(BaseModel):
    """Update cluster information"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    tags: Optional[Dict[str, str]] = Field(None)
    is_active: Optional[bool] = Field(None)


# Analysis Models
class ClusterAnalysisRequest(BaseModel):
    """Request cluster-wide analysis"""
    cluster_id: str = Field(..., description="Cluster UUID")
    analysis_type: AnalysisType = Field(AnalysisType.CLUSTER)
    include_metrics: bool = Field(True, description="Include detailed metrics")
    time_range_hours: int = Field(24, ge=1, le=168, description="Time range in hours (1-168)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": "550e8400-e29b-41d4-a716-446655440000",
                "analysis_type": "cluster",
                "include_metrics": True,
                "time_range_hours": 24
            }
        }


class IdleAnalysisRequest(BaseModel):
    """Request idle workload analysis"""
    cluster_id: str = Field(..., description="Cluster UUID")
    namespace: str = Field("default", description="Kubernetes namespace")
    confidence_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Confidence threshold (0.0-1.0)")
    cpu_threshold_percent: float = Field(5.0, ge=0.0, le=100.0, description="CPU usage threshold percentage")
    memory_threshold_percent: float = Field(10.0, ge=0.0, le=100.0, description="Memory usage threshold percentage")
    exclude_health_checks: bool = Field(True, description="Exclude health check traffic from analysis")
    time_range_hours: int = Field(24, ge=1, le=168, description="Analysis time range in hours")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": "550e8400-e29b-41d4-a716-446655440000",
                "namespace": "default",
                "confidence_threshold": 0.85,
                "cpu_threshold_percent": 5.0,
                "memory_threshold_percent": 10.0,
                "exclude_health_checks": True,
                "time_range_hours": 24
            }
        }


class CostAnalysisRequest(BaseModel):
    """Request cost analysis"""
    cluster_id: str = Field(..., description="Cluster UUID")
    time_range_days: int = Field(30, ge=1, le=365, description="Cost analysis period in days")
    include_projections: bool = Field(True, description="Include cost projections")
    breakdown_by: List[str] = Field(
        default=["namespace", "workload"],
        description="Cost breakdown dimensions"
    )


# Optimization Models
class ZeroPodScalingRequest(BaseModel):
    """Request zero-pod scaling optimization"""
    cluster_id: str = Field(..., description="Cluster UUID")
    namespace: str = Field("default", description="Target namespace")
    workload_selector: Optional[Dict[str, str]] = Field(None, description="Label selector for workloads")
    dry_run: bool = Field(True, description="Perform dry run without actual changes")
    safety_checks: bool = Field(True, description="Enable safety checks and rollback")
    rollback_timeout_minutes: int = Field(5, ge=1, le=60, description="Rollback timeout in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": "550e8400-e29b-41d4-a716-446655440000",
                "namespace": "default",
                "workload_selector": {"app": "web-server"},
                "dry_run": True,
                "safety_checks": True,
                "rollback_timeout_minutes": 5
            }
        }


class ResourceOptimizationRequest(BaseModel):
    """Request resource limit optimization"""
    cluster_id: str = Field(..., description="Cluster UUID")
    namespace: str = Field("default", description="Target namespace")
    optimization_target: str = Field("cost", pattern="^(cost|performance|balanced)$")
    cpu_optimization: bool = Field(True, description="Optimize CPU limits")
    memory_optimization: bool = Field(True, description="Optimize memory limits")
    safety_margin_percent: float = Field(20.0, ge=0.0, le=100.0, description="Safety margin percentage")
    dry_run: bool = Field(True, description="Perform dry run without actual changes")


class BatchOptimizationRequest(BaseModel):
    """Request batch optimization across multiple resources"""
    cluster_id: str = Field(..., description="Cluster UUID")
    optimizations: List[OptimizationType] = Field(..., description="List of optimizations to apply")
    target_namespaces: List[str] = Field(default=["default"], description="Target namespaces")
    dry_run: bool = Field(True, description="Perform dry run without actual changes")
    parallel_execution: bool = Field(False, description="Execute optimizations in parallel")


# Reporting Models
class ExecutiveReportRequest(BaseModel):
    """Request executive cost report"""
    cluster_ids: List[str] = Field(..., description="List of cluster UUIDs")
    time_range_days: int = Field(30, ge=1, le=365, description="Report period in days")
    include_projections: bool = Field(True, description="Include cost projections")
    include_recommendations: bool = Field(True, description="Include optimization recommendations")
    format: str = Field("json", pattern="^(json|pdf|excel)$", description="Report format")


class CustomReportRequest(BaseModel):
    """Request custom report generation"""
    cluster_id: str = Field(..., description="Cluster UUID")
    metrics: List[str] = Field(..., description="Metrics to include in report")
    filters: Optional[Dict[str, Any]] = Field(None, description="Report filters")
    time_range_hours: int = Field(24, ge=1, le=8760, description="Time range in hours")
    aggregation: str = Field("hourly", pattern="^(minutely|hourly|daily|weekly)$")


# Configuration Models
class ConfigurationUpdateRequest(BaseModel):
    """Update system configuration"""
    ml_enabled: Optional[bool] = Field(None, description="Enable ML predictions")
    auto_optimization: Optional[bool] = Field(None, description="Enable automatic optimization")
    safety_checks: Optional[bool] = Field(None, description="Enable safety checks")
    notification_settings: Optional[Dict[str, Any]] = Field(None, description="Notification configuration")
    thresholds: Optional[Dict[str, float]] = Field(None, description="Alert thresholds")


# Webhook Models
class WebhookRequest(BaseModel):
    """Register webhook endpoint"""
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Events to subscribe to")
    secret: Optional[str] = Field(None, description="Webhook secret for validation")
    is_active: bool = Field(True, description="Whether webhook is active")