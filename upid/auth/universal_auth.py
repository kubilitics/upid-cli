"""
Universal Authentication System for UPID CLI
Supports multiple authentication providers and enterprise security standards
"""

import asyncio
import logging
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AuthProviderType(Enum):
    """Supported authentication provider types"""
    KUBECONFIG = "kubeconfig"
    TOKEN = "token"
    OIDC = "oidc"
    SAML = "saml"
    LDAP = "ldap"
    AWS_IAM = "aws_iam"
    GCP_IAM = "gcp_iam"
    AZURE_AD = "azure_ad"


class AuthLevel(Enum):
    """Authentication levels"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class AuthUser:
    """Authenticated user information"""
    username: str
    email: Optional[str] = None
    groups: List[str] = None
    roles: List[str] = None
    permissions: List[str] = None
    auth_provider: AuthProviderType = None
    auth_level: AuthLevel = AuthLevel.READ
    session_expires: Optional[datetime] = None


@dataclass
class AuthSession:
    """Authentication session data"""
    session_id: str
    user: AuthUser
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    last_activity: datetime = None


class AuthProvider(ABC):
    """Abstract base class for authentication providers"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[AuthUser]:
        """Authenticate user with provided credentials"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[AuthUser]:
        """Validate authentication token"""
        pass
    
    @abstractmethod
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh authentication token"""
        pass


