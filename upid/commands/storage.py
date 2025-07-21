"""
Storage CLI Commands
Commands for managing UPID storage, data collection, and analytics.
"""

import asyncio
import click
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ..core.storage_integration import StorageIntegration


@click.group()
def storage():
    """Storage and data management commands."""
    pass


@storage.command()
@click.option('--cluster-id', '-c', required=True, help='Cluster identifier')
@click.option('--cluster-context', help='Kubernetes cluster context')
@click.option('--store-historical', is_flag=True, default=True, help='Store historical data')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def collect(cluster_id: str, cluster_context: Optional[str], store_historical: bool, output: str):
    """Collect and store metrics from Kubernetes cluster."""
    click.echo("📊 Collecting and storing metrics...")
    
    try:
        with StorageIntegration() as storage_integration:
            summary = await storage_integration.collect_and_store_metrics(
                cluster_id=cluster_id,
                cluster_context=cluster_context,
                store_historical=store_historical
            )
            
            if output == 'json':
                click.echo(json.dumps(summary, indent=2, default=str))
            else:
                _display_collection_summary(summary)
                
    except Exception as e:
        click.echo(f"❌ Error collecting metrics: {e}")


@storage.command()
@click.option('--cluster-id', '-c', required=True, help='Cluster identifier')
@click.option('--cluster-context', help='Kubernetes cluster context')
@click.option('--include-historical', is_flag=True, default=True, help='Include historical data in analysis')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def analyze(cluster_id: str, cluster_context: Optional[str], include_historical: bool, output: str):
    """Run intelligence analysis with stored data."""
    click.echo("🧠 Running intelligence analysis with storage...")
    
    try:
        with StorageIntegration() as storage_integration:
            result = await storage_integration.run_intelligence_with_storage(
                cluster_id=cluster_id,
                cluster_context=cluster_context,
                include_historical=include_historical
            )
            
            if output == 'json':
                click.echo(json.dumps(result, indent=2, default=str))
            else:
                _display_intelligence_with_storage_summary(result)
                
    except Exception as e:
        click.echo(f"❌ Error running intelligence analysis: {e}")


@storage.command()
@click.option('--cluster-id', '-c', required=True, help='Cluster identifier')
@click.option('--metric-name', '-m', required=True, help='Metric name to analyze')
@click.option('--days', '-d', default=30, help='Number of days to analyze')
@click.option('--aggregation', '-a', default='avg', type=click.Choice(['avg', 'sum', 'min', 'max', 'count']), help='Aggregation function')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def analytics(cluster_id: str, metric_name: str, days: int, aggregation: str, output: str):
    """Get analytics from stored data."""
    click.echo(f"📈 Analyzing {metric_name} for cluster {cluster_id}...")
    
    try:
        with StorageIntegration() as storage_integration:
            analytics_result = storage_integration.get_storage_analytics(
                cluster_id=cluster_id,
                metric_name=metric_name,
                days=days,
                aggregation=aggregation
            )
            
            if output == 'json':
                click.echo(json.dumps(analytics_result, indent=2, default=str))
            else:
                _display_analytics_summary(analytics_result)
                
    except Exception as e:
        click.echo(f"❌ Error getting analytics: {e}")


@storage.command()
@click.option('--days-to-keep', '-d', default=90, help='Number of days of data to keep')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned up without actually doing it')
async def cleanup(days_to_keep: int, dry_run: bool):
    """Clean up old data to manage storage size."""
    if dry_run:
        click.echo(f"🔍 Dry run: Would clean up data older than {days_to_keep} days")
    else:
        click.echo(f"🧹 Cleaning up data older than {days_to_keep} days...")
    
    try:
        with StorageIntegration() as storage_integration:
            if not dry_run:
                storage_integration.cleanup_old_data(days_to_keep)
                click.echo("✅ Cleanup completed successfully")
            else:
                # Show what would be cleaned up
                stats = storage_integration.storage.get_storage_stats()
                click.echo(f"📊 Current storage stats:")
                click.echo(f"  • Total metrics: {stats.get('total_metrics', 0)}")
                click.echo(f"  • Database size: {stats.get('database_size_mb', 0):.2f} MB")
                click.echo(f"  • Audit entries: {stats.get('audit_entries', 0)}")
                
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")


