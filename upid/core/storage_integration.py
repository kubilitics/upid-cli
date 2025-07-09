"""
Storage Integration Module
Integrates DuckDB storage with UPID intelligence engines and metrics collection.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from .storage import UPIDStorage, TimeSeriesPoint, ClusterMetadata, UserSession
from .metrics_collector import KubernetesMetricsCollector
from .intelligence import IntelligenceEngine

logger = logging.getLogger(__name__)


def serialize_datetime(obj):
    """Custom JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class StorageIntegration:
    """
    Integrates UPID storage with intelligence engines and metrics collection.
    Provides seamless data persistence and retrieval for analytics.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize storage integration.
        
        Args:
            storage_path: Optional path to DuckDB database file
        """
        self.storage = UPIDStorage(storage_path)
        self.metrics_collector = KubernetesMetricsCollector()
        self.intelligence_engine = IntelligenceEngine()
        
        logger.info("Initialized UPID storage integration")
    
    async def collect_and_store_metrics(
        self,
        cluster_id: str,
        cluster_context: Optional[str] = None,
        store_historical: bool = True
    ) -> Dict[str, Any]:
        """
        Collect metrics from Kubernetes cluster and store them in DuckDB.
        
        Args:
            cluster_id: Unique cluster identifier
            cluster_context: Kubernetes cluster context
            store_historical: Whether to also store historical data
            
        Returns:
            Collection summary
        """
        try:
            logger.info(f"Collecting and storing metrics for cluster {cluster_id}")
            
            # Collect current metrics
            current_metrics = await self.metrics_collector.collect_metrics(cluster_context)
            
            # Convert to TimeSeriesPoint format
            time_series_points = []
            timestamp = datetime.now()
            
            # CPU metrics
            if 'cpu_usage' in current_metrics:
                time_series_points.append(TimeSeriesPoint(
                    timestamp=timestamp,
                    metric_name='cpu_usage_percent',
                    value=current_metrics['cpu_usage'].get('average', 0.0),
                    labels={'cluster_id': cluster_id, 'source': 'kubectl'},
                    cluster_id=cluster_id,
                    source='kubectl'
                ))
            
            # Memory metrics
            if 'memory_usage' in current_metrics:
                time_series_points.append(TimeSeriesPoint(
                    timestamp=timestamp,
                    metric_name='memory_usage_percent',
                    value=current_metrics['memory_usage'].get('average', 0.0),
                    labels={'cluster_id': cluster_id, 'source': 'kubectl'},
                    cluster_id=cluster_id,
                    source='kubectl'
                ))
            
            # Pod count
            if 'pod_count' in current_metrics:
                time_series_points.append(TimeSeriesPoint(
                    timestamp=timestamp,
                    metric_name='pod_count',
                    value=float(current_metrics['pod_count'].get('count', 0)),
                    labels={'cluster_id': cluster_id, 'source': 'kubectl'},
                    cluster_id=cluster_id,
                    source='kubectl'
                ))
            
            # Error rate
            if 'error_rate' in current_metrics:
                time_series_points.append(TimeSeriesPoint(
                    timestamp=timestamp,
                    metric_name='error_rate_percent',
                    value=current_metrics['error_rate'].get('rate', 0.0),
                    labels={'cluster_id': cluster_id, 'source': 'kubectl'},
                    cluster_id=cluster_id,
                    source='kubectl'
                ))
            
            # Prometheus metrics
            if 'prometheus' in current_metrics and 'error' not in current_metrics['prometheus']:
                prom_data = current_metrics['prometheus']
                for metric_name, metric_data in prom_data.items():
                    if isinstance(metric_data, list) and metric_data:
                        # Extract value from Prometheus result
                        value = metric_data[0].get('value', [0, 0])[1] if isinstance(metric_data[0], dict) else 0.0
                        time_series_points.append(TimeSeriesPoint(
                            timestamp=timestamp,
                            metric_name=f'prometheus_{metric_name}',
                            value=float(value),
                            labels={'cluster_id': cluster_id, 'source': 'prometheus'},
                            cluster_id=cluster_id,
                            source='prometheus'
                        ))
            
            # cAdvisor metrics
            if 'cadvisor' in current_metrics and 'error' not in current_metrics['cadvisor']:
                cadvisor_data = current_metrics['cadvisor']
                if 'container_count' in cadvisor_data:
                    time_series_points.append(TimeSeriesPoint(
                        timestamp=timestamp,
                        metric_name='cadvisor_container_count',
                        value=float(cadvisor_data['container_count']),
                        labels={'cluster_id': cluster_id, 'source': 'cadvisor'},
                        cluster_id=cluster_id,
                        source='cadvisor'
                    ))
                
                if 'avg_cpu_per_container' in cadvisor_data:
                    time_series_points.append(TimeSeriesPoint(
                        timestamp=timestamp,
                        metric_name='cadvisor_avg_cpu_per_container',
                        value=float(cadvisor_data['avg_cpu_per_container']),
                        labels={'cluster_id': cluster_id, 'source': 'cadvisor'},
                        cluster_id=cluster_id,
                        source='cadvisor'
                    ))
            
            # Store metrics in DuckDB
            if time_series_points:
                self.storage.store_metrics(cluster_id, time_series_points)
            
            # Store historical data if requested
            if store_historical:
                await self._store_historical_data(cluster_id, cluster_context)
            
            # Update cluster metadata
            await self._update_cluster_metadata(cluster_id, cluster_context)
            
            summary = {
                'cluster_id': cluster_id,
                'timestamp': timestamp.isoformat(),
                'metrics_stored': len(time_series_points),
                'sources': list(set(point.source for point in time_series_points)),
                'metric_names': list(set(point.metric_name for point in time_series_points))
            }
            
            logger.info(f"Successfully collected and stored {len(time_series_points)} metrics for cluster {cluster_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to collect and store metrics for cluster {cluster_id}: {e}")
            raise
    
    async def _store_historical_data(self, cluster_id: str, cluster_context: Optional[str] = None):
        """Store historical data for trend analysis."""
        try:
            historical_data = await self.metrics_collector.get_historical_data(cluster_context)
            timestamp = datetime.now()
            
            time_series_points = []
            
            # Store historical CPU data
            if 'cpu' in historical_data:
                for i, cpu_value in enumerate(historical_data['cpu']):
                    point_time = timestamp - timedelta(hours=len(historical_data['cpu']) - i)
                    time_series_points.append(TimeSeriesPoint(
                        timestamp=point_time,
                        metric_name='cpu_usage_percent',
                        value=float(cpu_value),
                        labels={'cluster_id': cluster_id, 'source': 'historical'},
                        cluster_id=cluster_id,
                        source='historical'
                    ))
            
            # Store historical memory data
            if 'memory' in historical_data:
                for i, mem_value in enumerate(historical_data['memory']):
                    point_time = timestamp - timedelta(hours=len(historical_data['memory']) - i)
                    time_series_points.append(TimeSeriesPoint(
                        timestamp=point_time,
                        metric_name='memory_usage_percent',
                        value=float(mem_value),
                        labels={'cluster_id': cluster_id, 'source': 'historical'},
                        cluster_id=cluster_id,
                        source='historical'
                    ))
            
            # Store historical pod count data
            if 'pods' in historical_data:
                for i, pod_count in enumerate(historical_data['pods']):
                    point_time = timestamp - timedelta(hours=len(historical_data['pods']) - i)
                    time_series_points.append(TimeSeriesPoint(
                        timestamp=point_time,
                        metric_name='pod_count',
                        value=float(pod_count),
                        labels={'cluster_id': cluster_id, 'source': 'historical'},
                        cluster_id=cluster_id,
                        source='historical'
                    ))
            
            if time_series_points:
                self.storage.store_metrics(cluster_id, time_series_points)
                logger.info(f"Stored {len(time_series_points)} historical data points for cluster {cluster_id}")
                
        except Exception as e:
            logger.error(f"Failed to store historical data for cluster {cluster_id}: {e}")
    
    async def _update_cluster_metadata(self, cluster_id: str, cluster_context: Optional[str] = None):
        """Update cluster metadata."""
        try:
            # Get current cluster info
            cluster_info = await self._get_cluster_info(cluster_context)
            
            cluster_metadata = ClusterMetadata(
                cluster_id=cluster_id,
                name=cluster_info.get('name', cluster_id),
                provider=cluster_info.get('provider', 'unknown'),
                region=cluster_info.get('region', 'unknown'),
                created_at=datetime.now(),
                last_seen=datetime.now(),
                config=cluster_info
            )
            
            self.storage.store_cluster_metadata(cluster_metadata)
            
        except Exception as e:
            logger.error(f"Failed to update cluster metadata for cluster {cluster_id}: {e}")
    
    async def _get_cluster_info(self, cluster_context: Optional[str] = None) -> Dict[str, Any]:
        """Get basic cluster information."""
        try:
            # This would typically query kubectl for cluster info
            # For now, return basic info
            return {
                'name': cluster_context or 'default',
                'provider': 'local',  # Would detect from kubectl context
                'region': 'local',
                'version': '1.0.0',
                'nodes': 1
            }
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            return {
                'name': 'unknown',
                'provider': 'unknown',
                'region': 'unknown'
            }
    
    async def run_intelligence_with_storage(
        self,
        cluster_id: str,
        cluster_context: Optional[str] = None,
        include_historical: bool = True
    ) -> Dict[str, Any]:
        """
        Run intelligence analysis with stored historical data.
        
        Args:
            cluster_id: Cluster identifier
            cluster_context: Kubernetes cluster context
            include_historical: Whether to include historical data in analysis
            
        Returns:
            Intelligence analysis results
        """
        try:
            logger.info(f"Running intelligence analysis with storage for cluster {cluster_id}")
            
            # Collect and store current metrics
            collection_summary = await self.collect_and_store_metrics(
                cluster_id, cluster_context, store_historical=True
            )
            
            # Get historical data from storage
            historical_metrics = {}
            if include_historical:
                # Get last 30 days of data
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)
                
                cpu_metrics = self.storage.get_metrics(
                    cluster_id, 'cpu_usage_percent', start_time, end_time
                )
                memory_metrics = self.storage.get_metrics(
                    cluster_id, 'memory_usage_percent', start_time, end_time
                )
                pod_metrics = self.storage.get_metrics(
                    cluster_id, 'pod_count', start_time, end_time
                )
                
                historical_metrics = {
                    'cpu': [m.value for m in cpu_metrics],
                    'memory': [m.value for m in memory_metrics],
                    'pods': [m.value for m in pod_metrics]
                }
            
            # Run intelligence analysis
            intelligence_report = await self.intelligence_engine.run_comprehensive_analysis(
                cluster_context=cluster_context
            )
            
            # Store audit log with proper datetime serialization
            audit_details = {
                'collection_summary': collection_summary,
                'historical_data_points': sum(len(v) for v in historical_metrics.values()),
                'intelligence_insights': len(intelligence_report.business_insights),
                'predictions': len(intelligence_report.predictions),
                'optimizations': len(intelligence_report.optimizations)
            }
            
            self.storage.log_audit_event(
                user_id='system',
                action='intelligence_analysis',
                resource_type='cluster',
                resource_id=cluster_id,
                details=audit_details
            )
            
            result = {
                'cluster_id': cluster_id,
                'collection_summary': collection_summary,
                'intelligence_report': intelligence_report.summary,
                'storage_stats': self.storage.get_storage_stats()
            }
            
            logger.info(f"Completed intelligence analysis with storage for cluster {cluster_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to run intelligence with storage for cluster {cluster_id}: {e}")
            raise
    
    def get_storage_analytics(
        self,
        cluster_id: str,
        metric_name: str,
        days: int = 30,
        aggregation: str = 'avg'
    ) -> Dict[str, Any]:
        """
        Get analytics from stored data.
        
        Args:
            cluster_id: Cluster identifier
            metric_name: Metric name to analyze
            days: Number of days to analyze
            aggregation: Aggregation function
            
        Returns:
            Analytics results
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Get raw metrics
            raw_metrics = self.storage.get_metrics(
                cluster_id, metric_name, start_time, end_time
            )
            
            # Get aggregated metrics
            aggregated_metrics = self.storage.get_aggregated_metrics(
                cluster_id, metric_name, aggregation, '1 day', start_time, end_time
            )
            
            # Calculate statistics
            values = [m.value for m in raw_metrics]
            if values:
                stats = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values),
                    'latest': values[0] if values else 0
                }
            else:
                stats = {'min': 0, 'max': 0, 'avg': 0, 'count': 0, 'latest': 0}
            
            return {
                'cluster_id': cluster_id,
                'metric_name': metric_name,
                'period_days': days,
                'raw_metrics_count': len(raw_metrics),
                'aggregated_points': len(aggregated_metrics),
                'statistics': stats,
                'aggregated_data': aggregated_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage analytics for cluster {cluster_id}: {e}")
            raise
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to manage storage size."""
        try:
            self.storage.cleanup_old_data(days_to_keep)
            logger.info(f"Cleaned up data older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """Get comprehensive storage summary."""
        try:
            stats = self.storage.get_storage_stats()
            clusters = self.storage.list_clusters()
            
            return {
                'storage_stats': stats,
                'clusters': [
                    {
                        'cluster_id': cluster.cluster_id,
                        'name': cluster.name,
                        'provider': cluster.provider,
                        'region': cluster.region,
                        'last_seen': cluster.last_seen.isoformat()
                    }
                    for cluster in clusters
                ],
                'database_path': self.storage.db_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage summary: {e}")
            raise
    
    def close(self):
        """Close storage connection."""
        self.storage.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 