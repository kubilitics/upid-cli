"""
Time-Series Data Store for UPID Intelligence Engine
Handles 90-day historical data collection, compression, and pattern analysis
"""

import os
import json
import sqlite3
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TimeSeriesDataStore:
    """Enterprise-grade time-series data store for Kubernetes metrics"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the time-series data store"""
        if data_dir is None:
            data_dir = os.path.expanduser("~/.upid/data")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Database files
        self.metrics_db = self.data_dir / "metrics.db"
        self.patterns_db = self.data_dir / "patterns.db"
        self.compressed_dir = self.data_dir / "compressed"
        self.compressed_dir.mkdir(exist_ok=True)
        
        # Initialize databases
        self._init_metrics_db()
        self._init_patterns_db()
        
        # Configuration
        self.retention_days = 90
        self.compression_threshold_days = 7  # Compress data older than 7 days
        self.collection_interval_seconds = 30
        
    def _init_metrics_db(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for efficient querying
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cluster_timestamp 
            ON metrics(cluster_id, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metric_type 
            ON metrics(metric_type, metric_name)
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_patterns_db(self):
        """Initialize patterns database"""
        conn = sqlite3.connect(self.patterns_db)
        cursor = conn.cursor()
        
        # Create patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_name TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL NOT NULL,
                detected_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pattern_cluster 
            ON patterns(cluster_id, pattern_type)
        ''')
        
        conn.commit()
        conn.close()
    
    def store_metrics(self, cluster_id: str, metrics: Dict[str, Any], timestamp: str = None):
        """Store metrics data with timestamp"""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        try:
            # Store node metrics
            if 'nodes' in metrics:
                for node in metrics['nodes']:
                    if 'cpu' in node:
                        cursor.execute('''
                            INSERT INTO metrics (cluster_id, timestamp, metric_type, metric_name, metric_value, metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cluster_id, timestamp, 'node', 'cpu_usage', float(node['cpu']), json.dumps(node)))
                    
                    if 'memory' in node:
                        cursor.execute('''
                            INSERT INTO metrics (cluster_id, timestamp, metric_type, metric_name, metric_value, metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cluster_id, timestamp, 'node', 'memory_usage', float(node['memory']), json.dumps(node)))
            
            # Store pod metrics
            if 'pods' in metrics:
                for pod in metrics['pods']:
                    if 'cpu' in pod:
                        cursor.execute('''
                            INSERT INTO metrics (cluster_id, timestamp, metric_type, metric_name, metric_value, metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cluster_id, timestamp, 'pod', 'cpu_usage', float(pod['cpu']), json.dumps(pod)))
                    
                    if 'memory' in pod:
                        cursor.execute('''
                            INSERT INTO metrics (cluster_id, timestamp, metric_type, metric_name, metric_value, metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cluster_id, timestamp, 'pod', 'memory_usage', float(pod['memory']), json.dumps(pod)))
            
            # Store resource metrics
            if 'resources' in metrics:
                resources = metrics['resources']
                if 'cpu' in resources:
                    cpu_used = resources['cpu'].get('used', 0)
                    cpu_total = resources['cpu'].get('total', 1)
                    cpu_percent = (cpu_used / cpu_total * 100) if cpu_total > 0 else 0
                    
                    cursor.execute('''
                        INSERT INTO metrics (cluster_id, timestamp, metric_type, metric_name, metric_value, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (cluster_id, timestamp, 'cluster', 'cpu_utilization', cpu_percent, json.dumps(resources['cpu'])))
                
                if 'memory' in resources:
                    memory_used = resources['memory'].get('used', 0)
                    memory_total = resources['memory'].get('total', 1)
                    memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
                    
                    cursor.execute('''
                        INSERT INTO metrics (cluster_id, timestamp, metric_type, metric_name, metric_value, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (cluster_id, timestamp, 'cluster', 'memory_utilization', memory_percent, json.dumps(resources['memory'])))
            
            conn.commit()
            logger.info(f"Stored metrics for cluster {cluster_id} at {timestamp}")
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_metrics(self, cluster_id: str, metric_type: str = None, 
                   start_time: str = None, end_time: str = None, 
                   limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve metrics data with optional filtering"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT cluster_id, timestamp, metric_type, metric_name, metric_value, metadata
                FROM metrics 
                WHERE cluster_id = ?
            '''
            params = [cluster_id]
            
            if metric_type:
                query += ' AND metric_type = ?'
                params.append(metric_type)
            
            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            metrics = []
            for row in results:
                metrics.append({
                    'cluster_id': row[0],
                    'timestamp': row[1],
                    'metric_type': row[2],
                    'metric_name': row[3],
                    'metric_value': row[4],
                    'metadata': json.loads(row[5]) if row[5] else {}
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            return []
        finally:
            conn.close()
    
    def get_historical_data(self, cluster_id: str, days: int = 90) -> Dict[str, Any]:
        """Get historical data for analysis"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        metrics = self.get_metrics(
            cluster_id=cluster_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            limit=10000
        )
        
        # Group metrics by type and time
        historical_data = {
            'cluster_id': cluster_id,
            'period_days': days,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'metrics': {
                'cpu_utilization': [],
                'memory_utilization': [],
                'pod_count': [],
                'node_count': []
            },
            'patterns': self.get_patterns(cluster_id)
        }
        
        # Process metrics into time series
        for metric in metrics:
            if metric['metric_name'] == 'cpu_utilization':
                historical_data['metrics']['cpu_utilization'].append({
                    'timestamp': metric['timestamp'],
                    'value': metric['metric_value']
                })
            elif metric['metric_name'] == 'memory_utilization':
                historical_data['metrics']['memory_utilization'].append({
                    'timestamp': metric['timestamp'],
                    'value': metric['metric_value']
                })
        
        return historical_data
    
    def store_pattern(self, cluster_id: str, pattern_type: str, pattern_name: str, 
                     pattern_data: Dict[str, Any], confidence: float):
        """Store detected patterns"""
        conn = sqlite3.connect(self.patterns_db)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO patterns (cluster_id, pattern_type, pattern_name, pattern_data, confidence, detected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cluster_id, pattern_type, pattern_name, json.dumps(pattern_data), confidence, datetime.utcnow().isoformat()))
            
            conn.commit()
            logger.info(f"Stored pattern {pattern_name} for cluster {cluster_id} with confidence {confidence}")
            
        except Exception as e:
            logger.error(f"Error storing pattern: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_patterns(self, cluster_id: str, pattern_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve patterns for a cluster"""
        conn = sqlite3.connect(self.patterns_db)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT cluster_id, pattern_type, pattern_name, pattern_data, confidence, detected_at
                FROM patterns 
                WHERE cluster_id = ?
            '''
            params = [cluster_id]
            
            if pattern_type:
                query += ' AND pattern_type = ?'
                params.append(pattern_type)
            
            query += ' ORDER BY detected_at DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            patterns = []
            for row in results:
                patterns.append({
                    'cluster_id': row[0],
                    'pattern_type': row[1],
                    'pattern_name': row[2],
                    'pattern_data': json.loads(row[3]),
                    'confidence': row[4],
                    'detected_at': row[5]
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error retrieving patterns: {e}")
            return []
        finally:
            conn.close()
    
    def compress_old_data(self, days_threshold: int = None):
        """Compress data older than threshold days"""
        if days_threshold is None:
            days_threshold = self.compression_threshold_days
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        try:
            # Get old data
            cursor.execute('''
                SELECT * FROM metrics 
                WHERE timestamp < ?
                ORDER BY timestamp
            ''', (cutoff_date.isoformat(),))
            
            old_data = cursor.fetchall()
            
            if old_data:
                # Compress and store
                compressed_file = self.compressed_dir / f"metrics_{cutoff_date.strftime('%Y%m%d')}.gz"
                
                with gzip.open(compressed_file, 'wt') as f:
                    json.dump(old_data, f)
                
                # Delete old data from database
                cursor.execute('''
                    DELETE FROM metrics 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                conn.commit()
                logger.info(f"Compressed {len(old_data)} old records to {compressed_file}")
            
        except Exception as e:
            logger.error(f"Error compressing old data: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def cleanup_old_data(self, retention_days: int = None):
        """Clean up data older than retention period"""
        if retention_days is None:
            retention_days = self.retention_days
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        try:
            # Delete old metrics
            cursor.execute('''
                DELETE FROM metrics 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            # Delete old patterns
            conn2 = sqlite3.connect(self.patterns_db)
            cursor2 = conn2.cursor()
            cursor2.execute('''
                DELETE FROM patterns 
                WHERE detected_at < ?
            ''', (cutoff_date.isoformat(),))
            
            conn.commit()
            conn2.commit()
            
            logger.info(f"Cleaned up data older than {retention_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            conn.rollback()
        finally:
            conn.close()
            conn2.close()
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        try:
            # Get metrics count
            cursor.execute('SELECT COUNT(*) FROM metrics')
            metrics_count = cursor.fetchone()[0]
            
            # Get oldest and newest timestamps
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM metrics')
            time_range = cursor.fetchone()
            
            # Get disk usage
            db_size = self.metrics_db.stat().st_size if self.metrics_db.exists() else 0
            compressed_size = sum(f.stat().st_size for f in self.compressed_dir.glob('*.gz'))
            
            return {
                'metrics_count': metrics_count,
                'oldest_timestamp': time_range[0] if time_range[0] else None,
                'newest_timestamp': time_range[1] if time_range[1] else None,
                'database_size_bytes': db_size,
                'compressed_size_bytes': compressed_size,
                'total_size_bytes': db_size + compressed_size
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
        finally:
            conn.close() 