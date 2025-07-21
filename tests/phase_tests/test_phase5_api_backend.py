#!/usr/bin/env python3
"""
Phase 5: Real API Backend Tests
Comprehensive tests for FastAPI backend with authentication, endpoints, and integration.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Import API components
from upid.api.main import app
from upid.api.auth import (
    create_access_token, verify_token, authenticate_user,
    get_current_user, require_permission, require_admin
)
from upid.core.storage_integration import StorageIntegration
from upid.core.intelligence import IntelligenceEngine
from upid.core.optimization_engine import ConfidenceOptimizationEngine as OptimizationEngine


class TestAPIAuthentication:
    """Test API authentication functionality."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {
            "sub": "test-user-001",
            "username": "testuser",
            "permissions": ["read", "write"],
            "organization": "test-org"
        }
        
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = verify_token(token)
        assert payload["sub"] == "test-user-001"
        assert payload["username"] == "testuser"
        assert "read" in payload["permissions"]
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        data = {
            "sub": "test-user-001",
            "username": "testuser"
        }
        
        # Create token with short expiration
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(Exception):
            verify_token(token)
    
    def test_authenticate_user_valid(self):
        """Test user authentication with valid credentials."""
        user = asyncio.run(authenticate_user("admin", "password"))
        assert user is not None
        assert user["username"] == "admin"
        assert user["user_id"] == "admin-001"
        assert "admin" in user["permissions"]
    
    def test_authenticate_user_invalid(self):
        """Test user authentication with invalid credentials."""
        user = asyncio.run(authenticate_user("invalid", "wrong"))
        assert user is None


