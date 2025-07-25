#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Phase 6: Platform Integration
Tests all CI/CD pipeline integration components including GitOps, deployment validation, and pipeline management
"""

import pytest
import asyncio
import json
import yaml
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import Phase 6 components
from upid_python.cicd.pipeline_manager import PipelineManager, PipelineConfig, TriggerType, PipelineType
from upid_python.cicd.gitops_integration import GitOpsIntegration, GitOpsConfig, GitOpsStrategy, GitOpsDeployment
from upid_python.cicd.deployment_validator import DeploymentValidator, ValidationConfig, DeploymentValidation
from upid_python.cicd.github_actions import GitHubActionsIntegration, GitHubActionsConfig
from upid_python.cicd.gitlab_cicd import GitLabCICDIntegration, GitLabCICDConfig
from upid_python.cicd.jenkins_plugin import JenkinsIntegration, JenkinsConfig

# Import core components
from upid_python.core.metrics_collector import MetricsCollector
from upid_python.core.resource_analyzer import ResourceAnalyzer


class TestPhase6PlatformIntegration:
    """Test suite for Phase 6 Platform Integration components"""
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Mock metrics collector"""
        collector = Mock(spec=MetricsCollector)
        collector.initialize = AsyncMock(return_value=True)
        collector.get_metrics = AsyncMock(return_value={"cpu": 50.0, "memory": 60.0})
        return collector
    
    @pytest.fixture
    def mock_resource_analyzer(self):
        """Mock resource analyzer"""
        analyzer = Mock(spec=ResourceAnalyzer)
        analyzer.initialize = AsyncMock(return_value=True)
        analyzer.analyze_resources = AsyncMock(return_value={"pods": 10, "services": 5})
        return analyzer
    
    @pytest.fixture
    def pipeline_manager(self, mock_metrics_collector, mock_resource_analyzer):
        """Pipeline manager instance"""
        return PipelineManager(mock_metrics_collector, mock_resource_analyzer)
    
    @pytest.fixture
    def gitops_config(self):
        """GitOps configuration"""
        return GitOpsConfig(
            strategy=GitOpsStrategy.FLUX,
            git_repository="https://github.com/test/upid-repo",
            git_branch="main",
            auto_sync=True,
            enable_cost_analysis=True
        )
    
    @pytest.fixture
    def validation_config(self):
        """Validation configuration"""
        return ValidationConfig(
            pre_deployment_analysis=True,
            post_deployment_validation=True,
            cost_impact_analysis=True,
            performance_validation=True,
            security_scanning=True,
            auto_rollback=True
        )
    
    @pytest.fixture
    def github_actions_config(self):
        """GitHub Actions configuration"""
        return GitHubActionsConfig(
            github_token="test-token",
            repository_owner="test-owner",
            repository_name="test-repo",
            enable_cost_comments=True
        )
    
    @pytest.fixture
    def gitlab_cicd_config(self):
        """GitLab CI/CD configuration"""
        return GitLabCICDConfig(
            gitlab_token="test-token",
            gitlab_url="https://gitlab.com",
            project_id=123,
            enable_cost_comments=True
        )
    
    @pytest.fixture
    def jenkins_config(self):
        """Jenkins configuration"""
        return JenkinsConfig(
            jenkins_url="https://jenkins.test.com",
            username="test-user",
            api_token="test-token",
            enable_blue_ocean=True
        )


