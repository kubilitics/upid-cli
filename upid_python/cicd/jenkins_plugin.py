#!/usr/bin/env python3
"""
UPID CLI - Jenkins Integration
Phase 6: Platform Integration - Task 6.1
Enterprise-grade Jenkins integration for automated UPID workflows
"""

import logging
import asyncio
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import base64
import urllib.parse

from .pipeline_manager import PipelineManager, PipelineConfig, TriggerType, PipelineType

logger = logging.getLogger(__name__)


@dataclass
class JenkinsConfig:
    """Jenkins integration configuration"""
    jenkins_url: str = ""
    username: Optional[str] = None
    api_token: Optional[str] = None
    crumb_issuer: bool = True
    job_templates_dir: str = "jenkins/jobs"
    upid_agent_label: str = "upid-capable"
    enable_blue_ocean: bool = True
    pipeline_library: str = "upid-pipeline-library"


@dataclass
class JenkinsJob:
    """Jenkins job definition"""
    name: str
    description: str
    job_type: str  # "pipeline", "freestyle", "multibranch"
    script: Optional[str] = None
    scm_config: Optional[Dict[str, Any]] = None
    triggers: List[Dict[str, Any]] = None
    parameters: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []
        if self.parameters is None:
            self.parameters = []


class JenkinsJobTemplateGenerator:
    """Generates Jenkins job templates"""
    
    def __init__(self, config: JenkinsConfig):
        self.config = config
    
    def generate_cost_optimization_job(self, cluster_config: Dict[str, Any]) -> JenkinsJob:
        """Generate cost optimization Jenkins job"""
        
        cluster_id = cluster_config.get("cluster_id", "default")
        pipeline_script = f"""
@Library('{self.config.pipeline_library}') _

pipeline {{
    agent {{
        label '{self.config.upid_agent_label}'
    }}
    
    parameters {{
        string(name: 'CLUSTER_ID', defaultValue: '{cluster_id}', description: 'Target cluster ID')
        choice(name: 'OPTIMIZATION_TYPE', choices: ['zero-pod', 'rightsizing', 'all'], description: 'Optimization strategy')
        booleanParam(name: 'DRY_RUN', defaultValue: true, description: 'Run in dry-run mode')
        booleanParam(name: 'REQUIRE_APPROVAL', defaultValue: true, description: 'Require manual approval')
    }}
    
    environment {{
        UPID_LOG_LEVEL = 'INFO'
        UPID_SAFETY_MODE = 'true'
        KUBECONFIG = credentials('kubeconfig-${{params.CLUSTER_ID}}')
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                script {{
                    echo "Starting UPID cost optimization for cluster: ${{params.CLUSTER_ID}}"
                    sh 'upid --version'
                    sh 'upid auth validate'
                }}
            }}
        }}
        
        stage('Cost Analysis') {{
            steps {{
                script {{
                    sh '''
                        upid analyze cost --cluster-id ${{params.CLUSTER_ID}} --output json > cost-analysis.json
                        upid analyze idle --cluster-id ${{params.CLUSTER_ID}}
                    '''
                    
                    def costData = readJSON file: 'cost-analysis.json'
                    def monthlyCost = costData.monthly_cost ?: 0
                    def potentialSavings = costData.potential_savings ?: 0
                    
                    echo "Monthly Cost: $${{monthlyCost}}"
                    echo "Potential Savings: $${{potentialSavings}}"
                }}
            }}
        }}
        
        stage('Optimization Planning') {{
            steps {{
                script {{
                    sh '''
                        upid optimize plan --cluster-id ${{params.CLUSTER_ID}} --type ${{params.OPTIMIZATION_TYPE}} --output json > optimization-results.json
                    '''
                    
                    def optimizationData = readJSON file: 'optimization-results.json'
                    def estimatedSavings = optimizationData.estimated_savings ?: 0
                    
                    timeout(time: 60, unit: 'MINUTES') {{
                        input message: "UPID Cost Optimization Approval Required - Cluster: ${{params.CLUSTER_ID}} - Estimated Savings: $${{estimatedSavings}}", 
                        ok: 'Approve Optimization',
                        submitterParameter: 'APPROVER'
                    }}
                    
                    echo "Optimization approved by: ${{env.APPROVER}}"
                }}
            }}
        }}
        
        stage('Apply Optimizations') {{
            when {{
                expression {{ params.DRY_RUN == false }}
            }}
            steps {{
                script {{
                    sh 'upid backup create --cluster-id ${{params.CLUSTER_ID}} --name "pre-optimization-${{BUILD_NUMBER}}"'
                    echo "Applying optimizations..."
                    sh 'upid optimize apply --cluster-id ${{params.CLUSTER_ID}} --strategies optimization-results.json --confirm'
                    sh 'upid monitor start --cluster-id ${{params.CLUSTER_ID}} --duration 300'
                }}
            }}
        }}
        
        stage('Post-Optimization Validation') {{
            when {{
                expression {{ params.DRY_RUN == false }}
            }}
            steps {{
                script {{
                    sleep 60
                    sh '''
                        upid analyze cost --cluster-id ${{params.CLUSTER_ID}} --output json > post-optimization-cost.json
                        upid report optimization --before cost-analysis.json --after post-optimization-cost.json --output markdown > optimization-report.md
                    '''
                    
                    archiveArtifacts artifacts: 'post-optimization-cost.json, optimization-report.md', fingerprint: true
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'optimization-report.md',
                        reportName: 'UPID Optimization Report'
                    ])
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            script {{
                def optimizationData = readJSON file: 'optimization-results.json'
                def savings = optimizationData.estimated_savings ?: 0
                
                slackSend(
                    channel: '#devops',
                    color: 'good',
                    message: "UPID Cost Optimization Completed Successfully - Cluster: ${{params.CLUSTER_ID}} - Estimated Savings: $${{savings}} - Build: ${{env.BUILD_URL}}"
                )
            }}
        }}
        failure {{
            slackSend(
                channel: '#devops',
                color: 'danger',
                message: "UPID Cost Optimization Failed - Cluster: ${{params.CLUSTER_ID}} - Build: ${{env.BUILD_URL}}"
            )
        }}
    }}
}}
        """
        
        scm_config = {
            "git": {
                "url": cluster_config.get("git_url", ""),
                "branches": ["*/main", "*/develop"],
                "credentials": "git-credentials"
            }
        }
        
        triggers = [
            {
                "scm": "H/15 * * * *"  # Poll SCM every 15 minutes
            },
            {
                "webhook": True
            }
        ]
        
        return JenkinsJob(
            name=f"upid-cost-optimization-{cluster_config.get('cluster_id', 'default')}",
            description=f"UPID cost optimization for {cluster_config.get('cluster_id', 'default')}",
            job_type="pipeline",
            script=pipeline_script,
            scm_config=scm_config,
            triggers=triggers
        )
    
    def generate_deployment_validation_job(self, deployment_config: Dict[str, Any]) -> JenkinsJob:
        """Generate deployment validation Jenkins job"""
        
        pipeline_script = f"""
@Library('{self.config.pipeline_library}') _

pipeline {{
    agent {{
        label '{self.config.upid_agent_label}'
    }}
    
    parameters {{
        string(name: 'CLUSTER_ID', defaultValue: '{deployment_config.get("cluster_id", "default")}', description: 'Target cluster ID')
        string(name: 'NAMESPACE', defaultValue: '{deployment_config.get("namespace", "default")}', description: 'Kubernetes namespace')
        string(name: 'DEPLOYMENT_NAME', defaultValue: '{deployment_config.get("deployment_name", "app")}', description: 'Deployment name')
        string(name: 'MANIFEST_PATH', defaultValue: 'k8s/', description: 'Path to Kubernetes manifests')
    }}
    
    environment {{
        KUBECONFIG = credentials('kubeconfig-${{params.CLUSTER_ID}}')
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Pre-Deployment Analysis') {{
            parallel {{
                stage('Manifest Validation') {{
                    steps {{
                        script {{
                            sh '''
                                upid validate manifests --path ${{params.MANIFEST_PATH}} --output json > validation-results.json
                                upid estimate cost --manifests ${{params.MANIFEST_PATH}} --cluster-id ${{params.CLUSTER_ID}} --output json > cost-estimate.json
                            '''
                            
                            def validationResults = readJSON file: 'validation-results.json'
                            if (validationResults.errors?.size() > 0) {{
                                error("Manifest validation failed: ${{validationResults.errors}}")
                            }}
                        }}
                    }}
                }}
                
                stage('Cost Impact Assessment') {{
                    steps {{
                        script {{
                            sh '''
                                upid analyze cost --cluster-id ${{params.CLUSTER_ID}} --namespace ${{params.NAMESPACE}} --output json > pre-deployment-cost.json
                            '''
                            
                            def costData = readJSON file: 'pre-deployment-cost.json'
                            echo "Pre-deployment monthly cost: $${{costData.monthly_cost}}"
                        }}
                    }}
                }}
                
                stage('Security Scan') {{
                    steps {{
                        script {{
                            sh '''
                                upid analyze security --cluster-id ${{params.CLUSTER_ID}} --manifests ${{params.MANIFEST_PATH}} --output json > security-scan.json
                            '''
                            
                            def securityData = readJSON file: 'security-scan.json'
                            echo "Security vulnerabilities found: ${{securityData.vulnerabilities_count}}"
                        }}
                    }}
                }}
            }}
        }}
        
        stage('Deploy to Staging') {{
            steps {{
                script {{
                    sh '''
                        kubectl apply -f ${{params.MANIFEST_PATH}} --namespace ${{params.NAMESPACE}} --dry-run=server
                        kubectl apply -f ${{params.MANIFEST_PATH}} --namespace ${{params.NAMESPACE}}
                        kubectl rollout status deployment/${{params.DEPLOYMENT_NAME}} --namespace ${{params.NAMESPACE}} --timeout=300s
                    '''
                }}
            }}
        }}
        
        stage('Deploy to Production') {{
            when {{
                expression {{ params.REQUIRE_APPROVAL == true }}
            }}
            steps {{
                script {{
                    timeout(time: 30, unit: 'MINUTES') {{
                        input message: "Deploy to Production? - Cluster: ${{params.CLUSTER_ID}} - Namespace: ${{params.NAMESPACE}} - Deployment: ${{params.DEPLOYMENT_NAME}}",
                        ok: 'Deploy to Production'
                    }}
                    
                    sh '''
                        kubectl apply -f ${{params.MANIFEST_PATH}} --namespace ${{params.NAMESPACE}}
                        kubectl rollout status deployment/${{params.DEPLOYMENT_NAME}} --namespace ${{params.NAMESPACE}} --timeout=600s
                    '''
                }}
            }}
        }}
        
        stage('Post-Deployment Validation') {{
            steps {{
                script {{
                    sleep 120
                    
                    sh '''
                        upid analyze cost --cluster-id ${{params.CLUSTER_ID}} --output json > post-deployment-cost.json
                        upid report deployment --before pre-deployment-cost.json --after post-deployment-cost.json --output markdown > deployment-impact-report.md
                    '''
                    
                    archiveArtifacts artifacts: 'post-deployment-cost.json, deployment-impact-report.md', fingerprint: true
                    
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'deployment-impact-report.md',
                        reportName: 'UPID Deployment Impact Report'
                    ])
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "Deployment Validation Completed - Cluster: ${{params.CLUSTER_ID}} - Deployment: ${{params.DEPLOYMENT_NAME}} - Build: ${{env.BUILD_URL}}"
            )
        }}
        failure {{
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "Deployment Validation Failed - Cluster: ${{params.CLUSTER_ID}} - Deployment: ${{params.DEPLOYMENT_NAME}} - Build: ${{env.BUILD_URL}}"
            )
        }}
    }}
}}
        """
        
        scm_config = {
            "git": {
                "url": deployment_config.get("git_url", ""),
                "branches": ["*/main", "*/develop"],
                "credentials": "git-credentials"
            }
        }
        
        triggers = [
            {
                "scm": "H/5 * * * *"  # Poll SCM every 5 minutes
            },
            {
                "webhook": True
            }
        ]
        
        return JenkinsJob(
            name=f"upid-deployment-validation-{deployment_config.get('deployment_name', 'app')}",
            description=f"UPID deployment validation for {deployment_config.get('deployment_name', 'app')}",
            job_type="pipeline",
            script=pipeline_script,
            scm_config=scm_config,
            triggers=triggers
        )
    
    def generate_monitoring_job(self, monitoring_config: Dict[str, Any]) -> JenkinsJob:
        """Generate monitoring Jenkins job"""
        
        pipeline_script = f"""
@Library('{self.config.pipeline_library}') _

pipeline {{
    agent {{
        label '{self.config.upid_agent_label}'
    }}
    
    parameters {{
        string(name: 'CLUSTER_ID', defaultValue: '{monitoring_config.get("cluster_id", "default")}', description: 'Target cluster ID')
        string(name: 'MONITORING_DURATION', defaultValue: '3600', description: 'Monitoring duration in seconds')
        booleanParam(name: 'ENABLE_ALERTS', defaultValue: true, description: 'Enable alerting')
    }}
    
    environment {{
        KUBECONFIG = credentials('kubeconfig-${{params.CLUSTER_ID}}')
    }}
    
    stages {{
        stage('Setup Monitoring') {{
            steps {{
                script {{
                    echo "Starting UPID monitoring for cluster: ${{params.CLUSTER_ID}}"
                    sh 'upid --version'
                }}
            }}
        }}
        
        stage('Start Monitoring') {{
            steps {{
                script {{
                    sh '''
                        upid monitor start --cluster-id ${{params.CLUSTER_ID}} --duration ${{params.MONITORING_DURATION}} --output json > monitoring-results.json
                    '''
                    
                    def monitoringData = readJSON file: 'monitoring-results.json'
                    echo "Monitoring started for ${{params.MONITORING_DURATION}} seconds"
                }}
            }}
        }}
        
        stage('Analyze Results') {{
            steps {{
                script {{
                    sh '''
                        upid analyze performance --cluster-id ${{params.CLUSTER_ID}} --output json > performance-analysis.json
                        upid analyze anomalies --cluster-id ${{params.CLUSTER_ID}} --output json > anomaly-analysis.json
                    '''
                    
                    def performanceData = readJSON file: 'performance-analysis.json'
                    def anomalyData = readJSON file: 'anomaly-analysis.json'
                    
                    echo "Performance score: ${{performanceData.performance_score}}%"
                    echo "Anomalies detected: ${{anomalyData.anomalies_count}}"
                }}
            }}
        }}
        
        stage('Generate Report') {{
            steps {{
                script {{
                    sh '''
                        upid report monitoring --cluster-id ${{params.CLUSTER_ID}} --output markdown > monitoring-report.md
                    '''
                    
                    archiveArtifacts artifacts: 'monitoring-results.json, performance-analysis.json, anomaly-analysis.json, monitoring-report.md', fingerprint: true
                    
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'monitoring-report.md',
                        reportName: 'UPID Monitoring Report'
                    ])
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            slackSend(
                channel: '#monitoring',
                color: 'good',
                message: "Monitoring Completed - Cluster: ${{params.CLUSTER_ID}} - Duration: ${{params.MONITORING_DURATION}} seconds - Build: ${{env.BUILD_URL}}"
            )
        }}
        failure {{
            slackSend(
                channel: '#monitoring',
                color: 'danger',
                message: "Monitoring Failed - Cluster: ${{params.CLUSTER_ID}} - Build: ${{env.BUILD_URL}}"
            )
        }}
    }}
}}
        """
        
        scm_config = {
            "git": {
                "url": monitoring_config.get("git_url", ""),
                "branches": ["*/main"],
                "credentials": "git-credentials"
            }
        }
        
        triggers = [
            {
                "cron": "0 */6 * * *"  # Every 6 hours
            }
        ]
        
        return JenkinsJob(
            name=f"upid-monitoring-{monitoring_config.get('cluster_id', 'default')}",
            description=f"UPID monitoring for {monitoring_config.get('cluster_id', 'default')}",
            job_type="pipeline",
            script=pipeline_script,
            scm_config=scm_config,
            triggers=triggers
        )


