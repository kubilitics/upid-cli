"""
Unit tests for configuration management
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from upid.core.config import Config


class TestConfig:
    """Test configuration management"""

    @pytest.mark.unit
    def test_config_initialization(self, temp_config_dir):
        """Test config initialization with default values"""
        # Create a fresh config instance with a unique config file
        config = Config()
        config.config_file = Path(temp_config_dir) / 'test_config.json'
        
        # Test default values
        assert config.get('api_url') == 'https://api.upid.io'
        assert config.get('api_version') == 'v1'
        assert config.get('timeout') == 30
        assert config.get('verbose') is False
        assert config.get('output_format') == 'table'
        assert config.get('color_output') is True
        assert config.get('optimization_strategy') == 'balanced'
        assert config.get('safety_level') == 'strict'
        assert config.get('cost_model') == 'aws'
        assert config.get('currency') == 'USD'

    @pytest.mark.unit
    def test_config_set_and_get(self, mock_config):
        """Test setting and getting configuration values"""
        config = mock_config
        
        # Test setting values
        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'
        
        # Test getting with default
        assert config.get('non_existent', 'default') == 'default'

    @pytest.mark.unit
    def test_auth_token_management(self, mock_config):
        """Test authentication token management"""
        config = mock_config
        
        # Test setting auth token
        config.set_auth_token('test_token_123')
        assert config.get_auth_token() == 'test_token_123'
        assert config.is_authenticated() is True
        
        # Test clearing auth token
        config.clear_auth_token()
        assert config.get_auth_token() is None
        assert config.is_authenticated() is False

    @pytest.mark.unit
    def test_config_persistence(self, temp_config_dir):
        """Test config persistence to file"""
        config = Config()
        config.config_dir = Path(temp_config_dir)
        config.config_file = config.config_dir / 'config.json'
        
        # Set some values
        config.set('test_key', 'test_value')
        config.set('api_url', 'https://test.upid.io')
        
        # Create new config instance to test loading
        new_config = Config()
        new_config.config_dir = Path(temp_config_dir)
        new_config.config_file = new_config.config_dir / 'config.json'
        
        # Should load the saved values
        assert new_config.get('test_key') == 'test_value'
        assert new_config.get('api_url') == 'https://test.upid.io'

    @pytest.mark.unit
    def test_config_export_import(self, mock_config):
        """Test config export and import"""
        config = mock_config
        
        # Set some values
        config.set('export_test', 'export_value')
        config.set('api_url', 'https://export.upid.io')
        
        # Export config
        export_file = Path('/tmp/test_export.json')
        config.export_config(str(export_file))
        
        # Import config
        new_config = Config()
        new_config.import_config(str(export_file))
        
        # Check imported values
        assert new_config.get('export_test') == 'export_value'
        assert new_config.get('api_url') == 'https://export.upid.io'
        
        # Cleanup
        export_file.unlink(missing_ok=True)

    @pytest.mark.unit
    def test_config_reset(self, mock_config):
        """Test config reset to defaults"""
        config = mock_config
        
        # Set custom values
        config.set('api_url', 'https://custom.upid.io')
        config.set('test_key', 'test_value')
        config.set_auth_token('test_token')
        
        # Reset config
        config.reset_config()
        
        # Check defaults are restored
        assert config.get('api_url') == 'https://api.upid.io'
        assert config.get('test_key') is None
        assert config.get_auth_token() is None

    @pytest.mark.unit
    def test_cluster_management(self, mock_config):
        """Test cluster management methods"""
        config = mock_config
        
        # Test setting default cluster
        config.set_default_cluster('cluster-123')
        assert config.get_default_cluster() == 'cluster-123'
        
        # Test clearing default cluster
        config.set_default_cluster(None)
        assert config.get_default_cluster() is None

    @pytest.mark.unit
    def test_optimization_strategy(self, mock_config):
        """Test optimization strategy management"""
        config = mock_config
        
        # Test setting strategy
        config.set_optimization_strategy('cost-focused')
        assert config.get_optimization_strategy() == 'cost-focused'
        
        # Test default strategy
        config.reset_config()
        assert config.get_optimization_strategy() == 'balanced'

    @pytest.mark.unit
    def test_safety_level(self, mock_config):
        """Test safety level management"""
        config = mock_config
        
        # Test setting safety level
        config.set_safety_level('aggressive')
        assert config.get_safety_level() == 'aggressive'
        
        # Test default safety level
        config.reset_config()
        assert config.get_safety_level() == 'strict'

    @pytest.mark.unit
    def test_cost_model(self, mock_config):
        """Test cost model management"""
        config = mock_config
        
        # Test setting cost model
        config.set_cost_model('gcp')
        assert config.get_cost_model() == 'gcp'
        
        # Test default cost model
        config.reset_config()
        assert config.get_cost_model() == 'aws'

    @pytest.mark.unit
    def test_currency(self, mock_config):
        """Test currency management"""
        config = mock_config
        
        # Test setting currency
        config.set_currency('EUR')
        assert config.get_currency() == 'EUR'
        
        # Test default currency
        config.reset_config()
        assert config.get_currency() == 'USD'

    @pytest.mark.unit
    def test_verbose_mode(self, mock_config):
        """Test verbose mode management"""
        config = mock_config
        
        # Test setting verbose mode
        config.set_verbose(True)
        assert config.is_verbose() is True
        
        # Test default verbose mode
        config.reset_config()
        assert config.is_verbose() is False

    @pytest.mark.unit
    def test_output_format(self, mock_config):
        """Test output format management"""
        config = mock_config
        
        # Test setting output format
        config.set_output_format('json')
        assert config.get_output_format() == 'json'
        
        # Test default output format
        config.reset_config()
        assert config.get_output_format() == 'table'

    @pytest.mark.unit
    def test_color_output(self, mock_config):
        """Test color output management"""
        config = mock_config
        
        # Test setting color output
        config.set_color_output(False)
        assert config.is_color_output() is False
        
        # Test default color output
        config.reset_config()
        assert config.is_color_output() is True

    @pytest.mark.unit
    def test_timeout(self, mock_config):
        """Test timeout management"""
        config = mock_config
        
        # Test setting timeout
        config.set_timeout(60)
        assert config.get_timeout() == 60
        
        # Test default timeout
        config.reset_config()
        assert config.get_timeout() == 30

    @pytest.mark.unit
    def test_notification_channels(self, mock_config):
        """Test notification channels management"""
        config = mock_config
        
        # Test adding channels
        config.add_notification_channel('slack')
        config.add_notification_channel('email')
        channels = config.get_notification_channels()
        assert 'slack' in channels
        assert 'email' in channels
        
        # Test removing channels
        config.remove_notification_channel('slack')
        channels = config.get_notification_channels()
        assert 'slack' not in channels
        assert 'email' in channels

    @pytest.mark.unit
    def test_config_file_io_error_handling(self, temp_config_dir):
        """Test config file I/O error handling"""
        config = Config()
        config.config_dir = Path(temp_config_dir)
        config.config_file = config.config_dir / 'config.json'
        
        # Test with invalid JSON in config file
        with open(config.config_file, 'w') as f:
            f.write('invalid json content')
        
        # Should handle gracefully and use defaults
        new_config = Config()
        new_config.config_dir = Path(temp_config_dir)
        new_config.config_file = new_config.config_dir / 'config.json'
        
        assert new_config.get('api_url') == 'https://api.upid.io'  # Default value

    @pytest.mark.unit
    def test_auth_file_io_error_handling(self, temp_config_dir):
        """Test auth file I/O error handling"""
        config = Config()
        config.config_dir = Path(temp_config_dir)
        config.auth_file = config.config_dir / 'auth.json'
        
        # Test with invalid JSON in auth file
        with open(config.auth_file, 'w') as f:
            f.write('invalid json content')
        
        # Should handle gracefully and return None
        assert config.get_auth_token() is None
        assert config.is_authenticated() is False

    @pytest.mark.unit
    def test_config_directory_creation(self, temp_config_dir):
        """Test config directory creation"""
        # Remove directory if it exists
        import shutil
        if Path(temp_config_dir).exists():
            shutil.rmtree(temp_config_dir)
        
        # Create config - should create directory
        config = Config()
        config.config_dir = Path(temp_config_dir)
        config.config_file = config.config_dir / 'config.json'
        
        # Set a value to trigger file creation
        config.set('test_key', 'test_value')
        
        # Check directory and file were created
        assert config.config_dir.exists()
        assert config.config_file.exists()

    @pytest.mark.unit
    def test_config_validation(self, mock_config):
        """Test config value validation"""
        config = mock_config
        
        # Test valid values
        config.set('optimization_strategy', 'balanced')
        config.set('safety_level', 'strict')
        config.set('cost_model', 'aws')
        config.set('currency', 'USD')
        
        # Test invalid values (should still work but log warnings)
        config.set('optimization_strategy', 'invalid_strategy')
        config.set('safety_level', 'invalid_level')
        config.set('cost_model', 'invalid_model')
        config.set('currency', 'INVALID')
        
        # Values should still be set
        assert config.get('optimization_strategy') == 'invalid_strategy'
        assert config.get('safety_level') == 'invalid_level'
        assert config.get('cost_model') == 'invalid_model'
        assert config.get('currency') == 'INVALID' 