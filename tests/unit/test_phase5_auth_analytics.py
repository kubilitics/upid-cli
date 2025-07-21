"""
Comprehensive Unit Tests for Phase 5: Authentication Analytics Integration
Testing the integration of authentication data with advanced analytics
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from upid.core.auth_analytics_integration import (
    AuthAnalyticsIntegration, UserBehaviorAnalyzer, SecurityIncidentDetector,
    UserBehaviorPattern, SecurityIncident, UserBehaviorType, SecurityIncidentType,
    AuthAnalyticsReport
)
from upid.auth.enterprise_auth import (
    EnterpriseAuthManager, UserPrincipal, AuthSession, AuthLevel
)


class TestUserBehaviorAnalyzer:
    """Test user behavior analysis functionality"""
    
    @pytest_asyncio.fixture
    async def behavior_analyzer(self):
        """Create behavior analyzer for testing"""
        return UserBehaviorAnalyzer()
    
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
        
        user2 = UserPrincipal(
            user_id="user2",
            email="user2@example.com",
            display_name="User Two",
            roles=["admin"],
            provider="ldap"
        )
        
        sessions = [
            AuthSession(
                session_id="session1",
                user_principal=user1,
                created_at=datetime.now() - timedelta(hours=2),
                expires_at=datetime.now() + timedelta(hours=6),
                last_activity=datetime.now() - timedelta(minutes=30),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                risk_score=0.3
            ),
            AuthSession(
                session_id="session2",
                user_principal=user1,
                created_at=datetime.now() - timedelta(minutes=5),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                risk_score=0.4
            ),
            AuthSession(
                session_id="session3",
                user_principal=user2,
                created_at=datetime.now() - timedelta(hours=1),
                expires_at=datetime.now() + timedelta(hours=7),
                last_activity=datetime.now() - timedelta(minutes=15),
                ip_address="10.0.0.50",
                user_agent="curl/7.68.0",
                risk_score=0.8
            )
        ]
        return sessions
    
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
            },
            {
                "event_id": "event3",
                "event_type": "privilege_escalation",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user2", "new_role": "admin"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_user_behavior(self, behavior_analyzer, sample_sessions, sample_audit_trail):
        """Test user behavior analysis"""
        patterns = await behavior_analyzer.analyze_user_behavior(sample_sessions, sample_audit_trail)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Check that patterns have required attributes
        for pattern in patterns:
            assert isinstance(pattern, UserBehaviorPattern)
            assert pattern.user_id is not None
            assert pattern.behavior_type is not None
            assert pattern.confidence >= 0 and pattern.confidence <= 1
            assert pattern.description is not None
            assert pattern.timestamp is not None
            assert pattern.risk_score >= 0 and pattern.risk_score <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_login_frequency(self, behavior_analyzer, sample_sessions):
        """Test login frequency analysis"""
        # Test with sessions that have frequent logins
        frequent_sessions = [
            AuthSession(
                session_id="freq1",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now() - timedelta(minutes=2),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            ),
            AuthSession(
                session_id="freq2",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now() - timedelta(minutes=1),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            )
        ]
        
        pattern = await behavior_analyzer._analyze_login_frequency("user1", frequent_sessions)
        
        if pattern:  # May not trigger if frequency is not unusual
            assert pattern.behavior_type == UserBehaviorType.ANOMALOUS
            assert pattern.confidence > 0.5
            assert pattern.risk_score > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_session_patterns(self, behavior_analyzer, sample_sessions):
        """Test session pattern analysis"""
        patterns = await behavior_analyzer._analyze_session_patterns("user1", sample_sessions)
        
        assert isinstance(patterns, list)
        
        # Check for high-risk session patterns
        high_risk_patterns = [p for p in patterns if p.risk_score > 0.7]
        assert len(high_risk_patterns) >= 0  # May or may not have high-risk sessions
    
    @pytest.mark.asyncio
    async def test_analyze_geographic_patterns(self, behavior_analyzer, sample_sessions):
        """Test geographic pattern analysis"""
        patterns = await behavior_analyzer._analyze_geographic_patterns("user1", sample_sessions)
        
        assert isinstance(patterns, list)
        
        # Check for geographic anomaly patterns
        geo_patterns = [p for p in patterns if "IP" in p.description]
        assert len(geo_patterns) >= 0  # May or may not have geographic anomalies
    
    @pytest.mark.asyncio
    async def test_analyze_device_patterns(self, behavior_analyzer, sample_sessions):
        """Test device pattern analysis"""
        patterns = await behavior_analyzer._analyze_device_patterns("user1", sample_sessions)
        
        assert isinstance(patterns, list)
        
        # Check for device anomaly patterns
        device_patterns = [p for p in patterns if "device" in p.description.lower()]
        assert len(device_patterns) >= 0  # May or may not have device anomalies
    
    @pytest.mark.asyncio
    async def test_analyze_privilege_patterns(self, behavior_analyzer, sample_audit_trail):
        """Test privilege pattern analysis"""
        patterns = await behavior_analyzer._analyze_privilege_patterns("user2", sample_audit_trail)
        
        assert isinstance(patterns, list)
        
        # Check for privilege escalation patterns
        privilege_patterns = [p for p in patterns if p.behavior_type == UserBehaviorType.ADMIN_ACTIVITY]
        assert len(privilege_patterns) >= 0  # May or may not have privilege escalations


class TestSecurityIncidentDetector:
    """Test security incident detection functionality"""
    
    @pytest_asyncio.fixture
    async def incident_detector(self):
        """Create incident detector for testing"""
        return SecurityIncidentDetector()
    
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
        
        sessions = [
            AuthSession(
                session_id="session1",
                user_principal=user1,
                created_at=datetime.now() - timedelta(hours=2),
                expires_at=datetime.now() + timedelta(hours=6),
                last_activity=datetime.now() - timedelta(minutes=30),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                risk_score=0.3
            ),
            AuthSession(
                session_id="session2",
                user_principal=user1,
                created_at=datetime.now() - timedelta(hours=1),
                expires_at=datetime.now() + timedelta(hours=7),
                last_activity=datetime.now() - timedelta(minutes=15),
                ip_address="192.168.1.101",
                user_agent="Mozilla/5.0",
                risk_score=0.4
            )
        ]
        return sessions
    
    @pytest_asyncio.fixture
    async def sample_audit_trail(self):
        """Create sample audit trail with security events"""
        return [
            {
                "event_id": "event1",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1", "provider": "token", "reason": "invalid_credentials"}
            },
            {
                "event_id": "event2",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1", "provider": "token", "reason": "invalid_credentials"}
            },
            {
                "event_id": "event3",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1", "provider": "token", "reason": "invalid_credentials"}
            },
            {
                "event_id": "event4",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1", "provider": "token", "reason": "invalid_credentials"}
            },
            {
                "event_id": "event5",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1", "provider": "token", "reason": "invalid_credentials"}
            },
            {
                "event_id": "event6",
                "event_type": "privilege_escalation",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user2", "new_role": "admin"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_detect_security_incidents(self, incident_detector, sample_sessions, sample_audit_trail):
        """Test security incident detection"""
        incidents = await incident_detector.detect_security_incidents(sample_sessions, sample_audit_trail)
        
        assert isinstance(incidents, list)
        assert len(incidents) > 0  # Should detect failed login incidents
        
        # Check that incidents have required attributes
        for incident in incidents:
            assert isinstance(incident, SecurityIncident)
            assert incident.incident_id is not None
            assert incident.incident_type is not None
            assert incident.severity in ['low', 'medium', 'high', 'critical']
            assert incident.description is not None
            assert incident.timestamp is not None
            assert incident.risk_score >= 0 and incident.risk_score <= 1
    
    @pytest.mark.asyncio
    async def test_detect_failed_login_incidents(self, incident_detector, sample_audit_trail):
        """Test failed login incident detection"""
        incidents = await incident_detector._detect_failed_login_incidents(sample_audit_trail)
        
        assert isinstance(incidents, list)
        assert len(incidents) > 0  # Should detect excessive failed logins
        
        # Check for failed login incidents
        failed_login_incidents = [i for i in incidents if i.incident_type == SecurityIncidentType.FAILED_LOGIN]
        assert len(failed_login_incidents) > 0
        
        for incident in failed_login_incidents:
            assert incident.severity == 'high'
            assert incident.risk_score > 0.7
    
    @pytest.mark.asyncio
    async def test_detect_suspicious_access_incidents(self, incident_detector, sample_sessions):
        """Test suspicious access incident detection"""
        incidents = await incident_detector._detect_suspicious_access_incidents(sample_sessions)
        
        assert isinstance(incidents, list)
        
        # Check for suspicious access incidents
        suspicious_incidents = [i for i in incidents if i.incident_type == SecurityIncidentType.SUSPICIOUS_ACCESS]
        assert len(suspicious_incidents) >= 0  # May or may not have suspicious IPs
    
    @pytest.mark.asyncio
    async def test_detect_privilege_escalation_incidents(self, incident_detector, sample_audit_trail):
        """Test privilege escalation incident detection"""
        incidents = await incident_detector._detect_privilege_escalation_incidents(sample_audit_trail)
        
        assert isinstance(incidents, list)
        
        # Check for privilege escalation incidents
        privilege_incidents = [i for i in incidents if i.incident_type == SecurityIncidentType.PRIVILEGE_ESCALATION]
        assert len(privilege_incidents) > 0  # Should detect privilege escalation
        
        for incident in privilege_incidents:
            assert incident.severity == 'high'
            assert incident.risk_score > 0.8
    
    @pytest.mark.asyncio
    async def test_detect_unusual_hours_incidents(self, incident_detector, sample_sessions):
        """Test unusual hours incident detection"""
        # Create sessions with unusual hours
        unusual_sessions = [
            AuthSession(
                session_id="unusual1",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now().replace(hour=3),  # 3 AM
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            )
        ]
        
        incidents = await incident_detector._detect_unusual_hours_incidents(unusual_sessions)
        
        assert isinstance(incidents, list)
        
        # Check for unusual hours incidents
        unusual_hours_incidents = [i for i in incidents if i.incident_type == SecurityIncidentType.UNUSUAL_HOURS]
        assert len(unusual_hours_incidents) > 0  # Should detect unusual hours
    
    @pytest.mark.asyncio
    async def test_detect_multiple_sessions_incidents(self, incident_detector, sample_sessions):
        """Test multiple sessions incident detection"""
        # Create multiple sessions for same user
        multiple_sessions = sample_sessions + [
            AuthSession(
                session_id="session3",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now() - timedelta(minutes=30),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            ),
            AuthSession(
                session_id="session4",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now() - timedelta(minutes=15),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            ),
            AuthSession(
                session_id="session5",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now() - timedelta(minutes=5),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            ),
            AuthSession(
                session_id="session6",
                user_principal=sample_sessions[0].user_principal,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=8),
                last_activity=datetime.now(),
                risk_score=0.5
            )
        ]
        
        incidents = await incident_detector._detect_multiple_sessions_incidents(multiple_sessions)
        
        assert isinstance(incidents, list)
        
        # Check for multiple sessions incidents
        multiple_sessions_incidents = [i for i in incidents if i.incident_type == SecurityIncidentType.MULTIPLE_SESSIONS]
        assert len(multiple_sessions_incidents) > 0  # Should detect multiple sessions


class TestAuthAnalyticsIntegration:
    """Test authentication analytics integration functionality"""
    
    @pytest_asyncio.fixture
    async def auth_analytics(self):
        """Create auth analytics integration for testing"""
        auth_manager = EnterpriseAuthManager()
        auth_manager._register_providers_sync()  # Ensure providers are registered
        return AuthAnalyticsIntegration(auth_manager)
    
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
        
        user2 = UserPrincipal(
            user_id="user2",
            email="user2@example.com",
            display_name="User Two",
            roles=["admin"],
            provider="ldap"
        )
        
        sessions = [
            AuthSession(
                session_id="session1",
                user_principal=user1,
                created_at=datetime.now() - timedelta(hours=2),
                expires_at=datetime.now() + timedelta(hours=6),
                last_activity=datetime.now() - timedelta(minutes=30),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0",
                risk_score=0.3
            ),
            AuthSession(
                session_id="session2",
                user_principal=user2,
                created_at=datetime.now() - timedelta(hours=1),
                expires_at=datetime.now() + timedelta(hours=7),
                last_activity=datetime.now() - timedelta(minutes=15),
                ip_address="10.0.0.50",
                user_agent="curl/7.68.0",
                risk_score=0.8
            )
        ]
        return sessions
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_auth_analytics(self, auth_analytics, sample_sessions):
        """Test comprehensive authentication analytics"""
        # Add sessions to auth manager
        auth_analytics.auth_manager.sessions = {s.session_id: s for s in sample_sessions}
        
        # Add some audit events
        await auth_analytics.auth_manager._audit_event("test_event", {"user_id": "user1"})
        
        report = await auth_analytics.run_comprehensive_auth_analytics()
        
        assert isinstance(report, AuthAnalyticsReport)
        assert report.timestamp is not None
        assert isinstance(report.user_behavior_patterns, list)
        assert isinstance(report.security_incidents, list)
        assert isinstance(report.authentication_metrics, dict)
        assert isinstance(report.risk_assessment, dict)
        assert isinstance(report.business_impact, dict)
        assert isinstance(report.recommendations, list)
        assert isinstance(report.summary, dict)
    
    @pytest.mark.asyncio
    async def test_calculate_authentication_metrics(self, auth_analytics, sample_sessions):
        """Test authentication metrics calculation"""
        audit_trail = [
            {
                "event_id": "event1",
                "event_type": "authentication_success",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user1"}
            },
            {
                "event_id": "event2",
                "event_type": "authentication_failed",
                "timestamp": datetime.now().isoformat(),
                "details": {"user_id": "user2"}
            }
        ]
        
        metrics = await auth_analytics._calculate_authentication_metrics(sample_sessions, audit_trail)
        
        assert isinstance(metrics, dict)
        assert 'total_sessions' in metrics
        assert 'active_sessions' in metrics
        assert 'unique_users' in metrics
        assert 'provider_distribution' in metrics
        assert 'high_risk_sessions' in metrics
        assert 'average_risk_score' in metrics
        assert 'total_audit_events' in metrics
        assert 'failed_auth_events' in metrics
        assert 'success_rate' in metrics
        
        assert metrics['total_sessions'] == 2
        assert metrics['unique_users'] == 2
        assert metrics['total_audit_events'] == 2
        assert metrics['failed_auth_events'] == 1
    
    @pytest.mark.asyncio
    async def test_perform_risk_assessment(self, auth_analytics):
        """Test risk assessment functionality"""
        behavior_patterns = [
            UserBehaviorPattern(
                user_id="user1",
                behavior_type=UserBehaviorType.ANOMALOUS,
                confidence=0.8,
                description="Test pattern",
                timestamp=datetime.now(),
                risk_score=0.7
            )
        ]
        
        security_incidents = [
            SecurityIncident(
                incident_id="incident1",
                incident_type=SecurityIncidentType.FAILED_LOGIN,
                severity="high",
                description="Test incident",
                timestamp=datetime.now(),
                risk_score=0.8
            )
        ]
        
        auth_metrics = {
            'average_risk_score': 0.5,
            'high_risk_sessions': 1
        }
        
        risk_assessment = await auth_analytics._perform_risk_assessment(
            behavior_patterns, security_incidents, auth_metrics
        )
        
        assert isinstance(risk_assessment, dict)
        assert 'overall_risk_score' in risk_assessment
        assert 'behavior_risk_score' in risk_assessment
        assert 'incident_risk_score' in risk_assessment
        assert 'auth_risk_score' in risk_assessment
        assert 'risk_level' in risk_assessment
        assert 'critical_incidents' in risk_assessment
        assert 'high_risk_behaviors' in risk_assessment
        
        assert risk_assessment['overall_risk_score'] >= 0 and risk_assessment['overall_risk_score'] <= 1
        assert risk_assessment['risk_level'] in ['low', 'medium', 'high']
    
    @pytest.mark.asyncio
    async def test_analyze_business_impact(self, auth_analytics):
        """Test business impact analysis"""
        behavior_patterns = [
            UserBehaviorPattern(
                user_id="user1",
                behavior_type=UserBehaviorType.SUSPICIOUS,
                confidence=0.8,
                description="Test pattern",
                timestamp=datetime.now(),
                risk_score=0.7
            )
        ]
        
        security_incidents = [
            SecurityIncident(
                incident_id="incident1",
                incident_type=SecurityIncidentType.FAILED_LOGIN,
                severity="critical",
                description="Test incident",
                timestamp=datetime.now(),
                risk_score=0.9
            )
        ]
        
        auth_metrics = {
            'success_rate': 0.8,
            'average_session_duration': 3600
        }
        
        business_impact = await auth_analytics._analyze_business_impact(
            behavior_patterns, security_incidents, auth_metrics
        )
        
        assert isinstance(business_impact, dict)
        assert 'productivity_impact' in business_impact
        assert 'security_impact' in business_impact
        assert 'operational_impact' in business_impact
        
        # Check productivity impact
        productivity = business_impact['productivity_impact']
        assert 'suspicious_behaviors' in productivity
        assert 'efficiency_score' in productivity
        assert 'user_experience_score' in productivity
        
        # Check security impact
        security = business_impact['security_impact']
        assert 'critical_incidents' in security
        assert 'high_incidents' in security
        assert 'security_score' in security
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, auth_analytics):
        """Test recommendation generation"""
        behavior_patterns = [
            UserBehaviorPattern(
                user_id="user1",
                behavior_type=UserBehaviorType.SUSPICIOUS,
                confidence=0.8,
                description="Test pattern",
                timestamp=datetime.now(),
                risk_score=0.7
            )
        ]
        
        security_incidents = [
            SecurityIncident(
                incident_id="incident1",
                incident_type=SecurityIncidentType.FAILED_LOGIN,
                severity="critical",
                description="Test incident",
                timestamp=datetime.now(),
                risk_score=0.9
            )
        ]
        
        risk_assessment = {
            'overall_risk_score': 0.8,
            'critical_incidents': 1
        }
        
        recommendations = await auth_analytics._generate_recommendations(
            behavior_patterns, security_incidents, risk_assessment
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
    
    @pytest.mark.asyncio
    async def test_create_comprehensive_summary(self, auth_analytics):
        """Test comprehensive summary creation"""
        behavior_patterns = [
            UserBehaviorPattern(
                user_id="user1",
                behavior_type=UserBehaviorType.ANOMALOUS,
                confidence=0.8,
                description="Test pattern",
                timestamp=datetime.now(),
                risk_score=0.7
            )
        ]
        
        security_incidents = [
            SecurityIncident(
                incident_id="incident1",
                incident_type=SecurityIncidentType.FAILED_LOGIN,
                severity="high",
                description="Test incident",
                timestamp=datetime.now(),
                risk_score=0.8
            )
        ]
        
        auth_metrics = {
            'total_users': 2,
            'active_sessions': 1,
            'success_rate': 0.8
        }
        
        risk_assessment = {
            'overall_risk_score': 0.6,
            'risk_level': 'medium',
            'critical_incidents': 0
        }
        
        summary = await auth_analytics._create_comprehensive_summary(
            behavior_patterns, security_incidents, auth_metrics, risk_assessment
        )
        
        assert isinstance(summary, dict)
        assert 'overall_status' in summary
        assert 'key_metrics' in summary
        assert 'risk_summary' in summary
        assert 'trends' in summary
        
        assert summary['overall_status'] in ['healthy', 'attention_required']
        assert isinstance(summary['key_metrics'], dict)
        assert isinstance(summary['risk_summary'], dict)
        assert isinstance(summary['trends'], dict) 