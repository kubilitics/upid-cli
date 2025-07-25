#!/usr/bin/env python3
"""
UPID CLI - GitHub Actions Integration
Phase 6: Platform Integration - Task 6.1
Enterprise-grade GitHub Actions integration for automated UPID workflows
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
class GitHubActionsConfig:
    """GitHub Actions integration configuration"""
    github_token: Optional[str] = None
    repository_owner: str = ""
    repository_name: str = ""
    webhook_secret: Optional[str] = None
    workflow_templates_dir: str = ".github/workflows"
    upid_action_version: str = "v1"
    enable_auto_pr: bool = True
    enable_cost_comments: bool = True
    enable_optimization_suggestions: bool = True


@dataclass
class GitHubWorkflow:
    """GitHub Actions workflow definition"""
    name: str
    description: str
    triggers: List[str]
    jobs: Dict[str, Any]
    workflow_file: str
    
    def to_yaml(self) -> str:
        """Convert workflow to YAML format"""
        workflow_dict = {
            "name": self.name,
            "on": self.triggers,
            "jobs": self.jobs
        }
        return yaml.dump(workflow_dict, default_flow_style=False, sort_keys=False)


class GitHubActionsTemplateGenerator:
    """Generates GitHub Actions workflow templates"""
    
    def __init__(self, config: GitHubActionsConfig):
        self.config = config
    
    def generate_cost_optimization_workflow(self, cluster_config: Dict[str, Any]) -> GitHubWorkflow:
        """Generate cost optimization workflow"""
        
        jobs = {
            "upid-cost-optimization": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout",
                        "uses": "actions/checkout@v4"
                    },
                    {
                        "name": "Setup UPID CLI",
                        "uses": f"upid/setup-upid@{self.config.upid_action_version}",
                        "with": {
                            "version": "latest"
                        }
                    },
                    {
                        "name": "Authenticate with cluster",
                        "env": {
                            "KUBECONFIG": "${{ secrets.KUBECONFIG }}"
                        },
                        "run": "upid auth validate"
                    },
                    {
                        "name": "Analyze cluster costs",
                        "id": "cost-analysis",
                        "run": f"upid analyze cost --cluster-id {cluster_config.get('cluster_id', 'default')} --output json > cost-analysis.json"
                    },
                    {
                        "name": "Detect idle workloads",
                        "id": "idle-detection", 
                        "run": f"upid analyze idle --cluster-id {cluster_config.get('cluster_id', 'default')} --output json > idle-workloads.json"
                    },
                    {
                        "name": "Generate optimization recommendations",
                        "id": "optimization",
                        "run": f"upid optimize strategies --cluster-id {cluster_config.get('cluster_id', 'default')} --dry-run --output json > optimization-recommendations.json"
                    },
                    {
                        "name": "Create optimization PR",
                        "if": "steps.optimization.outputs.savings > 100",
                        "uses": "peter-evans/create-pull-request@v5",
                        "with": {
                            "token": "${{ secrets.GITHUB_TOKEN }}",
                            "commit-message": "💰 UPID: Automated cost optimization recommendations",
                            "title": "🤖 UPID Cost Optimization - Potential savings: ${{ steps.optimization.outputs.savings }}",
                            "body": self._generate_pr_body_template(),
                            "branch": "upid/cost-optimization-${{ github.run_number }}",
                            "labels": "upid,cost-optimization,automated"
                        }
                    },
                    {
                        "name": "Upload analysis artifacts",
                        "uses": "actions/upload-artifact@v3",
                        "with": {
                            "name": "upid-analysis-${{ github.run_number }}",
                            "path": "*.json"
                        }
                    },
                    {
                        "name": "Comment on PR with cost analysis",
                        "if": "github.event_name == 'pull_request' && github.event.action == 'opened'",
                        "uses": "actions/github-script@v6",
                        "with": {
                            "script": self._generate_pr_comment_script()
                        }
                    }
                ]
            }
        }
        
        triggers = [
            "schedule",
            {"cron": "0 2 * * *"},  # Daily at 2 AM
            "workflow_dispatch",
            {
                "pull_request": {
                    "types": ["opened", "synchronize"],
                    "paths": ["k8s/**", "helm/**", "manifests/**"]
                }
            }
        ]
        
        return GitHubWorkflow(
            name="UPID Cost Optimization",
            description="Automated Kubernetes cost optimization with UPID CLI",
            triggers=triggers,
            jobs=jobs,
            workflow_file="upid-cost-optimization.yml"
        )
    
    def generate_deployment_validation_workflow(self, deployment_config: Dict[str, Any]) -> GitHubWorkflow:
        """Generate deployment validation workflow"""
        
        jobs = {
            "upid-deployment-validation": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout",
                        "uses": "actions/checkout@v4"
                    },
                    {
                        "name": "Setup UPID CLI",
                        "uses": f"upid/setup-upid@{self.config.upid_action_version}",
                        "with": {
                            "version": "latest"
                        }
                    },
                    {
                        "name": "Pre-deployment cost analysis",
                        "id": "pre-analysis",
                        "env": {
                            "KUBECONFIG": "${{ secrets.KUBECONFIG }}"
                        },
                        "run": f"upid analyze cost --cluster-id {deployment_config.get('cluster_id', 'default')} --output json > pre-deployment-cost.json"
                    },
                    {
                        "name": "Validate deployment manifests",
                        "run": "upid validate manifests --path ${{ github.workspace }}/k8s/ --output json > validation-results.json"
                    },
                    {
                        "name": "Estimate deployment cost impact",
                        "id": "cost-estimate",
                        "run": "upid estimate cost --manifests ${{ github.workspace }}/k8s/ --cluster-id ${{ vars.CLUSTER_ID }} --output json > cost-estimate.json"
                    },
                    {
                        "name": "Deploy to staging",
                        "if": "github.ref == 'refs/heads/main'",
                        "env": {
                            "KUBECONFIG": "${{ secrets.STAGING_KUBECONFIG }}"
                        },
                        "run": "kubectl apply -f k8s/ --dry-run=server"
                    },
                    {
                        "name": "Post-deployment validation",
                        "if": "success()",
                        "run": "upid analyze cost --cluster-id staging --output json > post-deployment-cost.json"
                    },
                    {
                        "name": "Generate cost impact report", 
                        "run": "upid report cost-impact --before pre-deployment-cost.json --after post-deployment-cost.json --output markdown > cost-impact-report.md"
                    },
                    {
                        "name": "Post cost impact as comment",
                        "if": "github.event_name == 'pull_request'",
                        "uses": "actions/github-script@v6",
                        "with": {
                            "script": self._generate_cost_impact_comment_script()
                        }
                    }
                ]
            }
        }
        
        triggers = [
            {
                "push": {
                    "branches": ["main", "develop"],
                    "paths": ["k8s/**", "helm/**", "manifests/**"]
                }
            },
            {
                "pull_request": {
                    "types": ["opened", "synchronize"],
                    "paths": ["k8s/**", "helm/**", "manifests/**"]
                }
            }
        ]
        
        return GitHubWorkflow(
            name="UPID Deployment Validation",
            description="Validate Kubernetes deployments with cost impact analysis",
            triggers=triggers,
            jobs=jobs,
            workflow_file="upid-deployment-validation.yml"
        )
    
    def generate_performance_monitoring_workflow(self, monitoring_config: Dict[str, Any]) -> GitHubWorkflow:
        """Generate performance monitoring workflow"""
        
        jobs = {
            "upid-performance-monitoring": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Setup UPID CLI",
                        "uses": f"upid/setup-upid@{self.config.upid_action_version}"
                    },
                    {
                        "name": "Cluster performance analysis",
                        "env": {
                            "KUBECONFIG": "${{ secrets.KUBECONFIG }}"
                        },
                        "run": f"upid analyze performance --cluster-id {monitoring_config.get('cluster_id', 'default')} --output json > performance-analysis.json"
                    },
                    {
                        "name": "ML-based anomaly detection",
                        "run": f"upid ml predict --cluster-id {monitoring_config.get('cluster_id', 'default')} --model anomaly --output json > anomaly-detection.json"
                    },
                    {
                        "name": "Generate performance report",
                        "run": "upid report performance --input performance-analysis.json --format markdown > performance-report.md"
                    },
                    {
                        "name": "Check for performance degradation",
                        "id": "performance-check",
                        "run": """
                        if upid analyze performance --cluster-id ${{ vars.CLUSTER_ID }} --threshold 0.8; then
                          echo "performance_ok=true" >> $GITHUB_OUTPUT
                        else
                          echo "performance_ok=false" >> $GITHUB_OUTPUT
                        fi
                        """
                    },
                    {
                        "name": "Create performance issue",
                        "if": "steps.performance-check.outputs.performance_ok == 'false'",
                        "uses": "actions/github-script@v6",
                        "with": {
                            "script": self._generate_performance_issue_script()
                        }
                    },
                    {
                        "name": "Send Slack notification",
                        "if": "steps.performance-check.outputs.performance_ok == 'false'",
                        "uses": "8398a7/action-slack@v3",
                        "with": {
                            "status": "custom",
                            "custom_payload": {
                                "text": "🚨 Performance degradation detected in cluster ${{ vars.CLUSTER_ID }}",
                                "blocks": [
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": "Performance monitoring alert from UPID CLI"
                                        }
                                    }
                                ]
                            }
                        },
                        "env": {
                            "SLACK_WEBHOOK_URL": "${{ secrets.SLACK_WEBHOOK }}"
                        }
                    }
                ]
            }
        }
        
        triggers = [
            "schedule",
            {"cron": "*/15 * * * *"},  # Every 15 minutes
            "workflow_dispatch"
        ]
        
        return GitHubWorkflow(
            name="UPID Performance Monitoring",
            description="Continuous performance monitoring and anomaly detection",
            triggers=triggers,
            jobs=jobs,
            workflow_file="upid-performance-monitoring.yml"
        )
    
    def generate_security_scan_workflow(self, security_config: Dict[str, Any]) -> GitHubWorkflow:
        """Generate security scanning workflow"""
        
        jobs = {
            "upid-security-scan": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout",
                        "uses": "actions/checkout@v4"
                    },
                    {
                        "name": "Setup UPID CLI",
                        "uses": f"upid/setup-upid@{self.config.upid_action_version}"
                    },
                    {
                        "name": "Scan Kubernetes manifests",
                        "run": "upid security scan --path k8s/ --output json > security-scan.json"
                    },
                    {
                        "name": "Check security compliance",
                        "run": "upid security compliance --cluster-id ${{ vars.CLUSTER_ID }} --standard cis --output json > compliance-check.json"
                    },
                    {
                        "name": "Generate security report",
                        "run": "upid report security --input security-scan.json --format markdown > security-report.md"
                    },
                    {
                        "name": "Upload security artifacts",
                        "uses": "actions/upload-artifact@v3",
                        "with": {
                            "name": "upid-security-scan-${{ github.run_number }}",
                            "path": "*-scan.json"
                        }
                    }
                ]
            }
        }
        
        triggers = [
            {
                "push": {
                    "branches": ["main"],
                    "paths": ["k8s/**", "helm/**"]
                }
            },
            "schedule",
            {"cron": "0 3 * * 1"},  # Weekly on Monday at 3 AM
            "workflow_dispatch"
        ]
        
        return GitHubWorkflow(
            name="UPID Security Scan",
            description="Security scanning and compliance checking for Kubernetes resources",
            triggers=triggers,
            jobs=jobs,
            workflow_file="upid-security-scan.yml"
        )
    
    def _generate_pr_body_template(self) -> str:
        """Generate PR body template for cost optimization"""
        return """
