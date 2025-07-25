#!/usr/bin/env python3
"""
Debug script for UPID CLI Mock Data System
"""

from upid_python.core.mock_data import generate_demo_data
from upid_python.core.mock_api import MockAPIServer

def debug_demo_data():
    """Debug the demo data structure"""
    print("🔍 Debugging UPID CLI Mock Data System...")
    
    # Generate demo data
    demo_data = generate_demo_data('production')
    
    print(f"\n📊 Demo Data Structure:")
    print(f"✅ Scenario Type: {demo_data.get('scenario_type', 'N/A')}")
    print(f"✅ Clusters: {len(demo_data.get('clusters', []))}")
    print(f"✅ Pods by Cluster: {len(demo_data.get('pods', {}))}")
    print(f"✅ Nodes by Cluster: {len(demo_data.get('nodes', {}))}")
    print(f"✅ Optimizations by Cluster: {len(demo_data.get('optimizations', {}))}")
    print(f"✅ Cost Breakdowns by Cluster: {len(demo_data.get('cost_breakdowns', {}))}")
    
    # Show cluster details
    print(f"\n📋 Cluster Details:")
    for i, cluster in enumerate(demo_data.get('clusters', [])):
        cluster_id = cluster.get('id', 'N/A')
        name = cluster.get('name', 'N/A')
        status = cluster.get('status', 'N/A')
        print(f"   {i+1}. ID: {cluster_id}")
        print(f"      Name: {name}")
        print(f"      Status: {status}")
        print(f"      Pods: {len(demo_data.get('pods', {}).get(cluster_id, []))}")
        print(f"      Nodes: {len(demo_data.get('nodes', {}).get(cluster_id, []))}")
        print()
    
    # Test MockAPIServer directly
    print(f"\n🧪 Testing MockAPIServer Directly:")
    server = MockAPIServer('production')
    
    # Test with first cluster
    if demo_data.get('clusters'):
        test_cluster_id = demo_data['clusters'][0]['id']
        print(f"✅ Testing with cluster ID: {test_cluster_id}")
        
        # Test analyze cluster
        response = server.analyze_cluster(test_cluster_id)
        print(f"✅ Analyze Cluster Status: {response.status_code}")
        print(f"✅ Analyze Cluster Success: {response.success}")
        
        if response.success:
            summary = response.data.get('summary', {})
            print(f"✅ Total Pods: {summary.get('total_pods', 0)}")
            print(f"✅ Idle Pods: {summary.get('idle_pods', 0)}")
            print(f"✅ Monthly Cost: ${summary.get('monthly_cost', 0):,.2f}")
        else:
            print(f"❌ Error: {response.error_message}")

if __name__ == "__main__":
    debug_demo_data() 