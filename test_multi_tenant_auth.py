#!/usr/bin/env python3
"""
Simple test script for multi-tenant authentication system
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid_python.core.multi_tenant_auth import (
    MultiTenantAuthManager,
    TenantRole,
    Permission,
    ResourceType
)


async def test_multi_tenant_auth():
    """Test the multi-tenant authentication system"""
    print("🧪 Testing Multi-Tenant Authentication System")
    print("=" * 50)
    
    # Initialize auth manager
    config = {
        "session_timeout_hours": 24,
        "max_audit_events": 1000,
        "default_tenant": "default"
    }
    
    auth_manager = MultiTenantAuthManager(config)
    
    # Test initialization
    print("1. Testing initialization...")
    result = await auth_manager.initialize()
    assert result is True
    print("✅ Initialization successful")
    
    # Test tenant creation
    print("\n2. Testing tenant creation...")
    result = await auth_manager.create_tenant(
        tenant_id="test-tenant",
        name="Test Organization",
        description="Test tenant for validation"
    )
    assert result is True
    print("✅ Tenant creation successful")
    
    # Test user creation
    print("\n3. Testing user creation...")
    result = await auth_manager.create_user(
        user_id="test-user",
        email="test@example.com",
        tenant_id="test-tenant",
        roles=[TenantRole.OPERATOR]
    )
    assert result is True
    print("✅ User creation successful")
    
    # Test permission checking
    print("\n4. Testing permission checking...")
    has_cluster_read = await auth_manager.check_permission(
        "test-user", Permission.CLUSTER_READ
    )
    assert has_cluster_read is True
    print("✅ Permission checking successful")
    
    # Test permission granting
    print("\n5. Testing permission granting...")
    result = await auth_manager.grant_permission(
        user_id="test-user",
        permission=Permission.CLUSTER_WRITE,
        granted_by="admin"
    )
    assert result is True
    print("✅ Permission granting successful")
    
    # Test user permissions retrieval
    print("\n6. Testing user permissions retrieval...")
    permissions = await auth_manager.get_user_permissions("test-user")
    assert permissions is not None
    assert permissions["user_id"] == "test-user"
    print("✅ User permissions retrieval successful")
    
    # Test tenant users retrieval
    print("\n7. Testing tenant users retrieval...")
    users = await auth_manager.get_tenant_users("test-tenant")
    assert len(users) >= 1
    print("✅ Tenant users retrieval successful")
    
    # Test session management
    print("\n8. Testing session management...")
    session_id = await auth_manager.create_session("test-user", "test-tenant")
    assert session_id is not None
    
    session_info = await auth_manager.validate_session(session_id)
    assert session_info is not None
    print("✅ Session management successful")
    
    # Test audit logging
    print("\n9. Testing audit logging...")
    audit_events = await auth_manager.get_audit_log(
        tenant_id="test-tenant",
        event_type="permission_granted"
    )
    assert len(audit_events) > 0
    print("✅ Audit logging successful")
    
    # Test tenant summary
    print("\n10. Testing tenant summary...")
    summary = await auth_manager.get_tenant_summary("test-tenant")
    assert summary is not None
    assert summary["tenant_id"] == "test-tenant"
    print("✅ Tenant summary successful")
    
    print("\n🎉 All tests passed! Multi-tenant authentication system is working correctly.")
    
    # Print summary
    print("\n📊 Summary:")
    print(f"  - Tenants: {len(auth_manager.tenants)}")
    print(f"  - Users: {len(auth_manager.users)}")
    print(f"  - Sessions: {len(auth_manager.sessions)}")
    print(f"  - Audit Events: {len(auth_manager.audit_events)}")
    print(f"  - Resource Permissions: {len(auth_manager.resource_permissions)}")


if __name__ == "__main__":
    asyncio.run(test_multi_tenant_auth()) 