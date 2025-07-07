"""
Authentication management for UPID CLI
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class AuthManager:
    """Authentication manager for UPID CLI"""
    
    def __init__(self, config_or_auth_file: Optional[object] = None):
        # Accept either a Config object or a string path
        if config_or_auth_file is None:
            self.config = None
            self.auth_file = os.path.expanduser("~/.upid/auth.json")
        elif hasattr(config_or_auth_file, 'auth_file'):
            self.config = config_or_auth_file
            self.auth_file = str(self.config.auth_file)
        elif isinstance(config_or_auth_file, str):
            self.config = None
            self.auth_file = config_or_auth_file
        else:
            raise TypeError("AuthManager expects a Config object or a path string")
        self.auth_dir = Path(self.auth_file).parent
        self.auth_data = self._load_auth()
        self._current_user = None
        self.api_client = None
    
    def _load_auth(self) -> Dict[str, Any]:
        """Load authentication data"""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load auth: {e}")
                return {}
        return {}
    
    def _save_auth(self) -> None:
        """Save authentication data"""
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.auth_file, 'w') as f:
                json.dump(self.auth_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save auth: {e}")
    
    def set_token(self, token: str) -> None:
        """Set authentication token"""
        if self.config:
            self.config.set_auth_token(token)
        else:
            self.auth_data['token'] = token
            self._save_auth()
    
    def clear_token(self) -> None:
        """Clear authentication token"""
        if self.config:
            self.config.clear_auth_token()
        else:
            self.auth_data.pop('token', None)
            self._save_auth()
        self._current_user = None
    
    def get_token(self) -> Optional[str]:
        """Get current authentication token"""
        if self.config:
            return self.config.get_auth_token()
        return self.auth_data.get('token')
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        token = self.get_token()
        if not token:
            return False
        try:
            # Always try to get current user if token is set
            user = self.get_current_user()
            if user is not None:
                return True
            else:
                self.clear_token()
                if self.config:
                    self.config.save_config()
                return False
        except Exception:
            self.clear_token()
            if self.config:
                self.config.save_config()
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        token = self.get_token()
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        return {}
    
    def login(self, email, password, api_url=None):
        if not self.api_client:
            raise Exception("No API client available for login")
        try:
            if api_url and self.config:
                self.config.set('api_url', api_url)
            response = self.api_client.login(email, password)
            token = response.get('token') if isinstance(response, dict) else None
            user = response.get('user') if isinstance(response, dict) else None
            if not token:
                raise Exception("No token received from server")
            self.set_token(token)
            self._current_user = user
            return token
        except Exception as e:
            raise Exception(f"Login failed: {e}")

    def logout(self):
        token = self.get_token()
        if self.api_client and token:
            try:
                self.api_client.logout()
            except Exception:
                pass  # Ignore API errors on logout
        self.clear_token()
    
    def get_current_user(self):
        if self._current_user is not None:
            return self._current_user
        if self.api_client:
            try:
                profile = self.api_client.get_profile()
                user = profile.get('user') if isinstance(profile, dict) else None
                self._current_user = user
                return user
            except Exception as e:
                raise Exception(f"Failed to get user profile: {e}")
        raise Exception("No API client available for user profile")

    def get_user_email(self):
        user = self._current_user
        if user and 'email' in user:
            return user['email']
        return None

    def get_user_organization(self):
        user = self._current_user
        if user and 'organization' in user:
            return user['organization']
        return None

    def get_user_roles(self):
        user = self._current_user
        if user and 'roles' in user:
            return user['roles']
        return []

    def has_role(self, role):
        roles = self.get_user_roles()
        return role in roles

    def has_permission(self, permission):
        user = self._current_user
        if user and 'permissions' in user:
            return permission in user['permissions']
        return False

    def validate_token(self):
        try:
            user = self.get_current_user()
            return user is not None
        except Exception:
            return False

    def refresh_token(self):
        if self.api_client:
            try:
                response = self.api_client.refresh_token()
                token = response.get('token') if isinstance(response, dict) else None
                if not token:
                    raise Exception("No token received from refresh")
                self.set_token(token)
                return token
            except Exception as e:
                raise Exception(f"Token refresh failed: {e}")
        raise Exception("No API client available for token refresh")
