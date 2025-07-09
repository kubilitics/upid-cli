"""
Intelligence Engine - Main Intelligence Module
Integrates all intelligence capabilities including business correlation, predictive analytics, and optimization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .business_intelligence import BusinessIntelligenceEngine, BusinessMetric, BusinessMetricType
from .predictive_analytics import PredictiveAnalyticsEngine, Prediction, AnomalyDetection
from .intelligent_optimization import IntelligentOptimizationEngine, OptimizationRecommendation, ResourceProfile
from .metrics_collector import KubernetesMetricsCollector

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceReport:
    """Comprehensive intelligence report combining all analysis."""
    timestamp: datetime
    business_insights: List[Any]
    predictions: List[Prediction]
    anomalies: List[AnomalyDetection]
    optimizations: List[OptimizationRecommendation]
    resource_profiles: List[ResourceProfile]
    summary: Dict[str, Any]


class IntelligenceEngine:
    """
    Main Intelligence Engine that orchestrates all intelligence capabilities.
    """
    
    def __init__(self):
        self.business_engine = BusinessIntelligenceEngine()
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.optimization_engine = IntelligentOptimizationEngine()
        self.metrics_collector = KubernetesMetricsCollector()
        
    async def run_comprehensive_analysis(
        self,
        cluster_context: Optional[str] = None,
        business_metrics: Optional[List[BusinessMetric]] = None,
        cost_data: Optional[Dict[str, Any]] = None
    ) -> IntelligenceReport:
        """
        Run comprehensive intelligence analysis including all engines.
        
        Args:
            cluster_context: Kubernetes cluster context
            business_metrics: Optional business metrics for correlation
            cost_data: Optional cost data for optimization
            
        Returns:
            Comprehensive intelligence report
        """
        logger.info("Starting comprehensive intelligence analysis")
        
        # Collect Kubernetes metrics
        k8s_metrics = await self.metrics_collector.collect_metrics(cluster_context)
        historical_data = await self.metrics_collector.get_historical_data(cluster_context)
        
        # Run business intelligence analysis
        business_insights = []
        business_impact_score = 0.0
        if business_metrics and k8s_metrics:
            business_insights = await self.business_engine.analyze_business_correlation(
                k8s_metrics, business_metrics
            )
            business_impact_score = await self.business_engine.get_business_impact_score(
                k8s_metrics, business_metrics
            )
        
        # Run predictive analytics
        predictions = await self.predictive_engine.predict_resource_usage(
            k8s_metrics, historical_data
        )
        anomalies = await self.predictive_engine.detect_anomalies(
            k8s_metrics, historical_data
        )
        
        # Run intelligent optimization
        resource_profiles = await self.optimization_engine.analyze_resource_profiles(
            k8s_metrics, historical_data
        )
        optimizations = await self.optimization_engine.generate_optimization_recommendations(
            resource_profiles, cost_data
        )
        
        # Generate comprehensive summary
        summary = await self._generate_comprehensive_summary(
            business_insights, predictions, anomalies, optimizations, business_impact_score
        )
        
        report = IntelligenceReport(
            timestamp=datetime.now(),
            business_insights=business_insights,
            predictions=predictions,
            anomalies=anomalies,
            optimizations=optimizations,
            resource_profiles=resource_profiles,
            summary=summary
        )
        
        logger.info("Completed comprehensive intelligence analysis")
        return report
    
    async def run_business_intelligence(
        self,
        cluster_context: Optional[str] = None,
        business_metrics: Optional[List[BusinessMetric]] = None
    ) -> Dict[str, Any]:
        """
        Run business intelligence analysis only.
        
        Args:
            cluster_context: Kubernetes cluster context
            business_metrics: Business metrics for correlation
            
        Returns:
            Business intelligence report
        """
        logger.info("Running business intelligence analysis")
        
        k8s_metrics = await self.metrics_collector.collect_metrics(cluster_context)
        
        if not business_metrics:
            # Generate sample business metrics for demonstration
            business_metrics = await self._generate_sample_business_metrics()
        
        insights = await self.business_engine.analyze_business_correlation(
            k8s_metrics, business_metrics
        )
        impact_score = await self.business_engine.get_business_impact_score(
            k8s_metrics, business_metrics
        )
        recommendations = await self.business_engine.generate_business_recommendations(insights)
        
        return await self.business_engine.export_business_report(insights, impact_score)
    
    async def run_predictive_analytics(
        self,
        cluster_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run predictive analytics analysis only.
        
        Args:
            cluster_context: Kubernetes cluster context
            
        Returns:
            Predictive analytics report
        """
        logger.info("Running predictive analytics analysis")
        
        k8s_metrics = await self.metrics_collector.collect_metrics(cluster_context)
        historical_data = await self.metrics_collector.get_historical_data(cluster_context)
        
        predictions = await self.predictive_engine.predict_resource_usage(
            k8s_metrics, historical_data
        )
        anomalies = await self.predictive_engine.detect_anomalies(
            k8s_metrics, historical_data
        )
        
        return await self.predictive_engine.generate_predictive_report(predictions, anomalies)
    
    async def run_intelligent_optimization(
        self,
        cluster_context: Optional[str] = None,
        cost_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run intelligent optimization analysis only.
        
        Args:
            cluster_context: Kubernetes cluster context
            cost_data: Optional cost data for optimization
            
        Returns:
            Optimization report
        """
        logger.info("Running intelligent optimization analysis")
        
        k8s_metrics = await self.metrics_collector.collect_metrics(cluster_context)
        historical_data = await self.metrics_collector.get_historical_data(cluster_context)
        
        resource_profiles = await self.optimization_engine.analyze_resource_profiles(
            k8s_metrics, historical_data
        )
        optimizations = await self.optimization_engine.generate_optimization_recommendations(
            resource_profiles, cost_data
        )
        
        return await self.optimization_engine.generate_optimization_report(
            resource_profiles, optimizations
        )
    
    async def get_real_time_insights(
        self,
        cluster_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get real-time insights from current cluster state.
        
        Args:
            cluster_context: Kubernetes cluster context
            
        Returns:
            Real-time insights report
        """
        logger.info("Getting real-time insights")
        
        k8s_metrics = await self.metrics_collector.collect_metrics(cluster_context)
        
        insights = {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": k8s_metrics,
            "health_status": await self._assess_cluster_health(k8s_metrics),
            "immediate_alerts": await self._generate_immediate_alerts(k8s_metrics),
            "quick_recommendations": await self._generate_quick_recommendations(k8s_metrics)
        }
        
        return insights
    
    async def _generate_comprehensive_summary(
        self,
        business_insights: List[Any],
        predictions: List[Prediction],
        anomalies: List[AnomalyDetection],
        optimizations: List[OptimizationRecommendation],
        business_impact_score: float
    ) -> Dict[str, Any]:
        """Generate comprehensive summary of all intelligence analysis."""
        
        critical_anomalies = [a for a in anomalies if a.severity in ['high', 'critical']]
        high_priority_optimizations = [o for o in optimizations if o.priority in ['high', 'critical']]
        
        return {
            "overall_status": self._determine_overall_status(
                business_impact_score, len(critical_anomalies), len(high_priority_optimizations)
            ),
            "key_metrics": {
                "business_impact_score": business_impact_score,
                "total_predictions": len(predictions),
                "high_confidence_predictions": len([p for p in predictions if p.confidence > 0.8]),
                "total_anomalies": len(anomalies),
                "critical_anomalies": len(critical_anomalies),
                "total_optimizations": len(optimizations),
                "high_priority_optimizations": len(high_priority_optimizations)
            },
            "priority_actions": await self._generate_priority_actions(
                business_insights, predictions, anomalies, optimizations
            ),
            "trends": await self._identify_trends(predictions, anomalies),
            "recommendations": await self._generate_top_recommendations(
                business_insights, predictions, anomalies, optimizations
            )
        }
    
    async def _generate_sample_business_metrics(self) -> List[BusinessMetric]:
        """Generate sample business metrics for demonstration."""
        now = datetime.now()
        
        return [
            BusinessMetric(
                name="Revenue",
                value=15000.0,
                timestamp=now,
                metric_type=BusinessMetricType.REVENUE,
                unit="USD",
                description="Daily revenue"
            ),
            BusinessMetric(
                name="User Activity",
                value=2500.0,
                timestamp=now,
                metric_type=BusinessMetricType.USER_ACTIVITY,
                unit="users",
                description="Active users"
            ),
            BusinessMetric(
                name="Transaction Volume",
                value=5000.0,
                timestamp=now,
                metric_type=BusinessMetricType.TRANSACTION_VOLUME,
                unit="transactions",
                description="Daily transactions"
            ),
            BusinessMetric(
                name="Error Rate",
                value=2.5,
                timestamp=now,
                metric_type=BusinessMetricType.ERROR_RATE,
                unit="%",
                description="Application error rate"
            )
        ]
    
    async def _assess_cluster_health(self, metrics: Dict[str, Any]) -> str:
        """Assess overall cluster health based on metrics."""
        health_score = 100
        
        if 'cpu_usage' in metrics and 'average' in metrics['cpu_usage']:
            cpu_usage = metrics['cpu_usage']['average']
            if cpu_usage > 90:
                health_score -= 30
            elif cpu_usage > 80:
                health_score -= 15
        
        if 'memory_usage' in metrics and 'average' in metrics['memory_usage']:
            memory_usage = metrics['memory_usage']['average']
            if memory_usage > 95:
                health_score -= 40
            elif memory_usage > 85:
                health_score -= 20
        
        if 'error_rate' in metrics and 'rate' in metrics['error_rate']:
            error_rate = metrics['error_rate']['rate']
            if error_rate > 5:
                health_score -= 25
            elif error_rate > 2:
                health_score -= 10
        
        if health_score >= 80:
            return "healthy"
        elif health_score >= 60:
            return "warning"
        else:
            return "critical"
    
    async def _generate_immediate_alerts(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate immediate alerts based on current metrics."""
        alerts = []
        
        if 'cpu_usage' in metrics and 'average' in metrics['cpu_usage']:
            cpu_usage = metrics['cpu_usage']['average']
            if cpu_usage > 90:
                alerts.append("CRITICAL: CPU usage above 90% - immediate scaling required")
            elif cpu_usage > 80:
                alerts.append("WARNING: CPU usage above 80% - monitor closely")
        
        if 'memory_usage' in metrics and 'average' in metrics['memory_usage']:
            memory_usage = metrics['memory_usage']['average']
            if memory_usage > 95:
                alerts.append("CRITICAL: Memory usage above 95% - OOM risk")
            elif memory_usage > 85:
                alerts.append("WARNING: Memory usage above 85% - monitor memory pressure")
        
        if 'error_rate' in metrics and 'rate' in metrics['error_rate']:
            error_rate = metrics['error_rate']['rate']
            if error_rate > 5:
                alerts.append("CRITICAL: Error rate above 5% - investigate immediately")
            elif error_rate > 2:
                alerts.append("WARNING: Error rate above 2% - review error handling")
        
        return alerts
    
    async def _generate_quick_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate quick recommendations based on current metrics."""
        recommendations = []
        
        if 'cpu_usage' in metrics and 'average' in metrics['cpu_usage']:
            cpu_usage = metrics['cpu_usage']['average']
            if cpu_usage < 30:
                recommendations.append("Consider reducing CPU requests to optimize costs")
            elif cpu_usage > 80:
                recommendations.append("Consider horizontal scaling or increasing CPU limits")
        
        if 'memory_usage' in metrics and 'average' in metrics['memory_usage']:
            memory_usage = metrics['memory_usage']['average']
            if memory_usage < 40:
                recommendations.append("Consider reducing memory requests to optimize costs")
            elif memory_usage > 85:
                recommendations.append("Consider increasing memory limits or investigating memory leaks")
        
        return recommendations
    
    def _determine_overall_status(
        self,
        business_impact_score: float,
        critical_anomalies: int,
        high_priority_optimizations: int
    ) -> str:
        """Determine overall system status."""
        if critical_anomalies > 0:
            return "critical"
        elif business_impact_score < 50 or high_priority_optimizations > 3:
            return "warning"
        else:
            return "healthy"
    
    async def _generate_priority_actions(
        self,
        business_insights: List[Any],
        predictions: List[Prediction],
        anomalies: List[AnomalyDetection],
        optimizations: List[OptimizationRecommendation]
    ) -> List[str]:
        """Generate priority actions based on all analysis."""
        actions = []
        
        # Critical anomalies require immediate action
        critical_anomalies = [a for a in anomalies if a.severity == 'critical']
        for anomaly in critical_anomalies:
            actions.append(f"URGENT: {anomaly.description}")
        
        # High priority optimizations
        high_optimizations = [o for o in optimizations if o.priority == 'high']
        for opt in high_optimizations[:3]:  # Top 3
            actions.append(f"OPTIMIZE: {opt.description}")
        
        # High confidence predictions
        high_confidence_predictions = [p for p in predictions if p.confidence > 0.9]
        for pred in high_confidence_predictions[:2]:  # Top 2
            actions.append(f"PREPARE: {pred.description}")
        
        return actions
    
    async def _identify_trends(
        self,
        predictions: List[Prediction],
        anomalies: List[AnomalyDetection]
    ) -> List[str]:
        """Identify trends from predictions and anomalies."""
        trends = []
        
        # Analyze prediction trends
        resource_predictions = [p for p in predictions if p.prediction_type.value == 'resource_usage']
        if resource_predictions:
            avg_predicted_value = sum(p.predicted_value for p in resource_predictions) / len(resource_predictions)
            if avg_predicted_value > 80:
                trends.append("Trending: Resource usage expected to increase")
            elif avg_predicted_value < 30:
                trends.append("Trending: Resource usage expected to decrease")
        
        # Analyze anomaly trends
        if len(anomalies) > 2:
            trends.append("Trending: Multiple anomalies detected - investigate patterns")
        
        return trends
    
    async def _generate_top_recommendations(
        self,
        business_insights: List[Any],
        predictions: List[Prediction],
        anomalies: List[AnomalyDetection],
        optimizations: List[OptimizationRecommendation]
    ) -> List[str]:
        """Generate top recommendations from all analysis."""
        recommendations = []
        
        # Top business recommendations
        if business_insights:
            actionable_insights = [i for i in business_insights if hasattr(i, 'actionable') and i.actionable]
            for insight in actionable_insights[:2]:
                if hasattr(insight, 'recommendations'):
                    recommendations.extend(insight.recommendations[:1])
        
        # Top optimization recommendations
        high_priority_optimizations = [o for o in optimizations if o.priority in ['high', 'critical']]
        for opt in high_priority_optimizations[:2]:
            recommendations.append(opt.description)
        
        # Top anomaly recommendations
        critical_anomalies = [a for a in anomalies if a.severity in ['high', 'critical']]
        for anomaly in critical_anomalies[:2]:
            recommendations.extend(anomaly.recommendations[:1])
        
        return list(set(recommendations))[:5]  # Top 5 unique recommendations 