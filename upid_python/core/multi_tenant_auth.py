"""
UPID CLI - Multi-tenant Authentication & RBAC
Enhanced authentication system with tenant isolation and role-based access control
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class TenantRole(Enum):
    """Tenant roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"      # Can manage all tenants
    TENANT_ADMIN = "tenant_admin"    # Can manage tenant resources
    OPERATOR = "operator"            # Can perform operations
    VIEWER = "viewer"               # Read-only access
    GUEST = "guest"                 # Limited access


class ResourceType(Enum):
    """Resource types for permission control"""
    CLUSTER = "cluster"
    NAMESPACE = "namespace"
    DEPLOYMENT = "deployment"
    POD = "pod"
    SERVICE = "service"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    REPORT = "report"
    USER = "user"
    TENANT = "tenant"


class Permission(Enum):
    """Granular permissions"""
    # Cluster permissions
    CLUSTER_READ = "cluster:read"
    CLUSTER_WRITE = "cluster:write"
    CLUSTER_DELETE = "cluster:delete"
    CLUSTER_ADMIN = "cluster:admin"
    
    # Namespace permissions
    NAMESPACE_READ = "namespace:read"
    NAMESPACE_WRITE = "namespace:write"
    NAMESPACE_DELETE = "namespace:delete"
    NAMESPACE_ADMIN = "namespace:admin"
    
    # Resource permissions
    RESOURCE_READ = "resource:read"
    RESOURCE_WRITE = "resource:write"
    RESOURCE_DELETE = "resource:delete"
    RESOURCE_ADMIN = "resource:admin"
    
    # Analysis permissions
    ANALYSIS_READ = "analysis:read"
    ANALYSIS_WRITE = "analysis:write"
    ANALYSIS_DELETE = "analysis:delete"
    
    # Optimization permissions
    OPTIMIZATION_READ = "optimization:read"
    OPTIMIZATION_WRITE = "optimization:write"
    OPTIMIZATION_EXECUTE = "optimization:execute"
    OPTIMIZATION_DELETE = "optimization:delete"
    
    # Reporting permissions
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    REPORT_DELETE = "report:delete"
    REPORT_EXPORT = "report:export"
    
    # User management permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_ADMIN = "user:admin"
    
    # Tenant management permissions
    TENANT_READ = "tenant:read"
    TENANT_WRITE = "tenant:write"
    TENANT_DELETE = "tenant:delete"
    TENANT_ADMIN = "tenant:admin"
    
    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_ADMIN = "system:admin"


@dataclass
class Tenant:
    """Tenant information with security context"""
    tenant_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    max_users: int = 100
    max_clusters: int = 50
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User:
    """User information with tenant context"""
    user_id: str
    email: str
    tenant_id: str
    roles: List[TenantRole] = field(default_factory=list)
    permissions: List[Permission] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def has_role(self, role: TenantRole) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return TenantRole.TENANT_ADMIN in self.roles or TenantRole.SUPER_ADMIN in self.roles


