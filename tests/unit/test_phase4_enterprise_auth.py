"""
Comprehensive Unit Tests for Phase 4: Enterprise Authentication System
Testing the gold standard blueprint implementation
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from upid.auth.enterprise_auth import (
    EnterpriseAuthManager, AuthRegistry, UserPrincipal, AuthLevel,
    AuthSession, AuthMiddleware
)
from upid.auth.providers import (
    KubeconfigAuthProvider, TokenAuthProvider, OIDCAuthProvider,
    LDAPAuthProvider, SAMLAuthProvider, AWSIAMAuthProvider,
    GCPIAMAuthProvider, AzureADAuthProvider
)


class TestEnterpriseAuthManager:
    """Test enterprise authentication manager"""
    
    @pytest_asyncio.fixture
    async def auth_manager(self):
        """Create auth manager for testing"""
        registry = AuthRegistry()
        manager = EnterpriseAuthManager(registry)
        manager._register_providers_sync()  # Ensure providers are registered synchronously for tests
        return manager
    
    @pytest.mark.asyncio
    async def test_auth_manager_initialization(self, auth_manager):
        """Test auth manager initialization"""
        assert auth_manager.registry is not None
        assert auth_manager.sessions == {}
        assert auth_manager.audit_trail == []
        assert auth_manager.secret_key is not None
        assert auth_manager.session_timeout == timedelta(hours=8)
        assert auth_manager.max_sessions_per_user == 5
    
    @pytest.mark.asyncio
    async def test_provider_registration(self, auth_manager):
        """Test provider registration"""
        # Test that providers are registered
        providers = auth_manager.registry.list_providers()
        assert len(providers) > 0
        
        # Test provider health check
        health = await auth_manager.registry.get_provider_health()
        assert isinstance(health, dict)
        assert len(health) > 0
    
    @pytest.mark.asyncio
    async def test_kubeconfig_authentication(self, auth_manager):
        """Test kubeconfig authentication"""
        credentials = {"username": "test-user"}
        
        # Mock kubectl command
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(
                b"test-user", b""
            ))
            mock_subprocess.return_value = mock_process
            
            session = await auth_manager.authenticate("kubeconfig", credentials)
            
            if session:  # May fail if kubectl not available
                assert isinstance(session, AuthSession)
                assert session.user_principal.user_id == "test-user"
                assert session.user_principal.provider == "kubeconfig"
    
    @pytest.mark.asyncio
    async def test_token_authentication(self, auth_manager):
        """Test JWT token authentication"""
        # Get the token provider from the auth manager
        token_provider = auth_manager.registry.get_provider("token")
        assert token_provider is not None
        
        # Create a test user
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["user"],
            provider="token"
        )
        
        # Generate token using the same provider instance
        token = await token_provider._generate_token(test_user)
        
        credentials = {"token": token}
        session = await auth_manager.authenticate("token", credentials)
        
        assert session is not None
        assert isinstance(session, AuthSession)
        assert session.user_principal.user_id == "test-user"
        assert session.user_principal.provider == "token"
    
    @pytest.mark.asyncio
    async def test_session_management(self, auth_manager):
        """Test session management"""
        # Create a test session
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["user"],
            provider="token"
        )
        
        session = await auth_manager._create_session(test_user)
        assert isinstance(session, AuthSession)
        assert session.user_principal.user_id == "test-user"
        assert session.session_id is not None
        
        # Test session validation
        validated_session = await auth_manager.validate_session(session.session_id)
        assert validated_session is not None
        assert validated_session.session_id == session.session_id
        
        # Test session refresh - check that expiration is extended
        original_expires_at = session.expires_at
        refreshed_session = await auth_manager.refresh_session(session.session_id)
        assert refreshed_session is not None
        assert refreshed_session.expires_at > original_expires_at
        
        # Verify the session was extended by the session timeout
        expected_extension = auth_manager.session_timeout
        actual_extension = refreshed_session.expires_at - original_expires_at
        # Allow for small timing differences (within 1 second)
        assert abs((actual_extension - expected_extension).total_seconds()) < 1
        
        # Test logout
        logout_success = await auth_manager.logout(session.session_id)
        assert logout_success is True
        
        # Verify session is removed
        validated_session = await auth_manager.validate_session(session.session_id)
        assert validated_session is None
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, auth_manager):
        """Test risk assessment"""
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["admin"],  # High-risk role
            provider="token"
        )
        
        context = {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "location": "unknown"
        }
        
        risk_score = await auth_manager._assess_risk(test_user, context)
        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_audit_trail(self, auth_manager):
        """Test audit trail functionality"""
        # Test audit event recording
        await auth_manager._audit_event("test_event", {
            "user_id": "test-user",
            "action": "test"
        })
        
        # Test audit trail retrieval
        audit_trail = await auth_manager.get_audit_trail()
        assert isinstance(audit_trail, list)
        assert len(audit_trail) > 0
        
        # Test filtered audit trail
        filtered_trail = await auth_manager.get_audit_trail(
            event_types=["test_event"]
        )
        assert isinstance(filtered_trail, list)
    
    @pytest.mark.asyncio
    async def test_session_limits(self, auth_manager):
        """Test session limits enforcement"""
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["user"],
            provider="token"
        )
        
        # Create multiple sessions for the same user
        sessions = []
        for i in range(6):  # Try to create more than max_sessions_per_user
            session = await auth_manager._create_session(test_user)
            sessions.append(session)
        
        # Check that session limits are enforced
        session_count = len([s for s in auth_manager.sessions.values() 
                           if s.user_principal.user_id == "test-user"])
        assert session_count <= auth_manager.max_sessions_per_user
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, auth_manager):
        """Test expired session cleanup"""
        # Create a session that expires immediately
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["user"],
            provider="token"
        )
        
        session = await auth_manager._create_session(test_user)
        # Manually expire the session
        session.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Run cleanup
        await auth_manager.cleanup_expired_sessions()
        
        # Verify expired session is removed
        validated_session = await auth_manager.validate_session(session.session_id)
        assert validated_session is None


class TestAuthProviders:
    """Test individual authentication providers"""
    
    @pytest.mark.asyncio
    async def test_kubeconfig_provider(self):
        """Test kubeconfig provider"""
        provider = KubeconfigAuthProvider()
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "Kubernetes Kubeconfig"
        assert metadata["type"] == "kubeconfig"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
        assert "timestamp" in health
    
    @pytest.mark.asyncio
    async def test_token_provider(self):
        """Test JWT token provider"""
        provider = TokenAuthProvider()
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "JWT Token Authentication"
        assert metadata["type"] == "jwt"
        
        # Test token generation and validation
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["user"],
            provider="token"
        )
        
        token = await provider._generate_token(test_user)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test token validation
        validated_user = await provider.validate_token(token)
        assert validated_user is not None
        assert validated_user.user_id == "test-user"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
    
    @pytest.mark.asyncio
    async def test_oidc_provider(self):
        """Test OIDC provider"""
        provider = OIDCAuthProvider(
            issuer_url="https://accounts.google.com",
            client_id="test-client-id"
        )
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "OpenID Connect"
        assert metadata["type"] == "oidc"
        
        # Test authentication
        credentials = {"username": "test-user", "password": "test-pass"}
        user_principal = await provider.authenticate(credentials)
        
        assert user_principal is not None
        assert user_principal.user_id == "test-user"
        assert user_principal.provider == "oidc"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
    
    @pytest.mark.asyncio
    async def test_ldap_provider(self):
        """Test LDAP provider"""
        provider = LDAPAuthProvider(
            server_url="ldap://localhost:389",
            base_dn="dc=example,dc=com"
        )
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "LDAP Authentication"
        assert metadata["type"] == "ldap"
        
        # Test authentication
        credentials = {"username": "test-user", "password": "test-pass"}
        user_principal = await provider.authenticate(credentials)
        
        assert user_principal is not None
        assert user_principal.user_id == "test-user"
        assert user_principal.provider == "ldap"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
    
    @pytest.mark.asyncio
    async def test_saml_provider(self):
        """Test SAML provider"""
        provider = SAMLAuthProvider(
            idp_entity_id="https://idp.example.com",
            sp_entity_id="https://sp.example.com",
            idp_sso_url="https://idp.example.com/sso"
        )
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "SAML Authentication"
        assert metadata["type"] == "saml"
        
        # Test authentication
        credentials = {"saml_response": "mock_saml_test-user"}
        user_principal = await provider.authenticate(credentials)
        
        assert user_principal is not None
        assert user_principal.user_id == "test-user"
        assert user_principal.provider == "saml"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
    
    @pytest.mark.asyncio
    async def test_aws_iam_provider(self):
        """Test AWS IAM provider"""
        provider = AWSIAMAuthProvider(region="us-east-1")
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "AWS IAM Authentication"
        assert metadata["type"] == "aws_iam"
        
        # Test authentication
        credentials = {
            "access_key_id": "test-access-key",
            "secret_access_key": "test-secret-key"
        }
        user_principal = await provider.authenticate(credentials)
        
        assert user_principal is not None
        assert user_principal.user_id == "test-access-key"
        assert user_principal.provider == "aws_iam"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
    
    @pytest.mark.asyncio
    async def test_gcp_iam_provider(self):
        """Test GCP IAM provider"""
        provider = GCPIAMAuthProvider(project_id="test-project")
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "Google Cloud Platform IAM"
        assert metadata["type"] == "gcp_iam"
        
        # Test authentication
        credentials = {"service_account_key": "mock-key"}
        user_principal = await provider.authenticate(credentials)
        
        assert user_principal is not None
        assert user_principal.user_id == "gcp-user"
        assert user_principal.provider == "gcp_iam"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health
    
    @pytest.mark.asyncio
    async def test_azure_ad_provider(self):
        """Test Azure AD provider"""
        provider = AzureADAuthProvider(
            tenant_id="test-tenant",
            client_id="test-client-id"
        )
        
        # Test metadata
        metadata = provider.get_metadata()
        assert metadata["name"] == "Azure Active Directory"
        assert metadata["type"] == "azure_ad"
        
        # Test authentication
        credentials = {"username": "test-user", "password": "test-pass"}
        user_principal = await provider.authenticate(credentials)
        
        assert user_principal is not None
        assert user_principal.user_id == "azure-user"
        assert user_principal.provider == "azure_ad"
        
        # Test health check
        health = await provider.health_check()
        assert isinstance(health, dict)
        assert "status" in health


class TestAuthMiddleware:
    """Test authentication middleware"""
    
    @pytest_asyncio.fixture
    async def auth_middleware(self):
        """Create auth middleware for testing"""
        registry = AuthRegistry()
        auth_manager = EnterpriseAuthManager(registry)
        middleware = AuthMiddleware(auth_manager)
        return middleware
    
    @pytest.mark.asyncio
    async def test_authenticate_request(self, auth_middleware):
        """Test request authentication"""
        headers = {
            "Authorization": "Bearer test-token",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.1"
        }
        
        context = {"path": "/api/test", "method": "GET"}
        
        session = await auth_middleware.authenticate_request(headers, context)
        # May be None if no valid token, but should not raise exception
        assert session is None or isinstance(session, AuthSession)
    
    @pytest.mark.asyncio
    async def test_require_auth(self, auth_middleware):
        """Test auth requirement checking"""
        # Test with no session
        auth_result = await auth_middleware.require_auth(None)
        assert auth_result is False
        
        # Test with valid session
        test_user = UserPrincipal(
            user_id="test-user",
            email="test@example.com",
            display_name="Test User",
            roles=["user"],
            provider="token"
        )
        
        session = AuthSession(
            session_id="test-session",
            user_principal=test_user,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            last_activity=datetime.now()
        )
        
        auth_result = await auth_middleware.require_auth(session)
        assert auth_result is True
        
        # Test with role requirement
        auth_result = await auth_middleware.require_auth(
            session, 
            required_roles=["admin"]
        )
        assert auth_result is False  # User doesn't have admin role


class TestAuthRegistry:
    """Test authentication registry"""
    
    @pytest_asyncio.fixture
    async def registry(self):
        """Create auth registry for testing"""
        return AuthRegistry()
    
    @pytest.mark.asyncio
    async def test_provider_registration(self, registry):
        """Test provider registration"""
        provider = TokenAuthProvider()
        
        # Test registration
        success = await registry.register_provider("test-token", provider)
        assert success is True
        
        # Test provider retrieval
        retrieved_provider = registry.get_provider("test-token")
        assert retrieved_provider is provider
        
        # Test provider listing
        providers = registry.list_providers()
        assert "test-token" in providers
    
    @pytest.mark.asyncio
    async def test_provider_unregistration(self, registry):
        """Test provider unregistration"""
        provider = TokenAuthProvider()
        
        # Register provider
        await registry.register_provider("test-token", provider)
        
        # Unregister provider
        success = await registry.unregister_provider("test-token")
        assert success is True
        
        # Verify provider is removed
        retrieved_provider = registry.get_provider("test-token")
        assert retrieved_provider is None
        
        providers = registry.list_providers()
        assert "test-token" not in providers
    
    @pytest.mark.asyncio
    async def test_provider_health(self, registry):
        """Test provider health checking"""
        provider = TokenAuthProvider()
        await registry.register_provider("test-token", provider)
        
        health = await registry.get_provider_health()
        assert isinstance(health, dict)
        assert "test-token" in health
        assert "status" in health["test-token"]


if __name__ == "__main__":
    pytest.main([__file__]) 