#!/usr/bin/env python3
"""
UPID CLI - GitLab CI/CD Integration
Phase 6: Platform Integration - Task 6.1
Enterprise-grade GitLab CI/CD integration for automated UPID workflows
"""

import logging
import asyncio
import json
import yaml
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import re

from .pipeline_manager import PipelineManager, PipelineConfig, TriggerType, PipelineType

logger = logging.getLogger(__name__)


@dataclass
class GitLabCICDConfig:
    """GitLab CI/CD integration configuration"""
    gitlab_token: Optional[str] = None
    gitlab_url: str = "https://gitlab.com"
    project_id: Optional[int] = None
    project_path: str = ""
    webhook_secret: Optional[str] = None
    ci_templates_dir: str = ".gitlab"
    upid_runner_image: str = "upid/upid-cli:latest"
    enable_auto_mr: bool = True
    enable_cost_comments: bool = True
    enable_optimization_suggestions: bool = True


@dataclass
class GitLabPipeline:
    """GitLab CI pipeline definition"""
    name: str
    description: str
    stages: List[str]
    variables: Dict[str, Any]
    jobs: Dict[str, Any]
    pipeline_file: str
    
    def to_yaml(self) -> str:
        """Convert pipeline to YAML format"""
        pipeline_dict = {
            "stages": self.stages,
            "variables": self.variables,
            **self.jobs
        }
        return yaml.dump(pipeline_dict, default_flow_style=False, sort_keys=False)


