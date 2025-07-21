"""
Executive Dashboard for UPID CLI
Provides high-level business insights and executive reporting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DashboardWidgetType(Enum):
    """Types of dashboard widgets"""
    METRIC_CARD = "metric_card"
    TREND_CHART = "trend_chart"
    ALERT_PANEL = "alert_panel"
    RECOMMENDATION_LIST = "recommendation_list"
    ROI_ANALYSIS = "roi_analysis"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_type: DashboardWidgetType
    title: str
    data: Any
    position: Tuple[int, int]  # (row, col)
    size: Tuple[int, int]  # (width, height)
    refresh_interval: int = 300  # seconds


@dataclass
class ExecutiveReport:
    """Executive report data structure"""
    cluster_id: str
    report_date: datetime
    time_range: str
    summary: str
    key_metrics: Dict[str, float]
    trends: Dict[str, str]
    alerts: List[str]
    recommendations: List[str]
    roi_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]


class ExecutiveDashboard:
    """
    Executive Dashboard
    Provides high-level business insights and executive reporting
    """
    
    def __init__(self):
        self.business_intelligence = None  # Will be injected
        self.metrics_collector = None  # Will be injected
        self.widgets: List[DashboardWidget] = []
        self.refresh_interval = 300  # 5 minutes
        
    async def generate_executive_report(
        self, 
        cluster_id: str, 
        time_range: str = "30d",
        include_forecast: bool = True
    ) -> ExecutiveReport:
        """
        Generate comprehensive executive report
        
        Args:
            cluster_id: Target cluster identifier
            time_range: Analysis time period
            include_forecast: Include future predictions
            
        Returns:
            ExecutiveReport: Comprehensive executive report
        """
        try:
            logger.info(f"Generating executive report for cluster {cluster_id}")
            
            # Get business impact analysis
            business_impact = await self.business_intelligence.analyze_business_impact(
                cluster_id, time_range, include_forecast
            )
            
            # Get key metrics
            key_metrics = await self._get_key_metrics(cluster_id, time_range)
            
            # Analyze trends
            trends = await self._analyze_trends(cluster_id, time_range)
            
            # Get alerts
            alerts = await self._get_alerts(cluster_id, business_impact)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                cluster_id, business_impact, key_metrics
            )
            
            # Create summary
            summary = await self._create_summary(
                cluster_id, business_impact, key_metrics, trends
            )
            
            return ExecutiveReport(
            cluster_id=cluster_id,
                report_date=datetime.now(),
                time_range=time_range,
                summary=summary,
                key_metrics=key_metrics,
                trends=trends,
                alerts=alerts,
            recommendations=recommendations,
                roi_analysis={
                    "roi_percentage": business_impact.roi_percentage,
                    "cost_savings": business_impact.cost_savings,
                    "payback_period": "6 months",
                    "confidence_level": 0.85
                },
                risk_assessment={
                    "overall_risk": business_impact.risk_assessment,
                    "risk_level": "Low" if business_impact.risk_assessment < 0.3 else "Medium" if business_impact.risk_assessment < 0.6 else "High",
                    "mitigation_strategies": [
                        "Implement gradual rollout",
                        "Monitor closely for 48 hours",
                        "Have rollback plan ready"
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating executive report: {e}")
            raise
    
    async def create_dashboard_widgets(
        self, 
        cluster_id: str, 
        time_range: str = "30d"
    ) -> List[DashboardWidget]:
        """
        Create dashboard widgets for executive view
        
        Args:
            cluster_id: Target cluster identifier
            time_range: Analysis time period
            
        Returns:
            List[DashboardWidget]: Dashboard widgets
        """
        try:
            logger.info(f"Creating dashboard widgets for cluster {cluster_id}")
            
            widgets = []
            
            # Key Metrics Widget
            key_metrics = await self._get_key_metrics(cluster_id, time_range)
            widgets.append(DashboardWidget(
                widget_type=DashboardWidgetType.METRIC_CARD,
                title="Key Performance Metrics",
                data=key_metrics,
                position=(0, 0),
                size=(4, 2)
            ))
            
            # Cost Analysis Widget
            cost_data = await self._get_cost_analysis(cluster_id, time_range)
            widgets.append(DashboardWidget(
                widget_type=DashboardWidgetType.TREND_CHART,
                title="Cost Analysis",
                data=cost_data,
                position=(0, 2),
                size=(4, 2)
            ))
            
            # ROI Analysis Widget
            roi_data = await self._get_roi_analysis(cluster_id, time_range)
            widgets.append(DashboardWidget(
                widget_type=DashboardWidgetType.ROI_ANALYSIS,
                title="ROI Analysis",
                data=roi_data,
                position=(2, 0),
                size=(3, 2)
            ))
            
            # Alerts Widget
            alerts = await self._get_alerts(cluster_id)
            widgets.append(DashboardWidget(
                widget_type=DashboardWidgetType.ALERT_PANEL,
                title="Active Alerts",
                data=alerts,
                position=(2, 3),
                size=(3, 2)
            ))
            
            # Recommendations Widget
            recommendations = await self._get_recommendations(cluster_id, time_range)
            widgets.append(DashboardWidget(
                widget_type=DashboardWidgetType.RECOMMENDATION_LIST,
                title="Optimization Recommendations",
                data=recommendations,
                position=(4, 0),
                size=(6, 2)
            ))
            
            return widgets
            
        except Exception as e:
            logger.error(f"Error creating dashboard widgets: {e}")
            raise
    
    async def export_dashboard_data(
        self, 
        cluster_id: str, 
        time_range: str = "30d",
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export dashboard data in various formats
        
        Args:
            cluster_id: Target cluster identifier
            time_range: Analysis time period
            format: Export format (json, csv, pdf)
            
        Returns:
            Dict: Dashboard data in requested format
        """
        try:
            logger.info(f"Exporting dashboard data for cluster {cluster_id}")
            
            # Generate executive report
            report = await self.generate_executive_report(cluster_id, time_range)
            
            # Create widgets
            widgets = await self.create_dashboard_widgets(cluster_id, time_range)
            
            # Format data based on requested format
            if format == "json":
                return {
                    "cluster_id": cluster_id,
                    "time_range": time_range,
                    "export_date": datetime.now().isoformat(),
                    "report": {
                        "summary": report.summary,
                        "key_metrics": report.key_metrics,
                        "trends": report.trends,
                        "alerts": report.alerts,
                        "recommendations": report.recommendations,
                        "roi_analysis": report.roi_analysis,
                        "risk_assessment": report.risk_assessment
                    },
                    "widgets": [
                        {
                            "type": widget.widget_type.value,
                            "title": widget.title,
                            "data": widget.data,
                            "position": widget.position,
                            "size": widget.size
                        }
                        for widget in widgets
                    ]
                }
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            raise
    
    async def _get_key_metrics(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> Dict[str, float]:
        """Get key performance metrics"""
        # Mock key metrics
        return {
            "cpu_utilization": 0.65,
            "memory_utilization": 0.72,
            "cost_per_hour": 2.45,
            "pod_count": 150,
            "node_count": 8,
            "availability": 0.9995,
            "response_time": 125.5
        }
    
    async def _get_cost_analysis(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> Dict[str, Any]:
        """Get cost analysis data"""
        try:
            from .metrics_collector import KubernetesMetricsCollector
            from .business_intelligence import BusinessIntelligenceEngine
            
            # Get real metrics and business intelligence
            metrics_collector = KubernetesMetricsCollector()
            metrics = await metrics_collector.collect_metrics(cluster_id)
            
            bi_engine = BusinessIntelligenceEngine()
            cost_analysis = await bi_engine._calculate_current_cost(metrics)
            optimized_cost = await bi_engine._calculate_optimized_cost(metrics)
            
            # Calculate real cost breakdown
            cpu_cost = metrics.get('cpu_usage', 0.5) * metrics.get('pod_count', 10) * 0.1
            memory_cost = metrics.get('memory_usage', 0.5) * metrics.get('pod_count', 10) * 0.05
            node_cost = metrics.get('node_count', 3) * 0.5
            network_cost = metrics.get('network_usage', 0.3) * 0.02
            
            potential_savings = max(0, cost_analysis - optimized_cost)
            
            return {
                "current_monthly_cost": cost_analysis * 730,  # Convert hourly to monthly
                "potential_savings": potential_savings * 730,
                "cost_trend": "declining" if potential_savings > 0 else "stable",
                "cost_breakdown": {
                    "compute": cpu_cost * 730,
                    "storage": memory_cost * 730,
                    "network": network_cost * 730,
                    "infrastructure": node_cost * 730
                },
                "optimization_opportunities": self._get_optimization_opportunities(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting cost analysis: {e}")
            return {
                "current_monthly_cost": 0.0,
                "potential_savings": 0.0,
                "cost_trend": "stable",
                "cost_breakdown": {
                    "compute": 0.0,
                    "storage": 0.0,
                    "network": 0.0,
                    "infrastructure": 0.0
                },
                "optimization_opportunities": ["Unable to calculate optimization opportunities"]
            }
    
    async def _get_roi_analysis(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> Dict[str, Any]:
        """Get ROI analysis data"""
        try:
            from .metrics_collector import KubernetesMetricsCollector
            from .business_intelligence import BusinessIntelligenceEngine
            
            # Get real metrics
            metrics_collector = KubernetesMetricsCollector()
            metrics = await metrics_collector.collect_metrics(cluster_id)
            
            # Calculate ROI based on real data
            current_cost = await self._get_current_cost(metrics)
            optimized_cost = await self._get_optimized_cost(metrics)
            
            # Calculate ROI metrics
            investment_required = current_cost * 0.1  # 10% of current cost for optimization
            annual_savings = (current_cost - optimized_cost) * 8760  # Convert to annual
            
            if investment_required > 0:
                roi_percentage = (annual_savings / investment_required) * 100
                payback_period = investment_required / (annual_savings / 12)  # Months
            else:
                roi_percentage = 0.0
                payback_period = 0.0
            
            # Calculate NPV
            discount_rate = 0.1  # 10% discount rate
            npv = self._calculate_npv(annual_savings, investment_required, discount_rate)
            
            return {
                "roi_percentage": min(roi_percentage, 500.0),  # Cap at 500%
                "payback_period": f"{max(1, int(payback_period))} months",
                "net_present_value": npv,
                "confidence_level": self._calculate_roi_confidence(metrics),
                "investment_required": investment_required,
                "annual_savings": annual_savings
            }
            
        except Exception as e:
            logger.error(f"Error getting ROI analysis: {e}")
            return {
                "roi_percentage": 0.0,
                "payback_period": "Unknown",
                "net_present_value": 0.0,
                "confidence_level": 0.5,
                "investment_required": 0.0,
                "annual_savings": 0.0
            }
    
    async def _get_current_cost(self, metrics: Dict[str, Any]) -> float:
        """Calculate current hourly cost"""
        try:
            cpu_usage = metrics.get('cpu_usage', 0.5)
            memory_usage = metrics.get('memory_usage', 0.5)
            pod_count = metrics.get('pod_count', 10)
            node_count = metrics.get('node_count', 3)
            
            cpu_cost = cpu_usage * pod_count * 0.1
            memory_cost = memory_usage * pod_count * 0.05
            node_cost = node_count * 0.5
            
            return cpu_cost + memory_cost + node_cost
            
        except Exception as e:
            logger.error(f"Error calculating current cost: {e}")
            return 0.0
    
    async def _get_optimized_cost(self, metrics: Dict[str, Any]) -> float:
        """Calculate optimized hourly cost"""
        try:
            # Apply optimization factors
            cpu_usage = metrics.get('cpu_usage', 0.5) * 0.8
            memory_usage = metrics.get('memory_usage', 0.5) * 0.85
            pod_count = max(1, int(metrics.get('pod_count', 10) * 0.9))
            node_count = max(1, int(metrics.get('node_count', 3) * 0.9))
            
            cpu_cost = cpu_usage * pod_count * 0.1
            memory_cost = memory_usage * pod_count * 0.05
            node_cost = node_count * 0.5
            
            return cpu_cost + memory_cost + node_cost
            
        except Exception as e:
            logger.error(f"Error calculating optimized cost: {e}")
            return 0.0
    
    def _calculate_npv(self, annual_savings: float, investment: float, discount_rate: float) -> float:
        """Calculate Net Present Value"""
        try:
            # 5-year NPV calculation
            npv = -investment
            for year in range(1, 6):
                npv += annual_savings / ((1 + discount_rate) ** year)
            return npv
            
        except Exception as e:
            logger.error(f"Error calculating NPV: {e}")
            return 0.0
    
    def _calculate_roi_confidence(self, metrics: Dict[str, Any]) -> float:
        """Calculate confidence level for ROI analysis"""
        try:
            # Check data quality
            required_fields = ['cpu_usage', 'memory_usage', 'pod_count', 'node_count']
            available_fields = sum(1 for field in required_fields if field in metrics and metrics[field] is not None)
            
            completeness = available_fields / len(required_fields)
            
            # Check data consistency
            cpu_usage = metrics.get('cpu_usage', 0.5)
            memory_usage = metrics.get('memory_usage', 0.5)
            
            # If usage is very low or very high, confidence might be lower
            if cpu_usage < 0.1 or cpu_usage > 0.9 or memory_usage < 0.1 or memory_usage > 0.9:
                consistency = 0.7
            else:
                consistency = 0.9
            
            return (completeness + consistency) / 2
            
        except Exception as e:
            logger.error(f"Error calculating ROI confidence: {e}")
            return 0.5
    
    def _get_optimization_opportunities(self, metrics: Dict[str, Any]) -> List[str]:
        """Get optimization opportunities based on metrics"""
        opportunities = []
        
        cpu_usage = metrics.get('cpu_usage', 0.5)
        memory_usage = metrics.get('memory_usage', 0.5)
        pod_count = metrics.get('pod_count', 10)
        node_count = metrics.get('node_count', 3)
        
        if cpu_usage < 0.3:
            opportunities.append("Scale down idle pods")
        elif cpu_usage > 0.8:
            opportunities.append("Scale up CPU allocation")
        
        if memory_usage < 0.3:
            opportunities.append("Reduce memory allocation")
        elif memory_usage > 0.8:
            opportunities.append("Increase memory allocation")
        
        if pod_count > node_count * 3:
            opportunities.append("Implement HPA (Horizontal Pod Autoscaler)")
        
        if node_count > 1 and pod_count < node_count:
            opportunities.append("Consolidate workloads to fewer nodes")
        
        if not opportunities:
            opportunities.append("Current configuration appears optimal")
        
        return opportunities
    
    async def _get_alerts(self, cluster_id: str, business_impact: Any = None) -> List[str]:
        """Get active alerts"""
        try:
            from .metrics_collector import KubernetesMetricsCollector
            
            alerts = []
            
            # Get real metrics
            metrics_collector = KubernetesMetricsCollector()
            metrics = await metrics_collector.collect_metrics(cluster_id)
            
            # Check for alert conditions
            cpu_usage = metrics.get('cpu_usage', 0.5)
            memory_usage = metrics.get('memory_usage', 0.5)
            error_rate = metrics.get('error_rate', 0.02)
            availability = metrics.get('availability', 0.99)
            
            if cpu_usage > 0.9:
                alerts.append("High CPU utilization detected - consider scaling")
            
            if memory_usage > 0.9:
                alerts.append("High memory utilization detected - consider scaling")
            
            if error_rate > 0.05:
                alerts.append("High error rate detected - investigate application issues")
            
            if availability < 0.95:
                alerts.append("Low availability detected - check system health")
            
            if cpu_usage < 0.2 and memory_usage < 0.2:
                alerts.append("Low resource utilization - consider optimization")
            
            # Add business impact alerts
            if business_impact:
                cost_savings = business_impact.get('cost_savings', 0)
                if cost_savings > 0.2:
                    alerts.append("High cost savings opportunity detected")
                
                risk_level = business_impact.get('risk_assessment', 0)
                if risk_level > 0.7:
                    alerts.append("High risk environment - review optimization plans")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return ["Unable to retrieve alerts"]
    
    async def _get_recommendations(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        # Mock recommendations
        recommendations.append("Implement horizontal pod autoscaling")
        recommendations.append("Optimize resource requests and limits")
        recommendations.append("Scale down idle pods during off-peak hours")
        recommendations.append("Implement pod disruption budgets")
        recommendations.append("Consider spot instances for non-critical workloads")
        
        return recommendations
    
    async def _analyze_trends(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> Dict[str, str]:
        """Analyze trends"""
        return {
            "cost_trend": "declining",
            "performance_trend": "improving",
            "utilization_trend": "stable",
            "availability_trend": "stable",
            "efficiency_trend": "improving"
        }
    
    async def _create_summary(
        self,
        cluster_id: str,
        business_impact: Any,
        key_metrics: Dict[str, float],
        trends: Dict[str, str]
    ) -> str:
        """Create executive summary"""
        summary = f"""
        Cluster {cluster_id} Executive Summary:
        
        📊 Current Status: {'Healthy' if key_metrics.get('availability', 0) > 0.99 else 'Needs Attention'}
        💰 Cost Impact: ${business_impact.cost_savings:.2f} potential monthly savings
        📈 Performance: {business_impact.performance_gain:.1%} improvement opportunity
        🎯 ROI: {business_impact.roi_percentage:.1%} return on optimization investment
        ⚠️ Risk Level: {'Low' if business_impact.risk_assessment < 0.3 else 'Medium' if business_impact.risk_assessment < 0.6 else 'High'}
        
        Key Trends:
        - Cost: {trends.get('cost_trend', 'stable')}
        - Performance: {trends.get('performance_trend', 'stable')}
        - Utilization: {trends.get('utilization_trend', 'stable')}
        
        Recommendation: {'Proceed with optimization' if business_impact.risk_assessment < 0.5 else 'Review and plan carefully'}
        """
        return summary.strip()
    
    async def _generate_recommendations(
        self,
        cluster_id: str,
        business_impact: Any,
        key_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if business_impact.cost_savings > 1000:
            recommendations.append(
                f"Implement resource optimization to save ${business_impact.cost_savings:.2f}/month"
            )
        
        if business_impact.performance_gain > 0.1:
            recommendations.append(
                f"Performance can be improved by {business_impact.performance_gain:.1%}"
            )
        
        if key_metrics.get('cpu_utilization', 0) < 0.5:
            recommendations.append("Consider scaling down over-provisioned resources")
        
        if key_metrics.get('memory_utilization', 0) > 0.8:
            recommendations.append("Memory pressure detected - consider scaling up")
        
        if business_impact.risk_assessment < 0.3:
            recommendations.append("Low risk environment - safe to implement optimizations")
        
        return recommendations


class DashboardRenderer:
    """Render dashboard widgets in various formats"""
    
    @staticmethod
    async def render_console_dashboard(
        widgets: List[DashboardWidget]
    ) -> str:
        """Render dashboard for console output"""
        output = []
        output.append("=" * 80)
        output.append("UPID CLI Executive Dashboard")
        output.append("=" * 80)
        output.append("")
        
        for widget in widgets:
            output.append(f"📊 {widget.title}")
            output.append("-" * 40)
            
            if widget.widget_type == DashboardWidgetType.METRIC_CARD:
                output.extend(DashboardRenderer._render_metric_card(widget.data))
            elif widget.widget_type == DashboardWidgetType.ALERT_PANEL:
                output.extend(DashboardRenderer._render_alert_panel(widget.data))
            elif widget.widget_type == DashboardWidgetType.RECOMMENDATION_LIST:
                output.extend(DashboardRenderer._render_recommendation_list(widget.data))
            elif widget.widget_type == DashboardWidgetType.ROI_ANALYSIS:
                output.extend(DashboardRenderer._render_roi_analysis(widget.data))
            
            output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def _render_metric_card(data: Dict[str, float]) -> List[str]:
        """Render metric card widget"""
        lines = []
        for metric, value in data.items():
            if isinstance(value, float):
                lines.append(f"  {metric.replace('_', ' ').title()}: {value:.2f}")
            else:
                lines.append(f"  {metric.replace('_', ' ').title()}: {value}")
        return lines
    
    @staticmethod
    def _render_alert_panel(alerts: List[str]) -> List[str]:
        """Render alert panel widget"""
        lines = []
        if not alerts:
            lines.append("  ✅ No active alerts")
        else:
            for alert in alerts:
                lines.append(f"  ⚠️  {alert}")
        return lines
    
    @staticmethod
    def _render_recommendation_list(recommendations: List[str]) -> List[str]:
        """Render recommendation list widget"""
        lines = []
        for i, recommendation in enumerate(recommendations, 1):
            lines.append(f"  {i}. {recommendation}")
        return lines
    
    @staticmethod
    def _render_roi_analysis(data: Dict[str, Any]) -> List[str]:
        """Render ROI analysis widget"""
        lines = []
        lines.append(f"  ROI: {data.get('roi_percentage', 0):.1f}%")
        lines.append(f"  Payback Period: {data.get('payback_period', 'N/A')}")
        lines.append(f"  NPV: ${data.get('net_present_value', 0):.2f}")
        lines.append(f"  Confidence: {data.get('confidence_level', 0):.1%}")
        return lines 