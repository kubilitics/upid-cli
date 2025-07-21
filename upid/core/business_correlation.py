"""
Business Impact Correlation Engine for UPID
Connects technical Kubernetes metrics to business outcomes and financial impact
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BusinessMetric(Enum):
    """Types of business metrics"""
    REVENUE_PER_POD = "revenue_per_pod"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    SLA_COMPLIANCE = "sla_compliance"
    ERROR_RATE_IMPACT = "error_rate_impact"
    RESPONSE_TIME_IMPACT = "response_time_impact"
    AVAILABILITY_IMPACT = "availability_impact"

@dataclass
class BusinessImpact:
    """Business impact assessment"""
    metric_type: BusinessMetric
    technical_metric: str
    correlation_strength: float  # 0-1
    business_value: float
    confidence: float  # 0-100
    impact_description: str
    roi_estimate: float  # Return on investment percentage

class BusinessCorrelationEngine:
    """Engine for correlating technical metrics with business outcomes"""
    
    def __init__(self):
        """Initialize the business correlation engine"""
        self.correlation_thresholds = {
            'strong': 0.7,
            'moderate': 0.5,
            'weak': 0.3
        }
        
        self.business_metrics = {
            'revenue_per_pod': {
                'description': 'Revenue generated per pod',
                'unit': 'USD/pod/day',
                'correlation_factors': ['cpu_utilization', 'memory_utilization', 'response_time']
            },
            'customer_satisfaction': {
                'description': 'Customer satisfaction score',
                'unit': 'score (1-10)',
                'correlation_factors': ['response_time', 'error_rate', 'availability']
            },
            'sla_compliance': {
                'description': 'Service Level Agreement compliance',
                'unit': 'percentage',
                'correlation_factors': ['availability', 'response_time', 'error_rate']
            }
        }
    
    def analyze_business_impact(self, technical_metrics: Dict[str, Any], 
                              cluster_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business impact of technical metrics"""
        business_analysis = {
            'cluster_id': cluster_info.get('name', 'unknown'),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'business_impacts': [],
            'correlation_matrix': {},
            'roi_estimates': {},
            'recommendations': []
        }
        
        try:
            # Analyze revenue per pod
            revenue_impact = self._analyze_revenue_per_pod(technical_metrics, cluster_info)
            if revenue_impact:
                business_analysis['business_impacts'].append(revenue_impact)
            
            # Analyze customer satisfaction
            satisfaction_impact = self._analyze_customer_satisfaction(technical_metrics, cluster_info)
            if satisfaction_impact:
                business_analysis['business_impacts'].append(satisfaction_impact)
            
            # Analyze SLA compliance
            sla_impact = self._analyze_sla_compliance(technical_metrics, cluster_info)
            if sla_impact:
                business_analysis['business_impacts'].append(sla_impact)
            
            # Generate correlation matrix
            business_analysis['correlation_matrix'] = self._generate_correlation_matrix(technical_metrics)
            
            # Calculate ROI estimates
            business_analysis['roi_estimates'] = self._calculate_roi_estimates(business_analysis['business_impacts'])
            
            # Generate business recommendations
            business_analysis['recommendations'] = self._generate_business_recommendations(business_analysis)
            
            logger.info(f"Completed business impact analysis for cluster {cluster_info.get('name', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error analyzing business impact: {e}")
            business_analysis['error'] = str(e)
        
        return business_analysis
    
    def _analyze_revenue_per_pod(self, technical_metrics: Dict[str, Any], 
                                cluster_info: Dict[str, Any]) -> Optional[BusinessImpact]:
        """Analyze revenue per pod correlation"""
        try:
            # Extract relevant technical metrics
            cpu_utilization = technical_metrics.get('cpu_utilization', 0)
            memory_utilization = technical_metrics.get('memory_utilization', 0)
            response_time = technical_metrics.get('response_time_p95', 100)
            
            # Calculate correlation strength
            correlation_factors = []
            
            # CPU utilization correlation (higher utilization = higher revenue potential)
            if cpu_utilization > 0:
                cpu_correlation = min(1.0, cpu_utilization / 100)
                correlation_factors.append(cpu_correlation)
            
            # Memory utilization correlation
            if memory_utilization > 0:
                memory_correlation = min(1.0, memory_utilization / 100)
                correlation_factors.append(memory_correlation)
            
            # Response time correlation (lower response time = higher revenue)
            if response_time > 0:
                response_correlation = max(0, 1 - (response_time - 50) / 200)
                correlation_factors.append(response_correlation)
            
            if not correlation_factors:
                return None
            
            # Calculate average correlation strength
            correlation_strength = np.mean(correlation_factors)
            
            # Estimate revenue per pod
            base_revenue = 100  # Base revenue per pod per day
            utilization_multiplier = (cpu_utilization + memory_utilization) / 200
            performance_multiplier = max(0.5, 1 - (response_time - 50) / 200)
            
            estimated_revenue = base_revenue * utilization_multiplier * performance_multiplier
            
            # Calculate confidence based on data quality
            confidence = min(100, correlation_strength * 100)
            
            # Calculate ROI estimate
            roi_estimate = (estimated_revenue - base_revenue) / base_revenue * 100
            
            return BusinessImpact(
                metric_type=BusinessMetric.REVENUE_PER_POD,
                technical_metric='resource_utilization',
                correlation_strength=correlation_strength,
                business_value=estimated_revenue,
                confidence=confidence,
                impact_description=f"Estimated ${estimated_revenue:.2f} revenue per pod per day",
                roi_estimate=roi_estimate
            )
            
        except Exception as e:
            logger.error(f"Error analyzing revenue per pod: {e}")
            return None
    
    def _analyze_customer_satisfaction(self, technical_metrics: Dict[str, Any], 
                                     cluster_info: Dict[str, Any]) -> Optional[BusinessImpact]:
        """Analyze customer satisfaction correlation"""
        try:
            # Extract relevant technical metrics
            response_time = technical_metrics.get('response_time_p95', 100)
            error_rate = technical_metrics.get('error_rate', 0.01)
            availability = technical_metrics.get('availability', 99.9)
            
            # Calculate correlation factors
            correlation_factors = []
            
            # Response time impact (lower = better satisfaction)
            if response_time > 0:
                response_satisfaction = max(0, 1 - (response_time - 50) / 200)
                correlation_factors.append(response_satisfaction)
            
            # Error rate impact (lower = better satisfaction)
            if error_rate > 0:
                error_satisfaction = max(0, 1 - error_rate * 100)
                correlation_factors.append(error_satisfaction)
            
            # Availability impact (higher = better satisfaction)
            if availability > 0:
                availability_satisfaction = availability / 100
                correlation_factors.append(availability_satisfaction)
            
            if not correlation_factors:
                return None
            
            # Calculate average correlation strength
            correlation_strength = np.mean(correlation_factors)
            
            # Estimate customer satisfaction score (1-10)
            base_satisfaction = 7.0  # Base satisfaction score
            performance_impact = (correlation_strength - 0.5) * 6  # ±3 points impact
            estimated_satisfaction = max(1, min(10, base_satisfaction + performance_impact))
            
            # Calculate confidence
            confidence = min(100, correlation_strength * 100)
            
            # Calculate ROI estimate (customer retention value)
            roi_estimate = (estimated_satisfaction - base_satisfaction) * 10  # 10% per satisfaction point
            
            return BusinessImpact(
                metric_type=BusinessMetric.CUSTOMER_SATISFACTION,
                technical_metric='performance_metrics',
                correlation_strength=correlation_strength,
                business_value=estimated_satisfaction,
                confidence=confidence,
                impact_description=f"Estimated {estimated_satisfaction:.1f}/10 customer satisfaction score",
                roi_estimate=roi_estimate
            )
            
        except Exception as e:
            logger.error(f"Error analyzing customer satisfaction: {e}")
            return None
    
    def _analyze_sla_compliance(self, technical_metrics: Dict[str, Any], 
                               cluster_info: Dict[str, Any]) -> Optional[BusinessImpact]:
        """Analyze SLA compliance correlation"""
        try:
            # Extract relevant technical metrics
            availability = technical_metrics.get('availability', 99.9)
            response_time = technical_metrics.get('response_time_p95', 100)
            error_rate = technical_metrics.get('error_rate', 0.01)
            
            # Define SLA targets
            sla_targets = {
                'availability': 99.95,  # 99.95% availability
                'response_time': 200,   # 200ms max response time
                'error_rate': 0.01     # 1% max error rate
            }
            
            # Calculate SLA compliance scores
            compliance_scores = []
            
            # Availability compliance
            availability_compliance = min(1.0, availability / sla_targets['availability'])
            compliance_scores.append(availability_compliance)
            
            # Response time compliance
            response_compliance = max(0, 1 - (response_time - sla_targets['response_time']) / sla_targets['response_time'])
            compliance_scores.append(response_compliance)
            
            # Error rate compliance
            error_compliance = max(0, 1 - error_rate / sla_targets['error_rate'])
            compliance_scores.append(error_compliance)
            
            if not compliance_scores:
                return None
            
            # Calculate overall SLA compliance
            overall_compliance = np.mean(compliance_scores) * 100
            correlation_strength = np.mean(compliance_scores)
            
            # Calculate confidence
            confidence = min(100, correlation_strength * 100)
            
            # Calculate ROI estimate (SLA penalty avoidance)
            sla_penalty_rate = 0.05  # 5% penalty for SLA violations
            roi_estimate = (overall_compliance - 95) * sla_penalty_rate  # 95% baseline
            
            return BusinessImpact(
                metric_type=BusinessMetric.SLA_COMPLIANCE,
                technical_metric='performance_metrics',
                correlation_strength=correlation_strength,
                business_value=overall_compliance,
                confidence=confidence,
                impact_description=f"{overall_compliance:.1f}% SLA compliance rate",
                roi_estimate=roi_estimate
            )
            
        except Exception as e:
            logger.error(f"Error analyzing SLA compliance: {e}")
            return None
    
    def _generate_correlation_matrix(self, technical_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate correlation matrix between technical and business metrics"""
        matrix = {
            'cpu_utilization': {},
            'memory_utilization': {},
            'response_time': {},
            'error_rate': {},
            'availability': {}
        }
        
        # CPU utilization correlations
        matrix['cpu_utilization'] = {
            'revenue_per_pod': 0.7,  # Higher utilization = higher revenue potential
            'customer_satisfaction': 0.3,  # Moderate impact
            'sla_compliance': 0.4   # Moderate impact
        }
        
        # Memory utilization correlations
        matrix['memory_utilization'] = {
            'revenue_per_pod': 0.6,  # Higher utilization = higher revenue potential
            'customer_satisfaction': 0.2,  # Low impact
            'sla_compliance': 0.5   # Moderate impact
        }
        
        # Response time correlations
        matrix['response_time'] = {
            'revenue_per_pod': -0.8,  # Lower response time = higher revenue
            'customer_satisfaction': -0.9,  # Strong negative correlation
            'sla_compliance': -0.7   # Strong negative correlation
        }
        
        # Error rate correlations
        matrix['error_rate'] = {
            'revenue_per_pod': -0.6,  # Lower error rate = higher revenue
            'customer_satisfaction': -0.8,  # Strong negative correlation
            'sla_compliance': -0.9   # Very strong negative correlation
        }
        
        # Availability correlations
        matrix['availability'] = {
            'revenue_per_pod': 0.5,  # Higher availability = higher revenue
            'customer_satisfaction': 0.8,  # Strong positive correlation
            'sla_compliance': 0.9    # Very strong positive correlation
        }
        
        return matrix
    
    def _calculate_roi_estimates(self, business_impacts: List[BusinessImpact]) -> Dict[str, Any]:
        """Calculate ROI estimates for business impacts"""
        roi_estimates = {
            'total_roi': 0.0,
            'breakdown': {},
            'recommendations': []
        }
        
        total_roi = 0.0
        
        for impact in business_impacts:
            roi_estimates['breakdown'][impact.metric_type.value] = {
                'roi_percentage': impact.roi_estimate,
                'business_value': impact.business_value,
                'confidence': impact.confidence
            }
            total_roi += impact.roi_estimate
        
        roi_estimates['total_roi'] = total_roi
        
        # Generate ROI-based recommendations
        if total_roi > 20:
            roi_estimates['recommendations'].append({
                'type': 'high_roi',
                'description': 'High ROI opportunity detected',
                'priority': 'high',
                'estimated_impact': f"{total_roi:.1f}% ROI potential"
            })
        elif total_roi > 10:
            roi_estimates['recommendations'].append({
                'type': 'moderate_roi',
                'description': 'Moderate ROI opportunity available',
                'priority': 'medium',
                'estimated_impact': f"{total_roi:.1f}% ROI potential"
            })
        
        return roi_estimates
    
    def _generate_business_recommendations(self, business_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business-focused recommendations"""
        recommendations = []
        
        # Analyze business impacts
        for impact in business_analysis.get('business_impacts', []):
            if impact.correlation_strength > self.correlation_thresholds['strong']:
                recommendations.append({
                    'type': 'strong_correlation',
                    'metric': impact.metric_type.value,
                    'description': f"Strong correlation detected for {impact.metric_type.value}",
                    'confidence': impact.confidence,
                    'business_value': impact.business_value,
                    'priority': 'high'
                })
            
            if impact.roi_estimate > 15:
                recommendations.append({
                    'type': 'high_roi',
                    'metric': impact.metric_type.value,
                    'description': f"High ROI opportunity: {impact.roi_estimate:.1f}% potential return",
                    'confidence': impact.confidence,
                    'business_value': impact.business_value,
                    'priority': 'high'
                })
        
        # Performance-based recommendations
        correlation_matrix = business_analysis.get('correlation_matrix', {})
        
        # Response time optimization
        if 'response_time' in correlation_matrix:
            response_correlations = correlation_matrix['response_time']
            if response_correlations.get('customer_satisfaction', 0) < -0.8:
                recommendations.append({
                    'type': 'performance_optimization',
                    'metric': 'response_time',
                    'description': 'Response time significantly impacts customer satisfaction',
                    'priority': 'high',
                    'action': 'Optimize response time to improve customer satisfaction'
                })
        
        # Availability optimization
        if 'availability' in correlation_matrix:
            availability_correlations = correlation_matrix['availability']
            if availability_correlations.get('sla_compliance', 0) > 0.8:
                recommendations.append({
                    'type': 'sla_optimization',
                    'metric': 'availability',
                    'description': 'Availability strongly correlates with SLA compliance',
                    'priority': 'medium',
                    'action': 'Focus on availability improvements for SLA compliance'
                })
        
        return recommendations
    
    def calculate_business_impact_of_optimization(self, optimization: Dict[str, Any], 
                                               current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate business impact of a specific optimization"""
        impact_analysis = {
            'optimization_type': optimization.get('type', 'unknown'),
            'business_impacts': {},
            'roi_estimate': 0.0,
            'risk_assessment': {},
            'implementation_priority': 'medium'
        }
        
        try:
            optimization_type = optimization.get('type', '')
            potential_savings = optimization.get('potential_savings', 0)
            
            # Calculate business impacts based on optimization type
            if 'zero_pod_scaling' in optimization_type:
                impact_analysis['business_impacts'] = {
                    'cost_savings': potential_savings * 100,
                    'revenue_impact': 'minimal',
                    'customer_impact': 'minimal',
                    'sla_impact': 'minimal'
                }
                impact_analysis['roi_estimate'] = potential_savings * 100
                impact_analysis['implementation_priority'] = 'high'
            
            elif 'business_hours_scaling' in optimization_type:
                impact_analysis['business_impacts'] = {
                    'cost_savings': potential_savings * 100,
                    'revenue_impact': 'minimal',
                    'customer_impact': 'minimal',
                    'sla_impact': 'minimal'
                }
                impact_analysis['roi_estimate'] = potential_savings * 100
                impact_analysis['implementation_priority'] = 'medium'
            
            elif 'memory_optimization' in optimization_type:
                impact_analysis['business_impacts'] = {
                    'cost_savings': potential_savings * 100,
                    'revenue_impact': 'improvement',
                    'customer_impact': 'improvement',
                    'sla_impact': 'improvement'
                }
                impact_analysis['roi_estimate'] = potential_savings * 100 + 5  # Additional 5% for performance
                impact_analysis['implementation_priority'] = 'high'
            
            # Risk assessment
            confidence = optimization.get('confidence', 0)
            risk_level = optimization.get('risk_level', 'medium')
            
            impact_analysis['risk_assessment'] = {
                'confidence_level': confidence,
                'risk_level': risk_level,
                'business_risk': 'low' if confidence > 80 else 'medium' if confidence > 60 else 'high',
                'recommendation': 'proceed' if confidence > 70 else 'review' if confidence > 50 else 'avoid'
            }
            
        except Exception as e:
            logger.error(f"Error calculating business impact: {e}")
            impact_analysis['error'] = str(e)
        
        return impact_analysis 