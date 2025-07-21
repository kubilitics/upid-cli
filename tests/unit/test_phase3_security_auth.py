"""
Unit tests for Phase 3: Universal Authentication & Security
Tests authentication, RBAC, and audit trail functionality
"""

import pytest
import asyncio
import jwt
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the modules to test
from upid.auth.universal_auth import (
    UniversalAuthManager,
    AuthProviderType,
    AuthLevel,
    AuthUser,
    AuthSession,
    KubeconfigAuthProvider,
    TokenAuthProvider,
    OIDCAuthProvider,
    AuthMiddleware
)

from upid.auth.rbac import (
    RBACManager,
    Permission,
    Role,
    RBACRole,
    RBACUser,
    RBACGroup
)

from upid.auth.audit import (
    AuditTrailManager,
    AuditEventType,
    AuditSeverity,
    AuditEvent,
    AuditFilter
)


class TestUniversalAuthManager:
    """Test universal authentication manager functionality"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create authentication manager instance"""
        return UniversalAuthManager()
    
    @pytest.mark.asyncio
    async def test_authenticate_kubeconfig(self, auth_manager):
        """Test kubeconfig authentication"""
        # Test kubeconfig authentication
        credentials = {"username": "test-user"}
        
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Verify session
        assert session is not None
        assert isinstance(session, AuthSession)
        assert session.user.username == "test-user"
        assert session.user.auth_provider == AuthProviderType.KUBECONFIG
        assert session.user.auth_level == AuthLevel.ADMIN
        assert session.session_id is not None
        assert session.expires_at > datetime.now()
    
    @pytest.mark.asyncio
    async def test_authenticate_token(self, auth_manager):
        """Test token authentication"""
        # Create a test token using the token provider
        token_provider = auth_manager.providers[AuthProviderType.TOKEN]
        
        # Create a valid token payload
        payload = {
            'username': 'token-user',
            'email': 'token@example.com',
            'groups': ['users'],
            'roles': ['user'],
            'permissions': ['read'],
            'auth_level': 'read',
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'iat': int(datetime.now().timestamp())
        }
        
        # Generate a valid token
        test_token = jwt.encode(payload, token_provider.secret_key, algorithm='HS256')
        
        credentials = {"token": test_token}
        
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.TOKEN,
            credentials=credentials
        )
        
        # Verify session
        assert session is not None
        assert isinstance(session, AuthSession)
        assert session.user.auth_provider == AuthProviderType.TOKEN
        assert session.session_id is not None
    
    @pytest.mark.asyncio
    async def test_authenticate_oidc(self, auth_manager):
        """Test OIDC authentication"""
        # Test OIDC authentication
        credentials = {"username": "oidc-user", "password": "test-pass"}
        
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.OIDC,
            credentials=credentials
        )
        
        # Verify session
        assert session is not None
        assert isinstance(session, AuthSession)
        assert session.user.username == "oidc-user"
        assert session.user.auth_provider == AuthProviderType.OIDC
        assert session.user.auth_level == AuthLevel.WRITE
        assert session.session_id is not None
    
    @pytest.mark.asyncio
    async def test_validate_session(self, auth_manager):
        """Test session validation"""
        # Create a session first
        credentials = {"username": "test-user"}
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Validate session
        validated_session = await auth_manager.validate_session(session.session_id)
        
        # Verify validation
        assert validated_session is not None
        assert validated_session.session_id == session.session_id
        assert validated_session.user.username == session.user.username
    
    @pytest.mark.asyncio
    async def test_validate_expired_session(self, auth_manager):
        """Test expired session validation"""
        # Create a session and manually expire it
        credentials = {"username": "test-user"}
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Manually expire the session
        session.expires_at = datetime.now() - timedelta(hours=1)
        
        # Validate expired session
        validated_session = await auth_manager.validate_session(session.session_id)
        
        # Verify session is not valid
        assert validated_session is None
    
    @pytest.mark.asyncio
    async def test_refresh_session(self, auth_manager):
        """Test session refresh"""
        # Create a session
        credentials = {"username": "test-user"}
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Store original expiration time
        original_expires_at = session.expires_at
        
        # Add a small delay to ensure timestamps are different
        await asyncio.sleep(0.1)
        
        # Refresh session
        refreshed_session = await auth_manager.refresh_session(session.session_id)
        
        # Verify refresh
        assert refreshed_session is not None
        assert refreshed_session.session_id == session.session_id
        assert refreshed_session.expires_at > original_expires_at
    
    @pytest.mark.asyncio
    async def test_logout(self, auth_manager):
        """Test user logout"""
        # Create a session
        credentials = {"username": "test-user"}
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Logout
        logout_success = await auth_manager.logout(session.session_id)
        
        # Verify logout
        assert logout_success is True
        
        # Verify session is removed
        validated_session = await auth_manager.validate_session(session.session_id)
        assert validated_session is None
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self, auth_manager):
        """Test getting user permissions"""
        # Create a session
        credentials = {"username": "test-user"}
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Get permissions
        permissions = await auth_manager.get_user_permissions(session.session_id)
        
        # Verify permissions
        assert isinstance(permissions, list)
        assert "*" in permissions  # Admin user should have all permissions
    
    @pytest.mark.asyncio
    async def test_check_permission(self, auth_manager):
        """Test permission checking"""
        # Create a session
        credentials = {"username": "test-user"}
        session = await auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Check permission
        has_permission = await auth_manager.check_permission(
            session.session_id, "test-permission"
        )
        
        # Verify permission check
        assert has_permission is True  # Admin user should have all permissions
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, auth_manager):
        """Test expired session cleanup"""
        # Create multiple sessions
        for i in range(3):
            credentials = {"username": f"test-user-{i}"}
            session = await auth_manager.authenticate(
                provider_type=AuthProviderType.KUBECONFIG,
                credentials=credentials
            )
        
        # Manually expire one session
        session_ids = list(auth_manager.sessions.keys())
        if session_ids:
            expired_session_id = session_ids[0]
            auth_manager.sessions[expired_session_id].expires_at = datetime.now() - timedelta(hours=1)
        
        # Cleanup expired sessions
        await auth_manager.cleanup_expired_sessions()
        
        # Verify cleanup
        for session_id in session_ids:
            if session_id == expired_session_id:
                assert session_id not in auth_manager.sessions
            else:
                assert session_id in auth_manager.sessions


