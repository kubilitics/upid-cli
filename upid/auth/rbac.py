"""
RBAC Enforcer for UPID CLI
Handles role-based access control for Kubernetes clusters
"""

import subprocess
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class RBACInfo:
    """RBAC information for current user"""
    user: str
    namespace: str
    roles: List[str]
    permissions: List[str]
    can_read: bool = False
    can_write: bool = False
    can_delete: bool = False
    can_exec: bool = False

@dataclass
class PermissionCheck:
    """Result of permission check"""
    allowed: bool
    reason: str
    required_permissions: List[str]
    user_permissions: List[str]

class RBACEnforcer:
    """
    RBAC enforcer for Kubernetes clusters
    """
    
    def __init__(self):
        self.required_permissions = {
            'read': ['get', 'list', 'watch'],
            'write': ['create', 'update', 'patch'],
            'delete': ['delete'],
            'exec': ['create']
        }
    
    async def check_user_permissions(self, namespace: str = "default") -> RBACInfo:
        """
        Check current user's RBAC permissions
        """
        try:
            # Get current user
            user = await self._get_current_user()
            if not user:
                return RBACInfo(
                    user="unknown",
                    namespace=namespace,
                    roles=[],
                    permissions=[],
                    can_read=False,
                    can_write=False,
                    can_delete=False,
                    can_exec=False
                )
            
            # Get user roles
            roles = await self._get_user_roles(user, namespace)
            
            # Get user permissions
            permissions = await self._get_user_permissions(user, namespace)
            
            # Check specific permissions
            can_read = await self._check_permission(user, namespace, self.required_permissions['read'])
            can_write = await self._check_permission(user, namespace, self.required_permissions['write'])
            can_delete = await self._check_permission(user, namespace, self.required_permissions['delete'])
            can_exec = await self._check_permission(user, namespace, self.required_permissions['exec'])
            
            return RBACInfo(
                user=user,
                namespace=namespace,
                roles=roles,
                permissions=permissions,
                can_read=can_read,
                can_write=can_write,
                can_delete=can_delete,
                can_exec=can_exec
            )
            
        except Exception as e:
            logger.error(f"RBAC check failed: {e}")
            return RBACInfo(
                user="error",
                namespace=namespace,
                roles=[],
                permissions=[],
                can_read=False,
                can_write=False,
                can_delete=False,
                can_exec=False
            )
    
    async def check_resource_permission(self, resource: str, action: str, namespace: str = "default") -> PermissionCheck:
        """
        Check if user can perform action on specific resource
        """
        try:
            user = await self._get_current_user()
            if not user:
                return PermissionCheck(
                    allowed=False,
                    reason="No authenticated user",
                    required_permissions=[f"{action} {resource}"],
                    user_permissions=[]
                )
            
            # Check specific permission
            allowed = await self._check_specific_permission(user, namespace, action, resource)
            
            if allowed:
                return PermissionCheck(
                    allowed=True,
                    reason="Permission granted",
                    required_permissions=[f"{action} {resource}"],
                    user_permissions=[f"{action} {resource}"]
                )
            else:
                return PermissionCheck(
                    allowed=False,
                    reason="Permission denied",
                    required_permissions=[f"{action} {resource}"],
                    user_permissions=[]
                )
                
        except Exception as e:
            logger.error(f"Resource permission check failed: {e}")
            return PermissionCheck(
                allowed=False,
                reason=f"Error: {str(e)}",
                required_permissions=[f"{action} {resource}"],
                user_permissions=[]
            )
    
    async def get_namespace_permissions(self, namespace: str) -> Dict[str, Any]:
        """
        Get detailed permissions for a namespace
        """
        try:
            rbac_info = await self.check_user_permissions(namespace)
            
            return {
                'user': rbac_info.user,
                'namespace': rbac_info.namespace,
                'roles': rbac_info.roles,
                'permissions': rbac_info.permissions,
                'capabilities': {
                    'read': rbac_info.can_read,
                    'write': rbac_info.can_write,
                    'delete': rbac_info.can_delete,
                    'exec': rbac_info.can_exec
                }
            }
        except Exception as e:
            logger.error(f"Namespace permissions check failed: {e}")
            return {
                'user': 'error',
                'namespace': namespace,
                'roles': [],
                'permissions': [],
                'capabilities': {
                    'read': False,
                    'write': False,
                    'delete': False,
                    'exec': False
                }
            }
    
    async def _get_current_user(self) -> Optional[str]:
        """
        Get current authenticated user
        """
        try:
            result = subprocess.run(
                ['kubectl', 'config', 'view', '--minify', '--output', 'jsonpath={..user}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to get current user: {e}")
            return None
    
    async def _get_user_roles(self, user: str, namespace: str) -> List[str]:
        """
        Get roles assigned to user in namespace
        """
        try:
            # Get role bindings
            result = subprocess.run(
                ['kubectl', 'get', 'rolebindings', '-n', namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                roles = []
                
                for rb in data.get('items', []):
                    subjects = rb.get('subjects', [])
                    for subject in subjects:
                        if subject.get('kind') == 'User' and subject.get('name') == user:
                            role_ref = rb.get('roleRef', {})
                            if role_ref.get('kind') == 'Role':
                                roles.append(role_ref.get('name', ''))
                            elif role_ref.get('kind') == 'ClusterRole':
                                roles.append(f"cluster:{role_ref.get('name', '')}")
                
                return roles
            
            return []
            
        except Exception as e:
            logger.debug(f"Failed to get user roles: {e}")
            return []
    
    async def _get_user_permissions(self, user: str, namespace: str) -> List[str]:
        """
        Get permissions for user in namespace
        """
        try:
            # Get roles first
            roles = await self._get_user_roles(user, namespace)
            permissions = []
            
            for role in roles:
                if role.startswith('cluster:'):
                    # Cluster role
                    cluster_role = role.replace('cluster:', '')
                    role_permissions = await self._get_cluster_role_permissions(cluster_role)
                else:
                    # Namespace role
                    role_permissions = await self._get_role_permissions(role, namespace)
                
                permissions.extend(role_permissions)
            
            return list(set(permissions))  # Remove duplicates
            
        except Exception as e:
            logger.debug(f"Failed to get user permissions: {e}")
            return []
    
    async def _get_role_permissions(self, role_name: str, namespace: str) -> List[str]:
        """
        Get permissions for a specific role
        """
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'role', role_name, '-n', namespace, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                permissions = []
                
                for rule in data.get('rules', []):
                    resources = rule.get('resources', [])
                    verbs = rule.get('verbs', [])
                    
                    for resource in resources:
                        for verb in verbs:
                            permissions.append(f"{verb} {resource}")
                
                return permissions
            
            return []
            
        except Exception as e:
            logger.debug(f"Failed to get role permissions: {e}")
            return []
    
    async def _get_cluster_role_permissions(self, role_name: str) -> List[str]:
        """
        Get permissions for a specific cluster role
        """
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'clusterrole', role_name, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                permissions = []
                
                for rule in data.get('rules', []):
                    resources = rule.get('resources', [])
                    verbs = rule.get('verbs', [])
                    
                    for resource in resources:
                        for verb in verbs:
                            permissions.append(f"{verb} {resource}")
                
                return permissions
            
            return []
            
        except Exception as e:
            logger.debug(f"Failed to get cluster role permissions: {e}")
            return []
    
    async def _check_permission(self, user: str, namespace: str, required_permissions: List[str]) -> bool:
        """
        Check if user has required permissions
        """
        try:
            user_permissions = await self._get_user_permissions(user, namespace)
            
            for required in required_permissions:
                if not any(required in perm for perm in user_permissions):
                    return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Permission check failed: {e}")
            return False
    
    async def _check_specific_permission(self, user: str, namespace: str, action: str, resource: str) -> bool:
        """
        Check if user can perform specific action on resource
        """
        try:
            # Try to perform the action
            result = subprocess.run(
                ['kubectl', 'auth', 'can-i', action, resource, '-n', namespace],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0 and 'yes' in result.stdout.lower()
            
        except Exception as e:
            logger.debug(f"Specific permission check failed: {e}")
            return False 