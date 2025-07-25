#!/usr/bin/env python3
"""
UPID CLI - Enhanced Deployment Validator
Phase 6: Platform Integration - Task 6.3
Enterprise-grade enhanced deployment validation with advanced rules, plugins, and compliance
"""

import logging
import asyncio
import json
import yaml
import base64
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
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
import importlib.util
import inspect

from .deployment_validator import DeploymentValidator, ValidationConfig, DeploymentValidation
from .pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)


class ValidationRuleType(str, Enum):
    """Enhanced validation rule types"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COST = "cost"
    AVAILABILITY = "availability"
    CUSTOM = "custom"


class ValidationSeverity(str, Enum):
    """Validation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EnhancedValidationRule:
    """Enhanced validation rule definition"""
    name: str
    description: str
    rule_type: ValidationRuleType
    severity: ValidationSeverity
    enabled: bool = True
    timeout: int = 300  # 5 minutes
    custom_function: Optional[Callable] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class PerformanceBenchmark:
    """Performance benchmarking configuration"""
    baseline_metrics: Dict[str, float]
    threshold_percentage: float = 20.0  # 20% degradation threshold
    measurement_duration: int = 300  # 5 minutes
    metrics_to_benchmark: List[str] = None
    
    def __post_init__(self):
        if self.metrics_to_benchmark is None:
            self.metrics_to_benchmark = ["cpu", "memory", "response_time", "throughput"]


@dataclass
class SecurityComplianceConfig:
    """Security compliance configuration"""
    compliance_frameworks: List[str] = None
    security_scanners: List[str] = None
    vulnerability_threshold: int = 0  # 0 critical vulnerabilities allowed
    compliance_checks: List[str] = None
    
    def __post_init__(self):
        if self.compliance_frameworks is None:
            self.compliance_frameworks = ["soc2", "iso27001"]
        if self.security_scanners is None:
            self.security_scanners = ["trivy", "falco", "kubesec"]
        if self.compliance_checks is None:
            self.compliance_checks = ["rbac", "network_policies", "pod_security"]


class CustomValidationPlugin:
    """Base class for custom validation plugins"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate deployment - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0"
        }


class PerformanceValidationRule(EnhancedValidationRule):
    """Performance validation rule"""
    
    def __init__(self, benchmark: PerformanceBenchmark):
        super().__init__(
            name="performance_validation",
            description="Validate deployment performance against baseline",
            rule_type=ValidationRuleType.PERFORMANCE,
            severity=ValidationSeverity.HIGH
        )
        self.benchmark = benchmark
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate performance against baseline"""
        try:
            # Get current performance metrics
            current_metrics = await self._get_performance_metrics(deployment)
            
            # Compare with baseline
            performance_results = {}
            for metric in self.benchmark.metrics_to_benchmark:
                baseline = self.benchmark.baseline_metrics.get(metric, 0)
                current = current_metrics.get(metric, 0)
                
                if baseline > 0:
                    degradation = ((baseline - current) / baseline) * 100
                    threshold = self.benchmark.threshold_percentage
                    
                    performance_results[metric] = {
                        "baseline": baseline,
                        "current": current,
                        "degradation_percentage": degradation,
                        "within_threshold": degradation <= threshold,
                        "threshold": threshold
                    }
                else:
                    performance_results[metric] = {
                        "baseline": baseline,
                        "current": current,
                        "degradation_percentage": 0,
                        "within_threshold": True,
                        "threshold": self.benchmark.threshold_percentage
                    }
            
            # Determine overall performance status
            failed_metrics = [m for m, r in performance_results.items() if not r["within_threshold"]]
            overall_passed = len(failed_metrics) == 0
            
            return {
                "passed": overall_passed,
                "performance_results": performance_results,
                "failed_metrics": failed_metrics,
                "message": f"Performance validation {'passed' if overall_passed else 'failed'}: {len(failed_metrics)} metrics exceeded threshold"
            }
            
        except Exception as e:
            logger.error(f"Performance validation failed: {e}")
            return {
                "passed": False,
                "error": str(e),
                "message": "Performance validation failed due to error"
            }
    
    async def _get_performance_metrics(self, deployment: DeploymentValidation) -> Dict[str, float]:
        """Get current performance metrics"""
        try:
            result = await self._run_command([
                "upid", "analyze", "performance",
                "--cluster-id", deployment.cluster_id,
                "--namespace", deployment.namespace,
                "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "cpu": data.get("cpu_usage_percent", 0.0),
                    "memory": data.get("memory_usage_percent", 0.0),
                    "response_time": data.get("avg_response_time_ms", 0.0),
                    "throughput": data.get("requests_per_second", 0.0)
                }
            
            return {"cpu": 0.0, "memory": 0.0, "response_time": 0.0, "throughput": 0.0}
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"cpu": 0.0, "memory": 0.0, "response_time": 0.0, "throughput": 0.0}
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()


