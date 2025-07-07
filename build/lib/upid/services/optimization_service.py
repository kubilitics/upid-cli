"""
Optimization service for UPID CLI
"""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.config import Config
from ..core.utils import calculate_savings, format_zero_pod_recommendation

class OptimizationService:
    """Service for resource optimization calculations"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
    
    def calculate_resource_optimization(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource optimization recommendations"""
        cpu_usage = cluster_data.get('cpu_usage', 0)
        memory_usage = cluster_data.get('memory_usage', 0)
        current_cost = cluster_data.get('current_cost', 0)
        
        # Calculate optimization potential
        cpu_optimization = max(0, cpu_usage - 80)  # Target 80% usage
        memory_optimization = max(0, memory_usage - 80)  # Target 80% usage
        
        # Estimate cost savings
        cpu_savings = (cpu_optimization / 100) * current_cost * 0.3  # 30% of cost is CPU
        memory_savings = (memory_optimization / 100) * current_cost * 0.2  # 20% of cost is memory
        
        total_savings = cpu_savings + memory_savings
        
        return {
            'cpu_optimization': cpu_optimization,
            'memory_optimization': memory_optimization,
            'estimated_savings': total_savings,
            'optimization_score': min(100, (cpu_optimization + memory_optimization) / 2),
            'recommendations': self._generate_recommendations(cpu_usage, memory_usage)
        }
    
    def calculate_zero_pod_recommendations(self, pod_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate zero-pod scaling recommendations"""
        recommendations = []
        idle_threshold = self.config.get('zero_pod.idle_threshold', '30m')
        idle_seconds = self._parse_duration(idle_threshold)
        
        for pod in pod_data:
            idle_time = pod.get('idle_time_seconds', 0)
            
            if idle_time >= idle_seconds:
                current_replicas = pod.get('current_replicas', 1)
                recommended_replicas = max(0, current_replicas - 1)
                
                if recommended_replicas == 0:
                    # Calculate savings for zero-pod scaling
                    pod_cost = pod.get('estimated_cost', 0)
                    savings = pod_cost * (idle_time / (24 * 3600))  # Daily savings
                    
                    recommendations.append({
                        'namespace': pod.get('namespace', ''),
                        'deployment': pod.get('deployment', ''),
                        'current_replicas': current_replicas,
                        'recommended_replicas': recommended_replicas,
                        'idle_time_seconds': idle_time,
                        'idle_time': self._format_duration(idle_time),
                        'estimated_savings': savings,
                        'risk_level': self._assess_risk(pod),
                        'reason': f"Pod idle for {self._format_duration(idle_time)}"
                    })
        
        return recommendations
    
    def calculate_cost_optimization(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost optimization recommendations"""
        current_cost = cost_data.get('current_cost', 0)
        categories = cost_data.get('categories', [])
        
        total_optimized_cost = 0
        optimizations = []
        
        for category in categories:
            current = category.get('current_cost', 0)
            optimized = category.get('optimized_cost', 0)
            savings = current - optimized
            
            if savings > 0:
                total_optimized_cost += optimized
                optimizations.append({
                    'category': category.get('name', ''),
                    'current_cost': current,
                    'optimized_cost': optimized,
                    'savings': savings,
                    'savings_percentage': (savings / current * 100) if current > 0 else 0
                })
        
        total_savings = current_cost - total_optimized_cost
        savings_percentage = (total_savings / current_cost * 100) if current_cost > 0 else 0
        
        return {
            'current_cost': current_cost,
            'optimized_cost': total_optimized_cost,
            'total_savings': total_savings,
            'savings_percentage': savings_percentage,
            'optimizations': optimizations,
            'recommendations': self._generate_cost_recommendations(optimizations)
        }
    
    def _generate_recommendations(self, cpu_usage: float, memory_usage: float) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if cpu_usage > 80:
            recommendations.append("Consider scaling up CPU resources or optimizing CPU-intensive workloads")
        
        if memory_usage > 80:
            recommendations.append("Consider scaling up memory resources or optimizing memory usage")
        
        if cpu_usage < 20:
            recommendations.append("Consider scaling down CPU resources to reduce costs")
        
        if memory_usage < 20:
            recommendations.append("Consider scaling down memory resources to reduce costs")
        
        if not recommendations:
            recommendations.append("Resource usage is optimal")
        
        return recommendations
    
    def _generate_cost_recommendations(self, optimizations: List[Dict[str, Any]]) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        for opt in optimizations:
            if opt['savings_percentage'] > 20:
                recommendations.append(f"High savings potential in {opt['category']}: {opt['savings_percentage']:.1f}%")
            elif opt['savings_percentage'] > 10:
                recommendations.append(f"Moderate savings potential in {opt['category']}: {opt['savings_percentage']:.1f}%")
        
        return recommendations
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        duration_str = duration_str.lower()
        
        if duration_str.endswith('s'):
            return int(duration_str[:-1])
        elif duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith('d'):
            return int(duration_str[:-1]) * 86400
        else:
            # Assume minutes
            return int(duration_str) * 60
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration to human readable string"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _assess_risk(self, pod_data: Dict[str, Any]) -> str:
        """Assess risk level for zero-pod scaling"""
        # Simple risk assessment based on pod characteristics
        critical_services = ['database', 'cache', 'load-balancer', 'monitoring']
        pod_name = pod_data.get('deployment', '').lower()
        
        for service in critical_services:
            if service in pod_name:
                return 'high'
        
        # Check if it's a production namespace
        namespace = pod_data.get('namespace', '').lower()
        if 'prod' in namespace or 'production' in namespace:
            return 'medium'
        
        return 'low'
