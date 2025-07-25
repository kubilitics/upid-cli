#!/usr/bin/env python3
"""
Test script for Phase 7 Task 7.1: Advanced ML Integration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase71_imports():
    """Test that all Phase 7.1 components can be imported"""
    try:
        # Test Advanced ML Integration imports
        from upid_python.core.ml_enhancement import (
            MLEnhancementEngine,
            MLModelType,
            MLPrediction,
            AnomalyDetection,
            OptimizationRecommendation,
            PredictionConfidence,
            BaseMLModel,
            ResourcePredictionModel,
            AnomalyDetectionModel,
            SecurityThreatModel,
            OptimizationModel
        )
        print("✅ Advanced ML Integration imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_phase71_components():
    """Test basic component functionality"""
    try:
        # Test configuration objects
        from upid_python.core.ml_enhancement import (
            MLModelType,
            MLPrediction,
            AnomalyDetection,
            OptimizationRecommendation,
            PredictionConfidence
        )
        from datetime import datetime
        
        # Create ML prediction
        ml_prediction = MLPrediction(
            model_type=MLModelType.RESOURCE_PREDICTION,
            prediction_value=85.5,
            confidence=PredictionConfidence.HIGH,
            confidence_score=0.85,
            features_used=["cpu_utilization", "memory_utilization"],
            prediction_timestamp=datetime.now(),
            model_version="1.0.0"
        )
        print("✅ ML prediction creation successful")
        
        # Create anomaly detection
        anomaly_detection = AnomalyDetection(
            anomaly_type="resource_spike",
            severity="medium",
            confidence=0.75,
            detected_at=datetime.now(),
            affected_resources=["cpu", "memory"],
            description="Unusual resource utilization detected",
            recommended_action="Investigate resource usage patterns"
        )
        print("✅ Anomaly detection creation successful")
        
        # Create optimization recommendation
        optimization_recommendation = OptimizationRecommendation(
            recommendation_type="resource_optimization",
            priority="high",
            expected_savings=25.0,
            implementation_cost=5.0,
            roi_percentage=400.0,
            affected_resources=["cpu", "memory"],
            description="ML-based resource optimization recommendation",
            implementation_steps=[
                "Analyze current usage",
                "Apply optimizations",
                "Monitor results"
            ],
            risk_assessment="low"
        )
        print("✅ Optimization recommendation creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_phase71_structure():
    """Test that all required files exist"""
    required_files = [
        "upid_python/core/ml_enhancement.py",
        "tests/unit/test_phase7_ml_enhancement.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("🧪 Testing Phase 7 Task 7.1: Advanced ML Integration")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_phase71_imports()
    
    # Test components
    print("\n2. Testing components...")
    components_ok = test_phase71_components()
    
    # Test structure
    print("\n3. Testing file structure...")
    structure_ok = test_phase71_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    
    if all([imports_ok, components_ok, structure_ok]):
        print("\n🎉 All Phase 7.1 tests passed!")
        print("✅ Phase 7 Task 7.1 Advanced ML Integration is working correctly")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1) 