@dataclass
class ResourcePermission:
    """Resource-specific permission"""
    resource_type: ResourceType
    resource_id: str
    tenant_id: str
    permissions: List[Permission] = field(default_factory=list)
    granted_to: List[str] = field(default_factory=list)  # user_ids
    granted_by: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class AuditEvent:
    """Audit event for security tracking"""
    event_id: str
    tenant_id: str
    user_id: str
    event_type: str
    action: str
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class MultiTenantAuthManager:
    """
    Multi-tenant Authentication and RBAC Manager
    
    Provides comprehensive multi-tenant authentication capabilities:
    - Tenant isolation and security
    - Role-based access control (RBAC)
    - Resource-based permissions
    - Audit logging and compliance
    - Session management
    - Permission inheritance and delegation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, User] = {}
        self.resource_permissions: Dict[str, ResourcePermission] = {}
        self.audit_events: List[AuditEvent] = []
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Role-permission mappings
        self.role_permissions: Dict[TenantRole, Set[Permission]] = {
            TenantRole.SUPER_ADMIN: {
                Permission.TENANT_ADMIN, Permission.TENANT_WRITE, Permission.TENANT_DELETE,
                Permission.USER_ADMIN, Permission.SYSTEM_ADMIN, Permission.SYSTEM_WRITE,
                Permission.CLUSTER_ADMIN, Permission.RESOURCE_ADMIN, Permission.REPORT_WRITE
            },
            TenantRole.TENANT_ADMIN: {
                Permission.TENANT_READ, Permission.USER_ADMIN, Permission.USER_WRITE,
                Permission.CLUSTER_ADMIN, Permission.RESOURCE_ADMIN, Permission.REPORT_WRITE,
                Permission.OPTIMIZATION_EXECUTE, Permission.ANALYSIS_WRITE
            },
            TenantRole.OPERATOR: {
                Permission.CLUSTER_READ, Permission.CLUSTER_WRITE, Permission.RESOURCE_READ,
                Permission.RESOURCE_WRITE, Permission.OPTIMIZATION_READ, Permission.OPTIMIZATION_EXECUTE,
                Permission.ANALYSIS_READ, Permission.ANALYSIS_WRITE, Permission.REPORT_READ
            },
            TenantRole.VIEWER: {
                Permission.CLUSTER_READ, Permission.RESOURCE_READ, Permission.ANALYSIS_READ,
                Permission.REPORT_READ, Permission.OPTIMIZATION_READ
            },
            TenantRole.GUEST: {
                Permission.CLUSTER_READ, Permission.RESOURCE_READ
            }
        }
        
        logger.info("🔧 Initializing multi-tenant auth manager")
    
    async def initialize(self) -> bool:
        """Initialize multi-tenant auth manager"""
        try:
            logger.info("🚀 Initializing multi-tenant auth manager...")
            
            # Setup default tenant and admin user
            await self._setup_default_tenant()
            await self._setup_default_admin()
            
            # Load existing data if available
            await self._load_persistent_data()
            
            logger.info("✅ Multi-tenant auth manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize multi-tenant auth manager: {e}")
            return False
    
    async def _setup_default_tenant(self):
        """Setup default tenant for demonstration"""
        default_tenant = Tenant(
            tenant_id="default",
            name="Default Organization",
            description="Default tenant for UPID CLI",
            settings={
                "max_clusters": 10,
                "max_users": 50,
                "features": ["analysis", "optimization", "reporting"]
            }
        )
        
        self.tenants["default"] = default_tenant
        logger.info("✅ Default tenant created")
    
    async def _setup_default_admin(self):
        """Setup default admin user"""
        admin_user = User(
            user_id="admin",
            email="admin@upid.io",
            tenant_id="default",
            roles=[TenantRole.SUPER_ADMIN],
            permissions=list(self.role_permissions[TenantRole.SUPER_ADMIN])
        )
        
        self.users["admin"] = admin_user
        logger.info("✅ Default admin user created")
    
    async def _load_persistent_data(self):
        """Load persistent data from storage"""
        try:
            # Load tenants
            tenants_file = Path("data/tenants.json")
            if tenants_file.exists():
                with open(tenants_file, 'r') as f:
                    tenants_data = json.load(f)
                    for tenant_data in tenants_data:
                        tenant = Tenant(**tenant_data)
                        self.tenants[tenant.tenant_id] = tenant
            
            # Load users
            users_file = Path("data/users.json")
            if users_file.exists():
                with open(users_file, 'r') as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = User(**user_data)
                        self.users[user.user_id] = user
            
            logger.info("✅ Persistent data loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load persistent data: {e}")
    
    async def create_tenant(self, 
                          tenant_id: str,
                          name: str,
                          description: Optional[str] = None,
                          settings: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new tenant"""
        try:
            logger.info(f"🏢 Creating tenant: {tenant_id}")
            
            if tenant_id in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} already exists")
                return False
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                description=description,
                settings=settings or {}
            )
            
            self.tenants[tenant_id] = tenant
            
            # Log audit event
            await self._log_audit_event(
                tenant_id="system",
                user_id="system",
                event_type="tenant_created",
                action="create",
                details={"tenant_id": tenant_id, "name": name}
            )
            
            logger.info(f"✅ Tenant {tenant_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tenant {tenant_id}: {e}")
            return False
    
    async def create_user(self,
                         user_id: str,
                         email: str,
                         tenant_id: str,
                         roles: List[TenantRole] = None,
                         permissions: List[Permission] = None) -> bool:
        """Create a new user in a tenant"""
        try:
            logger.info(f"👤 Creating user: {user_id} in tenant: {tenant_id}")
            
            # Validate tenant exists
            if tenant_id not in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} does not exist")
                return False
            
            if user_id in self.users:
                logger.error(f"❌ User {user_id} already exists")
                return False
            
            # Set default roles and permissions
            if roles is None:
                roles = [TenantRole.VIEWER]
            
            if permissions is None:
                permissions = list(self.role_permissions[TenantRole.VIEWER])
            
            user = User(
                user_id=user_id,
                email=email,
                tenant_id=tenant_id,
                roles=roles,
                permissions=permissions
            )
            
            self.users[user_id] = user
            
            # Log audit event
            await self._log_audit_event(
                tenant_id=tenant_id,
                user_id="system",
                event_type="user_created",
                action="create",
                details={"user_id": user_id, "email": email, "roles": [r.value for r in roles]}
            )
            
            logger.info(f"✅ User {user_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create user {user_id}: {e}")
            return False
    
    async def check_permission(self,
                             user_id: str,
                             permission: Permission,
                             resource_type: Optional[ResourceType] = None,
                             resource_id: Optional[str] = None) -> bool:
        """Check if user has permission for specific resource"""
        try:
            # Get user
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return False
            
            # Check if user has permission directly
            if permission in user.permissions:
                return True
            
            # Check resource-specific permissions
            if resource_type and resource_id:
                resource_key = f"{resource_type.value}:{resource_id}"
                resource_perm = self.resource_permissions.get(resource_key)
                
                if resource_perm and user_id in resource_perm.granted_to:
                    if permission in resource_perm.permissions:
                        return True
            
            # Check role-based permissions
            for role in user.roles:
                role_perms = self.role_permissions.get(role, set())
                if permission in role_perms:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking permission: {e}")
            return False
    
    async def grant_permission(self,
                             user_id: str,
                             permission: Permission,
                             granted_by: str,
                             resource_type: Optional[ResourceType] = None,
                             resource_id: Optional[str] = None,
                             expires_at: Optional[datetime] = None) -> bool:
        """Grant permission to user"""
        try:
            logger.info(f"🔐 Granting permission {permission.value} to user {user_id}")
            
            # Validate grantor permissions
            if not await self.check_permission(granted_by, Permission.USER_ADMIN):
                logger.error(f"❌ User {granted_by} cannot grant permissions")
                return False
            
            # Get user
            user = self.users.get(user_id)
            if not user:
                logger.error(f"❌ User {user_id} does not exist")
                return False
            
            # Grant permission
            if permission not in user.permissions:
                user.permissions.append(permission)
                user.updated_at = datetime.utcnow()
            
            # Create resource-specific permission if needed
            if resource_type and resource_id:
                resource_key = f"{resource_type.value}:{resource_id}"
                resource_perm = ResourcePermission(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    tenant_id=user.tenant_id,
                    permissions=[permission],
                    granted_to=[user_id],
                    granted_by=granted_by,
                    expires_at=expires_at
                )
                self.resource_permissions[resource_key] = resource_perm
            
            # Log audit event
            await self._log_audit_event(
                tenant_id=user.tenant_id,
                user_id=granted_by,
                event_type="permission_granted",
                action="grant",
                details={
                    "target_user": user_id,
                    "permission": permission.value,
                    "resource_type": resource_type.value if resource_type else None,
                    "resource_id": resource_id
                }
            )
            
            logger.info(f"✅ Permission {permission.value} granted to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to grant permission: {e}")
            return False
    
    async def revoke_permission(self,
                              user_id: str,
                              permission: Permission,
                              revoked_by: str,
                              resource_type: Optional[ResourceType] = None,
                              resource_id: Optional[str] = None) -> bool:
        """Revoke permission from user"""
        try:
            logger.info(f"🔐 Revoking permission {permission.value} from user {user_id}")
            
            # Validate revoker permissions
            if not await self.check_permission(revoked_by, Permission.USER_ADMIN):
                logger.error(f"❌ User {revoked_by} cannot revoke permissions")
                return False
            
            # Get user
            user = self.users.get(user_id)
            if not user:
                logger.error(f"❌ User {user_id} does not exist")
                return False
            
            # Revoke permission
            if permission in user.permissions:
                user.permissions.remove(permission)
                user.updated_at = datetime.utcnow()
            
            # Remove resource-specific permission if needed
            if resource_type and resource_id:
                resource_key = f"{resource_type.value}:{resource_id}"
                if resource_key in self.resource_permissions:
                    resource_perm = self.resource_permissions[resource_key]
                    if user_id in resource_perm.granted_to:
                        resource_perm.granted_to.remove(user_id)
                        if permission in resource_perm.permissions:
                            resource_perm.permissions.remove(permission)
            
            # Log audit event
            await self._log_audit_event(
                tenant_id=user.tenant_id,
                user_id=revoked_by,
                event_type="permission_revoked",
                action="revoke",
                details={
                    "target_user": user_id,
                    "permission": permission.value,
                    "resource_type": resource_type.value if resource_type else None,
                    "resource_id": resource_id
                }
            )
            
            logger.info(f"✅ Permission {permission.value} revoked from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to revoke permission: {e}")
            return False
    
    async def get_user_permissions(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user permissions and roles"""
        try:
            user = self.users.get(user_id)
            if not user:
                return None
            
            return {
                "user_id": user.user_id,
                "email": user.email,
                "tenant_id": user.tenant_id,
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions],
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user permissions: {e}")
            return None
    
    async def get_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all users in a tenant"""
        try:
            if tenant_id not in self.tenants:
                return []
            
            tenant_users = []
            for user in self.users.values():
                if user.tenant_id == tenant_id:
                    tenant_users.append({
                        "user_id": user.user_id,
                        "email": user.email,
                        "roles": [role.value for role in user.roles],
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat() if user.last_login else None
                    })
            
            return tenant_users
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant users: {e}")
            return []
    
    async def _log_audit_event(self,
                              tenant_id: str,
                              user_id: str,
                              event_type: str,
                              action: str,
                              details: Dict[str, Any],
                              resource_type: Optional[ResourceType] = None,
                              resource_id: Optional[str] = None) -> None:
        """Log audit event"""
        try:
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                details=details
            )
            
            self.audit_events.append(event)
            
            # Keep only last 1000 events
            if len(self.audit_events) > 1000:
                self.audit_events = self.audit_events[-1000:]
                
        except Exception as e:
            logger.error(f"❌ Failed to log audit event: {e}")
    
    async def get_audit_log(self,
                           tenant_id: Optional[str] = None,
                           user_id: Optional[str] = None,
                           event_type: Optional[str] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log with filters"""
        try:
            filtered_events = []
            
            for event in reversed(self.audit_events):
                # Apply filters
                if tenant_id and event.tenant_id != tenant_id:
                    continue
                if user_id and event.user_id != user_id:
                    continue
                if event_type and event.event_type != event_type:
                    continue
                
                filtered_events.append({
                    "event_id": event.event_id,
                    "tenant_id": event.tenant_id,
                    "user_id": event.user_id,
                    "event_type": event.event_type,
                    "resource_type": event.resource_type.value if event.resource_type else None,
                    "resource_id": event.resource_id,
                    "action": event.action,
                    "details": event.details,
                    "timestamp": event.timestamp.isoformat(),
                    "ip_address": event.ip_address,
                    "user_agent": event.user_agent
                })
                
                if len(filtered_events) >= limit:
                    break
            
            return filtered_events
            
        except Exception as e:
            logger.error(f"❌ Error getting audit log: {e}")
            return []
    
    async def create_session(self, user_id: str, tenant_id: str) -> Optional[str]:
        """Create user session"""
        try:
            user = self.users.get(user_id)
            if not user or user.tenant_id != tenant_id:
                return None
            
            session_id = str(uuid.uuid4())
            session_data = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            self.sessions[session_id] = session_data
            
            # Update user last login
            user.last_login = datetime.utcnow()
            
            # Log audit event
            await self._log_audit_event(
                tenant_id=tenant_id,
                user_id=user_id,
                event_type="session_created",
                action="login",
                details={"session_id": session_id}
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            return None
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user info"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            # Check if session expired
            if session["expires_at"] < datetime.utcnow():
                del self.sessions[session_id]
                return None
            
            # Get user info
            user = self.users.get(session["user_id"])
            if not user or not user.is_active:
                return None
            
            return {
                "user_id": user.user_id,
                "email": user.email,
                "tenant_id": user.tenant_id,
                "roles": [role.value for role in user.roles],
                "permissions": [perm.value for perm in user.permissions]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to validate session: {e}")
            return None
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Log audit event
                await self._log_audit_event(
                    tenant_id=session["tenant_id"],
                    user_id=session["user_id"],
                    event_type="session_invalidated",
                    action="logout",
                    details={"session_id": session_id}
                )
                
                del self.sessions[session_id]
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to invalidate session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            expired_count = 0
            current_time = datetime.utcnow()
            
            session_ids = list(self.sessions.keys())
            for session_id in session_ids:
                session = self.sessions[session_id]
                if session["expires_at"] < current_time:
                    del self.sessions[session_id]
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"🧹 Cleaned up {expired_count} expired sessions")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup sessions: {e}")
            return 0
    
    async def get_tenant_summary(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant summary with user and permission statistics"""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                return None
            
            # Count users by role
            role_counts = {}
            active_users = 0
            total_users = 0
            
            for user in self.users.values():
                if user.tenant_id == tenant_id:
                    total_users += 1
                    if user.is_active:
                        active_users += 1
                    
                    for role in user.roles:
                        role_counts[role.value] = role_counts.get(role.value, 0) + 1
            
            # Count resource permissions
            resource_permission_counts = {}
            for perm in self.resource_permissions.values():
                if perm.tenant_id == tenant_id:
                    resource_type = perm.resource_type.value
                    resource_permission_counts[resource_type] = resource_permission_counts.get(resource_type, 0) + 1
            
            return {
                "tenant_id": tenant.tenant_id,
                "name": tenant.name,
                "description": tenant.description,
                "created_at": tenant.created_at.isoformat(),
                "is_active": tenant.is_active,
                "settings": tenant.settings,
                "statistics": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "role_distribution": role_counts,
                    "resource_permissions": resource_permission_counts
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting tenant summary: {e}")
            return None 