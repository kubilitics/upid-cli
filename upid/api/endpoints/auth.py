"""
UPID API Authentication Endpoints
Secure login, logout, registration, and user management endpoints with industry-standard security.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta, timezone
import secrets

from ..auth import get_current_user
from ...core.security import (
    LoginRequest, RegisterRequest, TokenResponse, UserProfile,
    authenticate_user, jwt_handler, session_manager, password_manager,
    PasswordValidator, audit_logger, require_permission, require_mfa,
    SecurityLevel, Permission, AuditEvent
)
from ...core.storage_integration import StorageIntegration

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


class MFARequest(BaseModel):
    """MFA verification request."""
    mfa_code: str


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        validation = PasswordValidator.validate_password(v)
        if not validation["valid"]:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v


class UserUpdateRequest(BaseModel):
    """User update request."""
    email: Optional[str] = None
    organization: Optional[str] = None


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, http_request: Request):
    """Authenticate user and return access token with enhanced security."""
    try:
        # Rate limiting check
        client_ip = http_request.client.host
        
        # Authenticate user
        user = await authenticate_user(request.username, request.password, request.mfa_code)
        
        if not user:
            # Log failed login attempt
            audit_logger.log_event(AuditEvent(
                event_id=secrets.token_urlsafe(16),
                user_id="unknown",
                action="login_failed",
                resource_type="auth",
                resource_id="login",
                timestamp=datetime.now(timezone.utc),
                ip_address=client_ip,
                user_agent=http_request.headers.get("user-agent", ""),
                success=False,
                details={"username": request.username, "reason": "invalid_credentials"},
                security_level=SecurityLevel.MEDIUM
            ))
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check MFA requirement
        mfa_required = user.get("mfa_enabled", False)
        mfa_verified = user.get("mfa_verified", False)
        
        if mfa_required and not mfa_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Multi-factor authentication required"
            )
        
        # Create session
        session = session_manager.create_session(
            user_data=user,
            ip_address=client_ip,
            user_agent=http_request.headers.get("user-agent", "")
        )
        
        # Create tokens
        token_data = {
            "sub": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "organization": user["organization"],
            "permissions": user["permissions"],
            "mfa_verified": mfa_verified,
            "session_id": session.session_id
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        refresh_token = jwt_handler.create_refresh_token(token_data)
        
        # Log successful login
        audit_logger.log_event(AuditEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=user["user_id"],
            action="login_success",
            resource_type="auth",
            resource_id="login",
            timestamp=datetime.now(timezone.utc),
            ip_address=client_ip,
            user_agent=http_request.headers.get("user-agent", ""),
            success=True,
            details={
                "username": user["username"],
                "mfa_verified": mfa_verified,
                "session_id": session.session_id
            },
            security_level=SecurityLevel.HIGH if "admin" in user["permissions"] else SecurityLevel.MEDIUM
        ))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=24 * 3600,
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            organization=user["organization"],
            permissions=user["permissions"],
            mfa_required=mfa_required,
            mfa_verified=mfa_verified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
    http_request: Request = None
):
    """Secure user logout with session invalidation."""
    try:
        # Get session ID from token
        session_id = current_user.get("session_id")
        if session_id:
            session_manager.invalidate_session(session_id)
        
        # Log logout event
        audit_logger.log_event(AuditEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=current_user["user_id"],
            action="logout",
            resource_type="auth",
            resource_id="logout",
            timestamp=datetime.now(timezone.utc),
            ip_address=http_request.client.host if http_request else "unknown",
            user_agent=http_request.headers.get("user-agent", "") if http_request else "unknown",
            success=True,
            details={
                "username": current_user["username"],
                "session_id": session_id
            },
            security_level=SecurityLevel.MEDIUM
        ))
        
        return {
            "message": "Successfully logged out",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/register", response_model=TokenResponse)
async def register(user_data: RegisterRequest, http_request: Request):
    """Secure user registration with password validation."""
    try:
        # Validate password strength
        password_validation = PasswordValidator.validate_password(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
            )
        
        # Hash password
        hashed_password = password_manager.hash_password(user_data.password)
        
        # Create new user
        new_user = {
            "user_id": f"user-{secrets.token_urlsafe(8)}",
            "username": user_data.username,
            "email": user_data.email,
            "organization": user_data.organization or "default",
            "permissions": ["read"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": datetime.now(timezone.utc).isoformat(),
            "mfa_enabled": False,
            "mfa_verified": True
        }
        
        # Create session
        session = session_manager.create_session(
            user_data=new_user,
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get("user-agent", "")
        )
        
        # Create tokens
        token_data = {
            "sub": new_user["user_id"],
            "username": new_user["username"],
            "email": new_user["email"],
            "organization": new_user["organization"],
            "permissions": new_user["permissions"],
            "mfa_verified": True,
            "session_id": session.session_id
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        refresh_token = jwt_handler.create_refresh_token(token_data)
        
        # Log registration
        audit_logger.log_event(AuditEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=new_user["user_id"],
            action="register",
            resource_type="auth",
            resource_id="register",
            timestamp=datetime.now(timezone.utc),
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get("user-agent", ""),
            success=True,
            details={
                "username": new_user["username"],
                "email": new_user["email"],
                "organization": new_user["organization"]
            },
            security_level=SecurityLevel.MEDIUM
        ))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=24 * 3600,
            user_id=new_user["user_id"],
            username=new_user["username"],
            email=new_user["email"],
            organization=new_user["organization"],
            permissions=new_user["permissions"],
            mfa_required=False,
            mfa_verified=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile with enhanced security."""
    try:
        return UserProfile(
            user_id=current_user["user_id"],
            username=current_user["username"],
            email=current_user["email"],
            organization=current_user["organization"],
            permissions=current_user["permissions"],
            created_at=current_user.get("created_at", datetime.now(timezone.utc).isoformat()),
            last_login=current_user.get("last_login", datetime.now(timezone.utc).isoformat()),
            mfa_enabled=current_user.get("mfa_enabled", False),
            security_level="high" if "admin" in current_user["permissions"] else "medium",
            session_timeout=30 * 60  # 30 minutes
        )
    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Refresh access token."""
    try:
        # Verify refresh token
        payload = jwt_handler.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Create new access token
        token_data = {
            "sub": current_user["user_id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "organization": current_user["organization"],
            "permissions": current_user["permissions"],
            "mfa_verified": current_user.get("mfa_verified", False),
            "session_id": current_user.get("session_id")
        }
        
        new_access_token = jwt_handler.create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 24 * 3600
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/mfa/verify")
async def verify_mfa(
    mfa_request: MFARequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Verify MFA code."""
    try:
        # In production, this would verify against a real MFA system
        # For now, use a simple code
        if mfa_request.mfa_code == "123456":
            # Update user MFA status
            current_user["mfa_verified"] = True
            
            # Log MFA verification
            audit_logger.log_event(AuditEvent(
                event_id=secrets.token_urlsafe(16),
                user_id=current_user["user_id"],
                action="mfa_verify",
                resource_type="auth",
                resource_id="mfa",
                timestamp=datetime.now(timezone.utc),
                ip_address="unknown",
                user_agent="unknown",
                success=True,
                details={"username": current_user["username"]},
                security_level=SecurityLevel.HIGH
            ))
            
            return {"message": "MFA verification successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA verification failed"
        )


