#!/usr/bin/env python3
"""
Test script for UPID Intelligence Engine
Demonstrates time-series data collection and pattern analysis
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid.core.data_store import TimeSeriesDataStore
from upid.core.analytics import PatternAnalyzer

def generate_sample_data():
    """Generate sample metrics data for testing"""
    base_time = datetime.utcnow() - timedelta(days=30)
    
    # Generate CPU utilization with business hours pattern
    cpu_data = []
    for i in range(720):  # 30 days * 24 hours
        timestamp = base_time + timedelta(hours=i)
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Business hours pattern (9 AM - 6 PM, Mon-Fri)
        if 9 <= hour <= 18 and day_of_week < 5:  # Business hours
            base_usage = 60 + (hour - 9) * 2  # Higher during business hours
        else:
            base_usage = 20  # Lower during off-hours
        
        # Add some noise
        import random
        noise = random.uniform(-10, 10)
        usage = max(0, min(100, base_usage + noise))
        
        cpu_data.append({
            'timestamp': timestamp.isoformat(),
            'value': usage
        })
    
    # Generate memory utilization with slight upward trend (potential memory leak)
    memory_data = []
    for i in range(720):
        timestamp = base_time + timedelta(hours=i)
        
        # Upward trend with some noise
        base_usage = 40 + (i / 720) * 20  # Gradual increase
        noise = random.uniform(-5, 5)
        usage = max(0, min(100, base_usage + noise))
        
        memory_data.append({
            'timestamp': timestamp.isoformat(),
            'value': usage
        })
    
    return {
        'cpu_utilization': cpu_data,
        'memory_utilization': memory_data
    }

def test_intelligence_engine():
    """Test the intelligence engine with sample data"""
    print("🧠 Testing UPID Intelligence Engine")
    print("=" * 50)
    
    # Initialize components
    data_store = TimeSeriesDataStore()
    pattern_analyzer = PatternAnalyzer()
    
    # Generate sample data
    print("📊 Generating sample metrics data...")
    sample_data = generate_sample_data()
    
    # Store sample data
    cluster_id = "test-cluster-001"
    print(f"💾 Storing data for cluster: {cluster_id}")
    
    # Store CPU metrics
    for point in sample_data['cpu_utilization']:
        metrics = {
            'resources': {
                'cpu': {'used': point['value'] / 100, 'total': 1.0}
            }
        }
        data_store.store_metrics(cluster_id, metrics, point['timestamp'])
    
    # Store memory metrics
    for point in sample_data['memory_utilization']:
        metrics = {
            'resources': {
                'memory': {'used': point['value'] / 100, 'total': 1.0}
            }
        }
        data_store.store_metrics(cluster_id, metrics, point['timestamp'])
    
    print(f"✅ Stored {len(sample_data['cpu_utilization'])} data points")
    
    # Get historical data for analysis
    print("🔍 Retrieving historical data for analysis...")
    historical_data = data_store.get_historical_data(cluster_id, days=30)
    
    # Run pattern analysis
    print("🧠 Running pattern analysis...")
    analysis = pattern_analyzer.analyze_historical_data(historical_data)
    
    # Display results
    print("\n📈 Analysis Results:")
    print("-" * 30)
    
    # Patterns detected
    if analysis.get('patterns'):
        print("\n🎯 Detected Patterns:")
        for resource, patterns in analysis['patterns'].items():
            print(f"\n{resource.upper()}:")
            for pattern_name, pattern_data in patterns.items():
                if isinstance(pattern_data, dict) and 'confidence' in pattern_data:
                    print(f"  • {pattern_name}: {pattern_data['confidence']:.1f}% confidence")
    
    # Trends
    if analysis.get('trends'):
        print("\n📊 Usage Trends:")
        for resource, trend in analysis['trends'].items():
            if trend:
                direction_icon = "📈" if trend['direction'] == 'increasing' else "📉" if trend['direction'] == 'decreasing' else "➡️"
                print(f"  • {resource.upper()}: {direction_icon} {trend['direction']} (confidence: {trend['confidence']:.1f}%)")
    
    # Anomalies
    if analysis.get('anomalies'):
        print("\n⚠️  Detected Anomalies:")
        for resource, anomalies in analysis['anomalies'].items():
            print(f"  • {resource.upper()}: {len(anomalies)} anomalies")
    
    # Recommendations
    if analysis.get('recommendations'):
        print("\n💡 Optimization Recommendations:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"  {i}. {priority_icon} {rec['type'].replace('_', ' ').title()}")
            print(f"     {rec['description']}")
            print(f"     Confidence: {rec['confidence']:.1f}%")
            print(f"     Potential Savings: {rec['potential_savings']*100:.1f}%")
    
    # Storage statistics
    storage_stats = data_store.get_storage_stats()
    print(f"\n💾 Storage Statistics:")
    print(f"  • Total metrics: {storage_stats.get('metrics_count', 0)}")
    print(f"  • Database size: {storage_stats.get('database_size_bytes', 0) / 1024:.1f} KB")
    print(f"  • Data range: {storage_stats.get('oldest_timestamp', 'N/A')[:10]} to {storage_stats.get('newest_timestamp', 'N/A')[:10]}")
    
    print("\n✅ Intelligence Engine test completed successfully!")

if __name__ == "__main__":
    test_intelligence_engine() 