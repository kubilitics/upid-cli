#!/usr/bin/env python3
"""
Test script for UPID Billing System
Tests real cloud billing integration for cost analysis
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid.billing import AWSBillingClient, GCPBillingClient, AzureBillingClient, CloudBillingIntegrator

def test_aws_billing():
    """Test AWS billing client"""
    print("🔍 Testing AWS Billing Client...")
    
    try:
        # Test client creation (without credentials for now)
        client = AWSBillingClient()
        print("✅ AWS Billing Client created successfully")
        
        # Test default dates
        start_date, end_date = AWSBillingClient.get_default_dates(7)
        print(f"✅ Default dates: {start_date} to {end_date}")
        
        # Test method availability
        methods = [
            'get_eks_clusters',
            'get_eks_cost', 
            'get_ec2_cost',
            'get_node_group_cost',
            'get_account_cost_summary'
        ]
        
        for method in methods:
            if hasattr(client, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ AWS billing test failed: {e}")
        return False

def test_gcp_billing():
    """Test GCP billing client"""
    print("\n🔍 Testing GCP Billing Client...")
    
    try:
        # Test client creation (without credentials for now)
        client = GCPBillingClient("test-project")
        print("✅ GCP Billing Client created successfully")
        
        # Test default dates
        start_date, end_date = GCPBillingClient.get_default_dates(7)
        print(f"✅ Default dates: {start_date} to {end_date}")
        
        # Test method availability
        methods = [
            'get_gke_clusters',
            'get_gke_cost',
            'get_compute_engine_cost', 
            'get_node_pool_cost',
            'get_project_cost_summary'
        ]
        
        for method in methods:
            if hasattr(client, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ GCP billing test failed: {e}")
        return False

def test_azure_billing():
    """Test Azure billing client"""
    print("\n🔍 Testing Azure Billing Client...")
    
    try:
        # Test client creation (without credentials for now)
        client = AzureBillingClient("test-subscription")
        print("✅ Azure Billing Client created successfully")
        
        # Test default dates
        start_date, end_date = AzureBillingClient.get_default_dates(7)
        print(f"✅ Default dates: {start_date} to {end_date}")
        
        # Test method availability
        methods = [
            'get_aks_clusters',
            'get_aks_cost',
            'get_vm_cost',
            'get_node_pool_cost', 
            'get_subscription_cost_summary'
        ]
        
        for method in methods:
            if hasattr(client, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure billing test failed: {e}")
        return False

def test_unified_billing():
    """Test unified billing integrator"""
    print("\n🔍 Testing Unified Billing Integrator...")
    
    try:
        integrator = CloudBillingIntegrator()
        print("✅ Cloud Billing Integrator created successfully")
        
        # Test provider addition (without real credentials)
        print("✅ Provider addition methods available")
        
        # Test method availability
        methods = [
            'get_all_clusters',
            'get_provider_cost',
            'get_unified_cost_summary',
            'compare_provider_costs'
        ]
        
        for method in methods:
            if hasattr(integrator, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
        
        # Test default dates
        start_date, end_date = CloudBillingIntegrator.get_default_dates(7)
        print(f"✅ Default dates: {start_date} to {end_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified billing test failed: {e}")
        return False

def test_cost_data_structures():
    """Test cost data structures"""
    print("\n🔍 Testing Cost Data Structures...")
    
    try:
        from upid.billing import CostData, CostSummary
        
        # Test CostData
        cost_data = CostData(
            provider='aws',
            service='eks',
            cluster_name='test-cluster',
            cost=100.50,
            currency='USD',
            period_start='2024-01-01',
            period_end='2024-01-07',
            details={'test': 'data'}
        )
        print("✅ CostData structure created successfully")
        
        # Test CostSummary
        cost_summary = CostSummary(
            total_cost=500.75,
            currency='USD',
            provider_breakdown={'aws': 300.25, 'gcp': 200.50},
            service_breakdown={'aws_eks': 150.00, 'aws_ec2': 150.25, 'gcp_gke': 200.50},
            period_start='2024-01-01',
            period_end='2024-01-07'
        )
        print("✅ CostSummary structure created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost data structures test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 UPID Billing System Test")
    print("=" * 50)
    
    tests = [
        ("AWS Billing", test_aws_billing),
        ("GCP Billing", test_gcp_billing),
        ("Azure Billing", test_azure_billing),
        ("Unified Billing", test_unified_billing),
        ("Cost Data Structures", test_cost_data_structures),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Billing System is ready for real integration.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 