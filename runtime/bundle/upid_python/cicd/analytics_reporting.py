#!/usr/bin/env python3
"""
UPID CLI - CI/CD Analytics & Reporting
Phase 6: Platform Integration - Task 6.4
Enterprise-grade CI/CD analytics and reporting with deployment metrics, cost tracking, and executive dashboards
"""

import logging
import asyncio
import json
import yaml
import base64
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import aiohttp
import subprocess
import tempfile
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor

from .pipeline_manager import PipelineManager
from .deployment_validator import DeploymentValidator
from .enhanced_deployment_validator import EnhancedDeploymentValidator

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Analytics metric types"""
    DEPLOYMENT_SUCCESS = "deployment_success"
    COST_IMPACT = "cost_impact"
    PERFORMANCE_TREND = "performance_trend"
    SECURITY_COMPLIANCE = "security_compliance"
    RESOURCE_UTILIZATION = "resource_utilization"
    CUSTOM = "custom"


class ReportType(str, Enum):
    """Report types"""
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


@dataclass
class DeploymentMetrics:
    """Deployment success metrics"""
    deployment_name: str
    namespace: str
    cluster_id: str
    deployment_time: datetime
    success: bool
    duration_seconds: float
    validation_passed: bool
    cost_impact: float
    performance_score: float
    security_score: float
    rollback_count: int = 0
    failure_reason: Optional[str] = None


@dataclass
class CostImpactMetrics:
    """Cost impact tracking metrics"""
    deployment_name: str
    cluster_id: str
    pre_deployment_cost: float
    post_deployment_cost: float
    cost_change_percentage: float
    monthly_savings: float
    roi_percentage: float
    cost_breakdown: Dict[str, float] = None
    
    def __post_init__(self):
        if self.cost_breakdown is None:
            self.cost_breakdown = {}


@dataclass
class PerformanceTrendMetrics:
    """Performance trend analysis metrics"""
    deployment_name: str
    cluster_id: str
    measurement_date: datetime
    cpu_utilization: float
    memory_utilization: float
    response_time_ms: float
    throughput_rps: float
    error_rate_percentage: float
    availability_percentage: float


@dataclass
class ExecutiveReportConfig:
    """Executive report configuration"""
    report_period_days: int = 30
    include_cost_analysis: bool = True
    include_performance_trends: bool = True
    include_security_metrics: bool = True
    include_roi_analysis: bool = True
    chart_format: str = "png"
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["pdf", "html", "json"]


class DeploymentAnalytics:
    """Deployment success analytics"""
    
    def __init__(self):
        self.deployment_history: List[DeploymentMetrics] = []
        self.analytics_cache: Dict[str, Any] = {}
    
    async def record_deployment(self, metrics: DeploymentMetrics):
        """Record deployment metrics"""
        self.deployment_history.append(metrics)
        logger.info(f"📊 Recorded deployment metrics for: {metrics.deployment_name}")
    
    async def get_deployment_success_rate(self, cluster_id: Optional[str] = None, 
                                        days: int = 30) -> Dict[str, Any]:
        """Get deployment success rate"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if cluster_id:
            deployments = [d for d in self.deployment_history 
                         if d.cluster_id == cluster_id and d.deployment_time >= cutoff_date]
        else:
            deployments = [d for d in self.deployment_history 
                         if d.deployment_time >= cutoff_date]
        
        if not deployments:
            return {"success_rate": 0.0, "total_deployments": 0, "successful_deployments": 0}
        
        successful = sum(1 for d in deployments if d.success)
        total = len(deployments)
        success_rate = (successful / total) * 100
        
        return {
            "success_rate": success_rate,
            "total_deployments": total,
            "successful_deployments": successful,
            "failed_deployments": total - successful,
            "period_days": days
        }


