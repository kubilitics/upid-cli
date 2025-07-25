"""
UPID CLI - Kubeconfig Management
Enterprise-grade kubeconfig parsing and management for UPID platform
"""

import logging
import os
import base64
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import yaml
from urllib.parse import urlparse

from kubernetes import config
from kubernetes.config.config_exception import ConfigException

logger = logging.getLogger(__name__)


@dataclass
class Context:
    """Kubernetes context information"""
    name: str
    cluster: str
    user: str
    namespace: Optional[str] = None


@dataclass
class Cluster:
    """Kubernetes cluster information"""
    name: str
    server: str
    certificate_authority: Optional[str] = None
    certificate_authority_data: Optional[str] = None
    insecure_skip_tls_verify: bool = False


@dataclass
class User:
    """Kubernetes user information"""
    name: str
    client_certificate: Optional[str] = None
    client_certificate_data: Optional[str] = None
    client_key: Optional[str] = None
    client_key_data: Optional[str] = None
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    auth_provider: Optional[Dict[str, Any]] = None
    exec: Optional[Dict[str, Any]] = None


@dataclass
class KubeconfigData:
    """Complete kubeconfig data structure"""
    current_context: Optional[str]
    contexts: List[Context]
    clusters: List[Cluster]
    users: List[User]
    api_version: str = "v1"
    kind: str = "Config"


