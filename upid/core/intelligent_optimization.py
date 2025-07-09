"""
Intelligent Optimization Engine
Automatically optimizes resource allocation, scaling policies, and cost efficiency.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimizations that can be performed."""
    RESOURCE_ALLOCATION = "resource_allocation"
    SCALING_POLICY = "scaling_policy"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_TUNING = "performance_tuning"
    CAPACITY_PLANNING = "capacity_planning"


@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation."""
    optimization_type: OptimizationType
    target_resource: str
    current_value: float
    recommended_value: float
    expected_improvement: float  # Percentage
    confidence: float  # 0 to 1
    priority: str  # low, medium, high, critical
    description: str
    implementation_steps: List[str]
    risk_assessment: str


@dataclass
class ResourceProfile:
    """Represents a resource usage profile."""
    resource_name: str
    current_usage: float
    peak_usage: float
    average_usage: float
    utilization_efficiency: float  # 0 to 1
    optimization_potential: float  # 0 to 1
    recommendations: List[str]


class IntelligentOptimizationEngine:
    """
    Intelligent Optimization Engine that automatically optimizes Kubernetes resources.
    """
    
    def __init__(self):
        self.optimization_threshold = 0.1  # 10% improvement threshold
        self.confidence_threshold = 0.7
        self.cost_optimization_weight = 0.4
        self.performance_weight = 0.3
        self.reliability_weight = 0.3
        
    async def analyze_resource_profiles(
        self, 
        current_metrics: Dict[str, Any],
        historical_data: Dict[str, List[float]]
    ) -> List[ResourceProfile]:
        """
        Analyze resource usage profiles to identify optimization opportunities.
        
        Args:
            current_metrics: Current Kubernetes metrics
            historical_data: Historical metrics data
            
        Returns:
            List of resource profiles with optimization recommendations
        """
        logger.info("Starting resource profile analysis")
        
        profiles = []
        
        # Analyze CPU profile
        if 'cpu_usage' in current_metrics:
            cpu_profile = await self._analyze_cpu_profile(
                current_metrics['cpu_usage'], historical_data.get('cpu', [])
            )
            if cpu_profile:
                profiles.append(cpu_profile)
        
        # Analyze memory profile
        if 'memory_usage' in current_metrics:
            memory_profile = await self._analyze_memory_profile(
                current_metrics['memory_usage'], historical_data.get('memory', [])
            )
            if memory_profile:
                profiles.append(memory_profile)
        
        # Analyze pod scaling profile
        if 'pod_count' in current_metrics:
            pod_profile = await self._analyze_pod_profile(
                current_metrics['pod_count'], historical_data.get('pods', [])
            )
            if pod_profile:
                profiles.append(pod_profile)
        
        logger.info(f"Generated {len(profiles)} resource profiles")
        return profiles
    
    async def _analyze_cpu_profile(
        self, 
        current_cpu: Dict[str, Any], 
        historical_cpu: List[float]
    ) -> Optional[ResourceProfile]:
        """Analyze CPU usage profile for optimization opportunities."""
        if not historical_cpu or 'average' not in current_cpu:
            return None
        
        current_usage = current_cpu['average']
        peak_usage = max(historical_cpu) if historical_cpu else current_usage
        average_usage = sum(historical_cpu) / len(historical_cpu) if historical_cpu else current_usage
        
        # Calculate utilization efficiency
        efficiency = self._calculate_efficiency(current_usage, peak_usage)
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(
            current_usage, average_usage, peak_usage
        )
        
        recommendations = []
        if current_usage < 30:
            recommendations.append("Consider reducing CPU requests to optimize costs")
        elif current_usage > 80:
            recommendations.append("Consider increasing CPU limits to prevent throttling")
        
        if peak_usage > 90:
            recommendations.append("Monitor for CPU bottlenecks during peak usage")
        
        return ResourceProfile(
            resource_name="CPU",
            current_usage=current_usage,
            peak_usage=peak_usage,
            average_usage=average_usage,
            utilization_efficiency=efficiency,
            optimization_potential=optimization_potential,
            recommendations=recommendations
        )
    
    async def _analyze_memory_profile(
        self, 
        current_memory: Dict[str, Any], 
        historical_memory: List[float]
    ) -> Optional[ResourceProfile]:
        """Analyze memory usage profile for optimization opportunities."""
        if not historical_memory or 'average' not in current_memory:
            return None
        
        current_usage = current_memory['average']
        peak_usage = max(historical_memory) if historical_memory else current_usage
        average_usage = sum(historical_memory) / len(historical_memory) if historical_memory else current_usage
        
        # Calculate utilization efficiency
        efficiency = self._calculate_efficiency(current_usage, peak_usage)
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(
            current_usage, average_usage, peak_usage
        )
        
        recommendations = []
        if current_usage < 40:
            recommendations.append("Consider reducing memory requests to optimize costs")
        elif current_usage > 85:
            recommendations.append("Consider increasing memory limits to prevent OOM")
        
        if peak_usage > 95:
            recommendations.append("Monitor for memory pressure during peak usage")
        
        return ResourceProfile(
            resource_name="Memory",
            current_usage=current_usage,
            peak_usage=peak_usage,
            average_usage=average_usage,
            utilization_efficiency=efficiency,
            optimization_potential=optimization_potential,
            recommendations=recommendations
        )
    
    async def _analyze_pod_profile(
        self, 
        current_pods: Dict[str, Any], 
        historical_pods: List[float]
    ) -> Optional[ResourceProfile]:
        """Analyze pod scaling profile for optimization opportunities."""
        if not historical_pods or 'count' not in current_pods:
            return None
        
        current_count = current_pods['count']
        peak_count = max(historical_pods) if historical_pods else current_count
        average_count = sum(historical_pods) / len(historical_pods) if historical_pods else current_count
        
        # Calculate utilization efficiency
        efficiency = self._calculate_efficiency(current_count, peak_count)
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(
            current_count, average_count, peak_count
        )
        
        recommendations = []
        if current_count < average_count * 0.7:
            recommendations.append("Consider reducing minimum replicas to optimize costs")
        elif current_count > average_count * 1.3:
            recommendations.append("Review scaling policies for over-provisioning")
        
        return ResourceProfile(
            resource_name="Pods",
            current_usage=current_count,
            peak_usage=peak_count,
            average_usage=average_count,
            utilization_efficiency=efficiency,
            optimization_potential=optimization_potential,
            recommendations=recommendations
        )
    
    async def generate_optimization_recommendations(
        self, 
        resource_profiles: List[ResourceProfile],
        cost_data: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationRecommendation]:
        """
        Generate optimization recommendations based on resource profiles.
        
        Args:
            resource_profiles: List of resource profiles
            cost_data: Optional cost data for cost optimization
            
        Returns:
            List of optimization recommendations
        """
        logger.info("Generating optimization recommendations")
        
        recommendations = []
        
        for profile in resource_profiles:
            if profile.optimization_potential > self.optimization_threshold:
                recommendation = await self._create_optimization_recommendation(profile, cost_data)
                if recommendation:
                    recommendations.append(recommendation)
        
        # Add cost optimization recommendations if cost data is available
        if cost_data:
            cost_recommendations = await self._generate_cost_optimizations(cost_data, resource_profiles)
            recommendations.extend(cost_recommendations)
        
        # Sort by priority and expected improvement
        recommendations.sort(key=lambda r: (self._priority_score(r.priority), r.expected_improvement), reverse=True)
        
        logger.info(f"Generated {len(recommendations)} optimization recommendations")
        return recommendations
    
    async def _create_optimization_recommendation(
        self, 
        profile: ResourceProfile,
        cost_data: Optional[Dict[str, Any]]
    ) -> Optional[OptimizationRecommendation]:
        """Create an optimization recommendation for a resource profile."""
        
        if profile.resource_name == "CPU":
            return await self._create_cpu_optimization(profile, cost_data)
        elif profile.resource_name == "Memory":
            return await self._create_memory_optimization(profile, cost_data)
        elif profile.resource_name == "Pods":
            return await self._create_pod_optimization(profile, cost_data)
        
        return None
    
    async def _create_cpu_optimization(
        self, 
        profile: ResourceProfile,
        cost_data: Optional[Dict[str, Any]]
    ) -> OptimizationRecommendation:
        """Create CPU optimization recommendation."""
        
        if profile.current_usage < 30:
            # Under-utilization: recommend reducing requests
            recommended_value = profile.current_usage * 1.2  # 20% buffer
            improvement = (profile.current_usage - recommended_value) / profile.current_usage * 100
            
            return OptimizationRecommendation(
                optimization_type=OptimizationType.RESOURCE_ALLOCATION,
                target_resource="CPU Requests",
                current_value=profile.current_usage,
                recommended_value=recommended_value,
                expected_improvement=improvement,
                confidence=0.85,
                priority="medium",
                description=f"Reduce CPU requests from {profile.current_usage:.1f}% to {recommended_value:.1f}%",
                implementation_steps=[
                    "Review current CPU requests in deployment specs",
                    "Reduce CPU requests by 20-30%",
                    "Monitor performance after changes",
                    "Adjust based on actual usage patterns"
                ],
                risk_assessment="Low risk - conservative reduction with monitoring"
            )
        
        elif profile.current_usage > 80:
            # Over-utilization: recommend increasing limits
            recommended_value = min(100, profile.current_usage * 1.1)  # 10% increase
            improvement = (recommended_value - profile.current_usage) / profile.current_usage * 100
            
            return OptimizationRecommendation(
                optimization_type=OptimizationType.PERFORMANCE_TUNING,
                target_resource="CPU Limits",
                current_value=profile.current_usage,
                recommended_value=recommended_value,
                expected_improvement=improvement,
                confidence=0.90,
                priority="high",
                description=f"Increase CPU limits to {recommended_value:.1f}% to prevent throttling",
                implementation_steps=[
                    "Review current CPU limits in deployment specs",
                    "Increase CPU limits by 10-15%",
                    "Monitor for throttling events",
                    "Consider horizontal scaling if needed"
                ],
                risk_assessment="Medium risk - monitor for resource contention"
            )
        
        return None
    
    async def _create_memory_optimization(
        self, 
        profile: ResourceProfile,
        cost_data: Optional[Dict[str, Any]]
    ) -> OptimizationRecommendation:
        """Create memory optimization recommendation."""
        
        if profile.current_usage < 40:
            # Under-utilization: recommend reducing requests
            recommended_value = profile.current_usage * 1.3  # 30% buffer
            improvement = (profile.current_usage - recommended_value) / profile.current_usage * 100
            
            return OptimizationRecommendation(
                optimization_type=OptimizationType.RESOURCE_ALLOCATION,
                target_resource="Memory Requests",
                current_value=profile.current_usage,
                recommended_value=recommended_value,
                expected_improvement=improvement,
                confidence=0.80,
                priority="medium",
                description=f"Reduce memory requests from {profile.current_usage:.1f}% to {recommended_value:.1f}%",
                implementation_steps=[
                    "Review current memory requests in deployment specs",
                    "Reduce memory requests by 25-35%",
                    "Monitor for OOM events",
                    "Adjust based on actual usage patterns"
                ],
                risk_assessment="Medium risk - monitor for memory pressure"
            )
        
        elif profile.current_usage > 85:
            # Over-utilization: recommend increasing limits
            recommended_value = min(100, profile.current_usage * 1.15)  # 15% increase
            improvement = (recommended_value - profile.current_usage) / profile.current_usage * 100
            
            return OptimizationRecommendation(
                optimization_type=OptimizationType.PERFORMANCE_TUNING,
                target_resource="Memory Limits",
                current_value=profile.current_usage,
                recommended_value=recommended_value,
                expected_improvement=improvement,
                confidence=0.95,
                priority="critical",
                description=f"Increase memory limits to {recommended_value:.1f}% to prevent OOM",
                implementation_steps=[
                    "Review current memory limits in deployment specs",
                    "Increase memory limits by 15-20%",
                    "Monitor for OOM events",
                    "Consider memory optimization in application code"
                ],
                risk_assessment="High risk - immediate action required"
            )
        
        return None
    
    async def _create_pod_optimization(
        self, 
        profile: ResourceProfile,
        cost_data: Optional[Dict[str, Any]]
    ) -> OptimizationRecommendation:
        """Create pod scaling optimization recommendation."""
        
        if profile.current_usage < profile.average_usage * 0.7:
            # Under-utilization: recommend reducing minimum replicas
            recommended_value = max(1, profile.current_usage * 0.8)
            improvement = (profile.current_usage - recommended_value) / profile.current_usage * 100
            
            return OptimizationRecommendation(
                optimization_type=OptimizationType.SCALING_POLICY,
                target_resource="Minimum Replicas",
                current_value=profile.current_usage,
                recommended_value=recommended_value,
                expected_improvement=improvement,
                confidence=0.75,
                priority="low",
                description=f"Reduce minimum replicas from {profile.current_usage:.0f} to {recommended_value:.0f}",
                implementation_steps=[
                    "Review current HPA configuration",
                    "Reduce minimum replicas by 20-30%",
                    "Monitor scaling behavior",
                    "Adjust based on traffic patterns"
                ],
                risk_assessment="Low risk - conservative scaling with monitoring"
            )
        
        return None
    
    async def _generate_cost_optimizations(
        self, 
        cost_data: Dict[str, Any],
        resource_profiles: List[ResourceProfile]
    ) -> List[OptimizationRecommendation]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Analyze cost per resource
        if 'cost_per_cpu' in cost_data and 'cost_per_memory' in cost_data:
            cpu_cost = cost_data['cost_per_cpu']
            memory_cost = cost_data['cost_per_memory']
            
            # Find under-utilized resources for cost optimization
            for profile in resource_profiles:
                if profile.optimization_potential > 0.2:  # 20% optimization potential
                    if profile.resource_name == "CPU" and profile.current_usage < 40:
                        cost_savings = (40 - profile.current_usage) * cpu_cost
                        
                        recommendations.append(OptimizationRecommendation(
                            optimization_type=OptimizationType.COST_OPTIMIZATION,
                            target_resource="CPU Cost",
                            current_value=profile.current_usage * cpu_cost,
                            recommended_value=(profile.current_usage * 0.8) * cpu_cost,
                            expected_improvement=cost_savings,
                            confidence=0.80,
                            priority="medium",
                            description=f"Potential cost savings of ${cost_savings:.2f} by optimizing CPU usage",
                            implementation_steps=[
                                "Review CPU requests and limits",
                                "Implement resource quotas",
                                "Monitor cost impact",
                                "Consider spot instances for non-critical workloads"
                            ],
                            risk_assessment="Low risk - gradual optimization with monitoring"
                        ))
        
        return recommendations
    
    def _calculate_efficiency(self, current: float, peak: float) -> float:
        """Calculate utilization efficiency."""
        if peak == 0:
            return 0.0
        return min(1.0, current / peak)
    
    def _calculate_optimization_potential(
        self, 
        current: float, 
        average: float, 
        peak: float
    ) -> float:
        """Calculate optimization potential based on usage patterns."""
        if peak == 0:
            return 0.0
        
        # Calculate potential based on variance from average
        variance = abs(current - average) / max(average, 1.0)
        
        # Higher variance = higher optimization potential
        return min(1.0, variance)
    
    def _priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score."""
        priority_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        return priority_map.get(priority, 1)
    
    async def generate_optimization_report(
        self, 
        profiles: List[ResourceProfile],
        recommendations: List[OptimizationRecommendation]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report.
        
        Args:
            profiles: List of resource profiles
            recommendations: List of optimization recommendations
            
        Returns:
            Dictionary containing the optimization report
        """
        total_savings = sum(r.expected_improvement for r in recommendations if r.optimization_type == OptimizationType.COST_OPTIMIZATION)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "resource_profiles": {
                "total": len(profiles),
                "profiles": [
                    {
                        "resource": profile.resource_name,
                        "current_usage": profile.current_usage,
                        "peak_usage": profile.peak_usage,
                        "average_usage": profile.average_usage,
                        "efficiency": profile.utilization_efficiency,
                        "optimization_potential": profile.optimization_potential,
                        "recommendations": profile.recommendations
                    }
                    for profile in profiles
                ]
            },
            "optimization_recommendations": {
                "total": len(recommendations),
                "by_type": {
                    opt_type.value: len([r for r in recommendations if r.optimization_type == opt_type])
                    for opt_type in OptimizationType
                },
                "by_priority": {
                    "critical": len([r for r in recommendations if r.priority == "critical"]),
                    "high": len([r for r in recommendations if r.priority == "high"]),
                    "medium": len([r for r in recommendations if r.priority == "medium"]),
                    "low": len([r for r in recommendations if r.priority == "low"])
                },
                "estimated_savings": total_savings,
                "details": [
                    {
                        "type": rec.optimization_type.value,
                        "target": rec.target_resource,
                        "current_value": rec.current_value,
                        "recommended_value": rec.recommended_value,
                        "improvement": rec.expected_improvement,
                        "confidence": rec.confidence,
                        "priority": rec.priority,
                        "description": rec.description,
                        "implementation_steps": rec.implementation_steps,
                        "risk_assessment": rec.risk_assessment
                    }
                    for rec in recommendations
                ]
            },
            "summary": {
                "status": "optimization_needed" if recommendations else "well_optimized",
                "key_insights": [
                    f"Found {len(profiles)} resource profiles",
                    f"Generated {len(recommendations)} optimization recommendations",
                    f"Estimated savings: ${total_savings:.2f}" if total_savings > 0 else "No cost savings identified"
                ]
            }
        } 