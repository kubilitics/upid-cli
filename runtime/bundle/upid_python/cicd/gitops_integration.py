#!/usr/bin/env python3
"""
UPID CLI - GitOps Integration
Phase 6: Platform Integration - Task 6.1
Enterprise-grade GitOps workflow integration for automated deployment management
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


class GitOpsStrategy(str, Enum):
    """GitOps deployment strategies"""
    FLUX = "flux"
    ARGO_CD = "argo_cd"
    JENKINS_X = "jenkins_x"
    CUSTOM = "custom"


@dataclass
class GitOpsConfig:
    """GitOps integration configuration"""
    strategy: GitOpsStrategy = GitOpsStrategy.FLUX
    git_repository: str = ""
    git_branch: str = "main"
    git_credentials: Optional[str] = None
    sync_interval: int = 300  # 5 minutes
    auto_sync: bool = True
    enable_pr_validation: bool = True
    enable_cost_analysis: bool = True
    enable_optimization_suggestions: bool = True
    notification_channels: List[str] = None
    kustomize_enabled: bool = True
    helm_enabled: bool = True
    terraform_enabled: bool = False


@dataclass
class GitOpsDeployment:
    """GitOps deployment configuration"""
    name: str
    namespace: str
    git_path: str
    cluster_id: str
    strategy: GitOpsStrategy
    sync_policy: Dict[str, Any]
    health_checks: List[Dict[str, Any]]
    rollback_policy: Dict[str, Any]
    cost_monitoring: bool = True
    optimization_enabled: bool = True


class GitOpsTemplateGenerator:
    """Generates GitOps configuration templates"""
    
    def __init__(self, config: GitOpsConfig):
        self.config = config
    
    def generate_flux_kustomization(self, deployment: GitOpsDeployment) -> Dict[str, Any]:
        """Generate Flux Kustomization configuration"""
        
        return {
            "apiVersion": "kustomize.toolkit.fluxcd.io/v1",
            "kind": "Kustomization",
            "metadata": {
                "name": f"upid-{deployment.name}",
                "namespace": "flux-system"
            },
            "spec": {
                "interval": "5m",
                "path": deployment.git_path,
                "prune": True,
                "sourceRef": {
                    "kind": "GitRepository",
                    "name": f"upid-{deployment.cluster_id}"
                },
                "targetNamespace": deployment.namespace,
                "healthChecks": [
                    {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": deployment.name,
                        "namespace": deployment.namespace
                    }
                ],
                "postBuild": {
                    "substitute": {
                        "UPID_CLUSTER_ID": deployment.cluster_id,
                        "UPID_NAMESPACE": deployment.namespace,
                        "UPID_DEPLOYMENT_NAME": deployment.name
                    }
                }
            }
        }
    
    def generate_flux_git_repository(self, cluster_id: str, git_url: str) -> Dict[str, Any]:
        """Generate Flux GitRepository configuration"""
        
        return {
            "apiVersion": "source.toolkit.fluxcd.io/v1",
            "kind": "GitRepository",
            "metadata": {
                "name": f"upid-{cluster_id}",
                "namespace": "flux-system"
            },
            "spec": {
                "interval": "1m",
                "url": git_url,
                "ref": {
                    "branch": self.config.git_branch
                },
                "secretRef": {
                    "name": "upid-git-credentials"
                }
            }
        }
    
    def generate_argo_application(self, deployment: GitOpsDeployment) -> Dict[str, Any]:
        """Generate Argo CD Application configuration"""
        
        return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": f"upid-{deployment.name}",
                "namespace": "argocd"
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": self.config.git_repository,
                    "targetRevision": self.config.git_branch,
                    "path": deployment.git_path
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": deployment.namespace
                },
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": True
                    },
                    "syncOptions": [
                        "CreateNamespace=true",
                        "PrunePropagationPolicy=foreground"
                    ]
                },
                "revisionHistoryLimit": 10
            }
        }
    
    def generate_jenkins_x_pipeline(self, deployment: GitOpsDeployment) -> Dict[str, Any]:
        """Generate Jenkins X pipeline configuration"""
        
        return {
            "apiVersion": "jenkins.io/v1",
            "kind": "PipelineActivity",
            "metadata": {
                "name": f"upid-{deployment.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "namespace": "jx"
            },
            "spec": {
                "pipeline": f"upid-{deployment.name}",
                "build": "1",
                "version": "1.0.0",
                "status": "Running",
                "startedTimestamp": datetime.now().isoformat(),
                "steps": [
                    {
                        "name": "pre-deployment-analysis",
                        "description": "UPID pre-deployment cost analysis",
                        "status": "Running"
                    },
                    {
                        "name": "deploy",
                        "description": "Deploy to Kubernetes",
                        "status": "NotExecuted"
                    },
                    {
                        "name": "post-deployment-validation",
                        "description": "UPID post-deployment validation",
                        "status": "NotExecuted"
                    }
                ]
            }
        }
    
    def generate_cost_analysis_workflow(self, deployment: GitOpsDeployment) -> Dict[str, Any]:
        """Generate cost analysis workflow for GitOps"""
        
        return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "name": f"upid-cost-analysis-{deployment.name}",
                "namespace": "upid-system"
            },
            "spec": {
                "entrypoint": "cost-analysis",
                "templates": [
                    {
                        "name": "cost-analysis",
                        "steps": [
                            {
                                "name": "pre-deployment",
                                "template": "upid-analyze",
                                "arguments": {
                                    "parameters": [
                                        {"name": "cluster-id", "value": deployment.cluster_id},
                                        {"name": "analysis-type", "value": "cost"}
                                    ]
                                }
                            },
                            {
                                "name": "deploy",
                                "template": "deploy",
                                "arguments": {
                                    "parameters": [
                                        {"name": "deployment-name", "value": deployment.name},
                                        {"name": "namespace", "value": deployment.namespace}
                                    ]
                                }
                            },
                            {
                                "name": "post-deployment",
                                "template": "upid-analyze",
                                "arguments": {
                                    "parameters": [
                                        {"name": "cluster-id", "value": deployment.cluster_id},
                                        {"name": "analysis-type", "value": "cost"}
                                    ]
                                }
                            }
                        ]
                    },
                    {
                        "name": "upid-analyze",
                        "inputs": {
                            "parameters": [
                                {"name": "cluster-id"},
                                {"name": "analysis-type"}
                            ]
                        },
                        "script": {
                            "image": "upid/upid-cli:latest",
                            "command": ["upid"],
                            "args": [
                                "analyze",
                                "{{inputs.parameters.analysis-type}}",
                                "--cluster-id",
                                "{{inputs.parameters.cluster-id}}",
                                "--output",
                                "json"
                            ]
                        }
                    },
                    {
                        "name": "deploy",
                        "inputs": {
                            "parameters": [
                                {"name": "deployment-name"},
                                {"name": "namespace"}
                            ]
                        },
                        "script": {
                            "image": "bitnami/kubectl:latest",
                            "command": ["kubectl"],
                            "args": [
                                "apply",
                                "-f",
                                "k8s/",
                                "-n",
                                "{{inputs.parameters.namespace}}"
                            ]
                        }
                    }
                ]
            }
        }


class GitOpsIntegration:
    """
    GitOps integration for UPID CLI
    
    Features:
    - Multi-strategy GitOps support (Flux, Argo CD, Jenkins X)
    - Automated deployment validation
    - Cost analysis integration
    - Optimization suggestions
    - Health monitoring and rollback
    - Infrastructure as Code templates
    """
    
    def __init__(self, pipeline_manager: PipelineManager, config: GitOpsConfig):
        self.pipeline_manager = pipeline_manager
        self.config = config
        self.template_generator = GitOpsTemplateGenerator(config)
        
        # GitOps components
        self.deployments: Dict[str, GitOpsDeployment] = {}
        self.sync_status: Dict[str, Dict[str, Any]] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.sync_threads: Dict[str, threading.Thread] = {}
        
        logger.info("🔧 Initializing GitOps integration")
    
    async def initialize(self) -> bool:
        """Initialize GitOps integration"""
        try:
            logger.info("🚀 Initializing GitOps integration...")
            
            # Validate GitOps strategy
            await self._validate_gitops_strategy()
            
            # Setup GitOps components
            await self._setup_gitops_components()
            
            # Start sync monitoring if auto-sync enabled
            if self.config.auto_sync:
                await self._start_sync_monitoring()
            
            logger.info("✅ GitOps integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GitOps integration: {e}")
            return False
    
    async def _validate_gitops_strategy(self):
        """Validate GitOps strategy configuration"""
        if self.config.strategy == GitOpsStrategy.FLUX:
            # Check if Flux is installed
            try:
                result = await self._run_command(["flux", "version"])
                if result.returncode != 0:
                    logger.warning("Flux not found, installing...")
                    await self._install_flux()
            except Exception as e:
                logger.warning(f"Flux validation failed: {e}")
        
        elif self.config.strategy == GitOpsStrategy.ARGO_CD:
            # Check if Argo CD is accessible
            try:
                result = await self._run_command(["kubectl", "get", "namespace", "argocd"])
                if result.returncode != 0:
                    logger.warning("Argo CD namespace not found")
            except Exception as e:
                logger.warning(f"Argo CD validation failed: {e}")
    
    async def _setup_gitops_components(self):
        """Setup GitOps components"""
        if self.config.strategy == GitOpsStrategy.FLUX:
            await self._setup_flux_components()
        elif self.config.strategy == GitOpsStrategy.ARGO_CD:
            await self._setup_argocd_components()
        elif self.config.strategy == GitOpsStrategy.JENKINS_X:
            await self._setup_jenkins_x_components()
    
    async def _setup_flux_components(self):
        """Setup Flux components"""
        # Create GitRepository for UPID
        git_repo_config = self.template_generator.generate_flux_git_repository(
            "upid-system", 
            self.config.git_repository
        )
        
        # Apply GitRepository
        await self._apply_k8s_resource(git_repo_config)
        
        logger.info("✅ Flux components setup completed")
    
    async def _setup_argocd_components(self):
        """Setup Argo CD components"""
        # Create UPID project
        project_config = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "AppProject",
            "metadata": {
                "name": "upid-project",
                "namespace": "argocd"
            },
            "spec": {
                "description": "UPID CLI GitOps project",
                "sourceRepos": ["*"],
                "destinations": [
                    {
                        "namespace": "*",
                        "server": "https://kubernetes.default.svc"
                    }
                ],
                "clusterResourceWhitelist": [
                    {"group": "", "kind": "Namespace"}
                ],
                "namespaceResourceWhitelist": [
                    {"group": "", "kind": "Deployment"},
                    {"group": "", "kind": "Service"},
                    {"group": "", "kind": "ConfigMap"},
                    {"group": "", "kind": "Secret"}
                ]
            }
        }
        
        await self._apply_k8s_resource(project_config)
        logger.info("✅ Argo CD components setup completed")
    
    async def _setup_jenkins_x_components(self):
        """Setup Jenkins X components"""
        # Create UPID pipeline catalog
        catalog_config = {
            "apiVersion": "jenkins.io/v1",
            "kind": "PipelineCatalog",
            "metadata": {
                "name": "upid-catalog",
                "namespace": "jx"
            },
            "spec": {
                "repositories": [
                    {
                        "name": "upid-pipelines",
                        "url": self.config.git_repository,
                        "ref": self.config.git_branch
                    }
                ]
            }
        }
        
        await self._apply_k8s_resource(catalog_config)
        logger.info("✅ Jenkins X components setup completed")
    
    async def create_deployment(self, deployment: GitOpsDeployment) -> bool:
        """Create a new GitOps deployment"""
        try:
            logger.info(f"🔧 Creating GitOps deployment: {deployment.name}")
            
            # Generate configuration based on strategy
            if deployment.strategy == GitOpsStrategy.FLUX:
                config = self.template_generator.generate_flux_kustomization(deployment)
            elif deployment.strategy == GitOpsStrategy.ARGO_CD:
                config = self.template_generator.generate_argo_application(deployment)
            elif deployment.strategy == GitOpsStrategy.JENKINS_X:
                config = self.template_generator.generate_jenkins_x_pipeline(deployment)
            else:
                raise ValueError(f"Unsupported GitOps strategy: {deployment.strategy}")
            
            # Apply configuration
            await self._apply_k8s_resource(config)
            
            # Store deployment
            self.deployments[deployment.name] = deployment
            
            # Start monitoring if cost monitoring enabled
            if deployment.cost_monitoring:
                await self._start_cost_monitoring(deployment)
            
            logger.info(f"✅ GitOps deployment created: {deployment.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create GitOps deployment: {e}")
            return False
    
    async def sync_deployment(self, deployment_name: str) -> bool:
        """Sync a GitOps deployment"""
        try:
            logger.info(f"🔄 Syncing GitOps deployment: {deployment_name}")
            
            deployment = self.deployments.get(deployment_name)
            if not deployment:
                raise ValueError(f"Deployment not found: {deployment_name}")
            
            if deployment.strategy == GitOpsStrategy.FLUX:
                await self._run_command([
                    "flux", "reconcile", "kustomization", 
                    f"upid-{deployment_name}", "--namespace", "flux-system"
                ])
            elif deployment.strategy == GitOpsStrategy.ARGO_CD:
                await self._run_command([
                    "argocd", "app", "sync", f"upid-{deployment_name}"
                ])
            elif deployment.strategy == GitOpsStrategy.JENKINS_X:
                # Jenkins X syncs automatically
                logger.info("Jenkins X syncs automatically")
            
            # Update sync status
            self.sync_status[deployment_name] = {
                "last_sync": datetime.now().isoformat(),
                "status": "synced"
            }
            
            logger.info(f"✅ GitOps deployment synced: {deployment_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to sync GitOps deployment: {e}")
            return False
    
    async def get_deployment_status(self, deployment_name: str) -> Dict[str, Any]:
        """Get GitOps deployment status"""
        try:
            deployment = self.deployments.get(deployment_name)
            if not deployment:
                return {"error": "Deployment not found"}
            
            status = {
                "name": deployment_name,
                "namespace": deployment.namespace,
                "strategy": deployment.strategy.value,
                "git_path": deployment.git_path,
                "cluster_id": deployment.cluster_id,
                "sync_status": self.sync_status.get(deployment_name, {}),
                "health_status": await self._get_health_status(deployment),
                "cost_analysis": await self._get_cost_analysis(deployment)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to get deployment status: {e}")
            return {"error": str(e)}
    
    async def _get_health_status(self, deployment: GitOpsDeployment) -> Dict[str, Any]:
        """Get deployment health status"""
        try:
            if deployment.strategy == GitOpsStrategy.FLUX:
                result = await self._run_command([
                    "kubectl", "get", "kustomization", f"upid-{deployment.name}",
                    "-n", "flux-system", "-o", "json"
                ])
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return {
                        "ready": data.get("status", {}).get("conditions", [{}])[0].get("status") == "True",
                        "message": data.get("status", {}).get("conditions", [{}])[0].get("message", "")
                    }
            
            elif deployment.strategy == GitOpsStrategy.ARGO_CD:
                result = await self._run_command([
                    "argocd", "app", "get", f"upid-{deployment.name}", "-o", "json"
                ])
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    return {
                        "ready": data.get("status", {}).get("health", {}).get("status") == "Healthy",
                        "message": data.get("status", {}).get("health", {}).get("message", "")
                    }
            
            return {"ready": False, "message": "Unknown status"}
            
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {"ready": False, "message": str(e)}
    
    async def _get_cost_analysis(self, deployment: GitOpsDeployment) -> Dict[str, Any]:
        """Get cost analysis for deployment"""
        try:
            if not deployment.cost_monitoring:
                return {"enabled": False}
            
            # Get cost analysis from UPID
            result = await self._run_command([
                "upid", "analyze", "cost", "--cluster-id", deployment.cluster_id,
                "--namespace", deployment.namespace, "--output", "json"
            ])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "enabled": True,
                    "monthly_cost": data.get("monthly_cost", 0),
                    "optimization_potential": data.get("optimization_potential", 0),
                    "last_updated": datetime.now().isoformat()
                }
            
            return {"enabled": True, "error": "Failed to get cost analysis"}
            
        except Exception as e:
            logger.error(f"Failed to get cost analysis: {e}")
            return {"enabled": True, "error": str(e)}
    
    async def _start_sync_monitoring(self):
        """Start automatic sync monitoring"""
        async def monitor_sync():
            while True:
                try:
                    for deployment_name in self.deployments:
                        deployment = self.deployments[deployment_name]
                        last_sync = self.sync_status.get(deployment_name, {}).get("last_sync")
                        
                        if last_sync:
                            last_sync_time = datetime.fromisoformat(last_sync)
                            if datetime.now() - last_sync_time > timedelta(minutes=self.config.sync_interval):
                                await self.sync_deployment(deployment_name)
                    
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Sync monitoring error: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        
        asyncio.create_task(monitor_sync())
        logger.info("🔄 Started automatic sync monitoring")
    
    async def _start_cost_monitoring(self, deployment: GitOpsDeployment):
        """Start cost monitoring for deployment"""
        async def monitor_cost():
            while True:
                try:
                    # Get cost analysis
                    cost_data = await self._get_cost_analysis(deployment)
                    
                    if cost_data.get("enabled") and not cost_data.get("error"):
                        monthly_cost = cost_data.get("monthly_cost", 0)
                        optimization_potential = cost_data.get("optimization_potential", 0)
                        
                        # Send notification if cost exceeds threshold
                        if monthly_cost > 1000:  # $1000 threshold
                            await self._send_cost_alert(deployment, monthly_cost, optimization_potential)
                    
                    await asyncio.sleep(3600)  # Check every hour
                    
                except Exception as e:
                    logger.error(f"Cost monitoring error: {e}")
                    await asyncio.sleep(3600)
        
        asyncio.create_task(monitor_cost())
        logger.info(f"💰 Started cost monitoring for deployment: {deployment.name}")
    
    async def _send_cost_alert(self, deployment: GitOpsDeployment, cost: float, potential: float):
        """Send cost alert notification"""
        message = f"""
