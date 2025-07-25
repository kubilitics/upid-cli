"""
UPID CLI API Server - Authentication Router
Enterprise authentication endpoints with JWT token management
"""

import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api_server.models.requests import LoginRequest, TokenRefreshRequest
from api_server.models.responses import TokenResponse, UserInfoResponse, BaseResponse, ResponseStatus
from api_server.core.auth import create_access_token, verify_token
from api_server.core.config import get_settings
from api_server.database.connection import get_db
from api_server.services.user_service import UserService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens
    
    This endpoint validates user credentials and returns both access and refresh tokens.
    The access token is used for authenticated API requests, while the refresh token
    can be used to obtain new access tokens without re-authentication.
    """
    try:
        # Authenticate user using database service
        user_service = UserService(db)
        user = await user_service.authenticate_user(login_request.username, login_request.password)
        
        if not user:
            logger.warning(f"🚫 Login attempt failed for username: {login_request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": str(user.id), "type": "access"},
            expires_delta=access_token_expires
        )
        
        # Create refresh token (longer expiration)
        refresh_token_expires = timedelta(days=7)  # 7 days
        refresh_token = create_access_token(
            data={"sub": user.username, "user_id": str(user.id), "type": "refresh"},
            expires_delta=refresh_token_expires
        )
        
        # Get user permissions
        permissions = await user_service.get_user_permissions(str(user.id))
        
        logger.info(f"✅ User logged in successfully: {user.username}")
        
        return TokenResponse(
            status=ResponseStatus.SUCCESS,
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user_info={
                "username": user.username,
                "email": user.email,
                "roles": permissions,
                "is_superuser": user.is_superuser
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: TokenRefreshRequest):
    """
    Refresh access token using refresh token
    
    This endpoint allows clients to obtain a new access token using a valid refresh token,
    enabling long-term authentication without requiring users to re-enter credentials.
    """
    try:
        # Verify refresh token
        payload = await verify_token(refresh_request.refresh_token)
        
        # Verify this is actually a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        new_access_token = create_access_token(
            data={"sub": username, "type": "access"},
            expires_delta=access_token_expires
        )
        
        # Get user info for response
        permissions = await get_user_permissions(username)
        
        logger.info(f"✅ Token refreshed for user: {username}")
        
        return TokenResponse(
            status=ResponseStatus.SUCCESS,
            message="Token refreshed successfully",
            access_token=new_access_token,
            refresh_token=refresh_request.refresh_token,  # Keep same refresh token
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user_info={
                "username": username,
                "roles": permissions
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    
    Returns detailed information about the currently authenticated user,
    including permissions, roles, and preferences.
    """
    try:
        # Verify token and get user info
        payload = await verify_token(credentials.credentials)
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Get user permissions
        permissions = await user_service.get_user_permissions(user_id)
        
        # Convert user to dict
        user_info = user_service.to_user_dict(user, include_sensitive=True)
        
        return UserInfoResponse(
            status=ResponseStatus.SUCCESS,
            message="User information retrieved successfully",
            user=user_info,
            permissions=permissions,
            preferences=user.preferences or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve user information"
        )


@router.post("/logout", response_model=BaseResponse)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate token
    
    In a production system, this would add the token to a blacklist.
    For now, it simply confirms the logout action.
    """
    try:
        # Verify token (to ensure it's valid before logout)
        payload = await verify_token(credentials.credentials)
        username = payload.get("sub")
        
        # In production, add token to blacklist here
        logger.info(f"✅ User logged out: {username}")
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="Logout successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )


@router.get("/validate", response_model=BaseResponse)
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate authentication token
    
    This endpoint can be used by clients to verify if their token is still valid
    without making a full API request.
    """
    try:
        payload = await verify_token(credentials.credentials)
        username = payload.get("sub")
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Token is valid for user: {username}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed"
        )