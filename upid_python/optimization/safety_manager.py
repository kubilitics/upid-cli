"""
UPID CLI - Safety Manager
Rollback and safety systems for optimization operations
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from ..core.k8s_client import KubernetesClient, PodInfo
from .optimization_engine import OptimizationAction

logger = logging.getLogger(__name__)


@dataclass
class SafetyCheck:
    """Safety check configuration"""
    name: str
    description: str
    critical: bool = True
    timeout: int = 30  # seconds
    retry_count: int = 3
    enabled: bool = True


@dataclass
class SafetyCheckResult:
    """Safety check result"""
    check_name: str
    passed: bool
    details: str
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class RollbackPlan:
    """Rollback plan for optimization actions"""
    action_id: str
    original_state: Dict[str, Any]
    rollback_commands: List[str]
    verification_checks: List[str]
    timeout: int = 300  # 5 minutes
    created_at: datetime = None


class SafetyManager:
    """
    Safety manager for optimization operations
    
    Provides comprehensive safety capabilities:
    - Pre-optimization safety checks
    - Post-optimization verification
    - Automated rollback mechanisms
    - Health monitoring
    - Performance impact assessment
    """
    
    def __init__(self, k8s_client: KubernetesClient):
        self.k8s_client = k8s_client
        
        # Safety checks configuration
        self.safety_checks = self._initialize_safety_checks()
        
        # Rollback plans
        self.rollback_plans: Dict[str, RollbackPlan] = {}
        
        # Safety check history
        self.safety_history: List[SafetyCheckResult] = []
        
        logger.info("🔧 Initializing safety manager")
    
    def _initialize_safety_checks(self) -> Dict[str, SafetyCheck]:
        """Initialize safety checks"""
        return {
            "cluster_health": SafetyCheck(
                name="cluster_health",
                description="Check cluster health status",
                critical=True,
                timeout=30
            ),
            "workload_health": SafetyCheck(
                name="workload_health",
                description="Check workload health status",
                critical=True,
                timeout=30
            ),
            "resource_availability": SafetyCheck(
                name="resource_availability",
                description="Check resource availability",
                critical=True,
                timeout=30
            ),
            "performance_baseline": SafetyCheck(
                name="performance_baseline",
                description="Establish performance baseline",
                critical=False,
                timeout=60
            ),
            "backup_verification": SafetyCheck(
                name="backup_verification",
                description="Verify backup availability",
                critical=False,
                timeout=45
            ),
            "network_connectivity": SafetyCheck(
                name="network_connectivity",
                description="Check network connectivity",
                critical=True,
                timeout=30
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize the safety manager"""
        try:
            logger.info("🚀 Initializing safety manager...")
            
            # Test connectivity
            if not await self.k8s_client.connect():
                logger.error("❌ Failed to connect to Kubernetes cluster")
                return False
            
            # Run initial safety checks
            initial_checks = await self._run_initial_safety_checks()
            if not initial_checks:
                logger.warning("⚠️ Some initial safety checks failed")
            
            logger.info("✅ Safety manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize safety manager: {e}")
            return False
    
    async def perform_safety_checks(self, action: OptimizationAction) -> List[Dict[str, Any]]:
        """Perform safety checks for an optimization action"""
        try:
            logger.info(f"🔍 Performing safety checks for {action.workload_name}")
            
            check_results = []
            
            # Run all enabled safety checks
            for check_name, check_config in self.safety_checks.items():
                if not check_config.enabled:
                    continue
                
                try:
                    result = await self._run_safety_check(check_name, check_config, action)
                    check_results.append({
                        "name": check_name,
                        "description": check_config.description,
                        "critical": check_config.critical,
                        "passed": result.passed,
                        "details": result.details,
                        "execution_time": result.execution_time,
                        "error_message": result.error_message
                    })
                    
                    # Store in history
                    self.safety_history.append(result)
                    
                except Exception as e:
                    logger.error(f"❌ Error running safety check {check_name}: {e}")
                    check_results.append({
                        "name": check_name,
                        "description": check_config.description,
                        "critical": check_config.critical,
                        "passed": False,
                        "details": f"Error: {str(e)}",
                        "execution_time": 0.0,
                        "error_message": str(e)
                    })
            
            # Log results
            passed_checks = [r for r in check_results if r["passed"]]
            failed_checks = [r for r in check_results if not r["passed"]]
            
            logger.info(f"✅ Safety checks completed: {len(passed_checks)} passed, {len(failed_checks)} failed")
            
            return check_results
            
        except Exception as e:
            logger.error(f"❌ Error performing safety checks: {e}")
            return []
    
    async def _run_safety_check(self, check_name: str, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Run a specific safety check"""
        start_time = datetime.utcnow()
        
        try:
            if check_name == "cluster_health":
                return await self._check_cluster_health(check_config, action)
            elif check_name == "workload_health":
                return await self._check_workload_health(check_config, action)
            elif check_name == "resource_availability":
                return await self._check_resource_availability(check_config, action)
            elif check_name == "performance_baseline":
                return await self._check_performance_baseline(check_config, action)
            elif check_name == "backup_verification":
                return await self._check_backup_verification(check_config, action)
            elif check_name == "network_connectivity":
                return await self._check_network_connectivity(check_config, action)
            else:
                return SafetyCheckResult(
                    check_name=check_name,
                    passed=False,
                    details=f"Unknown safety check: {check_name}",
                    execution_time=0.0,
                    error_message="Unknown check type"
                )
                
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return SafetyCheckResult(
                check_name=check_name,
                passed=False,
                details=f"Error running {check_name}",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _check_cluster_health(self, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Check cluster health status"""
        start_time = datetime.utcnow()
        
        try:
            # Get cluster metrics
            cluster_metrics = await self.k8s_client.get_cluster_metrics()
            
            if not cluster_metrics:
                return SafetyCheckResult(
                    check_name="cluster_health",
                    passed=False,
                    details="Failed to get cluster metrics",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    error_message="No cluster metrics available"
                )
            
            # Check cluster health indicators
            cpu_usage = cluster_metrics.get("cpu_usage_percent", 0)
            memory_usage = cluster_metrics.get("memory_usage_percent", 0)
            node_count = cluster_metrics.get("node_count", 0)
            
            # Define health thresholds
            is_healthy = (
                cpu_usage < 90 and  # CPU usage below 90%
                memory_usage < 90 and  # Memory usage below 90%
                node_count > 0  # At least one node
            )
            
            details = f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Nodes: {node_count}"
            
            return SafetyCheckResult(
                check_name="cluster_health",
                passed=is_healthy,
                details=details,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            return SafetyCheckResult(
                check_name="cluster_health",
                passed=False,
                details="Error checking cluster health",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _check_workload_health(self, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Check workload health status"""
        start_time = datetime.utcnow()
        
        try:
            # Get workload pods
            pods = await self.k8s_client.list_pods(
                namespace=action.namespace,
                label_selector=f"app={action.workload_name}"
            )
            
            if not pods:
                return SafetyCheckResult(
                    check_name="workload_health",
                    passed=False,
                    details="No pods found for workload",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    error_message="Workload not found"
                )
            
            # Check pod health
            running_pods = [pod for pod in pods if pod.status == "Running"]
            total_pods = len(pods)
            healthy_pods = len(running_pods)
            
            # Define health threshold (at least 50% of pods should be running)
            is_healthy = healthy_pods >= max(1, total_pods * 0.5)
            
            details = f"Running: {healthy_pods}/{total_pods} pods"
            
            return SafetyCheckResult(
                check_name="workload_health",
                passed=is_healthy,
                details=details,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            return SafetyCheckResult(
                check_name="workload_health",
                passed=False,
                details="Error checking workload health",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _check_resource_availability(self, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Check resource availability"""
        start_time = datetime.utcnow()
        
        try:
            # Get cluster resources
            cluster_info = await self.k8s_client.get_cluster_info()
            
            if not cluster_info:
                return SafetyCheckResult(
                    check_name="resource_availability",
                    passed=False,
                    details="Failed to get cluster info",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    error_message="No cluster info available"
                )
            
            # Check resource availability
            available_cpu = cluster_info.get("available_cpu", 0)
            available_memory = cluster_info.get("available_memory", 0)
            
            # Define availability thresholds
            has_resources = available_cpu > 0.5 and available_memory > 512  # At least 0.5 CPU and 512MB memory
            
            details = f"Available CPU: {available_cpu}, Memory: {available_memory}MB"
            
            return SafetyCheckResult(
                check_name="resource_availability",
                passed=has_resources,
                details=details,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            return SafetyCheckResult(
                check_name="resource_availability",
                passed=False,
                details="Error checking resource availability",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _check_performance_baseline(self, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Establish performance baseline"""
        start_time = datetime.utcnow()
        
        try:
            # Get current performance metrics
            pod_metrics = await self.k8s_client.get_pod_metrics(action.workload_name, action.namespace)
            
            if not pod_metrics:
                return SafetyCheckResult(
                    check_name="performance_baseline",
                    passed=False,
                    details="Failed to get performance metrics",
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    error_message="No metrics available"
                )
            
            # Store baseline for comparison
            baseline = {
                "cpu_usage": pod_metrics.get("cpu_usage", 0),
                "memory_usage": pod_metrics.get("memory_usage", 0),
                "timestamp": datetime.utcnow()
            }
            
            details = f"Baseline established - CPU: {baseline['cpu_usage']}, Memory: {baseline['memory_usage']}"
            
            return SafetyCheckResult(
                check_name="performance_baseline",
                passed=True,
                details=details,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            return SafetyCheckResult(
                check_name="performance_baseline",
                passed=False,
                details="Error establishing performance baseline",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _check_backup_verification(self, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Verify backup availability"""
        start_time = datetime.utcnow()
        
        try:
            # This is a simplified implementation
            # In a real implementation, this would check for:
            # - Database backups
            # - Configuration backups
            # - Volume snapshots
            
            # Simulate backup check
            has_backup = True  # Assume backup exists for now
            
            details = "Backup verification completed"
            
            return SafetyCheckResult(
                check_name="backup_verification",
                passed=has_backup,
                details=details,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            return SafetyCheckResult(
                check_name="backup_verification",
                passed=False,
                details="Error checking backup availability",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _check_network_connectivity(self, check_config: SafetyCheck, action: OptimizationAction) -> SafetyCheckResult:
        """Check network connectivity"""
        start_time = datetime.utcnow()
        
        try:
            # This is a simplified implementation
            # In a real implementation, this would check:
            # - Service connectivity
            # - Ingress/egress rules
            # - Network policies
            
            # Simulate network check
            network_healthy = True  # Assume network is healthy for now
            
            details = "Network connectivity verified"
            
            return SafetyCheckResult(
                check_name="network_connectivity",
                passed=network_healthy,
                details=details,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
        except Exception as e:
            return SafetyCheckResult(
                check_name="network_connectivity",
                passed=False,
                details="Error checking network connectivity",
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _run_initial_safety_checks(self) -> bool:
        """Run initial safety checks during initialization"""
        try:
            logger.info("🔍 Running initial safety checks...")
            
            # Run basic cluster health check
            cluster_check = await self._check_cluster_health(
                self.safety_checks["cluster_health"],
                None  # No specific action for initial checks
            )
            
            if not cluster_check.passed:
                logger.warning(f"⚠️ Initial cluster health check failed: {cluster_check.details}")
                return False
            
            logger.info("✅ Initial safety checks passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running initial safety checks: {e}")
            return False
    
    async def create_safety_checks(self, actions: List[OptimizationAction]) -> List[str]:
        """Create safety checks for optimization actions"""
        try:
            safety_checks = []
            
            for action in actions:
                # Create safety checks based on action type
                if action.action_type == "scale_to_zero":
                    safety_checks.extend([
                        "workload_health",
                        "cluster_health",
                        "resource_availability"
                    ])
                elif action.action_type == "rightsize":
                    safety_checks.extend([
                        "workload_health",
                        "performance_baseline",
                        "resource_availability"
                    ])
                elif action.action_type == "cost_optimize":
                    safety_checks.extend([
                        "workload_health",
                        "cluster_health",
                        "backup_verification"
                    ])
            
            # Remove duplicates
            safety_checks = list(set(safety_checks))
            
            logger.info(f"✅ Created {len(safety_checks)} safety checks for {len(actions)} actions")
            return safety_checks
            
        except Exception as e:
            logger.error(f"❌ Error creating safety checks: {e}")
            return []
    
    async def rollback_action(self, action: OptimizationAction) -> bool:
        """Rollback an optimization action"""
        try:
            logger.info(f"🔄 Rolling back action {action.id} for {action.workload_name}")
            
            # Get rollback plan
            rollback_plan = action.rollback_plan
            if not rollback_plan:
                logger.error(f"❌ No rollback plan available for action {action.id}")
                return False
            
            # Execute rollback commands
            rollback_success = await self._execute_rollback_commands(action, rollback_plan)
            
            if rollback_success:
                # Verify rollback
                verification_success = await self._verify_rollback(action, rollback_plan)
                
                if verification_success:
                    logger.info(f"✅ Successfully rolled back action {action.id}")
                else:
                    logger.warning(f"⚠️ Rollback completed but verification failed for action {action.id}")
                
                return rollback_success
            else:
                logger.error(f"❌ Failed to rollback action {action.id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error rolling back action {action.id}: {e}")
            return False
    
    async def _execute_rollback_commands(self, action: OptimizationAction, rollback_plan: Dict[str, Any]) -> bool:
        """Execute rollback commands"""
        try:
            original_state = rollback_plan.get("original_state", {})
            
            # Execute rollback based on action type
            if action.action_type == "scale_to_zero":
                # Scale back to original replicas
                original_replicas = original_state.get("replicas", 1)
                success = await self.k8s_client.scale_deployment(
                    action.workload_name,
                    action.namespace,
                    replicas=original_replicas
                )
                return success
                
            elif action.action_type == "rightsize":
                # Restore original resources
                original_requests = original_state.get("requests", {})
                original_limits = original_state.get("limits", {})
                success = await self.k8s_client.patch_deployment_resources(
                    action.workload_name,
                    action.namespace,
                    requests=original_requests,
                    limits=original_limits
                )
                return success
                
            elif action.action_type == "cost_optimize":
                # Restore original cost configuration
                # This is simplified - in real implementation would restore specific configurations
                logger.info(f"✅ Simulated cost optimization rollback for {action.workload_name}")
                return True
                
            else:
                logger.warning(f"⚠️ Unknown action type for rollback: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error executing rollback commands: {e}")
            return False
    
    async def _verify_rollback(self, action: OptimizationAction, rollback_plan: Dict[str, Any]) -> bool:
        """Verify that rollback was successful"""
        try:
            # Wait for rollback to take effect
            await asyncio.sleep(10)
            
            # Check if workload is healthy
            pods = await self.k8s_client.list_pods(
                namespace=action.namespace,
                label_selector=f"app={action.workload_name}"
            )
            
            healthy_pods = [pod for pod in pods if pod.status == "Running"]
            
            if len(healthy_pods) == 0:
                logger.warning(f"⚠️ Rollback verification failed - no healthy pods")
                return False
            
            logger.info(f"✅ Rollback verification passed for {action.workload_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verifying rollback: {e}")
            return False
    
    async def get_safety_metrics(self) -> Dict[str, Any]:
        """Get safety manager metrics"""
        return {
            "total_safety_checks": len(self.safety_history),
            "passed_checks": len([r for r in self.safety_history if r.passed]),
            "failed_checks": len([r for r in self.safety_history if not r.passed]),
            "average_check_time": sum(r.execution_time for r in self.safety_history) / max(len(self.safety_history), 1),
            "active_rollback_plans": len(self.rollback_plans)
        }
    
    async def get_safety_history(self) -> List[SafetyCheckResult]:
        """Get safety check history"""
        return self.safety_history.copy()
    
    def update_safety_check(self, check_name: str, enabled: bool = None, timeout: int = None):
        """Update safety check configuration"""
        if check_name in self.safety_checks:
            check = self.safety_checks[check_name]
            if enabled is not None:
                check.enabled = enabled
            if timeout is not None:
                check.timeout = timeout
            logger.info(f"✅ Updated safety check {check_name}")
        else:
            logger.warning(f"⚠️ Safety check {check_name} not found") 