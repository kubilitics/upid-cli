"""
Enterprise-Grade Authentication System for UPID CLI
Following the gold standard blueprint for robust, secure, and maintainable identity systems
"""

import asyncio
import logging
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import uuid

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
    CUSTOM = "custom"


class AuthLevel(Enum):
    """Authentication assurance levels"""
    NONE = 0
    SINGLE_FACTOR = 1
    MULTI_FACTOR = 2
    STEP_UP = 3
    HARDWARE_TOKEN = 4


@dataclass
class UserPrincipal:
    """Canonical user model - all providers map to this"""
    user_id: str
    email: str
    display_name: str
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    claims: Dict[str, str] = field(default_factory=dict)
    mfa_authenticated: bool = False
    auth_level: AuthLevel = AuthLevel.SINGLE_FACTOR
    provider: str = ""
    session_expires: Optional[datetime] = None
    last_login: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthSession:
    """Enterprise session with full context"""
    session_id: str
    user_principal: UserPrincipal
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    mfa_completed: bool = False
    risk_score: float = 0.0
    audit_trail: List[str] = field(default_factory=list)


class AuthProvider(ABC):
    """Strict interface for all authentication providers"""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserPrincipal]:
        """Authenticate user with provided credentials"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[UserPrincipal]:
        """Validate authentication token"""
        pass
    
    @abstractmethod
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh authentication token"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get provider metadata and capabilities"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health and connectivity"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test provider connectivity"""
        pass


