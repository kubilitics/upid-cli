"""
Business Intelligence Engine
Correlates Kubernetes metrics with business KPIs and provides actionable insights.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BusinessMetricType(Enum):
    """Types of business metrics that can be correlated with K8s data."""
    REVENUE = "revenue"
    USER_ACTIVITY = "user_activity"
    TRANSACTION_VOLUME = "transaction_volume"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    COST_PER_TRANSACTION = "cost_per_transaction"


@dataclass
class BusinessMetric:
    """Represents a business metric with its value and metadata."""
    name: str
    value: float
    timestamp: datetime
    metric_type: BusinessMetricType
    unit: str
    description: str


@dataclass
class CorrelationInsight:
    """Represents a correlation insight between K8s and business metrics."""
    k8s_metric: str
    business_metric: str
    correlation_strength: float  # -1 to 1
    confidence: float  # 0 to 1
    insight_type: str
    description: str
    actionable: bool
    recommendations: List[str]


class BusinessIntelligenceEngine:
    """
    Business Intelligence Engine that correlates Kubernetes metrics with business KPIs.
    """
    
    def __init__(self):
        self.correlation_threshold = 0.7
        self.confidence_threshold = 0.8
        self.insights_history: List[CorrelationInsight] = []
        
    async def analyze_business_correlation(
        self, 
        k8s_metrics: Dict[str, Any],
        business_metrics: List[BusinessMetric]
    ) -> List[CorrelationInsight]:
        """
        Analyze correlation between Kubernetes metrics and business metrics.
        
        Args:
            k8s_metrics: Dictionary of Kubernetes metrics data
            business_metrics: List of business metrics to correlate
            
        Returns:
            List of correlation insights
        """
        logger.info("Starting business correlation analysis")
        
        insights = []
        
        # Analyze CPU usage vs business metrics
        if 'cpu_usage' in k8s_metrics:
            cpu_insights = await self._analyze_cpu_correlation(
                k8s_metrics['cpu_usage'], business_metrics
            )
            insights.extend(cpu_insights)
        
        # Analyze memory usage vs business metrics
        if 'memory_usage' in k8s_metrics:
            memory_insights = await self._analyze_memory_correlation(
                k8s_metrics['memory_usage'], business_metrics
            )
            insights.extend(memory_insights)
        
        # Analyze pod count vs business metrics
        if 'pod_count' in k8s_metrics:
            pod_insights = await self._analyze_pod_correlation(
                k8s_metrics['pod_count'], business_metrics
            )
            insights.extend(pod_insights)
        
        # Analyze error rates vs business metrics
        if 'error_rate' in k8s_metrics:
            error_insights = await self._analyze_error_correlation(
                k8s_metrics['error_rate'], business_metrics
            )
            insights.extend(error_insights)
        
        # Store insights for historical analysis
        self.insights_history.extend(insights)
        
        logger.info(f"Generated {len(insights)} business correlation insights")
        return insights
    
    async def _analyze_cpu_correlation(
        self, 
        cpu_data: Dict[str, Any], 
        business_metrics: List[BusinessMetric]
    ) -> List[CorrelationInsight]:
        """Analyze correlation between CPU usage and business metrics."""
        insights = []
        
        # Find revenue metrics
        revenue_metrics = [m for m in business_metrics if m.metric_type == BusinessMetricType.REVENUE]
        
        if revenue_metrics and 'average' in cpu_data:
            cpu_avg = cpu_data['average']
            
            # Simulate correlation analysis
            correlation = self._calculate_correlation(cpu_avg, [m.value for m in revenue_metrics])
            
            if abs(correlation) > self.correlation_threshold:
                insight = CorrelationInsight(
                    k8s_metric="CPU Usage",
                    business_metric="Revenue",
                    correlation_strength=correlation,
                    confidence=0.85,
                    insight_type="performance_revenue_correlation",
                    description=f"CPU usage shows {abs(correlation):.2f} correlation with revenue",
                    actionable=True,
                    recommendations=[
                        "Monitor CPU scaling patterns during high-revenue periods",
                        "Consider auto-scaling based on revenue projections",
                        "Optimize resource allocation for revenue-generating services"
                    ]
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_memory_correlation(
        self, 
        memory_data: Dict[str, Any], 
        business_metrics: List[BusinessMetric]
    ) -> List[CorrelationInsight]:
        """Analyze correlation between memory usage and business metrics."""
        insights = []
        
        # Find user activity metrics
        user_metrics = [m for m in business_metrics if m.metric_type == BusinessMetricType.USER_ACTIVITY]
        
        if user_metrics and 'average' in memory_data:
            memory_avg = memory_data['average']
            
            # Simulate correlation analysis
            correlation = self._calculate_correlation(memory_avg, [m.value for m in user_metrics])
            
            if abs(correlation) > self.correlation_threshold:
                insight = CorrelationInsight(
                    k8s_metric="Memory Usage",
                    business_metric="User Activity",
                    correlation_strength=correlation,
                    confidence=0.82,
                    insight_type="memory_user_correlation",
                    description=f"Memory usage shows {abs(correlation):.2f} correlation with user activity",
                    actionable=True,
                    recommendations=[
                        "Scale memory resources based on user activity patterns",
                        "Implement memory optimization for high-traffic periods",
                        "Monitor memory leaks during peak usage"
                    ]
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_pod_correlation(
        self, 
        pod_data: Dict[str, Any], 
        business_metrics: List[BusinessMetric]
    ) -> List[CorrelationInsight]:
        """Analyze correlation between pod count and business metrics."""
        insights = []
        
        # Find transaction volume metrics
        transaction_metrics = [m for m in business_metrics if m.metric_type == BusinessMetricType.TRANSACTION_VOLUME]
        
        if transaction_metrics and 'count' in pod_data:
            pod_count = pod_data['count']
            
            # Simulate correlation analysis
            correlation = self._calculate_correlation(pod_count, [m.value for m in transaction_metrics])
            
            if abs(correlation) > self.correlation_threshold:
                insight = CorrelationInsight(
                    k8s_metric="Pod Count",
                    business_metric="Transaction Volume",
                    correlation_strength=correlation,
                    confidence=0.88,
                    insight_type="scaling_transaction_correlation",
                    description=f"Pod count shows {abs(correlation):.2f} correlation with transaction volume",
                    actionable=True,
                    recommendations=[
                        "Implement horizontal pod autoscaling based on transaction volume",
                        "Optimize pod scaling policies for transaction patterns",
                        "Monitor pod efficiency during high-transaction periods"
                    ]
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_error_correlation(
        self, 
        error_data: Dict[str, Any], 
        business_metrics: List[BusinessMetric]
    ) -> List[CorrelationInsight]:
        """Analyze correlation between error rates and business metrics."""
        insights = []
        
        # Find error rate metrics
        error_metrics = [m for m in business_metrics if m.metric_type == BusinessMetricType.ERROR_RATE]
        
        if error_metrics and 'rate' in error_data:
            k8s_error_rate = error_data['rate']
            
            # Simulate correlation analysis
            correlation = self._calculate_correlation(k8s_error_rate, [m.value for m in error_metrics])
            
            if abs(correlation) > self.correlation_threshold:
                insight = CorrelationInsight(
                    k8s_metric="K8s Error Rate",
                    business_metric="Business Error Rate",
                    correlation_strength=correlation,
                    confidence=0.90,
                    insight_type="error_correlation",
                    description=f"Kubernetes error rate shows {abs(correlation):.2f} correlation with business error rate",
                    actionable=True,
                    recommendations=[
                        "Investigate infrastructure errors during high business error periods",
                        "Implement error correlation alerts",
                        "Optimize error handling and recovery procedures"
                    ]
                )
                insights.append(insight)
        
        return insights
    
    def _calculate_correlation(self, value1: float, values2: List[float]) -> float:
        """
        Calculate correlation between a single value and a list of values.
        This is a simplified correlation calculation for demonstration.
        """
        if not values2:
            return 0.0
        
        # Simplified correlation calculation
        avg_value2 = sum(values2) / len(values2)
        
        # Normalize the correlation to be between -1 and 1
        if avg_value2 == 0:
            return 0.0
        
        # Simple linear correlation
        correlation = (value1 - avg_value2) / max(avg_value2, 1.0)
        return max(-1.0, min(1.0, correlation))
    
    async def generate_business_recommendations(
        self, 
        insights: List[CorrelationInsight]
    ) -> List[str]:
        """
        Generate actionable business recommendations based on insights.
        
        Args:
            insights: List of correlation insights
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        for insight in insights:
            if insight.actionable and insight.confidence > self.confidence_threshold:
                recommendations.extend(insight.recommendations)
        
        # Add general recommendations based on patterns
        if len(insights) > 3:
            recommendations.append("Consider implementing comprehensive monitoring dashboard")
            recommendations.append("Review resource allocation strategies")
            recommendations.append("Implement automated scaling policies")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def get_business_impact_score(
        self, 
        k8s_metrics: Dict[str, Any],
        business_metrics: List[BusinessMetric]
    ) -> float:
        """
        Calculate overall business impact score based on K8s metrics.
        
        Args:
            k8s_metrics: Kubernetes metrics data
            business_metrics: Business metrics data
            
        Returns:
            Business impact score (0-100)
        """
        score = 50.0  # Base score
        
        # Adjust based on resource utilization
        if 'cpu_usage' in k8s_metrics and 'average' in k8s_metrics['cpu_usage']:
            cpu_usage = k8s_metrics['cpu_usage']['average']
            if cpu_usage > 80:
                score -= 10  # High CPU usage is concerning
            elif cpu_usage < 20:
                score -= 5   # Low CPU usage might indicate over-provisioning
        
        if 'memory_usage' in k8s_metrics and 'average' in k8s_metrics['memory_usage']:
            memory_usage = k8s_metrics['memory_usage']['average']
            if memory_usage > 85:
                score -= 15  # High memory usage is critical
            elif memory_usage < 30:
                score -= 3   # Low memory usage might indicate waste
        
        # Adjust based on business metrics
        revenue_metrics = [m for m in business_metrics if m.metric_type == BusinessMetricType.REVENUE]
        if revenue_metrics:
            avg_revenue = sum(m.value for m in revenue_metrics) / len(revenue_metrics)
            if avg_revenue > 1000:  # Assuming high revenue is good
                score += 10
        
        # Normalize score to 0-100 range
        return max(0.0, min(100.0, score))
    
    async def export_business_report(
        self, 
        insights: List[CorrelationInsight],
        impact_score: float
    ) -> Dict[str, Any]:
        """
        Export comprehensive business intelligence report.
        
        Args:
            insights: List of correlation insights
            impact_score: Business impact score
            
        Returns:
            Dictionary containing the business report
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "business_impact_score": impact_score,
            "total_insights": len(insights),
            "high_confidence_insights": len([i for i in insights if i.confidence > 0.8]),
            "actionable_insights": len([i for i in insights if i.actionable]),
            "insights": [
                {
                    "k8s_metric": insight.k8s_metric,
                    "business_metric": insight.business_metric,
                    "correlation_strength": insight.correlation_strength,
                    "confidence": insight.confidence,
                    "description": insight.description,
                    "recommendations": insight.recommendations
                }
                for insight in insights
            ],
            "summary": {
                "status": "healthy" if impact_score > 70 else "needs_attention",
                "key_findings": [
                    f"Found {len(insights)} business correlations",
                    f"Business impact score: {impact_score:.1f}/100",
                    f"{len([i for i in insights if i.actionable])} actionable insights"
                ]
            }
        } 