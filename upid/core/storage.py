"""
UPID Storage System
Lightweight, embeddable storage using DuckDB for time-series data and metadata.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import duckdb
from dataclasses import dataclass, asdict
import sqlite3

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesPoint:
    """A single time-series data point."""
    timestamp: datetime
    metric_name: str
    value: float
    labels: Dict[str, str]
    cluster_id: str
    source: str


@dataclass
class ClusterMetadata:
    """Cluster metadata and configuration."""
    cluster_id: str
    name: str
    provider: str  # aws, gcp, azure, local
    region: str
    created_at: datetime
    last_seen: datetime
    config: Dict[str, Any]


@dataclass
class UserSession:
    """User session and authentication data."""
    session_id: str
    user_id: str
    cluster_id: str
    created_at: datetime
    expires_at: datetime
    permissions: List[str]


class UPIDStorage:
    """
    Unified storage system using DuckDB for time-series data and metadata.
    Lightweight, embeddable, and cross-platform.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize UPID storage system.
        
        Args:
            db_path: Path to DuckDB database file. If None, uses default location.
        """
        if db_path is None:
            # Use default location in user's home directory
            home = Path.home()
            upid_dir = home / ".upid"
            upid_dir.mkdir(exist_ok=True)
            db_path = upid_dir / "upid_data.duckdb"
        
        self.db_path = str(db_path)
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with required tables and indexes."""
        try:
            self.connection = duckdb.connect(self.db_path)
            
            # Create time-series table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS time_series (
                    timestamp TIMESTAMP NOT NULL,
                    metric_name VARCHAR NOT NULL,
                    value DOUBLE NOT NULL,
                    labels JSON,
                    cluster_id VARCHAR NOT NULL,
                    source VARCHAR NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create cluster metadata table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    provider VARCHAR NOT NULL,
                    region VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config JSON
                )
            """)
            
            # Create user sessions table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id VARCHAR PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    cluster_id VARCHAR NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    permissions JSON
                )
            """)
            
            # Create audit log table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id VARCHAR,
                    action VARCHAR NOT NULL,
                    resource_type VARCHAR,
                    resource_id VARCHAR,
                    details JSON
                )
            """)
            
            # Create indexes for performance
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_time_series_timestamp ON time_series(timestamp)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_time_series_metric ON time_series(metric_name)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_time_series_cluster ON time_series(cluster_id)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id)")
            
            logger.info(f"Initialized UPID storage at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            raise
    
    def store_metrics(self, cluster_id: str, metrics: List[TimeSeriesPoint]):
        """
        Store time-series metrics in DuckDB.
        
        Args:
            cluster_id: Kubernetes cluster identifier
            metrics: List of time-series data points
        """
        try:
            for metric in metrics:
                self.connection.execute("""
                    INSERT INTO time_series (timestamp, metric_name, value, labels, cluster_id, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metric.timestamp,
                    metric.metric_name,
                    metric.value,
                    json.dumps(metric.labels),
                    metric.cluster_id,
                    metric.source
                ))
            
            self.connection.commit()
            logger.info(f"Stored {len(metrics)} metrics for cluster {cluster_id}")
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            raise
    
    def get_metrics(
        self,
        cluster_id: str,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[TimeSeriesPoint]:
        """
        Retrieve time-series metrics from DuckDB.
        
        Args:
            cluster_id: Kubernetes cluster identifier
            metric_name: Optional metric name filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Optional limit on number of results
            
        Returns:
            List of time-series data points
        """
        try:
            query = "SELECT timestamp, metric_name, value, labels, cluster_id, source FROM time_series WHERE cluster_id = ?"
            params = [cluster_id]
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            result = self.connection.execute(query, params).fetchall()
            
            metrics = []
            for row in result:
                timestamp, metric_name, value, labels_json, cluster_id, source = row
                labels = json.loads(labels_json) if labels_json else {}
                
                metrics.append(TimeSeriesPoint(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    value=value,
                    labels=labels,
                    cluster_id=cluster_id,
                    source=source
                ))
            
            logger.info(f"Retrieved {len(metrics)} metrics for cluster {cluster_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to retrieve metrics: {e}")
            raise
    
    def get_aggregated_metrics(
        self,
        cluster_id: str,
        metric_name: str,
        aggregation: str = 'avg',  # avg, sum, min, max, count
        interval: str = '1 hour',  # time interval for aggregation
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated time-series metrics.
        
        Args:
            cluster_id: Kubernetes cluster identifier
            metric_name: Metric name to aggregate
            aggregation: Aggregation function (avg, sum, min, max, count)
            interval: Time interval for aggregation
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of aggregated data points
        """
        try:
            # Build time bucket query
            time_bucket = f"time_bucket('{interval}', timestamp)"
            
            query = f"""
                SELECT 
                    {time_bucket} as bucket,
                    {aggregation}(value) as aggregated_value,
                    COUNT(*) as point_count
                FROM time_series 
                WHERE cluster_id = ? AND metric_name = ?
            """
            params = [cluster_id, metric_name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += f" GROUP BY {time_bucket} ORDER BY bucket DESC"
            
            result = self.connection.execute(query, params).fetchall()
            
            aggregated_data = []
            for row in result:
                bucket, aggregated_value, point_count = row
                aggregated_data.append({
                    'timestamp': bucket,
                    'value': aggregated_value,
                    'point_count': point_count,
                    'metric_name': metric_name,
                    'aggregation': aggregation
                })
            
            logger.info(f"Retrieved {len(aggregated_data)} aggregated points for {metric_name}")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve aggregated metrics: {e}")
            raise
    
    def store_cluster_metadata(self, cluster: ClusterMetadata):
        """Store cluster metadata."""
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO clusters 
                (cluster_id, name, provider, region, created_at, last_seen, config)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cluster.cluster_id,
                cluster.name,
                cluster.provider,
                cluster.region,
                cluster.created_at,
                cluster.last_seen,
                json.dumps(cluster.config)
            ))
            
            self.connection.commit()
            logger.info(f"Stored metadata for cluster {cluster.cluster_id}")
            
        except Exception as e:
            logger.error(f"Failed to store cluster metadata: {e}")
            raise
    
    def get_cluster_metadata(self, cluster_id: str) -> Optional[ClusterMetadata]:
        """Retrieve cluster metadata."""
        try:
            result = self.connection.execute("""
                SELECT cluster_id, name, provider, region, created_at, last_seen, config
                FROM clusters WHERE cluster_id = ?
            """, [cluster_id]).fetchone()
            
            if result:
                cluster_id, name, provider, region, created_at, last_seen, config_json = result
                config = json.loads(config_json) if config_json else {}
                
                return ClusterMetadata(
                    cluster_id=cluster_id,
                    name=name,
                    provider=provider,
                    region=region,
                    created_at=created_at,
                    last_seen=last_seen,
                    config=config
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cluster metadata: {e}")
            raise
    
    def list_clusters(self) -> List[ClusterMetadata]:
        """List all clusters."""
        try:
            result = self.connection.execute("""
                SELECT cluster_id, name, provider, region, created_at, last_seen, config
                FROM clusters ORDER BY last_seen DESC
            """).fetchall()
            
            clusters = []
            for row in result:
                cluster_id, name, provider, region, created_at, last_seen, config_json = row
                config = json.loads(config_json) if config_json else {}
                
                clusters.append(ClusterMetadata(
                    cluster_id=cluster_id,
                    name=name,
                    provider=provider,
                    region=region,
                    created_at=created_at,
                    last_seen=last_seen,
                    config=config
                ))
            
            return clusters
            
        except Exception as e:
            logger.error(f"Failed to list clusters: {e}")
            raise
    
    def store_user_session(self, session: UserSession):
        """Store user session data."""
        try:
            self.connection.execute("""
                INSERT OR REPLACE INTO user_sessions 
                (session_id, user_id, cluster_id, created_at, expires_at, permissions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.cluster_id,
                session.created_at,
                session.expires_at,
                json.dumps(session.permissions)
            ))
            
            self.connection.commit()
            logger.info(f"Stored session {session.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store user session: {e}")
            raise
    
    def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """Retrieve user session data."""
        try:
            result = self.connection.execute("""
                SELECT session_id, user_id, cluster_id, created_at, expires_at, permissions
                FROM user_sessions WHERE session_id = ?
            """, [session_id]).fetchone()
            
            if result:
                session_id, user_id, cluster_id, created_at, expires_at, permissions_json = result
                permissions = json.loads(permissions_json) if permissions_json else []
                
                return UserSession(
                    session_id=session_id,
                    user_id=user_id,
                    cluster_id=cluster_id,
                    created_at=created_at,
                    expires_at=expires_at,
                    permissions=permissions
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve user session: {e}")
            raise
    
    def log_audit_event(
        self,
        user_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an audit event."""
        try:
            self.connection.execute("""
                INSERT INTO audit_log (user_id, action, resource_type, resource_id, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                action,
                resource_type,
                resource_id,
                json.dumps(details) if details else None
            ))
            
            self.connection.commit()
            logger.info(f"Logged audit event: {action} by {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            raise
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve audit log entries."""
        try:
            query = "SELECT timestamp, user_id, action, resource_type, resource_id, details FROM audit_log WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            result = self.connection.execute(query, params).fetchall()
            
            audit_entries = []
            for row in result:
                timestamp, user_id, action, resource_type, resource_id, details_json = row
                details = json.loads(details_json) if details_json else {}
                
                audit_entries.append({
                    'timestamp': timestamp,
                    'user_id': user_id,
                    'action': action,
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'details': details
                })
            
            return audit_entries
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit log: {e}")
            raise
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """
        Clean up old data to manage storage size.
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up old time-series data
            self.connection.execute("""
                DELETE FROM time_series WHERE timestamp < ?
            """, [cutoff_date])
            
            # Clean up expired sessions
            self.connection.execute("""
                DELETE FROM user_sessions WHERE expires_at < ?
            """, [datetime.now()])
            
            # Clean up old audit logs
            self.connection.execute("""
                DELETE FROM audit_log WHERE timestamp < ?
            """, [cutoff_date])
            
            self.connection.commit()
            logger.info(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {}
            
            # Time-series data stats
            result = self.connection.execute("SELECT COUNT(*) FROM time_series").fetchone()
            stats['total_metrics'] = result[0] if result else 0
            
            result = self.connection.execute("SELECT COUNT(DISTINCT cluster_id) FROM time_series").fetchone()
            stats['clusters_with_metrics'] = result[0] if result else 0
            
            result = self.connection.execute("SELECT COUNT(DISTINCT metric_name) FROM time_series").fetchone()
            stats['unique_metrics'] = result[0] if result else 0
            
            # Cluster metadata stats
            result = self.connection.execute("SELECT COUNT(*) FROM clusters").fetchone()
            stats['total_clusters'] = result[0] if result else 0
            
            # Session stats
            result = self.connection.execute("SELECT COUNT(*) FROM user_sessions").fetchone()
            stats['active_sessions'] = result[0] if result else 0
            
            # Audit log stats
            result = self.connection.execute("SELECT COUNT(*) FROM audit_log").fetchone()
            stats['audit_entries'] = result[0] if result else 0
            
            # Database file size
            if os.path.exists(self.db_path):
                stats['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
            else:
                stats['database_size_mb'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Closed UPID storage connection")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 