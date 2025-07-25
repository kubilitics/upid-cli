#!/usr/bin/env python3
"""
UPID CLI - Production API Server Starter
Starts the FastAPI server with production configurations
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "runtime" / "bundle"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup production environment"""
    # Set API server environment variables
    os.environ['UPID_ENV'] = 'production'
    os.environ['UPID_API_HOST'] = '0.0.0.0'
    os.environ['UPID_API_PORT'] = '8000'
    os.environ['UPID_DATABASE_URL'] = 'sqlite:///upid.db'
    
    # Add runtime site-packages to path
    runtime_site_packages = project_root / "runtime" / "python" / "venv" / "lib" / "python3.13" / "site-packages"
    if runtime_site_packages.exists():
        sys.path.insert(0, str(runtime_site_packages))
    
    logger.info("Environment setup completed")

def start_api_server():
    """Start the API server"""
    try:
        setup_environment()
        
        logger.info("🚀 Starting UPID API Server in production mode...")
        
        # Import after environment setup
        import uvicorn
        from api_server.main import app
        
        # Start server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False,
            workers=1
        )
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.info("Please ensure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_api_server()