class KubeconfigManager:
    """
    Enterprise-grade kubeconfig management for UPID platform
    
    Provides comprehensive kubeconfig parsing, validation, and management:
    - Multi-context support
    - Secure credential handling
    - Context switching and validation
    - Cluster connectivity testing
    - Configuration merging and updates
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize kubeconfig manager
        
        Args:
            kubeconfig_path: Optional path to kubeconfig file. If None, uses default
        """
        self.kubeconfig_path = kubeconfig_path or self._get_default_kubeconfig_path()
        self._kubeconfig_data: Optional[KubeconfigData] = None
        
        logger.info(f"🔧 Initializing kubeconfig manager: {self.kubeconfig_path}")
    
    def _get_default_kubeconfig_path(self) -> str:
        """Get default kubeconfig path"""
        # Check KUBECONFIG environment variable first
        if os.getenv("KUBECONFIG"):
            return os.getenv("KUBECONFIG")
        
        # Default to ~/.kube/config
        home_dir = Path.home()
        return str(home_dir / ".kube" / "config")
    
    async def load_kubeconfig(self, kubeconfig_path: Optional[str] = None) -> KubeconfigData:
        """
        Load and parse kubeconfig file
        
        Args:
            kubeconfig_path: Optional path to kubeconfig file
            
        Returns:
            KubeconfigData object with parsed configuration
        """
        config_path = kubeconfig_path or self.kubeconfig_path
        
        try:
            logger.info(f"📁 Loading kubeconfig from: {config_path}")
            
            if not Path(config_path).exists():
                raise ConfigException(f"Kubeconfig file not found: {config_path}")
            
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                raise ConfigException(f"Empty kubeconfig file: {config_path}")
            
            # Parse contexts
            contexts = []
            for ctx_data in config_data.get("contexts", []):
                context = Context(
                    name=ctx_data["name"],
                    cluster=ctx_data["context"]["cluster"],
                    user=ctx_data["context"]["user"],
                    namespace=ctx_data["context"].get("namespace")
                )
                contexts.append(context)
            
            # Parse clusters
            clusters = []
            for cluster_data in config_data.get("clusters", []):
                cluster = Cluster(
                    name=cluster_data["name"],
                    server=cluster_data["cluster"]["server"],
                    certificate_authority=cluster_data["cluster"].get("certificate-authority"),
                    certificate_authority_data=cluster_data["cluster"].get("certificate-authority-data"),
                    insecure_skip_tls_verify=cluster_data["cluster"].get("insecure-skip-tls-verify", False)
                )
                clusters.append(cluster)
            
            # Parse users
            users = []
            for user_data in config_data.get("users", []):
                user = User(
                    name=user_data["name"],
                    client_certificate=user_data["user"].get("client-certificate"),
                    client_certificate_data=user_data["user"].get("client-certificate-data"),
                    client_key=user_data["user"].get("client-key"),
                    client_key_data=user_data["user"].get("client-key-data"),
                    token=user_data["user"].get("token"),
                    username=user_data["user"].get("username"),
                    password=user_data["user"].get("password"),
                    auth_provider=user_data["user"].get("auth-provider"),
                    exec=user_data["user"].get("exec")
                )
                users.append(user)
            
            self._kubeconfig_data = KubeconfigData(
                current_context=config_data.get("current-context"),
                contexts=contexts,
                clusters=clusters,
                users=users,
                api_version=config_data.get("apiVersion", "v1"),
                kind=config_data.get("kind", "Config")
            )
            
            logger.info(f"✅ Loaded kubeconfig: {len(contexts)} contexts, {len(clusters)} clusters, {len(users)} users")
            return self._kubeconfig_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load kubeconfig: {e}")
            raise ConfigException(f"Failed to load kubeconfig: {e}")
    
    async def get_contexts(self) -> List[Context]:
        """
        Get all available contexts
        
        Returns:
            List of Context objects
        """
        if not self._kubeconfig_data:
            await self.load_kubeconfig()
        
        return self._kubeconfig_data.contexts
    
    async def get_current_context(self) -> Optional[Context]:
        """
        Get current active context
        
        Returns:
            Current Context object or None
        """
        if not self._kubeconfig_data:
            await self.load_kubeconfig()
        
        if not self._kubeconfig_data.current_context:
            return None
        
        for context in self._kubeconfig_data.contexts:
            if context.name == self._kubeconfig_data.current_context:
                return context
        
        return None
    
    async def switch_context(self, context_name: str) -> bool:
        """
        Switch to a different context
        
        Args:
            context_name: Name of context to switch to
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"🔄 Switching to context: {context_name}")
            
            if not self._kubeconfig_data:
                await self.load_kubeconfig()
            
            # Verify context exists
            context_exists = any(ctx.name == context_name for ctx in self._kubeconfig_data.contexts)
            if not context_exists:
                available_contexts = [ctx.name for ctx in self._kubeconfig_data.contexts]
                raise ConfigException(f"Context '{context_name}' not found. Available: {available_contexts}")
            
            # Update current context in memory
            self._kubeconfig_data.current_context = context_name
            
            # Save to kubeconfig file
            await self._save_kubeconfig()
            
            logger.info(f"✅ Switched to context: {context_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to switch context: {e}")
            raise ConfigException(f"Failed to switch context: {e}")
    
    async def validate_cluster_access(self, cluster_name: Optional[str] = None, context_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate access to cluster
        
        Args:
            cluster_name: Optional cluster name to validate
            context_name: Optional context name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            logger.info(f"🔍 Validating cluster access...")
            
            if not self._kubeconfig_data:
                await self.load_kubeconfig()
            
            # Determine context to validate
            target_context = None
            if context_name:
                target_context = next((ctx for ctx in self._kubeconfig_data.contexts if ctx.name == context_name), None)
                if not target_context:
                    return False, f"Context '{context_name}' not found"
            else:
                target_context = await self.get_current_context()
                if not target_context:
                    return False, "No current context set"
            
            # Find cluster and user information
            cluster_info = next((c for c in self._kubeconfig_data.clusters if c.name == target_context.cluster), None)
            user_info = next((u for u in self._kubeconfig_data.users if u.name == target_context.user), None)
            
            if not cluster_info:
                return False, f"Cluster '{target_context.cluster}' not found in kubeconfig"
            
            if not user_info:
                return False, f"User '{target_context.user}' not found in kubeconfig"
            
            # Validate cluster endpoint
            try:
                parsed_url = urlparse(cluster_info.server)
                if not parsed_url.scheme or not parsed_url.netloc:
                    return False, f"Invalid cluster server URL: {cluster_info.server}"
            except Exception as e:
                return False, f"Invalid cluster server URL: {e}"
            
            # Test actual connectivity using kubernetes-python client
            try:
                # Temporarily switch to target context for testing
                original_context = self._kubeconfig_data.current_context
                
                if original_context != target_context.name:
                    self._kubeconfig_data.current_context = target_context.name
                    await self._save_kubeconfig()
                
                # Test connection
                config.load_kube_config(config_file=self.kubeconfig_path, context=target_context.name)
                
                # Try a simple API call
                from kubernetes import client
                api_client = client.ApiClient()
                core_v1 = client.CoreV1Api(api_client)
                
                # Simple test - get API resources
                api_resources = core_v1.get_api_resources()
                
                # Restore original context if different
                if original_context != target_context.name and original_context:
                    self._kubeconfig_data.current_context = original_context
                    await self._save_kubeconfig()
                
                logger.info(f"✅ Cluster access validated: {target_context.cluster}")
                return True, "Cluster access validated successfully"
                
            except Exception as e:
                # Restore original context on error
                if 'original_context' in locals() and original_context != target_context.name and original_context:
                    self._kubeconfig_data.current_context = original_context
                    await self._save_kubeconfig()
                
                return False, f"Failed to connect to cluster: {str(e)}"
            
        except Exception as e:
            logger.error(f"❌ Failed to validate cluster access: {e}")
            return False, f"Validation error: {str(e)}"
    
    async def get_cluster_endpoint(self, cluster_name: Optional[str] = None) -> Optional[str]:
        """
        Get cluster endpoint URL
        
        Args:
            cluster_name: Optional cluster name. If None, uses current context
            
        Returns:
            Cluster endpoint URL or None
        """
        if not self._kubeconfig_data:
            await self.load_kubeconfig()
        
        target_cluster = cluster_name
        if not target_cluster:
            current_context = await self.get_current_context()
            if current_context:
                target_cluster = current_context.cluster
        
        if target_cluster:
            cluster_info = next((c for c in self._kubeconfig_data.clusters if c.name == target_cluster), None)
            if cluster_info:
                return cluster_info.server
        
        return None
    
    async def create_context(
        self, 
        context_name: str, 
        cluster_name: str, 
        user_name: str, 
        namespace: Optional[str] = None
    ) -> bool:
        """
        Create a new context
        
        Args:
            context_name: Name for new context
            cluster_name: Cluster name to use
            user_name: User name to use
            namespace: Optional default namespace
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"🆕 Creating context: {context_name}")
            
            if not self._kubeconfig_data:
                await self.load_kubeconfig()
            
            # Check if context already exists
            if any(ctx.name == context_name for ctx in self._kubeconfig_data.contexts):
                logger.warning(f"Context '{context_name}' already exists")
                return True
            
            # Verify cluster and user exist
            cluster_exists = any(c.name == cluster_name for c in self._kubeconfig_data.clusters)
            user_exists = any(u.name == user_name for u in self._kubeconfig_data.users)
            
            if not cluster_exists:
                raise ConfigException(f"Cluster '{cluster_name}' not found")
            
            if not user_exists:
                raise ConfigException(f"User '{user_name}' not found")
            
            # Create new context
            new_context = Context(
                name=context_name,
                cluster=cluster_name,
                user=user_name,
                namespace=namespace
            )
            
            self._kubeconfig_data.contexts.append(new_context)
            
            # Save updated kubeconfig
            await self._save_kubeconfig()
            
            logger.info(f"✅ Created context: {context_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create context: {e}")
            raise ConfigException(f"Failed to create context: {e}")
    
    async def delete_context(self, context_name: str) -> bool:
        """
        Delete a context
        
        Args:
            context_name: Name of context to delete
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"🗑️ Deleting context: {context_name}")
            
            if not self._kubeconfig_data:
                await self.load_kubeconfig()
            
            # Find and remove context
            original_count = len(self._kubeconfig_data.contexts)
            self._kubeconfig_data.contexts = [
                ctx for ctx in self._kubeconfig_data.contexts 
                if ctx.name != context_name
            ]
            
            if len(self._kubeconfig_data.contexts) == original_count:
                logger.warning(f"Context '{context_name}' not found")
                return True
            
            # Clear current context if it was the deleted one
            if self._kubeconfig_data.current_context == context_name:
                self._kubeconfig_data.current_context = None
                if self._kubeconfig_data.contexts:
                    self._kubeconfig_data.current_context = self._kubeconfig_data.contexts[0].name
            
            # Save updated kubeconfig
            await self._save_kubeconfig()
            
            logger.info(f"✅ Deleted context: {context_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete context: {e}")
            raise ConfigException(f"Failed to delete context: {e}")
    
    async def _save_kubeconfig(self):
        """Save kubeconfig data back to file"""
        if not self._kubeconfig_data:
            return
        
        try:
            # Convert back to dictionary format
            config_dict = {
                "apiVersion": self._kubeconfig_data.api_version,
                "kind": self._kubeconfig_data.kind,
                "current-context": self._kubeconfig_data.current_context,
                "contexts": [
                    {
                        "name": ctx.name,
                        "context": {
                            "cluster": ctx.cluster,
                            "user": ctx.user,
                            **({"namespace": ctx.namespace} if ctx.namespace else {})
                        }
                    }
                    for ctx in self._kubeconfig_data.contexts
                ],
                "clusters": [
                    {
                        "name": cluster.name,
                        "cluster": {
                            "server": cluster.server,
                            **({"certificate-authority": cluster.certificate_authority} if cluster.certificate_authority else {}),
                            **({"certificate-authority-data": cluster.certificate_authority_data} if cluster.certificate_authority_data else {}),
                            **({"insecure-skip-tls-verify": cluster.insecure_skip_tls_verify} if cluster.insecure_skip_tls_verify else {})
                        }
                    }
                    for cluster in self._kubeconfig_data.clusters
                ],
                "users": [
                    {
                        "name": user.name,
                        "user": {
                            k: v for k, v in {
                                "client-certificate": user.client_certificate,
                                "client-certificate-data": user.client_certificate_data,
                                "client-key": user.client_key,
                                "client-key-data": user.client_key_data,
                                "token": user.token,
                                "username": user.username,
                                "password": user.password,
                                "auth-provider": user.auth_provider,
                                "exec": user.exec
                            }.items() if v is not None
                        }
                    }
                    for user in self._kubeconfig_data.users
                ]
            }
            
            # Create backup of existing kubeconfig
            backup_path = f"{self.kubeconfig_path}.backup"
            if Path(self.kubeconfig_path).exists():
                import shutil
                shutil.copy2(self.kubeconfig_path, backup_path)
            
            # Write updated kubeconfig
            with open(self.kubeconfig_path, 'w') as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False, sort_keys=False)
            
            logger.debug(f"💾 Saved kubeconfig to: {self.kubeconfig_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save kubeconfig: {e}")
            # Restore from backup if available
            backup_path = f"{self.kubeconfig_path}.backup"
            if Path(backup_path).exists():
                import shutil
                shutil.copy2(backup_path, self.kubeconfig_path)
                logger.info("🔄 Restored kubeconfig from backup")
            raise ConfigException(f"Failed to save kubeconfig: {e}")
    
    async def merge_kubeconfig(self, additional_config_path: str) -> bool:
        """
        Merge additional kubeconfig into current one
        
        Args:
            additional_config_path: Path to kubeconfig to merge
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"🔗 Merging kubeconfig from: {additional_config_path}")
            
            # Load current config
            if not self._kubeconfig_data:
                await self.load_kubeconfig()
            
            # Load additional config
            additional_manager = KubeconfigManager(additional_config_path)
            additional_data = await additional_manager.load_kubeconfig()
            
            # Merge contexts (avoid duplicates)
            existing_context_names = {ctx.name for ctx in self._kubeconfig_data.contexts}
            for ctx in additional_data.contexts:
                if ctx.name not in existing_context_names:
                    self._kubeconfig_data.contexts.append(ctx)
            
            # Merge clusters (avoid duplicates)
            existing_cluster_names = {cluster.name for cluster in self._kubeconfig_data.clusters}
            for cluster in additional_data.clusters:
                if cluster.name not in existing_cluster_names:
                    self._kubeconfig_data.clusters.append(cluster)
            
            # Merge users (avoid duplicates)
            existing_user_names = {user.name for user in self._kubeconfig_data.users}
            for user in additional_data.users:
                if user.name not in existing_user_names:
                    self._kubeconfig_data.users.append(user)
            
            # Save merged config
            await self._save_kubeconfig()
            
            logger.info(f"✅ Successfully merged kubeconfig")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to merge kubeconfig: {e}")
            raise ConfigException(f"Failed to merge kubeconfig: {e}")
    
    def get_kubeconfig_info(self) -> Dict[str, Any]:
        """
        Get summary information about kubeconfig
        
        Returns:
            Dictionary with kubeconfig summary
        """
        if not self._kubeconfig_data:
            return {"error": "Kubeconfig not loaded"}
        
        return {
            "kubeconfig_path": str(self.kubeconfig_path),
            "current_context": self._kubeconfig_data.current_context,
            "total_contexts": len(self._kubeconfig_data.contexts),
            "total_clusters": len(self._kubeconfig_data.clusters),
            "total_users": len(self._kubeconfig_data.users),
            "contexts": [ctx.name for ctx in self._kubeconfig_data.contexts],
            "clusters": [cluster.name for cluster in self._kubeconfig_data.clusters],
            "users": [user.name for user in self._kubeconfig_data.users]
        }