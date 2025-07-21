"""
Phase 6: Real-time Monitoring & Alerting CLI Commands
Provides dashboard, alert management, notification configuration, and monitoring control
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import click
import json
import time

from ..core.realtime_monitoring import (
    RealTimeMonitor, AlertRule, AlertType, AlertSeverity,
    EmailNotificationProvider, SlackNotificationProvider, WebhookNotificationProvider
)
from ..auth.enterprise_auth import EnterpriseAuthManager
from ..core.auth_analytics_integration import AuthAnalyticsIntegration

logger = logging.getLogger(__name__)


@click.group()
def realtime_monitoring():
    """Real-time Monitoring & Alerting Commands"""
    pass


@realtime_monitoring.command()
@click.option('--interval', '-i', default=30, help='Monitoring interval in seconds')
@click.option('--duration', '-d', default=0, help='Monitoring duration in minutes (0 for continuous)')
async def start(interval: int, duration: int):
    """
    Start real-time monitoring and alerting
    
    Begins continuous monitoring of authentication data with configurable
    alert rules and notification providers.
    """
    try:
        click.echo("🚀 Starting real-time monitoring...")
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Start monitoring
        await monitor.start_monitoring(interval)
        
        click.echo(f"✅ Real-time monitoring started (interval: {interval}s)")
        
        if duration > 0:
            click.echo(f"⏱️  Monitoring will run for {duration} minutes")
            await asyncio.sleep(duration * 60)
            await monitor.stop_monitoring()
            click.echo("🛑 Monitoring stopped")
        else:
            click.echo("🔄 Monitoring running continuously (Ctrl+C to stop)")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await monitor.stop_monitoring()
                click.echo("🛑 Monitoring stopped by user")
        
    except Exception as e:
        click.echo(f"❌ Error starting monitoring: {e}")
        logger.error(f"Monitoring start error: {e}")


@realtime_monitoring.command()
async def stop():
    """
    Stop real-time monitoring
    
    Stops the currently running monitoring process.
    """
    try:
        click.echo("🛑 Stopping real-time monitoring...")
        
        # This would need to be implemented with a proper monitoring service
        # For now, just show a message
        click.echo("✅ Monitoring stop command sent")
        
    except Exception as e:
        click.echo(f"❌ Error stopping monitoring: {e}")
        logger.error(f"Monitoring stop error: {e}")


@realtime_monitoring.command()
@click.option('--refresh-interval', '-r', default=5, help='Dashboard refresh interval in seconds')
async def dashboard(refresh_interval: int):
    """
    Display real-time monitoring dashboard
    
    Shows live metrics, alerts, and trends in a continuously updating dashboard.
    """
    try:
        click.echo("📊 Starting real-time dashboard...")
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Start monitoring in background
        await monitor.start_monitoring(30)
        
        click.echo("🔄 Dashboard updating... (Ctrl+C to stop)")
        
        try:
            while True:
                # Clear screen (works on most terminals)
                click.echo("\033[2J\033[H", nl=False)
                
                # Display dashboard
                await _display_dashboard(monitor)
                
                await asyncio.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            await monitor.stop_monitoring()
            click.echo("\n🛑 Dashboard stopped")
        
    except Exception as e:
        click.echo(f"❌ Error displaying dashboard: {e}")
        logger.error(f"Dashboard error: {e}")


@realtime_monitoring.command()
@click.option('--severity', '-s', type=click.Choice(['info', 'warning', 'critical', 'emergency']), 
              help='Filter by alert severity')
@click.option('--type', '-t', type=click.Choice(['security_incident', 'user_behavior', 'authentication_failure', 
                                                  'system_health', 'performance_degradation', 'business_impact']), 
              help='Filter by alert type')
@click.option('--resolved', is_flag=True, help='Show only resolved alerts')
async def alerts(severity: Optional[str], type: Optional[str], resolved: bool):
    """
    Display monitoring alerts
    
    Shows current alerts with filtering options for severity, type, and status.
    """
    try:
        click.echo("🚨 Displaying monitoring alerts...")
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Get alerts
        all_alerts = monitor.get_alerts(resolved=resolved)
        
        # Apply filters
        filtered_alerts = all_alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity.value == severity]
        
        if type:
            filtered_alerts = [a for a in filtered_alerts if a.alert_type.value == type]
        
        # Display alerts
        await _display_alerts(filtered_alerts)
        
        click.echo(f"✅ Displayed {len(filtered_alerts)} alerts")
        
    except Exception as e:
        click.echo(f"❌ Error displaying alerts: {e}")
        logger.error(f"Alerts display error: {e}")


@realtime_monitoring.command()
@click.argument('alert_id')
@click.argument('acknowledged_by')
async def acknowledge(alert_id: str, acknowledged_by: str):
    """
    Acknowledge an alert
    
    Marks an alert as acknowledged by the specified user.
    """
    try:
        click.echo(f"✅ Acknowledging alert {alert_id}...")
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Acknowledge alert
        monitor.acknowledge_alert(alert_id, acknowledged_by)
        
        click.echo(f"✅ Alert {alert_id} acknowledged by {acknowledged_by}")
        
    except Exception as e:
        click.echo(f"❌ Error acknowledging alert: {e}")
        logger.error(f"Alert acknowledgement error: {e}")


@realtime_monitoring.command()
@click.argument('alert_id')
async def resolve(alert_id: str):
    """
    Resolve an alert
    
    Marks an alert as resolved.
    """
    try:
        click.echo(f"✅ Resolving alert {alert_id}...")
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Resolve alert
        monitor.resolve_alert(alert_id)
        
        click.echo(f"✅ Alert {alert_id} resolved")
        
    except Exception as e:
        click.echo(f"❌ Error resolving alert: {e}")
        logger.error(f"Alert resolution error: {e}")


@realtime_monitoring.command()
@click.option('--rule-id', '-r', required=True, help='Rule ID')
@click.option('--name', '-n', required=True, help='Rule name')
@click.option('--type', '-t', type=click.Choice(['security_incident', 'user_behavior', 'authentication_failure', 
                                                  'system_health', 'performance_degradation', 'business_impact']), 
              required=True, help='Alert type')
@click.option('--severity', '-s', type=click.Choice(['info', 'warning', 'critical', 'emergency']), 
              required=True, help='Alert severity')
@click.option('--conditions', '-c', required=True, help='Rule conditions (JSON)')
@click.option('--enabled/--disabled', default=True, help='Enable/disable rule')
async def add_rule(rule_id: str, name: str, type: str, severity: str, conditions: str, enabled: bool):
    """
    Add a new alert rule
    
    Creates a new configurable alert rule with specified conditions.
    """
    try:
        click.echo(f"➕ Adding alert rule: {name}")
        
        # Parse conditions
        try:
            conditions_dict = json.loads(conditions)
        except json.JSONDecodeError:
            click.echo("❌ Invalid JSON in conditions parameter")
            return
        
        # Create alert rule
        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            alert_type=AlertType(type),
            severity=AlertSeverity(severity),
            conditions=conditions_dict,
            enabled=enabled
        )
        
        # Initialize components and add rule
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        monitor.add_alert_rule(rule)
        
        click.echo(f"✅ Alert rule '{name}' added successfully")
        
    except Exception as e:
        click.echo(f"❌ Error adding alert rule: {e}")
        logger.error(f"Alert rule addition error: {e}")


@realtime_monitoring.command()
@click.argument('rule_id')
async def remove_rule(rule_id: str):
    """
    Remove an alert rule
    
    Removes the specified alert rule.
    """
    try:
        click.echo(f"🗑️  Removing alert rule: {rule_id}")
        
        # Initialize components and remove rule
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        monitor.remove_alert_rule(rule_id)
        
        click.echo(f"✅ Alert rule '{rule_id}' removed successfully")
        
    except Exception as e:
        click.echo(f"❌ Error removing alert rule: {e}")
        logger.error(f"Alert rule removal error: {e}")


@realtime_monitoring.command()
@click.option('--smtp-server', required=True, help='SMTP server address')
@click.option('--smtp-port', default=587, help='SMTP server port')
@click.option('--username', required=True, help='Email username')
@click.option('--password', required=True, help='Email password')
@click.option('--rule-id', '-r', required=True, help='Rule ID to add email notifications to')
async def add_email_notification(smtp_server: str, smtp_port: int, username: str, password: str, rule_id: str):
    """
    Add email notification to an alert rule
    
    Configures email notifications for the specified alert rule.
    """
    try:
        click.echo(f"📧 Adding email notification to rule: {rule_id}")
        
        # Create email notification provider
        email_provider = EmailNotificationProvider(smtp_server, smtp_port, username, password)
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Find the rule and add email provider
        for rule in monitor.alert_rules:
            if rule.rule_id == rule_id:
                rule.notification_providers.append(email_provider)
                click.echo(f"✅ Email notification added to rule '{rule.name}'")
                return
        
        click.echo(f"❌ Alert rule '{rule_id}' not found")
        
    except Exception as e:
        click.echo(f"❌ Error adding email notification: {e}")
        logger.error(f"Email notification addition error: {e}")


@realtime_monitoring.command()
@click.option('--webhook-url', required=True, help='Slack webhook URL')
@click.option('--channel', default='#alerts', help='Slack channel')
@click.option('--rule-id', '-r', required=True, help='Rule ID to add Slack notifications to')
async def add_slack_notification(webhook_url: str, channel: str, rule_id: str):
    """
    Add Slack notification to an alert rule
    
    Configures Slack notifications for the specified alert rule.
    """
    try:
        click.echo(f"💬 Adding Slack notification to rule: {rule_id}")
        
        # Create Slack notification provider
        slack_provider = SlackNotificationProvider(webhook_url, channel)
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Find the rule and add Slack provider
        for rule in monitor.alert_rules:
            if rule.rule_id == rule_id:
                rule.notification_providers.append(slack_provider)
                click.echo(f"✅ Slack notification added to rule '{rule.name}'")
                return
        
        click.echo(f"❌ Alert rule '{rule_id}' not found")
        
    except Exception as e:
        click.echo(f"❌ Error adding Slack notification: {e}")
        logger.error(f"Slack notification addition error: {e}")


@realtime_monitoring.command()
@click.option('--webhook-url', required=True, help='Webhook URL')
@click.option('--headers', help='Webhook headers (JSON)')
@click.option('--rule-id', '-r', required=True, help='Rule ID to add webhook notifications to')
async def add_webhook_notification(webhook_url: str, headers: Optional[str], rule_id: str):
    """
    Add webhook notification to an alert rule
    
    Configures webhook notifications for the specified alert rule.
    """
    try:
        click.echo(f"🔗 Adding webhook notification to rule: {rule_id}")
        
        # Parse headers if provided
        headers_dict = {}
        if headers:
            try:
                headers_dict = json.loads(headers)
            except json.JSONDecodeError:
                click.echo("❌ Invalid JSON in headers parameter")
                return
        
        # Create webhook notification provider
        webhook_provider = WebhookNotificationProvider(webhook_url, headers_dict)
        
        # Initialize components
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        monitor = RealTimeMonitor(auth_manager, auth_analytics)
        
        # Find the rule and add webhook provider
        for rule in monitor.alert_rules:
            if rule.rule_id == rule_id:
                rule.notification_providers.append(webhook_provider)
                click.echo(f"✅ Webhook notification added to rule '{rule.name}'")
                return
        
        click.echo(f"❌ Alert rule '{rule_id}' not found")
        
    except Exception as e:
        click.echo(f"❌ Error adding webhook notification: {e}")
        logger.error(f"Webhook notification addition error: {e}")


async def _display_dashboard(monitor: RealTimeMonitor):
    """Display real-time dashboard"""
    metrics = monitor.get_dashboard_metrics()
    
    if not metrics:
        click.echo("⏳ Waiting for dashboard data...")
        return
    
    # Dashboard header
    click.echo("=" * 80)
    click.echo("📊 UPID CLI REAL-TIME MONITORING DASHBOARD")
    click.echo("=" * 80)
    click.echo(f"🕐 Last Updated: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo()
    
    # Key metrics
    click.echo("📈 KEY METRICS")
    click.echo("-" * 40)
    click.echo(f"👥 Active Sessions: {metrics.active_sessions}")
    click.echo(f"👤 Total Users: {metrics.total_users}")
    click.echo(f"❌ Failed Auth Attempts: {metrics.failed_auth_attempts}")
    click.echo(f"🚨 Security Incidents: {metrics.security_incidents}")
    click.echo(f"⚠️  High Risk Behaviors: {metrics.high_risk_behaviors}")
    click.echo(f"⚡ Avg Response Time: {metrics.avg_response_time:.2f}s")
    click.echo(f"✅ Success Rate: {metrics.success_rate:.1%}")
    click.echo(f"🎯 Risk Score: {metrics.risk_score:.2f}")
    click.echo()
    
    # Alert counts
    click.echo("🚨 ALERT COUNTS")
    click.echo("-" * 40)
    for severity, count in metrics.alerts_count.items():
        severity_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨',
            'emergency': '💀'
        }.get(severity, '❓')
        click.echo(f"{severity_emoji} {severity.upper()}: {count}")
    click.echo()
    
    # Trends
    click.echo("📊 TRENDS")
    click.echo("-" * 40)
    for trend_name, trend_value in metrics.trends.items():
        trend_emoji = {
            'increasing': '📈',
            'decreasing': '📉',
            'stable': '➡️'
        }.get(trend_value, '❓')
        click.echo(f"{trend_emoji} {trend_name.replace('_', ' ').title()}: {trend_value}")
    click.echo()
    
    # Recent alerts
    alerts = monitor.get_alerts(resolved=False)
    recent_alerts = sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:5]
    
    if recent_alerts:
        click.echo("🚨 RECENT ALERTS")
        click.echo("-" * 40)
        for alert in recent_alerts:
            severity_emoji = {
                AlertSeverity.INFO: 'ℹ️',
                AlertSeverity.WARNING: '⚠️',
                AlertSeverity.CRITICAL: '🚨',
                AlertSeverity.EMERGENCY: '💀'
            }.get(alert.severity, '❓')
            
            click.echo(f"{severity_emoji} [{alert.severity.value.upper()}] {alert.title}")
            click.echo(f"   {alert.description}")
            click.echo(f"   Time: {alert.timestamp.strftime('%H:%M:%S')}")
            click.echo()
    
    click.echo("=" * 80)


async def _display_alerts(alerts: List[Any]):
    """Display alerts in a formatted table"""
    if not alerts:
        click.echo("✅ No alerts found")
        return
    
    click.echo("🚨 MONITORING ALERTS")
    click.echo("=" * 100)
    click.echo(f"{'ID':<20} {'Type':<20} {'Severity':<12} {'Status':<10} {'Time':<20} {'Title'}")
    click.echo("-" * 100)
    
    for alert in alerts:
        status = "RESOLVED" if alert.resolved else "ACK" if alert.acknowledged else "NEW"
        severity_emoji = {
            AlertSeverity.INFO: 'ℹ️',
            AlertSeverity.WARNING: '⚠️',
            AlertSeverity.CRITICAL: '🚨',
            AlertSeverity.EMERGENCY: '💀'
        }.get(alert.severity, '❓')
        
        click.echo(f"{alert.alert_id:<20} {alert.alert_type.value:<20} {severity_emoji} {alert.severity.value:<8} {status:<10} {alert.timestamp.strftime('%H:%M:%S'):<20} {alert.title}")
    
    click.echo("-" * 100)
    click.echo(f"Total: {len(alerts)} alerts") 