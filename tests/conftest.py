"""
Pytest configuration and fixtures for UPID CLI tests
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path
from upid_python.core.config import Config
from upid_python.core.auth import AuthManager
from upid_python.core.api_client import UPIDAPIClient

@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_config(temp_config_dir):
    """Create a mock config for testing"""
    config = Config()
    # Override config directory for tests
    config.config_dir = Path(temp_config_dir)
    config.config_file = config.config_dir / 'config.json'
    config.auth_file = config.config_dir / 'auth.json'
    return config

@pytest.fixture
def mock_auth_manager(mock_config):
    """Create a mock auth manager for testing"""
    auth_manager = AuthManager(mock_config)
    auth_manager.api_client = Mock(spec=UPIDAPIClient)
    return auth_manager

@pytest.fixture
def mock_api_client():
    """Create a mock API client for testing"""
    client = Mock(spec=UPIDAPIClient)
    return client

@pytest.fixture
def sample_cluster_data():
    """Sample cluster data for testing"""
    return {
        'cluster_id': 'test-cluster-123',
        'name': 'test-cluster',
        'region': 'us-west-2',
        'status': 'healthy',
        'nodes_count': 3,
        'pods_count': 50,
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }

@pytest.fixture
def sample_optimization_result():
    """Sample optimization result for testing"""
    return {
        'cluster_id': 'test-cluster-123',
        'potential_savings': 1500.0,
        'efficiency_score': 85.5,
        'performance_impact': 2.1,
        'zero_pod_opportunities': {
            'scalable_pods_count': 5,
            'total_potential_savings': 800.0,
            'idle_patterns': {
                'cluster_idle_percentage': 35.2,
                'avg_cluster_idle_duration': 45.5
            }
        },
        'recommendations': [
            {
                'title': 'Reduce CPU allocation',
                'description': 'CPU is over-provisioned',
                'savings': 500.0,
                'risk_level': 'low',
                'type': 'cpu_optimization'
            }
        ]
    }

@pytest.fixture
def sample_idle_analysis():
    """Sample idle analysis for testing"""
    return {
        'idle_opportunities': [
            {
                'pod_name': 'test-pod-1',
                'namespace': 'default',
                'idle_percentage': 75.5,
                'avg_idle_duration': 120.0,
                'idle_pattern': 'predictable',
                'can_scale_to_zero': True,
                'potential_savings': 200.0,
                'recommended_scale_down_time': 300,
                'scale_up_conditions': {
                    'cpu_threshold': 0.1,
                    'memory_threshold': 0.1,
                    'request_threshold': 1,
                    'network_threshold': 1000
                }
            }
        ],
        'total_potential_savings': 800.0,
        'scalable_pods_count': 5,
        'idle_patterns': {
            'cluster_idle_percentage': 35.2,
            'avg_cluster_idle_duration': 45.5,
            'total_idle_periods': 25,
            'total_pods_analyzed': 50
        }
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'email': 'test@example.com',
        'name': 'Test User',
        'organization': 'Test Corp',
        'roles': ['user', 'admin'],
        'permissions': ['read', 'write', 'optimize']
    }

@pytest.fixture
def mock_kubeconfig():
    """Sample kubeconfig for testing"""
    return """
apiVersion: v1
kind: Config
clusters:
- name: test-cluster
  cluster:
    server: https://test-cluster.example.com
    certificate-authority-data: test-ca-data
contexts:
- name: test-context
  context:
    cluster: test-cluster
    user: test-user
current-context: test-context
users:
- name: test-user
  user:
    token: test-token
