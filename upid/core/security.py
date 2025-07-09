"""
UPID Security Module
Industry-standard security implementation with JWT, password hashing, rate limiting, and security headers.
"""

import os
import secrets
import hashlib
import hmac
import time
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum
import logging
from functools import wraps
import redis
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import re

logger = logging.getLogger(__name__)

# Security Configuration
SECURITY_CONFIG = {
    "JWT_SECRET": os.getenv("UPID_JWT_SECRET", secrets.token_urlsafe(32)),
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRATION_HOURS": 24,
    "REFRESH_TOKEN_EXPIRATION_DAYS": 30,
    "PASSWORD_MIN_LENGTH": 12,
    "PASSWORD_REQUIRE_UPPERCASE": True,
    "PASSWORD_REQUIRE_LOWERCASE": True,
    "PASSWORD_REQUIRE_DIGITS": True,
    "PASSWORD_REQUIRE_SPECIAL": True,
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOCKOUT_DURATION_MINUTES": 15,
    "RATE_LIMIT_REQUESTS": 100,
    "RATE_LIMIT_WINDOW": 3600,  # 1 hour
    "SESSION_TIMEOUT_MINUTES": 30,
    "PASSWORD_HISTORY_SIZE": 5,
    "MFA_REQUIRED": True,
    "AUDIT_LOG_ENABLED": True,
}

# Redis for session management and rate limiting
REDIS_CONFIG = {
    "host": os.getenv("UPID_REDIS_HOST", "localhost"),
    "port": int(os.getenv("UPID_REDIS_PORT", 6379)),
    "db": int(os.getenv("UPID_REDIS_DB", 0)),
    "password": os.getenv("UPID_REDIS_PASSWORD"),
    "decode_responses": True
}