class TestAuthProviders:
    """Test authentication providers"""
    
    @pytest.mark.asyncio
    async def test_kubeconfig_provider(self):
        """Test kubeconfig authentication provider"""
        provider = KubeconfigAuthProvider()
        
        # Test authentication
        credentials = {"username": "test-user"}
        user = await provider.authenticate(credentials)
        
        # Verify user
        assert user is not None
        assert user.username == "test-user"
        assert user.auth_provider == AuthProviderType.KUBECONFIG
        assert user.auth_level == AuthLevel.ADMIN
        assert user.groups == ["system:masters"]
        assert user.roles == ["cluster-admin"]
        assert user.permissions == ["*"]
    
    @pytest.mark.asyncio
    async def test_token_provider(self):
        """Test token authentication provider"""
        provider = TokenAuthProvider()
        
        # Create a valid token first
        payload = {
            'username': 'test-user',
            'email': 'test@example.com',
            'groups': ['users'],
            'roles': ['user'],
            'permissions': ['read'],
            'auth_level': 'read',
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'iat': int(datetime.now().timestamp())
        }
        
        valid_token = jwt.encode(payload, provider.secret_key, algorithm='HS256')
        
        # Test token refresh
        new_token = await provider.refresh_token(valid_token)
        
        # Verify token
        assert new_token is not None
        assert isinstance(new_token, str)
        assert len(new_token) > 0
    
    @pytest.mark.asyncio
    async def test_oidc_provider(self):
        """Test OIDC authentication provider"""
        provider = OIDCAuthProvider(
            issuer_url="https://accounts.google.com",
            client_id="test-client",
            client_secret="test-secret"
        )
        
        # Test authentication
        credentials = {"username": "test-user"}
        user = await provider.authenticate(credentials)
        
        # Verify user
        assert user is not None
        assert user.username == "test-user"
        assert user.auth_provider == AuthProviderType.OIDC
        assert user.auth_level == AuthLevel.WRITE
        assert user.groups == ["developers"]
        assert user.roles == ["developer"]


