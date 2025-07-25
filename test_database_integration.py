#!/usr/bin/env python3
"""
UPID CLI API Server Database Integration Test
Tests database operations and API endpoints with real data persistence
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from api_server.main import app
from api_server.database.connection import init_database, close_database, SessionLocal
from api_server.services.user_service import UserService
from api_server.services.cluster_service import ClusterService
from api_server.models.requests import ClusterRegisterRequest
from api_server.database.models import CloudProvider
import uuid
import asyncio


async def test_database_integration():
    """Test comprehensive database integration with API endpoints"""
    
    print("🔍 Testing UPID CLI API Server with Database Integration...")
    
    # Initialize database
    await init_database()
    
    client = TestClient(app)
    
    # Test 1: System endpoints (no auth required)
    print("\n📊 Testing system endpoints...")
    
    response = client.get("/health")
    assert response.status_code == 200
    print("✅ Health check endpoint works")
    
    # Test 2: Authentication with database
    print("\n🔐 Testing database authentication...")
    
    # Login with demo user (should be created during startup)
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    auth_data = response.json()
    assert "access_token" in auth_data
    access_token = auth_data["access_token"]
    print("✅ Database authentication works")
    
    # Set up authentication headers
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 3: User info from database
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["user"]["username"] == "demo"
    assert "id" in user_data["user"]
    user_id = user_data["user"]["id"]
    print("✅ Database user info endpoint works")
    
    # Test 4: List clusters from database
    print("\n🏗️ Testing database cluster operations...")
    
    response = client.get("/api/v1/clusters/", headers=headers)
    assert response.status_code == 200
    clusters_data = response.json()
    assert isinstance(clusters_data["data"], list)
    print(f"✅ Listed {len(clusters_data['data'])} clusters from database")
    
    # Test 5: Create a new cluster in database
    new_cluster_data = {
        "name": f"test-cluster-{uuid.uuid4().hex[:8]}",
        "cloud_provider": "aws",
        "region": "us-east-1",
        "tags": {"test": "true", "environment": "testing"}
    }
    
    response = client.post("/api/v1/clusters/", json=new_cluster_data, headers=headers)
    assert response.status_code == 200
    created_cluster = response.json()
    assert created_cluster["data"]["name"] == new_cluster_data["name"]
    cluster_id = created_cluster["data"]["id"]
    print("✅ Created cluster in database")
    
    # Test 6: Get specific cluster from database
    response = client.get(f"/api/v1/clusters/{cluster_id}", headers=headers)
    assert response.status_code == 200
    cluster_data = response.json()
    assert cluster_data["data"]["id"] == cluster_id
    assert cluster_data["data"]["name"] == new_cluster_data["name"]
    print("✅ Retrieved specific cluster from database")
    
    # Test 7: Update cluster in database
    update_data = {
        "tags": {"test": "true", "environment": "testing", "updated": "true"}
    }
    response = client.put(f"/api/v1/clusters/{cluster_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_cluster = response.json()
    assert updated_cluster["data"]["tags"]["updated"] == "true"
    print("✅ Updated cluster in database")
    
    # Test 8: Test cluster health check
    response = client.post(f"/api/v1/clusters/{cluster_id}/health-check", headers=headers)
    assert response.status_code == 200
    print("✅ Cluster health check works with database")
    
    # Test 9: Delete cluster from database
    response = client.delete(f"/api/v1/clusters/{cluster_id}", headers=headers)
    assert response.status_code == 200
    print("✅ Deleted cluster from database")
    
    # Test 10: Verify cluster is deleted
    response = client.get(f"/api/v1/clusters/{cluster_id}", headers=headers)
    assert response.status_code == 404
    print("✅ Confirmed cluster deletion from database")
    
    # Test 11: Database is working (tested via API endpoints above)
    print("\n✅ Database operations verified through API endpoints")
    
    print("\n🎉 All database integration tests passed!")
    print("🚀 UPID CLI API Server with Database is fully functional!")
    
    return True


async def test_database_services():
    """Test database services directly"""
    print("\n🔧 Testing database services directly...")
    
    db = SessionLocal()
    try:
        # Test creating a user
        user_service = UserService(db)
        
        # Create test user
        test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        test_user = await user_service.create_user(
            username=test_username,
            email=f"{test_username}@test.com",
            password="testpass123",
            full_name="Test User"
        )
        
        assert test_user.username == test_username
        print("✅ Created user directly via database service")
        
        # Test user authentication
        auth_user = await user_service.authenticate_user(test_username, "testpass123")
        assert auth_user is not None
        assert auth_user.id == test_user.id
        print("✅ Authenticated user via database service")
        
        # Test creating cluster for user
        cluster_service = ClusterService(db)
        test_cluster = await cluster_service.create_cluster(
            ClusterRegisterRequest(
                name=f"test-db-cluster-{uuid.uuid4().hex[:8]}",
                cloud_provider=CloudProvider.AWS,
                region="us-west-1",
                tags={"test": "database_service"}
            ),
            str(test_user.id)
        )
        
        assert test_cluster.name.startswith("test-db-cluster")
        assert test_cluster.owner_id == test_user.id
        print("✅ Created cluster directly via database service")
        
        # Test getting cluster
        retrieved_cluster = await cluster_service.get_cluster(str(test_cluster.id), str(test_user.id))
        assert retrieved_cluster is not None
        assert retrieved_cluster.id == test_cluster.id
        print("✅ Retrieved cluster via database service")
        
        # Clean up
        await cluster_service.delete_cluster(str(test_cluster.id), str(test_user.id))
        await user_service.delete_user(str(test_user.id))
        print("✅ Cleaned up test data")
        
    finally:
        db.close()


if __name__ == "__main__":
    try:
        # Test API integration and database services
        async def run_all_tests():
            success = await test_database_integration()
            await test_database_services()
            return success
        
        success = asyncio.run(run_all_tests())
        
        if success:
            print("\n✅ Database Integration Test Suite: PASSED")
            print("🎉 Database is fully integrated and functional!")
            sys.exit(0)
    except Exception as e:
        print(f"\n❌ Database Integration Test Suite: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)