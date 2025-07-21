#!/usr/bin/env python3
"""
Phase 3 Test Script: Executive Dashboard & Reporting
Tests executive dashboard, financial analysis, business impact, and alerts
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from upid.core.dashboard import ExecutiveDashboard, DashboardInsight, DashboardMetric
from upid.core.business_correlation import BusinessCorrelationEngine, BusinessImpact, BusinessMetric
from upid.core.optimization_engine import ConfidenceOptimizationEngine, OptimizationRecommendation
from upid.core.cluster_detector import ClusterDetector
# from upid.core.intelligence_engine import IntelligenceEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_executive_dashboard():
    """Test executive dashboard functionality"""
    print("\n" + "="*60)
    print("🎯 TESTING EXECUTIVE DASHBOARD")
    print("="*60)
    
    try:
        # Initialize components
        dashboard_engine = ExecutiveDashboard()
        cluster_detector = ClusterDetector()
        
        # Generate mock cluster data
        cluster_data = {
            'cluster_info': {
                'name': 'test-cluster',
                'version': '1.25.0',
                'nodes': 5,
                'pods': 150,
                'namespaces': 8
            },
            'performance': {
                'cpu_utilization': 75.5,
                'memory_utilization': 68.2,
                'response_time_p95': 45.2,
                'throughput': 1250,
                'error_rate': 0.5
            },
            'availability': {
                'uptime': 99.95,
                'downtime_minutes': 2.5,
                'incidents': 1,
                'mttr_minutes': 15.0
            },
            'costs': {
                'infrastructure': 2500.0,
                'compute': 1800.0,
                'storage': 800.0,
                'network': 400.0,
                'cost_per_pod': 35.0
            },
            'historical_data': {
                'patterns': [
                    {'type': 'usage_spike', 'confidence': 0.85, 'impact': 'high'},
                    {'type': 'cost_trend', 'confidence': 0.92, 'impact': 'medium'}
                ]
            }
        }
        
        # Generate optimization data
        optimization_data = {
            'recommendations': [
                {
                    'title': 'Right-size underutilized pods',
                    'description': 'Reduce resource requests for pods with low utilization',
                    'potential_savings': 0.15,
                    'confidence': 0.85,
                    'risk_level': 'low',
                    'implementation_time': '2 hours'
                },
                {
                    'title': 'Implement HPA for dynamic scaling',
                    'description': 'Add Horizontal Pod Autoscaler for better resource utilization',
                    'potential_savings': 0.08,
                    'confidence': 0.92,
                    'risk_level': 'medium',
                    'implementation_time': '4 hours'
                },
                {
                    'title': 'Optimize storage classes',
                    'description': 'Use appropriate storage classes for different workloads',
                    'potential_savings': 0.12,
                    'confidence': 0.78,
                    'risk_level': 'low',
                    'implementation_time': '6 hours'
                }
            ]
        }
        
        # Generate business data
        business_data = {
            'roi_estimates': {
                'total_roi': 18.5,
                'cost_savings_roi': 25.0,
                'performance_roi': 12.0
            },
            'business_impacts': [
                BusinessImpact(
                    metric_type=BusinessMetric.REVENUE_PER_POD,
                    technical_metric='resource_utilization',
                    correlation_strength=0.75,
                    business_value=1250.0,
                    confidence=88.0,
                    impact_description='Estimated $1250.00 revenue per pod per day',
                    roi_estimate=25.0
                ),
                BusinessImpact(
                    metric_type=BusinessMetric.CUSTOMER_SATISFACTION,
                    technical_metric='performance_metrics',
                    correlation_strength=0.68,
                    business_value=8.2,
                    confidence=85.0,
                    impact_description='Estimated 8.2/10 customer satisfaction score',
                    roi_estimate=12.0
                ),
                BusinessImpact(
                    metric_type=BusinessMetric.SLA_COMPLIANCE,
                    technical_metric='performance_metrics',
                    correlation_strength=0.82,
                    business_value=99.95,
                    confidence=92.0,
                    impact_description='99.95% SLA compliance rate',
                    roi_estimate=18.5
                )
            ]
        }
        
        # Generate executive dashboard
        dashboard_result = dashboard_engine.generate_executive_dashboard(
            cluster_data, optimization_data, business_data
        )
        
        # Validate dashboard structure
        required_sections = ['summary', 'financial_metrics', 'operational_metrics', 
                           'business_metrics', 'insights', 'recommendations', 'alerts']
        
        for section in required_sections:
            assert section in dashboard_result, f"Missing dashboard section: {section}"
        
        # Validate summary
        summary = dashboard_result['summary']
        assert 'overall_health' in summary, "Missing overall health in summary"
        assert 'key_metrics' in summary, "Missing key metrics in summary"
        
        # Validate financial metrics
        financial = dashboard_result['financial_metrics']
        assert 'cost_savings' in financial, "Missing cost savings in financial metrics"
        assert 'roi_analysis' in financial, "Missing ROI analysis in financial metrics"
        
        # Validate operational metrics
        operational = dashboard_result['operational_metrics']
        assert 'performance' in operational, "Missing performance in operational metrics"
        assert 'availability' in operational, "Missing availability in operational metrics"
        
        # Validate business metrics
        business = dashboard_result['business_metrics']
        assert 'revenue_impact' in business, "Missing revenue impact in business metrics"
        assert 'customer_satisfaction' in business, "Missing customer satisfaction in business metrics"
        
        # Display dashboard summary
        print(f"✅ Dashboard generated successfully!")
        print(f"📊 Overall Health: {summary.get('overall_health', 'unknown').upper()}")
        print(f"💰 Cost Savings: {financial['cost_savings'].get('current_savings', 0):.1f}%")
        print(f"📈 ROI: {financial['roi_analysis'].get('current_roi', 0):.1f}%")
        print(f"⚡ Availability: {operational['availability'].get('current_uptime', 0):.3f}%")
        print(f"📊 Performance Score: {operational['performance'].get('performance_score', 0):.1f}")
        print(f"💡 Insights Generated: {len(dashboard_result.get('insights', []))}")
        print(f"🎯 Recommendations: {len(dashboard_result.get('recommendations', []))}")
        print(f"🚨 Alerts: {len(dashboard_result.get('alerts', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Executive dashboard test failed: {e}")
        return False

def test_financial_analysis():
    """Test financial analysis functionality"""
    print("\n" + "="*60)
    print("💰 TESTING FINANCIAL ANALYSIS")
    print("="*60)
    
    try:
        dashboard_engine = ExecutiveDashboard()
        
        # Mock data
        cluster_data = {
            'costs': {
                'infrastructure': 2500.0,
                'compute': 1800.0,
                'storage': 800.0,
                'network': 400.0
            }
        }
        
        optimization_data = {
            'recommendations': [
                {'potential_savings': 0.15, 'confidence': 0.85},
                {'potential_savings': 0.08, 'confidence': 0.92},
                {'potential_savings': 0.12, 'confidence': 0.78}
            ]
        }
        
        business_data = {
            'roi_estimates': {
                'total_roi': 18.5
            }
        }
        
        # Generate financial metrics
        financial_metrics = dashboard_engine._generate_financial_metrics(
            cluster_data, optimization_data, business_data
        )
        
        # Validate financial metrics
        assert 'cost_savings' in financial_metrics, "Missing cost savings"
        assert 'roi_analysis' in financial_metrics, "Missing ROI analysis"
        assert 'cost_attribution' in financial_metrics, "Missing cost attribution"
        assert 'budget_impact' in financial_metrics, "Missing budget impact"
        
        # Validate cost savings
        cost_savings = financial_metrics['cost_savings']
        assert 'current_savings' in cost_savings, "Missing current savings"
        assert 'target_savings' in cost_savings, "Missing target savings"
        assert 'achievement_percentage' in cost_savings, "Missing achievement percentage"
        
        # Validate ROI analysis
        roi_analysis = financial_metrics['roi_analysis']
        assert 'current_roi' in roi_analysis, "Missing current ROI"
        assert 'target_roi' in roi_analysis, "Missing target ROI"
        assert 'achievement_percentage' in roi_analysis, "Missing ROI achievement"
        
        # Display financial analysis
        print(f"✅ Financial analysis completed!")
        print(f"💵 Cost Savings: {cost_savings.get('current_savings', 0):.1f}%")
        print(f"📈 ROI: {roi_analysis.get('current_roi', 0):.1f}%")
        print(f"💰 Total Cost: ${financial_metrics['cost_attribution'].get('total_cost', 0):,.0f}")
        print(f"📊 Monthly Projection: ${cost_savings.get('monthly_projection', 0):,.0f}")
        print(f"🎯 Payback Period: {roi_analysis.get('payback_period', 0):.1f} months")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Financial analysis test failed: {e}")
        return False

def test_business_impact_analysis():
    """Test business impact analysis functionality"""
    print("\n" + "="*60)
    print("📈 TESTING BUSINESS IMPACT ANALYSIS")
    print("="*60)
    
    try:
        dashboard_engine = ExecutiveDashboard()
        business_engine = BusinessCorrelationEngine()
        
        # Mock data
        cluster_data = {
            'performance': {
                'cpu_utilization': 75.5,
                'memory_utilization': 68.2,
                'response_time_p95': 45.2
            },
            'availability': {
                'uptime': 99.95,
                'downtime_minutes': 2.5
            }
        }
        
        optimization_data = {
            'recommendations': [
                {'potential_savings': 0.15, 'confidence': 0.85},
                {'potential_savings': 0.08, 'confidence': 0.92}
            ]
        }
        
        # Generate business data
        business_data = business_engine.analyze_business_impact(
            cluster_data, optimization_data
        )
        
        # Generate business metrics
        business_metrics = dashboard_engine._generate_business_metrics(business_data)
        
        # Validate business metrics
        assert 'revenue_impact' in business_metrics, "Missing revenue impact"
        assert 'customer_satisfaction' in business_metrics, "Missing customer satisfaction"
        assert 'sla_compliance' in business_metrics, "Missing SLA compliance"
        assert 'business_value' in business_metrics, "Missing business value"
        
        # Validate revenue impact
        revenue_impact = business_metrics['revenue_impact']
        assert 'revenue_per_pod' in revenue_impact, "Missing revenue per pod"
        assert 'total_revenue' in revenue_impact, "Missing total revenue"
        assert 'revenue_trend' in revenue_impact, "Missing revenue trend"
        
        # Validate customer satisfaction
        customer_satisfaction = business_metrics['customer_satisfaction']
        assert 'satisfaction_score' in customer_satisfaction, "Missing satisfaction score"
        assert 'target_score' in customer_satisfaction, "Missing target score"
        assert 'achievement_percentage' in customer_satisfaction, "Missing achievement percentage"
        
        # Validate SLA compliance
        sla_compliance = business_metrics['sla_compliance']
        assert 'compliance_rate' in sla_compliance, "Missing compliance rate"
        assert 'target_compliance' in sla_compliance, "Missing target compliance"
        assert 'achievement_percentage' in sla_compliance, "Missing SLA achievement percentage"
        
        # Display business analysis
        print(f"✅ Business impact analysis completed!")
        print(f"💰 Revenue per Pod: ${revenue_impact.get('revenue_per_pod', 0):,.0f}")
        print(f"😊 Customer Satisfaction: {customer_satisfaction.get('satisfaction_score', 0):.1f}/10")
        print(f"📋 SLA Compliance: {sla_compliance.get('compliance_rate', 0):.3f}%")
        print(f"📈 Business Value Score: {business_metrics['business_value'].get('business_value_score', 0):.1f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Business impact analysis test failed: {e}")
        return False

def test_executive_alerts():
    """Test executive alerts functionality"""
    print("\n" + "="*60)
    print("🚨 TESTING EXECUTIVE ALERTS")
    print("="*60)
    
    try:
        dashboard_engine = ExecutiveDashboard()
        
        # Mock data with issues to trigger alerts
        cluster_data = {
            'performance': {
                'cpu_utilization': 95.5,  # High CPU to trigger alert
                'memory_utilization': 88.2,  # High memory to trigger alert
                'response_time_p95': 150.2,  # High response time
                'error_rate': 2.5  # High error rate
            },
            'availability': {
                'uptime': 98.5,  # Below target to trigger alert
                'downtime_minutes': 45.0,
                'incidents': 3
            },
            'costs': {
                'infrastructure': 5000.0,  # High costs
                'compute': 3500.0,
                'storage': 1200.0,
                'network': 800.0
            }
        }
        
        optimization_data = {
            'recommendations': [
                {'potential_savings': 0.05, 'confidence': 0.85}  # Low savings
            ]
        }
        
        business_data = {
            'roi_estimates': {
                'total_roi': 8.5  # Low ROI to trigger alert
            }
        }
        
        # Generate dashboard with alerts
        dashboard_result = dashboard_engine.generate_executive_dashboard(
            cluster_data, optimization_data, business_data
        )
        
        alerts = dashboard_result.get('alerts', [])
        
        # Validate alerts
        assert len(alerts) > 0, "No alerts generated despite issues"
        
        # Check for specific alert types
        alert_titles = [alert.get('title', '') for alert in alerts]
        alert_severities = [alert.get('severity', '') for alert in alerts]
        
        print(f"✅ Executive alerts test completed!")
        print(f"🚨 Total Alerts Generated: {len(alerts)}")
        print(f"🔴 Critical Alerts: {len([a for a in alerts if a.get('severity') == 'critical'])}")
        print(f"🟡 Warning Alerts: {len([a for a in alerts if a.get('severity') == 'warning'])}")
        print(f"🔵 Info Alerts: {len([a for a in alerts if a.get('severity') == 'info'])}")
        
        # Display sample alerts
        for i, alert in enumerate(alerts[:3], 1):
            severity_icon = "🔴" if alert.get('severity') == 'critical' else "🟡" if alert.get('severity') == 'warning' else "🔵"
            print(f"\n{i}. {severity_icon} {alert.get('title', 'Unknown Alert')}")
            print(f"   Severity: {alert.get('severity', 'unknown').upper()}")
            print(f"   Description: {alert.get('description', 'No description')}")
            print(f"   Action Required: {alert.get('action_required', 'No action specified')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Executive alerts test failed: {e}")
        return False

def test_dashboard_insights():
    """Test dashboard insights generation"""
    print("\n" + "="*60)
    print("💡 TESTING DASHBOARD INSIGHTS")
    print("="*60)
    
    try:
        dashboard_engine = ExecutiveDashboard()
        
        # Mock data with good performance to generate positive insights
        cluster_data = {
            'performance': {
                'cpu_utilization': 75.5,
                'memory_utilization': 68.2,
                'response_time_p95': 45.2
            },
            'availability': {
                'uptime': 99.98,
                'downtime_minutes': 0.5
            },
            'costs': {
                'infrastructure': 2000.0,
                'compute': 1500.0,
                'storage': 600.0,
                'network': 300.0
            }
        }
        
        optimization_data = {
            'recommendations': [
                {'potential_savings': 0.25, 'confidence': 0.85},
                {'potential_savings': 0.15, 'confidence': 0.92},
                {'potential_savings': 0.20, 'confidence': 0.78}
            ]
        }
        
        business_data = {
            'roi_estimates': {
                'total_roi': 22.5
            }
        }
        
        # Generate dashboard
        dashboard_result = dashboard_engine.generate_executive_dashboard(
            cluster_data, optimization_data, business_data
        )
        
        insights = dashboard_result.get('insights', [])
        
        # Validate insights
        assert len(insights) > 0, "No insights generated"
        
        # Check insight structure
        for insight in insights:
            assert hasattr(insight, 'title'), "Insight missing title"
            assert hasattr(insight, 'value'), "Insight missing value"
            assert hasattr(insight, 'trend'), "Insight missing trend"
            assert hasattr(insight, 'confidence'), "Insight missing confidence"
            assert hasattr(insight, 'business_impact'), "Insight missing business impact"
        
        print(f"✅ Dashboard insights test completed!")
        print(f"💡 Total Insights Generated: {len(insights)}")
        
        # Display sample insights
        for i, insight in enumerate(insights[:3], 1):
            print(f"\n{i}. {insight.title}")
            print(f"   Value: {insight.value:.1f} {insight.unit}")
            print(f"   Trend: {insight.trend.title()}")
            print(f"   Confidence: {insight.confidence:.1f}%")
            print(f"   Impact: {insight.business_impact}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard insights test failed: {e}")
        return False

def test_dashboard_recommendations():
    """Test dashboard recommendations generation"""
    print("\n" + "="*60)
    print("🎯 TESTING DASHBOARD RECOMMENDATIONS")
    print("="*60)
    
    try:
        dashboard_engine = ExecutiveDashboard()
        
        # Mock data with issues to generate recommendations
        cluster_data = {
            'performance': {
                'cpu_utilization': 85.5,  # High CPU
                'memory_utilization': 78.2,  # High memory
                'response_time_p95': 85.2,  # High response time
                'error_rate': 1.5
            },
            'availability': {
                'uptime': 99.2,  # Below target
                'downtime_minutes': 15.0,
                'incidents': 2
            },
            'costs': {
                'infrastructure': 3000.0,
                'compute': 2200.0,
                'storage': 900.0,
                'network': 500.0
            }
        }
        
        optimization_data = {
            'recommendations': [
                {'potential_savings': 0.10, 'confidence': 0.85}  # Low savings
            ]
        }
        
        business_data = {
            'roi_estimates': {
                'total_roi': 12.5  # Below target
            }
        }
        
        # Generate dashboard
        dashboard_result = dashboard_engine.generate_executive_dashboard(
            cluster_data, optimization_data, business_data
        )
        
        recommendations = dashboard_result.get('recommendations', [])
        
        # Validate recommendations
        assert len(recommendations) > 0, "No recommendations generated"
        
        # Check recommendation structure
        for rec in recommendations:
            assert 'title' in rec, "Recommendation missing title"
            assert 'priority' in rec, "Recommendation missing priority"
            assert 'description' in rec, "Recommendation missing description"
            assert 'action' in rec, "Recommendation missing action"
            assert 'expected_impact' in rec, "Recommendation missing expected impact"
            assert 'timeline' in rec, "Recommendation missing timeline"
        
        print(f"✅ Dashboard recommendations test completed!")
        print(f"🎯 Total Recommendations Generated: {len(recommendations)}")
        
        # Count by priority
        high_priority = len([r for r in recommendations if r.get('priority') == 'high'])
        medium_priority = len([r for r in recommendations if r.get('priority') == 'medium'])
        low_priority = len([r for r in recommendations if r.get('priority') == 'low'])
        
        print(f"🔴 High Priority: {high_priority}")
        print(f"🟡 Medium Priority: {medium_priority}")
        print(f"🟢 Low Priority: {low_priority}")
        
        # Display sample recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            priority_icon = "🔴" if rec.get('priority') == 'high' else "🟡" if rec.get('priority') == 'medium' else "🟢"
            print(f"\n{i}. {priority_icon} {rec.get('title', 'Unknown')}")
            print(f"   Priority: {rec.get('priority', 'unknown').upper()}")
            print(f"   Description: {rec.get('description', 'No description')}")
            print(f"   Action: {rec.get('action', 'No action specified')}")
            print(f"   Expected Impact: {rec.get('expected_impact', 'Unknown')}")
            print(f"   Timeline: {rec.get('timeline', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard recommendations test failed: {e}")
        return False

def test_dashboard_export():
    """Test dashboard export functionality"""
    print("\n" + "="*60)
    print("📁 TESTING DASHBOARD EXPORT")
    print("="*60)
    
    try:
        dashboard_engine = ExecutiveDashboard()
        
        # Mock data
        cluster_data = {
            'cluster_info': {'name': 'test-cluster'},
            'performance': {'cpu_utilization': 75.5},
            'availability': {'uptime': 99.95},
            'costs': {'infrastructure': 2500.0}
        }
        
        optimization_data = {
            'recommendations': [
                {'potential_savings': 0.15, 'confidence': 0.85}
            ]
        }
        
        business_data = {
            'roi_estimates': {'total_roi': 18.5}
        }
        
        # Generate dashboard
        dashboard_result = dashboard_engine.generate_executive_dashboard(
            cluster_data, optimization_data, business_data
        )
        
        # Export to JSON
        export_filename = 'test_dashboard_export.json'
        with open(export_filename, 'w') as f:
            json.dump(dashboard_result, f, indent=2, default=str)
        
        # Verify export
        with open(export_filename, 'r') as f:
            exported_data = json.load(f)
        
        # Validate exported data
        assert 'summary' in exported_data, "Missing summary in exported data"
        assert 'financial_metrics' in exported_data, "Missing financial metrics in exported data"
        assert 'operational_metrics' in exported_data, "Missing operational metrics in exported data"
        assert 'business_metrics' in exported_data, "Missing business metrics in exported data"
        
        # Clean up
        os.remove(export_filename)
        
        print(f"✅ Dashboard export test completed!")
        print(f"📁 Successfully exported dashboard to JSON")
        print(f"📊 Exported sections: {list(exported_data.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dashboard export test failed: {e}")
        return False

def run_phase3_tests():
    """Run all Phase 3 tests"""
    print("\n" + "🚀" + "="*58 + "🚀")
    print("🎯 PHASE 3: EXECUTIVE DASHBOARD & REPORTING TESTS")
    print("🚀" + "="*58 + "🚀")
    
    tests = [
        ("Executive Dashboard", test_executive_dashboard),
        ("Financial Analysis", test_financial_analysis),
        ("Business Impact Analysis", test_business_impact_analysis),
        ("Executive Alerts", test_executive_alerts),
        ("Dashboard Insights", test_dashboard_insights),
        ("Dashboard Recommendations", test_dashboard_recommendations),
        ("Dashboard Export", test_dashboard_export)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED - {e}")
    
    print("\n" + "="*60)
    print(f"📊 PHASE 3 TEST RESULTS")
    print("="*60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL PHASE 3 TESTS PASSED! 🎉")
        print("🚀 Executive Dashboard & Reporting is ready for production!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review and fix.")
    
    return passed == total

if __name__ == "__main__":
    success = run_phase3_tests()
    sys.exit(0 if success else 1) 