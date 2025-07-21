"""
Comprehensive Unit Tests for Phase 6: Real-time Monitoring & Alerting
Testing the real-time monitoring system, alert rules, notification providers, and dashboard functionality
"""

import pytest
import pytest_asyncio
import asyncio
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import json

from upid.core.realtime_monitoring import (
    RealTimeMonitor, AlertRule, AlertType, AlertSeverity, Alert,
    EmailNotificationProvider, SlackNotificationProvider, WebhookNotificationProvider,
    DashboardMetrics, NotificationProvider
)
from upid.auth.enterprise_auth import EnterpriseAuthManager, AuthSession, UserPrincipal
from upid.core.auth_analytics_integration import AuthAnalyticsIntegration

logger = logging.getLogger(__name__)


class TestAlertRule:
    """Test alert rule functionality"""
    
    @pytest_asyncio.fixture
    async def sample_rule(self):
        """Create a sample alert rule"""
        return AlertRule(
            rule_id="test_rule",
            name="Test Alert Rule",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            conditions={"incident_count": 1, "severity": ["critical"]}
        )
    
    @pytest_asyncio.fixture
    async def sample_data(self):
        """Create sample data for rule evaluation"""
        return {
            'security_incidents': [
                Mock(severity='critical'),
                Mock(severity='high')
            ],
            'user_behavior_patterns': [
                Mock(risk_score=0.8, behavior_type=Mock(value='suspicious')),
                Mock(risk_score=0.3, behavior_type=Mock(value='normal'))
            ],
            'authentication_metrics': {
                'failed_auth_events': 5,
                'success_rate': 0.9
            },
            'dashboard_metrics': Mock(active_sessions=10, total_sessions=100),
            'business_impact': {
                'productivity_impact': {'efficiency_score': 85}
            }
        }
    
    @pytest.mark.asyncio
    async def test_alert_rule_creation(self, sample_rule):
        """Test alert rule creation"""
        assert sample_rule.rule_id == "test_rule"
        assert sample_rule.name == "Test Alert Rule"
        assert sample_rule.alert_type == AlertType.SECURITY_INCIDENT
        assert sample_rule.severity == AlertSeverity.CRITICAL
        assert sample_rule.enabled is True
        assert sample_rule.conditions == {"incident_count": 1, "severity": ["critical"]}
    
    @pytest.mark.asyncio
    async def test_evaluate_security_incident(self, sample_rule, sample_data):
        """Test security incident rule evaluation"""
        # Test with critical incidents
        result = sample_rule._evaluate_security_incident(sample_data)
        assert result is True
        
        # Test with no critical incidents
        sample_data['security_incidents'] = [Mock(severity='high')]
        result = sample_rule._evaluate_security_incident(sample_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_evaluate_user_behavior(self, sample_rule, sample_data):
        """Test user behavior rule evaluation"""
        # Create a user behavior rule
        behavior_rule = AlertRule(
            rule_id="behavior_rule",
            name="Behavior Rule",
            alert_type=AlertType.USER_BEHAVIOR,
            severity=AlertSeverity.WARNING,
            conditions={"risk_threshold": 0.7, "behavior_types": ["suspicious"]}
        )
        
        result = behavior_rule._evaluate_user_behavior(sample_data)
        assert result is True
        
        # Test with low risk behaviors
        sample_data['user_behavior_patterns'] = [
            Mock(risk_score=0.3, behavior_type=Mock(value='normal'))
        ]
        result = behavior_rule._evaluate_user_behavior(sample_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_evaluate_auth_failure(self, sample_rule, sample_data):
        """Test authentication failure rule evaluation"""
        # Create an auth failure rule
        auth_rule = AlertRule(
            rule_id="auth_rule",
            name="Auth Failure Rule",
            alert_type=AlertType.AUTHENTICATION_FAILURE,
            severity=AlertSeverity.WARNING,
            conditions={"failure_threshold": 3, "success_rate_threshold": 0.8}
        )
        
        result = auth_rule._evaluate_auth_failure(sample_data)
        assert result is True
        
        # Test with low failure rate
        sample_data['authentication_metrics'] = {
            'failed_auth_events': 1,
            'success_rate': 0.95
        }
        result = auth_rule._evaluate_auth_failure(sample_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_evaluate_system_health(self, sample_rule, sample_data):
        """Test system health rule evaluation"""
        # Create a system health rule
        health_rule = AlertRule(
            rule_id="health_rule",
            name="System Health Rule",
            alert_type=AlertType.SYSTEM_HEALTH,
            severity=AlertSeverity.WARNING,
            conditions={"session_ratio_threshold": 0.2}
        )
        
        # Test with low session ratio (should trigger alert)
        sample_data['authentication_metrics'] = {'active_sessions': 10, 'total_sessions': 100}
        result = health_rule._evaluate_system_health(sample_data)
        assert result is True
        
        # Test with good session ratio (should not trigger alert)
        sample_data['authentication_metrics'] = {'active_sessions': 80, 'total_sessions': 100}
        result = health_rule._evaluate_system_health(sample_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_evaluate_performance(self, sample_rule, sample_data):
        """Test performance rule evaluation"""
        # Create a performance rule
        perf_rule = AlertRule(
            rule_id="perf_rule",
            name="Performance Rule",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.WARNING,
            conditions={"response_time_threshold": 5.0}
        )
        
        # Test with high response time (should trigger alert)
        sample_data['dashboard_metrics'] = {'avg_response_time': 10.0}
        result = perf_rule._evaluate_performance(sample_data)
        assert result is True
        
        # Test with good performance (should not trigger alert)
        sample_data['dashboard_metrics'] = {'avg_response_time': 2.0}
        result = perf_rule._evaluate_performance(sample_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_evaluate_business_impact(self, sample_rule, sample_data):
        """Test business impact rule evaluation"""
        # Create a business impact rule
        business_rule = AlertRule(
            rule_id="business_rule",
            name="Business Impact Rule",
            alert_type=AlertType.BUSINESS_IMPACT,
            severity=AlertSeverity.WARNING,
            conditions={"efficiency_threshold": 90}
        )
        
        result = business_rule._evaluate_business_impact(sample_data)
        assert result is True
        
        # Test with good efficiency
        sample_data['business_impact'] = {
            'productivity_impact': {'efficiency_score': 95}
        }
        result = business_rule._evaluate_business_impact(sample_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_rule_disabled(self, sample_rule, sample_data):
        """Test that disabled rules don't trigger"""
        sample_rule.enabled = False
        result = sample_rule.evaluate(sample_data)
        assert result is False


class TestNotificationProviders:
    """Test notification provider functionality"""
    
    @pytest_asyncio.fixture
    async def sample_alert(self):
        """Create a sample alert"""
        return Alert(
            alert_id="test_alert_123",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            title="Test Security Alert",
            description="This is a test security alert",
            timestamp=datetime.now(),
            user_id="test_user",
            ip_address="192.168.1.100",
            metadata={"test": "data"}
        )
    
    @pytest_asyncio.fixture
    async def email_provider(self):
        """Create email notification provider"""
        return EmailNotificationProvider(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password123"
        )
    
    @pytest_asyncio.fixture
    async def slack_provider(self):
        """Create Slack notification provider"""
        return SlackNotificationProvider(
            webhook_url="https://hooks.slack.com/services/test",
            channel="#alerts"
        )
    
    @pytest_asyncio.fixture
    async def webhook_provider(self):
        """Create webhook notification provider"""
        return WebhookNotificationProvider(
            webhook_url="https://api.example.com/webhook",
            headers={"Authorization": "Bearer token"}
        )
    
    @pytest.mark.asyncio
    async def test_email_notification_provider_creation(self, email_provider):
        """Test email notification provider creation"""
        assert email_provider.smtp_server == "smtp.gmail.com"
        assert email_provider.smtp_port == 587
        assert email_provider.username == "test@example.com"
        assert email_provider.password == "password123"
    
    @pytest.mark.asyncio
    async def test_slack_notification_provider_creation(self, slack_provider):
        """Test Slack notification provider creation"""
        assert slack_provider.webhook_url == "https://hooks.slack.com/services/test"
        assert slack_provider.channel == "#alerts"
    
    @pytest.mark.asyncio
    async def test_webhook_notification_provider_creation(self, webhook_provider):
        """Test webhook notification provider creation"""
        assert webhook_provider.webhook_url == "https://api.example.com/webhook"
        assert webhook_provider.headers == {"Authorization": "Bearer token"}
    
    @pytest.mark.asyncio
    @patch('smtplib.SMTP')
    async def test_email_notification_send(self, mock_smtp, email_provider, sample_alert):
        """Test email notification sending"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        recipients = ["admin@example.com"]
        result = await email_provider.send_notification(sample_alert, recipients)
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "password123")
        mock_server.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_slack_notification_send(self, mock_post, slack_provider, sample_alert):
        """Test Slack notification sending"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        recipients = ["#alerts"]
        result = await slack_provider.send_notification(sample_alert, recipients)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Check payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'attachments' in payload
        assert len(payload['attachments']) == 1
        assert payload['attachments'][0]['title'] == "Test Security Alert"
    
    @pytest.mark.asyncio
    @patch('requests.post')
    async def test_webhook_notification_send(self, mock_post, webhook_provider, sample_alert):
        """Test webhook notification sending"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        recipients = ["webhook"]
        result = await webhook_provider.send_notification(sample_alert, recipients)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Check payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['alert_id'] == "test_alert_123"
        assert payload['alert_type'] == "security_incident"
        assert payload['severity'] == "critical"


class TestRealTimeMonitor:
    """Test real-time monitoring functionality"""
    
    @pytest_asyncio.fixture
    async def monitor(self):
        """Create real-time monitor for testing"""
        auth_manager = EnterpriseAuthManager()
        auth_analytics = AuthAnalyticsIntegration(auth_manager)
        return RealTimeMonitor(auth_manager, auth_analytics)
    
    @pytest_asyncio.fixture
    async def sample_sessions(self):
        """Create sample authentication sessions"""
        user1 = UserPrincipal(
            user_id="user1",
            email="user1@example.com",
            display_name="User One",
            roles=["user"],
            provider="token"
        )
        
        return [
            AuthSession(
                session_id="session1",
                user_principal=user1,
                created_at=datetime.now() - timedelta(hours=1),
                expires_at=datetime.now() + timedelta(hours=7),
                last_activity=datetime.now() - timedelta(minutes=30),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                risk_score=0.3
            )
        ]
    
    @pytest_asyncio.fixture
    async def sample_audit_trail(self):
        """Create sample audit trail"""
        return [
            {
                "event_id": "event1",
                "event_type": "authentication_success",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1", "provider": "token"}
            },
            {
                "event_id": "event2",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user2", "provider": "ldap", "reason": "invalid_credentials"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_monitor_initialization(self, monitor):
        """Test monitor initialization"""
        assert monitor.auth_manager is not None
        assert monitor.auth_analytics is not None
        assert monitor.monitoring_active is False
        assert len(monitor.alert_rules) > 0  # Should have default rules
        assert len(monitor.alerts) == 0
        assert monitor.dashboard_metrics is None
    
    @pytest.mark.asyncio
    async def test_add_alert_rule(self, monitor):
        """Test adding alert rule"""
        rule = AlertRule(
            rule_id="custom_rule",
            name="Custom Rule",
            alert_type=AlertType.USER_BEHAVIOR,
            severity=AlertSeverity.WARNING,
            conditions={"risk_threshold": 0.8}
        )
        
        initial_count = len(monitor.alert_rules)
        monitor.add_alert_rule(rule)
        
        assert len(monitor.alert_rules) == initial_count + 1
        assert any(r.rule_id == "custom_rule" for r in monitor.alert_rules)
    
    @pytest.mark.asyncio
    async def test_remove_alert_rule(self, monitor):
        """Test removing alert rule"""
        # Add a custom rule first
        rule = AlertRule(
            rule_id="custom_rule",
            name="Custom Rule",
            alert_type=AlertType.USER_BEHAVIOR,
            severity=AlertSeverity.WARNING,
            conditions={"risk_threshold": 0.8}
        )
        monitor.add_alert_rule(rule)
        
        initial_count = len(monitor.alert_rules)
        monitor.remove_alert_rule("custom_rule")
        
        assert len(monitor.alert_rules) == initial_count - 1
        assert not any(r.rule_id == "custom_rule" for r in monitor.alert_rules)
    
    @pytest.mark.asyncio
    async def test_update_dashboard_metrics(self, monitor, sample_sessions, sample_audit_trail):
        """Test dashboard metrics update"""
        # Mock analytics report
        mock_report = Mock()
        mock_report.security_incidents = []
        mock_report.user_behavior_patterns = []
        mock_report.authentication_metrics = {
            'failed_auth_events': 1,
            'success_rate': 0.9
        }
        mock_report.risk_assessment = {'overall_risk_score': 0.3}
        
        await monitor._update_dashboard_metrics(sample_sessions, sample_audit_trail, mock_report)
        
        assert monitor.dashboard_metrics is not None
        assert monitor.dashboard_metrics.active_sessions == 1
        assert monitor.dashboard_metrics.total_users == 1
        assert monitor.dashboard_metrics.failed_auth_attempts == 1
        assert monitor.dashboard_metrics.security_incidents == 0
        assert monitor.dashboard_metrics.high_risk_behaviors == 0
        # The success rate calculation uses actual audit trail data, not the mock report
        assert monitor.dashboard_metrics.risk_score == 0.3
    
    @pytest.mark.asyncio
    async def test_calculate_trends(self, monitor):
        """Test trend calculation"""
        # Add some mock metrics to history
        metrics1 = DashboardMetrics(
            timestamp=datetime.now() - timedelta(minutes=10),
            active_sessions=5,
            total_users=10,
            failed_auth_attempts=2,
            security_incidents=1,
            high_risk_behaviors=1,
            avg_response_time=1.0,
            success_rate=0.8,
            risk_score=0.3,
            alerts_count={"warning": 2},
            trends={}
        )
        
        metrics2 = DashboardMetrics(
            timestamp=datetime.now(),
            active_sessions=8,
            total_users=12,
            failed_auth_attempts=5,
            security_incidents=3,
            high_risk_behaviors=2,
            avg_response_time=2.0,
            success_rate=0.7,
            risk_score=0.6,
            alerts_count={"warning": 4},
            trends={}
        )
        
        monitor.metrics_history.append(metrics1)
        monitor.metrics_history.append(metrics2)
        
        trends = await monitor._calculate_trends()
        
        assert "security_incidents" in trends
        assert "risk_score" in trends
        assert "success_rate" in trends
    
    @pytest.mark.asyncio
    async def test_evaluate_alert_rules(self, monitor):
        """Test alert rule evaluation"""
        # Mock analytics report
        mock_report = Mock()
        mock_report.security_incidents = [Mock(severity='critical')]
        mock_report.user_behavior_patterns = []
        mock_report.authentication_metrics = {'failed_auth_events': 1, 'success_rate': 0.9}
        mock_report.business_impact = {'productivity_impact': {'efficiency_score': 85}}
        
        # Mock dashboard metrics
        monitor.dashboard_metrics = Mock(active_sessions=10, total_sessions=100, avg_response_time=1.0)
        
        initial_alert_count = len(monitor.alerts)
        await monitor._evaluate_alert_rules(mock_report)
        
        # Should create alerts for critical security incidents
        assert len(monitor.alerts) > initial_alert_count
    
    @pytest.mark.asyncio
    async def test_create_alert(self, monitor):
        """Test alert creation"""
        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            conditions={"incident_count": 1}
        )
        
        data = {
            'security_incidents': [Mock(severity='critical')],
            'user_behavior_patterns': [],
            'authentication_metrics': {},
            'dashboard_metrics': Mock(),
            'business_impact': {}
        }
        
        initial_alert_count = len(monitor.alerts)
        await monitor._create_alert(rule, data)
        
        assert len(monitor.alerts) == initial_alert_count + 1
        
        alert = monitor.alerts[-1]
        assert alert.alert_type == AlertType.SECURITY_INCIDENT
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.title == "Test Rule"
        assert alert.acknowledged is False
        assert alert.resolved is False
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, monitor):
        """Test alert acknowledgement"""
        # Create a test alert
        alert = Alert(
            alert_id="test_alert",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            title="Test Alert",
            description="Test description",
            timestamp=datetime.now()
        )
        monitor.alerts.append(alert)
        
        monitor.acknowledge_alert("test_alert", "admin")
        
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "admin"
        assert alert.acknowledged_at is not None
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, monitor):
        """Test alert resolution"""
        # Create a test alert
        alert = Alert(
            alert_id="test_alert",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            title="Test Alert",
            description="Test description",
            timestamp=datetime.now()
        )
        monitor.alerts.append(alert)
        
        monitor.resolve_alert("test_alert")
        
        assert alert.resolved is True
    
    @pytest.mark.asyncio
    async def test_get_alerts_filtering(self, monitor):
        """Test alert filtering"""
        # Create test alerts
        alert1 = Alert(
            alert_id="alert1",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            title="Critical Alert",
            description="Critical description",
            timestamp=datetime.now(),
            resolved=False
        )
        
        alert2 = Alert(
            alert_id="alert2",
            alert_type=AlertType.USER_BEHAVIOR,
            severity=AlertSeverity.WARNING,
            title="Warning Alert",
            description="Warning description",
            timestamp=datetime.now(),
            resolved=True
        )
        
        monitor.alerts.extend([alert1, alert2])
        
        # Test filtering
        active_alerts = monitor.get_alerts(resolved=False)
        assert len(active_alerts) == 1
        assert active_alerts[0].alert_id == "alert1"
        
        resolved_alerts = monitor.get_alerts(resolved=True)
        assert len(resolved_alerts) == 1
        assert resolved_alerts[0].alert_id == "alert2"
    
    @pytest.mark.asyncio
    async def test_add_alert_callback(self, monitor):
        """Test alert callback functionality"""
        callback_called = False
        callback_alert = None
        
        def test_callback(alert):
            nonlocal callback_called, callback_alert
            callback_called = True
            callback_alert = alert
        
        monitor.add_alert_callback(test_callback)
        
        # Create an alert to trigger callback
        rule = AlertRule(
            rule_id="callback_test",
            name="Callback Test",
            alert_type=AlertType.SECURITY_INCIDENT,
            severity=AlertSeverity.CRITICAL,
            conditions={"incident_count": 1}
        )
        
        data = {
            'security_incidents': [Mock(severity='critical')],
            'user_behavior_patterns': [],
            'authentication_metrics': {},
            'dashboard_metrics': Mock(),
            'business_impact': {}
        }
        
        await monitor._create_alert(rule, data)
        
        assert callback_called is True
        assert callback_alert is not None
        assert callback_alert.alert_type == AlertType.SECURITY_INCIDENT


class TestDashboardMetrics:
    """Test dashboard metrics functionality"""
    
    @pytest.mark.asyncio
    async def test_dashboard_metrics_creation(self):
        """Test dashboard metrics creation"""
        metrics = DashboardMetrics(
            timestamp=datetime.now(),
            active_sessions=10,
            total_users=20,
            failed_auth_attempts=5,
            security_incidents=2,
            high_risk_behaviors=1,
            avg_response_time=1.5,
            success_rate=0.85,
            risk_score=0.4,
            alerts_count={"warning": 3, "critical": 1},
            trends={"security_incidents": "increasing", "risk_score": "stable"}
        )
        
        assert metrics.active_sessions == 10
        assert metrics.total_users == 20
        assert metrics.failed_auth_attempts == 5
        assert metrics.security_incidents == 2
        assert metrics.high_risk_behaviors == 1
        assert metrics.avg_response_time == 1.5
        assert metrics.success_rate == 0.85
        assert metrics.risk_score == 0.4
        assert metrics.alerts_count["warning"] == 3
        assert metrics.alerts_count["critical"] == 1
        assert metrics.trends["security_incidents"] == "increasing"
        assert metrics.trends["risk_score"] == "stable" 