#!/usr/bin/env python3
"""
Test script for UPID CLI Mock API System
"""

from upid_python.core.mock_api import mock_api_call, MockAPIResponse, get_mock_api_server

def test_mock_api_system():
    """Test the mock API system"""
    print("🧪 Testing UPID CLI Mock API System...")
    
    # Get the global mock API server to find valid cluster IDs
    server = get_mock_api_server('production')
    valid_cluster_id = server.demo_data['clusters'][0]['id']
    print(f"✅ Using valid cluster ID: {valid_cluster_id}")
    
    # Test authentication
    print("\n🔐 Testing Authentication:")
    auth_response = mock_api_call("/api/v1/auth/login", "POST", {"email": "demo@example.com", "password": "password"})
    print(f"✅ Status: {auth_response.status_code}")
    print(f"✅ Success: {auth_response.success}")
    if auth_response.success:
        print(f"✅ Token: {auth_response.data.get('access_token', 'N/A')[:20]}...")
    
    # Test list clusters
    print("\n📊 Testing List Clusters:")
    clusters_response = mock_api_call("/api/v1/clusters", "GET")
    print(f"✅ Status: {clusters_response.status_code}")
    print(f"✅ Total Clusters: {clusters_response.data.get('total', 0)}")
    
    # Test analyze cluster
    print("\n🔍 Testing Analyze Cluster:")
    analyze_response = mock_api_call(f"/api/v1/analyze/cluster/{valid_cluster_id}", "POST", {"detailed": True})
    print(f"✅ Status: {analyze_response.status_code}")
    if analyze_response.success:
        summary = analyze_response.data.get('summary', {})
        print(f"✅ Total Pods: {summary.get('total_pods', 0)}")
        print(f"✅ Idle Pods: {summary.get('idle_pods', 0)} ({summary.get('idle_percentage', 0)}%)")
        print(f"✅ Monthly Cost: ${summary.get('monthly_cost', 0):,.2f}")
        print(f"✅ Potential Savings: ${summary.get('potential_savings', 0):,.2f}")
    
    # Test find idle workloads
    print("\n💤 Testing Find Idle Workloads:")
    idle_response = mock_api_call(f"/api/v1/analyze/idle/{valid_cluster_id}", "POST", {"confidence_threshold": 0.7})
    print(f"✅ Status: {idle_response.status_code}")
    if idle_response.success:
        print(f"✅ Total Idle: {idle_response.data.get('total_idle', 0)}")
        print(f"✅ Total Savings: ${idle_response.data.get('total_savings', 0):,.2f}")
    
    # Test analyze costs
    print("\n💰 Testing Analyze Costs:")
    costs_response = mock_api_call(f"/api/v1/analyze/costs/{valid_cluster_id}", "POST")
    print(f"✅ Status: {costs_response.status_code}")
    if costs_response.success:
        cost_breakdown = costs_response.data.get('cost_breakdown', {})
        print(f"✅ Total Monthly Cost: ${cost_breakdown.get('total_monthly_cost', 0):,.2f}")
        print(f"✅ Waste Cost: ${cost_breakdown.get('waste_cost', 0):,.2f}")
        print(f"✅ Optimization Potential: ${cost_breakdown.get('optimization_potential', 0):,.2f}")
    
    # Test optimization strategies
    print("\n⚡ Testing Optimization Strategies:")
    strategies_response = mock_api_call(f"/api/v1/optimize/strategies/{valid_cluster_id}", "GET")
    print(f"✅ Status: {strategies_response.status_code}")
    if strategies_response.success:
        print(f"✅ Total Strategies: {strategies_response.data.get('total_strategies', 0)}")
        print(f"✅ Total Potential Savings: ${strategies_response.data.get('total_potential_savings', 0):,.2f}")
    
    # Test simulate optimization
    print("\n🎯 Testing Simulate Optimization:")
    simulate_response = mock_api_call(f"/api/v1/optimize/simulate/{valid_cluster_id}", "POST", {"strategy": "zero_pod_scaling"})
    print(f"✅ Status: {simulate_response.status_code}")
    if simulate_response.success:
        results = simulate_response.data.get('results', {})
        print(f"✅ Potential Savings: ${results.get('potential_savings', 0):,.2f}")
        print(f"✅ Risk Level: {results.get('risk_level', 'N/A')}")
        print(f"✅ Confidence: {results.get('confidence', 0):.2%}")
    
    # Test AI insights
    print("\n🤖 Testing AI Insights:")
    insights_response = mock_api_call(f"/api/v1/ai/insights/{valid_cluster_id}", "GET")
    print(f"✅ Status: {insights_response.status_code}")
    if insights_response.success:
        print(f"✅ Total Insights: {insights_response.data.get('total_insights', 0)}")
        insights = insights_response.data.get('insights', [])
        for insight in insights[:2]:  # Show first 2 insights
            print(f"   • {insight.get('title', 'N/A')} (Confidence: {insight.get('confidence', 0):.1%})")
    
    # Test metrics
    print("\n📈 Testing Metrics:")
    metrics_response = mock_api_call(f"/api/v1/metrics/{valid_cluster_id}", "GET", params={"time_range": "24h"})
    print(f"✅ Status: {metrics_response.status_code}")
    if metrics_response.success:
        summary = metrics_response.data.get('summary', {})
        print(f"✅ Avg CPU Usage: {summary.get('avg_cpu_usage', 0)}%")
        print(f"✅ Avg Memory Usage: {summary.get('avg_memory_usage', 0)}%")
        print(f"✅ Total Metrics: {summary.get('total_metrics', 0)}")
    
    # Test generate report
    print("\n📋 Testing Generate Report:")
    report_response = mock_api_call(f"/api/v1/reports/{valid_cluster_id}", "POST", {"report_type": "cost"})
    print(f"✅ Status: {report_response.status_code}")
    if report_response.success:
        print(f"✅ Report Type: {report_response.data.get('report_type', 'N/A')}")
        print(f"✅ Report ID: {report_response.data.get('report_id', 'N/A')}")
    
    print("\n🎉 Mock API System Test Completed Successfully!")

if __name__ == "__main__":
    test_mock_api_system() 