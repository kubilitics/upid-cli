"""
UPID API Authentication Module
JWT token management, user authentication, and dependency injection.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
import logging
from datetime import datetime, timedelta

from ..core.config import Config
from ..core.auth import AuthManager
from ..core.storage_integration import StorageIntegration

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = "your-secret-key"  # Configure for production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request model."""
    username: str
    email: str
    password: str
    organization: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    username: str


class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    username: str
    email: str
    organization: Optional[str]
    permissions: list
    created_at: str
    last_login: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except (jwt.InvalidTokenError, jwt.DecodeError, jwt.InvalidSignatureError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )
    
    # Get user from storage
    try:
        with StorageIntegration() as storage:
            # For now, return basic user info
            # In production, this would query the user database
            return {
                "user_id": user_id,
                "username": payload.get("username", "unknown"),
                "permissions": payload.get("permissions", []),
                "organization": payload.get("organization", "default")
            }
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password."""
    try:
        # In production, this would validate against a user database
        # For now, use a simple authentication scheme
        if username == "admin" and password == "password":
            return {
                "user_id": "admin-001",
                "username": "admin",
                "email": "admin@upid.io",
                "organization": "upid",
                "permissions": ["read", "write", "admin"],
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
        elif username == "user" and password == "password":
            return {
                "user_id": "user-001",
                "username": "user",
                "email": "user@upid.io",
                "organization": "upid",
                "permissions": ["read"],
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def permission_checker(current_user = Depends(get_current_user)):
        # Support both dict and User model
        perms = None
        if hasattr(current_user, 'permissions'):
            perms = current_user.permissions
        elif isinstance(current_user, dict):
            perms = current_user.get("permissions", [])
        else:
            perms = []
        if permission not in perms:
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker


def require_admin():
    """Decorator to require admin permission."""
    return require_permission("admin") 