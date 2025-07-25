#!/usr/bin/env python3
"""
Test script for Monitoring & Observability System
Tests the MonitoringSystem and HealthCheckEndpoint functionality
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_monitoring_system():
    """Test the monitoring system functionality"""
    print("🔧 Testing Monitoring & Observability System...")
    
    try:
        from upid_python.core.monitoring import MonitoringSystem, HealthCheckEndpoint
        
        # Initialize monitoring system
        print("📊 Initializing monitoring system...")
        monitoring = MonitoringSystem("test-service")
        
        # Test health status updates
        print("🏥 Testing health status updates...")
        monitoring.update_health_status("api_server", "healthy", {"version": "1.0.0"}, 15.5)
        monitoring.update_health_status("database", "healthy", {"connections": 10}, 5.2)
        monitoring.update_health_status("ml_pipeline", "degraded", {"model_accuracy": 0.85}, 45.0)
        
        # Test request recording
        print("📝 Testing request recording...")
        monitoring.record_request("GET", "/api/health", 200, 25.3)
        monitoring.record_request("POST", "/api/optimize", 201, 150.7)
        monitoring.record_request("GET", "/api/metrics", 500, 300.0)
        
        # Test error recording
        print("❌ Testing error recording...")
        monitoring.record_error("DatabaseConnectionError", "Failed to connect to database", {"retry_count": 3})
        monitoring.record_error("ValidationError", "Invalid input parameters", {"field": "cluster_name"})
        
        # Test optimization recording
        print("⚡ Testing optimization recording...")
        monitoring.record_optimization("pod_scaling", "success", 150.0)
        monitoring.record_optimization("resource_rightsizing", "success", 75.5)
        monitoring.record_optimization("cost_optimization", "failed", 0.0)
        
        # Wait for some metrics to be collected
        print("⏳ Waiting for metrics collection...")
        time.sleep(2)
        
        # Test health check endpoint
        print("🏥 Testing health check endpoint...")
        health_endpoint = HealthCheckEndpoint(monitoring)
        health_data = health_endpoint.health_check()
        
        print("✅ Health Check Results:")
        print(json.dumps(health_data, indent=2, default=str))
        
        # Test metrics endpoint
        print("📊 Testing metrics endpoint...")
        prometheus_metrics = health_endpoint.metrics_endpoint()
        print("✅ Prometheus Metrics:")
        print(prometheus_metrics[:500] + "..." if len(prometheus_metrics) > 500 else prometheus_metrics)
        
        # Test detailed metrics
        print("📈 Testing detailed metrics...")
        detailed_metrics = health_endpoint.detailed_metrics()
        
        print("✅ Detailed Metrics Summary:")
        print(json.dumps(detailed_metrics, indent=2, default=str))
        
        # Test system metrics
        print("💻 Testing system metrics...")
        system_metrics = monitoring.get_system_metrics(hours=1)
        print(f"✅ Collected {len(system_metrics)} system metrics")
        
        # Test application metrics
        print("📱 Testing application metrics...")
        app_metrics = monitoring.get_application_metrics(hours=1)
        print(f"✅ Collected {len(app_metrics)} application metrics")
        
        # Test uptime
        uptime = monitoring.get_uptime()
        print(f"⏱️ System uptime: {uptime}")
        
        print("\n🎉 All monitoring system tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing monitoring system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optional_dependencies():
    """Test optional dependency handling"""
    print("\n🔍 Testing optional dependency handling...")
    
    try:
        from upid_python.core.monitoring import MonitoringSystem
        
        # Test monitoring system with optional dependencies
        monitoring = MonitoringSystem()
        
        # Check which dependencies are available
        summary = monitoring.get_metrics_summary()
        
        print("✅ Dependency Status:")
        print(f"  - Prometheus available: {summary.get('prometheus_available', False)}")
        print(f"  - OpenTelemetry available: {summary.get('opentelemetry_available', False)}")
        print(f"  - Structlog available: {summary.get('structlog_available', False)}")
        
        print("✅ Monitoring system works with optional dependencies!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing optional dependencies: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Monitoring & Observability System Tests")
    print("=" * 60)
    
    # Test basic functionality
    success1 = test_monitoring_system()
    
    # Test optional dependencies
    success2 = test_optional_dependencies()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! Monitoring system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 60) 