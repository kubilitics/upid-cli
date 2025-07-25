#!/usr/bin/env python3
"""
Simple Database Test - Verify core database functionality
"""

import sys
import os
from pathlib import Path
import asyncio

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api_server.database.connection import init_database
from api_server.services.user_service import UserService
from api_server.services.cluster_service import ClusterService
from api_server.models.requests import ClusterRegisterRequest
from api_server.database.models import CloudProvider
import uuid


async def test_database_basics():
    """Test basic database operations"""
    
    print("🔍 Testing UPID CLI Database Integration...")
    
    try:
        # Initialize database
        print("📋 Initializing database...")
        await init_database()
        print("✅ Database initialized")
        
        # Re-import SessionLocal after initialization
        from api_server.database.connection import SessionLocal
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Test 1: User Service
            print("\n👤 Testing User Service...")
            user_service = UserService(db)
            
            # The init_sample_data should have created default users
            users, total = await user_service.list_users()
            print(f"✅ Found {len(users)} users in database")
            
            # Test authentication
            demo_user = await user_service.authenticate_user("admin", "admin123")
            if demo_user:
                print("✅ Admin user authentication works")
                print(f"   - Username: {demo_user.username}")
                print(f"   - Email: {demo_user.email}")
                print(f"   - Role: {demo_user.role}")
            else:
                print("❌ Admin user authentication failed")
                return False
            
            # Test 2: Cluster Service
            print("\n🏗️ Testing Cluster Service...")
            cluster_service = ClusterService(db)
            
            # List existing clusters
            clusters, total = await cluster_service.list_clusters(str(demo_user.id))
            print(f"✅ Found {len(clusters)} clusters for admin user")
            
            # Create a test cluster
            test_cluster_name = f"test-cluster-{uuid.uuid4().hex[:8]}"
            test_cluster = await cluster_service.create_cluster(
                ClusterRegisterRequest(
                    name=test_cluster_name,
                    cloud_provider=CloudProvider.AWS,
                    region="us-west-1",
                    tags={"test": "true"}
                ),
                str(demo_user.id)
            )
            
            print(f"✅ Created test cluster: {test_cluster.name}")
            print(f"   - ID: {test_cluster.id}")
            print(f"   - Status: {test_cluster.status}")
            print(f"   - Cloud Provider: {test_cluster.cloud_provider}")
            
            # Retrieve the cluster
            retrieved_cluster = await cluster_service.get_cluster(
                str(test_cluster.id), 
                str(demo_user.id)
            )
            
            if retrieved_cluster:
                print("✅ Successfully retrieved cluster from database")
            else:
                print("❌ Failed to retrieve cluster")
                return False
            
            # Clean up test cluster
            deleted = await cluster_service.delete_cluster(
                str(test_cluster.id), 
                str(demo_user.id)
            )
            
            if deleted:
                print("✅ Successfully deleted test cluster")
            else:
                print("❌ Failed to delete test cluster")
            
            print("\n🎉 All database tests passed!")
            print("✅ Database integration is working correctly!")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_database_basics())
        
        if success:
            print("\n✅ Database Test Suite: PASSED")
            print("🚀 Database is ready for production use!")
            sys.exit(0)
        else:
            print("\n❌ Database Test Suite: FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Database Test Suite: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)