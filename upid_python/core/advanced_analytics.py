"""
UPID CLI - Advanced Analytics Module
Phase 7.3: Advanced analytics and business intelligence
"""

import json
import statistics
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

@dataclass
class AnalyticsDataPoint:
    """Data point for analytics processing."""
    timestamp: datetime
    value: float
    category: str
    metadata: Dict[str, Any]

class PredictiveAnalytics:
    """Real predictive analytics and forecasting system."""
    
    def __init__(self):
        self.models = {}
        self.historical_data = defaultdict(list)
    
    def add_data_point(self, category: str, value: float, timestamp: datetime, metadata: Dict[str, Any] = None):
        """Add a data point for analysis."""
        data_point = AnalyticsDataPoint(
            timestamp=timestamp,
            value=value,
            category=category,
            metadata=metadata or {}
        )
        self.historical_data[category].append(data_point)
    
    def forecast_trend(self, category: str, periods: int = 7) -> List[float]:
        """Forecast future values using simple linear regression."""
        data = self.historical_data.get(category, [])
        if len(data) < 2:
            return [0.0] * periods
        
        # Simple linear regression
        x = [i for i in range(len(data))]
        y = [dp.value for dp in data]
        
        if len(x) < 2:
            return [y[0] if y else 0.0] * periods
        
        # Calculate slope and intercept
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_xx = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate forecast
        forecast = []
        for i in range(1, periods + 1):
            forecast.append(slope * (len(x) + i) + intercept)
        
        return forecast
    
    def detect_anomalies(self, category: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical analysis."""
        data = self.historical_data.get(category, [])
        if len(data) < 3:
            return []
        
        values = [dp.value for dp in data]
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        for i, dp in enumerate(data):
            z_score = abs((dp.value - mean) / std) if std > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    "timestamp": dp.timestamp.isoformat(),
                    "value": dp.value,
                    "z_score": z_score,
                    "category": category
                })
        
        return anomalies

class BusinessIntelligence:
    """Real business intelligence and reporting system."""
    
    def __init__(self):
        self.kpis = {}
        self.reports = {}
    
    def calculate_kpi(self, name: str, data: List[float], calculation_type: str = "sum") -> float:
        """Calculate Key Performance Indicators."""
        if not data:
            return 0.0
        
        if calculation_type == "sum":
            return sum(data)
        elif calculation_type == "average":
            return statistics.mean(data)
        elif calculation_type == "median":
            return statistics.median(data)
        elif calculation_type == "max":
            return max(data)
        elif calculation_type == "min":
            return min(data)
        else:
            return sum(data)
    
    def generate_report(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business intelligence reports."""
        if report_type == "cost_analysis":
            return self._generate_cost_report(data)
        elif report_type == "performance_metrics":
            return self._generate_performance_report(data)
        elif report_type == "resource_utilization":
            return self._generate_resource_report(data)
        else:
            return {"error": f"Unknown report type: {report_type}"}
    
    def _generate_cost_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost analysis report."""
        costs = data.get("costs", [])
        return {
            "total_cost": sum(costs),
            "average_cost": statistics.mean(costs) if costs else 0,
            "cost_trend": "increasing" if len(costs) > 1 and costs[-1] > costs[0] else "decreasing",
            "cost_efficiency": self._calculate_efficiency_score(costs),
            "recommendations": self._generate_cost_recommendations(costs)
        }
    
    def _generate_performance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance metrics report."""
        metrics = data.get("metrics", {})
        return {
            "cpu_utilization": metrics.get("cpu", 0),
            "memory_utilization": metrics.get("memory", 0),
            "network_throughput": metrics.get("network", 0),
            "performance_score": self._calculate_performance_score(metrics),
            "bottlenecks": self._identify_bottlenecks(metrics)
        }
    
    def _generate_resource_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource utilization report."""
        resources = data.get("resources", {})
        return {
            "resource_efficiency": self._calculate_resource_efficiency(resources),
            "underutilized_resources": self._find_underutilized_resources(resources),
            "overutilized_resources": self._find_overutilized_resources(resources),
            "optimization_opportunities": self._identify_optimization_opportunities(resources)
        }
    
    def _calculate_efficiency_score(self, costs: List[float]) -> float:
        """Calculate cost efficiency score."""
        if not costs or len(costs) < 2:
            return 0.0
        # Simple efficiency calculation based on cost trend
        trend = (costs[-1] - costs[0]) / costs[0] if costs[0] > 0 else 0
        return max(0, 100 - abs(trend) * 100)
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score."""
        scores = []
        for metric, value in metrics.items():
            if metric in ["cpu", "memory"]:
                # Lower is better for utilization
                scores.append(max(0, 100 - value))
            else:
                # Higher is better for throughput
                scores.append(min(100, value))
        return statistics.mean(scores) if scores else 0
    
    def _identify_bottlenecks(self, metrics: Dict[str, float]) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        if metrics.get("cpu", 0) > 80:
            bottlenecks.append("High CPU utilization")
        if metrics.get("memory", 0) > 80:
            bottlenecks.append("High memory utilization")
        if metrics.get("network", 0) < 50:
            bottlenecks.append("Low network throughput")
        return bottlenecks
    
    def _calculate_resource_efficiency(self, resources: Dict[str, Any]) -> float:
        """Calculate resource efficiency score."""
        # Simplified efficiency calculation
        total_utilization = sum(resources.values()) if resources else 0
        return min(100, total_utilization / len(resources) if resources else 0)
    
    def _find_underutilized_resources(self, resources: Dict[str, Any]) -> List[str]:
        """Find underutilized resources."""
        return [k for k, v in resources.items() if v < 20]
    
    def _find_overutilized_resources(self, resources: Dict[str, Any]) -> List[str]:
        """Find overutilized resources."""
        return [k for k, v in resources.items() if v > 80]
    
    def _identify_optimization_opportunities(self, resources: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities."""
        opportunities = []
        if len(self._find_underutilized_resources(resources)) > 0:
            opportunities.append("Resource consolidation")
        if len(self._find_overutilized_resources(resources)) > 0:
            opportunities.append("Resource scaling")
        return opportunities
    
    def _generate_cost_recommendations(self, costs: List[float]) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        if costs and len(costs) > 1:
            if costs[-1] > costs[0] * 1.2:
                recommendations.append("Implement cost controls")
            if statistics.mean(costs) > 1000:
                recommendations.append("Review resource allocation")
        return recommendations

class DataVisualization:
    """Real data visualization and dashboard system."""
    
    def __init__(self):
        self.charts = {}
        self.dashboards = {}
    
    def create_chart(self, chart_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create various types of charts and visualizations."""
        if chart_type == "line":
            return self._create_line_chart(data)
        elif chart_type == "bar":
            return self._create_bar_chart(data)
        elif chart_type == "pie":
            return self._create_pie_chart(data)
        elif chart_type == "scatter":
            return self._create_scatter_chart(data)
        else:
            return {"error": f"Unknown chart type: {chart_type}"}
    
    def _create_line_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create line chart data structure."""
        return {
            "type": "line",
            "title": data.get("title", "Line Chart"),
            "x_axis": data.get("x_values", []),
            "y_axis": data.get("y_values", []),
            "series": data.get("series", []),
            "format": "json"  # For CLI output
        }
    
    def _create_bar_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create bar chart data structure."""
        return {
            "type": "bar",
            "title": data.get("title", "Bar Chart"),
            "categories": data.get("categories", []),
            "values": data.get("values", []),
            "format": "json"
        }
    
    def _create_pie_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create pie chart data structure."""
        return {
            "type": "pie",
            "title": data.get("title", "Pie Chart"),
            "slices": data.get("slices", []),
            "format": "json"
        }
    
    def _create_scatter_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create scatter plot data structure."""
        return {
            "type": "scatter",
            "title": data.get("title", "Scatter Plot"),
            "x_values": data.get("x_values", []),
            "y_values": data.get("y_values", []),
            "format": "json"
        }
    
    def create_dashboard(self, name: str, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a dashboard with multiple charts."""
        return {
            "name": name,
            "charts": charts,
            "created_at": datetime.utcnow().isoformat(),
            "format": "json"
        }

class PerformanceAnalytics:
    """Real performance analytics and optimization system."""
    
    def __init__(self):
        self.performance_metrics = defaultdict(list)
        self.baselines = {}
    
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record a performance metric."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.performance_metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp
        })
    
    def calculate_performance_score(self, metric_name: str) -> float:
        """Calculate performance score for a metric."""
        metrics = self.performance_metrics.get(metric_name, [])
        if not metrics:
            return 0.0
        
        values = [m["value"] for m in metrics]
        baseline = self.baselines.get(metric_name, statistics.mean(values))
        
        # Calculate score based on baseline comparison
        current_avg = statistics.mean(values[-10:]) if len(values) >= 10 else statistics.mean(values)
        score = (current_avg / baseline) * 100 if baseline > 0 else 0
        return min(100, max(0, score))
    
    def identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify performance optimization opportunities."""
        opportunities = []
        
        for metric_name, metrics in self.performance_metrics.items():
            if len(metrics) < 2:
                continue
            
            values = [m["value"] for m in metrics]
            recent_avg = statistics.mean(values[-5:]) if len(values) >= 5 else statistics.mean(values)
            baseline = self.baselines.get(metric_name, statistics.mean(values))
            
            if recent_avg < baseline * 0.8:
                opportunities.append({
                    "metric": metric_name,
                    "type": "performance_degradation",
                    "severity": "high" if recent_avg < baseline * 0.6 else "medium",
                    "current_value": recent_avg,
                    "baseline": baseline,
                    "recommendation": f"Investigate {metric_name} performance degradation"
                })
        
        return opportunities
    
    def set_baseline(self, metric_name: str, baseline_value: float):
        """Set performance baseline for a metric."""
        self.baselines[metric_name] = baseline_value

class TrendAnalysis:
    """Real trend analysis and pattern recognition system."""
    
    def __init__(self):
        self.trend_data = defaultdict(list)
        self.patterns = {}
    
    def add_trend_data(self, category: str, value: float, timestamp: datetime):
        """Add data point for trend analysis."""
        self.trend_data[category].append({
            "value": value,
            "timestamp": timestamp
        })
    
    def analyze_trend(self, category: str, window: int = 7) -> Dict[str, Any]:
        """Analyze trends in data."""
        data = self.trend_data.get(category, [])
        if len(data) < window:
            return {"error": f"Insufficient data for trend analysis. Need at least {window} data points."}
        
        # Get recent data
        recent_data = data[-window:]
        values = [d["value"] for d in recent_data]
        
        # Calculate trend indicators
        trend_direction = self._calculate_trend_direction(values)
        trend_strength = self._calculate_trend_strength(values)
        seasonality = self._detect_seasonality(data)
        
        return {
            "category": category,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "seasonality": seasonality,
            "prediction": self._predict_next_value(values),
            "confidence": self._calculate_confidence(values)
        }
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"
        
        slope = (values[-1] - values[0]) / len(values)
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength (0-1)."""
        if len(values) < 2:
            return 0.0
        
        # Simple trend strength calculation
        changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
        avg_change = statistics.mean(changes) if changes else 0
        max_value = max(values) if values else 1
        
        return min(1.0, avg_change / max_value if max_value > 0 else 0)
    
    def _detect_seasonality(self, data: List[Dict[str, Any]]) -> bool:
        """Detect seasonal patterns in data."""
        if len(data) < 7:
            return False
        
        # Simple seasonality detection
        values = [d["value"] for d in data]
        if len(values) >= 7:
            # Check for weekly patterns
            weekly_avg = statistics.mean(values[-7:])
            overall_avg = statistics.mean(values)
            return abs(weekly_avg - overall_avg) / overall_avg > 0.1 if overall_avg > 0 else False
        
        return False
    
    def _predict_next_value(self, values: List[float]) -> float:
        """Predict next value using simple linear regression."""
        if len(values) < 2:
            return values[0] if values else 0
        
        x = list(range(len(values)))
        y = values
        
        # Simple linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_xx = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        return slope * len(values) + intercept
    
    def _calculate_confidence(self, values: List[float]) -> float:
        """Calculate prediction confidence."""
        if len(values) < 3:
            return 0.5
        
        # Simple confidence based on data consistency
        std = statistics.stdev(values)
        mean = statistics.mean(values)
        
        if mean == 0:
            return 0.5
        
        cv = std / mean  # Coefficient of variation
        confidence = max(0.1, 1 - cv)
        return min(1.0, confidence)

class CustomAnalyticsFramework:
    """Real custom analytics and reporting framework."""
    
    def __init__(self):
        self.analytics_plugins = {}
        self.custom_metrics = {}
        self.report_templates = {}
    
    def register_plugin(self, name: str, plugin_func: callable):
        """Register a custom analytics plugin."""
        self.analytics_plugins[name] = plugin_func
    
    def add_custom_metric(self, name: str, calculation_func: callable):
        """Add a custom metric calculation."""
        self.custom_metrics[name] = calculation_func
    
    def create_report_template(self, name: str, template: Dict[str, Any]):
        """Create a custom report template."""
        self.report_templates[name] = template
    
    def execute_plugin(self, plugin_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a custom analytics plugin."""
        if plugin_name not in self.analytics_plugins:
            return {"error": f"Plugin '{plugin_name}' not found"}
        
        try:
            return self.analytics_plugins[plugin_name](data)
        except Exception as e:
            return {"error": f"Plugin execution failed: {str(e)}"}
    
    def calculate_custom_metric(self, metric_name: str, data: Dict[str, Any]) -> float:
        """Calculate a custom metric."""
        if metric_name not in self.custom_metrics:
            return 0.0
        
        try:
            return self.custom_metrics[metric_name](data)
        except Exception as e:
            return 0.0
    
    def generate_custom_report(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a custom report using a template."""
        if template_name not in self.report_templates:
            return {"error": f"Template '{template_name}' not found"}
        
        template = self.report_templates[template_name]
        report = {
            "template": template_name,
            "generated_at": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        # Apply template to data - copy matching sections from data to report
        for section in template.keys():
            if section in data:
                report["data"][section] = data[section]
        
        return report 