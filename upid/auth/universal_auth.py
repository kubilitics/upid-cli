"""
Universal Authentication System for UPID CLI
Handles all authentication scenarios automatically
"""

import os
import subprocess
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .local import LocalKubernetesDetector
from .cloud import CloudKubernetesDetector
from .rbac import RBACEnforcer

logger = logging.getLogger(__name__)

@dataclass
class EnvironmentInfo:
    """Information about detected Kubernetes environment"""
    is_local_cluster: bool
    cluster_type: str
    kubeconfig_path: Optional[str] = None
    auth_required: bool = False
    requires_setup: bool = False
    cloud_provider: Optional[str] = None
    context_name: Optional[str] = None
    cluster_name: Optional[str] = None
    region: Optional[str] = None
    project_id: Optional[str] = None
    resource_group: Optional[str] = None

@dataclass
class AuthResult:
    """Result of authentication attempt"""
    success: bool
    environment_info: EnvironmentInfo
    auth_method: str
    error_message: Optional[str] = None
    requires_action: bool = False

class UniversalAuthenticator:
    """
    Universal authenticator that handles all authentication scenarios automatically
    Based on the architecture guide implementation
    """
    
    def __init__(self):
        self.local_detector = LocalKubernetesDetector()
        self.cloud_detector = CloudKubernetesDetector()
        self.rbac_enforcer = RBACEnforcer()
        
    async def authenticate_user(self, context: Dict[str, Any]) -> AuthResult:
        """
        Universal authentication flow
        """
        try:
            # Step 1: Detect environment
            env_info = await self.detect_environment()
            
            # Step 2: Choose authentication strategy
            if env_info.is_local_cluster:
                return await self.authenticate_local(env_info)
            elif env_info.cloud_provider:
                return await self.authenticate_cloud(env_info)
            else:
                return await self.authenticate_upid_saas(context)
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return AuthResult(
                success=False,
                environment_info=EnvironmentInfo(
                    is_local_cluster=False,
                    cluster_type="unknown",
                    auth_required=True,
                    requires_setup=True
                ),
                auth_method="unknown",
                error_message=str(e),
                requires_action=True
            )
    
    async def detect_environment(self) -> EnvironmentInfo:
        """
        Auto-detect Kubernetes environment
        """
        # Check for local clusters first
        local_info = await self.local_detector.detect()
        if local_info.detected:
            return EnvironmentInfo(
                is_local_cluster=True,
                cluster_type=local_info.cluster_type,
                kubeconfig_path=local_info.kubeconfig_path,
                auth_required=False,
                context_name=local_info.context_name,
                cluster_name=local_info.cluster_name
            )
        
        # Check for cloud clusters
        cloud_info = await self.cloud_detector.detect()
        if cloud_info.detected:
            return EnvironmentInfo(
                is_local_cluster=False,
                cluster_type=cloud_info.cluster_type,
                cloud_provider=cloud_info.provider,
                kubeconfig_path=cloud_info.kubeconfig_path,
                auth_required=cloud_info.auth_required,
                context_name=cloud_info.context_name,
                cluster_name=cloud_info.cluster_name,
                region=cloud_info.region,
                project_id=cloud_info.project_id,
                resource_group=cloud_info.resource_group
            )
        
        # No cluster detected - prompt for UPID SaaS
        return EnvironmentInfo(
            is_local_cluster=False,
            cluster_type="unknown",
            auth_required=True,
            requires_setup=True
        )
    
    async def authenticate_local(self, env_info: EnvironmentInfo) -> AuthResult:
        """
        Authenticate with local Kubernetes cluster
        """
        try:
            # Test connection to local cluster
            if await self.test_local_connection(env_info):
                return AuthResult(
                    success=True,
                    environment_info=env_info,
                    auth_method="local_k8s"
                )
            else:
                return AuthResult(
                    success=False,
                    environment_info=env_info,
                    auth_method="local_k8s",
                    error_message="Failed to connect to local cluster",
                    requires_action=True
                )
        except Exception as e:
            return AuthResult(
                success=False,
                environment_info=env_info,
                auth_method="local_k8s",
                error_message=str(e),
                requires_action=True
            )
    
    async def authenticate_cloud(self, env_info: EnvironmentInfo) -> AuthResult:
        """
        Authenticate with cloud Kubernetes cluster
        """
        try:
            # Test connection to cloud cluster
            if await self.test_cloud_connection(env_info):
                return AuthResult(
                    success=True,
                    environment_info=env_info,
                    auth_method="cloud_k8s"
                )
            else:
                return AuthResult(
                    success=False,
                    environment_info=env_info,
                    auth_method="cloud_k8s",
                    error_message="Failed to connect to cloud cluster",
                    requires_action=True
                )
        except Exception as e:
            return AuthResult(
                success=False,
                environment_info=env_info,
                auth_method="cloud_k8s",
                error_message=str(e),
                requires_action=True
            )
    
    async def authenticate_upid_saas(self, context: Dict[str, Any]) -> AuthResult:
        """
        Authenticate with UPID SaaS platform
        """
        try:
            # This would integrate with the existing AuthManager
            # For now, return a setup-required result
            return AuthResult(
                success=False,
                environment_info=EnvironmentInfo(
                    is_local_cluster=False,
                    cluster_type="saas",
                    auth_required=True,
                    requires_setup=True
                ),
                auth_method="upid_saas",
                error_message="UPID SaaS authentication not yet implemented",
                requires_action=True
            )
        except Exception as e:
            return AuthResult(
                success=False,
                environment_info=EnvironmentInfo(
                    is_local_cluster=False,
                    cluster_type="saas",
                    auth_required=True,
                    requires_setup=True
                ),
                auth_method="upid_saas",
                error_message=str(e),
                requires_action=True
            )
    
    async def test_local_connection(self, env_info: EnvironmentInfo) -> bool:
        """
        Test connection to local Kubernetes cluster
        """
        try:
            # Use kubectl to test connection
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Local connection test failed: {e}")
            return False
    
    async def test_cloud_connection(self, env_info: EnvironmentInfo) -> bool:
        """
        Test connection to cloud Kubernetes cluster
        """
        try:
            # Use kubectl to test connection
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Cloud connection test failed: {e}")
            return False
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about the current cluster
        """
        try:
            # Get cluster info
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    'cluster_info': result.stdout,
                    'connection_status': 'connected'
                }
            else:
                return {
                    'cluster_info': 'Not connected',
                    'connection_status': 'disconnected'
                }
        except Exception as e:
            return {
                'cluster_info': f'Error: {str(e)}',
                'connection_status': 'error'
            } 