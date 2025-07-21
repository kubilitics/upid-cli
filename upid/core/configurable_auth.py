"""
Configurable Authentication System for UPID CLI
Allows organizations to use their preferred authentication methods via environment variables
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import subprocess
import logging

from .oidc_auth import OIDCAuthenticator, OIDCConfig
from .saml_auth import SAMLAuthenticator, SAMLConfig
from .ldap_auth import LDAPAuthenticator, LDAPConfig

logger = logging.getLogger(__name__)

@dataclass
class AuthConfig:
    """Authentication configuration from environment variables"""
    auth_type: str  # 'kubectl', 'oidc', 'saml', 'ldap', 'custom'
    auth_endpoint: Optional[str] = None
    auth_client_id: Optional[str] = None
    auth_client_secret: Optional[str] = None
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None
    auth_cert_path: Optional[str] = None
    auth_key_path: Optional[str] = None
    auth_ca_path: Optional[str] = None
    auth_scope: Optional[str] = None
    auth_redirect_uri: Optional[str] = None
    auth_provider: Optional[str] = None  # 'azure', 'aws', 'gcp', 'okta', 'auth0', etc.
    auth_tenant_id: Optional[str] = None
    auth_audience: Optional[str] = None
    auth_issuer: Optional[str] = None
    auth_custom_headers: Optional[Dict[str, str]] = None
    auth_custom_params: Optional[Dict[str, str]] = None

class ConfigurableAuthenticator:
    """
    Configurable authentication system that supports multiple authentication methods
    via environment variables, with kubectl as the default for individual users
    """
    
    def __init__(self):
        self.config = self._load_auth_config()
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Initialize specialized authenticators
        self.oidc_auth = None
        self.saml_auth = None
        self.ldap_auth = None
        
        if self.config.auth_type == 'oidc':
            oidc_config = OIDCConfig(
                endpoint=self.config.auth_endpoint,
                client_id=self.config.auth_client_id,
                client_secret=self.config.auth_client_secret,
                scope=self.config.auth_scope,
                audience=self.config.auth_audience,
                redirect_uri=self.config.auth_redirect_uri,
                provider=self.config.auth_provider,
                tenant_id=self.config.auth_tenant_id
            )
            self.oidc_auth = OIDCAuthenticator(oidc_config)
        
        elif self.config.auth_type == 'saml':
            saml_config = SAMLConfig(
                endpoint=self.config.auth_endpoint,
                client_id=self.config.auth_client_id,
                client_secret=self.config.auth_client_secret,
                provider=self.config.auth_provider,
                tenant_id=self.config.auth_tenant_id
            )
            self.saml_auth = SAMLAuthenticator(saml_config)
        
        elif self.config.auth_type == 'ldap':
            ldap_config = LDAPConfig(
                endpoint=self.config.auth_endpoint,
                username=self.config.auth_username,
                password=self.config.auth_password,
                provider=self.config.auth_provider
            )
            self.ldap_auth = LDAPAuthenticator(ldap_config)
    
    def _load_auth_config(self) -> AuthConfig:
        """Load authentication configuration from environment variables"""
        
        # Default to kubectl authentication for individual users
        auth_type = os.getenv('UPID_AUTH_TYPE', 'kubectl')
        
        # Load configuration based on auth type
        if auth_type == 'kubectl':
            return AuthConfig(
                auth_type='kubectl',
                auth_endpoint=None,
                auth_client_id=None,
                auth_client_secret=None,
                auth_username=None,
                auth_password=None,
                auth_token=None,
                auth_cert_path=os.getenv('UPID_AUTH_CERT_PATH'),
                auth_key_path=os.getenv('UPID_AUTH_KEY_PATH'),
                auth_ca_path=os.getenv('UPID_AUTH_CA_PATH')
            )
        
        elif auth_type == 'oidc':
            return AuthConfig(
                auth_type='oidc',
                auth_endpoint=os.getenv('UPID_AUTH_ENDPOINT'),
                auth_client_id=os.getenv('UPID_AUTH_CLIENT_ID'),
                auth_client_secret=os.getenv('UPID_AUTH_CLIENT_SECRET'),
                auth_username=os.getenv('UPID_AUTH_USERNAME'),
                auth_password=os.getenv('UPID_AUTH_PASSWORD'),
                auth_token=os.getenv('UPID_AUTH_TOKEN'),
                auth_scope=os.getenv('UPID_AUTH_SCOPE', 'openid profile email'),
                auth_redirect_uri=os.getenv('UPID_AUTH_REDIRECT_URI'),
                auth_provider=os.getenv('UPID_AUTH_PROVIDER'),
                auth_audience=os.getenv('UPID_AUTH_AUDIENCE'),
                auth_issuer=os.getenv('UPID_AUTH_ISSUER')
            )
        
        elif auth_type == 'saml':
            return AuthConfig(
                auth_type='saml',
                auth_endpoint=os.getenv('UPID_AUTH_ENDPOINT'),
                auth_client_id=os.getenv('UPID_AUTH_CLIENT_ID'),
                auth_client_secret=os.getenv('UPID_AUTH_CLIENT_SECRET'),
                auth_username=os.getenv('UPID_AUTH_USERNAME'),
                auth_password=os.getenv('UPID_AUTH_PASSWORD'),
                auth_token=os.getenv('UPID_AUTH_TOKEN'),
                auth_provider=os.getenv('UPID_AUTH_PROVIDER'),
                auth_tenant_id=os.getenv('UPID_AUTH_TENANT_ID')
            )
        
        elif auth_type == 'ldap':
            return AuthConfig(
                auth_type='ldap',
                auth_endpoint=os.getenv('UPID_AUTH_ENDPOINT'),
                auth_username=os.getenv('UPID_AUTH_USERNAME'),
                auth_password=os.getenv('UPID_AUTH_PASSWORD'),
                auth_provider=os.getenv('UPID_AUTH_PROVIDER')
            )
        
        elif auth_type == 'custom':
            # Parse custom headers and parameters from JSON strings
            custom_headers = {}
            custom_params = {}
            
            if os.getenv('UPID_AUTH_CUSTOM_HEADERS'):
                try:
                    custom_headers = json.loads(os.getenv('UPID_AUTH_CUSTOM_HEADERS'))
                except json.JSONDecodeError:
                    logger.warning("Invalid UPID_AUTH_CUSTOM_HEADERS JSON")
            
            if os.getenv('UPID_AUTH_CUSTOM_PARAMS'):
                try:
                    custom_params = json.loads(os.getenv('UPID_AUTH_CUSTOM_PARAMS'))
                except json.JSONDecodeError:
                    logger.warning("Invalid UPID_AUTH_CUSTOM_PARAMS JSON")
            
            return AuthConfig(
                auth_type='custom',
                auth_endpoint=os.getenv('UPID_AUTH_ENDPOINT'),
                auth_client_id=os.getenv('UPID_AUTH_CLIENT_ID'),
                auth_client_secret=os.getenv('UPID_AUTH_CLIENT_SECRET'),
                auth_username=os.getenv('UPID_AUTH_USERNAME'),
                auth_password=os.getenv('UPID_AUTH_PASSWORD'),
                auth_token=os.getenv('UPID_AUTH_TOKEN'),
                auth_custom_headers=custom_headers,
                auth_custom_params=custom_params
            )
        
        else:
            raise ValueError(f"Unsupported authentication type: {auth_type}")
    
    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate using the configured method
        """
        try:
            if self.config.auth_type == 'kubectl':
                return self._authenticate_kubectl()
            elif self.config.auth_type == 'oidc':
                return self._authenticate_oidc()
            elif self.config.auth_type == 'saml':
                return self._authenticate_saml()
            elif self.config.auth_type == 'ldap':
                return self._authenticate_ldap()
            elif self.config.auth_type == 'custom':
                return self._authenticate_custom()
            else:
                raise ValueError(f"Unsupported authentication type: {self.config.auth_type}")
        
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'auth_type': self.config.auth_type
            }
    
    def _authenticate_kubectl(self) -> Dict[str, Any]:
        """
        Authenticate using kubectl (default for individual users)
        """
        try:
            # Check if kubectl is available
            result = subprocess.run(['kubectl', 'version', '--client'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'kubectl not available or not configured',
                    'auth_type': 'kubectl'
                }
            
            # Test cluster connection
            result = subprocess.run(['kubectl', 'cluster-info'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Failed to connect to Kubernetes cluster',
                    'auth_type': 'kubectl'
                }
            
            # Get current context
            result = subprocess.run(['kubectl', 'config', 'current-context'], 
                                  capture_output=True, text=True, timeout=10)
            
            context = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            # Get user info
            result = subprocess.run(['kubectl', 'whoami'], 
                                  capture_output=True, text=True, timeout=10)
            
            user = result.stdout.strip() if result.returncode == 0 else 'unknown'
            
            return {
                'success': True,
                'auth_type': 'kubectl',
                'context': context,
                'user': user,
                'method': 'kubectl'
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'kubectl command timed out',
                'auth_type': 'kubectl'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'auth_type': 'kubectl'
            }
    
    def _authenticate_oidc(self) -> Dict[str, Any]:
        """
        Authenticate using OIDC with device code flow
        """
        if not self.oidc_auth:
            return {
                'success': False,
                'error': 'OIDC authenticator not initialized',
                'auth_type': 'oidc'
            }
        
        try:
            # Try device code flow first (recommended for CLI)
            token_response = self.oidc_auth.authenticate_device_code()
            
            if token_response:
                return {
                    'success': True,
                    'auth_type': 'oidc',
                    'token': token_response.access_token,
                    'token_type': token_response.token_type,
                    'expires_in': token_response.expires_in,
                    'method': 'oidc_device_code'
                }
            else:
                # Fall back to client credentials if device code fails
                token_response = self.oidc_auth.authenticate_client_credentials()
                
                if token_response:
                    return {
                        'success': True,
                        'auth_type': 'oidc',
                        'token': token_response.access_token,
                        'token_type': token_response.token_type,
                        'expires_in': token_response.expires_in,
                        'method': 'oidc_client_credentials'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'OIDC authentication failed',
                        'auth_type': 'oidc'
                    }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'auth_type': 'oidc'
            }
    
    def _authenticate_saml(self) -> Dict[str, Any]:
        """
        Authenticate using SAML
        """
        if not self.saml_auth:
            return {
                'success': False,
                'error': 'SAML authenticator not initialized',
                'auth_type': 'saml'
            }
        
        try:
            # Try browser flow first
            saml_response = self.saml_auth.authenticate_browser_flow()
            
            if saml_response:
                return {
                    'success': True,
                    'auth_type': 'saml',
                    'token': saml_response.assertion,
                    'method': 'saml_browser',
                    'user_dn': saml_response.name_id
                }
            else:
                # Fall back to token validation if browser flow fails
                if self.config.auth_token:
                    saml_response = self.saml_auth.authenticate_token_flow(self.config.auth_token)
                    
                    if saml_response:
                        return {
                            'success': True,
                            'auth_type': 'saml',
                            'token': saml_response.assertion,
                            'method': 'saml_token',
                            'user_dn': saml_response.name_id
                        }
                
                return {
                    'success': False,
                    'error': 'SAML authentication failed',
                    'auth_type': 'saml'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'auth_type': 'saml'
            }
    
    def _authenticate_ldap(self) -> Dict[str, Any]:
        """
        Authenticate using LDAP
        """
        if not self.ldap_auth:
            return {
                'success': False,
                'error': 'LDAP authenticator not initialized',
                'auth_type': 'ldap'
            }
        
        try:
            # Try username/password authentication
            ldap_response = self.ldap_auth.authenticate_username_password()
            
            if ldap_response:
                return {
                    'success': True,
                    'auth_type': 'ldap',
                    'token': ldap_response.token,
                    'method': 'ldap_username_password',
                    'user_dn': ldap_response.user_dn
                }
            else:
                # Fall back to token validation if username/password fails
                if self.config.auth_token:
                    ldap_response = self.ldap_auth.authenticate_token_flow(self.config.auth_token)
                    
                    if ldap_response:
                        return {
                            'success': True,
                            'auth_type': 'ldap',
                            'token': ldap_response.token,
                            'method': 'ldap_token',
                            'user_dn': ldap_response.user_dn
                        }
                
                return {
                    'success': False,
                    'error': 'LDAP authentication failed',
                    'auth_type': 'ldap'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'auth_type': 'ldap'
            }
    
    def _authenticate_custom(self) -> Dict[str, Any]:
        """
        Authenticate using custom authentication method
        """
        if not self.config.auth_endpoint:
            return {
                'success': False,
                'error': 'UPID_AUTH_ENDPOINT not configured',
                'auth_type': 'custom'
            }
        
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.config.auth_token:
                headers['Authorization'] = f'Bearer {self.config.auth_token}'
            
            if self.config.auth_custom_headers:
                headers.update(self.config.auth_custom_headers)
            
            # Prepare data
            data = {}
            
            if self.config.auth_username:
                data['username'] = self.config.auth_username
            
            if self.config.auth_password:
                data['password'] = self.config.auth_password
            
            if self.config.auth_client_id:
                data['client_id'] = self.config.auth_client_id
            
            if self.config.auth_client_secret:
                data['client_secret'] = self.config.auth_client_secret
            
            if self.config.auth_custom_params:
                data.update(self.config.auth_custom_params)
            
            # Make request
            if data:
                response = self.session.post(
                    self.config.auth_endpoint,
                    json=data,
                    headers=headers
                )
            else:
                response = self.session.get(
                    self.config.auth_endpoint,
                    headers=headers
                )
            
            if response.status_code == 200:
                auth_data = response.json()
                return {
                    'success': True,
                    'auth_type': 'custom',
                    'token': auth_data.get('token'),
                    'user': auth_data.get('user'),
                    'method': 'custom'
                }
            else:
                return {
                    'success': False,
                    'error': f'Custom authentication failed: {response.status_code}',
                    'auth_type': 'custom'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'auth_type': 'custom'
            }
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'UPID-CLI/1.0.0'
        }
        
        # For kubectl auth, we don't need additional headers
        if self.config.auth_type == 'kubectl':
            return headers
        
        # For other auth types, we need to get the token
        auth_result = self.authenticate()
        
        if auth_result.get('success') and auth_result.get('token'):
            token_type = auth_result.get('token_type', 'Bearer')
            headers['Authorization'] = f'{token_type} {auth_result["token"]}'
        
        return headers
    
    def validate_auth(self) -> Dict[str, Any]:
        """
        Validate current authentication
        """
        return self.authenticate()
    
    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get authentication information
        """
        return {
            'auth_type': self.config.auth_type,
            'auth_endpoint': self.config.auth_endpoint,
            'auth_provider': self.config.auth_provider,
            'auth_username': self.config.auth_username,
            'has_token': bool(self.config.auth_token),
            'has_cert': bool(self.config.auth_cert_path),
            'has_key': bool(self.config.auth_key_path),
            'has_ca': bool(self.config.auth_ca_path)
        } 