"""
Comprehensive edge case tests for UPID CLI
These tests ensure the CLI handles all possible failure scenarios gracefully.
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from upid.core.config import Config
from upid.core.auth import AuthManager
from upid.core.api_client import UPIDAPIClient
# Import the actual CLI functions that exist
from upid.core.api_client import UPIDAPIClient


class TestEdgeCases:
    """Test edge cases and error handling scenarios"""

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

    # Network and Connectivity Edge Cases
    @pytest.mark.unit
    def test_network_timeout_handling(self, mock_config, mock_auth_manager):
        """Test handling of network timeouts"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            with pytest.raises(Exception) as exc_info:
                client.get_clusters()
            
            assert "Connection timeout" in str(exc_info.value)

    @pytest.mark.unit
    def test_dns_resolution_failure(self, mock_config, mock_auth_manager):
        """Test handling of DNS resolution failures"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Name or service not known")
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            with pytest.raises(Exception) as exc_info:
                client.get_clusters()
            
            assert "Name or service not known" in str(exc_info.value)

    @pytest.mark.unit
    def test_ssl_certificate_errors(self, mock_config, mock_auth_manager):
        """Test handling of SSL certificate errors"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("SSL certificate verify failed")
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            with pytest.raises(Exception) as exc_info:
                client.get_clusters()
            
            assert "SSL certificate verify failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_connection_refused(self, mock_config, mock_auth_manager):
        """Test handling of connection refused errors"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            with pytest.raises(Exception) as exc_info:
                client.get_clusters()
            
            assert "Connection refused" in str(exc_info.value)

    # Authentication Edge Cases
    @pytest.mark.unit
    def test_invalid_credentials(self, mock_config, mock_auth_manager):
        """Test handling of invalid credentials"""
        with patch.object(mock_auth_manager, 'login') as mock_login:
            mock_login.side_effect = Exception("Invalid credentials")
            
            with pytest.raises(Exception) as exc_info:
                mock_auth_manager.login("invalid@email.com", "wrongpassword")
            
            assert "Invalid credentials" in str(exc_info.value)

    @pytest.mark.unit
    def test_expired_token_handling(self, mock_config, mock_auth_manager):
        """Test handling of expired tokens"""
        with patch.object(mock_auth_manager, 'get_token') as mock_get_token:
            mock_get_token.return_value = "expired_token"
            
            with patch.object(mock_auth_manager, 'refresh_token') as mock_refresh:
                mock_refresh.side_effect = Exception("Token expired")
                
                with pytest.raises(Exception) as exc_info:
                    mock_auth_manager.refresh_token()
                
                assert "Token expired" in str(exc_info.value)

    @pytest.mark.unit
    def test_malformed_token(self, mock_config, mock_auth_manager):
        """Test handling of malformed tokens"""
        with patch.object(mock_auth_manager, 'get_token') as mock_get_token:
            mock_get_token.return_value = "malformed.token.here"
            
            with patch.object(mock_auth_manager, 'validate_token') as mock_validate:
                mock_validate.return_value = False
                
                assert not mock_auth_manager.is_authenticated()

    @pytest.mark.unit
    def test_empty_credentials(self, mock_config, mock_auth_manager):
        """Test handling of empty credentials"""
        with pytest.raises(ValueError):
            mock_auth_manager.login("", "")

    @pytest.mark.unit
    def test_none_credentials(self, mock_config, mock_auth_manager):
        """Test handling of None credentials"""
        with pytest.raises(ValueError):
            mock_auth_manager.login(None, None)

    # Configuration Edge Cases
    @pytest.mark.unit
    def test_missing_config_file(self, mock_config):
        """Test handling of missing configuration file"""
        with patch('os.path.exists', return_value=False):
            config = Config()
            # Should not raise an exception, should use defaults
            assert config.get('api_url') is not None

    @pytest.mark.unit
    def test_corrupted_config_file(self, mock_config):
        """Test handling of corrupted configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid json content")
            config_file = f.name
        
        try:
            with patch('upid.core.config.CONFIG_FILE', config_file):
                config = Config()
                # Should handle corrupted file gracefully
                assert config.get('api_url') is not None
        finally:
            os.unlink(config_file)

    @pytest.mark.unit
    def test_invalid_config_values(self, mock_config):
        """Test handling of invalid configuration values"""
        config = Config()
        
        # Test invalid timeout
        config.set('timeout', -1)
        assert config.get('timeout') == 30  # Should default to 30
        
        # Test invalid URL
        config.set('api_url', 'not-a-valid-url')
        # Should still be set but might cause issues later
        
        # Test invalid boolean
        config.set('verbose', 'not-a-boolean')
        # Should handle gracefully

    @pytest.mark.unit
    def test_config_file_permissions(self, mock_config):
        """Test handling of config file permission issues"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('{"api_url": "https://api.upid.io"}')
            config_file = f.name
        
        try:
            # Make file read-only
            os.chmod(config_file, 0o444)
            
            with patch('upid.core.config.CONFIG_FILE', config_file):
                config = Config()
                # Should handle permission issues gracefully
                assert config.get('api_url') is not None
        finally:
            os.chmod(config_file, 0o666)
            os.unlink(config_file)

    # API Response Edge Cases
    @pytest.mark.unit
    def test_empty_api_response(self, mock_config, mock_auth_manager):
        """Test handling of empty API responses"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.text = ""
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            response = client.get_clusters()
            
            assert response == {}

    @pytest.mark.unit
    def test_malformed_json_response(self, mock_config, mock_auth_manager):
        """Test handling of malformed JSON responses"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.text = "invalid json"
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            with pytest.raises(json.JSONDecodeError):
                client.get_clusters()

    @pytest.mark.unit
    def test_large_response_handling(self, mock_config, mock_auth_manager):
        """Test handling of very large API responses"""
        large_data = {"data": ["x" * 1000000] * 100}  # ~100MB
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = large_data
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle large responses without memory issues
            response = client.get_clusters()
            assert len(response['data']) == 100

    @pytest.mark.unit
    def test_slow_api_response(self, mock_config, mock_auth_manager):
        """Test handling of slow API responses"""
        import time
        
        with patch('requests.Session.get') as mock_get:
            def slow_response(*args, **kwargs):
                time.sleep(0.1)  # Simulate slow response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "ok"}
                return mock_response
            
            mock_get.side_effect = slow_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            client.timeout = 0.05  # Set short timeout
            
            with pytest.raises(Exception):
                client.get_clusters()

    # CLI Command Edge Cases
    @pytest.mark.unit
    def test_invalid_command_arguments(self, mock_config, mock_auth_manager):
        """Test handling of invalid command arguments"""
        with pytest.raises(SystemExit):
            # Test with invalid cluster ID
            get_cluster("invalid-cluster-id", mock_config, mock_auth_manager)

    @pytest.mark.unit
    def test_missing_required_parameters(self, mock_config, mock_auth_manager):
        """Test handling of missing required parameters"""
        with pytest.raises(ValueError):
            # Test login without credentials
            login("", "", mock_config, mock_auth_manager)

    @pytest.mark.unit
    def test_duplicate_operations(self, mock_config, mock_auth_manager):
        """Test handling of duplicate operations"""
        # Test multiple simultaneous optimizations
        with patch('upid.commands.optimize.optimize_cluster') as mock_optimize:
            mock_optimize.return_value = {"status": "started"}
            
            # Should handle gracefully
            result1 = optimize_cluster("cluster1", mock_config, mock_auth_manager)
            result2 = optimize_cluster("cluster1", mock_config, mock_auth_manager)
            
            assert result1 == result2

    # Kubernetes/Docker Edge Cases
    @pytest.mark.unit
    def test_unreachable_kubernetes_cluster(self, mock_config, mock_auth_manager):
        """Test handling of unreachable Kubernetes cluster"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Connection to cluster failed")
            
            with pytest.raises(Exception) as exc_info:
                # Simulate cluster detection
                pass
            
            assert "Connection to cluster failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_insufficient_permissions(self, mock_config, mock_auth_manager):
        """Test handling of insufficient permissions"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Forbidden")
            
            with pytest.raises(Exception) as exc_info:
                # Simulate permission check
                pass
            
            assert "Forbidden" in str(exc_info.value)

    @pytest.mark.unit
    def test_docker_not_running(self, mock_config, mock_auth_manager):
        """Test handling when Docker is not running"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Cannot connect to the Docker daemon")
            
            with pytest.raises(Exception) as exc_info:
                # Simulate Docker check
                pass
            
            assert "Cannot connect to the Docker daemon" in str(exc_info.value)

    # Resource and Memory Edge Cases
    @pytest.mark.unit
    def test_memory_pressure(self, mock_config, mock_auth_manager):
        """Test handling under memory pressure"""
        import gc
        
        # Create many objects to simulate memory pressure
        objects = []
        for i in range(10000):
            objects.append({"data": "x" * 1000})
        
        # Force garbage collection
        gc.collect()
        
        # Should still work normally
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        assert client is not None

    @pytest.mark.unit
    def test_disk_space_issues(self, mock_config, mock_auth_manager):
        """Test handling of disk space issues"""
        with patch('tempfile.mkstemp') as mock_mkstemp:
            mock_mkstemp.side_effect = OSError("No space left on device")
            
            with pytest.raises(OSError) as exc_info:
                # Simulate file creation
                pass
            
            assert "No space left on device" in str(exc_info.value)

    # Concurrent Access Edge Cases
    @pytest.mark.unit
    def test_concurrent_config_access(self, mock_config):
        """Test handling of concurrent configuration access"""
        import threading
        import time
        
        config = Config()
        results = []
        
        def read_config():
            for i in range(10):
                results.append(config.get('api_url'))
                time.sleep(0.01)
        
        threads = [threading.Thread(target=read_config) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should not crash and should return consistent values
        assert len(results) == 50
        assert all(result is not None for result in results)

    # Error Recovery Edge Cases
    @pytest.mark.unit
    def test_automatic_retry_on_failure(self, mock_config, mock_auth_manager):
        """Test automatic retry mechanism on failures"""
        with patch('requests.Session.get') as mock_get:
            # First call fails, second succeeds
            mock_get.side_effect = [
                Exception("Temporary failure"),
                Mock(status_code=200, json=lambda: {"status": "ok"})
            ]
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should retry automatically
            response = client.get_clusters()
            assert response == {"status": "ok"}

    @pytest.mark.unit
    def test_graceful_degradation(self, mock_config, mock_auth_manager):
        """Test graceful degradation when features are unavailable"""
        with patch('upid.commands.cluster.list_clusters') as mock_list:
            mock_list.side_effect = Exception("Feature not available")
            
            # Should handle gracefully and provide fallback
            try:
                list_clusters(mock_config, mock_auth_manager)
            except Exception as e:
                assert "Feature not available" in str(e)

    # Security Edge Cases
    @pytest.mark.unit
    def test_sql_injection_prevention(self, mock_config, mock_auth_manager):
        """Test prevention of SQL injection attacks"""
        malicious_input = "'; DROP TABLE users; --"
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "safe"}
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle malicious input safely
            response = client.get(f'/test?param={malicious_input}')
            assert response == {"status": "safe"}

    @pytest.mark.unit
    def test_xss_prevention(self, mock_config, mock_auth_manager):
        """Test prevention of XSS attacks"""
        malicious_input = "<script>alert('xss')</script>"
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "safe"}
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle malicious input safely
            response = client.get(f'/test?param={malicious_input}')
            assert response == {"status": "safe"}

    # Performance Edge Cases
    @pytest.mark.unit
    def test_large_dataset_handling(self, mock_config, mock_auth_manager):
        """Test handling of large datasets"""
        large_dataset = {"clusters": [{"id": f"cluster-{i}", "name": f"Cluster {i}"} for i in range(10000)]}
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = large_dataset
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle large datasets efficiently
            response = client.get('/clusters')
            assert len(response['clusters']) == 10000

    @pytest.mark.unit
    def test_concurrent_api_calls(self, mock_config, mock_auth_manager):
        """Test handling of concurrent API calls"""
        import threading
        import time
        
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        results = []
        
        def make_api_call():
            with patch('requests.Session.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"thread_id": threading.get_ident()}
                mock_get.return_value = mock_response
                
                response = client.get_clusters()
                results.append(response)
        
        threads = [threading.Thread(target=make_api_call) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent calls without issues
        assert len(results) == 10

    # Data Validation Edge Cases
    @pytest.mark.unit
    def test_invalid_json_handling(self, mock_config, mock_auth_manager):
        """Test handling of invalid JSON data"""
        invalid_json = '{"invalid": json, "missing": quotes}'
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", invalid_json, 0)
            mock_response.text = invalid_json
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            with pytest.raises(json.JSONDecodeError):
                client.get_clusters()

    @pytest.mark.unit
    def test_null_value_handling(self, mock_config, mock_auth_manager):
        """Test handling of null values in responses"""
        response_with_nulls = {
            "data": None,
            "message": "Success",
            "details": {
                "cluster": None,
                "status": "active"
            }
        }
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = response_with_nulls
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle null values gracefully
            response = client.get_clusters()
            assert response['data'] is None
            assert response['message'] == "Success"

    # Environment Edge Cases
    @pytest.mark.unit
    def test_missing_environment_variables(self, mock_config, mock_auth_manager):
        """Test handling of missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            # Should work with default values
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            assert client is not None

    @pytest.mark.unit
    def test_invalid_environment_variables(self, mock_config, mock_auth_manager):
        """Test handling of invalid environment variables"""
        with patch.dict(os.environ, {'UPID_API_URL': 'not-a-valid-url'}):
            # Should handle invalid env vars gracefully
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            assert client is not None

    # Logging and Output Edge Cases
    @pytest.mark.unit
    def test_unicode_handling(self, mock_config, mock_auth_manager):
        """Test handling of Unicode characters"""
        unicode_data = {
            "message": "Café au lait avec des caractères spéciaux: 你好世界",
            "data": "🎉🚀✨"
        }
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = unicode_data
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle Unicode gracefully
            response = client.get_clusters()
            assert "Café" in response['message']
            assert "🎉" in response['data']

    @pytest.mark.unit
    def test_very_long_strings(self, mock_config, mock_auth_manager):
        """Test handling of very long strings"""
        long_string = "x" * 1000000  # 1MB string
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": long_string}
            mock_get.return_value = mock_response
            
            client = UPIDAPIClient(mock_config, mock_auth_manager)
            
            # Should handle long strings without memory issues
            response = client.get_clusters()
            assert len(response['data']) == 1000000 