class CostImpactAnalytics:
    """Cost impact tracking analytics"""
    
    def __init__(self):
        self.cost_history: List[CostImpactMetrics] = []
        self.cost_cache: Dict[str, Any] = {}
    
    async def record_cost_impact(self, metrics: CostImpactMetrics):
        """Record cost impact metrics"""
        self.cost_history.append(metrics)
        logger.info(f"💰 Recorded cost impact for: {metrics.deployment_name}")
    
    async def get_cost_savings_summary(self, cluster_id: Optional[str] = None, 
                                     days: int = 30) -> Dict[str, Any]:
        """Get cost savings summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if cluster_id:
            costs = [c for c in self.cost_history 
                    if c.cluster_id == cluster_id and c.measurement_date >= cutoff_date]
        else:
            costs = [c for c in self.cost_history 
                    if c.measurement_date >= cutoff_date]
        
        if not costs:
            return {"total_savings": 0.0, "avg_roi": 0.0, "deployments_analyzed": 0}
        
        total_savings = sum(c.monthly_savings for c in costs)
        avg_roi = sum(c.roi_percentage for c in costs) / len(costs)
        
        return {
            "total_savings": total_savings,
            "avg_roi": avg_roi,
            "deployments_analyzed": len(costs),
            "period_days": days
        }


class PerformanceTrendAnalytics:
    """Performance trend analysis"""
    
    def __init__(self):
        self.performance_history: List[PerformanceTrendMetrics] = []
        self.performance_cache: Dict[str, Any] = {}
    
    async def record_performance_metrics(self, metrics: PerformanceTrendMetrics):
        """Record performance metrics"""
        self.performance_history.append(metrics)
        logger.info(f"📈 Recorded performance metrics for: {metrics.deployment_name}")
    
    async def get_performance_summary(self, cluster_id: Optional[str] = None, 
                                    days: int = 30) -> Dict[str, Any]:
        """Get performance summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if cluster_id:
            metrics = [p for p in self.performance_history 
                      if p.cluster_id == cluster_id and p.measurement_date >= cutoff_date]
        else:
            metrics = [p for p in self.performance_history 
                      if p.measurement_date >= cutoff_date]
        
        if not metrics:
            return {"avg_cpu": 0.0, "avg_memory": 0.0, "avg_response_time": 0.0, "avg_availability": 0.0}
        
        avg_cpu = sum(p.cpu_utilization for p in metrics) / len(metrics)
        avg_memory = sum(p.memory_utilization for p in metrics) / len(metrics)
        avg_response_time = sum(p.response_time_ms for p in metrics) / len(metrics)
        avg_availability = sum(p.availability_percentage for p in metrics) / len(metrics)
        
        return {
            "avg_cpu": avg_cpu,
            "avg_memory": avg_memory,
            "avg_response_time": avg_response_time,
            "avg_availability": avg_availability,
            "measurements_count": len(metrics),
            "period_days": days
        }


