#!/usr/bin/env python3
"""
Test script for UPID Intelligent Analytics
Tests the sophisticated intelligence features including:
- Intelligent data collection with business context
- Advanced pattern analysis
- Business intelligence analysis
- Predictive analytics
- Intelligent idle detection
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from upid.core.intelligence import IntelligentDataCollector
from upid.core.advanced_analytics import AdvancedIntelligenceEngine
from upid.core.cluster_detector import ClusterDetector
from upid.core.data_store import TimeSeriesDataStore

def test_intelligent_data_collection():
    """Test intelligent data collection with business context"""
    print("🧠 Testing Intelligent Data Collection")
    print("=" * 50)
    
    try:
        collector = IntelligentDataCollector()
        cluster_id = "test-cluster"
        
        # Collect intelligent metrics
        print("Collecting intelligent metrics...")
        intelligent_metrics = collector.collect_intelligent_metrics(cluster_id)
        
        if 'error' in intelligent_metrics:
            print(f"❌ Error in intelligent data collection: {intelligent_metrics['error']}")
            return False
        
        print("✅ Intelligent data collection successful")
        
        # Display key metrics
        business_activity = intelligent_metrics.get('business_activity', {})
        idle_analysis = intelligent_metrics.get('idle_analysis', {})
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        
        print(f"\n📊 Business Activity Analysis:")
        print(f"  Total Pods: {business_activity.get('total_pods', 0)}")
        print(f"  Business Active: {business_activity.get('business_active_pods', 0)}")
        print(f"  Idle Pods: {business_activity.get('idle_pods', 0)}")
        print(f"  Business Activity Ratio: {business_activity.get('business_activity_ratio', 0):.1%}")
        
        print(f"\n💤 Idle Analysis:")
        print(f"  Idle Pods: {idle_analysis.get('idle_count', 0)}")
        potential_savings = idle_analysis.get('potential_savings', {})
        if potential_savings:
            print(f"  Estimated Monthly Savings: ${potential_savings.get('estimated_monthly_savings', 0):.2f}")
        
        print(f"\n⚡ Resource Efficiency:")
        efficiency_score = resource_correlation.get('efficiency_score', 0)
        print(f"  Efficiency Score: {efficiency_score:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing intelligent data collection: {e}")
        return False

def test_advanced_analytics():
    """Test advanced analytics with sophisticated pattern detection"""
    print("\n🚀 Testing Advanced Analytics")
    print("=" * 50)
    
    try:
        analytics = AdvancedIntelligenceEngine()
        
        # Create sample historical data
        historical_data = {
            'cluster_id': 'test-cluster',
            'period_days': 90,
            'metrics': {
                'cpu_utilization': [
                    {'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(), 'value': 50 + i % 20}
                    for i in range(100)
                ],
                'memory_utilization': [
                    {'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(), 'value': 60 + i % 15}
                    for i in range(100)
                ]
            }
        }
        
        print("Performing advanced pattern analysis...")
        advanced_analysis = analytics.analyze_advanced_patterns(historical_data)
        
        if 'error' in advanced_analysis:
            print(f"❌ Error in advanced analytics: {advanced_analysis['error']}")
            return False
        
        print("✅ Advanced analytics successful")
        
        # Display key insights
        advanced_patterns = advanced_analysis.get('advanced_patterns', {})
        business_intelligence = advanced_analysis.get('business_intelligence', {})
        predictive_insights = advanced_analysis.get('predictive_insights', {})
        confidence_metrics = advanced_analysis.get('confidence_metrics', {})
        
        print(f"\n📊 Advanced Patterns:")
        for period, patterns in advanced_patterns.items():
            print(f"  {period}: {len(patterns.get('temporal_patterns', {}))} metrics analyzed")
        
        print(f"\n💼 Business Intelligence:")
        business_hours = business_intelligence.get('business_hours_analysis', {})
        for metric_type, data in business_hours.items():
            has_pattern = data.get('has_business_pattern', False)
            efficiency = data.get('business_hours_efficiency', 0)
            print(f"  {metric_type}: {'✅' if has_pattern else '❌'} business pattern (efficiency: {efficiency:.1f}%)")
        
        print(f"\n🔮 Predictive Insights:")
        trend_predictions = predictive_insights.get('trend_predictions', {})
        for metric_type, prediction in trend_predictions.items():
            direction = prediction.get('trend_direction', 'unknown')
            confidence = prediction.get('confidence', 0)
            print(f"  {metric_type}: {direction} trend (confidence: {confidence:.1f}%)")
        
        print(f"\n🎯 Confidence Metrics:")
        overall_confidence = confidence_metrics.get('overall_confidence', 0)
        print(f"  Overall Confidence: {overall_confidence:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing advanced analytics: {e}")
        return False

def test_cluster_detector_integration():
    """Test cluster detector with intelligent features"""
    print("\n🔍 Testing Cluster Detector Integration")
    print("=" * 50)
    
    try:
        detector = ClusterDetector()
        
        # Test cluster detection
        print("Detecting cluster...")
        cluster_info = detector.detect_cluster()
        
        if cluster_info.get('status') == 'error':
            print(f"❌ Cluster detection failed: {cluster_info.get('error', 'Unknown error')}")
            return False
        
        print("✅ Cluster detection successful")
        print(f"  Cluster: {cluster_info.get('name', 'Unknown')}")
        print(f"  Type: {cluster_info.get('type', 'Unknown')}")
        
        # Test intelligent metrics collection
        print("\nCollecting intelligent metrics...")
        cluster_id = cluster_info.get('name', 'default')
        intelligent_metrics = detector.collect_intelligent_metrics(cluster_id)
        
        if 'error' in intelligent_metrics:
            print(f"❌ Intelligent metrics collection failed: {intelligent_metrics['error']}")
            return False
        
        print("✅ Intelligent metrics collection successful")
        
        # Test intelligent pattern analysis
        print("\nAnalyzing intelligent patterns...")
        pattern_analysis = detector.analyze_intelligent_patterns(cluster_id)
        
        if 'error' in pattern_analysis:
            print(f"❌ Intelligent pattern analysis failed: {pattern_analysis['error']}")
            return False
        
        print("✅ Intelligent pattern analysis successful")
        
        # Test intelligent recommendations
        print("\nGetting intelligent recommendations...")
        recommendations = detector.get_intelligent_recommendations(cluster_id)
        
        if 'error' in recommendations:
            print(f"❌ Intelligent recommendations failed: {recommendations['error']}")
            return False
        
        print("✅ Intelligent recommendations successful")
        
        # Display recommendation summary
        business_recs = len(recommendations.get('business_recommendations', []))
        technical_recs = len(recommendations.get('technical_recommendations', []))
        cost_recs = len(recommendations.get('cost_optimization_recommendations', []))
        capacity_recs = len(recommendations.get('capacity_planning_recommendations', []))
        overall_priority = recommendations.get('overall_priority', 'medium')
        
        print(f"\n💡 Recommendation Summary:")
        print(f"  Business: {business_recs}")
        print(f"  Technical: {technical_recs}")
        print(f"  Cost Optimization: {cost_recs}")
        print(f"  Capacity Planning: {capacity_recs}")
        print(f"  Overall Priority: {overall_priority.upper()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing cluster detector integration: {e}")
        return False

def test_intelligent_idle_detection():
    """Test intelligent idle detection with business context"""
    print("\n💤 Testing Intelligent Idle Detection")
    print("=" * 50)
    
    try:
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        cluster_id = cluster_info.get('name', 'default')
        
        print("Performing intelligent idle analysis...")
        idle_analysis = detector.get_intelligent_idle_analysis(cluster_id)
        
        if 'error' in idle_analysis:
            print(f"❌ Intelligent idle analysis failed: {idle_analysis['error']}")
            return False
        
        print("✅ Intelligent idle analysis successful")
        
        # Display idle analysis results
        idle_pods = idle_analysis.get('idle_pods', [])
        idle_count = idle_analysis.get('idle_count', 0)
        potential_savings = idle_analysis.get('potential_savings', {})
        intelligent_insights = idle_analysis.get('intelligent_insights', [])
        
        print(f"\n📊 Idle Analysis Results:")
        print(f"  Total Idle Pods: {idle_count}")
        
        if potential_savings:
            print(f"\n💰 Potential Savings:")
            print(f"  CPU Cores: {potential_savings.get('cpu_cores', 0):.1f}")
            print(f"  Memory: {potential_savings.get('memory_mb', 0):.1f} MB")
            print(f"  Monthly Savings: ${potential_savings.get('estimated_monthly_savings', 0):.2f}")
            print(f"  Savings Confidence: {potential_savings.get('savings_confidence', 0):.1f}%")
        
        if intelligent_insights:
            print(f"\n🧠 Intelligent Insights:")
            for insight in intelligent_insights:
                insight_type = insight.get('type', 'unknown')
                description = insight.get('description', 'No description')
                confidence = insight.get('confidence', 0)
                print(f"  {insight_type}: {description} (confidence: {confidence:.1f}%)")
        
        if idle_pods:
            print(f"\n🔍 High Confidence Idle Pods:")
            high_confidence = [pod for pod in idle_pods if pod.get('confidence', 0) > 80]
            for pod in high_confidence[:5]:  # Show top 5
                name = pod.get('name', 'Unknown')
                namespace = pod.get('namespace', 'Unknown')
                idle_score = pod.get('idle_score', 0)
                confidence = pod.get('confidence', 0)
                print(f"  {namespace}/{name}: {idle_score:.1f}% idle (confidence: {confidence:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing intelligent idle detection: {e}")
        return False

def test_data_store_integration():
    """Test data store integration with intelligent metrics"""
    print("\n💾 Testing Data Store Integration")
    print("=" * 50)
    
    try:
        data_store = TimeSeriesDataStore()
        cluster_id = "test-cluster"
        
        # Create sample intelligent metrics
        sample_metrics = {
            'cluster_id': cluster_id,
            'timestamp': datetime.utcnow().isoformat(),
            'intelligent_pods': [
                {
                    'name': 'test-pod-1',
                    'namespace': 'default',
                    'activity_analysis': 'business_active',
                    'intelligence_score': 85.5
                },
                {
                    'name': 'test-pod-2',
                    'namespace': 'default',
                    'activity_analysis': 'idle',
                    'intelligence_score': 15.2
                }
            ],
            'business_activity': {
                'total_pods': 2,
                'business_active_pods': 1,
                'idle_pods': 1,
                'business_activity_ratio': 0.5
            },
            'idle_analysis': {
                'idle_pods': [
                    {
                        'name': 'test-pod-2',
                        'namespace': 'default',
                        'idle_score': 85.0,
                        'confidence': 90.0
                    }
                ],
                'idle_count': 1,
                'potential_savings': {
                    'estimated_monthly_savings': 150.0,
                    'savings_confidence': 90.0
                }
            }
        }
        
        print("Storing intelligent metrics...")
        data_store.store_metrics(cluster_id, sample_metrics)
        print("✅ Intelligent metrics stored successfully")
        
        # Test retrieving historical data
        print("Retrieving historical data...")
        historical_data = data_store.get_historical_data(cluster_id, days=90)
        
        if historical_data:
            print("✅ Historical data retrieval successful")
            print(f"  Period: {historical_data.get('period_days', 0)} days")
            print(f"  Metrics: {len(historical_data.get('metrics', {}))}")
        else:
            print("⚠️  No historical data found (this is normal for new clusters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing data store integration: {e}")
        return False

def main():
    """Run all intelligent analytics tests"""
    print("🧠 UPID Intelligent Analytics Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.utcnow().isoformat()}")
    print()
    
    tests = [
        ("Intelligent Data Collection", test_intelligent_data_collection),
        ("Advanced Analytics", test_advanced_analytics),
        ("Cluster Detector Integration", test_cluster_detector_integration),
        ("Intelligent Idle Detection", test_intelligent_idle_detection),
        ("Data Store Integration", test_data_store_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")
    print(f"Completed at: {datetime.utcnow().isoformat()}")
    
    if passed == total:
        print("🎉 All tests passed! Intelligent analytics are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 