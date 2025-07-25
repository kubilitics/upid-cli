#!/usr/bin/env python3
"""
UPID CLI API Server Startup Script
Enterprise-grade FastAPI server launcher with proper configuration
"""

import sys
import os
import logging
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Start the UPID CLI API Server"""
    try:
        logger.info("🚀 Starting UPID CLI API Server...")
        
        # Import here to ensure proper path setup
        from api_server.core.config import get_settings
        
        settings = get_settings()
        
        logger.info(f"📡 Server will be available at: http://{settings.host}:{settings.port}")
        logger.info(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
        logger.info(f"🔍 Interactive API Explorer: http://{settings.host}:{settings.port}/redoc")
        
        # Start server
        uvicorn.run(
            "api_server.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            workers=1 if settings.debug else settings.workers,
            log_level=settings.log_level.lower(),
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()