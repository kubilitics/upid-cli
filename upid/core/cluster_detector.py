"""
Universal Kubernetes Cluster Detector
Detects and configures any Kubernetes cluster automatically
Enhanced with time-series intelligence capabilities
"""

import os
import subprocess
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime
from .data_store import TimeSeriesDataStore
from .analytics import PatternAnalyzer
from .intelligence import IntelligentDataCollector
from .advanced_analytics import AdvancedIntelligenceEngine
from .confidence_optimizer import ConfidenceOptimizer
from .business_impact import BusinessImpactCorrelator
from .executive_dashboard import ExecutiveDashboardEngine
import numpy as np

class ClusterDetector:
    """Detects and analyzes any Kubernetes cluster with intelligence capabilities"""
    
    def __init__(self):
        self.kubeconfig = os.getenv('KUBECONFIG', '~/.kube/config')
        self.kubeconfig = os.path.expanduser(self.kubeconfig)
        
        # Initialize intelligence components
        self.data_store = TimeSeriesDataStore()
        self.pattern_analyzer = PatternAnalyzer()
        self.intelligent_collector = IntelligentDataCollector()
        self.advanced_analytics = AdvancedIntelligenceEngine()
        
        # Initialize Phase 2 components
        self.confidence_optimizer = ConfidenceOptimizer()
        self.business_impact_correlator = BusinessImpactCorrelator()
        
        # Initialize Phase 3 component
        self.executive_dashboard_engine = ExecutiveDashboardEngine()
    
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
        """Get real-time cluster metrics with intelligence"""
        metrics = {
            'nodes': {},
            'pods': {},
            'resources': {},
            'costs': {},
            'intelligence': {}
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
            
            # Store metrics in time-series database
            cluster_info = self.detect_cluster()
            cluster_id = cluster_info.get('name', 'unknown')
            self.data_store.store_metrics(cluster_id, metrics)
            
            # Add intelligence insights
            metrics['intelligence'] = self._get_intelligence_insights(cluster_id)
            
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
    
    def collect_intelligent_metrics(self, cluster_id: str) -> Dict[str, Any]:
        """Collect intelligent metrics with business context"""
        try:
            # Use the intelligent data collector
            intelligent_metrics = self.intelligent_collector.collect_intelligent_metrics(cluster_id)
            
            # Store the intelligent metrics
            self.data_store.store_metrics(cluster_id, intelligent_metrics)
            
            return intelligent_metrics
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def analyze_intelligent_patterns(self, cluster_id: str) -> Dict[str, Any]:
        """Analyze intelligent patterns with advanced analytics"""
        try:
            # Get historical data
            historical_data = self.data_store.get_historical_data(cluster_id, days=90)
            
            # Perform advanced pattern analysis
            advanced_analysis = self.advanced_analytics.analyze_advanced_patterns(historical_data)
            
            # Also perform basic pattern analysis for comparison
            basic_analysis = self.pattern_analyzer.analyze_historical_data(historical_data)
            
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'advanced_analysis': advanced_analysis,
                'basic_analysis': basic_analysis,
                'analysis_comparison': {
                    'advanced_features': len(advanced_analysis.get('advanced_patterns', {})),
                    'basic_features': len(basic_analysis.get('patterns', {})),
                    'intelligence_level': 'advanced' if advanced_analysis.get('confidence_metrics', {}).get('overall_confidence', 0) > 70 else 'basic'
                }
            }
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def get_intelligent_recommendations(self, cluster_id: str) -> Dict[str, Any]:
        """Get intelligent recommendations with business context"""
        try:
            # Collect current intelligent metrics
            current_metrics = self.collect_intelligent_metrics(cluster_id)
            
            # Analyze patterns
            pattern_analysis = self.analyze_intelligent_patterns(cluster_id)
            
            # Generate recommendations
            recommendations = {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'business_recommendations': [],
                'technical_recommendations': [],
                'cost_optimization_recommendations': [],
                'capacity_planning_recommendations': [],
                'overall_priority': 'medium'
            }
            
            # Extract recommendations from advanced analysis
            advanced_analysis = pattern_analysis.get('advanced_analysis', {})
            
            # Business recommendations
            business_intelligence = advanced_analysis.get('business_intelligence', {})
            for metric_type, business_data in business_intelligence.get('business_hours_analysis', {}).items():
                if not business_data.get('has_business_pattern', False):
                    recommendations['business_recommendations'].append({
                        'type': 'business_pattern_optimization',
                        'priority': 'medium',
                        'resource': metric_type,
                        'description': f'No clear business hours pattern detected for {metric_type}',
                        'action': 'review_business_hours_utilization',
                        'confidence': business_data.get('business_hours_efficiency', 0)
                    })
            
            # Technical recommendations
            efficiency_analysis = advanced_analysis.get('efficiency_analysis', {})
            for recommendation in efficiency_analysis.get('efficiency_recommendations', []):
                recommendations['technical_recommendations'].append(recommendation)
            
            # Cost optimization recommendations
            cost_analysis = business_intelligence.get('cost_optimization', {})
            for metric_type, savings in cost_analysis.get('potential_savings', {}).items():
                if savings.get('potential_savings_percent', 0) > 20:
                    recommendations['cost_optimization_recommendations'].append({
                        'type': 'cost_optimization',
                        'priority': 'high' if savings['potential_savings_percent'] > 50 else 'medium',
                        'resource': metric_type,
                        'description': f'Potential savings of {savings["potential_savings_percent"]:.1f}% for {metric_type}',
                        'action': 'implement_optimization',
                        'savings_percent': savings.get('potential_savings_percent', 0)
                    })
            
            # Capacity planning recommendations
            capacity_analysis = business_intelligence.get('capacity_planning', {})
            for metric_type, capacity_data in capacity_analysis.get('scaling_insights', {}).items():
                if capacity_data.get('scaling_needed', False):
                    recommendations['capacity_planning_recommendations'].append({
                        'type': 'capacity_planning',
                        'priority': capacity_data.get('urgency', 'medium'),
                        'resource': metric_type,
                        'description': f'Scaling needed for {metric_type}',
                        'action': capacity_data.get('recommended_action', 'review_capacity'),
                        'urgency': capacity_data.get('urgency', 'medium')
                    })
            
            # Determine overall priority
            high_priority_count = sum(1 for rec in recommendations['business_recommendations'] + 
                                   recommendations['technical_recommendations'] + 
                                   recommendations['cost_optimization_recommendations'] + 
                                   recommendations['capacity_planning_recommendations'] 
                                   if rec.get('priority') == 'high')
            
            if high_priority_count > 3:
                recommendations['overall_priority'] = 'high'
            elif high_priority_count > 1:
                recommendations['overall_priority'] = 'medium'
            else:
                recommendations['overall_priority'] = 'low'
            
            return recommendations
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def get_intelligent_idle_analysis(self, cluster_id: str) -> Dict[str, Any]:
        """Get intelligent idle analysis with business context"""
        try:
            # Collect intelligent metrics
            intelligent_metrics = self.collect_intelligent_metrics(cluster_id)
            
            # Extract idle analysis
            idle_analysis = intelligent_metrics.get('idle_analysis', {})
            
            # Enhance with business context
            enhanced_idle_analysis = {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'idle_pods': idle_analysis.get('idle_pods', []),
                'idle_count': idle_analysis.get('idle_count', 0),
                'potential_savings': idle_analysis.get('potential_savings', {}),
                'business_context': {
                    'idle_by_environment': idle_analysis.get('idle_by_environment', {}),
                    'idle_by_namespace': idle_analysis.get('idle_by_namespace', {}),
                    'confidence_distribution': idle_analysis.get('idle_confidence_distribution', {})
                },
                'intelligent_insights': []
            }
            
            # Generate intelligent insights
            business_activity = intelligent_metrics.get('business_activity', {})
            resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
            
            # Business hours analysis
            if business_activity.get('business_activity_ratio', 0) < 0.3:
                enhanced_idle_analysis['intelligent_insights'].append({
                    'type': 'business_activity_low',
                    'description': 'Low business activity detected across cluster',
                    'recommendation': 'Review business hours utilization and consider scaling down during off-hours',
                    'confidence': business_activity.get('business_activity_ratio', 0) * 100
                })
            
            # Resource efficiency insights
            efficiency_score = resource_correlation.get('efficiency_score', 0)
            if efficiency_score < 50:
                enhanced_idle_analysis['intelligent_insights'].append({
                    'type': 'resource_efficiency_low',
                    'description': f'Low resource efficiency ({efficiency_score:.1f}%)',
                    'recommendation': 'Optimize resource allocation and eliminate idle resources',
                    'confidence': 100 - efficiency_score
                })
            
            # High confidence idle pods
            high_confidence_idle = [pod for pod in idle_analysis.get('idle_pods', []) 
                                  if pod.get('confidence', 0) > 80]
            
            if high_confidence_idle:
                enhanced_idle_analysis['intelligent_insights'].append({
                    'type': 'high_confidence_idle',
                    'description': f'{len(high_confidence_idle)} pods with high confidence idle detection',
                    'recommendation': 'Consider scaling down these pods immediately',
                    'confidence': np.mean([pod.get('confidence', 0) for pod in high_confidence_idle])
                })
            
            return enhanced_idle_analysis
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def generate_confidence_optimization_plans(self, cluster_id: str) -> Dict[str, Any]:
        """Generate confidence-based optimization plans"""
        try:
            # Collect intelligent metrics
            intelligent_metrics = self.collect_intelligent_metrics(cluster_id)
            
            # Get historical data
            historical_data = self.data_store.get_historical_data(cluster_id, days=90)
            
            # Generate optimization plans
            optimization_plans = self.confidence_optimizer.generate_optimization_plans(
                cluster_id, intelligent_metrics, historical_data
            )
            
            # Get optimization summary
            optimization_summary = self.confidence_optimizer.get_optimization_summary(optimization_plans)
            
            return {
                'cluster_id': cluster_id,
                'optimization_plans': [plan.__dict__ for plan in optimization_plans],
                'optimization_summary': optimization_summary,
                'total_plans': len(optimization_plans),
                'high_confidence_plans': len([p for p in optimization_plans if p.confidence_score >= 0.8]),
                'low_risk_plans': len([p for p in optimization_plans if p.risk_level.value in ['low', 'medium']])
            }
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'error': str(e),
                'optimization_plans': [],
                'optimization_summary': {},
                'total_plans': 0,
                'high_confidence_plans': 0,
                'low_risk_plans': 0
            }
    
    def correlate_business_impact(self, cluster_id: str) -> Dict[str, Any]:
        """Correlate technical metrics to business outcomes"""
        try:
            # Collect intelligent metrics
            intelligent_metrics = self.collect_intelligent_metrics(cluster_id)
            
            # Generate optimization plans for business impact analysis
            optimization_plans = self.confidence_optimizer.generate_optimization_plans(
                cluster_id, intelligent_metrics, {}
            )
            
            # Correlate business impact
            business_correlation = self.business_impact_correlator.correlate_technical_to_business(
                cluster_id, intelligent_metrics, optimization_plans
            )
            
            # Generate business report
            business_report = self.business_impact_correlator.generate_business_report(business_correlation)
            
            return {
                'cluster_id': cluster_id,
                'business_correlation': business_correlation,
                'business_report': business_report,
                'revenue_analysis': business_correlation.get('revenue_analysis', {}),
                'roi_analysis': business_correlation.get('roi_analysis', {}),
                'sla_analysis': business_correlation.get('sla_compliance_analysis', {})
            }
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'error': str(e),
                'business_correlation': {},
                'business_report': {},
                'revenue_analysis': {},
                'roi_analysis': {},
                'sla_analysis': {}
            }
    
    def execute_optimization_plan(self, cluster_id: str, plan_index: int, dry_run: bool = True) -> Dict[str, Any]:
        """Execute a specific optimization plan"""
        try:
            # Generate optimization plans
            optimization_result = self.generate_confidence_optimization_plans(cluster_id)
            
            if 'error' in optimization_result:
                return optimization_result
            
            optimization_plans = optimization_result.get('optimization_plans', [])
            
            if plan_index >= len(optimization_plans):
                return {
                    'cluster_id': cluster_id,
                    'error': f'Plan index {plan_index} out of range. Total plans: {len(optimization_plans)}'
                }
            
            # Convert dict back to OptimizationPlan object
            plan_dict = optimization_plans[plan_index]
            from .confidence_optimizer import OptimizationPlan, OptimizationType, RiskLevel, SafetyBoundary
            
            plan = OptimizationPlan(
                operation_type=OptimizationType(plan_dict['operation_type']),
                target_resource=plan_dict['target_resource'],
                current_value=plan_dict['current_value'],
                proposed_value=plan_dict['proposed_value'],
                confidence_score=plan_dict['confidence_score'],
                risk_level=RiskLevel(plan_dict['risk_level']),
                risk_score=plan_dict['risk_score'],
                potential_savings=plan_dict['potential_savings'],
                business_impact=plan_dict['business_impact'],
                rollback_plan=plan_dict['rollback_plan'],
                safety_boundaries=SafetyBoundary(),
                simulation_results=plan_dict['simulation_results']
            )
            
            # Execute the plan
            execution_result = self.confidence_optimizer.execute_optimization(plan, dry_run)
            
            return {
                'cluster_id': cluster_id,
                'plan_index': plan_index,
                'execution_result': execution_result,
                'dry_run': dry_run
            }
            
        except Exception as e:
            return {
                'cluster_id': cluster_id,
                'error': str(e),
                'plan_index': plan_index,
                'execution_result': {},
                'dry_run': dry_run
            }
    
    def generate_executive_dashboard(self, cluster_id: str, format: str = 'json') -> str:
        """Generate and export the executive dashboard summary for a cluster"""
        # Gather optimization history (last 90 days)
        optimization_history = []
        try:
            # Use confidence optimizer to get plans (simulate history)
            optimization_result = self.generate_confidence_optimization_plans(cluster_id)
            optimization_history = optimization_result.get('optimization_plans', [])
        except Exception:
            pass
        # Gather business reports (simulate with current)
        business_reports = []
        try:
            business_result = self.correlate_business_impact(cluster_id)
            if business_result.get('business_report'):
                business_reports.append(business_result['business_report'])
        except Exception:
            pass
        # Gather KPI history (simulate with current)
        kpi_history = []
        try:
            if business_result.get('business_correlation') and business_result['business_correlation'].get('business_kpis'):
                kpi_history.append(business_result['business_correlation']['business_kpis'])
        except Exception:
            pass
        # Generate dashboard
        summary = self.executive_dashboard_engine.generate_dashboard(
            cluster_id, optimization_history, business_reports, kpi_history
        )
        return self.executive_dashboard_engine.export_dashboard(summary, format=format) 