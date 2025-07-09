#!/usr/bin/env python3
"""
Test script for UPID Configurable Authentication System
"""

import os
import sys
import subprocess
from pathlib import Path

def test_kubectl_auth():
    """Test kubectl authentication (default for individuals)"""
    print("🧪 Testing kubectl authentication...")
    
    # Set kubectl auth type
    os.environ['UPID_AUTH_TYPE'] = 'kubectl'
    
    try:
        # Test kubectl is available
        result = subprocess.run(['kubectl', 'version', '--client'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ kubectl is available")
            
            # Test cluster connection
            result = subprocess.run(['kubectl', 'cluster-info'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ kubectl cluster connection successful")
                return True
            else:
                print("❌ kubectl cluster connection failed")
                return False
        else:
            print("❌ kubectl not available")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ kubectl command timed out")
        return False
    except Exception as e:
        print(f"❌ kubectl test failed: {e}")
        return False

def test_oidc_config():
    """Test OIDC configuration (without actual authentication)"""
    print("🧪 Testing OIDC configuration...")
    
    # Set OIDC environment variables
    os.environ['UPID_AUTH_TYPE'] = 'oidc'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://example.com/oauth2/token'
    os.environ['UPID_AUTH_CLIENT_ID'] = 'test_client_id'
    os.environ['UPID_AUTH_CLIENT_SECRET'] = 'test_client_secret'
    os.environ['UPID_AUTH_SCOPE'] = 'openid profile email'
    os.environ['UPID_AUTH_PROVIDER'] = 'test'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'oidc':
            print("✅ OIDC configuration loaded correctly")
            print(f"   Endpoint: {auth_info['auth_endpoint']}")
            print(f"   Provider: {auth_info['auth_provider']}")
            return True
        else:
            print("❌ OIDC configuration failed")
            return False
            
    except Exception as e:
        print(f"❌ OIDC test failed: {e}")
        return False

def test_saml_config():
    """Test SAML configuration (without actual authentication)"""
    print("🧪 Testing SAML configuration...")
    
    # Set SAML environment variables
    os.environ['UPID_AUTH_TYPE'] = 'saml'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://example.com/saml/login'
    os.environ['UPID_AUTH_CLIENT_ID'] = 'test_client_id'
    os.environ['UPID_AUTH_CLIENT_SECRET'] = 'test_client_secret'
    os.environ['UPID_AUTH_PROVIDER'] = 'test'
    os.environ['UPID_AUTH_TENANT_ID'] = 'test_tenant'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'saml':
            print("✅ SAML configuration loaded correctly")
            print(f"   Endpoint: {auth_info['auth_endpoint']}")
            print(f"   Provider: {auth_info['auth_provider']}")
            return True
        else:
            print("❌ SAML configuration failed")
            return False
            
    except Exception as e:
        print(f"❌ SAML test failed: {e}")
        return False

def test_ldap_config():
    """Test LDAP configuration (without actual authentication)"""
    print("🧪 Testing LDAP configuration...")
    
    # Set LDAP environment variables
    os.environ['UPID_AUTH_TYPE'] = 'ldap'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://example.com/ldap/auth'
    os.environ['UPID_AUTH_USERNAME'] = 'test_user'
    os.environ['UPID_AUTH_PASSWORD'] = 'test_password'
    os.environ['UPID_AUTH_PROVIDER'] = 'test_ldap'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'ldap':
            print("✅ LDAP configuration loaded correctly")
            print(f"   Endpoint: {auth_info['auth_endpoint']}")
            print(f"   Username: {auth_info['auth_username']}")
            return True
        else:
            print("❌ LDAP configuration failed")
            return False
            
    except Exception as e:
        print(f"❌ LDAP test failed: {e}")
        return False

def test_custom_config():
    """Test custom authentication configuration (without actual authentication)"""
    print("🧪 Testing custom authentication configuration...")
    
    # Set custom environment variables
    os.environ['UPID_AUTH_TYPE'] = 'custom'
    os.environ['UPID_AUTH_ENDPOINT'] = 'https://example.com/custom/auth'
    os.environ['UPID_AUTH_CUSTOM_HEADERS'] = '{"X-API-Key": "test_key", "X-Client-ID": "test_client"}'
    os.environ['UPID_AUTH_CUSTOM_PARAMS'] = '{"grant_type": "client_credentials", "scope": "read write"}'
    
    try:
        # Import and test configurable auth
        sys.path.insert(0, str(Path(__file__).parent))
        from upid.core.configurable_auth import ConfigurableAuthenticator
        
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        if auth_info['auth_type'] == 'custom':
            print("✅ Custom authentication configuration loaded correctly")
            print(f"   Endpoint: {auth_info['auth_endpoint']}")
            return True
        else:
            print("❌ Custom authentication configuration failed")
            return False
            
    except Exception as e:
        print(f"❌ Custom authentication test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI commands for configurable authentication"""
    print("🧪 Testing CLI commands...")
    
    try:
        # Test help command
        result = subprocess.run(['python', '-m', 'upid.cli', 'configurable-auth', 'help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI help command works")
        else:
            print("❌ CLI help command failed")
            return False
        
        # Test status command
        result = subprocess.run(['python', '-m', 'upid.cli', 'configurable-auth', 'status'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI status command works")
        else:
            print("❌ CLI status command failed")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
        return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 UPID Configurable Authentication Test Suite\n")
    
    tests = [
        ("kubectl", test_kubectl_auth),
        ("OIDC", test_oidc_config),
        ("SAML", test_saml_config),
        ("LDAP", test_ldap_config),
        ("Custom", test_custom_config),
        ("CLI Commands", test_cli_commands)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! Configurable authentication system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 