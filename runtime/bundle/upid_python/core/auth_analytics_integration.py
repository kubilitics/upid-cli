#!/usr/bin/env python3
"""
UPID CLI - Auth Analytics Integration
Integration between authentication and analytics systems
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from upid_python.auth.enterprise_auth import EnterpriseAuthManager, AuthSession, UserPrincipal

logger = logging.getLogger(__name__)


@dataclass
class AuthAnalyticsEvent:
    """Authentication analytics event"""
    event_type: str
    user_id: str
    session_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AuthAnalyticsIntegration:
    """
    Auth Analytics Integration
    
    Features:
    - Authentication event tracking
    - Session analytics
    - Risk assessment integration
    - Security analytics
    """
    
    def __init__(self, auth_manager: EnterpriseAuthManager):
        self.auth_manager = auth_manager
        self.analytics_events: List[AuthAnalyticsEvent] = []
        self.risk_threshold = 0.7
        
        logger.info("🔧 Initializing Auth Analytics Integration")
    
    async def initialize(self) -> bool:
        """Initialize Auth Analytics Integration"""
        try:
            logger.info("🚀 Initializing Auth Analytics Integration...")
            
            # Load existing analytics data
            await self._load_analytics_data()
            
            logger.info("✅ Auth Analytics Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Auth Analytics Integration: {e}")
            return False
    
    async def _load_analytics_data(self):
        """Load existing analytics data"""
        try:
            # This would typically load from database or file
            logger.info("📝 Loading analytics data...")
            
        except Exception as e:
            logger.error(f"❌ Failed to load analytics data: {e}")
    
    async def track_auth_event(self, event_type: str, session: AuthSession, metadata: Dict[str, Any] = None):
        """Track authentication event"""
        try:
            event = AuthAnalyticsEvent(
                event_type=event_type,
                user_id=session.user_principal.user_id,
                session_id=session.session_id,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            self.analytics_events.append(event)
            
            # Keep only last 1000 events
            if len(self.analytics_events) > 1000:
                self.analytics_events = self.analytics_events[-1000:]
            
            logger.debug(f"📊 Tracked auth event: {event_type} for user {session.user_principal.email}")
            
        except Exception as e:
            logger.error(f"❌ Failed to track auth event: {e}")
    
    async def run_comprehensive_auth_analytics(self, session: AuthSession) -> Dict[str, Any]:
        """Run comprehensive authentication analytics"""
        try:
            # Assess session risk
            risk_score = await self.auth_manager.assess_risk(session)
            
            # Analyze user behavior
            user_behavior = await self._analyze_user_behavior(session.user_principal.user_id)
            
            # Check for anomalies
            anomalies = await self._detect_auth_anomalies(session)
            
            # Generate security insights
            security_insights = await self._generate_security_insights(session, risk_score)
            
            analytics_result = {
                "session_id": session.session_id,
                "user_id": session.user_principal.user_id,
                "risk_score": risk_score,
                "user_behavior": user_behavior,
                "anomalies": anomalies,
                "security_insights": security_insights,
                "timestamp": datetime.now().isoformat()
            }
            
            # Track analytics event
            await self.track_auth_event("analytics_run", session, analytics_result)
            
            logger.info(f"📊 Completed auth analytics for session {session.session_id}")
            return analytics_result
            
        except Exception as e:
            logger.error(f"❌ Failed to run auth analytics: {e}")
            return {"error": str(e)}
    
    async def _analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            # Get user's recent sessions
            user_sessions = [
                event for event in self.analytics_events
                if event.user_id == user_id
            ]
            
            if not user_sessions:
                return {"message": "No behavior data available"}
            
            # Analyze session patterns
            session_count = len(user_sessions)
            recent_sessions = [
                event for event in user_sessions
                if event.timestamp > datetime.now() - timedelta(days=7)
            ]
            
            # Calculate behavior metrics
            behavior_metrics = {
                "total_sessions": session_count,
                "recent_sessions": len(recent_sessions),
                "avg_sessions_per_day": len(recent_sessions) / 7,
                "last_activity": max(event.timestamp for event in user_sessions).isoformat(),
                "activity_pattern": "normal" if len(recent_sessions) > 0 else "inactive"
            }
            
            return behavior_metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze user behavior: {e}")
            return {"error": str(e)}
    
    async def _detect_auth_anomalies(self, session: AuthSession) -> List[Dict[str, Any]]:
        """Detect authentication anomalies"""
        try:
            anomalies = []
            
            # Check for high risk score
            if session.risk_score > self.risk_threshold:
                anomalies.append({
                    "type": "high_risk_session",
                    "severity": "high",
                    "description": f"Session risk score {session.risk_score:.2f} exceeds threshold {self.risk_threshold}",
                    "recommendation": "Review session activity and consider termination"
                })
            
            # Check for unusual session duration
            session_duration = (datetime.now() - session.created_at).total_seconds()
            if session_duration > 7200:  # 2 hours
                anomalies.append({
                    "type": "long_session",
                    "severity": "medium",
                    "description": f"Session duration {session_duration/3600:.1f} hours",
                    "recommendation": "Consider session timeout"
                })
            
            # Check for inactivity
            inactivity = (datetime.now() - session.last_activity).total_seconds()
            if inactivity > 1800:  # 30 minutes
                anomalies.append({
                    "type": "inactive_session",
                    "severity": "medium",
                    "description": f"Session inactive for {inactivity/60:.1f} minutes",
                    "recommendation": "Consider session termination"
                })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Failed to detect auth anomalies: {e}")
            return []
    
    async def _generate_security_insights(self, session: AuthSession, risk_score: float) -> Dict[str, Any]:
        """Generate security insights"""
        try:
            insights = {
                "session_security": "secure" if risk_score < 0.3 else "moderate" if risk_score < 0.7 else "high_risk",
                "recommendations": []
            }
            
            # Generate recommendations based on risk score
            if risk_score > 0.7:
                insights["recommendations"].append("Immediately terminate session")
                insights["recommendations"].append("Review user permissions")
                insights["recommendations"].append("Enable additional authentication factors")
            elif risk_score > 0.4:
                insights["recommendations"].append("Monitor session activity")
                insights["recommendations"].append("Consider session timeout")
            else:
                insights["recommendations"].append("Session appears normal")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to generate security insights: {e}")
            return {"error": str(e)}
    
    async def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for specified period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter events by date
            recent_events = [
                event for event in self.analytics_events
                if event.timestamp >= cutoff_date
            ]
            
            # Calculate summary metrics
            total_events = len(recent_events)
            unique_users = len(set(event.user_id for event in recent_events))
            event_types = {}
            
            for event in recent_events:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            summary = {
                "period_days": days,
                "total_events": total_events,
                "unique_users": unique_users,
                "event_types": event_types,
                "avg_events_per_day": total_events / days if days > 0 else 0
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get analytics summary: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Shutdown Auth Analytics Integration"""
        logger.info("🛑 Shutting down Auth Analytics Integration...")
        
        # Save analytics data
        await self._save_analytics_data()
        
        logger.info("✅ Auth Analytics Integration shutdown complete")
    
    async def _save_analytics_data(self):
        """Save analytics data to storage"""
        try:
            # This would typically save to database or file
            logger.info("💾 Saving analytics data...")
            
        except Exception as e:
            logger.error(f"❌ Failed to save analytics data: {e}") 