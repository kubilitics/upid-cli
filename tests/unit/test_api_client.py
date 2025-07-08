"""
Unit tests for API client
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import RequestException, HTTPError
from upid.core.api_client import UPIDAPIClient
from upid.core.config import Config


class TestUPIDAPIClient:
    """Test API client functionality"""

    @pytest.mark.unit
    def test_api_client_initialization(self, mock_config, mock_auth_manager):
        """Test API client initialization"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        assert client.config == mock_config
        assert client.auth_manager == mock_auth_manager
        assert client.base_url == 'https://api.upid.io'
        assert client.api_version == 'v1'
        assert client.timeout == 30

    @pytest.mark.unit
    def test_api_client_custom_config(self, mock_config, mock_auth_manager):
        """Test API client with custom configuration"""
        mock_config.set('api_url', 'https://custom.upid.io')
        mock_config.set('api_version', 'v2')
        mock_config.set('timeout', 60)
        
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        assert client.base_url == 'https://custom.upid.io'
        assert client.api_version == 'v2'
        assert client.timeout == 60

    @pytest.mark.unit
    def test_get_auth_headers_with_token(self, mock_config, mock_auth_manager):
        """Test getting auth headers with token"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        # Mock the get_token method
        with patch.object(mock_auth_manager, 'get_token', return_value='test_token_123'):
            headers = client._get_headers()
            
            assert headers['Authorization'] == 'Bearer test_token_123'
            assert headers['Content-Type'] == 'application/json'
            assert headers['User-Agent'] == 'UPID-CLI/1.0.0'

    @pytest.mark.unit
    def test_get_auth_headers_without_token(self, mock_config, mock_auth_manager):
        """Test getting auth headers without token"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        # Mock the get_token method
        with patch.object(mock_auth_manager, 'get_token', return_value=None):
            headers = client._get_headers()
            
            assert 'Authorization' not in headers
            assert headers['Content-Type'] == 'application/json'
            assert headers['User-Agent'] == 'UPID-CLI/1.0.0'

    @pytest.mark.unit
    def test_get_request_success(self, mock_config, mock_auth_manager):
        """Test successful GET request"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            # Test GET request
            response = client._get('/test-endpoint')
            
            assert response == {'data': 'test'}
            mock_get.assert_called_once()

    @pytest.mark.unit
    def test_get_request_with_params(self, mock_config, mock_auth_manager):
        """Test GET request with parameters"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            # Test GET request with params
            params = {'key': 'value', 'filter': 'active'}
            response = client._get('/test-endpoint', params=params)
            
            assert response == {'data': 'test'}
            # Check that params were passed correctly
            call_args = mock_get.call_args
            assert call_args[1]['params'] == params

    @pytest.mark.unit
    def test_get_request_http_error(self, mock_config, mock_auth_manager):
        """Test GET request with HTTP error"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock HTTP error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_response.raise_for_status.side_effect = HTTPError("404 Client Error: Not Found for url: https://api.upid.io/v1/test-endpoint")
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            # Test HTTP error
            with pytest.raises(HTTPError, match="404 Client Error"):
                client._get('/test-endpoint')

    @pytest.mark.unit
    def test_get_request_connection_error(self, mock_config, mock_auth_manager):
        """Test GET request with connection error"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        with patch.object(client.session, 'get', side_effect=RequestException("Connection failed")) as mock_get:
            # Test connection error
            with pytest.raises(Exception, match="Request failed: Connection failed"):
                client._get('/test-endpoint')

    @pytest.mark.unit
    def test_post_request_success(self, mock_config, mock_auth_manager):
        """Test successful POST request"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': '123', 'status': 'created'}
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            # Test POST request
            data = {'name': 'test', 'value': 42}
            response = client._post('/test-endpoint', data=data)
            
            assert response == {'id': '123', 'status': 'created'}
            mock_post.assert_called_once()

    @pytest.mark.unit
    def test_post_request_with_json(self, mock_config, mock_auth_manager):
        """Test POST request with JSON data"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': '123'}
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            # Test POST request with JSON
            json_data = {'complex': {'nested': 'data'}}
            response = client._post('/test-endpoint', json=json_data)
            
            assert response == {'id': '123'}
            # Check that JSON was passed correctly
            call_args = mock_post.call_args
            assert call_args[1]['json'] == json_data

    @pytest.mark.unit
    def test_post_request_server_error(self, mock_config, mock_auth_manager):
        """Test POST request with server error"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock server error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error: Internal Server Error for url: https://api.upid.io/v1/test-endpoint")
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            # Test server error
            with pytest.raises(HTTPError, match="500 Server Error"):
                client._post('/test-endpoint', data={'test': 'data'})

    @pytest.mark.unit
    def test_put_request_success(self, mock_config, mock_auth_manager):
        """Test successful PUT request"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': '123', 'status': 'updated'}
        
        with patch.object(client.session, 'put', return_value=mock_response) as mock_put:
            # Test PUT request
            data = {'name': 'updated', 'value': 100}
            response = client._put('/test-endpoint/123', data=data)
            
            assert response == {'id': '123', 'status': 'updated'}
            mock_put.assert_called_once()

    @pytest.mark.unit
    def test_delete_request_success(self, mock_config, mock_auth_manager):
        """Test successful DELETE request"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        
        with patch.object(client.session, 'delete', return_value=mock_response) as mock_delete:
            # Test DELETE request
            response = client._delete('/test-endpoint/123')
            
            assert response == {}
            mock_delete.assert_called_once()

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_login_success(self, mock_post, mock_config, mock_auth_manager):
        """Test successful login"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock login response
        mock_response = {
            'token': 'test_token_123',
            'user': {
                'email': 'test@example.com',
                'name': 'Test User'
            }
        }
        mock_post.return_value = mock_response
        
        # Test login
        response = client.login('test@example.com', 'password123')
        
        assert response == mock_response
        mock_post.assert_called_once_with('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_login_failure(self, mock_post, mock_config, mock_auth_manager):
        """Test login failure"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock login error
        mock_post.side_effect = HTTPError("401 Unauthorized")
        
        # Test login failure
        with pytest.raises(HTTPError, match="401 Unauthorized"):
            client.login('test@example.com', 'wrong_password')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_logout_success(self, mock_post, mock_config, mock_auth_manager):
        """Test successful logout"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock logout response
        mock_response = {'message': 'Logged out successfully'}
        mock_post.return_value = mock_response
        
        # Test logout
        response = client.logout()
        
        assert response == mock_response
        mock_post.assert_called_once_with('/auth/logout')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_profile_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful profile retrieval"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock profile response
        mock_response = {
            'user': {
                'email': 'test@example.com',
                'name': 'Test User',
                'organization': 'Test Corp'
            }
        }
        mock_get.return_value = mock_response
        
        # Test get profile
        response = client.get_profile()
        
        assert response == mock_response
        mock_get.assert_called_once_with('/auth/profile')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_refresh_token_success(self, mock_post, mock_config, mock_auth_manager):
        """Test successful token refresh"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock refresh response
        mock_response = {'token': 'new_token_456'}
        mock_post.return_value = mock_response
        
        # Test token refresh
        response = client.refresh_token()
        
        assert response == 'new_token_456'
        mock_post.assert_called_once_with('/auth/refresh')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_clusters_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful clusters retrieval"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock clusters response
        mock_response = {
            'clusters': [
                {'id': 'cluster-1', 'name': 'Test Cluster 1'},
                {'id': 'cluster-2', 'name': 'Test Cluster 2'}
            ]
        }
        mock_get.return_value = mock_response
        
        # Test get clusters
        response = client.get_clusters()
        
        assert response == mock_response
        mock_get.assert_called_once_with('/clusters')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_cluster_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful single cluster retrieval"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock cluster response
        mock_response = {
            'cluster': {
                'id': 'cluster-123',
                'name': 'Test Cluster',
                'status': 'healthy'
            }
        }
        mock_get.return_value = mock_response
        
        # Test get cluster
        response = client.get_cluster('cluster-123')
        
        assert response == mock_response
        mock_get.assert_called_once_with('/clusters/cluster-123')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_create_cluster_success(self, mock_post, mock_config, mock_auth_manager):
        """Test successful cluster creation"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock creation response
        mock_response = {
            'cluster': {
                'id': 'cluster-123',
                'name': 'New Cluster',
                'status': 'creating'
            }
        }
        mock_post.return_value = mock_response
        
        # Test create cluster
        cluster_data = {
            'name': 'New Cluster',
            'region': 'us-west-2',
            'kubeconfig': 'base64_encoded_config'
        }
        response = client.create_cluster(cluster_data)
        
        assert response == mock_response
        mock_post.assert_called_once_with('/clusters', json=cluster_data)

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_delete')
    def test_delete_cluster_success(self, mock_delete, mock_config, mock_auth_manager):
        """Test successful cluster deletion"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock deletion response
        mock_response = {'message': 'Cluster deleted successfully'}
        mock_delete.return_value = mock_response
        
        # Test delete cluster
        response = client.delete_cluster('cluster-123')
        
        assert response == mock_response
        mock_delete.assert_called_once_with('/clusters/cluster-123')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_optimize_cluster_success(self, mock_post, mock_config, mock_auth_manager):
        """Test successful cluster optimization"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock optimization response
        mock_response = {
            'optimization_id': 'opt-123',
            'status': 'running',
            'estimated_savings': 1500.0
        }
        mock_post.return_value = mock_response
        
        # Test optimize cluster
        optimization_params = {
            'strategy': 'cost-focused',
            'safety_level': 'strict'
        }
        response = client.optimize_cluster('cluster-123', optimization_params)
        
        assert response == mock_response
        mock_post.assert_called_once_with(
            '/clusters/cluster-123/optimize',
            json=optimization_params
        )

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_optimization_result_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful optimization result retrieval"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock result response
        mock_response = {
            'optimization_id': 'opt-123',
            'status': 'completed',
            'savings': 1500.0,
            'recommendations': []
        }
        mock_get.return_value = mock_response
        
        # Test get optimization result
        response = client.get_optimization_result('opt-123')
        
        assert response == mock_response
        mock_get.assert_called_once_with('/optimizations/opt-123')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_post')
    def test_deploy_optimization_success(self, mock_post, mock_config, mock_auth_manager):
        """Test successful optimization deployment"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock deployment response
        mock_response = {
            'deployment_id': 'deploy-123',
            'status': 'deploying',
            'progress': {'completed': 0, 'total': 10}
        }
        mock_post.return_value = mock_response
        
        # Test deploy optimization
        deployment_data = {
            'optimization_id': 'opt-123',
            'confirm': True
        }
        response = client.deploy_optimization('cluster-123', deployment_data)
        
        assert response == mock_response
        mock_post.assert_called_once_with(
            '/clusters/cluster-123/deploy',
            json=deployment_data
        )

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_deployment_status_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful deployment status retrieval"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock status response
        mock_response = {
            'deployment_id': 'deploy-123',
            'status': 'completed',
            'progress': {'completed': 10, 'total': 10, 'percentage': 100}
        }
        mock_get.return_value = mock_response
        
        # Test get deployment status
        response = client.get_deployment_status('deploy-123')
        
        assert response == mock_response
        mock_get.assert_called_once_with('/deployments/deploy-123')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_cost_analysis_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful cost analysis retrieval"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock cost analysis response
        mock_response = {
            'total_cost': 2500.0,
            'breakdown': {'compute': 1800.0, 'storage': 400.0, 'network': 300.0},
            'trends': []
        }
        mock_get.return_value = mock_response
        
        # Test get cost analysis
        response = client.get_cost_analysis('cluster-123')
        
        assert response == mock_response
        mock_get.assert_called_once_with('/clusters/cluster-123/cost')

    @pytest.mark.unit
    @patch.object(UPIDAPIClient, '_get')
    def test_get_report_success(self, mock_get, mock_config, mock_auth_manager):
        """Test successful report generation"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock report response
        mock_response = {
            'report_id': 'report-123',
            'executive_summary': {},
            'recommendations': []
        }
        mock_get.return_value = mock_response
        
        # Test get report
        response = client.get_report('cluster-123', 'executive')
        
        assert response == mock_response
        mock_get.assert_called_once_with('/clusters/cluster-123/report', params={'type': 'executive'})

    @pytest.mark.unit
    def test_build_url(self, mock_config, mock_auth_manager):
        """Test URL building"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Test basic URL building
        url = client._build_url('/test')
        assert url == 'https://api.upid.io/v1/test'
        
        # Test URL with custom base
        client.base_url = 'https://custom.upid.io'
        url = client._build_url('/custom')
        assert url == 'https://custom.upid.io/v1/custom'

    @pytest.mark.unit
    def test_handle_response_success(self, mock_config, mock_auth_manager):
        """Test successful response handling"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        
        # Test response handling
        result = client._handle_response(mock_response)
        assert result == {'data': 'test'}

    @pytest.mark.unit
    def test_handle_response_error(self, mock_config, mock_auth_manager):
        """Test error response handling"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_response.raise_for_status.side_effect = HTTPError("400 Client Error")
        
        # Test error handling
        with pytest.raises(HTTPError, match="400 Client Error"):
            client._handle_response(mock_response)

    @pytest.mark.unit
    def test_handle_response_json_error(self, mock_config, mock_auth_manager):
        """Test response handling with JSON decode error"""
        client = UPIDAPIClient(mock_config, mock_auth_manager)
        
        # Mock response with JSON error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        # Test JSON error handling
        with pytest.raises(Exception, match="Invalid JSON response"):
            client._handle_response(mock_response) 