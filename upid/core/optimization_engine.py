"""
Confidence-Based Optimization Engine for UPID
Provides safe, risk-assessed optimization recommendations with simulation capabilities
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types of optimizations"""
    ZERO_POD_SCALING = "zero_pod_scaling"
    BUSINESS_HOURS_SCALING = "business_hours_scaling"
    MEMORY_OPTIMIZATION = "memory_optimization"
    CPU_OPTIMIZATION = "cpu_optimization"
    STORAGE_OPTIMIZATION = "storage_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    CAPACITY_PLANNING = "capacity_planning"

class RiskLevel(Enum):
    """Risk levels for optimizations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation with confidence and risk assessment"""
    type: OptimizationType
    description: str
    confidence: float  # 0-100
    risk_level: RiskLevel
    potential_savings: float  # Percentage
    implementation_effort: str  # low/medium/high
    safety_boundaries: Dict[str, Any]
    rollback_plan: Dict[str, Any]
    business_impact: Dict[str, Any]
    simulation_results: Optional[Dict[str, Any]] = None

class ConfidenceOptimizationEngine:
    """Confidence-based optimization engine with safety controls"""
    
    def __init__(self):
        """Initialize the optimization engine"""
        self.confidence_thresholds = {
            'low_risk': 70.0,
            'medium_risk': 85.0,
            'high_risk': 95.0,
            'critical_risk': 99.0
        }
        
        self.safety_boundaries = {
            'max_cpu_reduction': 0.30,  # 30% max CPU reduction
            'max_memory_reduction': 0.25,  # 25% max memory reduction
            'min_pod_count': 1,  # Minimum pods to keep running
            'max_rollback_time': 300,  # 5 minutes max rollback time
            'performance_degradation_threshold': 0.10  # 10% max performance impact
        }
    
    def generate_optimization_plan(self, analysis: Dict[str, Any], 
                                 cluster_info: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate confidence-based optimization recommendations"""
        recommendations = []
        
        try:
            # Process patterns for optimization opportunities
            if 'patterns' in analysis:
                for resource, patterns in analysis['patterns'].items():
                    resource_recs = self._analyze_resource_patterns(resource, patterns, cluster_info)
                    recommendations.extend(resource_recs)
            
            # Process trends for capacity planning
            if 'trends' in analysis:
                trend_recs = self._analyze_trends_for_planning(analysis['trends'], cluster_info)
                recommendations.extend(trend_recs)
            
            # Process anomalies for immediate actions
            if 'anomalies' in analysis:
                anomaly_recs = self._analyze_anomalies_for_action(analysis['anomalies'], cluster_info)
                recommendations.extend(anomaly_recs)
            
            # Sort by confidence and potential savings
            recommendations.sort(key=lambda x: (x.confidence * x.potential_savings), reverse=True)
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            
        except Exception as e:
            logger.error(f"Error generating optimization plan: {e}")
        
        return recommendations
    
    def _analyze_resource_patterns(self, resource: str, patterns: Dict[str, Any], 
                                 cluster_info: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze resource patterns for optimization opportunities"""
        recommendations = []
        
        # Idle periods optimization
        if 'idle_periods' in patterns:
            idle_data = patterns['idle_periods']
            if idle_data['idle_percentage'] > 50 and idle_data['confidence'] > 70:
                rec = self._create_zero_pod_scaling_recommendation(idle_data, cluster_info)
                recommendations.append(rec)
        
        # Business hours pattern optimization
        if 'business_hours_pattern' in patterns:
            business_data = patterns['business_hours_pattern']
            if business_data['ratio'] > 1.5 and business_data['confidence'] > 60:
                rec = self._create_business_hours_scaling_recommendation(business_data, cluster_info)
                recommendations.append(rec)
        
        # Memory leak optimization
        if 'memory_leak' in patterns:
            leak_data = patterns['memory_leak']
            if leak_data['confidence'] > 80:
                rec = self._create_memory_optimization_recommendation(leak_data, cluster_info)
                recommendations.append(rec)
        
        # Memory pressure optimization
        if 'memory_pressure' in patterns:
            pressure_data = patterns['memory_pressure']
            if pressure_data['high_usage_percentage'] > 30:
                rec = self._create_memory_scaling_recommendation(pressure_data, cluster_info)
                recommendations.append(rec)
        
        return recommendations
    
    def _analyze_trends_for_planning(self, trends: Dict[str, Any], 
                                   cluster_info: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze trends for capacity planning"""
        recommendations = []
        
        for resource, trend in trends.items():
            if trend and trend['direction'] == 'increasing' and trend['strength'] > 0.5:
                rec = self._create_capacity_planning_recommendation(resource, trend, cluster_info)
                recommendations.append(rec)
        
        return recommendations
    
    def _analyze_anomalies_for_action(self, anomalies: Dict[str, Any], 
                                    cluster_info: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze anomalies for immediate optimization actions"""
        recommendations = []
        
        for resource, resource_anomalies in anomalies.items():
            if len(resource_anomalies) > 10:  # Significant number of anomalies
                rec = self._create_anomaly_optimization_recommendation(resource, resource_anomalies, cluster_info)
                recommendations.append(rec)
        
        return recommendations
    
    def _create_zero_pod_scaling_recommendation(self, idle_data: Dict[str, Any], 
                                              cluster_info: Dict[str, Any]) -> OptimizationRecommendation:
        """Create zero-pod scaling recommendation"""
        confidence = idle_data['confidence']
        idle_percentage = idle_data['idle_percentage']
        
        # Calculate potential savings
        potential_savings = idle_percentage / 100 * 0.8  # 80% of idle time as savings
        
        # Determine risk level based on confidence
        risk_level = self._calculate_risk_level(confidence, 'low_risk')
        
        # Safety boundaries
        safety_boundaries = {
            'max_idle_threshold': 70,  # Only scale to zero if >70% idle
            'min_pod_count': 1,
            'warmup_time': 60,  # 1 minute warmup time
            'cooldown_time': 300,  # 5 minutes cooldown
            'max_scale_down_percentage': 50  # Max 50% scale down at once
        }
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': ['high_cpu_usage', 'high_memory_usage', 'error_rate_increase'],
            'rollback_time': 60,  # 1 minute rollback
            'restore_pods': True,
            'notify_team': True
        }
        
        # Business impact
        business_impact = {
            'cost_savings_percentage': potential_savings * 100,
            'availability_impact': 'minimal',
            'performance_impact': 'minimal',
            'implementation_time': 'immediate'
        }
        
        return OptimizationRecommendation(
            type=OptimizationType.ZERO_POD_SCALING,
            description=f"Scale pods to zero during {idle_percentage:.1f}% idle periods",
            confidence=confidence,
            risk_level=risk_level,
            potential_savings=potential_savings,
            implementation_effort='low',
            safety_boundaries=safety_boundaries,
            rollback_plan=rollback_plan,
            business_impact=business_impact
        )
    
    def _create_business_hours_scaling_recommendation(self, business_data: Dict[str, Any], 
                                                    cluster_info: Dict[str, Any]) -> OptimizationRecommendation:
        """Create business hours scaling recommendation"""
        confidence = business_data['confidence']
        ratio = business_data['ratio']
        
        # Calculate potential savings
        potential_savings = min(0.25, (ratio - 1) / ratio * 0.8)  # Max 25% savings
        
        # Determine risk level
        risk_level = self._calculate_risk_level(confidence, 'medium_risk')
        
        # Safety boundaries
        safety_boundaries = {
            'business_hours_start': '09:00',
            'business_hours_end': '18:00',
            'weekdays_only': True,
            'min_pod_count_business': 2,
            'min_pod_count_off_hours': 1,
            'scale_up_buffer': 300,  # 5 minutes before business hours
            'scale_down_buffer': 600  # 10 minutes after business hours
        }
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': ['high_traffic_during_off_hours', 'performance_degradation'],
            'rollback_time': 120,  # 2 minutes rollback
            'restore_full_capacity': True,
            'notify_team': True
        }
        
        # Business impact
        business_impact = {
            'cost_savings_percentage': potential_savings * 100,
            'availability_impact': 'minimal',
            'performance_impact': 'minimal',
            'implementation_time': 'scheduled'
        }
        
        return OptimizationRecommendation(
            type=OptimizationType.BUSINESS_HOURS_SCALING,
            description=f"Implement time-based scaling (business hours {ratio:.1f}x higher usage)",
            confidence=confidence,
            risk_level=risk_level,
            potential_savings=potential_savings,
            implementation_effort='medium',
            safety_boundaries=safety_boundaries,
            rollback_plan=rollback_plan,
            business_impact=business_impact
        )
    
    def _create_memory_optimization_recommendation(self, leak_data: Dict[str, Any], 
                                                 cluster_info: Dict[str, Any]) -> OptimizationRecommendation:
        """Create memory optimization recommendation"""
        confidence = leak_data['confidence']
        slope = leak_data['slope']
        
        # Calculate potential savings
        potential_savings = min(0.15, slope * 0.1)  # Max 15% savings
        
        # Determine risk level
        risk_level = self._calculate_risk_level(confidence, 'high_risk')
        
        # Safety boundaries
        safety_boundaries = {
            'max_memory_reduction': 0.20,  # Max 20% memory reduction
            'memory_pressure_threshold': 0.85,  # 85% memory usage threshold
            'restart_threshold': 0.95,  # 95% memory usage triggers restart
            'monitoring_interval': 60  # 1 minute monitoring
        }
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': ['memory_pressure', 'performance_degradation', 'error_rate_increase'],
            'rollback_time': 180,  # 3 minutes rollback
            'restart_services': True,
            'notify_team': True
        }
        
        # Business impact
        business_impact = {
            'cost_savings_percentage': potential_savings * 100,
            'availability_impact': 'low',
            'performance_impact': 'improvement',
            'implementation_time': 'scheduled'
        }
        
        return OptimizationRecommendation(
            type=OptimizationType.MEMORY_OPTIMIZATION,
            description=f"Optimize memory usage (detected leak with {slope:.2f} slope)",
            confidence=confidence,
            risk_level=risk_level,
            potential_savings=potential_savings,
            implementation_effort='high',
            safety_boundaries=safety_boundaries,
            rollback_plan=rollback_plan,
            business_impact=business_impact
        )
    
    def _create_memory_scaling_recommendation(self, pressure_data: Dict[str, Any], 
                                            cluster_info: Dict[str, Any]) -> OptimizationRecommendation:
        """Create memory scaling recommendation"""
        confidence = pressure_data['confidence']
        high_usage_percentage = pressure_data['high_usage_percentage']
        
        # This is a cost increase, not savings
        potential_savings = -0.05  # 5% cost increase for better performance
        
        # Determine risk level
        risk_level = self._calculate_risk_level(confidence, 'medium_risk')
        
        # Safety boundaries
        safety_boundaries = {
            'memory_increase_percentage': 0.25,  # 25% memory increase
            'monitoring_period': 3600,  # 1 hour monitoring before scaling
            'auto_scale_threshold': 0.80,  # 80% usage triggers scaling
            'max_scale_up_percentage': 0.50  # Max 50% scale up
        }
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': ['cost_exceeded', 'performance_not_improved'],
            'rollback_time': 300,  # 5 minutes rollback
            'scale_down_memory': True,
            'notify_team': True
        }
        
        # Business impact
        business_impact = {
            'cost_increase_percentage': 5.0,
            'availability_impact': 'improvement',
            'performance_impact': 'significant_improvement',
            'implementation_time': 'immediate'
        }
        
        return OptimizationRecommendation(
            type=OptimizationType.MEMORY_OPTIMIZATION,
            description=f"Scale up memory to address {high_usage_percentage:.1f}% high usage periods",
            confidence=confidence,
            risk_level=risk_level,
            potential_savings=potential_savings,
            implementation_effort='medium',
            safety_boundaries=safety_boundaries,
            rollback_plan=rollback_plan,
            business_impact=business_impact
        )
    
    def _create_capacity_planning_recommendation(self, resource: str, trend: Dict[str, Any], 
                                               cluster_info: Dict[str, Any]) -> OptimizationRecommendation:
        """Create capacity planning recommendation"""
        confidence = trend['confidence']
        strength = trend['strength']
        
        # No immediate savings, but prevents future issues
        potential_savings = 0.0
        
        # Determine risk level
        risk_level = self._calculate_risk_level(confidence, 'low_risk')
        
        # Safety boundaries
        safety_boundaries = {
            'planning_horizon_days': 30,
            'capacity_buffer_percentage': 0.20,  # 20% buffer
            'monitoring_frequency': 3600,  # 1 hour monitoring
            'alert_threshold': 0.85  # 85% usage alert
        }
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': ['trend_reversal', 'unexpected_usage_drop'],
            'rollback_time': 0,  # No rollback needed for planning
            'adjust_plan': True,
            'notify_team': True
        }
        
        # Business impact
        business_impact = {
            'cost_impact': 'planning_only',
            'availability_impact': 'improvement',
            'performance_impact': 'prevention',
            'implementation_time': 'planned'
        }
        
        return OptimizationRecommendation(
            type=OptimizationType.CAPACITY_PLANNING,
            description=f"Plan capacity increase for {resource} (strong {trend['direction']} trend)",
            confidence=confidence,
            risk_level=risk_level,
            potential_savings=potential_savings,
            implementation_effort='high',
            safety_boundaries=safety_boundaries,
            rollback_plan=rollback_plan,
            business_impact=business_impact
        )
    
    def _create_anomaly_optimization_recommendation(self, resource: str, anomalies: List[Dict[str, Any]], 
                                                  cluster_info: Dict[str, Any]) -> OptimizationRecommendation:
        """Create anomaly-based optimization recommendation"""
        # Calculate confidence based on anomaly frequency
        confidence = min(90, len(anomalies) * 5)  # Max 90% confidence
        
        # Calculate potential savings
        potential_savings = min(0.10, len(anomalies) / 100)  # Max 10% savings
        
        # Determine risk level
        risk_level = self._calculate_risk_level(confidence, 'medium_risk')
        
        # Safety boundaries
        safety_boundaries = {
            'anomaly_threshold': 3,  # 3 anomalies trigger action
            'monitoring_period': 3600,  # 1 hour monitoring
            'auto_correction': True,
            'manual_review_threshold': 10  # 10+ anomalies require manual review
        }
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': ['performance_degradation', 'error_rate_increase'],
            'rollback_time': 120,  # 2 minutes rollback
            'restore_previous_state': True,
            'notify_team': True
        }
        
        # Business impact
        business_impact = {
            'cost_savings_percentage': potential_savings * 100,
            'availability_impact': 'improvement',
            'performance_impact': 'stabilization',
            'implementation_time': 'immediate'
        }
        
        return OptimizationRecommendation(
            type=OptimizationType.CPU_OPTIMIZATION,
            description=f"Optimize {resource} to address {len(anomalies)} detected anomalies",
            confidence=confidence,
            risk_level=risk_level,
            potential_savings=potential_savings,
            implementation_effort='medium',
            safety_boundaries=safety_boundaries,
            rollback_plan=rollback_plan,
            business_impact=business_impact
        )
    
    def _calculate_risk_level(self, confidence: float, base_threshold: str) -> RiskLevel:
        """Calculate risk level based on confidence and thresholds"""
        threshold = self.confidence_thresholds[base_threshold]
        
        if confidence >= self.confidence_thresholds['critical_risk']:
            return RiskLevel.LOW
        elif confidence >= self.confidence_thresholds['high_risk']:
            return RiskLevel.MEDIUM
        elif confidence >= self.confidence_thresholds['medium_risk']:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def simulate_optimization(self, recommendation: OptimizationRecommendation, 
                            current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the impact of an optimization"""
        simulation = {
            'recommendation_type': recommendation.type.value,
            'confidence': recommendation.confidence,
            'risk_level': recommendation.risk_level.value,
            'simulation_results': {},
            'safety_checks': {},
            'rollback_scenario': {}
        }
        
        try:
            # Simulate based on optimization type
            if recommendation.type == OptimizationType.ZERO_POD_SCALING:
                simulation['simulation_results'] = self._simulate_zero_pod_scaling(recommendation, current_metrics)
            elif recommendation.type == OptimizationType.BUSINESS_HOURS_SCALING:
                simulation['simulation_results'] = self._simulate_business_hours_scaling(recommendation, current_metrics)
            elif recommendation.type == OptimizationType.MEMORY_OPTIMIZATION:
                simulation['simulation_results'] = self._simulate_memory_optimization(recommendation, current_metrics)
            
            # Run safety checks
            simulation['safety_checks'] = self._run_safety_checks(recommendation, current_metrics)
            
            # Simulate rollback scenario
            simulation['rollback_scenario'] = self._simulate_rollback(recommendation, current_metrics)
            
        except Exception as e:
            logger.error(f"Error simulating optimization: {e}")
            simulation['error'] = str(e)
        
        return simulation
    
    def _simulate_zero_pod_scaling(self, recommendation: OptimizationRecommendation, 
                                 current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate zero-pod scaling impact"""
        idle_percentage = recommendation.potential_savings * 100
        
        return {
            'cost_savings': idle_percentage * 0.8,  # 80% of idle time as savings
            'performance_impact': 'minimal',
            'availability_impact': 'minimal',
            'warmup_time_seconds': 60,
            'cooldown_time_seconds': 300,
            'estimated_monthly_savings': idle_percentage * 0.8 * 30,  # Monthly projection
            'risk_factors': ['cold_start_latency', 'service_discovery_delay']
        }
    
    def _simulate_business_hours_scaling(self, recommendation: OptimizationRecommendation, 
                                       current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate business hours scaling impact"""
        savings_percentage = recommendation.potential_savings * 100
        
        return {
            'cost_savings': savings_percentage,
            'performance_impact': 'minimal',
            'availability_impact': 'minimal',
            'scale_up_time_seconds': 120,
            'scale_down_time_seconds': 300,
            'estimated_monthly_savings': savings_percentage * 30,
            'risk_factors': ['timezone_mismatch', 'holiday_schedules']
        }
    
    def _simulate_memory_optimization(self, recommendation: OptimizationRecommendation, 
                                    current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate memory optimization impact"""
        savings_percentage = recommendation.potential_savings * 100
        
        return {
            'cost_savings': savings_percentage,
            'performance_impact': 'improvement',
            'availability_impact': 'improvement',
            'restart_time_seconds': 180,
            'monitoring_period_hours': 24,
            'estimated_monthly_savings': savings_percentage * 30,
            'risk_factors': ['service_restart', 'memory_leak_recurrence']
        }
    
    def _run_safety_checks(self, recommendation: OptimizationRecommendation, 
                          current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Run safety checks for the optimization"""
        checks = {
            'passed': True,
            'warnings': [],
            'blockers': []
        }
        
        # Check confidence threshold
        if recommendation.confidence < self.confidence_thresholds['low_risk']:
            checks['warnings'].append(f"Low confidence ({recommendation.confidence:.1f}%)")
        
        # Check risk level
        if recommendation.risk_level == RiskLevel.CRITICAL:
            checks['blockers'].append("Critical risk level - manual review required")
            checks['passed'] = False
        
        # Check safety boundaries
        if 'max_cpu_reduction' in recommendation.safety_boundaries:
            current_cpu = current_metrics.get('cpu_utilization', 0)
            if current_cpu > 80:
                checks['warnings'].append("High CPU usage - consider gradual optimization")
        
        # Check business impact
        if recommendation.business_impact.get('availability_impact') == 'high':
            checks['warnings'].append("High availability impact - proceed with caution")
        
        return checks
    
    def _simulate_rollback(self, recommendation: OptimizationRecommendation, 
                          current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate rollback scenario"""
        return {
            'rollback_time_seconds': recommendation.rollback_plan.get('rollback_time', 300),
            'trigger_conditions': recommendation.rollback_plan.get('trigger_conditions', []),
            'restore_actions': recommendation.rollback_plan.get('restore_pods', False),
            'notification_required': recommendation.rollback_plan.get('notify_team', True),
            'estimated_downtime_seconds': 60,  # 1 minute estimated downtime
            'data_loss_risk': 'minimal'
        } 