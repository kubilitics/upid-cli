#!/usr/bin/env python3
"""
Debug Database Connection - Test the connection initialization
"""

import sys
import os
from pathlib import Path
import asyncio

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def debug_connection():
    """Debug database connection initialization"""
    
    print("🔍 Debugging UPID CLI Database Connection...")
    
    try:
        print("📋 Importing modules...")
        from api_server.database.connection import init_database, SessionLocal, engine
        from api_server.core.config import get_settings
        
        print(f"✅ Modules imported")
        
        # Check initial state
        print(f"🔍 Initial state:")
        print(f"   - engine: {engine}")
        print(f"   - SessionLocal: {SessionLocal}")
        
        # Get settings
        settings = get_settings()
        print(f"🔧 Settings:")
        print(f"   - database_url: {settings.database_url}")
        print(f"   - debug: {settings.debug}")
        
        # Initialize database
        print("📋 Calling init_database()...")
        await init_database()
        
        # Check state after initialization
        print(f"🔍 State after init_database():")
        print(f"   - engine: {engine}")
        print(f"   - SessionLocal: {SessionLocal}")
        
        # Try to import again
        from api_server.database.connection import SessionLocal as SessionLocal2
        print(f"   - SessionLocal (re-imported): {SessionLocal2}")
        
        if SessionLocal2:
            print("✅ SessionLocal is properly initialized!")
            
            # Try to create a session
            db = SessionLocal2()
            print(f"✅ Session created: {db}")
            db.close()
            print("✅ Session closed successfully")
            
        else:
            print("❌ SessionLocal is still None after initialization")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(debug_connection())
        
        if success:
            print("\n✅ Database Connection Debug: PASSED")
            sys.exit(0)
        else:
            print("\n❌ Database Connection Debug: FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Database Connection Debug: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)