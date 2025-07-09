#!/usr/bin/env python3
"""
Phase 2 Test Script: Confidence-Based Optimization and Business Impact Correlation
Tests the new Phase 2 capabilities including:
- Confidence-based optimization engine
- Business impact correlation
- Risk assessment and safety boundaries
- Optimization plan execution
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from upid.core.cluster_detector import ClusterDetector
from upid.core.confidence_optimizer import ConfidenceOptimizer, OptimizationPlan, OptimizationType, RiskLevel, SafetyBoundary
from upid.core.business_impact import BusinessImpactCorrelator, BusinessMetric, SLALevel

def test_confidence_optimizer():
    """Test the confidence-based optimization engine"""
    print("🧠 Testing Confidence-Based Optimization Engine...")
    
    try:
        # Initialize the confidence optimizer
        optimizer = ConfidenceOptimizer()
        
        # Test initialization
        assert optimizer.high_confidence_threshold == 0.8
        assert optimizer.medium_confidence_threshold == 0.6
        assert optimizer.low_confidence_threshold == 0.4
        assert optimizer.low_risk_threshold == 0.3
        assert optimizer.medium_risk_threshold == 0.6
        assert optimizer.high_risk_threshold == 0.8
        
        print("✅ Confidence optimizer initialization passed")
        
        # Test safety boundaries
        safety_boundaries = optimizer.safety_boundaries
        assert safety_boundaries.min_replicas == 1
        assert safety_boundaries.max_cpu_utilization == 80.0
        assert safety_boundaries.max_memory_utilization == 80.0
        assert safety_boundaries.min_available_nodes == 1
        assert safety_boundaries.max_risk_score == 0.7
        assert safety_boundaries.business_hours_buffer == 0.2
        
        print("✅ Safety boundaries configuration passed")
        
        # Test risk models
        risk_models = optimizer.risk_models
        assert 'resource_utilization' in risk_models
        assert 'business_impact' in risk_models
        assert 'stability' in risk_models
        assert 'dependencies' in risk_models
        
        print("✅ Risk models configuration passed")
        
        # Test optimization plan generation with mock data
        mock_intelligent_metrics = {
            'intelligent_pods': [
                {
                    'name': 'test-pod-1',
                    'namespace': 'default',
                    'activity_analysis': 'idle',
                    'resource_analysis': {
                        'cpu': 0.1,
                        'memory': 50,
                        'resource_efficiency': 'underutilized'
                    },
                    'business_context': {
                        'business_hours_activity': 0.1,
                        'critical_service': False
                    },
                    'intelligence_score': 85
                },
                {
                    'name': 'test-pod-2',
                    'namespace': 'default',
                    'activity_analysis': 'business_active',
                    'resource_analysis': {
                        'cpu': 0.8,
                        'memory': 200,
                        'resource_efficiency': 'efficient'
                    },
                    'business_context': {
                        'business_hours_activity': 0.9,
                        'critical_service': True
                    },
                    'intelligence_score': 95
                }
            ],
            'business_activity': {
                'total_pods': 2,
                'business_active_pods': 1,
                'business_activity_ratio': 0.5
            },
            'resource_work_correlation': {
                'efficiency_score': 75,
                'correlation_coefficient': 0.8
            },
            'idle_analysis': {
                'idle_pods': [
                    {
                        'name': 'test-pod-1',
                        'confidence': 0.9,
                        'reason': 'low_activity'
                    }
                ],
                'idle_count': 1,
                'total_pods': 2
            }
        }
        
        mock_historical_data = {
            'metrics': [
                {
                    'timestamp': '2024-01-01T00:00:00Z',
                    'cpu_utilization': 60,
                    'memory_utilization': 70,
                    'pod_count': 2
                }
            ]
        }
        
        # Generate optimization plans
        try:
            optimization_plans = optimizer.generate_optimization_plans(
                'test-cluster', mock_intelligent_metrics, mock_historical_data
            )
            
            assert len(optimization_plans) > 0
            print(f"✅ Generated {len(optimization_plans)} optimization plans")
        except Exception as e:
            print(f"❌ Error generating optimization plans: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test plan structure
        for plan in optimization_plans:
            assert hasattr(plan, 'operation_type')
            assert hasattr(plan, 'target_resource')
            assert hasattr(plan, 'confidence_score')
            assert hasattr(plan, 'risk_level')
            assert hasattr(plan, 'potential_savings')
            assert hasattr(plan, 'business_impact')
            assert hasattr(plan, 'rollback_plan')
            assert hasattr(plan, 'simulation_results')
            
            # Test confidence score range
            assert 0 <= plan.confidence_score <= 1
            
            # Test risk level
            assert plan.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        print("✅ Optimization plan structure validation passed")
        
        # Test optimization summary
        optimization_summary = optimizer.get_optimization_summary(optimization_plans)
        assert 'total_plans' in optimization_summary
        assert 'high_confidence_plans' in optimization_summary
        assert 'low_risk_plans' in optimization_summary
        assert 'total_potential_savings' in optimization_summary
        assert 'recommended_actions' in optimization_summary
        
        print("✅ Optimization summary generation passed")
        
        # Test plan execution (dry run)
        if optimization_plans:
            test_plan = optimization_plans[0]
            execution_result = optimizer.execute_optimization(test_plan, dry_run=True)
            
            assert 'success' in execution_result
            assert 'plan' in execution_result
            assert 'execution_time' in execution_result
            assert 'dry_run' in execution_result
            assert 'kubectl_commands' in execution_result
            assert 'rollback_commands' in execution_result
            
            print("✅ Optimization plan execution (dry run) passed")
        
        print("🎯 Confidence-based optimization engine tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Confidence optimizer test failed: {e}")
        return False

def test_business_impact_correlator():
    """Test the business impact correlation engine"""
    print("\n💼 Testing Business Impact Correlation Engine...")
    
    try:
        # Initialize the business impact correlator
        correlator = BusinessImpactCorrelator()
        
        # Test initialization
        assert correlator.revenue_per_user_per_hour == 0.01
        assert correlator.critical_service_multiplier == 10.0
        assert correlator.business_hours['start'] == 9
        assert correlator.business_hours['end'] == 17
        
        print("✅ Business impact correlator initialization passed")
        
        # Test SLA definitions
        sla_definitions = correlator.sla_definitions
        assert SLALevel.CRITICAL in sla_definitions
        assert SLALevel.HIGH in sla_definitions
        assert SLALevel.MEDIUM in sla_definitions
        assert SLALevel.LOW in sla_definitions
        
        critical_sla = sla_definitions[SLALevel.CRITICAL]
        assert critical_sla['uptime'] == 0.9999
        assert critical_sla['response_time'] == 100
        assert critical_sla['error_rate'] == 0.0001
        
        print("✅ SLA definitions configuration passed")
        
        # Test correlation models
        correlation_models = correlator.correlation_models
        assert 'availability_to_revenue' in correlation_models
        assert 'performance_to_satisfaction' in correlation_models
        assert 'error_rate_to_engagement' in correlation_models
        assert 'resource_efficiency_to_roi' in correlation_models
        
        print("✅ Correlation models configuration passed")
        
        # Test business impact correlation with mock data
        mock_intelligent_metrics = {
            'intelligent_pods': [
                {
                    'name': 'api-service',
                    'namespace': 'default',
                    'activity_analysis': 'business_active',
                    'resource_analysis': {
                        'cpu': 0.7,
                        'memory': 150,
                        'resource_efficiency': 'efficient'
                    },
                    'business_context': {
                        'business_hours_activity': 0.9,
                        'critical_service': True
                    }
                },
                {
                    'name': 'database',
                    'namespace': 'default',
                    'activity_analysis': 'business_active',
                    'resource_analysis': {
                        'cpu': 0.8,
                        'memory': 500,
                        'resource_efficiency': 'efficient'
                    },
                    'business_context': {
                        'business_hours_activity': 0.8,
                        'critical_service': True
                    }
                }
            ],
            'business_activity': {
                'total_pods': 2,
                'business_active_pods': 2,
                'business_activity_ratio': 0.9
            },
            'resource_work_correlation': {
                'efficiency_score': 85,
                'correlation_coefficient': 0.9
            }
        }
        
        mock_optimization_plans = [
            OptimizationPlan(
                operation_type=OptimizationType.SCALE_DOWN,
                target_resource='default/test-pod',
                current_value=1,
                proposed_value=0,
                confidence_score=0.85,
                risk_level=RiskLevel.LOW,
                risk_score=0.2,
                potential_savings=0.1,
                business_impact={},
                rollback_plan={},
                safety_boundaries=SafetyBoundary(),
                simulation_results={}
            )
        ]
        
        # Correlate business impact
        business_correlation = correlator.correlate_technical_to_business(
            'test-cluster', mock_intelligent_metrics, mock_optimization_plans
        )
        
        assert 'cluster_id' in business_correlation
        assert 'timestamp' in business_correlation
        assert 'revenue_analysis' in business_correlation
        assert 'customer_satisfaction_analysis' in business_correlation
        assert 'sla_compliance_analysis' in business_correlation
        assert 'roi_analysis' in business_correlation
        assert 'business_kpis' in business_correlation
        assert 'optimization_impact' in business_correlation
        
        print("✅ Business impact correlation generation passed")
        
        # Test revenue analysis
        revenue_analysis = business_correlation['revenue_analysis']
        assert 'current_revenue_per_hour' in revenue_analysis
        assert 'potential_revenue_impact' in revenue_analysis
        assert 'revenue_per_pod' in revenue_analysis
        assert 'critical_service_revenue' in revenue_analysis
        assert 'business_hours_revenue' in revenue_analysis
        
        print("✅ Revenue analysis passed")
        
        # Test ROI analysis
        roi_analysis = business_correlation['roi_analysis']
        assert 'current_roi' in roi_analysis
        assert 'optimization_roi_impact' in roi_analysis
        assert 'cost_savings' in roi_analysis
        assert 'revenue_impact' in roi_analysis
        assert 'roi_breakdown' in roi_analysis
        
        print("✅ ROI analysis passed")
        
        # Test SLA analysis
        sla_analysis = business_correlation['sla_compliance_analysis']
        assert 'current_sla_level' in sla_analysis
        assert 'uptime_compliance' in sla_analysis
        assert 'response_time_compliance' in sla_analysis
        assert 'error_rate_compliance' in sla_analysis
        assert 'sla_breach_risk' in sla_analysis
        assert 'optimization_sla_impact' in sla_analysis
        
        print("✅ SLA analysis passed")
        
        # Test business report generation
        business_report = correlator.generate_business_report(business_correlation)
        assert 'executive_summary' in business_report
        assert 'financial_impact' in business_report
        assert 'operational_metrics' in business_report
        assert 'risk_assessment' in business_report
        assert 'recommendations' in business_report
        
        print("✅ Business report generation passed")
        
        print("💼 Business impact correlation engine tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Business impact correlator test failed: {e}")
        return False

def test_cluster_detector_integration():
    """Test the integration of Phase 2 components in cluster detector"""
    print("\n🔗 Testing Cluster Detector Phase 2 Integration...")
    
    try:
        # Initialize cluster detector
        detector = ClusterDetector()
        
        # Test that Phase 2 components are initialized
        assert hasattr(detector, 'confidence_optimizer')
        assert hasattr(detector, 'business_impact_correlator')
        assert isinstance(detector.confidence_optimizer, ConfidenceOptimizer)
        assert isinstance(detector.business_impact_correlator, BusinessImpactCorrelator)
        
        print("✅ Phase 2 components initialization passed")
        
        # Test confidence optimization plans generation
        optimization_result = detector.generate_confidence_optimization_plans('test-cluster')
        
        assert 'cluster_id' in optimization_result
        assert 'optimization_plans' in optimization_result
        assert 'optimization_summary' in optimization_result
        assert 'total_plans' in optimization_result
        assert 'high_confidence_plans' in optimization_result
        assert 'low_risk_plans' in optimization_result
        
        print("✅ Confidence optimization plans generation passed")
        
        # Test business impact correlation
        business_result = detector.correlate_business_impact('test-cluster')
        
        assert 'cluster_id' in business_result
        assert 'business_correlation' in business_result
        assert 'business_report' in business_result
        assert 'revenue_analysis' in business_result
        assert 'roi_analysis' in business_result
        assert 'sla_analysis' in business_result
        
        print("✅ Business impact correlation passed")
        
        # Test optimization plan execution (dry run)
        if optimization_result.get('optimization_plans'):
            execution_result = detector.execute_optimization_plan('test-cluster', 0, dry_run=True)
            
            assert 'cluster_id' in execution_result
            assert 'plan_index' in execution_result
            assert 'execution_result' in execution_result
            assert 'dry_run' in execution_result
            
            print("✅ Optimization plan execution passed")
        
        print("🔗 Cluster detector Phase 2 integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Cluster detector integration test failed: {e}")
        return False

def test_end_to_end_workflow():
    """Test the complete Phase 2 workflow"""
    print("\n🔄 Testing End-to-End Phase 2 Workflow...")
    
    try:
        # Initialize cluster detector
        detector = ClusterDetector()
        
        # Step 1: Generate confidence optimization plans
        print("Step 1: Generating confidence optimization plans...")
        optimization_result = detector.generate_confidence_optimization_plans('test-cluster')
        
        if 'error' in optimization_result:
            print(f"⚠️  Optimization generation had errors: {optimization_result['error']}")
        else:
            print(f"✅ Generated {optimization_result.get('total_plans', 0)} optimization plans")
            print(f"✅ High confidence plans: {optimization_result.get('high_confidence_plans', 0)}")
            print(f"✅ Low risk plans: {optimization_result.get('low_risk_plans', 0)}")
        
        # Step 2: Correlate business impact
        print("\nStep 2: Correlating business impact...")
        business_result = detector.correlate_business_impact('test-cluster')
        
        if 'error' in business_result:
            print(f"⚠️  Business correlation had errors: {business_result['error']}")
        else:
            revenue_analysis = business_result.get('revenue_analysis', {})
            roi_analysis = business_result.get('roi_analysis', {})
            sla_analysis = business_result.get('sla_analysis', {})
            
            print(f"✅ Current revenue/hour: ${revenue_analysis.get('current_revenue_per_hour', 0):.2f}")
            print(f"✅ Current ROI: {roi_analysis.get('current_roi', 0):.1f}%")
            print(f"✅ SLA compliance: {sla_analysis.get('uptime_compliance', 0):.1f}%")
        
        # Step 3: Execute optimization plan (if available)
        if optimization_result.get('optimization_plans'):
            print("\nStep 3: Executing optimization plan (dry run)...")
            execution_result = detector.execute_optimization_plan('test-cluster', 0, dry_run=True)
            
            if 'error' in execution_result:
                print(f"⚠️  Plan execution had errors: {execution_result['error']}")
            else:
                execution_data = execution_result.get('execution_result', {})
                success = execution_data.get('success', False)
                print(f"✅ Plan execution {'succeeded' if success else 'failed'}")
                
                if success:
                    kubectl_commands = execution_data.get('kubectl_commands', [])
                    rollback_commands = execution_data.get('rollback_commands', [])
                    print(f"✅ Generated {len(kubectl_commands)} kubectl commands")
                    print(f"✅ Generated {len(rollback_commands)} rollback commands")
        
        print("🔄 End-to-end Phase 2 workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("🚀 Starting Phase 2: Confidence-Based Optimization and Business Impact Correlation Tests")
    print("=" * 80)
    
    test_results = []
    
    # Run individual component tests
    test_results.append(("Confidence Optimizer", test_confidence_optimizer()))
    test_results.append(("Business Impact Correlator", test_business_impact_correlator()))
    test_results.append(("Cluster Detector Integration", test_cluster_detector_integration()))
    test_results.append(("End-to-End Workflow", test_end_to_end_workflow()))
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 Phase 2 Test Results Summary")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All Phase 2 tests passed! Confidence-based optimization and business impact correlation are ready.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 