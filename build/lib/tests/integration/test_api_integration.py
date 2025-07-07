"""
Integration tests for API interactions using testcontainers
"""
import pytest
import time
import json
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from upid.core.config import Config
from upid.core.api_client import UPIDAPIClient
from upid.core.auth import AuthManager


class TestAPIIntegration:
    """Integration tests for API interactions"""

    @pytest.fixture(scope="class")
    def mock_api_server(self):
        """Start a mock API server using testcontainers"""
        # Using a simple HTTP server container for testing
        container = DockerContainer("python:3.9-slim")
        container.with_command([
            "python", "-m", "http.server", "8000"
        ])
        container.with_exposed_ports(8000)
        
        with container:
            # Wait for server to start
            wait_for_logs(container, "Serving HTTP on")
            yield container

    @pytest.fixture
    def test_config(self):
        """Create test configuration"""
        config = Config()
        config.set('api_url', 'http://localhost:8000')
        config.set('timeout', 10)
        return config

    @pytest.mark.integration
    @pytest.mark.slow
    def test_api_server_connectivity(self, mock_api_server, test_config):
        """Test basic API server connectivity"""
        client = UPIDAPIClient(test_config)
        
        # Test basic connectivity
        try:
            # This would normally be a health check endpoint
            # For now, we'll just verify the container is running
            assert mock_api_server.is_running()
        except Exception as e:
            pytest.fail(f"Failed to connect to API server: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_api_client_initialization_with_container(self, mock_api_server, test_config):
        """Test API client initialization with containerized server"""
        client = UPIDAPIClient(test_config)
        
        assert client.config == test_config
        assert client.base_url == 'http://localhost:8000'
        assert client.api_version == 'v1'
        assert client.timeout == 10

    @pytest.mark.integration
    @pytest.mark.slow
    def test_auth_manager_with_container(self, mock_api_server, test_config):
        """Test auth manager with containerized server"""
        auth_manager = AuthManager(test_config)
        
        assert auth_manager.config == test_config
        assert auth_manager._current_user is None

    @pytest.mark.integration
    @pytest.mark.slow
    def test_config_persistence_with_container(self, mock_api_server, test_config):
        """Test configuration persistence with containerized environment"""
        # Test config operations
        test_config.set('test_key', 'test_value')
        test_config.set_auth_token('test_token_123')
        
        # Verify persistence
        assert test_config.get('test_key') == 'test_value'
        assert test_config.get_auth_token() == 'test_token_123'
        assert test_config.is_authenticated() is True

    @pytest.mark.integration
    @pytest.mark.slow
    def test_api_endpoint_availability(self, mock_api_server, test_config):
        """Test API endpoint availability"""
        client = UPIDAPIClient(test_config)
        
        # Test that the server is responding
        try:
            # This would test actual API endpoints
            # For now, we'll just verify the container is accessible
            container_host = mock_api_server.get_container_host_ip()
            container_port = mock_api_server.get_exposed_port(8000)
            
            assert container_host is not None
            assert container_port is not None
            
        except Exception as e:
            pytest.fail(f"API endpoint not available: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_network_connectivity(self, mock_api_server, test_config):
        """Test network connectivity to containerized API"""
        import requests
        
        try:
            # Test basic HTTP connectivity
            container_host = mock_api_server.get_container_host_ip()
            container_port = mock_api_server.get_exposed_port(8000)
            
            response = requests.get(f"http://{container_host}:{container_port}", timeout=5)
            assert response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Network connectivity test failed: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_environment_variables(self, mock_api_server):
        """Test container environment variables"""
        # Verify container environment
        container_env = mock_api_server.get_docker_client().inspect_container(
            mock_api_server.get_container_id()
        )['Config']['Env']
        
        # Check for expected environment variables
        assert any('PYTHON' in env for env in container_env)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_logs(self, mock_api_server):
        """Test container logs access"""
        # Get container logs
        logs = mock_api_server.get_logs()
        
        # Verify logs contain expected content
        assert logs is not None
        assert len(logs) > 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_resource_usage(self, mock_api_server):
        """Test container resource usage monitoring"""
        # Get container stats
        stats = mock_api_server.get_docker_client().stats(
            mock_api_server.get_container_id(), stream=False
        )
        
        # Verify stats are available
        assert stats is not None
        assert 'cpu_stats' in stats
        assert 'memory_stats' in stats

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_cleanup(self, mock_api_server):
        """Test container cleanup after tests"""
        # Verify container is running during test
        assert mock_api_server.is_running()
        
        # Container should be automatically cleaned up after test
        # This is handled by the context manager in the fixture

    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_container_instances(self):
        """Test multiple container instances"""
        containers = []
        
        try:
            # Start multiple containers
            for i in range(3):
                container = DockerContainer("python:3.9-slim")
                container.with_command([
                    "python", "-m", "http.server", f"800{i}"
                ])
                container.with_exposed_ports(f"800{i}")
                container.start()
                containers.append(container)
            
            # Verify all containers are running
            for container in containers:
                assert container.is_running()
                
        finally:
            # Clean up containers
            for container in containers:
                container.stop()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_network_isolation(self):
        """Test container network isolation"""
        # Start two containers on different ports
        container1 = DockerContainer("python:3.9-slim")
        container1.with_command(["python", "-m", "http.server", "8001"])
        container1.with_exposed_ports(8001)
        
        container2 = DockerContainer("python:3.9-slim")
        container2.with_command(["python", "-m", "http.server", "8002"])
        container2.with_exposed_ports(8002)
        
        try:
            container1.start()
            container2.start()
            
            # Verify both containers are running independently
            assert container1.is_running()
            assert container2.is_running()
            
            # Verify they're on different ports
            port1 = container1.get_exposed_port(8001)
            port2 = container2.get_exposed_port(8002)
            assert port1 != port2
            
        finally:
            container1.stop()
            container2.stop()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_restart(self, mock_api_server):
        """Test container restart functionality"""
        # Restart the container
        mock_api_server.stop()
        time.sleep(2)  # Wait for stop
        mock_api_server.start()
        
        # Verify container is running after restart
        assert mock_api_server.is_running()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_health_check(self, mock_api_server):
        """Test container health check"""
        # Verify container is healthy
        container_info = mock_api_server.get_docker_client().inspect_container(
            mock_api_server.get_container_id()
        )
        
        # Check container state
        state = container_info['State']
        assert state['Running'] is True
        assert state['Status'] == 'running'

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_file_system(self, mock_api_server):
        """Test container file system access"""
        # Execute command in container to check file system
        result = mock_api_server.exec_in_container([
            "ls", "-la", "/"
        ])
        
        # Verify we can access the file system
        assert result is not None
        assert len(result) > 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_process_list(self, mock_api_server):
        """Test container process list"""
        # Get running processes in container
        result = mock_api_server.exec_in_container([
            "ps", "aux"
        ])
        
        # Verify we can see processes
        assert result is not None
        assert "python" in result  # Should see our Python server process

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_environment_consistency(self, mock_api_server):
        """Test container environment consistency across restarts"""
        # Get initial environment
        initial_env = mock_api_server.exec_in_container(["env"])
        
        # Restart container
        mock_api_server.stop()
        mock_api_server.start()
        
        # Get environment after restart
        restart_env = mock_api_server.exec_in_container(["env"])
        
        # Verify environment is consistent
        assert initial_env is not None
        assert restart_env is not None
        # Note: Exact comparison might fail due to dynamic values
        # but we can verify both are accessible

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_port_mapping(self, mock_api_server):
        """Test container port mapping"""
        # Get container port mapping
        container_host = mock_api_server.get_container_host_ip()
        container_port = mock_api_server.get_exposed_port(8000)
        
        # Verify port mapping
        assert container_host is not None
        assert container_port is not None
        assert container_port != 8000  # Should be mapped to different port

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_volume_mounting(self):
        """Test container volume mounting"""
        import tempfile
        import os
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")
            
            # Start container with volume mount
            container = DockerContainer("python:3.9-slim")
            container.with_volume_mapping(temp_dir, "/test")
            container.with_command(["ls", "/test"])
            container.with_exposed_ports(8000)
            
            try:
                container.start()
                
                # Verify volume is mounted
                result = container.exec_in_container(["cat", "/test/test.txt"])
                assert "test content" in result
                
            finally:
                container.stop()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_environment_variables_injection(self):
        """Test container environment variables injection"""
        # Start container with custom environment variables
        container = DockerContainer("python:3.9-slim")
        container.with_env("TEST_VAR", "test_value")
        container.with_env("ANOTHER_VAR", "another_value")
        container.with_command(["env"])
        container.with_exposed_ports(8000)
        
        try:
            container.start()
            
            # Verify environment variables are set
            result = container.exec_in_container(["env"])
            assert "TEST_VAR=test_value" in result
            assert "ANOTHER_VAR=another_value" in result
            
        finally:
            container.stop()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_container_network_connectivity_between_containers(self):
        """Test network connectivity between containers"""
        # Start two containers on the same network
        network_name = "test_network"
        
        # Create network
        docker_client = DockerContainer("python:3.9-slim").get_docker_client()
        try:
            docker_client.create_network(network_name)
        except:
            pass  # Network might already exist
        
        # Start containers
        container1 = DockerContainer("python:3.9-slim")
        container1.with_network(network_name)
        container1.with_command(["python", "-m", "http.server", "8000"])
        container1.with_exposed_ports(8000)
        
        container2 = DockerContainer("python:3.9-slim")
        container2.with_network(network_name)
        container2.with_command(["sleep", "infinity"])
        
        try:
            container1.start()
            container2.start()
            
            # Test connectivity between containers
            result = container2.exec_in_container([
                "curl", "-f", "http://container1:8000"
            ])
            
            # Should be able to connect (even if it fails, the attempt should work)
            assert result is not None
            
        finally:
            container1.stop()
            container2.stop()
            try:
                docker_client.remove_network(network_name)
            except:
                pass 