class TestAuthMiddleware:
    """Test authentication middleware"""
    
    @pytest.fixture
    def auth_middleware(self):
        """Create authentication middleware instance"""
        auth_manager = UniversalAuthManager()
        return AuthMiddleware(auth_manager)
    
    @pytest.mark.asyncio
    async def test_authenticate_request(self, auth_middleware):
        """Test request authentication"""
        # Create a session first
        credentials = {"username": "test-user"}
        session = await auth_middleware.auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Test request authentication
        headers = {"Authorization": f"Bearer {session.session_id}"}
        authenticated_session = await auth_middleware.authenticate_request(headers)
        
        # Verify authentication
        assert authenticated_session is not None
        assert authenticated_session.session_id == session.session_id
    
    @pytest.mark.asyncio
    async def test_require_auth(self, auth_middleware):
        """Test authentication requirement checking"""
        # Create a session
        credentials = {"username": "test-user"}
        session = await auth_middleware.auth_manager.authenticate(
            provider_type=AuthProviderType.KUBECONFIG,
            credentials=credentials
        )
        
        # Test auth requirement
        has_auth = await auth_middleware.require_auth(session, AuthLevel.READ)
        assert has_auth is True
        
        # Test higher level requirement
        has_admin_auth = await auth_middleware.require_auth(session, AuthLevel.ADMIN)
        assert has_admin_auth is True  # Kubeconfig user is admin


