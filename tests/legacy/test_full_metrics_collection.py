#!/usr/bin/env python3
"""
Test Full Metrics Collection
Comprehensive test for Prometheus, cAdvisor, and custom metrics integration.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, '.')

from upid.core.metrics_collector import KubernetesMetricsCollector


async def test_full_metrics_collection():
    """Test the complete metrics collection with all integrations."""
    print("🔌 Testing Full Metrics Collection...")
    
    # Test with different configurations
    test_configs = [
        {
            'name': 'Default Configuration',
            'env_vars': {},
            'description': 'Testing with default localhost endpoints'
        },
        {
            'name': 'Custom Prometheus',
            'env_vars': {
                'UPID_PROMETHEUS_URL': 'http://prometheus:9090'
            },
            'description': 'Testing with custom Prometheus endpoint'
        },
        {
            'name': 'Custom cAdvisor',
            'env_vars': {
                'UPID_CADVISOR_URL': 'http://cadvisor:8080'
            },
            'description': 'Testing with custom cAdvisor endpoint'
        },
        {
            'name': 'Custom Metrics',
            'env_vars': {
                'UPID_CUSTOM_METRICS_URL': 'http://metrics:8080'
            },
            'description': 'Testing with custom metrics endpoint'
        },
        {
            'name': 'Full Configuration',
            'env_vars': {
                'UPID_PROMETHEUS_URL': 'http://prometheus:9090',
                'UPID_CADVISOR_URL': 'http://cadvisor:8080',
                'UPID_CUSTOM_METRICS_URL': 'http://metrics:8080',
                'UPID_METRICS_TIMEOUT': '15'
            },
            'description': 'Testing with all custom endpoints'
        }
    ]
    
    for config in test_configs:
        print(f"\n{'='*60}")
        print(f"Testing: {config['name']}")
        print(f"Description: {config['description']}")
        print(f"{'='*60}")
        
        # Set environment variables
        original_env = {}
        for key, value in config['env_vars'].items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            # Test connection status
            collector = KubernetesMetricsCollector()
            connection_results = collector.test_connections()
            
            print(f"Connection Test Results:")
            for service, result in connection_results.items():
                status = result.get('status', 'unknown')
                message = result.get('message', 'No message')
                
                if status == 'connected':
                    print(f"  ✅ {service.upper()}: {message}")
                elif status == 'error':
                    print(f"  ❌ {service.upper()}: {message}")
                elif status == 'not_configured':
                    print(f"  ⚠️  {service.upper()}: {message}")
                else:
                    print(f"  ❓ {service.upper()}: {message}")
            
            # Test metrics collection
            try:
                metrics = await collector.collect_metrics()
                print(f"\nMetrics Collection Results:")
                print(f"  ✅ CPU Usage: {metrics.get('cpu_usage', {}).get('average', 'N/A')}%")
                print(f"  ✅ Memory Usage: {metrics.get('memory_usage', {}).get('average', 'N/A')}%")
                print(f"  ✅ Pod Count: {metrics.get('pod_count', {}).get('count', 'N/A')}")
                
                # Check Prometheus data
                prometheus_data = metrics.get('prometheus', {})
                if 'error' not in prometheus_data:
                    print(f"  ✅ Prometheus: Data collected successfully")
                else:
                    print(f"  ⚠️  Prometheus: {prometheus_data.get('error', 'Unknown error')}")
                
                # Check cAdvisor data
                cadvisor_data = metrics.get('cadvisor', {})
                if 'error' not in cadvisor_data:
                    print(f"  ✅ cAdvisor: Data collected successfully")
                else:
                    print(f"  ⚠️  cAdvisor: {cadvisor_data.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"  ❌ Metrics collection failed: {e}")
            
            # Test individual metric collection methods
            await test_individual_methods(collector)
            
        finally:
            # Restore original environment variables
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


async def test_individual_methods(collector: KubernetesMetricsCollector):
    """Test individual metric collection methods."""
    print(f"\nIndividual Method Tests:")
    
    # Test Prometheus metrics
    try:
        prom_data = collector.get_prometheus_metrics()
        if 'error' not in prom_data:
            print(f"  ✅ Prometheus metrics: {len(prom_data)} metrics collected")
        else:
            print(f"  ⚠️  Prometheus metrics: {prom_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Prometheus metrics failed: {e}")
    
    # Test cAdvisor metrics
    try:
        cadvisor_data = collector.get_cadvisor_metrics()
        if 'error' not in cadvisor_data:
            print(f"  ✅ cAdvisor metrics: {cadvisor_data.get('container_count', 0)} containers")
        else:
            print(f"  ⚠️  cAdvisor metrics: {cadvisor_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ cAdvisor metrics failed: {e}")
    
    # Test custom metrics
    try:
        custom_data = collector.get_custom_metrics('test_metric')
        if 'error' not in custom_data:
            print(f"  ✅ Custom metrics: {custom_data.get('metric_name', 'N/A')}")
        else:
            print(f"  ⚠️  Custom metrics: {custom_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"  ❌ Custom metrics failed: {e}")


def test_environment_setup():
    """Test environment variable setup and validation."""
    print("🔧 Testing Environment Setup...")
    
    # Test environment variable handling
    test_vars = {
        'UPID_PROMETHEUS_URL': 'http://test-prometheus:9090',
        'UPID_CADVISOR_URL': 'http://test-cadvisor:8080',
        'UPID_CUSTOM_METRICS_URL': 'http://test-metrics:8080',
        'UPID_METRICS_TIMEOUT': '20'
    }
    
    # Set test environment variables
    original_env = {}
    for key, value in test_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        collector = KubernetesMetricsCollector()
        
        print(f"  ✅ Prometheus URL: {collector.prometheus_url}")
        print(f"  ✅ cAdvisor URL: {collector.cadvisor_url}")
        print(f"  ✅ Custom Metrics URL: {collector.custom_metrics_url}")
        print(f"  ✅ Timeout: {collector.timeout}s")
        
        # Test that environment variables are properly read
        assert collector.prometheus_url == test_vars['UPID_PROMETHEUS_URL']
        assert collector.cadvisor_url == test_vars['UPID_CADVISOR_URL']
        assert collector.custom_metrics_url == test_vars['UPID_CUSTOM_METRICS_URL']
        assert collector.timeout == int(test_vars['UPID_METRICS_TIMEOUT'])
        
        print(f"  ✅ Environment variable validation passed")
        
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_error_handling():
    """Test error handling for various failure scenarios."""
    print("🛡️  Testing Error Handling...")
    
    collector = KubernetesMetricsCollector()
    
    # Test with invalid URLs
    test_cases = [
        {
            'name': 'Invalid Prometheus URL',
            'method': lambda: collector.get_prometheus_metrics('http://invalid:9999'),
            'expected': 'error'
        },
        {
            'name': 'Invalid cAdvisor URL',
            'method': lambda: collector.get_cadvisor_metrics('http://invalid:9999'),
            'expected': 'error'
        },
        {
            'name': 'Invalid Custom Metrics URL',
            'method': lambda: collector.get_custom_metrics('test', 'http://invalid:9999'),
            'expected': 'error'
        }
    ]
    
    for test_case in test_cases:
        try:
            result = test_case['method']()
            if 'error' in result:
                print(f"  ✅ {test_case['name']}: Properly handled error")
            else:
                print(f"  ⚠️  {test_case['name']}: Expected error but got success")
        except Exception as e:
            print(f"  ✅ {test_case['name']}: Exception properly caught: {e}")


async def main():
    """Run all metrics collection tests."""
    print("🚀 Starting Full Metrics Collection Tests\n")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Error Handling", test_error_handling),
        ("Full Metrics Collection", test_full_metrics_collection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {test_name}")
            print(f"{'='*60}")
            
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
            
            results.append((test_name, True))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            print(f"❌ {test_name} - FAILED")
            print(f"   Error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All metrics collection tests passed!")
        print("\n📋 CUSTOMER SETUP INSTRUCTIONS:")
        print("1. Set environment variables for your monitoring stack:")
        print("   export UPID_PROMETHEUS_URL='http://your-prometheus:9090'")
        print("   export UPID_CADVISOR_URL='http://your-cadvisor:8080'")
        print("   export UPID_CUSTOM_METRICS_URL='http://your-metrics:8080'")
        print("2. Test connections: upid intelligence test-connections")
        print("3. Run analysis: upid intelligence analyze")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 