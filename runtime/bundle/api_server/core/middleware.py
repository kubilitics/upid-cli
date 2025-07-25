"""
UPID CLI API Server Middleware
Enterprise-grade middleware for logging, monitoring, and performance tracking
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

logger = logging.getLogger(__name__)


async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    """Add processing time header to all responses"""
    start_time = time.time()
    
    # Generate request ID for tracing
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Log incoming request
    logger.info(
        f"🔄 Request [{request_id}]: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Log response
    logger.info(
        f"✅ Response [{request_id}]: {response.status_code} "
        f"({process_time:.3f}s)"
    )
    
    return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls_per_minute: int = 100):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.client_requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        self.client_requests = {
            ip: requests for ip, requests in self.client_requests.items()
            if any(req_time > current_time - 60 for req_time in requests)
        }
        
        # Get client request history
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        
        # Filter requests from last minute
        recent_requests = [
            req_time for req_time in self.client_requests[client_ip]
            if req_time > current_time - 60
        ]
        
        # Check rate limit
        if len(recent_requests) >= self.calls_per_minute:
            logger.warning(f"🚫 Rate limit exceeded for {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        recent_requests.append(current_time)
        self.client_requests[client_ip] = recent_requests
        
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Detailed request/response logging middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request details
        logger.debug(f"📥 Request: {request.method} {request.url}")
        logger.debug(f"📥 Headers: {dict(request.headers)}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log response details
        logger.debug(f"📤 Response: {response.status_code} ({process_time:.3f}s)")
        logger.debug(f"📤 Headers: {dict(response.headers)}")
        
        return response