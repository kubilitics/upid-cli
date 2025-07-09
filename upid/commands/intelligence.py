"""
Intelligence CLI Commands
Commands for running business intelligence, predictive analytics, and optimization.
"""

import asyncio
import click
import json
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.intelligence import IntelligenceEngine
from ..core.business_intelligence import BusinessMetric, BusinessMetricType


@click.group()
def intelligence():
    """Intelligence and analytics commands."""
    pass


@intelligence.command()
@click.option('--cluster', '-c', help='Kubernetes cluster context')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
@click.option('--business-metrics', '-b', help='Path to business metrics JSON file')
async def analyze(cluster: Optional[str], output: str, business_metrics: Optional[str]):
    """Run comprehensive intelligence analysis."""
    click.echo("🔍 Running comprehensive intelligence analysis...")
    
    engine = IntelligenceEngine()
    
    # Load business metrics if provided
    business_metrics_data = None
    if business_metrics:
        try:
            with open(business_metrics, 'r') as f:
                business_metrics_data = json.load(f)
        except Exception as e:
            click.echo(f"⚠️  Warning: Could not load business metrics: {e}")
    
    try:
        report = await engine.run_comprehensive_analysis(
            cluster_context=cluster,
            business_metrics=business_metrics_data
        )
        
        if output == 'json':
            click.echo(json.dumps(report.summary, indent=2, default=str))
        elif output == 'table':
            _display_intelligence_table(report)
        else:
            _display_intelligence_summary(report)
            
    except Exception as e:
        click.echo(f"❌ Error running intelligence analysis: {e}")


@intelligence.command()
@click.option('--cluster', '-c', help='Kubernetes cluster context')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def business(cluster: Optional[str], output: str):
    """Run business intelligence analysis."""
    click.echo("💼 Running business intelligence analysis...")
    
    engine = IntelligenceEngine()
    
    try:
        report = await engine.run_business_intelligence(cluster_context=cluster)
        
        if output == 'json':
            click.echo(json.dumps(report, indent=2, default=str))
        elif output == 'table':
            _display_business_intelligence_table(report)
        else:
            _display_business_intelligence_summary(report)
            
    except Exception as e:
        click.echo(f"❌ Error running business intelligence: {e}")


@intelligence.command()
@click.option('--cluster', '-c', help='Kubernetes cluster context')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def predict(cluster: Optional[str], output: str):
    """Run predictive analytics."""
    click.echo("🔮 Running predictive analytics...")
    
    engine = IntelligenceEngine()
    
    try:
        report = await engine.run_predictive_analytics(cluster_context=cluster)
        
        if output == 'json':
            click.echo(json.dumps(report, indent=2, default=str))
        elif output == 'table':
            _display_predictive_analytics_table(report)
        else:
            _display_predictive_analytics_summary(report)
            
    except Exception as e:
        click.echo(f"❌ Error running predictive analytics: {e}")


@intelligence.command()
@click.option('--cluster', '-c', help='Kubernetes cluster context')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
@click.option('--cost-data', '-d', help='Path to cost data JSON file')
async def optimize(cluster: Optional[str], output: str, cost_data: Optional[str]):
    """Run intelligent optimization analysis."""
    click.echo("⚡ Running intelligent optimization analysis...")
    
    engine = IntelligenceEngine()
    
    # Load cost data if provided
    cost_data_dict = None
    if cost_data:
        try:
            with open(cost_data, 'r') as f:
                cost_data_dict = json.load(f)
        except Exception as e:
            click.echo(f"⚠️  Warning: Could not load cost data: {e}")
    
    try:
        report = await engine.run_intelligent_optimization(
            cluster_context=cluster,
            cost_data=cost_data_dict
        )
        
        if output == 'json':
            click.echo(json.dumps(report, indent=2, default=str))
        elif output == 'table':
            _display_optimization_table(report)
        else:
            _display_optimization_summary(report)
            
    except Exception as e:
        click.echo(f"❌ Error running optimization analysis: {e}")


@intelligence.command()
@click.option('--cluster', '-c', help='Kubernetes cluster context')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def insights(cluster: Optional[str], output: str):
    """Get real-time insights."""
    click.echo("📊 Getting real-time insights...")
    
    engine = IntelligenceEngine()
    
    try:
        insights = await engine.get_real_time_insights(cluster_context=cluster)
        
        if output == 'json':
            click.echo(json.dumps(insights, indent=2, default=str))
        elif output == 'table':
            _display_insights_table(insights)
        else:
            _display_insights_summary(insights)
            
    except Exception as e:
        click.echo(f"❌ Error getting real-time insights: {e}")


@intelligence.command()
@click.option('--cluster', '-c', help='Kubernetes cluster context')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def test_connections(cluster: Optional[str], output: str):
    """Test connections to all metric collection endpoints."""
    click.echo("🔌 Testing metric collection connections...")
    
    from ..core.metrics_collector import KubernetesMetricsCollector
    
    collector = KubernetesMetricsCollector()
    results = collector.test_connections()
    
    if output == 'json':
        click.echo(json.dumps(results, indent=2))
    else:
        _display_connection_test_summary(results)


