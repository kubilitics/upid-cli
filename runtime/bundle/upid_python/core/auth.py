"""
Authentication management for UPID CLI
Handles login, logout, token management, and enterprise SSO
"""

import os
import json
import time
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import jwt
from enum import Enum


class Permission(Enum):
    """User permissions"""
    READ_CLUSTERS = "read:clusters"
    WRITE_CLUSTERS = "write:clusters"
    DELETE_CLUSTERS = "delete:clusters"
    READ_ANALYSIS = "read:analysis"
    WRITE_ANALYSIS = "write:analysis"
    READ_OPTIMIZATION = "read:optimization"
    WRITE_OPTIMIZATION = "write:optimization"
    READ_REPORTS = "read:reports"
    WRITE_REPORTS = "write:reports"
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    ADMIN = "admin"


class Role(Enum):
    """User roles"""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class UserPermissions:
    """User permissions and roles"""
    user_id: str
    email: str
    roles: List[Role]
    permissions: List[Permission]
    organization_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def has_role(self, role: Role) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return Role.ADMIN in self.roles or Role.SUPER_ADMIN in self.roles


@dataclass
class OIDCProvider:
    """OIDC provider configuration"""
    name: str
    issuer_url: str
    client_id: str
    client_secret: Optional[str] = None
    scopes: List[str] = None
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = ["openid", "profile", "email"]


