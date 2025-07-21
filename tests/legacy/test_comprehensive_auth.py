#!/usr/bin/env python3
"""
Comprehensive Authentication Test Suite for UPID CLI
Tests all authentication methods: OIDC, SAML, LDAP, kubectl, and custom
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def test_kubectl_auth():
    """Test kubectl authentication"""
    console.print("\n[bold blue]Testing kubectl authentication...[/bold blue]")
    
    # Set kubectl auth type
    os.environ['UPID_AUTH_TYPE'] = 'kubectl'
    
    try:
        # Test kubectl is available
        result = subprocess.run(['kubectl', 'version', '--client'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': 'kubectl not available',
                'method': 'kubectl'
            }
        
        # Test cluster connection
        result = subprocess.run(['kubectl', 'cluster-info'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': 'kubectl cluster connection failed',
                'method': 'kubectl'
            }
        
        # Get current context and user
        context_result = subprocess.run(['kubectl', 'config', 'current-context'], 
                                      capture_output=True, text=True, timeout=5)
        user_result = subprocess.run(['kubectl', 'whoami'], 
                                   capture_output=True, text=True, timeout=5)
        
        context = context_result.stdout.strip() if context_result.returncode == 0 else 'unknown'
        user = user_result.stdout.strip() if user_result.returncode == 0 else 'unknown'
        
        return {
            'success': True,
            'method': 'kubectl',
            'context': context,
            'user': user
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'kubectl command timed out',
            'method': 'kubectl'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'kubectl'
        }

def test_oidc_auth():
    """Test OIDC authentication configuration"""
    console.print("\n[bold blue]Testing OIDC authentication...[/bold blue]")
    
    # Set OIDC environment variables
    os.environ['UPID_AUTH_TYPE'] = 'oidc'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token'
    os.environ['UPID_AUTH_CLIENT_ID'] = 'test-client-id'
    os.environ['UPID_AUTH_CLIENT_SECRET'] = 'test-client-secret'
    os.environ['UPID_AUTH_SCOPE'] = 'openid profile email'
    os.environ['UPID_AUTH_PROVIDER'] = 'azure'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'oidc':
            return {
                'success': True,
                'method': 'oidc',
                'endpoint': auth_info['auth_endpoint'],
                'provider': auth_info['auth_provider']
            }
        else:
            return {
                'success': False,
                'error': 'OIDC configuration failed',
                'method': 'oidc'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'oidc'
        }

def test_saml_auth():
    """Test SAML authentication configuration"""
    console.print("\n[bold blue]Testing SAML authentication...[/bold blue]")
    
    # Set SAML environment variables
    os.environ['UPID_AUTH_TYPE'] = 'saml'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://test-okta.okta.com/app/test-app/sso/saml'
    os.environ['UPID_AUTH_CLIENT_ID'] = 'test-client-id'
    os.environ['UPID_AUTH_CLIENT_SECRET'] = 'test-client-secret'
    os.environ['UPID_AUTH_PROVIDER'] = 'okta'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'saml':
            return {
                'success': True,
                'method': 'saml',
                'endpoint': auth_info['auth_endpoint'],
                'provider': auth_info['auth_provider']
            }
        else:
            return {
                'success': False,
                'error': 'SAML configuration failed',
                'method': 'saml'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'saml'
        }

def test_ldap_auth():
    """Test LDAP authentication configuration"""
    console.print("\n[bold blue]Testing LDAP authentication...[/bold blue]")
    
    # Set LDAP environment variables
    os.environ['UPID_AUTH_TYPE'] = 'ldap'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://ldap-gateway.company.com/auth'
    os.environ['UPID_AUTH_USERNAME'] = 'test-user'
    os.environ['UPID_AUTH_PASSWORD'] = 'test-password'
    os.environ['UPID_AUTH_PROVIDER'] = 'active_directory'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'ldap':
            return {
                'success': True,
                'method': 'ldap',
                'endpoint': auth_info['auth_endpoint'],
                'username': auth_info['auth_username'],
                'provider': auth_info['auth_provider']
            }
        else:
            return {
                'success': False,
                'error': 'LDAP configuration failed',
                'method': 'ldap'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'ldap'
        }

def test_custom_auth():
    """Test custom authentication configuration"""
    console.print("\n[bold blue]Testing custom authentication...[/bold blue]")
    
    # Set custom environment variables
    os.environ['UPID_AUTH_TYPE'] = 'custom'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://custom-auth.company.com/authenticate'
    os.environ['UPID_AUTH_CUSTOM_HEADERS'] = '{"X-API-Key": "test-key", "X-Client-ID": "test-client"}'
    os.environ['UPID_AUTH_CUSTOM_PARAMS'] = '{"grant_type": "client_credentials", "scope": "read write"}'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'custom':
            return {
                'success': True,
                'method': 'custom',
                'endpoint': auth_info['auth_endpoint']
            }
        else:
            return {
                'success': False,
                'error': 'Custom configuration failed',
                'method': 'custom'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'custom'
        }

def test_onboarding_commands():
    """Test onboarding CLI commands"""
    console.print("\n[bold blue]Testing onboarding CLI commands...[/bold blue]")
    
    try:
        # Test help command
        result = subprocess.run(['python', '-m', 'upid.cli', 'onboarding', 'help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': 'onboarding help command failed',
                'method': 'onboarding'
            }
        
        # Test status command
        result = subprocess.run(['python', '-m', 'upid.cli', 'onboarding', 'status'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': 'onboarding status command failed',
                'method': 'onboarding'
            }
        
        return {
            'success': True,
            'method': 'onboarding'
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'onboarding command timed out',
            'method': 'onboarding'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'onboarding'
        }

def test_configurable_auth_commands():
    """Test configurable auth CLI commands"""
    console.print("\n[bold blue]Testing configurable auth CLI commands...[/bold blue]")
    
    try:
        # Test help command
        result = subprocess.run(['python', '-m', 'upid.cli', 'configurable-auth', 'help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': 'configurable-auth help command failed',
                'method': 'configurable-auth'
            }
        
        # Test status command
        result = subprocess.run(['python', '-m', 'upid.cli', 'configurable-auth', 'status'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': 'configurable-auth status command failed',
                'method': 'configurable-auth'
            }
        
        return {
            'success': True,
            'method': 'configurable-auth'
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'configurable-auth command timed out',
            'method': 'configurable-auth'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'configurable-auth'
        }

def test_oidc_modules():
    """Test OIDC authentication modules"""
    console.print("\n[bold blue]Testing OIDC authentication modules...[/bold blue]")
    
    try:
        # Import OIDC modules
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.oidc_auth import OIDCAuthenticator, OIDCConfig, TokenResponse
        
        # Test OIDC config
        config = OIDCConfig(
            endpoint='https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token',
            client_id='test-client-id',
            client_secret='test-client-secret',
            scope='openid profile email',
            provider='azure'
        )
        
        # Test OIDC authenticator initialization
        authenticator = OIDCAuthenticator(config)
        
        return {
            'success': True,
            'method': 'oidc_modules',
            'config': str(config)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'oidc_modules'
        }

def test_saml_modules():
    """Test SAML authentication modules"""
    console.print("\n[bold blue]Testing SAML authentication modules...[/bold blue]")
    
    try:
        # Import SAML modules
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.saml_auth import SAMLAuthenticator, SAMLConfig, SAMLResponse
        
        # Test SAML config
        config = SAMLConfig(
            endpoint='https://test-okta.okta.com/app/test-app/sso/saml',
            client_id='test-client-id',
            client_secret='test-client-secret',
            provider='okta'
        )
        
        # Test SAML authenticator initialization
        authenticator = SAMLAuthenticator(config)
        
        return {
            'success': True,
            'method': 'saml_modules',
            'config': str(config)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'saml_modules'
        }

def test_ldap_modules():
    """Test LDAP authentication modules"""
    console.print("\n[bold blue]Testing LDAP authentication modules...[/bold blue]")
    
    try:
        # Import LDAP modules
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.ldap_auth import LDAPAuthenticator, LDAPConfig, LDAPResponse
        
        # Test LDAP config
        config = LDAPConfig(
            endpoint='https://ldap-gateway.company.com/auth',
            username='test-user',
            password='test-password',
            provider='active_directory'
        )
        
        # Test LDAP authenticator initialization
        authenticator = LDAPAuthenticator(config)
        
        return {
            'success': True,
            'method': 'ldap_modules',
            'config': str(config)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'ldap_modules'
        }

def main():
    """Run comprehensive authentication tests"""
    console.print("\n[bold blue]🔐 UPID CLI Comprehensive Authentication Test Suite[/bold blue]\n")
    
    tests = [
        ("kubectl", test_kubectl_auth),
        ("OIDC", test_oidc_auth),
        ("SAML", test_saml_auth),
        ("LDAP", test_ldap_auth),
        ("Custom", test_custom_auth),
        ("OIDC Modules", test_oidc_modules),
        ("SAML Modules", test_saml_modules),
        ("LDAP Modules", test_ldap_modules),
        ("Onboarding Commands", test_onboarding_commands),
        ("Configurable Auth Commands", test_configurable_auth_commands)
    ]
    
    results = []
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        console.print(f"\n{'='*60}")
        console.print(f"Testing: {test_name}")
        console.print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result['success']:
                console.print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                console.print(f"❌ {test_name} test FAILED: {result.get('error', 'Unknown error')}")
        except Exception as e:
            console.print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, {'success': False, 'error': str(e), 'method': test_name}))
    
    # Display results summary
    console.print(f"\n{'='*60}")
    console.print(f"[bold blue]Test Results Summary[/bold blue]")
    console.print('='*60)
    
    # Create results table
    table = Table(title="Authentication Test Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Method", style="yellow")
    table.add_column("Details", style="white")
    
    for test_name, result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        method = result.get('method', 'unknown')
        details = result.get('error', 'Success')
        
        table.add_row(test_name, status, method, details)
    
    console.print(table)
    
    console.print(f"\n[bold]Overall Results: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("\n[bold green]🎉 All authentication tests passed![/bold green]")
        console.print("[green]The UPID CLI authentication system is working correctly.[/green]")
        return 0
    else:
        console.print(f"\n[bold yellow]⚠️  {total - passed} test(s) failed. Please check the configuration.[/bold yellow]")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 