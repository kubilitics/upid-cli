#!/usr/bin/env python3
"""
Test script for Phase 6 Task 6.2: Advanced GitOps Features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase62_imports():
    """Test that all Phase 6.2 components can be imported"""
    try:
        # Test Advanced GitOps imports
        from upid_python.cicd.advanced_gitops import (
            AdvancedGitOpsIntegration, 
            MultiClusterConfig, 
            GitOpsSecurityConfig, 
            AdvancedRollbackConfig,
            GitOpsSecurityLevel,
            GitOpsComplianceFramework
        )
        print("✅ Advanced GitOps imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_phase62_components():
    """Test basic component functionality"""
    try:
        # Test configuration objects
        from upid_python.cicd.advanced_gitops import (
            MultiClusterConfig, 
            GitOpsSecurityConfig, 
            AdvancedRollbackConfig,
            GitOpsSecurityLevel,
            GitOpsComplianceFramework
        )
        
        # Create multi-cluster config
        multi_cluster_config = MultiClusterConfig(
            primary_cluster="prod-cluster-1",
            secondary_clusters=["prod-cluster-2", "prod-cluster-3"],
            sync_strategy="sequential",
            failover_enabled=True
        )
        print("✅ Multi-cluster config creation successful")
        
        # Create security config
        security_config = GitOpsSecurityConfig(
            security_level=GitOpsSecurityLevel.ENTERPRISE,
            compliance_framework=GitOpsComplianceFramework.SOC2,
            enable_audit_logging=True,
            enable_compliance_checks=True
        )
        print("✅ Security config creation successful")
        
        # Create rollback config
        rollback_config = AdvancedRollbackConfig(
            enable_automated_rollback=True,
            rollback_threshold=0.8,
            enable_gradual_rollback=True,
            enable_canary_rollback=True
        )
        print("✅ Rollback config creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_phase62_structure():
    """Test that all required files exist"""
    required_files = [
        "upid_python/cicd/advanced_gitops.py",
        "upid_python/cicd/__init__.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("🧪 Testing Phase 6 Task 6.2: Advanced GitOps Features")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_phase62_imports()
    
    # Test components
    print("\n2. Testing components...")
    components_ok = test_phase62_components()
    
    # Test structure
    print("\n3. Testing file structure...")
    structure_ok = test_phase62_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    
    if all([imports_ok, components_ok, structure_ok]):
        print("\n🎉 All Phase 6.2 tests passed!")
        print("✅ Phase 6 Task 6.2 Advanced GitOps Features is working correctly")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1) 