@dataclass
class AuthToken:
    """Authentication token data"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    organization_id: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_expiring_soon(self, minutes: int = 5) -> bool:
        """Check if token is expiring soon"""
        if self.expires_at is None:
            return False
        return datetime.now() > (self.expires_at - timedelta(minutes=minutes))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'scope': self.scope,
            'user_id': self.user_id,
            'email': self.email,
            'organization_id': self.organization_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthToken':
        """Create from dictionary"""
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        return cls(
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token'),
            token_type=data.get('token_type', 'Bearer'),
            expires_at=expires_at,
            scope=data.get('scope'),
            user_id=data.get('user_id'),
            email=data.get('email'),
            organization_id=data.get('organization_id')
        )


class OIDCManager:
    """OIDC provider manager"""
    
    def __init__(self, config):
        self.config = config
        self.providers: Dict[str, OIDCProvider] = {}
        self._load_providers()
    
    def _load_providers(self):
        """Load OIDC providers from config"""
        # Default providers
        self.providers = {
            "google": OIDCProvider(
                name="Google",
                issuer_url="https://accounts.google.com",
                client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
                authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
                jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
            ),
            "github": OIDCProvider(
                name="GitHub",
                issuer_url="https://github.com",
                client_id=os.getenv("GITHUB_CLIENT_ID", ""),
                client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
                authorization_endpoint="https://github.com/login/oauth/authorize",
                token_endpoint="https://github.com/login/oauth/access_token",
                userinfo_endpoint="https://api.github.com/user"
            ),
            "azure": OIDCProvider(
                name="Azure AD",
                issuer_url=os.getenv("AZURE_ISSUER_URL", ""),
                client_id=os.getenv("AZURE_CLIENT_ID", ""),
                client_secret=os.getenv("AZURE_CLIENT_SECRET", ""),
                scopes=["openid", "profile", "email", "User.Read"]
            )
        }
    
    def get_provider(self, name: str) -> Optional[OIDCProvider]:
        """Get OIDC provider by name"""
        return self.providers.get(name)
    
    def discover_provider(self, issuer_url: str) -> Optional[OIDCProvider]:
        """Discover OIDC provider configuration"""
        try:
            response = requests.get(f"{issuer_url}/.well-known/openid_configuration")
            if response.status_code == 200:
                config = response.json()
                return OIDCProvider(
                    name="Custom",
                    issuer_url=issuer_url,
                    client_id=os.getenv("OIDC_CLIENT_ID", ""),
                    client_secret=os.getenv("OIDC_CLIENT_SECRET", ""),
                    authorization_endpoint=config.get("authorization_endpoint"),
                    token_endpoint=config.get("token_endpoint"),
                    userinfo_endpoint=config.get("userinfo_endpoint"),
                    jwks_uri=config.get("jwks_uri")
                )
        except Exception as e:
            if self.config.debug:
                print(f"OIDC discovery error: {e}")
        return None


class RBACManager:
    """Role-based access control manager"""
    
    def __init__(self, config):
        self.config = config
        self.permissions: Dict[str, UserPermissions] = {}
        self._load_permissions()
    
    def _load_permissions(self):
        """Load user permissions from config or API"""
        # Default permissions for demo
        self.permissions = {
            "admin@upid.io": UserPermissions(
                user_id="admin-001",
                email="admin@upid.io",
                roles=[Role.ADMIN],
                permissions=[p for p in Permission],
                organization_id="org-001",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            "user@upid.io": UserPermissions(
                user_id="user-001",
                email="user@upid.io",
                roles=[Role.OPERATOR],
                permissions=[
                    Permission.READ_CLUSTERS,
                    Permission.READ_ANALYSIS,
                    Permission.READ_OPTIMIZATION,
                    Permission.READ_REPORTS
                ],
                organization_id="org-001",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            "viewer@upid.io": UserPermissions(
                user_id="viewer-001",
                email="viewer@upid.io",
                roles=[Role.VIEWER],
                permissions=[
                    Permission.READ_CLUSTERS,
                    Permission.READ_ANALYSIS,
                    Permission.READ_REPORTS
                ],
                organization_id="org-001",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        }
    
    def get_user_permissions(self, email: str) -> Optional[UserPermissions]:
        """Get user permissions by email"""
        return self.permissions.get(email)
    
    def check_permission(self, email: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user_perms = self.get_user_permissions(email)
        if not user_perms:
            return False
        return user_perms.has_permission(permission)
    
    def check_role(self, email: str, role: Role) -> bool:
        """Check if user has specific role"""
        user_perms = self.get_user_permissions(email)
        if not user_perms:
            return False
        return user_perms.has_role(role)
    
    def is_admin(self, email: str) -> bool:
        """Check if user is admin"""
        user_perms = self.get_user_permissions(email)
        if not user_perms:
            return False
        return user_perms.is_admin()


class SessionManager:
    """Session management for authentication"""
    
    def __init__(self, config):
        self.config = config
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, user_id: str, email: str, token: str) -> str:
        """Create new session"""
        session_id = f"session_{int(time.time())}_{user_id}"
        self.sessions[session_id] = {
            "user_id": user_id,
            "email": email,
            "token": token,
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        # Check if session is expired
        if datetime.now() > session["created_at"] + timedelta(seconds=self.session_timeout):
            self.sessions.pop(session_id, None)
            return None
        
        # Update last activity
        session["last_activity"] = datetime.now()
        return session
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time > session["created_at"] + timedelta(seconds=self.session_timeout)
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]


class AuthManager:
    """Enhanced authentication manager for UPID CLI"""
    
    def __init__(self, config):
        self.config = config
        self.token: Optional[AuthToken] = None
        self.auth_file = Path.home() / ".upid" / "auth.json"
        self.auth_file.parent.mkdir(exist_ok=True)
        self.oidc_manager = OIDCManager(config)
        self.rbac_manager = RBACManager(config)
        self.session_manager = SessionManager(config)
        self._load_token()
    
    def _load_token(self):
        """Load authentication token from file"""
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r') as f:
                    data = json.load(f)
                    self.token = AuthToken.from_dict(data)
            except Exception as e:
                if self.config.debug:
                    print(f"Warning: Failed to load auth token: {e}")
                self.token = None
    
    def _save_token(self):
        """Save authentication token to file"""
        if self.token:
            try:
                with open(self.auth_file, 'w') as f:
                    json.dump(self.token.to_dict(), f, indent=2)
            except Exception as e:
                if self.config.debug:
                    print(f"Warning: Failed to save auth token: {e}")
    
    def _clear_token(self):
        """Clear authentication token"""
        self.token = None
        if self.auth_file.exists():
            try:
                self.auth_file.unlink()
            except Exception:
                pass
    
    def login(self, email: str, password: str, server: Optional[str] = None) -> bool:
        """
        Login with email and password
        
        Args:
            email: User email
            password: User password
            server: Optional custom server URL
            
        Returns:
            bool: True if login successful
        """
        try:
            # Use custom server if provided, otherwise use config
            api_url = server or self.config.api_url
            login_url = f"{api_url}/auth/login"
            
            # Prepare login data
            login_data = {
                "email": email,
                "password": password
            }
            
            # Make login request
            response = requests.post(
                login_url,
                json=login_data,
                timeout=self.config.api_timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse token data
                expires_at = None
                if data.get('expires_in'):
                    expires_at = datetime.now() + timedelta(seconds=data['expires_in'])
                
                self.token = AuthToken(
                    access_token=data['access_token'],
                    refresh_token=data.get('refresh_token'),
                    token_type=data.get('token_type', 'Bearer'),
                    expires_at=expires_at,
                    scope=data.get('scope'),
                    user_id=data.get('user_id'),
                    email=data.get('email'),
                    organization_id=data.get('organization_id')
                )
                
                # Save token
                self._save_token()
                
                # Update config
                self.config.auth_token = self.token.access_token
                self.config.save()
                
                return True
            else:
                if self.config.debug:
                    print(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            if self.config.debug:
                print(f"Login error: {e}")
            return False
    
    def login_with_token(self, token: str, server: Optional[str] = None) -> bool:
        """
        Login with existing token
        
        Args:
            token: Authentication token
            server: Optional custom server URL
            
        Returns:
            bool: True if token is valid
        """
        try:
            # Use custom server if provided, otherwise use config
            api_url = server or self.config.api_url
            verify_url = f"{api_url}/auth/verify"
            
            # Verify token
            response = requests.get(
                verify_url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.token = AuthToken(
                    access_token=token,
                    token_type="Bearer",
                    user_id=data.get('user_id'),
                    email=data.get('email'),
                    organization_id=data.get('organization_id')
                )
                
                # Save token
                self._save_token()
                
                # Update config
                self.config.auth_token = self.token.access_token
                self.config.save()
                
                return True
            else:
                return False
                
        except Exception as e:
            if self.config.debug:
                print(f"Token verification error: {e}")
            return False
    
    def sso_login(self, provider: str = "google") -> bool:
        """
        Login with SSO provider
        
        Args:
            provider: SSO provider (google, github, azure, okta)
            
        Returns:
            bool: True if SSO login successful
        """
        try:
            api_url = self.config.api_url
            sso_url = f"{api_url}/auth/sso/{provider}"
            
            # For CLI, we'll use a device flow approach
            response = requests.post(
                sso_url,
                json={"client_type": "cli"},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display device code to user
                print(f"🔐 SSO Login Required")
                print(f"Please visit: {data['verification_uri']}")
                print(f"Enter code: {data['user_code']}")
                print(f"Waiting for authentication...")
                
                # Poll for completion
                device_code = data['device_code']
                interval = data.get('interval', 5)
                
                while True:
                    time.sleep(interval)
                    
                    poll_response = requests.post(
                        f"{api_url}/auth/sso/{provider}/poll",
                        json={"device_code": device_code},
                        timeout=self.config.api_timeout
                    )
                    
                    if poll_response.status_code == 200:
                        token_data = poll_response.json()
                        
                        # Parse token data
                        expires_at = None
                        if token_data.get('expires_in'):
                            expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
                        
                        self.token = AuthToken(
                            access_token=token_data['access_token'],
                            refresh_token=token_data.get('refresh_token'),
                            token_type=token_data.get('token_type', 'Bearer'),
                            expires_at=expires_at,
                            scope=token_data.get('scope'),
                            user_id=token_data.get('user_id'),
                            email=token_data.get('email'),
                            organization_id=token_data.get('organization_id')
                        )
                        
                        # Save token
                        self._save_token()
                        
                        # Update config
                        self.config.auth_token = self.token.access_token
                        self.config.save()
                        
                        print("✅ SSO login successful!")
                        return True
                    
                    elif poll_response.status_code == 400:
                        error_data = poll_response.json()
                        if error_data.get('error') == 'authorization_pending':
                            continue
                        else:
                            print(f"❌ SSO login failed: {error_data.get('error_description', 'Unknown error')}")
                            return False
                    
                    else:
                        print("❌ SSO login failed")
                        return False
            else:
                print(f"❌ Failed to initiate SSO login: {response.status_code}")
                return False
                
        except Exception as e:
            if self.config.debug:
                print(f"SSO login error: {e}")
            return False
    
    def logout(self) -> bool:
        """
        Logout and clear authentication
        
        Returns:
            bool: True if logout successful
        """
        try:
            if self.token and self.token.access_token:
                # Revoke token on server
                api_url = self.config.api_url
                logout_url = f"{api_url}/auth/logout"
                
                response = requests.post(
                    logout_url,
                    headers={"Authorization": f"Bearer {self.token.access_token}"},
                    timeout=self.config.api_timeout
                )
                
                # Clear token regardless of server response
                self._clear_token()
                
                # Update config
                self.config.auth_token = None
                self.config.save()
                
                return True
            else:
                # No token to logout
                return True
                
        except Exception as e:
            if self.config.debug:
                print(f"Logout error: {e}")
            # Clear token even if server request fails
            self._clear_token()
            return True
    
    def refresh_token(self) -> bool:
        """
        Refresh authentication token
        
        Returns:
            bool: True if refresh successful
        """
        try:
            if not self.token or not self.token.refresh_token:
                return False
            
            api_url = self.config.api_url
            refresh_url = f"{api_url}/auth/refresh"
            
            response = requests.post(
                refresh_url,
                json={"refresh_token": self.token.refresh_token},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse token data
                expires_at = None
                if data.get('expires_in'):
                    expires_at = datetime.now() + timedelta(seconds=data['expires_in'])
                
                self.token = AuthToken(
                    access_token=data['access_token'],
                    refresh_token=data.get('refresh_token', self.token.refresh_token),
                    token_type=data.get('token_type', 'Bearer'),
                    expires_at=expires_at,
                    scope=data.get('scope'),
                    user_id=data.get('user_id'),
                    email=data.get('email'),
                    organization_id=data.get('organization_id')
                )
                
                # Save token
                self._save_token()
                
                # Update config
                self.config.auth_token = self.token.access_token
                self.config.save()
                
                return True
            else:
                return False
                
        except Exception as e:
            if self.config.debug:
                print(f"Token refresh error: {e}")
            return False
    
    def get_token(self) -> Optional[str]:
        """
        Get current authentication token
        
        Returns:
            str: Current token or None if not authenticated
        """
        if not self.token:
            return None
        
        # Check if token is expired
        if self.token.is_expired():
            # Try to refresh token
            if not self.refresh_token():
                # Refresh failed, clear token
                self._clear_token()
                return None
        
        return self.token.access_token
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            bool: True if authenticated
        """
        return self.get_token() is not None
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information
        
        Returns:
            dict: User information or None if not authenticated
        """
        try:
            if not self.is_authenticated():
                return None
            
            api_url = self.config.api_url
            user_url = f"{api_url}/auth/user"
            
            response = requests.get(
                user_url,
                headers={"Authorization": f"Bearer {self.get_token()}"},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            if self.config.debug:
                print(f"Get user info error: {e}")
            return None
    
    def get_organizations(self) -> List[Dict[str, Any]]:
        """
        Get user's organizations
        
        Returns:
            list: List of organizations
        """
        try:
            if not self.is_authenticated():
                return []
            
            api_url = self.config.api_url
            orgs_url = f"{api_url}/auth/organizations"
            
            response = requests.get(
                orgs_url,
                headers={"Authorization": f"Bearer {self.get_token()}"},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                return response.json().get('organizations', [])
            else:
                return []
                
        except Exception as e:
            if self.config.debug:
                print(f"Get organizations error: {e}")
            return []
    
    def switch_organization(self, org_id: str) -> bool:
        """
        Switch to a different organization
        
        Args:
            org_id: Organization ID
            
        Returns:
            bool: True if switch successful
        """
        try:
            if not self.is_authenticated():
                return False
            
            api_url = self.config.api_url
            switch_url = f"{api_url}/auth/organizations/{org_id}/switch"
            
            response = requests.post(
                switch_url,
                headers={"Authorization": f"Bearer {self.get_token()}"},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update token with new organization context
                if self.token:
                    self.token.organization_id = org_id
                    self._save_token()
                
                # Update config
                self.config.enterprise_org_id = org_id
                self.config.save()
                
                return True
            else:
                return False
                
        except Exception as e:
            if self.config.debug:
                print(f"Switch organization error: {e}")
            return False
    
    def oidc_login(self, provider_name: str) -> bool:
        """
        Login with OIDC provider
        
        Args:
            provider_name: OIDC provider name (google, github, azure, custom)
            
        Returns:
            bool: True if OIDC login successful
        """
        provider = self.oidc_manager.get_provider(provider_name)
        if not provider:
            print(f"❌ OIDC provider '{provider_name}' not found")
            return False
        
        try:
            # Generate authorization URL
            auth_url = f"{provider.authorization_endpoint}?"
            auth_url += f"client_id={provider.client_id}&"
            auth_url += f"response_type=code&"
            auth_url += f"scope={' '.join(provider.scopes)}&"
            auth_url += f"redirect_uri={self.config.api_url}/auth/oidc/callback"
            
            print(f"🔐 OIDC Login Required")
            print(f"Please visit: {auth_url}")
            print(f"After authentication, you'll be redirected back to the CLI")
            
            # For CLI, we'll use a simplified flow
            # In production, this would use a proper OIDC flow
            return self._handle_oidc_callback(provider)
            
        except Exception as e:
            if self.config.debug:
                print(f"OIDC login error: {e}")
            return False
    
    def _handle_oidc_callback(self, provider: OIDCProvider) -> bool:
        """Handle OIDC callback (simplified for CLI)"""
        try:
            # Simulate OIDC callback for demo
            if self.config.mock_mode:
                # Mock OIDC response
                token_data = {
                    "access_token": f"oidc_token_{int(time.time())}",
                    "refresh_token": f"oidc_refresh_{int(time.time())}",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": " ".join(provider.scopes),
                    "user_id": "oidc_user_001",
                    "email": "user@example.com",
                    "organization_id": "org-001"
                }
                
                # Parse token data
                expires_at = None
                if token_data.get('expires_in'):
                    expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
                
                self.token = AuthToken(
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_at=expires_at,
                    scope=token_data.get('scope'),
                    user_id=token_data.get('user_id'),
                    email=token_data.get('email'),
                    organization_id=token_data.get('organization_id')
                )
                
                # Save token
                self._save_token()
                
                # Update config
                self.config.auth_token = self.token.access_token
                self.config.save()
                
                print("✅ OIDC login successful!")
                return True
            else:
                # Real OIDC flow would be implemented here
                print("❌ Real OIDC flow not implemented for CLI")
                return False
                
        except Exception as e:
            if self.config.debug:
                print(f"OIDC callback error: {e}")
            return False
    
    def check_permission(self, permission: Permission) -> bool:
        """
        Check if current user has specific permission
        
        Args:
            permission: Permission to check
            
        Returns:
            bool: True if user has permission
        """
        if not self.is_authenticated():
            return False
        
        user_info = self.get_user_info()
        if not user_info:
            return False
        
        email = user_info.get('email')
        if not email:
            return False
        
        return self.rbac_manager.check_permission(email, permission)
    
    def check_role(self, role: Role) -> bool:
        """
        Check if current user has specific role
        
        Args:
            role: Role to check
            
        Returns:
            bool: True if user has role
        """
        if not self.is_authenticated():
            return False
        
        user_info = self.get_user_info()
        if not user_info:
            return False
        
        email = user_info.get('email')
        if not email:
            return False
        
        return self.rbac_manager.check_role(email, role)
    
    def is_admin(self) -> bool:
        """
        Check if current user is admin
        
        Returns:
            bool: True if user is admin
        """
        if not self.is_authenticated():
            return False
        
        user_info = self.get_user_info()
        if not user_info:
            return False
        
        email = user_info.get('email')
        if not email:
            return False
        
        return self.rbac_manager.is_admin(email)
    
    def create_session(self, user_id: str, email: str) -> str:
        """
        Create new session for user
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            str: Session ID
        """
        if not self.is_authenticated():
            return None
        
        return self.session_manager.create_session(
            user_id, email, self.token.access_token
        )
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Optional[Dict]: Session data or None
        """
        return self.session_manager.get_session(session_id)
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate session
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if session invalidated
        """
        return self.session_manager.invalidate_session(session_id)
    
    def cleanup_sessions(self):
        """Clean up expired sessions"""
        self.session_manager.cleanup_expired_sessions()
    
    def get_user_permissions(self) -> Optional[UserPermissions]:
        """
        Get current user permissions
        
        Returns:
            Optional[UserPermissions]: User permissions or None
        """
        if not self.is_authenticated():
            return None
        
        user_info = self.get_user_info()
        if not user_info:
            return None
        
        email = user_info.get('email')
        if not email:
            return None
        
        return self.rbac_manager.get_user_permissions(email) 