"""
UPID API Backend - Main FastAPI Application
Real API backend for UPID CLI with authentication, intelligence, and optimization endpoints.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from ..core.config import Config
from ..core.auth import AuthManager
from ..core.api_client import UPIDAPIClient
from ..core.storage_integration import StorageIntegration
from ..core.security import security_middleware, audit_logger, SecurityLevel, AuditEvent
from .auth import get_current_user, authenticate_user
from .endpoints.auth import router as auth_router
from .endpoints.analyze import router as analyze_router
from .endpoints.optimize import router as optimize_router
from .endpoints.report import router as report_router
from .endpoints.storage import router as storage_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="UPID API",
    description="Universal Pod Intelligence Director API - Kubernetes Resource Optimization Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# CORS configuration with enhanced security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

# Add security middleware
app.middleware("http")(security_middleware)

# Global dependencies
config = Config()
auth_manager = AuthManager(config)
api_client = UPIDAPIClient(config, auth_manager)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Starting UPID API Backend...")
    logger.info(f"API Version: {app.version}")
    logger.info(f"Environment: {config.get('environment', 'development')}")
    
    # Log startup event
    audit_logger.log_event(AuditEvent(
        event_id="startup",
        user_id="system",
        action="application_startup",
        resource_type="system",
        resource_id="api",
        timestamp=datetime.now(timezone.utc),
        ip_address="localhost",
        user_agent="system",
        success=True,
        details={"version": app.version, "environment": config.get('environment', 'development')},
        security_level=SecurityLevel.HIGH
    ))


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down UPID API Backend...")
    
    # Log shutdown event
    audit_logger.log_event(AuditEvent(
        event_id="shutdown",
        user_id="system",
        action="application_shutdown",
        resource_type="system",
        resource_id="api",
        timestamp=datetime.now(timezone.utc),
        ip_address="localhost",
        user_agent="system",
        success=True,
        details={"version": app.version},
        security_level=SecurityLevel.HIGH
    ))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "UPID API - Kubernetes Resource Optimization Platform",
        "version": app.version,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "security": {
            "mfa_required": True,
            "rate_limiting": True,
            "audit_logging": True,
            "session_management": True
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check core services
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": app.version,
            "services": {
                "api": "healthy",
                "auth": "healthy",
                "storage": "healthy",
                "security": "healthy"
            },
            "security": {
                "jwt_enabled": True,
                "rate_limiting": True,
                "audit_logging": True,
                "session_management": True
            }
        }
        
        # Check storage
        try:
            with StorageIntegration() as storage:
                stats = storage.get_storage_summary()
                health_status["services"]["storage"] = "healthy"
                health_status["storage_stats"] = stats.get("storage_stats", {})
        except Exception as e:
            health_status["services"]["storage"] = f"unhealthy: {str(e)}"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_version": "v1",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": {
            "authentication": True,
            "intelligence": True,
            "optimization": True,
            "storage": True,
            "analytics": True,
            "security": {
                "mfa": True,
                "rate_limiting": True,
                "audit_logging": True,
                "session_management": True,
                "password_validation": True
            }
        }
    }


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(analyze_router, prefix="/api/v1/analyze", tags=["Analysis"])
app.include_router(optimize_router, prefix="/api/v1/optimize", tags=["Optimization"])
app.include_router(report_router, prefix="/api/v1/report", tags=["Reporting"])
app.include_router(storage_router, prefix="/api/v1/storage", tags=["Storage"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler with audit logging."""
    # Log the error
    audit_logger.log_event(AuditEvent(
        event_id="error",
        user_id="unknown",
        action=f"http_error_{exc.status_code}",
        resource_type="http",
        resource_id=str(request.url),
        timestamp=datetime.now(timezone.utc),
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", ""),
        success=False,
        details={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path)
        },
        security_level=SecurityLevel.MEDIUM
    ))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler with audit logging."""
    logger.error(f"Unhandled exception: {exc}")
    
    # Log the error
    audit_logger.log_event(AuditEvent(
        event_id="error",
        user_id="unknown",
        action="unhandled_exception",
        resource_type="http",
        resource_id=str(request.url),
        timestamp=datetime.now(timezone.utc),
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", ""),
        success=False,
        details={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": str(request.url.path)
        },
        security_level=SecurityLevel.HIGH
    ))
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "upid.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 