class GitLabCICDTemplateGenerator:
    """Generates GitLab CI/CD pipeline templates"""
    
    def __init__(self, config: GitLabCICDConfig):
        self.config = config
    
    def generate_cost_optimization_pipeline(self, cluster_config: Dict[str, Any]) -> GitLabPipeline:
        """Generate cost optimization pipeline"""
        
        stages = ["prepare", "analyze", "optimize", "validate", "deploy"]
        
        variables = {
            "UPID_CLI_VERSION": "latest",
            "CLUSTER_ID": cluster_config.get("cluster_id", "default"),
            "UPID_LOG_LEVEL": "INFO",
            "SAFETY_MODE": "true"
        }
        
        jobs = {
            ".upid_base": {
                "image": self.config.upid_runner_image,
                "before_script": [
                    "upid --version",
                    "upid auth validate"
                ],
                "variables": {
                    "KUBECONFIG": "$KUBECONFIG_CONTENT"
                }
            },
            
            "prepare:setup": {
                "extends": ".upid_base",
                "stage": "prepare",
                "script": [
                    "echo 'Setting up UPID environment'",
                    "upid config validate",
                    "upid cluster connect --cluster-id $CLUSTER_ID --verify"
                ],
                "artifacts": {
                    "reports": {
                        "dotenv": "upid.env"
                    },
                    "expire_in": "1 hour"
                }
            },
            
            "analyze:cost_analysis": {
                "extends": ".upid_base",
                "stage": "analyze",
                "script": [
                    "upid analyze cost --cluster-id $CLUSTER_ID --output json > cost-analysis.json",
                    "upid analyze idle --cluster-id $CLUSTER_ID --output json > idle-workloads.json",
                    "upid analyze waste --cluster-id $CLUSTER_ID --output json > waste-analysis.json"
                ],
                "artifacts": {
                    "reports": {
                        "coverage_report": {
                            "coverage_format": "generic",
                            "path": "cost-analysis.json"
                        }
                    },
                    "paths": [
                        "*.json"
                    ],
                    "expire_in": "1 week"
                },
                "dependencies": ["prepare:setup"]
            },
            
            "analyze:ml_predictions": {
                "extends": ".upid_base",
                "stage": "analyze",
                "script": [
                    "upid ml predict --cluster-id $CLUSTER_ID --model cost --output json > cost-predictions.json",
                    "upid ml predict --cluster-id $CLUSTER_ID --model anomaly --output json > anomaly-detection.json"
                ],
                "artifacts": {
                    "paths": [
                        "*-predictions.json",
                        "*-detection.json"
                    ],
                    "expire_in": "1 week"
                },
                "dependencies": ["prepare:setup"],
                "allow_failure": True
            },
            
            "optimize:generate_strategies": {
                "extends": ".upid_base",
                "stage": "optimize",
                "script": [
                    "upid optimize strategies --cluster-id $CLUSTER_ID --dry-run --output json > optimization-strategies.json",
                    "upid optimize zero-pod --cluster-id $CLUSTER_ID --dry-run --output json > zero-pod-optimization.json",
                    "upid optimize rightsizing --cluster-id $CLUSTER_ID --dry-run --output json > rightsizing-optimization.json"
                ],
                "artifacts": {
                    "paths": [
                        "*-optimization.json",
                        "*-strategies.json"
                    ],
                    "expire_in": "1 week"
                },
                "dependencies": ["analyze:cost_analysis"]
            },
            
            "optimize:safety_validation": {
                "extends": ".upid_base",
                "stage": "optimize",
                "script": [
                    "upid validate optimization --input optimization-strategies.json --safety-threshold 0.8",
                    "upid simulate optimization --input optimization-strategies.json --output simulation-results.json"
                ],
                "artifacts": {
                    "paths": [
                        "simulation-results.json"
                    ],
                    "expire_in": "1 week"
                },
                "dependencies": ["optimize:generate_strategies"]
            },
            
            "validate:pre_deployment": {
                "extends": ".upid_base",
                "stage": "validate",
                "script": [
                    "upid validate cluster --cluster-id $CLUSTER_ID",
                    "upid backup create --cluster-id $CLUSTER_ID --name pre-optimization-backup"
                ],
                "dependencies": ["optimize:safety_validation"],
                "when": "manual",
                "allow_failure": False
            },
            
            "deploy:apply_optimizations": {
                "extends": ".upid_base",
                "stage": "deploy",
                "script": [
                    "echo 'Applying UPID optimizations'",
                    "upid optimize apply --cluster-id $CLUSTER_ID --strategies optimization-strategies.json --confirm",
                    "upid monitor start --cluster-id $CLUSTER_ID --duration 300"
                ],
                "artifacts": {
                    "paths": [
                        "optimization-results.json"
                    ],
                    "expire_in": "1 month"
                },
                "dependencies": ["validate:pre_deployment"],
                "when": "manual",
                "timeout": "30 minutes"
            },
            
            "deploy:post_validation": {
                "extends": ".upid_base",
                "stage": "deploy",
                "script": [
                    "sleep 60",  # Wait for changes to take effect
                    "upid analyze cost --cluster-id $CLUSTER_ID --output json > post-optimization-cost.json",
                    "upid report optimization --before cost-analysis.json --after post-optimization-cost.json --output markdown > optimization-report.md"
                ],
                "artifacts": {
                    "paths": [
                        "post-optimization-cost.json",
                        "optimization-report.md"
                    ],
                    "expire_in": "1 month"
                },
                "dependencies": ["deploy:apply_optimizations"]
            }
        }
        
        return GitLabPipeline(
            name="UPID Cost Optimization",
            description="Automated Kubernetes cost optimization with UPID CLI",
            stages=stages,
            variables=variables,
            jobs=jobs,
            pipeline_file=".gitlab-ci.yml"
        )
    
    def generate_deployment_validation_pipeline(self, deployment_config: Dict[str, Any]) -> GitLabPipeline:
        """Generate deployment validation pipeline"""
        
        stages = ["validate", "analyze", "deploy", "monitor"]
        
        variables = {
            "CLUSTER_ID": deployment_config.get("cluster_id", "default"),
            "NAMESPACE": deployment_config.get("namespace", "default"),
            "DEPLOYMENT_NAME": deployment_config.get("deployment_name", "app")
        }
        
        jobs = {
            ".upid_base": {
                "image": self.config.upid_runner_image,
                "before_script": [
                    "upid --version",
                    "kubectl version --client"
                ]
            },
            
            "validate:manifests": {
                "extends": ".upid_base",
                "stage": "validate",
                "script": [
                    "upid validate manifests --path k8s/ --output json > validation-results.json",
                    "upid estimate cost --manifests k8s/ --cluster-id $CLUSTER_ID --output json > cost-estimate.json"
                ],
                "artifacts": {
                    "reports": {
                        "junit": "validation-results.xml"
                    },
                    "paths": [
                        "*.json"
                    ],
                    "expire_in": "1 week"
                },
                "rules": [
                    {
                        "if": "$CI_PIPELINE_SOURCE == 'merge_request_event'",
                        "changes": ["k8s/**/*", "manifests/**/*", "helm/**/*"]
                    }
                ]
            },
            
            "analyze:security_scan": {
                "extends": ".upid_base",
                "stage": "analyze",
                "script": [
                    "upid security scan --path k8s/ --output json > security-scan.json",
                    "upid security compliance --cluster-id $CLUSTER_ID --standard cis --output json > compliance-check.json"
                ],
                "artifacts": {
                    "reports": {
                        "sast": "security-scan.json"
                    },
                    "expire_in": "1 week"
                },
                "dependencies": ["validate:manifests"]
            },
            
            "analyze:impact_assessment": {
                "extends": ".upid_base",
                "stage": "analyze",
                "script": [
                    "upid analyze cost --cluster-id $CLUSTER_ID --output json > pre-deployment-cost.json",
                    "upid impact assess --manifests k8s/ --cluster-id $CLUSTER_ID --output json > impact-assessment.json"
                ],
                "artifacts": {
                    "paths": [
                        "*-cost.json",
                        "*-assessment.json"
                    ],
                    "expire_in": "1 week"
                },
                "dependencies": ["validate:manifests"]
            },
            
            "deploy:staging": {
                "extends": ".upid_base",
                "stage": "deploy",
                "environment": {
                    "name": "staging",
                    "url": "https://staging.example.com"
                },
                "script": [
                    "kubectl apply -f k8s/ --namespace $NAMESPACE --dry-run=server",
                    "kubectl apply -f k8s/ --namespace $NAMESPACE",
                    "kubectl rollout status deployment/$DEPLOYMENT_NAME --namespace $NAMESPACE --timeout=300s"
                ],
                "rules": [
                    {
                        "if": "$CI_COMMIT_BRANCH == 'main'"
                    }
                ],
                "dependencies": ["analyze:impact_assessment", "analyze:security_scan"]
            },
            
            "deploy:production": {
                "extends": ".upid_base",
                "stage": "deploy",
                "environment": {
                    "name": "production",
                    "url": "https://production.example.com"
                },
                "script": [
                    "kubectl apply -f k8s/ --namespace $NAMESPACE",
                    "kubectl rollout status deployment/$DEPLOYMENT_NAME --namespace $NAMESPACE --timeout=600s"
                ],
                "when": "manual",
                "only": ["main"],
                "dependencies": ["deploy:staging"]
            },
            
            "monitor:post_deployment": {
                "extends": ".upid_base",
                "stage": "monitor",
                "script": [
                    "sleep 120",  # Wait for deployment to stabilize
                    "upid analyze cost --cluster-id $CLUSTER_ID --output json > post-deployment-cost.json",
                    "upid report deployment --before pre-deployment-cost.json --after post-deployment-cost.json --output markdown > deployment-report.md"
                ],
                "artifacts": {
                    "paths": [
                        "post-deployment-cost.json",
                        "deployment-report.md"
                    ],
                    "expire_in": "1 month"
                },
                "dependencies": ["deploy:production"]
            }
        }
        
        return GitLabPipeline(
            name="UPID Deployment Validation",
            description="Validate Kubernetes deployments with cost impact analysis",
            stages=stages,
            variables=variables,
            jobs=jobs,
            pipeline_file="deployment-validation.gitlab-ci.yml"
        )
    
    def generate_monitoring_pipeline(self, monitoring_config: Dict[str, Any]) -> GitLabPipeline:
        """Generate monitoring and alerting pipeline"""
        
        stages = ["monitor", "analyze", "alert"]
        
        variables = {
            "CLUSTER_ID": monitoring_config.get("cluster_id", "default"),
            "MONITORING_INTERVAL": "300",  # 5 minutes
            "ALERT_THRESHOLD": "0.8"
        }
        
        jobs = {
            ".upid_base": {
                "image": self.config.upid_runner_image,
                "before_script": ["upid --version"]
            },
            
            "monitor:performance": {
                "extends": ".upid_base",
                "stage": "monitor",
                "script": [
                    "upid analyze performance --cluster-id $CLUSTER_ID --output json > performance-analysis.json",
                    "upid ml predict --cluster-id $CLUSTER_ID --model anomaly --output json > anomaly-detection.json"
                ],
                "artifacts": {
                    "paths": [
                        "*-analysis.json",
                        "*-detection.json"
                    ],
                    "expire_in": "1 day"
                },
                "rules": [
                    {
                        "if": "$CI_PIPELINE_SOURCE == 'schedule'"
                    },
                    {
                        "if": "$CI_PIPELINE_SOURCE == 'trigger'"
                    }
                ]
            },
            
            "analyze:performance_trends": {
                "extends": ".upid_base",
                "stage": "analyze",
                "script": [
                    "upid trends analyze --cluster-id $CLUSTER_ID --window 24h --output json > trends-analysis.json",
                    "upid predict degradation --cluster-id $CLUSTER_ID --horizon 2h --output json > degradation-prediction.json"
                ],
                "artifacts": {
                    "paths": [
                        "*-analysis.json",
                        "*-prediction.json"
                    ],
                    "expire_in": "1 day"
                },
                "dependencies": ["monitor:performance"]
            },
            
            "alert:performance_issues": {
                "extends": ".upid_base",
                "stage": "alert",
                "script": [
                    "upid alert check --input performance-analysis.json --threshold $ALERT_THRESHOLD",
                    "if [ $? -ne 0 ]; then upid notify slack --message 'Performance degradation detected'; fi"
                ],
                "rules": [
                    {
                        "if": "$CI_PIPELINE_SOURCE == 'schedule'",
                        "when": "on_failure"
                    }
                ],
                "dependencies": ["analyze:performance_trends"],
                "allow_failure": True
            }
        }
        
        return GitLabPipeline(
            name="UPID Performance Monitoring",
            description="Continuous performance monitoring and alerting",
            stages=stages,
            variables=variables,
            jobs=jobs,
            pipeline_file="monitoring.gitlab-ci.yml"
        )


