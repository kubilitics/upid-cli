#!/usr/bin/env python3
"""
Test Connections Script
Simple test to verify the test-connections functionality.
"""

import asyncio
import sys

# Add the project root to the path
sys.path.insert(0, '.')

from upid.core.metrics_collector import KubernetesMetricsCollector


async def test_connections():
    """Test the connections functionality."""
    print("🔌 Testing Metric Collection Connections...")
    
    collector = KubernetesMetricsCollector()
    results = collector.test_connections()
    
    print("\n" + "="*60)
    print("🔌 METRIC COLLECTION CONNECTION TEST")
    print("="*60)
    
    for service, result in results.items():
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        
        if status == 'connected':
            print(f"✅ {service.upper()}: {message}")
        elif status == 'error':
            print(f"❌ {service.upper()}: {message}")
        elif status == 'not_configured':
            print(f"⚠️  {service.upper()}: {message}")
        else:
            print(f"❓ {service.upper()}: {message}")
    
    print(f"\n📋 SETUP INSTRUCTIONS:")
    print(f"1. Kubernetes: Ensure kubectl is configured and cluster is accessible")
    print(f"2. Prometheus: Set UPID_PROMETHEUS_URL environment variable")
    print(f"3. cAdvisor: Set UPID_CADVISOR_URL environment variable")
    print(f"4. Custom Metrics: Set UPID_CUSTOM_METRICS_URL environment variable")
    print(f"\nExample:")
    print(f"export UPID_PROMETHEUS_URL='http://prometheus:9090'")
    print(f"export UPID_CADVISOR_URL='http://cadvisor:8080'")
    print(f"python test_connections.py")


if __name__ == "__main__":
    asyncio.run(test_connections()) 