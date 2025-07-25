import pytest
import pyotp
from upid_python.core.enterprise_security import MultiFactorAuth, ComplianceFramework, SingleSignOn, SecurityMonitor
from datetime import datetime, timedelta
import os
from unittest.mock import patch
from upid_python.core.enterprise_security import ThreatDetection, AccessControl, SecurityAnalytics

def test_mfa_real():
    mfa = MultiFactorAuth()
    user = 'user1'
    uri = mfa.enable_mfa(user)
    assert uri.startswith('otpauth://totp/')
    secret = mfa.secrets[user]
    totp = pyotp.TOTP(secret)
    code = totp.now()
    assert mfa.verify_mfa(user, code)
    assert not mfa.verify_mfa(user, '000000')

def test_compliance_framework_real(tmp_path):
    log_path = tmp_path / 'audit_log.jsonl'
    cf = ComplianceFramework()
    cf.AUDIT_LOG = str(log_path)
    cf.record_action('user1', 'login', {'ip': '127.0.0.1'})
    cf.record_action('user2', 'logout', {'ip': '127.0.0.2'})
    all_entries = cf.get_audit_trail()
    assert len(all_entries) == 2
    user1_entries = cf.get_audit_trail('user1')
    assert len(user1_entries) == 1
    assert user1_entries[0]['action'] == 'login'

def test_security_monitor():
    monitor = SecurityMonitor()
    monitor.log_event({"type": "login_success", "user": "user1"})
    monitor.log_event({"type": "login_failed", "user": "user2"})
    alerts = monitor.get_alerts()
    assert len(alerts) == 1
    assert alerts[0]["alert"] == "Failed login detected"
    assert alerts[0]["event"]["user"] == "user2"

def test_sso_google_oauth2():
    sso = SingleSignOn()
    url = sso.initiate_sso("google", "user1")
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth")
    # Mock token and userinfo exchange
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post.return_value.json.return_value = {"access_token": "token123"}
        mock_post.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {"email": "user1@example.com"}
        mock_get.return_value.raise_for_status = lambda: None
        userinfo = sso.verify_sso("google", "dummy_code")
        assert userinfo["email"] == "user1@example.com"

def test_threat_detection():
    td = ThreatDetection()
    logs = [
        {"message": "User login successful", "user": "user1"},
        {"message": "failed_login attempt", "user": "user2"},  # Matches "failed_login" pattern
        {"message": "unusual_access pattern detected", "user": "user3"}  # Matches "unusual_access" pattern
    ]
    threats = td.detect_threats(logs)
    assert len(threats) == 2  # failed_login and unusual_access
    assert any(t["type"] == "failed_login" for t in threats)
    assert any(t["type"] == "unusual_access" for t in threats)

def test_access_control():
    ac = AccessControl()
    ac.set_permissions("user1", ["read", "write"])
    assert ac.check_permission("user1", "read")
    assert ac.check_permission("user1", "write")
    assert not ac.check_permission("user1", "delete")

    # Test role assignment
    assert ac.assign_role("user2", "admin")
    assert ac.check_permission("user2", "admin")
    assert not ac.assign_role("user3", "invalid_role")

def test_security_analytics():
    sa = SecurityAnalytics()
    # Add some test events
    sa.security_events = [
        {"type": "login_failed", "timestamp": datetime.utcnow()},
        {"type": "threat", "timestamp": datetime.utcnow()},
        {"type": "login_success", "timestamp": datetime.utcnow()}
    ]

    report = sa.generate_report(datetime.utcnow() - timedelta(days=1), datetime.utcnow())
    assert report["metrics"]["total_events"] == 3
    assert report["metrics"]["failed_logins"] == 1
    assert report["metrics"]["threats_detected"] == 1
    assert "risk_score" in report["metrics"]
    assert "recommendations" in report 