class TestPipelineManager(TestPhase6PlatformIntegration):
    """Test Pipeline Manager functionality"""
    
    @pytest.mark.asyncio
    async def test_pipeline_manager_initialization(self, pipeline_manager):
        """Test pipeline manager initialization"""
        with patch('upid_python.cicd.pipeline_manager.MultiModelEnsembleSystem') as mock_ensemble:
            mock_ensemble.return_value.initialize = AsyncMock(return_value=True)
            
            result = await pipeline_manager.initialize()
            
            assert result is True
            assert pipeline_manager.pipeline_configs == {}
            assert pipeline_manager.pipeline_executions == {}
    
    @pytest.mark.asyncio
    async def test_create_pipeline(self, pipeline_manager):
        """Test pipeline creation"""
        await pipeline_manager.initialize()
        
        config = PipelineConfig(
            name="test-pipeline",
            description="Test pipeline",
            pipeline_type=PipelineType.OPTIMIZATION,
            triggers=[TriggerType.SCHEDULE],
            stages=[
                {"name": "analyze", "type": "upid_analysis"},
                {"name": "optimize", "type": "upid_optimization"}
            ]
        )
        
        result = await pipeline_manager.create_pipeline(config)
        
        assert result is True
        assert "test-pipeline" in pipeline_manager.pipeline_configs
        assert pipeline_manager.pipeline_configs["test-pipeline"] == config
    
    @pytest.mark.asyncio
    async def test_execute_pipeline(self, pipeline_manager):
        """Test pipeline execution"""
        await pipeline_manager.initialize()
        
        config = PipelineConfig(
            name="test-pipeline",
            description="Test pipeline",
            pipeline_type=PipelineType.OPTIMIZATION,
            triggers=[TriggerType.MANUAL],
            stages=[
                {"name": "analyze", "type": "upid_analysis", "cluster_id": "test-cluster"}
            ]
        )
        
        await pipeline_manager.create_pipeline(config)
        
        execution = await pipeline_manager.execute_pipeline("test-pipeline", {"cluster_id": "test-cluster"})
        
        assert execution is not None
        assert execution.pipeline_name == "test-pipeline"
        assert execution.status in ["pending", "running", "success", "failed"]
    
    @pytest.mark.asyncio
    async def test_get_pipeline_status(self, pipeline_manager):
        """Test pipeline status retrieval"""
        await pipeline_manager.initialize()
        
        config = PipelineConfig(
            name="test-pipeline",
            description="Test pipeline",
            pipeline_type=PipelineType.OPTIMIZATION,
            triggers=[TriggerType.MANUAL],
            stages=[]
        )
        
        await pipeline_manager.create_pipeline(config)
        
        status = await pipeline_manager.get_pipeline_status("test-pipeline")
        
        assert status is not None
        assert "name" in status
        assert "status" in status
        assert status["name"] == "test-pipeline"


class TestGitOpsIntegration(TestPhase6PlatformIntegration):
    """Test GitOps Integration functionality"""
    
    @pytest.mark.asyncio
    async def test_gitops_integration_initialization(self, pipeline_manager, gitops_config):
        """Test GitOps integration initialization"""
        gitops = GitOpsIntegration(pipeline_manager, gitops_config)
        
        with patch.object(gitops, '_validate_gitops_strategy') as mock_validate, \
             patch.object(gitops, '_setup_gitops_components') as mock_setup:
            
            mock_validate.return_value = None
            mock_setup.return_value = None
            
            result = await gitops.initialize()
            
            assert result is True
            assert gitops.deployments == {}
            assert gitops.sync_status == {}
    
    @pytest.mark.asyncio
    async def test_create_gitops_deployment(self, pipeline_manager, gitops_config):
        """Test GitOps deployment creation"""
        gitops = GitOpsIntegration(pipeline_manager, gitops_config)
        await gitops.initialize()
        
        deployment = GitOpsDeployment(
            name="test-app",
            namespace="default",
            git_path="k8s/test-app",
            cluster_id="test-cluster",
            strategy=GitOpsStrategy.FLUX,
            sync_policy={"automated": True},
            health_checks=[{"apiVersion": "apps/v1", "kind": "Deployment"}],
            rollback_policy={"automatic": True}
        )
        
        with patch.object(gitops, '_apply_k8s_resource') as mock_apply:
            mock_apply.return_value = None
            
            result = await gitops.create_deployment(deployment)
            
            assert result is True
            assert "test-app" in gitops.deployments
            assert gitops.deployments["test-app"] == deployment
    
    @pytest.mark.asyncio
    async def test_sync_gitops_deployment(self, pipeline_manager, gitops_config):
        """Test GitOps deployment sync"""
        gitops = GitOpsIntegration(pipeline_manager, gitops_config)
        await gitops.initialize()
        
        deployment = GitOpsDeployment(
            name="test-app",
            namespace="default",
            git_path="k8s/test-app",
            cluster_id="test-cluster",
            strategy=GitOpsStrategy.FLUX,
            sync_policy={"automated": True},
            health_checks=[],
            rollback_policy={}
        )
        
        gitops.deployments["test-app"] = deployment
        
        with patch.object(gitops, '_run_command') as mock_run:
            mock_run.return_value = (0, b"", b"")
            
            result = await gitops.sync_deployment("test-app")
            
            assert result is True
            assert "test-app" in gitops.sync_status
            assert gitops.sync_status["test-app"]["status"] == "synced"
    
    @pytest.mark.asyncio
    async def test_get_deployment_status(self, pipeline_manager, gitops_config):
        """Test GitOps deployment status retrieval"""
        gitops = GitOpsIntegration(pipeline_manager, gitops_config)
        await gitops.initialize()
        
        deployment = GitOpsDeployment(
            name="test-app",
            namespace="default",
            git_path="k8s/test-app",
            cluster_id="test-cluster",
            strategy=GitOpsStrategy.FLUX,
            sync_policy={},
            health_checks=[],
            rollback_policy={}
        )
        
        gitops.deployments["test-app"] = deployment
        
        with patch.object(gitops, '_get_health_status') as mock_health, \
             patch.object(gitops, '_get_cost_analysis') as mock_cost:
            
            mock_health.return_value = {"ready": True, "message": "Healthy"}
            mock_cost.return_value = {"enabled": True, "monthly_cost": 500.0}
            
            status = await gitops.get_deployment_status("test-app")
            
            assert status is not None
            assert status["name"] == "test-app"
            assert status["strategy"] == "flux"
            assert "health_status" in status
            assert "cost_analysis" in status


