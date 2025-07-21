"""
OIDC Authentication Module for UPID CLI
Supports device code flow and browser-based authentication for seamless SSO
"""

import os
import json
import time
import webbrowser
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs, urlparse
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

@dataclass
class OIDCConfig:
    """OIDC configuration"""
    endpoint: str
    client_id: str
    client_secret: Optional[str] = None
    scope: str = "openid profile email"
    audience: Optional[str] = None
    redirect_uri: Optional[str] = None
    provider: Optional[str] = None
    tenant_id: Optional[str] = None

@dataclass
class DeviceCodeResponse:
    """Device code response from OIDC provider"""
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int
    message: Optional[str] = None

@dataclass
class TokenResponse:
    """Token response from OIDC provider"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    scope: Optional[str] = None

class OIDCAuthenticator:
    """OIDC Authenticator with device code flow and browser-based authentication"""
    
    def __init__(self, config: OIDCConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = 30
    
    def authenticate_device_code(self) -> Optional[TokenResponse]:
        """
        Authenticate using device code flow (recommended for CLI)
        """
        try:
            console.print("[yellow]🔐 Starting OIDC device code authentication...[/yellow]")
            
            # Step 1: Get device code
            device_code_response = self._get_device_code()
            if not device_code_response:
                return None
            
            # Step 2: Display user instructions
            self._display_device_code_instructions(device_code_response)
            
            # Step 3: Poll for token
            token_response = self._poll_for_token(device_code_response)
            
            if token_response:
                console.print("[green]✅ OIDC authentication successful![/green]")
                return token_response
            else:
                console.print("[red]❌ OIDC authentication failed or timed out[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ OIDC authentication error: {e}[/red]")
            return None
    
    def authenticate_browser_flow(self) -> Optional[TokenResponse]:
        """
        Authenticate using browser-based authorization code flow
        """
        try:
            console.print("[yellow]🔐 Starting OIDC browser authentication...[/yellow]")
            
            # Step 1: Generate authorization URL
            auth_url = self._generate_auth_url()
            
            # Step 2: Open browser
            console.print(f"[cyan]Opening browser for authentication...[/cyan]")
            webbrowser.open(auth_url)
            
            # Step 3: Get authorization code from user
            console.print("\n[yellow]Please complete authentication in your browser and copy the authorization code.[/yellow]")
            auth_code = Prompt.ask("Enter authorization code")
            
            if not auth_code:
                console.print("[red]❌ No authorization code provided[/red]")
                return None
            
            # Step 4: Exchange code for token
            token_response = self._exchange_code_for_token(auth_code)
            
            if token_response:
                console.print("[green]✅ OIDC authentication successful![/green]")
                return token_response
            else:
                console.print("[red]❌ OIDC authentication failed[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ OIDC authentication error: {e}[/red]")
            return None
    
    def authenticate_client_credentials(self) -> Optional[TokenResponse]:
        """
        Authenticate using client credentials flow (for service accounts)
        """
        try:
            console.print("[yellow]🔐 Starting OIDC client credentials authentication...[/yellow]")
            
            if not self.config.client_secret:
                console.print("[red]❌ Client secret required for client credentials flow[/red]")
                return None
            
            # Prepare token request
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'scope': self.config.scope
            }
            
            if self.config.audience:
                data['audience'] = self.config.audience
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Make token request
            response = self.session.post(
                self.config.endpoint,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return TokenResponse(
                    access_token=token_data['access_token'],
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_in=token_data.get('expires_in'),
                    scope=token_data.get('scope')
                )
            else:
                console.print(f"[red]❌ Token request failed: {response.status_code}[/red]")
                console.print(f"[red]Response: {response.text}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ OIDC authentication error: {e}[/red]")
            return None
    
    def _get_device_code(self) -> Optional[DeviceCodeResponse]:
        """Get device code from OIDC provider"""
        
        # Determine device code endpoint
        if self.config.provider == 'azure':
            device_endpoint = self.config.endpoint.replace('/token', '/devicecode')
        elif self.config.provider == 'google':
            device_endpoint = 'https://oauth2.googleapis.com/device/code'
        else:
            # Try common device code endpoints
            device_endpoint = self.config.endpoint.replace('/token', '/devicecode')
        
        # Prepare device code request
        data = {
            'client_id': self.config.client_id,
            'scope': self.config.scope
        }
        
        if self.config.audience:
            data['audience'] = self.config.audience
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = self.session.post(
                device_endpoint,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                device_data = response.json()
                return DeviceCodeResponse(
                    device_code=device_data['device_code'],
                    user_code=device_data['user_code'],
                    verification_uri=device_data['verification_uri'],
                    expires_in=device_data.get('expires_in', 1800),
                    interval=device_data.get('interval', 5),
                    message=device_data.get('message')
                )
            else:
                console.print(f"[red]❌ Device code request failed: {response.status_code}[/red]")
                console.print(f"[red]Response: {response.text}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Device code request error: {e}[/red]")
            return None
    
    def _display_device_code_instructions(self, device_code: DeviceCodeResponse):
        """Display device code instructions to user"""
        
        console.print("\n" + "="*60)
        console.print("[bold blue]🔐 OIDC Device Code Authentication[/bold blue]")
        console.print("="*60)
        
        if device_code.message:
            console.print(f"\n[cyan]{device_code.message}[/cyan]")
        else:
            console.print(f"\n[cyan]Please visit the following URL and enter the code:[/cyan]")
        
        console.print(f"\n[bold green]URL:[/bold green] {device_code.verification_uri}")
        console.print(f"[bold green]Code:[/bold green] {device_code.user_code}")
        
        # Try to open browser automatically
        try:
            webbrowser.open(device_code.verification_uri)
            console.print("\n[green]✅ Browser opened automatically[/green]")
        except:
            console.print("\n[yellow]⚠️  Please open the URL manually in your browser[/yellow]")
        
        console.print(f"\n[yellow]⏰ This code expires in {device_code.expires_in} seconds[/yellow]")
        console.print("[yellow]⏳ Waiting for authentication...[/yellow]\n")
    
    def _poll_for_token(self, device_code: DeviceCodeResponse) -> Optional[TokenResponse]:
        """Poll for token after user completes authentication"""
        
        max_attempts = device_code.expires_in // device_code.interval
        attempts = 0
        
        with console.status("[yellow]Waiting for authentication...[/yellow]", spinner="dots"):
            while attempts < max_attempts:
                try:
                    # Prepare token request
                    data = {
                        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                        'client_id': self.config.client_id,
                        'device_code': device_code.device_code
                    }
                    
                    if self.config.client_secret:
                        data['client_secret'] = self.config.client_secret
                    
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    
                    # Make token request
                    response = self.session.post(
                        self.config.endpoint,
                        data=data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        token_data = response.json()
                        return TokenResponse(
                            access_token=token_data['access_token'],
                            token_type=token_data.get('token_type', 'Bearer'),
                            expires_in=token_data.get('expires_in'),
                            refresh_token=token_data.get('refresh_token'),
                            id_token=token_data.get('id_token'),
                            scope=token_data.get('scope')
                        )
                    elif response.status_code == 400:
                        error_data = response.json()
                        error = error_data.get('error', 'unknown')
                        
                        if error == 'authorization_pending':
                            # User hasn't completed authentication yet
                            time.sleep(device_code.interval)
                            attempts += 1
                            continue
                        elif error == 'authorization_declined':
                            console.print("[red]❌ Authentication was declined by user[/red]")
                            return None
                        elif error == 'expired_token':
                            console.print("[red]❌ Device code expired[/red]")
                            return None
                        else:
                            console.print(f"[red]❌ Token request error: {error}[/red]")
                            return None
                    else:
                        console.print(f"[red]❌ Token request failed: {response.status_code}[/red]")
                        return None
                        
                except Exception as e:
                    console.print(f"[red]❌ Token polling error: {e}[/red]")
                    return None
        
        console.print("[red]❌ Authentication timed out[/red]")
        return None
    
    def _generate_auth_url(self) -> str:
        """Generate authorization URL for browser flow"""
        
        # Determine authorization endpoint
        if self.config.provider == 'azure':
            auth_endpoint = self.config.endpoint.replace('/token', '/authorize')
        elif self.config.provider == 'google':
            auth_endpoint = 'https://accounts.google.com/o/oauth2/v2/auth'
        else:
            # Try common authorization endpoints
            auth_endpoint = self.config.endpoint.replace('/token', '/authorize')
        
        # Prepare authorization parameters
        params = {
            'client_id': self.config.client_id,
            'response_type': 'code',
            'scope': self.config.scope,
            'redirect_uri': self.config.redirect_uri or 'urn:ietf:wg:oauth:2.0:oob'
        }
        
        if self.config.audience:
            params['audience'] = self.config.audience
        
        # Add provider-specific parameters
        if self.config.provider == 'azure':
            params['response_mode'] = 'query'
        
        return f"{auth_endpoint}?{urlencode(params)}"
    
    def _exchange_code_for_token(self, auth_code: str) -> Optional[TokenResponse]:
        """Exchange authorization code for token"""
        
        # Prepare token request
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.config.client_id,
            'code': auth_code,
            'redirect_uri': self.config.redirect_uri or 'urn:ietf:wg:oauth:2.0:oob'
        }
        
        if self.config.client_secret:
            data['client_secret'] = self.config.client_secret
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = self.session.post(
                self.config.endpoint,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return TokenResponse(
                    access_token=token_data['access_token'],
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_in=token_data.get('expires_in'),
                    refresh_token=token_data.get('refresh_token'),
                    id_token=token_data.get('id_token'),
                    scope=token_data.get('scope')
                )
            else:
                console.print(f"[red]❌ Token exchange failed: {response.status_code}[/red]")
                console.print(f"[red]Response: {response.text}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Token exchange error: {e}[/red]")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """Refresh access token using refresh token"""
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.config.client_id,
            'refresh_token': refresh_token
        }
        
        if self.config.client_secret:
            data['client_secret'] = self.config.client_secret
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = self.session.post(
                self.config.endpoint,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return TokenResponse(
                    access_token=token_data['access_token'],
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_in=token_data.get('expires_in'),
                    refresh_token=token_data.get('refresh_token', refresh_token),
                    id_token=token_data.get('id_token'),
                    scope=token_data.get('scope')
                )
            else:
                console.print(f"[red]❌ Token refresh failed: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Token refresh error: {e}[/red]")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from OIDC provider"""
        
        # Try common userinfo endpoints
        userinfo_endpoints = [
            self.config.endpoint.replace('/token', '/userinfo'),
            'https://www.googleapis.com/oauth2/v2/userinfo',  # Google
            'https://graph.microsoft.com/v1.0/me'  # Azure
        ]
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        for endpoint in userinfo_endpoints:
            try:
                response = self.session.get(endpoint, headers=headers)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        
        return None 