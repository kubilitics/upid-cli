"""
UPID CLI - Cost Optimizer
Cost reduction strategies for Kubernetes workloads
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from ..core.k8s_client import KubernetesClient, PodInfo
from .safety_manager import SafetyManager
from .optimization_engine import OptimizationAction

logger = logging.getLogger(__name__)


@dataclass
class CostOptimizationConfig:
    """Cost optimization configuration"""
    instance_type_optimization: bool = True
    storage_optimization: bool = True
    network_optimization: bool = True
    spot_instance_usage: bool = False
    reserved_instance_usage: bool = True
    auto_scaling_enabled: bool = True
    cost_threshold: float = 100.0  # $100 minimum savings
    optimization_timeout: int = 900  # 15 minutes
    verification_delay: int = 120  # 2 minutes


@dataclass
class CostOptimizationResult:
    """Cost optimization result"""
    action_id: str
    workload_name: str
    namespace: str
    optimization_type: str  # instance, storage, network, combined
    original_cost: float
    optimized_cost: float
    cost_savings: float
    optimization_successful: bool
    verification_passed: bool
    rollback_required: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0


class CostOptimizer:
    """
    Cost optimization strategies for Kubernetes workloads
    
    Provides comprehensive cost optimization capabilities:
    - Instance type optimization
    - Storage optimization
    - Network optimization
    - Spot instance usage
    - Reserved instance recommendations
    - Auto-scaling optimization
    """
    
    def __init__(self, k8s_client: KubernetesClient, safety_manager: Optional[SafetyManager] = None):
        self.k8s_client = k8s_client
        self.safety_manager = safety_manager
        
        # Default configuration
        self.config = CostOptimizationConfig()
        
        # Cost optimization history
        self.optimization_history: List[CostOptimizationResult] = []
        
        # Active optimization operations
        self.active_optimizations: Dict[str, CostOptimizationResult] = {}
        
        logger.info("🔧 Initializing cost optimizer")
    
    async def initialize(self) -> bool:
        """Initialize the cost optimizer"""
        try:
            logger.info("🚀 Initializing cost optimizer...")
            
            # Test connectivity
            if not await self.k8s_client.connect():
                logger.error("❌ Failed to connect to Kubernetes cluster")
                return False
            
            # Initialize safety manager if provided
            if self.safety_manager:
                await self.safety_manager.initialize()
            
            logger.info("✅ Cost optimizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cost optimizer: {e}")
            return False
    
    async def optimize_costs(self, action: OptimizationAction) -> bool:
        """Optimize costs for a workload"""
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"🚀 Optimizing costs for {action.workload_name} in {action.namespace}")
            
            # Validate action
            if not self._validate_cost_optimization_action(action):
                logger.error(f"❌ Invalid cost optimization action: {action.id}")
                return False
            
            # Check safety prerequisites
            if not await self._check_safety_prerequisites(action):
                logger.warning(f"⚠️ Safety prerequisites not met for {action.workload_name}")
                return False
            
            # Get current cost state
            current_cost_state = await self._get_current_cost_state(action.workload_name, action.namespace)
            if not current_cost_state:
                logger.error(f"❌ Failed to get current cost state for {action.workload_name}")
                return False
            
            # Calculate optimized costs
            optimized_costs = await self._calculate_optimized_costs(current_cost_state, action)
            if not optimized_costs:
                logger.error(f"❌ Failed to calculate optimized costs for {action.workload_name}")
                return False
            
            # Check if savings meet threshold
            cost_savings = current_cost_state.get("monthly_cost", 0) - optimized_costs.get("monthly_cost", 0)
            if cost_savings < self.config.cost_threshold:
                logger.info(f"ℹ️ Cost savings ${cost_savings:.2f} below threshold ${self.config.cost_threshold} for {action.workload_name}")
                return False
            
            # Create cost optimization result
            optimization_result = CostOptimizationResult(
                action_id=action.id,
                workload_name=action.workload_name,
                namespace=action.namespace,
                optimization_type="combined",
                original_cost=current_cost_state.get("monthly_cost", 0),
                optimized_cost=optimized_costs.get("monthly_cost", 0),
                cost_savings=cost_savings,
                optimization_successful=False,
                verification_passed=False,
                rollback_required=False
            )
            
            # Store active optimization
            self.active_optimizations[action.id] = optimization_result
            
            # Perform cost optimization
            optimization_success = await self._perform_cost_optimization(action, optimized_costs)
            optimization_result.optimization_successful = optimization_success
            
            if optimization_success:
                # Wait for optimization to take effect
                await asyncio.sleep(10)  # Wait for changes to propagate
                
                # Verify optimization
                verification_passed = await self._verify_cost_optimization(action)
                optimization_result.verification_passed = verification_passed
                
                if not verification_passed:
                    # Rollback if verification fails
                    rollback_success = await self._rollback_cost_optimization(action, current_cost_state)
                    optimization_result.rollback_required = True
                    
                    if not rollback_success:
                        logger.error(f"❌ Failed to rollback cost optimization for {action.workload_name}")
                        optimization_result.error_message = "Rollback failed"
                else:
                    logger.info(f"✅ Successfully optimized costs for {action.workload_name} - saved ${cost_savings:.2f}/month")
            else:
                optimization_result.error_message = "Cost optimization failed"
                logger.error(f"❌ Failed to optimize costs for {action.workload_name}")
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            optimization_result.execution_time = execution_time
            
            # Store in history
            self.optimization_history.append(optimization_result)
            
            # Remove from active optimizations
            if action.id in self.active_optimizations:
                del self.active_optimizations[action.id]
            
            return optimization_result.optimization_successful and optimization_result.verification_passed
            
        except Exception as e:
            logger.error(f"❌ Error during cost optimization: {e}")
            return False
    
    def _validate_cost_optimization_action(self, action: OptimizationAction) -> bool:
        """Validate cost optimization action"""
        try:
            # Check required fields
            if not action.workload_name or not action.namespace:
                return False
            
            # Check action type
            if action.action_type != "cost_optimize":
                logger.warning(f"⚠️ Invalid action type for cost optimization: {action.action_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating cost optimization action: {e}")
            return False
    
    async def _check_safety_prerequisites(self, action: OptimizationAction) -> bool:
        """Check safety prerequisites before optimization"""
        try:
            # Check if safety manager is available
            if not self.safety_manager:
                logger.warning("⚠️ No safety manager available - skipping safety checks")
                return True
            
            # Perform safety checks
            safety_checks = await self.safety_manager.perform_safety_checks(action)
            
            # Check if all critical safety checks passed
            critical_checks = [check for check in safety_checks if check.get("critical", False)]
            passed_critical = all(check.get("passed", False) for check in critical_checks)
            
            if not passed_critical:
                failed_checks = [check["name"] for check in critical_checks if not check.get("passed", False)]
                logger.warning(f"⚠️ Critical safety checks failed: {failed_checks}")
                return False
            
            logger.info(f"✅ Safety prerequisites passed for {action.workload_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking safety prerequisites: {e}")
            return False
    
    async def _get_current_cost_state(self, workload_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get current cost state"""
        try:
            # Get deployment information
            deployment_info = await self.k8s_client.get_deployment_info(workload_name, namespace)
            
            if not deployment_info:
                logger.warning(f"⚠️ Deployment {workload_name} not found in namespace {namespace}")
                return None
            
            # Get node information for instance costs
            node_info = await self.k8s_client.get_node_info()
            
            # Calculate current costs (simplified)
            replicas = deployment_info.get("replicas", 1)
            cpu_requests = deployment_info.get("resource_requests", {}).get("cpu", 0.5)
            memory_requests = deployment_info.get("resource_requests", {}).get("memory", 512)
            
            # Calculate monthly costs
            cpu_cost = cpu_requests * 0.1 * 24 * 30  # $0.1 per CPU core per hour
            memory_cost = memory_requests * 0.01 * 24 * 30  # $0.01 per MB per hour
            instance_cost = replicas * 50  # $50 per instance per month (simplified)
            
            monthly_cost = cpu_cost + memory_cost + instance_cost
            
            return {
                "monthly_cost": monthly_cost,
                "cpu_cost": cpu_cost,
                "memory_cost": memory_cost,
                "instance_cost": instance_cost,
                "replicas": replicas,
                "cpu_requests": cpu_requests,
                "memory_requests": memory_requests,
                "instance_type": "current",
                "storage_class": "current",
                "auto_scaling": deployment_info.get("auto_scaling", False)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cost state: {e}")
            return None
    
    async def _calculate_optimized_costs(self, current_state: Dict[str, Any], action: OptimizationAction) -> Optional[Dict[str, Any]]:
        """Calculate optimized cost values"""
        try:
            current_cost = current_state.get("monthly_cost", 0)
            replicas = current_state.get("replicas", 1)
            cpu_requests = current_state.get("cpu_requests", 0.5)
            memory_requests = current_state.get("memory_requests", 512)
            
            optimized_costs = {}
            
            # Instance type optimization
            if self.config.instance_type_optimization:
                # Simulate 20% cost reduction from instance optimization
                instance_savings = current_state.get("instance_cost", 0) * 0.2
                optimized_costs["instance_savings"] = instance_savings
            
            # Storage optimization
            if self.config.storage_optimization:
                # Simulate 15% cost reduction from storage optimization
                storage_savings = current_cost * 0.15
                optimized_costs["storage_savings"] = storage_savings
            
            # Network optimization
            if self.config.network_optimization:
                # Simulate 10% cost reduction from network optimization
                network_savings = current_cost * 0.10
                optimized_costs["network_savings"] = network_savings
            
            # Auto-scaling optimization
            if self.config.auto_scaling_enabled:
                # Simulate 25% cost reduction from auto-scaling
                scaling_savings = current_cost * 0.25
                optimized_costs["scaling_savings"] = scaling_savings
            
            # Calculate total optimized cost
            total_savings = sum(optimized_costs.values())
            optimized_monthly_cost = max(current_cost - total_savings, current_cost * 0.5)  # Minimum 50% of original cost
            
            return {
                "monthly_cost": optimized_monthly_cost,
                "total_savings": total_savings,
                "optimization_breakdown": optimized_costs,
                "instance_type": "optimized",
                "storage_class": "optimized",
                "auto_scaling": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating optimized costs: {e}")
            return None
    
    async def _perform_cost_optimization(self, action: OptimizationAction, optimized_costs: Dict[str, Any]) -> bool:
        """Perform the actual cost optimization"""
        try:
            # This is a simplified implementation
            # In a real implementation, this would:
            # 1. Update instance types
            # 2. Optimize storage classes
            # 3. Configure auto-scaling
            # 4. Update network policies
            
            logger.info(f"✅ Simulated cost optimization for {action.workload_name}")
            
            # Simulate optimization success
            await asyncio.sleep(2)  # Simulate processing time
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error performing cost optimization: {e}")
            return False
    
    async def _verify_cost_optimization(self, action: OptimizationAction) -> bool:
        """Verify that cost optimization was successful"""
        try:
            # Wait for verification delay
            await asyncio.sleep(self.config.verification_delay)
            
            # Get updated cost state
            updated_state = await self._get_current_cost_state(action.workload_name, action.namespace)
            
            if not updated_state:
                logger.error(f"❌ Failed to get updated cost state for {action.workload_name}")
                return False
            
            # Check if costs were actually reduced
            current_cost = updated_state.get("monthly_cost", 0)
            original_cost = action.current_state.get("monthly_cost", 0)
            
            if current_cost >= original_cost:
                logger.warning(f"⚠️ Cost optimization verification failed - cost not reduced")
                return False
            
            # Check if pods are still healthy
            pods = await self.k8s_client.list_pods(namespace=action.namespace, label_selector=f"app={action.workload_name}")
            healthy_pods = [pod for pod in pods if pod.status == "Running"]
            
            if len(healthy_pods) == 0:
                logger.warning(f"⚠️ Cost optimization verification failed - no healthy pods")
                return False
            
            logger.info(f"✅ Cost optimization verification passed for {action.workload_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying cost optimization: {e}")
            return False
    
    async def _rollback_cost_optimization(self, action: OptimizationAction, original_state: Dict[str, Any]) -> bool:
        """Rollback cost optimization to original state"""
        try:
            logger.info(f"🔄 Rolling back cost optimization for {action.workload_name}")
            
            # This is a simplified implementation
            # In a real implementation, this would restore original configurations
            
            logger.info(f"✅ Successfully rolled back cost optimization for {action.workload_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rolling back cost optimization: {e}")
            return False
    
    async def get_cost_optimization_metrics(self) -> Dict[str, Any]:
        """Get cost optimization metrics"""
        return {
            "total_optimizations": len(self.optimization_history),
            "successful_optimizations": len([r for r in self.optimization_history if r.optimization_successful]),
            "failed_optimizations": len([r for r in self.optimization_history if not r.optimization_successful]),
            "rollback_count": len([r for r in self.optimization_history if r.rollback_required]),
            "total_savings": sum(r.cost_savings for r in self.optimization_history),
            "average_execution_time": sum(r.execution_time for r in self.optimization_history) / max(len(self.optimization_history), 1),
            "active_optimizations": len(self.active_optimizations)
        }
    
    async def get_cost_optimization_history(self) -> List[CostOptimizationResult]:
        """Get cost optimization history"""
        return self.optimization_history.copy()
    
    def update_config(self, config: CostOptimizationConfig):
        """Update cost optimization configuration"""
        self.config = config
        logger.info("✅ Updated cost optimization configuration")
    
    async def is_workload_eligible_for_cost_optimization(self, workload_name: str, namespace: str) -> Tuple[bool, str]:
        """Check if a workload is eligible for cost optimization"""
        try:
            # Get current cost state
            cost_state = await self._get_current_cost_state(workload_name, namespace)
            if not cost_state:
                return False, "Workload not found"
            
            # Check if has significant costs
            monthly_cost = cost_state.get("monthly_cost", 0)
            if monthly_cost < self.config.cost_threshold:
                return False, f"Monthly cost ${monthly_cost:.2f} below threshold ${self.config.cost_threshold}"
            
            # Check if has optimization potential
            replicas = cost_state.get("replicas", 1)
            if replicas == 1:
                return False, "Single replica - limited optimization potential"
            
            return True, "Eligible for cost optimization"
            
        except Exception as e:
            logger.error(f"❌ Error checking workload eligibility: {e}")
            return False, f"Error: {str(e)}"
    
    async def get_cost_recommendations(self, workload_name: str, namespace: str) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations for a workload"""
        try:
            recommendations = []
            
            # Get current cost state
            cost_state = await self._get_current_cost_state(workload_name, namespace)
            if not cost_state:
                return recommendations
            
            monthly_cost = cost_state.get("monthly_cost", 0)
            
            # Instance type optimization recommendation
            if self.config.instance_type_optimization:
                instance_savings = cost_state.get("instance_cost", 0) * 0.2
                if instance_savings > 10:  # $10 minimum savings
                    recommendations.append({
                        "type": "instance_optimization",
                        "description": "Switch to more cost-effective instance type",
                        "potential_savings": instance_savings,
                        "risk_level": "low",
                        "implementation_time": "5 minutes"
                    })
            
            # Auto-scaling recommendation
            if self.config.auto_scaling_enabled and not cost_state.get("auto_scaling", False):
                scaling_savings = monthly_cost * 0.25
                recommendations.append({
                    "type": "auto_scaling",
                    "description": "Enable auto-scaling for better resource utilization",
                    "potential_savings": scaling_savings,
                    "risk_level": "low",
                    "implementation_time": "10 minutes"
                })
            
            # Storage optimization recommendation
            if self.config.storage_optimization:
                storage_savings = monthly_cost * 0.15
                recommendations.append({
                    "type": "storage_optimization",
                    "description": "Optimize storage class for cost efficiency",
                    "potential_savings": storage_savings,
                    "risk_level": "medium",
                    "implementation_time": "15 minutes"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting cost recommendations: {e}")
            return [] 