class GitLabCICDIntegration:
    """
    GitLab CI/CD integration for UPID CLI
    
    Features:
    - Automated pipeline generation
    - Cost optimization workflows
    - Deployment validation pipelines
    - Performance monitoring automation
    - Security scanning integration
    - MR-based cost analysis
    - Automated optimization suggestions
    """
    
    def __init__(self, pipeline_manager: PipelineManager, config: GitLabCICDConfig):
        self.pipeline_manager = pipeline_manager
        self.config = config
        self.template_generator = GitLabCICDTemplateGenerator(config)
        
        # GitLab API session
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("🔧 Initializing GitLab CI/CD integration")
    
    async def initialize(self) -> bool:
        """Initialize GitLab CI/CD integration"""
        try:
            logger.info("🚀 Initializing GitLab CI/CD integration...")
            
            # Initialize HTTP session
            headers = {}
            if self.config.gitlab_token:
                headers["Private-Token"] = self.config.gitlab_token
                headers["Content-Type"] = "application/json"
            
            self.session = aiohttp.ClientSession(headers=headers)
            
            # Validate GitLab API access
            if self.config.gitlab_token:
                await self._validate_gitlab_access()
            
            logger.info("✅ GitLab CI/CD integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GitLab CI/CD integration: {e}")
            return False
    
    async def _validate_gitlab_access(self) -> bool:
        """Validate GitLab API access"""
        try:
            if self.config.project_id:
                url = f"{self.config.gitlab_url}/api/v4/projects/{self.config.project_id}"
            elif self.config.project_path:
                encoded_path = self.config.project_path.replace("/", "%2F")
                url = f"{self.config.gitlab_url}/api/v4/projects/{encoded_path}"
            else:
                logger.warning("No project ID or path configured")
                return False
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    project_data = await response.json()
                    logger.info(f"✅ GitLab project validated: {project_data['name']}")
                    return True
                else:
                    logger.warning(f"GitLab API access validation failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.warning(f"GitLab API validation error: {e}")
            return False
    
    async def setup_project_pipelines(self, cluster_configs: List[Dict[str, Any]]) -> bool:
        """Setup UPID pipelines in GitLab project"""
        try:
            logger.info("🔧 Setting up UPID pipelines in GitLab project...")
            
            pipelines = []
            
            for cluster_config in cluster_configs:
                # Generate pipelines for each cluster
                cost_pipeline = self.template_generator.generate_cost_optimization_pipeline(cluster_config)
                deployment_pipeline = self.template_generator.generate_deployment_validation_pipeline(cluster_config)
                monitoring_pipeline = self.template_generator.generate_monitoring_pipeline(cluster_config)
                
                pipelines.extend([cost_pipeline, deployment_pipeline, monitoring_pipeline])
            
            # Create pipeline files in repository
            for pipeline in pipelines:
                await self._create_pipeline_file(pipeline)
            
            # Setup pipeline schedules
            await self._setup_pipeline_schedules()
            
            logger.info(f"✅ Successfully created {len(pipelines)} pipelines")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup project pipelines: {e}")
            return False
    
    async def _create_pipeline_file(self, pipeline: GitLabPipeline) -> bool:
        """Create pipeline file in GitLab repository"""
        try:
            pipeline_path = f"{self.config.ci_templates_dir}/{pipeline.pipeline_file}"
            pipeline_content = pipeline.to_yaml()
            
            # Create file via GitLab API
            if self.config.project_id:
                url = f"{self.config.gitlab_url}/api/v4/projects/{self.config.project_id}/repository/files/{pipeline_path.replace('/', '%2F')}"
            else:
                encoded_path = self.config.project_path.replace("/", "%2F")
                url = f"{self.config.gitlab_url}/api/v4/projects/{encoded_path}/repository/files/{pipeline_path.replace('/', '%2F')}"
            
            # Check if file exists
            async with self.session.get(url, params={"ref": "main"}) as response:
                if response.status == 200:
                    # File exists, update it
                    existing_file = await response.json()
                    
                    payload = {
                        "branch": "main",
                        "commit_message": f"Update UPID pipeline: {pipeline.name}",
                        "content": pipeline_content,
                        "last_commit_id": existing_file.get("last_commit_id")
                    }
                    
                    async with self.session.put(url, json=payload) as put_response:
                        if put_response.status in [200, 201]:
                            logger.info(f"✅ Updated pipeline: {pipeline.pipeline_file}")
                            return True
                        else:
                            logger.error(f"❌ Failed to update pipeline {pipeline.pipeline_file}: {put_response.status}")
                            return False
                else:
                    # File doesn't exist, create it
                    payload = {
                        "branch": "main",
                        "commit_message": f"Add UPID pipeline: {pipeline.name}",
                        "content": pipeline_content
                    }
                    
                    async with self.session.post(url, json=payload) as post_response:
                        if post_response.status in [200, 201]:
                            logger.info(f"✅ Created pipeline: {pipeline.pipeline_file}")
                            return True
                        else:
                            logger.error(f"❌ Failed to create pipeline {pipeline.pipeline_file}: {post_response.status}")
                            return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating pipeline file {pipeline.pipeline_file}: {e}")
            return False
    
    async def _setup_pipeline_schedules(self) -> bool:
        """Setup pipeline schedules"""
        try:
            schedules = [
                {
                    "description": "Daily cost optimization",
                    "ref": "main",
                    "cron": "0 2 * * *",  # Daily at 2 AM
                    "active": True,
                    "variables": [
                        {"key": "PIPELINE_TYPE", "value": "cost_optimization"}
                    ]
                },
                {
                    "description": "Performance monitoring",
                    "ref": "main", 
                    "cron": "*/15 * * * *",  # Every 15 minutes
                    "active": True,
                    "variables": [
                        {"key": "PIPELINE_TYPE", "value": "monitoring"}
                    ]
                }
            ]
            
            for schedule_config in schedules:
                await self._create_pipeline_schedule(schedule_config)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup pipeline schedules: {e}")
            return False
    
    async def _create_pipeline_schedule(self, schedule_config: Dict[str, Any]) -> bool:
        """Create a pipeline schedule"""
        try:
            if self.config.project_id:
                url = f"{self.config.gitlab_url}/api/v4/projects/{self.config.project_id}/pipeline_schedules"
            else:
                encoded_path = self.config.project_path.replace("/", "%2F")
                url = f"{self.config.gitlab_url}/api/v4/projects/{encoded_path}/pipeline_schedules"
            
            async with self.session.post(url, json=schedule_config) as response:
                if response.status in [200, 201]:
                    schedule_data = await response.json()
                    logger.info(f"✅ Created pipeline schedule: {schedule_config['description']}")
                    return True
                else:
                    logger.warning(f"Failed to create schedule: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating pipeline schedule: {e}")
            return False
    
    async def trigger_pipeline(self, ref: str = "main", variables: Dict[str, Any] = None) -> bool:
        """Trigger a GitLab pipeline"""
        try:
            if self.config.project_id:
                url = f"{self.config.gitlab_url}/api/v4/projects/{self.config.project_id}/trigger/pipeline"
            else:
                encoded_path = self.config.project_path.replace("/", "%2F")
                url = f"{self.config.gitlab_url}/api/v4/projects/{encoded_path}/trigger/pipeline"
            
            payload = {
                "ref": ref,
                "variables": variables or {}
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status in [200, 201]:
                    pipeline_data = await response.json()
                    logger.info(f"✅ Triggered pipeline: {pipeline_data.get('id')}")
                    return True
                else:
                    logger.error(f"❌ Failed to trigger pipeline: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error triggering pipeline: {e}")
            return False
    
    async def get_pipeline_status(self, pipeline_id: int) -> Optional[Dict[str, Any]]:
        """Get pipeline status"""
        try:
            if self.config.project_id:
                url = f"{self.config.gitlab_url}/api/v4/projects/{self.config.project_id}/pipelines/{pipeline_id}"
            else:
                encoded_path = self.config.project_path.replace("/", "%2F")
                url = f"{self.config.gitlab_url}/api/v4/projects/{encoded_path}/pipelines/{pipeline_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"❌ Failed to get pipeline status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error getting pipeline status: {e}")
            return None
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Process GitLab webhook event"""
        try:
            event_type = webhook_data.get("object_kind")
            
            logger.info(f"📨 Processing GitLab webhook: {event_type}")
            
            if event_type == "merge_request":
                await self._handle_merge_request_event(webhook_data)
            elif event_type == "push":
                await self._handle_push_event(webhook_data)
            elif event_type == "pipeline":
                await self._handle_pipeline_event(webhook_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            return False
    
    async def _handle_merge_request_event(self, webhook_data: Dict[str, Any]):
        """Handle merge request event"""
        mr_data = webhook_data.get("object_attributes", {})
        action = mr_data.get("action")
        
        if action in ["open", "update"]:
            # Check if MR affects Kubernetes manifests
            changes = webhook_data.get("changes", {})
            
            # Trigger deployment validation pipeline
            await self.trigger_pipeline(
                ref=mr_data.get("source_branch", "main"),
                variables={
                    "MR_IID": str(mr_data.get("iid")),
                    "PIPELINE_TYPE": "deployment_validation"
                }
            )
    
    async def _handle_push_event(self, webhook_data: Dict[str, Any]):
        """Handle push event"""
        ref = webhook_data.get("ref", "")
        
        if ref == "refs/heads/main":
            # Trigger monitoring on main branch
            await self.trigger_pipeline(
                ref="main",
                variables={"PIPELINE_TYPE": "monitoring"}
            )
    
    async def _handle_pipeline_event(self, webhook_data: Dict[str, Any]):
        """Handle pipeline event"""
        pipeline_data = webhook_data.get("object_attributes", {})
        status = pipeline_data.get("status")
        
        if status == "failed":
            logger.warning(f"Pipeline failed: {pipeline_data.get('id')}")
        elif status == "success":
            logger.info(f"Pipeline completed: {pipeline_data.get('id')}")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get GitLab CI/CD integration status"""
        pipelines_info = []
        
        if self.session and self.config.gitlab_token:
            try:
                if self.config.project_id:
                    url = f"{self.config.gitlab_url}/api/v4/projects/{self.config.project_id}/pipelines"
                else:
                    encoded_path = self.config.project_path.replace("/", "%2F")
                    url = f"{self.config.gitlab_url}/api/v4/projects/{encoded_path}/pipelines"
                
                async with self.session.get(url, params={"per_page": 10}) as response:
                    if response.status == 200:
                        pipelines_info = await response.json()
            except Exception as e:
                logger.warning(f"Failed to get pipelines info: {e}")
        
        return {
            "config": asdict(self.config),
            "gitlab_api_connected": bool(self.session and self.config.gitlab_token),
            "project_configured": bool(self.config.project_id or self.config.project_path),
            "recent_pipelines_count": len(pipelines_info),
            "recent_pipelines": [
                {
                    "id": p.get("id"),
                    "status": p.get("status"),
                    "ref": p.get("ref"),
                    "created_at": p.get("created_at")
                }
                for p in pipelines_info[:5]  # Limit to first 5
            ]
        }
    
    async def shutdown(self):
        """Shutdown GitLab CI/CD integration"""
        logger.info("🛑 Shutting down GitLab CI/CD integration...")
        
        if self.session:
            await self.session.close()
        
        logger.info("✅ GitLab CI/CD integration shutdown complete")


# Export main classes
__all__ = [
    'GitLabCICDIntegration',
    'GitLabCICDConfig',
    'GitLabPipeline',
    'GitLabCICDTemplateGenerator'
]