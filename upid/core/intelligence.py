"""
Intelligent Data Collection Engine for UPID
Implements sophisticated intelligence beyond simple kubectl metrics
Features:
- Real business activity detection (distinguishing real user requests from health checks)
- Business calendar intelligence
- Dependency chain analysis
- Resource vs work correlation
- Advanced pod idle detection
"""

import os
import subprocess
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
import logging
import re
from collections import defaultdict, Counter
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class IntelligentDataCollector:
    """Sophisticated data collection with business intelligence"""
    
    def __init__(self):
        """Initialize the intelligent data collector"""
        self.business_hours = {
            'start': 9,  # 9 AM
            'end': 17,   # 5 PM
            'timezone': 'UTC'
        }
        
        self.health_check_patterns = [
            r'/health',
            r'/ready',
            r'/live',
            r'/ping',
            r'/status',
            r'healthz',
            r'readyz',
            r'livez'
        ]
        
        self.business_request_patterns = [
            r'/api/',
            r'/v1/',
            r'/v2/',
            r'/users/',
            r'/orders/',
            r'/payments/',
            r'/products/',
            r'/customers/'
        ]
        
        # Cache for dependency analysis
        self.dependency_cache = {}
        self.activity_cache = {}
        
    def collect_intelligent_metrics(self, cluster_id: str) -> Dict[str, Any]:
        """Collect intelligent metrics with business context"""
        try:
            # Get basic cluster info
            cluster_info = self._get_cluster_info()
            
            # Collect intelligent pod metrics
            intelligent_pods = self._collect_intelligent_pod_metrics()
            
            # Analyze business activity patterns
            business_activity = self._analyze_business_activity(intelligent_pods)
            
            # Perform dependency chain analysis
            dependencies = self._analyze_dependency_chains(intelligent_pods)
            
            # Correlate resources with actual work
            resource_work_correlation = self._correlate_resources_with_work(intelligent_pods, business_activity)
            
            # Detect intelligent idle patterns
            idle_analysis = self._detect_intelligent_idle_patterns(intelligent_pods, business_activity)
            
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'cluster_info': cluster_info,
                'intelligent_pods': intelligent_pods,
                'business_activity': business_activity,
                'dependencies': dependencies,
                'resource_work_correlation': resource_work_correlation,
                'idle_analysis': idle_analysis,
                'intelligence_metadata': {
                    'business_hours_analyzed': True,
                    'dependency_chains_detected': len(dependencies['chains']),
                    'real_activity_detected': business_activity['real_activity_count'],
                    'health_check_filtered': business_activity['health_check_count']
                }
            }
            
        except Exception as e:
            logger.error(f"Error collecting intelligent metrics: {e}")
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _get_cluster_info(self) -> Dict[str, Any]:
        """Get enhanced cluster information"""
        try:
            # Get cluster info
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True, text=True, timeout=10
            )
            
            # Get nodes with labels
            result_nodes = subprocess.run(
                ['kubectl', 'get', 'nodes', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            
            # Get namespaces
            result_ns = subprocess.run(
                ['kubectl', 'get', 'namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            
            return {
                'cluster_info': result.stdout if result.returncode == 0 else '',
                'nodes': json.loads(result_nodes.stdout) if result_nodes.returncode == 0 else {},
                'namespaces': json.loads(result_ns.stdout) if result_ns.returncode == 0 else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            return {}
    
    def _collect_intelligent_pod_metrics(self) -> List[Dict[str, Any]]:
        """Collect intelligent pod metrics with business context"""
        try:
            # Get all pods with detailed information
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode != 0:
                return []
            
            pods_data = json.loads(result.stdout)
            intelligent_pods = []
            
            for pod in pods_data.get('items', []):
                pod_info = self._analyze_pod_intelligence(pod)
                if pod_info:
                    intelligent_pods.append(pod_info)
            
            return intelligent_pods
            
        except Exception as e:
            logger.error(f"Error collecting intelligent pod metrics: {e}")
            return []
    
    def _analyze_pod_intelligence(self, pod: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze individual pod with business intelligence"""
        try:
            metadata = pod.get('metadata', {})
            spec = pod.get('spec', {})
            status = pod.get('status', {})
            
            pod_name = metadata.get('name', '')
            namespace = metadata.get('namespace', '')
            labels = metadata.get('labels', {})
            
            # Get pod logs for activity analysis
            logs = self._get_pod_logs(namespace, pod_name)
            
            # Analyze request patterns
            request_analysis = self._analyze_request_patterns(logs)
            
            # Detect business vs health activity
            activity_type = self._classify_activity_type(request_analysis)
            
            # Analyze resource usage patterns
            resource_analysis = self._analyze_resource_patterns(pod)
            
            # Detect idle patterns
            idle_patterns = self._detect_pod_idle_patterns(request_analysis, resource_analysis)
            
            return {
                'name': pod_name,
                'namespace': namespace,
                'labels': labels,
                'status': status.get('phase', ''),
                'activity_analysis': activity_type,
                'request_patterns': request_analysis,
                'resource_analysis': resource_analysis,
                'idle_patterns': idle_patterns,
                'business_context': self._extract_business_context(labels, namespace),
                'intelligence_score': self._calculate_intelligence_score(activity_type, request_analysis, resource_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pod intelligence: {e}")
            return None
    
    def _get_pod_logs(self, namespace: str, pod_name: str, lines: int = 100) -> str:
        """Get pod logs for activity analysis"""
        try:
            result = subprocess.run(
                ['kubectl', 'logs', f'{namespace}/{pod_name}', '--tail={lines}'],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout if result.returncode == 0 else ''
        except Exception:
            return ''
    
    def _analyze_request_patterns(self, logs: str) -> Dict[str, Any]:
        """Analyze request patterns in pod logs"""
        if not logs:
            return {'total_requests': 0, 'business_requests': 0, 'health_checks': 0}
        
        lines = logs.split('\n')
        total_requests = 0
        business_requests = 0
        health_checks = 0
        
        # Analyze each log line
        for line in lines:
            if self._is_http_request(line):
                total_requests += 1
                
                if self._is_business_request(line):
                    business_requests += 1
                elif self._is_health_check(line):
                    health_checks += 1
        
        return {
            'total_requests': total_requests,
            'business_requests': business_requests,
            'health_checks': health_checks,
            'business_ratio': business_requests / total_requests if total_requests > 0 else 0,
            'health_check_ratio': health_checks / total_requests if total_requests > 0 else 0
        }
    
    def _is_http_request(self, line: str) -> bool:
        """Check if log line contains HTTP request"""
        http_patterns = [
            r'GET\s+',
            r'POST\s+',
            r'PUT\s+',
            r'DELETE\s+',
            r'PATCH\s+',
            r'HTTP/\d+\.\d+\s+\d+',
            r'status=\d+',
            r'method='
        ]
        
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in http_patterns)
    
    def _is_business_request(self, line: str) -> bool:
        """Check if request is business-related"""
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in self.business_request_patterns)
    
    def _is_health_check(self, line: str) -> bool:
        """Check if request is a health check"""
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in self.health_check_patterns)
    
    def _classify_activity_type(self, request_analysis: Dict[str, Any]) -> str:
        """Classify pod activity type"""
        business_ratio = request_analysis.get('business_ratio', 0)
        health_ratio = request_analysis.get('health_check_ratio', 0)
        total_requests = request_analysis.get('total_requests', 0)
        
        if total_requests == 0:
            return 'idle'
        elif business_ratio > 0.7:
            return 'business_active'
        elif business_ratio > 0.3:
            return 'mixed_activity'
        elif health_ratio > 0.8:
            return 'health_check_only'
        else:
            return 'low_activity'
    
    def _analyze_resource_patterns(self, pod: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource usage patterns"""
        try:
            # Get pod resource usage
            namespace = pod.get('metadata', {}).get('namespace', '')
            pod_name = pod.get('metadata', {}).get('name', '')
            
            result = subprocess.run(
                ['kubectl', 'top', 'pod', f'{namespace}/{pod_name}'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return {'cpu': 0, 'memory': 0, 'resource_efficiency': 'unknown'}
            
            # Parse top output
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 3:
                    cpu = self._parse_cpu(parts[1])
                    memory = self._parse_memory(parts[2])
                    
                    # Calculate resource efficiency
                    efficiency = self._calculate_resource_efficiency(cpu, memory)
                    
                    return {
                        'cpu': cpu,
                        'memory': memory,
                        'resource_efficiency': efficiency,
                        'resource_utilization': {
                            'cpu_percent': cpu,
                            'memory_percent': memory
                        }
                    }
            
            return {'cpu': 0, 'memory': 0, 'resource_efficiency': 'unknown'}
            
        except Exception as e:
            logger.error(f"Error analyzing resource patterns: {e}")
            return {'cpu': 0, 'memory': 0, 'resource_efficiency': 'unknown'}
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU usage string"""
        try:
            if cpu_str.endswith('m'):
                return float(cpu_str[:-1]) / 1000
            elif cpu_str.endswith('%'):
                return float(cpu_str[:-1])
            else:
                return float(cpu_str)
        except:
            return 0.0
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory usage string"""
        try:
            if memory_str.endswith('Mi'):
                return int(memory_str[:-2])
            elif memory_str.endswith('Gi'):
                return int(float(memory_str[:-2]) * 1024)
            else:
                return int(memory_str)
        except:
            return 0
    
    def _calculate_resource_efficiency(self, cpu: float, memory: int) -> str:
        """Calculate resource efficiency score"""
        if cpu == 0 and memory == 0:
            return 'idle'
        elif cpu < 5 and memory < 50:
            return 'underutilized'
        elif cpu > 80 or memory > 800:
            return 'overutilized'
        else:
            return 'efficient'
    
    def _detect_pod_idle_patterns(self, request_analysis: Dict[str, Any], 
                                 resource_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detect intelligent idle patterns"""
        total_requests = request_analysis.get('total_requests', 0)
        cpu = resource_analysis.get('cpu', 0)
        memory = resource_analysis.get('memory', 0)
        
        idle_score = 0
        idle_reasons = []
        
        # No requests
        if total_requests == 0:
            idle_score += 40
            idle_reasons.append('no_requests')
        
        # Low resource usage
        if cpu < 1 and memory < 50:
            idle_score += 30
            idle_reasons.append('low_resource_usage')
        
        # Only health checks
        health_ratio = request_analysis.get('health_check_ratio', 0)
        if health_ratio > 0.9:
            idle_score += 20
            idle_reasons.append('health_checks_only')
        
        # Low business activity
        business_ratio = request_analysis.get('business_ratio', 0)
        if business_ratio < 0.1:
            idle_score += 10
            idle_reasons.append('low_business_activity')
        
        return {
            'idle_score': min(100, idle_score),
            'idle_reasons': idle_reasons,
            'is_idle': idle_score > 50,
            'idle_confidence': min(100, idle_score + (100 - idle_score) * 0.3)
        }
    
    def _extract_business_context(self, labels: Dict[str, str], namespace: str) -> Dict[str, Any]:
        """Extract business context from labels and namespace"""
        context = {
            'environment': 'unknown',
            'application': 'unknown',
            'team': 'unknown',
            'business_unit': 'unknown'
        }
        
        # Extract from labels
        if 'app' in labels:
            context['application'] = labels['app']
        if 'environment' in labels:
            context['environment'] = labels['environment']
        if 'team' in labels:
            context['team'] = labels['team']
        if 'business-unit' in labels:
            context['business_unit'] = labels['business-unit']
        
        # Extract from namespace
        if namespace.startswith('prod-') or namespace == 'production':
            context['environment'] = 'production'
        elif namespace.startswith('staging-') or namespace == 'staging':
            context['environment'] = 'staging'
        elif namespace.startswith('dev-') or namespace == 'development':
            context['environment'] = 'development'
        
        return context
    
    def _calculate_intelligence_score(self, activity_type: str, 
                                   request_analysis: Dict[str, Any],
                                   resource_analysis: Dict[str, Any]) -> float:
        """Calculate intelligence score for pod"""
        score = 0.0
        
        # Activity type scoring
        activity_scores = {
            'business_active': 90,
            'mixed_activity': 70,
            'low_activity': 40,
            'health_check_only': 20,
            'idle': 10
        }
        
        score += activity_scores.get(activity_type, 0)
        
        # Resource efficiency scoring
        efficiency = resource_analysis.get('resource_efficiency', 'unknown')
        efficiency_scores = {
            'efficient': 10,
            'underutilized': 5,
            'overutilized': 5,
            'idle': 0
        }
        
        score += efficiency_scores.get(efficiency, 0)
        
        return min(100, score)
    
    def _analyze_business_activity(self, intelligent_pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze business activity patterns across the cluster"""
        total_pods = len(intelligent_pods)
        business_active_pods = 0
        idle_pods = 0
        health_check_only_pods = 0
        
        activity_by_namespace = defaultdict(lambda: {'business': 0, 'idle': 0, 'health': 0})
        activity_by_environment = defaultdict(lambda: {'business': 0, 'idle': 0, 'health': 0})
        
        for pod in intelligent_pods:
            activity_type = pod.get('activity_analysis', 'unknown')
            namespace = pod.get('namespace', '')
            environment = pod.get('business_context', {}).get('environment', 'unknown')
            
            if activity_type == 'business_active':
                business_active_pods += 1
                activity_by_namespace[namespace]['business'] += 1
                activity_by_environment[environment]['business'] += 1
            elif activity_type == 'idle':
                idle_pods += 1
                activity_by_namespace[namespace]['idle'] += 1
                activity_by_environment[environment]['idle'] += 1
            elif activity_type == 'health_check_only':
                health_check_only_pods += 1
                activity_by_namespace[namespace]['health'] += 1
                activity_by_environment[environment]['health'] += 1
        
        return {
            'total_pods': total_pods,
            'business_active_pods': business_active_pods,
            'idle_pods': idle_pods,
            'health_check_only_pods': health_check_only_pods,
            'business_activity_ratio': business_active_pods / total_pods if total_pods > 0 else 0,
            'idle_ratio': idle_pods / total_pods if total_pods > 0 else 0,
            'activity_by_namespace': dict(activity_by_namespace),
            'activity_by_environment': dict(activity_by_environment),
            'real_activity_count': business_active_pods,
            'health_check_count': health_check_only_pods
        }
    
    def _analyze_dependency_chains(self, intelligent_pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze dependency chains between pods"""
        try:
            # Get services
            result = subprocess.run(
                ['kubectl', 'get', 'services', '--all-namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return {'chains': [], 'dependencies': {}}
            
            services_data = json.loads(result.stdout)
            
            # Build dependency map
            dependencies = {}
            chains = []
            
            for service in services_data.get('items', []):
                service_name = service.get('metadata', {}).get('name', '')
                namespace = service.get('metadata', {}).get('namespace', '')
                selector = service.get('spec', {}).get('selector', {})
                
                # Find pods that match this service
                matching_pods = []
                for pod in intelligent_pods:
                    pod_namespace = pod.get('namespace', '')
                    pod_labels = pod.get('labels', {})
                    
                    if pod_namespace == namespace and self._labels_match_selector(pod_labels, selector):
                        matching_pods.append(pod.get('name', ''))
                
                if matching_pods:
                    dependencies[f"{namespace}/{service_name}"] = matching_pods
            
            # Detect chains
            chains = self._detect_dependency_chains(dependencies)
            
            return {
                'chains': chains,
                'dependencies': dependencies,
                'chain_count': len(chains),
                'dependency_count': len(dependencies)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing dependency chains: {e}")
            return {'chains': [], 'dependencies': {}}
    
    def _labels_match_selector(self, labels: Dict[str, str], selector: Dict[str, str]) -> bool:
        """Check if pod labels match service selector"""
        for key, value in selector.items():
            if key not in labels or labels[key] != value:
                return False
        return True
    
    def _detect_dependency_chains(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect dependency chains between services"""
        chains = []
        visited = set()
        
        for service, pods in dependencies.items():
            if service not in visited:
                chain = self._dfs_dependency_chain(service, dependencies, visited, set())
                if len(chain) > 1:
                    chains.append(chain)
        
        return chains
    
    def _dfs_dependency_chain(self, service: str, dependencies: Dict[str, List[str]], 
                            visited: Set[str], path: Set[str]) -> List[str]:
        """Depth-first search for dependency chains"""
        if service in path:
            return []  # Circular dependency
        
        if service in visited:
            return []
        
        visited.add(service)
        path.add(service)
        
        chain = [service]
        
        # Find services that depend on this service
        for other_service, pods in dependencies.items():
            if other_service != service and other_service not in visited:
                # Check if there's a dependency relationship
                # This is a simplified check - in reality, you'd analyze service calls
                if self._has_dependency_relationship(service, other_service, dependencies):
                    sub_chain = self._dfs_dependency_chain(other_service, dependencies, visited, path)
                    chain.extend(sub_chain)
        
        path.remove(service)
        return chain
    
    def _has_dependency_relationship(self, service1: str, service2: str, 
                                  dependencies: Dict[str, List[str]]) -> bool:
        """Check if service2 depends on service1"""
        # Simplified dependency detection
        # In reality, this would analyze service calls, network policies, etc.
        return False  # Placeholder
    
    def _correlate_resources_with_work(self, intelligent_pods: List[Dict[str, Any]], 
                                     business_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate resource usage with actual business work"""
        correlation_data = {
            'total_cpu': 0,
            'total_memory': 0,
            'business_cpu': 0,
            'business_memory': 0,
            'idle_cpu': 0,
            'idle_memory': 0,
            'efficiency_score': 0
        }
        
        for pod in intelligent_pods:
            resource_analysis = pod.get('resource_analysis', {})
            activity_type = pod.get('activity_analysis', 'unknown')
            
            cpu = resource_analysis.get('cpu', 0)
            memory = resource_analysis.get('memory', 0)
            
            correlation_data['total_cpu'] += cpu
            correlation_data['total_memory'] += memory
            
            if activity_type == 'business_active':
                correlation_data['business_cpu'] += cpu
                correlation_data['business_memory'] += memory
            elif activity_type in ['idle', 'health_check_only']:
                correlation_data['idle_cpu'] += cpu
                correlation_data['idle_memory'] += memory
        
        # Calculate efficiency score
        total_cpu = correlation_data['total_cpu']
        total_memory = correlation_data['total_memory']
        
        if total_cpu > 0:
            cpu_efficiency = correlation_data['business_cpu'] / total_cpu
        else:
            cpu_efficiency = 0
        
        if total_memory > 0:
            memory_efficiency = correlation_data['business_memory'] / total_memory
        else:
            memory_efficiency = 0
        
        correlation_data['efficiency_score'] = (cpu_efficiency + memory_efficiency) / 2 * 100
        
        return correlation_data
    
    def _detect_intelligent_idle_patterns(self, intelligent_pods: List[Dict[str, Any]], 
                                        business_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Detect intelligent idle patterns with business context"""
        idle_pods = []
        idle_by_namespace = defaultdict(list)
        idle_by_environment = defaultdict(list)
        
        for pod in intelligent_pods:
            idle_patterns = pod.get('idle_patterns', {})
            
            if idle_patterns.get('is_idle', False):
                idle_pods.append({
                    'name': pod.get('name', ''),
                    'namespace': pod.get('namespace', ''),
                    'idle_score': idle_patterns.get('idle_score', 0),
                    'idle_reasons': idle_patterns.get('idle_reasons', []),
                    'confidence': idle_patterns.get('idle_confidence', 0),
                    'business_context': pod.get('business_context', {}),
                    'resource_analysis': pod.get('resource_analysis', {})
                })
                
                namespace = pod.get('namespace', '')
                environment = pod.get('business_context', {}).get('environment', 'unknown')
                
                idle_by_namespace[namespace].append(pod.get('name', ''))
                idle_by_environment[environment].append(pod.get('name', ''))
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(idle_pods)
        
        return {
            'idle_pods': idle_pods,
            'idle_count': len(idle_pods),
            'idle_by_namespace': dict(idle_by_namespace),
            'idle_by_environment': dict(idle_by_environment),
            'potential_savings': potential_savings,
            'idle_confidence_distribution': self._calculate_confidence_distribution(idle_pods)
        }
    
    def _calculate_potential_savings(self, idle_pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate potential cost savings from idle pods"""
        total_cpu = 0
        total_memory = 0
        high_confidence_count = 0
        
        for pod in idle_pods:
            resource_analysis = pod.get('resource_analysis', {})
            confidence = pod.get('confidence', 0)
            
            cpu = resource_analysis.get('cpu', 0)
            memory = resource_analysis.get('memory', 0)
            
            total_cpu += cpu
            total_memory += memory
            
            if confidence > 80:
                high_confidence_count += 1
        
        # Estimate cost savings (simplified)
        # In reality, this would use actual pricing data
        estimated_cpu_cost = total_cpu * 0.1  # $0.1 per CPU core per hour
        estimated_memory_cost = total_memory * 0.01  # $0.01 per MB per hour
        
        return {
            'cpu_cores': total_cpu,
            'memory_mb': total_memory,
            'estimated_hourly_savings': estimated_cpu_cost + estimated_memory_cost,
            'estimated_daily_savings': (estimated_cpu_cost + estimated_memory_cost) * 24,
            'estimated_monthly_savings': (estimated_cpu_cost + estimated_memory_cost) * 24 * 30,
            'high_confidence_count': high_confidence_count,
            'savings_confidence': min(100, high_confidence_count / len(idle_pods) * 100) if idle_pods else 0
        }
    
    def _calculate_confidence_distribution(self, idle_pods: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate confidence distribution for idle pods"""
        distribution = {
            'high_confidence': 0,    # 80-100%
            'medium_confidence': 0,  # 60-79%
            'low_confidence': 0      # <60%
        }
        
        for pod in idle_pods:
            confidence = pod.get('confidence', 0)
            
            if confidence >= 80:
                distribution['high_confidence'] += 1
            elif confidence >= 60:
                distribution['medium_confidence'] += 1
            else:
                distribution['low_confidence'] += 1
        
        return distribution 