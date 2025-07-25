#!/usr/bin/env python3
"""
Quick test script for UPID CLI API Server
Tests basic functionality of all major endpoints
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from api_server.main import app

def test_api_endpoints():
    """Test all major API endpoints"""
    
    print("🔍 Testing UPID CLI API Server endpoints...")
    
    client = TestClient(app)
    
    # Test system endpoints (no auth required)
    print("\n📊 Testing system endpoints...")
    
    # Health check
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check endpoint works")
    
    # System info
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "UPID CLI API Server" in data["service"]
    print("✅ System info endpoint works")
    
    # Root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "UPID CLI API Server" in data["message"]
    print("✅ Root endpoint works")
    
    # Test authentication endpoints
    print("\n🔐 Testing authentication endpoints...")
    
    # Login with demo user
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    auth_data = response.json()
    assert "access_token" in auth_data
    access_token = auth_data["access_token"]
    print("✅ Login endpoint works")
    
    # Set up authentication headers
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test user info
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["user"]["username"] == "demo"
    print("✅ User info endpoint works")
    
    # Test cluster endpoints
    print("\n🏗️ Testing cluster management endpoints...")
    
    # List clusters
    response = client.get("/api/v1/clusters/", headers=headers)
    assert response.status_code == 200
    clusters_data = response.json()
    assert len(clusters_data["data"]) > 0
    cluster_id = clusters_data["data"][0]["id"]
    print("✅ List clusters endpoint works")
    
    # Get specific cluster
    response = client.get(f"/api/v1/clusters/{cluster_id}", headers=headers)
    assert response.status_code == 200
    cluster_data = response.json()
    assert cluster_data["data"]["id"] == cluster_id
    print("✅ Get cluster endpoint works")
    
    # Test analysis endpoints
    print("\n🔍 Testing analysis endpoints...")
    
    # Cluster analysis
    analysis_request = {
        "cluster_id": cluster_id,
        "analysis_type": "cluster",
        "include_metrics": True,
        "time_range_hours": 24
    }
    response = client.post("/api/v1/analyze/cluster", json=analysis_request, headers=headers)
    assert response.status_code == 200
    analysis_data = response.json()
    assert analysis_data["data"]["cluster_id"] == cluster_id
    print("✅ Cluster analysis endpoint works")
    
    # Idle workload analysis
    idle_request = {
        "cluster_id": cluster_id,
        "namespace": "default",
        "confidence_threshold": 0.85,
        "cpu_threshold_percent": 5.0,
        "memory_threshold_percent": 10.0,
        "exclude_health_checks": True,
        "time_range_hours": 24
    }
    response = client.post("/api/v1/analyze/idle", json=idle_request, headers=headers)
    assert response.status_code == 200
    idle_data = response.json()
    assert idle_data["data"]["cluster_id"] == cluster_id
    print("✅ Idle analysis endpoint works")
    
    # Test optimization endpoints
    print("\n⚡ Testing optimization endpoints...")
    
    # Zero-pod scaling (dry run)
    zero_pod_request = {
        "cluster_id": cluster_id,
        "namespace": "default",
        "dry_run": True,
        "safety_checks": True,
        "rollback_timeout_minutes": 5
    }
    response = client.post("/api/v1/optimize/zero-pod", json=zero_pod_request, headers=headers)
    assert response.status_code == 200
    optimization_data = response.json()
    assert optimization_data["data"]["cluster_id"] == cluster_id
    assert optimization_data["data"]["dry_run"] == True
    print("✅ Zero-pod scaling endpoint works")
    
    # Resource optimization (dry run)
    resource_request = {
        "cluster_id": cluster_id,
        "namespace": "default",
        "optimization_target": "cost",
        "cpu_optimization": True,
        "memory_optimization": True,
        "safety_margin_percent": 20.0,
        "dry_run": True
    }
    response = client.post("/api/v1/optimize/resources", json=resource_request, headers=headers)
    assert response.status_code == 200
    resource_data = response.json()
    assert resource_data["data"]["cluster_id"] == cluster_id
    print("✅ Resource optimization endpoint works")
    
    # Test reporting endpoints
    print("\n📊 Testing reporting endpoints...")
    
    # Executive report
    report_request = {
        "cluster_ids": [cluster_id],
        "time_range_days": 30,
        "include_projections": True,
        "include_recommendations": True,
        "format": "json"
    }
    response = client.post("/api/v1/reports/executive", json=report_request, headers=headers)
    assert response.status_code == 200
    report_data = response.json()
    assert cluster_id in report_data["data"]["clusters_analyzed"]
    print("✅ Executive report endpoint works")
    
    print("\n🎉 All API endpoint tests passed!")
    print("🚀 UPID CLI API Server is fully functional!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_api_endpoints()
        if success:
            print("\n✅ API Server Test Suite: PASSED")
            sys.exit(0)
    except Exception as e:
        print(f"\n❌ API Server Test Suite: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)