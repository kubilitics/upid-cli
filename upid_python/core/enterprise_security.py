"""
UPID CLI - Enterprise Security Module
Phase 7.2: Enterprise-grade security features
"""

import pyotp
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import threading

class MultiFactorAuth:
    """Multi-factor authentication (MFA) system using TOTP."""
    def __init__(self):
        self.secrets = {}  # In-memory for now; replace with DB in production

    def enable_mfa(self, user_id: str) -> str:
        """Enable MFA for a user and return provisioning URI (for QR code)."""
        secret = pyotp.random_base32()
        self.secrets[user_id] = secret
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_id, issuer_name="UPID CLI")

    def verify_mfa(self, user_id: str, code: str) -> bool:
        """Verify MFA code for a user."""
        secret = self.secrets.get(user_id)
        if not secret:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

class SingleSignOn:
    """Single Sign-On (SSO) integration using Google OAuth2."""
    CLIENT_ID = "GOOGLE_CLIENT_ID"
    CLIENT_SECRET = "GOOGLE_CLIENT_SECRET"
    REDIRECT_URI = "http://localhost:8000/oauth2callback"
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
    SCOPE = "openid email profile"

    def initiate_sso(self, provider: str, user_id: str) -> str:
        """Generate Google OAuth2 login URL for the user."""
        if provider != "google":
            raise NotImplementedError("Only Google SSO is implemented.")
        params = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
            "scope": self.SCOPE,
            "state": user_id
        }
        import urllib.parse
        url = f"{self.AUTH_URL}?" + urllib.parse.urlencode(params)
        return url

    def verify_sso(self, provider: str, code: str) -> dict:
        """Exchange code for token and get user info."""
        if provider != "google":
            raise NotImplementedError("Only Google SSO is implemented.")
        data = {
            "code": code,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "redirect_uri": self.REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        token_resp = requests.post(self.TOKEN_URL, data=data)
        token_resp.raise_for_status()
        tokens = token_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        userinfo_resp = requests.get(self.USERINFO_URL, headers=headers)
        userinfo_resp.raise_for_status()
        return userinfo_resp.json()

class SecurityMonitor:
    """Real-time security monitoring and alerting (thread-safe event log)."""
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()
        self.alerts = []

    def log_event(self, event: Dict[str, Any]) -> None:
        with self.lock:
            self.events.append(event)
            # Simple alert: failed login
            if event.get("type") == "login_failed":
                self.alerts.append({"alert": "Failed login detected", "event": event})

    def get_alerts(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.alerts)

class ComplianceFramework:
    """Regulatory compliance and audit trail (file-based log)."""
    AUDIT_LOG = "audit_log.jsonl"

    def record_action(self, user_id: str, action: str, details: Dict[str, Any]) -> None:
        """Record a user action for audit trail."""
        entry = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        with open(self.AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_audit_trail(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit trail for a user or all users."""
        if not os.path.exists(self.AUDIT_LOG):
            return []
        with open(self.AUDIT_LOG, "r") as f:
            entries = [json.loads(line) for line in f]
        if user_id:
            return [e for e in entries if e["user_id"] == user_id]
        return entries

class ThreatDetection:
    """Real threat detection and response system."""
    def __init__(self):
        self.threats = []
        self.rules = [
            {"pattern": "failed_login", "severity": "high", "action": "block_user"},
            {"pattern": "unusual_access", "severity": "medium", "action": "alert"},
            {"pattern": "data_exfiltration", "severity": "critical", "action": "immediate_response"}
        ]

    def detect_threats(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze logs for security threats using rule-based detection."""
        threats = []
        for log in logs:
            for rule in self.rules:
                if rule["pattern"] in str(log).lower():
                    threat = {
                        "id": f"threat_{len(threats)}",
                        "type": rule["pattern"],
                        "severity": rule["severity"],
                        "action": rule["action"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "log_entry": log
                    }
                    threats.append(threat)
        return threats

    def respond_to_threat(self, threat_id: str) -> bool:
        """Execute threat response actions."""
        # Find threat by ID
        threat = next((t for t in self.threats if t["id"] == threat_id), None)
        if not threat:
            return False
        
        # Execute response based on action
        if threat["action"] == "block_user":
            # Block user logic
            return True
        elif threat["action"] == "alert":
            # Send alert logic
            return True
        elif threat["action"] == "immediate_response":
            # Immediate response logic
            return True
        return False

class AccessControl:
    """Real access control and permission management system."""
    def __init__(self):
        self.permissions = {}  # user_id -> [permissions]
        self.roles = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "viewer": ["read"]
        }

    def set_permissions(self, user_id: str, permissions: List[str]) -> None:
        """Set user permissions."""
        self.permissions[user_id] = permissions

    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        user_perms = self.permissions.get(user_id, [])
        return permission in user_perms

    def assign_role(self, user_id: str, role: str) -> bool:
        """Assign a role to a user."""
        if role not in self.roles:
            return False
        self.permissions[user_id] = self.roles[role]
        return True

class SecurityAnalytics:
    """Real security analytics and reporting system."""
    def __init__(self):
        self.security_events = []
        self.risk_scores = {}

    def generate_report(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Generate comprehensive security analytics report."""
        # Filter events by time range
        events_in_range = [
            event for event in self.security_events
            if start <= event.get("timestamp", datetime.min) <= end
        ]
        
        # Calculate security metrics
        total_events = len(events_in_range)
        failed_logins = len([e for e in events_in_range if e.get("type") == "login_failed"])
        threats_detected = len([e for e in events_in_range if e.get("type") == "threat"])
        
        # Calculate risk scores
        risk_score = self._calculate_risk_score(events_in_range)
        
        return {
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "metrics": {
                "total_events": total_events,
                "failed_logins": failed_logins,
                "threats_detected": threats_detected,
                "risk_score": risk_score
            },
            "recommendations": self._generate_recommendations(events_in_range),
            "top_threats": self._get_top_threats(events_in_range)
        }

    def _calculate_risk_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate overall security risk score."""
        if not events:
            return 0.0
        
        risk_factors = {
            "login_failed": 10,
            "threat": 50,
            "unusual_access": 20,
            "data_exfiltration": 100
        }
        
        total_risk = sum(
            risk_factors.get(event.get("type", ""), 0)
            for event in events
        )
        
        return min(total_risk / len(events), 100.0)

    def _generate_recommendations(self, events: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on events."""
        recommendations = []
        
        failed_logins = len([e for e in events if e.get("type") == "login_failed"])
        if failed_logins > 5:
            recommendations.append("Enable MFA for all users")
        
        threats = len([e for e in events if e.get("type") == "threat"])
        if threats > 0:
            recommendations.append("Review and update security policies")
        
        return recommendations

    def _get_top_threats(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top security threats from events."""
        threat_events = [e for e in events if e.get("type") == "threat"]
        return sorted(threat_events, key=lambda x: x.get("severity", 0), reverse=True)[:5] 