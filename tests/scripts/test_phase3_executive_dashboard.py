#!/usr/bin/env python3
"""
Phase 3 Test Script: Executive Dashboard Engine and CLI Integration
Tests:
- ExecutiveDashboardEngine summary and export
- ClusterDetector executive dashboard integration
- CLI output for all formats
"""
import sys
import os
import json
from datetime import datetime
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from upid.core.executive_dashboard import ExecutiveDashboardEngine, ExecutiveSummary
from upid.core.cluster_detector import ClusterDetector

def test_dashboard_engine():
    print("\n🏢 Testing ExecutiveDashboardEngine...")
    try:
        engine = ExecutiveDashboardEngine()
        # Mock data
        cluster_id = 'test-cluster'
        optimization_history = [
            {'operation_type': 'scale_down', 'target_resource': 'default/app1', 'confidence_score': 0.9, 'risk_level': 'low', 'potential_savings': 0.2, 'risk_score': 0.1},
            {'operation_type': 'resource_limits', 'target_resource': 'default/app2', 'confidence_score': 0.85, 'risk_level': 'medium', 'potential_savings': 0.1, 'risk_score': 0.3}
        ]
        business_reports = [
            {'roi_analysis': {'current_roi': 12.5}, 'executive_summary': {'optimization_potential': 0.5}, 'recommendations': [{'action': 'Scale down app1'}]}
        ]
        kpi_history = [
            {'resource_efficiency': 80, 'availability_score': 99, 'performance_score': 85, 'business_activity_score': 70},
            {'resource_efficiency': 85, 'availability_score': 99.5, 'performance_score': 88, 'business_activity_score': 75}
        ]
        summary = engine.generate_dashboard(cluster_id, optimization_history, business_reports, kpi_history)
        assert isinstance(summary, ExecutiveSummary)
        print("✅ ExecutiveSummary generation passed")
        # Test export formats
        for fmt in ['json', 'yaml', 'markdown', 'html']:
            output = engine.export_dashboard(summary, format=fmt)
            assert output
            print(f"✅ Export format '{fmt}' passed")
        print("🏢 ExecutiveDashboardEngine tests completed successfully!")
        return True
    except Exception as e:
        print(f"❌ ExecutiveDashboardEngine test failed: {e}")
        return False

def test_cluster_detector_dashboard():
    print("\n🔗 Testing ClusterDetector executive dashboard integration...")
    try:
        detector = ClusterDetector()
        # Use mock cluster_id
        cluster_id = 'test-cluster'
        for fmt in ['json', 'yaml', 'markdown', 'html']:
            dashboard = detector.generate_executive_dashboard(cluster_id, format=fmt)
            assert dashboard
            print(f"✅ ClusterDetector dashboard export '{fmt}' passed")
        print("🔗 ClusterDetector executive dashboard integration tests completed!")
        return True
    except Exception as e:
        print(f"❌ ClusterDetector dashboard integration test failed: {e}")
        return False

def main():
    print("\n🚀 Phase 3: Executive Dashboard Engine and CLI Integration Tests")
    print("=" * 80)
    results = []
    results.append(("ExecutiveDashboardEngine", test_dashboard_engine()))
    results.append(("ClusterDetector Dashboard Integration", test_cluster_detector_dashboard()))
    print("\n" + "=" * 80)
    print("📊 Phase 3 Test Results Summary")
    print("=" * 80)
    passed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:<40} {status}")
        if result:
            passed += 1
    print("-" * 80)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")
    print(f"Success Rate: {(passed/len(results))*100:.1f}%")
    if passed == len(results):
        print("\n🎉 All Phase 3 tests passed! Executive dashboard is ready.")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 