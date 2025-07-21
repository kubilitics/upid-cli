"""
Phase 6: Real-time Monitoring & Alerting
Provides live authentication analytics dashboard, configurable alerts, notification integration, and automated response capabilities
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from collections import defaultdict, deque
import threading
import time

from ..auth.enterprise_auth import EnterpriseAuthManager, AuthSession
from .auth_analytics_integration import AuthAnalyticsIntegration, UserBehaviorPattern, SecurityIncident

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Types of alerts"""
    SECURITY_INCIDENT = "security_incident"
    USER_BEHAVIOR = "user_behavior"
    AUTHENTICATION_FAILURE = "authentication_failure"
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    BUSINESS_IMPACT = "business_impact"


@dataclass
class Alert:
    """Represents a monitoring alert"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics"""
    timestamp: datetime
    active_sessions: int
    total_users: int
    failed_auth_attempts: int
    security_incidents: int
    high_risk_behaviors: int
    avg_response_time: float
    success_rate: float
    risk_score: float
    alerts_count: Dict[str, int]
    trends: Dict[str, str]


class NotificationProvider:
    """Base class for notification providers"""
    
    async def send_notification(self, alert: Alert, recipients: List[str]) -> bool:
        """Send notification for an alert"""
        raise NotImplementedError


class EmailNotificationProvider(NotificationProvider):
    """Email notification provider"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_notification(self, alert: Alert, recipients: List[str]) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
Alert Details:
- Type: {alert.alert_type.value}
- Severity: {alert.severity.value}
- Description: {alert.description}
- Timestamp: {alert.timestamp}
- User ID: {alert.user_id or 'N/A'}
- IP Address: {alert.ip_address or 'N/A'}

Metadata: {json.dumps(alert.metadata, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False


class SlackNotificationProvider(NotificationProvider):
    """Slack notification provider"""
    
    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send_notification(self, alert: Alert, recipients: List[str]) -> bool:
        """Send Slack notification"""
        try:
            color_map = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff8c00",
                AlertSeverity.CRITICAL: "#ff0000",
                AlertSeverity.EMERGENCY: "#8b0000"
            }
            
            payload = {
                "channel": self.channel,
                "attachments": [{
                    "color": color_map.get(alert.severity, "#000000"),
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Type",
                            "value": alert.alert_type.value,
                            "short": True
                        },
                        {
                            "title": "User ID",
                            "value": alert.user_id or "N/A",
                            "short": True
                        },
                        {
                            "title": "IP Address",
                            "value": alert.ip_address or "N/A",
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True
                        }
                    ],
                    "footer": "UPID CLI Security Alert"
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


class WebhookNotificationProvider(NotificationProvider):
    """Webhook notification provider"""
    
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {}
    
    async def send_notification(self, alert: Alert, recipients: List[str]) -> bool:
        """Send webhook notification"""
        try:
            payload = {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "user_id": alert.user_id,
                "session_id": alert.session_id,
                "ip_address": alert.ip_address,
                "metadata": alert.metadata,
                "recipients": recipients
            }
            
            response = requests.post(self.webhook_url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class AlertRule:
    """Configurable alert rule"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        conditions: Dict[str, Any],
        enabled: bool = True,
        notification_providers: List[NotificationProvider] = None
    ):
        self.rule_id = rule_id
        self.name = name
        self.alert_type = alert_type
        self.severity = severity
        self.conditions = conditions
        self.enabled = enabled
        self.notification_providers = notification_providers or []
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate if the rule should trigger an alert"""
        if not self.enabled:
            return False
        
        # Evaluate conditions based on alert type
        if self.alert_type == AlertType.SECURITY_INCIDENT:
            return self._evaluate_security_incident(data)
        elif self.alert_type == AlertType.USER_BEHAVIOR:
            return self._evaluate_user_behavior(data)
        elif self.alert_type == AlertType.AUTHENTICATION_FAILURE:
            return self._evaluate_auth_failure(data)
        elif self.alert_type == AlertType.SYSTEM_HEALTH:
            return self._evaluate_system_health(data)
        elif self.alert_type == AlertType.PERFORMANCE_DEGRADATION:
            return self._evaluate_performance(data)
        elif self.alert_type == AlertType.BUSINESS_IMPACT:
            return self._evaluate_business_impact(data)
        
        return False
    
    def _evaluate_security_incident(self, data: Dict[str, Any]) -> bool:
        """Evaluate security incident conditions"""
        incidents = data.get('security_incidents', [])
        threshold = self.conditions.get('incident_count', 0)
        severity_filter = self.conditions.get('severity', [])
        
        if severity_filter:
            incidents = [i for i in incidents if i.severity in severity_filter]
        
        return len(incidents) >= threshold
    
    def _evaluate_user_behavior(self, data: Dict[str, Any]) -> bool:
        """Evaluate user behavior conditions"""
        behaviors = data.get('user_behavior_patterns', [])
        risk_threshold = self.conditions.get('risk_threshold', 0.7)
        behavior_types = self.conditions.get('behavior_types', [])
        
        if behavior_types:
            behaviors = [b for b in behaviors if b.behavior_type.value in behavior_types]
        
        high_risk_behaviors = [b for b in behaviors if b.risk_score >= risk_threshold]
        return len(high_risk_behaviors) > 0
    
    def _evaluate_auth_failure(self, data: Dict[str, Any]) -> bool:
        """Evaluate authentication failure conditions"""
        auth_metrics = data.get('authentication_metrics', {})
        failure_threshold = self.conditions.get('failure_threshold', 5)
        success_rate_threshold = self.conditions.get('success_rate_threshold', 0.8)
        
        failed_attempts = auth_metrics.get('failed_auth_events', 0)
        success_rate = auth_metrics.get('success_rate', 1.0)
        
        return failed_attempts >= failure_threshold or success_rate < success_rate_threshold
    
    def _evaluate_system_health(self, data: Dict[str, Any]) -> bool:
        """Evaluate system health conditions"""
        auth_metrics = data.get('authentication_metrics', {})
        active_sessions = auth_metrics.get('active_sessions', 0)
        total_sessions = auth_metrics.get('total_sessions', 0)
        
        if total_sessions == 0:
            return False
        
        session_ratio = active_sessions / total_sessions
        threshold = self.conditions.get('session_ratio_threshold', 0.1)
        
        return session_ratio < threshold
    
    def _evaluate_performance(self, data: Dict[str, Any]) -> bool:
        """Evaluate performance conditions"""
        dashboard_metrics = data.get('dashboard_metrics', {})
        avg_response_time = dashboard_metrics.get('avg_response_time', 0)
        threshold = self.conditions.get('response_time_threshold', 5.0)
        
        return avg_response_time > threshold
    
    def _evaluate_business_impact(self, data: Dict[str, Any]) -> bool:
        """Evaluate business impact conditions"""
        business_impact = data.get('business_impact', {})
        productivity_impact = business_impact.get('productivity_impact', {})
        efficiency_score = productivity_impact.get('efficiency_score', 100)
        threshold = self.conditions.get('efficiency_threshold', 80)
        
        return efficiency_score < threshold


class RealTimeMonitor:
    """
    Real-time monitoring and alerting system
    """
    
    def __init__(self, auth_manager: EnterpriseAuthManager, auth_analytics: AuthAnalyticsIntegration):
        self.auth_manager = auth_manager
        self.auth_analytics = auth_analytics
        self.alert_rules: List[AlertRule] = []
        self.alerts: List[Alert] = []
        self.dashboard_metrics: DashboardMetrics = None
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="critical_security_incident",
                name="Critical Security Incident",
                alert_type=AlertType.SECURITY_INCIDENT,
                severity=AlertSeverity.CRITICAL,
                conditions={"incident_count": 1, "severity": ["critical"]}
            ),
            AlertRule(
                rule_id="high_risk_behavior",
                name="High Risk User Behavior",
                alert_type=AlertType.USER_BEHAVIOR,
                severity=AlertSeverity.WARNING,
                conditions={"risk_threshold": 0.8, "behavior_types": ["suspicious", "malicious"]}
            ),
            AlertRule(
                rule_id="auth_failure_spike",
                name="Authentication Failure Spike",
                alert_type=AlertType.AUTHENTICATION_FAILURE,
                severity=AlertSeverity.WARNING,
                conditions={"failure_threshold": 10, "success_rate_threshold": 0.7}
            ),
            AlertRule(
                rule_id="system_health_degradation",
                name="System Health Degradation",
                alert_type=AlertType.SYSTEM_HEALTH,
                severity=AlertSeverity.WARNING,
                conditions={"session_ratio_threshold": 0.05}
            ),
            AlertRule(
                rule_id="performance_degradation",
                name="Performance Degradation",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                severity=AlertSeverity.WARNING,
                conditions={"response_time_threshold": 10.0}
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start real-time monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting real-time monitoring")
        
        # Start monitoring in a separate thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run monitoring cycle
                asyncio.run(self._monitoring_cycle())
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        try:
            # Collect current data
            auth_sessions = list(self.auth_manager.sessions.values())
            audit_trail = await self.auth_manager.get_audit_trail()
            
            # Run analytics
            analytics_report = await self.auth_analytics.run_comprehensive_auth_analytics()
            
            # Update dashboard metrics
            await self._update_dashboard_metrics(auth_sessions, audit_trail, analytics_report)
            
            # Evaluate alert rules
            await self._evaluate_alert_rules(analytics_report)
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    async def _update_dashboard_metrics(
        self,
        auth_sessions: List[AuthSession],
        audit_trail: List[Dict[str, Any]],
        analytics_report: Any
    ):
        """Update real-time dashboard metrics"""
        try:
            # Calculate basic metrics
            active_sessions = len([s for s in auth_sessions if s.expires_at > datetime.now()])
            total_users = len(set(s.user_principal.user_id for s in auth_sessions))
            
            # Calculate authentication metrics
            failed_auth_attempts = len([e for e in audit_trail if e.get('event_type') == 'authentication_failed'])
            total_auth_events = len(audit_trail)
            success_rate = (total_auth_events - failed_auth_attempts) / total_auth_events if total_auth_events > 0 else 1.0
            
            # Calculate security metrics
            security_incidents = len(analytics_report.security_incidents)
            high_risk_behaviors = len([b for b in analytics_report.user_behavior_patterns if b.risk_score > 0.7])
            
            # Calculate performance metrics (mock for now)
            avg_response_time = 0.5  # Mock value
            risk_score = analytics_report.risk_assessment.get('overall_risk_score', 0.0)
            
            # Calculate alert counts by severity
            alerts_count = defaultdict(int)
            for alert in self.alerts:
                if not alert.resolved:
                    alerts_count[alert.severity.value] += 1
            
            # Calculate trends
            trends = await self._calculate_trends()
            
            self.dashboard_metrics = DashboardMetrics(
                timestamp=datetime.now(),
                active_sessions=active_sessions,
                total_users=total_users,
                failed_auth_attempts=failed_auth_attempts,
                security_incidents=security_incidents,
                high_risk_behaviors=high_risk_behaviors,
                avg_response_time=avg_response_time,
                success_rate=success_rate,
                risk_score=risk_score,
                alerts_count=dict(alerts_count),
                trends=trends
            )
            
            # Store in history
            self.metrics_history.append(self.dashboard_metrics)
            
        except Exception as e:
            logger.error(f"Error updating dashboard metrics: {e}")
    
    async def _calculate_trends(self) -> Dict[str, str]:
        """Calculate trends from metrics history"""
        if len(self.metrics_history) < 2:
            return {"security_incidents": "stable", "risk_score": "stable", "success_rate": "stable"}
        
        # Get recent metrics
        recent_metrics = list(self.metrics_history)[-5:]  # Last 5 data points
        
        trends = {}
        
        # Calculate security incidents trend
        incident_counts = [m.security_incidents for m in recent_metrics]
        if len(incident_counts) >= 2:
            if incident_counts[-1] > incident_counts[0]:
                trends["security_incidents"] = "increasing"
            elif incident_counts[-1] < incident_counts[0]:
                trends["security_incidents"] = "decreasing"
            else:
                trends["security_incidents"] = "stable"
        
        # Calculate risk score trend
        risk_scores = [m.risk_score for m in recent_metrics]
        if len(risk_scores) >= 2:
            if risk_scores[-1] > risk_scores[0] + 0.1:
                trends["risk_score"] = "increasing"
            elif risk_scores[-1] < risk_scores[0] - 0.1:
                trends["risk_score"] = "decreasing"
            else:
                trends["risk_score"] = "stable"
        
        # Calculate success rate trend
        success_rates = [m.success_rate for m in recent_metrics]
        if len(success_rates) >= 2:
            if success_rates[-1] < success_rates[0] - 0.05:
                trends["success_rate"] = "decreasing"
            elif success_rates[-1] > success_rates[0] + 0.05:
                trends["success_rate"] = "increasing"
            else:
                trends["success_rate"] = "stable"
        
        return trends
    
    async def _evaluate_alert_rules(self, analytics_report: Any):
        """Evaluate all alert rules"""
        try:
            # Prepare data for rule evaluation
            evaluation_data = {
                'security_incidents': analytics_report.security_incidents,
                'user_behavior_patterns': analytics_report.user_behavior_patterns,
                'authentication_metrics': analytics_report.authentication_metrics,
                'dashboard_metrics': self.dashboard_metrics,
                'business_impact': analytics_report.business_impact
            }
            
            # Evaluate each rule
            for rule in self.alert_rules:
                if rule.evaluate(evaluation_data):
                    await self._create_alert(rule, evaluation_data)
                    
        except Exception as e:
            logger.error(f"Error evaluating alert rules: {e}")
    
    async def _create_alert(self, rule: AlertRule, data: Dict[str, Any]):
        """Create and process an alert"""
        try:
            alert_id = f"{rule.rule_id}_{datetime.now().timestamp()}"
            
            # Generate alert description based on rule type
            description = await self._generate_alert_description(rule, data)
            
            alert = Alert(
                alert_id=alert_id,
                alert_type=rule.alert_type,
                severity=rule.severity,
                title=rule.name,
                description=description,
                timestamp=datetime.now(),
                metadata={
                    'rule_id': rule.rule_id,
                    'conditions': rule.conditions,
                    'evaluation_data': data
                }
            )
            
            # Add alert to list
            self.alerts.append(alert)
            
            # Send notifications
            await self._send_notifications(alert, rule)
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            logger.info(f"Alert created: {alert.alert_id} - {alert.title}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    async def _generate_alert_description(self, rule: AlertRule, data: Dict[str, Any]) -> str:
        """Generate alert description based on rule type and data"""
        if rule.alert_type == AlertType.SECURITY_INCIDENT:
            incidents = data.get('security_incidents', [])
            critical_incidents = [i for i in incidents if i.severity == 'critical']
            return f"Detected {len(critical_incidents)} critical security incidents"
        
        elif rule.alert_type == AlertType.USER_BEHAVIOR:
            behaviors = data.get('user_behavior_patterns', [])
            high_risk = [b for b in behaviors if b.risk_score > 0.7]
            return f"Detected {len(high_risk)} high-risk user behavior patterns"
        
        elif rule.alert_type == AlertType.AUTHENTICATION_FAILURE:
            auth_metrics = data.get('authentication_metrics', {})
            failed_attempts = auth_metrics.get('failed_auth_events', 0)
            success_rate = auth_metrics.get('success_rate', 1.0)
            return f"Authentication failures: {failed_attempts}, Success rate: {success_rate:.1%}"
        
        elif rule.alert_type == AlertType.SYSTEM_HEALTH:
            dashboard_metrics = data.get('dashboard_metrics')
            if dashboard_metrics:
                return f"System health degraded: {dashboard_metrics.active_sessions} active sessions"
            return "System health degradation detected"
        
        elif rule.alert_type == AlertType.PERFORMANCE_DEGRADATION:
            dashboard_metrics = data.get('dashboard_metrics')
            if dashboard_metrics:
                return f"Performance degraded: {dashboard_metrics.avg_response_time:.2f}s avg response time"
            return "Performance degradation detected"
        
        elif rule.alert_type == AlertType.BUSINESS_IMPACT:
            business_impact = data.get('business_impact', {})
            productivity = business_impact.get('productivity_impact', {})
            efficiency = productivity.get('efficiency_score', 100)
            return f"Business impact detected: {efficiency:.1f}% efficiency score"
        
        return f"Alert triggered by rule: {rule.name}"
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send notifications for an alert"""
        for provider in rule.notification_providers:
            try:
                # Get recipients from rule or use defaults
                recipients = rule.conditions.get('recipients', ['admin@company.com'])
                
                success = await provider.send_notification(alert, recipients)
                if success:
                    logger.info(f"Notification sent via {provider.__class__.__name__} for alert {alert.alert_id}")
                else:
                    logger.warning(f"Failed to send notification via {provider.__class__.__name__} for alert {alert.alert_id}")
                    
            except Exception as e:
                logger.error(f"Error sending notification via {provider.__class__.__name__}: {e}")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        self.alert_rules = [r for r in self.alert_rules if r.rule_id != rule_id]
        logger.info(f"Removed alert rule: {rule_id}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add an alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_dashboard_metrics(self) -> Optional[DashboardMetrics]:
        """Get current dashboard metrics"""
        return self.dashboard_metrics
    
    def get_alerts(self, resolved: bool = False) -> List[Alert]:
        """Get alerts, optionally filtered by resolved status"""
        return [a for a in self.alerts if a.resolved == resolved]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                break
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"Alert {alert_id} resolved")
                break 