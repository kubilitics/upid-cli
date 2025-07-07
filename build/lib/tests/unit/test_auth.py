"""
Unit tests for authentication management
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from upid.core.auth import AuthManager
from upid.core.config import Config


class TestAuthManager:
    """Test authentication management"""

    @pytest.mark.unit
    def test_auth_manager_initialization(self, mock_config):
        """Test auth manager initialization"""
        auth_manager = AuthManager(mock_config)
        
        assert auth_manager.config == mock_config
        assert auth_manager._current_user is None

    @pytest.mark.unit
    def test_login_success(self, mock_config, mock_api_client):
        """Test successful login"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock successful login response
        mock_response = {
            'token': 'test_token_123',
            'user': {
                'email': 'test@example.com',
                'name': 'Test User',
                'organization': 'Test Corp'
            }
        }
        mock_api_client.login.return_value = mock_response
        
        # Test login
        token = auth_manager.login('test@example.com', 'password123')
        
        assert token == 'test_token_123'
        assert auth_manager._current_user == mock_response['user']
        mock_api_client.login.assert_called_once_with('test@example.com', 'password123')

    @pytest.mark.unit
    def test_login_with_server(self, mock_config, mock_api_client):
        """Test login with custom server"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        mock_response = {'token': 'test_token_123', 'user': {}}
        mock_api_client.login.return_value = mock_response
        
        # Test login with server
        auth_manager.login('test@example.com', 'password123', 'https://custom.upid.io')
        
        # Should update API URL
        assert mock_config.get('api_url') == 'https://custom.upid.io'

    @pytest.mark.unit
    def test_login_failure_no_token(self, mock_config, mock_api_client):
        """Test login failure when no token received"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock response without token
        mock_response = {'user': {'email': 'test@example.com'}}
        mock_api_client.login.return_value = mock_response
        
        # Test login failure
        with pytest.raises(Exception, match="No token received from server"):
            auth_manager.login('test@example.com', 'password123')

    @pytest.mark.unit
    def test_login_failure_api_error(self, mock_config, mock_api_client):
        """Test login failure due to API error"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock API error
        mock_api_client.login.side_effect = Exception("API Error")
        
        # Test login failure
        with pytest.raises(Exception, match="Login failed: API Error"):
            auth_manager.login('test@example.com', 'password123')

    @pytest.mark.unit
    def test_logout_success(self, mock_config, mock_api_client):
        """Test successful logout"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Set auth token
        auth_manager.config.set_auth_token('test_token_123')
        auth_manager._current_user = {'email': 'test@example.com'}
        
        # Test logout
        auth_manager.logout()
        
        # Should clear token and user
        assert auth_manager.config.get_auth_token() is None
        assert auth_manager._current_user is None
        mock_api_client.logout.assert_called_once()

    @pytest.mark.unit
    def test_logout_without_token(self, mock_config, mock_api_client):
        """Test logout when no token is set"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Test logout without token (should not fail)
        auth_manager.logout()
        
        # Should not call API logout
        mock_api_client.logout.assert_not_called()

    @pytest.mark.unit
    def test_logout_api_error(self, mock_config, mock_api_client):
        """Test logout with API error (should not fail)"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Set auth token
        auth_manager.config.set_auth_token('test_token_123')
        
        # Mock API error
        mock_api_client.logout.side_effect = Exception("API Error")
        
        # Test logout (should not fail)
        auth_manager.logout()
        
        # Should still clear token
        assert auth_manager.config.get_auth_token() is None

    @pytest.mark.unit
    def test_is_authenticated_with_token(self, mock_config):
        """Test authentication check with valid token"""
        auth_manager = AuthManager(mock_config)
        
        # Set token
        auth_manager.config.set_auth_token('test_token_123')
        
        # Mock successful user profile
        with patch.object(auth_manager, 'get_current_user') as mock_get_user:
            mock_get_user.return_value = {'email': 'test@example.com'}
            
            assert auth_manager.is_authenticated() is True

    @pytest.mark.unit
    def test_is_authenticated_without_token(self, mock_config):
        """Test authentication check without token"""
        auth_manager = AuthManager(mock_config)
        
        # No token set
        assert auth_manager.is_authenticated() is False

    @pytest.mark.unit
    def test_is_authenticated_invalid_token(self, mock_config):
        """Test authentication check with invalid token"""
        auth_manager = AuthManager(mock_config)
        
        # Set token
        auth_manager.config.set_auth_token('invalid_token')
        
        # Mock failed user profile
        with patch.object(auth_manager, 'get_current_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Invalid token")
            
            assert auth_manager.is_authenticated() is False
            # Should clear invalid token
            assert auth_manager.config.get_auth_token() is None

    @pytest.mark.unit
    def test_get_current_user_success(self, mock_config, mock_api_client, sample_user_data):
        """Test getting current user successfully"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock API response
        mock_api_client.get_profile.return_value = {'user': sample_user_data}
        
        # Test getting user
        user = auth_manager.get_current_user()
        
        assert user == sample_user_data
        mock_api_client.get_profile.assert_called_once()

    @pytest.mark.unit
    def test_get_current_user_cached(self, mock_config, sample_user_data):
        """Test getting current user from cache"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = sample_user_data
        
        # Should return cached user without API call
        user = auth_manager.get_current_user()
        
        assert user == sample_user_data

    @pytest.mark.unit
    def test_get_current_user_api_error(self, mock_config, mock_api_client):
        """Test getting current user with API error"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock API error
        mock_api_client.get_profile.side_effect = Exception("API Error")
        
        # Test API error
        with pytest.raises(Exception, match="Failed to get user profile: API Error"):
            auth_manager.get_current_user()

    @pytest.mark.unit
    def test_refresh_token_success(self, mock_config, mock_api_client):
        """Test successful token refresh"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock refresh response
        mock_response = {'token': 'new_token_456'}
        mock_api_client.refresh_token.return_value = mock_response
        
        # Test token refresh
        token = auth_manager.refresh_token()
        
        assert token == 'new_token_456'
        mock_api_client.refresh_token.assert_called_once()

    @pytest.mark.unit
    def test_refresh_token_failure(self, mock_config, mock_api_client):
        """Test token refresh failure"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock API error
        mock_api_client.refresh_token.side_effect = Exception("Refresh Error")
        
        # Test refresh failure
        with pytest.raises(Exception, match="Token refresh failed: Refresh Error"):
            auth_manager.refresh_token()

    @pytest.mark.unit
    def test_refresh_token_no_token(self, mock_config, mock_api_client):
        """Test token refresh when no token received"""
        auth_manager = AuthManager(mock_config)
        auth_manager.api_client = mock_api_client
        
        # Mock response without token
        mock_response = {'message': 'Refresh successful'}
        mock_api_client.refresh_token.return_value = mock_response
        
        # Test refresh failure
        with pytest.raises(Exception, match="No token received from refresh"):
            auth_manager.refresh_token()

    @pytest.mark.unit
    def test_get_token(self, mock_config):
        """Test getting current token"""
        auth_manager = AuthManager(mock_config)
        
        # Set token
        auth_manager.config.set_auth_token('test_token_123')
        
        assert auth_manager.get_token() == 'test_token_123'

    @pytest.mark.unit
    def test_validate_token_success(self, mock_config):
        """Test token validation success"""
        auth_manager = AuthManager(mock_config)
        
        # Mock successful user profile
        with patch.object(auth_manager, 'get_current_user') as mock_get_user:
            mock_get_user.return_value = {'email': 'test@example.com'}
            
            assert auth_manager.validate_token() is True

    @pytest.mark.unit
    def test_validate_token_failure(self, mock_config):
        """Test token validation failure"""
        auth_manager = AuthManager(mock_config)
        
        # Mock failed user profile
        with patch.object(auth_manager, 'get_current_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Invalid token")
            
            assert auth_manager.validate_token() is False

    @pytest.mark.unit
    def test_get_user_email(self, mock_config, sample_user_data):
        """Test getting user email"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = sample_user_data
        
        assert auth_manager.get_user_email() == 'test@example.com'

    @pytest.mark.unit
    def test_get_user_email_no_user(self, mock_config):
        """Test getting user email when no user"""
        auth_manager = AuthManager(mock_config)
        
        assert auth_manager.get_user_email() is None

    @pytest.mark.unit
    def test_get_user_organization(self, mock_config, sample_user_data):
        """Test getting user organization"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = sample_user_data
        
        assert auth_manager.get_user_organization() == 'Test Corp'

    @pytest.mark.unit
    def test_get_user_organization_no_user(self, mock_config):
        """Test getting user organization when no user"""
        auth_manager = AuthManager(mock_config)
        
        assert auth_manager.get_user_organization() is None

    @pytest.mark.unit
    def test_get_user_roles(self, mock_config, sample_user_data):
        """Test getting user roles"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = sample_user_data
        
        roles = auth_manager.get_user_roles()
        assert 'user' in roles
        assert 'admin' in roles

    @pytest.mark.unit
    def test_get_user_roles_no_user(self, mock_config):
        """Test getting user roles when no user"""
        auth_manager = AuthManager(mock_config)
        
        roles = auth_manager.get_user_roles()
        assert roles == []

    @pytest.mark.unit
    def test_has_role(self, mock_config, sample_user_data):
        """Test checking if user has specific role"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = sample_user_data
        
        assert auth_manager.has_role('admin') is True
        assert auth_manager.has_role('user') is True
        assert auth_manager.has_role('superuser') is False

    @pytest.mark.unit
    def test_has_permission(self, mock_config, sample_user_data):
        """Test checking if user has specific permission"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = sample_user_data
        
        assert auth_manager.has_permission('read') is True
        assert auth_manager.has_permission('write') is True
        assert auth_manager.has_permission('optimize') is True
        assert auth_manager.has_permission('delete') is False

    @pytest.mark.unit
    def test_has_permission_no_user(self, mock_config):
        """Test checking permissions when no user"""
        auth_manager = AuthManager(mock_config)
        
        assert auth_manager.has_permission('read') is False

    @pytest.mark.unit
    def test_has_permission_api_error(self, mock_config):
        """Test checking permissions with API error"""
        auth_manager = AuthManager(mock_config)
        auth_manager._current_user = {'email': 'test@example.com'}  # No permissions field
        
        assert auth_manager.has_permission('read') is False 