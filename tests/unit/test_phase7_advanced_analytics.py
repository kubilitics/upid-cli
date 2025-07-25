"""
Unit tests for Phase 7.3 Advanced Analytics
"""

import pytest
from datetime import datetime, timedelta
from upid_python.core.advanced_analytics import (
    PredictiveAnalytics, BusinessIntelligence, DataVisualization,
    PerformanceAnalytics, TrendAnalysis, CustomAnalyticsFramework
)

def test_predictive_analytics():
    pa = PredictiveAnalytics()
    
    # Add test data
    for i in range(10):
        pa.add_data_point("cpu_usage", 50 + i, datetime.utcnow() + timedelta(hours=i))
    
    # Test forecasting
    forecast = pa.forecast_trend("cpu_usage", 5)
    assert len(forecast) == 5
    assert all(isinstance(f, float) for f in forecast)
    
    # Test anomaly detection
    pa.add_data_point("cpu_usage", 200, datetime.utcnow())  # Anomaly
    anomalies = pa.detect_anomalies("cpu_usage")
    assert len(anomalies) > 0
    assert any(a["value"] == 200 for a in anomalies)

def test_business_intelligence():
    bi = BusinessIntelligence()
    
    # Test KPI calculation
    data = [100, 200, 300, 400, 500]
    assert bi.calculate_kpi("total_cost", data, "sum") == 1500
    assert bi.calculate_kpi("avg_cost", data, "average") == 300
    
    # Test cost analysis report
    cost_data = {"costs": [100, 200, 300, 400, 500]}
    cost_report = bi.generate_report("cost_analysis", cost_data)
    assert cost_report["total_cost"] == 1500
    assert "cost_trend" in cost_report
    assert "recommendations" in cost_report
    
    # Test performance report
    perf_data = {"metrics": {"cpu": 75, "memory": 60, "network": 80}}
    perf_report = bi.generate_report("performance_metrics", perf_data)
    assert "cpu_utilization" in perf_report
    assert "performance_score" in perf_report
    assert "bottlenecks" in perf_report

def test_data_visualization():
    dv = DataVisualization()
    
    # Test line chart
    line_data = {
        "title": "CPU Usage Over Time",
        "x_values": [1, 2, 3, 4, 5],
        "y_values": [50, 60, 70, 80, 90]
    }
    line_chart = dv.create_chart("line", line_data)
    assert line_chart["type"] == "line"
    assert line_chart["title"] == "CPU Usage Over Time"
    
    # Test bar chart
    bar_data = {
        "title": "Resource Usage",
        "categories": ["CPU", "Memory", "Network"],
        "values": [75, 60, 80]
    }
    bar_chart = dv.create_chart("bar", bar_data)
    assert bar_chart["type"] == "bar"
    assert len(bar_chart["categories"]) == 3
    
    # Test dashboard creation
    dashboard = dv.create_dashboard("Test Dashboard", [line_chart, bar_chart])
    assert dashboard["name"] == "Test Dashboard"
    assert len(dashboard["charts"]) == 2

def test_performance_analytics():
    pa = PerformanceAnalytics()
    
    # Record metrics
    for i in range(10):
        pa.record_metric("cpu_usage", 50 + i)
    
    # Set baseline
    pa.set_baseline("cpu_usage", 55)
    
    # Test performance score
    score = pa.calculate_performance_score("cpu_usage")
    assert 0 <= score <= 100
    
    # Test optimization opportunities
    opportunities = pa.identify_optimization_opportunities()
    assert isinstance(opportunities, list)

def test_trend_analysis():
    ta = TrendAnalysis()
    
    # Add trend data
    for i in range(10):
        ta.add_trend_data("cost", 100 + i * 10, datetime.utcnow() + timedelta(days=i))
    
    # Test trend analysis
    analysis = ta.analyze_trend("cost", 7)
    assert "trend_direction" in analysis
    assert "trend_strength" in analysis
    assert "seasonality" in analysis
    assert "prediction" in analysis
    assert "confidence" in analysis
    
    # Test with insufficient data
    insufficient_analysis = ta.analyze_trend("nonexistent", 7)
    assert "error" in insufficient_analysis

def test_custom_analytics_framework():
    caf = CustomAnalyticsFramework()
    
    # Test plugin registration and execution
    def test_plugin(data):
        return {"result": sum(data.get("values", []))}
    
    caf.register_plugin("sum_calculator", test_plugin)
    result = caf.execute_plugin("sum_calculator", {"values": [1, 2, 3, 4, 5]})
    assert result["result"] == 15
    
    # Test custom metric
    def custom_metric(data):
        return len(data.get("items", []))
    
    caf.add_custom_metric("item_count", custom_metric)
    count = caf.calculate_custom_metric("item_count", {"items": [1, 2, 3]})
    assert count == 3
    
    # Test report template
    template = {
        "cost_summary": "cost_summary",
        "cost_details": "cost_details"
    }
    caf.create_report_template("cost_report", template)
    
    report = caf.generate_custom_report("cost_report", {
        "cost_summary": "Total: $1000",
        "cost_details": "Breakdown..."
    })
    assert report["template"] == "cost_report"
    assert "cost_summary" in report["data"]
    
    # Test error handling
    error_result = caf.execute_plugin("nonexistent", {})
    assert "error" in error_result
    
    error_metric = caf.calculate_custom_metric("nonexistent", {})
    assert error_metric == 0.0

def test_integration_scenario():
    """Test integration between multiple analytics components."""
    pa = PredictiveAnalytics()
    bi = BusinessIntelligence()
    dv = DataVisualization()
    
    # Simulate a complete analytics workflow
    # 1. Add historical data
    for i in range(30):
        pa.add_data_point("monthly_cost", 1000 + i * 50, datetime.utcnow() - timedelta(days=30-i))
    
    # 2. Generate forecast
    forecast = pa.forecast_trend("monthly_cost", 3)
    assert len(forecast) == 3
    
    # 3. Create business intelligence report
    cost_data = {"costs": [1000, 1100, 1200, 1300, 1400]}
    report = bi.generate_report("cost_analysis", cost_data)
    assert report["total_cost"] == 6000
    
    # 4. Create visualization
    chart_data = {
        "title": "Cost Forecast",
        "x_values": ["Jan", "Feb", "Mar"],
        "y_values": forecast
    }
    chart = dv.create_chart("line", chart_data)
    assert chart["type"] == "line"
    
    # 5. Create dashboard
    dashboard = dv.create_dashboard("Cost Analytics", [chart])
    assert dashboard["name"] == "Cost Analytics"
    assert len(dashboard["charts"]) == 1 