"""
Phase 7: Machine Learning Enhancement Unit Tests
Tests ML models, predictions, anomaly detection, optimization recommendations, and ML enhancement engine
"""

import pytest
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

from upid_python.core.ml_enhancement import (
    MLEnhancementEngine, MLModelType, MLPrediction, AnomalyDetection,
    OptimizationRecommendation, PredictionConfidence, BaseMLModel,
    ResourcePredictionModel, AnomalyDetectionModel, SecurityThreatModel,
    OptimizationModel
)
from upid_python.auth.enterprise_auth import EnterpriseAuthManager, AuthSession, UserPrincipal
from upid_python.core.auth_analytics_integration import AuthAnalyticsIntegration
from upid_python.core.realtime_monitoring import RealTimeMonitor

logger = logging.getLogger(__name__)


@pytest.fixture
def mock_auth_manager():
    """Mock enterprise auth manager"""
    manager = Mock(spec=EnterpriseAuthManager)
    manager.sessions = {}
    return manager


@pytest.fixture
def mock_auth_analytics():
    """Mock auth analytics integration"""
    analytics = Mock(spec=AuthAnalyticsIntegration)
    analytics.run_comprehensive_auth_analytics = AsyncMock()
    return analytics


@pytest.fixture
def mock_monitor():
    """Mock real-time monitor"""
    monitor = Mock(spec=RealTimeMonitor)
    monitor.get_dashboard_metrics = Mock()
    return monitor


@pytest.fixture
def mock_ml_engine(mock_auth_manager, mock_auth_analytics, mock_monitor):
    """Mock ML enhancement engine"""
    engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
    return engine


@pytest.fixture
def sample_auth_session():
    """Sample auth session for testing"""
    user_principal = UserPrincipal(
        user_id="test-user",
        email="test@example.com",
        display_name="Test User",
        groups=["admin"],
        roles=["admin"],
        claims={"permissions": "read,write"}
    )
    
    session = AuthSession(
        session_id="test-session-123",
        user_principal=user_principal,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1),
        last_activity=datetime.now(),
        risk_score=0.3
    )
    return session


class TestBaseMLModel:
    """Test base ML model functionality"""
    
    @pytest.mark.asyncio
    async def test_base_model_initialization(self):
        """Test base ML model initialization"""
        model = BaseMLModel(MLModelType.RESOURCE_PREDICTION, "test_model.pkl")
        
        assert model.model_type == MLModelType.RESOURCE_PREDICTION
        assert model.model_path == "test_model.pkl"
        assert model.model is None
        assert not model.is_trained
        assert model.last_training is None
        assert model.performance_metrics == {}
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self):
        """Test confidence score calculation"""
        model = BaseMLModel(MLModelType.RESOURCE_PREDICTION)
        
        # Test with high confidence
        with patch('numpy.random.uniform', return_value=0.95):
            score, level = model._calculate_confidence({})
            assert score == 0.95
            assert level == PredictionConfidence.VERY_HIGH
        
        # Test with medium confidence
        with patch('numpy.random.uniform', return_value=0.5):
            score, level = model._calculate_confidence({})
            assert score == 0.5
            assert level == PredictionConfidence.MEDIUM
        
        # Test with low confidence
        with patch('numpy.random.uniform', return_value=0.2):
            score, level = model._calculate_confidence({})
            assert score == 0.2
            assert level == PredictionConfidence.LOW
    
    @pytest.mark.asyncio
    async def test_model_save_load(self, tmp_path):
        """Test model save and load functionality"""
        model = BaseMLModel(MLModelType.RESOURCE_PREDICTION, str(tmp_path / "test_model.pkl"))
        model.model = {"test": "data"}
        model.is_trained = True
        
        # Test save
        success = await model.save_model()
        assert success
        
        # Test load
        new_model = BaseMLModel(MLModelType.RESOURCE_PREDICTION, str(tmp_path / "test_model.pkl"))
        success = await new_model.load_model()
        assert success
        assert new_model.model == {"test": "data"}
        assert new_model.is_trained


