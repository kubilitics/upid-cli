#!/usr/bin/env python3
"""
UPID CLI - Deployment Validator
Phase 6: Platform Integration - Task 6.1
Enterprise-grade deployment validation and rollback system
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

from .pipeline_manager import PipelineManager, PipelineConfig, TriggerType, PipelineType
from ..core.metrics_collector import MetricsCollector
from ..core.resource_analyzer import ResourceAnalyzer

logger = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
    """Deployment validation status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"
    TIMEOUT = "timeout"


@dataclass
class ValidationConfig:
    """Deployment validation configuration"""
    pre_deployment_analysis: bool = True
    post_deployment_validation: bool = True
    cost_impact_analysis: bool = True
    performance_validation: bool = True
    security_scanning: bool = True
    health_check_timeout: int = 300  # 5 minutes
    rollback_threshold: float = 0.8  # 80% health threshold
    cost_threshold: float = 1000.0  # $1000 cost threshold
    notification_channels: List[str] = None
    auto_rollback: bool = True
    dry_run_first: bool = True


@dataclass
class DeploymentValidation:
    """Deployment validation configuration"""
    deployment_name: str
    namespace: str
    cluster_id: str
    manifest_path: str
    validation_config: ValidationConfig
    pre_deployment_state: Dict[str, Any]
    post_deployment_state: Dict[str, Any]
    validation_results: Dict[str, Any]
    rollback_triggered: bool = False
    rollback_reason: Optional[str] = None


class ValidationRule:
    """Base class for validation rules"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate deployment according to rule"""
        raise NotImplementedError


class CostImpactRule(ValidationRule):
    """Validate cost impact of deployment"""
    
    def __init__(self):
        super().__init__("cost_impact", "Validate deployment cost impact")
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate cost impact"""
        try:
            # Get pre-deployment cost
            pre_cost = await self._get_cluster_cost(deployment.cluster_id, deployment.namespace)
            
            # Get post-deployment cost
            post_cost = await self._get_cluster_cost(deployment.cluster_id, deployment.namespace)
            
            cost_increase = post_cost - pre_cost
            cost_threshold = deployment.validation_config.cost_threshold
            
            return {
                "passed": cost_increase <= cost_threshold,
                "pre_cost": pre_cost,
                "post_cost": post_cost,
                "cost_increase": cost_increase,
                "threshold": cost_threshold,
                "message": f"Cost increase: ${cost_increase:.2f} (threshold: ${cost_threshold:.2f})"
            }
            
        except Exception as e:
            logger.error(f"Cost impact validation failed: {e}")
            return {
                "passed": False,
                "error": str(e),
                "message": "Failed to validate cost impact"
            }
    
    async def _get_cluster_cost(self, cluster_id: str, namespace: str) -> float:
        """Get cluster cost for namespace"""
        try:
            result = await self._run_command([
                "upid", "analyze", "cost", "--cluster-id", cluster_id,
                "--namespace", namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("monthly_cost", 0.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to get cluster cost: {e}")
            return 0.0
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()


class PerformanceRule(ValidationRule):
    """Validate deployment performance impact"""
    
    def __init__(self):
        super().__init__("performance", "Validate deployment performance impact")
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate performance impact"""
        try:
            # Get pre-deployment performance metrics
            pre_metrics = await self._get_performance_metrics(deployment.cluster_id, deployment.namespace)
            
            # Get post-deployment performance metrics
            post_metrics = await self._get_performance_metrics(deployment.cluster_id, deployment.namespace)
            
            # Calculate performance impact
            cpu_impact = post_metrics.get("cpu_usage", 0) - pre_metrics.get("cpu_usage", 0)
            memory_impact = post_metrics.get("memory_usage", 0) - pre_metrics.get("memory_usage", 0)
            
            # Define thresholds
            cpu_threshold = 20.0  # 20% CPU increase
            memory_threshold = 30.0  # 30% memory increase
            
            cpu_passed = cpu_impact <= cpu_threshold
            memory_passed = memory_impact <= memory_threshold
            
            return {
                "passed": cpu_passed and memory_passed,
                "cpu_impact": cpu_impact,
                "memory_impact": memory_impact,
                "cpu_threshold": cpu_threshold,
                "memory_threshold": memory_threshold,
                "message": f"CPU: {cpu_impact:.1f}% (threshold: {cpu_threshold}%), Memory: {memory_impact:.1f}% (threshold: {memory_threshold}%)"
            }
            
        except Exception as e:
            logger.error(f"Performance validation failed: {e}")
            return {
                "passed": False,
                "error": str(e),
                "message": "Failed to validate performance impact"
            }
    
    async def _get_performance_metrics(self, cluster_id: str, namespace: str) -> Dict[str, float]:
        """Get performance metrics for namespace"""
        try:
            result = await self._run_command([
                "upid", "analyze", "performance", "--cluster-id", cluster_id,
                "--namespace", namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "cpu_usage": data.get("cpu_usage_percent", 0.0),
                    "memory_usage": data.get("memory_usage_percent", 0.0),
                    "network_usage": data.get("network_usage_mbps", 0.0)
                }
            
            return {"cpu_usage": 0.0, "memory_usage": 0.0, "network_usage": 0.0}
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"cpu_usage": 0.0, "memory_usage": 0.0, "network_usage": 0.0}
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()


