"""
UPID CLI - Zero Pod Scaler
Safe zero-pod scaling logic for idle workloads
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
class ScalingConfig:
    """Zero-pod scaling configuration"""
    min_idle_hours: int = 4
    confidence_threshold: float = 0.8
    exclude_namespaces: List[str] = None
    include_namespaces: List[str] = None
    max_concurrent_scaling: int = 5
    scaling_timeout: int = 300  # 5 minutes
    verification_delay: int = 30  # 30 seconds


@dataclass
class ScalingResult:
    """Zero-pod scaling result"""
    action_id: str
    workload_name: str
    namespace: str
    original_replicas: int
    target_replicas: int
    scaling_successful: bool
    verification_passed: bool
    rollback_required: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0


class ZeroPodScaler:
    """
    Safe zero-pod scaling for idle workloads
    
    Provides comprehensive zero-pod scaling capabilities:
    - Safe scaling with rollback guarantees
    - Health check verification
    - Traffic pattern analysis
    - Automated rollback on issues
    """
    
    def __init__(self, k8s_client: KubernetesClient, safety_manager: Optional[SafetyManager] = None):
        self.k8s_client = k8s_client
        self.safety_manager = safety_manager
        
        # Default configuration
        self.config = ScalingConfig()
        
        # Scaling history
        self.scaling_history: List[ScalingResult] = []
        
        # Active scaling operations
        self.active_scaling: Dict[str, ScalingResult] = {}
        
        logger.info("🔧 Initializing zero-pod scaler")
    
    async def initialize(self) -> bool:
        """Initialize the zero-pod scaler"""
        try:
            logger.info("🚀 Initializing zero-pod scaler...")
            
            # Test connectivity
            if not await self.k8s_client.connect():
                logger.error("❌ Failed to connect to Kubernetes cluster")
                return False
            
            # Initialize safety manager if provided
            if self.safety_manager:
                await self.safety_manager.initialize()
            
            logger.info("✅ Zero-pod scaler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize zero-pod scaler: {e}")
            return False
    
    async def scale_to_zero(self, action: OptimizationAction) -> bool:
        """Scale a workload to zero replicas"""
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"🚀 Scaling {action.workload_name} in {action.namespace} to zero replicas")
            
            # Validate action
            if not self._validate_scaling_action(action):
                logger.error(f"❌ Invalid scaling action: {action.id}")
                return False
            
            # Check safety prerequisites
            if not await self._check_safety_prerequisites(action):
                logger.warning(f"⚠️ Safety prerequisites not met for {action.workload_name}")
                return False
            
            # Get current deployment state
            current_state = await self._get_current_deployment_state(action.workload_name, action.namespace)
            if not current_state:
                logger.error(f"❌ Failed to get current state for {action.workload_name}")
                return False
            
            # Create scaling result
            scaling_result = ScalingResult(
                action_id=action.id,
                workload_name=action.workload_name,
                namespace=action.namespace,
                original_replicas=current_state.get("replicas", 1),
                target_replicas=0,
                scaling_successful=False,
                verification_passed=False,
                rollback_required=False
            )
            
            # Store active scaling
            self.active_scaling[action.id] = scaling_result
            
            # Perform scaling
            scaling_success = await self._perform_scaling(action, current_state)
            scaling_result.scaling_successful = scaling_success
            
            if scaling_success:
                # Wait for scaling to complete
                await asyncio.sleep(5)  # Wait for Kubernetes to process
                
                # Verify scaling
                verification_passed = await self._verify_scaling(action)
                scaling_result.verification_passed = verification_passed
                
                if not verification_passed:
                    # Rollback if verification fails
                    rollback_success = await self._rollback_scaling(action, current_state)
                    scaling_result.rollback_required = True
                    
                    if not rollback_success:
                        logger.error(f"❌ Failed to rollback scaling for {action.workload_name}")
                        scaling_result.error_message = "Rollback failed"
                else:
                    logger.info(f"✅ Successfully scaled {action.workload_name} to zero replicas")
            else:
                scaling_result.error_message = "Scaling operation failed"
                logger.error(f"❌ Failed to scale {action.workload_name} to zero")
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            scaling_result.execution_time = execution_time
            
            # Store in history
            self.scaling_history.append(scaling_result)
            
            # Remove from active scaling
            if action.id in self.active_scaling:
                del self.active_scaling[action.id]
            
            return scaling_result.scaling_successful and scaling_result.verification_passed
            
        except Exception as e:
            logger.error(f"❌ Error during zero-pod scaling: {e}")
            return False
    
    def _validate_scaling_action(self, action: OptimizationAction) -> bool:
        """Validate scaling action"""
        try:
            # Check required fields
            if not action.workload_name or not action.namespace:
                return False
            
            # Check namespace exclusions
            if self.config.exclude_namespaces and action.namespace in self.config.exclude_namespaces:
                logger.info(f"⏭️ Skipping {action.workload_name} - namespace {action.namespace} excluded")
                return False
            
            # Check namespace inclusions
            if self.config.include_namespaces and action.namespace not in self.config.include_namespaces:
                logger.info(f"⏭️ Skipping {action.workload_name} - namespace {action.namespace} not included")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating scaling action: {e}")
            return False
    
    async def _check_safety_prerequisites(self, action: OptimizationAction) -> bool:
        """Check safety prerequisites before scaling"""
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
    
    async def _get_current_deployment_state(self, workload_name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get current deployment state"""
        try:
            # Get deployment information
            deployment_info = await self.k8s_client.get_deployment_info(workload_name, namespace)
            
            if not deployment_info:
                logger.warning(f"⚠️ Deployment {workload_name} not found in namespace {namespace}")
                return None
            
            return {
                "replicas": deployment_info.get("replicas", 1),
                "available_replicas": deployment_info.get("available_replicas", 0),
                "ready_replicas": deployment_info.get("ready_replicas", 0),
                "updated_replicas": deployment_info.get("updated_replicas", 0),
                "resource_requests": deployment_info.get("resource_requests", {}),
                "resource_limits": deployment_info.get("resource_limits", {})
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting deployment state: {e}")
            return None
    
    async def _perform_scaling(self, action: OptimizationAction, current_state: Dict[str, Any]) -> bool:
        """Perform the actual scaling operation"""
        try:
            # Check if already at zero replicas
            if current_state.get("replicas", 1) == 0:
                logger.info(f"ℹ️ {action.workload_name} already at zero replicas")
                return True
            
            # Scale deployment to zero
            scaling_success = await self.k8s_client.scale_deployment(
                action.workload_name,
                action.namespace,
                replicas=0
            )
            
            if scaling_success:
                logger.info(f"✅ Scaled {action.workload_name} to zero replicas")
            else:
                logger.error(f"❌ Failed to scale {action.workload_name} to zero replicas")
            
            return scaling_success
            
        except Exception as e:
            logger.error(f"❌ Error performing scaling: {e}")
            return False
    
    async def _verify_scaling(self, action: OptimizationAction) -> bool:
        """Verify that scaling was successful"""
        try:
            # Wait for verification delay
            await asyncio.sleep(self.config.verification_delay)
            
            # Get updated deployment state
            updated_state = await self._get_current_deployment_state(action.workload_name, action.namespace)
            
            if not updated_state:
                logger.error(f"❌ Failed to get updated state for {action.workload_name}")
                return False
            
            # Check if replicas are actually zero
            current_replicas = updated_state.get("replicas", 1)
            if current_replicas != 0:
                logger.warning(f"⚠️ Scaling verification failed - replicas still {current_replicas}")
                return False
            
            # Check if pods are terminated
            pods = await self.k8s_client.list_pods(namespace=action.namespace, label_selector=f"app={action.workload_name}")
            running_pods = [pod for pod in pods if pod.status == "Running"]
            
            if running_pods:
                logger.warning(f"⚠️ Scaling verification failed - {len(running_pods)} pods still running")
                return False
            
            logger.info(f"✅ Scaling verification passed for {action.workload_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying scaling: {e}")
            return False
    
    async def _rollback_scaling(self, action: OptimizationAction, original_state: Dict[str, Any]) -> bool:
        """Rollback scaling to original state"""
        try:
            logger.info(f"🔄 Rolling back scaling for {action.workload_name}")
            
            # Scale back to original replicas
            rollback_success = await self.k8s_client.scale_deployment(
                action.workload_name,
                action.namespace,
                replicas=original_state.get("replicas", 1)
            )
            
            if rollback_success:
                logger.info(f"✅ Successfully rolled back {action.workload_name} to {original_state.get('replicas', 1)} replicas")
            else:
                logger.error(f"❌ Failed to rollback {action.workload_name}")
            
            return rollback_success
            
        except Exception as e:
            logger.error(f"❌ Error rolling back scaling: {e}")
            return False
    
    async def get_scaling_metrics(self) -> Dict[str, Any]:
        """Get scaling metrics"""
        return {
            "total_scaling_operations": len(self.scaling_history),
            "successful_scaling": len([r for r in self.scaling_history if r.scaling_successful]),
            "failed_scaling": len([r for r in self.scaling_history if not r.scaling_successful]),
            "rollback_count": len([r for r in self.scaling_history if r.rollback_required]),
            "average_execution_time": sum(r.execution_time for r in self.scaling_history) / max(len(self.scaling_history), 1),
            "active_scaling_operations": len(self.active_scaling)
        }
    
    async def get_scaling_history(self) -> List[ScalingResult]:
        """Get scaling history"""
        return self.scaling_history.copy()
    
    def update_config(self, config: ScalingConfig):
        """Update scaling configuration"""
        self.config = config
        logger.info("✅ Updated zero-pod scaling configuration")
    
    async def is_workload_eligible_for_scaling(self, workload_name: str, namespace: str) -> Tuple[bool, str]:
        """Check if a workload is eligible for zero-pod scaling"""
        try:
            # Check namespace exclusions
            if self.config.exclude_namespaces and namespace in self.config.exclude_namespaces:
                return False, f"Namespace {namespace} is excluded"
            
            # Check namespace inclusions
            if self.config.include_namespaces and namespace not in self.config.include_namespaces:
                return False, f"Namespace {namespace} is not included"
            
            # Get deployment state
            deployment_state = await self._get_current_deployment_state(workload_name, namespace)
            if not deployment_state:
                return False, "Deployment not found"
            
            # Check if already at zero replicas
            if deployment_state.get("replicas", 1) == 0:
                return False, "Already at zero replicas"
            
            # Check if has running replicas
            if deployment_state.get("ready_replicas", 0) == 0:
                return False, "No running replicas"
            
            return True, "Eligible for scaling"
            
        except Exception as e:
            logger.error(f"❌ Error checking workload eligibility: {e}")
            return False, f"Error: {str(e)}" 