## 🤖 UPID Automated Cost Optimization

This pull request contains automated cost optimization recommendations generated by UPID CLI.

### 📊 Cost Analysis Summary
- **Current Monthly Cost**: ${{ steps.cost-analysis.outputs.current_cost }}
- **Potential Savings**: ${{ steps.optimization.outputs.savings }}
- **Savings Percentage**: {{ steps.optimization.outputs.savings_percentage }}%
- **Idle Workloads Detected**: {{ steps.idle-detection.outputs.idle_count }}

### 🎯 Optimization Recommendations
{{ steps.optimization.outputs.recommendations }}

### 🔒 Safety Information
- All optimizations are tested in staging environment
- Rollback plan is automatically generated
- Safety score: {{ steps.optimization.outputs.safety_score }}/1.0

### 🚀 Next Steps
1. Review the optimization recommendations
2. Test in staging environment if needed
3. Approve and merge to apply optimizations
4. Monitor cluster performance post-optimization

---
*Generated by UPID CLI v{{ steps.setup.outputs.version }} on {{ github.run_date }}*
        """
    
    def _generate_pr_comment_script(self) -> str:
        """Generate PR comment script for cost analysis"""
        return """
        const fs = require('fs');
        
        try {
          const costAnalysis = JSON.parse(fs.readFileSync('cost-analysis.json', 'utf8'));
          const idleWorkloads = JSON.parse(fs.readFileSync('idle-workloads.json', 'utf8'));
          
          const comment = `
## 💰 UPID Cost Analysis Report

### Current Cluster Costs
- **Monthly Cost**: $${costAnalysis.total_monthly_cost}
- **Compute**: $${costAnalysis.compute_cost}
- **Storage**: $${costAnalysis.storage_cost}
- **Network**: $${costAnalysis.network_cost}

### Optimization Opportunities
- **Idle Workloads**: ${idleWorkloads.idle_pods} pods
- **Potential Savings**: $${idleWorkloads.potential_savings}
- **Waste Percentage**: ${costAnalysis.waste_percentage}%

### Recommendations
${costAnalysis.recommendations.map(r => '- ' + r).join('\\n')}

---
*Analyzed by UPID CLI on ${new Date().toISOString()}*
          `;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
        } catch (error) {
          console.log('Error posting cost analysis comment:', error);
        }
        """
    
    def _generate_cost_impact_comment_script(self) -> str:
        """Generate cost impact comment script"""
        return """
        const fs = require('fs');
        
        try {
          const report = fs.readFileSync('cost-impact-report.md', 'utf8');
          
          const comment = `
## 📈 Deployment Cost Impact Analysis

${report}

---
*Generated by UPID CLI Deployment Validation*
          `;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
        } catch (error) {
          console.log('Error posting cost impact comment:', error);
        }
        """
    
    def _generate_performance_issue_script(self) -> str:
        """Generate performance issue creation script"""
        return """
        const fs = require('fs');
        
        try {
          const performanceData = JSON.parse(fs.readFileSync('performance-analysis.json', 'utf8'));
          const anomalyData = JSON.parse(fs.readFileSync('anomaly-detection.json', 'utf8'));
          
          const title = `🚨 Performance Degradation Alert - Cluster ${process.env.CLUSTER_ID}`;
          const body = `
## Performance Monitoring Alert

### Issue Summary
Performance degradation detected in cluster **${process.env.CLUSTER_ID}**.

### Performance Metrics
- **CPU Utilization**: ${performanceData.cpu_utilization}%
- **Memory Utilization**: ${performanceData.memory_utilization}%
- **Response Time**: ${performanceData.avg_response_time}ms
- **Error Rate**: ${performanceData.error_rate}%

### Anomaly Detection
${anomalyData.anomalies.map(a => `- ${a.type}: ${a.description}`).join('\\n')}

### Recommended Actions
${performanceData.recommendations.map(r => `- ${r}`).join('\\n')}

### Auto-assigned Labels
- performance
- alert
- cluster-${process.env.CLUSTER_ID}

---
*Detected by UPID CLI Performance Monitoring on ${new Date().toISOString()}*
          `;
          
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: title,
            body: body,
            labels: ['performance', 'alert', 'upid', `cluster-${process.env.CLUSTER_ID}`]
          });
        } catch (error) {
          console.log('Error creating performance issue:', error);
        }
        """


class GitHubActionsIntegration:
    """
    GitHub Actions integration for UPID CLI
    
    Features:
    - Automated workflow generation
    - Cost optimization workflows
    - Deployment validation pipelines
    - Performance monitoring automation
    - Security scanning integration
    - PR-based cost analysis
    - Automated optimization suggestions
    """
    
    def __init__(self, pipeline_manager: PipelineManager, config: GitHubActionsConfig):
        self.pipeline_manager = pipeline_manager
        self.config = config
        self.template_generator = GitHubActionsTemplateGenerator(config)
        
        # GitHub API session
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("🔧 Initializing GitHub Actions integration")
    
    async def initialize(self) -> bool:
        """Initialize GitHub Actions integration"""
        try:
            logger.info("🚀 Initializing GitHub Actions integration...")
            
            # Initialize HTTP session
            headers = {}
            if self.config.github_token:
                headers["Authorization"] = f"token {self.config.github_token}"
                headers["Accept"] = "application/vnd.github.v3+json"
            
            self.session = aiohttp.ClientSession(headers=headers)
            
            # Validate GitHub API access
            if self.config.github_token:
                await self._validate_github_access()
            
            logger.info("✅ GitHub Actions integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GitHub Actions integration: {e}")
            return False
    
    async def _validate_github_access(self) -> bool:
        """Validate GitHub API access"""
        try:
            if not self.config.repository_owner or not self.config.repository_name:
                logger.warning("Repository owner/name not configured")
                return False
            
            url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    repo_data = await response.json()
                    logger.info(f"✅ GitHub repository validated: {repo_data['full_name']}")
                    return True
                else:
                    logger.warning(f"GitHub API access validation failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.warning(f"GitHub API validation error: {e}")
            return False
    
    async def setup_repository_workflows(self, cluster_configs: List[Dict[str, Any]]) -> bool:
        """Setup UPID workflows in GitHub repository"""
        try:
            logger.info("🔧 Setting up UPID workflows in GitHub repository...")
            
            workflows = []
            
            for cluster_config in cluster_configs:
                # Generate workflows for each cluster
                cost_workflow = self.template_generator.generate_cost_optimization_workflow(cluster_config)
                deployment_workflow = self.template_generator.generate_deployment_validation_workflow(cluster_config)
                monitoring_workflow = self.template_generator.generate_performance_monitoring_workflow(cluster_config)
                security_workflow = self.template_generator.generate_security_scan_workflow(cluster_config)
                
                workflows.extend([cost_workflow, deployment_workflow, monitoring_workflow, security_workflow])
            
            # Create workflows in repository
            for workflow in workflows:
                await self._create_workflow_file(workflow)
            
            # Create UPID action setup
            await self._create_upid_action_setup()
            
            logger.info(f"✅ Successfully created {len(workflows)} workflows")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup repository workflows: {e}")
            return False
    
    async def _create_workflow_file(self, workflow: GitHubWorkflow) -> bool:
        """Create workflow file in GitHub repository"""
        try:
            workflow_path = f".github/workflows/{workflow.workflow_file}"
            workflow_content = workflow.to_yaml()
            
            # Create file via GitHub API
            url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}/contents/{workflow_path}"
            
            # Check if file exists
            async with self.session.get(url) as response:
                if response.status == 200:
                    # File exists, update it
                    existing_file = await response.json()
                    sha = existing_file['sha']
                    
                    payload = {
                        "message": f"Update UPID workflow: {workflow.name}",
                        "content": base64.b64encode(workflow_content.encode()).decode(),
                        "sha": sha
                    }
                else:
                    # File doesn't exist, create it
                    payload = {
                        "message": f"Add UPID workflow: {workflow.name}",
                        "content": base64.b64encode(workflow_content.encode()).decode()
                    }
            
            async with self.session.put(url, json=payload) as response:
                if response.status in [200, 201]:
                    logger.info(f"✅ Created/updated workflow: {workflow.workflow_file}")
                    return True
                else:
                    logger.error(f"❌ Failed to create workflow {workflow.workflow_file}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating workflow file {workflow.workflow_file}: {e}")
            return False
    
    async def _create_upid_action_setup(self) -> bool:
        """Create UPID CLI setup action"""
        try:
            action_yml_content = """
