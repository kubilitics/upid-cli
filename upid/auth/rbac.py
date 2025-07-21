"""
Role-Based Access Control (RBAC) System for UPID CLI
Provides enterprise-grade access control and permissions management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions"""
    # Read permissions
    READ_CLUSTER_INFO = "read:cluster:info"
    READ_PODS = "read:pods"
    READ_SERVICES = "read:services"
    READ_DEPLOYMENTS = "read:deployments"
    READ_METRICS = "read:metrics"
    READ_LOGS = "read:logs"
    READ_COSTS = "read:costs"
    READ_REPORTS = "read:reports"
    
    # Write permissions
    WRITE_PODS = "write:pods"
    WRITE_SERVICES = "write:services"
    WRITE_DEPLOYMENTS = "write:deployments"
    WRITE_CONFIG = "write:config"
    WRITE_OPTIMIZATIONS = "write:optimizations"
    
    # Admin permissions
    ADMIN_CLUSTER = "admin:cluster"
    ADMIN_USERS = "admin:users"
    ADMIN_ROLES = "admin:roles"
    ADMIN_BILLING = "admin:billing"
    ADMIN_AUDIT = "admin:audit"


class Role(Enum):
    """Predefined roles"""
    VIEWER = "viewer"
    DEVELOPER = "developer"
    OPERATOR = "operator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class RBACRole:
    """RBAC role definition"""
    name: str
    description: str
    permissions: List[Permission]
    is_system_role: bool = False
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class RBACUser:
    """RBAC user definition"""
    username: str
    email: Optional[str] = None
    roles: List[str] = None
    groups: List[str] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class RBACGroup:
    """RBAC group definition"""
    name: str
    description: str
    roles: List[str] = None
    members: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None