class TestResourcePredictionModel:
    """Test resource prediction model"""
    
    @pytest.mark.asyncio
    async def test_resource_model_initialization(self):
        """Test resource prediction model initialization"""
        model = ResourcePredictionModel()
        
        assert model.model_type == MLModelType.RESOURCE_PREDICTION
        assert model.model_path == "models/resource_prediction.pkl"
        assert len(model.feature_columns) == 18  # 18 feature columns
    
    @pytest.mark.asyncio
    async def test_resource_prediction(self):
        """Test resource usage prediction"""
        model = ResourcePredictionModel()
        
        features = {
            'cpu_usage_24h_avg': 0.6,
            'memory_usage_24h_avg': 0.7,
            'network_io_24h_avg': 500,
            'request_count_24h': 5000,
            'error_rate_24h': 0.02,
            'cost_per_hour_24h_avg': 50
        }
        
        prediction = await model.predict(features)
        
        assert isinstance(prediction, MLPrediction)
        assert prediction.model_type == MLModelType.RESOURCE_PREDICTION
        assert prediction.prediction_id.startswith("resource_pred_")
        assert isinstance(prediction.confidence_score, float)
        assert prediction.confidence_score >= 0.7
        assert prediction.confidence_score <= 0.95
        assert prediction.features_used == model.feature_columns
        assert 'cpu_prediction_7d' in prediction.prediction
        assert 'memory_prediction_7d' in prediction.prediction
        assert 'scaling_recommendations' in prediction.prediction
    
    @pytest.mark.asyncio
    async def test_resource_model_training(self):
        """Test resource model training"""
        model = ResourcePredictionModel()
        
        training_data = [
            {
                'cpu_usage_24h_avg': 0.5,
                'memory_usage_24h_avg': 0.6,
                'target_cpu_prediction': 0.6,
                'target_memory_prediction': 0.7
            }
            for _ in range(10)
        ]
        
        success = await model.train(training_data)
        
        assert success
        assert model.is_trained
        assert model.last_training is not None
        assert 'accuracy' in model.performance_metrics
        assert 'precision' in model.performance_metrics
        assert 'recall' in model.performance_metrics


