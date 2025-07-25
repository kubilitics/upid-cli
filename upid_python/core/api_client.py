"""
API client for UPID CLI
Handles all API communication with retry logic and error handling
Supports both real API and mock mode for demonstrations
"""

import json
import time
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import Config
from .auth import AuthManager
from .mock_api import mock_api_call, MockAPIResponse


@dataclass
class APIResponse:
    """API response wrapper"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    success: bool
    error_message: Optional[str] = None


class UPIDAPIClient:
    """API client for UPID CLI"""
    
    def __init__(self, config: Config, auth_manager: AuthManager):
        self.config = config
        self.auth_manager = auth_manager
        self.session = self._create_session()
        self.mock_mode = self._is_mock_mode()
    
    def _is_mock_mode(self) -> bool:
        """Check if mock mode is enabled"""
        # Check environment variable
        import os
        if os.getenv('UPID_MOCK_MODE', '').lower() in ['true', '1', 'yes']:
            return True
        
        # Check config setting
        if hasattr(self.config, 'mock_mode') and self.config.mock_mode:
            return True
        
        # Check if API URL is mock
        if self.config.api_url in ['mock://', 'mock://localhost', 'http://mock']:
            return True
        
        return False
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.api_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"UPID-CLI/2.0.0",
            "Accept": "application/json"
        }
        
        if include_auth:
            token = self.auth_manager.get_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        include_auth: bool = True
    ) -> APIResponse:
        """Make HTTP request with error handling"""
        
        # Use mock API if in mock mode
        if self.mock_mode:
            return self._make_mock_request(method, endpoint, data, params)
        
        try:
            url = f"{self.config.api_url}{endpoint}"
            headers = self._get_headers(include_auth)
            
            if self.config.debug:
                print(f"API Request: {method} {url}")
                if data:
                    print(f"Request Data: {json.dumps(data, indent=2)}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.config.api_timeout
            )
            
            if self.config.debug:
                print(f"API Response: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
            
            # Parse response
            try:
                response_data = response.json() if response.content else None
            except json.JSONDecodeError:
                response_data = response.text
            
            # Create APIResponse
            api_response = APIResponse(
                status_code=response.status_code,
                data=response_data,
                headers=dict(response.headers),
                success=response.status_code < 400,
                error_message=None if response.status_code < 400 else response_data.get('error', 'Unknown error') if isinstance(response_data, dict) else str(response_data)
            )
            
            return api_response
            
        except requests.exceptions.RequestException as e:
            return APIResponse(
                status_code=0,
                data=None,
                headers={},
                success=False,
                error_message=f"Request failed: {str(e)}"
            )
    
    def _make_mock_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> APIResponse:
        """Make mock API request"""
        if self.config.debug:
            print(f"Mock API Request: {method} {endpoint}")
            if data:
                print(f"Mock Request Data: {json.dumps(data, indent=2)}")
        
        # Call mock API
        mock_response = mock_api_call(endpoint, method, data, params)
        
        if self.config.debug:
            print(f"Mock API Response: {mock_response.status_code}")
            print(f"Mock Response Success: {mock_response.success}")
        
        # Convert MockAPIResponse to APIResponse
        api_response = APIResponse(
            status_code=mock_response.status_code,
            data=mock_response.data,
            headers={},  # Mock responses don't have headers
            success=mock_response.success,
            error_message=mock_response.error_message
        )
        
        return api_response
    
    # Authentication endpoints
    def login(self, email: str, password: str) -> APIResponse:
        """Login with email and password"""
        data = {"email": email, "password": password}
        if self.mock_mode:
            return self._make_mock_request("POST", "/api/v1/auth/login", data=data)
        return self._make_request("POST", "/auth/login", data=data, include_auth=False)
    
    def logout(self) -> APIResponse:
        """Logout current user"""
        return self._make_request("POST", "/auth/logout")
    
    def refresh_token(self, refresh_token: str) -> APIResponse:
        """Refresh authentication token"""
        data = {"refresh_token": refresh_token}
        return self._make_request("POST", "/auth/refresh", data=data, include_auth=False)
    
    def get_user_info(self) -> APIResponse:
        """Get current user information"""
        return self._make_request("GET", "/auth/user")
    
    def get_organizations(self) -> APIResponse:
        """Get user's organizations"""
        return self._make_request("GET", "/auth/organizations")
    
    def switch_organization(self, org_id: str) -> APIResponse:
        """Switch to a different organization"""
        return self._make_request("POST", f"/auth/organizations/{org_id}/switch")
    
    # Cluster management endpoints
    def list_clusters(self) -> APIResponse:
        """List all clusters"""
        if self.mock_mode:
            return self._make_mock_request("GET", "/api/v1/clusters")
        return self._make_request("GET", "/clusters")
    
    def get_cluster(self, cluster_id: str) -> APIResponse:
        """Get cluster details"""
        return self._make_request("GET", f"/clusters/{cluster_id}")
    
    def add_cluster(self, cluster_data: Dict) -> APIResponse:
        """Add a new cluster"""
        return self._make_request("POST", "/clusters", data=cluster_data)
    
    def update_cluster(self, cluster_id: str, cluster_data: Dict) -> APIResponse:
        """Update cluster configuration"""
        return self._make_request("PUT", f"/clusters/{cluster_id}", data=cluster_data)
    
    def delete_cluster(self, cluster_id: str) -> APIResponse:
        """Delete a cluster"""
        return self._make_request("DELETE", f"/clusters/{cluster_id}")
    
    def get_cluster_status(self, cluster_id: str) -> APIResponse:
        """Get cluster health status"""
        return self._make_request("GET", f"/clusters/{cluster_id}/status")
    
    # Analysis endpoints
    def analyze_cluster(self, cluster_id: str) -> APIResponse:
        """Analyze a specific cluster"""
        if self.mock_mode:
            return self._make_mock_request("POST", f"/api/v1/analyze/cluster/{cluster_id}")
        return self._make_request("GET", f"/clusters/{cluster_id}/analyze")
    
    def analyze_pod(self, cluster_id: str, pod_name: str, namespace: str = "default", params: Optional[Dict] = None) -> APIResponse:
        """Analyze specific pod"""
        data = {"pod_name": pod_name, "namespace": namespace}
        if params:
            data.update(params)
        return self._make_request("POST", f"/clusters/{cluster_id}/analyze/pod", data=data)
    
    def find_idle_workloads(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Find idle workloads using ML analysis"""
        if self.mock_mode:
            return self._make_mock_request("POST", f"/api/v1/analyze/idle/{cluster_id}", data=params)
        return self._make_request("POST", f"/clusters/{cluster_id}/analyze/idle", params=params)
    
    def analyze_resources(self, cluster_id: str, resource_type: str = "all", params: Optional[Dict] = None) -> APIResponse:
        """Analyze resource usage"""
        data = {"resource_type": resource_type}
        if params:
            data.update(params)
        return self._make_request("POST", f"/clusters/{cluster_id}/analyze/resources", data=data)
    
    def analyze_costs(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Analyze cluster costs"""
        if self.mock_mode:
            return self._make_mock_request("POST", f"/api/v1/analyze/costs/{cluster_id}", data=params)
        return self._make_request("POST", f"/clusters/{cluster_id}/analyze/costs", params=params)
    
    def analyze_performance(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Analyze cluster performance"""
        return self._make_request("POST", f"/clusters/{cluster_id}/analyze/performance", params=params)
    
    # Optimization endpoints
    def get_optimization_strategies(self, cluster_id: str) -> APIResponse:
        """Get available optimization strategies"""
        if self.mock_mode:
            return self._make_mock_request("GET", f"/api/v1/optimize/strategies/{cluster_id}")
        return self._make_request("GET", f"/clusters/{cluster_id}/optimization/strategies")
    
    def simulate_optimization(self, cluster_id: str, strategy: str, params: Optional[Dict] = None) -> APIResponse:
        """Simulate optimization without applying changes"""
        data = {"strategy": strategy}
        if params:
            data.update(params)
        return self._make_request("POST", f"/clusters/{cluster_id}/optimization/simulate", data=data)
    
    def apply_optimization(self, cluster_id: str, optimization_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Apply optimization changes"""
        data = {"optimization_id": optimization_id}
        if params:
            data.update(params)
        return self._make_request("POST", f"/clusters/{cluster_id}/optimization/apply", data=data)
    
    def auto_optimize(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Automatically optimize cluster"""
        return self._make_request("POST", f"/clusters/{cluster_id}/optimization/auto", params=params)
    
    def get_optimization_history(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Get optimization history"""
        return self._make_request("GET", f"/clusters/{cluster_id}/optimization/history", params=params)
    
    # Monitoring endpoints
    def start_monitoring(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Start cluster monitoring"""
        return self._make_request("POST", f"/clusters/{cluster_id}/monitoring/start", params=params)
    
    def stop_monitoring(self, cluster_id: str) -> APIResponse:
        """Stop cluster monitoring"""
        return self._make_request("POST", f"/clusters/{cluster_id}/monitoring/stop")
    
    def get_monitoring_status(self, cluster_id: str) -> APIResponse:
        """Get monitoring status"""
        return self._make_request("GET", f"/clusters/{cluster_id}/monitoring/status")
    
    def get_alerts(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Get monitoring alerts"""
        return self._make_request("GET", f"/clusters/{cluster_id}/monitoring/alerts", params=params)
    
    def get_metrics(self, cluster_id: str, hours: int = 24) -> APIResponse:
        """Get metrics for a cluster"""
        params = {"hours": hours}
        if self.mock_mode:
            return self._make_mock_request("GET", f"/api/v1/metrics/{cluster_id}", params=params)
        return self._make_request("GET", f"/clusters/{cluster_id}/metrics", params=params)
    
    # Reporting endpoints
    def generate_report(self, cluster_id: str, report_type: str, params: Optional[Dict] = None) -> APIResponse:
        """Generate cluster report"""
        data = {"report_type": report_type}
        if params:
            data.update(params)
        if self.mock_mode:
            return self._make_mock_request("POST", f"/api/v1/reports/{cluster_id}", data=data)
        return self._make_request("POST", f"/clusters/{cluster_id}/reports", data=data)
    
    def get_reports(self, cluster_id: str) -> APIResponse:
        """Get reports for a cluster"""
        if self.mock_mode:
            return self._make_mock_request("GET", f"/clusters/{cluster_id}/reports")
        return self._make_request("GET", f"/clusters/{cluster_id}/reports")
    
    def get_report(self, cluster_id: str, report_id: str) -> APIResponse:
        """Get specific report"""
        return self._make_request("GET", f"/clusters/{cluster_id}/reports/{report_id}")
    
    def export_report(self, cluster_id: str, report_id: str, format: str = "pdf") -> APIResponse:
        """Export report in specified format"""
        params = {"format": format}
        return self._make_request("GET", f"/clusters/{cluster_id}/reports/{report_id}/export", params=params)
    
    # AI/ML endpoints
    def get_ai_insights(self, cluster_id: str) -> APIResponse:
        """Get AI-powered insights for a cluster"""
        if self.mock_mode:
            return self._make_mock_request("GET", f"/api/v1/ai/insights/{cluster_id}")
        return self._make_request("GET", f"/clusters/{cluster_id}/ai-insights")
    
    def predict_scaling(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Predict scaling needs"""
        return self._make_request("POST", f"/clusters/{cluster_id}/ai/predict/scaling", params=params)
    
    def predict_costs(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Predict future costs"""
        return self._make_request("POST", f"/clusters/{cluster_id}/ai/predict/costs", params=params)
    
    def detect_anomalies(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Detect anomalies in cluster"""
        return self._make_request("POST", f"/clusters/{cluster_id}/ai/anomalies", params=params)
    
    # Enterprise endpoints
    def sync_enterprise_data(self, cluster_id: str, params: Optional[Dict] = None) -> APIResponse:
        """Sync enterprise data"""
        return self._make_request("POST", f"/clusters/{cluster_id}/enterprise/sync", params=params)
    
    def get_enterprise_status(self, cluster_id: str) -> APIResponse:
        """Get enterprise integration status"""
        return self._make_request("GET", f"/clusters/{cluster_id}/enterprise/status")
    
    def get_enterprise_policies(self, cluster_id: str) -> APIResponse:
        """Get enterprise policies"""
        return self._make_request("GET", f"/clusters/{cluster_id}/enterprise/policies")
    
    def apply_enterprise_policy(self, cluster_id: str, policy_id: str) -> APIResponse:
        """Apply enterprise policy"""
        return self._make_request("POST", f"/clusters/{cluster_id}/enterprise/policies/{policy_id}/apply")
    
    # System endpoints
    def get_system_health(self) -> APIResponse:
        """Get system health status"""
        return self._make_request("GET", "/system/health")
    
    def get_system_metrics(self) -> APIResponse:
        """Get system metrics"""
        return self._make_request("GET", "/system/metrics")
    
    def get_api_status(self) -> APIResponse:
        """Get API status"""
        return self._make_request("GET", "/system/api/status")
    
    def get_version(self) -> APIResponse:
        """Get API version"""
        return self._make_request("GET", "/system/version")
    
    # Utility methods
    def handle_response(self, response: APIResponse) -> bool:
        """Handle API response and return success status"""
        if not response.success:
            if self.config.debug:
                print(f"API Error: {response.error_message}")
            return False
        return True
    
    def format_response(self, response: APIResponse, output_format: str = None) -> str:
        """Format API response for output"""
        if not response.success:
            return f"Error: {response.error_message}"
        
        if output_format is None:
            output_format = self.config.output_format
        
        if output_format == "json":
            return json.dumps(response.data, indent=2)
        elif output_format == "yaml":
            import yaml
            return yaml.dump(response.data, default_flow_style=False)
        elif output_format == "csv":
            # Simple CSV conversion for tabular data
            if isinstance(response.data, list) and response.data:
                headers = list(response.data[0].keys())
                csv_lines = [",".join(headers)]
                for row in response.data:
                    csv_lines.append(",".join(str(row.get(h, "")) for h in headers))
                return "\n".join(csv_lines)
            else:
                return str(response.data)
        else:  # table format
            # Simple table formatting
            if isinstance(response.data, list) and response.data:
                headers = list(response.data[0].keys())
                table_lines = [" | ".join(headers)]
                table_lines.append("-" * len(table_lines[0]))
                for row in response.data:
                    table_lines.append(" | ".join(str(row.get(h, "")) for h in headers))
                return "\n".join(table_lines)
            else:
                return str(response.data) 