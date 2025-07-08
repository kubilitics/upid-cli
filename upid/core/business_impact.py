"""
Business Impact Correlation Engine for UPID
Connects technical Kubernetes metrics to business outcomes
Features:
- Revenue per pod analysis
- Customer satisfaction correlation
- SLA compliance tracking
- ROI estimates
- Business KPI correlation
"""

import os
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BusinessMetric(Enum):
    """Business metrics for correlation"""
    REVENUE = "revenue"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    SLA_COMPLIANCE = "sla_compliance"
    USER_ENGAGEMENT = "user_engagement"
    CONVERSION_RATE = "conversion_rate"
    ERROR_RATE = "error_rate"

class SLALevel(Enum):
    """SLA compliance levels"""
    CRITICAL = "critical"      # 99.99% uptime
    HIGH = "high"             # 99.9% uptime
    MEDIUM = "medium"         # 99% uptime
    LOW = "low"               # 95% uptime

@dataclass
class BusinessImpact:
    """Business impact assessment"""
    revenue_impact: float
    customer_satisfaction_impact: float
    sla_compliance_impact: float
    roi_estimate: float
    business_kpis: Dict[str, Any]
    confidence_score: float

class BusinessImpactCorrelator:
    """Business impact correlation engine"""
    
    def __init__(self):
        """Initialize the business impact correlator"""
        self.business_metrics = {}
        self.sla_definitions = self._initialize_sla_definitions()
        self.correlation_models = self._initialize_correlation_models()
        
        # Business hours configuration
        self.business_hours = {
            'start': 9,
            'end': 17,
            'timezone': 'UTC'
        }
        
        # Revenue estimation parameters
        self.revenue_per_user_per_hour = 0.01  # $0.01 per user per hour
        self.critical_service_multiplier = 10.0  # 10x revenue impact for critical services
        
    def _initialize_sla_definitions(self) -> Dict[str, Any]:
        """Initialize SLA definitions"""
        return {
            SLALevel.CRITICAL: {
                'uptime': 0.9999,
                'response_time': 100,  # ms
                'error_rate': 0.0001
            },
            SLALevel.HIGH: {
                'uptime': 0.999,
                'response_time': 200,
                'error_rate': 0.001
            },
            SLALevel.MEDIUM: {
                'uptime': 0.99,
                'response_time': 500,
                'error_rate': 0.01
            },
            SLALevel.LOW: {
                'uptime': 0.95,
                'response_time': 1000,
                'error_rate': 0.05
            }
        }
    
    def _initialize_correlation_models(self) -> Dict[str, Any]:
        """Initialize correlation models for business metrics"""
        return {
            'availability_to_revenue': {
                'correlation_coefficient': 0.8,
                'impact_multiplier': 1.5
            },
            'performance_to_satisfaction': {
                'correlation_coefficient': 0.7,
                'impact_multiplier': 1.2
            },
            'error_rate_to_engagement': {
                'correlation_coefficient': -0.6,
                'impact_multiplier': 0.8
            },
            'resource_efficiency_to_roi': {
                'correlation_coefficient': 0.9,
                'impact_multiplier': 2.0
            }
        }
    
    def correlate_technical_to_business(self, cluster_id: str,
                                     intelligent_metrics: Dict[str, Any],
                                     optimization_plans: List[Any]) -> Dict[str, Any]:
        """Correlate technical metrics to business outcomes"""
        try:
            business_correlation = {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'revenue_analysis': {},
                'customer_satisfaction_analysis': {},
                'sla_compliance_analysis': {},
                'roi_analysis': {},
                'business_kpis': {},
                'optimization_impact': {}
            }
            
            # Revenue analysis
            business_correlation['revenue_analysis'] = self._analyze_revenue_impact(
                intelligent_metrics, optimization_plans
            )
            
            # Customer satisfaction analysis
            business_correlation['customer_satisfaction_analysis'] = self._analyze_customer_satisfaction(
                intelligent_metrics, optimization_plans
            )
            
            # SLA compliance analysis
            business_correlation['sla_compliance_analysis'] = self._analyze_sla_compliance(
                intelligent_metrics, optimization_plans
            )
            
            # ROI analysis
            business_correlation['roi_analysis'] = self._analyze_roi_impact(
                intelligent_metrics, optimization_plans
            )
            
            # Business KPIs
            business_correlation['business_kpis'] = self._calculate_business_kpis(
                intelligent_metrics, optimization_plans
            )
            
            # Optimization impact
            business_correlation['optimization_impact'] = self._assess_optimization_business_impact(
                optimization_plans
            )
            
            return business_correlation
            
        except Exception as e:
            logger.error(f"Error correlating technical to business metrics: {e}")
            return {
                'cluster_id': cluster_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _analyze_revenue_impact(self, intelligent_metrics: Dict[str, Any],
                               optimization_plans: List[Any]) -> Dict[str, Any]:
        """Analyze revenue impact of current state and optimizations"""
        revenue_analysis = {
            'current_revenue_per_hour': 0,
            'potential_revenue_impact': 0,
            'revenue_per_pod': {},
            'critical_service_revenue': 0,
            'business_hours_revenue': 0
        }
        
        # Calculate current revenue
        business_activity = intelligent_metrics.get('business_activity', {})
        total_pods = business_activity.get('total_pods', 0)
        business_active_pods = business_activity.get('business_active_pods', 0)
        
        # Revenue per pod calculation
        for pod in intelligent_metrics.get('intelligent_pods', []):
            pod_name = pod.get('name', '')
            namespace = pod.get('namespace', '')
            activity_type = pod.get('activity_analysis', 'unknown')
            business_context = pod.get('business_context', {})
            
            # Determine revenue impact
            revenue_multiplier = 1.0
            if activity_type == 'business_active':
                revenue_multiplier = 2.0
            elif activity_type == 'idle':
                revenue_multiplier = 0.1
            
            # Critical service multiplier
            if any(critical in pod_name.lower() for critical in ['database', 'redis', 'api', 'web']):
                revenue_multiplier *= self.critical_service_multiplier
            
            # Business hours multiplier
            current_hour = datetime.utcnow().hour
            is_business_hours = self.business_hours['start'] <= current_hour <= self.business_hours['end']
            if is_business_hours:
                revenue_multiplier *= 1.5
            
            pod_revenue = self.revenue_per_user_per_hour * revenue_multiplier
            revenue_analysis['revenue_per_pod'][f"{namespace}/{pod_name}"] = pod_revenue
            
            if revenue_multiplier >= self.critical_service_multiplier:
                revenue_analysis['critical_service_revenue'] += pod_revenue
            
            if is_business_hours:
                revenue_analysis['business_hours_revenue'] += pod_revenue
        
        revenue_analysis['current_revenue_per_hour'] = sum(revenue_analysis['revenue_per_pod'].values())
        
        # Calculate potential revenue impact from optimizations
        total_potential_impact = 0
        for plan in optimization_plans:
            if hasattr(plan, 'potential_savings'):
                # Estimate revenue impact from cost savings
                revenue_impact = plan.potential_savings * 0.1  # 10% of cost savings as revenue impact
                total_potential_impact += revenue_impact
        
        revenue_analysis['potential_revenue_impact'] = total_potential_impact
        
        return revenue_analysis
    
    def _analyze_customer_satisfaction(self, intelligent_metrics: Dict[str, Any],
                                     optimization_plans: List[Any]) -> Dict[str, Any]:
        """Analyze customer satisfaction impact"""
        satisfaction_analysis = {
            'current_satisfaction_score': 0,
            'performance_impact': 0,
            'availability_impact': 0,
            'error_rate_impact': 0,
            'predicted_satisfaction_change': 0
        }
        
        # Calculate current satisfaction based on performance metrics
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        efficiency_score = resource_correlation.get('efficiency_score', 0)
        
        # Base satisfaction score
        base_satisfaction = 0.7  # 70% base satisfaction
        
        # Performance impact
        if efficiency_score > 80:
            performance_impact = 0.2
        elif efficiency_score > 60:
            performance_impact = 0.1
        else:
            performance_impact = -0.1
        
        # Availability impact
        business_activity = intelligent_metrics.get('business_activity', {})
        business_ratio = business_activity.get('business_activity_ratio', 0)
        
        if business_ratio > 0.7:
            availability_impact = 0.15
        elif business_ratio > 0.3:
            availability_impact = 0.05
        else:
            availability_impact = -0.1
        
        # Error rate impact (simplified)
        error_rate_impact = -0.05  # Assume some error rate
        
        # Calculate current satisfaction
        current_satisfaction = base_satisfaction + performance_impact + availability_impact + error_rate_impact
        satisfaction_analysis['current_satisfaction_score'] = max(0, min(1, current_satisfaction))
        
        # Calculate impacts
        satisfaction_analysis['performance_impact'] = performance_impact
        satisfaction_analysis['availability_impact'] = availability_impact
        satisfaction_analysis['error_rate_impact'] = error_rate_impact
        
        # Predict satisfaction change from optimizations
        predicted_change = 0
        for plan in optimization_plans:
            if hasattr(plan, 'risk_level'):
                if plan.risk_level.value == 'low':
                    predicted_change += 0.05  # Small positive impact
                elif plan.risk_level.value == 'high':
                    predicted_change -= 0.1   # Negative impact
        
        satisfaction_analysis['predicted_satisfaction_change'] = predicted_change
        
        return satisfaction_analysis
    
    def _analyze_sla_compliance(self, intelligent_metrics: Dict[str, Any],
                               optimization_plans: List[Any]) -> Dict[str, Any]:
        """Analyze SLA compliance impact"""
        sla_analysis = {
            'current_sla_level': SLALevel.MEDIUM.value,
            'uptime_compliance': 0.99,
            'response_time_compliance': 0.95,
            'error_rate_compliance': 0.98,
            'sla_breach_risk': 0.1,
            'optimization_sla_impact': {}
        }
        
        # Calculate current SLA compliance
        business_activity = intelligent_metrics.get('business_activity', {})
        business_ratio = business_activity.get('business_activity_ratio', 0)
        
        # Determine SLA level based on business activity
        if business_ratio > 0.8:
            sla_analysis['current_sla_level'] = SLALevel.CRITICAL.value
        elif business_ratio > 0.6:
            sla_analysis['current_sla_level'] = SLALevel.HIGH.value
        elif business_ratio > 0.3:
            sla_analysis['current_sla_level'] = SLALevel.MEDIUM.value
        else:
            sla_analysis['current_sla_level'] = SLALevel.LOW.value
        
        # Calculate compliance metrics
        sla_definitions = self.sla_definitions[SLALevel(sla_analysis['current_sla_level'])]
        
        # Simulate compliance based on current state
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        efficiency_score = resource_correlation.get('efficiency_score', 0)
        
        # Uptime compliance
        if efficiency_score > 80:
            sla_analysis['uptime_compliance'] = sla_definitions['uptime']
        elif efficiency_score > 60:
            sla_analysis['uptime_compliance'] = sla_definitions['uptime'] * 0.95
        else:
            sla_analysis['uptime_compliance'] = sla_definitions['uptime'] * 0.9
        
        # Response time compliance
        sla_analysis['response_time_compliance'] = 0.95  # Simplified
        
        # Error rate compliance
        sla_analysis['error_rate_compliance'] = 0.98  # Simplified
        
        # SLA breach risk
        if sla_analysis['uptime_compliance'] < sla_definitions['uptime']:
            sla_analysis['sla_breach_risk'] = 0.3
        elif sla_analysis['uptime_compliance'] < sla_definitions['uptime'] * 1.1:
            sla_analysis['sla_breach_risk'] = 0.1
        else:
            sla_analysis['sla_breach_risk'] = 0.05
        
        # Analyze optimization impact on SLA
        for plan in optimization_plans:
            if hasattr(plan, 'risk_level'):
                plan_impact = {
                    'risk_level': plan.risk_level.value,
                    'sla_breach_risk_increase': 0,
                    'compliance_impact': 'neutral'
                }
                
                if plan.risk_level.value == 'high':
                    plan_impact['sla_breach_risk_increase'] = 0.2
                    plan_impact['compliance_impact'] = 'negative'
                elif plan.risk_level.value == 'low':
                    plan_impact['sla_breach_risk_increase'] = 0.05
                    plan_impact['compliance_impact'] = 'positive'
                
                sla_analysis['optimization_sla_impact'][plan.target_resource] = plan_impact
        
        return sla_analysis
    
    def _analyze_roi_impact(self, intelligent_metrics: Dict[str, Any],
                           optimization_plans: List[Any]) -> Dict[str, Any]:
        """Analyze ROI impact of optimizations"""
        roi_analysis = {
            'current_roi': 0,
            'optimization_roi_impact': 0,
            'cost_savings': 0,
            'revenue_impact': 0,
            'roi_breakdown': {}
        }
        
        # Calculate current ROI
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        efficiency_score = resource_correlation.get('efficiency_score', 0)
        
        # Simplified ROI calculation
        current_cost = 100  # Base cost
        current_revenue = 150  # Base revenue
        
        # Adjust based on efficiency
        if efficiency_score > 80:
            current_roi = (current_revenue - current_cost * 0.8) / (current_cost * 0.8)
        elif efficiency_score > 60:
            current_roi = (current_revenue - current_cost * 0.9) / (current_cost * 0.9)
        else:
            current_roi = (current_revenue - current_cost) / current_cost
        
        roi_analysis['current_roi'] = current_roi
        
        # Calculate optimization ROI impact
        total_cost_savings = 0
        total_revenue_impact = 0
        
        for plan in optimization_plans:
            if hasattr(plan, 'potential_savings'):
                cost_savings = plan.potential_savings
                total_cost_savings += cost_savings
                
                # Estimate revenue impact
                if hasattr(plan, 'risk_level'):
                    if plan.risk_level.value == 'low':
                        revenue_impact = cost_savings * 0.1  # 10% of savings as revenue
                    else:
                        revenue_impact = -cost_savings * 0.05  # Negative impact for high risk
                else:
                    revenue_impact = 0
                
                total_revenue_impact += revenue_impact
        
        roi_analysis['cost_savings'] = total_cost_savings
        roi_analysis['revenue_impact'] = total_revenue_impact
        
        # Calculate new ROI
        new_cost = current_cost - total_cost_savings
        new_revenue = current_revenue + total_revenue_impact
        
        if new_cost > 0:
            new_roi = (new_revenue - new_cost) / new_cost
            roi_analysis['optimization_roi_impact'] = new_roi - current_roi
        
        # ROI breakdown
        roi_analysis['roi_breakdown'] = {
            'efficiency_impact': efficiency_score / 100,
            'cost_optimization_impact': total_cost_savings / current_cost,
            'revenue_optimization_impact': total_revenue_impact / current_revenue
        }
        
        return roi_analysis
    
    def _calculate_business_kpis(self, intelligent_metrics: Dict[str, Any],
                               optimization_plans: List[Any]) -> Dict[str, Any]:
        """Calculate business KPIs"""
        business_kpis = {
            'resource_efficiency': 0,
            'cost_per_user': 0,
            'revenue_per_user': 0,
            'availability_score': 0,
            'performance_score': 0,
            'business_activity_score': 0
        }
        
        # Resource efficiency
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        business_kpis['resource_efficiency'] = resource_correlation.get('efficiency_score', 0)
        
        # Business activity score
        business_activity = intelligent_metrics.get('business_activity', {})
        business_kpis['business_activity_score'] = business_activity.get('business_activity_ratio', 0) * 100
        
        # Availability score
        business_kpis['availability_score'] = 95  # Simplified calculation
        
        # Performance score
        business_kpis['performance_score'] = business_kpis['resource_efficiency']
        
        # Cost per user (simplified)
        total_pods = business_activity.get('total_pods', 1)
        business_kpis['cost_per_user'] = 0.1 / total_pods if total_pods > 0 else 0.1
        
        # Revenue per user (simplified)
        business_kpis['revenue_per_user'] = business_kpis['cost_per_user'] * 1.5
        
        return business_kpis
    
    def _assess_optimization_business_impact(self, optimization_plans: List[Any]) -> Dict[str, Any]:
        """Assess business impact of optimization plans"""
        optimization_impact = {
            'high_impact_plans': [],
            'low_risk_plans': [],
            'revenue_positive_plans': [],
            'sla_positive_plans': [],
            'overall_business_impact': 'neutral'
        }
        
        for plan in optimization_plans:
            plan_impact = {
                'target': plan.target_resource,
                'type': plan.operation_type.value,
                'confidence': plan.confidence_score,
                'risk': plan.risk_level.value,
                'savings': plan.potential_savings,
                'business_impact': 'neutral'
            }
            
            # Categorize plans
            if plan.confidence_score > 0.8:
                optimization_impact['high_impact_plans'].append(plan_impact)
            
            if plan.risk_level.value in ['low', 'medium']:
                optimization_impact['low_risk_plans'].append(plan_impact)
            
            if plan.potential_savings > 0:
                optimization_impact['revenue_positive_plans'].append(plan_impact)
            
            # Determine business impact
            if plan.confidence_score > 0.8 and plan.risk_level.value == 'low':
                plan_impact['business_impact'] = 'positive'
            elif plan.risk_level.value == 'high':
                plan_impact['business_impact'] = 'negative'
        
        # Overall business impact
        positive_plans = len([p for p in optimization_plans if p.confidence_score > 0.8 and p.risk_level.value == 'low'])
        negative_plans = len([p for p in optimization_plans if p.risk_level.value == 'high'])
        
        if positive_plans > negative_plans:
            optimization_impact['overall_business_impact'] = 'positive'
        elif negative_plans > positive_plans:
            optimization_impact['overall_business_impact'] = 'negative'
        else:
            optimization_impact['overall_business_impact'] = 'neutral'
        
        return optimization_impact
    
    def generate_business_report(self, business_correlation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business report"""
        report = {
            'executive_summary': {},
            'financial_impact': {},
            'operational_metrics': {},
            'risk_assessment': {},
            'recommendations': []
        }
        
        # Executive summary
        revenue_analysis = business_correlation.get('revenue_analysis', {})
        roi_analysis = business_correlation.get('roi_analysis', {})
        sla_analysis = business_correlation.get('sla_compliance_analysis', {})
        
        report['executive_summary'] = {
            'current_revenue_per_hour': revenue_analysis.get('current_revenue_per_hour', 0),
            'current_roi': roi_analysis.get('current_roi', 0),
            'sla_compliance': sla_analysis.get('uptime_compliance', 0),
            'optimization_potential': revenue_analysis.get('potential_revenue_impact', 0)
        }
        
        # Financial impact
        report['financial_impact'] = {
            'cost_savings_potential': roi_analysis.get('cost_savings', 0),
            'revenue_impact': roi_analysis.get('revenue_impact', 0),
            'roi_improvement': roi_analysis.get('optimization_roi_impact', 0)
        }
        
        # Operational metrics
        business_kpis = business_correlation.get('business_kpis', {})
        report['operational_metrics'] = {
            'resource_efficiency': business_kpis.get('resource_efficiency', 0),
            'availability_score': business_kpis.get('availability_score', 0),
            'performance_score': business_kpis.get('performance_score', 0)
        }
        
        # Risk assessment
        report['risk_assessment'] = {
            'sla_breach_risk': sla_analysis.get('sla_breach_risk', 0),
            'optimization_risk': 'low'  # Simplified
        }
        
        # Recommendations
        optimization_impact = business_correlation.get('optimization_impact', {})
        if optimization_impact.get('overall_business_impact') == 'positive':
            report['recommendations'].append({
                'priority': 'high',
                'action': 'Proceed with high-confidence, low-risk optimizations',
                'expected_impact': 'positive',
                'timeline': 'immediate'
            })
        
        if roi_analysis.get('optimization_roi_impact', 0) > 0:
            report['recommendations'].append({
                'priority': 'medium',
                'action': 'Implement cost optimization strategies',
                'expected_impact': 'cost_reduction',
                'timeline': '1-2_weeks'
            })
        
        return report 