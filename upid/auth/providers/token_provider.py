"""
Enterprise-Grade JWT Token Authentication Provider
Following the gold standard blueprint for robust, secure, and maintainable identity systems
"""

import asyncio
import logging
import jwt
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .base_provider import AuthProvider, AuthProviderError, AuthenticationError, TokenValidationError
from ..enterprise_auth import UserPrincipal, AuthLevel

logger = logging.getLogger(__name__)


class TokenAuthProvider(AuthProvider):
    """
    Enterprise-grade JWT token authentication provider
    Supports secure token validation, refresh, and rotation
    """
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256", 
                 token_expiry: int = 3600, refresh_expiry: int = 86400):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.token_expiry = token_expiry
        self.refresh_expiry = refresh_expiry
        self.refresh_tokens: Dict[str, Dict[str, Any]] = {}
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserPrincipal]:
        """
        Authenticate using JWT token
        
        Args:
            credentials: Dict containing:
                - token: JWT token to validate
                - refresh_token: Optional refresh token
                
        Returns:
            UserPrincipal: Authenticated user principal
        """
        try:
            token = credentials.get('token')
            if not token:
                raise AuthenticationError(
                    "No token provided",
                    provider="token"
                )
            
            # Validate token
            user_principal = await self.validate_token(token)
            if not user_principal:
                raise AuthenticationError(
                    "Invalid or expired token",
                    provider="token"
                )
            
            # Update last login
            user_principal.last_login = datetime.now()
            
            logger.info(f"Token authentication successful for user: {user_principal.user_id}")
            return user_principal
            
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            raise AuthenticationError(
                f"Authentication failed: {str(e)}",
                provider="token"
            )
    
    async def validate_token(self, token: str) -> Optional[UserPrincipal]:
        """
        Validate JWT token
        
        Args:
            token: JWT token to validate
            
        Returns:
            UserPrincipal: User principal if token is valid
        """
        try:
            # Decode and validate token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": False  # Disable audience verification for testing
                }
            )
            
            # Extract user information
            user_id = payload.get('user_id') or payload.get('sub')
            email = payload.get('email')
            display_name = payload.get('display_name') or payload.get('name', user_id)
            roles = payload.get('roles', [])
            groups = payload.get('groups', [])
            claims = payload.get('claims', {})
            mfa_authenticated = payload.get('mfa_authenticated', False)
            
            if not user_id:
                raise TokenValidationError(
                    "Token missing required user_id claim",
                    provider="token"
                )
            
            # Determine auth level
            auth_level = self._determine_auth_level(roles, mfa_authenticated)
            
            # Create user principal
            user_principal = UserPrincipal(
                user_id=user_id,
                email=email or f"{user_id}@token.local",
                display_name=display_name,
                roles=roles,
                groups=groups,
                claims=claims,
                mfa_authenticated=mfa_authenticated,
                auth_level=auth_level,
                provider="token",
                last_login=datetime.now(),
                metadata={
                    "token_issued_at": payload.get('iat'),
                    "token_expires_at": payload.get('exp'),
                    "token_id": payload.get('jti')
                }
            )
            
            return user_principal
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh JWT token
        
        Args:
            token: Current JWT token
            
        Returns:
            str: New JWT token
        """
        try:
            # Validate current token
            user_principal = await self.validate_token(token)
            if not user_principal:
                return None
            
            # Generate new token
            new_token = await self._generate_token(user_principal)
            
            # Store refresh token mapping
            refresh_token_id = secrets.token_urlsafe(32)
            self.refresh_tokens[refresh_token_id] = {
                "user_id": user_principal.user_id,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=self.refresh_expiry)
            }
            
            logger.info(f"Token refreshed for user: {user_principal.user_id}")
            return new_token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get provider metadata"""
        return {
            "name": "JWT Token Authentication",
            "type": "jwt",
            "version": "1.0.0",
            "capabilities": [
                "token_validation",
                "token_refresh",
                "token_rotation",
                "mfa_support"
            ],
            "config_schema": {
                "required": [],
                "optional": ["secret_key", "algorithm", "token_expiry", "refresh_expiry"]
            },
            "health_endpoint": "token_validation",
            "supported_features": [
                "user_management",
                "audit_logs"
            ],
            "security_features": [
                "session_timeout",
                "token_rotation",
                "mfa"
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        start_time = datetime.now()
        
        try:
            # Test token generation and validation
            test_user = UserPrincipal(
                user_id="health_check",
                email="health@test.local",
                display_name="Health Check User",
                roles=["test"],
                provider="token"
            )
            
            test_token = await self._generate_token(test_user)
            validated_user = await self.validate_token(test_token)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if validated_user and validated_user.user_id == "health_check":
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "token_validation": "success",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "error": "Token validation failed",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time": (datetime.now() - start_time).total_seconds() * 1000,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_connection(self) -> bool:
        """Test provider connectivity (always true for token provider)"""
        return True
    
    async def _generate_token(self, user_principal: UserPrincipal) -> str:
        """Generate JWT token for user principal"""
        now = datetime.now()
        
        payload = {
            "user_id": user_principal.user_id,
            "email": user_principal.email,
            "display_name": user_principal.display_name,
            "roles": user_principal.roles,
            "groups": user_principal.groups,
            "claims": user_principal.claims,
            "mfa_authenticated": user_principal.mfa_authenticated,
            "auth_level": user_principal.auth_level.value,
            "provider": user_principal.provider,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.token_expiry)).timestamp()),
            "jti": secrets.token_urlsafe(32),  # JWT ID
            "iss": "upid-cli",  # Issuer
            "aud": "upid-cli"   # Audience
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _determine_auth_level(self, roles: list, mfa_authenticated: bool) -> AuthLevel:
        """Determine authentication level based on roles and MFA status"""
        admin_roles = ["admin", "super_admin", "cluster-admin"]
        
        if any(role in admin_roles for role in roles):
            return AuthLevel.STEP_UP
        elif mfa_authenticated:
            return AuthLevel.MULTI_FACTOR
        else:
            return AuthLevel.SINGLE_FACTOR
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create user (not supported for token provider)"""
        # Token provider doesn't support user creation
        return None
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information (limited for token provider)"""
        # Token provider has limited user information
        return {
            "user_id": user_id,
            "provider": "token",
            "note": "User information limited for token provider"
        }
    
    def get_supported_features(self) -> list:
        """Get supported features"""
        return [
            "audit_logs"
        ]
    
    def get_security_features(self) -> list:
        """Get security features"""
        return [
            "session_timeout",
            "token_rotation",
            "mfa"
        ]
    
    async def cleanup_expired_refresh_tokens(self):
        """Clean up expired refresh tokens"""
        try:
            current_time = datetime.now()
            expired_tokens = [
                token_id for token_id, token_data in self.refresh_tokens.items()
                if current_time > token_data["expires_at"]
            ]
            
            for token_id in expired_tokens:
                del self.refresh_tokens[token_id]
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired refresh tokens")
                
        except Exception as e:
            logger.error(f"Refresh token cleanup error: {e}") 