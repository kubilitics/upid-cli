"""
UPID CLI API Server Authentication
Enterprise-grade authentication and authorization system
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from passlib.context import CryptContext
from api_server.core.config import get_settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get settings
settings = get_settings()


class AuthManager:
    """Enterprise authentication manager"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✅ Access token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.debug(f"✅ Token verified for user: {username}")
            return payload
            
        except jwt.PyJWTError as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )


# Global auth manager instance
auth_manager = AuthManager()


# Convenience functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token using global auth manager"""
    return auth_manager.create_access_token(data, expires_delta)


async def verify_token(token: str) -> Dict[str, Any]:
    """Verify token using global auth manager"""
    return auth_manager.verify_token(token)


def hash_password(password: str) -> str:
    """Hash password using global auth manager"""
    return auth_manager.get_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using global auth manager"""
    return auth_manager.verify_password(plain_password, hashed_password)


# Default users for development (remove in production)
DEFAULT_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@upid.io",
        "hashed_password": hash_password("admin123"),
        "is_active": True,
        "is_superuser": True,
        "roles": ["admin", "user"]
    },
    "demo": {
        "username": "demo", 
        "email": "demo@upid.io",
        "hashed_password": hash_password("demo123"),
        "is_active": True,
        "is_superuser": False,
        "roles": ["user"]
    }
}


async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username/password"""
    try:
        # In production, this would query the database
        user = DEFAULT_USERS.get(username)
        
        if not user:
            logger.warning(f"🚫 Authentication failed: user '{username}' not found")
            return None
        
        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"🚫 Authentication failed: invalid password for user '{username}'")
            return None
        
        if not user.get("is_active", False):
            logger.warning(f"🚫 Authentication failed: user '{username}' is inactive")
            return None
        
        logger.info(f"✅ User authenticated successfully: {username}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


async def get_user_permissions(username: str) -> list:
    """Get user permissions/roles"""
    user = DEFAULT_USERS.get(username, {})
    return user.get("roles", [])


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would implement actual permission checking
            return await func(*args, **kwargs)
        return wrapper
    return decorator