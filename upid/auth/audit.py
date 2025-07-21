"""
Audit Trail System for UPID CLI
Provides comprehensive logging and compliance features for enterprise security
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    SESSION_EXPIRED = "session_expired"
    TOKEN_REFRESHED = "token_refreshed"
    
    # Authorization events
    PERMISSION_CHECK = "permission_check"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Resource events
    RESOURCE_READ = "resource_read"
    RESOURCE_WRITE = "resource_write"
    RESOURCE_DELETE = "resource_delete"
    RESOURCE_CREATE = "resource_create"
    
    # Configuration events
    CONFIG_CHANGED = "config_changed"
    SETTINGS_UPDATED = "settings_updated"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    BACKUP_CREATED = "backup_created"
    RESTORE_PERFORMED = "restore_performed"
    
    # Security events
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCESS_BLOCKED = "access_blocked"


class AuditSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: str
    username: str
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    severity: AuditSeverity = AuditSeverity.LOW
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AuditFilter:
    """Audit event filter criteria"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    event_type: Optional[AuditEventType] = None
    severity: Optional[AuditSeverity] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    success: Optional[bool] = None


class AuditTrailManager:
    """
    Audit Trail Manager
    Manages comprehensive audit logging and compliance features
    """
    
    def __init__(self, storage_backend: str = "memory"):
        self.storage_backend = storage_backend
        self.events: List[AuditEvent] = []
        self.retention_days = 90
        self.max_events = 100000
        self.compression_enabled = True
        
        # Initialize storage
        self._init_storage()
    
    def _init_storage(self):
        """Initialize audit storage backend"""
        if self.storage_backend == "memory":
            # In-memory storage (for testing)
            self.storage = self.events
        else:
            # Could be extended to support database storage
            logger.warning(f"Storage backend {self.storage_backend} not implemented, using memory")
            self.storage = self.events
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        username: str,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of audit event
            user_id: User identifier
            username: Username
            session_id: Session identifier (optional)
            ip_address: IP address (optional)
            user_agent: User agent string (optional)
            resource_type: Type of resource accessed (optional)
            resource_id: Resource identifier (optional)
            action: Action performed (optional)
            details: Additional event details (optional)
            severity: Event severity level
            success: Whether the action was successful
            error_message: Error message if failed (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            str: Event ID
        """
        try:
            event_id = str(uuid.uuid4())
            
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.now(),
                user_id=user_id,
                username=username,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                details=details,
                severity=severity,
                success=success,
                error_message=error_message,
                metadata=metadata
            )
            
            # Add to storage
            self.storage.append(event)
            
            # Enforce retention policy
            await self._enforce_retention()
            
            # Log to system logger
            log_message = f"AUDIT: {event_type.value} - User: {username}, Resource: {resource_type or 'N/A'}, Success: {success}"
            if severity == AuditSeverity.CRITICAL:
                logger.critical(log_message)
            elif severity == AuditSeverity.HIGH:
                logger.error(log_message)
            elif severity == AuditSeverity.MEDIUM:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return ""
    
    async def log_login(
        self,
        user_id: str,
        username: str,
        session_id: str,
        ip_address: str = None,
        user_agent: str = None,
        auth_provider: str = None
    ) -> str:
        """Log successful login event"""
        return await self.log_event(
            event_type=AuditEventType.LOGIN,
            user_id=user_id,
            username=username,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"auth_provider": auth_provider},
            severity=AuditSeverity.LOW,
            success=True
        )
    
    async def log_login_failed(
        self,
        username: str,
        ip_address: str = None,
        user_agent: str = None,
        reason: str = None
    ) -> str:
        """Log failed login event"""
        return await self.log_event(
            event_type=AuditEventType.LOGIN_FAILED,
            user_id="unknown",
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
            severity=AuditSeverity.MEDIUM,
            success=False,
            error_message=reason
        )
    
    async def log_logout(
        self,
        user_id: str,
        username: str,
        session_id: str,
        ip_address: str = None
    ) -> str:
        """Log logout event"""
        return await self.log_event(
            event_type=AuditEventType.LOGOUT,
            user_id=user_id,
            username=username,
            session_id=session_id,
            ip_address=ip_address,
            severity=AuditSeverity.LOW,
            success=True
        )
    
    async def log_permission_check(
        self,
        user_id: str,
        username: str,
        permission: str,
        resource_type: str = None,
        resource_id: str = None,
        granted: bool = True
    ) -> str:
        """Log permission check event"""
        event_type = AuditEventType.PERMISSION_CHECK if granted else AuditEventType.PERMISSION_DENIED
        severity = AuditSeverity.MEDIUM if not granted else AuditSeverity.LOW
        
        return await self.log_event(
            event_type=event_type,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            action=permission,
            details={"permission": permission, "granted": granted},
            severity=severity,
            success=granted
        )
    
    async def log_resource_access(
        self,
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: str,
        session_id: str = None,
        ip_address: str = None,
        success: bool = True,
        error_message: str = None
    ) -> str:
        """Log resource access event"""
        event_type_map = {
            "read": AuditEventType.RESOURCE_READ,
            "write": AuditEventType.RESOURCE_WRITE,
            "create": AuditEventType.RESOURCE_CREATE,
            "delete": AuditEventType.RESOURCE_DELETE
        }
        
        event_type = event_type_map.get(action, AuditEventType.RESOURCE_READ)
        severity = AuditSeverity.MEDIUM if not success else AuditSeverity.LOW
        
        return await self.log_event(
            event_type=event_type,
            user_id=user_id,
            username=username,
            session_id=session_id,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            severity=severity,
            success=success,
            error_message=error_message
        )
    
    async def log_security_alert(
        self,
        alert_type: str,
        description: str,
        user_id: str = None,
        username: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None
    ) -> str:
        """Log security alert event"""
        return await self.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            user_id=user_id or "system",
            username=username or "system",
            ip_address=ip_address,
            action=alert_type,
            details=details,
            severity=AuditSeverity.HIGH,
            success=False,
            error_message=description
        )
    
    async def query_events(
        self,
        filter_criteria: AuditFilter = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[AuditEvent]:
        """
        Query audit events with filters
        
        Args:
            filter_criteria: Filter criteria
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List[AuditEvent]: Filtered audit events
        """
        try:
            events = self.storage.copy()
            
            # Apply filters
            if filter_criteria:
                events = await self._apply_filters(events, filter_criteria)
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply pagination
            events = events[offset:offset + limit]
            
            return events
            
        except Exception as e:
            logger.error(f"Error querying audit events: {e}")
            return []
    
    async def _apply_filters(
        self, 
        events: List[AuditEvent], 
        filter_criteria: AuditFilter
    ) -> List[AuditEvent]:
        """Apply filters to audit events"""
        filtered_events = events
        
        if filter_criteria.start_time:
            filtered_events = [
                e for e in filtered_events 
                if e.timestamp >= filter_criteria.start_time
            ]
        
        if filter_criteria.end_time:
            filtered_events = [
                e for e in filtered_events 
                if e.timestamp <= filter_criteria.end_time
            ]
        
        if filter_criteria.user_id:
            filtered_events = [
                e for e in filtered_events 
                if e.user_id == filter_criteria.user_id
            ]
        
        if filter_criteria.username:
            filtered_events = [
                e for e in filtered_events 
                if e.username == filter_criteria.username
            ]
        
        if filter_criteria.event_type:
            filtered_events = [
                e for e in filtered_events 
                if e.event_type == filter_criteria.event_type
            ]
        
        if filter_criteria.severity:
            filtered_events = [
                e for e in filtered_events 
                if e.severity == filter_criteria.severity
            ]
        
        if filter_criteria.resource_type:
            filtered_events = [
                e for e in filtered_events 
                if e.resource_type == filter_criteria.resource_type
            ]
        
        if filter_criteria.resource_id:
            filtered_events = [
                e for e in filtered_events 
                if e.resource_id == filter_criteria.resource_id
            ]
        
        if filter_criteria.success is not None:
            filtered_events = [
                e for e in filtered_events 
                if e.success == filter_criteria.success
            ]
        
        return filtered_events
    
    async def get_event_statistics(
        self,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict[str, Any]:
        """
        Get audit event statistics
        
        Args:
            start_time: Start time for statistics
            end_time: End time for statistics
            
        Returns:
            Dict: Event statistics
        """
        try:
            filter_criteria = AuditFilter(
                start_time=start_time,
                end_time=end_time
            )
            
            events = await self.query_events(filter_criteria, limit=100000)
            
            # Calculate statistics
            total_events = len(events)
            successful_events = len([e for e in events if e.success])
            failed_events = total_events - successful_events
            
            # Event type distribution
            event_type_counts = {}
            for event in events:
                event_type = event.event_type.value
                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
            # Severity distribution
            severity_counts = {}
            for event in events:
                severity = event.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # User activity
            user_activity = {}
            for event in events:
                user = event.username
                user_activity[user] = user_activity.get(user, 0) + 1
            
            return {
                "total_events": total_events,
                "successful_events": successful_events,
                "failed_events": failed_events,
                "success_rate": (successful_events / total_events * 100) if total_events > 0 else 0,
                "event_type_distribution": event_type_counts,
                "severity_distribution": severity_counts,
                "user_activity": user_activity,
                "time_range": {
                    "start": start_time.isoformat() if start_time else None,
                    "end": end_time.isoformat() if end_time else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting event statistics: {e}")
            return {}
    
    async def export_audit_log(
        self,
        filter_criteria: AuditFilter = None,
        format: str = "json"
    ) -> str:
        """
        Export audit log in specified format
        
        Args:
            filter_criteria: Filter criteria
            format: Export format (json, csv)
            
        Returns:
            str: Exported audit log
        """
        try:
            events = await self.query_events(filter_criteria, limit=100000)
            
            if format == "json":
                return json.dumps([
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "user_id": event.user_id,
                        "username": event.username,
                        "session_id": event.session_id,
                        "ip_address": event.ip_address,
                        "user_agent": event.user_agent,
                        "resource_type": event.resource_type,
                        "resource_id": event.resource_id,
                        "action": event.action,
                        "details": event.details,
                        "severity": event.severity.value,
                        "success": event.success,
                        "error_message": event.error_message,
                        "metadata": event.metadata
                    }
                    for event in events
                ], indent=2)
            
            elif format == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    "event_id", "event_type", "timestamp", "user_id", "username",
                    "session_id", "ip_address", "resource_type", "resource_id",
                    "action", "severity", "success", "error_message"
                ])
                
                # Write data
                for event in events:
                    writer.writerow([
                        event.event_id,
                        event.event_type.value,
                        event.timestamp.isoformat(),
                        event.user_id,
                        event.username,
                        event.session_id,
                        event.ip_address,
                        event.resource_type,
                        event.resource_id,
                        event.action,
                        event.severity.value,
                        event.success,
                        event.error_message
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting audit log: {e}")
            return ""
    
    async def _enforce_retention(self):
        """Enforce audit log retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Remove old events
            original_count = len(self.storage)
            self.storage = [
                event for event in self.storage
                if event.timestamp > cutoff_date
            ]
            
            removed_count = original_count - len(self.storage)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} old audit events due to retention policy")
            
            # Enforce maximum events limit
            if len(self.storage) > self.max_events:
                # Remove oldest events
                self.storage.sort(key=lambda x: x.timestamp)
                excess_count = len(self.storage) - self.max_events
                self.storage = self.storage[excess_count:]
                logger.info(f"Removed {excess_count} audit events due to size limit")
                
        except Exception as e:
            logger.error(f"Error enforcing retention policy: {e}")
    
    async def cleanup_old_events(self) -> int:
        """
        Clean up old audit events
        
        Returns:
            int: Number of events removed
        """
        try:
            original_count = len(self.storage)
            await self._enforce_retention()
            return original_count - len(self.storage)
            
        except Exception as e:
            logger.error(f"Error cleaning up old events: {e}")
            return 0
    
    async def get_compliance_report(
        self,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report
        
        Args:
            start_time: Report start time
            end_time: Report end time
            
        Returns:
            Dict: Compliance report
        """
        try:
            if not start_time:
                start_time = datetime.now() - timedelta(days=30)
            if not end_time:
                end_time = datetime.now()
            
            filter_criteria = AuditFilter(
                start_time=start_time,
                end_time=end_time
            )
            
            events = await self.query_events(filter_criteria, limit=100000)
            
            # Security events
            security_events = [
                e for e in events
                if e.event_type in [
                    AuditEventType.LOGIN_FAILED,
                    AuditEventType.PERMISSION_DENIED,
                    AuditEventType.SECURITY_ALERT,
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    AuditEventType.ACCESS_BLOCKED
                ]
            ]
            
            # Authentication events
            auth_events = [
                e for e in events
                if e.event_type in [
                    AuditEventType.LOGIN,
                    AuditEventType.LOGOUT,
                    AuditEventType.SESSION_EXPIRED
                ]
            ]
            
            # Resource access events
            resource_events = [
                e for e in events
                if e.event_type in [
                    AuditEventType.RESOURCE_READ,
                    AuditEventType.RESOURCE_WRITE,
                    AuditEventType.RESOURCE_CREATE,
                    AuditEventType.RESOURCE_DELETE
                ]
            ]
            
            return {
                "report_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "total_events": len(events),
                "security_events": len(security_events),
                "authentication_events": len(auth_events),
                "resource_access_events": len(resource_events),
                "failed_events": len([e for e in events if not e.success]),
                "critical_events": len([e for e in events if e.severity == AuditSeverity.CRITICAL]),
                "high_severity_events": len([e for e in events if e.severity == AuditSeverity.HIGH]),
                "unique_users": len(set(e.username for e in events)),
                "compliance_score": self._calculate_compliance_score(events)
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {}
    
    def _calculate_compliance_score(self, events: List[AuditEvent]) -> float:
        """Calculate compliance score based on audit events"""
        try:
            if not events:
                return 100.0
            
            total_events = len(events)
            failed_events = len([e for e in events if not e.success])
            security_events = len([
                e for e in events
                if e.event_type in [
                    AuditEventType.LOGIN_FAILED,
                    AuditEventType.PERMISSION_DENIED,
                    AuditEventType.SECURITY_ALERT
                ]
            ])
            
            # Calculate score (100 = perfect compliance)
            score = 100.0
            
            # Deduct points for failed events
            if total_events > 0:
                failure_rate = failed_events / total_events
                score -= failure_rate * 20  # Up to 20 points for failures
            
            # Deduct points for security events
            if total_events > 0:
                security_rate = security_events / total_events
                score -= security_rate * 30  # Up to 30 points for security issues
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
            return 0.0 