def _display_intelligence_summary(report):
    """Display comprehensive intelligence summary."""
    click.echo("\n" + "="*60)
    click.echo("🧠 COMPREHENSIVE INTELLIGENCE ANALYSIS")
    click.echo("="*60)
    
    summary = report.summary
    status = summary.get('overall_status', 'unknown')
    status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "🚨"}.get(status, "❓")
    
    click.echo(f"\n{status_emoji} Overall Status: {status.upper()}")
    
    # Key metrics
    metrics = summary.get('key_metrics', {})
    click.echo(f"\n📈 Key Metrics:")
    click.echo(f"  • Business Impact Score: {metrics.get('business_impact_score', 0):.1f}/100")
    click.echo(f"  • Predictions: {metrics.get('total_predictions', 0)}")
    click.echo(f"  • Anomalies: {metrics.get('total_anomalies', 0)}")
    click.echo(f"  • Optimizations: {metrics.get('total_optimizations', 0)}")
    
    # Priority actions
    actions = summary.get('priority_actions', [])
    if actions:
        click.echo(f"\n🎯 Priority Actions:")
        for action in actions[:5]:
            click.echo(f"  • {action}")
    
    # Trends
    trends = summary.get('trends', [])
    if trends:
        click.echo(f"\n📊 Trends:")
        for trend in trends:
            click.echo(f"  • {trend}")
    
    # Top recommendations
    recommendations = summary.get('recommendations', [])
    if recommendations:
        click.echo(f"\n💡 Top Recommendations:")
        for rec in recommendations[:3]:
            click.echo(f"  • {rec}")


def _display_business_intelligence_summary(report):
    """Display business intelligence summary."""
    click.echo("\n" + "="*60)
    click.echo("💼 BUSINESS INTELLIGENCE ANALYSIS")
    click.echo("="*60)
    
    click.echo(f"\n📊 Business Impact Score: {report.get('business_impact_score', 0):.1f}/100")
    
    insights = report.get('insights', [])
    click.echo(f"\n🔍 Business Correlations: {len(insights)}")
    
    for insight in insights[:3]:
        click.echo(f"  • {insight.get('description', 'N/A')}")
        click.echo(f"    Correlation: {insight.get('correlation_strength', 0):.2f}")
        click.echo(f"    Confidence: {insight.get('confidence', 0):.2f}")
    
    summary = report.get('summary', {})
    status = summary.get('status', 'unknown')
    status_emoji = {"healthy": "✅", "needs_attention": "⚠️"}.get(status, "❓")
    
    click.echo(f"\n{status_emoji} Status: {status.upper()}")
    
    findings = summary.get('key_findings', [])
    if findings:
        click.echo(f"\n📋 Key Findings:")
        for finding in findings:
            click.echo(f"  • {finding}")


def _display_predictive_analytics_summary(report):
    """Display predictive analytics summary."""
    click.echo("\n" + "="*60)
    click.echo("🔮 PREDICTIVE ANALYTICS")
    click.echo("="*60)
    
    predictions = report.get('predictions', {})
    click.echo(f"\n📈 Predictions: {predictions.get('total', 0)}")
    click.echo(f"  • High Confidence: {predictions.get('high_confidence', 0)}")
    
    prediction_details = predictions.get('details', [])
    for pred in prediction_details[:3]:
        click.echo(f"  • {pred.get('description', 'N/A')}")
        click.echo(f"    Confidence: {pred.get('confidence', 0):.2f}")
    
    anomalies = report.get('anomalies', {})
    click.echo(f"\n🚨 Anomalies: {anomalies.get('total', 0)}")
    click.echo(f"  • Critical: {anomalies.get('critical', 0)}")
    click.echo(f"  • High: {anomalies.get('high', 0)}")
    
    anomaly_details = anomalies.get('details', [])
    for anomaly in anomaly_details[:3]:
        click.echo(f"  • {anomaly.get('description', 'N/A')}")
        click.echo(f"    Severity: {anomaly.get('severity', 'unknown')}")
    
    summary = report.get('summary', {})
    status = summary.get('status', 'unknown')
    status_emoji = {"healthy": "✅", "needs_attention": "⚠️"}.get(status, "❓")
    
    click.echo(f"\n{status_emoji} Status: {status.upper()}")