class RBACManager:
    """
    Role-Based Access Control Manager
    Manages roles, permissions, and access control
    """
    
    def __init__(self):
        self.roles: Dict[str, RBACRole] = {}
        self.users: Dict[str, RBACUser] = {}
        self.groups: Dict[str, RBACGroup] = {}
        self.user_permissions_cache: Dict[str, Set[Permission]] = {}
        
        # Initialize system roles
        self._init_system_roles()
    
    def _init_system_roles(self):
        """Initialize system-defined roles"""
        system_roles = {
            Role.VIEWER: RBACRole(
                name=Role.VIEWER.value,
                description="Read-only access to cluster information",
                permissions=[
                    Permission.READ_CLUSTER_INFO,
                    Permission.READ_PODS,
                    Permission.READ_SERVICES,
                    Permission.READ_DEPLOYMENTS,
                    Permission.READ_METRICS,
                    Permission.READ_LOGS,
                    Permission.READ_COSTS,
                    Permission.READ_REPORTS
                ],
                is_system_role=True,
                created_at=datetime.now()
            ),
            Role.DEVELOPER: RBACRole(
                name=Role.DEVELOPER.value,
                description="Developer access with limited write permissions",
                permissions=[
                    Permission.READ_CLUSTER_INFO,
                    Permission.READ_PODS,
                    Permission.READ_SERVICES,
                    Permission.READ_DEPLOYMENTS,
                    Permission.READ_METRICS,
                    Permission.READ_LOGS,
                    Permission.READ_COSTS,
                    Permission.READ_REPORTS,
                    Permission.WRITE_PODS,
                    Permission.WRITE_SERVICES,
                    Permission.WRITE_DEPLOYMENTS
                ],
                is_system_role=True,
                created_at=datetime.now()
            ),
            Role.OPERATOR: RBACRole(
                name=Role.OPERATOR.value,
                description="Operator access with optimization permissions",
                permissions=[
                    Permission.READ_CLUSTER_INFO,
                    Permission.READ_PODS,
                    Permission.READ_SERVICES,
                    Permission.READ_DEPLOYMENTS,
                    Permission.READ_METRICS,
                    Permission.READ_LOGS,
                    Permission.READ_COSTS,
                    Permission.READ_REPORTS,
                    Permission.WRITE_PODS,
                    Permission.WRITE_SERVICES,
                    Permission.WRITE_DEPLOYMENTS,
                    Permission.WRITE_CONFIG,
                    Permission.WRITE_OPTIMIZATIONS
                ],
                is_system_role=True,
                created_at=datetime.now()
            ),
            Role.ADMIN: RBACRole(
                name=Role.ADMIN.value,
                description="Administrator access with full cluster control",
                permissions=[
                    Permission.READ_CLUSTER_INFO,
                    Permission.READ_PODS,
                    Permission.READ_SERVICES,
                    Permission.READ_DEPLOYMENTS,
                    Permission.READ_METRICS,
                    Permission.READ_LOGS,
                    Permission.READ_COSTS,
                    Permission.READ_REPORTS,
                    Permission.WRITE_PODS,
                    Permission.WRITE_SERVICES,
                    Permission.WRITE_DEPLOYMENTS,
                    Permission.WRITE_CONFIG,
                    Permission.WRITE_OPTIMIZATIONS,
                    Permission.ADMIN_CLUSTER,
                    Permission.ADMIN_USERS,
                    Permission.ADMIN_ROLES,
                    Permission.ADMIN_BILLING
                ],
                is_system_role=True,
                created_at=datetime.now()
            ),
            Role.SUPER_ADMIN: RBACRole(
                name=Role.SUPER_ADMIN.value,
                description="Super administrator with all permissions",
                permissions=list(Permission),  # All permissions
                is_system_role=True,
                created_at=datetime.now()
            )
        }
        
        for role_name, role_def in system_roles.items():
            self.roles[role_name.value] = role_def
    
    async def create_role(
        self, 
        name: str, 
        description: str, 
        permissions: List[Permission]
    ) -> Optional[RBACRole]:
        """
        Create a new RBAC role
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permissions for the role
            
        Returns:
            RBACRole: Created role or None if failed
        """
        try:
            if name in self.roles:
                logger.error(f"Role already exists: {name}")
                return None
            
            role = RBACRole(
                name=name,
                description=description,
                permissions=permissions,
                is_system_role=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.roles[name] = role
            logger.info(f"Created role: {name}")
            return role
            
        except Exception as e:
            logger.error(f"Error creating role {name}: {e}")
            return None
    
    async def update_role(
        self, 
        name: str, 
        description: str = None, 
        permissions: List[Permission] = None
    ) -> bool:
        """
        Update an existing RBAC role
        
        Args:
            name: Role name
            description: New description (optional)
            permissions: New permissions list (optional)
            
        Returns:
            bool: True if update successful
        """
        try:
            if name not in self.roles:
                logger.error(f"Role not found: {name}")
                return False
            
            role = self.roles[name]
            
            if description is not None:
                role.description = description
            
            if permissions is not None:
                role.permissions = permissions
            
            role.updated_at = datetime.now()
            
            # Clear user permission cache
            self.user_permissions_cache.clear()
            
            logger.info(f"Updated role: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating role {name}: {e}")
            return False
    
    async def delete_role(self, name: str) -> bool:
        """
        Delete an RBAC role
        
        Args:
            name: Role name
            
        Returns:
            bool: True if deletion successful
        """
        try:
            if name not in self.roles:
                logger.error(f"Role not found: {name}")
                return False
            
            role = self.roles[name]
            if role.is_system_role:
                logger.error(f"Cannot delete system role: {name}")
                return False
            
            # Check if role is assigned to any users
            for user in self.users.values():
                if name in user.roles:
                    logger.error(f"Cannot delete role {name} - assigned to user {user.username}")
                    return False
            
            del self.roles[name]
            
            # Clear user permission cache
            self.user_permissions_cache.clear()
            
            logger.info(f"Deleted role: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting role {name}: {e}")
            return False
    
    async def create_user(
        self, 
        username: str, 
        email: str = None, 
        roles: List[str] = None
    ) -> Optional[RBACUser]:
        """
        Create a new RBAC user
        
        Args:
            username: Username
            email: User email (optional)
            roles: List of role names (optional)
            
        Returns:
            RBACUser: Created user or None if failed
        """
        try:
            if username in self.users:
                logger.error(f"User already exists: {username}")
                return None
            
            # Validate roles
            if roles:
                for role_name in roles:
                    if role_name not in self.roles:
                        logger.error(f"Role not found: {role_name}")
                        return None
            
            user = RBACUser(
                username=username,
                email=email,
                roles=roles or [],
                groups=[],
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.users[username] = user
            
            # Clear permission cache for this user
            if username in self.user_permissions_cache:
                del self.user_permissions_cache[username]
            
            logger.info(f"Created user: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None
    
    async def update_user(
        self, 
        username: str, 
        email: str = None, 
        roles: List[str] = None,
        is_active: bool = None
    ) -> bool:
        """
        Update an existing RBAC user
        
        Args:
            username: Username
            email: New email (optional)
            roles: New roles list (optional)
            is_active: New active status (optional)
            
        Returns:
            bool: True if update successful
        """
        try:
            if username not in self.users:
                logger.error(f"User not found: {username}")
                return False
            
            user = self.users[username]
            
            if email is not None:
                user.email = email
            
            if roles is not None:
                # Validate roles
                for role_name in roles:
                    if role_name not in self.roles:
                        logger.error(f"Role not found: {role_name}")
                        return False
                user.roles = roles
            
            if is_active is not None:
                user.is_active = is_active
            
            user.updated_at = datetime.now()
            
            # Clear permission cache for this user
            if username in self.user_permissions_cache:
                del self.user_permissions_cache[username]
            
            logger.info(f"Updated user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user {username}: {e}")
            return False
    
    async def delete_user(self, username: str) -> bool:
        """
        Delete an RBAC user
        
        Args:
            username: Username
            
        Returns:
            bool: True if deletion successful
        """
        try:
            if username not in self.users:
                logger.error(f"User not found: {username}")
                return False
            
            del self.users[username]
            
            # Clear permission cache for this user
            if username in self.user_permissions_cache:
                del self.user_permissions_cache[username]
            
            logger.info(f"Deleted user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            return False
    
    async def get_user_permissions(self, username: str) -> Set[Permission]:
        """
        Get all permissions for a user
        
        Args:
            username: Username
            
        Returns:
            Set[Permission]: Set of user permissions
        """
        try:
            # Check cache first
            if username in self.user_permissions_cache:
                return self.user_permissions_cache[username]
            
            if username not in self.users:
                logger.error(f"User not found: {username}")
                return set()
            
            user = self.users[username]
            if not user.is_active:
                return set()
            
            permissions = set()
            
            # Get permissions from user roles
            for role_name in user.roles:
                if role_name in self.roles:
                    role = self.roles[role_name]
                    permissions.update(role.permissions)
            
            # Get permissions from user groups
            for group_name in user.groups:
                if group_name in self.groups:
                    group = self.groups[group_name]
                    for role_name in group.roles:
                        if role_name in self.roles:
                            role = self.roles[role_name]
                            permissions.update(role.permissions)
            
            # Cache the result
            self.user_permissions_cache[username] = permissions
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting permissions for user {username}: {e}")
            return set()
    
    async def check_permission(
        self, 
        username: str, 
        permission: Permission
    ) -> bool:
        """
        Check if user has specific permission
        
        Args:
            username: Username
            permission: Permission to check
            
        Returns:
            bool: True if user has permission
        """
        try:
            user_permissions = await self.get_user_permissions(username)
            return permission in user_permissions
            
        except Exception as e:
            logger.error(f"Error checking permission for user {username}: {e}")
            return False
    
    async def check_any_permission(
        self, 
        username: str, 
        permissions: List[Permission]
    ) -> bool:
        """
        Check if user has any of the specified permissions
        
        Args:
            username: Username
            permissions: List of permissions to check
            
        Returns:
            bool: True if user has any of the permissions
        """
        try:
            user_permissions = await self.get_user_permissions(username)
            return any(permission in user_permissions for permission in permissions)
            
        except Exception as e:
            logger.error(f"Error checking permissions for user {username}: {e}")
            return False
    
    async def check_all_permissions(
        self, 
        username: str, 
        permissions: List[Permission]
    ) -> bool:
        """
        Check if user has all of the specified permissions
        
        Args:
            username: Username
            permissions: List of permissions to check
            
        Returns:
            bool: True if user has all of the permissions
        """
        try:
            user_permissions = await self.get_user_permissions(username)
            return all(permission in user_permissions for permission in permissions)
            
        except Exception as e:
            logger.error(f"Error checking permissions for user {username}: {e}")
            return False
    
    async def create_group(
        self, 
        name: str, 
        description: str, 
        roles: List[str] = None
    ) -> Optional[RBACGroup]:
        """
        Create a new RBAC group
        
        Args:
            name: Group name
            description: Group description
            roles: List of role names (optional)
            
        Returns:
            RBACGroup: Created group or None if failed
        """
        try:
            if name in self.groups:
                logger.error(f"Group already exists: {name}")
                return None
            
            # Validate roles
            if roles:
                for role_name in roles:
                    if role_name not in self.roles:
                        logger.error(f"Role not found: {role_name}")
                        return None
            
            group = RBACGroup(
                name=name,
                description=description,
                roles=roles or [],
                members=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.groups[name] = group
            logger.info(f"Created group: {name}")
            return group
            
        except Exception as e:
            logger.error(f"Error creating group {name}: {e}")
            return None
    
    async def add_user_to_group(self, username: str, group_name: str) -> bool:
        """
        Add user to group
        
        Args:
            username: Username
            group_name: Group name
            
        Returns:
            bool: True if successful
        """
        try:
            if username not in self.users:
                logger.error(f"User not found: {username}")
                return False
            
            if group_name not in self.groups:
                logger.error(f"Group not found: {group_name}")
                return False
            
            user = self.users[username]
            group = self.groups[group_name]
            
            if username not in group.members:
                group.members.append(username)
                group.updated_at = datetime.now()
            
            if group_name not in user.groups:
                user.groups.append(group_name)
                user.updated_at = datetime.now()
            
            # Clear permission cache for this user
            if username in self.user_permissions_cache:
                del self.user_permissions_cache[username]
            
            logger.info(f"Added user {username} to group {group_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding user {username} to group {group_name}: {e}")
            return False
    
    async def remove_user_from_group(self, username: str, group_name: str) -> bool:
        """
        Remove user from group
        
        Args:
            username: Username
            group_name: Group name
            
        Returns:
            bool: True if successful
        """
        try:
            if username not in self.users:
                logger.error(f"User not found: {username}")
                return False
            
            if group_name not in self.groups:
                logger.error(f"Group not found: {group_name}")
                return False
            
            user = self.users[username]
            group = self.groups[group_name]
            
            if username in group.members:
                group.members.remove(username)
                group.updated_at = datetime.now()
            
            if group_name in user.groups:
                user.groups.remove(group_name)
                user.updated_at = datetime.now()
            
            # Clear permission cache for this user
            if username in self.user_permissions_cache:
                del self.user_permissions_cache[username]
            
            logger.info(f"Removed user {username} from group {group_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing user {username} from group {group_name}: {e}")
            return False
    
    async def get_roles(self) -> List[RBACRole]:
        """Get all roles"""
        return list(self.roles.values())
    
    async def get_users(self) -> List[RBACUser]:
        """Get all users"""
        return list(self.users.values())
    
    async def get_groups(self) -> List[RBACGroup]:
        """Get all groups"""
        return list(self.groups.values())
    
    async def clear_permission_cache(self):
        """Clear the permission cache"""
        self.user_permissions_cache.clear()
        logger.info("Permission cache cleared") 