@storage.command()
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def status(output: str):
    """Show storage status and statistics."""
    click.echo("📊 Getting storage status...")
    
    try:
        with StorageIntegration() as storage_integration:
            summary = storage_integration.get_storage_summary()
            
            if output == 'json':
                click.echo(json.dumps(summary, indent=2, default=str))
            else:
                _display_storage_status(summary)
                
    except Exception as e:
        click.echo(f"❌ Error getting storage status: {e}")


@storage.command()
@click.option('--cluster-id', '-c', help='Cluster identifier (optional)')
@click.option('--start-time', help='Start time for audit log (YYYY-MM-DD HH:MM:SS)')
@click.option('--end-time', help='End time for audit log (YYYY-MM-DD HH:MM:SS)')
@click.option('--limit', '-l', default=50, help='Maximum number of entries to show')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'summary']), default='summary', help='Output format')
async def audit_log(cluster_id: Optional[str], start_time: Optional[str], end_time: Optional[str], limit: int, output: str):
    """Show audit log entries."""
    click.echo("📋 Getting audit log...")
    
    try:
        with StorageIntegration() as storage_integration:
            # Parse time parameters
            start_dt = None
            end_dt = None
            
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace(' ', 'T'))
            if end_time:
                end_dt = datetime.fromisoformat(end_time.replace(' ', 'T'))
            
            audit_entries = storage_integration.storage.get_audit_log(
                user_id=None,  # Could add user_id parameter if needed
                start_time=start_dt,
                end_time=end_dt,
                limit=limit
            )
            
            if output == 'json':
                click.echo(json.dumps(audit_entries, indent=2, default=str))
            else:
                _display_audit_log(audit_entries)
                
    except Exception as e:
        click.echo(f"❌ Error getting audit log: {e}")


def _display_collection_summary(summary: Dict[str, Any]):
    """Display metrics collection summary."""
    click.echo("\n" + "="*60)
    click.echo("📊 METRICS COLLECTION SUMMARY")
    click.echo("="*60)
    
    click.echo(f"Cluster ID: {summary.get('cluster_id', 'N/A')}")
    click.echo(f"Timestamp: {summary.get('timestamp', 'N/A')}")
    click.echo(f"Metrics Stored: {summary.get('metrics_stored', 0)}")
    click.echo(f"Sources: {', '.join(summary.get('sources', []))}")
    click.echo(f"Metric Names: {', '.join(summary.get('metric_names', []))}")


def _display_intelligence_with_storage_summary(result: Dict[str, Any]):
    """Display intelligence analysis with storage summary."""
    click.echo("\n" + "="*60)
    click.echo("🧠 INTELLIGENCE ANALYSIS WITH STORAGE")
    click.echo("="*60)
    
    collection_summary = result.get('collection_summary', {})
    intelligence_report = result.get('intelligence_report', {})
    storage_stats = result.get('storage_stats', {})
    
    click.echo(f"Cluster ID: {result.get('cluster_id', 'N/A')}")
    click.echo(f"Metrics Collected: {collection_summary.get('metrics_stored', 0)}")
    click.echo(f"Sources: {', '.join(collection_summary.get('sources', []))}")
    
    click.echo(f"\n📈 Intelligence Results:")
    click.echo(f"  • Business Insights: {len(intelligence_report.get('business_insights', []))}")
    click.echo(f"  • Predictions: {len(intelligence_report.get('predictions', []))}")
    click.echo(f"  • Anomalies: {len(intelligence_report.get('anomalies', []))}")
    click.echo(f"  • Optimizations: {len(intelligence_report.get('optimizations', []))}")
    
    click.echo(f"\n💾 Storage Stats:")
    click.echo(f"  • Total Metrics: {storage_stats.get('total_metrics', 0)}")
    click.echo(f"  • Database Size: {storage_stats.get('database_size_mb', 0):.2f} MB")
    click.echo(f"  • Clusters: {storage_stats.get('total_clusters', 0)}")


