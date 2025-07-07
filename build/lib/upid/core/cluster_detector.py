"""
Universal Kubernetes Cluster Detector
Detects and configures any Kubernetes cluster automatically
"""

import os
import subprocess
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

class ClusterDetector:
    """Detects and analyzes any Kubernetes cluster"""
    
    def __init__(self):
        self.kubeconfig = os.getenv('KUBECONFIG', '~/.kube/config')
        self.kubeconfig = os.path.expanduser(self.kubeconfig)
    
    def detect_cluster(self) -> Dict[str, Any]:
        """Detect cluster type and capabilities"""
        try:
            # Get current context
            context = self._get_current_context()
            cluster_info = self._get_cluster_info(context)
            
            # Detect cluster type
            cluster_type = self._detect_cluster_type(cluster_info)
            
            # Get cluster capabilities
            capabilities = self._detect_capabilities()
            
            return {
                'name': context,
                'type': cluster_type,
                'info': cluster_info,
                'capabilities': capabilities,
                'status': 'connected',
                'kubeconfig': self.kubeconfig
            }
        except Exception as e:
            return {
                'name': 'unknown',
                'type': 'unknown',
                'status': 'error',
                'error': str(e)
            }
    
    def _get_current_context(self) -> str:
        """Get current kubectl context"""
        try:
            result = subprocess.run(
                ['kubectl', 'config', 'current-context'],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip()
        except Exception:
            return 'default'
    
    def _get_cluster_info(self, context: str) -> Dict[str, Any]:
        """Get detailed cluster information"""
        info = {}
        
        try:
            # Get cluster info
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True, text=True, timeout=10
            )
            info['cluster_info'] = result.stdout
            
            # Get nodes
            result = subprocess.run(
                ['kubectl', 'get', 'nodes', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info['nodes'] = json.loads(result.stdout)
            
            # Get namespaces
            result = subprocess.run(
                ['kubectl', 'get', 'namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info['namespaces'] = json.loads(result.stdout)
            
            # Get pods
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info['pods'] = json.loads(result.stdout)
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _detect_cluster_type(self, cluster_info: Dict[str, Any]) -> str:
        """Detect the type of Kubernetes cluster"""
        try:
            # Check for cloud providers
            if 'nodes' in cluster_info:
                nodes = cluster_info['nodes']
                for node in nodes.get('items', []):
                    node_name = node.get('metadata', {}).get('name', '')
                    
                    # AWS EKS
                    if 'eks' in node_name.lower() or 'ip-' in node_name:
                        return 'eks'
                    
                    # Azure AKS
                    if 'aks' in node_name.lower():
                        return 'aks'
                    
                    # Google GKE
                    if 'gke' in node_name.lower():
                        return 'gke'
                    
                    # Docker Desktop
                    if 'docker-desktop' in node_name.lower():
                        return 'docker-desktop'
                    
                    # Minikube
                    if 'minikube' in node_name.lower():
                        return 'minikube'
                    
                    # Kind
                    if 'kind' in node_name.lower():
                        return 'kind'
                    
                    # K3s
                    if 'k3s' in node_name.lower():
                        return 'k3s'
            
            # Check cluster info for hints
            cluster_info_text = cluster_info.get('cluster_info', '')
            if 'eks' in cluster_info_text.lower():
                return 'eks'
            elif 'aks' in cluster_info_text.lower():
                return 'aks'
            elif 'gke' in cluster_info_text.lower():
                return 'gke'
            elif 'docker-desktop' in cluster_info_text.lower():
                return 'docker-desktop'
            elif 'minikube' in cluster_info_text.lower():
                return 'minikube'
            elif 'kind' in cluster_info_text.lower():
                return 'kind'
            elif 'k3s' in cluster_info_text.lower():
                return 'k3s'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'
    
    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect cluster capabilities"""
        capabilities = {
            'metrics_server': False,
            'prometheus': False,
            'grafana': False,
            'ingress': False,
            'load_balancer': False,
            'storage_class': False,
            'helm': False
        }
        
        try:
            # Check for metrics-server
            result = subprocess.run(
                ['kubectl', 'get', 'deployment', 'metrics-server', '-n', 'kube-system'],
                capture_output=True, text=True, timeout=5
            )
            capabilities['metrics_server'] = result.returncode == 0
            
            # Check for Prometheus
            result = subprocess.run(
                ['kubectl', 'get', 'deployment', 'prometheus', '--all-namespaces'],
                capture_output=True, text=True, timeout=5
            )
            capabilities['prometheus'] = result.returncode == 0
            
            # Check for Grafana
            result = subprocess.run(
                ['kubectl', 'get', 'deployment', 'grafana', '--all-namespaces'],
                capture_output=True, text=True, timeout=5
            )
            capabilities['grafana'] = result.returncode == 0
            
            # Check for ingress controller
            result = subprocess.run(
                ['kubectl', 'get', 'ingressclass'],
                capture_output=True, text=True, timeout=5
            )
            capabilities['ingress'] = result.returncode == 0
            
            # Check for storage classes
            result = subprocess.run(
                ['kubectl', 'get', 'storageclass'],
                capture_output=True, text=True, timeout=5
            )
            capabilities['storage_class'] = result.returncode == 0
            
            # Check for Helm
            result = subprocess.run(
                ['helm', 'version'],
                capture_output=True, text=True, timeout=5
            )
            capabilities['helm'] = result.returncode == 0
            
        except Exception:
            pass
        
        return capabilities
    
    def get_cluster_metrics(self) -> Dict[str, Any]:
        """Get real-time cluster metrics"""
        metrics = {
            'nodes': {},
            'pods': {},
            'resources': {},
            'costs': {}
        }
        
        try:
            # Get node metrics
            result = subprocess.run(
                ['kubectl', 'top', 'nodes'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                metrics['nodes'] = self._parse_top_output(result.stdout)
            
            # Get pod metrics
            result = subprocess.run(
                ['kubectl', 'top', 'pods', '--all-namespaces'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                metrics['pods'] = self._parse_top_output(result.stdout)
            
            # Get resource usage
            metrics['resources'] = self._get_resource_usage()
            
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics
    
    def _parse_top_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse kubectl top output"""
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split()
        results = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split()
                if len(values) >= len(headers):
                    row = {}
                    for i, header in enumerate(headers):
                        row[header.lower()] = values[i] if i < len(values) else ''
                    results.append(row)
        
        return results
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get detailed resource usage"""
        resources = {
            'cpu': {'used': 0, 'total': 0},
            'memory': {'used': 0, 'total': 0},
            'pods': {'running': 0, 'total': 0}
        }
        
        try:
            # Get node resources
            result = subprocess.run(
                ['kubectl', 'get', 'nodes', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                nodes = json.loads(result.stdout)
                for node in nodes.get('items', []):
                    status = node.get('status', {})
                    allocatable = status.get('allocatable', {})
                    
                    # CPU
                    cpu_str = allocatable.get('cpu', '0')
                    cpu_cores = self._parse_cpu(cpu_str)
                    resources['cpu']['total'] += cpu_cores
                    
                    # Memory
                    memory_str = allocatable.get('memory', '0')
                    memory_bytes = self._parse_memory(memory_str)
                    resources['memory']['total'] += memory_bytes
            
            # Get pod resources
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                pods = json.loads(result.stdout)
                for pod in pods.get('items', []):
                    status = pod.get('status', {}).get('phase', '')
                    if status == 'Running':
                        resources['pods']['running'] += 1
                    resources['pods']['total'] += 1
                    
                    # Calculate resource usage from pod specs
                    spec = pod.get('spec', {})
                    containers = spec.get('containers', [])
                    for container in containers:
                        requests = container.get('resources', {}).get('requests', {})
                        
                        # CPU
                        cpu_str = requests.get('cpu', '0')
                        cpu_cores = self._parse_cpu(cpu_str)
                        resources['cpu']['used'] += cpu_cores
                        
                        # Memory
                        memory_str = requests.get('memory', '0')
                        memory_bytes = self._parse_memory(memory_str)
                        resources['memory']['used'] += memory_bytes
            
        except Exception:
            pass
        
        return resources
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to cores"""
        try:
            if cpu_str.endswith('m'):
                return float(cpu_str[:-1]) / 1000
            return float(cpu_str)
        except:
            return 0.0
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory string to bytes"""
        try:
            if memory_str.endswith('Ki'):
                return int(memory_str[:-2]) * 1024
            elif memory_str.endswith('Mi'):
                return int(memory_str[:-2]) * 1024 * 1024
            elif memory_str.endswith('Gi'):
                return int(memory_str[:-2]) * 1024 * 1024 * 1024
            elif memory_str.endswith('Ti'):
                return int(memory_str[:-2]) * 1024 * 1024 * 1024 * 1024
            else:
                return int(memory_str)
        except:
            return 0 