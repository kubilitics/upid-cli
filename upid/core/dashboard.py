"""
Executive Dashboard Engine for UPID
Provides high-level business insights, cost attribution, and ROI tracking
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DashboardMetric(Enum):
    """Types of dashboard metrics"""
    COST_SAVINGS = "cost_savings"
    ROI = "roi"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    EFFICIENCY = "efficiency"
    BUSINESS_IMPACT = "business_impact"

@dataclass
class DashboardInsight:
    """Executive dashboard insight"""
    metric_type: DashboardMetric
    title: str
    value: float
    unit: str
    trend: str  # increasing, decreasing, stable
    trend_percentage: float
    confidence: float
    business_impact: str
    recommendation: str

class ExecutiveDashboard:
    """Executive dashboard for business insights and decision making"""
    
    def __init__(self):
        """Initialize the executive dashboard"""
        self.metric_thresholds = {
            'cost_savings_target': 25.0,  # 25% target savings
            'roi_target': 20.0,  # 20% target ROI
            'availability_target': 99.9,  # 99.9% availability target
            'performance_target': 95.0,  # 95% performance target
        }
        
        self.dashboard_sections = {
            'financial': ['cost_savings', 'roi', 'cost_attribution'],
            'operational': ['performance', 'availability', 'efficiency'],
            'business': ['revenue_impact', 'customer_satisfaction', 'sla_compliance']
        }
    
    def generate_executive_dashboard(self, cluster_data: Dict[str, Any], 
                                   optimization_data: Dict[str, Any],
                                   business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive executive dashboard"""
        dashboard = {
            'generated_at': datetime.utcnow().isoformat(),
            'cluster_info': cluster_data.get('cluster_info', {}),
            'summary': {},
            'financial_metrics': {},
            'operational_metrics': {},
            'business_metrics': {},
            'insights': [],
            'recommendations': [],
            'trends': {},
            'alerts': []
        }
        
        try:
            # Generate financial metrics
            dashboard['financial_metrics'] = self._generate_financial_metrics(
                cluster_data, optimization_data, business_data
            )
            
            # Generate operational metrics
            dashboard['operational_metrics'] = self._generate_operational_metrics(
                cluster_data, optimization_data
            )
            
            # Generate business metrics
            dashboard['business_metrics'] = self._generate_business_metrics(
                business_data
            )
            
            # Generate executive insights
            dashboard['insights'] = self._generate_executive_insights(dashboard)
            
            # Generate recommendations
            dashboard['recommendations'] = self._generate_executive_recommendations(dashboard)
            
            # Generate trends
            dashboard['trends'] = self._generate_trend_analysis(cluster_data)
            
            # Generate alerts
            dashboard['alerts'] = self._generate_alerts(dashboard)
            
            # Generate summary
            dashboard['summary'] = self._generate_dashboard_summary(dashboard)
            
            logger.info("Generated comprehensive executive dashboard")
            
        except Exception as e:
            logger.error(f"Error generating executive dashboard: {e}")
            dashboard['error'] = str(e)
        
        return dashboard
    
    def _generate_financial_metrics(self, cluster_data: Dict[str, Any], 
                                  optimization_data: Dict[str, Any],
                                  business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial metrics for executive dashboard"""
        financial_metrics = {
            'cost_savings': {},
            'roi_analysis': {},
            'cost_attribution': {},
            'budget_impact': {}
        }
        
        # Cost savings analysis
        total_savings = 0
        if optimization_data.get('recommendations'):
            for rec in optimization_data['recommendations']:
                savings = rec.get('potential_savings', 0) * 100
                total_savings += savings
        
        financial_metrics['cost_savings'] = {
            'current_savings': total_savings,
            'target_savings': self.metric_thresholds['cost_savings_target'],
            'achievement_percentage': (total_savings / self.metric_thresholds['cost_savings_target']) * 100,
            'trend': 'increasing' if total_savings > 20 else 'stable',
            'monthly_projection': total_savings * 30,  # Monthly projection
            'annual_projection': total_savings * 365   # Annual projection
        }
        
        # ROI analysis
        total_roi = business_data.get('roi_estimates', {}).get('total_roi', 0)
        financial_metrics['roi_analysis'] = {
            'current_roi': total_roi,
            'target_roi': self.metric_thresholds['roi_target'],
            'achievement_percentage': (total_roi / self.metric_thresholds['roi_target']) * 100,
            'trend': 'increasing' if total_roi > 15 else 'stable',
            'investment_return': total_roi / 100,  # Investment return ratio
            'payback_period': 12 / (total_roi / 100) if total_roi > 0 else float('inf')
        }
        
        # Cost attribution
        cluster_info = cluster_data.get('cluster_info', {})
        financial_metrics['cost_attribution'] = {
            'infrastructure_cost': cluster_data.get('costs', {}).get('infrastructure', 0),
            'compute_cost': cluster_data.get('costs', {}).get('compute', 0),
            'storage_cost': cluster_data.get('costs', {}).get('storage', 0),
            'network_cost': cluster_data.get('costs', {}).get('network', 0),
            'total_cost': sum([
                cluster_data.get('costs', {}).get('infrastructure', 0),
                cluster_data.get('costs', {}).get('compute', 0),
                cluster_data.get('costs', {}).get('storage', 0),
                cluster_data.get('costs', {}).get('network', 0)
            ])
        }
        
        # Budget impact
        total_cost = financial_metrics['cost_attribution']['total_cost']
        financial_metrics['budget_impact'] = {
            'current_spend': total_cost,
            'optimized_spend': total_cost * (1 - total_savings / 100),
            'savings_amount': total_cost * (total_savings / 100),
            'budget_utilization': 85.0,  # Mock budget utilization
            'budget_remaining': 15.0
        }
        
        return financial_metrics
    
    def _generate_operational_metrics(self, cluster_data: Dict[str, Any], 
                                    optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate operational metrics for executive dashboard"""
        operational_metrics = {
            'performance': {},
            'availability': {},
            'efficiency': {},
            'reliability': {}
        }
        
        # Performance metrics
        current_performance = cluster_data.get('performance', {})
        operational_metrics['performance'] = {
            'cpu_utilization': current_performance.get('cpu_utilization', 0),
            'memory_utilization': current_performance.get('memory_utilization', 0),
            'response_time_p95': current_performance.get('response_time_p95', 0),
            'throughput': current_performance.get('throughput', 0),
            'target_performance': self.metric_thresholds['performance_target'],
            'performance_score': self._calculate_performance_score(current_performance)
        }
        
        # Availability metrics
        availability_data = cluster_data.get('availability', {})
        operational_metrics['availability'] = {
            'current_uptime': availability_data.get('uptime', 99.9),
            'target_uptime': self.metric_thresholds['availability_target'],
            'downtime_minutes': availability_data.get('downtime_minutes', 0),
            'incidents_count': availability_data.get('incidents', 0),
            'mttr_minutes': availability_data.get('mttr_minutes', 0),
            'availability_trend': 'stable'
        }
        
        # Efficiency metrics
        efficiency_score = self._calculate_efficiency_score(cluster_data)
        operational_metrics['efficiency'] = {
            'resource_efficiency': efficiency_score,
            'cost_per_pod': cluster_data.get('costs', {}).get('cost_per_pod', 0),
            'pods_per_node': cluster_data.get('cluster_info', {}).get('pods_per_node', 0),
            'utilization_ratio': current_performance.get('cpu_utilization', 0) / 100,
            'efficiency_trend': 'improving' if efficiency_score > 80 else 'stable'
        }
        
        # Reliability metrics
        operational_metrics['reliability'] = {
            'error_rate': cluster_data.get('performance', {}).get('error_rate', 0),
            'success_rate': 100 - cluster_data.get('performance', {}).get('error_rate', 0),
            'recovery_time': availability_data.get('mttr_minutes', 0),
            'reliability_score': self._calculate_reliability_score(cluster_data)
        }
        
        return operational_metrics
    
    def _generate_business_metrics(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business metrics for executive dashboard"""
        business_metrics = {
            'revenue_impact': {},
            'customer_satisfaction': {},
            'sla_compliance': {},
            'business_value': {}
        }
        
        # Revenue impact
        business_impacts = business_data.get('business_impacts', [])
        revenue_impact = next((impact for impact in business_impacts 
                             if impact.metric_type.value == 'revenue_per_pod'), None)
        
        business_metrics['revenue_impact'] = {
            'revenue_per_pod': revenue_impact.business_value if revenue_impact else 0,
            'total_revenue': revenue_impact.business_value * 100 if revenue_impact else 0,  # Mock total pods
            'revenue_trend': 'increasing' if revenue_impact and revenue_impact.business_value > 100 else 'stable',
            'revenue_confidence': revenue_impact.confidence if revenue_impact else 0
        }
        
        # Customer satisfaction
        satisfaction_impact = next((impact for impact in business_impacts 
                                 if impact.metric_type.value == 'customer_satisfaction'), None)
        
        business_metrics['customer_satisfaction'] = {
            'satisfaction_score': satisfaction_impact.business_value if satisfaction_impact else 7.0,
            'target_score': 8.5,
            'achievement_percentage': (satisfaction_impact.business_value / 8.5 * 100) if satisfaction_impact else 82.4,
            'satisfaction_trend': 'improving' if satisfaction_impact and satisfaction_impact.business_value > 8.0 else 'stable',
            'satisfaction_confidence': satisfaction_impact.confidence if satisfaction_impact else 0
        }
        
        # SLA compliance
        sla_impact = next((impact for impact in business_impacts 
                          if impact.metric_type.value == 'sla_compliance'), None)
        
        business_metrics['sla_compliance'] = {
            'compliance_rate': sla_impact.business_value if sla_impact else 99.5,
            'target_compliance': 99.95,
            'achievement_percentage': (sla_impact.business_value / 99.95 * 100) if sla_impact else 99.5,
            'compliance_trend': 'exceeding' if sla_impact and sla_impact.business_value > 99.9 else 'meeting',
            'compliance_confidence': sla_impact.confidence if sla_impact else 0
        }
        
        # Business value
        total_roi = business_data.get('roi_estimates', {}).get('total_roi', 0)
        business_metrics['business_value'] = {
            'total_roi': total_roi,
            'business_value_score': min(100, max(0, total_roi + 50)),  # Normalize to 0-100
            'value_trend': 'increasing' if total_roi > 10 else 'stable',
            'value_confidence': 85.0  # Mock confidence
        }
        
        return business_metrics
    
    def _generate_executive_insights(self, dashboard: Dict[str, Any]) -> List[DashboardInsight]:
        """Generate executive insights from dashboard data"""
        insights = []
        
        # Financial insights
        financial = dashboard.get('financial_metrics', {})
        cost_savings = financial.get('cost_savings', {})
        roi_analysis = financial.get('roi_analysis', {})
        
        if cost_savings.get('current_savings', 0) > 20:
            insights.append(DashboardInsight(
                metric_type=DashboardMetric.COST_SAVINGS,
                title="Significant Cost Savings Achieved",
                value=cost_savings.get('current_savings', 0),
                unit="%",
                trend="increasing",
                trend_percentage=cost_savings.get('achievement_percentage', 0),
                confidence=85.0,
                business_impact="Direct cost reduction in infrastructure spending",
                recommendation="Continue optimization efforts to maintain savings momentum"
            ))
        
        if roi_analysis.get('current_roi', 0) > 15:
            insights.append(DashboardInsight(
                metric_type=DashboardMetric.ROI,
                title="Strong ROI Performance",
                value=roi_analysis.get('current_roi', 0),
                unit="%",
                trend="increasing",
                trend_percentage=roi_analysis.get('achievement_percentage', 0),
                confidence=90.0,
                business_impact="Positive return on infrastructure investments",
                recommendation="Consider expanding optimization to other clusters"
            ))
        
        # Operational insights
        operational = dashboard.get('operational_metrics', {})
        performance = operational.get('performance', {})
        availability = operational.get('availability', {})
        
        if performance.get('performance_score', 0) > 90:
            insights.append(DashboardInsight(
                metric_type=DashboardMetric.PERFORMANCE,
                title="Excellent Performance Metrics",
                value=performance.get('performance_score', 0),
                unit="score",
                trend="stable",
                trend_percentage=0,
                confidence=88.0,
                business_impact="High system reliability and user satisfaction",
                recommendation="Maintain current performance standards"
            ))
        
        if availability.get('current_uptime', 0) > 99.9:
            insights.append(DashboardInsight(
                metric_type=DashboardMetric.AVAILABILITY,
                title="Outstanding Availability",
                value=availability.get('current_uptime', 0),
                unit="%",
                trend="exceeding",
                trend_percentage=0,
                confidence=92.0,
                business_impact="Minimal downtime ensures business continuity",
                recommendation="Continue monitoring and preventive maintenance"
            ))
        
        return insights
    
    def _generate_executive_recommendations(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate executive recommendations"""
        recommendations = []
        
        # Financial recommendations
        financial = dashboard.get('financial_metrics', {})
        cost_savings = financial.get('cost_savings', {})
        roi_analysis = financial.get('roi_analysis', {})
        
        if cost_savings.get('achievement_percentage', 0) < 80:
            recommendations.append({
                'category': 'financial',
                'priority': 'high',
                'title': 'Accelerate Cost Optimization',
                'description': f"Current savings at {cost_savings.get('current_savings', 0):.1f}% below target of {self.metric_thresholds['cost_savings_target']}%",
                'action': 'Implement additional optimization strategies',
                'expected_impact': 'Increase savings by 5-10%',
                'timeline': '30 days'
            })
        
        if roi_analysis.get('current_roi', 0) < 15:
            recommendations.append({
                'category': 'financial',
                'priority': 'medium',
                'title': 'Improve ROI Performance',
                'description': f"Current ROI at {roi_analysis.get('current_roi', 0):.1f}% below target of {self.metric_thresholds['roi_target']}%",
                'action': 'Focus on high-impact optimizations',
                'expected_impact': 'Increase ROI by 5-8%',
                'timeline': '60 days'
            })
        
        # Operational recommendations
        operational = dashboard.get('operational_metrics', {})
        performance = operational.get('performance', {})
        availability = operational.get('availability', {})
        
        if performance.get('performance_score', 0) < 85:
            recommendations.append({
                'category': 'operational',
                'priority': 'high',
                'title': 'Performance Optimization Required',
                'description': f"Performance score at {performance.get('performance_score', 0):.1f} below target of {self.metric_thresholds['performance_target']}",
                'action': 'Investigate and resolve performance bottlenecks',
                'expected_impact': 'Improve performance by 10-15%',
                'timeline': '45 days'
            })
        
        if availability.get('current_uptime', 0) < 99.9:
            recommendations.append({
                'category': 'operational',
                'priority': 'critical',
                'title': 'Availability Improvement Needed',
                'description': f"Current uptime at {availability.get('current_uptime', 0):.3f}% below target of {self.metric_thresholds['availability_target']}%",
                'action': 'Implement high-availability measures',
                'expected_impact': 'Achieve 99.9%+ uptime',
                'timeline': '30 days'
            })
        
        return recommendations
    
    def _generate_trend_analysis(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend analysis for executive dashboard"""
        trends = {
            'cost_trend': 'decreasing',
            'performance_trend': 'stable',
            'availability_trend': 'improving',
            'efficiency_trend': 'increasing',
            'business_value_trend': 'increasing'
        }
        
        # Analyze trends based on historical data
        historical_data = cluster_data.get('historical_data', {})
        if historical_data:
            # Mock trend analysis based on available data
            trends['cost_trend'] = 'decreasing'  # Optimizations reducing costs
            trends['performance_trend'] = 'stable'  # Consistent performance
            trends['availability_trend'] = 'improving'  # Better monitoring
            trends['efficiency_trend'] = 'increasing'  # Resource optimization
            trends['business_value_trend'] = 'increasing'  # ROI improvements
        
        return trends
    
    def _generate_alerts(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate executive alerts"""
        alerts = []
        
        # Financial alerts
        financial = dashboard.get('financial_metrics', {})
        cost_savings = financial.get('cost_savings', {})
        roi_analysis = financial.get('roi_analysis', {})
        
        if cost_savings.get('current_savings', 0) < 10:
            alerts.append({
                'severity': 'warning',
                'category': 'financial',
                'title': 'Low Cost Savings',
                'description': f"Cost savings at {cost_savings.get('current_savings', 0):.1f}% below target",
                'action_required': 'Review optimization strategies'
            })
        
        if roi_analysis.get('current_roi', 0) < 10:
            alerts.append({
                'severity': 'critical',
                'category': 'financial',
                'title': 'Poor ROI Performance',
                'description': f"ROI at {roi_analysis.get('current_roi', 0):.1f}% below target",
                'action_required': 'Immediate optimization review required'
            })
        
        # Operational alerts
        operational = dashboard.get('operational_metrics', {})
        availability = operational.get('availability', {})
        performance = operational.get('performance', {})
        
        if availability.get('current_uptime', 0) < 99.5:
            alerts.append({
                'severity': 'critical',
                'category': 'operational',
                'title': 'Availability Below Target',
                'description': f"Uptime at {availability.get('current_uptime', 0):.3f}% below 99.9% target",
                'action_required': 'Immediate availability improvement required'
            })
        
        if performance.get('performance_score', 0) < 80:
            alerts.append({
                'severity': 'warning',
                'category': 'operational',
                'title': 'Performance Degradation',
                'description': f"Performance score at {performance.get('performance_score', 0):.1f} below target",
                'action_required': 'Performance optimization needed'
            })
        
        return alerts
    
    def _generate_dashboard_summary(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive dashboard summary"""
        financial = dashboard.get('financial_metrics', {})
        operational = dashboard.get('operational_metrics', {})
        business = dashboard.get('business_metrics', {})
        
        summary = {
            'overall_health': 'excellent',
            'key_metrics': {},
            'achievements': [],
            'challenges': [],
            'next_quarter_focus': []
        }
        
        # Overall health assessment
        health_score = 0
        if financial.get('cost_savings', {}).get('current_savings', 0) > 20:
            health_score += 25
        if financial.get('roi_analysis', {}).get('current_roi', 0) > 15:
            health_score += 25
        if operational.get('availability', {}).get('current_uptime', 0) > 99.9:
            health_score += 25
        if operational.get('performance', {}).get('performance_score', 0) > 90:
            health_score += 25
        
        if health_score >= 90:
            summary['overall_health'] = 'excellent'
        elif health_score >= 75:
            summary['overall_health'] = 'good'
        elif health_score >= 60:
            summary['overall_health'] = 'fair'
        else:
            summary['overall_health'] = 'poor'
        
        # Key metrics
        summary['key_metrics'] = {
            'cost_savings': financial.get('cost_savings', {}).get('current_savings', 0),
            'roi': financial.get('roi_analysis', {}).get('current_roi', 0),
            'availability': operational.get('availability', {}).get('current_uptime', 0),
            'performance_score': operational.get('performance', {}).get('performance_score', 0),
            'customer_satisfaction': business.get('customer_satisfaction', {}).get('satisfaction_score', 0)
        }
        
        # Achievements
        if financial.get('cost_savings', {}).get('current_savings', 0) > 20:
            summary['achievements'].append("Exceeded cost savings target")
        if financial.get('roi_analysis', {}).get('current_roi', 0) > 15:
            summary['achievements'].append("Achieved strong ROI performance")
        if operational.get('availability', {}).get('current_uptime', 0) > 99.9:
            summary['achievements'].append("Maintained excellent availability")
        
        # Challenges
        if financial.get('cost_savings', {}).get('current_savings', 0) < 15:
            summary['challenges'].append("Cost savings below target")
        if operational.get('performance', {}).get('performance_score', 0) < 85:
            summary['challenges'].append("Performance optimization needed")
        
        # Next quarter focus
        summary['next_quarter_focus'] = [
            "Expand optimization to additional clusters",
            "Implement advanced analytics for predictive optimization",
            "Enhance business impact correlation analysis"
        ]
        
        return summary
    
    def _calculate_performance_score(self, performance_data: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        cpu_score = min(100, performance_data.get('cpu_utilization', 0) * 1.2)
        memory_score = min(100, performance_data.get('memory_utilization', 0) * 1.2)
        response_score = max(0, 100 - (performance_data.get('response_time_p95', 0) - 50) / 2)
        
        return (cpu_score + memory_score + response_score) / 3
    
    def _calculate_efficiency_score(self, cluster_data: Dict[str, Any]) -> float:
        """Calculate resource efficiency score"""
        performance = cluster_data.get('performance', {})
        cpu_util = performance.get('cpu_utilization', 0)
        memory_util = performance.get('memory_utilization', 0)
        
        # Optimal utilization is around 70-80%
        cpu_efficiency = 100 - abs(cpu_util - 75)
        memory_efficiency = 100 - abs(memory_util - 75)
        
        return (cpu_efficiency + memory_efficiency) / 2
    
    def _calculate_reliability_score(self, cluster_data: Dict[str, Any]) -> float:
        """Calculate reliability score"""
        performance = cluster_data.get('performance', {})
        availability = cluster_data.get('availability', {})
        
        error_rate = performance.get('error_rate', 0)
        uptime = availability.get('uptime', 99.9)
        
        error_score = max(0, 100 - error_rate * 1000)  # Convert to percentage
        uptime_score = min(100, uptime * 100)
        
        return (error_score + uptime_score) / 2 