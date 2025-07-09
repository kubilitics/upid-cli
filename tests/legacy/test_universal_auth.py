#!/usr/bin/env python3
"""
Test script for Universal Authentication System
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid.auth import UniversalAuthenticator
from upid.auth.universal_auth import EnvironmentInfo, AuthResult

async def test_environment_detection():
    """Test environment detection"""
    print("🔍 Testing Environment Detection...")
    
    authenticator = UniversalAuthenticator()
    
    # Test local detection
    local_info = await authenticator.local_detector.detect()
    print(f"Local Detection: {local_info.detected} ({local_info.cluster_type})")
    
    # Test cloud detection
    cloud_info = await authenticator.cloud_detector.detect()
    print(f"Cloud Detection: {cloud_info.detected} ({cloud_info.cluster_type})")
    
    # Test universal detection
    env_info = await authenticator.detect_environment()
    print(f"Universal Detection: {env_info.cluster_type}")
    print(f"  - Is Local: {env_info.is_local_cluster}")
    print(f"  - Cloud Provider: {env_info.cloud_provider}")
    print(f"  - Cluster Name: {env_info.cluster_name}")
    print(f"  - Context: {env_info.context_name}")
    
    return env_info

async def test_authentication():
    """Test authentication flow"""
    print("\n🔐 Testing Authentication Flow...")
    
    authenticator = UniversalAuthenticator()
    
    # Test authentication
    auth_result = await authenticator.authenticate_user({})
    print(f"Authentication Result: {auth_result.success}")
    print(f"  - Method: {auth_result.auth_method}")
    print(f"  - Requires Action: {auth_result.requires_action}")
    if auth_result.error_message:
        print(f"  - Error: {auth_result.error_message}")
    
    return auth_result

async def test_rbac_permissions():
    """Test RBAC permissions"""
    print("\n🔒 Testing RBAC Permissions...")
    
    authenticator = UniversalAuthenticator()
    
    # Test RBAC check
    rbac_info = await authenticator.rbac_enforcer.check_user_permissions("default")
    print(f"RBAC Check: {rbac_info.user}")
    print(f"  - Can Read: {rbac_info.can_read}")
    print(f"  - Can Write: {rbac_info.can_write}")
    print(f"  - Can Delete: {rbac_info.can_delete}")
    print(f"  - Can Exec: {rbac_info.can_exec}")
    print(f"  - Roles: {rbac_info.roles}")
    print(f"  - Permissions: {len(rbac_info.permissions)}")
    
    return rbac_info

async def test_cluster_info():
    """Test cluster information"""
    print("\n📊 Testing Cluster Information...")
    
    authenticator = UniversalAuthenticator()
    
    # Test cluster info
    cluster_info = authenticator.get_cluster_info()
    print(f"Cluster Info: {cluster_info['connection_status']}")
    if cluster_info['cluster_info'] != 'Not connected':
        print(f"  - Info: {cluster_info['cluster_info'][:100]}...")
    
    return cluster_info

async def test_permission_check():
    """Test specific permission checks"""
    print("\n✅ Testing Permission Checks...")
    
    authenticator = UniversalAuthenticator()
    
    # Test specific permissions
    permissions_to_test = [
        ("pods", "get"),
        ("pods", "create"),
        ("pods", "delete"),
        ("services", "get"),
        ("deployments", "get"),
    ]
    
    for resource, action in permissions_to_test:
        permission_check = await authenticator.rbac_enforcer.check_resource_permission(
            resource, action, "default"
        )
        print(f"  - {action} {resource}: {'✅' if permission_check.allowed else '❌'} ({permission_check.reason})")
    
    return True

async def main():
    """Main test function"""
    print("🚀 UPID Universal Authentication System Test")
    print("=" * 50)
    
    try:
        # Test environment detection
        env_info = await test_environment_detection()
        
        # Test authentication
        auth_result = await test_authentication()
        
        # Test RBAC permissions
        rbac_info = await test_rbac_permissions()
        
        # Test cluster info
        cluster_info = await test_cluster_info()
        
        # Test permission checks
        await test_permission_check()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
        # Summary
        print("\n📋 Test Summary:")
        print(f"  - Environment: {env_info.cluster_type}")
        print(f"  - Authentication: {'✅ Success' if auth_result.success else '❌ Failed'}")
        print(f"  - RBAC User: {rbac_info.user}")
        print(f"  - Cluster Status: {cluster_info['connection_status']}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 