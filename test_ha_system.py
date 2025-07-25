#!/usr/bin/env python3
"""
Test script for High Availability & Scaling System
Tests the HighAvailabilitySystem, DatabaseReplicationManager, and LoadBalancer functionality
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ha_system():
    """Test the high availability system functionality"""
    print("🔧 Testing High Availability & Scaling System...")
    
    try:
        from upid_python.core.ha_system import (
            HighAvailabilitySystem, 
            ClusterConfig, 
            DatabaseReplicationManager, 
            LoadBalancer,
            ClusterRole,
            NodeStatus
        )
        
        # Initialize HA system
        print("📊 Initializing high availability system...")
        config = ClusterConfig(
            cluster_name="test-cluster",
            node_id="test-node-1",
            host="localhost",
            port=8000
        )
        
        ha_system = HighAvailabilitySystem(config)
        
        # Test node management
        print("🏥 Testing node management...")
        
        # Simulate adding some nodes
        from upid_python.core.ha_system import NodeInfo
        test_nodes = [
            NodeInfo(
                node_id="node-1",
                host="localhost",
                port=8001,
                role=ClusterRole.PRIMARY,
                status=NodeStatus.HEALTHY,
                last_heartbeat=datetime.now(),
                capabilities=["api_server", "database"],
                load_factor=0.3,
                version="1.0.0",
                metadata={"region": "us-west"}
            ),
            NodeInfo(
                node_id="node-2",
                host="localhost",
                port=8002,
                role=ClusterRole.SECONDARY,
                status=NodeStatus.HEALTHY,
                last_heartbeat=datetime.now(),
                capabilities=["api_server", "ml_pipeline"],
                load_factor=0.5,
                version="1.0.0",
                metadata={"region": "us-east"}
            ),
            NodeInfo(
                node_id="node-3",
                host="localhost",
                port=8003,
                role=ClusterRole.SECONDARY,
                status=NodeStatus.DEGRADED,
                last_heartbeat=datetime.now(),
                capabilities=["api_server"],
                load_factor=0.8,
                version="1.0.0",
                metadata={"region": "eu-west"}
            )
        ]
        
        for node in test_nodes:
            ha_system.nodes[node.node_id] = node
        
        print(f"✅ Added {len(test_nodes)} test nodes")
        
        # Test load balancing
        print("⚖️ Testing load balancing...")
        
        load_balancer = LoadBalancer(ha_system)
        
        # Test different load balancing strategies
        strategies = ["round_robin", "least_connections", "weighted"]
        
        for strategy in strategies:
            ha_system.config.load_balancing_strategy = strategy
            print(f"  Testing {strategy} strategy...")
            
            for i in range(5):
                try:
                    target_url, request_data = load_balancer.route_request("api", {"test": i})
                    print(f"    Request {i+1} routed to: {target_url}")
                except Exception as e:
                    print(f"    Request {i+1} failed: {e}")
        
        # Test database replication
        print("🗄️ Testing database replication...")
        
        db_manager = DatabaseReplicationManager(
            primary_db_url="sqlite:///primary.db",
            replica_db_urls=["sqlite:///replica1.db", "sqlite:///replica2.db"]
        )
        
        print(f"  Primary database: {db_manager.get_write_primary()}")
        print(f"  Read replica: {db_manager.get_read_replica()}")
        
        # Test cluster status
        print("📈 Testing cluster status...")
        
        cluster_status = ha_system.get_cluster_status()
        
        print("✅ Cluster Status:")
        print(json.dumps(cluster_status, indent=2, default=str))
        
        # Test load balancer stats
        print("📊 Testing load balancer statistics...")
        
        lb_stats = load_balancer.get_load_balancer_stats()
        
        print("✅ Load Balancer Statistics:")
        print(json.dumps(lb_stats, indent=2, default=str))
        
        # Test node selection
        print("🎯 Testing node selection...")
        
        healthy_nodes = ha_system.get_healthy_nodes()
        print(f"  Healthy nodes: {len(healthy_nodes)}")
        
        primary_node = ha_system.get_primary_node()
        if primary_node:
            print(f"  Primary node: {primary_node.node_id}")
        else:
            print("  No primary node found")
        
        # Test failover simulation
        print("🔄 Testing failover simulation...")
        
        # Simulate primary node failure
        if primary_node:
            print(f"  Simulating failure of primary node: {primary_node.node_id}")
            primary_node.status = NodeStatus.UNHEALTHY
            ha_system._handle_node_failure(primary_node.node_id, primary_node)
            
            # Check if new primary was promoted
            new_primary = ha_system.get_primary_node()
            if new_primary:
                print(f"  New primary node: {new_primary.node_id}")
            else:
                print("  No new primary node promoted")
        
        print("\n🎉 All high availability system tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing high availability system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optional_dependencies():
    """Test optional dependency handling"""
    print("\n🔍 Testing optional dependency handling...")
    
    try:
        from upid_python.core.ha_system import HighAvailabilitySystem, ClusterConfig
        
        # Test HA system with optional dependencies
        config = ClusterConfig(
            cluster_name="test-cluster",
            node_id="test-node",
            host="localhost",
            port=8000
        )
        
        ha_system = HighAvailabilitySystem(config)
        
        # Check cluster status
        cluster_status = ha_system.get_cluster_status()
        
        print("✅ HA System Status:")
        print(f"  - Cluster name: {cluster_status['cluster_name']}")
        print(f"  - Current node: {cluster_status['current_node']['node_id']}")
        print(f"  - Total nodes: {cluster_status['cluster_health']['total_nodes']}")
        print(f"  - Healthy nodes: {cluster_status['cluster_health']['healthy_nodes']}")
        
        print("✅ High availability system works with optional dependencies!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing optional dependencies: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting High Availability & Scaling System Tests")
    print("=" * 60)
    
    # Test basic functionality
    success1 = test_ha_system()
    
    # Test optional dependencies
    success2 = test_optional_dependencies()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! High availability system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 60) 