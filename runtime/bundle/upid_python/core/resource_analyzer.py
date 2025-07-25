"""
UPID CLI - Resource Analysis Engine
Enterprise-grade Kubernetes resource analysis and optimization for UPID platform
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
from enum import Enum

from .k8s_client import KubernetesClient, NodeInfo, PodInfo
from .metrics_collector import MetricsCollector, NodeMetrics, PodMetrics, ClusterMetrics, ResourceEfficiency

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimization recommendations"""
    ZERO_POD_SCALING = "zero_pod_scaling"
    RESOURCE_RIGHT_SIZING = "resource_right_sizing"
    NODE_CONSOLIDATION = "node_consolidation"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_OPTIMIZATION = "security_optimization"


class ConfidenceLevel(Enum):
    """Confidence levels for recommendations"""
    HIGH = "high"        # 90%+ confidence
    MEDIUM = "medium"    # 70-90% confidence
    LOW = "low"         # 50-70% confidence


@dataclass
class IdleWorkload:
    """Idle or underutilized workload identification"""
    name: str
    namespace: str
    workload_type: str  # deployment, statefulset, daemonset, job
    idle_duration_hours: float
    cpu_usage_percent: float
    memory_usage_percent: float
    network_activity_bytes: int
    last_activity: datetime
    confidence: ConfidenceLevel
    potential_savings_monthly: float
    recommendation: str
    risk_assessment: str


@dataclass
class ResourceOptimization:
    """Resource optimization recommendation"""
    resource_type: str  # cpu, memory, storage
    workload_name: str
    namespace: str
    current_request: str
    current_limit: str
    recommended_request: str
    recommended_limit: str
    potential_savings_percent: float
    potential_savings_monthly: float
    confidence: ConfidenceLevel
    justification: str
    implementation_steps: List[str]


@dataclass
class NodeOptimization:
    """Node-level optimization recommendation"""
    node_name: str
    node_type: str
    current_utilization_percent: float
    optimization_type: OptimizationType
    recommendation: str
    potential_cost_savings_monthly: float
    affected_workloads: List[str]
    migration_plan: List[str]
    risk_level: str
    confidence: ConfidenceLevel


@dataclass
class CostBreakdown:
    """Detailed cost analysis and breakdown"""
    cluster_name: str
    total_monthly_cost: float
    compute_cost: float
    storage_cost: float
    network_cost: float
    waste_cost: float
    optimization_potential: float
    cost_per_namespace: Dict[str, float]
    cost_per_workload: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class EfficiencyReport:
    """Comprehensive efficiency analysis report"""
    cluster_name: str
    overall_efficiency_score: float
    resource_efficiency: List[ResourceEfficiency]
    idle_workloads: List[IdleWorkload]
    optimization_opportunities: List[ResourceOptimization]
    node_optimizations: List[NodeOptimization]
    cost_analysis: CostBreakdown
    priority_actions: List[str]
    estimated_monthly_savings: float
    implementation_complexity: str
    timestamp: datetime