def _display_analytics_summary(analytics: Dict[str, Any]):
    """Display analytics summary."""
    click.echo("\n" + "="*60)
    click.echo("📈 STORAGE ANALYTICS SUMMARY")
    click.echo("="*60)
    
    click.echo(f"Cluster ID: {analytics.get('cluster_id', 'N/A')}")
    click.echo(f"Metric Name: {analytics.get('metric_name', 'N/A')}")
    click.echo(f"Period: {analytics.get('period_days', 0)} days")
    click.echo(f"Raw Metrics: {analytics.get('raw_metrics_count', 0)}")
    click.echo(f"Aggregated Points: {analytics.get('aggregated_points', 0)}")
    
    stats = analytics.get('statistics', {})
    click.echo(f"\n📊 Statistics:")
    click.echo(f"  • Min: {stats.get('min', 0):.2f}")
    click.echo(f"  • Max: {stats.get('max', 0):.2f}")
    click.echo(f"  • Average: {stats.get('avg', 0):.2f}")
    click.echo(f"  • Count: {stats.get('count', 0)}")
    click.echo(f"  • Latest: {stats.get('latest', 0):.2f}")


def _display_storage_status(summary: Dict[str, Any]):
    """Display storage status."""
    click.echo("\n" + "="*60)
    click.echo("💾 STORAGE STATUS")
    click.echo("="*60)
    
    storage_stats = summary.get('storage_stats', {})
    clusters = summary.get('clusters', [])
    
    click.echo(f"Database Path: {summary.get('database_path', 'N/A')}")
    click.echo(f"Total Metrics: {storage_stats.get('total_metrics', 0)}")
    click.echo(f"Unique Metrics: {storage_stats.get('unique_metrics', 0)}")
    click.echo(f"Clusters with Metrics: {storage_stats.get('clusters_with_metrics', 0)}")
    click.echo(f"Total Clusters: {storage_stats.get('total_clusters', 0)}")
    click.echo(f"Active Sessions: {storage_stats.get('active_sessions', 0)}")
    click.echo(f"Audit Entries: {storage_stats.get('audit_entries', 0)}")
    click.echo(f"Database Size: {storage_stats.get('database_size_mb', 0):.2f} MB")
    
    if clusters:
        click.echo(f"\n📊 Clusters:")
        for cluster in clusters:
            click.echo(f"  • {cluster.get('name', 'N/A')} ({cluster.get('cluster_id', 'N/A')})")
            click.echo(f"    Provider: {cluster.get('provider', 'N/A')}")
            click.echo(f"    Region: {cluster.get('region', 'N/A')}")
            click.echo(f"    Last Seen: {cluster.get('last_seen', 'N/A')}")


def _display_audit_log(audit_entries: List[Dict[str, Any]]):
    """Display audit log entries."""
    click.echo("\n" + "="*60)
    click.echo("📋 AUDIT LOG")
    click.echo("="*60)
    
    if not audit_entries:
        click.echo("No audit log entries found.")
        return
    
    for entry in audit_entries:
        click.echo(f"Timestamp: {entry.get('timestamp', 'N/A')}")
        click.echo(f"User: {entry.get('user_id', 'N/A')}")
        click.echo(f"Action: {entry.get('action', 'N/A')}")
        click.echo(f"Resource: {entry.get('resource_type', 'N/A')} - {entry.get('resource_id', 'N/A')}")
        
        details = entry.get('details', {})
        if details:
            click.echo(f"Details: {json.dumps(details, indent=2)}")
        
        click.echo("-" * 40) 