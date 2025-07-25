"""
UPID CLI - Resource Rightsizer
Resource request/limit optimization for Kubernetes workloads
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
class RightsizingConfig:
    """Resource rightsizing configuration"""
    cpu_optimization: bool = True
    memory_optimization: bool = True
    safety_margin: float = 0.2  # 20% safety margin
    min_cpu_request: float = 0.1  # 100m
    min_memory_request: float = 64  # 64MB
    max_cpu_limit_multiplier: float = 2.0  # 2x requests
    max_memory_limit_multiplier: float = 1.5  # 1.5x requests
    optimization_threshold: float = 0.3  # 30% optimization potential
    verification_delay: int = 60  # 60 seconds
    rollback_timeout: int = 300  # 5 minutes


@dataclass
class RightsizingResult:
    """Resource rightsizing result"""
    action_id: str
    workload_name: str
    namespace: str
    resource_type: str  # cpu, memory, both
    original_requests: Dict[str, float]
    original_limits: Dict[str, float]
    optimized_requests: Dict[str, float]
    optimized_limits: Dict[str, float]
    optimization_successful: bool
    verification_passed: bool
    rollback_required: bool
    estimated_savings: float
    error_message: Optional[str] = None
    execution_time: float = 0.0


class ResourceRightsizer:
    """
    Resource request/limit optimization for Kubernetes workloads
    
    Provides comprehensive resource optimization capabilities:
    - CPU and memory request optimization
    - Resource limit optimization
    - Safety margin enforcement
    - Performance verification
    - Automated rollback on issues
    """
    
    def __init__(self, k8s_client: KubernetesClient, safety_manager: Optional[SafetyManager] = None):
        self.k8s_client = k8s_client
        self.safety_manager = safety_manager
        
        # Default configuration
        self.config = RightsizingConfig()
        
        # Rightsizing history
        self.rightsizing_history: List[RightsizingResult] = []
        
        # Active rightsizing operations
        self.active_rightsizing: Dict[str, RightsizingResult] = {}
        
        logger.info("🔧 Initializing resource rightsizer")
    
    async def initialize(self) -> bool:
        """Initialize the resource rightsizer"""
        try:
            logger.info("🚀 Initializing resource rightsizer...")
            
            # Test connectivity
            if not await self.k8s_client.connect():
                logger.error("❌ Failed to connect to Kubernetes cluster")
                return False
            
            # Initialize safety manager if provided
            if self.safety_manager:
                await self.safety_manager.initialize()
            
            logger.info("✅ Resource rightsizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize resource rightsizer: {e}")
            return False
    
    async def optimize_resources(self, action: OptimizationAction) -> bool:
        """Optimize resource requests and limits for a workload"""
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"🚀 Optimizing resources for {action.workload_name} in {action.namespace}")
            
            # Validate action
            if not self._validate_rightsizing_action(action):
                logger.error(f"❌ Invalid rightsizing action: {action.id}")
                return False
            
            # Check safety prerequisites
            if not await self._check_safety_prerequisites(action):
                logger.warning(f"⚠️ Safety prerequisites not met for {action.workload_name}")
                return False
            
            # Get current resource state
            current_state = await self._get_current_resource_state(action.workload_name, action.namespace)
            if not current_state:
                logger.error(f"❌ Failed to get current resource state for {action.workload_name}")
                return False
            
            # Calculate optimized resources
            optimized_resources = await self._calculate_optimized_resources(current_state, action)
            if not optimized_resources:
                logger.error(f"❌ Failed to calculate optimized resources for {action.workload_name}")
                return False
            
            # Create rightsizing result
            rightsizing_result = RightsizingResult(
                action_id=action.id,
                workload_name=action.workload_name,
                namespace=action.namespace,
                resource_type="both" if self.config.cpu_optimization and self.config.memory_optimization else "cpu" if self.config.cpu_optimization else "memory",
                original_requests=current_state.get("requests", {}),
                original_limits=current_state.get("limits", {}),
                optimized_requests=optimized_resources["requests"],
                optimized_limits=optimized_resources["limits"],
                optimization_successful=False,
                verification_passed=False,
                rollback_required=False,
                estimated_savings=action.estimated_savings
            )
            
            # Store active rightsizing
            self.active_rightsizing[action.id] = rightsizing_result
            
            # Perform resource optimization
            optimization_success = await self._perform_resource_optimization(action, optimized_resources)
            rightsizing_result.optimization_successful = optimization_success
            
            if optimization_success:
                # Wait for optimization to take effect
                await asyncio.sleep(10)  # Wait for Kubernetes to process
                
                # Verify optimization
                verification_passed = await self._verify_optimization(action)
                rightsizing_result.verification_passed = verification_passed
                
                if not verification_passed:
                    # Rollback if verification fails
                    rollback_success = await self._rollback_optimization(action, current_state)
                    rightsizing_result.rollback_required = True
                    
                    if not rollback_success:
                        logger.error(f"❌ Failed to rollback optimization for {action.workload_name}")
                        rightsizing_result.error_message = "Rollback failed"
                else:
                    logger.info(f"✅ Successfully optimized resources for {action.workload_name}")
            else:
                rightsizing_result.error_message = "Resource optimization failed"
                logger.error(f"❌ Failed to optimize resources for {action.workload_name}")
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            rightsizing_result.execution_time = execution_time
            
            # Store in history
            self.rightsizing_history.append(rightsizing_result)
            
            # Remove from active rightsizing
            if action.id in self.active_rightsizing:
                del self.active_rightsizing[action.id]
            
            return rightsizing_result.optimization_successful and rightsizing_result.verification_passed
            
        except Exception as e:
            logger.error(f"❌ Error during resource optimization: {e}")
            return False
    
    def _validate_rightsizing_action(self, action: OptimizationAction) -> bool:
        """Validate rightsizing action"""
        try:
            # Check required fields
            if not action.workload_name or not action.namespace:
                return False
            
            # Check action type
            if action.action_type != "rightsize":
                logger.warning(f"⚠️ Invalid action type for rightsizing: {action.action_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating rightsizing action: {e}")
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
    
    async def _get_current_resource_state(self, workload_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get current resource state"""
        try:
            # Get deployment information
            deployment_info = await self.k8s_client.get_deployment_info(workload_name, namespace)
            
            if not deployment_info:
                logger.warning(f"⚠️ Deployment {workload_name} not found in namespace {namespace}")
                return None
            
            # Get pod metrics for resource usage
            pod_metrics = await self.k8s_client.get_pod_metrics(workload_name, namespace)
            
            return {
                "requests": deployment_info.get("resource_requests", {}),
                "limits": deployment_info.get("resource_limits", {}),
                "usage": pod_metrics.get("usage", {}) if pod_metrics else {},
                "replicas": deployment_info.get("replicas", 1)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting resource state: {e}")
            return None
    
    async def _calculate_optimized_resources(self, current_state: Dict[str, Any], action: OptimizationAction) -> Optional[Dict[str, Any]]:
        """Calculate optimized resource values"""
        try:
            current_requests = current_state.get("requests", {})
            current_limits = current_state.get("limits", {})
            usage = current_state.get("usage", {})
            
            optimized_requests = {}
            optimized_limits = {}
            
            # Optimize CPU if enabled
            if self.config.cpu_optimization:
                cpu_request = current_requests.get("cpu", 0.5)
                cpu_usage = usage.get("cpu", 0.3)
                
                # Calculate optimized CPU request with safety margin
                optimized_cpu = max(cpu_usage * (1 + self.config.safety_margin), self.config.min_cpu_request)
                
                # Ensure we don't increase requests unnecessarily
                if optimized_cpu < cpu_request * (1 - self.config.optimization_threshold):
                    optimized_requests["cpu"] = optimized_cpu
                    optimized_limits["cpu"] = optimized_cpu * self.config.max_cpu_limit_multiplier
                else:
                    optimized_requests["cpu"] = cpu_request
                    optimized_limits["cpu"] = current_limits.get("cpu", cpu_request * 2)
            
            # Optimize memory if enabled
            if self.config.memory_optimization:
                memory_request = current_requests.get("memory", 512)
                memory_usage = usage.get("memory", 256)
                
                # Calculate optimized memory request with safety margin
                optimized_memory = max(memory_usage * (1 + self.config.safety_margin), self.config.min_memory_request)
                
                # Ensure we don't increase requests unnecessarily
                if optimized_memory < memory_request * (1 - self.config.optimization_threshold):
                    optimized_requests["memory"] = optimized_memory
                    optimized_limits["memory"] = optimized_memory * self.config.max_memory_limit_multiplier
                else:
                    optimized_requests["memory"] = memory_request
                    optimized_limits["memory"] = current_limits.get("memory", memory_request * 1.5)
            
            return {
                "requests": optimized_requests,
                "limits": optimized_limits
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating optimized resources: {e}")
            return None
    
    async def _perform_resource_optimization(self, action: OptimizationAction, optimized_resources: Dict[str, Any]) -> bool:
        """Perform the actual resource optimization"""
        try:
            # Update deployment with optimized resources
            patch_success = await self.k8s_client.patch_deployment_resources(
                action.workload_name,
                action.namespace,
                requests=optimized_resources["requests"],
                limits=optimized_resources["limits"]
            )
            
            if patch_success:
                logger.info(f"✅ Successfully updated resources for {action.workload_name}")
            else:
                logger.error(f"❌ Failed to update resources for {action.workload_name}")
            
            return patch_success
            
        except Exception as e:
            logger.error(f"❌ Error performing resource optimization: {e}")
            return False
    
    async def _verify_optimization(self, action: OptimizationAction) -> bool:
        """Verify that resource optimization was successful"""
        try:
            # Wait for verification delay
            await asyncio.sleep(self.config.verification_delay)
            
            # Get updated deployment state
            updated_state = await self._get_current_resource_state(action.workload_name, action.namespace)
            
            if not updated_state:
                logger.error(f"❌ Failed to get updated state for {action.workload_name}")
                return False
            
            # Check if resources were actually updated
            current_requests = updated_state.get("requests", {})
            target_requests = action.target_state
            
            # Verify CPU optimization
            if self.config.cpu_optimization:
                current_cpu = current_requests.get("cpu", 0)
                target_cpu = target_requests.get("cpu_requests", 0)
                
                if abs(current_cpu - target_cpu) > 0.01:  # Allow small tolerance
                    logger.warning(f"⚠️ CPU optimization verification failed - current: {current_cpu}, target: {target_cpu}")
                    return False
            
            # Verify memory optimization
            if self.config.memory_optimization:
                current_memory = current_requests.get("memory", 0)
                target_memory = target_requests.get("memory_requests", 0)
                
                if abs(current_memory - target_memory) > 1:  # Allow small tolerance
                    logger.warning(f"⚠️ Memory optimization verification failed - current: {current_memory}, target: {target_memory}")
                    return False
            
            # Check if pods are still healthy
            pods = await self.k8s_client.list_pods(namespace=action.namespace, label_selector=f"app={action.workload_name}")
            healthy_pods = [pod for pod in pods if pod.status == "Running"]
            
            if len(healthy_pods) == 0:
                logger.warning(f"⚠️ Optimization verification failed - no healthy pods")
                return False
            
            logger.info(f"✅ Resource optimization verification passed for {action.workload_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying optimization: {e}")
            return False
    
    async def _rollback_optimization(self, action: OptimizationAction, original_state: Dict[str, Any]) -> bool:
        """Rollback resource optimization to original state"""
        try:
            logger.info(f"🔄 Rolling back resource optimization for {action.workload_name}")
            
            # Restore original resources
            rollback_success = await self.k8s_client.patch_deployment_resources(
                action.workload_name,
                action.namespace,
                requests=original_state.get("requests", {}),
                limits=original_state.get("limits", {})
            )
            
            if rollback_success:
                logger.info(f"✅ Successfully rolled back resources for {action.workload_name}")
            else:
                logger.error(f"❌ Failed to rollback resources for {action.workload_name}")
            
            return rollback_success
            
        except Exception as e:
            logger.error(f"❌ Error rolling back optimization: {e}")
            return False
    
    async def get_rightsizing_metrics(self) -> Dict[str, Any]:
        """Get rightsizing metrics"""
        return {
            "total_optimizations": len(self.rightsizing_history),
            "successful_optimizations": len([r for r in self.rightsizing_history if r.optimization_successful]),
            "failed_optimizations": len([r for r in self.rightsizing_history if not r.optimization_successful]),
            "rollback_count": len([r for r in self.rightsizing_history if r.rollback_required]),
            "total_savings": sum(r.estimated_savings for r in self.rightsizing_history),
            "average_execution_time": sum(r.execution_time for r in self.rightsizing_history) / max(len(self.rightsizing_history), 1),
            "active_optimizations": len(self.active_rightsizing)
        }
    
    async def get_rightsizing_history(self) -> List[RightsizingResult]:
        """Get rightsizing history"""
        return self.rightsizing_history.copy()
    
    def update_config(self, config: RightsizingConfig):
        """Update rightsizing configuration"""
        self.config = config
        logger.info("✅ Updated resource rightsizing configuration")
    
    async def is_workload_eligible_for_rightsizing(self, workload_name: str, namespace: str) -> Tuple[bool, str]:
        """Check if a workload is eligible for resource rightsizing"""
        try:
            # Get current resource state
            resource_state = await self._get_current_resource_state(workload_name, namespace)
            if not resource_state:
                return False, "Workload not found"
            
            # Check if has resource requests
            requests = resource_state.get("requests", {})
            if not requests:
                return False, "No resource requests defined"
            
            # Check if has usage data
            usage = resource_state.get("usage", {})
            if not usage:
                return False, "No usage data available"
            
            # Check if optimization is needed
            cpu_request = requests.get("cpu", 0)
            cpu_usage = usage.get("cpu", 0)
            memory_request = requests.get("memory", 0)
            memory_usage = usage.get("memory", 0)
            
            if cpu_request > 0 and cpu_usage < cpu_request * (1 - self.config.optimization_threshold):
                return True, "CPU optimization needed"
            
            if memory_request > 0 and memory_usage < memory_request * (1 - self.config.optimization_threshold):
                return True, "Memory optimization needed"
            
            return False, "No optimization needed"
            
        except Exception as e:
            logger.error(f"❌ Error checking workload eligibility: {e}")
            return False, f"Error: {str(e)}" 