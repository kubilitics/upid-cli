#!/usr/bin/env python3
"""
Test script for UPID CLI Mock Data System
"""

from upid_python.core.mock_data import generate_demo_data, get_demo_summary

def test_mock_data_system():
    """Test the mock data system"""
    print("🧪 Testing UPID CLI Mock Data System...")
    
    # Test production scenario
    print("\n📊 Production Scenario:")
    data = generate_demo_data('production')
    summary = get_demo_summary('production')
    
    print(f"✅ Clusters: {summary['total_clusters']}")
    print(f"✅ Pods: {summary['total_pods']}")
    print(f"✅ Nodes: {summary['total_nodes']}")
    print(f"✅ Idle Pods: {summary['idle_pods']} ({summary['idle_pod_percentage']}%)")
    print(f"✅ Monthly Cost: ${summary['total_monthly_cost']:,.2f}")
    print(f"✅ Savings Potential: ${summary['total_savings_potential']:,.2f} ({summary['savings_percentage']}%)")
    
    # Test staging scenario
    print("\n📊 Staging Scenario:")
    summary_staging = get_demo_summary('staging')
    print(f"✅ Clusters: {summary_staging['total_clusters']}")
    print(f"✅ Pods: {summary_staging['total_pods']}")
    print(f"✅ Monthly Cost: ${summary_staging['total_monthly_cost']:,.2f}")
    
    # Test development scenario
    print("\n📊 Development Scenario:")
    summary_dev = get_demo_summary('development')
    print(f"✅ Clusters: {summary_dev['total_clusters']}")
    print(f"✅ Pods: {summary_dev['total_pods']}")
    print(f"✅ Monthly Cost: ${summary_dev['total_monthly_cost']:,.2f}")
    
    print("\n🎉 Mock Data System Test Completed Successfully!")

if __name__ == "__main__":
    test_mock_data_system() 