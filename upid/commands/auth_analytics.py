"""
Phase 5: Authentication Analytics CLI Commands
Provides comprehensive authentication intelligence with user behavior analysis and security incident detection
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import click
import json

from ..core.auth_analytics_integration import AuthAnalyticsIntegration
from ..auth.enterprise_auth import EnterpriseAuthManager

logger = logging.getLogger(__name__)


@click.group()
def auth_analytics():
    """Authentication Analytics Commands"""
    pass


@auth_analytics.command()
@click.option('--cluster-context', '-c', help='Kubernetes cluster context')
@click.option('--time-range', '-t', default='24h', help='Analysis time range (e.g., 24h, 7d, 30d)')
@click.option('--output-format', '-o', default='summary', 
              type=click.Choice(['summary', 'json', 'detailed']), 
              help='Output format')
@click.option('--include-behavior', is_flag=True, help='Include detailed behavior analysis')
@click.option('--include-incidents', is_flag=True, help='Include security incident details')
async def analyze(cluster_context: Optional[str], time_range: str, output_format: str, 
                 include_behavior: bool, include_incidents: bool):
    """
    Run comprehensive authentication analytics
    
    Analyzes user behavior patterns, detects security incidents, and provides
    business intelligence insights from authentication data.
    """
    try:
        click.echo("🔐 Starting comprehensive authentication analytics...")
        
        # Initialize authentication analytics integration
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        
        # Run comprehensive analysis
        report = await auth_analytics.run_comprehensive_auth_analytics(
            cluster_context=cluster_context,
            time_range=time_range
        )
        
        # Display results based on output format
        if output_format == 'summary':
            await _display_summary_report(report)
        elif output_format == 'json':
            await _display_json_report(report)
        elif output_format == 'detailed':
            await _display_detailed_report(report, include_behavior, include_incidents)
        
        click.echo("✅ Authentication analytics completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error running authentication analytics: {e}")
        logger.error(f"Authentication analytics error: {e}")


@auth_analytics.command()
@click.option('--cluster-context', '-c', help='Kubernetes cluster context')
@click.option('--time-range', '-t', default='24h', help='Analysis time range')
async def behavior(cluster_context: Optional[str], time_range: str):
    """
    Analyze user behavior patterns from authentication data
    
    Identifies anomalous behavior patterns, user activity trends, and potential
    security concerns based on authentication patterns.
    """
    try:
        click.echo("👤 Analyzing user behavior patterns...")
        
        # Initialize authentication analytics integration
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        
        # Get authentication data
        auth_sessions = list(auth_manager.sessions.values())
        audit_trail = await auth_manager.get_audit_trail()
        
        # Analyze user behavior
        behavior_patterns = await auth_analytics.user_behavior_analyzer.analyze_user_behavior(
            auth_sessions, audit_trail
        )
        
        # Display behavior analysis
        await _display_behavior_analysis(behavior_patterns)
        
        click.echo("✅ User behavior analysis completed!")
        
    except Exception as e:
        click.echo(f"❌ Error analyzing user behavior: {e}")
        logger.error(f"User behavior analysis error: {e}")


@auth_analytics.command()
@click.option('--cluster-context', '-c', help='Kubernetes cluster context')
@click.option('--time-range', '-t', default='24h', help='Analysis time range')
@click.option('--severity', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']), 
              help='Filter by incident severity')
async def incidents(cluster_context: Optional[str], time_range: str, severity: Optional[str]):
    """
    Detect and analyze security incidents from authentication data
    
    Identifies security incidents such as failed logins, suspicious access,
    privilege escalation, and unusual authentication patterns.
    """
    try:
        click.echo("🚨 Detecting security incidents...")
        
        # Initialize authentication analytics integration
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        
        # Get authentication data
        auth_sessions = list(auth_manager.sessions.values())
        audit_trail = await auth_manager.get_audit_trail()
        
        # Detect security incidents
        security_incidents = await auth_analytics.security_incident_detector.detect_security_incidents(
            auth_sessions, audit_trail
        )
        
        # Filter by severity if specified
        if severity:
            security_incidents = [i for i in security_incidents if i.severity == severity]
        
        # Display security incidents
        await _display_security_incidents(security_incidents)
        
        click.echo("✅ Security incident detection completed!")
        
    except Exception as e:
        click.echo(f"❌ Error detecting security incidents: {e}")
        logger.error(f"Security incident detection error: {e}")


@auth_analytics.command()
@click.option('--cluster-context', '-c', help='Kubernetes cluster context')
@click.option('--time-range', '-t', default='24h', help='Analysis time range')
async def metrics(cluster_context: Optional[str], time_range: str):
    """
    Display authentication metrics and statistics
    
    Shows comprehensive authentication metrics including success rates,
    user statistics, risk scores, and provider distribution.
    """
    try:
        click.echo("📊 Calculating authentication metrics...")
        
        # Initialize authentication analytics integration
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        
        # Get authentication data
        auth_sessions = list(auth_manager.sessions.values())
        audit_trail = await auth_manager.get_audit_trail()
        
        # Calculate authentication metrics
        auth_metrics = await auth_analytics._calculate_authentication_metrics(
            auth_sessions, audit_trail
        )
        
        # Display authentication metrics
        await _display_authentication_metrics(auth_metrics)
        
        click.echo("✅ Authentication metrics calculated!")
        
    except Exception as e:
        click.echo(f"❌ Error calculating authentication metrics: {e}")
        logger.error(f"Authentication metrics error: {e}")


@auth_analytics.command()
@click.option('--cluster-context', '-c', help='Kubernetes cluster context')
@click.option('--time-range', '-t', default='24h', help='Analysis time range')
async def risk(cluster_context: Optional[str], time_range: str):
    """
    Perform comprehensive risk assessment
    
    Analyzes overall security risk based on user behavior patterns,
    security incidents, and authentication metrics.
    """
    try:
        click.echo("⚠️  Performing risk assessment...")
        
        # Initialize authentication analytics integration
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        
        # Get authentication data
        auth_sessions = list(auth_manager.sessions.values())
        audit_trail = await auth_manager.get_audit_trail()
        
        # Analyze user behavior and security incidents
        behavior_patterns = await auth_analytics.user_behavior_analyzer.analyze_user_behavior(
            auth_sessions, audit_trail
        )
        security_incidents = await auth_analytics.security_incident_detector.detect_security_incidents(
            auth_sessions, audit_trail
        )
        auth_metrics = await auth_analytics._calculate_authentication_metrics(
            auth_sessions, audit_trail
        )
        
        # Perform risk assessment
        risk_assessment = await auth_analytics._perform_risk_assessment(
            behavior_patterns, security_incidents, auth_metrics
        )
        
        # Display risk assessment
        await _display_risk_assessment(risk_assessment)
        
        click.echo("✅ Risk assessment completed!")
        
    except Exception as e:
        click.echo(f"❌ Error performing risk assessment: {e}")
        logger.error(f"Risk assessment error: {e}")


async def _display_summary_report(report):
    """Display summary authentication analytics report"""
    click.echo("\n" + "="*60)
    click.echo("🔐 AUTHENTICATION ANALYTICS SUMMARY")
    click.echo("="*60)
    
    # Overall status
    status = report.summary.get('overall_status', 'unknown')
    status_emoji = "🟢" if status == 'healthy' else "🟡" if status == 'attention_required' else "🔴"
    click.echo(f"{status_emoji} Overall Status: {status.upper()}")
    
    # Key metrics
    key_metrics = report.summary.get('key_metrics', {})
    click.echo(f"\n📊 Key Metrics:")
    click.echo(f"   • Total Users: {key_metrics.get('total_users', 0)}")
    click.echo(f"   • Active Sessions: {key_metrics.get('active_sessions', 0)}")
    click.echo(f"   • Behavior Patterns: {key_metrics.get('behavior_patterns', 0)}")
    click.echo(f"   • Security Incidents: {key_metrics.get('security_incidents', 0)}")
    click.echo(f"   • Success Rate: {key_metrics.get('success_rate', 0):.1f}%")
    
    # Risk summary
    risk_summary = report.summary.get('risk_summary', {})
    click.echo(f"\n⚠️  Risk Assessment:")
    click.echo(f"   • Overall Risk: {risk_summary.get('overall_risk', 0):.2f}")
    click.echo(f"   • Risk Level: {risk_summary.get('risk_level', 'unknown').upper()}")
    click.echo(f"   • Critical Incidents: {risk_summary.get('critical_incidents', 0)}")
    
    # Trends
    trends = report.summary.get('trends', {})
    click.echo(f"\n📈 Trends:")
    for trend_name, trend_value in trends.items():
        trend_emoji = "📈" if trend_value == 'increasing' else "📉" if trend_value == 'decreasing' else "➡️"
        click.echo(f"   • {trend_name.replace('_', ' ').title()}: {trend_emoji} {trend_value}")
    
    # Top recommendations
    if report.recommendations:
        click.echo(f"\n💡 Top Recommendations:")
        for i, recommendation in enumerate(report.recommendations[:3], 1):
            click.echo(f"   {i}. {recommendation}")


async def _display_json_report(report):
    """Display authentication analytics report in JSON format"""
    # Convert report to JSON-serializable format
    json_report = {
        'timestamp': report.timestamp.isoformat(),
        'user_behavior_patterns': [
            {
                'user_id': p.user_id,
                'behavior_type': p.behavior_type.value,
                'confidence': p.confidence,
                'description': p.description,
                'timestamp': p.timestamp.isoformat(),
                'risk_score': p.risk_score,
                'metadata': p.metadata
            }
            for p in report.user_behavior_patterns
        ],
        'security_incidents': [
            {
                'incident_id': i.incident_id,
                'incident_type': i.incident_type.value,
                'severity': i.severity,
                'description': i.description,
                'timestamp': i.timestamp.isoformat(),
                'risk_score': i.risk_score,
                'metadata': i.metadata
            }
            for i in report.security_incidents
        ],
        'authentication_metrics': report.authentication_metrics,
        'risk_assessment': report.risk_assessment,
        'business_impact': report.business_impact,
        'recommendations': report.recommendations,
        'summary': report.summary
    }
    
    click.echo(json.dumps(json_report, indent=2))


async def _display_detailed_report(report, include_behavior: bool, include_incidents: bool):
    """Display detailed authentication analytics report"""
    await _display_summary_report(report)
    
    if include_behavior and report.user_behavior_patterns:
        click.echo("\n" + "="*60)
        click.echo("👤 DETAILED USER BEHAVIOR ANALYSIS")
        click.echo("="*60)
        
        for pattern in report.user_behavior_patterns:
            behavior_emoji = {
                'normal': '✅',
                'anomalous': '⚠️',
                'suspicious': '🚨',
                'malicious': '💀',
                'admin_activity': '👑',
                'bulk_operations': '📦'
            }.get(pattern.behavior_type.value, '❓')
            
            click.echo(f"\n{behavior_emoji} {pattern.behavior_type.value.upper()}")
            click.echo(f"   User: {pattern.user_id}")
            click.echo(f"   Description: {pattern.description}")
            click.echo(f"   Confidence: {pattern.confidence:.2f}")
            click.echo(f"   Risk Score: {pattern.risk_score:.2f}")
            click.echo(f"   Timestamp: {pattern.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if include_incidents and report.security_incidents:
        click.echo("\n" + "="*60)
        click.echo("🚨 DETAILED SECURITY INCIDENTS")
        click.echo("="*60)
        
        for incident in report.security_incidents:
            severity_emoji = {
                'low': '🟡',
                'medium': '🟠',
                'high': '🔴',
                'critical': '💀'
            }.get(incident.severity, '❓')
            
            click.echo(f"\n{severity_emoji} {incident.incident_type.value.upper()} ({incident.severity.upper()})")
            click.echo(f"   Description: {incident.description}")
            click.echo(f"   Risk Score: {incident.risk_score:.2f}")
            click.echo(f"   Timestamp: {incident.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if incident.user_id:
                click.echo(f"   User: {incident.user_id}")
            if incident.ip_address:
                click.echo(f"   IP: {incident.ip_address}")


async def _display_behavior_analysis(behavior_patterns: List):
    """Display user behavior analysis results"""
    click.echo("\n" + "="*60)
    click.echo("👤 USER BEHAVIOR ANALYSIS")
    click.echo("="*60)
    
    if not behavior_patterns:
        click.echo("✅ No anomalous behavior patterns detected")
        return
    
    # Group patterns by type
    patterns_by_type = {}
    for pattern in behavior_patterns:
        pattern_type = pattern.behavior_type.value
        if pattern_type not in patterns_by_type:
            patterns_by_type[pattern_type] = []
        patterns_by_type[pattern_type].append(pattern)
    
    # Display patterns by type
    for pattern_type, patterns in patterns_by_type.items():
        behavior_emoji = {
            'normal': '✅',
            'anomalous': '⚠️',
            'suspicious': '🚨',
            'malicious': '💀',
            'admin_activity': '👑',
            'bulk_operations': '📦'
        }.get(pattern_type, '❓')
        
        click.echo(f"\n{behavior_emoji} {pattern_type.upper()} PATTERNS ({len(patterns)})")
        for pattern in patterns:
            click.echo(f"   • {pattern.user_id}: {pattern.description}")
            click.echo(f"     Risk Score: {pattern.risk_score:.2f}, Confidence: {pattern.confidence:.2f}")


async def _display_security_incidents(security_incidents: List):
    """Display security incidents analysis results"""
    click.echo("\n" + "="*60)
    click.echo("🚨 SECURITY INCIDENTS DETECTION")
    click.echo("="*60)
    
    if not security_incidents:
        click.echo("✅ No security incidents detected")
        return
    
    # Group incidents by severity
    incidents_by_severity = {}
    for incident in security_incidents:
        severity = incident.severity
        if severity not in incidents_by_severity:
            incidents_by_severity[severity] = []
        incidents_by_severity[severity].append(incident)
    
    # Display incidents by severity
    for severity in ['critical', 'high', 'medium', 'low']:
        if severity in incidents_by_severity:
            severity_emoji = {
                'low': '🟡',
                'medium': '🟠',
                'high': '🔴',
                'critical': '💀'
            }.get(severity, '❓')
            
            incidents = incidents_by_severity[severity]
            click.echo(f"\n{severity_emoji} {severity.upper()} INCIDENTS ({len(incidents)})")
            for incident in incidents:
                click.echo(f"   • {incident.incident_type.value}: {incident.description}")
                click.echo(f"     Risk Score: {incident.risk_score:.2f}")


async def _display_authentication_metrics(auth_metrics: Dict[str, Any]):
    """Display authentication metrics"""
    click.echo("\n" + "="*60)
    click.echo("📊 AUTHENTICATION METRICS")
    click.echo("="*60)
    
    click.echo(f"\n📈 Session Statistics:")
    click.echo(f"   • Total Sessions: {auth_metrics.get('total_sessions', 0)}")
    click.echo(f"   • Active Sessions: {auth_metrics.get('active_sessions', 0)}")
    click.echo(f"   • Unique Users: {auth_metrics.get('unique_users', 0)}")
    
    click.echo(f"\n🔐 Provider Distribution:")
    provider_dist = auth_metrics.get('provider_distribution', {})
    for provider, count in provider_dist.items():
        click.echo(f"   • {provider}: {count}")
    
    click.echo(f"\n⚠️  Risk Statistics:")
    click.echo(f"   • High Risk Sessions: {auth_metrics.get('high_risk_sessions', 0)}")
    click.echo(f"   • Average Risk Score: {auth_metrics.get('average_risk_score', 0):.2f}")
    
    click.echo(f"\n📋 Audit Statistics:")
    click.echo(f"   • Total Audit Events: {auth_metrics.get('total_audit_events', 0)}")
    click.echo(f"   • Failed Auth Events: {auth_metrics.get('failed_auth_events', 0)}")
    click.echo(f"   • Success Rate: {auth_metrics.get('success_rate', 1.0) * 100:.1f}%")


async def _display_risk_assessment(risk_assessment: Dict[str, Any]):
    """Display risk assessment results"""
    click.echo("\n" + "="*60)
    click.echo("⚠️  RISK ASSESSMENT")
    click.echo("="*60)
    
    overall_risk = risk_assessment.get('overall_risk_score', 0)
    risk_level = risk_assessment.get('risk_level', 'unknown')
    
    # Risk level emoji
    risk_emoji = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴',
        'critical': '💀'
    }.get(risk_level, '❓')
    
    click.echo(f"\n{risk_emoji} Overall Risk Assessment:")
    click.echo(f"   • Risk Score: {overall_risk:.2f}")
    click.echo(f"   • Risk Level: {risk_level.upper()}")
    
    click.echo(f"\n📊 Risk Breakdown:")
    click.echo(f"   • Behavior Risk: {risk_assessment.get('behavior_risk_score', 0):.2f}")
    click.echo(f"   • Incident Risk: {risk_assessment.get('incident_risk_score', 0):.2f}")
    click.echo(f"   • Auth Risk: {risk_assessment.get('auth_risk_score', 0):.2f}")
    
    click.echo(f"\n🚨 Critical Issues:")
    click.echo(f"   • Critical Incidents: {risk_assessment.get('critical_incidents', 0)}")
    click.echo(f"   • High Risk Behaviors: {risk_assessment.get('high_risk_behaviors', 0)}") 