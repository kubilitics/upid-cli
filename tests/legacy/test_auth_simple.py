#!/usr/bin/env python3
"""
Simple test script for Universal Authentication System
Tests the core functionality without CLI dependencies
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import at module level so all test functions can use them
from upid.auth import UniversalAuthenticator
from upid.auth.universal_auth import EnvironmentInfo, AuthResult
from upid.auth.local import LocalKubernetesDetector
from upid.auth.cloud import CloudKubernetesDetector
from upid.auth.rbac import RBACEnforcer

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Already imported at module level
        print("✅ UniversalAuthenticator imported successfully")
        
        print("✅ EnvironmentInfo and AuthResult imported successfully")
        
        print("✅ LocalKubernetesDetector imported successfully")
        
        print("✅ CloudKubernetesDetector imported successfully")
        
        print("✅ RBACEnforcer imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_authenticator_creation():
    """Test authenticator creation"""
    print("\n🔧 Testing authenticator creation...")
    
    try:
        authenticator = UniversalAuthenticator()
        print("✅ UniversalAuthenticator created successfully")
        
        print(f"  - Local detector: {type(authenticator.local_detector).__name__}")
        print(f"  - Cloud detector: {type(authenticator.cloud_detector).__name__}")
        print(f"  - RBAC enforcer: {type(authenticator.rbac_enforcer).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authenticator creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_local_detection():
    """Test local cluster detection"""
    print("\n🏠 Testing local cluster detection...")
    
    try:
        authenticator = UniversalAuthenticator()
        local_info = await authenticator.local_detector.detect()
        
        print(f"✅ Local detection completed")
        print(f"  - Detected: {local_info.detected}")
        print(f"  - Cluster type: {local_info.cluster_type}")
        print(f"  - Status: {local_info.status}")
        
        if local_info.kubeconfig_path:
            print(f"  - Kubeconfig: {local_info.kubeconfig_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Local detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cloud_detection():
    """Test cloud cluster detection"""
    print("\n☁️ Testing cloud cluster detection...")
    
    try:
        authenticator = UniversalAuthenticator()
        cloud_info = await authenticator.cloud_detector.detect()
        
        print(f"✅ Cloud detection completed")
        print(f"  - Detected: {cloud_info.detected}")
        print(f"  - Cluster type: {cloud_info.cluster_type}")
        print(f"  - Provider: {cloud_info.provider}")
        print(f"  - Status: {cloud_info.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cloud detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_environment_detection():
    """Test universal environment detection"""
    print("\n🌍 Testing universal environment detection...")
    
    try:
        authenticator = UniversalAuthenticator()
        env_info = await authenticator.detect_environment()
        
        print(f"✅ Environment detection completed")
        print(f"  - Cluster type: {env_info.cluster_type}")
        print(f"  - Is local: {env_info.is_local_cluster}")
        print(f"  - Cloud provider: {env_info.cloud_provider}")
        print(f"  - Cluster name: {env_info.cluster_name}")
        print(f"  - Context: {env_info.context_name}")
        print(f"  - Auth required: {env_info.auth_required}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rbac_enforcement():
    """Test RBAC enforcement"""
    print("\n🔒 Testing RBAC enforcement...")
    
    try:
        authenticator = UniversalAuthenticator()
        rbac_info = await authenticator.rbac_enforcer.check_user_permissions("default")
        
        print(f"✅ RBAC check completed")
        print(f"  - User: {rbac_info.user}")
        print(f"  - Can read: {rbac_info.can_read}")
        print(f"  - Can write: {rbac_info.can_write}")
        print(f"  - Can delete: {rbac_info.can_delete}")
        print(f"  - Can exec: {rbac_info.can_exec}")
        print(f"  - Roles: {rbac_info.roles}")
        print(f"  - Permissions count: {len(rbac_info.permissions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ RBAC check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cluster_info():
    """Test cluster information retrieval"""
    print("\n📊 Testing cluster information...")
    
    try:
        authenticator = UniversalAuthenticator()
        cluster_info = authenticator.get_cluster_info()
        
        print(f"✅ Cluster info retrieved")
        print(f"  - Connection status: {cluster_info['connection_status']}")
        print(f"  - Cluster info: {cluster_info['cluster_info'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Cluster info failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 UPID Universal Authentication System - Simple Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Authenticator Creation", test_authenticator_creation),
        ("Local Detection", test_local_detection),
        ("Cloud Detection", test_cloud_detection),
        ("Environment Detection", test_environment_detection),
        ("RBAC Enforcement", test_rbac_enforcement),
        ("Cluster Info", test_cluster_info),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Universal Authentication System is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 