"""

@pytest.fixture
def mock_metrics_data():
    """Sample metrics data for testing"""
    return {
        'cpu_utilization': [45.2, 52.1, 38.9, 61.3, 49.7],
        'memory_utilization': [67.8, 71.2, 65.4, 73.1, 69.5],
        'network_throughput': 1024000,  # 1MB/s
        'storage_io': 1500,  # IOPS
        'pods': [
            {
                'name': 'test-pod-1',
                'namespace': 'default',
                'cpu_usage': [10.2, 12.5, 8.9, 15.3, 11.7],
                'memory_usage': [256, 512, 128, 1024, 512],
                'http_requests': [100, 150, 50, 200, 120],
                'network_io': [1024, 2048, 512, 4096, 1536],
                'resource_allocation': {
                    'cpu_request': 0.5,
                    'memory_request': 512
                },
                'replicas': 2
            }
        ]
    }

@pytest.fixture
def mock_cost_data():
    """Sample cost data for testing"""
    return {
        'total_cost': 2500.0,
        'breakdown': {
            'compute': 1800.0,
            'storage': 400.0,
            'network': 300.0
        },
        'optimization_potential': 800.0,
        'trends': [
            {'period': 'Jan', 'cost': 2400.0, 'change': 4.2},
            {'period': 'Feb', 'cost': 2500.0, 'change': 4.2},
            {'period': 'Mar', 'cost': 2450.0, 'change': -2.0}
        ]
    }

@pytest.fixture
def mock_deployment_data():
    """Sample deployment data for testing"""
    return {
        'deployment_id': 'deploy-123',
        'deployment_type': 'optimization',
        'status': 'completed',
        'created_at': '2024-01-01T10:00:00Z',
        'savings': 500.0,
        'progress': {
            'completed': 10,
            'total': 10,
            'percentage': 100
        }
    }

@pytest.fixture
def mock_report_data():
    """Sample report data for testing"""
    return {
        'executive_summary': {
            'total_cost': 2500.0,
            'potential_savings': 800.0,
            'efficiency_score': 85.5,
            'security_score': 92.0
        },
        'key_findings': [
            {
                'description': 'High CPU utilization during peak hours',
                'impact': 'Performance bottleneck',
                'recommendation': 'Scale up CPU resources'
            }
        ],
        'cost_analysis': {
            'current_monthly_cost': 2500.0,
            'optimized_monthly_cost': 1700.0,
            'monthly_savings': 800.0,
            'annual_savings': 9600.0,
            'roi': 320.0
        },
        'zero_pod_analysis': {
            'scalable_pods_count': 5,
            'potential_savings': 300.0,
            'idle_time_percentage': 35.2
        },
        'recommendations': [
            {
                'title': 'Implement zero-pod scaling',
                'description': 'Scale idle pods to zero',
                'impact': 'High',
                'savings': 300.0,
                'priority': 'high'
            }
        ]
    }

@pytest.fixture(autouse=True)
def mock_rich_console():
    """Mock rich console to avoid output during tests"""
    # Temporarily disabled due to missing utils module
    yield Mock()

@pytest.fixture(autouse=True)
def mock_click_echo():
    """Mock click.echo to avoid output during tests"""
    with patch('click.echo') as mock_echo:
        yield mock_echo

@pytest.fixture
def mock_show_progress():
    """Mock show_progress to avoid progress bars during tests"""
    with patch('upid.core.utils.show_progress') as mock_progress:
        mock_progress.return_value.__enter__ = Mock()
        mock_progress.return_value.__exit__ = Mock()
        yield mock_progress

@pytest.fixture
def mock_confirm_action():
    """Mock confirm_action to return True by default"""
    with patch('upid.core.utils.confirm_action') as mock_confirm:
        mock_confirm.return_value = True
        yield mock_confirm

@pytest.fixture
def mock_prompt_input():
    """Mock prompt_input to return default values"""
    with patch('upid.core.utils.prompt_input') as mock_prompt:
        mock_prompt.return_value = 'test-value'
        yield mock_prompt

@pytest.fixture
def mock_prompt_choice():
    """Mock prompt_choice to return first choice"""
    with patch('upid.core.utils.prompt_choice') as mock_choice:
        mock_choice.return_value = 'test-choice'
        yield mock_choice

@pytest.fixture
def mock_validate_cluster_id():
    """Mock validate_cluster_id to return True"""
    with patch('upid.core.utils.validate_cluster_id') as mock_validate:
        mock_validate.return_value = True
        yield mock_validate

@pytest.fixture
def mock_validate_email():
    """Mock validate_email to return True"""
    with patch('upid.core.utils.validate_email') as mock_validate:
        mock_validate.return_value = True
        yield mock_validate

@pytest.fixture
def mock_validate_url():
    """Mock validate_url to return True"""
    with patch('upid.core.utils.validate_url') as mock_validate:
        mock_validate.return_value = True
        yield mock_validate

@pytest.fixture
def mock_read_kubeconfig():
    """Mock read_kubeconfig to return encoded config"""
    with patch('upid.core.utils.read_kubeconfig') as mock_read:
        mock_read.return_value = 'dGVzdC1rdWJlY29uZmln'
        yield mock_read

@pytest.fixture
def mock_validate_kubeconfig():
    """Mock validate_kubeconfig to return True"""
    with patch('upid.core.utils.validate_kubeconfig') as mock_validate:
        mock_validate.return_value = True
        yield mock_validate

@pytest.fixture
def mock_format_currency():
    """Mock format_currency to return formatted string"""
    with patch('upid.core.utils.format_currency') as mock_format:
        mock_format.return_value = '$1,500.00'
        yield mock_format

@pytest.fixture
def mock_format_percentage():
    """Mock format_percentage to return formatted string"""
    with patch('upid.core.utils.format_percentage') as mock_format:
        mock_format.return_value = '85.5%'
        yield mock_format

@pytest.fixture
def mock_format_duration():
    """Mock format_duration to return formatted string"""
    with patch('upid.core.utils.format_duration') as mock_format:
        mock_format.return_value = '2m 30s'
        yield mock_format

@pytest.fixture
def mock_format_bytes():
    """Mock format_bytes to return formatted string"""
    with patch('upid.core.utils.format_bytes') as mock_format:
        mock_format.return_value = '1.5 GB'
        yield mock_format

@pytest.fixture
def mock_print_success():
    """Mock print_success to avoid output during tests"""
    with patch('upid.core.utils.print_success') as mock_print:
        yield mock_print

@pytest.fixture
def mock_print_error():
    """Mock print_error to avoid output during tests"""
    with patch('upid.core.utils.print_error') as mock_print:
        yield mock_print

@pytest.fixture
def mock_print_info():
    """Mock print_info to avoid output during tests"""
    with patch('upid.core.utils.print_info') as mock_print:
        yield mock_print

@pytest.fixture
def mock_print_warning():
    """Mock print_warning to avoid output during tests"""
    with patch('upid.core.utils.print_warning') as mock_print:
        yield mock_print

@pytest.fixture
def mock_print_table():
    """Mock print_table to avoid output during tests"""
    with patch('upid.core.utils.print_table') as mock_print:
        yield mock_print

@pytest.fixture
def mock_print_json():
    """Mock print_json to avoid output during tests"""
    with patch('upid.core.utils.print_json') as mock_print:
        yield mock_print

@pytest.fixture
def mock_print_panel():
    """Mock print_panel to avoid output during tests"""
    with patch('upid.core.utils.print_panel') as mock_print:
        yield mock_print

@pytest.fixture
def mock_save_json_file():
    """Mock save_json_file to avoid file I/O during tests"""
    with patch('upid.core.utils.save_json_file') as mock_save:
        yield mock_save

@pytest.fixture
def mock_save_yaml_file():
    """Mock save_yaml_file to avoid file I/O during tests"""
    with patch('upid.core.utils.save_yaml_file') as mock_save:
        yield mock_save

@pytest.fixture
def mock_load_json_file():
    """Mock load_json_file to return test data"""
    with patch('upid.core.utils.load_json_file') as mock_load:
        mock_load.return_value = {'test': 'data'}
        yield mock_load

@pytest.fixture
def mock_load_yaml_file():
    """Mock load_yaml_file to return test data"""
    with patch('upid.core.utils.load_yaml_file') as mock_load:
        mock_load.return_value = {'test': 'data'}
        yield mock_load

@pytest.fixture
def mock_calculate_cost_savings():
    """Mock calculate_cost_savings to return test data"""
    with patch('upid.core.utils.calculate_cost_savings') as mock_calc:
        mock_calc.return_value = {
            'current_cost': 2500.0,
            'optimized_cost': 1700.0,
            'savings': 800.0,
            'savings_percentage': 32.0
        }
        yield mock_calc

@pytest.fixture
def mock_calculate_efficiency_score():
    """Mock calculate_efficiency_score to return test score"""
    with patch('upid.core.utils.calculate_efficiency_score') as mock_calc:
        mock_calc.return_value = 85.5
        yield mock_calc

@pytest.fixture
def mock_format_optimization_result():
    """Mock format_optimization_result to return formatted string"""
    with patch('upid.core.utils.format_optimization_result') as mock_format:
        mock_format.return_value = '💰 Potential Savings: $1,500.00\n📊 Efficiency Score: 85.5%'
        yield mock_format

@pytest.fixture
def mock_format_idle_analysis():
    """Mock format_idle_analysis to return formatted string"""
    with patch('upid.core.utils.format_idle_analysis') as mock_format:
        mock_format.return_value = '📦 Total Pods Analyzed: 50\n✅ Scalable to Zero: 5'
        yield mock_format 