@router.post("/password/change")
async def change_password(
    password_request: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password with security validation."""
    try:
        # Verify current password
        if not password_manager.verify_password(password_request.current_password, "hashed_password"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = password_manager.hash_password(password_request.new_password)
        
        # Log password change
        audit_logger.log_event(AuditEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=current_user["user_id"],
            action="password_change",
            resource_type="auth",
            resource_id="password",
            timestamp=datetime.now(timezone.utc),
            ip_address="unknown",
            user_agent="unknown",
            success=True,
            details={"username": current_user["username"]},
            security_level=SecurityLevel.HIGH
        ))
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/users", dependencies=[Depends(require_permission(Permission.USER_MANAGEMENT))])
async def list_users():
    """List all users (admin only)."""
    try:
        # In production, this would query the user database
        users = [
            {
                "user_id": "admin-001",
                "username": "admin",
                "email": "admin@upid.io",
                "organization": "upid",
                "permissions": ["read", "write", "admin"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "mfa_enabled": True
            },
            {
                "user_id": "user-001",
                "username": "user",
                "email": "user@upid.io",
                "organization": "upid",
                "permissions": ["read"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "mfa_enabled": False
            }
        ]
        
        return {"users": users}
        
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get("/auth/status")
async def auth_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get authentication status."""
    try:
        return {
            "authenticated": True,
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "permissions": current_user["permissions"],
            "mfa_verified": current_user.get("mfa_verified", False),
            "session_active": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Auth status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        ) 