def _display_optimization_summary(report):
    """Display optimization summary."""
    click.echo("\n" + "="*60)
    click.echo("⚡ INTELLIGENT OPTIMIZATION")
    click.echo("="*60)
    
    profiles = report.get('resource_profiles', {})
    click.echo(f"\n📊 Resource Profiles: {profiles.get('total', 0)}")
    
    profile_details = profiles.get('profiles', [])
    for profile in profile_details:
        click.echo(f"  • {profile.get('resource', 'N/A')}: {profile.get('current_usage', 0):.1f}%")
        click.echo(f"    Efficiency: {profile.get('efficiency', 0):.2f}")
        click.echo(f"    Optimization Potential: {profile.get('optimization_potential', 0):.2f}")
    
    optimizations = report.get('optimization_recommendations', {})
    click.echo(f"\n🔧 Optimizations: {optimizations.get('total', 0)}")
    click.echo(f"  • Critical: {optimizations.get('by_priority', {}).get('critical', 0)}")
    click.echo(f"  • High: {optimizations.get('by_priority', {}).get('high', 0)}")
    
    optimization_details = optimizations.get('details', [])
    for opt in optimization_details[:3]:
        click.echo(f"  • {opt.get('description', 'N/A')}")
        click.echo(f"    Priority: {opt.get('priority', 'unknown')}")
        click.echo(f"    Expected Improvement: {opt.get('improvement', 0):.1f}%")
    
    estimated_savings = optimizations.get('estimated_savings', 0)
    if estimated_savings > 0:
        click.echo(f"\n💰 Estimated Savings: ${estimated_savings:.2f}")
    
    summary = report.get('summary', {})
    status = summary.get('status', 'unknown')
    status_emoji = {"well_optimized": "✅", "optimization_needed": "⚠️"}.get(status, "❓")
    
    click.echo(f"\n{status_emoji} Status: {status.upper()}")


def _display_insights_summary(insights):
    """Display real-time insights summary."""
    click.echo("\n" + "="*60)
    click.echo("📊 REAL-TIME INSIGHTS")
    click.echo("="*60)
    
    health_status = insights.get('health_status', 'unknown')
    status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "🚨"}.get(health_status, "❓")
    
    click.echo(f"\n{status_emoji} Cluster Health: {health_status.upper()}")
    
    alerts = insights.get('immediate_alerts', [])
    if alerts:
        click.echo(f"\n🚨 Immediate Alerts:")
        for alert in alerts:
            click.echo(f"  • {alert}")
    
    recommendations = insights.get('quick_recommendations', [])
    if recommendations:
        click.echo(f"\n💡 Quick Recommendations:")
        for rec in recommendations:
            click.echo(f"  • {rec}")
    
    current_metrics = insights.get('current_metrics', {})
    if current_metrics:
        click.echo(f"\n📈 Current Metrics:")
        if 'cpu_usage' in current_metrics:
            cpu = current_metrics['cpu_usage'].get('average', 0)
            click.echo(f"  • CPU Usage: {cpu:.1f}%")
        if 'memory_usage' in current_metrics:
            memory = current_metrics['memory_usage'].get('average', 0)
            click.echo(f"  • Memory Usage: {memory:.1f}%")
        if 'pod_count' in current_metrics:
            pods = current_metrics['pod_count'].get('count', 0)
            click.echo(f"  • Pod Count: {pods}")


def _display_connection_test_summary(results):
    """Display connection test results."""
    click.echo("\n" + "="*60)
    click.echo("🔌 METRIC COLLECTION CONNECTION TEST")
    click.echo("="*60)
    
    for service, result in results.items():
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        
        if status == 'connected':
            click.echo(f"✅ {service.upper()}: {message}")
        elif status == 'error':
            click.echo(f"❌ {service.upper()}: {message}")
        elif status == 'not_configured':
            click.echo(f"⚠️  {service.upper()}: {message}")
        else:
            click.echo(f"❓ {service.upper()}: {message}")
    
    click.echo(f"\n📋 SETUP INSTRUCTIONS:")
    click.echo(f"1. Kubernetes: Ensure kubectl is configured and cluster is accessible")
    click.echo(f"2. Prometheus: Set UPID_PROMETHEUS_URL environment variable")
    click.echo(f"3. cAdvisor: Set UPID_CADVISOR_URL environment variable")
    click.echo(f"4. Custom Metrics: Set UPID_CUSTOM_METRICS_URL environment variable")
    click.echo(f"\nExample:")
    click.echo(f"export UPID_PROMETHEUS_URL='http://prometheus:9090'")
    click.echo(f"export UPID_CADVISOR_URL='http://cadvisor:8080'")
    click.echo(f"upid intelligence test-connections")


def _display_intelligence_table(report):
    """Display intelligence data in table format."""
    # Implementation for table display
    click.echo("Table format not yet implemented")


def _display_business_intelligence_table(report):
    """Display business intelligence data in table format."""
    # Implementation for table display
    click.echo("Table format not yet implemented")


def _display_predictive_analytics_table(report):
    """Display predictive analytics data in table format."""
    # Implementation for table display
    click.echo("Table format not yet implemented")


def _display_optimization_table(report):
    """Display optimization data in table format."""
    # Implementation for table display
    click.echo("Table format not yet implemented")


def _display_insights_table(insights):
    """Display insights data in table format."""
    # Implementation for table display
    click.echo("Table format not yet implemented") 