#!/usr/bin/env python3
"""
Test Storage System
Comprehensive tests for UPID storage system using DuckDB.
"""

import asyncio
import os
import sys
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

# Add the project root to the path
sys.path.insert(0, '.')

from upid.core.storage import UPIDStorage, TimeSeriesPoint, ClusterMetadata, UserSession
from upid.core.storage_integration import StorageIntegration


async def test_storage_system():
    """Test the complete storage system."""
    print("💾 Testing UPID Storage System...")
    
    # Create a unique file path for the DuckDB database (do not pre-create the file)
    db_path = os.path.join(tempfile.gettempdir(), f"upid_test_{uuid.uuid4().hex}.duckdb")
    
    try:
        # Test 1: Basic Storage Operations
        print("\n1. 🔧 Testing Basic Storage Operations...")
        await test_basic_storage_operations(db_path)
        
        # Test 2: Time-Series Data
        print("\n2. 📊 Testing Time-Series Data...")
        await test_time_series_data(db_path)
        
        # Test 3: Cluster Metadata
        print("\n3. 🏢 Testing Cluster Metadata...")
        await test_cluster_metadata(db_path)
        
        # Test 4: User Sessions
        print("\n4. 👤 Testing User Sessions...")
        await test_user_sessions(db_path)
        
        # Test 5: Audit Logging
        print("\n5. 📋 Testing Audit Logging...")
        await test_audit_logging(db_path)
        
        # Test 6: Analytics and Aggregation
        print("\n6. 📈 Testing Analytics and Aggregation...")
        await test_analytics_and_aggregation(db_path)
        
        # Test 7: Storage Integration
        print("\n7. 🔗 Testing Storage Integration...")
        await test_storage_integration(db_path)
        
        # Test 8: Data Cleanup
        print("\n8. 🧹 Testing Data Cleanup...")
        await test_data_cleanup(db_path)
        
        print("\n✅ All storage system tests passed!")
        
    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)


async def test_basic_storage_operations(db_path: str):
    """Test basic storage operations."""
    with UPIDStorage(db_path) as storage:
        # Test storage initialization
        assert storage.connection is not None
        print("  ✅ Storage initialization successful")
        
        # Test storage stats
        stats = storage.get_storage_stats()
        assert isinstance(stats, dict)
        assert 'total_metrics' in stats
        assert 'total_clusters' in stats
        print("  ✅ Storage stats retrieval successful")
        
        # Test database path
        assert storage.db_path == db_path
        print("  ✅ Database path configuration correct")


async def test_time_series_data(db_path: str):
    """Test time-series data operations."""
    with UPIDStorage(db_path) as storage:
        cluster_id = "test-cluster-1"
        timestamp = datetime.now()
        
        # Create test metrics
        metrics = [
            TimeSeriesPoint(
                timestamp=timestamp,
                metric_name="cpu_usage_percent",
                value=75.5,
                labels={"cluster_id": cluster_id, "source": "kubectl"},
                cluster_id=cluster_id,
                source="kubectl"
            ),
            TimeSeriesPoint(
                timestamp=timestamp,
                metric_name="memory_usage_percent",
                value=82.3,
                labels={"cluster_id": cluster_id, "source": "kubectl"},
                cluster_id=cluster_id,
                source="kubectl"
            ),
            TimeSeriesPoint(
                timestamp=timestamp,
                metric_name="pod_count",
                value=12.0,
                labels={"cluster_id": cluster_id, "source": "kubectl"},
                cluster_id=cluster_id,
                source="kubectl"
            )
        ]
        
        # Store metrics
        storage.store_metrics(cluster_id, metrics)
        print("  ✅ Metrics storage successful")
        
        # Retrieve metrics
        retrieved_metrics = storage.get_metrics(cluster_id)
        assert len(retrieved_metrics) == 3
        print("  ✅ Metrics retrieval successful")
        
        # Test metric filtering
        cpu_metrics = storage.get_metrics(cluster_id, metric_name="cpu_usage_percent")
        assert len(cpu_metrics) == 1
        assert cpu_metrics[0].value == 75.5
        print("  ✅ Metric filtering successful")
        
        # Test time filtering
        start_time = timestamp - timedelta(minutes=5)
        end_time = timestamp + timedelta(minutes=5)
        time_filtered_metrics = storage.get_metrics(
            cluster_id, start_time=start_time, end_time=end_time
        )
        assert len(time_filtered_metrics) == 3
        print("  ✅ Time filtering successful")


async def test_cluster_metadata(db_path: str):
    """Test cluster metadata operations."""
    with UPIDStorage(db_path) as storage:
        # Create test cluster metadata
        cluster_metadata = ClusterMetadata(
            cluster_id="test-cluster-1",
            name="Test Cluster",
            provider="aws",
            region="us-west-2",
            created_at=datetime.now(),
            last_seen=datetime.now(),
            config={"version": "1.24", "nodes": 3}
        )
        
        # Store cluster metadata
        storage.store_cluster_metadata(cluster_metadata)
        print("  ✅ Cluster metadata storage successful")
        
        # Retrieve cluster metadata
        retrieved_cluster = storage.get_cluster_metadata("test-cluster-1")
        assert retrieved_cluster is not None
        assert retrieved_cluster.name == "Test Cluster"
        assert retrieved_cluster.provider == "aws"
        print("  ✅ Cluster metadata retrieval successful")
        
        # List clusters
        clusters = storage.list_clusters()
        assert len(clusters) == 1
        assert clusters[0].cluster_id == "test-cluster-1"
        print("  ✅ Cluster listing successful")


