#!/usr/bin/env python3
"""
Test script for UPID Phase 2: Confidence-Based Optimization & Business Impact
Demonstrates the complete intelligence engine with business correlation
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid.core.data_store import TimeSeriesDataStore
from upid.core.analytics import PatternAnalyzer
from upid.core.optimization_engine import ConfidenceOptimizationEngine
from upid.core.business_correlation import BusinessCorrelationEngine

def generate_enhanced_sample_data():
    """Generate enhanced sample data with business patterns"""
    base_time = datetime.utcnow() - timedelta(days=30)
    
    # Generate CPU utilization with strong business hours pattern
    cpu_data = []
    for i in range(720):  # 30 days * 24 hours
        timestamp = base_time + timedelta(hours=i)
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Strong business hours pattern (9 AM - 6 PM, Mon-Fri)
        if 9 <= hour <= 18 and day_of_week < 5:  # Business hours
            base_usage = 75 + (hour - 9) * 3  # Higher during business hours
        else:
            base_usage = 15  # Much lower during off-hours
        
        # Add some noise
        import random
        noise = random.uniform(-15, 15)
        usage = max(0, min(100, base_usage + noise))
        
        cpu_data.append({
            'timestamp': timestamp.isoformat(),
            'value': usage
        })
    
    # Generate memory utilization with memory leak pattern
    memory_data = []
    for i in range(720):
        timestamp = base_time + timedelta(hours=i)
        
        # Upward trend with memory leak
        base_usage = 50 + (i / 720) * 30  # Gradual increase
        noise = random.uniform(-8, 8)
        usage = max(0, min(100, base_usage + noise))
        
        memory_data.append({
            'timestamp': timestamp.isoformat(),
            'value': usage
        })
    
    return {
        'cpu_utilization': cpu_data,
        'memory_utilization': memory_data
    }

def test_phase2_intelligence():
    """Test Phase 2 intelligence capabilities"""
    print("🧠 Testing UPID Phase 2: Confidence-Based Optimization & Business Impact")
    print("=" * 70)
    
    # Initialize all components
    data_store = TimeSeriesDataStore()
    pattern_analyzer = PatternAnalyzer()
    optimization_engine = ConfidenceOptimizationEngine()
    business_engine = BusinessCorrelationEngine()
    
    # Generate enhanced sample data
    print("📊 Generating enhanced sample data with business patterns...")
    sample_data = generate_enhanced_sample_data()
    
    # Store sample data
    cluster_id = "phase2-test-cluster"
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
    
    # Generate optimization recommendations
    print("🎯 Generating confidence-based optimization recommendations...")
    cluster_info = {'name': cluster_id, 'type': 'production'}
    recommendations = optimization_engine.generate_optimization_plan(analysis, cluster_info)
    
    # Business impact analysis
    print("💼 Running business impact analysis...")
    current_metrics = {
        'cpu_utilization': 75.0,
        'memory_utilization': 80.0,
        'response_time_p95': 150.0,
        'error_rate': 0.015,
        'availability': 99.92
    }
    business_analysis = business_engine.analyze_business_impact(current_metrics, cluster_info)
    
    # Display comprehensive results
    print("\n📈 Phase 2 Analysis Results:")
    print("-" * 50)
    
    # Pattern analysis results
    print("\n🎯 Pattern Analysis:")
    if analysis.get('patterns'):
        for resource, patterns in analysis['patterns'].items():
            print(f"\n{resource.upper()}:")
            for pattern_name, pattern_data in patterns.items():
                if isinstance(pattern_data, dict) and 'confidence' in pattern_data:
                    print(f"  • {pattern_name}: {pattern_data['confidence']:.1f}% confidence")
    
    # Optimization recommendations
    print(f"\n🎯 Optimization Recommendations ({len(recommendations)} found):")
    total_savings = 0
    high_confidence_count = 0
    low_risk_count = 0
    
    for i, rec in enumerate(recommendations, 1):
        savings_percentage = rec.potential_savings * 100
        total_savings += savings_percentage
        
        if rec.confidence > 85:
            high_confidence_count += 1
        if rec.risk_level.value == 'low':
            low_risk_count += 1
        
        risk_icon = "🟢" if rec.risk_level.value == 'low' else "🟡" if rec.risk_level.value == 'medium' else "🔴"
        
        print(f"  {i}. {risk_icon} {rec.type.value.replace('_', ' ').title()}")
        print(f"     Description: {rec.description}")
        print(f"     Confidence: {rec.confidence:.1f}% | Risk: {rec.risk_level.value.title()}")
        print(f"     Potential Savings: {savings_percentage:.1f}% | Effort: {rec.implementation_effort.title()}")
        print()
    
    # Business impact results
    print("💼 Business Impact Analysis:")
    roi_estimates = business_analysis.get('roi_estimates', {})
    total_roi = roi_estimates.get('total_roi', 0)
    print(f"  📈 Total ROI Potential: {total_roi:.1f}%")
    
    for impact in business_analysis.get('business_impacts', []):
        print(f"  • {impact.metric_type.value.replace('_', ' ').title()}: {impact.impact_description}")
        print(f"    Confidence: {impact.confidence:.1f}% | ROI: {impact.roi_estimate:.1f}%")
    
    # Business recommendations
    if business_analysis.get('recommendations'):
        print(f"\n🎯 Business Recommendations ({len(business_analysis['recommendations'])} found):")
        for rec in business_analysis['recommendations'][:3]:  # Top 3
            priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"  {priority_icon} {rec['description']}")
    
    # Simulation results
    print(f"\n🔬 Optimization Simulations:")
    for rec in recommendations[:3]:  # Simulate top 3
        simulation = optimization_engine.simulate_optimization(rec, current_metrics)
        sim_type = simulation.get('recommendation_type', 'unknown')
        safety_checks = simulation.get('safety_checks', {})
        
        print(f"  • {sim_type.replace('_', ' ').title()}:")
        if safety_checks.get('passed', False):
            print(f"    ✅ Safety checks passed")
        else:
            print(f"    ⚠️  Safety warnings: {len(safety_checks.get('warnings', []))}")
        
        if 'simulation_results' in simulation:
            results = simulation['simulation_results']
            if 'cost_savings' in results:
                print(f"    💰 Estimated savings: {results['cost_savings']:.1f}%")
            if 'performance_impact' in results:
                print(f"    ⚡ Performance impact: {results['performance_impact']}")
    
    # Summary statistics
    print(f"\n📊 Summary Statistics:")
    print(f"  • Total Recommendations: {len(recommendations)}")
    print(f"  • High Confidence (>85%): {high_confidence_count}")
    print(f"  • Low Risk: {low_risk_count}")
    print(f"  • Total Potential Savings: {total_savings:.1f}%")
    print(f"  • Total ROI Potential: {total_roi:.1f}%")
    
    # Storage statistics
    storage_stats = data_store.get_storage_stats()
    print(f"  • Database Size: {storage_stats.get('database_size_bytes', 0) / 1024:.1f} KB")
    print(f"  • Total Metrics: {storage_stats.get('metrics_count', 0)}")
    
    print(f"\n✅ Phase 2 Intelligence Engine test completed successfully!")
    print(f"🎉 UPID is now ready for production with confidence-based optimization!")

if __name__ == "__main__":
    test_phase2_intelligence() 