class ResourceAnalyzer:
    """
    Enterprise-grade Kubernetes resource analysis and optimization engine
    
    Provides comprehensive analysis and optimization recommendations:
    - Idle workload detection with confidence scoring
    - Resource right-sizing recommendations
    - Node consolidation opportunities
    - Cost optimization strategies
    - Performance improvement suggestions
    - Security and compliance optimizations
    """
    
    def __init__(self, k8s_client: KubernetesClient, metrics_collector: MetricsCollector):
        """
        Initialize resource analyzer
        
        Args:
            k8s_client: Connected Kubernetes client instance
            metrics_collector: Metrics collector instance
        """
        self.k8s_client = k8s_client
        self.metrics_collector = metrics_collector
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(minutes=15)  # Cache analysis for 15 minutes
        
        # Default cost assumptions (can be configured per cluster)
        self.default_costs = {
            "cpu_core_per_hour": 0.05,      # $0.05 per CPU core per hour
            "memory_gb_per_hour": 0.01,     # $0.01 per GB memory per hour
            "storage_gb_per_hour": 0.0001,  # $0.0001 per GB storage per hour
            "network_gb": 0.01              # $0.01 per GB network transfer
        }
        
        logger.info("🔍 Initializing UPID resource analyzer")
    
    async def analyze_idle_workloads(
        self, 
        confidence_threshold: float = 0.7,
        observation_hours: int = 24
    ) -> List[IdleWorkload]:
        """
        Identify idle or underutilized workloads
        
        Args:
            confidence_threshold: Minimum confidence level (0.0-1.0)
            observation_hours: Hours of data to analyze
            
        Returns:
            List of IdleWorkload objects with optimization recommendations
        """
        try:
            logger.info(f"🔍 Analyzing idle workloads with {confidence_threshold:.0%} confidence threshold...")
            
            # Get current metrics
            pod_metrics = await self.metrics_collector.collect_pod_metrics()
            cluster_metrics = await self.metrics_collector.collect_cluster_metrics()
            
            idle_workloads = []
            
            # Group pods by workload (deployment, statefulset, etc.)
            workload_pods = self._group_pods_by_workload(pod_metrics)
            
            for workload_name, pods in workload_pods.items():
                try:
                    # Analyze workload utilization
                    analysis = await self._analyze_workload_utilization(
                        workload_name, 
                        pods, 
                        observation_hours
                    )
                    
                    if analysis["confidence"] >= confidence_threshold:
                        idle_workload = IdleWorkload(
                            name=analysis["name"],
                            namespace=analysis["namespace"],
                            workload_type=analysis["type"],
                            idle_duration_hours=analysis["idle_hours"],
                            cpu_usage_percent=analysis["cpu_usage"],
                            memory_usage_percent=analysis["memory_usage"],
                            network_activity_bytes=analysis["network_activity"],
                            last_activity=analysis["last_activity"],
                            confidence=self._get_confidence_level(analysis["confidence"]),
                            potential_savings_monthly=analysis["potential_savings"],
                            recommendation=analysis["recommendation"],
                            risk_assessment=analysis["risk"]
                        )
                        
                        idle_workloads.append(idle_workload)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to analyze workload {workload_name}: {e}")
                    continue
            
            # Sort by potential savings
            idle_workloads.sort(key=lambda x: x.potential_savings_monthly, reverse=True)
            
            logger.info(f"✅ Identified {len(idle_workloads)} idle workloads with potential savings")
            return idle_workloads
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze idle workloads: {e}")
            return []
    
    async def calculate_resource_efficiency(self) -> EfficiencyReport:
        """
        Calculate comprehensive resource efficiency metrics
        
        Returns:
            EfficiencyReport with detailed analysis and recommendations
        """
        try:
            logger.info("📊 Calculating comprehensive resource efficiency...")
            
            # Check cache first
            cache_key = "efficiency_report"
            if self._is_cache_valid(cache_key):
                logger.debug("📦 Using cached efficiency report")
                return self.analysis_cache[cache_key]["data"]
            
            # Collect base metrics
            cluster_metrics = await self.metrics_collector.collect_cluster_metrics()
            resource_efficiency = await self.metrics_collector.analyze_resource_efficiency()
            
            # Analyze different optimization opportunities
            idle_workloads = await self.analyze_idle_workloads()
            optimization_opportunities = await self._identify_optimization_opportunities()
            node_optimizations = await self._analyze_node_optimizations()
            cost_analysis = await self.cost_analysis()
            
            # Calculate overall efficiency score
            overall_efficiency = self._calculate_overall_efficiency(
                cluster_metrics, resource_efficiency, idle_workloads
            )
            
            # Generate priority actions
            priority_actions = self._generate_priority_actions(
                idle_workloads, optimization_opportunities, node_optimizations
            )
            
            # Calculate estimated savings
            estimated_savings = sum([
                iw.potential_savings_monthly for iw in idle_workloads
            ]) + sum([
                opt.potential_savings_monthly for opt in optimization_opportunities
            ]) + sum([
                node.potential_cost_savings_monthly for node in node_optimizations
            ])
            
            # Determine implementation complexity
            complexity = self._assess_implementation_complexity(
                len(idle_workloads), len(optimization_opportunities), len(node_optimizations)
            )
            
            report = EfficiencyReport(
                cluster_name=cluster_metrics.cluster_name,
                overall_efficiency_score=overall_efficiency,
                resource_efficiency=resource_efficiency,
                idle_workloads=idle_workloads,
                optimization_opportunities=optimization_opportunities,
                node_optimizations=node_optimizations,
                cost_analysis=cost_analysis,
                priority_actions=priority_actions,
                estimated_monthly_savings=estimated_savings,
                implementation_complexity=complexity,
                timestamp=datetime.utcnow()
            )
            
            # Cache the result
            self._cache_analysis(cache_key, report)
            
            logger.info(f"✅ Generated efficiency report: {overall_efficiency:.1f}% efficiency, ${estimated_savings:.2f}/month potential savings")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate resource efficiency: {e}")
            # Return empty report on error
            return EfficiencyReport(
                cluster_name="unknown",
                overall_efficiency_score=0.0,
                resource_efficiency=[],
                idle_workloads=[],
                optimization_opportunities=[],
                node_optimizations=[],
                cost_analysis=CostBreakdown(
                    cluster_name="unknown",
                    total_monthly_cost=0.0,
                    compute_cost=0.0,
                    storage_cost=0.0,
                    network_cost=0.0,
                    waste_cost=0.0,
                    optimization_potential=0.0,
                    cost_per_namespace={},
                    cost_per_workload={},
                    recommendations=[],
                    timestamp=datetime.utcnow()
                ),
                priority_actions=[],
                estimated_monthly_savings=0.0,
                implementation_complexity="unknown",
                timestamp=datetime.utcnow()
            )
    
    async def identify_optimization_opportunities(self) -> List[ResourceOptimization]:
        """
        Identify specific resource optimization opportunities
        
        Returns:
            List of ResourceOptimization recommendations
        """
        try:
            logger.info("🎯 Identifying optimization opportunities...")
            
            pod_metrics = await self.metrics_collector.collect_pod_metrics()
            optimizations = []
            
            for pod in pod_metrics:
                try:
                    # Analyze CPU optimization
                    cpu_opt = await self._analyze_cpu_optimization(pod)
                    if cpu_opt:
                        optimizations.append(cpu_opt)
                    
                    # Analyze memory optimization
                    memory_opt = await self._analyze_memory_optimization(pod)
                    if memory_opt:
                        optimizations.append(memory_opt)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to analyze pod {pod.pod_name}: {e}")
                    continue
            
            # Sort by potential savings
            optimizations.sort(key=lambda x: x.potential_savings_monthly, reverse=True)
            
            logger.info(f"✅ Identified {len(optimizations)} optimization opportunities")
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Failed to identify optimization opportunities: {e}")
            return []
    
    async def cost_analysis(self) -> CostBreakdown:
        """
        Perform detailed cost analysis and breakdown
        
        Returns:
            CostBreakdown with comprehensive cost information
        """
        try:
            logger.info("💰 Performing cost analysis...")
            
            cluster_metrics = await self.metrics_collector.collect_cluster_metrics()
            pod_metrics = await self.metrics_collector.collect_pod_metrics()
            
            # Calculate compute costs
            compute_cost = (
                cluster_metrics.cpu_capacity_cores * self.default_costs["cpu_core_per_hour"] * 24 * 30 +
                (cluster_metrics.memory_capacity_bytes / (1024**3)) * self.default_costs["memory_gb_per_hour"] * 24 * 30
            )
            
            # Estimate storage costs (simplified)
            storage_cost = cluster_metrics.total_pods * 20 * self.default_costs["storage_gb_per_hour"] * 24 * 30  # 20GB avg per pod
            
            # Estimate network costs (simplified)
            network_cost = cluster_metrics.total_pods * 10 * self.default_costs["network_gb"] * 30  # 10GB avg per pod per month
            
            # Calculate waste costs
            total_cpu_requests = sum(pm.cpu_requests_millicores for pm in pod_metrics) / 1000.0
            total_memory_requests = sum(pm.memory_requests_bytes for pm in pod_metrics) / (1024**3)
            
            cpu_waste = max(0, cluster_metrics.cpu_capacity_cores - total_cpu_requests)
            memory_waste = max(0, (cluster_metrics.memory_capacity_bytes / (1024**3)) - total_memory_requests)
            
            waste_cost = (
                cpu_waste * self.default_costs["cpu_core_per_hour"] * 24 * 30 +
                memory_waste * self.default_costs["memory_gb_per_hour"] * 24 * 30
            )
            
            total_cost = compute_cost + storage_cost + network_cost
            
            # Calculate cost per namespace
            namespace_costs = defaultdict(float)
            workload_costs = defaultdict(float)
            
            for pod in pod_metrics:
                pod_cpu_cost = (pod.cpu_requests_millicores / 1000.0) * self.default_costs["cpu_core_per_hour"] * 24 * 30
                pod_memory_cost = (pod.memory_requests_bytes / (1024**3)) * self.default_costs["memory_gb_per_hour"] * 24 * 30
                pod_total_cost = pod_cpu_cost + pod_memory_cost
                
                namespace_costs[pod.namespace] += pod_total_cost
                workload_costs[f"{pod.namespace}/{pod.pod_name}"] = pod_total_cost
            
            # Generate cost optimization recommendations
            recommendations = []
            if waste_cost > total_cost * 0.2:
                recommendations.append("High resource waste detected - consider right-sizing workloads")
            if len(namespace_costs) > 10 and max(namespace_costs.values()) > total_cost * 0.5:
                recommendations.append("Cost concentration in single namespace - review resource allocation")
            
            return CostBreakdown(
                cluster_name=cluster_metrics.cluster_name,
                total_monthly_cost=total_cost,
                compute_cost=compute_cost,
                storage_cost=storage_cost,
                network_cost=network_cost,
                waste_cost=waste_cost,
                optimization_potential=min(waste_cost, total_cost * 0.4),
                cost_per_namespace=dict(namespace_costs),
                cost_per_workload=dict(workload_costs),
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to perform cost analysis: {e}")
            return CostBreakdown(
                cluster_name="unknown",
                total_monthly_cost=0.0,
                compute_cost=0.0,
                storage_cost=0.0,
                network_cost=0.0,
                waste_cost=0.0,
                optimization_potential=0.0,
                cost_per_namespace={},
                cost_per_workload={},
                recommendations=[],
                timestamp=datetime.utcnow()
            )
    
    def _group_pods_by_workload(self, pod_metrics: List[PodMetrics]) -> Dict[str, List[PodMetrics]]:
        """Group pods by their parent workload"""
        workload_pods = defaultdict(list)
        
        for pod in pod_metrics:
            # Extract workload name from pod name (simplified heuristic)
            workload_name = self._extract_workload_name(pod.pod_name, pod.namespace)
            workload_pods[workload_name].append(pod)
        
        return dict(workload_pods)
    
    def _extract_workload_name(self, pod_name: str, namespace: str) -> str:
        """Extract workload name from pod name"""
        # Remove common suffixes from pod names
        suffixes_to_remove = [
            r'-[a-f0-9]{8,10}-[a-z0-9]{5}',  # ReplicaSet suffix
            r'-[a-f0-9]{5}',                 # Short hash suffix
            r'-\d+$'                         # Numeric suffix
        ]
        
        workload_name = pod_name
        import re
        for suffix in suffixes_to_remove:
            workload_name = re.sub(suffix, '', workload_name)
        
        return f"{namespace}/{workload_name}"
    
    async def _analyze_workload_utilization(
        self, 
        workload_name: str, 
        pods: List[PodMetrics], 
        observation_hours: int
    ) -> Dict[str, Any]:
        """Analyze utilization patterns for a workload"""
        if not pods:
            return {}
        
        # Calculate average utilization across pods
        avg_cpu_usage = statistics.mean([p.cpu_usage_millicores for p in pods])
        avg_memory_usage = statistics.mean([p.memory_usage_bytes for p in pods])
        
        # Calculate average requests
        avg_cpu_requests = statistics.mean([p.cpu_requests_millicores for p in pods if p.cpu_requests_millicores > 0])
        avg_memory_requests = statistics.mean([p.memory_requests_bytes for p in pods if p.memory_requests_bytes > 0])
        
        # Calculate utilization percentages
        cpu_usage_percent = (avg_cpu_usage / max(avg_cpu_requests, 1)) * 100 if avg_cpu_requests > 0 else 0
        memory_usage_percent = (avg_memory_usage / max(avg_memory_requests, 1)) * 100 if avg_memory_requests > 0 else 0
        
        # Determine if workload is idle
        is_idle = cpu_usage_percent < 5 and memory_usage_percent < 10
        is_underutilized = cpu_usage_percent < 20 or memory_usage_percent < 30
        
        # Calculate confidence based on data quality and patterns
        confidence = 0.5  # Base confidence
        if observation_hours >= 24:
            confidence += 0.2
        if len(pods) > 1:
            confidence += 0.1
        if is_idle:
            confidence += 0.2
        
        # Estimate potential savings
        monthly_cost = len(pods) * (
            (avg_cpu_requests / 1000.0) * self.default_costs["cpu_core_per_hour"] * 24 * 30 +
            (avg_memory_requests / (1024**3)) * self.default_costs["memory_gb_per_hour"] * 24 * 30
        )
        
        potential_savings = monthly_cost * 0.8 if is_idle else monthly_cost * 0.3 if is_underutilized else 0
        
        # Generate recommendations
        if is_idle:
            recommendation = "Consider scaling down or removing this workload - very low utilization detected"
            risk = "Low risk - workload appears unused"
        elif is_underutilized:
            recommendation = "Consider reducing resource requests or consolidating with other workloads"
            risk = "Medium risk - verify workload requirements before changes"
        else:
            recommendation = "Workload utilization appears optimal"
            risk = "No action needed"
        
        return {
            "name": workload_name.split("/")[-1],
            "namespace": pods[0].namespace,
            "type": "deployment",  # Simplified
            "idle_hours": observation_hours if is_idle else 0,
            "cpu_usage": cpu_usage_percent,
            "memory_usage": memory_usage_percent,
            "network_activity": 0,  # Simplified
            "last_activity": datetime.utcnow() - timedelta(hours=observation_hours if is_idle else 0),
            "confidence": min(1.0, confidence),
            "potential_savings": potential_savings,
            "recommendation": recommendation,
            "risk": risk
        }
    
    async def _identify_optimization_opportunities(self) -> List[ResourceOptimization]:
        """Identify resource optimization opportunities"""
        return await self.identify_optimization_opportunities()
    
    async def _analyze_node_optimizations(self) -> List[NodeOptimization]:
        """Analyze node-level optimization opportunities"""
        try:
            node_metrics = await self.metrics_collector.collect_node_metrics()
            optimizations = []
            
            for node in node_metrics:
                # Calculate utilization
                total_utilization = (node.cpu_usage_percent + node.memory_usage_percent) / 2
                
                if total_utilization < 30:
                    # Node is underutilized
                    optimization = NodeOptimization(
                        node_name=node.node_name,
                        node_type="worker",  # Simplified
                        current_utilization_percent=total_utilization,
                        optimization_type=OptimizationType.NODE_CONSOLIDATION,
                        recommendation=f"Node is {total_utilization:.1f}% utilized - consider consolidation",
                        potential_cost_savings_monthly=200.0,  # Estimated
                        affected_workloads=[],  # Would list actual workloads
                        migration_plan=[
                            "1. Cordon the node to prevent new scheduling",
                            "2. Drain workloads to other nodes",
                            "3. Remove the node from cluster",
                            "4. Terminate the underlying instance"
                        ],
                        risk_level="medium",
                        confidence=ConfidenceLevel.MEDIUM
                    )
                    optimizations.append(optimization)
            
            return optimizations
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze node optimizations: {e}")
            return []
    
    async def _analyze_cpu_optimization(self, pod: PodMetrics) -> Optional[ResourceOptimization]:
        """Analyze CPU optimization opportunities for a pod"""
        if pod.cpu_requests_millicores == 0:
            return None
        
        # Calculate CPU utilization
        cpu_utilization = (pod.cpu_usage_millicores / max(pod.cpu_requests_millicores, 1)) * 100
        
        if cpu_utilization < 20:  # Overprovisioned
            # Recommend reducing CPU requests
            new_request = max(10, int(pod.cpu_usage_millicores * 1.5))  # 50% buffer
            savings_percent = ((pod.cpu_requests_millicores - new_request) / pod.cpu_requests_millicores) * 100
            
            monthly_savings = (pod.cpu_requests_millicores - new_request) / 1000.0 * \
                            self.default_costs["cpu_core_per_hour"] * 24 * 30
            
            return ResourceOptimization(
                resource_type="cpu",
                workload_name=pod.pod_name,
                namespace=pod.namespace,
                current_request=f"{pod.cpu_requests_millicores}m",
                current_limit=f"{pod.cpu_limits_millicores}m" if pod.cpu_limits_millicores else "none",
                recommended_request=f"{new_request}m",
                recommended_limit=f"{new_request * 2}m",  # 2x buffer for limits
                potential_savings_percent=savings_percent,
                potential_savings_monthly=monthly_savings,
                confidence=ConfidenceLevel.HIGH if cpu_utilization < 10 else ConfidenceLevel.MEDIUM,
                justification=f"CPU utilization is {cpu_utilization:.1f}%, well below requested resources",
                implementation_steps=[
                    "1. Update deployment/statefulset resource requests",
                    "2. Monitor application performance after changes",
                    "3. Adjust if needed based on performance metrics"
                ]
            )
        
        return None
    
    async def _analyze_memory_optimization(self, pod: PodMetrics) -> Optional[ResourceOptimization]:
        """Analyze memory optimization opportunities for a pod"""
        if pod.memory_requests_bytes == 0:
            return None
        
        # Calculate memory utilization
        memory_utilization = (pod.memory_usage_bytes / max(pod.memory_requests_bytes, 1)) * 100
        
        if memory_utilization < 30:  # Overprovisioned
            # Recommend reducing memory requests
            new_request = max(64 * 1024 * 1024, int(pod.memory_usage_bytes * 1.5))  # 50% buffer, min 64MB
            savings_percent = ((pod.memory_requests_bytes - new_request) / pod.memory_requests_bytes) * 100
            
            monthly_savings = (pod.memory_requests_bytes - new_request) / (1024**3) * \
                            self.default_costs["memory_gb_per_hour"] * 24 * 30
            
            return ResourceOptimization(
                resource_type="memory",
                workload_name=pod.pod_name,
                namespace=pod.namespace,
                current_request=f"{pod.memory_requests_bytes // (1024**2)}Mi",
                current_limit=f"{pod.memory_limits_bytes // (1024**2)}Mi" if pod.memory_limits_bytes else "none",
                recommended_request=f"{new_request // (1024**2)}Mi",
                recommended_limit=f"{(new_request * 2) // (1024**2)}Mi",  # 2x buffer for limits
                potential_savings_percent=savings_percent,
                potential_savings_monthly=monthly_savings,
                confidence=ConfidenceLevel.HIGH if memory_utilization < 15 else ConfidenceLevel.MEDIUM,
                justification=f"Memory utilization is {memory_utilization:.1f}%, well below requested resources",
                implementation_steps=[
                    "1. Update deployment/statefulset memory requests",
                    "2. Monitor for OOMKilled events after changes",
                    "3. Adjust if memory pressure occurs"
                ]
            )
        
        return None
    
    def _calculate_overall_efficiency(
        self, 
        cluster_metrics: ClusterMetrics, 
        resource_efficiency: List[ResourceEfficiency],
        idle_workloads: List[IdleWorkload]
    ) -> float:
        """Calculate overall cluster efficiency score"""
        try:
            # Base efficiency from cluster metrics
            base_efficiency = cluster_metrics.cluster_efficiency_score
            
            # Resource efficiency score
            if resource_efficiency:
                resource_score = statistics.mean([re.efficiency_percent for re in resource_efficiency])
            else:
                resource_score = 50.0  # Neutral score
            
            # Idle workload penalty
            idle_penalty = min(20.0, len(idle_workloads) * 2.0)
            
            # Weighted calculation
            overall_efficiency = (
                base_efficiency * 0.4 +
                resource_score * 0.4 +
                max(0, 100 - idle_penalty) * 0.2
            )
            
            return min(100.0, max(0.0, overall_efficiency))
            
        except Exception:
            return 0.0
    
    def _generate_priority_actions(
        self, 
        idle_workloads: List[IdleWorkload],
        optimizations: List[ResourceOptimization],
        node_optimizations: List[NodeOptimization]
    ) -> List[str]:
        """Generate prioritized list of recommended actions"""
        actions = []
        
        # High-impact idle workloads
        high_impact_idle = [iw for iw in idle_workloads if iw.potential_savings_monthly > 100]
        if high_impact_idle:
            actions.append(f"Remove or scale down {len(high_impact_idle)} idle workloads (${sum(iw.potential_savings_monthly for iw in high_impact_idle):.0f}/month savings)")
        
        # High-confidence optimizations
        high_confidence_opts = [opt for opt in optimizations if opt.confidence == ConfidenceLevel.HIGH]
        if high_confidence_opts:
            total_savings = sum(opt.potential_savings_monthly for opt in high_confidence_opts)
            actions.append(f"Right-size {len(high_confidence_opts)} overprovisioned workloads (${total_savings:.0f}/month savings)")
        
        # Node consolidation opportunities
        if node_optimizations:
            total_node_savings = sum(node.potential_cost_savings_monthly for node in node_optimizations)
            actions.append(f"Consolidate {len(node_optimizations)} underutilized nodes (${total_node_savings:.0f}/month savings)")
        
        # Default actions if no specific optimizations found
        if not actions:
            actions.append("Continue monitoring - no immediate optimization opportunities identified")
        
        return actions[:5]  # Return top 5 actions
    
    def _assess_implementation_complexity(
        self, 
        idle_count: int, 
        optimization_count: int, 
        node_count: int
    ) -> str:
        """Assess overall implementation complexity"""
        total_changes = idle_count + optimization_count + node_count
        
        if total_changes == 0:
            return "none"
        elif total_changes <= 5:
            return "low"
        elif total_changes <= 15:
            return "medium"
        else:
            return "high"
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to enum"""
        if confidence >= 0.9:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached analysis is still valid"""
        if cache_key not in self.analysis_cache:
            return False
        
        cache_entry = self.analysis_cache[cache_key]
        return datetime.utcnow() - cache_entry["timestamp"] < self.cache_ttl
    
    def _cache_analysis(self, cache_key: str, data: Any):
        """Cache analysis results"""
        self.analysis_cache[cache_key] = {
            "timestamp": datetime.utcnow(),
            "data": data
        }
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of analysis capabilities"""
        return {
            "supported_analysis": [
                "idle_workload_detection",
                "resource_optimization",
                "node_consolidation",
                "cost_analysis",
                "efficiency_scoring"
            ],
            "confidence_levels": [level.value for level in ConfidenceLevel],
            "optimization_types": [opt_type.value for opt_type in OptimizationType],
            "cache_entries": len(self.analysis_cache),
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60
        }