async def test_user_sessions(db_path: str):
    """Test user session operations."""
    with UPIDStorage(db_path) as storage:
        # Create test user session
        session = UserSession(
            session_id="test-session-1",
            user_id="test-user",
            cluster_id="test-cluster-1",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24),
            permissions=["read", "write"]
        )
        
        # Store user session
        storage.store_user_session(session)
        print("  ✅ User session storage successful")
        
        # Retrieve user session
        retrieved_session = storage.get_user_session("test-session-1")
        assert retrieved_session is not None
        assert retrieved_session.user_id == "test-user"
        assert "read" in retrieved_session.permissions
        print("  ✅ User session retrieval successful")


async def test_audit_logging(db_path: str):
    """Test audit logging operations."""
    with UPIDStorage(db_path) as storage:
        # Log audit events
        storage.log_audit_event(
            user_id="test-user",
            action="cluster_access",
            resource_type="cluster",
            resource_id="test-cluster-1",
            details={"ip": "192.168.1.1", "user_agent": "upid-cli"}
        )
        
        storage.log_audit_event(
            user_id="test-user",
            action="metrics_collection",
            resource_type="metrics",
            resource_id="test-cluster-1",
            details={"metrics_count": 5, "sources": ["kubectl", "prometheus"]}
        )
        
        print("  ✅ Audit event logging successful")
        
        # Retrieve audit log
        audit_entries = storage.get_audit_log(limit=10)
        assert len(audit_entries) >= 2
        print("  ✅ Audit log retrieval successful")
        
        # Test audit log filtering
        user_audit_entries = storage.get_audit_log(user_id="test-user")
        assert len(user_audit_entries) >= 2
        print("  ✅ Audit log filtering successful")


async def test_analytics_and_aggregation(db_path: str):
    """Test analytics and aggregation features."""
    # Use StorageIntegration for analytics
    with StorageIntegration(db_path) as integration:
        cluster_id = "test-cluster-2"
        # Create historical data for analytics
        base_time = datetime.now()
        for i in range(24):  # 24 hours of data
            timestamp = base_time - timedelta(hours=i)
            metrics = [
                TimeSeriesPoint(
                    timestamp=timestamp,
                    metric_name="cpu_usage_percent",
                    value=70.0 + (i % 10),  # Varying values
                    labels={"cluster_id": cluster_id},
                    cluster_id=cluster_id,
                    source="kubectl"
                )
            ]
            integration.storage.store_metrics(cluster_id, metrics)
        print("  ✅ Historical data creation successful")
        # Test analytics
        analytics = integration.get_storage_analytics(
            cluster_id=cluster_id,
            metric_name="cpu_usage_percent",
            days=1,
            aggregation="avg"
        )
        assert analytics['cluster_id'] == cluster_id
        assert analytics['metric_name'] == "cpu_usage_percent"
        assert analytics['raw_metrics_count'] >= 24
        print("  ✅ Analytics calculation successful")
        # Test aggregated metrics
        aggregated = integration.storage.get_aggregated_metrics(
            cluster_id=cluster_id,
            metric_name="cpu_usage_percent",
            aggregation="avg",
            interval="1 hour"
        )
        assert len(aggregated) > 0
        print("  ✅ Aggregated metrics successful")


async def test_storage_integration(db_path: str):
    """Test storage integration with intelligence engines."""
    with StorageIntegration(db_path) as integration:
        # Test storage summary
        summary = integration.get_storage_summary()
        assert isinstance(summary, dict)
        assert 'storage_stats' in summary
        assert 'clusters' in summary
        print("  ✅ Storage integration summary successful")
        
        # Test data cleanup
        integration.cleanup_old_data(days_to_keep=1)
        print("  ✅ Data cleanup successful")


async def test_data_cleanup(db_path: str):
    """Test data cleanup functionality."""
    with UPIDStorage(db_path) as storage:
        # Create old data
        old_timestamp = datetime.now() - timedelta(days=100)
        old_metrics = [
            TimeSeriesPoint(
                timestamp=old_timestamp,
                metric_name="old_metric",
                value=50.0,
                labels={"cluster_id": "old-cluster"},
                cluster_id="old-cluster",
                source="test"
            )
        ]
        storage.store_metrics("old-cluster", old_metrics)
        
        # Create recent data
        recent_timestamp = datetime.now()
        recent_metrics = [
            TimeSeriesPoint(
                timestamp=recent_timestamp,
                metric_name="recent_metric",
                value=75.0,
                labels={"cluster_id": "recent-cluster"},
                cluster_id="recent-cluster",
                source="test"
            )
        ]
        storage.store_metrics("recent-cluster", recent_metrics)
        
        # Test cleanup
        storage.cleanup_old_data(days_to_keep=90)
        
        # Verify old data is removed but recent data remains
        old_metrics_after = storage.get_metrics("old-cluster")
        recent_metrics_after = storage.get_metrics("recent-cluster")
        
        assert len(old_metrics_after) == 0  # Old data should be cleaned up
        assert len(recent_metrics_after) == 1  # Recent data should remain
        print("  ✅ Data cleanup verification successful")


async def main():
    """Run all storage system tests."""
    print("🚀 Starting UPID Storage System Tests\n")
    
    try:
        await test_storage_system()
        print("\n🎉 All storage system tests completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Storage system tests failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 