class TestAPIEndpoints:
    """Test API endpoints functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert data["status"] == "healthy"
    
    def test_api_status_endpoint(self, client):
        """Test API status endpoint."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "api_version" in data
        assert "status" in data
        assert "features" in data
        assert data["status"] == "operational"


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    def test_login_endpoint_success(self, client):
        """Test successful login."""
        login_data = {
            "username": "admin",
            "password": "password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user_id" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == "admin-001"
    
    def test_login_endpoint_failure(self, client):
        """Test failed login."""
        login_data = {
            "username": "invalid",
            "password": "wrong"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]
    
    def test_register_endpoint(self, client):
        """Test user registration."""
        register_data = {
            "username": "newuser",
            "email": "newuser@upid.io",
            "password": "password",
            "organization": "test-org"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["username"] == "newuser"
    
    def test_profile_endpoint_with_token(self, client):
        """Test profile endpoint with valid token."""
        # First login to get token
        login_data = {"username": "admin", "password": "password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to access profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert "permissions" in data


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers."""
        login_data = {"username": "admin", "password": "password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_intelligence_analysis_endpoint(self, client, auth_headers):
        """Test intelligence analysis endpoint."""
        analysis_data = {
            "cluster_name": "test-cluster",
            "namespace": "default",
            "time_range": "24h",
            "include_business_metrics": True,
            "include_predictions": True
        }
        
        response = client.post("/api/v1/analyze/intelligence", 
                             json=analysis_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis_id" in data
        assert "timestamp" in data
        assert "cluster_info" in data
        assert "recommendations" in data
    
    def test_metrics_collection_endpoint(self, client, auth_headers):
        """Test metrics collection endpoint."""
        metrics_data = {
            "cluster_name": "test-cluster",
            "namespace": "default",
            "time_range": "1h",
            "include_prometheus": True,
            "include_cadvisor": True,
            "include_custom": True
        }
        
        response = client.post("/api/v1/analyze/metrics", 
                             json=metrics_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "cluster_name" in data
        assert "timestamp" in data
        assert "pod_metrics" in data
        assert "node_metrics" in data
        assert "collection_status" in data
    
    def test_business_correlation_endpoint(self, client, auth_headers):
        """Test business correlation endpoint."""
        correlation_data = {
            "cluster_name": "test-cluster",
            "namespace": "default",
            "time_range": "7d"
        }
        
        response = client.post("/api/v1/analyze/business-correlation", 
                             json=correlation_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "correlation_id" in data
        assert "timestamp" in data
        assert "business_impact" in data
        assert "kpi_correlations" in data
    
    def test_analysis_summary_endpoint(self, client, auth_headers):
        """Test analysis summary endpoint."""
        response = client.get("/api/v1/analyze/analysis/summary", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_analyses" in data
        assert "recent_analyses" in data
        assert "average_cpu_utilization" in data
        assert "total_cost_savings" in data


class TestOptimizationEndpoints:
    """Test optimization endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers."""
        login_data = {"username": "admin", "password": "password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_resource_optimization_endpoint(self, client, auth_headers):
        """Test resource optimization endpoint."""
        optimization_data = {
            "cluster_name": "test-cluster",
            "namespace": "default",
            "optimization_type": "resource",
            "include_cost_analysis": True,
            "include_business_impact": True,
            "dry_run": True
        }
        
        response = client.post("/api/v1/optimize/resources", 
                             json=optimization_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "optimization_id" in data
        assert "timestamp" in data
        assert "current_state" in data
        assert "optimized_state" in data
        assert "recommendations" in data
    
    def test_cost_analysis_endpoint(self, client, auth_headers):
        """Test cost analysis endpoint."""
        cost_data = {
            "cluster_name": "test-cluster",
            "namespace": "default",
            "time_range": "30d",
            "include_historical": True,
            "include_projections": True
        }
        
        response = client.post("/api/v1/optimize/cost-analysis", 
                             json=cost_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis_id" in data
        assert "timestamp" in data
        assert "current_costs" in data
        assert "historical_costs" in data
        assert "optimization_opportunities" in data
    
    def test_recommendations_endpoint(self, client, auth_headers):
        """Test optimization recommendations endpoint."""
        response = client.get("/api/v1/optimize/recommendations", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "cluster_name" in data
        assert "priority" in data
        assert "recommendations" in data
        assert "total_count" in data
    
    def test_optimization_summary_endpoint(self, client, auth_headers):
        """Test optimization summary endpoint."""
        response = client.get("/api/v1/optimize/summary", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_optimizations" in data
        assert "applied_optimizations" in data
        assert "total_savings" in data
        assert "pending_recommendations" in data


class TestReportingEndpoints:
    """Test reporting endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers."""
        login_data = {"username": "admin", "password": "password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_report_generation_endpoint(self, client, auth_headers):
        """Test report generation endpoint."""
        report_data = {
            "report_type": "executive",
            "cluster_name": "test-cluster",
            "namespace": "default",
            "time_range": "30d",
            "include_charts": True,
            "include_recommendations": True,
            "format": "json"
        }
        
        response = client.post("/api/v1/report/generate", 
                             json=report_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "report_id" in data
        assert "report_type" in data
        assert "timestamp" in data
        assert "data" in data
    
    def test_dashboard_endpoint(self, client, auth_headers):
        """Test dashboard endpoint."""
        response = client.get("/api/v1/report/dashboard", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "dashboard_type" in data
        assert "cluster_name" in data
        assert "time_range" in data
        assert "data" in data
    
    def test_kpis_endpoint(self, client, auth_headers):
        """Test KPIs endpoint."""
        response = client.get("/api/v1/report/kpis", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "cluster_name" in data
        assert "time_range" in data
        assert "kpis" in data
    
    def test_alerts_endpoint(self, client, auth_headers):
        """Test alerts endpoint."""
        response = client.get("/api/v1/report/alerts", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "total_count" in data
        assert isinstance(data["alerts"], list)


class TestStorageEndpoints:
    """Test storage endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers."""
        login_data = {"username": "admin", "password": "password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_storage_summary_endpoint(self, client, auth_headers):
        """Test storage summary endpoint."""
        response = client.get("/api/v1/storage/summary", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "summary" in data
    
    def test_storage_analytics_endpoint(self, client, auth_headers):
        """Test storage analytics endpoint."""
        response = client.get("/api/v1/storage/analytics", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "data_type" in data
        assert "time_range" in data
        assert "analytics" in data
    
    def test_storage_metrics_endpoint(self, client, auth_headers):
        """Test storage metrics endpoint."""
        response = client.get("/api/v1/storage/metrics", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "metric_type" in data
        assert "metrics" in data
    
    def test_storage_health_endpoint(self, client, auth_headers):
        """Test storage health endpoint."""
        response = client.get("/api/v1/storage/health", 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "health" in data


class TestAPIIntegration:
    """Test API integration scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    def test_complete_workflow(self, client):
        """Test complete API workflow."""
        # 1. Login
        login_data = {"username": "admin", "password": "password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check API status
        status_response = client.get("/api/v1/status", headers=headers)
        assert status_response.status_code == 200
        
        # 3. Run intelligence analysis
        analysis_data = {
            "cluster_name": "test-cluster",
            "time_range": "24h"
        }
        analysis_response = client.post("/api/v1/analyze/intelligence", 
                                     json=analysis_data, headers=headers)
        assert analysis_response.status_code == 200
        
        # 4. Get optimization recommendations
        recommendations_response = client.get("/api/v1/optimize/recommendations", 
                                           headers=headers)
        assert recommendations_response.status_code == 200
        
        # 5. Generate report
        report_data = {
            "report_type": "executive",
            "time_range": "7d"
        }
        report_response = client.post("/api/v1/report/generate", 
                                   json=report_data, headers=headers)
        assert report_response.status_code == 200
        
        # 6. Check storage summary
        storage_response = client.get("/api/v1/storage/summary", 
                                   headers=headers)
        assert storage_response.status_code == 200
    
    def test_error_handling(self, client):
        """Test API error handling."""
        # Test unauthorized access
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 401
        
        # Test invalid endpoint
        response = client.get("/api/v1/invalid/endpoint")
        assert response.status_code == 404
        
        # Test invalid login
        login_data = {"username": "invalid", "password": "wrong"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401


def run_phase5_tests():
    """Run all Phase 5 tests."""
    print("🚀 Running Phase 5: Real API Backend Tests...")
    
    # Test authentication
    print("\n📋 Testing API Authentication...")
    auth_tests = TestAPIAuthentication()
    auth_tests.test_create_access_token()
    auth_tests.test_verify_token_expired()
    auth_tests.test_authenticate_user_valid()
    auth_tests.test_authenticate_user_invalid()
    print("✅ Authentication tests passed")
    
    # Test endpoints
    print("\n📋 Testing API Endpoints...")
    endpoint_tests = TestAPIEndpoints()
    client = endpoint_tests.client()
    endpoint_tests.test_root_endpoint(client)
    endpoint_tests.test_health_endpoint(client)
    endpoint_tests.test_api_status_endpoint(client)
    print("✅ Endpoint tests passed")
    
    # Test authentication endpoints
    print("\n📋 Testing Authentication Endpoints...")
    auth_endpoint_tests = TestAuthenticationEndpoints()
    client = auth_endpoint_tests.client()
    auth_endpoint_tests.test_login_endpoint_success(client)
    auth_endpoint_tests.test_login_endpoint_failure(client)
    auth_endpoint_tests.test_register_endpoint(client)
    auth_endpoint_tests.test_profile_endpoint_with_token(client)
    print("✅ Authentication endpoint tests passed")
    
    # Test analysis endpoints
    print("\n📋 Testing Analysis Endpoints...")
    analysis_tests = TestAnalysisEndpoints()
    client = analysis_tests.client()
    auth_headers = analysis_tests.auth_headers(client)
    analysis_tests.test_intelligence_analysis_endpoint(client, auth_headers)
    analysis_tests.test_metrics_collection_endpoint(client, auth_headers)
    analysis_tests.test_business_correlation_endpoint(client, auth_headers)
    analysis_tests.test_analysis_summary_endpoint(client, auth_headers)
    print("✅ Analysis endpoint tests passed")
    
    # Test optimization endpoints
    print("\n📋 Testing Optimization Endpoints...")
    optimization_tests = TestOptimizationEndpoints()
    client = optimization_tests.client()
    auth_headers = optimization_tests.auth_headers(client)
    optimization_tests.test_resource_optimization_endpoint(client, auth_headers)
    optimization_tests.test_cost_analysis_endpoint(client, auth_headers)
    optimization_tests.test_recommendations_endpoint(client, auth_headers)
    optimization_tests.test_optimization_summary_endpoint(client, auth_headers)
    print("✅ Optimization endpoint tests passed")
    
    # Test reporting endpoints
    print("\n📋 Testing Reporting Endpoints...")
    reporting_tests = TestReportingEndpoints()
    client = reporting_tests.client()
    auth_headers = reporting_tests.auth_headers(client)
    reporting_tests.test_report_generation_endpoint(client, auth_headers)
    reporting_tests.test_dashboard_endpoint(client, auth_headers)
    reporting_tests.test_kpis_endpoint(client, auth_headers)
    reporting_tests.test_alerts_endpoint(client, auth_headers)
    print("✅ Reporting endpoint tests passed")
    
    # Test storage endpoints
    print("\n📋 Testing Storage Endpoints...")
    storage_tests = TestStorageEndpoints()
    client = storage_tests.client()
    auth_headers = storage_tests.auth_headers(client)
    storage_tests.test_storage_summary_endpoint(client, auth_headers)
    storage_tests.test_storage_analytics_endpoint(client, auth_headers)
    storage_tests.test_storage_metrics_endpoint(client, auth_headers)
    storage_tests.test_storage_health_endpoint(client, auth_headers)
    print("✅ Storage endpoint tests passed")
    
    # Test integration scenarios
    print("\n📋 Testing API Integration...")
    integration_tests = TestAPIIntegration()
    client = integration_tests.client()
    integration_tests.test_complete_workflow(client)
    integration_tests.test_error_handling(client)
    print("✅ Integration tests passed")
    
    print("\n🎉 Phase 5: Real API Backend - ALL TESTS PASSED!")
    print("✅ FastAPI backend with authentication")
    print("✅ RESTful endpoints for all core functionality")
    print("✅ JWT token management")
    print("✅ Comprehensive error handling")
    print("✅ Integration with intelligence engines")
    print("✅ Storage integration")
    print("✅ Production-ready API backend")


if __name__ == "__main__":
    run_phase5_tests() 