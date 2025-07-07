"""
Deployment service for UPID CLI
"""

import yaml
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from ..core.config import Config
from ..core.utils import format_cost

class DeploymentService:
    """Service for deploying optimizations to Kubernetes"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
    
    def create_horizontal_pod_autoscaler(self, deployment_name: str, namespace: str, 
                                        min_replicas: int = 0, max_replicas: int = 10,
                                        target_cpu_percentage: int = 80) -> Dict[str, Any]:
        """Create HorizontalPodAutoscaler configuration"""
        hpa_config = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': f"{deployment_name}-hpa",
                'namespace': namespace,
                'labels': {
                    'app': deployment_name,
                    'managed-by': 'upid-cli'
                }
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': deployment_name
                },
                'minReplicas': min_replicas,
                'maxReplicas': max_replicas,
                'metrics': [
                    {
                        'type': 'Resource',
                        'resource': {
                            'name': 'cpu',
                            'target': {
                                'type': 'Utilization',
                                'averageUtilization': target_cpu_percentage
                            }
                        }
                    }
                ]
            }
        }
        
        return hpa_config
    
    def create_zero_pod_config(self, deployment_name: str, namespace: str,
                              idle_threshold: str = '30m') -> Dict[str, Any]:
        """Create zero-pod scaling configuration"""
        # This would create a custom resource or annotation-based configuration
        # for zero-pod scaling (like Knative or custom controllers)
        
        config = {
            'apiVersion': 'upid.io/v1alpha1',
            'kind': 'ZeroPodScaler',
            'metadata': {
                'name': f"{deployment_name}-zero-pod",
                'namespace': namespace,
                'labels': {
                    'app': deployment_name,
                    'managed-by': 'upid-cli'
                }
            },
            'spec': {
                'deploymentRef': {
                    'name': deployment_name,
                    'namespace': namespace
                },
                'idleThreshold': idle_threshold,
                'minReplicas': 0,
                'maxReplicas': 10,
                'scaleDownDelay': '5m',
                'scaleUpDelay': '1m'
            }
        }
        
        return config
    
    def create_resource_quota(self, namespace: str, cpu_limit: str = '4', 
                             memory_limit: str = '8Gi') -> Dict[str, Any]:
        """Create ResourceQuota configuration"""
        quota_config = {
            'apiVersion': 'v1',
            'kind': 'ResourceQuota',
            'metadata': {
                'name': f"{namespace}-quota",
                'namespace': namespace,
                'labels': {
                    'managed-by': 'upid-cli'
                }
            },
            'spec': {
                'hard': {
                    'requests.cpu': cpu_limit,
                    'requests.memory': memory_limit,
                    'limits.cpu': cpu_limit,
                    'limits.memory': memory_limit
                }
            }
        }
        
        return quota_config
    
    def create_limit_range(self, namespace: str, default_cpu: str = '100m',
                          default_memory: str = '128Mi') -> Dict[str, Any]:
        """Create LimitRange configuration"""
        limit_range_config = {
            'apiVersion': 'v1',
            'kind': 'LimitRange',
            'metadata': {
                'name': f"{namespace}-limits",
                'namespace': namespace,
                'labels': {
                    'managed-by': 'upid-cli'
                }
            },
            'spec': {
                'limits': [
                    {
                        'type': 'Container',
                        'default': {
                            'cpu': default_cpu,
                            'memory': default_memory
                        },
                        'defaultRequest': {
                            'cpu': default_cpu,
                            'memory': default_memory
                        }
                    }
                ]
            }
        }
        
        return limit_range_config
    
    def generate_deployment_manifest(self, optimizations: List[Dict[str, Any]], 
                                   cluster_name: str) -> List[Dict[str, Any]]:
        """Generate Kubernetes manifests for optimizations"""
        manifests = []
        
        for optimization in optimizations:
            opt_type = optimization.get('type', '')
            
            if opt_type == 'zero_pod_scaling':
                deployment_name = optimization.get('deployment', '')
                namespace = optimization.get('namespace', 'default')
                
                # Create HPA for zero-pod scaling
                hpa_config = self.create_horizontal_pod_autoscaler(
                    deployment_name, namespace, min_replicas=0, max_replicas=10
                )
                manifests.append(hpa_config)
                
                # Create zero-pod configuration
                zero_pod_config = self.create_zero_pod_config(deployment_name, namespace)
                manifests.append(zero_pod_config)
            
            elif opt_type == 'resource_quota':
                namespace = optimization.get('namespace', 'default')
                cpu_limit = optimization.get('cpu_limit', '4')
                memory_limit = optimization.get('memory_limit', '8Gi')
                
                quota_config = self.create_resource_quota(namespace, cpu_limit, memory_limit)
                manifests.append(quota_config)
            
            elif opt_type == 'limit_range':
                namespace = optimization.get('namespace', 'default')
                default_cpu = optimization.get('default_cpu', '100m')
                default_memory = optimization.get('default_memory', '128Mi')
                
                limit_range_config = self.create_limit_range(namespace, default_cpu, default_memory)
                manifests.append(limit_range_config)
        
        return manifests
    
    def save_manifests(self, manifests: List[Dict[str, Any]], output_dir: str = './upid-manifests') -> str:
        """Save manifests to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for i, manifest in enumerate(manifests):
            kind = manifest.get('kind', 'Unknown')
            name = manifest.get('metadata', {}).get('name', f'manifest-{i}')
            namespace = manifest.get('metadata', {}).get('namespace', 'default')
            
            filename = f"{namespace}-{name}-{kind.lower()}.yaml"
            filepath = output_path / filename
            
            with open(filepath, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False)
            
            saved_files.append(str(filepath))
        
        return output_dir
    
    def validate_manifests(self, manifests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate Kubernetes manifests"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for manifest in manifests:
            # Basic validation
            if 'apiVersion' not in manifest:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Missing apiVersion in {manifest.get('kind', 'Unknown')}")
            
            if 'kind' not in manifest:
                validation_results['valid'] = False
                validation_results['errors'].append("Missing kind in manifest")
            
            if 'metadata' not in manifest:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Missing metadata in {manifest.get('kind', 'Unknown')}")
            
            # Check for required fields based on kind
            kind = manifest.get('kind', '')
            if kind == 'HorizontalPodAutoscaler':
                if 'spec' not in manifest:
                    validation_results['valid'] = False
                    validation_results['errors'].append("HPA missing spec")
                
                spec = manifest.get('spec', {})
                if 'scaleTargetRef' not in spec:
                    validation_results['valid'] = False
                    validation_results['errors'].append("HPA missing scaleTargetRef")
            
            elif kind == 'ResourceQuota':
                if 'spec' not in manifest:
                    validation_results['valid'] = False
                    validation_results['errors'].append("ResourceQuota missing spec")
                
                spec = manifest.get('spec', {})
                if 'hard' not in spec:
                    validation_results['warnings'].append("ResourceQuota missing hard limits")
        
        return validation_results
    
    def generate_deployment_summary(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate deployment summary"""
        summary = {
            'total_optimizations': len(optimizations),
            'estimated_savings': 0,
            'risk_level': 'low',
            'deployments': []
        }
        
        total_savings = 0
        risk_levels = []
        
        for optimization in optimizations:
            savings = optimization.get('estimated_savings', 0)
            total_savings += savings
            risk_level = optimization.get('risk_level', 'low')
            risk_levels.append(risk_level)
            
            summary['deployments'].append({
                'name': optimization.get('deployment', ''),
                'namespace': optimization.get('namespace', ''),
                'type': optimization.get('type', ''),
                'savings': savings,
                'risk_level': risk_level
            })
        
        summary['estimated_savings'] = total_savings
        
        # Determine overall risk level
        if 'high' in risk_levels:
            summary['risk_level'] = 'high'
        elif 'medium' in risk_levels:
            summary['risk_level'] = 'medium'
        else:
            summary['risk_level'] = 'low'
        
        return summary
