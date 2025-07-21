"""
Unit tests for Phase 2: Business Intelligence & Executive Dashboard
Tests business intelligence engine and executive dashboard functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the modules to test
from upid.core.business_intelligence import (
    BusinessIntelligenceEngine,
    BusinessMetricType,
    BusinessKPI,
    BusinessImpact,
    CostCalculator,
    PerformanceAnalyzer,
    ROICalculator,
    BusinessRiskAssessor
)

from upid.core.executive_dashboard import (
    ExecutiveDashboard,
    DashboardWidget,
    DashboardWidgetType,
    ExecutiveReport,
    DashboardRenderer
)


class TestBusinessIntelligenceEngine:
    """Test business intelligence engine functionality"""
    
    @pytest.fixture
    def business_intelligence(self):
        """Create business intelligence engine instance"""
        return BusinessIntelligenceEngine()
    
    @pytest.mark.asyncio
    async def test_analyze_business_impact(self, business_intelligence):
        """Test business impact analysis"""
        # Mock dependencies
        business_intelligence.cost_calculator.analyze = AsyncMock(return_value=Mock(
            current_monthly_cost=2500.0,
            potential_savings=750.0
        ))
        business_intelligence.performance_analyzer.analyze = AsyncMock(return_value=Mock(
            current_performance=0.72,
            performance_gain=0.13
        ))
        business_intelligence.roi_calculator.calculate = AsyncMock(return_value=Mock(
            roi_percentage=125.0,
            payback_period="6 months",
            net_present_value=4500.0,
            confidence_level=0.85
        ))
        business_intelligence.risk_assessor.assess = AsyncMock(return_value=Mock(
            overall_risk=0.25,
            technical_risk=0.15,
            business_risk=0.30,
            financial_risk=0.20
        ))
        
        # Test business impact analysis
        result = await business_intelligence.analyze_business_impact(
            cluster_id="test-cluster",
            time_range="30d",
            include_forecast=True
        )
        
        # Verify result
        assert isinstance(result, BusinessImpact)
        assert result.roi_percentage == 125.0
        assert result.cost_savings == 750.0
        assert result.performance_gain == 0.13
        assert result.risk_assessment == 0.25
        assert len(result.recommendations) > 0
        assert len(result.executive_summary) > 0
    
    @pytest.mark.asyncio
    async def test_get_executive_dashboard(self, business_intelligence):
        """Test executive dashboard generation"""
        # Mock analyze_business_impact
        business_intelligence.analyze_business_impact = AsyncMock(return_value=Mock(
            roi_percentage=125.0,
            cost_savings=750.0,
            performance_gain=0.13,
            risk_assessment=0.25,
            recommendations=["Test recommendation"],
            executive_summary="Test summary"
        ))
        
        # Test dashboard generation
        result = await business_intelligence.get_executive_dashboard(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify result structure
        assert isinstance(result, dict)
        assert result["cluster_id"] == "test-cluster"
        assert result["time_range"] == "30d"
        assert "business_impact" in result
        assert "kpis" in result
        assert "trends" in result
        assert "alerts" in result
        assert "last_updated" in result
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, business_intelligence):
        """Test recommendation generation"""
        # Mock analysis results
        cost_analysis = Mock(potential_savings=1500.0)
        performance_analysis = Mock(performance_gain=0.15)
        risk_assessment = Mock(overall_risk=0.2)
        
        # Test recommendation generation
        recommendations = await business_intelligence._generate_recommendations(
            cost_analysis, performance_analysis, risk_assessment
        )
        
        # Verify recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Check for savings recommendation (should be present for high savings)
        assert any("savings" in rec.lower() or "save" in rec.lower() for rec in recommendations)
        # Check for performance recommendation (should be present for high performance gain)
        assert any("performance" in rec.lower() or "improved" in rec.lower() for rec in recommendations)
        # Check for risk recommendation (should be present for low risk)
        assert any("risk" in rec.lower() or "safe" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_create_executive_summary(self, business_intelligence):
        """Test executive summary creation"""
        # Mock analysis results
        cost_analysis = Mock(potential_savings=1000.0)
        performance_analysis = Mock(performance_gain=0.12)
        roi_analysis = Mock(roi_percentage=120.0)
        risk_assessment = Mock(overall_risk=0.25)
        
        # Test summary creation
        summary = await business_intelligence._create_executive_summary(
            cost_analysis, performance_analysis, roi_analysis, risk_assessment
        )
        
        # Verify summary
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Cost Impact" in summary
        assert "Performance" in summary
        assert "ROI" in summary
        assert "Risk Level" in summary
        assert "Recommendation" in summary
    
    @pytest.mark.asyncio
    async def test_calculate_kpis(self, business_intelligence):
        """Test KPI calculation"""
        # Test KPI calculation
        kpis = await business_intelligence._calculate_kpis(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify KPIs
        assert isinstance(kpis, list)
        assert len(kpis) > 0
        
        for kpi in kpis:
            assert isinstance(kpi, BusinessKPI)
            assert kpi.metric_type in BusinessMetricType
            assert 0 <= kpi.confidence <= 1
            assert 0 <= kpi.impact_score <= 1
            assert kpi.trend in ["improving", "declining", "stable"]
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self, business_intelligence):
        """Test trend analysis"""
        # Test trend analysis
        trends = await business_intelligence._analyze_trends(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify trends
        assert isinstance(trends, dict)
        assert "cost_trend" in trends
        assert "performance_trend" in trends
        assert "utilization_trend" in trends
        assert "forecast" in trends
        
        # Verify trend values
        for trend in trends.values():
            if isinstance(trend, str):
                assert trend in ["improving", "declining", "stable"]
    
    @pytest.mark.asyncio
    async def test_get_business_alerts(self, business_intelligence):
        """Test business alert generation"""
        # Mock business impact
        business_impact = Mock(
            cost_savings=2500.0,
            risk_assessment=0.8,
            roi_percentage=200.0
        )
        
        # Test alert generation
        alerts = await business_intelligence._get_business_alerts(
            cluster_id="test-cluster",
            business_impact=business_impact
        )
        
        # Verify alerts
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        assert any("cost savings" in alert.lower() for alert in alerts)
        assert any("risk" in alert.lower() for alert in alerts)
        assert any("roi" in alert.lower() for alert in alerts)


class TestCostCalculator:
    """Test cost calculator functionality"""
    
    @pytest.fixture
    def cost_calculator(self):
        """Create cost calculator instance"""
        return CostCalculator()
    
    @pytest.mark.asyncio
    async def test_analyze_cost(self, cost_calculator):
        """Test cost analysis"""
        # Mock metrics
        metrics = {
            "cpu_utilization": 0.65,
            "memory_utilization": 0.72,
            "cost_per_hour": 2.45
        }
        
        # Test cost analysis
        result = await cost_calculator.analyze(
            cluster_id="test-cluster",
            metrics=metrics,
            time_range="30d"
        )
        
        # Verify result
        assert hasattr(result, 'current_monthly_cost')
        assert hasattr(result, 'potential_savings')
        assert hasattr(result, 'optimization_opportunities')
        assert hasattr(result, 'cost_trend')
        assert result.current_monthly_cost > 0
        assert result.potential_savings >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_roi(self, cost_calculator):
        """Test ROI calculation"""
        # Test ROI calculation
        roi = await cost_calculator.calculate_roi(
            investment=1000.0,
            savings=2000.0,
            time_period="12m"
        )
        
        # Verify ROI
        assert roi == 200.0  # (2000/1000) * 100
        
        # Test zero investment
        roi_zero = await cost_calculator.calculate_roi(
            investment=0.0,
            savings=1000.0
        )
        assert roi_zero == float('inf')


class TestPerformanceAnalyzer:
    """Test performance analyzer functionality"""
    
    @pytest.fixture
    def performance_analyzer(self):
        """Create performance analyzer instance"""
        return PerformanceAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_performance(self, performance_analyzer):
        """Test performance analysis"""
        # Mock metrics
        metrics = {
            "cpu_utilization": 0.65,
            "memory_utilization": 0.72,
            "network_io": 1024.5
        }
        
        # Test performance analysis
        result = await performance_analyzer.analyze(
            cluster_id="test-cluster",
            metrics=metrics,
            time_range="30d"
        )
        
        # Verify result
        assert hasattr(result, 'current_performance')
        assert hasattr(result, 'performance_gain')
        assert hasattr(result, 'bottlenecks')
        assert hasattr(result, 'optimization_impact')
        assert 0 <= result.current_performance <= 1
        assert result.performance_gain >= 0
    
    @pytest.mark.asyncio
    async def test_identify_bottlenecks(self, performance_analyzer):
        """Test bottleneck identification"""
        # Test with high CPU utilization
        metrics_high_cpu = {"cpu_utilization": 0.85}
        bottlenecks = await performance_analyzer.identify_bottlenecks(
            cluster_id="test-cluster",
            metrics=metrics_high_cpu
        )
        
        assert isinstance(bottlenecks, list)
        assert len(bottlenecks) > 0
        assert any("CPU" in bottleneck for bottleneck in bottlenecks)
        
        # Test with high memory utilization
        metrics_high_memory = {"memory_utilization": 0.9}
        bottlenecks = await performance_analyzer.identify_bottlenecks(
            cluster_id="test-cluster",
            metrics=metrics_high_memory
        )
        
        assert isinstance(bottlenecks, list)
        assert len(bottlenecks) > 0
        assert any("Memory" in bottleneck for bottleneck in bottlenecks)


class TestROICalculator:
    """Test ROI calculator functionality"""
    
    @pytest.fixture
    def roi_calculator(self):
        """Create ROI calculator instance"""
        return ROICalculator()
    
    @pytest.mark.asyncio
    async def test_calculate_roi(self, roi_calculator):
        """Test ROI calculation"""
        # Mock analysis results
        cost_analysis = Mock(potential_savings=1000.0)
        performance_analysis = Mock(performance_gain=0.1)
        
        # Test ROI calculation
        result = await roi_calculator.calculate(
            cluster_id="test-cluster",
            cost_analysis=cost_analysis,
            performance_analysis=performance_analysis,
            time_range="30d"
        )
        
        # Verify result
        assert hasattr(result, 'roi_percentage')
        assert hasattr(result, 'payback_period')
        assert hasattr(result, 'net_present_value')
        assert hasattr(result, 'confidence_level')
        assert result.roi_percentage > 0
        assert result.confidence_level > 0
    
    @pytest.mark.asyncio
    async def test_calculate_npv(self, roi_calculator):
        """Test NPV calculation"""
        # Test NPV calculation
        cash_flows = [1000.0, 1200.0, 1400.0]
        npv = await roi_calculator.calculate_npv(
            cash_flows=cash_flows,
            discount_rate=0.1
        )
        
        # Verify NPV
        assert isinstance(npv, float)
        assert npv > 0  # Positive NPV for positive cash flows


class TestBusinessRiskAssessor:
    """Test business risk assessor functionality"""
    
    @pytest.fixture
    def risk_assessor(self):
        """Create risk assessor instance"""
        return BusinessRiskAssessor()
    
    @pytest.mark.asyncio
    async def test_assess_risk(self, risk_assessor):
        """Test risk assessment"""
        # Mock data
        metrics = {"cpu_utilization": 0.65}
        cost_analysis = Mock(potential_savings=1000.0)
        
        # Test risk assessment
        result = await risk_assessor.assess(
            cluster_id="test-cluster",
            metrics=metrics,
            cost_analysis=cost_analysis
        )
        
        # Verify result
        assert hasattr(result, 'overall_risk')
        assert hasattr(result, 'technical_risk')
        assert hasattr(result, 'business_risk')
        assert hasattr(result, 'financial_risk')
        assert hasattr(result, 'mitigation_strategies')
        assert 0 <= result.overall_risk <= 1
        assert len(result.mitigation_strategies) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_risk_score(self, risk_assessor):
        """Test risk score calculation"""
        # Test risk score calculation
        technical_factors = {"cpu_risk": 0.3, "memory_risk": 0.2}
        business_factors = {"cost_risk": 0.4, "performance_risk": 0.1}
        
        risk_score = await risk_assessor.calculate_risk_score(
            technical_factors=technical_factors,
            business_factors=business_factors
        )
        
        # Verify risk score
        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1
        # Expected: (0.25 + 0.25) / 2 = 0.25
        assert abs(risk_score - 0.25) < 0.01


class TestExecutiveDashboard:
    """Test executive dashboard functionality"""
    
    @pytest.fixture
    def executive_dashboard(self):
        """Create executive dashboard instance"""
        dashboard = ExecutiveDashboard()
        dashboard.business_intelligence = Mock()
        dashboard.metrics_collector = Mock()
        return dashboard
    
    @pytest.mark.asyncio
    async def test_generate_executive_report(self, executive_dashboard):
        """Test executive report generation"""
        # Mock business intelligence
        executive_dashboard.business_intelligence.analyze_business_impact = AsyncMock(return_value=Mock(
            roi_percentage=125.0,
            cost_savings=750.0,
            performance_gain=0.13,
            risk_assessment=0.25,
            recommendations=["Test recommendation"],
            executive_summary="Test summary"
        ))
        
        # Test report generation
        result = await executive_dashboard.generate_executive_report(
            cluster_id="test-cluster",
            time_range="30d",
            include_forecast=True
        )
        
        # Verify result
        assert isinstance(result, ExecutiveReport)
        assert result.cluster_id == "test-cluster"
        assert result.time_range == "30d"
        assert len(result.summary) > 0
        assert len(result.key_metrics) > 0
        assert len(result.trends) > 0
        assert len(result.alerts) >= 0
        assert len(result.recommendations) > 0
        assert "roi_percentage" in result.roi_analysis
        assert "overall_risk" in result.risk_assessment
    
    @pytest.mark.asyncio
    async def test_create_dashboard_widgets(self, executive_dashboard):
        """Test dashboard widget creation"""
        # Test widget creation
        widgets = await executive_dashboard.create_dashboard_widgets(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify widgets
        assert isinstance(widgets, list)
        assert len(widgets) > 0
        
        for widget in widgets:
            assert isinstance(widget, DashboardWidget)
            assert widget.widget_type in DashboardWidgetType
            assert len(widget.title) > 0
            assert widget.position[0] >= 0
            assert widget.position[1] >= 0
            assert widget.size[0] > 0
            assert widget.size[1] > 0
    
    @pytest.mark.asyncio
    async def test_export_dashboard_data(self, executive_dashboard):
        """Test dashboard data export"""
        # Mock report generation
        executive_dashboard.generate_executive_report = AsyncMock(return_value=Mock(
            summary="Test summary",
            key_metrics={"cpu": 0.65},
            trends={"cost": "declining"},
            alerts=["Test alert"],
            recommendations=["Test recommendation"],
            roi_analysis={"roi": 125.0},
            risk_assessment={"risk": 0.25}
        ))
        
        # Mock widget creation
        executive_dashboard.create_dashboard_widgets = AsyncMock(return_value=[
            DashboardWidget(
                widget_type=DashboardWidgetType.METRIC_CARD,
                title="Test Widget",
                data={"test": "data"},
                position=(0, 0),
                size=(2, 2)
            )
        ])
        
        # Test data export
        result = await executive_dashboard.export_dashboard_data(
            cluster_id="test-cluster",
            time_range="30d",
            format="json"
        )
        
        # Verify result
        assert isinstance(result, dict)
        assert result["cluster_id"] == "test-cluster"
        assert result["time_range"] == "30d"
        assert "export_date" in result
        assert "report" in result
        assert "widgets" in result
    
    @pytest.mark.asyncio
    async def test_get_key_metrics(self, executive_dashboard):
        """Test key metrics retrieval"""
        # Test key metrics
        metrics = await executive_dashboard._get_key_metrics(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify metrics
        assert isinstance(metrics, dict)
        assert "cpu_utilization" in metrics
        assert "memory_utilization" in metrics
        assert "cost_per_hour" in metrics
        assert "pod_count" in metrics
        assert "node_count" in metrics
        assert "availability" in metrics
        assert "response_time" in metrics
        
        # Verify metric values
        for value in metrics.values():
            assert isinstance(value, (int, float))
            assert value >= 0
    
    @pytest.mark.asyncio
    async def test_get_cost_analysis(self, executive_dashboard):
        """Test cost analysis retrieval"""
        # Test cost analysis
        cost_data = await executive_dashboard._get_cost_analysis(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify cost data
        assert isinstance(cost_data, dict)
        assert "current_monthly_cost" in cost_data
        assert "potential_savings" in cost_data
        assert "cost_trend" in cost_data
        assert "cost_breakdown" in cost_data
        assert "optimization_opportunities" in cost_data
        
        # Verify values
        assert cost_data["current_monthly_cost"] > 0
        assert cost_data["potential_savings"] >= 0
        assert cost_data["cost_trend"] in ["declining", "stable", "increasing"]
    
    @pytest.mark.asyncio
    async def test_get_roi_analysis(self, executive_dashboard):
        """Test ROI analysis retrieval"""
        # Test ROI analysis
        roi_data = await executive_dashboard._get_roi_analysis(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify ROI data
        assert isinstance(roi_data, dict)
        assert "roi_percentage" in roi_data
        assert "payback_period" in roi_data
        assert "net_present_value" in roi_data
        assert "confidence_level" in roi_data
        assert "investment_required" in roi_data
        assert "annual_savings" in roi_data
        
        # Verify values
        assert roi_data["roi_percentage"] > 0
        assert roi_data["confidence_level"] > 0
        assert roi_data["confidence_level"] <= 1
    
    @pytest.mark.asyncio
    async def test_get_alerts(self, executive_dashboard):
        """Test alert retrieval"""
        # Test alerts
        alerts = await executive_dashboard._get_alerts(cluster_id="test-cluster")
        
        # Verify alerts
        assert isinstance(alerts, list)
        # Should have some alerts for test cluster
        assert len(alerts) > 0
        
        for alert in alerts:
            assert isinstance(alert, str)
            assert len(alert) > 0
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self, executive_dashboard):
        """Test recommendation retrieval"""
        # Test recommendations
        recommendations = await executive_dashboard._get_recommendations(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self, executive_dashboard):
        """Test trend analysis"""
        # Test trends
        trends = await executive_dashboard._analyze_trends(
            cluster_id="test-cluster",
            time_range="30d"
        )
        
        # Verify trends
        assert isinstance(trends, dict)
        assert "cost_trend" in trends
        assert "performance_trend" in trends
        assert "utilization_trend" in trends
        assert "availability_trend" in trends
        assert "efficiency_trend" in trends
        
        # Verify trend values
        for trend in trends.values():
            if isinstance(trend, str):
                assert trend in ["improving", "declining", "stable"]
    
    @pytest.mark.asyncio
    async def test_create_summary(self, executive_dashboard):
        """Test summary creation"""
        # Mock data
        business_impact = Mock(
            cost_savings=1000.0,
            performance_gain=0.15,
            roi_percentage=120.0,
            risk_assessment=0.25
        )
        key_metrics = {"availability": 0.9995}
        trends = {"cost_trend": "declining", "performance_trend": "improving"}
        
        # Test summary creation
        summary = await executive_dashboard._create_summary(
            cluster_id="test-cluster",
            business_impact=business_impact,
            key_metrics=key_metrics,
            trends=trends
        )
        
        # Verify summary
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "test-cluster" in summary
        assert "Cost Impact" in summary
        assert "Performance" in summary
        assert "ROI" in summary
        assert "Risk Level" in summary
        assert "Recommendation" in summary
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, executive_dashboard):
        """Test recommendation generation"""
        # Mock data
        business_impact = Mock(
            cost_savings=1500.0,
            performance_gain=0.12,
            risk_assessment=0.2
        )
        key_metrics = {"cpu_utilization": 0.4, "memory_utilization": 0.9}
        
        # Test recommendation generation
        recommendations = await executive_dashboard._generate_recommendations(
            cluster_id="test-cluster",
            business_impact=business_impact,
            key_metrics=key_metrics
        )
        
        # Verify recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0


class TestDashboardRenderer:
    """Test dashboard renderer functionality"""
    
    @pytest.mark.asyncio
    async def test_render_console_dashboard(self):
        """Test console dashboard rendering"""
        # Create test widgets
        widgets = [
            DashboardWidget(
                widget_type=DashboardWidgetType.METRIC_CARD,
                title="Test Metrics",
                data={"cpu": 0.65, "memory": 0.72},
                position=(0, 0),
                size=(2, 2)
            ),
            DashboardWidget(
                widget_type=DashboardWidgetType.ALERT_PANEL,
                title="Test Alerts",
                data=["Test alert 1", "Test alert 2"],
                position=(0, 2),
                size=(2, 2)
            ),
            DashboardWidget(
                widget_type=DashboardWidgetType.RECOMMENDATION_LIST,
                title="Test Recommendations",
                data=["Rec 1", "Rec 2", "Rec 3"],
                position=(2, 0),
                size=(4, 2)
            ),
            DashboardWidget(
                widget_type=DashboardWidgetType.ROI_ANALYSIS,
                title="Test ROI",
                data={"roi_percentage": 125.0, "payback_period": "6 months"},
                position=(2, 2),
                size=(2, 2)
            )
        ]
        
        # Test rendering
        result = await DashboardRenderer.render_console_dashboard(widgets)
        
        # Verify result
        assert isinstance(result, str)
        assert len(result) > 0
        assert "UPID CLI Executive Dashboard" in result
        assert "Test Metrics" in result
        assert "Test Alerts" in result
        assert "Test Recommendations" in result
        assert "Test ROI" in result
    
    def test_render_metric_card(self):
        """Test metric card rendering"""
        # Test metric card rendering
        data = {"cpu_utilization": 0.65, "memory_usage": 0.72, "cost_per_hour": 2.45}
        lines = DashboardRenderer._render_metric_card(data)
        
        # Verify lines
        assert isinstance(lines, list)
        assert len(lines) == 3
        
        for line in lines:
            assert isinstance(line, str)
            assert ":" in line
    
    def test_render_alert_panel(self):
        """Test alert panel rendering"""
        # Test with alerts
        alerts = ["Alert 1", "Alert 2"]
        lines = DashboardRenderer._render_alert_panel(alerts)
        
        assert isinstance(lines, list)
        assert len(lines) == 2
        
        for line in lines:
            assert isinstance(line, str)
            assert "⚠️" in line
        
        # Test without alerts
        empty_alerts = []
        lines = DashboardRenderer._render_alert_panel(empty_alerts)
        
        assert isinstance(lines, list)
        assert len(lines) == 1
        assert "✅" in lines[0]
    
    def test_render_recommendation_list(self):
        """Test recommendation list rendering"""
        # Test recommendation list rendering
        recommendations = ["Rec 1", "Rec 2", "Rec 3"]
        lines = DashboardRenderer._render_recommendation_list(recommendations)
        
        # Verify lines
        assert isinstance(lines, list)
        assert len(lines) == 3
        
        for i, line in enumerate(lines, 1):
            assert isinstance(line, str)
            assert f"{i}." in line
    
    def test_render_roi_analysis(self):
        """Test ROI analysis rendering"""
        # Test ROI analysis rendering
        data = {
            "roi_percentage": 125.0,
            "payback_period": "6 months",
            "net_present_value": 4500.0,
            "confidence_level": 0.85
        }
        lines = DashboardRenderer._render_roi_analysis(data)
        
        # Verify lines
        assert isinstance(lines, list)
        assert len(lines) == 4
        
        for line in lines:
            assert isinstance(line, str)
            assert ":" in line


if __name__ == "__main__":
    pytest.main([__file__]) 