class CICDAnalyticsReporting:
    """
    CI/CD Analytics and Reporting for UPID CLI
    
    Features:
    - Deployment success metrics
    - Cost impact tracking
    - Performance trend analysis
    - Executive reporting
    - Chart generation
    - Report export
    """
    
    def __init__(self, pipeline_manager: PipelineManager, 
                 deployment_validator: DeploymentValidator,
                 enhanced_validator: EnhancedDeploymentValidator):
        self.pipeline_manager = pipeline_manager
        self.deployment_validator = deployment_validator
        self.enhanced_validator = enhanced_validator
        
        # Analytics components
        self.deployment_analytics = DeploymentAnalytics()
        self.cost_analytics = CostImpactAnalytics()
        self.performance_analytics = PerformanceTrendAnalytics()
        
        # Configuration
        self.reporting_configs: Dict[str, ExecutiveReportConfig] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        logger.info("🔧 Initializing CI/CD Analytics and Reporting")
    
    async def initialize(self) -> bool:
        """Initialize CI/CD Analytics and Reporting"""
        try:
            logger.info("🚀 Initializing CI/CD Analytics and Reporting...")
            
            # Setup default reporting configurations
            await self._setup_default_configs()
            
            logger.info("✅ CI/CD Analytics and Reporting initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CI/CD Analytics and Reporting: {e}")
            return False
    
    async def _setup_default_configs(self):
        """Setup default reporting configurations"""
        logger.info("🔧 Setting up default reporting configurations...")
        
        # Default executive report config
        default_config = ExecutiveReportConfig(
            report_period_days=30,
            include_cost_analysis=True,
            include_performance_trends=True,
            include_security_metrics=True,
            include_roi_analysis=True
        )
        
        self.reporting_configs["default"] = default_config
        logger.info("✅ Setup default reporting configurations")
    
    async def record_deployment_metrics(self, deployment_name: str, namespace: str, 
                                      cluster_id: str, success: bool, duration_seconds: float,
                                      validation_passed: bool, cost_impact: float = 0.0,
                                      performance_score: float = 0.0, security_score: float = 0.0,
                                      rollback_count: int = 0, failure_reason: Optional[str] = None):
        """Record deployment metrics"""
        try:
            metrics = DeploymentMetrics(
                deployment_name=deployment_name,
                namespace=namespace,
                cluster_id=cluster_id,
                deployment_time=datetime.now(),
                success=success,
                duration_seconds=duration_seconds,
                validation_passed=validation_passed,
                cost_impact=cost_impact,
                performance_score=performance_score,
                security_score=security_score,
                rollback_count=rollback_count,
                failure_reason=failure_reason
            )
            
            await self.deployment_analytics.record_deployment(metrics)
            logger.info(f"📊 Recorded deployment metrics for: {deployment_name}")
            
        except Exception as e:
            logger.error(f"Failed to record deployment metrics: {e}")
    
    async def record_cost_impact(self, deployment_name: str, cluster_id: str,
                               pre_deployment_cost: float, post_deployment_cost: float,
                               monthly_savings: float, roi_percentage: float,
                               cost_breakdown: Optional[Dict[str, float]] = None):
        """Record cost impact metrics"""
        try:
            cost_change = post_deployment_cost - pre_deployment_cost
            cost_change_percentage = (cost_change / pre_deployment_cost * 100) if pre_deployment_cost > 0 else 0
            
            metrics = CostImpactMetrics(
                deployment_name=deployment_name,
                cluster_id=cluster_id,
                pre_deployment_cost=pre_deployment_cost,
                post_deployment_cost=post_deployment_cost,
                cost_change_percentage=cost_change_percentage,
                monthly_savings=monthly_savings,
                roi_percentage=roi_percentage,
                cost_breakdown=cost_breakdown
            )
            
            await self.cost_analytics.record_cost_impact(metrics)
            logger.info(f"💰 Recorded cost impact for: {deployment_name}")
            
        except Exception as e:
            logger.error(f"Failed to record cost impact: {e}")
    
    async def record_performance_metrics(self, deployment_name: str, cluster_id: str,
                                       cpu_utilization: float, memory_utilization: float,
                                       response_time_ms: float, throughput_rps: float,
                                       error_rate_percentage: float, availability_percentage: float):
        """Record performance metrics"""
        try:
            metrics = PerformanceTrendMetrics(
                deployment_name=deployment_name,
                cluster_id=cluster_id,
                measurement_date=datetime.now(),
                cpu_utilization=cpu_utilization,
                memory_utilization=memory_utilization,
                response_time_ms=response_time_ms,
                throughput_rps=throughput_rps,
                error_rate_percentage=error_rate_percentage,
                availability_percentage=availability_percentage
            )
            
            await self.performance_analytics.record_performance_metrics(metrics)
            logger.info(f"📈 Recorded performance metrics for: {deployment_name}")
            
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {e}")
    
    async def generate_executive_report(self, cluster_id: Optional[str] = None,
                                      config_name: str = "default") -> Dict[str, Any]:
        """Generate executive report"""
        try:
            config = self.reporting_configs.get(config_name)
            if not config:
                config = ExecutiveReportConfig()
            
            # Get deployment success metrics
            deployment_success = await self.deployment_analytics.get_deployment_success_rate(
                cluster_id, config.report_period_days
            )
            
            # Get cost impact metrics
            cost_summary = await self.cost_analytics.get_cost_savings_summary(
                cluster_id, config.report_period_days
            )
            
            # Get performance metrics
            performance_summary = await self.performance_analytics.get_performance_summary(
                cluster_id, config.report_period_days
            )
            
            report = {
                "report_type": "executive",
                "generated_at": datetime.now().isoformat(),
                "period_days": config.report_period_days,
                "cluster_id": cluster_id,
                "deployment_metrics": deployment_success,
                "cost_metrics": cost_summary,
                "performance_metrics": performance_summary
            }
            
            logger.info(f"📊 Generated executive report for cluster: {cluster_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate executive report: {e}")
            return {"error": str(e)}
    
    async def get_analytics_summary(self, cluster_id: Optional[str] = None, 
                                   days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            # Get deployment success metrics
            deployment_success = await self.deployment_analytics.get_deployment_success_rate(
                cluster_id, days
            )
            
            # Get cost impact metrics
            cost_summary = await self.cost_analytics.get_cost_savings_summary(
                cluster_id, days
            )
            
            # Get performance metrics
            performance_summary = await self.performance_analytics.get_performance_summary(
                cluster_id, days
            )
            
            return {
                "deployment_metrics": deployment_success,
                "cost_metrics": cost_summary,
                "performance_metrics": performance_summary,
                "period_days": days,
                "cluster_id": cluster_id,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {"error": str(e)}
    
    async def get_analytics_status(self) -> Dict[str, Any]:
        """Get analytics and reporting status"""
        return {
            "deployment_metrics_count": len(self.deployment_analytics.deployment_history),
            "cost_metrics_count": len(self.cost_analytics.cost_history),
            "performance_metrics_count": len(self.performance_analytics.performance_history),
            "reporting_configs_count": len(self.reporting_configs)
        }
    
    async def shutdown(self):
        """Shutdown CI/CD Analytics and Reporting"""
        logger.info("🛑 Shutting down CI/CD Analytics and Reporting...")
        
        self.executor.shutdown(wait=True)
        logger.info("✅ CI/CD Analytics and Reporting shutdown complete") 