"""
UPID CLI API Server - Database Models
Enterprise-grade SQLAlchemy models for all UPID entities
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import enum

# Import shared Base class
from api_server.database.base import Base


def create_uuid_column(primary_key=False, nullable=True, foreign_key=None):
    """Create UUID column that works with both SQLite and PostgreSQL"""
    # For SQLite, use String(36) to store UUID as string
    # For PostgreSQL, use UUID type
    if foreign_key:
        return Column(
            String(36), 
            ForeignKey(foreign_key), 
            primary_key=primary_key, 
            nullable=nullable,
            default=lambda: str(uuid.uuid4()) if not primary_key else None
        )
    else:
        return Column(
            String(36), 
            primary_key=primary_key, 
            nullable=nullable,
            default=lambda: str(uuid.uuid4())
        )


# Enums for type safety
class ClusterStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning" 
    ERROR = "error"
    CONNECTING = "connecting"
    DISABLED = "disabled"


class CloudProvider(str, enum.Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "on-premise"


class OptimizationType(str, enum.Enum):
    ZERO_POD_SCALING = "zero_pod_scaling"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    COST_OPTIMIZATION = "cost_optimization"
    SCALING = "scaling"


class OptimizationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# Core Models
class User(Base):
    """User accounts and authentication"""
    __tablename__ = "users"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # User status and permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # User preferences and settings
    preferences = Column(JSON, default=dict)
    
    # Relationships
    clusters = relationship("Cluster", back_populates="owner", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="created_by")
    reports = relationship("Report", back_populates="created_by")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Cluster(Base):
    """Kubernetes clusters registered with UPID"""
    __tablename__ = "clusters"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    
    # Cluster connection details
    endpoint = Column(String(500))  # Kubernetes API endpoint
    kubeconfig = Column(Text)  # Encrypted kubeconfig
    
    # Cloud provider information
    cloud_provider = Column(SQLEnum(CloudProvider), default=CloudProvider.ON_PREMISE)
    region = Column(String(50))
    
    # Cluster metadata
    kubernetes_version = Column(String(20))
    node_count = Column(Integer, default=0)
    namespace_count = Column(Integer, default=0)
    pod_count = Column(Integer, default=0)
    
    # Status and health
    status = Column(SQLEnum(ClusterStatus), default=ClusterStatus.CONNECTING, nullable=False)
    health_score = Column(Float, default=0.0)  # 0-100 health score
    efficiency_score = Column(Float, default=0.0)  # 0-100 efficiency score
    
    # Cost information
    monthly_cost = Column(Float, default=0.0)
    projected_monthly_cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_analysis = Column(DateTime(timezone=True))
    
    # Configuration and tags
    tags = Column(JSON, default=dict)
    configuration = Column(JSON, default=dict)
    
    # Owner relationship
    owner_id = create_uuid_column(foreign_key="users.id", nullable=False)
    owner = relationship("User", back_populates="clusters")
    
    # Relationships
    workloads = relationship("Workload", back_populates="cluster", cascade="all, delete-orphan")
    metrics = relationship("ClusterMetric", back_populates="cluster", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="cluster")
    reports = relationship("Report", back_populates="cluster")
    
    # Indexes
    __table_args__ = (
        Index('idx_cluster_owner_name', 'owner_id', 'name'),
        Index('idx_cluster_status', 'status'),
        Index('idx_cluster_cloud_provider', 'cloud_provider'),
        UniqueConstraint('owner_id', 'name', name='uq_cluster_owner_name')
    )
    
    def __repr__(self):
        return f"<Cluster(name='{self.name}', status='{self.status}')>"


class Workload(Base):
    """Kubernetes workloads (Deployments, StatefulSets, etc.)"""
    __tablename__ = "workloads"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    cluster_id = create_uuid_column(foreign_key="clusters.id", nullable=False)
    
    # Workload identification
    name = Column(String(253), nullable=False)  # Kubernetes name limit
    namespace = Column(String(253), nullable=False, default="default")
    workload_type = Column(String(50), nullable=False)  # Deployment, StatefulSet, etc.
    
    # Workload status
    status = Column(String(50), default="Unknown")
    replicas = Column(Integer, default=1)
    ready_replicas = Column(Integer, default=0)
    
    # Resource specifications
    cpu_request = Column(String(20))  # e.g., "500m"
    cpu_limit = Column(String(20))    # e.g., "1000m"
    memory_request = Column(String(20))  # e.g., "512Mi"
    memory_limit = Column(String(20))    # e.g., "1Gi"
    
    # Labels and annotations
    labels = Column(JSON, default=dict)
    annotations = Column(JSON, default=dict)
    
    # UPID analysis data
    is_idle = Column(Boolean, default=False)
    idle_confidence = Column(Float, default=0.0)  # 0.0-1.0
    last_traffic_seen = Column(DateTime(timezone=True))
    health_check_filtered = Column(Boolean, default=False)
    
    # Cost information
    estimated_monthly_cost = Column(Float, default=0.0)
    potential_monthly_savings = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_analyzed = Column(DateTime(timezone=True))
    
    # Relationships
    cluster = relationship("Cluster", back_populates="workloads")
    metrics = relationship("WorkloadMetric", back_populates="workload", cascade="all, delete-orphan")
    optimization_actions = relationship("OptimizationAction", back_populates="workload")
    
    # Indexes
    __table_args__ = (
        Index('idx_workload_cluster_namespace', 'cluster_id', 'namespace'),
        Index('idx_workload_name', 'name'),
        Index('idx_workload_idle', 'is_idle'),
        UniqueConstraint('cluster_id', 'namespace', 'name', name='uq_workload_cluster_ns_name')
    )
    
    def __repr__(self):
        return f"<Workload(name='{self.name}', namespace='{self.namespace}', type='{self.workload_type}')>"


class ClusterMetric(Base):
    """Time-series metrics for clusters"""
    __tablename__ = "cluster_metrics"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    cluster_id = create_uuid_column(foreign_key="clusters.id", nullable=False)
    
    # Timestamp for time-series data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Resource utilization metrics
    cpu_usage_cores = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_bytes = Column(Integer, default=0)
    memory_usage_percent = Column(Float, default=0.0)
    
    # Network metrics
    network_rx_bytes = Column(Integer, default=0)
    network_tx_bytes = Column(Integer, default=0)
    
    # Storage metrics
    storage_usage_bytes = Column(Integer, default=0)
    storage_available_bytes = Column(Integer, default=0)
    
    # Pod and node counts
    node_count = Column(Integer, default=0)
    pod_count = Column(Integer, default=0)
    namespace_count = Column(Integer, default=0)
    
    # Cost metrics
    hourly_cost = Column(Float, default=0.0)
    
    # Relationships
    cluster = relationship("Cluster", back_populates="metrics")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_cluster_metrics_time', 'cluster_id', 'timestamp'),
        Index('idx_cluster_metrics_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<ClusterMetric(cluster_id='{self.cluster_id}', timestamp='{self.timestamp}')>"


class WorkloadMetric(Base):
    """Time-series metrics for individual workloads"""
    __tablename__ = "workload_metrics"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    workload_id = create_uuid_column(foreign_key="workloads.id", nullable=False)
    
    # Timestamp for time-series data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Resource utilization metrics
    cpu_usage_cores = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_bytes = Column(Integer, default=0)
    memory_usage_percent = Column(Float, default=0.0)
    
    # Network metrics
    network_rx_bytes = Column(Integer, default=0)
    network_tx_bytes = Column(Integer, default=0)
    
    # Request metrics (for traffic analysis)
    request_count = Column(Integer, default=0)
    health_check_requests = Column(Integer, default=0)  # Health Check Illusion filtering
    business_requests = Column(Integer, default=0)
    
    # Response time metrics
    avg_response_time_ms = Column(Float, default=0.0)
    p95_response_time_ms = Column(Float, default=0.0)
    
    # Relationships
    workload = relationship("Workload", back_populates="metrics")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_workload_metrics_time', 'workload_id', 'timestamp'),
        Index('idx_workload_metrics_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<WorkloadMetric(workload_id='{self.workload_id}', timestamp='{self.timestamp}')>"


class OptimizationRun(Base):
    """Optimization execution runs and their results"""
    __tablename__ = "optimization_runs"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    cluster_id = create_uuid_column(foreign_key="clusters.id", nullable=False)
    created_by_id = create_uuid_column(foreign_key="users.id", nullable=False)
    
    # Run metadata
    optimization_type = Column(SQLEnum(OptimizationType), nullable=False)
    status = Column(SQLEnum(OptimizationStatus), default=OptimizationStatus.PENDING, nullable=False)
    
    # Execution parameters
    target_namespace = Column(String(253), default="default")
    dry_run = Column(Boolean, default=True, nullable=False)
    safety_checks_enabled = Column(Boolean, default=True, nullable=False)
    
    # Results
    actions_planned = Column(Integer, default=0)
    actions_executed = Column(Integer, default=0)
    actions_successful = Column(Integer, default=0)
    actions_failed = Column(Integer, default=0)
    
    # Financial impact
    estimated_monthly_savings = Column(Float, default=0.0)
    actual_monthly_savings = Column(Float, default=0.0)
    
    # Rollback information
    rollback_available = Column(Boolean, default=False)
    rollback_expires_at = Column(DateTime(timezone=True))
    rollback_data = Column(JSON)  # Stores rollback configuration
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Execution details
    configuration = Column(JSON, default=dict)
    execution_log = Column(Text)  # Detailed execution log
    error_message = Column(Text)
    
    # Relationships
    cluster = relationship("Cluster", back_populates="optimization_runs")
    created_by = relationship("User", back_populates="optimization_runs")
    actions = relationship("OptimizationAction", back_populates="optimization_run", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_optimization_cluster_type', 'cluster_id', 'optimization_type'),
        Index('idx_optimization_status', 'status'),
        Index('idx_optimization_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<OptimizationRun(type='{self.optimization_type}', status='{self.status}')>"


class OptimizationAction(Base):
    """Individual actions within an optimization run"""
    __tablename__ = "optimization_actions"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    optimization_run_id = create_uuid_column(foreign_key="optimization_runs.id", nullable=False)
    workload_id = create_uuid_column(foreign_key="workloads.id", nullable=False)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # e.g., "scale_to_zero", "update_resources"
    target_resource = Column(String(500), nullable=False)  # Resource identifier
    
    # Configuration changes
    original_configuration = Column(JSON, default=dict)
    target_configuration = Column(JSON, default=dict)
    applied_configuration = Column(JSON, default=dict)
    
    # Execution details
    execution_order = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, executing, completed, failed
    
    # Impact
    estimated_savings = Column(Float, default=0.0)
    risk_level = Column(String(20), default="low")  # low, medium, high
    
    # Rollback information
    rollback_configuration = Column(JSON, default=dict)
    rollback_successful = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    executed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Execution details
    execution_log = Column(Text)
    error_message = Column(Text)
    
    # Relationships
    optimization_run = relationship("OptimizationRun", back_populates="actions")
    workload = relationship("Workload", back_populates="optimization_actions")
    
    # Indexes
    __table_args__ = (
        Index('idx_action_run_order', 'optimization_run_id', 'execution_order'),
        Index('idx_action_workload', 'workload_id'),
        Index('idx_action_status', 'status'),
    )
    
    def __repr__(self):
        return f"<OptimizationAction(type='{self.action_type}', status='{self.status}')>"


class Report(Base):
    """Generated reports and business intelligence"""
    __tablename__ = "reports"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    cluster_id = create_uuid_column(foreign_key="clusters.id", nullable=False)
    created_by_id = create_uuid_column(foreign_key="users.id", nullable=False)
    
    # Report metadata
    report_type = Column(String(100), nullable=False)  # executive, custom, cost_trends, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Time range
    time_range_start = Column(DateTime(timezone=True), nullable=False)
    time_range_end = Column(DateTime(timezone=True), nullable=False)
    
    # Report data
    report_data = Column(JSON, nullable=False)  # Complete report JSON
    summary_metrics = Column(JSON, default=dict)  # Key metrics for quick access
    
    # Configuration
    configuration = Column(JSON, default=dict)  # Report generation parameters
    format = Column(String(20), default="json")  # json, pdf, excel, csv
    
    # Status
    status = Column(String(50), default="generated")  # generating, generated, failed
    file_path = Column(String(500))  # Path to generated file (if applicable)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))  # When report/file expires
    
    # Relationships
    cluster = relationship("Cluster", back_populates="reports")
    created_by = relationship("User", back_populates="reports")
    
    # Indexes
    __table_args__ = (
        Index('idx_report_cluster_type', 'cluster_id', 'report_type'),
        Index('idx_report_created', 'created_at'),
        Index('idx_report_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<Report(type='{self.report_type}', title='{self.title}')>"


class AuditLog(Base):
    """Audit trail for all system actions"""
    __tablename__ = "audit_logs"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    user_id = create_uuid_column(foreign_key="users.id", nullable=True)
    cluster_id = create_uuid_column(foreign_key="clusters.id", nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False)  # login, create_cluster, run_optimization, etc.
    resource_type = Column(String(100))  # cluster, workload, optimization_run, etc.
    resource_id = create_uuid_column(nullable=True)
    
    # Request details
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(String(500))
    request_id = Column(String(100))
    
    # Action outcome
    status = Column(String(20), nullable=False)  # success, failure, error
    details = Column(JSON, default=dict)  # Additional context
    error_message = Column(Text)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
        Index('idx_audit_cluster_time', 'cluster_id', 'timestamp'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', status='{self.status}')>"


class SystemConfiguration(Base):
    """System-wide configuration and feature flags"""
    __tablename__ = "system_configuration"
    
    id = create_uuid_column(primary_key=True, nullable=False)
    
    # Configuration key-value
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    
    # Metadata
    description = Column(Text)
    category = Column(String(50), default="general")  # general, security, ml, optimization
    
    # Validation
    value_type = Column(String(20), default="string")  # string, integer, float, boolean, json
    allowed_values = Column(JSON)  # For enum-like configurations
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_config_category', 'category'),
    )
    
    def __repr__(self):
        return f"<SystemConfiguration(key='{self.key}', category='{self.category}')>"