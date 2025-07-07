"""
API client for UPID platform
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from .config import Config
from .auth import AuthManager

class UPIDAPIClient:
    """UPID API Client for interacting with the UPID platform"""
    
    def __init__(self, config: Config, auth_manager: AuthManager):
        self.config = config
        self.auth_manager = auth_manager
        self.session = requests.Session()
        self.timeout = self.config.get('timeout', 30)
        self.session.timeout = self.timeout
        self.base_url = self.config.get('api_url')
        self.api_version = self.config.get('api_version', 'v1')
        self.local_mode = self.config.get('local_mode', False)

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith('http'):
            return endpoint
        # Only add /v1 if not already present
        if endpoint.startswith(f'/{self.api_version}'):
            return f"{self.base_url.rstrip('/')}{endpoint}"
        if endpoint.startswith('/api/'):
            return f"{self.base_url.rstrip('/')}{endpoint}"
        return f"{self.base_url.rstrip('/')}/{self.api_version}{endpoint}"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'UPID-CLI/1.0.0'
        }
        
        # Skip authentication in local mode
        if self.local_mode:
            return headers
            
        token = self.auth_manager.get_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            if response.content:
                try:
                    return response.json()
                except Exception:
                    raise Exception('Invalid JSON response')
            return None
        except requests.exceptions.HTTPError as e:
            raise e

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        headers = self._get_headers()
        try:
            response = self.session.get(url, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            raise Exception(f'Request failed: {e}')
        return self._handle_response(response)

    def _post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        headers = self._get_headers()
        try:
            payload = json if json is not None else data
            response = self.session.post(url, headers=headers, json=payload)
        except requests.exceptions.RequestException as e:
            raise Exception(f'Request failed: {e}')
        return self._handle_response(response)

    def _put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        headers = self._get_headers()
        try:
            payload = json if json is not None else data
            response = self.session.put(url, headers=headers, json=payload)
        except requests.exceptions.RequestException as e:
            raise Exception(f'Request failed: {e}')
        return self._handle_response(response)

    def _delete(self, endpoint: str) -> Any:
        url = self._build_url(endpoint)
        headers = self._get_headers()
        try:
            response = self.session.delete(url, headers=headers)
        except requests.exceptions.RequestException as e:
            raise Exception(f'Request failed: {e}')
        return self._handle_response(response)

    # Local mode methods for testing
    def _get_local_clusters(self) -> List[Dict[str, Any]]:
        """Get local clusters for testing"""
        return [
            {
                'cluster_id': 'local-cluster',
                'name': 'Local Kubernetes Cluster',
                'region': 'local',
                'status': 'healthy',
                'nodes_count': 1,
                'pods_count': 5,
                'created_at': '2024-01-01T00:00:00Z',
                'platform': 'local'
            }
        ]
    
    def _get_local_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """Get local cluster details"""
        return {
            'cluster_id': cluster_id,
            'name': 'Local Kubernetes Cluster',
            'region': 'local',
            'status': 'healthy',
            'nodes_count': 1,
            'pods_count': 5,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
            'platform': 'local',
            'version': '1.24.0',
            'cost': 0.0
        }
    
    def _get_local_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Get local analysis data for testing"""
        if analysis_type == 'resources':
            return {
                'cpu': {'used': 2.5, 'total': 4.0},
                'memory': {'used': 4.0, 'total': 8.0},
                'storage': {'used': 20.0, 'total': 100.0},
                'nodes': [
                    {
                        'name': 'local-node',
                        'cpu_used': 2.5, 'cpu_total': 4.0,
                        'memory_used': 4.0, 'memory_total': 8.0,
                        'storage_used': 20.0, 'storage_total': 100.0,
                        'status': 'ready'
                    }
                ],
                'pods': [
                    {
                        'name': 'nginx-pod',
                        'namespace': 'default',
                        'cpu_used': 0.1,
                        'memory_used': 0.5,
                        'status': 'running'
                    }
                ]
            }
        elif analysis_type == 'costs':
            return {
                'total_cost': 0.0,
                'infrastructure': {'cost': 0.0, 'trend': 'stable'},
                'compute': {'cost': 0.0, 'trend': 'stable'},
                'storage': {'cost': 0.0, 'trend': 'stable'},
                'network': {'cost': 0.0, 'trend': 'stable'},
                'total_trend': 'stable',
                'recommendations': []
            }
        elif analysis_type == 'performance':
            return {
                'cpu': {'current': 62.5, 'average': 50.0, 'peak': 80.0},
                'memory': {'current': 50.0, 'average': 45.0, 'peak': 70.0},
                'network': {'current': 10.0, 'average': 8.0, 'peak': 25.0},
                'storage': {'current': 20.0, 'average': 18.0, 'peak': 30.0},
                'recommendations': []
            }
        return {}

    # Authentication methods
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to UPID platform"""
        if self.local_mode:
            return {'token': 'local-token', 'user': {'name': 'Local User', 'email': email}}
        
        data = {'email': email, 'password': password}
        response = self._post('/auth/login', json=data)
        if 'token' in response:
            self.auth_manager.set_token(response['token'])
        return response
    
    def logout(self) -> Dict[str, Any]:
        """Logout from UPID platform"""
        if self.local_mode:
            return {'message': 'Logged out from local mode'}
        
        response = self._post('/auth/logout')
        self.auth_manager.clear_token()
        return response
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        if self.local_mode:
            return {'name': 'Local User', 'email': 'local@example.com', 'organization': 'Local'}
        
        return self._get('/auth/profile')
    
    def refresh_token(self) -> Dict[str, Any]:
        """Refresh authentication token"""
        if self.local_mode:
            return {'token': 'local-token-refreshed'}
        
        return self._post('/auth/refresh')

    # Cluster management methods
    def get_clusters(self) -> List[Dict[str, Any]]:
        """Get list of clusters"""
        if self.local_mode:
            return self._get_local_clusters()
        
        return self._get('/clusters')
    
    def get_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Get cluster information"""
        if self.local_mode:
            return self._get_local_cluster(cluster_name)
        
        return self._get(f'/clusters/{cluster_name}')
    
    def create_cluster(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new cluster"""
        if self.local_mode:
            return {
                'cluster_id': 'local-cluster-new',
                'name': cluster_data.get('name', 'Local Cluster'),
                'status': 'creating',
                'message': 'Local cluster creation simulated'
            }
        
        return self._post('/clusters', json=cluster_data)
    
    def delete_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Delete a cluster"""
        if self.local_mode:
            return {'message': f'Local cluster {cluster_name} deletion simulated'}
        
        return self._delete(f'/clusters/{cluster_name}')
    
    def get_cluster_info(self, cluster_name: str) -> Dict[str, Any]:
        """Get cluster information"""
        if self.local_mode:
            return self._get_local_cluster(cluster_name)
        
        return self._get(f'/clusters/{cluster_name}')
    
    def analyze_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Analyze cluster resources"""
        if self.local_mode:
            return self._get_local_analysis('resources')
        
        return self._post(f'/clusters/{cluster_name}/analyze')
    
    def optimize_cluster(self, cluster_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize cluster resources"""
        if self.local_mode:
            return {
                'optimizations': [],
                'savings': 0.0,
                'message': 'Local optimization simulated'
            }
        
        return self._post(f'/clusters/{cluster_name}/optimize', json=options)
    
    def get_optimization_result(self, optimization_id: str) -> Dict[str, Any]:
        """Get optimization result"""
        if self.local_mode:
            return {'status': 'completed', 'result': 'Local optimization completed'}
        
        return self._get(f'/optimizations/{optimization_id}')
    
    def deploy_optimization(self, cluster_name: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy optimization to cluster"""
        if self.local_mode:
            return {'status': 'deployed', 'message': 'Local deployment simulated'}
        
        return self._post(f'/clusters/{cluster_name}/deploy', json=deployment_data)
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status"""
        if self.local_mode:
            return {'status': 'ready', 'message': 'Local deployment ready'}
        
        return self._get(f'/deployments/{deployment_id}')
    
    def deploy_optimizations(self, cluster_name: str, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deploy optimizations to cluster"""
        if self.local_mode:
            return {'status': 'deployed', 'message': 'Local optimizations deployed'}
        
        return self._post(f'/clusters/{cluster_name}/deploy', data={'optimizations': optimizations})
    
    def get_zero_pod_recommendations(self, cluster_name: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get zero-pod scaling recommendations"""
        if self.local_mode:
            return [
                {
                    'namespace': 'default',
                    'deployment': 'nginx-deployment',
                    'current_replicas': 3,
                    'idle_time': '2h',
                    'savings': 0.0,
                    'risk_level': 'low'
                }
            ]
        
        params = {'namespace': namespace} if namespace else None
        return self._get(f'/clusters/{cluster_name}/zero-pod-recommendations', params=params)
    
    def get_cost_analysis(self, cluster_name: str) -> Dict[str, Any]:
        """Get cost analysis for cluster"""
        if self.local_mode:
            return self._get_local_analysis('costs')
        
        return self._get(f'/clusters/{cluster_name}/cost')
    
    def get_optimization_history(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Get optimization history for cluster"""
        if self.local_mode:
            return [
                {
                    'id': 'local-opt-1',
                    'type': 'resource',
                    'timestamp': '2024-01-01T00:00:00Z',
                    'savings': 0.0
                }
            ]
        
        return self._get(f'/clusters/{cluster_name}/optimization-history')
    
    def get_report(self, cluster_name: str, report_type: str = 'summary') -> Dict[str, Any]:
        """Get cluster report"""
        if self.local_mode:
            return {
                'cluster_name': cluster_name,
                'report_type': report_type,
                'generated_at': '2024-01-01T00:00:00Z',
                'data': self._get_local_analysis('resources')
            }
        
        return self._get(f'/clusters/{cluster_name}/report', params={'type': report_type})
    
    # Analysis Methods
    def analyze_resources(self, cluster_id: str) -> Dict[str, Any]:
        """Analyze cluster resources"""
        if self.local_mode:
            return self._get_local_analysis('resources')
        
        return self._get(f'/clusters/{cluster_id}/analysis/resources')
    
    def analyze_costs(self, cluster_id: str, period: str = '30d') -> Dict[str, Any]:
        """Analyze cluster costs"""
        if self.local_mode:
            return self._get_local_analysis('costs')
        
        return self._get(f'/clusters/{cluster_id}/analysis/costs', params={'period': period})
    
    def analyze_performance(self, cluster_id: str) -> Dict[str, Any]:
        """Analyze cluster performance"""
        if self.local_mode:
            return self._get_local_analysis('performance')
        
        return self._get(f'/clusters/{cluster_id}/analysis/performance')
    
    # Optimization Methods
    def get_resource_optimizations(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Get resource optimization recommendations"""
        if self.local_mode:
            return [
                {
                    'type': 'cpu',
                    'resource': 'CPU allocation',
                    'current_value': '4 cores',
                    'recommended_value': '2 cores',
                    'savings': 0.0,
                    'impact': 'low'
                }
            ]
        
        return self._get(f'/clusters/{cluster_id}/optimizations/resources')
    
    def apply_resource_optimizations(self, cluster_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply resource optimizations"""
        if self.local_mode:
            return {
                'applied_count': len(recommendations),
                'actual_savings': 0.0,
                'message': 'Local optimizations applied'
            }
        
        return self._post(f'/clusters/{cluster_id}/optimizations/resources', json={'recommendations': recommendations})
    
    def get_cost_optimizations(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        if self.local_mode:
            return [
                {
                    'category': 'compute',
                    'action': 'Scale down instances',
                    'current_cost': 0.0,
                    'optimized_cost': 0.0,
                    'savings': 0.0,
                    'priority': 'low'
                }
            ]
        
        return self._get(f'/clusters/{cluster_id}/optimizations/costs')
    
    def apply_cost_optimizations(self, cluster_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply cost optimizations"""
        if self.local_mode:
            return {
                'applied_count': len(recommendations),
                'actual_savings': 0.0,
                'message': 'Local cost optimizations applied'
            }
        
        return self._post(f'/clusters/{cluster_id}/optimizations/costs', json={'recommendations': recommendations})
    
    def apply_zero_pod_optimizations(self, cluster_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply zero-pod scaling optimizations"""
        if self.local_mode:
            return {
                'applied_count': len(recommendations),
                'actual_savings': 0.0,
                'message': 'Local zero-pod optimizations applied'
            }
        
        return self._post(f'/clusters/{cluster_id}/optimizations/zero-pod', json={'recommendations': recommendations})
    
    def enable_auto_optimization(self, cluster_id: str, schedule: Optional[str] = None) -> Dict[str, Any]:
        """Enable automatic optimization"""
        if self.local_mode:
            return {
                'schedule': schedule or 'default',
                'next_run': '2024-01-02T02:00:00Z',
                'message': 'Local auto optimization enabled'
            }
        
        data = {'enabled': True}
        if schedule:
            data['schedule'] = schedule
        return self._post(f'/clusters/{cluster_id}/optimizations/auto', json=data)
    
    def disable_auto_optimization(self, cluster_id: str) -> Dict[str, Any]:
        """Disable automatic optimization"""
        if self.local_mode:
            return {'message': 'Local auto optimization disabled'}
        
        return self._post(f'/clusters/{cluster_id}/optimizations/auto', json={'enabled': False})
    
    # Deployment Methods
    def create_deployment(self, cluster_id: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deployment"""
        if self.local_mode:
            return {
                'name': deployment_data.get('name', 'local-deployment'),
                'namespace': deployment_data.get('namespace', 'default'),
                'replicas': deployment_data.get('replicas', 1),
                'status': 'creating',
                'message': 'Local deployment created'
            }
        
        return self._post(f'/clusters/{cluster_id}/deployments', json=deployment_data)
    
    def get_deployments(self, cluster_id: str, namespace: str = 'default') -> List[Dict[str, Any]]:
        """Get deployments in a namespace"""
        if self.local_mode:
            return [
                {
                    'name': 'nginx-deployment',
                    'replicas': 3,
                    'available': 3,
                    'status': 'ready',
                    'age': '1h'
                }
            ]
        
        return self._get(f'/clusters/{cluster_id}/deployments', params={'namespace': namespace})
    
    def get_deployment(self, cluster_id: str, deployment_name: str, namespace: str = 'default') -> Dict[str, Any]:
        """Get deployment details"""
        if self.local_mode:
            return {
                'name': deployment_name,
                'namespace': namespace,
                'replicas': 3,
                'available': 3,
                'status': 'ready',
                'image': 'nginx:latest',
                'port': 80,
                'age': '1h',
                'environment': {}
            }
        
        return self._get(f'/clusters/{cluster_id}/deployments/{deployment_name}', params={'namespace': namespace})
    
    def scale_deployment(self, cluster_id: str, deployment_name: str, namespace: str, replicas: int) -> Dict[str, Any]:
        """Scale a deployment"""
        if self.local_mode:
            return {
                'name': deployment_name,
                'replicas': replicas,
                'status': 'scaling',
                'message': 'Local deployment scaled'
            }
        
        return self._post(f'/clusters/{cluster_id}/deployments/{deployment_name}/scale', 
                         json={'replicas': replicas}, params={'namespace': namespace})
    
    def delete_deployment(self, cluster_id: str, deployment_name: str, namespace: str = 'default') -> None:
        """Delete a deployment"""
        if self.local_mode:
            return  # Local deletion simulated
        
        self._delete(f'/clusters/{cluster_id}/deployments/{deployment_name}', params={'namespace': namespace})
    
    # Reporting Methods
    def generate_summary_report(self, cluster_id: str, period: str = '30d') -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        if self.local_mode:
            return {
                'cluster_name': cluster_id,
                'generated_at': '2024-01-01T00:00:00Z',
                'resources': self._get_local_analysis('resources'),
                'costs': self._get_local_analysis('costs'),
                'performance': self._get_local_analysis('performance'),
                'recommendations': []
            }
        
        return self._get(f'/clusters/{cluster_id}/reports/summary', params={'period': period})
    
    def generate_cost_report(self, cluster_id: str, period: str = '30d') -> Dict[str, Any]:
        """Generate detailed cost report"""
        if self.local_mode:
            return {
                'cluster_name': cluster_id,
                'total_cost': 0.0,
                'services': {},
                'optimization_opportunities': []
            }
        
        return self._get(f'/clusters/{cluster_id}/reports/cost', params={'period': period})
    
    def generate_performance_report(self, cluster_id: str, period: str = '30d') -> Dict[str, Any]:
        """Generate detailed performance report"""
        if self.local_mode:
            return {
                'cluster_name': cluster_id,
                'metrics': self._get_local_analysis('performance'),
                'issues': []
            }
        
        return self._get(f'/clusters/{cluster_id}/reports/performance', params={'period': period})
    
    # User Management Methods
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        if self.local_mode:
            return {
                'name': 'Local User',
                'email': 'local@example.com',
                'organization': 'Local',
                'roles': ['admin'],
                'permissions': ['read', 'write']
            }
        
        return self._get('/user/profile')
    
    def refresh_token(self) -> str:
        """Refresh authentication token"""
        if self.local_mode:
            return 'local-token-refreshed'
        
        response = self._post('/auth/refresh')
        return response.get('token', '')
    
    def logout(self) -> Dict[str, Any]:
        """Logout user"""
        if self.local_mode:
            return {'message': 'Logged out from local mode'}
        
        return self._post('/auth/logout')

