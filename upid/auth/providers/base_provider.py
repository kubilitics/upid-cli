"""
Base Authentication Provider Interface
All authentication providers must implement this strict interface
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..enterprise_auth import UserPrincipal, AuthLevel

logger = logging.getLogger(__name__)


class AuthProvider(ABC):
    """
    Strict interface for all authentication providers
    Following enterprise security standards and zero-trust principles
    """
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserPrincipal]:
        """
        Authenticate user with provided credentials
        
        Args:
            credentials: Authentication credentials (provider-specific)
            
        Returns:
            UserPrincipal: Authenticated user principal or None if failed
            
        Raises:
            AuthProviderError: For provider-specific errors
        """
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[UserPrincipal]:
        """
        Validate authentication token
        
        Args:
            token: Authentication token to validate
            
        Returns:
            UserPrincipal: User principal if token is valid, None otherwise
            
        Raises:
            AuthProviderError: For provider-specific errors
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh authentication token
        
        Args:
            token: Current authentication token
            
        Returns:
            str: New authentication token or None if refresh failed
            
        Raises:
            AuthProviderError: For provider-specific errors
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get provider metadata and capabilities
        
        Returns:
            Dict containing provider information:
            - name: Provider name
            - type: Provider type
            - version: Provider version
            - capabilities: List of supported features
            - config_schema: Configuration schema
            - health_endpoint: Health check endpoint
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check provider health and connectivity
        
        Returns:
            Dict containing health status:
            - status: "healthy", "degraded", or "unhealthy"
            - response_time: Response time in milliseconds
            - error: Error message if unhealthy
            - timestamp: Health check timestamp
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test provider connectivity
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate provider configuration
        
        Args:
            config: Provider configuration to validate
            
        Returns:
            bool: True if configuration is valid
        """
        try:
            required_fields = self.get_metadata().get("config_schema", {}).get("required", [])
            for field in required_fields:
                if field not in config:
                    logger.error(f"Missing required config field: {field}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed user information from provider
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict: User information or None if not found
        """
        # Default implementation - override in specific providers
        return None
    
    async def list_users(self, filter_criteria: Dict[str, Any] = None) -> list:
        """
        List users from provider (if supported)
        
        Args:
            filter_criteria: Optional filter criteria
            
        Returns:
            List: User information list
        """
        # Default implementation - override in specific providers
        return []
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """
        Create user in provider (if supported)
        
        Args:
            user_data: User data to create
            
        Returns:
            str: User ID if successful, None otherwise
        """
        # Default implementation - override in specific providers
        return None
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Update user in provider (if supported)
        
        Args:
            user_id: User identifier
            user_data: Updated user data
            
        Returns:
            bool: True if successful
        """
        # Default implementation - override in specific providers
        return False
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user from provider (if supported)
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if successful
        """
        # Default implementation - override in specific providers
        return False
    
    def get_supported_features(self) -> list:
        """
        Get list of supported features
        
        Returns:
            List of supported features:
            - "user_management": User CRUD operations
            - "group_management": Group CRUD operations
            - "role_management": Role CRUD operations
            - "mfa": Multi-factor authentication
            - "sso": Single sign-on
            - "audit_logs": Audit logging
            - "real_time_sync": Real-time synchronization
        """
        return []
    
    def get_security_features(self) -> list:
        """
        Get list of security features
        
        Returns:
            List of security features:
            - "password_policy": Password policy enforcement
            - "account_lockout": Account lockout protection
            - "session_timeout": Session timeout management
            - "ip_whitelist": IP address whitelisting
            - "device_trust": Device trust management
            - "risk_based_auth": Risk-based authentication
        """
        return []


class AuthProviderError(Exception):
    """Base exception for authentication provider errors"""
    
    def __init__(self, message: str, provider: str = None, error_code: str = None):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(AuthProviderError):
    """Exception raised for authentication failures"""
    pass


class TokenValidationError(AuthProviderError):
    """Exception raised for token validation failures"""
    pass


class ConfigurationError(AuthProviderError):
    """Exception raised for configuration errors"""
    pass


class ConnectionError(AuthProviderError):
    """Exception raised for connection failures"""
    pass 