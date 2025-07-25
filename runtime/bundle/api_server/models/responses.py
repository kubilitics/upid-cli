"""
UPID CLI API Server Response Models
Pydantic models for consistent API responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response statuses"""
    SUCCESS = "success"
    ERROR = "error" 
    WARNING = "warning"
    PENDING = "pending"


class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")


class DataResponse(BaseResponse):
    """Response model with data payload"""
    data: Any = Field(..., description="Response data")


class ListResponse(BaseResponse):
    """Response model for list data with pagination"""
    data: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(50, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")


# Authentication Responses
class TokenResponse(BaseResponse):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_info: Dict[str, Any] = Field(..., description="User information")


class UserInfoResponse(BaseResponse):
    """User information response"""
    user: Dict[str, Any] = Field(..., description="User details")
    permissions: List[str] = Field(..., description="User permissions")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")


# Cluster Management Responses
class ClusterInfo(BaseModel):
    """Cluster information model"""
    id: str = Field(..., description="Cluster UUID")
    name: str = Field(..., description="Cluster name")
    status: str = Field(..., description="Cluster status")
    version: str = Field(..., description="Kubernetes version")
    node_count: int = Field(..., description="Number of nodes")
    namespace_count: int = Field(..., description="Number of namespaces")
    pod_count: int = Field(..., description="Number of pods")
    cloud_provider: str = Field(..., description="Cloud provider")
    region: Optional[str] = Field(None, description="Cloud region")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_seen: datetime = Field(..., description="Last health check timestamp")
    tags: Dict[str, str] = Field(default_factory=dict, description="Cluster tags")


class ClusterResponse(DataResponse):
    """Single cluster response"""
    data: ClusterInfo


class ClusterListResponse(ListResponse):
    """Multiple clusters response"""
    data: List[ClusterInfo]


# Analysis Responses
class ResourceMetrics(BaseModel):
    """Resource utilization metrics"""
    cpu_usage_cores: float = Field(..., description="CPU usage in cores")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    memory_usage_bytes: int = Field(..., description="Memory usage in bytes")
    memory_usage_percent: float = Field(..., description="Memory usage percentage")
    network_rx_bytes: int = Field(..., description="Network received bytes")
    network_tx_bytes: int = Field(..., description="Network transmitted bytes")
    storage_usage_bytes: int = Field(..., description="Storage usage in bytes")


class WorkloadInfo(BaseModel):
    """Workload information"""
    name: str = Field(..., description="Workload name")
    namespace: str = Field(..., description="Kubernetes namespace")
    type: str = Field(..., description="Workload type (Deployment, StatefulSet, etc.)")
    replicas: int = Field(..., description="Number of replicas")
    status: str = Field(..., description="Workload status")
    labels: Dict[str, str] = Field(default_factory=dict, description="Workload labels")
    annotations: Dict[str, str] = Field(default_factory=dict, description="Workload annotations")
    created_at: datetime = Field(..., description="Creation timestamp")
    metrics: Optional[ResourceMetrics] = Field(None, description="Current resource metrics")


class ClusterAnalysisResult(BaseModel):
    """Cluster analysis results"""
    cluster_id: str = Field(..., description="Cluster UUID")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")
    cluster_metrics: ResourceMetrics = Field(..., description="Cluster-wide metrics")
    workloads: List[WorkloadInfo] = Field(..., description="Workload information")
    cost_analysis: Dict[str, Any] = Field(..., description="Cost breakdown")
    recommendations: List[Dict[str, Any]] = Field(..., description="Optimization recommendations")
    health_score: float = Field(..., ge=0.0, le=100.0, description="Cluster health score")
    efficiency_score: float = Field(..., ge=0.0, le=100.0, description="Resource efficiency score")


class IdleWorkload(BaseModel):
    """Idle workload detection result"""
    workload: WorkloadInfo = Field(..., description="Workload information")
    idle_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence that workload is idle")
    idle_duration_hours: float = Field(..., description="Duration of idle state in hours")
    potential_savings_monthly: float = Field(..., description="Potential monthly cost savings")
    recommendation: str = Field(..., description="Optimization recommendation")
    risk_level: str = Field(..., description="Risk level of optimization")


class IdleAnalysisResult(BaseModel):
    """Idle workload analysis results"""
    cluster_id: str = Field(..., description="Cluster UUID")
    namespace: str = Field(..., description="Analyzed namespace")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")
    time_range_hours: int = Field(..., description="Analysis time range")
    total_workloads_analyzed: int = Field(..., description="Total workloads analyzed")
    idle_workloads: List[IdleWorkload] = Field(..., description="Detected idle workloads")
    total_potential_savings: float = Field(..., description="Total potential monthly savings")
    health_check_traffic_filtered: bool = Field(..., description="Whether health check traffic was filtered")


class AnalysisResponse(DataResponse):
    """Analysis response wrapper"""
    data: Union[ClusterAnalysisResult, IdleAnalysisResult]


# Optimization Responses
class OptimizationAction(BaseModel):
    """Individual optimization action"""
    action_type: str = Field(..., description="Type of optimization action")
    target_resource: str = Field(..., description="Target resource identifier")
    current_config: Dict[str, Any] = Field(..., description="Current resource configuration")
    recommended_config: Dict[str, Any] = Field(..., description="Recommended configuration")
    estimated_savings: float = Field(..., description="Estimated monthly cost savings")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")
    rollback_plan: Dict[str, Any] = Field(..., description="Rollback plan if needed")


class OptimizationResult(BaseModel):
    """Optimization execution result"""
    cluster_id: str = Field(..., description="Cluster UUID")
    optimization_id: str = Field(..., description="Optimization execution UUID")
    execution_timestamp: datetime = Field(..., description="Execution timestamp")
    dry_run: bool = Field(..., description="Whether this was a dry run")
    actions_planned: List[OptimizationAction] = Field(..., description="Planned optimization actions")
    actions_executed: List[Dict[str, Any]] = Field(..., description="Actually executed actions")
    total_estimated_savings: float = Field(..., description="Total estimated monthly savings")
    execution_status: str = Field(..., description="Execution status")
    rollback_available: bool = Field(..., description="Whether rollback is available")
    rollback_expires_at: Optional[datetime] = Field(None, description="Rollback expiration time")


class ZeroPodScalingResult(OptimizationResult):
    """Zero-pod scaling specific result"""
    scaled_workloads: List[str] = Field(..., description="List of scaled workloads")
    monitoring_enabled: bool = Field(..., description="Whether monitoring is enabled for rollback")
    traffic_threshold: float = Field(..., description="Traffic threshold for auto-scale-up")


class OptimizationResponse(DataResponse):
    """Optimization response wrapper"""
    data: OptimizationResult


# Reporting Responses
class CostBreakdown(BaseModel):
    """Cost breakdown information"""
    dimension: str = Field(..., description="Breakdown dimension (namespace, workload, etc.)")
    items: List[Dict[str, Any]] = Field(..., description="Cost breakdown items")
    total_cost: float = Field(..., description="Total cost for this dimension")
    currency: str = Field("USD", description="Currency code")


class ExecutiveReport(BaseModel):
    """Executive-level cost and optimization report"""
    report_id: str = Field(..., description="Report UUID")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    time_period_days: int = Field(..., description="Report time period")
    clusters_analyzed: List[str] = Field(..., description="Analyzed cluster IDs")
    
    # Cost Summary
    total_kubernetes_cost: float = Field(..., description="Total Kubernetes costs")
    potential_savings: float = Field(..., description="Total potential savings identified")
    actual_savings: float = Field(..., description="Actual savings achieved")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    
    # Breakdown
    cost_breakdown: List[CostBreakdown] = Field(..., description="Detailed cost breakdown")
    top_cost_centers: List[Dict[str, Any]] = Field(..., description="Top cost-generating resources")
    optimization_opportunities: List[Dict[str, Any]] = Field(..., description="Optimization opportunities")
    
    # Trends
    cost_trend: List[Dict[str, Any]] = Field(..., description="Cost trend over time")
    savings_trend: List[Dict[str, Any]] = Field(..., description="Savings trend over time")
    
    # Recommendations
    priority_recommendations: List[Dict[str, Any]] = Field(..., description="Priority optimization recommendations")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment for recommendations")


class ReportResponse(DataResponse):
    """Report response wrapper"""
    data: Union[ExecutiveReport, Dict[str, Any]]


# System Responses
class HealthCheckResponse(BaseResponse):
    """Health check response"""
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    database_status: str = Field(..., description="Database connection status")
    kubernetes_status: str = Field(..., description="Kubernetes connectivity status")
    ml_models_status: str = Field(..., description="ML models status")


class SystemInfoResponse(DataResponse):
    """System information response"""
    data: Dict[str, Any] = Field(..., description="System information")


# Error Responses
class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseResponse):
    """Error response model"""
    status: ResponseStatus = Field(ResponseStatus.ERROR)
    error_code: str = Field(..., description="Specific error code")
    errors: List[ErrorDetail] = Field(..., description="Detailed error information")
    suggestion: Optional[str] = Field(None, description="Suggested resolution")


class ValidationErrorResponse(ErrorResponse):
    """Validation error response"""
    error_code: str = Field("VALIDATION_ERROR")
    invalid_fields: List[str] = Field(..., description="List of invalid fields")