"""
Unit tests for Phase 1: Advanced Analytics & Intelligence Engine
Tests all core components: PatternRecognitionEngine, AnomalyDetectionEngine, PredictiveAnalyticsEngine, BusinessIntelligenceEngine, AdvancedAnalyticsEngine
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from upid.core.advanced_analytics import (
    PatternRecognitionEngine, AnomalyDetectionEngine, PredictiveAnalyticsEngine,
    BusinessIntelligenceEngine, AdvancedAnalyticsEngine, Pattern, Anomaly, Prediction
)

pytest_plugins = ["pytest_asyncio"]


class TestPatternRecognitionEngine:
    """Test PatternRecognitionEngine functionality"""
    
    def setup_method(self):
        self.engine = PatternRecognitionEngine()
    
    def test_init(self):
        """Test PatternRecognitionEngine initialization"""
        assert hasattr(self.engine, 'patterns')
        assert hasattr(self.engine, 'pattern_detectors')
        assert len(self.engine.pattern_detectors) == 5  # business_cycles, resource_spikes, request_patterns, error_patterns, cost_patterns
    
    def test_analyze_patterns(self):
        """Test comprehensive pattern analysis"""
        test_data = {
            'log_analysis': {
                'request_patterns': {
                    'hourly_distribution': {i: 10 for i in range(24)},
                    'endpoints': {'/api/users': 100, '/api/orders': 50, '/health': 10},
                    'status_codes': {'200': 150, '404': 5, '500': 5}
                }
            },
            'metrics_analysis': {
                'cpu_usage': {'average': 85.0},
                'memory_usage': {'average': 90.0}
            },
            'business_impact': {
                'efficiency_score': 30.0,
                'business_request_ratio': 0.8
            }
        }
        
        patterns = self.engine.analyze_patterns(test_data)
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Check that patterns have required attributes
        for pattern in patterns:
            assert hasattr(pattern, 'pattern_type')
            assert hasattr(pattern, 'confidence')
            assert hasattr(pattern, 'description')
            assert hasattr(pattern, 'severity')
    
    def test_detect_business_cycles(self):
        """Test business cycle detection"""
        test_data = {
            'log_analysis': {
                'request_patterns': {
                    'hourly_distribution': {i: 10 for i in range(24)}
                }
            }
        }
        
        # Set peak hours
        test_data['log_analysis']['request_patterns']['hourly_distribution'][9] = 100  # 9 AM peak
        test_data['log_analysis']['request_patterns']['hourly_distribution'][14] = 80   # 2 PM peak
        
        patterns = self.engine._detect_business_cycles(test_data)
        assert len(patterns) > 0
        
        # Check that business cycle patterns are detected
        business_cycles = [p for p in patterns if p.pattern_type == "business_cycle"]
        assert len(business_cycles) > 0
    
    def test_detect_resource_spikes(self):
        """Test resource spike detection"""
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 85.0},
                'memory_usage': {'average': 90.0}
            }
        }
        
        patterns = self.engine._detect_resource_spikes(test_data)
        assert len(patterns) > 0
        
        # Check that resource spike patterns are detected
        resource_spikes = [p for p in patterns if p.pattern_type == "resource_spike"]
        assert len(resource_spikes) > 0
        
        # Check CPU spike detection
        cpu_spikes = [p for p in resource_spikes if "CPU" in p.description]
        assert len(cpu_spikes) > 0
        
        # Check memory spike detection
        memory_spikes = [p for p in resource_spikes if "memory" in p.description.lower()]
        assert len(memory_spikes) > 0
    
    def test_detect_request_patterns(self):
        """Test request pattern detection"""
        test_data = {
            'log_analysis': {
                'request_patterns': {
                    'endpoints': {'/api/users': 100, '/api/orders': 50, '/health': 10}
                }
            }
        }
        
        patterns = self.engine._detect_request_patterns(test_data)
        assert len(patterns) > 0
        
        # Check that request patterns are detected
        request_patterns = [p for p in patterns if p.pattern_type == "request_pattern"]
        assert len(request_patterns) > 0
    
    def test_detect_error_patterns(self):
        """Test error pattern detection"""
        test_data = {
            'log_analysis': {
                'request_patterns': {
                    'status_codes': {'200': 80, '404': 10, '500': 10}  # 20% error rate
                }
            }
        }
        
        patterns = self.engine._detect_error_patterns(test_data)
        assert len(patterns) > 0
        
        # Check that error patterns are detected
        error_patterns = [p for p in patterns if p.pattern_type == "error_pattern"]
        assert len(error_patterns) > 0
    
    def test_detect_cost_patterns(self):
        """Test cost pattern detection"""
        test_data = {
            'business_impact': {
                'efficiency_score': 25.0,
                'business_request_ratio': 0.8
            }
        }
        
        patterns = self.engine._detect_cost_patterns(test_data)
        assert len(patterns) > 0
        
        # Check that cost patterns are detected
        cost_patterns = [p for p in patterns if p.pattern_type == "cost_pattern"]
        assert len(cost_patterns) > 0


class TestAnomalyDetectionEngine:
    """Test AnomalyDetectionEngine functionality"""
    
    def setup_method(self):
        self.engine = AnomalyDetectionEngine()
    
    def test_init(self):
        """Test AnomalyDetectionEngine initialization"""
        assert hasattr(self.engine, 'baselines')
        assert hasattr(self.engine, 'anomalies')
        assert hasattr(self.engine, 'detection_methods')
        assert len(self.engine.detection_methods) == 3  # statistical, threshold, trend
    
    def test_detect_anomalies(self):
        """Test comprehensive anomaly detection"""
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 95.0},
                'memory_usage': {'average': 90.0}
            }
        }
        
        # Mock historical data
        historical_data = [
            {
                'metrics_analysis': {
                    'cpu_usage': {'average': 50.0},
                    'memory_usage': {'average': 60.0}
                }
            }
        ] * 7  # 7 days of data
        
        anomalies = self.engine.detect_anomalies(test_data, historical_data)
        assert isinstance(anomalies, list)
        assert len(anomalies) > 0
        
        # Check that anomalies have required attributes
        for anomaly in anomalies:
            assert hasattr(anomaly, 'anomaly_type')
            assert hasattr(anomaly, 'severity')
            assert hasattr(anomaly, 'confidence')
            assert hasattr(anomaly, 'description')
    
    def test_update_baselines(self):
        """Test baseline updates from historical data"""
        historical_data = [
            {
                'metrics_analysis': {
                    'cpu_usage': {'average': 50.0},
                    'memory_usage': {'average': 60.0}
                }
            }
        ] * 10  # 10 data points
        
        self.engine._update_baselines(historical_data)
        
        assert 'cpu' in self.engine.baselines
        assert 'memory' in self.engine.baselines
        assert 'mean' in self.engine.baselines['cpu']
        assert 'std' in self.engine.baselines['cpu']
    
    def test_statistical_anomaly_detection(self):
        """Test statistical anomaly detection"""
        # Set up baselines
        self.engine.baselines = {
            'cpu': {'mean': 50.0, 'std': 10.0},
            'memory': {'mean': 60.0, 'std': 15.0}
        }
        
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 85.0},  # High anomaly
                'memory_usage': {'average': 90.0}  # High anomaly
            }
        }
        
        anomalies = self.engine._statistical_anomaly_detection(test_data)
        assert len(anomalies) > 0
        
        # Check that statistical anomalies are detected
        statistical_anomalies = [a for a in anomalies if a.anomaly_type == "statistical"]
        assert len(statistical_anomalies) > 0
    
    def test_threshold_anomaly_detection(self):
        """Test threshold-based anomaly detection"""
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 95.0},  # Critical threshold
                'memory_usage': {'average': 90.0}  # High threshold
            }
        }
        
        anomalies = self.engine._threshold_anomaly_detection(test_data)
        assert len(anomalies) > 0
        
        # Check that threshold anomalies are detected
        threshold_anomalies = [a for a in anomalies if a.anomaly_type == "threshold"]
        assert len(threshold_anomalies) > 0
        
        # Check severity levels
        critical_anomalies = [a for a in threshold_anomalies if a.severity == "critical"]
        high_anomalies = [a for a in threshold_anomalies if a.severity == "high"]
        assert len(critical_anomalies) > 0 or len(high_anomalies) > 0


class TestPredictiveAnalyticsEngine:
    """Test PredictiveAnalyticsEngine functionality"""
    
    def setup_method(self):
        self.engine = PredictiveAnalyticsEngine()
    
    def test_init(self):
        """Test PredictiveAnalyticsEngine initialization"""
        assert hasattr(self.engine, 'models')
        assert hasattr(self.engine, 'predictions')
    
    def test_generate_predictions(self):
        """Test comprehensive prediction generation"""
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 75.0},
                'memory_usage': {'average': 80.0}
            },
            'business_impact': {
                'efficiency_score': 60.0,
                'business_request_ratio': 0.7
            }
        }
        
        # Mock historical data
        historical_data = [
            {
                'metrics_analysis': {
                    'cpu_usage': {'average': 70.0},
                    'memory_usage': {'average': 75.0}
                }
            }
        ] * 7  # 7 days of data
        
        predictions = self.engine.generate_predictions(test_data, historical_data)
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        
        # Check that predictions have required attributes
        for prediction in predictions:
            assert hasattr(prediction, 'resource_type')
            assert hasattr(prediction, 'predicted_value')
            assert hasattr(prediction, 'confidence')
            assert hasattr(prediction, 'trend')
            assert hasattr(prediction, 'recommendation')
    
    def test_predict_cpu_usage(self):
        """Test CPU usage prediction"""
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 85.0}
            }
        }
        
        historical_data = [
            {
                'metrics_analysis': {
                    'cpu_usage': {'average': 70.0}
                }
            }
        ] * 7
        
        prediction = self.engine._predict_cpu_usage(test_data, historical_data)
        assert prediction is not None
        assert prediction.resource_type == "cpu"
        assert prediction.confidence > 0
        assert prediction.trend in ["increasing", "decreasing", "stable"]
    
    def test_predict_memory_usage(self):
        """Test memory usage prediction"""
        test_data = {
            'metrics_analysis': {
                'memory_usage': {'average': 85.0}
            }
        }
        
        historical_data = [
            {
                'metrics_analysis': {
                    'memory_usage': {'average': 75.0}
                }
            }
        ] * 7
        
        prediction = self.engine._predict_memory_usage(test_data, historical_data)
        assert prediction is not None
        assert prediction.resource_type == "memory"
        assert prediction.confidence > 0
        assert prediction.trend in ["increasing", "decreasing", "stable"]
    
    def test_predict_cost_trends(self):
        """Test cost trend prediction"""
        test_data = {
            'business_impact': {
                'efficiency_score': 30.0,
                'business_request_ratio': 0.8
            }
        }
        
        prediction = self.engine._predict_cost_trends(test_data, None)
        assert prediction is not None
        assert prediction.resource_type == "cost"
        assert prediction.confidence > 0
        assert prediction.trend in ["increasing", "decreasing", "stable"]


class TestBusinessIntelligenceEngine:
    """Test BusinessIntelligenceEngine functionality"""
    
    def setup_method(self):
        self.engine = BusinessIntelligenceEngine()
    
    def test_init(self):
        """Test BusinessIntelligenceEngine initialization"""
        assert hasattr(self.engine, 'kpi_correlations')
        assert hasattr(self.engine, 'business_insights')
    
    def test_analyze_business_impact(self):
        """Test comprehensive business impact analysis"""
        test_data = {
            'business_impact': {
                'efficiency_score': 65.0,
                'business_request_ratio': 0.75
            },
            'metrics_analysis': {
                'cpu_usage': {'average': 70.0},
                'memory_usage': {'average': 75.0}
            },
            'log_analysis': {
                'total_requests': 1000,
                'business_requests': 750,
                'error_summary': {'404': 20, '500': 10}
            }
        }
        
        insights = self.engine.analyze_business_impact(test_data)
        assert isinstance(insights, dict)
        assert 'efficiency_analysis' in insights
        assert 'cost_analysis' in insights
        assert 'performance_analysis' in insights
        assert 'recommendations' in insights
        assert 'risk_assessment' in insights
    
    def test_analyze_efficiency(self):
        """Test efficiency analysis"""
        test_data = {
            'business_impact': {
                'efficiency_score': 65.0,
                'business_request_ratio': 0.75
            }
        }
        
        analysis = self.engine._analyze_efficiency(test_data)
        assert 'efficiency_score' in analysis
        assert 'business_request_ratio' in analysis
        assert 'efficiency_level' in analysis
        assert 'business_impact' in analysis
        assert 'optimization_potential' in analysis
    
    def test_analyze_cost_impact(self):
        """Test cost impact analysis"""
        test_data = {
            'metrics_analysis': {
                'cpu_usage': {'average': 70.0},
                'memory_usage': {'average': 75.0}
            }
        }
        
        analysis = self.engine._analyze_cost_impact(test_data)
        assert 'current_resource_usage' in analysis
        assert 'cost_optimization_potential' in analysis
        assert 'resource_waste' in analysis
        assert 'cost_impact' in analysis
    
    def test_analyze_performance_impact(self):
        """Test performance impact analysis"""
        test_data = {
            'log_analysis': {
                'total_requests': 1000,
                'business_requests': 750,
                'error_summary': {'404': 20, '500': 10}
            }
        }
        
        analysis = self.engine._analyze_performance_impact(test_data)
        assert 'total_requests' in analysis
        assert 'business_requests' in analysis
        assert 'error_rate' in analysis
        assert 'performance_impact' in analysis
        assert 'availability_score' in analysis
    
    def test_generate_business_recommendations(self):
        """Test business recommendation generation"""
        test_data = {
            'business_impact': {
                'efficiency_score': 30.0,
                'business_request_ratio': 0.3
            },
            'metrics_analysis': {
                'cpu_usage': {'average': 85.0},
                'memory_usage': {'average': 90.0}
            }
        }
        
        recommendations = self.engine._generate_business_recommendations(test_data)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for specific recommendation types
        efficiency_recs = [r for r in recommendations if "efficiency" in r.lower()]
        resource_recs = [r for r in recommendations if "cpu" in r.lower() or "memory" in r.lower()]
        assert len(efficiency_recs) > 0 or len(resource_recs) > 0
    
    def test_assess_business_risks(self):
        """Test business risk assessment"""
        test_data = {
            'business_impact': {
                'efficiency_score': 25.0
            },
            'metrics_analysis': {
                'cpu_usage': {'average': 95.0},
                'memory_usage': {'average': 90.0}
            }
        }
        
        risks = self.engine._assess_business_risks(test_data)
        assert 'high_risk' in risks
        assert 'medium_risk' in risks
        assert 'low_risk' in risks
        assert isinstance(risks['high_risk'], list)
        assert isinstance(risks['medium_risk'], list)
        assert isinstance(risks['low_risk'], list)


class TestAdvancedAnalyticsEngine:
    """Test AdvancedAnalyticsEngine functionality"""
    
    def setup_method(self):
        self.engine = AdvancedAnalyticsEngine()
    
    def test_init(self):
        """Test AdvancedAnalyticsEngine initialization"""
        assert hasattr(self.engine, 'pattern_engine')
        assert hasattr(self.engine, 'anomaly_engine')
        assert hasattr(self.engine, 'predictive_engine')
        assert hasattr(self.engine, 'business_engine')
        assert hasattr(self.engine, 'analyzer')
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self):
        """Test comprehensive analytics analysis"""
        with patch.object(self.engine.analyzer, 'analyze_pod_batch', return_value={
            'pod_name': 'test-pod',
            'namespace': 'default',
            'log_analysis': {
                'request_patterns': {
                    'hourly_distribution': {i: 10 for i in range(24)},
                    'endpoints': {'/api/users': 100, '/api/orders': 50},
                    'status_codes': {'200': 150, '404': 5, '500': 5}
                }
            },
            'metrics_analysis': {
                'cpu_usage': {'average': 85.0},
                'memory_usage': {'average': 90.0}
            },
            'business_impact': {
                'efficiency_score': 65.0,
                'business_request_ratio': 0.75
            }
        }):
            result = await self.engine.comprehensive_analysis('test-pod', 'default', '1h')
            
            assert 'pod_name' in result
            assert 'analysis_timestamp' in result
            assert 'patterns' in result
            assert 'anomalies' in result
            assert 'predictions' in result
            assert 'business_insights' in result
            assert 'summary' in result
    
    def test_pattern_to_dict(self):
        """Test pattern serialization"""
        pattern = Pattern(
            pattern_type="test",
            confidence=0.8,
            description="Test pattern",
            data_points=[{"test": "data"}],
            start_time=datetime.now(),
            end_time=datetime.now(),
            severity="info"
        )
        
        result = self.engine._pattern_to_dict(pattern)
        assert isinstance(result, dict)
        assert result['pattern_type'] == "test"
        assert result['confidence'] == 0.8
        assert result['description'] == "Test pattern"
    
    def test_anomaly_to_dict(self):
        """Test anomaly serialization"""
        anomaly = Anomaly(
            anomaly_type="test",
            severity="high",
            confidence=0.9,
            description="Test anomaly",
            detected_at=datetime.now(),
            affected_metrics=["cpu"],
            baseline_value=50.0,
            current_value=90.0,
            deviation_percentage=80.0
        )
        
        result = self.engine._anomaly_to_dict(anomaly)
        assert isinstance(result, dict)
        assert result['anomaly_type'] == "test"
        assert result['severity'] == "high"
        assert result['confidence'] == 0.9
    
    def test_prediction_to_dict(self):
        """Test prediction serialization"""
        prediction = Prediction(
            resource_type="cpu",
            predicted_value=85.0,
            confidence=0.8,
            time_horizon="24h",
            prediction_date=datetime.now(),
            trend="increasing",
            recommendation="Test recommendation"
        )
        
        result = self.engine._prediction_to_dict(prediction)
        assert isinstance(result, dict)
        assert result['resource_type'] == "cpu"
        assert result['predicted_value'] == 85.0
        assert result['trend'] == "increasing"
    
    def test_generate_summary(self):
        """Test summary generation"""
        patterns = [Pattern("test", 0.8, "Test", [], datetime.now(), datetime.now())]
        anomalies = [Anomaly("test", "high", 0.9, "Test", datetime.now(), [], 50.0, 90.0, 80.0)]
        predictions = [Prediction("cpu", 85.0, 0.8, "24h", datetime.now(), "increasing", "Test")]
        business_insights = {"test": "data"}
        
        summary = self.engine._generate_summary(patterns, anomalies, predictions, business_insights)
        assert 'total_patterns' in summary
        assert 'total_anomalies' in summary
        assert 'total_predictions' in summary
        assert 'overall_health' in summary
        assert 'key_insights' in summary


if __name__ == "__main__":
    pytest.main([__file__]) 