class TestAnomalyDetectionModel:
    """Test anomaly detection model"""
    
    @pytest.mark.asyncio
    async def test_anomaly_model_initialization(self):
        """Test anomaly detection model initialization"""
        model = AnomalyDetectionModel()
        
        assert model.model_type == MLModelType.ANOMALY_DETECTION
        assert model.model_path == "models/anomaly_detection.pkl"
        assert len(model.anomaly_types) == 6
    
    @pytest.mark.asyncio
    async def test_anomaly_detection(self):
        """Test anomaly detection"""
        model = AnomalyDetectionModel()
        
        metrics = {
            'active_sessions': 50,
            'failed_auth_attempts': 5,
            'security_incidents': 2,
            'risk_score': 0.6,
            'success_rate': 0.95
        }
        
        # Mock random to simulate anomaly detection
        with patch('numpy.random.random', return_value=0.05):  # 5% chance of anomaly
            with patch('numpy.random.choice', side_effect=['resource_spike', 'high']):
                anomalies = await model.detect_anomalies(metrics)
        
        assert isinstance(anomalies, list)
        if anomalies:  # If anomaly detected
            anomaly = anomalies[0]
            assert isinstance(anomaly, AnomalyDetection)
            assert anomaly.anomaly_type == 'resource_spike'
            assert anomaly.severity == 'high'
            assert anomaly.confidence_score >= 0.7
            assert anomaly.confidence_score <= 0.95
            assert len(anomaly.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_anomaly_detection_no_anomaly(self):
        """Test anomaly detection when no anomaly is detected"""
        model = AnomalyDetectionModel()
        
        metrics = {
            'active_sessions': 10,
            'failed_auth_attempts': 0,
            'security_incidents': 0,
            'risk_score': 0.1,
            'success_rate': 1.0
        }
        
        # Mock random to simulate no anomaly
        with patch('numpy.random.random', return_value=0.9):  # 90% chance of no anomaly
            anomalies = await model.detect_anomalies(metrics)
        
        assert isinstance(anomalies, list)
        assert len(anomalies) == 0


class TestSecurityThreatModel:
    """Test security threat model"""
    
    @pytest.mark.asyncio
    async def test_security_model_initialization(self):
        """Test security threat model initialization"""
        model = SecurityThreatModel()
        
        assert model.model_type == MLModelType.SECURITY_THREAT
        assert model.model_path == "models/security_threat.pkl"
        assert len(model.threat_types) == 6
    
    @pytest.mark.asyncio
    async def test_threat_detection(self):
        """Test security threat detection"""
        model = SecurityThreatModel()
        
        security_data = {
            'security_incidents': 3,
            'high_risk_behaviors': 2,
            'failed_auth_events': 15
        }
        
        # Mock random to simulate threat detection
        with patch('numpy.random.random', return_value=0.03):  # 3% chance of threat
            with patch('numpy.random.choice', side_effect=['brute_force_attack', 'high']):
                threats = await model.detect_threats(security_data)
        
        assert isinstance(threats, list)
        if threats:  # If threat detected
            threat = threats[0]
            assert isinstance(threat, dict)
            assert threat['threat_type'] == 'brute_force_attack'
            assert threat['severity'] == 'high'
            assert threat['confidence_score'] >= 0.8
            assert threat['confidence_score'] <= 0.98
            assert 'risk_score' in threat
            assert len(threat['recommendations']) > 0


class TestOptimizationModel:
    """Test optimization model"""
    
    @pytest.mark.asyncio
    async def test_optimization_model_initialization(self):
        """Test optimization model initialization"""
        model = OptimizationModel()
        
        assert model.model_type == MLModelType.COST_OPTIMIZATION
        assert model.model_path == "models/optimization.pkl"
        assert len(model.optimization_types) == 5
    
    @pytest.mark.asyncio
    async def test_optimization_recommendations(self):
        """Test optimization recommendation generation"""
        model = OptimizationModel()
        
        cluster_data = {
            'active_sessions': 25,
            'total_users': 10,
            'avg_risk_score': 0.4,
            'security_incidents': 1
        }
        
        recommendations = await model.generate_recommendations(cluster_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 2  # Should generate 2 recommendations
        
        for rec in recommendations:
            assert isinstance(rec, OptimizationRecommendation)
            assert rec.optimization_type in model.optimization_types
            assert rec.target_entity == 'cluster-1'
            assert rec.confidence_score >= 0.7
            assert rec.confidence_score <= 0.95
            assert 'risk_level' in rec.risk_assessment
            assert len(rec.implementation_steps) > 0
            assert len(rec.rollback_plan) > 0
            assert 'cost_savings' in rec.expected_impact


class TestMLEnhancementEngine:
    """Test ML enhancement engine"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test ML enhancement engine initialization"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        assert engine.auth_manager == mock_auth_manager
        assert engine.auth_analytics == mock_auth_analytics
        assert engine.monitor == mock_monitor
        assert len(engine.models) == 0  # Models are loaded during initialize()
        assert not engine.is_processing
        assert engine.processing_thread is None
    
    @pytest.mark.asyncio
    async def test_load_all_models(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test loading all ML models"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        await engine._load_all_models()
        
        # Verify models were loaded
        assert len(engine.models) == 4  # 4 model types
        assert MLModelType.RESOURCE_PREDICTION in engine.models
        assert MLModelType.ANOMALY_DETECTION in engine.models
        assert MLModelType.SECURITY_THREAT in engine.models
        assert MLModelType.OPTIMIZATION in engine.models
    
    @pytest.mark.asyncio
    async def test_ml_processing_start_stop(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test ML processing start and stop"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Test start
        await engine.start_ml_processing(interval_seconds=60)
        assert engine.ml_active
        assert engine.ml_thread is not None
        
        # Test stop
        await engine.stop_ml_processing()
        assert not engine.ml_active
    
    @pytest.mark.asyncio
    async def test_ml_processing_cycle(self, mock_auth_manager, mock_auth_analytics, mock_monitor, sample_auth_session):
        """Test ML processing cycle"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Setup mock data
        mock_auth_manager.sessions = {"session1": sample_auth_session}
        mock_auth_analytics.run_comprehensive_auth_analytics.return_value = Mock()
        mock_monitor.get_dashboard_metrics.return_value = Mock()
        
        # Mock model methods
        for model in engine.models.values():
            model.predict = AsyncMock(return_value=Mock())
            model.detect_anomalies = AsyncMock(return_value=[])
            model.detect_threats = AsyncMock(return_value=[])
            model.generate_recommendations = AsyncMock(return_value=[])
        
        # Run processing cycle
        await engine._ml_processing_cycle()
        
        # Verify all processing methods were called
        mock_auth_analytics.run_comprehensive_auth_analytics.assert_called_once()
        mock_monitor.get_dashboard_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_predictions(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test getting predictions"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Add some mock predictions to the queue
        mock_prediction = Mock(spec=MLPrediction)
        mock_prediction.model_type = MLModelType.RESOURCE_PREDICTION
        engine.processing_queue.append(mock_prediction)
        
        # Test get all predictions
        predictions = await engine.get_predictions()
        assert len(predictions) == 1
        assert predictions[0] == mock_prediction
        
        # Test get filtered predictions
        predictions = await engine.get_predictions(MLModelType.RESOURCE_PREDICTION)
        assert len(predictions) == 1
        
        predictions = await engine.get_predictions(MLModelType.ANOMALY_DETECTION)
        assert len(predictions) == 0
    
    @pytest.mark.asyncio
    async def test_get_optimization_recommendations(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test getting optimization recommendations"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Add some mock recommendations to the queue
        mock_recommendation = Mock(spec=OptimizationRecommendation)
        engine.processing_queue.append(mock_recommendation)
        
        recommendations = await engine.get_optimization_recommendations()
        assert len(recommendations) == 1
        assert recommendations[0] == mock_recommendation
    
    @pytest.mark.asyncio
    async def test_train_model(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test training a model"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Mock the train method
        engine.models[MLModelType.RESOURCE_PREDICTION].train = AsyncMock(return_value=True)
        
        training_data = [{"feature": "value"} for _ in range(10)]
        success = await engine.train_model(MLModelType.RESOURCE_PREDICTION, training_data)
        
        assert success
        engine.models[MLModelType.RESOURCE_PREDICTION].train.assert_called_once_with(training_data)
    
    @pytest.mark.asyncio
    async def test_get_model_performance(self, mock_auth_manager, mock_auth_analytics, mock_monitor):
        """Test getting model performance"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Mock a trained model
        model = engine.models[MLModelType.RESOURCE_PREDICTION]
        model.is_trained = True
        model.last_training = datetime.now()
        model.performance_metrics = {"accuracy": 0.85, "precision": 0.80}
        
        performance = await engine.get_model_performance(MLModelType.RESOURCE_PREDICTION)
        
        assert performance["model_type"] == "resource_prediction"
        assert performance["is_trained"] is True
        assert performance["last_training"] is not None
        assert "accuracy" in performance["performance_metrics"]
        assert "precision" in performance["performance_metrics"]
    
    @pytest.mark.asyncio
    async def test_feature_extraction_methods(self, mock_auth_manager, mock_auth_analytics, mock_monitor, sample_auth_session):
        """Test feature extraction methods"""
        engine = MLEnhancementEngine(mock_auth_manager, mock_auth_analytics, mock_monitor)
        
        # Test resource features extraction
        auth_sessions = [sample_auth_session]
        analytics_report = Mock()
        
        features = engine._extract_resource_features(auth_sessions, analytics_report)
        assert isinstance(features, dict)
        assert 'cpu_usage_24h_avg' in features
        assert 'memory_usage_24h_avg' in features
        assert 'cost_per_hour_24h_avg' in features
        
        # Test anomaly metrics extraction
        dashboard_metrics = Mock()
        dashboard_metrics.active_sessions = 10
        dashboard_metrics.failed_auth_attempts = 2
        dashboard_metrics.security_incidents = 1
        dashboard_metrics.risk_score = 0.3
        dashboard_metrics.success_rate = 0.95
        
        metrics = engine._extract_anomaly_metrics(dashboard_metrics, analytics_report)
        assert isinstance(metrics, dict)
        assert metrics['active_sessions'] == 10
        assert metrics['failed_auth_attempts'] == 2
        assert metrics['security_incidents'] == 1
        assert metrics['risk_score'] == 0.3
        assert metrics['success_rate'] == 0.95
        
        # Test security data extraction
        analytics_report.security_incidents = [Mock(), Mock()]
        analytics_report.user_behavior_patterns = [Mock(risk_score=0.8), Mock(risk_score=0.3)]
        analytics_report.authentication_metrics = {'failed_auth_events': 15}
        
        security_data = engine._extract_security_data(analytics_report)
        assert isinstance(security_data, dict)
        assert security_data['security_incidents'] == 2
        assert security_data['high_risk_behaviors'] == 1
        assert security_data['failed_auth_events'] == 15
        
        # Test cluster data extraction
        cluster_data = engine._extract_cluster_data(auth_sessions, analytics_report)
        assert isinstance(cluster_data, dict)
        assert cluster_data['active_sessions'] == 1
        assert cluster_data['total_users'] == 1
        assert cluster_data['avg_risk_score'] == 0.3


class TestMLPrediction:
    """Test ML prediction data structure"""
    
    def test_ml_prediction_creation(self):
        """Test ML prediction creation"""
        prediction_data = {
            'cpu_prediction_7d': 0.6,
            'memory_prediction_7d': 0.7,
            'cost_prediction_7d': 100
        }
        
        prediction = MLPrediction(
            prediction_id="test_pred_123",
            model_type=MLModelType.RESOURCE_PREDICTION,
            prediction=prediction_data,
            confidence_score=0.85,
            confidence_level=PredictionConfidence.HIGH,
            timestamp=datetime.now(),
            features_used=['cpu_usage_24h_avg', 'memory_usage_24h_avg'],
            model_version="1.0.0"
        )
        
        assert prediction.prediction_id == "test_pred_123"
        assert prediction.model_type == MLModelType.RESOURCE_PREDICTION
        assert prediction.prediction == prediction_data
        assert prediction.confidence_score == 0.85
        assert prediction.confidence_level == PredictionConfidence.HIGH
        assert len(prediction.features_used) == 2
        assert prediction.model_version == "1.0.0"


class TestAnomalyDetection:
    """Test anomaly detection data structure"""
    
    def test_anomaly_detection_creation(self):
        """Test anomaly detection creation"""
        anomaly = AnomalyDetection(
            anomaly_id="anomaly_123",
            anomaly_type="resource_spike",
            severity="high",
            confidence_score=0.9,
            detected_at=datetime.now(),
            description="Detected CPU usage spike",
            affected_entities=["cluster-1", "namespace-default"],
            recommendations=["Scale up CPU", "Check for resource leaks"],
            metadata={"detection_method": "ml_model"}
        )
        
        assert anomaly.anomaly_id == "anomaly_123"
        assert anomaly.anomaly_type == "resource_spike"
        assert anomaly.severity == "high"
        assert anomaly.confidence_score == 0.9
        assert len(anomaly.affected_entities) == 2
        assert len(anomaly.recommendations) == 2
        assert anomaly.metadata["detection_method"] == "ml_model"


class TestOptimizationRecommendation:
    """Test optimization recommendation data structure"""
    
    def test_optimization_recommendation_creation(self):
        """Test optimization recommendation creation"""
        recommendation = OptimizationRecommendation(
            recommendation_id="opt_123",
            optimization_type="cost_reduction",
            target_entity="cluster-1",
            current_state={"cpu_usage": 0.6, "cost_per_hour": 50},
            recommended_state={"cpu_usage": 0.5, "cost_per_hour": 40},
            expected_impact={"cost_savings": 10, "performance_improvement": 5},
            confidence_score=0.85,
            risk_assessment={"risk_level": "low", "rollback_complexity": "low"},
            implementation_steps=["Analyze usage", "Apply changes"],
            rollback_plan=["Revert changes", "Restore backup"]
        )
        
        assert recommendation.recommendation_id == "opt_123"
        assert recommendation.optimization_type == "cost_reduction"
        assert recommendation.target_entity == "cluster-1"
        assert recommendation.current_state["cpu_usage"] == 0.6
        assert recommendation.recommended_state["cost_per_hour"] == 40
        assert recommendation.expected_impact["cost_savings"] == 10
        assert recommendation.confidence_score == 0.85
        assert recommendation.risk_assessment["risk_level"] == "low"
        assert len(recommendation.implementation_steps) == 2
        assert len(recommendation.rollback_plan) == 2


if __name__ == "__main__":
    pytest.main([__file__]) 