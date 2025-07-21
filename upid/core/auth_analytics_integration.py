"""
Phase 5: Advanced Analytics Integration
Integrates authentication data with advanced analytics for comprehensive intelligence
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict

from ..auth.enterprise_auth import (
    EnterpriseAuthManager, UserPrincipal, AuthSession, 
    AuthLevel, AuthProviderType
)
from .intelligence import IntelligenceEngine
from .advanced_analytics import AdvancedAnalyticsEngine
from .business_intelligence import BusinessIntelligenceEngine, BusinessKPI
from .predictive_analytics import PredictiveAnalyticsEngine

logger = logging.getLogger(__name__)


class UserBehaviorType(Enum):
    """Types of user behavior patterns"""
    NORMAL = "normal"
    ANOMALOUS = "anomalous"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    ADMIN_ACTIVITY = "admin_activity"
    BULK_OPERATIONS = "bulk_operations"


class SecurityIncidentType(Enum):
    """Types of security incidents"""
    FAILED_LOGIN = "failed_login"
    SUSPICIOUS_ACCESS = "suspicious_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNUSUAL_HOURS = "unusual_hours"
    MULTIPLE_SESSIONS = "multiple_sessions"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    DEVICE_ANOMALY = "device_anomaly"


@dataclass
class UserBehaviorPattern:
    """Represents a user behavior pattern"""
    user_id: str
    behavior_type: UserBehaviorType
    confidence: float
    description: str
    timestamp: datetime
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityIncident:
    """Represents a security incident"""
    incident_id: str
    incident_type: SecurityIncidentType
    severity: str  # low, medium, high, critical
    description: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    risk_score: float = 0.0
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthAnalyticsReport:
    """Comprehensive authentication analytics report"""
    timestamp: datetime
    user_behavior_patterns: List[UserBehaviorPattern]
    security_incidents: List[SecurityIncident]
    authentication_metrics: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    business_impact: Dict[str, Any]
    recommendations: List[str]
    summary: Dict[str, Any]


class UserBehaviorAnalyzer:
    """
    Analyzes user behavior patterns from authentication data
    """
    
    def __init__(self):
        self.behavior_baselines = {}
        self.anomaly_thresholds = {
            'login_frequency': 10,  # logins per hour
            'session_duration': 3600,  # seconds
            'geographic_distance': 1000,  # km
            'device_changes': 3,  # device changes per day
            'privilege_escalation': 1  # privilege changes per day
        }
    
    async def analyze_user_behavior(
        self, 
        auth_sessions: List[AuthSession],
        audit_trail: List[Dict[str, Any]]
    ) -> List[UserBehaviorPattern]:
        """
        Analyze user behavior patterns from authentication data
        
        Args:
            auth_sessions: List of authentication sessions
            audit_trail: Authentication audit trail
            
        Returns:
            List of user behavior patterns
        """
        logger.info("Analyzing user behavior patterns")
        
        patterns = []
        
        # Group sessions by user
        user_sessions = defaultdict(list)
        for session in auth_sessions:
            user_sessions[session.user_principal.user_id].append(session)
        
        # Analyze each user's behavior
        for user_id, sessions in user_sessions.items():
            user_patterns = await self._analyze_user_patterns(user_id, sessions, audit_trail)
            patterns.extend(user_patterns)
        
        logger.info(f"Identified {len(patterns)} user behavior patterns")
        return patterns
    
    async def _analyze_user_patterns(
        self, 
        user_id: str, 
        sessions: List[AuthSession],
        audit_trail: List[Dict[str, Any]]
    ) -> List[UserBehaviorPattern]:
        """Analyze patterns for a specific user"""
        patterns = []
        
        # Analyze login frequency
        login_frequency = await self._analyze_login_frequency(user_id, sessions)
        if login_frequency:
            patterns.append(login_frequency)
        
        # Analyze session duration patterns
        session_patterns = await self._analyze_session_patterns(user_id, sessions)
        patterns.extend(session_patterns)
        
        # Analyze geographic patterns
        geo_patterns = await self._analyze_geographic_patterns(user_id, sessions)
        patterns.extend(geo_patterns)
        
        # Analyze device patterns
        device_patterns = await self._analyze_device_patterns(user_id, sessions)
        patterns.extend(device_patterns)
        
        # Analyze privilege patterns
        privilege_patterns = await self._analyze_privilege_patterns(user_id, audit_trail)
        patterns.extend(privilege_patterns)
        
        return patterns
    
    async def _analyze_login_frequency(
        self, 
        user_id: str, 
        sessions: List[AuthSession]
    ) -> Optional[UserBehaviorPattern]:
        """Analyze login frequency patterns"""
        if len(sessions) < 2:
            return None
        
        # Calculate login frequency
        session_times = [s.created_at for s in sessions]
        session_times.sort()
        
        # Calculate time differences between logins
        time_diffs = []
        for i in range(1, len(session_times)):
            diff = (session_times[i] - session_times[i-1]).total_seconds() / 3600  # hours
            time_diffs.append(diff)
        
        avg_frequency = np.mean(time_diffs) if time_diffs else 0
        
        # Check for unusual frequency
        if avg_frequency < 0.1:  # Less than 6 minutes between logins
            return UserBehaviorPattern(
                user_id=user_id,
                behavior_type=UserBehaviorType.ANOMALOUS,
                confidence=0.8,
                description=f"Unusual login frequency: {avg_frequency:.2f} hours between logins",
                timestamp=datetime.now(),
                risk_score=0.7,
                metadata={'avg_frequency': avg_frequency, 'total_logins': len(sessions)}
            )
        
        return None
    
    async def _analyze_session_patterns(
        self, 
        user_id: str, 
        sessions: List[AuthSession]
    ) -> List[UserBehaviorPattern]:
        """Analyze session duration and activity patterns"""
        patterns = []
        
        for session in sessions:
            session_duration = (session.expires_at - session.created_at).total_seconds()
            
            # Check for unusually long sessions
            if session_duration > 86400:  # More than 24 hours
                patterns.append(UserBehaviorPattern(
                    user_id=user_id,
                    behavior_type=UserBehaviorType.ANOMALOUS,
                    confidence=0.6,
                    description=f"Unusually long session: {session_duration/3600:.1f} hours",
                    timestamp=session.created_at,
                    session_id=session.session_id,
                    risk_score=0.5,
                    metadata={'session_duration': session_duration}
                ))
            
            # Check for high-risk sessions
            if session.risk_score > 0.8:
                patterns.append(UserBehaviorPattern(
                    user_id=user_id,
                    behavior_type=UserBehaviorType.SUSPICIOUS,
                    confidence=0.9,
                    description=f"High-risk session detected (risk score: {session.risk_score:.2f})",
                    timestamp=session.created_at,
                    session_id=session.session_id,
                    risk_score=session.risk_score,
                    metadata={'session_risk_score': session.risk_score}
                ))
        
        return patterns
    
    async def _analyze_geographic_patterns(
        self, 
        user_id: str, 
        sessions: List[AuthSession]
    ) -> List[UserBehaviorPattern]:
        """Analyze geographic access patterns"""
        patterns = []
        
        # Group sessions by IP address
        ip_sessions = defaultdict(list)
        for session in sessions:
            if session.ip_address:
                ip_sessions[session.ip_address].append(session)
        
        # Check for geographic anomalies
        if len(ip_sessions) > 3:  # Multiple IP addresses
            patterns.append(UserBehaviorPattern(
                user_id=user_id,
                behavior_type=UserBehaviorType.ANOMALOUS,
                confidence=0.7,
                description=f"Multiple IP addresses detected: {len(ip_sessions)} different IPs",
                timestamp=datetime.now(),
                risk_score=0.6,
                metadata={'unique_ips': len(ip_sessions), 'ips': list(ip_sessions.keys())}
            ))
        
        return patterns
    
    async def _analyze_device_patterns(
        self, 
        user_id: str, 
        sessions: List[AuthSession]
    ) -> List[UserBehaviorPattern]:
        """Analyze device usage patterns"""
        patterns = []
        
        # Group sessions by device
        device_sessions = defaultdict(list)
        for session in sessions:
            device_id = session.device_id or session.user_agent or "unknown"
            device_sessions[device_id].append(session)
        
        # Check for device anomalies
        if len(device_sessions) > 2:  # Multiple devices
            patterns.append(UserBehaviorPattern(
                user_id=user_id,
                behavior_type=UserBehaviorType.ANOMALOUS,
                confidence=0.6,
                description=f"Multiple devices detected: {len(device_sessions)} different devices",
                timestamp=datetime.now(),
                risk_score=0.5,
                metadata={'unique_devices': len(device_sessions)}
            ))
        
        return patterns
    
    async def _analyze_privilege_patterns(
        self, 
        user_id: str, 
        audit_trail: List[Dict[str, Any]]
    ) -> List[UserBehaviorPattern]:
        """Analyze privilege escalation patterns"""
        patterns = []
        
        # Filter audit trail for this user
        user_events = [event for event in audit_trail 
                      if event.get('details', {}).get('user_id') == user_id]
        
        # Check for privilege escalation events
        privilege_events = [event for event in user_events 
                          if 'privilege' in event.get('event_type', '').lower()]
        
        if len(privilege_events) > 0:
            patterns.append(UserBehaviorPattern(
                user_id=user_id,
                behavior_type=UserBehaviorType.ADMIN_ACTIVITY,
                confidence=0.8,
                description=f"Privilege escalation detected: {len(privilege_events)} events",
                timestamp=datetime.now(),
                risk_score=0.7,
                metadata={'privilege_events': len(privilege_events)}
            ))
        
        return patterns


class SecurityIncidentDetector:
    """
    Detects security incidents from authentication data
    """
    
    def __init__(self):
        self.incident_thresholds = {
            'failed_logins': 5,  # failed logins per hour
            'suspicious_ips': 3,  # suspicious IPs per day
            'unusual_hours': 2,  # logins outside business hours
            'multiple_sessions': 5,  # concurrent sessions per user
            'geographic_distance': 1000  # km between logins
        }
    
    async def detect_security_incidents(
        self, 
        auth_sessions: List[AuthSession],
        audit_trail: List[Dict[str, Any]]
    ) -> List[SecurityIncident]:
        """
        Detect security incidents from authentication data
        
        Args:
            auth_sessions: List of authentication sessions
            audit_trail: Authentication audit trail
            
        Returns:
            List of security incidents
        """
        logger.info("Detecting security incidents")
        
        incidents = []
        
        # Detect failed login incidents
        failed_login_incidents = await self._detect_failed_login_incidents(audit_trail)
        incidents.extend(failed_login_incidents)
        
        # Detect suspicious access incidents
        suspicious_access_incidents = await self._detect_suspicious_access_incidents(auth_sessions)
        incidents.extend(suspicious_access_incidents)
        
        # Detect privilege escalation incidents
        privilege_incidents = await self._detect_privilege_escalation_incidents(audit_trail)
        incidents.extend(privilege_incidents)
        
        # Detect unusual hours incidents
        unusual_hours_incidents = await self._detect_unusual_hours_incidents(auth_sessions)
        incidents.extend(unusual_hours_incidents)
        
        # Detect multiple sessions incidents
        multiple_sessions_incidents = await self._detect_multiple_sessions_incidents(auth_sessions)
        incidents.extend(multiple_sessions_incidents)
        
        logger.info(f"Detected {len(incidents)} security incidents")
        return incidents
    
    async def _detect_failed_login_incidents(
        self, 
        audit_trail: List[Dict[str, Any]]
    ) -> List[SecurityIncident]:
        """Detect failed login incidents"""
        incidents = []
        
        # Group failed login events by user and time
        failed_logins = defaultdict(list)
        for event in audit_trail:
            if event.get('event_type') == 'authentication_failed':
                user_id = event.get('details', {}).get('user_id', 'unknown')
                timestamp = datetime.fromisoformat(event.get('timestamp', ''))
                failed_logins[user_id].append(timestamp)
        
        # Check for excessive failed logins
        for user_id, timestamps in failed_logins.items():
            if len(timestamps) >= self.incident_thresholds['failed_logins']:
                incidents.append(SecurityIncident(
                    incident_id=f"failed_login_{user_id}_{datetime.now().timestamp()}",
                    incident_type=SecurityIncidentType.FAILED_LOGIN,
                    severity='high',
                    description=f"Excessive failed logins for user {user_id}: {len(timestamps)} attempts",
                    timestamp=datetime.now(),
                    user_id=user_id,
                    risk_score=0.8,
                    metadata={'failed_attempts': len(timestamps)}
                ))
        
        return incidents
    
    async def _detect_suspicious_access_incidents(
        self, 
        auth_sessions: List[AuthSession]
    ) -> List[SecurityIncident]:
        """Detect suspicious access incidents"""
        incidents = []
        
        # Group sessions by IP address
        ip_sessions = defaultdict(list)
        for session in auth_sessions:
            if session.ip_address:
                ip_sessions[session.ip_address].append(session)
        
        # Check for suspicious IP patterns
        for ip_address, sessions in ip_sessions.items():
            if len(sessions) > self.incident_thresholds['suspicious_ips']:
                incidents.append(SecurityIncident(
                    incident_id=f"suspicious_ip_{ip_address}_{datetime.now().timestamp()}",
                    incident_type=SecurityIncidentType.SUSPICIOUS_ACCESS,
                    severity='medium',
                    description=f"Suspicious IP address {ip_address}: {len(sessions)} sessions",
                    timestamp=datetime.now(),
                    ip_address=ip_address,
                    risk_score=0.6,
                    metadata={'session_count': len(sessions), 'ip_address': ip_address}
                ))
        
        return incidents
    
    async def _detect_privilege_escalation_incidents(
        self, 
        audit_trail: List[Dict[str, Any]]
    ) -> List[SecurityIncident]:
        """Detect privilege escalation incidents"""
        incidents = []
        
        # Look for privilege escalation events
        privilege_events = [event for event in audit_trail 
                          if 'privilege' in event.get('event_type', '').lower()]
        
        for event in privilege_events:
            incidents.append(SecurityIncident(
                incident_id=f"privilege_escalation_{datetime.now().timestamp()}",
                incident_type=SecurityIncidentType.PRIVILEGE_ESCALATION,
                severity='high',
                description=f"Privilege escalation detected: {event.get('event_type')}",
                timestamp=datetime.fromisoformat(event.get('timestamp', '')),
                user_id=event.get('details', {}).get('user_id'),
                risk_score=0.9,
                metadata={'event_type': event.get('event_type'), 'details': event.get('details')}
            ))
        
        return incidents
    
    async def _detect_unusual_hours_incidents(
        self, 
        auth_sessions: List[AuthSession]
    ) -> List[SecurityIncident]:
        """Detect unusual hours incidents"""
        incidents = []
        
        for session in auth_sessions:
            hour = session.created_at.hour
            # Check for logins outside business hours (6 AM - 8 PM)
            if hour < 6 or hour > 20:
                incidents.append(SecurityIncident(
                    incident_id=f"unusual_hours_{session.user_principal.user_id}_{datetime.now().timestamp()}",
                    incident_type=SecurityIncidentType.UNUSUAL_HOURS,
                    severity='medium',
                    description=f"Login outside business hours: {hour}:00 for user {session.user_principal.user_id}",
                    timestamp=session.created_at,
                    user_id=session.user_principal.user_id,
                    session_id=session.session_id,
                    risk_score=0.5,
                    metadata={'login_hour': hour, 'user_id': session.user_principal.user_id}
                ))
        
        return incidents
    
    async def _detect_multiple_sessions_incidents(
        self, 
        auth_sessions: List[AuthSession]
    ) -> List[SecurityIncident]:
        """Detect multiple concurrent sessions incidents"""
        incidents = []
        
        # Group sessions by user
        user_sessions = defaultdict(list)
        for session in auth_sessions:
            user_sessions[session.user_principal.user_id].append(session)
        
        # Check for users with multiple concurrent sessions
        for user_id, sessions in user_sessions.items():
            if len(sessions) > self.incident_thresholds['multiple_sessions']:
                incidents.append(SecurityIncident(
                    incident_id=f"multiple_sessions_{user_id}_{datetime.now().timestamp()}",
                    incident_type=SecurityIncidentType.MULTIPLE_SESSIONS,
                    severity='medium',
                    description=f"Multiple concurrent sessions for user {user_id}: {len(sessions)} sessions",
                    timestamp=datetime.now(),
                    user_id=user_id,
                    risk_score=0.6,
                    metadata={'session_count': len(sessions), 'user_id': user_id}
                ))
        
        return incidents


class AuthAnalyticsIntegration:
    """
    Main integration engine that combines authentication data with advanced analytics
    """
    
    def __init__(self, auth_manager: EnterpriseAuthManager):
        self.auth_manager = auth_manager
        self.user_behavior_analyzer = UserBehaviorAnalyzer()
        self.security_incident_detector = SecurityIncidentDetector()
        self.intelligence_engine = IntelligenceEngine()
        self.advanced_analytics = AdvancedAnalyticsEngine()
        self.business_intelligence = BusinessIntelligenceEngine()
        self.predictive_analytics = PredictiveAnalyticsEngine()
    
    async def run_comprehensive_auth_analytics(
        self,
        cluster_context: Optional[str] = None,
        time_range: str = "24h"
    ) -> AuthAnalyticsReport:
        """
        Run comprehensive authentication analytics with business intelligence
        
        Args:
            cluster_context: Kubernetes cluster context
            time_range: Analysis time range
            
        Returns:
            Comprehensive authentication analytics report
        """
        logger.info("Starting comprehensive authentication analytics")
        
        # Get authentication data
        auth_sessions = list(self.auth_manager.sessions.values())
        audit_trail = await self.auth_manager.get_audit_trail()
        
        # Analyze user behavior patterns
        user_behavior_patterns = await self.user_behavior_analyzer.analyze_user_behavior(
            auth_sessions, audit_trail
        )
        
        # Detect security incidents
        security_incidents = await self.security_incident_detector.detect_security_incidents(
            auth_sessions, audit_trail
        )
        
        # Calculate authentication metrics
        auth_metrics = await self._calculate_authentication_metrics(auth_sessions, audit_trail)
        
        # Perform risk assessment
        risk_assessment = await self._perform_risk_assessment(
            user_behavior_patterns, security_incidents, auth_metrics
        )
        
        # Analyze business impact
        business_impact = await self._analyze_business_impact(
            user_behavior_patterns, security_incidents, auth_metrics
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            user_behavior_patterns, security_incidents, risk_assessment
        )
        
        # Create comprehensive summary
        summary = await self._create_comprehensive_summary(
            user_behavior_patterns, security_incidents, auth_metrics, risk_assessment
        )
        
        report = AuthAnalyticsReport(
            timestamp=datetime.now(),
            user_behavior_patterns=user_behavior_patterns,
            security_incidents=security_incidents,
            authentication_metrics=auth_metrics,
            risk_assessment=risk_assessment,
            business_impact=business_impact,
            recommendations=recommendations,
            summary=summary
        )
        
        logger.info("Completed comprehensive authentication analytics")
        return report
    
    async def _calculate_authentication_metrics(
        self, 
        auth_sessions: List[AuthSession],
        audit_trail: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive authentication metrics"""
        
        total_sessions = len(auth_sessions)
        active_sessions = len([s for s in auth_sessions if s.expires_at > datetime.now()])
        
        # Calculate user statistics
        unique_users = len(set(s.user_principal.user_id for s in auth_sessions))
        
        # Calculate provider statistics
        provider_stats = defaultdict(int)
        for session in auth_sessions:
            provider_stats[session.user_principal.provider] += 1
        
        # Calculate risk statistics
        high_risk_sessions = len([s for s in auth_sessions if s.risk_score > 0.7])
        avg_risk_score = np.mean([s.risk_score for s in auth_sessions]) if auth_sessions else 0
        
        # Calculate audit statistics
        total_audit_events = len(audit_trail)
        failed_auth_events = len([e for e in audit_trail if e.get('event_type') == 'authentication_failed'])
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'unique_users': unique_users,
            'provider_distribution': dict(provider_stats),
            'high_risk_sessions': high_risk_sessions,
            'average_risk_score': avg_risk_score,
            'total_audit_events': total_audit_events,
            'failed_auth_events': failed_auth_events,
            'success_rate': (total_audit_events - failed_auth_events) / total_audit_events if total_audit_events > 0 else 1.0
        }
    
    async def _perform_risk_assessment(
        self,
        user_behavior_patterns: List[UserBehaviorPattern],
        security_incidents: List[SecurityIncident],
        auth_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        
        # Calculate risk scores
        behavior_risk = np.mean([p.risk_score for p in user_behavior_patterns]) if user_behavior_patterns else 0
        incident_risk = np.mean([i.risk_score for i in security_incidents]) if security_incidents else 0
        auth_risk = auth_metrics.get('average_risk_score', 0)
        
        # Overall risk score (weighted average)
        overall_risk = (behavior_risk * 0.4 + incident_risk * 0.4 + auth_risk * 0.2)
        
        # Risk categories
        risk_categories = {
            'low': overall_risk < 0.3,
            'medium': 0.3 <= overall_risk < 0.7,
            'high': overall_risk >= 0.7
        }
        
        return {
            'overall_risk_score': overall_risk,
            'behavior_risk_score': behavior_risk,
            'incident_risk_score': incident_risk,
            'auth_risk_score': auth_risk,
            'risk_level': next((k for k, v in risk_categories.items() if v), 'low'),
            'critical_incidents': len([i for i in security_incidents if i.severity == 'critical']),
            'high_risk_behaviors': len([p for p in user_behavior_patterns if p.risk_score > 0.7])
        }
    
    async def _analyze_business_impact(
        self,
        user_behavior_patterns: List[UserBehaviorPattern],
        security_incidents: List[SecurityIncident],
        auth_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze business impact of authentication patterns"""
        
        # Calculate productivity impact
        suspicious_behaviors = len([p for p in user_behavior_patterns if p.behavior_type in [
            UserBehaviorType.SUSPICIOUS, UserBehaviorType.MALICIOUS
        ]])
        
        # Calculate security impact
        critical_incidents = len([i for i in security_incidents if i.severity == 'critical'])
        high_incidents = len([i for i in security_incidents if i.severity == 'high'])
        
        # Calculate efficiency metrics
        auth_success_rate = auth_metrics.get('success_rate', 1.0)
        avg_session_duration = auth_metrics.get('average_session_duration', 0)
        
        return {
            'productivity_impact': {
                'suspicious_behaviors': suspicious_behaviors,
                'efficiency_score': auth_success_rate * 100,
                'user_experience_score': min(100, (1 - suspicious_behaviors / max(1, len(user_behavior_patterns))) * 100)
            },
            'security_impact': {
                'critical_incidents': critical_incidents,
                'high_incidents': high_incidents,
                'security_score': max(0, 100 - (critical_incidents * 20 + high_incidents * 10))
            },
            'operational_impact': {
                'auth_success_rate': auth_success_rate,
                'avg_session_duration': avg_session_duration,
                'user_satisfaction': auth_success_rate * 100
            }
        }
    
    async def _generate_recommendations(
        self,
        user_behavior_patterns: List[UserBehaviorPattern],
        security_incidents: List[SecurityIncident],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # High-risk recommendations
        if risk_assessment.get('overall_risk_score', 0) > 0.7:
            recommendations.append("Implement additional security measures due to high overall risk")
        
        # Incident-based recommendations
        critical_incidents = risk_assessment.get('critical_incidents', 0)
        if critical_incidents > 0:
            recommendations.append(f"Investigate {critical_incidents} critical security incidents immediately")
        
        # Behavior-based recommendations
        suspicious_behaviors = len([p for p in user_behavior_patterns if p.behavior_type == UserBehaviorType.SUSPICIOUS])
        if suspicious_behaviors > 0:
            recommendations.append(f"Review {suspicious_behaviors} suspicious user behaviors")
        
        # General recommendations
        if len(security_incidents) > 5:
            recommendations.append("Consider implementing additional monitoring and alerting")
        
        if len(user_behavior_patterns) > 10:
            recommendations.append("Consider implementing user behavior analytics for better insights")
        
        return recommendations
    
    async def _create_comprehensive_summary(
        self,
        user_behavior_patterns: List[UserBehaviorPattern],
        security_incidents: List[SecurityIncident],
        auth_metrics: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive summary of authentication analytics"""
        
        return {
            'overall_status': 'healthy' if risk_assessment.get('overall_risk_score', 0) < 0.5 else 'attention_required',
            'key_metrics': {
                'total_users': auth_metrics.get('unique_users', 0),
                'active_sessions': auth_metrics.get('active_sessions', 0),
                'behavior_patterns': len(user_behavior_patterns),
                'security_incidents': len(security_incidents),
                'success_rate': auth_metrics.get('success_rate', 1.0) * 100
            },
            'risk_summary': {
                'overall_risk': risk_assessment.get('overall_risk_score', 0),
                'risk_level': risk_assessment.get('risk_level', 'low'),
                'critical_incidents': risk_assessment.get('critical_incidents', 0)
            },
            'trends': {
                'behavior_trend': 'increasing' if len(user_behavior_patterns) > 5 else 'stable',
                'incident_trend': 'increasing' if len(security_incidents) > 3 else 'stable',
                'risk_trend': 'increasing' if risk_assessment.get('overall_risk_score', 0) > 0.6 else 'stable'
            }
        } 