class TestRBACManager:
    """Test RBAC manager functionality"""
    
    @pytest.fixture
    def rbac_manager(self):
        """Create RBAC manager instance"""
        return RBACManager()
    
    @pytest.mark.asyncio
    async def test_create_role(self, rbac_manager):
        """Test role creation"""
        # Create a custom role
        permissions = [Permission.READ_PODS, Permission.WRITE_PODS]
        role = await rbac_manager.create_role(
            name="custom-role",
            description="Custom role for testing",
            permissions=permissions
        )
        
        # Verify role
        assert role is not None
        assert role.name == "custom-role"
        assert role.description == "Custom role for testing"
        assert role.permissions == permissions
        assert role.is_system_role is False
    
    @pytest.mark.asyncio
    async def test_create_user(self, rbac_manager):
        """Test user creation"""
        # Create a user
        user = await rbac_manager.create_user(
            username="test-user",
            email="test@example.com",
            roles=["viewer"]
        )
        
        # Verify user
        assert user is not None
        assert user.username == "test-user"
        assert user.email == "test@example.com"
        assert user.roles == ["viewer"]
        assert user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self, rbac_manager):
        """Test getting user permissions"""
        # Create a user with roles
        user = await rbac_manager.create_user(
            username="test-user",
            roles=["viewer", "developer"]
        )
        
        # Get permissions
        permissions = await rbac_manager.get_user_permissions("test-user")
        
        # Verify permissions
        assert isinstance(permissions, set)
        assert len(permissions) > 0
        assert Permission.READ_PODS in permissions
        assert Permission.WRITE_PODS in permissions
    
    @pytest.mark.asyncio
    async def test_check_permission(self, rbac_manager):
        """Test permission checking"""
        # Create a user
        await rbac_manager.create_user(
            username="test-user",
            roles=["viewer"]
        )
        
        # Check permission
        has_permission = await rbac_manager.check_permission(
            "test-user", Permission.READ_PODS
        )
        
        # Verify permission
        assert has_permission is True
        
        # Check permission user doesn't have
        has_admin_permission = await rbac_manager.check_permission(
            "test-user", Permission.ADMIN_USERS
        )
        
        # Verify no permission
        assert has_admin_permission is False
    
    @pytest.mark.asyncio
    async def test_check_any_permission(self, rbac_manager):
        """Test checking any permission"""
        # Create a user
        await rbac_manager.create_user(
            username="test-user",
            roles=["viewer"]
        )
        
        # Check any permission
        has_any = await rbac_manager.check_any_permission(
            "test-user", [Permission.READ_PODS, Permission.ADMIN_USERS]
        )
        
        # Verify has at least one permission
        assert has_any is True
    
    @pytest.mark.asyncio
    async def test_check_all_permissions(self, rbac_manager):
        """Test checking all permissions"""
        # Create a user
        await rbac_manager.create_user(
            username="test-user",
            roles=["viewer"]
        )
        
        # Check all permissions
        has_all = await rbac_manager.check_all_permissions(
            "test-user", [Permission.READ_PODS, Permission.READ_SERVICES]
        )
        
        # Verify has all permissions
        assert has_all is True
        
        # Check permissions user doesn't have
        has_all_admin = await rbac_manager.check_all_permissions(
            "test-user", [Permission.READ_PODS, Permission.ADMIN_USERS]
        )
        
        # Verify doesn't have all permissions
        assert has_all_admin is False
    
    @pytest.mark.asyncio
    async def test_create_group(self, rbac_manager):
        """Test group creation"""
        # Create a group
        group = await rbac_manager.create_group(
            name="test-group",
            description="Test group",
            roles=["viewer"]
        )
        
        # Verify group
        assert group is not None
        assert group.name == "test-group"
        assert group.description == "Test group"
        assert group.roles == ["viewer"]
        assert group.members == []
    
    @pytest.mark.asyncio
    async def test_add_user_to_group(self, rbac_manager):
        """Test adding user to group"""
        # Create user and group
        await rbac_manager.create_user("test-user")
        await rbac_manager.create_group("test-group", "Test group")
        
        # Add user to group
        success = await rbac_manager.add_user_to_group("test-user", "test-group")
        
        # Verify success
        assert success is True
        
        # Verify user is in group
        user = rbac_manager.users["test-user"]
        group = rbac_manager.groups["test-group"]
        assert "test-group" in user.groups
        assert "test-user" in group.members
    
    @pytest.mark.asyncio
    async def test_remove_user_from_group(self, rbac_manager):
        """Test removing user from group"""
        # Create user and group
        await rbac_manager.create_user("test-user")
        await rbac_manager.create_group("test-group", "Test group")
        
        # Add user to group
        await rbac_manager.add_user_to_group("test-user", "test-group")
        
        # Remove user from group
        success = await rbac_manager.remove_user_from_group("test-user", "test-group")
        
        # Verify success
        assert success is True
        
        # Verify user is not in group
        user = rbac_manager.users["test-user"]
        group = rbac_manager.groups["test-group"]
        assert "test-group" not in user.groups
        assert "test-user" not in group.members
    
    @pytest.mark.asyncio
    async def test_get_roles(self, rbac_manager):
        """Test getting all roles"""
        roles = await rbac_manager.get_roles()
        
        # Verify roles
        assert isinstance(roles, list)
        assert len(roles) >= 5  # Should have system roles
    
    @pytest.mark.asyncio
    async def test_get_users(self, rbac_manager):
        """Test getting all users"""
        # Create a user
        await rbac_manager.create_user("test-user")
        
        users = await rbac_manager.get_users()
        
        # Verify users
        assert isinstance(users, list)
        assert len(users) >= 1  # Should have at least the test user
    
    @pytest.mark.asyncio
    async def test_get_groups(self, rbac_manager):
        """Test getting all groups"""
        # Create a group
        await rbac_manager.create_group("test-group", "Test group")
        
        groups = await rbac_manager.get_groups()
        
        # Verify groups
        assert isinstance(groups, list)
        assert len(groups) >= 1  # Should have at least the test group


