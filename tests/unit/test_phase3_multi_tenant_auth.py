"""
Unit tests for Phase 3: Multi-tenant Authentication & RBAC
Tests multi-tenant authentication, role-based access control, and audit logging
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the modules to test
from upid.core.multi_tenant_auth import (
    MultiTenantAuthManager,
    TenantRole,
    Permission,
    ResourceType,
    Tenant,
    User,
    ResourcePermission,
    AuditEvent
)


class TestMultiTenantAuthManager:
    """Test multi-tenant authentication manager functionality"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create multi-tenant auth manager instance"""
        config = {
            "session_timeout_hours": 24,
            "max_audit_events": 1000,
            "default_tenant": "default"
        }
        return MultiTenantAuthManager(config)
    
    @pytest.fixture
    def sample_tenant(self):
        """Create sample tenant"""
        return Tenant(
            tenant_id="test-tenant",
            name="Test Organization",
            description="Test tenant for unit tests"
        )
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user"""
        return User(
            user_id="test-user",
            email="test@example.com",
            tenant_id="test-tenant",
            roles=[TenantRole.OPERATOR],
            permissions=[Permission.CLUSTER_READ, Permission.RESOURCE_READ]
        )
    
    @pytest.mark.asyncio
    async def test_initialize_auth_manager(self, auth_manager):
        """Test auth manager initialization"""
        # Test initialization
        result = await auth_manager.initialize()
        assert result is True
        
        # Verify default tenant created
        assert "default" in auth_manager.tenants
        assert auth_manager.tenants["default"].name == "Default Organization"
        
        # Verify default admin user created
        assert "admin" in auth_manager.users
        assert auth_manager.users["admin"].email == "admin@upid.io"
        assert TenantRole.SUPER_ADMIN in auth_manager.users["admin"].roles
    
    @pytest.mark.asyncio
    async def test_create_tenant(self, auth_manager):
        """Test tenant creation"""
        await auth_manager.initialize()
        
        # Create new tenant
        result = await auth_manager.create_tenant(
            tenant_id="new-tenant",
            name="New Organization",
            description="New tenant for testing"
        )
        
        assert result is True
        assert "new-tenant" in auth_manager.tenants
        assert auth_manager.tenants["new-tenant"].name == "New Organization"
        
        # Test duplicate tenant creation
        result = await auth_manager.create_tenant(
            tenant_id="new-tenant",
            name="Duplicate Organization"
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_create_user(self, auth_manager):
        """Test user creation"""
        await auth_manager.initialize()
        
        # Create new user
        result = await auth_manager.create_user(
            user_id="new-user",
            email="newuser@example.com",
            tenant_id="default",
            roles=[TenantRole.OPERATOR]
        )
        
        assert result is True
        assert "new-user" in auth_manager.users
        assert auth_manager.users["new-user"].email == "newuser@example.com"
        assert auth_manager.users["new-user"].tenant_id == "default"
        
        # Test creating user in non-existent tenant
        result = await auth_manager.create_user(
            user_id="invalid-user",
            email="invalid@example.com",
            tenant_id="non-existent-tenant"
        )
        assert result is False
        
        # Test duplicate user creation
        result = await auth_manager.create_user(
            user_id="new-user",
            email="duplicate@example.com",
            tenant_id="default"
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_permission(self, auth_manager):
        """Test permission checking"""
        await auth_manager.initialize()
        
        # Create test user with specific permissions
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default",
            roles=[TenantRole.OPERATOR]
        )
        
        # Test role-based permissions
        has_cluster_read = await auth_manager.check_permission(
            "test-user", Permission.CLUSTER_READ
        )
        assert has_cluster_read is True
        
        # Test permission user doesn't have
        has_admin = await auth_manager.check_permission(
            "test-user", Permission.TENANT_ADMIN
        )
        assert has_admin is False
        
        # Test with non-existent user
        has_permission = await auth_manager.check_permission(
            "non-existent-user", Permission.CLUSTER_READ
        )
        assert has_permission is False
    
    @pytest.mark.asyncio
    async def test_grant_permission(self, auth_manager):
        """Test permission granting"""
        await auth_manager.initialize()
        
        # Create test user
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default",
            roles=[TenantRole.VIEWER]
        )
        
        # Grant permission using admin
        result = await auth_manager.grant_permission(
            user_id="test-user",
            permission=Permission.CLUSTER_WRITE,
            granted_by="admin"
        )
        
        assert result is True
        
        # Verify permission was granted
        has_permission = await auth_manager.check_permission(
            "test-user", Permission.CLUSTER_WRITE
        )
        assert has_permission is True
        
        # Test granting permission without admin rights
        result = await auth_manager.grant_permission(
            user_id="test-user",
            permission=Permission.RESOURCE_WRITE,
            granted_by="test-user"  # Non-admin user
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_revoke_permission(self, auth_manager):
        """Test permission revocation"""
        await auth_manager.initialize()
        
        # Create test user with permission
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default",
            roles=[TenantRole.OPERATOR]
        )
        
        # Grant additional permission
        await auth_manager.grant_permission(
            user_id="test-user",
            permission=Permission.CLUSTER_WRITE,
            granted_by="admin"
        )
        
        # Revoke permission
        result = await auth_manager.revoke_permission(
            user_id="test-user",
            permission=Permission.CLUSTER_WRITE,
            revoked_by="admin"
        )
        
        assert result is True
        
        # Verify permission was revoked
        has_permission = await auth_manager.check_permission(
            "test-user", Permission.CLUSTER_WRITE
        )
        assert has_permission is False
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self, auth_manager):
        """Test getting user permissions"""
        await auth_manager.initialize()
        
        # Create test user
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default",
            roles=[TenantRole.OPERATOR]
        )
        
        # Get user permissions
        permissions = await auth_manager.get_user_permissions("test-user")
        
        assert permissions is not None
        assert permissions["user_id"] == "test-user"
        assert permissions["email"] == "test@example.com"
        assert permissions["tenant_id"] == "default"
        assert TenantRole.OPERATOR.value in permissions["roles"]
        assert Permission.CLUSTER_READ.value in permissions["permissions"]
        
        # Test non-existent user
        permissions = await auth_manager.get_user_permissions("non-existent-user")
        assert permissions is None
    
    @pytest.mark.asyncio
    async def test_get_tenant_users(self, auth_manager):
        """Test getting tenant users"""
        await auth_manager.initialize()
        
        # Create multiple users in default tenant
        await auth_manager.create_user(
            user_id="user1",
            email="user1@example.com",
            tenant_id="default",
            roles=[TenantRole.VIEWER]
        )
        
        await auth_manager.create_user(
            user_id="user2",
            email="user2@example.com",
            tenant_id="default",
            roles=[TenantRole.OPERATOR]
        )
        
        # Get tenant users
        users = await auth_manager.get_tenant_users("default")
        
        assert len(users) >= 3  # admin + user1 + user2
        user_ids = [user["user_id"] for user in users]
        assert "admin" in user_ids
        assert "user1" in user_ids
        assert "user2" in user_ids
        
        # Test non-existent tenant
        users = await auth_manager.get_tenant_users("non-existent-tenant")
        assert users == []
    
    @pytest.mark.asyncio
    async def test_session_management(self, auth_manager):
        """Test session creation and validation"""
        await auth_manager.initialize()
        
        # Create test user
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default"
        )
        
        # Create session
        session_id = await auth_manager.create_session("test-user", "default")
        assert session_id is not None
        
        # Validate session
        session_info = await auth_manager.validate_session(session_id)
        assert session_info is not None
        assert session_info["user_id"] == "test-user"
        assert session_info["tenant_id"] == "default"
        
        # Invalidate session
        result = await auth_manager.invalidate_session(session_id)
        assert result is True
        
        # Verify session is invalid
        session_info = await auth_manager.validate_session(session_id)
        assert session_info is None
    
    @pytest.mark.asyncio
    async def test_audit_logging(self, auth_manager):
        """Test audit event logging"""
        await auth_manager.initialize()
        
        # Create test user
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default"
        )
        
        # Perform action that generates audit event
        await auth_manager.grant_permission(
            user_id="test-user",
            permission=Permission.CLUSTER_WRITE,
            granted_by="admin"
        )
        
        # Get audit log
        audit_events = await auth_manager.get_audit_log(
            tenant_id="default",
            event_type="permission_granted"
        )
        
        assert len(audit_events) > 0
        assert audit_events[0]["event_type"] == "permission_granted"
        assert audit_events[0]["user_id"] == "admin"
        assert audit_events[0]["details"]["target_user"] == "test-user"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, auth_manager):
        """Test session cleanup"""
        await auth_manager.initialize()
        
        # Create test user
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default"
        )
        
        # Create session
        session_id = await auth_manager.create_session("test-user", "default")
        
        # Manually expire session
        auth_manager.sessions[session_id]["expires_at"] = datetime.utcnow() - timedelta(hours=1)
        
        # Cleanup expired sessions
        expired_count = await auth_manager.cleanup_expired_sessions()
        
        assert expired_count == 1
        
        # Verify session was removed
        session_info = await auth_manager.validate_session(session_id)
        assert session_info is None
    
    @pytest.mark.asyncio
    async def test_get_tenant_summary(self, auth_manager):
        """Test tenant summary generation"""
        await auth_manager.initialize()
        
        # Create additional users in default tenant
        await auth_manager.create_user(
            user_id="user1",
            email="user1@example.com",
            tenant_id="default",
            roles=[TenantRole.VIEWER]
        )
        
        await auth_manager.create_user(
            user_id="user2",
            email="user2@example.com",
            tenant_id="default",
            roles=[TenantRole.OPERATOR]
        )
        
        # Get tenant summary
        summary = await auth_manager.get_tenant_summary("default")
        
        assert summary is not None
        assert summary["tenant_id"] == "default"
        assert summary["name"] == "Default Organization"
        assert summary["statistics"]["total_users"] >= 3  # admin + user1 + user2
        assert summary["statistics"]["active_users"] >= 3
        
        # Test non-existent tenant
        summary = await auth_manager.get_tenant_summary("non-existent-tenant")
        assert summary is None
    
    @pytest.mark.asyncio
    async def test_resource_specific_permissions(self, auth_manager):
        """Test resource-specific permission management"""
        await auth_manager.initialize()
        
        # Create test user
        await auth_manager.create_user(
            user_id="test-user",
            email="test@example.com",
            tenant_id="default",
            roles=[TenantRole.VIEWER]
        )
        
        # Grant resource-specific permission
        result = await auth_manager.grant_permission(
            user_id="test-user",
            permission=Permission.RESOURCE_WRITE,
            granted_by="admin",
            resource_type=ResourceType.CLUSTER,
            resource_id="cluster-1"
        )
        
        assert result is True
        
        # Check permission for specific resource
        has_permission = await auth_manager.check_permission(
            "test-user",
            Permission.RESOURCE_WRITE,
            resource_type=ResourceType.CLUSTER,
            resource_id="cluster-1"
        )
        assert has_permission is True
        
        # Check permission for different resource
        has_permission = await auth_manager.check_permission(
            "test-user",
            Permission.RESOURCE_WRITE,
            resource_type=ResourceType.CLUSTER,
            resource_id="cluster-2"
        )
        assert has_permission is False
    
    @pytest.mark.asyncio
    async def test_role_hierarchy(self, auth_manager):
        """Test role-based permission hierarchy"""
        await auth_manager.initialize()
        
        # Test SUPER_ADMIN permissions
        super_admin_perms = auth_manager.role_permissions[TenantRole.SUPER_ADMIN]
        assert Permission.TENANT_ADMIN in super_admin_perms
        assert Permission.SYSTEM_ADMIN in super_admin_perms
        
        # Test TENANT_ADMIN permissions
        tenant_admin_perms = auth_manager.role_permissions[TenantRole.TENANT_ADMIN]
        assert Permission.USER_ADMIN in tenant_admin_perms
        assert Permission.CLUSTER_ADMIN in tenant_admin_perms
        
        # Test OPERATOR permissions
        operator_perms = auth_manager.role_permissions[TenantRole.OPERATOR]
        assert Permission.CLUSTER_READ in operator_perms
        assert Permission.OPTIMIZATION_EXECUTE in operator_perms
        
        # Test VIEWER permissions
        viewer_perms = auth_manager.role_permissions[TenantRole.VIEWER]
        assert Permission.CLUSTER_READ in viewer_perms
        assert Permission.REPORT_READ in viewer_perms
        
        # Test GUEST permissions
        guest_perms = auth_manager.role_permissions[TenantRole.GUEST]
        assert Permission.CLUSTER_READ in guest_perms
        assert len(guest_perms) < len(viewer_perms)  # Fewer permissions than viewer


class TestTenant:
    """Test Tenant data structure"""
    
    def test_tenant_creation(self):
        """Test tenant creation"""
        tenant = Tenant(
            tenant_id="test-tenant",
            name="Test Organization",
            description="Test tenant"
        )
        
        assert tenant.tenant_id == "test-tenant"
        assert tenant.name == "Test Organization"
        assert tenant.description == "Test tenant"
        assert tenant.is_active is True
        assert tenant.max_users == 100
        assert tenant.max_clusters == 50


class TestUser:
    """Test User data structure"""
    
    def test_user_creation(self):
        """Test user creation"""
        user = User(
            user_id="test-user",
            email="test@example.com",
            tenant_id="test-tenant",
            roles=[TenantRole.OPERATOR],
            permissions=[Permission.CLUSTER_READ]
        )
        
        assert user.user_id == "test-user"
        assert user.email == "test@example.com"
        assert user.tenant_id == "test-tenant"
        assert TenantRole.OPERATOR in user.roles
        assert Permission.CLUSTER_READ in user.permissions
        assert user.is_active is True
    
    def test_user_permission_checking(self):
        """Test user permission checking"""
        user = User(
            user_id="test-user",
            email="test@example.com",
            tenant_id="test-tenant",
            permissions=[Permission.CLUSTER_READ, Permission.RESOURCE_READ]
        )
        
        assert user.has_permission(Permission.CLUSTER_READ) is True
        assert user.has_permission(Permission.CLUSTER_WRITE) is False
        assert user.has_role(TenantRole.VIEWER) is False
        assert user.is_admin() is False
    
    def test_admin_user(self):
        """Test admin user functionality"""
        admin_user = User(
            user_id="admin",
            email="admin@example.com",
            tenant_id="test-tenant",
            roles=[TenantRole.TENANT_ADMIN]
        )
        
        assert admin_user.is_admin() is True
        
        super_admin = User(
            user_id="super-admin",
            email="super@example.com",
            tenant_id="test-tenant",
            roles=[TenantRole.SUPER_ADMIN]
        )
        
        assert super_admin.is_admin() is True


class TestResourcePermission:
    """Test ResourcePermission data structure"""
    
    def test_resource_permission_creation(self):
        """Test resource permission creation"""
        resource_perm = ResourcePermission(
            resource_type=ResourceType.CLUSTER,
            resource_id="cluster-1",
            tenant_id="test-tenant",
            permissions=[Permission.CLUSTER_READ, Permission.CLUSTER_WRITE],
            granted_to=["user1", "user2"],
            granted_by="admin"
        )
        
        assert resource_perm.resource_type == ResourceType.CLUSTER
        assert resource_perm.resource_id == "cluster-1"
        assert resource_perm.tenant_id == "test-tenant"
        assert Permission.CLUSTER_READ in resource_perm.permissions
        assert "user1" in resource_perm.granted_to
        assert resource_perm.granted_by == "admin"


class TestAuditEvent:
    """Test AuditEvent data structure"""
    
    def test_audit_event_creation(self):
        """Test audit event creation"""
        event = AuditEvent(
            event_id="event-1",
            tenant_id="test-tenant",
            user_id="test-user",
            event_type="permission_granted",
            resource_type=ResourceType.CLUSTER,
            resource_id="cluster-1",
            action="grant",
            details={"permission": "cluster:write"}
        )
        
        assert event.event_id == "event-1"
        assert event.tenant_id == "test-tenant"
        assert event.user_id == "test-user"
        assert event.event_type == "permission_granted"
        assert event.resource_type == ResourceType.CLUSTER
        assert event.resource_id == "cluster-1"
        assert event.action == "grant"
        assert event.details["permission"] == "cluster:write"


class TestPermissionEnums:
    """Test Permission and ResourceType enums"""
    
    def test_permission_values(self):
        """Test permission enum values"""
        assert Permission.CLUSTER_READ.value == "cluster:read"
        assert Permission.CLUSTER_WRITE.value == "cluster:write"
        assert Permission.OPTIMIZATION_EXECUTE.value == "optimization:execute"
        assert Permission.REPORT_EXPORT.value == "report:export"
    
    def test_resource_type_values(self):
        """Test resource type enum values"""
        assert ResourceType.CLUSTER.value == "cluster"
        assert ResourceType.NAMESPACE.value == "namespace"
        assert ResourceType.DEPLOYMENT.value == "deployment"
        assert ResourceType.POD.value == "pod"
    
    def test_tenant_role_values(self):
        """Test tenant role enum values"""
        assert TenantRole.SUPER_ADMIN.value == "super_admin"
        assert TenantRole.TENANT_ADMIN.value == "tenant_admin"
        assert TenantRole.OPERATOR.value == "operator"
        assert TenantRole.VIEWER.value == "viewer"
        assert TenantRole.GUEST.value == "guest" 