🚨 UPID Cost Alert

Deployment: {deployment.name}
Namespace: {deployment.namespace}
Monthly Cost: ${cost:.2f}
Optimization Potential: ${potential:.2f}

Consider running: upid optimize cost --cluster-id {deployment.cluster_id} --namespace {deployment.namespace}
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
    
    async def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """Run shell command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()
    
    async def _apply_k8s_resource(self, config: Dict[str, Any]):
        """Apply Kubernetes resource"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_file = f.name
        
        try:
            # Apply resource
            result = await self._run_command(["kubectl", "apply", "-f", temp_file])
            if result.returncode != 0:
                raise Exception(f"Failed to apply resource: {result.stderr.decode()}")
        finally:
            # Clean up
            import os
            os.unlink(temp_file)
    
    async def _install_flux(self):
        """Install Flux CLI"""
        try:
            # Install Flux CLI
            await self._run_command([
                "curl", "-s", "https://fluxcd.io/install.sh", "|", "bash"
            ])
            logger.info("✅ Flux CLI installed")
        except Exception as e:
            logger.error(f"Failed to install Flux: {e}")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get GitOps integration status"""
        return {
            "strategy": self.config.strategy.value,
            "git_repository": self.config.git_repository,
            "auto_sync": self.config.auto_sync,
            "deployments_count": len(self.deployments),
            "deployments": [
                {
                    "name": name,
                    "namespace": deployment.namespace,
                    "strategy": deployment.strategy.value,
                    "cost_monitoring": deployment.cost_monitoring
                }
                for name, deployment in self.deployments.items()
            ],
            "sync_status": self.sync_status
        }
    
    async def shutdown(self):
        """Shutdown GitOps integration"""
        logger.info("🛑 Shutting down GitOps integration...")
        
        # Stop all monitoring threads
        for thread in self.sync_threads.values():
            thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        logger.info("✅ GitOps integration shutdown complete") 