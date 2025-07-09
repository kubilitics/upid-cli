"""
SAML Authentication Module for UPID CLI
Supports browser-based SAML login and assertion handling for enterprise SSO
"""

import os
import json
import time
import webbrowser
import requests
import base64
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs, urlparse
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

@dataclass
class SAMLConfig:
    """SAML configuration"""
    endpoint: str
    client_id: str
    client_secret: Optional[str] = None
    provider: Optional[str] = None
    tenant_id: Optional[str] = None
    relay_state: Optional[str] = None

@dataclass
class SAMLResponse:
    """SAML response data"""
    assertion: str
    session_index: Optional[str] = None
    name_id: Optional[str] = None
    attributes: Dict[str, Any] = None

class SAMLAuthenticator:
    """SAML Authenticator with browser-based login"""
    
    def __init__(self, config: SAMLConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = 30
    
    def authenticate_browser_flow(self) -> Optional[SAMLResponse]:
        """
        Authenticate using browser-based SAML flow
        """
        try:
            console.print("[yellow]🔐 Starting SAML browser authentication...[/yellow]")
            
            # Step 1: Generate SAML request
            saml_request = self._generate_saml_request()
            if not saml_request:
                return None
            
            # Step 2: Build authentication URL
            auth_url = self._build_auth_url(saml_request)
            
            # Step 3: Open browser
            console.print(f"[cyan]Opening browser for SAML authentication...[/cyan]")
            webbrowser.open(auth_url)
            
            # Step 4: Get SAML response from user
            console.print("\n[yellow]Please complete authentication in your browser and copy the SAML response.[/yellow]")
            console.print("[yellow]The SAML response will be in the URL or you can copy it from the browser.[/yellow]")
            
            saml_response = Prompt.ask("Enter SAML response (or 'url' to enter URL)")
            
            if saml_response.lower() == 'url':
                response_url = Prompt.ask("Enter the URL you were redirected to")
                saml_response = self._extract_saml_response_from_url(response_url)
            
            if not saml_response:
                console.print("[red]❌ No SAML response provided[/red]")
                return None
            
            # Step 5: Process SAML response
            saml_data = self._process_saml_response(saml_response)
            
            if saml_data:
                console.print("[green]✅ SAML authentication successful![/green]")
                return saml_data
            else:
                console.print("[red]❌ SAML authentication failed[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ SAML authentication error: {e}[/red]")
            return None
    
    def authenticate_token_flow(self, token: str) -> Optional[SAMLResponse]:
        """
        Authenticate using existing SAML token
        """
        try:
            console.print("[yellow]🔐 Validating SAML token...[/yellow]")
            
            # Validate token with SAML provider
            validation_result = self._validate_saml_token(token)
            
            if validation_result:
                console.print("[green]✅ SAML token validation successful![/green]")
                return validation_result
            else:
                console.print("[red]❌ SAML token validation failed[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ SAML token validation error: {e}[/red]")
            return None
    
    def _generate_saml_request(self) -> Optional[str]:
        """Generate SAML authentication request"""
        
        # For now, we'll use a simple approach
        # In a real implementation, you'd generate a proper SAML request
        saml_request = f"""
        <samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                           xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                           ID="{self._generate_request_id()}"
                           Version="2.0"
                           IssueInstant="{self._get_iso_timestamp()}"
                           ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                           AssertionConsumerServiceURL="{self.config.endpoint}/acs">
            <saml:Issuer>{self.config.client_id}</saml:Issuer>
            <samlp:NameIDPolicy
                Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
                AllowCreate="true"/>
        </samlp:AuthnRequest>
        """
        
        return base64.b64encode(saml_request.encode()).decode()
    
    def _build_auth_url(self, saml_request: str) -> str:
        """Build SAML authentication URL"""
        
        params = {
            'SAMLRequest': saml_request,
            'RelayState': self.config.relay_state or 'upid-cli'
        }
        
        return f"{self.config.endpoint}?{urlencode(params)}"
    
    def _extract_saml_response_from_url(self, url: str) -> Optional[str]:
        """Extract SAML response from URL"""
        
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Look for SAMLResponse parameter
            if 'SAMLResponse' in query_params:
                return query_params['SAMLResponse'][0]
            
            # Look for SAML response in fragment
            if '#' in url:
                fragment = url.split('#')[1]
                if 'SAMLResponse=' in fragment:
                    saml_response = fragment.split('SAMLResponse=')[1].split('&')[0]
                    return saml_response
            
            return None
            
        except Exception as e:
            console.print(f"[red]❌ Error extracting SAML response from URL: {e}[/red]")
            return None
    
    def _process_saml_response(self, saml_response: str) -> Optional[SAMLResponse]:
        """Process SAML response and extract assertion"""
        
        try:
            # Decode SAML response
            if saml_response.startswith('http'):
                # Extract from URL
                saml_response = self._extract_saml_response_from_url(saml_response)
            
            if not saml_response:
                return None
            
            # Decode base64 SAML response
            try:
                decoded_response = base64.b64decode(saml_response).decode()
            except:
                # Try URL decoding first
                import urllib.parse
                decoded_response = urllib.parse.unquote(saml_response)
                try:
                    decoded_response = base64.b64decode(decoded_response).decode()
                except:
                    console.print("[red]❌ Invalid SAML response format[/red]")
                    return None
            
            # Parse SAML response (simplified)
            # In a real implementation, you'd use a proper SAML library
            saml_data = self._parse_saml_response(decoded_response)
            
            if saml_data:
                return SAMLResponse(
                    assertion=saml_response,
                    session_index=saml_data.get('session_index'),
                    name_id=saml_data.get('name_id'),
                    attributes=saml_data.get('attributes', {})
                )
            else:
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Error processing SAML response: {e}[/red]")
            return None
    
    def _parse_saml_response(self, saml_xml: str) -> Optional[Dict[str, Any]]:
        """Parse SAML XML response (simplified implementation)"""
        
        try:
            # This is a simplified parser
            # In production, use a proper SAML library like python-saml
            
            # Extract basic information
            data = {}
            
            # Look for NameID
            if '<saml:NameID>' in saml_xml:
                name_id_start = saml_xml.find('<saml:NameID>') + len('<saml:NameID>')
                name_id_end = saml_xml.find('</saml:NameID>')
                if name_id_end > name_id_start:
                    data['name_id'] = saml_xml[name_id_start:name_id_end]
            
            # Look for SessionIndex
            if 'SessionIndex="' in saml_xml:
                session_start = saml_xml.find('SessionIndex="') + len('SessionIndex="')
                session_end = saml_xml.find('"', session_start)
                if session_end > session_start:
                    data['session_index'] = saml_xml[session_start:session_end]
            
            # Extract attributes
            attributes = {}
            if '<saml:Attribute>' in saml_xml:
                # Parse attributes (simplified)
                attr_sections = saml_xml.split('<saml:Attribute')
                for section in attr_sections[1:]:
                    if 'Name="' in section:
                        name_start = section.find('Name="') + len('Name="')
                        name_end = section.find('"', name_start)
                        if name_end > name_start:
                            attr_name = section[name_start:name_end]
                            
                            # Look for attribute value
                            if '<saml:AttributeValue>' in section:
                                value_start = section.find('<saml:AttributeValue>') + len('<saml:AttributeValue>')
                                value_end = section.find('</saml:AttributeValue>')
                                if value_end > value_start:
                                    attr_value = section[value_start:value_end]
                                    attributes[attr_name] = attr_value
            
            data['attributes'] = attributes
            
            return data
            
        except Exception as e:
            console.print(f"[red]❌ Error parsing SAML response: {e}[/red]")
            return None
    
    def _validate_saml_token(self, token: str) -> Optional[SAMLResponse]:
        """Validate SAML token with provider"""
        
        try:
            # Validate token with SAML provider
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Try to validate with provider
            validation_endpoint = f"{self.config.endpoint}/validate"
            response = self.session.post(validation_endpoint, headers=headers)
            
            if response.status_code == 200:
                validation_data = response.json()
                return SAMLResponse(
                    assertion=token,
                    session_index=validation_data.get('session_index'),
                    name_id=validation_data.get('name_id'),
                    attributes=validation_data.get('attributes', {})
                )
            else:
                console.print(f"[red]❌ SAML token validation failed: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ SAML token validation error: {e}[/red]")
            return None
    
    def _generate_request_id(self) -> str:
        """Generate unique SAML request ID"""
        import uuid
        return f"_{uuid.uuid4().hex}"
    
    def _get_iso_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def get_user_info(self, saml_response: SAMLResponse) -> Dict[str, Any]:
        """Get user information from SAML response"""
        
        user_info = {
            'name_id': saml_response.name_id,
            'session_index': saml_response.session_index,
            'attributes': saml_response.attributes or {}
        }
        
        # Extract common attributes
        attributes = saml_response.attributes or {}
        
        user_info.update({
            'email': attributes.get('email') or attributes.get('mail'),
            'name': attributes.get('name') or attributes.get('displayName'),
            'first_name': attributes.get('firstName') or attributes.get('givenName'),
            'last_name': attributes.get('lastName') or attributes.get('surname'),
            'groups': attributes.get('groups') or attributes.get('memberOf', []),
            'roles': attributes.get('roles') or []
        })
        
        return user_info 