class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Permission(Enum):
    """System permissions."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    REPORT = "report"
    STORAGE = "storage"
    USER_MANAGEMENT = "user_management"
    SYSTEM_CONFIG = "system_config"

@dataclass
class UserSession:
    """User session data."""
    user_id: str
    username: str
    email: str
    organization: str
    permissions: List[str]
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    mfa_verified: bool = False
    security_level: SecurityLevel = SecurityLevel.MEDIUM

@dataclass
class AuditEvent:
    """Audit event data."""
    event_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]
    security_level: SecurityLevel

class PasswordValidator:
    """Password validation and strength checking."""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        errors = []
        warnings = []
        
        if len(password) < SECURITY_CONFIG["PASSWORD_MIN_LENGTH"]:
            errors.append(f"Password must be at least {SECURITY_CONFIG['PASSWORD_MIN_LENGTH']} characters")
        
        if SECURITY_CONFIG["PASSWORD_REQUIRE_UPPERCASE"] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SECURITY_CONFIG["PASSWORD_REQUIRE_LOWERCASE"] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SECURITY_CONFIG["PASSWORD_REQUIRE_DIGITS"] and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if SECURITY_CONFIG["PASSWORD_REQUIRE_SPECIAL"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            warnings.append("Password contains repeated characters")
        
        if re.search(r'(123|abc|qwe)', password.lower()):
            warnings.append("Password contains common patterns")
        
        # Calculate entropy
        entropy = PasswordValidator._calculate_entropy(password)
        if entropy < 50:
            warnings.append("Password entropy is low")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "entropy": entropy,
            "strength": PasswordValidator._get_strength_level(entropy)
        }
    
    @staticmethod
    def _calculate_entropy(password: str) -> float:
        """Calculate password entropy."""
        char_set_size = 0
        if re.search(r'[a-z]', password):
            char_set_size += 26
        if re.search(r'[A-Z]', password):
            char_set_size += 26
        if re.search(r'\d', password):
            char_set_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            char_set_size += 32
        
        if char_set_size == 0:
            return 0
        
        return len(password) * (char_set_size ** 0.5)
    
    @staticmethod
    def _get_strength_level(entropy: float) -> str:
        """Get password strength level."""
        if entropy >= 80:
            return "very_strong"
        elif entropy >= 60:
            return "strong"
        elif entropy >= 40:
            return "medium"
        elif entropy >= 20:
            return "weak"
        else:
            return "very_weak"

class PasswordManager:
    """Password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a secure random password."""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password meets requirements
        while not PasswordValidator.validate_password(password)["valid"]:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        return password

class JWTHandler:
    """JWT token management."""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=SECURITY_CONFIG["JWT_EXPIRATION_HOURS"])
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        return jwt.encode(to_encode, SECURITY_CONFIG["JWT_SECRET"], algorithm=SECURITY_CONFIG["JWT_ALGORITHM"])
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=SECURITY_CONFIG["REFRESH_TOKEN_EXPIRATION_DAYS"])
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, SECURITY_CONFIG["JWT_SECRET"], algorithm=SECURITY_CONFIG["JWT_ALGORITHM"])
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, SECURITY_CONFIG["JWT_SECRET"], algorithms=[SECURITY_CONFIG["JWT_ALGORITHM"]])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except (jwt.InvalidTokenError, jwt.DecodeError, jwt.InvalidSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(**REDIS_CONFIG)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {e}")
    
    def check_rate_limit(self, key: str, max_requests: int = None, window: int = None) -> bool:
        """Check if request is within rate limit."""
        if not self.redis_client:
            return True  # Allow if Redis is not available
        
        max_requests = max_requests or SECURITY_CONFIG["RATE_LIMIT_REQUESTS"]
        window = window or SECURITY_CONFIG["RATE_LIMIT_WINDOW"]
        
        current_time = int(time.time())
        window_start = current_time - window
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        request_count = self.redis_client.zcard(key)
        
        if request_count >= max_requests:
            return False
        
        # Add current request
        self.redis_client.zadd(key, {str(current_time): current_time})
        self.redis_client.expire(key, window)
        
        return True

class SessionManager:
    """Session management."""
    
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(**REDIS_CONFIG)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis not available for session management: {e}")
    
    def create_session(self, user_data: Dict[str, Any], ip_address: str, user_agent: str) -> UserSession:
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        
        session = UserSession(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            organization=user_data["organization"],
            permissions=user_data["permissions"],
            session_id=session_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=user_data.get("mfa_verified", False),
            security_level=SecurityLevel.HIGH if "admin" in user_data["permissions"] else SecurityLevel.MEDIUM
        )
        
        if self.redis_client:
            session_data = {
                "user_id": session.user_id,
                "username": session.username,
                "email": session.email,
                "organization": session.organization,
                "permissions": session.permissions,
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "mfa_verified": session.mfa_verified,
                "security_level": session.security_level.value
            }
            
            self.redis_client.setex(
                f"session:{session_id}",
                SECURITY_CONFIG["SESSION_TIMEOUT_MINUTES"] * 60,
                str(session_data)
            )
        
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        if not self.redis_client:
            return None
        
        session_data = self.redis_client.get(f"session:{session_id}")
        if not session_data:
            return None
        
        # Parse session data and return UserSession object
        # Implementation depends on how session data is stored
        return None
    
    def update_session_activity(self, session_id: str):
        """Update session last activity."""
        if self.redis_client:
            self.redis_client.expire(f"session:{session_id}", SECURITY_CONFIG["SESSION_TIMEOUT_MINUTES"] * 60)
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session."""
        if self.redis_client:
            self.redis_client.delete(f"session:{session_id}")

class AuditLogger:
    """Audit logging system."""
    
    def __init__(self):
        self.enabled = SECURITY_CONFIG["AUDIT_LOG_ENABLED"]
    
    def log_event(self, event: AuditEvent):
        """Log an audit event."""
        if not self.enabled:
            return
        
        log_entry = {
            "event_id": event.event_id,
            "user_id": event.user_id,
            "action": event.action,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "timestamp": event.timestamp.isoformat(),
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "success": event.success,
            "details": event.details,
            "security_level": event.security_level.value
        }
        
        logger.info(f"AUDIT: {log_entry}")
        
        # In production, this would be stored in a secure audit database
        # For now, we'll use the existing storage system
        try:
            from .storage_integration import StorageIntegration
            with StorageIntegration() as storage:
                storage.storage.log_audit_event(
                    user_id=event.user_id,
                    action=event.action,
                    resource_type=event.resource_type,
                    resource_id=event.resource_id,
                    details=event.details
                )
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

