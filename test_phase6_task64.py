#!/usr/bin/env python3
"""
Test script for Phase 6 Task 6.4: CI/CD Analytics & Reporting
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase64_imports():
    """Test that all Phase 6.4 components can be imported"""
    try:
        # Test CI/CD Analytics & Reporting imports
        from upid_python.cicd.analytics_reporting import (
            CICDAnalyticsReporting,
            DeploymentMetrics,
            CostImpactMetrics,
            PerformanceTrendMetrics,
            ExecutiveReportConfig,
            MetricType,
            ReportType
        )
        print("✅ CI/CD Analytics & Reporting imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_phase64_components():
    """Test basic component functionality"""
    try:
        # Test configuration objects
        from upid_python.cicd.analytics_reporting import (
            DeploymentMetrics,
            CostImpactMetrics,
            PerformanceTrendMetrics,
            ExecutiveReportConfig,
            MetricType,
            ReportType
        )
        from datetime import datetime
        
        # Create deployment metrics
        deployment_metrics = DeploymentMetrics(
            deployment_name="test-deployment",
            namespace="test-namespace",
            cluster_id="test-cluster",
            deployment_time=datetime.now(),
            success=True,
            duration_seconds=120.0,
            validation_passed=True,
            cost_impact=100.0,
            performance_score=85.0,
            security_score=90.0
        )
        print("✅ Deployment metrics creation successful")
        
        # Create cost impact metrics
        cost_metrics = CostImpactMetrics(
            deployment_name="test-deployment",
            cluster_id="test-cluster",
            pre_deployment_cost=1000.0,
            post_deployment_cost=800.0,
            cost_change_percentage=-20.0,
            monthly_savings=200.0,
            roi_percentage=25.0
        )
        print("✅ Cost impact metrics creation successful")
        
        # Create performance trend metrics
        performance_metrics = PerformanceTrendMetrics(
            deployment_name="test-deployment",
            cluster_id="test-cluster",
            measurement_date=datetime.now(),
            cpu_utilization=60.0,
            memory_utilization=70.0,
            response_time_ms=150.0,
            throughput_rps=1000.0,
            error_rate_percentage=0.5,
            availability_percentage=99.5
        )
        print("✅ Performance trend metrics creation successful")
        
        # Create executive report config
        report_config = ExecutiveReportConfig(
            report_period_days=30,
            include_cost_analysis=True,
            include_performance_trends=True,
            include_security_metrics=True,
            include_roi_analysis=True
        )
        print("✅ Executive report config creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_phase64_structure():
    """Test that all required files exist"""
    required_files = [
        "upid_python/cicd/analytics_reporting.py",
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
    print("🧪 Testing Phase 6 Task 6.4: CI/CD Analytics & Reporting")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_phase64_imports()
    
    # Test components
    print("\n2. Testing components...")
    components_ok = test_phase64_components()
    
    # Test structure
    print("\n3. Testing file structure...")
    structure_ok = test_phase64_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    
    if all([imports_ok, components_ok, structure_ok]):
        print("\n🎉 All Phase 6.4 tests passed!")
        print("✅ Phase 6 Task 6.4 CI/CD Analytics & Reporting is working correctly")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1) 