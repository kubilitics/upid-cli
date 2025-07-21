"""
Unit tests for Phase 0: Robust Foundations & Real Data Collection
Tests all core components: PodLogCollector, KubernetesMetricsCollector, RealTimeAnalyzer
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from upid.core.metrics_collector import PodLogCollector, KubernetesMetricsCollector, RealTimeAnalyzer

pytest_plugins = ["pytest_asyncio"]


class TestPodLogCollector:
    """Test PodLogCollector functionality"""
    
    def setup_method(self):
        self.collector = PodLogCollector()
    
    def test_init(self):
        """Test PodLogCollector initialization"""
        collector = PodLogCollector(kubeconfig="/path/to/config", context="test-context")
        assert collector.kubeconfig == "/path/to/config"
        assert collector.context == "test-context"
    
    def test_kubectl_logs_cmd(self):
        """Test kubectl command generation"""
        cmd = self.collector._kubectl_logs_cmd("test-pod", "test-namespace", 500, "1h", True)
        expected = ["kubectl", "logs", "test-pod", "-n", "test-namespace", "--tail=500", "--timestamps=true", "--since=1h", "--follow"]
        assert cmd == expected
    
    @patch('subprocess.run')
    def test_collect_logs_success(self, mock_run):
        """Test successful log collection"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "2024-01-15T10:00:00Z GET /api/users HTTP/1.1 200\n"
        mock_run.return_value = mock_result
        
        result = self.collector.collect_logs("test-pod", "default", 100)
        assert result == "2024-01-15T10:00:00Z GET /api/users HTTP/1.1 200\n"
    
    @patch('subprocess.run')
    def test_collect_logs_error(self, mock_run):
        """Test log collection error handling"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Pod not found"
        mock_run.return_value = mock_result
        
        result = self.collector.collect_logs("test-pod", "default", 100)
        assert result == ""
    
    def test_detect_log_format(self):
        """Test log format detection"""
        json_lines = ['{"timestamp": "2024-01-15", "method": "GET"}']
        nginx_lines = ['2024-01-15 GET /api/users HTTP/1.1" 200']
        apache_lines = ['127.0.0.1 - - [15/Jan/2024:10:00:00] "GET /api/users HTTP/1.1" 200']
        
        assert self.collector._detect_log_format(json_lines) == "json"
        assert self.collector._detect_log_format(nginx_lines) == "nginx"
        assert self.collector._detect_log_format(apache_lines) == "apache"
        assert self.collector._detect_log_format(["random line"]) == "custom"
    
    def test_parse_json_log(self):
        """Test JSON log parsing"""
        json_line = '{"timestamp": "2024-01-15T10:00:00Z", "method": "GET", "path": "/api/users", "status": "200", "user_agent": "Mozilla/5.0", "source_ip": "192.168.1.1"}'
        result = self.collector._parse_json_log(json_line)
        
        assert result["timestamp"] == "2024-01-15T10:00:00Z"
        assert result["method"] == "GET"
        assert result["path"] == "/api/users"
        assert result["status"] == "200"
        assert result["user_agent"] == "Mozilla/5.0"
        assert result["source_ip"] == "192.168.1.1"
    
    def test_parse_nginx_log(self):
        """Test Nginx log parsing"""
        nginx_line = '2024-01-15 10:00:00 GET /api/users HTTP/1.1" 200 145ms "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'
        result = self.collector._parse_nginx_log(nginx_line)
        
        assert result["timestamp"] == "2024-01-15 10:00:00"
        assert result["method"] == "GET"
        assert result["path"] == "/api/users"
        assert result["status"] == "200"
        assert "Mozilla/5.0" in result["user_agent"]
    
    def test_parse_apache_log(self):
        """Test Apache log parsing"""
        apache_line = '192.168.1.1 - - [15/Jan/2024:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
        result = self.collector._parse_apache_log(apache_line)
        
        assert result["source_ip"] == "192.168.1.1"
        assert "15/Jan/2024:10:00:00" in result["timestamp"]
        assert result["method"] == "GET"
        assert result["path"] == "/api/users"
        assert result["status"] == "200"
        assert "Mozilla/5.0" in result["user_agent"]
    
    def test_filter_business_requests(self):
        """Test business request filtering"""
        entries = [
            {"method": "GET", "path": "/api/users", "user_agent": "Mozilla/5.0"},
            {"method": "GET", "path": "/health", "user_agent": "kube-probe"},
            {"method": "GET", "path": "/api/orders", "user_agent": "Mozilla/5.0"},
            {"method": "GET", "path": "/ping", "user_agent": "ELB-HealthChecker"}
        ]
        
        business_requests = self.collector.filter_business_requests(entries)
        assert len(business_requests) == 2
        assert business_requests[0]["path"] == "/api/users"
        assert business_requests[1]["path"] == "/api/orders"
    
    def test_is_business_request(self):
        """Test business request detection"""
        # Business requests
        assert self.collector._is_business_request({"path": "/api/users", "user_agent": "Mozilla/5.0"})
        assert self.collector._is_business_request({"path": "/checkout", "user_agent": "Chrome/91.0"})
        
        # Health checks
        assert not self.collector._is_business_request({"path": "/health", "user_agent": "kube-probe"})
        assert not self.collector._is_business_request({"path": "/ping", "user_agent": "ELB-HealthChecker"})
        assert not self.collector._is_business_request({"path": "/status", "user_agent": "GoogleHC"})
        
        # Internal IPs
        assert not self.collector._is_business_request({"path": "/api/users", "source_ip": "10.0.0.1"})


class TestKubernetesMetricsCollector:
    """Test KubernetesMetricsCollector functionality"""
    
    def setup_method(self):
        self.collector = KubernetesMetricsCollector()
    
    @patch('subprocess.run')
    def test_get_pod_metrics(self, mock_run):
        """Test pod metrics collection"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """
NAME                     CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)   
test-pod-1              100m         10%      128Mi           5%        
test-pod-2              200m         20%      256Mi           10%       
"""
        mock_run.return_value = mock_result
        
        metrics = self.collector.get_pod_metrics()
        assert len(metrics) == 2
        assert metrics[0]["NAME"] == "test-pod-1"
        assert metrics[0]["CPU(%)"] == "10%"
        assert metrics[0]["MEMORY(%)"] == "5%"
    
    @patch.object(KubernetesMetricsCollector, 'get_prometheus_metrics', return_value={"cpu_usage": [{"value": [None, "123.45"]}]})
    def test_get_prometheus_metrics(self, mock_get_prom):
        """Test Prometheus metrics collection (fully isolated)"""
        metrics = self.collector.get_prometheus_metrics()
        assert "cpu_usage" in metrics
        assert metrics["cpu_usage"][0]["value"][1] == "123.45"

    @patch.object(KubernetesMetricsCollector, 'get_cadvisor_metrics', return_value={"container_count": 1, "avg_cpu_per_container": 10.0, "avg_memory_per_container": 5.0})
    def test_get_cadvisor_metrics(self, mock_get_cad):
        """Test cAdvisor metrics collection (fully isolated)"""
        metrics = self.collector.get_cadvisor_metrics()
        assert "container_count" in metrics
        assert "avg_cpu_per_container" in metrics
        assert "avg_memory_per_container" in metrics
    
    def test_aggregate_metrics_with_fallback(self):
        """Test metrics aggregation with fallback logic"""
        all_metrics = {
            'kubectl': {
                'status': 'success',
                'pod_metrics': [
                    {'CPU(%)': '10%', 'MEMORY(%)': '5%'},
                    {'CPU(%)': '20%', 'MEMORY(%)': '10%'}
                ]
            },
            'prometheus': {'status': 'failed'},
            'cadvisor': {'status': 'failed'}
        }
        
        aggregated = self.collector._aggregate_metrics_with_fallback(all_metrics)
        
        assert aggregated['cpu_usage']['average'] == 15.0
        assert aggregated['cpu_usage']['source'] == 'kubectl'
        assert aggregated['memory_usage']['average'] == 7.5
        assert aggregated['memory_usage']['source'] == 'kubectl'
        assert aggregated['pod_count']['count'] == 2
        assert aggregated['pod_count']['source'] == 'kubectl'
    
    def test_test_connections(self):
        """Test connection testing"""
        with patch.object(self.collector, 'get_pod_metrics', return_value=[]):
            with patch.object(self.collector, 'get_prometheus_metrics', return_value={'cpu_usage': []}):
                with patch.object(self.collector, 'get_cadvisor_metrics', return_value={'container_count': 0}):
                    results = self.collector.test_connections()
                    
                    assert 'kubectl' in results
                    assert 'prometheus' in results
                    assert 'cadvisor' in results
                    assert 'custom_metrics' in results
                    assert 'overall_status' in results
                    assert 'test_timestamp' in results


class TestRealTimeAnalyzer:
    """Test RealTimeAnalyzer functionality"""
    
    def setup_method(self):
        self.analyzer = RealTimeAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_pod_batch(self):
        """Test batch analysis of a pod"""
        with patch.object(self.analyzer.log_collector, 'collect_logs', return_value=""):
            with patch.object(self.analyzer.log_collector, 'parse_logs', return_value=[]):
                with patch.object(self.analyzer.log_collector, 'filter_business_requests', return_value=[]):
                    with patch.object(self.analyzer.metrics_collector, 'collect_all_metrics', return_value={'aggregated': {}}):
                        result = await self.analyzer.analyze_pod_batch("test-pod", "default", "1h")
                        
                        assert result['pod_name'] == "test-pod"
                        assert result['namespace'] == "default"
                        assert result['analysis_type'] == "batch"
                        assert result['time_range'] == "1h"
                        assert 'log_analysis' in result
                        assert 'metrics_analysis' in result
                        assert 'business_impact' in result
    
    def test_analyze_request_patterns(self):
        """Test request pattern analysis"""
        business_requests = [
            {"method": "GET", "path": "/api/users", "status": "200", "user_agent": "Mozilla/5.0", "timestamp": "2024-01-15T10:00:00Z"},
            {"method": "POST", "path": "/api/orders", "status": "201", "user_agent": "Chrome/91.0", "timestamp": "2024-01-15T11:00:00Z"},
            {"method": "GET", "path": "/api/users", "status": "200", "user_agent": "Mozilla/5.0", "timestamp": "2024-01-15T12:00:00Z"}
        ]
        
        patterns = self.analyzer._analyze_request_patterns(business_requests)
        
        assert patterns['endpoints']['/api/users'] == 2
        assert patterns['endpoints']['/api/orders'] == 1
        assert patterns['methods']['GET'] == 2
        assert patterns['methods']['POST'] == 1
        assert patterns['status_codes']['200'] == 2
        assert patterns['status_codes']['201'] == 1
        assert patterns['user_agents']['Mozilla/5.0'] == 2
        assert patterns['user_agents']['Chrome/91.0'] == 1
        assert 10 in patterns['hourly_distribution']
        assert 11 in patterns['hourly_distribution']
        assert 12 in patterns['hourly_distribution']
    
    def test_calculate_business_impact(self):
        """Test business impact calculation"""
        log_analysis = {
            'business_request_ratio': 0.8,
            'total_requests': 100,
            'business_requests': 80
        }
        metrics_analysis = {
            'cpu_usage': {'average': 50.0, 'source': 'kubectl'},
            'memory_usage': {'average': 60.0, 'source': 'kubectl'}
        }
        
        impact = self.analyzer._calculate_business_impact(log_analysis, metrics_analysis)
        
        assert impact['efficiency_score'] > 0
        assert impact['business_request_ratio'] == 80.0
        assert 'cpu_efficiency' in impact['resource_efficiency']
        assert 'memory_efficiency' in impact['resource_efficiency']
        assert isinstance(impact['recommendations'], list)
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        # High non-business ratio
        recommendations = self.analyzer._generate_recommendations(0.05, 50.0, 60.0)
        assert any("health check frequency" in rec for rec in recommendations)
        
        # High CPU usage
        recommendations = self.analyzer._generate_recommendations(0.8, 85.0, 60.0)
        assert any("CPU usage" in rec for rec in recommendations)
        
        # High memory usage
        recommendations = self.analyzer._generate_recommendations(0.8, 50.0, 85.0)
        assert any("memory usage" in rec for rec in recommendations)
        
        # High efficiency
        recommendations = self.analyzer._generate_recommendations(0.95, 15.0, 15.0)
        assert any("right-sizing" in rec for rec in recommendations)


if __name__ == "__main__":
    pytest.main([__file__]) 