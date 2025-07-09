"""
UPID API Package
FastAPI backend for UPID CLI with authentication, intelligence, and optimization endpoints.
"""

__version__ = "1.0.0"
__author__ = "UPID Team"
__description__ = "Universal Pod Intelligence Director API"

from .main import app
from .auth import (
    get_current_user, authenticate_user, create_access_token,
    verify_token, require_permission, require_admin
)

__all__ = [
    "app",
    "get_current_user",
    "authenticate_user", 
    "create_access_token",
    "verify_token",
    "require_permission",
    "require_admin"
] 