class SecurityRule(ValidationRule):
    """Validate deployment security"""
    
    def __init__(self):
        super().__init__("security", "Validate deployment security")
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate security"""
        try:
            # Run security scan
            security_results = await self._run_security_scan(deployment.manifest_path)
            
            # Check for critical vulnerabilities
            critical_vulns = security_results.get("critical_vulnerabilities", 0)
            high_vulns = security_results.get("high_vulnerabilities", 0)
            
            # Define thresholds
            critical_threshold = 0
            high_threshold = 2
            
            critical_passed = critical_vulns <= critical_threshold
            high_passed = high_vulns <= high_threshold
            
            return {
                "passed": critical_passed and high_passed,
                "critical_vulnerabilities": critical_vulns,
                "high_vulnerabilities": high_vulns,
                "critical_threshold": critical_threshold,
                "high_threshold": high_threshold,
                "message": f"Critical: {critical_vulns}, High: {high_vulns}"
            }
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {
                "passed": False,
                "error": str(e),
                "message": "Failed to validate security"
            }
    
    async def _run_security_scan(self, manifest_path: str) -> Dict[str, Any]:
        """Run security scan on manifests"""
        try:
            # Use trivy for security scanning
            result = await self._run_command([
                "trivy", "config", manifest_path, "--format", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "critical_vulnerabilities": len([v for v in data.get("vulnerabilities", []) if v.get("severity") == "CRITICAL"]),
                    "high_vulnerabilities": len([v for v in data.get("vulnerabilities", []) if v.get("severity") == "HIGH"]),
                    "medium_vulnerabilities": len([v for v in data.get("vulnerabilities", []) if v.get("severity") == "MEDIUM"]),
                    "low_vulnerabilities": len([v for v in data.get("vulnerabilities", []) if v.get("severity") == "LOW"])
                }
            
            return {"critical_vulnerabilities": 0, "high_vulnerabilities": 0, "medium_vulnerabilities": 0, "low_vulnerabilities": 0}
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {"critical_vulnerabilities": 0, "high_vulnerabilities": 0, "medium_vulnerabilities": 0, "low_vulnerabilities": 0}
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()


class HealthCheckRule(ValidationRule):
    """Validate deployment health"""
    
    def __init__(self):
        super().__init__("health_check", "Validate deployment health")
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate deployment health"""
        try:
            # Check deployment status
            deployment_status = await self._get_deployment_status(deployment.deployment_name, deployment.namespace)
            
            # Check pod health
            pod_health = await self._get_pod_health(deployment.deployment_name, deployment.namespace)
            
            # Check service health
            service_health = await self._get_service_health(deployment.deployment_name, deployment.namespace)
            
            # Calculate overall health score
            health_score = (deployment_status.get("ready_replicas", 0) / max(deployment_status.get("replicas", 1), 1)) * 100
            health_threshold = deployment.validation_config.rollback_threshold * 100
            
            return {
                "passed": health_score >= health_threshold,
                "health_score": health_score,
                "health_threshold": health_threshold,
                "deployment_status": deployment_status,
                "pod_health": pod_health,
                "service_health": service_health,
                "message": f"Health score: {health_score:.1f}% (threshold: {health_threshold:.1f}%)"
            }
            
        except Exception as e:
            logger.error(f"Health check validation failed: {e}")
            return {
                "passed": False,
                "error": str(e),
                "message": "Failed to validate health"
            }
    
    async def _get_deployment_status(self, deployment_name: str, namespace: str) -> Dict[str, Any]:
        """Get deployment status"""
        try:
            result = await self._run_command([
                "kubectl", "get", "deployment", deployment_name,
                "-n", namespace, "-o", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "replicas": data.get("spec", {}).get("replicas", 0),
                    "ready_replicas": data.get("status", {}).get("readyReplicas", 0),
                    "available_replicas": data.get("status", {}).get("availableReplicas", 0),
                    "updated_replicas": data.get("status", {}).get("updatedReplicas", 0)
                }
            
            return {"replicas": 0, "ready_replicas": 0, "available_replicas": 0, "updated_replicas": 0}
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {"replicas": 0, "ready_replicas": 0, "available_replicas": 0, "updated_replicas": 0}
    
    async def _get_pod_health(self, deployment_name: str, namespace: str) -> Dict[str, Any]:
        """Get pod health status"""
        try:
            result = await self._run_command([
                "kubectl", "get", "pods", "-l", f"app={deployment_name}",
                "-n", namespace, "-o", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                pods = data.get("items", [])
                
                total_pods = len(pods)
                ready_pods = len([p for p in pods if p.get("status", {}).get("phase") == "Running"])
                
                return {
                    "total_pods": total_pods,
                    "ready_pods": ready_pods,
                    "health_percentage": (ready_pods / max(total_pods, 1)) * 100
                }
            
            return {"total_pods": 0, "ready_pods": 0, "health_percentage": 0}
            
        except Exception as e:
            logger.error(f"Failed to get pod health: {e}")
            return {"total_pods": 0, "ready_pods": 0, "health_percentage": 0}
    
    async def _get_service_health(self, deployment_name: str, namespace: str) -> Dict[str, Any]:
        """Get service health status"""
        try:
            result = await self._run_command([
                "kubectl", "get", "service", deployment_name,
                "-n", namespace, "-o", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "type": data.get("spec", {}).get("type", "ClusterIP"),
                    "cluster_ip": data.get("spec", {}).get("clusterIP", ""),
                    "external_ip": data.get("status", {}).get("loadBalancer", {}).get("ingress", [{}])[0].get("ip", "")
                }
            
            return {"type": "Unknown", "cluster_ip": "", "external_ip": ""}
            
        except Exception as e:
            logger.error(f"Failed to get service health: {e}")
            return {"type": "Unknown", "cluster_ip": "", "external_ip": ""}
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()


class DeploymentValidator:
    """
    Enterprise-grade deployment validator
    
    Features:
    - Pre-deployment analysis
    - Post-deployment validation
    - Cost impact analysis
    - Performance validation
    - Security scanning
    - Health monitoring
    - Automated rollback
    - Multi-rule validation system
    """
    
    def __init__(self, pipeline_manager: PipelineManager, config: ValidationConfig):
        self.pipeline_manager = pipeline_manager
        self.config = config
        
        # Validation rules
        self.validation_rules: List[ValidationRule] = [
            CostImpactRule(),
            PerformanceRule(),
            SecurityRule(),
            HealthCheckRule()
        ]
        
        # Validation storage
        self.validations: Dict[str, DeploymentValidation] = {}
        self.validation_history: List[DeploymentValidation] = []
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.active_validations: Dict[str, threading.Thread] = {}
        
        logger.info("🔧 Initializing deployment validator")
    
    async def initialize(self) -> bool:
        """Initialize deployment validator"""
        try:
            logger.info("🚀 Initializing deployment validator...")
            
            # Validate configuration
            await self._validate_configuration()
            
            # Setup validation rules
            await self._setup_validation_rules()
            
            logger.info("✅ Deployment validator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize deployment validator: {e}")
            return False
    
    async def _validate_configuration(self):
        """Validate validator configuration"""
        if not self.config.pre_deployment_analysis and not self.config.post_deployment_validation:
            raise ValueError("At least one validation phase must be enabled")
        
        if self.config.health_check_timeout < 60:
            logger.warning("Health check timeout is very short (< 60s)")
        
        if self.config.rollback_threshold < 0.5:
            logger.warning("Rollback threshold is very low (< 50%)")
    
    async def _setup_validation_rules(self):
        """Setup validation rules"""
        logger.info(f"🔧 Setting up {len(self.validation_rules)} validation rules")
        
        for rule in self.validation_rules:
            logger.info(f"  - {rule.name}: {rule.description}")
    
    async def validate_deployment(self, deployment_name: str, namespace: str, cluster_id: str, 
                                manifest_path: str) -> Dict[str, Any]:
        """Validate a deployment"""
        try:
            logger.info(f"🔍 Starting deployment validation: {deployment_name}")
            
            # Create validation object
            validation = DeploymentValidation(
                deployment_name=deployment_name,
                namespace=namespace,
                cluster_id=cluster_id,
                manifest_path=manifest_path,
                validation_config=self.config,
                pre_deployment_state={},
                post_deployment_state={},
                validation_results={}
            )
            
            # Store validation
            self.validations[deployment_name] = validation
            
            # Run pre-deployment analysis
            if self.config.pre_deployment_analysis:
                await self._run_pre_deployment_analysis(validation)
            
            # Run post-deployment validation
            if self.config.post_deployment_validation:
                await self._run_post_deployment_validation(validation)
            
            # Determine overall validation result
            overall_result = await self._determine_validation_result(validation)
            
            # Store in history
            self.validation_history.append(validation)
            
            logger.info(f"✅ Deployment validation completed: {deployment_name}")
            return overall_result
            
        except Exception as e:
            logger.error(f"❌ Deployment validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_name": deployment_name,
                "validation_results": {}
            }
    
    async def _run_pre_deployment_analysis(self, validation: DeploymentValidation):
        """Run pre-deployment analysis"""
        logger.info(f"📊 Running pre-deployment analysis for {validation.deployment_name}")
        
        # Capture pre-deployment state
        validation.pre_deployment_state = await self._capture_cluster_state(
            validation.cluster_id, validation.namespace
        )
        
        # Run validation rules
        pre_results = {}
        for rule in self.validation_rules:
            if rule.name in ["cost_impact", "security"]:
                result = await rule.validate(validation)
                pre_results[rule.name] = result
        
        validation.validation_results["pre_deployment"] = pre_results
    
    async def _run_post_deployment_validation(self, validation: DeploymentValidation):
        """Run post-deployment validation"""
        logger.info(f"🔍 Running post-deployment validation for {validation.deployment_name}")
        
        # Wait for deployment to stabilize
        await asyncio.sleep(30)
        
        # Capture post-deployment state
        validation.post_deployment_state = await self._capture_cluster_state(
            validation.cluster_id, validation.namespace
        )
        
        # Run validation rules
        post_results = {}
        for rule in self.validation_rules:
            result = await rule.validate(validation)
            post_results[rule.name] = result
            
            # Check if rollback is needed
            if not result.get("passed", True) and self.config.auto_rollback:
                await self._trigger_rollback(validation, rule.name, result.get("message", "Validation failed"))
        
        validation.validation_results["post_deployment"] = post_results
    
    async def _capture_cluster_state(self, cluster_id: str, namespace: str) -> Dict[str, Any]:
        """Capture cluster state"""
        try:
            # Get deployment status
            deployment_status = await self._run_command([
                "kubectl", "get", "deployments", "-n", namespace, "-o", "json"
            ])
            
            # Get pod status
            pod_status = await self._run_command([
                "kubectl", "get", "pods", "-n", namespace, "-o", "json"
            ])
            
            # Get service status
            service_status = await self._run_command([
                "kubectl", "get", "services", "-n", namespace, "-o", "json"
            ])
            
            return {
                "deployments": json.loads(deployment_status.stdout) if deployment_status.returncode == 0 else {},
                "pods": json.loads(pod_status.stdout) if pod_status.returncode == 0 else {},
                "services": json.loads(service_status.stdout) if service_status.returncode == 0 else {},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to capture cluster state: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _trigger_rollback(self, validation: DeploymentValidation, rule_name: str, reason: str):
        """Trigger deployment rollback"""
        try:
            logger.warning(f"🔄 Triggering rollback for {validation.deployment_name}: {reason}")
            
            validation.rollback_triggered = True
            validation.rollback_reason = f"{rule_name}: {reason}"
            
            # Rollback deployment
            result = await self._run_command([
                "kubectl", "rollout", "undo", "deployment", validation.deployment_name,
                "-n", validation.namespace
            ])
            
            if result.returncode == 0:
                logger.info(f"✅ Rollback successful for {validation.deployment_name}")
                
                # Send notification
                await self._send_rollback_notification(validation, rule_name, reason)
            else:
                logger.error(f"❌ Rollback failed for {validation.deployment_name}: {result.stderr.decode()}")
            
        except Exception as e:
            logger.error(f"Failed to trigger rollback: {e}")
    
    async def _determine_validation_result(self, validation: DeploymentValidation) -> Dict[str, Any]:
        """Determine overall validation result"""
        pre_results = validation.validation_results.get("pre_deployment", {})
        post_results = validation.validation_results.get("post_deployment", {})
        
        # Check if any validation failed
        all_passed = True
        failed_rules = []
        
        for phase_results in [pre_results, post_results]:
            for rule_name, result in phase_results.items():
                if not result.get("passed", True):
                    all_passed = False
                    failed_rules.append(f"{rule_name}: {result.get('message', 'Validation failed')}")
        
        return {
            "success": all_passed and not validation.rollback_triggered,
            "deployment_name": validation.deployment_name,
            "namespace": validation.namespace,
            "cluster_id": validation.cluster_id,
            "rollback_triggered": validation.rollback_triggered,
            "rollback_reason": validation.rollback_reason,
            "failed_rules": failed_rules,
            "validation_results": validation.validation_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_rollback_notification(self, validation: DeploymentValidation, rule_name: str, reason: str):
        """Send rollback notification"""
        message = f"""
🚨 UPID Deployment Rollback

Deployment: {validation.deployment_name}
Namespace: {validation.namespace}
Cluster: {validation.cluster_id}
Failed Rule: {rule_name}
Reason: {reason}

Rollback has been triggered automatically.
        """
        
        # Send to configured notification channels
        for channel in self.config.notification_channels or []:
            await self._send_notification(channel, message)
    
    async def _send_notification(self, channel: str, message: str):
        """Send notification to channel"""
        try:
            if channel.startswith("slack://"):
                await self._send_slack_notification(channel, message)
            elif channel.startswith("email://"):
                await self._send_email_notification(channel, message)
            else:
                logger.info(f"Notification to {channel}: {message}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    async def _send_slack_notification(self, webhook_url: str, message: str):
        """Send Slack notification"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"text": message}
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Slack notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_email_notification(self, email_config: str, message: str):
        """Send email notification"""
        # Implementation would depend on email service
        logger.info(f"Email notification: {message}")
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()
    
    async def get_validation_status(self, deployment_name: str) -> Dict[str, Any]:
        """Get validation status for deployment"""
        validation = self.validations.get(deployment_name)
        if not validation:
            return {"error": "Validation not found"}
        
        return {
            "deployment_name": validation.deployment_name,
            "namespace": validation.namespace,
            "cluster_id": validation.cluster_id,
            "rollback_triggered": validation.rollback_triggered,
            "rollback_reason": validation.rollback_reason,
            "validation_results": validation.validation_results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get validation history"""
        return [
            {
                "deployment_name": v.deployment_name,
                "namespace": v.namespace,
                "cluster_id": v.cluster_id,
                "rollback_triggered": v.rollback_triggered,
                "rollback_reason": v.rollback_reason,
                "timestamp": datetime.now().isoformat()
            }
            for v in self.validation_history[-10:]  # Last 10 validations
        ]
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get deployment validator status"""
        return {
            "active_validations": len(self.validations),
            "validation_history_count": len(self.validation_history),
            "validation_rules_count": len(self.validation_rules),
            "auto_rollback_enabled": self.config.auto_rollback,
            "dry_run_enabled": self.config.dry_run_first,
            "notification_channels": self.config.notification_channels or []
        }
    
    async def shutdown(self):
        """Shutdown deployment validator"""
        logger.info("🛑 Shutting down deployment validator...")
        
        # Stop all active validations
        for thread in self.active_validations.values():
            thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        logger.info("✅ Deployment validator shutdown complete") 