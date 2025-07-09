#!/usr/bin/env python3
"""
Test script for KubernetesMetricsCollector
Tests real pod/node metrics collection using kubectl
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid.core.metrics_collector import KubernetesMetricsCollector

def test_pod_metrics():
    print("🔍 Testing pod metrics collection...")
    try:
        collector = KubernetesMetricsCollector()
        pod_metrics = collector.get_pod_metrics()
        print(f"✅ Pod metrics collected: {len(pod_metrics)} pods")
        if pod_metrics:
            print(f"  Example: {pod_metrics[0]}")
        return True
    except Exception as e:
        print(f"❌ Pod metrics test failed: {e}")
        return False

def test_node_metrics():
    print("🔍 Testing node metrics collection...")
    try:
        collector = KubernetesMetricsCollector()
        node_metrics = collector.get_node_metrics()
        print(f"✅ Node metrics collected: {len(node_metrics)} nodes")
        if node_metrics:
            print(f"  Example: {node_metrics[0]}")
        return True
    except Exception as e:
        print(f"❌ Node metrics test failed: {e}")
        return False

def main():
    print("🚀 UPID Metrics Collector Test")
    print("=" * 50)
    results = []
    results.append(("Pod Metrics", test_pod_metrics()))
    results.append(("Node Metrics", test_node_metrics()))
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    if passed == len(results):
        print("🎉 All tests passed! Metrics Collector is working.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 