name: 'Setup UPID CLI'
description: 'Setup UPID CLI for GitHub Actions workflows'
inputs:
  version:
    description: 'UPID CLI version to install'
    required: false
    default: 'latest'
  install-path:
    description: 'Installation path for UPID CLI'
    required: false
    default: '/usr/local/bin'
outputs:
  version:
    description: 'The installed UPID CLI version'
    value: ${{ steps.install.outputs.version }}
runs:
  using: 'composite'
  steps:
    - name: Install UPID CLI
      id: install
      shell: bash
      run: |
        echo "Installing UPID CLI..."
        
        # Download UPID CLI binary
        if [ "${{ inputs.version }}" = "latest" ]; then
          VERSION=$(curl -s https://api.github.com/repos/upid/upid-cli/releases/latest | grep tag_name | cut -d '"' -f 4)
        else
          VERSION="${{ inputs.version }}"
        fi
        
        # Determine platform
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        
        case $ARCH in
          x86_64) ARCH="amd64" ;;
          arm64|aarch64) ARCH="arm64" ;;
        esac
        
        BINARY_NAME="upid-${VERSION}-${OS}-${ARCH}"
        DOWNLOAD_URL="https://github.com/upid/upid-cli/releases/download/${VERSION}/${BINARY_NAME}"
        
        # Download and install
        curl -L "$DOWNLOAD_URL" -o upid
        chmod +x upid
        sudo mv upid ${{ inputs.install-path }}/upid
        
        # Verify installation
        upid --version
        
        echo "version=${VERSION}" >> $GITHUB_OUTPUT
        echo "✅ UPID CLI ${VERSION} installed successfully"
    
    - name: Verify UPID CLI
      shell: bash
      run: |
        upid --help
        echo "✅ UPID CLI is ready for use"
            """
            
            action_path = ".github/actions/setup-upid/action.yml"
            
            # Create action file
            url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}/contents/{action_path}"
            
            payload = {
                "message": "Add UPID CLI setup action",
                "content": base64.b64encode(action_yml_content.encode()).decode()
            }
            
            async with self.session.put(url, json=payload) as response:
                if response.status in [200, 201]:
                    logger.info("✅ Created UPID CLI setup action")
                    return True
                else:
                    logger.error(f"❌ Failed to create UPID setup action: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error creating UPID setup action: {e}")
            return False
    
    async def trigger_workflow(self, workflow_name: str, inputs: Dict[str, Any] = None) -> bool:
        """Trigger a GitHub Actions workflow"""
        try:
            url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}/actions/workflows/{workflow_name}/dispatches"
            
            payload = {
                "ref": "main",
                "inputs": inputs or {}
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 204:
                    logger.info(f"✅ Triggered workflow: {workflow_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to trigger workflow {workflow_name}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error triggering workflow {workflow_name}: {e}")
            return False
    
    async def get_workflow_runs(self, workflow_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow runs"""
        try:
            url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}/actions/workflows/{workflow_name}/runs"
            
            params = {"per_page": limit}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("workflow_runs", [])
                else:
                    logger.error(f"❌ Failed to get workflow runs: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error getting workflow runs: {e}")
            return []
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Process GitHub webhook event"""
        try:
            event_type = webhook_data.get("action")
            repository = webhook_data.get("repository", {})
            
            logger.info(f"📨 Processing GitHub webhook: {event_type}")
            
            if event_type == "opened" and "pull_request" in webhook_data:
                # Handle pull request opened
                await self._handle_pull_request_opened(webhook_data)
            elif event_type == "synchronize" and "pull_request" in webhook_data:
                # Handle pull request updated
                await self._handle_pull_request_updated(webhook_data)
            elif event_type == "push":
                # Handle push event
                await self._handle_push_event(webhook_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            return False
    
    async def _handle_pull_request_opened(self, webhook_data: Dict[str, Any]):
        """Handle pull request opened event"""
        pr_data = webhook_data["pull_request"]
        
        # Check if PR affects Kubernetes manifests
        changed_files = await self._get_pr_changed_files(pr_data["number"])
        k8s_files = [f for f in changed_files if any(path in f for path in ["k8s/", "helm/", "manifests/"])]
        
        if k8s_files:
            # Trigger deployment validation
            await self.trigger_workflow("upid-deployment-validation.yml", {
                "pr_number": str(pr_data["number"]),
                "branch": pr_data["head"]["ref"]
            })
    
    async def _handle_pull_request_updated(self, webhook_data: Dict[str, Any]):
        """Handle pull request updated event"""
        # Similar to opened, but might have different logic
        await self._handle_pull_request_opened(webhook_data)
    
    async def _handle_push_event(self, webhook_data: Dict[str, Any]):
        """Handle push event"""
        ref = webhook_data.get("ref", "")
        
        if ref == "refs/heads/main":
            # Trigger monitoring workflows on main branch
            await self.trigger_workflow("upid-performance-monitoring.yml")
    
    async def _get_pr_changed_files(self, pr_number: int) -> List[str]:
        """Get list of files changed in PR"""
        try:
            url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}/pulls/{pr_number}/files"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    files_data = await response.json()
                    return [f["filename"] for f in files_data]
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error getting PR files: {e}")
            return []
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get GitHub Actions integration status"""
        workflows_info = []
        
        if self.session and self.config.github_token:
            try:
                url = f"https://api.github.com/repos/{self.config.repository_owner}/{self.config.repository_name}/actions/workflows"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        workflows_info = data.get("workflows", [])
            except Exception as e:
                logger.warning(f"Failed to get workflows info: {e}")
        
        return {
            "config": asdict(self.config),
            "github_api_connected": bool(self.session and self.config.github_token),
            "repository_configured": bool(self.config.repository_owner and self.config.repository_name),
            "workflows_count": len(workflows_info),
            "workflows": [
                {
                    "name": w.get("name"),
                    "state": w.get("state"),
                    "created_at": w.get("created_at")
                }
                for w in workflows_info[:10]  # Limit to first 10
            ]
        }
    
    async def shutdown(self):
        """Shutdown GitHub Actions integration"""
        logger.info("🛑 Shutting down GitHub Actions integration...")
        
        if self.session:
            await self.session.close()
        
        logger.info("✅ GitHub Actions integration shutdown complete")


# Export main classes
__all__ = [
    'GitHubActionsIntegration',
    'GitHubActionsConfig',
    'GitHubWorkflow',
    'GitHubActionsTemplateGenerator'
]