"""
UPID CLI - Optimization Engine
Main optimization engine that coordinates all optimization strategies
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import json

from ..core.k8s_client import KubernetesClient, PodInfo
from ..core.metrics_collector import MetricsCollector, PodMetrics, ClusterMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from ..ml.pipeline import MLPipeline
from .zero_pod_scaler import ZeroPodScaler
from .resource_rightsizer import ResourceRightsizer
from .cost_optimizer import CostOptimizer
from .safety_manager import SafetyManager

logger = logging.getLogger(__name__)


@dataclass
class OptimizationStrategy:
    """Optimization strategy configuration"""
    name: str
    description: str
    enabled: bool = True
    risk_level: str = "low"  # low, medium, high
    savings_potential: float = 0.0
    implementation_time: int = 0  # seconds
    rollback_time: int = 0  # seconds
    prerequisites: List[str] = None
    parameters: Dict[str, Any] = None


@dataclass
class OptimizationAction:
    """Individual optimization action"""
    id: str
    strategy_name: str
    workload_name: str
    namespace: str
    action_type: str  # scale_to_zero, rightsize, cost_optimize
    current_state: Dict[str, Any]
    target_state: Dict[str, Any]
    estimated_savings: float
    risk_level: str
    confidence: float
    prerequisites: List[str]
    rollback_plan: Dict[str, Any]
    created_at: datetime
    status: str = "pending"  # pending, executing, completed, failed, rolled_back


@dataclass
class OptimizationPlan:
    """Complete optimization plan"""
    plan_id: str
    cluster_id: str
    created_at: datetime
    total_workloads: int
    total_actions: int
    estimated_savings: float
    risk_assessment: str
    actions: List[OptimizationAction]
    safety_checks: List[str]
    execution_timeout: int = 3600  # seconds
    status: str = "created"  # created, approved, executing, completed, failed


@dataclass
class OptimizationResult:
    """Optimization execution result"""
    plan_id: str
    execution_id: str
    start_time: datetime
    end_time: datetime
    total_actions: int
    successful_actions: int
    failed_actions: int
    actual_savings: float
    rollback_count: int
    execution_log: List[str]
    status: str = "completed"


class OptimizationEngine:
    """
    Enterprise-grade optimization engine for UPID platform
    
    Provides comprehensive optimization capabilities:
    - Safe zero-pod scaling with rollback guarantees
    - Resource request/limit optimization
    - Multi-cluster optimization strategies
    - Safety checks and automated rollbacks
    - ML-powered optimization recommendations
    """
    
    def __init__(self, k8s_client: KubernetesClient, metrics_collector: MetricsCollector, 
                 resource_analyzer: ResourceAnalyzer, ml_pipeline: MLPipeline):
        self.k8s_client = k8s_client
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.ml_pipeline = ml_pipeline
        
        # Initialize optimization components
        self.zero_pod_scaler = ZeroPodScaler(k8s_client, safety_manager=None)
        self.resource_rightsizer = ResourceRightsizer(k8s_client, safety_manager=None)
        self.cost_optimizer = CostOptimizer(k8s_client, safety_manager=None)
        self.safety_manager = SafetyManager(k8s_client)
        
        # Update safety manager references
        self.zero_pod_scaler.safety_manager = self.safety_manager
        self.resource_rightsizer.safety_manager = self.safety_manager
        self.cost_optimizer.safety_manager = self.safety_manager
        
        # Optimization strategies
        self.strategies = self._initialize_strategies()
        
        # Execution tracking
        self.active_plans: Dict[str, OptimizationPlan] = {}
        self.execution_history: List[OptimizationResult] = []
        
        logger.info("🔧 Initializing UPID optimization engine")
    
    def _initialize_strategies(self) -> Dict[str, OptimizationStrategy]:
        """Initialize available optimization strategies"""
        return {
            "zero_pod_scaling": OptimizationStrategy(
                name="Zero Pod Scaling",
                description="Scale idle workloads to zero replicas",
                enabled=True,
                risk_level="medium",
                savings_potential=0.3,  # 30% potential savings
                implementation_time=300,  # 5 minutes
                rollback_time=60,  # 1 minute
                prerequisites=["idle_detection", "health_checks"],
                parameters={
                    "min_idle_hours": 4,
                    "confidence_threshold": 0.8,
                    "exclude_namespaces": ["kube-system", "default"]
                }
            ),
            "resource_rightsizing": OptimizationStrategy(
                name="Resource Right-sizing",
                description="Optimize CPU and memory requests/limits",
                enabled=True,
                risk_level="low",
                savings_potential=0.2,  # 20% potential savings
                implementation_time=600,  # 10 minutes
                rollback_time=120,  # 2 minutes
                prerequisites=["usage_analysis", "performance_baseline"],
                parameters={
                    "cpu_optimization": True,
                    "memory_optimization": True,
                    "safety_margin": 0.2
                }
            ),
            "cost_optimization": OptimizationStrategy(
                name="Cost Optimization",
                description="Optimize resource allocation for cost reduction",
                enabled=True,
                risk_level="low",
                savings_potential=0.25,  # 25% potential savings
                implementation_time=900,  # 15 minutes
                rollback_time=180,  # 3 minutes
                prerequisites=["cost_analysis", "usage_patterns"],
                parameters={
                    "instance_type_optimization": True,
                    "storage_optimization": True,
                    "network_optimization": True
                }
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize the optimization engine"""
        try:
            logger.info("🚀 Initializing optimization engine...")
            
            # Initialize safety manager
            await self.safety_manager.initialize()
            
            # Test connectivity
            if not await self.k8s_client.connect():
                logger.error("❌ Failed to connect to Kubernetes cluster")
                return False
            
            logger.info("✅ Optimization engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize optimization engine: {e}")
            return False
    
    async def analyze_cluster(self, cluster_id: str) -> OptimizationPlan:
        """Analyze cluster and create optimization plan"""
        try:
            logger.info(f"🔍 Analyzing cluster {cluster_id} for optimization opportunities...")
            
            # Get current cluster state
            cluster_metrics = await self.metrics_collector.collect_cluster_metrics()
            pod_metrics = await self.metrics_collector.collect_pod_metrics()
            
            # Get ML predictions
            features_list = await self.ml_pipeline.extract_features(pod_metrics, cluster_metrics)
            
            # Generate optimization actions
            actions = []
            
            for i, features in enumerate(features_list):
                # Get ML predictions for this workload
                optimization_pred = await self.ml_pipeline.predict_optimization(features)
                
                if optimization_pred.confidence > 0.7:  # High confidence threshold
                    # Create optimization actions based on predictions
                    workload_actions = await self._create_optimization_actions(
                        features, optimization_pred, pod_metrics[i] if i < len(pod_metrics) else None
                    )
                    actions.extend(workload_actions)
            
            # Create optimization plan
            plan_id = f"opt_plan_{int(datetime.utcnow().timestamp())}"
            
            # Calculate total savings
            total_savings = sum(action.estimated_savings for action in actions)
            
            # Assess overall risk
            risk_levels = [action.risk_level for action in actions]
            overall_risk = self._assess_overall_risk(risk_levels)
            
            # Create safety checks
            safety_checks = await self.safety_manager.create_safety_checks(actions)
            
            plan = OptimizationPlan(
                plan_id=plan_id,
                cluster_id=cluster_id,
                created_at=datetime.utcnow(),
                total_workloads=len(set(action.workload_name for action in actions)),
                total_actions=len(actions),
                estimated_savings=total_savings,
                risk_assessment=overall_risk,
                actions=actions,
                safety_checks=safety_checks
            )
            
            # Store plan
            self.active_plans[plan_id] = plan
            
            logger.info(f"✅ Created optimization plan {plan_id}: {len(actions)} actions, ${total_savings:.2f} estimated savings")
            return plan
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze cluster: {e}")
            raise
    
    async def _create_optimization_actions(self, features, optimization_pred, pod_metrics) -> List[OptimizationAction]:
        """Create optimization actions based on ML predictions"""
        actions = []
        
        try:
            # Extract workload information
            workload_name = self._extract_workload_name(features.workload_type)
            namespace = features.namespace
            
            # Check if workload is idle (high confidence for zero-pod scaling)
            if features.idle_duration_hours > 4 and optimization_pred.confidence > 0.8:
                action = await self._create_zero_pod_action(features, pod_metrics)
                if action:
                    actions.append(action)
            
            # Check for resource optimization opportunities
            if features.cpu_usage_percent < 30 or features.memory_usage_percent < 40:
                action = await self._create_resource_rightsize_action(features, pod_metrics)
                if action:
                    actions.append(action)
            
            # Check for cost optimization opportunities
            if optimization_pred.prediction_value > 0.6:
                action = await self._create_cost_optimization_action(features, pod_metrics)
                if action:
                    actions.append(action)
            
        except Exception as e:
            logger.error(f"❌ Failed to create optimization actions: {e}")
        
        return actions
    
    async def _create_zero_pod_action(self, features, pod_metrics) -> Optional[OptimizationAction]:
        """Create zero-pod scaling action"""
        try:
            action_id = f"zero_pod_{int(datetime.utcnow().timestamp())}"
            
            current_state = {
                "replicas": 1,  # Assume current replica count
                "cpu_requests": features.resource_requests_cpu,
                "memory_requests": features.resource_requests_memory
            }
            
            target_state = {
                "replicas": 0,
                "cpu_requests": 0,
                "memory_requests": 0
            }
            
            # Calculate estimated savings
            estimated_savings = self._calculate_zero_pod_savings(features)
            
            return OptimizationAction(
                id=action_id,
                strategy_name="zero_pod_scaling",
                workload_name=self._extract_workload_name(features.workload_type),
                namespace=features.namespace,
                action_type="scale_to_zero",
                current_state=current_state,
                target_state=target_state,
                estimated_savings=estimated_savings,
                risk_level="medium",
                confidence=0.8,
                prerequisites=["idle_detection", "health_checks"],
                rollback_plan=self._create_rollback_plan(current_state),
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create zero-pod action: {e}")
            return None
    
    async def _create_resource_rightsize_action(self, features, pod_metrics) -> Optional[OptimizationAction]:
        """Create resource right-sizing action"""
        try:
            action_id = f"rightsize_{int(datetime.utcnow().timestamp())}"
            
            current_state = {
                "cpu_requests": features.resource_requests_cpu,
                "cpu_limits": features.resource_limits_cpu,
                "memory_requests": features.resource_requests_memory,
                "memory_limits": features.resource_limits_memory
            }
            
            # Calculate optimized resource values
            optimized_cpu = max(features.cpu_usage_percent * 1.2, 0.1)  # 20% safety margin
            optimized_memory = max(features.memory_usage_percent * 1.2, 64)  # 20% safety margin
            
            target_state = {
                "cpu_requests": optimized_cpu,
                "cpu_limits": optimized_cpu * 2,  # 2x requests
                "memory_requests": optimized_memory,
                "memory_limits": optimized_memory * 1.5  # 1.5x requests
            }
            
            # Calculate estimated savings
            estimated_savings = self._calculate_rightsize_savings(features, current_state, target_state)
            
            return OptimizationAction(
                id=action_id,
                strategy_name="resource_rightsizing",
                workload_name=self._extract_workload_name(features.workload_type),
                namespace=features.namespace,
                action_type="rightsize",
                current_state=current_state,
                target_state=target_state,
                estimated_savings=estimated_savings,
                risk_level="low",
                confidence=0.7,
                prerequisites=["usage_analysis", "performance_baseline"],
                rollback_plan=self._create_rollback_plan(current_state),
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create rightsize action: {e}")
            return None
    
    async def _create_cost_optimization_action(self, features, pod_metrics) -> Optional[OptimizationAction]:
        """Create cost optimization action"""
        try:
            action_id = f"cost_opt_{int(datetime.utcnow().timestamp())}"
            
            current_state = {
                "instance_type": "current",
                "storage_class": "current",
                "resource_allocation": "current"
            }
            
            target_state = {
                "instance_type": "optimized",
                "storage_class": "optimized",
                "resource_allocation": "optimized"
            }
            
            # Calculate estimated savings
            estimated_savings = self._calculate_cost_optimization_savings(features)
            
            return OptimizationAction(
                id=action_id,
                strategy_name="cost_optimization",
                workload_name=self._extract_workload_name(features.workload_type),
                namespace=features.namespace,
                action_type="cost_optimize",
                current_state=current_state,
                target_state=target_state,
                estimated_savings=estimated_savings,
                risk_level="low",
                confidence=0.6,
                prerequisites=["cost_analysis", "usage_patterns"],
                rollback_plan=self._create_rollback_plan(current_state),
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create cost optimization action: {e}")
            return None
    
    def _extract_workload_name(self, workload_type: str) -> str:
        """Extract workload name from type"""
        return workload_type.replace("_", "-")
    
    def _calculate_zero_pod_savings(self, features) -> float:
        """Calculate estimated savings from zero-pod scaling"""
        # Simple calculation based on resource usage
        cpu_cost = features.resource_requests_cpu * 0.1  # $0.1 per CPU core
        memory_cost = features.resource_requests_memory * 0.01  # $0.01 per MB
        return (cpu_cost + memory_cost) * 24 * 30  # Monthly savings
    
    def _calculate_rightsize_savings(self, features, current_state, target_state) -> float:
        """Calculate estimated savings from resource right-sizing"""
        cpu_savings = (current_state["cpu_requests"] - target_state["cpu_requests"]) * 0.1
        memory_savings = (current_state["memory_requests"] - target_state["memory_requests"]) * 0.01
        return (cpu_savings + memory_savings) * 24 * 30  # Monthly savings
    
    def _calculate_cost_optimization_savings(self, features) -> float:
        """Calculate estimated savings from cost optimization"""
        # Assume 15% savings from cost optimization
        base_cost = features.cpu_usage_percent * 0.1 + features.memory_usage_percent * 0.01
        return base_cost * 0.15 * 24 * 30  # 15% monthly savings
    
    def _create_rollback_plan(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create rollback plan for an action"""
        return {
            "original_state": current_state.copy(),
            "rollback_commands": [
                "kubectl scale deployment {workload} --replicas={replicas}",
                "kubectl patch deployment {workload} -p '{resource_patch}'"
            ],
            "rollback_timeout": 300,  # 5 minutes
            "verification_checks": [
                "kubectl get pods -l app={workload}",
                "kubectl top pods -l app={workload}"
            ]
        }
    
    def _assess_overall_risk(self, risk_levels: List[str]) -> str:
        """Assess overall risk level of optimization plan"""
        if not risk_levels:
            return "low"
        
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for risk in risk_levels:
            risk_counts[risk] += 1
        
        # Determine overall risk
        if risk_counts["high"] > 0:
            return "high"
        elif risk_counts["medium"] > len(risk_levels) * 0.3:  # More than 30% medium risk
            return "medium"
        else:
            return "low"
    
    async def execute_plan(self, plan_id: str, dry_run: bool = True) -> OptimizationResult:
        """Execute an optimization plan"""
        try:
            if plan_id not in self.active_plans:
                raise ValueError(f"Plan {plan_id} not found")
            
            plan = self.active_plans[plan_id]
            execution_id = f"exec_{int(datetime.utcnow().timestamp())}"
            
            logger.info(f"🚀 Executing optimization plan {plan_id} (dry_run={dry_run})")
            
            start_time = datetime.utcnow()
            successful_actions = 0
            failed_actions = 0
            rollback_count = 0
            execution_log = []
            
            # Execute each action
            for action in plan.actions:
                try:
                    if not dry_run:
                        # Execute the action
                        result = await self._execute_action(action)
                        if result:
                            successful_actions += 1
                            execution_log.append(f"✅ {action.action_type} for {action.workload_name}: SUCCESS")
                        else:
                            failed_actions += 1
                            execution_log.append(f"❌ {action.action_type} for {action.workload_name}: FAILED")
                            
                            # Attempt rollback
                            if await self._rollback_action(action):
                                rollback_count += 1
                                execution_log.append(f"🔄 Rollback for {action.workload_name}: SUCCESS")
                            else:
                                execution_log.append(f"❌ Rollback for {action.workload_name}: FAILED")
                    else:
                        # Dry run - just log what would be done
                        execution_log.append(f"🔍 DRY RUN: {action.action_type} for {action.workload_name}")
                        successful_actions += 1
                        
                except Exception as e:
                    failed_actions += 1
                    execution_log.append(f"❌ {action.action_type} for {action.workload_name}: ERROR - {e}")
            
            end_time = datetime.utcnow()
            
            # Calculate actual savings (simplified)
            actual_savings = plan.estimated_savings * (successful_actions / len(plan.actions)) if plan.actions else 0
            
            result = OptimizationResult(
                plan_id=plan_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                total_actions=len(plan.actions),
                successful_actions=successful_actions,
                failed_actions=failed_actions,
                actual_savings=actual_savings,
                rollback_count=rollback_count,
                execution_log=execution_log,
                status="completed" if failed_actions == 0 else "partial"
            )
            
            self.execution_history.append(result)
            
            logger.info(f"✅ Plan execution completed: {successful_actions}/{len(plan.actions)} successful")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to execute plan: {e}")
            raise
    
    async def _execute_action(self, action: OptimizationAction) -> bool:
        """Execute a single optimization action"""
        try:
            if action.action_type == "scale_to_zero":
                return await self.zero_pod_scaler.scale_to_zero(action)
            elif action.action_type == "rightsize":
                return await self.resource_rightsizer.optimize_resources(action)
            elif action.action_type == "cost_optimize":
                return await self.cost_optimizer.optimize_costs(action)
            else:
                logger.warning(f"⚠️ Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to execute action {action.id}: {e}")
            return False
    
    async def _rollback_action(self, action: OptimizationAction) -> bool:
        """Rollback a single optimization action"""
        try:
            return await self.safety_manager.rollback_action(action)
        except Exception as e:
            logger.error(f"❌ Failed to rollback action {action.id}: {e}")
            return False
    
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get optimization engine metrics"""
        return {
            "active_plans": len(self.active_plans),
            "total_executions": len(self.execution_history),
            "successful_executions": len([r for r in self.execution_history if r.status == "completed"]),
            "total_savings": sum(r.actual_savings for r in self.execution_history),
            "average_execution_time": sum((r.end_time - r.start_time).total_seconds() for r in self.execution_history) / max(len(self.execution_history), 1),
            "strategies_enabled": len([s for s in self.strategies.values() if s.enabled])
        }
    
    async def get_strategies(self) -> Dict[str, OptimizationStrategy]:
        """Get available optimization strategies"""
        return self.strategies.copy()
    
    async def update_strategy(self, strategy_name: str, enabled: bool = None, parameters: Dict[str, Any] = None):
        """Update optimization strategy configuration"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            if enabled is not None:
                strategy.enabled = enabled
            if parameters is not None:
                strategy.parameters.update(parameters)
            logger.info(f"✅ Updated strategy {strategy_name}")
        else:
            logger.warning(f"⚠️ Strategy {strategy_name} not found") 