class SecurityValidationRule(EnhancedValidationRule):
    """Security validation rule"""
    
    def __init__(self, compliance_config: SecurityComplianceConfig):
        super().__init__(
            name="security_validation",
            description="Validate deployment security and compliance",
            rule_type=ValidationRuleType.SECURITY,
            severity=ValidationSeverity.CRITICAL
        )
        self.compliance_config = compliance_config
    
    async def validate(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Validate security and compliance"""
        try:
            security_results = {}
            
            # Run vulnerability scanning
            vulnerability_results = await self._run_vulnerability_scan(deployment)
            security_results["vulnerabilities"] = vulnerability_results
            
            # Run compliance checks
            compliance_results = await self._run_compliance_checks(deployment)
            security_results["compliance"] = compliance_results
            
            # Determine overall security status
            critical_vulns = vulnerability_results.get("critical_vulnerabilities", 0)
            compliance_passed = compliance_results.get("overall_passed", False)
            
            overall_passed = critical_vulns <= self.compliance_config.vulnerability_threshold and compliance_passed
            
            return {
                "passed": overall_passed,
                "security_results": security_results,
                "critical_vulnerabilities": critical_vulns,
                "compliance_passed": compliance_passed,
                "message": f"Security validation {'passed' if overall_passed else 'failed'}: {critical_vulns} critical vulnerabilities, compliance {'passed' if compliance_passed else 'failed'}"
            }
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {
                "passed": False,
                "error": str(e),
                "message": "Security validation failed due to error"
            }
    
    async def _run_vulnerability_scan(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Run vulnerability scanning"""
        try:
            # Run Trivy scan
            result = await self._run_command([
                "trivy", "config", deployment.manifest_path, "--format", "json"
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
            logger.error(f"Vulnerability scan failed: {e}")
            return {"critical_vulnerabilities": 0, "high_vulnerabilities": 0, "medium_vulnerabilities": 0, "low_vulnerabilities": 0}
    
    async def _run_compliance_checks(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Run compliance checks"""
        try:
            compliance_results = {}
            
            # Check RBAC
            rbac_result = await self._check_rbac(deployment)
            compliance_results["rbac"] = rbac_result
            
            # Check network policies
            network_result = await self._check_network_policies(deployment)
            compliance_results["network_policies"] = network_result
            
            # Check pod security
            pod_security_result = await self._check_pod_security(deployment)
            compliance_results["pod_security"] = pod_security_result
            
            # Overall compliance status
            overall_passed = all([
                rbac_result.get("passed", False),
                network_result.get("passed", False),
                pod_security_result.get("passed", False)
            ])
            
            return {
                "overall_passed": overall_passed,
                "checks": compliance_results
            }
            
        except Exception as e:
            logger.error(f"Compliance checks failed: {e}")
            return {"overall_passed": False, "checks": {}}
    
    async def _check_rbac(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Check RBAC compliance"""
        try:
            result = await self._run_command([
                "kubectl", "get", "rbac", "-n", deployment.namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                rbac_resources = len(data.get("items", []))
                
                return {
                    "passed": rbac_resources > 0,
                    "rbac_resources_count": rbac_resources,
                    "message": f"RBAC compliance: {rbac_resources} RBAC resources found"
                }
            
            return {"passed": False, "message": "Failed to check RBAC compliance"}
            
        except Exception as e:
            logger.error(f"RBAC check failed: {e}")
            return {"passed": False, "message": f"RBAC check failed: {str(e)}"}
    
    async def _check_network_policies(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Check network policies compliance"""
        try:
            result = await self._run_command([
                "kubectl", "get", "networkpolicy", "-n", deployment.namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                network_policies = len(data.get("items", []))
                
                return {
                    "passed": network_policies > 0,
                    "network_policies_count": network_policies,
                    "message": f"Network policies compliance: {network_policies} network policies found"
                }
            
            return {"passed": False, "message": "Failed to check network policies compliance"}
            
        except Exception as e:
            logger.error(f"Network policies check failed: {e}")
            return {"passed": False, "message": f"Network policies check failed: {str(e)}"}
    
    async def _check_pod_security(self, deployment: DeploymentValidation) -> Dict[str, Any]:
        """Check pod security compliance"""
        try:
            result = await self._run_command([
                "kubectl", "get", "pods", "-n", deployment.namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                pods = data.get("items", [])
                
                # Check for privileged containers
                privileged_pods = []
                for pod in pods:
                    containers = pod.get("spec", {}).get("containers", [])
                    for container in containers:
                        security_context = container.get("securityContext", {})
                        if security_context.get("privileged", False):
                            privileged_pods.append(pod.get("metadata", {}).get("name", "unknown"))
                
                return {
                    "passed": len(privileged_pods) == 0,
                    "privileged_pods": privileged_pods,
                    "total_pods": len(pods),
                    "message": f"Pod security compliance: {len(privileged_pods)} privileged pods found"
                }
            
            return {"passed": False, "message": "Failed to check pod security compliance"}
            
        except Exception as e:
            logger.error(f"Pod security check failed: {e}")
            return {"passed": False, "message": f"Pod security check failed: {str(e)}"}
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()


class CustomValidationPluginManager:
    """Manages custom validation plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, CustomValidationPlugin] = {}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, plugin: CustomValidationPlugin):
        """Register a custom validation plugin"""
        self.plugins[plugin.name] = plugin
        self.plugin_metadata[plugin.name] = asyncio.run(plugin.get_metadata())
        logger.info(f"Registered custom validation plugin: {plugin.name}")
    
    def load_plugin_from_file(self, plugin_path: str) -> bool:
        """Load plugin from Python file"""
        try:
            spec = importlib.util.spec_from_file_location("custom_plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, CustomValidationPlugin) and 
                    obj != CustomValidationPlugin):
                    
                    plugin_instance = obj()
                    self.register_plugin(plugin_instance)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[CustomValidationPlugin]:
        """Get plugin by name"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [
            {
                "name": name,
                "metadata": self.plugin_metadata.get(name, {})
            }
            for name in self.plugins.keys()
        ]


class EnhancedDeploymentValidator:
    """
    Enhanced deployment validator for UPID CLI
    
    Features:
    - Advanced validation rules
    - Custom validation plugins
    - Performance benchmarking
    - Security compliance checks
    - Plugin management system
    """
    
    def __init__(self, pipeline_manager: PipelineManager, base_validator: DeploymentValidator):
        self.pipeline_manager = pipeline_manager
        self.base_validator = base_validator
        
        # Enhanced validation components
        self.enhanced_rules: List[EnhancedValidationRule] = []
        self.plugin_manager = CustomValidationPluginManager()
        
        # Performance benchmarking
        self.performance_benchmarks: Dict[str, PerformanceBenchmark] = {}
        
        # Security compliance
        self.security_configs: Dict[str, SecurityComplianceConfig] = {}
        
        # Validation history
        self.enhanced_validation_history: List[Dict[str, Any]] = []
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        logger.info("🔧 Initializing Enhanced Deployment Validator")
    
    async def initialize(self) -> bool:
        """Initialize Enhanced Deployment Validator"""
        try:
            logger.info("🚀 Initializing Enhanced Deployment Validator...")
            
            # Initialize base validator
            await self.base_validator.initialize()
            
            # Setup default enhanced rules
            await self._setup_default_enhanced_rules()
            
            # Load custom plugins
            await self._load_custom_plugins()
            
            logger.info("✅ Enhanced Deployment Validator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Deployment Validator: {e}")
            return False
    
    async def _setup_default_enhanced_rules(self):
        """Setup default enhanced validation rules"""
        logger.info("🔧 Setting up default enhanced validation rules...")
        
        # Performance validation rule
        performance_benchmark = PerformanceBenchmark(
            baseline_metrics={
                "cpu": 50.0,
                "memory": 60.0,
                "response_time": 100.0,
                "throughput": 1000.0
            },
            threshold_percentage=20.0
        )
        
        performance_rule = PerformanceValidationRule(performance_benchmark)
        self.enhanced_rules.append(performance_rule)
        
        # Security validation rule
        security_config = SecurityComplianceConfig(
            compliance_frameworks=["soc2", "iso27001"],
            vulnerability_threshold=0
        )
        
        security_rule = SecurityValidationRule(security_config)
        self.enhanced_rules.append(security_rule)
        
        logger.info(f"✅ Setup {len(self.enhanced_rules)} default enhanced validation rules")
    
    async def _load_custom_plugins(self):
        """Load custom validation plugins"""
        logger.info("🔌 Loading custom validation plugins...")
        
        # Look for plugins in plugins directory
        plugins_dir = Path("plugins/validation")
        if plugins_dir.exists():
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name != "__init__.py":
                    success = self.plugin_manager.load_plugin_from_file(str(plugin_file))
                    if success:
                        logger.info(f"✅ Loaded plugin: {plugin_file.name}")
                    else:
                        logger.warning(f"⚠️ Failed to load plugin: {plugin_file.name}")
        
        logger.info(f"✅ Loaded {len(self.plugin_manager.plugins)} custom plugins")
    
    async def add_enhanced_rule(self, rule: EnhancedValidationRule):
        """Add enhanced validation rule"""
        self.enhanced_rules.append(rule)
        logger.info(f"✅ Added enhanced validation rule: {rule.name}")
    
    async def add_performance_benchmark(self, deployment_name: str, benchmark: PerformanceBenchmark):
        """Add performance benchmark for deployment"""
        self.performance_benchmarks[deployment_name] = benchmark
        logger.info(f"✅ Added performance benchmark for: {deployment_name}")
    
    async def add_security_config(self, deployment_name: str, config: SecurityComplianceConfig):
        """Add security compliance config for deployment"""
        self.security_configs[deployment_name] = config
        logger.info(f"✅ Added security config for: {deployment_name}")
    
    async def validate_deployment_enhanced(self, deployment_name: str, namespace: str, cluster_id: str, 
                                         manifest_path: str) -> Dict[str, Any]:
        """Validate deployment with enhanced rules"""
        try:
            logger.info(f"🔍 Starting enhanced deployment validation: {deployment_name}")
            
            # Run base validation
            base_result = await self.base_validator.validate_deployment(
                deployment_name, namespace, cluster_id, manifest_path
            )
            
            # Create deployment validation object
            deployment = DeploymentValidation(
                deployment_name=deployment_name,
                namespace=namespace,
                cluster_id=cluster_id,
                manifest_path=manifest_path,
                validation_config=self.base_validator.config,
                pre_deployment_state={},
                post_deployment_state={},
                validation_results={}
            )
            
            # Run enhanced validation rules
            enhanced_results = {}
            for rule in self.enhanced_rules:
                if rule.enabled:
                    try:
                        rule_result = await rule.validate(deployment)
                        enhanced_results[rule.name] = rule_result
                        logger.info(f"✅ Enhanced rule {rule.name}: {'PASSED' if rule_result.get('passed') else 'FAILED'}")
                    except Exception as e:
                        logger.error(f"❌ Enhanced rule {rule.name} failed: {e}")
                        enhanced_results[rule.name] = {
                            "passed": False,
                            "error": str(e),
                            "message": f"Rule execution failed: {str(e)}"
                        }
            
            # Run custom plugins
            plugin_results = {}
            for plugin_name, plugin in self.plugin_manager.plugins.items():
                try:
                    plugin_result = await plugin.validate(deployment)
                    plugin_results[plugin_name] = plugin_result
                    logger.info(f"✅ Plugin {plugin_name}: {'PASSED' if plugin_result.get('passed') else 'FAILED'}")
                except Exception as e:
                    logger.error(f"❌ Plugin {plugin_name} failed: {e}")
                    plugin_results[plugin_name] = {
                        "passed": False,
                        "error": str(e),
                        "message": f"Plugin execution failed: {str(e)}"
                    }
            
            # Determine overall enhanced validation result
            all_enhanced_passed = all(
                result.get("passed", False) 
                for result in enhanced_results.values()
            )
            
            all_plugins_passed = all(
                result.get("passed", False) 
                for result in plugin_results.values()
            )
            
            overall_enhanced_passed = all_enhanced_passed and all_plugins_passed
            
            # Combine results
            combined_result = {
                "success": base_result.get("success", False) and overall_enhanced_passed,
                "deployment_name": deployment_name,
                "namespace": namespace,
                "cluster_id": cluster_id,
                "base_validation": base_result,
                "enhanced_validation": {
                    "overall_passed": overall_enhanced_passed,
                    "enhanced_rules": enhanced_results,
                    "custom_plugins": plugin_results
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in history
            self.enhanced_validation_history.append(combined_result)
            
            logger.info(f"✅ Enhanced deployment validation completed: {deployment_name}")
            return combined_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced deployment validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_name": deployment_name,
                "message": "Enhanced deployment validation failed due to error"
            }
    
    async def get_enhanced_validation_status(self, deployment_name: str) -> Dict[str, Any]:
        """Get enhanced validation status for deployment"""
        # Find the most recent validation for this deployment
        for validation in reversed(self.enhanced_validation_history):
            if validation.get("deployment_name") == deployment_name:
                return validation
        
        return {"error": "No enhanced validation found for deployment"}
    
    async def get_enhanced_validation_history(self) -> List[Dict[str, Any]]:
        """Get enhanced validation history"""
        return [
            {
                "deployment_name": v.get("deployment_name"),
                "namespace": v.get("namespace"),
                "cluster_id": v.get("cluster_id"),
                "success": v.get("success"),
                "timestamp": v.get("timestamp")
            }
            for v in self.enhanced_validation_history[-10:]  # Last 10 validations
        ]
    
    async def get_enhanced_validator_status(self) -> Dict[str, Any]:
        """Get enhanced validator status"""
        return {
            "enhanced_rules_count": len(self.enhanced_rules),
            "custom_plugins_count": len(self.plugin_manager.plugins),
            "performance_benchmarks_count": len(self.performance_benchmarks),
            "security_configs_count": len(self.security_configs),
            "enhanced_validation_history_count": len(self.enhanced_validation_history),
            "enhanced_rules": [
                {
                    "name": rule.name,
                    "type": rule.rule_type.value,
                    "severity": rule.severity.value,
                    "enabled": rule.enabled
                }
                for rule in self.enhanced_rules
            ],
            "custom_plugins": self.plugin_manager.list_plugins()
        }
    
    async def shutdown(self):
        """Shutdown Enhanced Deployment Validator"""
        logger.info("🛑 Shutting down Enhanced Deployment Validator...")
        
        # Shutdown base validator
        await self.base_validator.shutdown()
        
        self.executor.shutdown(wait=True)
        logger.info("✅ Enhanced Deployment Validator shutdown complete") 