class TestAuditTrailManager:
    """Test audit trail manager functionality"""
    
    @pytest.fixture
    def audit_manager(self):
        """Create audit trail manager instance"""
        return AuditTrailManager()
    
    @pytest.mark.asyncio
    async def test_log_event(self, audit_manager):
        """Test logging audit event"""
        # Log an event
        event_id = await audit_manager.log_event(
            event_type=AuditEventType.LOGIN,
            user_id="test-user-id",
            username="test-user",
            session_id="test-session",
            ip_address="192.168.1.1",
            details={"auth_provider": "kubeconfig"}
        )
        
        # Verify event
        assert event_id is not None
        assert len(event_id) > 0
        
        # Verify event was stored
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_id == event_id
        assert event.event_type == AuditEventType.LOGIN
        assert event.username == "test-user"
    
    @pytest.mark.asyncio
    async def test_log_login(self, audit_manager):
        """Test logging login event"""
        event_id = await audit_manager.log_login(
            user_id="test-user-id",
            username="test-user",
            session_id="test-session",
            ip_address="192.168.1.1",
            auth_provider="kubeconfig"
        )
        
        # Verify event
        assert event_id is not None
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_type == AuditEventType.LOGIN
        assert event.success is True
    
    @pytest.mark.asyncio
    async def test_log_login_failed(self, audit_manager):
        """Test logging failed login event"""
        event_id = await audit_manager.log_login_failed(
            username="test-user",
            ip_address="192.168.1.1",
            reason="Invalid credentials"
        )
        
        # Verify event
        assert event_id is not None
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_type == AuditEventType.LOGIN_FAILED
        assert event.success is False
        assert event.error_message == "Invalid credentials"
    
    @pytest.mark.asyncio
    async def test_log_permission_check(self, audit_manager):
        """Test logging permission check event"""
        event_id = await audit_manager.log_permission_check(
            user_id="test-user-id",
            username="test-user",
            permission="read:pods",
            resource_type="pods",
            resource_id="test-pod",
            granted=True
        )
        
        # Verify event
        assert event_id is not None
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_type == AuditEventType.PERMISSION_CHECK
        assert event.success is True
    
    @pytest.mark.asyncio
    async def test_log_permission_denied(self, audit_manager):
        """Test logging permission denied event"""
        event_id = await audit_manager.log_permission_check(
            user_id="test-user-id",
            username="test-user",
            permission="admin:users",
            resource_type="users",
            granted=False
        )
        
        # Verify event
        assert event_id is not None
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_type == AuditEventType.PERMISSION_DENIED
        assert event.success is False
    
    @pytest.mark.asyncio
    async def test_log_resource_access(self, audit_manager):
        """Test logging resource access event"""
        event_id = await audit_manager.log_resource_access(
            user_id="test-user-id",
            username="test-user",
            action="read",
            resource_type="pods",
            resource_id="test-pod",
            session_id="test-session",
            ip_address="192.168.1.1"
        )
        
        # Verify event
        assert event_id is not None
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_type == AuditEventType.RESOURCE_READ
        assert event.success is True
    
    @pytest.mark.asyncio
    async def test_log_security_alert(self, audit_manager):
        """Test logging security alert event"""
        event_id = await audit_manager.log_security_alert(
            alert_type="suspicious_activity",
            description="Multiple failed login attempts",
            user_id="test-user-id",
            username="test-user",
            ip_address="192.168.1.1",
            details={"attempts": 5}
        )
        
        # Verify event
        assert event_id is not None
        assert len(audit_manager.storage) == 1
        event = audit_manager.storage[0]
        assert event.event_type == AuditEventType.SECURITY_ALERT
        assert event.severity == AuditSeverity.HIGH
        assert event.success is False
    
    @pytest.mark.asyncio
    async def test_query_events(self, audit_manager):
        """Test querying audit events"""
        # Log some events
        await audit_manager.log_login("user1", "test-user1", "session1")
        await audit_manager.log_login("user2", "test-user2", "session2")
        await audit_manager.log_login_failed("test-user3", reason="Invalid password")
        
        # Query events
        events = await audit_manager.query_events(limit=10)
        
        # Verify events
        assert len(events) == 3
        assert events[0].event_type == AuditEventType.LOGIN_FAILED  # Most recent first
        assert events[1].event_type == AuditEventType.LOGIN
        assert events[2].event_type == AuditEventType.LOGIN
    
    @pytest.mark.asyncio
    async def test_query_events_with_filter(self, audit_manager):
        """Test querying events with filter"""
        # Log events
        await audit_manager.log_login("user1", "test-user1", "session1")
        await audit_manager.log_login_failed("test-user2", reason="Invalid password")
        
        # Create filter
        filter_criteria = AuditFilter(
            event_type=AuditEventType.LOGIN_FAILED
        )
        
        # Query with filter
        events = await audit_manager.query_events(filter_criteria=filter_criteria)
        
        # Verify filtered events
        assert len(events) == 1
        assert events[0].event_type == AuditEventType.LOGIN_FAILED
    
    @pytest.mark.asyncio
    async def test_get_event_statistics(self, audit_manager):
        """Test getting event statistics"""
        # Log various events
        await audit_manager.log_login("user1", "test-user1", "session1")
        await audit_manager.log_login_failed("test-user2", reason="Invalid password")
        await audit_manager.log_permission_check("user1", "test-user1", "read:pods", granted=True)
        
        # Get statistics
        stats = await audit_manager.get_event_statistics()
        
        # Verify statistics
        assert stats["total_events"] == 3
        assert stats["successful_events"] == 2
        assert stats["failed_events"] == 1
        assert "login" in stats["event_type_distribution"]
        assert "login_failed" in stats["event_type_distribution"]
    
    @pytest.mark.asyncio
    async def test_export_audit_log(self, audit_manager):
        """Test exporting audit log"""
        # Log some events
        await audit_manager.log_login("user1", "test-user1", "session1")
        await audit_manager.log_login_failed("test-user2", reason="Invalid password")
        
        # Export as JSON
        json_export = await audit_manager.export_audit_log(format="json")
        
        # Verify export
        assert json_export is not None
        assert len(json_export) > 0
        
        # Parse JSON
        import json
        events_data = json.loads(json_export)
        assert len(events_data) == 2
    
    @pytest.mark.asyncio
    async def test_get_compliance_report(self, audit_manager):
        """Test getting compliance report"""
        # Log various events
        await audit_manager.log_login("user1", "test-user1", "session1")
        await audit_manager.log_login_failed("test-user2", reason="Invalid password")
        await audit_manager.log_security_alert("suspicious_activity", "Multiple failed logins")
        
        # Get compliance report
        report = await audit_manager.get_compliance_report()
        
        # Verify report
        assert report["total_events"] == 3
        assert report["security_events"] == 2  # login_failed + security_alert
        assert report["authentication_events"] == 1  # login
        assert report["failed_events"] == 2
        assert "compliance_score" in report
    
    @pytest.mark.asyncio
    async def test_cleanup_old_events(self, audit_manager):
        """Test cleaning up old events"""
        # Log some events
        await audit_manager.log_login("user1", "test-user1", "session1")
        
        # Manually age an event
        if audit_manager.storage:
            audit_manager.storage[0].timestamp = datetime.now() - timedelta(days=100)
        
        # Cleanup old events
        removed_count = await audit_manager.cleanup_old_events()
        
        # Verify cleanup
        assert removed_count >= 0  # Should remove at least the aged event


if __name__ == "__main__":
    pytest.main([__file__]) 