class JenkinsIntegration:
    """
    Jenkins integration for UPID CLI
    
    Features:
    - Automated job generation
    - Pipeline-as-code support
    - Cost optimization workflows
    - Deployment validation pipelines
    - Performance monitoring automation
    - Blue Ocean integration
    - Plugin ecosystem support
    """
    
    def __init__(self, pipeline_manager: PipelineManager, config: JenkinsConfig):
        self.pipeline_manager = pipeline_manager
        self.config = config
        self.template_generator = JenkinsJobTemplateGenerator(config)
        
        # Jenkins API session
        self.session: Optional[aiohttp.ClientSession] = None
        self.crumb: Optional[str] = None
        
        logger.info("Initializing Jenkins integration")
    
    async def initialize(self) -> bool:
        """Initialize Jenkins integration"""
        try:
            logger.info("Initializing Jenkins integration...")
            
            # Initialize HTTP session
            auth = None
            if self.config.username and self.config.api_token:
                auth = aiohttp.BasicAuth(self.config.username, self.config.api_token)
            
            self.session = aiohttp.ClientSession(auth=auth)
            
            # Get CSRF crumb if enabled
            if self.config.crumb_issuer:
                await self._get_crumb()
            
            # Validate Jenkins connection
            await self._validate_jenkins_connection()
            
            logger.info("Jenkins integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Jenkins integration: {e}")
            return False
    
    async def _get_crumb(self) -> bool:
        """Get CSRF crumb from Jenkins"""
        try:
            if not self.session:
                return False
            
            url = f"{self.config.jenkins_url}/crumbIssuer/api/json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.crumb = data.get("crumb")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to get Jenkins crumb: {e}")
            return False
    
    async def _validate_jenkins_connection(self) -> bool:
        """Validate Jenkins connection"""
        try:
            if not self.session:
                return False
            
            url = f"{self.config.jenkins_url}/api/json"
            async with self.session.get(url) as response:
                return response.status == 200
            
        except Exception as e:
            logger.error(f"Failed to validate Jenkins connection: {e}")
            return False
    
    async def setup_jenkins_jobs(self, cluster_configs: List[Dict[str, Any]]) -> bool:
        """Setup UPID jobs in Jenkins"""
        try:
            logger.info("Setting up UPID jobs in Jenkins...")
            
            jobs = []
            
            for cluster_config in cluster_configs:
                # Generate jobs for each cluster
                cost_job = self.template_generator.generate_cost_optimization_job(cluster_config)
                deployment_job = self.template_generator.generate_deployment_validation_job(cluster_config)
                monitoring_job = self.template_generator.generate_monitoring_job(cluster_config)
                
                jobs.extend([cost_job, deployment_job, monitoring_job])
            
            # Create jobs in Jenkins
            for job in jobs:
                await self._create_jenkins_job(job)
            
            logger.info(f"Successfully created {len(jobs)} jobs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Jenkins jobs: {e}")
            return False
    
    async def _create_jenkins_job(self, job: JenkinsJob) -> bool:
        """Create a Jenkins job"""
        try:
            if not self.session:
                return False
            
            # Check if job already exists
            if await self._job_exists(job.name):
                logger.info(f"Job {job.name} already exists, skipping")
                return True
            
            # Generate job XML
            job_xml = self._generate_job_xml(job)
            
            # Create job
            url = f"{self.config.jenkins_url}/createItem"
            headers = {"Content-Type": "application/xml"}
            
            if self.crumb:
                headers["Jenkins-Crumb"] = self.crumb
            
            async with self.session.post(url, data=job_xml, headers=headers) as response:
                if response.status in [200, 201]:
                    logger.info(f"Created Jenkins job: {job.name}")
                    return True
                else:
                    logger.error(f"Failed to create job {job.name}: {response.status}")
                    return False
            
        except Exception as e:
            logger.error(f"Failed to create Jenkins job: {e}")
            return False
    
    async def _job_exists(self, job_name: str) -> bool:
        """Check if a Jenkins job exists"""
        try:
            if not self.session:
                return False
            
            url = f"{self.config.jenkins_url}/job/{job_name}/api/json"
            async with self.session.get(url) as response:
                return response.status == 200
            
        except Exception:
            return False
    
    def _generate_job_xml(self, job: JenkinsJob) -> str:
        """Generate Jenkins job XML"""
        if job.job_type == "pipeline":
            return self._generate_pipeline_job_xml(job)
        else:
            return self._generate_freestyle_job_xml(job)
    
    def _generate_pipeline_job_xml(self, job: JenkinsJob) -> str:
        """Generate pipeline job XML"""
        xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1.0">
    <description>{self._escape_xml(job.description)}</description>
    <keepDependencies>false</keepDependencies>
    <properties>
        <hudson.plugins.disk__usage.DiskUsageProperty/>
    </properties>
    <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@1.0">
        <script>{self._escape_xml(job.script)}</script>
        <sandbox>true</sandbox>
    </definition>
    <triggers>
        {self._generate_triggers_xml(job.triggers)}
    </triggers>
    <disabled>false</disabled>
