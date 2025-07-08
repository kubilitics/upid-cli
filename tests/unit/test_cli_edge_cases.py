"""
CLI Edge Case Tests for UPID CLI
Tests for command-line interface edge cases and error handling
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
# Import the actual CLI module
import upid.cli
from upid.core.config import Config
from upid.core.auth import AuthManager


class TestCLIEdgeCases:
    """Test CLI edge cases and error handling"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration"""
        config = Config()
        config.set('api_url', 'https://api.upid.io')
        config.set('timeout', 30)
        return config

    @pytest.fixture
    def mock_auth_manager(self):
        """Create a mock auth manager"""
        auth_manager = Mock(spec=AuthManager)
        auth_manager.get_token.return_value = None
        auth_manager.is_authenticated.return_value = False
        return auth_manager

    # Command Line Arguments Edge Cases
    @pytest.mark.unit
    def test_no_arguments(self):
        """Test CLI with no arguments"""
        with patch('sys.argv', ['upid']):
            with redirect_stdout(StringIO()) as stdout:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stdout.getvalue()
                assert "usage:" in output.lower()

    @pytest.mark.unit
    def test_invalid_command(self):
        """Test CLI with invalid command"""
        with patch('sys.argv', ['upid', 'invalid-command']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_help_command(self):
        """Test CLI help command"""
        with patch('sys.argv', ['upid', '--help']):
            with redirect_stdout(StringIO()) as stdout:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stdout.getvalue()
                assert "usage:" in output.lower()
                assert "commands:" in output.lower()

    @pytest.mark.unit
    def test_version_command(self):
        """Test CLI version command"""
        with patch('sys.argv', ['upid', '--version']):
            with redirect_stdout(StringIO()) as stdout:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stdout.getvalue()
                assert "upid" in output.lower()

    @pytest.mark.unit
    def test_extra_arguments(self):
        """Test CLI with extra arguments"""
        with patch('sys.argv', ['upid', 'login', 'extra', 'arguments']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_missing_required_arguments(self):
        """Test CLI with missing required arguments"""
        with patch('sys.argv', ['upid', 'login']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    # Authentication Command Edge Cases
    @pytest.mark.unit
    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        with patch('sys.argv', ['upid', 'login', '', '']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_login_invalid_email(self):
        """Test login with invalid email format"""
        with patch('sys.argv', ['upid', 'login', 'invalid-email', 'password']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_login_special_characters(self):
        """Test login with special characters in credentials"""
        with patch('sys.argv', ['upid', 'login', 'test@example.com', 'pass!@#$%^&*()']):
            with patch('upid.commands.auth.login') as mock_login:
                mock_login.return_value = True
                with redirect_stdout(StringIO()) as stdout:
                    upid.cli.main()
                    output = stdout.getvalue()
                    assert "success" in output.lower()

    @pytest.mark.unit
    def test_logout_without_login(self):
        """Test logout without being logged in"""
        with patch('sys.argv', ['upid', 'logout']):
            with patch('upid.commands.auth.logout') as mock_logout:
                mock_logout.return_value = True
                with redirect_stdout(StringIO()) as stdout:
                    upid.cli.main()
                    output = stdout.getvalue()
                    assert "logged out" in output.lower()

    # Cluster Command Edge Cases
    @pytest.mark.unit
    def test_list_clusters_unauthenticated(self):
        """Test list clusters without authentication"""
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=False):
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "not authenticated" in output.lower()

    @pytest.mark.unit
    def test_get_cluster_invalid_id(self):
        """Test get cluster with invalid cluster ID"""
        with patch('sys.argv', ['upid', 'cluster', 'get', 'invalid-cluster-id']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.get_cluster') as mock_get:
                    mock_get.side_effect = Exception("Cluster not found")
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "error:" in output.lower()

    @pytest.mark.unit
    def test_get_cluster_special_characters(self):
        """Test get cluster with special characters in cluster ID"""
        cluster_id = "cluster-with-special-chars-!@#$%^&*()"
        with patch('sys.argv', ['upid', 'cluster', 'get', cluster_id]):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.get_cluster') as mock_get:
                    mock_get.return_value = {"id": cluster_id, "name": "Test Cluster"}
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        assert cluster_id in output

    # Optimization Command Edge Cases
    @pytest.mark.unit
    def test_optimize_cluster_invalid_strategy(self):
        """Test optimize cluster with invalid strategy"""
        with patch('sys.argv', ['upid', 'optimize', 'cluster-id', '--strategy', 'invalid-strategy']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "error:" in output.lower()

    @pytest.mark.unit
    def test_optimize_cluster_invalid_safety_level(self):
        """Test optimize cluster with invalid safety level"""
        with patch('sys.argv', ['upid', 'optimize', 'cluster-id', '--safety', 'invalid-level']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "error:" in output.lower()

    @pytest.mark.unit
    def test_optimize_cluster_negative_timeout(self):
        """Test optimize cluster with negative timeout"""
        with patch('sys.argv', ['upid', 'optimize', 'cluster-id', '--timeout', '-1']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "error:" in output.lower()

    # Deploy Command Edge Cases
    @pytest.mark.unit
    def test_deploy_invalid_optimization_id(self):
        """Test deploy with invalid optimization ID"""
        with patch('sys.argv', ['upid', 'deploy', 'invalid-optimization-id']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.deploy.deploy_optimization') as mock_deploy:
                    mock_deploy.side_effect = Exception("Optimization not found")
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "error:" in output.lower()

    @pytest.mark.unit
    def test_deploy_without_confirmation(self):
        """Test deploy without confirmation flag"""
        with patch('sys.argv', ['upid', 'deploy', 'optimization-id']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.deploy.deploy_optimization') as mock_deploy:
                    mock_deploy.return_value = {"status": "deployed"}
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        assert "deployed" in output.lower()

    # Report Command Edge Cases
    @pytest.mark.unit
    def test_report_invalid_format(self):
        """Test report with invalid output format"""
        with patch('sys.argv', ['upid', 'report', '--format', 'invalid-format']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "error:" in output.lower()

    @pytest.mark.unit
    def test_report_invalid_date_range(self):
        """Test report with invalid date range"""
        with patch('sys.argv', ['upid', 'report', '--start-date', 'invalid-date']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "error:" in output.lower()

    # Configuration Command Edge Cases
    @pytest.mark.unit
    def test_config_set_invalid_key(self):
        """Test config set with invalid key"""
        with patch('sys.argv', ['upid', 'config', 'set', 'invalid-key', 'value']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_config_get_nonexistent_key(self):
        """Test config get with nonexistent key"""
        with patch('sys.argv', ['upid', 'config', 'get', 'nonexistent-key']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_config_reset(self):
        """Test config reset command"""
        with patch('sys.argv', ['upid', 'config', 'reset']):
            with patch('upid.core.config.Config.reset') as mock_reset:
                mock_reset.return_value = True
                with redirect_stdout(StringIO()) as stdout:
                    upid.cli.main()
                    output = stdout.getvalue()
                    assert "reset" in output.lower()

    # Input/Output Edge Cases
    @pytest.mark.unit
    def test_unicode_input(self):
        """Test CLI with Unicode input"""
        unicode_cluster_id = "cluster-你好世界-🎉"
        with patch('sys.argv', ['upid', 'cluster', 'get', unicode_cluster_id]):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.get_cluster') as mock_get:
                    mock_get.return_value = {"id": unicode_cluster_id, "name": "Unicode Cluster"}
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        assert unicode_cluster_id in output

    @pytest.mark.unit
    def test_very_long_input(self):
        """Test CLI with very long input"""
        long_cluster_id = "cluster-" + "x" * 1000
        with patch('sys.argv', ['upid', 'cluster', 'get', long_cluster_id]):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.get_cluster') as mock_get:
                    mock_get.return_value = {"id": long_cluster_id, "name": "Long Cluster"}
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        assert long_cluster_id in output

    @pytest.mark.unit
    def test_special_characters_in_output(self):
        """Test CLI with special characters in output"""
        special_output = "Output with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.return_value = [{"name": special_output}]
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        assert special_output in output

    # Environment Variable Edge Cases
    @pytest.mark.unit
    def test_environment_variable_override(self):
        """Test CLI with environment variable overrides"""
        with patch.dict(os.environ, {'UPID_API_URL': 'https://custom-api.upid.io'}):
            with patch('sys.argv', ['upid', 'config', 'get', 'api_url']):
                with redirect_stdout(StringIO()) as stdout:
                    upid.cli.main()
                    output = stdout.getvalue()
                    assert "custom-api.upid.io" in output

    @pytest.mark.unit
    def test_environment_variable_with_special_chars(self):
        """Test CLI with environment variables containing special characters"""
        with patch.dict(os.environ, {'UPID_API_URL': 'https://api.upid.io/path with spaces'}):
            with patch('sys.argv', ['upid', 'config', 'get', 'api_url']):
                with redirect_stdout(StringIO()) as stdout:
                    upid.cli.main()
                    output = stdout.getvalue()
                    assert "path with spaces" in output

    # Error Handling Edge Cases
    @pytest.mark.unit
    def test_keyboard_interrupt(self):
        """Test CLI handling of keyboard interrupt"""
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.side_effect = KeyboardInterrupt()
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "interrupted" in output.lower()

    @pytest.mark.unit
    def test_memory_error(self):
        """Test CLI handling of memory errors"""
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.side_effect = MemoryError("Out of memory")
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "memory" in output.lower()

    @pytest.mark.unit
    def test_permission_error(self):
        """Test CLI handling of permission errors"""
        with patch('sys.argv', ['upid', 'config', 'set', 'api_url', 'https://api.upid.io']):
            with patch('upid.core.config.Config.save') as mock_save:
                mock_save.side_effect = PermissionError("Permission denied")
                with redirect_stderr(StringIO()) as stderr:
                    with pytest.raises(SystemExit):
                        upid.cli.main()
                    output = stderr.getvalue()
                    assert "permission" in output.lower()

    # Network Edge Cases
    @pytest.mark.unit
    def test_network_timeout_during_command(self):
        """Test CLI handling of network timeouts"""
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.side_effect = Exception("Connection timeout")
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "timeout" in output.lower()

    @pytest.mark.unit
    def test_ssl_error_during_command(self):
        """Test CLI handling of SSL errors"""
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.side_effect = Exception("SSL certificate verify failed")
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "ssl" in output.lower()

    # File System Edge Cases
    @pytest.mark.unit
    def test_config_file_corruption(self):
        """Test CLI handling of corrupted config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid json content")
            config_file = f.name
        
        try:
            with patch('upid.core.config.CONFIG_FILE', config_file):
                with patch('sys.argv', ['upid', 'config', 'get', 'api_url']):
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "error" in output.lower()
        finally:
            os.unlink(config_file)

    @pytest.mark.unit
    def test_config_file_permission_denied(self):
        """Test CLI handling of config file permission issues"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('{"api_url": "https://api.upid.io"}')
            config_file = f.name
        
        try:
            # Make file read-only
            os.chmod(config_file, 0o444)
            
            with patch('upid.core.config.CONFIG_FILE', config_file):
                with patch('sys.argv', ['upid', 'config', 'set', 'api_url', 'https://new-api.upid.io']):
                    with redirect_stderr(StringIO()) as stderr:
                        with pytest.raises(SystemExit):
                            upid.cli.main()
                        output = stderr.getvalue()
                        assert "permission" in output.lower()
        finally:
            os.chmod(config_file, 0o666)
            os.unlink(config_file)

    # Concurrent Access Edge Cases
    @pytest.mark.unit
    def test_concurrent_cli_access(self):
        """Test CLI handling of concurrent access"""
        import threading
        import time
        
        results = []
        
        def run_cli_command():
            with patch('sys.argv', ['upid', 'config', 'get', 'api_url']):
                with patch('upid.core.config.Config.get', return_value='https://api.upid.io'):
                    with redirect_stdout(StringIO()) as stdout:
                        try:
                            upid.cli.main()
                            results.append("success")
                        except:
                            results.append("failed")
        
        threads = [threading.Thread(target=run_cli_command) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access gracefully
        assert len(results) == 5
        assert all(result == "success" for result in results)

    # Output Format Edge Cases
    @pytest.mark.unit
    def test_json_output_format(self):
        """Test CLI with JSON output format"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--format', 'json']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.return_value = [{"id": "cluster1", "name": "Test Cluster"}]
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        # Should be valid JSON
                        import json
                        json.loads(output)

    @pytest.mark.unit
    def test_yaml_output_format(self):
        """Test CLI with YAML output format"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--format', 'yaml']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.return_value = [{"id": "cluster1", "name": "Test Cluster"}]
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        # Should be valid YAML
                        import yaml
                        yaml.safe_load(output)

    @pytest.mark.unit
    def test_table_output_format(self):
        """Test CLI with table output format"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--format', 'table']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.return_value = [{"id": "cluster1", "name": "Test Cluster"}]
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        # Should contain table headers
                        assert "ID" in output or "Name" in output

    # Verbose Mode Edge Cases
    @pytest.mark.unit
    def test_verbose_mode(self):
        """Test CLI with verbose mode"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--verbose']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.return_value = [{"id": "cluster1", "name": "Test Cluster"}]
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        # Should contain verbose output
                        assert "DEBUG" in output or "INFO" in output

    @pytest.mark.unit
    def test_quiet_mode(self):
        """Test CLI with quiet mode"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--quiet']):
            with patch('upid.core.auth.AuthManager.is_authenticated', return_value=True):
                with patch('upid.commands.cluster.list_clusters') as mock_list:
                    mock_list.return_value = [{"id": "cluster1", "name": "Test Cluster"}]
                    with redirect_stdout(StringIO()) as stdout:
                        upid.cli.main()
                        output = stdout.getvalue()
                        # Should be minimal output
                        assert len(output.strip()) == 0 or "cluster1" in output 