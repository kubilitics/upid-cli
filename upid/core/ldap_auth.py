"""
LDAP/Active Directory Authentication Module for UPID CLI
Supports secure username/password authentication and session management
"""

import os
import json
import time
import requests
import getpass
from typing import Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

@dataclass
class LDAPConfig:
    """LDAP configuration"""
    endpoint: str
    username: str
    password: Optional[str] = None
    provider: Optional[str] = None
    base_dn: Optional[str] = None
    search_filter: Optional[str] = None

@dataclass
class LDAPResponse:
    """LDAP response data"""
    token: str
    user_dn: str
    groups: list = None
    attributes: Dict[str, Any] = None

class LDAPAuthenticator:
    """LDAP/Active Directory Authenticator"""
    
    def __init__(self, config: LDAPConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = 30
    
    def authenticate_username_password(self) -> Optional[LDAPResponse]:
        """
        Authenticate using username and password
        """
        try:
            console.print("[yellow]🔐 Starting LDAP authentication...[/yellow]")
            
            # Get username and password
            username = self.config.username
            if not username:
                username = Prompt.ask("Enter username")
            
            password = self.config.password
            if not password:
                password = getpass.getpass("Enter password: ")
            
            # Step 1: Authenticate with LDAP provider
            auth_result = self._authenticate_with_provider(username, password)
            
            if auth_result:
                console.print("[green]✅ LDAP authentication successful![/green]")
                return auth_result
            else:
                console.print("[red]❌ LDAP authentication failed[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ LDAP authentication error: {e}[/red]")
            return None
    
    def authenticate_token_flow(self, token: str) -> Optional[LDAPResponse]:
        """
        Authenticate using existing LDAP token
        """
        try:
            console.print("[yellow]🔐 Validating LDAP token...[/yellow]")
            
            # Validate token with LDAP provider
            validation_result = self._validate_ldap_token(token)
            
            if validation_result:
                console.print("[green]✅ LDAP token validation successful![/green]")
                return validation_result
            else:
                console.print("[red]❌ LDAP token validation failed[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ LDAP token validation error: {e}[/red]")
            return None
    
    def _authenticate_with_provider(self, username: str, password: str) -> Optional[LDAPResponse]:
        """Authenticate with LDAP provider"""
        
        try:
            # Prepare authentication data
            auth_data = {
                'username': username,
                'password': password
            }
            
            if self.config.provider:
                auth_data['provider'] = self.config.provider
            
            if self.config.base_dn:
                auth_data['base_dn'] = self.config.base_dn
            
            if self.config.search_filter:
                auth_data['search_filter'] = self.config.search_filter
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Make authentication request
            response = self.session.post(
                f"{self.config.endpoint}/authenticate",
                json=auth_data,
                headers=headers
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                
                return LDAPResponse(
                    token=auth_data.get('token'),
                    user_dn=auth_data.get('user_dn', username),
                    groups=auth_data.get('groups', []),
                    attributes=auth_data.get('attributes', {})
                )
            else:
                console.print(f"[red]❌ LDAP authentication failed: {response.status_code}[/red]")
                console.print(f"[red]Response: {response.text}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ LDAP authentication error: {e}[/red]")
            return None
    
    def _validate_ldap_token(self, token: str) -> Optional[LDAPResponse]:
        """Validate LDAP token with provider"""
        
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Validate token with provider
            validation_endpoint = f"{self.config.endpoint}/validate"
            response = self.session.post(validation_endpoint, headers=headers)
            
            if response.status_code == 200:
                validation_data = response.json()
                
                return LDAPResponse(
                    token=token,
                    user_dn=validation_data.get('user_dn'),
                    groups=validation_data.get('groups', []),
                    attributes=validation_data.get('attributes', {})
                )
            else:
                console.print(f"[red]❌ LDAP token validation failed: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ LDAP token validation error: {e}[/red]")
            return None
    
    def search_users(self, search_filter: str = None, base_dn: str = None) -> list:
        """Search for users in LDAP directory"""
        
        try:
            search_data = {
                'search_filter': search_filter or self.config.search_filter or '(objectClass=person)',
                'base_dn': base_dn or self.config.base_dn
            }
            
            headers = {
                'Authorization': f'Bearer {self.config.token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.config.endpoint}/search",
                json=search_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json().get('users', [])
            else:
                console.print(f"[red]❌ LDAP search failed: {response.status_code}[/red]")
                return []
                
        except Exception as e:
            console.print(f"[red]❌ LDAP search error: {e}[/red]")
            return []
    
    def get_user_groups(self, username: str) -> list:
        """Get groups for a specific user"""
        
        try:
            group_data = {
                'username': username
            }
            
            headers = {
                'Authorization': f'Bearer {self.config.token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.config.endpoint}/groups",
                json=group_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json().get('groups', [])
            else:
                console.print(f"[red]❌ LDAP group lookup failed: {response.status_code}[/red]")
                return []
                
        except Exception as e:
            console.print(f"[red]❌ LDAP group lookup error: {e}[/red]")
            return []
    
    def get_user_info(self, ldap_response: LDAPResponse) -> Dict[str, Any]:
        """Get user information from LDAP response"""
        
        user_info = {
            'user_dn': ldap_response.user_dn,
            'groups': ldap_response.groups or [],
            'attributes': ldap_response.attributes or {}
        }
        
        # Extract common attributes
        attributes = ldap_response.attributes or {}
        
        user_info.update({
            'email': attributes.get('email') or attributes.get('mail'),
            'name': attributes.get('name') or attributes.get('displayName'),
            'first_name': attributes.get('firstName') or attributes.get('givenName'),
            'last_name': attributes.get('lastName') or attributes.get('surname'),
            'username': attributes.get('username') or attributes.get('uid'),
            'department': attributes.get('department'),
            'title': attributes.get('title'),
            'manager': attributes.get('manager')
        })
        
        return user_info
    
    def test_connection(self) -> bool:
        """Test LDAP connection"""
        
        try:
            console.print("[yellow]Testing LDAP connection...[/yellow]")
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{self.config.endpoint}/health",
                headers=headers
            )
            
            if response.status_code == 200:
                console.print("[green]✅ LDAP connection successful[/green]")
                return True
            else:
                console.print(f"[red]❌ LDAP connection failed: {response.status_code}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ LDAP connection error: {e}[/red]")
            return False 