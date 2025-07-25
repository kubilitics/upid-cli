"""
UPID CLI - CI/CD Integration Module
Enterprise-grade CI/CD pipeline integration for automated optimization workflows
"""

# Import centralized configuration
try:
    from ..core.central_config import get_module_metadata
    _metadata = get_module_metadata()
    __version__ = _metadata["__version__"]
    __author__ = _metadata["__author__"]
    __email__ = _metadata["__email__"]
except ImportError:
    # Fallback values if config system not available
    __version__ = "2.0.0"
    __author__ = "UPID Team"
    __email__ = "support@upid.io"

from .pipeline_manager import PipelineManager
from .gitops_integration import GitOpsIntegration
from .github_actions import GitHubActionsIntegration
from .gitlab_cicd import GitLabCICDIntegration
from .jenkins_plugin import JenkinsIntegration
from .deployment_validator import DeploymentValidator
from .advanced_gitops import AdvancedGitOpsIntegration, MultiClusterConfig, GitOpsSecurityConfig, AdvancedRollbackConfig
from .enhanced_deployment_validator import EnhancedDeploymentValidator, EnhancedValidationRule, PerformanceBenchmark, SecurityComplianceConfig, CustomValidationPlugin
from .analytics_reporting import CICDAnalyticsReporting, DeploymentMetrics, CostImpactMetrics, PerformanceTrendMetrics, ExecutiveReportConfig

__all__ = [
    "PipelineManager",
    "GitOpsIntegration", 
    "GitHubActionsIntegration",
    "GitLabCICDIntegration",
    "JenkinsIntegration",
    "DeploymentValidator",
    "EnhancedDeploymentValidator",
    "EnhancedValidationRule",
    "PerformanceBenchmark",
    "SecurityComplianceConfig",
    "CustomValidationPlugin",
    "CICDAnalyticsReporting",
    "DeploymentMetrics",
    "CostImpactMetrics",
    "PerformanceTrendMetrics",
    "ExecutiveReportConfig",
    "AdvancedGitOpsIntegration",
    "MultiClusterConfig",
    "GitOpsSecurityConfig", 
    "AdvancedRollbackConfig"
]