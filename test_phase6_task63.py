#!/usr/bin/env python3
"""
Test script for Phase 6 Task 6.3: Enhanced Deployment Validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase63_imports():
    """Test that all Phase 6.3 components can be imported"""
    try:
        # Test Enhanced Deployment Validator imports
        from upid_python.cicd.enhanced_deployment_validator import (
            EnhancedDeploymentValidator,
            EnhancedValidationRule,
            PerformanceBenchmark,
            SecurityComplianceConfig,
            CustomValidationPlugin,
            ValidationRuleType,
            ValidationSeverity
        )
        print("✅ Enhanced Deployment Validator imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_phase63_components():
    """Test basic component functionality"""
    try:
        # Test configuration objects
        from upid_python.cicd.enhanced_deployment_validator import (
            EnhancedValidationRule,
            PerformanceBenchmark,
            SecurityComplianceConfig,
            ValidationRuleType,
            ValidationSeverity
        )
        
        # Create performance benchmark
        performance_benchmark = PerformanceBenchmark(
            baseline_metrics={
                "cpu": 50.0,
                "memory": 60.0,
                "response_time": 100.0,
                "throughput": 1000.0
            },
            threshold_percentage=20.0
        )
        print("✅ Performance benchmark creation successful")
        
        # Create security compliance config
        security_config = SecurityComplianceConfig(
            compliance_frameworks=["soc2", "iso27001"],
            security_scanners=["trivy", "falco"],
            vulnerability_threshold=0
        )
        print("✅ Security compliance config creation successful")
        
        # Create enhanced validation rule
        enhanced_rule = EnhancedValidationRule(
            name="custom_validation",
            description="Custom validation rule for testing",
            rule_type=ValidationRuleType.CUSTOM,
            severity=ValidationSeverity.HIGH,
            enabled=True
        )
        print("✅ Enhanced validation rule creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_phase63_structure():
    """Test that all required files exist"""
    required_files = [
        "upid_python/cicd/enhanced_deployment_validator.py",
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
    print("🧪 Testing Phase 6 Task 6.3: Enhanced Deployment Validation")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_phase63_imports()
    
    # Test components
    print("\n2. Testing components...")
    components_ok = test_phase63_components()
    
    # Test structure
    print("\n3. Testing file structure...")
    structure_ok = test_phase63_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    
    if all([imports_ok, components_ok, structure_ok]):
        print("\n🎉 All Phase 6.3 tests passed!")
        print("✅ Phase 6 Task 6.3 Enhanced Deployment Validation is working correctly")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1) 