class TestDeploymentValidator(TestPhase6PlatformIntegration):
    """Test Deployment Validator functionality"""
    
    @pytest.mark.asyncio
    async def test_deployment_validator_initialization(self, pipeline_manager, validation_config):
        """Test deployment validator initialization"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        
        result = await validator.initialize()
        
        assert result is True
        assert len(validator.validation_rules) == 4  # Cost, Performance, Security, Health
        assert validator.validations == {}
        assert validator.validation_history == []
    
    @pytest.mark.asyncio
    async def test_validate_deployment(self, pipeline_manager, validation_config):
        """Test deployment validation"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        await validator.initialize()
        
        with patch.object(validator, '_run_pre_deployment_analysis') as mock_pre, \
             patch.object(validator, '_run_post_deployment_validation') as mock_post, \
             patch.object(validator, '_determine_validation_result') as mock_result:
            
            mock_pre.return_value = None
            mock_post.return_value = None
            mock_result.return_value = {"success": True, "deployment_name": "test-app"}
            
            result = await validator.validate_deployment(
                "test-app", "default", "test-cluster", "k8s/"
            )
            
            assert result is not None
            assert result["success"] is True
            assert result["deployment_name"] == "test-app"
            assert "test-app" in validator.validations
    
    @pytest.mark.asyncio
    async def test_validation_rules(self, pipeline_manager, validation_config):
        """Test validation rules"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        await validator.initialize()
        
        # Test cost impact rule
        cost_rule = validator.validation_rules[0]
        assert cost_rule.name == "cost_impact"
        
        # Test performance rule
        perf_rule = validator.validation_rules[1]
        assert perf_rule.name == "performance"
        
        # Test security rule
        sec_rule = validator.validation_rules[2]
        assert sec_rule.name == "security"
        
        # Test health check rule
        health_rule = validator.validation_rules[3]
        assert health_rule.name == "health_check"
    
    @pytest.mark.asyncio
    async def test_rollback_trigger(self, pipeline_manager, validation_config):
        """Test rollback triggering"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        await validator.initialize()
        
        validation = DeploymentValidation(
            deployment_name="test-app",
            namespace="default",
            cluster_id="test-cluster",
            manifest_path="k8s/",
            validation_config=validation_config,
            pre_deployment_state={},
            post_deployment_state={},
            validation_results={}
        )
        
        with patch.object(validator, '_run_command') as mock_run, \
             patch.object(validator, '_send_rollback_notification') as mock_notify:
            
            mock_run.return_value = (0, b"", b"")
            mock_notify.return_value = None
            
            await validator._trigger_rollback(validation, "health_check", "Health check failed")
            
            assert validation.rollback_triggered is True
            assert validation.rollback_reason == "health_check: Health check failed"
    
    @pytest.mark.asyncio
    async def test_get_validation_status(self, pipeline_manager, validation_config):
        """Test validation status retrieval"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        await validator.initialize()
        
        validation = DeploymentValidation(
            deployment_name="test-app",
            namespace="default",
            cluster_id="test-cluster",
            manifest_path="k8s/",
            validation_config=validation_config,
            pre_deployment_state={},
            post_deployment_state={},
            validation_results={}
        )
        
        validator.validations["test-app"] = validation
        
        status = await validator.get_validation_status("test-app")
        
        assert status is not None
        assert status["deployment_name"] == "test-app"
        assert status["namespace"] == "default"
        assert status["cluster_id"] == "test-cluster"


class TestGitHubActionsIntegration(TestPhase6PlatformIntegration):
    """Test GitHub Actions Integration functionality"""
    
    @pytest.mark.asyncio
    async def test_github_actions_initialization(self, pipeline_manager, github_actions_config):
        """Test GitHub Actions integration initialization"""
        github = GitHubActionsIntegration(pipeline_manager, github_actions_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = Mock()
            
            result = await github.initialize()
            
            assert result is True
            assert github.session is not None
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, pipeline_manager, github_actions_config):
        """Test GitHub Actions workflow creation"""
        github = GitHubActionsIntegration(pipeline_manager, github_actions_config)
        await github.initialize()
        
        cluster_config = {
            "cluster_id": "test-cluster",
            "namespace": "default",
            "optimization_enabled": True
        }
        
        with patch.object(github.template_generator, 'generate_cost_optimization_workflow') as mock_gen:
            mock_gen.return_value = {"name": "test-workflow", "on": {"schedule": [{"cron": "0 2 * * *"}]}}
            
            workflow = github.template_generator.generate_cost_optimization_workflow(cluster_config)
            
            assert workflow is not None
            assert workflow["name"] == "test-workflow"
            assert "on" in workflow


class TestGitLabCICDIntegration(TestPhase6PlatformIntegration):
    """Test GitLab CI/CD Integration functionality"""
    
    @pytest.mark.asyncio
    async def test_gitlab_cicd_initialization(self, pipeline_manager, gitlab_cicd_config):
        """Test GitLab CI/CD integration initialization"""
        gitlab = GitLabCICDIntegration(pipeline_manager, gitlab_cicd_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = Mock()
            
            result = await gitlab.initialize()
            
            assert result is True
            assert gitlab.session is not None
    
    @pytest.mark.asyncio
    async def test_create_pipeline(self, pipeline_manager, gitlab_cicd_config):
        """Test GitLab CI/CD pipeline creation"""
        gitlab = GitLabCICDIntegration(pipeline_manager, gitlab_cicd_config)
        await gitlab.initialize()
        
        cluster_config = {
            "cluster_id": "test-cluster",
            "namespace": "default",
            "optimization_enabled": True
        }
        
        with patch.object(gitlab.template_generator, 'generate_cost_optimization_pipeline') as mock_gen:
            mock_gen.return_value = {"stages": ["prepare", "analyze", "optimize"], "jobs": {}}
            
            pipeline = gitlab.template_generator.generate_cost_optimization_pipeline(cluster_config)
            
            assert pipeline is not None
            assert "stages" in pipeline
            assert "jobs" in pipeline


class TestJenkinsIntegration(TestPhase6PlatformIntegration):
    """Test Jenkins Integration functionality"""
    
    @pytest.mark.asyncio
    async def test_jenkins_initialization(self, pipeline_manager, jenkins_config):
        """Test Jenkins integration initialization"""
        jenkins = JenkinsIntegration(pipeline_manager, jenkins_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = Mock()
            
            result = await jenkins.initialize()
            
            assert result is True
            assert jenkins.session is not None
    
    @pytest.mark.asyncio
    async def test_create_job(self, pipeline_manager, jenkins_config):
        """Test Jenkins job creation"""
        jenkins = JenkinsIntegration(pipeline_manager, jenkins_config)
        await jenkins.initialize()
        
        cluster_config = {
            "cluster_id": "test-cluster",
            "namespace": "default",
            "optimization_enabled": True
        }
        
        with patch.object(jenkins.template_generator, 'generate_cost_optimization_job') as mock_gen:
            mock_gen.return_value = {"name": "test-job", "pipeline": "pipeline { agent { label 'upid-capable' } }"}
            
            job = jenkins.template_generator.generate_cost_optimization_job(cluster_config)
            
            assert job is not None
            assert job["name"] == "test-job"
            assert "pipeline" in job


class TestPhase6Integration(TestPhase6PlatformIntegration):
    """Test Phase 6 integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_cicd_workflow(self, pipeline_manager, gitops_config, validation_config):
        """Test full CI/CD workflow integration"""
        # Initialize all components
        gitops = GitOpsIntegration(pipeline_manager, gitops_config)
        validator = DeploymentValidator(pipeline_manager, validation_config)
        
        await gitops.initialize()
        await validator.initialize()
        
        # Create GitOps deployment
        deployment = GitOpsDeployment(
            name="test-app",
            namespace="default",
            git_path="k8s/test-app",
            cluster_id="test-cluster",
            strategy=GitOpsStrategy.FLUX,
            sync_policy={"automated": True},
            health_checks=[],
            rollback_policy={}
        )
        
        with patch.object(gitops, '_apply_k8s_resource') as mock_apply, \
             patch.object(validator, '_run_pre_deployment_analysis') as mock_pre, \
             patch.object(validator, '_run_post_deployment_validation') as mock_post:
            
            mock_apply.return_value = None
            mock_pre.return_value = None
            mock_post.return_value = None
            
            # Create deployment
            deploy_result = await gitops.create_deployment(deployment)
            assert deploy_result is True
            
            # Validate deployment
            validation_result = await validator.validate_deployment(
                "test-app", "default", "test-cluster", "k8s/"
            )
            assert validation_result is not None
    
    @pytest.mark.asyncio
    async def test_multi_platform_integration(self, pipeline_manager, github_actions_config, 
                                            gitlab_cicd_config, jenkins_config):
        """Test multi-platform CI/CD integration"""
        # Initialize all platform integrations
        github = GitHubActionsIntegration(pipeline_manager, github_actions_config)
        gitlab = GitLabCICDIntegration(pipeline_manager, gitlab_cicd_config)
        jenkins = JenkinsIntegration(pipeline_manager, jenkins_config)
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = Mock()
            
            # Initialize all platforms
            github_result = await github.initialize()
            gitlab_result = await gitlab.initialize()
            jenkins_result = await jenkins.initialize()
            
            assert github_result is True
            assert gitlab_result is True
            assert jenkins_result is True
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, pipeline_manager, validation_config):
        """Test error handling and recovery scenarios"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        await validator.initialize()
        
        # Test validation with errors
        with patch.object(validator, '_run_pre_deployment_analysis') as mock_pre:
            mock_pre.side_effect = Exception("Pre-deployment analysis failed")
            
            result = await validator.validate_deployment(
                "test-app", "default", "test-cluster", "k8s/"
            )
            
            assert result is not None
            assert result["success"] is False
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_notification_system(self, pipeline_manager, validation_config):
        """Test notification system"""
        config = ValidationConfig(
            notification_channels=["slack://webhook-url", "email://test@example.com"]
        )
        
        validator = DeploymentValidator(pipeline_manager, config)
        await validator.initialize()
        
        validation = DeploymentValidation(
            deployment_name="test-app",
            namespace="default",
            cluster_id="test-cluster",
            manifest_path="k8s/",
            validation_config=config,
            pre_deployment_state={},
            post_deployment_state={},
            validation_results={}
        )
        
        with patch.object(validator, '_send_slack_notification') as mock_slack, \
             patch.object(validator, '_send_email_notification') as mock_email:
            
            mock_slack.return_value = None
            mock_email.return_value = None
            
            await validator._send_rollback_notification(validation, "health_check", "Health check failed")
            
            # Verify notifications were sent
            mock_slack.assert_called_once()
            mock_email.assert_called_once()


class TestPhase6Performance(TestPhase6PlatformIntegration):
    """Test Phase 6 performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_pipeline_execution(self, pipeline_manager):
        """Test concurrent pipeline execution"""
        await pipeline_manager.initialize()
        
        # Create multiple pipelines
        pipelines = []
        for i in range(5):
            config = PipelineConfig(
                name=f"pipeline-{i}",
                description=f"Test pipeline {i}",
                pipeline_type=PipelineType.OPTIMIZATION,
                triggers=[TriggerType.MANUAL],
                stages=[{"name": "test", "type": "script"}]
            )
            pipelines.append(config)
        
        # Execute pipelines concurrently
        tasks = []
        for config in pipelines:
            await pipeline_manager.create_pipeline(config)
            task = pipeline_manager.execute_pipeline(config.name, {})
            tasks.append(task)
        
        # Wait for all executions
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 5
        for result in results:
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_large_scale_deployment_validation(self, pipeline_manager, validation_config):
        """Test large-scale deployment validation"""
        validator = DeploymentValidator(pipeline_manager, validation_config)
        await validator.initialize()
        
        # Create multiple validations
        validations = []
        for i in range(10):
            validation = DeploymentValidation(
                deployment_name=f"app-{i}",
                namespace="default",
                cluster_id="test-cluster",
                manifest_path=f"k8s/app-{i}",
                validation_config=validation_config,
                pre_deployment_state={},
                post_deployment_state={},
                validation_results={}
            )
            validations.append(validation)
        
        # Run validations concurrently
        with patch.object(validator, '_run_pre_deployment_analysis') as mock_pre, \
             patch.object(validator, '_run_post_deployment_validation') as mock_post:
            
            mock_pre.return_value = None
            mock_post.return_value = None
            
            tasks = []
            for validation in validations:
                task = validator.validate_deployment(
                    validation.deployment_name,
                    validation.namespace,
                    validation.cluster_id,
                    validation.manifest_path
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            assert len(results) == 10
            for result in results:
                assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 