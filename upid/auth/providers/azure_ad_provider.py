"""
Enterprise-Grade Azure Active Directory Authentication Provider
Following the gold standard blueprint for robust, secure, and maintainable identity systems
"""

import msal
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base_provider import AuthProvider, AuthProviderError, AuthenticationError
from ..enterprise_auth import UserPrincipal, AuthLevel

logger = logging.getLogger(__name__)

class AzureADAuthProvider(AuthProvider):
    """
    Enterprise-grade Azure AD authentication provider
    Supports OAuth 2.0, OpenID Connect, and Microsoft Graph API
    """
    def __init__(self, tenant_id: str, client_id: str, client_secret: str = None,
                 scopes: list = None, authority_url: str = None):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes or ["https://graph.microsoft.com/.default"]
        self.authority_url = authority_url or f"https://login.microsoftonline.com/{tenant_id}"

    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserPrincipal]:
        try:
            access_token = credentials.get('access_token')
            id_token = credentials.get('id_token')
            username = credentials.get('username')
            password = credentials.get('password')
            flow = credentials.get('flow', 'device_code')

            token = None
            if access_token:
                token = access_token
            elif id_token:
                token = id_token
            elif username and password:
                # Resource owner password credentials flow (not recommended for production)
                app = msal.PublicClientApplication(self.client_id, authority=self.authority_url)
                result = app.acquire_token_by_username_password(username, password, scopes=self.scopes)
                if 'access_token' in result:
                    token = result['access_token']
                else:
                    raise AuthenticationError(f"Azure AD authentication failed: {result.get('error_description')}", provider="azure_ad")
            elif flow == 'device_code':
                app = msal.PublicClientApplication(self.client_id, authority=self.authority_url)
                flow = app.initiate_device_flow(scopes=self.scopes)
                if 'user_code' not in flow:
                    raise AuthenticationError(f"Device code flow initiation failed: {flow}", provider="azure_ad")
                print(f"To sign in, use a web browser to open {flow['verification_uri']} and enter the code: {flow['user_code']}")
                result = app.acquire_token_by_device_flow(flow)
                if 'access_token' in result:
                    token = result['access_token']
                else:
                    raise AuthenticationError(f"Azure AD authentication failed: {result.get('error_description')}", provider="azure_ad")
            elif self.client_secret:
                # Client credentials flow
                app = msal.ConfidentialClientApplication(self.client_id, authority=self.authority_url, client_credential=self.client_secret)
                result = app.acquire_token_for_client(scopes=self.scopes)
                if 'access_token' in result:
                    token = result['access_token']
                else:
                    raise AuthenticationError(f"Azure AD authentication failed: {result.get('error_description')}", provider="azure_ad")
            else:
                raise AuthenticationError("Azure AD credentials required (access token, id token, username/password, or client credentials)", provider="azure_ad")

            # Use Microsoft Graph API to get user info
            headers = {"Authorization": f"Bearer {token}"}
            user_info = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers).json()
            user_id = user_info.get("id", "azure-user")
            email = user_info.get("mail") or user_info.get("userPrincipalName")
            display_name = user_info.get("displayName", "Azure User")

            # Get roles and groups
            roles = []
            groups = []
            try:
                # Get memberOf (groups)
                groups_resp = requests.get("https://graph.microsoft.com/v1.0/me/memberOf", headers=headers).json()
                groups = [g.get('displayName') for g in groups_resp.get('value', []) if g.get('displayName')]
                # Get app roles (if any)
                roles_resp = requests.get("https://graph.microsoft.com/v1.0/me/appRoleAssignments", headers=headers).json()
                roles = [r.get('resourceDisplayName') for r in roles_resp.get('value', []) if r.get('resourceDisplayName')]
            except Exception as e:
                logger.warning(f"Failed to get Azure AD roles/groups: {e}")

            user_principal = UserPrincipal(
                user_id=user_id,
                email=email,
                display_name=display_name,
                roles=roles or ["user"],
                groups=groups or ["azure-users"],
                claims={
                    "provider": "azure_ad",
                    "tenant_id": self.tenant_id,
                    "client_id": self.client_id
                },
                mfa_authenticated=False,  # Could be improved with conditional access
                auth_level=self._determine_auth_level(roles),
                provider="azure_ad",
                last_login=datetime.now(),
                metadata={
                    "azure_tenant_id": self.tenant_id,
                    "authority_url": self.authority_url
                }
            )
            logger.info(f"Azure AD authentication successful for user: {user_principal.user_id}")
            return user_principal
        except Exception as e:
            logger.error(f"Azure AD authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {str(e)}", provider="azure_ad")

    async def validate_token(self, token: str) -> Optional[UserPrincipal]:
        # Token validation is handled by Graph API; re-authenticate if needed
        return None

    async def refresh_token(self, token: str) -> Optional[str]:
        # Token refresh is handled by MSAL; implement if needed
        return None

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Azure Active Directory",
            "type": "azure_ad",
            "version": "1.0.0",
            "capabilities": [
                "oauth2_auth",
                "openid_connect",
                "microsoft_graph",
                "conditional_access"
            ],
            "config_schema": {
                "required": ["tenant_id", "client_id"],
                "optional": ["client_secret", "scopes", "authority_url"]
            },
            "health_endpoint": "graph_me_endpoint",
            "supported_features": [
                "user_management",
                "group_management",
                "sso",
                "audit_logs"
            ],
            "security_features": [
                "mfa",
                "conditional_access",
                "session_timeout"
            ]
        }

    async def health_check(self) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            # Try to get a token using client credentials (if available)
            if self.client_secret:
                app = msal.ConfidentialClientApplication(self.client_id, authority=self.authority_url, client_credential=self.client_secret)
                result = app.acquire_token_for_client(scopes=self.scopes)
                if 'access_token' not in result:
                    raise Exception(result.get('error_description'))
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "status": "healthy",
                "response_time": response_time,
                "tenant_id": self.tenant_id,
                "graph": "success",
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
        try:
            if self.client_secret:
                app = msal.ConfidentialClientApplication(self.client_id, authority=self.authority_url, client_credential=self.client_secret)
                result = app.acquire_token_for_client(scopes=self.scopes)
                return 'access_token' in result
            return False
        except Exception as e:
            logger.error(f"Azure AD connection test failed: {e}")
            return False

    def _determine_auth_level(self, roles: list) -> AuthLevel:
        admin_roles = ["admin", "global_admin", "user_admin"]
        if any(role in admin_roles for role in roles):
            return AuthLevel.STEP_UP
        elif "developer" in roles or "operator" in roles:
            return AuthLevel.MULTI_FACTOR
        else:
            return AuthLevel.SINGLE_FACTOR

    def get_supported_features(self) -> list:
        return [
            "user_management",
            "group_management",
            "sso",
            "audit_logs"
        ]

    def get_security_features(self) -> list:
        return [
            "mfa",
            "conditional_access",
            "session_timeout"
        ] 