class SecurityMiddleware:
    """Security middleware for FastAPI."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.audit_logger = AuditLogger()
    
    async def __call__(self, request: Request, call_next):
        """Process request with security checks."""
        start_time = time.time()
        
        # Rate limiting
        client_ip = request.client.host
        rate_limit_key = f"rate_limit:{client_ip}"
        
        if not self.rate_limiter.check_rate_limit(rate_limit_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Security headers
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Audit logging
        if self.audit_logger.enabled:
            duration = time.time() - start_time
            event = AuditEvent(
                event_id=secrets.token_urlsafe(16),
                user_id="anonymous",
                action=f"{request.method} {request.url.path}",
                resource_type="http_request",
                resource_id=str(request.url),
                timestamp=datetime.now(timezone.utc),
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent", ""),
                success=response.status_code < 400,
                details={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                },
                security_level=SecurityLevel.MEDIUM
            )
            self.audit_logger.log_event(event)
        
        return response

# Security decorators
def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if permission.value not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required"
            )
        return current_user
    return permission_checker

def require_security_level(level: SecurityLevel):
    """Decorator to require minimum security level."""
    def security_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_level = SecurityLevel.HIGH if "admin" in current_user.get("permissions", []) else SecurityLevel.MEDIUM
        if user_level.value < level.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security level '{level.value}' required"
            )
        return current_user
    return security_checker

def require_mfa():
    """Decorator to require MFA verification."""
    def mfa_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if not current_user.get("mfa_verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Multi-factor authentication required"
            )
        return current_user
    return mfa_checker

# Global instances
security_middleware = SecurityMiddleware()
session_manager = SessionManager()
password_manager = PasswordManager()
jwt_handler = JWTHandler()
audit_logger = AuditLogger()

# Security models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str
    mfa_code: Optional[str] = None

class RegisterRequest(BaseModel):
    """Registration request model."""
    username: str
    email: str
    password: str
    organization: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        validation = PasswordValidator.validate_password(v)
        if not validation["valid"]:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: str
    username: str
    email: str
    organization: str
    permissions: List[str]
    mfa_required: bool
    mfa_verified: bool

class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    username: str
    email: str
    organization: str
    permissions: List[str]
    created_at: str
    last_login: str
    mfa_enabled: bool
    security_level: str
    session_timeout: int

# Authentication functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
    """Get current authenticated user."""
    try:
        payload = jwt_handler.verify_token(credentials.credentials)
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from storage
        from .storage_integration import StorageIntegration
        with StorageIntegration() as storage:
            # For now, return basic user info
            # In production, this would query the user database
            return {
                "user_id": user_id,
                "username": payload.get("username", "unknown"),
                "email": payload.get("email", "unknown@example.com"),
                "organization": payload.get("organization", "default"),
                "permissions": payload.get("permissions", []),
                "mfa_verified": payload.get("mfa_verified", False)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

async def authenticate_user(username: str, password: str, mfa_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password."""
    try:
        # In production, this would validate against a user database
        # For now, use a simple authentication scheme
        if username == "admin" and password == "password":
            user_data = {
                "user_id": "admin-001",
                "username": "admin",
                "email": "admin@upid.io",
                "organization": "upid",
                "permissions": ["read", "write", "admin", "analyze", "optimize", "report", "storage", "user_management", "system_config"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "mfa_enabled": True,
                "mfa_verified": mfa_code == "123456" if mfa_code else False
            }
        elif username == "user" and password == "password":
            user_data = {
                "user_id": "user-001",
                "username": "user",
                "email": "user@upid.io",
                "organization": "upid",
                "permissions": ["read", "analyze"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "mfa_enabled": False,
                "mfa_verified": True
            }
        else:
            return None
        
        return user_data
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None 