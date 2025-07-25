#!/usr/bin/env python3
"""
Debug Cluster Update - Test the cluster update functionality
"""

import sys
import os
from pathlib import Path
import asyncio
import uuid

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from api_server.main import app
from api_server.database.connection import init_database

async def debug_cluster_update():
    """Debug cluster update functionality"""
    
    print("🔍 Debugging cluster update...")
    
    # Initialize database
    await init_database()
    
    client = TestClient(app)
    
    # Login with demo user
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
        
    auth_data = response.json()
    access_token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create a test cluster
    test_cluster_name = f"debug-cluster-{uuid.uuid4().hex[:8]}"
    new_cluster_data = {
        "name": test_cluster_name,
        "cloud_provider": "aws",
        "region": "us-east-1",
        "tags": {"test": "true", "environment": "testing"}
    }
    
    response = client.post("/api/v1/clusters/", json=new_cluster_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Cluster creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
        
    created_cluster = response.json()
    cluster_id = created_cluster["data"]["id"]
    
    print(f"✅ Created cluster: {cluster_id}")
    print(f"Initial tags: {created_cluster['data']['tags']}")
    
    # Update the cluster
    update_data = {
        "tags": {"test": "true", "environment": "testing", "updated": "true"}
    }
    
    print(f"📝 Updating cluster with data: {update_data}")
    
    response = client.put(f"/api/v1/clusters/{cluster_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Cluster update failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
        
    updated_cluster = response.json()
    print(f"✅ Update response: {updated_cluster}")
    print(f"Updated tags: {updated_cluster['data']['tags']}")
    
    # Check if updated tag exists
    if "updated" in updated_cluster["data"]["tags"]:
        print("✅ 'updated' tag found in response")
        if updated_cluster["data"]["tags"]["updated"] == "true":
            print("✅ 'updated' tag has correct value")
        else:
            print(f"❌ 'updated' tag has wrong value: {updated_cluster['data']['tags']['updated']}")
    else:
        print("❌ 'updated' tag not found in response")
        print(f"Available tags: {list(updated_cluster['data']['tags'].keys())}")
    
    # Clean up - delete the test cluster
    response = client.delete(f"/api/v1/clusters/{cluster_id}", headers=headers)
    if response.status_code == 200:
        print("✅ Test cluster deleted")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(debug_cluster_update())
        
        if success:
            print("\n✅ Cluster Update Debug: SUCCESS")
            sys.exit(0)
        else:
            print("\n❌ Cluster Update Debug: FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Cluster Update Debug: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)