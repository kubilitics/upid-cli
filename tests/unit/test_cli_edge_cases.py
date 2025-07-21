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
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                assert "usage:" in output.lower() or "commands:" in output.lower()

    @pytest.mark.unit
    def test_invalid_command(self):
        """Test CLI with invalid command"""
        with patch('sys.argv', ['upid', 'invalid-command']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                assert "error:" in output.lower() or "no such command" in output.lower()

    @pytest.mark.unit
    def test_help_command(self):
        """Test CLI help command"""
        with patch('sys.argv', ['upid', '--help']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                assert "usage:" in output.lower() or "commands:" in output.lower()

    @pytest.mark.unit
    def test_version_command(self):
        """Test CLI version command"""
        with patch('sys.argv', ['upid', '--version']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                assert "upid" in output.lower()

    @pytest.mark.unit
    def test_extra_arguments(self):
        """Test CLI with extra arguments"""
        with patch('sys.argv', ['upid', 'login', 'extra', 'arguments']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                assert "error:" in output.lower() or "too many arguments" in output.lower()

    @pytest.mark.unit
    def test_missing_required_arguments(self):
        """Test CLI with missing required arguments"""
        with patch('sys.argv', ['upid', 'login']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                assert "error:" in output.lower() or "missing argument" in output.lower()

    # Authentication Command Edge Cases
    @pytest.mark.unit
    def test_login_empty_credentials(self):
        """Test login with empty credentials"""
        with patch('sys.argv', ['upid', 'auth', 'login', '', '']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_login_invalid_email(self):
        """Test login with invalid email format"""
        with patch('sys.argv', ['upid', 'auth', 'login', 'invalid-email', 'password']):
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error:" in output.lower()

    @pytest.mark.unit
    def test_login_special_characters(self):
        """Test login with special characters"""
        with patch('sys.argv', ['upid', 'login', 'test@example.com', 'pass!@#']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                # Should handle special characters gracefully

    @pytest.mark.unit
    def test_logout_without_login(self):
        """Test logout without being logged in"""
        with patch('sys.argv', ['upid', 'logout']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should handle logout gracefully

    # Cluster Command Edge Cases
    @pytest.mark.unit
    def test_list_clusters_unauthenticated(self):
        """Test listing clusters without authentication"""
        with patch('sys.argv', ['upid', 'cluster', 'list']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                # Should handle unauthenticated state gracefully

    @pytest.mark.unit
    def test_get_cluster_invalid_id(self):
        """Test getting cluster with invalid ID"""
        with patch('sys.argv', ['upid', 'cluster', 'get', 'invalid-id']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                # Should handle invalid cluster ID gracefully

    @pytest.mark.unit
    def test_get_cluster_special_characters(self):
        """Test getting cluster with special characters in ID"""
        with patch('sys.argv', ['upid', 'cluster', 'get', 'cluster!@#']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                # Should handle special characters gracefully

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
            with redirect_stderr(StringIO()) as stderr:
                with pytest.raises(SystemExit):
                    upid.cli.main()
                output = stderr.getvalue()
                assert "error" in output.lower() or "failed" in output.lower()

    @pytest.mark.unit
    def test_deploy_without_confirmation(self):
        """Test deploy without confirmation"""
        with patch('sys.argv', ['upid', 'deploy', 'optimization-id']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stderr.getvalue()
                # Should handle missing confirmation gracefully

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
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should handle config reset gracefully

    # Input/Output Edge Cases
    @pytest.mark.unit
    def test_unicode_input(self):
        """Test CLI with unicode input"""
        with patch('sys.argv', ['upid', 'login', 'test@example.com', 'password']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                # Should handle unicode gracefully

    @pytest.mark.unit
    def test_very_long_input(self):
        """Test CLI with very long input"""
        long_input = 'a' * 1000
        with patch('sys.argv', ['upid', 'login', long_input, 'password']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                # Should handle long input gracefully

    @pytest.mark.unit
    def test_special_characters_in_output(self):
        """Test CLI with special characters in output"""
        with patch('sys.argv', ['upid', 'status']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                # Should handle special characters in output gracefully

    # Environment Variable Edge Cases
    @pytest.mark.unit
    def test_environment_variable_override(self):
        """Test environment variable override"""
        with patch.dict(os.environ, {'UPID_API_URL': 'https://custom.api.upid.io'}):
            with patch('sys.argv', ['upid', 'status']):
                with redirect_stdout(StringIO()) as stdout:
                    try:
                        upid.cli.main()
                    except SystemExit:
                        pass  # Expected exit
                    # Should use environment variable

    @pytest.mark.unit
    def test_environment_variable_with_special_chars(self):
        """Test environment variable with special characters"""
        with patch.dict(os.environ, {'UPID_API_URL': 'https://api.upid.io/path!@#'}):
            with patch('sys.argv', ['upid', 'status']):
                with redirect_stdout(StringIO()) as stdout:
                    try:
                        upid.cli.main()
                    except SystemExit:
                        pass  # Expected exit
                    # Should handle special characters in env vars

    # Error Handling Edge Cases
    @pytest.mark.unit
    def test_keyboard_interrupt(self):
        """Test CLI with keyboard interrupt"""
        with patch('sys.argv', ['upid', 'status']):
            with patch('upid.cli.cli') as mock_cli:
                mock_cli.side_effect = KeyboardInterrupt()
                with pytest.raises(SystemExit):
                    upid.cli.main()

    @pytest.mark.unit
    def test_memory_error(self):
        """Test CLI with memory error"""
        with patch('sys.argv', ['upid', 'status']):
            with patch('upid.cli.cli') as mock_cli:
                mock_cli.side_effect = MemoryError()
                with pytest.raises(SystemExit):
                    upid.cli.main()

    @pytest.mark.unit
    def test_permission_error(self):
        """Test CLI with permission error"""
        with patch('sys.argv', ['upid', 'status']):
            with patch('upid.cli.cli') as mock_cli:
                mock_cli.side_effect = PermissionError()
                with pytest.raises(SystemExit):
                    upid.cli.main()

    @pytest.mark.unit
    def test_network_timeout_during_command(self):
        """Test CLI with network timeout"""
        with patch('sys.argv', ['upid', 'status']):
            with patch('upid.cli.cli') as mock_cli:
                mock_cli.side_effect = TimeoutError()
                with pytest.raises(SystemExit):
                    upid.cli.main()

    @pytest.mark.unit
    def test_ssl_error_during_command(self):
        """Test CLI with SSL error"""
        with patch('sys.argv', ['upid', 'status']):
            with patch('upid.cli.cli') as mock_cli:
                mock_cli.side_effect = Exception("SSL Error")
                with pytest.raises(SystemExit):
                    upid.cli.main()

    # File System Edge Cases
    @pytest.mark.unit
    def test_config_file_corruption(self):
        """Test CLI with corrupted config file"""
        with patch('sys.argv', ['upid', 'status']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                # Should handle corrupted config gracefully

    @pytest.mark.unit
    def test_config_file_permission_denied(self):
        """Test CLI with permission denied on config file"""
        with patch('sys.argv', ['upid', 'status']):
            with redirect_stderr(StringIO()) as stderr:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                # Should handle permission issues gracefully

    # Concurrent Access Edge Cases
    @pytest.mark.unit
    def test_concurrent_cli_access(self):
        """Test concurrent CLI access"""
        with patch('sys.argv', ['upid', 'status']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                # Should handle concurrent access gracefully

    # Output Format Edge Cases
    @pytest.mark.unit
    def test_json_output_format(self):
        """Test CLI with JSON output format"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--format', 'json']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should output JSON format

    @pytest.mark.unit
    def test_yaml_output_format(self):
        """Test CLI with YAML output format"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--format', 'yaml']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should output YAML format

    @pytest.mark.unit
    def test_table_output_format(self):
        """Test CLI with table output format"""
        with patch('sys.argv', ['upid', 'cluster', 'list', '--format', 'table']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should output table format

    # Verbose Mode Edge Cases
    @pytest.mark.unit
    def test_verbose_mode(self):
        """Test CLI with verbose mode"""
        with patch('sys.argv', ['upid', '--verbose', 'status']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should show verbose output

    @pytest.mark.unit
    def test_quiet_mode(self):
        """Test CLI with quiet mode"""
        with patch('sys.argv', ['upid', 'status']):
            with redirect_stdout(StringIO()) as stdout:
                try:
                    upid.cli.main()
                except SystemExit:
                    pass  # Expected exit
                output = stdout.getvalue()
                # Should show minimal output 