</flow-definition>"""
        return xml
    
    def _generate_freestyle_job_xml(self, job: JenkinsJob) -> str:
        """Generate freestyle job XML"""
        xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<project>
    <description>{self._escape_xml(job.description)}</description>
    <keepDependencies>false</keepDependencies>
    <properties>
        <hudson.plugins.disk__usage.DiskUsageProperty/>
    </properties>
    <scm class="hudson.plugins.git.GitSCM" plugin="git@1.0">
        <configVersion>2</configVersion>
        <userRemoteConfigs>
            <hudson.plugins.git.UserRemoteConfig>
                <url>{job.scm_config.get('git', {}).get('url', '')}</url>
                <credentialsId>{job.scm_config.get('git', {}).get('credentials', '')}</credentialsId>
            </hudson.plugins.git.UserRemoteConfig>
        </userRemoteConfigs>
        <branches>
            <hudson.plugins.git.BranchSpec>
                <name>*/main</name>
            </hudson.plugins.git.BranchSpec>
        </branches>
    </scm>
    <canRoam>true</canRoam>
    <disabled>false</disabled>
    <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
    <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
    <triggers>
        {self._generate_triggers_xml(job.triggers)}
    </triggers>
    <concurrentBuild>false</concurrentBuild>
    <builders>
        <hudson.tasks.Shell>
            <command>{self._escape_xml(job.script or 'echo "No script provided"')}</command>
        </hudson.tasks.Shell>
    </builders>
    <publishers/>
    <buildWrappers/>
</project>"""
        return xml
    
    def _generate_triggers_xml(self, triggers: List[Dict[str, Any]]) -> str:
        """Generate triggers XML"""
        xml_parts = []
        
        for trigger in triggers:
            if "scm" in trigger:
                xml_parts.append("""
        <hudson.triggers.SCMTrigger>
            <spec>H/15 * * * *</spec>
        </hudson.triggers.SCMTrigger>""")
            elif "cron" in trigger:
                xml_parts.append(f"""
        <hudson.triggers.TimerTrigger>
            <spec>{trigger['cron']}</spec>
        </hudson.triggers.TimerTrigger>""")
            elif "webhook" in trigger:
                xml_parts.append("""
        <com.cloudbees.jenkins.GitHubPushTrigger plugin="github@1.0">
            <spec></spec>
        </com.cloudbees.jenkins.GitHubPushTrigger>""")
        
        return "".join(xml_parts)
    
    def _generate_parameters_xml(self, parameters: List[Dict[str, Any]]) -> str:
        """Generate parameters XML"""
        if not parameters:
            return ""
        
        xml_parts = ['<parameterDefinitions>']
        
        for param in parameters:
            param_type = param.get('type', 'string')
            name = param.get('name', '')
            description = param.get('description', '')
            default_value = param.get('default_value', '')
            
            if param_type == 'string':
                xml_parts.append(f"""
            <hudson.model.StringParameterDefinition>
                <name>{self._escape_xml(name)}</name>
                <description>{self._escape_xml(description)}</description>
                <defaultValue>{self._escape_xml(default_value)}</defaultValue>
            </hudson.model.StringParameterDefinition>""")
            elif param_type == 'boolean':
                xml_parts.append(f"""
            <hudson.model.BooleanParameterDefinition>
                <name>{self._escape_xml(name)}</name>
                <description>{self._escape_xml(description)}</description>
                <defaultValue>{str(default_value).lower()}</defaultValue>
            </hudson.model.BooleanParameterDefinition>""")
            elif param_type == 'choice':
                choices = param.get('choices', [])
                choices_xml = "".join([f'<string>{choice}</string>' for choice in choices])
                xml_parts.append(f"""
            <hudson.model.ChoiceParameterDefinition>
                <name>{self._escape_xml(name)}</name>
                <description>{self._escape_xml(description)}</description>
                <choices>
                    {choices_xml}
                </choices>
            </hudson.model.ChoiceParameterDefinition>""")
        
        xml_parts.append('</parameterDefinitions>')
        return "".join(xml_parts)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ""
        
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&apos;"))
    
    async def trigger_job(self, job_name: str, parameters: Dict[str, Any] = None) -> bool:
        """Trigger a Jenkins job"""
        try:
            if not self.session:
                return False
            
            # Build job URL
            url = f"{self.config.jenkins_url}/job/{job_name}/buildWithParameters"
            
            # Add parameters
            if parameters:
                param_data = urllib.parse.urlencode(parameters)
                url = f"{url}?{param_data}"
            
            headers = {}
            if self.crumb:
                headers["Jenkins-Crumb"] = self.crumb
            
            async with self.session.post(url, headers=headers) as response:
                if response.status in [200, 201]:
                    logger.info(f"Triggered Jenkins job: {job_name}")
                    return True
                else:
                    logger.error(f"Failed to trigger job {job_name}: {response.status}")
                    return False
            
        except Exception as e:
            logger.error(f"Failed to trigger Jenkins job: {e}")
            return False
    
    async def get_job_status(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get Jenkins job status"""
        try:
            if not self.session:
                return None
            
            url = f"{self.config.jenkins_url}/job/{job_name}/lastBuild/api/json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": job_name,
                        "status": data.get("result"),
                        "building": data.get("building", False),
                        "timestamp": data.get("timestamp"),
                        "duration": data.get("duration"),
                        "url": data.get("url")
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get Jenkins integration status"""
        jobs_info = []
        
        if self.session:
            try:
                url = f"{self.config.jenkins_url}/api/json"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        jobs = data.get("jobs", [])
                        jobs_info = [
                            {
                                "name": job.get("name"),
                                "url": job.get("url"),
                                "color": job.get("color")
                            }
                            for job in jobs[:10]  # Limit to first 10
                        ]
            except Exception as e:
                logger.warning(f"Failed to get jobs info: {e}")
        
        return {
            "config": asdict(self.config),
            "jenkins_connected": bool(self.session),
            "jobs_count": len(jobs_info),
            "recent_jobs": jobs_info
        }
    
    async def shutdown(self):
        """Shutdown Jenkins integration"""
        logger.info("Shutting down Jenkins integration...")
        
        if self.session:
            await self.session.close()
        
        logger.info("Jenkins integration shutdown complete")


# Export main classes
__all__ = [
    'JenkinsIntegration',
    'JenkinsConfig',
    'JenkinsJob',
    'JenkinsJobTemplateGenerator'
]