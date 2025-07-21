"""
Business Intelligence Engine for UPID CLI
Provides executive-level insights and business impact analysis
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BusinessMetricType(Enum):
    """Types of business metrics"""
    COST_SAVINGS = "cost_savings"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    RESOURCE_UTILIZATION = "resource_utilization"
    SLA_COMPLIANCE = "sla_compliance"
    BUSINESS_IMPACT = "business_impact"


@dataclass
class BusinessKPI:
    """Business KPI data structure"""
    metric_type: BusinessMetricType
    current_value: float
    target_value: float
    unit: str
    trend: str  # "improving", "declining", "stable"
    confidence: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 1.0


@dataclass
class BusinessImpact:
    """Business impact analysis result"""
    roi_percentage: float
    cost_savings: float
    performance_gain: float
    risk_assessment: float
    recommendations: List[str]
    executive_summary: str


class BusinessIntelligenceEngine:
    """
    Business Intelligence Engine
    Provides executive-level insights and business impact analysis
    """
    
    def __init__(self):
        self.cost_calculator = CostCalculator()
        self.performance_analyzer = PerformanceAnalyzer()
        self.roi_calculator = ROICalculator()
        self.risk_assessor = BusinessRiskAssessor()
        
    async def analyze_business_impact(
        self, 
        cluster_id: str, 
        time_range: str = "30d",
        include_forecast: bool = True
    ) -> BusinessImpact:
        """
        Analyze business impact of cluster optimization
        
        Args:
            cluster_id: Target cluster identifier
            time_range: Analysis time period
            include_forecast: Include future predictions
            
        Returns:
            BusinessImpact: Comprehensive business impact analysis
        """
        try:
            logger.info(f"Analyzing business impact for cluster {cluster_id}")
            
            # Collect current metrics
            current_metrics = await self._collect_current_metrics(cluster_id, time_range)
            
            # Calculate cost analysis
            cost_analysis = await self.cost_calculator.analyze(
                cluster_id, current_metrics, time_range
            )
            
            # Analyze performance impact
            performance_analysis = await self.performance_analyzer.analyze(
                cluster_id, current_metrics, time_range
            )
            
            # Calculate ROI
            roi_analysis = await self.roi_calculator.calculate(
                cluster_id, cost_analysis, performance_analysis, time_range
            )
            
            # Assess business risks
            risk_assessment = await self.risk_assessor.assess(
                cluster_id, current_metrics, cost_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                cost_analysis, performance_analysis, risk_assessment
            )
            
            # Create executive summary
            executive_summary = await self._create_executive_summary(
                cost_analysis, performance_analysis, roi_analysis, risk_assessment
            )
            
            return BusinessImpact(
                roi_percentage=roi_analysis.roi_percentage,
                cost_savings=cost_analysis.potential_savings,
                performance_gain=performance_analysis.performance_gain,
                risk_assessment=risk_assessment.overall_risk,
                recommendations=recommendations,
                executive_summary=executive_summary
            )
            
        except Exception as e:
            logger.error(f"Error analyzing business impact: {e}")
            raise
    
    async def get_executive_dashboard(
        self, 
        cluster_id: str, 
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Generate executive dashboard with key business metrics
        
        Args:
            cluster_id: Target cluster identifier
            time_range: Analysis time period
            
        Returns:
            Dict: Executive dashboard data
        """
        try:
            logger.info(f"Generating executive dashboard for cluster {cluster_id}")
            
            # Get business impact analysis
            business_impact = await self.analyze_business_impact(cluster_id, time_range)
            
            # Get KPIs
            kpis = await self._calculate_kpis(cluster_id, time_range)
            
            # Get trends
            trends = await self._analyze_trends(cluster_id, time_range)
            
            # Get alerts
            alerts = await self._get_business_alerts(cluster_id, business_impact)
            
            return {
                "cluster_id": cluster_id,
                "time_range": time_range,
                "business_impact": business_impact,
                "kpis": kpis,
                "trends": trends,
                "alerts": alerts,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating executive dashboard: {e}")
            raise
    
    async def _collect_current_metrics(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> Dict[str, Any]:
        """Collect current cluster metrics for business analysis"""
        # This would integrate with the metrics collector
        # For now, return mock data
        return {
            "cpu_utilization": 0.65,
            "memory_utilization": 0.72,
            "network_io": 1024.5,
            "cost_per_hour": 2.45,
            "pod_count": 150,
            "node_count": 8
        }
    
    async def _generate_recommendations(
        self,
        cost_analysis: Any,
        performance_analysis: Any,
        risk_assessment: Any
    ) -> List[str]:
        """Generate business recommendations"""
        recommendations = []
        
        if cost_analysis.potential_savings > 1000:
            recommendations.append(
                f"Implement resource optimization to save ${cost_analysis.potential_savings:.2f}/month"
            )
        
        if performance_analysis.performance_gain > 0.1:
            recommendations.append(
                f"Performance can be improved by {performance_analysis.performance_gain:.1%}"
            )
        
        if risk_assessment.overall_risk < 0.3:
            recommendations.append("Low risk environment - safe to implement optimizations")
        
        return recommendations
    
    async def _create_executive_summary(
        self,
        cost_analysis: Any,
        performance_analysis: Any,
        roi_analysis: Any,
        risk_assessment: Any
    ) -> str:
        """Create executive summary"""
        summary = f"""
        Cluster Optimization Analysis Summary:
        
        💰 Cost Impact: ${cost_analysis.potential_savings:.2f} potential monthly savings
        📈 Performance: {performance_analysis.performance_gain:.1%} improvement opportunity
        🎯 ROI: {roi_analysis.roi_percentage:.1%} return on optimization investment
        ⚠️ Risk Level: {'Low' if risk_assessment.overall_risk < 0.3 else 'Medium' if risk_assessment.overall_risk < 0.6 else 'High'}
        
        Recommendation: {'Proceed with optimization' if risk_assessment.overall_risk < 0.5 else 'Review and plan carefully'}
        """
        return summary.strip()
    
    async def _calculate_kpis(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> List[BusinessKPI]:
        """Calculate key performance indicators"""
        try:
            from .metrics_collector import KubernetesMetricsCollector
            from .storage_integration import StorageIntegration
            
            # Get real metrics data
            metrics_collector = KubernetesMetricsCollector()
            metrics = await metrics_collector.collect_metrics(cluster_id)
            
            # Calculate real KPIs based on actual data
            kpis = []
            
            # Cost Savings KPI
            current_cost = self._calculate_current_cost(metrics)
            optimized_cost = self._calculate_optimized_cost(metrics)
            cost_savings = (current_cost - optimized_cost) / current_cost if current_cost > 0 else 0
            
            kpis.append(BusinessKPI(
                metric_type=BusinessMetricType.COST_SAVINGS,
                current_value=cost_savings,
                target_value=0.25,  # 25% target
                unit="%",
                trend="improving" if cost_savings > 0.15 else "stable" if cost_savings > 0.05 else "declining",
                confidence=self._calculate_confidence(metrics),
                impact_score=min(1.0, cost_savings * 4)  # Scale to 0-1
            ))
            
            # Performance Improvement KPI
            current_performance = self._calculate_performance_score(metrics)
            target_performance = 0.85
            
            kpis.append(BusinessKPI(
                metric_type=BusinessMetricType.PERFORMANCE_IMPROVEMENT,
                current_value=current_performance,
                target_value=target_performance,
                unit="%",
                trend="improving" if current_performance > 0.8 else "stable" if current_performance > 0.7 else "declining",
                confidence=self._calculate_confidence(metrics),
                impact_score=current_performance
            ))
            
            # Resource Utilization KPI
            resource_utilization = self._calculate_resource_utilization(metrics)
            target_utilization = 0.75
            
            kpis.append(BusinessKPI(
                metric_type=BusinessMetricType.RESOURCE_UTILIZATION,
                current_value=resource_utilization,
                target_value=target_utilization,
                unit="%",
                trend="improving" if resource_utilization > 0.7 else "stable" if resource_utilization > 0.6 else "declining",
                confidence=self._calculate_confidence(metrics),
                impact_score=resource_utilization
            ))
            
            return kpis
            
        except Exception as e:
            logger.error(f"Error calculating KPIs: {e}")
            # Return basic KPIs on error
            return [
                BusinessKPI(
                    metric_type=BusinessMetricType.COST_SAVINGS,
                    current_value=0.0,
                    target_value=0.25,
                    unit="%",
                    trend="stable",
                    confidence=0.5,
                    impact_score=0.0
                )
            ]
    
    def _calculate_current_cost(self, metrics: Dict[str, Any]) -> float:
        """Calculate current cost based on metrics"""
        try:
            # Extract cost-related metrics
            cpu_usage = metrics.get('cpu_usage', 0.5)
            memory_usage = metrics.get('memory_usage', 0.5)
            pod_count = metrics.get('pod_count', 10)
            node_count = metrics.get('node_count', 3)
            
            # Simple cost calculation (in production, this would use real pricing)
            cpu_cost = cpu_usage * pod_count * 0.1  # $0.1 per CPU hour
            memory_cost = memory_usage * pod_count * 0.05  # $0.05 per GB hour
            node_cost = node_count * 0.5  # $0.5 per node hour
            
            return cpu_cost + memory_cost + node_cost
            
        except Exception as e:
            logger.error(f"Error calculating current cost: {e}")
            return 0.0
    
    def _calculate_optimized_cost(self, metrics: Dict[str, Any]) -> float:
        """Calculate optimized cost based on metrics"""
        try:
            # Apply optimization factors
            cpu_usage = metrics.get('cpu_usage', 0.5) * 0.8  # 20% optimization
            memory_usage = metrics.get('memory_usage', 0.5) * 0.85  # 15% optimization
            pod_count = max(1, int(metrics.get('pod_count', 10) * 0.9))  # 10% reduction
            node_count = max(1, int(metrics.get('node_count', 3) * 0.9))  # 10% reduction
            
            # Calculate optimized cost
            cpu_cost = cpu_usage * pod_count * 0.1
            memory_cost = memory_usage * pod_count * 0.05
            node_cost = node_count * 0.5
            
            return cpu_cost + memory_cost + node_cost
            
        except Exception as e:
            logger.error(f"Error calculating optimized cost: {e}")
            return 0.0
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate performance score based on metrics"""
        try:
            # Extract performance metrics
            response_time = metrics.get('response_time', 100)
            error_rate = metrics.get('error_rate', 0.02)
            availability = metrics.get('availability', 0.99)
            
            # Calculate performance score (0-1)
            response_score = max(0, 1 - (response_time - 50) / 200)  # Normalize response time
            error_score = max(0, 1 - error_rate * 10)  # Normalize error rate
            availability_score = availability
            
            # Weighted average
            performance_score = (response_score * 0.4 + error_score * 0.3 + availability_score * 0.3)
            
            return min(1.0, max(0.0, performance_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 0.5
    
    def _calculate_resource_utilization(self, metrics: Dict[str, Any]) -> float:
        """Calculate resource utilization score"""
        try:
            cpu_usage = metrics.get('cpu_usage', 0.5)
            memory_usage = metrics.get('memory_usage', 0.5)
            
            # Average utilization
            utilization = (cpu_usage + memory_usage) / 2
            
            return min(1.0, max(0.0, utilization))
            
        except Exception as e:
            logger.error(f"Error calculating resource utilization: {e}")
            return 0.5
    
    def _calculate_confidence(self, metrics: Dict[str, Any]) -> float:
        """Calculate confidence level based on data quality"""
        try:
            # Check data completeness
            required_fields = ['cpu_usage', 'memory_usage', 'pod_count']
            available_fields = sum(1 for field in required_fields if field in metrics and metrics[field] is not None)
            
            completeness = available_fields / len(required_fields)
            
            # Check data freshness (assuming metrics have timestamps)
            freshness = 1.0  # Placeholder for real freshness calculation
            
            # Overall confidence
            confidence = (completeness + freshness) / 2
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    async def _analyze_trends(
        self, 
        cluster_id: str, 
        time_range: str
    ) -> Dict[str, Any]:
        """Analyze business trends"""
        try:
            from .metrics_collector import KubernetesMetricsCollector
            
            # Get historical data
            metrics_collector = KubernetesMetricsCollector()
            historical_data = await metrics_collector.get_historical_data(cluster_id)
            
            # Analyze trends
            cost_trend = self._analyze_cost_trend(historical_data)
            performance_trend = self._analyze_performance_trend(historical_data)
            utilization_trend = self._analyze_utilization_trend(historical_data)
            
            # Generate forecasts
            forecast = self._generate_forecast(historical_data, time_range)
            
            return {
                "cost_trend": cost_trend,
                "performance_trend": performance_trend,
                "utilization_trend": utilization_trend,
                "forecast": forecast
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {
                "cost_trend": "stable",
                "performance_trend": "stable",
                "utilization_trend": "stable",
                "forecast": {
                    "next_month_cost": 0.0,
                    "next_month_savings": 0.0,
                    "performance_prediction": 0.5
                }
            }
    
    def _analyze_cost_trend(self, historical_data: Dict[str, Any]) -> str:
        """Analyze cost trend from historical data"""
        try:
            costs = historical_data.get('cost', [])
            if len(costs) < 2:
                return "stable"
            
            # Calculate trend
            recent_avg = sum(costs[-3:]) / min(3, len(costs))
            older_avg = sum(costs[:-3]) / max(1, len(costs) - 3)
            
            if recent_avg < older_avg * 0.95:
                return "declining"
            elif recent_avg > older_avg * 1.05:
                return "increasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error analyzing cost trend: {e}")
            return "stable"
    
    def _analyze_performance_trend(self, historical_data: Dict[str, Any]) -> str:
        """Analyze performance trend from historical data"""
        try:
            # Use error rates as performance indicator
            errors = historical_data.get('errors', [])
            if len(errors) < 2:
                return "stable"
            
            recent_avg = sum(errors[-3:]) / min(3, len(errors))
            older_avg = sum(errors[:-3]) / max(1, len(errors) - 3)
            
            if recent_avg < older_avg * 0.9:
                return "improving"
            elif recent_avg > older_avg * 1.1:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error analyzing performance trend: {e}")
            return "stable"
    
    def _analyze_utilization_trend(self, historical_data: Dict[str, Any]) -> str:
        """Analyze utilization trend from historical data"""
        try:
            cpu_data = historical_data.get('cpu', [])
            memory_data = historical_data.get('memory', [])
            
            if len(cpu_data) < 2 or len(memory_data) < 2:
                return "stable"
            
            # Calculate average utilization
            recent_cpu = sum(cpu_data[-3:]) / min(3, len(cpu_data))
            older_cpu = sum(cpu_data[:-3]) / max(1, len(cpu_data) - 3)
            
            recent_memory = sum(memory_data[-3:]) / min(3, len(memory_data))
            older_memory = sum(memory_data[:-3]) / max(1, len(memory_data) - 3)
            
            recent_avg = (recent_cpu + recent_memory) / 2
            older_avg = (older_cpu + older_memory) / 2
            
            if recent_avg > older_avg * 1.05:
                return "improving"
            elif recent_avg < older_avg * 0.95:
                return "declining"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error analyzing utilization trend: {e}")
            return "stable"
    
    def _generate_forecast(self, historical_data: Dict[str, Any], time_range: str) -> Dict[str, Any]:
        """Generate forecast based on historical data"""
        try:
            # Simple linear regression for forecasting
            costs = historical_data.get('cost', [])
            if len(costs) < 3:
                return {
                    "next_month_cost": 0.0,
                    "next_month_savings": 0.0,
                    "performance_prediction": 0.5
                }
            
            # Calculate trend
            n = len(costs)
            x = list(range(n))
            y = costs
            
            # Simple linear regression
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            intercept = (sum_y - slope * sum_x) / n
            
            # Forecast next month
            next_month_cost = slope * (n + 30) + intercept
            current_cost = slope * n + intercept
            
            next_month_savings = max(0, current_cost - next_month_cost)
            
            return {
                "next_month_cost": max(0, next_month_cost),
                "next_month_savings": next_month_savings,
                "performance_prediction": 0.75  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return {
                "next_month_cost": 0.0,
                "next_month_savings": 0.0,
                "performance_prediction": 0.5
            }
    
    async def _get_business_alerts(
        self, 
        cluster_id: str, 
        business_impact: BusinessImpact
    ) -> List[str]:
        """Get business alerts"""
        alerts = []
        
        if business_impact.cost_savings > 2000:
            alerts.append("High cost savings opportunity detected")
        
        if business_impact.risk_assessment > 0.7:
            alerts.append("High risk environment - review optimization plans")
        
        if business_impact.roi_percentage > 150:
            alerts.append("Excellent ROI opportunity available")
        
        return alerts


class CostCalculator:
    """Calculate cost analysis and savings opportunities"""
    
    async def analyze(
        self, 
        cluster_id: str, 
        metrics: Dict[str, Any], 
        time_range: str
    ) -> Any:
        """Analyze cost optimization opportunities"""
        # Mock cost analysis
        return type('CostAnalysis', (), {
            'current_monthly_cost': 2500.0,
            'potential_savings': 750.0,
            'optimization_opportunities': [
                'Scale down idle pods',
                'Optimize resource requests',
                'Implement HPA'
            ],
            'cost_trend': 'declining'
        })()
    
    async def calculate_roi(
        self, 
        investment: float, 
        savings: float, 
        time_period: str = "12m"
    ) -> float:
        """Calculate ROI for optimization investment"""
        if investment == 0:
            return float('inf')
        return (savings / investment) * 100


class PerformanceAnalyzer:
    """Analyze performance impact and opportunities"""
    
    async def analyze(
        self, 
        cluster_id: str, 
        metrics: Dict[str, Any], 
        time_range: str
    ) -> Any:
        """Analyze performance optimization opportunities"""
        # Mock performance analysis
        return type('PerformanceAnalysis', (), {
            'current_performance': 0.72,
            'performance_gain': 0.13,
            'bottlenecks': [
                'CPU throttling on 3 pods',
                'Memory pressure on 2 nodes',
                'Network latency issues'
            ],
            'optimization_impact': 'high'
        })()
    
    async def identify_bottlenecks(
        self, 
        cluster_id: str, 
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        if metrics.get('cpu_utilization', 0) > 0.8:
            bottlenecks.append("High CPU utilization detected")
        
        if metrics.get('memory_utilization', 0) > 0.85:
            bottlenecks.append("Memory pressure detected")
        
        return bottlenecks


class ROICalculator:
    """Calculate return on investment for optimizations"""
    
    async def calculate(
        self, 
        cluster_id: str, 
        cost_analysis: Any, 
        performance_analysis: Any, 
        time_range: str
    ) -> Any:
        """Calculate ROI for cluster optimization"""
        # Mock ROI calculation
        return type('ROIAnalysis', (), {
            'roi_percentage': 125.0,
            'payback_period': '6 months',
            'net_present_value': 4500.0,
            'confidence_level': 0.85
        })()
    
    async def calculate_npv(
        self, 
        cash_flows: List[float], 
        discount_rate: float = 0.1
    ) -> float:
        """Calculate Net Present Value"""
        npv = 0
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** (i + 1))
        return npv


class BusinessRiskAssessor:
    """Assess business risks of optimization"""
    
    async def assess(
        self, 
        cluster_id: str, 
        metrics: Dict[str, Any], 
        cost_analysis: Any
    ) -> Any:
        """Assess business risks"""
        # Mock risk assessment
        return type('RiskAssessment', (), {
            'overall_risk': 0.25,
            'technical_risk': 0.15,
            'business_risk': 0.30,
            'financial_risk': 0.20,
            'mitigation_strategies': [
                'Implement gradual rollout',
                'Monitor closely for 48 hours',
                'Have rollback plan ready'
            ]
        })()
    
    async def calculate_risk_score(
        self, 
        technical_factors: Dict[str, float], 
        business_factors: Dict[str, float]
    ) -> float:
        """Calculate overall risk score"""
        technical_risk = sum(technical_factors.values()) / len(technical_factors)
        business_risk = sum(business_factors.values()) / len(business_factors)
        
        return (technical_risk + business_risk) / 2 