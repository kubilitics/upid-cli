#!/usr/bin/env python3
"""
UPID CLI API Server - Enterprise FastAPI Backend
Production-ready REST API server for UPID CLI operations

This is the core backend that the UPID CLI communicates with.
Implements all analysis, optimization, and management endpoints.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import centralized configuration
try:
    from upid_config import get_config
    upid_config = get_config()
except ImportError:
    upid_config = None

from api_server.routers import analyze, optimize, auth, clusters, reports
from api_server.database.connection import init_database, close_database
from api_server.core.config import get_settings
from api_server.core.auth import verify_token
from api_server.core.middleware import add_process_time_header

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting UPID CLI API Server...")
    await init_database()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down UPID CLI API Server...")
    await close_database()
    logger.info("✅ Database connections closed")

# Get configuration values
if upid_config:
    api_title = f"{upid_config.product.name} API Server"
    api_description = f"""
    **{upid_config.product.description}**
    
    Production-ready REST API for UPID CLI operations including:
    - Cluster analysis and resource optimization
    - ML-powered cost prediction and anomaly detection  
    - Zero-pod scaling with safety guarantees
    - Business intelligence and ROI reporting
    - Multi-tenant enterprise features
    
    Built for enterprise-grade reliability, security, and performance.
    """
    api_version = upid_config.product.api_version
    contact_info = {
        "name": f"{upid_config.product.name} Support",
        "email": upid_config.product.support_email,
        "url": upid_config.product.homepage
    }
else:
    api_title = "UPID CLI API Server"
    api_description = """
    **Enterprise Kubernetes Cost Optimization Platform**
    
    Production-ready REST API for UPID CLI operations including:
    - Cluster analysis and resource optimization
    - ML-powered cost prediction and anomaly detection  
    - Zero-pod scaling with safety guarantees
    - Business intelligence and ROI reporting
    - Multi-tenant enterprise features
    
    Built for enterprise-grade reliability, security, and performance.
    """
    api_version = "1.0.0"
    contact_info = {
        "name": "UPID Support",
        "email": "support@upid.io",
        "url": "https://upid.io/support"
    }

# FastAPI app instance
app = FastAPI(
    title=api_title,
    description=api_description,
    version=api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact=contact_info,
    license_info={
        "name": "Enterprise License",
        "url": "https://upid.io/license"
    }
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(add_process_time_header)

# Health check endpoint (no auth required)
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "upid-api-server"
    }

# System info endpoint (no auth required)  
@app.get("/info", tags=["System"])
async def system_info():
    """System information endpoint"""
    return {
        "service": "UPID CLI API Server",
        "version": "1.0.0",
        "description": "Enterprise Kubernetes Cost Optimization Platform",
        "features": [
            "Cluster Analysis & Resource Optimization", 
            "ML-Powered Cost Prediction",
            "Zero-Pod Scaling with Safety Guarantees",
            "Business Intelligence & ROI Reporting",
            "Multi-Tenant Enterprise Security"
        ],
        "docs": "/docs",
        "health": "/health"
    }

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token and return user info"""
    try:
        user_info = await verify_token(credentials.credentials)
        return user_info
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Include routers with authentication
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    analyze.router,
    prefix="/api/v1/analyze", 
    tags=["Analysis"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    optimize.router,
    prefix="/api/v1/optimize",
    tags=["Optimization"], 
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    clusters.router,
    prefix="/api/v1/clusters",
    tags=["Clusters"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    reports.router,
    prefix="/api/v1/reports", 
    tags=["Reports"],
    dependencies=[Depends(get_current_user)]
)

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "message": "🚀 UPID CLI API Server - Enterprise Kubernetes Cost Optimization Platform",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "info": "/info"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": True,
        "status_code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "error": True,
        "status_code": 500,
        "message": "Internal server error",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    """Run the API server directly"""
    settings = get_settings()
    
    logger.info("🚀 Starting UPID CLI API Server...")
    logger.info(f"📡 Server will be available at: http://localhost:{settings.port}")
    logger.info(f"📚 API Documentation: http://localhost:{settings.port}/docs")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
        log_level="info"
    )