class AuthRegistry:
    """
    Dynamic provider registry with hot reload capabilities
    """
    
    def __init__(self):
        self.providers: Dict[str, AuthProvider] = {}
        self.provider_configs: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def register_provider(
        self, 
        name: str, 
        provider: AuthProvider, 
        config: Dict[str, Any] = None
    ) -> bool:
        """Register a new authentication provider"""
        try:
            async with self._lock:
                # Test provider connectivity
                if not await provider.test_connection():
                    logger.error(f"Provider {name} failed connectivity test")
                    return False
                
                self.providers[name] = provider
                if config:
                    self.provider_configs[name] = config
                
                logger.info(f"Successfully registered provider: {name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register provider {name}: {e}")
            return False
    
    async def unregister_provider(self, name: str) -> bool:
        """Unregister an authentication provider"""
        try:
            async with self._lock:
                if name in self.providers:
                    del self.providers[name]
                if name in self.provider_configs:
                    del self.provider_configs[name]
                
                logger.info(f"Successfully unregistered provider: {name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unregister provider {name}: {e}")
            return False
    
    def get_provider(self, name: str) -> Optional[AuthProvider]:
        """Get a registered provider"""
        return self.providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self.providers.keys())
    
    async def get_provider_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all providers"""
        health_status = {}
        
        for name, provider in self.providers.items():
            try:
                health = await provider.health_check()
                health_status[name] = health
            except Exception as e:
                health_status[name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return health_status


class EnterpriseAuthManager:
    """
    Enterprise authentication manager with zero-trust principles
    """
    
    def __init__(self, registry: AuthRegistry = None):
        self.registry = registry or AuthRegistry()
        self.sessions: Dict[str, AuthSession] = {}
        self.audit_trail: List[Dict[str, Any]] = []
        self.secret_key = secrets.token_urlsafe(32)
        self.session_timeout = timedelta(hours=8)
        self.max_sessions_per_user = 5
        
        # Initialize default providers
        self._init_default_providers()
    
    def _init_default_providers(self):
        """Initialize default authentication providers"""
        try:
            from .providers import (
                KubeconfigAuthProvider, TokenAuthProvider, OIDCAuthProvider,
                LDAPAuthProvider, SAMLAuthProvider, AWSIAMAuthProvider,
                GCPIAMAuthProvider, AzureADAuthProvider
            )
            
            # Register default providers
            asyncio.create_task(self.registry.register_provider(
                "kubeconfig", 
                KubeconfigAuthProvider(),
                {"type": "kubeconfig"}
            ))
            
            asyncio.create_task(self.registry.register_provider(
                "token", 
                TokenAuthProvider(),
                {"type": "jwt"}
            ))
            
            asyncio.create_task(self.registry.register_provider(
                "oidc", 
                OIDCAuthProvider(
                    issuer_url="https://accounts.google.com",
                    client_id="mock-client-id",
                    client_secret="mock-client-secret"
                ),
                {"type": "oidc", "issuer": "https://accounts.google.com"}
            ))
            
            # Register enterprise providers
            asyncio.create_task(self.registry.register_provider(
                "ldap",
                LDAPAuthProvider(
                    server_url="ldap://localhost:389",
                    base_dn="dc=example,dc=com"
                ),
                {"type": "ldap"}
            ))
            
            asyncio.create_task(self.registry.register_provider(
                "saml",
                SAMLAuthProvider(
                    idp_entity_id="https://idp.example.com",
                    sp_entity_id="https://sp.example.com",
                    idp_sso_url="https://idp.example.com/sso"
                ),
                {"type": "saml"}
            ))
            
            asyncio.create_task(self.registry.register_provider(
                "aws_iam",
                AWSIAMAuthProvider(region="us-east-1"),
                {"type": "aws_iam"}
            ))
            
            asyncio.create_task(self.registry.register_provider(
                "gcp_iam",
                GCPIAMAuthProvider(project_id="example-project"),
                {"type": "gcp_iam"}
            ))
            
            asyncio.create_task(self.registry.register_provider(
                "azure_ad",
                AzureADAuthProvider(
                    tenant_id="example-tenant",
                    client_id="mock-client-id"
                ),
                {"type": "azure_ad"}
            ))
            
        except Exception as e:
            logger.error(f"Failed to initialize default providers: {e}")
            # Continue with basic providers only
            pass
    
    def _register_providers_sync(self):
        """Synchronously register all providers (for testing)"""
        from .providers import (
            KubeconfigAuthProvider, TokenAuthProvider, OIDCAuthProvider,
            LDAPAuthProvider, SAMLAuthProvider, AWSIAMAuthProvider,
            GCPIAMAuthProvider, AzureADAuthProvider
        )
        self.registry.providers = {
            "kubeconfig": KubeconfigAuthProvider(),
            "token": TokenAuthProvider(),
            "oidc": OIDCAuthProvider(
                issuer_url="https://accounts.google.com",
                client_id="mock-client-id",
                client_secret="mock-client-secret"
            ),
            "ldap": LDAPAuthProvider(
                server_url="ldap://localhost:389",
                base_dn="dc=example,dc=com"
            ),
            "saml": SAMLAuthProvider(
                idp_entity_id="https://idp.example.com",
                sp_entity_id="https://sp.example.com",
                idp_sso_url="https://idp.example.com/sso"
            ),
            "aws_iam": AWSIAMAuthProvider(region="us-east-1"),
            "gcp_iam": GCPIAMAuthProvider(project_id="example-project"),
            "azure_ad": AzureADAuthProvider(
                tenant_id="example-tenant",
                client_id="mock-client-id"
            )
        }

    async def authenticate(
        self, 
        provider_name: str, 
        credentials: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Optional[AuthSession]:
        """
        Authenticate user with specified provider
        
        Args:
            provider_name: Name of the authentication provider
            credentials: Authentication credentials
            context: Additional context (IP, user agent, etc.)
            
        Returns:
            AuthSession: Authentication session if successful
        """
        try:
            # Get provider
            provider = self.registry.get_provider(provider_name)
            if not provider:
                await self._audit_event("authentication_failed", {
                    "provider": provider_name,
                    "reason": "provider_not_found",
                    "context": context
                })
                return None
            
            # Authenticate with provider
            user_principal = await provider.authenticate(credentials)
            if not user_principal:
                await self._audit_event("authentication_failed", {
                    "provider": provider_name,
                    "reason": "invalid_credentials",
                    "context": context
                })
                return None
            
            # Apply risk assessment
            risk_score = await self._assess_risk(user_principal, context)
            user_principal.risk_score = risk_score
            
            # Check session limits
            if not await self._check_session_limits(user_principal.user_id):
                await self._audit_event("session_limit_exceeded", {
                    "user_id": user_principal.user_id,
                    "provider": provider_name
                })
                return None
            
            # Create session
            session = await self._create_session(user_principal, context)
            
            # Audit successful authentication
            await self._audit_event("authentication_success", {
                "user_id": user_principal.user_id,
                "provider": provider_name,
                "session_id": session.session_id,
                "risk_score": risk_score,
                "context": context
            })
            
            logger.info(f"Authentication successful for user: {user_principal.user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self._audit_event("authentication_error", {
                "provider": provider_name,
                "error": str(e),
                "context": context
            })
            return None
    
    async def validate_session(self, session_id: str) -> Optional[AuthSession]:
        """
        Validate authentication session with zero-trust principles
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                await self._audit_event("session_validation_failed", {
                    "session_id": session_id,
                    "reason": "session_not_found"
                })
                return None
            
            # Check session expiration
            if datetime.now() > session.expires_at:
                await self._audit_event("session_expired", {
                    "session_id": session_id,
                    "user_id": session.user_principal.user_id
                })
                await self._remove_session(session_id)
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
            
            # Re-assess risk (for long-running sessions)
            if (datetime.now() - session.created_at) > timedelta(hours=1):
                new_risk_score = await self._assess_risk(
                    session.user_principal, 
                    {"session_id": session_id}
                )
                session.risk_score = new_risk_score
            
            return session
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    async def refresh_session(self, session_id: str) -> Optional[AuthSession]:
        """Refresh authentication session"""
        try:
            session = await self.validate_session(session_id)
            if not session:
                return None
            # Extend session from current expires_at if in the future, else from now
            now = datetime.now()
            if session.expires_at > now:
                session.expires_at = session.expires_at + self.session_timeout
            else:
                session.expires_at = now + self.session_timeout
            session.last_activity = now
            await self._audit_event("session_refreshed", {
                "session_id": session_id,
                "user_id": session.user_principal.user_id
            })
            return session
        except Exception as e:
            logger.error(f"Session refresh error: {e}")
            return None
    
    async def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                await self._audit_event("logout", {
                    "session_id": session_id,
                    "user_id": session.user_principal.user_id
                })
                await self._remove_session(session_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def _create_session(
        self, 
        user_principal: UserPrincipal, 
        context: Dict[str, Any] = None
    ) -> AuthSession:
        """Create new authentication session, enforcing session limits"""
        # Enforce session limit: remove oldest if over limit
        user_sessions = [
            (sid, s) for sid, s in self.sessions.items()
            if s.user_principal.user_id == user_principal.user_id
        ]
        if len(user_sessions) >= self.max_sessions_per_user:
            # Remove oldest session
            oldest_sid = sorted(user_sessions, key=lambda x: x[1].created_at)[0][0]
            await self._remove_session(oldest_sid)
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + self.session_timeout
        session = AuthSession(
            session_id=session_id,
            user_principal=user_principal,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_activity=datetime.now(),
            ip_address=context.get('ip_address') if context else None,
            user_agent=context.get('user_agent') if context else None,
            device_id=context.get('device_id') if context else None,
            mfa_completed=user_principal.mfa_authenticated,
            risk_score=user_principal.risk_score
        )
        self.sessions[session_id] = session
        return session
    
    async def _remove_session(self, session_id: str):
        """Remove authentication session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def _check_session_limits(self, user_id: str) -> bool:
        """Check if user has exceeded session limits"""
        user_sessions = [
            s for s in self.sessions.values()
            if s.user_principal.user_id == user_id
        ]
        return len(user_sessions) < self.max_sessions_per_user
    
    async def _assess_risk(
        self, 
        user_principal: UserPrincipal, 
        context: Dict[str, Any] = None
    ) -> float:
        """Assess risk score for authentication attempt"""
        risk_score = 0.0
        
        # Time-based risk
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            risk_score += 0.2
        
        # Location-based risk (if IP available)
        if context and context.get('ip_address'):
            # In real implementation, check against known locations
            risk_score += 0.1
        
        # Device-based risk
        if context and context.get('device_id'):
            # In real implementation, check device trust
            risk_score += 0.1
        
        # MFA reduces risk
        if user_principal.mfa_authenticated:
            risk_score -= 0.3
        
        return max(0.0, min(1.0, risk_score))
    
    async def _audit_event(self, event_type: str, details: Dict[str, Any]):
        """Audit authentication event"""
        audit_entry = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        self.audit_trail.append(audit_entry)
        
        # In production, send to external audit system
        logger.info(f"AUDIT: {event_type} - {details}")
    
    async def get_audit_trail(
        self, 
        start_time: datetime = None, 
        end_time: datetime = None,
        event_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit trail with filtering"""
        filtered_events = self.audit_trail
        
        if start_time:
            filtered_events = [
                e for e in filtered_events
                if datetime.fromisoformat(e["timestamp"]) >= start_time
            ]
        
        if end_time:
            filtered_events = [
                e for e in filtered_events
                if datetime.fromisoformat(e["timestamp"]) <= end_time
            ]
        
        if event_types:
            filtered_events = [
                e for e in filtered_events
                if e["event_type"] in event_types
            ]
        
        return filtered_events
    
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
    """Enterprise authentication middleware"""
    
    def __init__(self, auth_manager: EnterpriseAuthManager):
        self.auth_manager = auth_manager
    
    async def authenticate_request(
        self, 
        request_headers: Dict[str, str],
        request_context: Dict[str, Any] = None
    ) -> Optional[AuthSession]:
        """Authenticate API request with full context"""
        try:
            # Extract session token
            session_token = request_headers.get('Authorization', '').replace('Bearer ', '')
            if not session_token:
                return None
            
            # Validate session
            session = await self.auth_manager.validate_session(session_token)
            
            # Add request context to audit
            if session and request_context:
                await self.auth_manager._audit_event("request_authenticated", {
                    "session_id": session.session_id,
                    "user_id": session.user_principal.user_id,
                    "context": request_context
                })
            
            return session
            
        except Exception as e:
            logger.error(f"Request authentication error: {e}")
            return None
    
    async def require_auth(
        self, 
        session: Optional[AuthSession], 
        required_level: AuthLevel = AuthLevel.SINGLE_FACTOR,
        required_roles: List[str] = None
    ) -> bool:
        """Require authentication at specified level with role checks"""
        if not session:
            return False
        
        # Check authentication level
        if session.user_principal.auth_level.value < required_level.value:
            return False
        
        # Check required roles
        if required_roles:
            user_roles = set(session.user_principal.roles)
            if not any(role in user_roles for role in required_roles):
                return False
        
        return True 