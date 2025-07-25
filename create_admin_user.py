#!/usr/bin/env python3
"""
Create Admin User - Simple script to create an admin user for testing
"""

import sys
import os
from pathlib import Path
import asyncio

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def create_admin_user():
    """Create admin user for testing"""
    
    print("🔍 Creating admin user for UPID CLI...")
    
    try:
        # Initialize database first
        from api_server.database.connection import init_database
        await init_database()
        
        # Import after initialization
        from api_server.database.connection import SessionLocal
        from api_server.database.models import User
        import uuid
        import bcrypt
        from datetime import datetime
        
        # Create session
        db = SessionLocal()
        
        try:
            # Check if admin user exists
            existing_admin = db.query(User).filter(User.username == "admin").first()
            if existing_admin:
                print("✅ Admin user already exists")
                return True
            
            # Hash password 
            password_bytes = "admin123".encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            # Create admin user
            admin_user = User(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@upid.io",
                hashed_password=hashed_password,
                full_name="UPID Administrator",
                is_active=True,
                is_superuser=True,
                role="admin",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(admin_user)
            db.commit()
            
            print("✅ Admin user created successfully!")
            print(f"   - Username: admin")
            print(f"   - Password: admin123")
            print(f"   - Email: admin@upid.io")
            print(f"   - Role: admin")
            
            # Test authentication
            test_user = db.query(User).filter(User.username == "admin").first()
            if test_user:
                # Test password verification
                stored_password = test_user.hashed_password.encode('utf-8')
                if bcrypt.checkpw(password_bytes, stored_password):
                    print("✅ Password verification works!")
                else:
                    print("❌ Password verification failed!")
                    return False
            
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(create_admin_user())
        
        if success:
            print("\n✅ Admin User Creation: SUCCESS")
            sys.exit(0)
        else:
            print("\n❌ Admin User Creation: FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Admin User Creation: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)