class KubeconfigAuthProvider(AuthProvider):
    """Kubernetes kubeconfig authentication provider"""
    
    def __init__(self):
        self.provider_type = AuthProviderType.KUBECONFIG
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[AuthUser]:
        """Authenticate using kubeconfig"""
        try:
            # Mock kubeconfig authentication
            # In real implementation, this would validate against kubeconfig
            username = credentials.get('username', 'kubeconfig-user')
            
            return AuthUser(
                username=username,
                auth_provider=self.provider_type,
                auth_level=AuthLevel.ADMIN,
                groups=['system:masters'],
                roles=['cluster-admin'],
                permissions=['*']
            )
        except Exception as e:
            logger.error(f"Kubeconfig authentication failed: {e}")
            return None
    
    async def validate_token(self, token: str) -> Optional[AuthUser]:
        """Validate kubeconfig token"""
        try:
            # Mock token validation
            # In real implementation, this would decode and validate the token
            return AuthUser(
                username='kubeconfig-user',
                auth_provider=self.provider_type,
                auth_level=AuthLevel.ADMIN
            )
        except Exception as e:
            logger.error(f"Kubeconfig token validation failed: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh kubeconfig token"""
        try:
            # Mock token refresh
            # In real implementation, this would generate a new token
            return f"refreshed-kubeconfig-token-{secrets.token_urlsafe(32)}"
        except Exception as e:
            logger.error(f"Kubeconfig token refresh failed: {e}")
            return None


class TokenAuthProvider(AuthProvider):
    """Token-based authentication provider"""
    
    def __init__(self, secret_key: str = None):
        self.provider_type = AuthProviderType.TOKEN
        self.secret_key = secret_key or secrets.token_urlsafe(32)
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[AuthUser]:
        """Authenticate using token"""
        try:
            token = credentials.get('token')
            if not token:
                return None
            
            # Validate token
            user = await self.validate_token(token)
            return user
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            return None
    
    async def validate_token(self, token: str) -> Optional[AuthUser]:
        """Validate authentication token"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            return AuthUser(
                username=payload.get('username', 'token-user'),
                email=payload.get('email'),
                groups=payload.get('groups', []),
                roles=payload.get('roles', []),
                permissions=payload.get('permissions', []),
                auth_provider=self.provider_type,
                auth_level=AuthLevel(payload.get('auth_level', 'read')),
                session_expires=datetime.fromisoformat(payload.get('expires_at'))
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[AuthUser]:
        """Authenticate using token"""
        try:
            token = credentials.get('token')
            if not token:
                return None
            
            # Validate token
            user = await self.validate_token(token)
            return user
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh authentication token"""
        try:
            # Validate current token
            user = await self.validate_token(token)
            if not user:
                return None
            
            # Generate new token
            payload = {
                'username': user.username,
                'email': user.email,
                'groups': user.groups,
                'roles': user.roles,
                'permissions': user.permissions,
                'auth_level': user.auth_level.value,
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
                'iat': datetime.now().isoformat()
            }
            
            new_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return new_token
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None


class OIDCAuthProvider(AuthProvider):
    """OpenID Connect authentication provider"""
    
    def __init__(self, issuer_url: str, client_id: str, client_secret: str):
        self.provider_type = AuthProviderType.OIDC
        self.issuer_url = issuer_url
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[AuthUser]:
        """Authenticate using OIDC"""
        try:
            # Mock OIDC authentication
            # In real implementation, this would validate against OIDC provider
            username = credentials.get('username', 'oidc-user')
            
            return AuthUser(
                username=username,
                email=f"{username}@example.com",
                auth_provider=self.provider_type,
                auth_level=AuthLevel.WRITE,
                groups=['developers'],
                roles=['developer'],
                permissions=['read', 'write']
            )
        except Exception as e:
            logger.error(f"OIDC authentication failed: {e}")
            return None
    
    async def validate_token(self, token: str) -> Optional[AuthUser]:
        """Validate OIDC token"""
        try:
            # Mock OIDC token validation
            # In real implementation, this would validate against OIDC provider
            return AuthUser(
                username='oidc-user',
                email='oidc-user@example.com',
                auth_provider=self.provider_type,
                auth_level=AuthLevel.WRITE
            )
        except Exception as e:
            logger.error(f"OIDC token validation failed: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh OIDC token"""
        try:
            # Mock OIDC token refresh
            # In real implementation, this would refresh with OIDC provider
            return f"refreshed-oidc-token-{secrets.token_urlsafe(32)}"
        except Exception as e:
            logger.error(f"OIDC token refresh failed: {e}")
            return None


class UniversalAuthManager:
    """
    Universal Authentication Manager
    Manages multiple authentication providers and sessions
    """
    
    def __init__(self):
        self.providers: Dict[AuthProviderType, AuthProvider] = {}
        self.sessions: Dict[str, AuthSession] = {}
        self.secret_key = secrets.token_urlsafe(32)
        
        # Initialize default providers
        self._init_default_providers()
    
    def _init_default_providers(self):
        """Initialize default authentication providers"""
        self.providers[AuthProviderType.KUBECONFIG] = KubeconfigAuthProvider()
        self.providers[AuthProviderType.TOKEN] = TokenAuthProvider(self.secret_key)
        self.providers[AuthProviderType.OIDC] = OIDCAuthProvider(
            issuer_url="https://accounts.google.com",
            client_id="mock-client-id",
            client_secret="mock-client-secret"
        )
    
    async def authenticate(
        self, 
        provider_type: AuthProviderType, 
        credentials: Dict[str, Any]
    ) -> Optional[AuthSession]:
        """
        Authenticate user with specified provider
        
        Args:
            provider_type: Type of authentication provider
            credentials: Authentication credentials
            
        Returns:
            AuthSession: Authentication session if successful
        """
        try:
            logger.info(f"Authenticating with provider: {provider_type.value}")
            
            # Get provider
            provider = self.providers.get(provider_type)
            if not provider:
                logger.error(f"Authentication provider not found: {provider_type}")
                return None
            
            # Authenticate user
            user = await provider.authenticate(credentials)
            if not user:
                logger.error(f"Authentication failed for provider: {provider_type}")
                return None
            
            # Create session
            session = await self._create_session(user)
            
            logger.info(f"Authentication successful for user: {user.username}")
            return session
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def validate_session(self, session_id: str) -> Optional[AuthSession]:
        """
        Validate authentication session
        
        Args:
            session_id: Session identifier
            
        Returns:
            AuthSession: Valid session or None
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session not found: {session_id}")
                return None
            
            # Check if session is expired
            if datetime.now() > session.expires_at:
                logger.warning(f"Session expired: {session_id}")
                await self._remove_session(session_id)
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
            
            return session
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    async def refresh_session(self, session_id: str) -> Optional[AuthSession]:
        """
        Refresh authentication session
        
        Args:
            session_id: Session identifier
            
        Returns:
            AuthSession: Refreshed session or None
        """
        try:
            session = await self.validate_session(session_id)
            if not session:
                return None
            
            # Extend session expiration
            session.expires_at = datetime.now() + timedelta(hours=24)
            session.last_activity = datetime.now()
            
            # Refresh token if provider supports it
            provider = self.providers.get(session.user.auth_provider)
            if provider and hasattr(provider, 'refresh_token'):
                new_token = await provider.refresh_token(session_id)
                if new_token:
                    # Update session with new token info
                    session.last_activity = datetime.now()
            
            return session
            
        except Exception as e:
            logger.error(f"Session refresh error: {e}")
            return None
    
    async def logout(self, session_id: str) -> bool:
        """
        Logout user and invalidate session
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if logout successful
        """
        try:
            if session_id in self.sessions:
                await self._remove_session(session_id)
                logger.info(f"User logged out: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def get_user_permissions(self, session_id: str) -> List[str]:
        """
        Get user permissions for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List[str]: User permissions
        """
        try:
            session = await self.validate_session(session_id)
            if not session:
                return []
            
            return session.user.permissions or []
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []
    
    async def check_permission(
        self, 
        session_id: str, 
        required_permission: str
    ) -> bool:
        """
        Check if user has required permission
        
        Args:
            session_id: Session identifier
            required_permission: Required permission
            
        Returns:
            bool: True if user has permission
        """
        try:
            permissions = await self.get_user_permissions(session_id)
            return required_permission in permissions or '*' in permissions
            
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return False
    
    async def _create_session(self, user: AuthUser) -> AuthSession:
        """Create new authentication session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        session = AuthSession(
            session_id=session_id,
            user=user,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session
        return session
    
    async def _remove_session(self, session_id: str):
        """Remove authentication session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = [
                session_id for session_id, session in self.sessions.items()
                if current_time > session.expires_at
            ]
            
            for session_id in expired_sessions:
                await self._remove_session(session_id)
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")


class AuthMiddleware:
    """Authentication middleware for API requests"""
    
    def __init__(self, auth_manager: UniversalAuthManager):
        self.auth_manager = auth_manager
    
    async def authenticate_request(
        self, 
        request_headers: Dict[str, str]
    ) -> Optional[AuthSession]:
        """
        Authenticate API request
        
        Args:
            request_headers: Request headers
            
        Returns:
            AuthSession: Authentication session or None
        """
        try:
            # Extract session token from headers
            session_token = request_headers.get('Authorization', '').replace('Bearer ', '')
            if not session_token:
                return None
            
            # Validate session
            session = await self.auth_manager.validate_session(session_token)
            return session
            
        except Exception as e:
            logger.error(f"Request authentication error: {e}")
            return None
    
    async def require_auth(
        self, 
        session: Optional[AuthSession], 
        required_level: AuthLevel = AuthLevel.READ
    ) -> bool:
        """
        Require authentication at specified level
        
        Args:
            session: Authentication session
            required_level: Required authentication level
            
        Returns:
            bool: True if authentication requirements met
        """
        if not session:
            return False
        
        # Check authentication level
        # Define level hierarchy
        level_hierarchy = {
            AuthLevel.NONE: 0,
            AuthLevel.READ: 1,
            AuthLevel.WRITE: 2,
            AuthLevel.ADMIN: 3
        }
        
        user_level = level_hierarchy.get(session.user.auth_level, 0)
        required_level_value = level_hierarchy.get(required_level, 0)
        
        if user_level < required_level_value:
            return False
        
        return True 