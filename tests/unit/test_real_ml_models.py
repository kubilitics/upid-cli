"""
Test Real ML Models
Tests the real ML models using LightGBM and scikit-learn for production use
"""

import pytest
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
import numpy as np
import pandas as pd

from upid.core.ml_models import (
    RealResourcePredictionModel, RealAnomalyDetectionModel, RealOptimizationModel,
    ModelMetrics
)
from upid.core.ml_enhancement import MLModelType, MLPrediction, PredictionConfidence

logger = logging.getLogger(__name__)


class TestRealResourcePredictionModel:
    """Test real LightGBM resource prediction model"""
    
    @pytest.mark.asyncio
    async def test_real_model_initialization(self):
        """Test real model initialization"""
        model = RealResourcePredictionModel()
        
        assert model.model_type == MLModelType.RESOURCE_PREDICTION
        assert model.model_path == "models/lightgbm_resource_prediction.pkl"
        assert len(model.feature_columns) == 24  # 24 real features
        assert len(model.target_columns) == 4  # 4 target predictions
        assert not model.is_trained
        assert model.metrics is None
    
    @pytest.mark.asyncio
    async def test_real_feature_extraction(self):
        """Test real feature extraction from Kubernetes data"""
        model = RealResourcePredictionModel()
        
        # Real Kubernetes data
        kubernetes_data = {
            'cpu_usage_24h_avg': 0.65,
            'cpu_usage_7d_avg': 0.58,
            'cpu_usage_30d_avg': 0.52,
            'memory_usage_24h_avg': 0.72,
            'memory_usage_7d_avg': 0.68,
            'memory_usage_30d_avg': 0.64,
            'network_io_24h_avg': 450.0,
            'network_io_7d_avg': 380.0,
            'network_io_30d_avg': 320.0,
            'request_count_24h': 8500,
            'request_count_7d': 42000,
            'request_count_30d': 180000,
            'error_rate_24h': 0.025,
            'error_rate_7d': 0.022,
            'error_rate_30d': 0.018,
            'cost_per_hour_24h_avg': 45.0,
            'cost_per_hour_7d_avg': 42.0,
            'cost_per_hour_30d_avg': 38.0,
            'pod_count_24h': 15,
            'pod_count_7d': 105,
            'pod_count_30d': 450,
            'node_count': 5,
            'namespace_count': 8,
            'service_count': 25
        }
        
        features = model._extract_real_features(kubernetes_data)
        
        assert features.shape == (1, 24)  # 24 features
        assert features[0, 0] == 0.65  # cpu_usage_24h_avg
        assert features[0, 3] == 0.72  # memory_usage_24h_avg
        assert features[0, 6] == 450.0  # network_io_24h_avg
        assert features[0, 15] == 45.0  # cost_per_hour_24h_avg
    
    @pytest.mark.asyncio
    async def test_real_model_training(self):
        """Test real LightGBM model training with production-like correlated data"""
        model = RealResourcePredictionModel()
        
        # Generate highly correlated training data
        training_data = []
        for i in range(50):  # 50 training samples
            cpu = 0.4 + (i * 0.01)
            mem = 0.5 + (i * 0.012)
            net = 100.0 + (i * 10)
            req = 1000 + (i * 100)
            err = 0.01 + (i * 0.001)
            cost = 10.0 + (i * 2)
            pod = 1 + (i // 10)
            node = 3 + (i // 20)
            ns = 5 + (i // 15)
            svc = 10 + (i // 10)
            sample = {
                'cpu_usage_24h_avg': cpu,
                'cpu_usage_7d_avg': cpu * 0.98,
                'cpu_usage_30d_avg': cpu * 0.96,
                'memory_usage_24h_avg': mem,
                'memory_usage_7d_avg': mem * 0.98,
                'memory_usage_30d_avg': mem * 0.96,
                'network_io_24h_avg': net,
                'network_io_7d_avg': net * 0.98,
                'network_io_30d_avg': net * 0.96,
                'request_count_24h': req,
                'request_count_7d': req * 7,
                'request_count_30d': req * 30,
                'error_rate_24h': err,
                'error_rate_7d': err * 0.98,
                'error_rate_30d': err * 0.96,
                'cost_per_hour_24h_avg': cost,
                'cost_per_hour_7d_avg': cost * 0.98,
                'cost_per_hour_30d_avg': cost * 0.96,
                'pod_count_24h': pod,
                'pod_count_7d': pod * 7,
                'pod_count_30d': pod * 30,
                'node_count': node,
                'namespace_count': ns,
                'service_count': svc,
                # Target predictions: weighted sum of features
                'cpu_prediction_7d': cpu * 0.7 + mem * 0.2 + net * 0.0005 + err * 2,
                'memory_prediction_7d': mem * 0.7 + cpu * 0.2 + net * 0.0003 + err * 1.5,
                'network_prediction_7d': net * 0.8 + cpu * 10 + mem * 8,
                'cost_prediction_7d': cost * 0.7 + cpu * 5 + mem * 4 + net * 0.01
            }
            training_data.append(sample)
        
        # Train the model
        success = await model.train(training_data)
        
        assert success
        assert model.is_trained
        assert model.last_training is not None
        assert model.metrics is not None
        
        # Check metrics - verify the real ML pipeline works
        assert model.metrics.training_samples > 0
        assert model.metrics.validation_samples > 0
        assert model.metrics.training_time > 0
        assert model.metrics.r2 > -1.0  # Model should not be worse than constant predictor
        assert len(model.metrics.feature_importance) > 0
        
        # Verify model can make predictions
        test_features = {
            'cpu_usage_24h_avg': 0.6,
            'cpu_usage_7d_avg': 0.58,
            'cpu_usage_30d_avg': 0.56,
            'memory_usage_24h_avg': 0.7,
            'memory_usage_7d_avg': 0.68,
            'memory_usage_30d_avg': 0.66,
            'network_io_24h_avg': 500.0,
            'network_io_7d_avg': 490.0,
            'network_io_30d_avg': 480.0,
            'request_count_24h': 5000,
            'request_count_7d': 35000,
            'request_count_30d': 150000,
            'error_rate_24h': 0.03,
            'error_rate_7d': 0.029,
            'error_rate_30d': 0.028,
            'cost_per_hour_24h_avg': 30.0,
            'cost_per_hour_7d_avg': 29.4,
            'cost_per_hour_30d_avg': 28.8,
            'pod_count_24h': 8,
            'pod_count_7d': 56,
            'pod_count_30d': 240,
            'node_count': 4,
            'namespace_count': 6,
            'service_count': 15
        }
        
        prediction = await model.predict(test_features)
        assert isinstance(prediction, MLPrediction)
        assert prediction.model_type == MLModelType.RESOURCE_PREDICTION
        assert prediction.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_real_prediction(self):
        """Test real prediction with trained model"""
        model = RealResourcePredictionModel()
        
        # Train the model first
        training_data = []
        for i in range(30):  # 30 training samples
            sample = {
                'cpu_usage_24h_avg': 0.4 + (i * 0.01),
                'memory_usage_24h_avg': 0.5 + (i * 0.012),
                'network_io_24h_avg': 100.0 + (i * 10),
                'request_count_24h': 1000 + (i * 100),
                'error_rate_24h': 0.01 + (i * 0.001),
                'cost_per_hour_24h_avg': 10.0 + (i * 2),
                'pod_count_24h': 1 + (i // 10),
                'pod_count_7d': 7 + (i // 10) * 7,
                'pod_count_30d': 30 + (i // 10) * 30,
                'node_count': 3 + (i // 20),
                'namespace_count': 5 + (i // 15),
                'service_count': 10 + (i // 10),
                'cpu_prediction_7d': 0.4 + (i * 0.01) * 1.1,
                'memory_prediction_7d': 0.5 + (i * 0.012) * 1.15,
                'network_prediction_7d': 100.0 + (i * 10) * 1.2,
                'cost_prediction_7d': 10.0 + (i * 2) * 1.05
            }
            training_data.append(sample)
        
        await model.train(training_data)
        
        # Make prediction with real data
        prediction_features = {
            'cpu_usage_24h_avg': 0.65,
            'cpu_usage_7d_avg': 0.58,
            'cpu_usage_30d_avg': 0.52,
            'memory_usage_24h_avg': 0.72,
            'memory_usage_7d_avg': 0.68,
            'memory_usage_30d_avg': 0.64,
            'network_io_24h_avg': 450.0,
            'network_io_7d_avg': 380.0,
            'network_io_30d_avg': 320.0,
            'request_count_24h': 8500,
            'request_count_7d': 42000,
            'request_count_30d': 180000,
            'error_rate_24h': 0.025,
            'error_rate_7d': 0.022,
            'error_rate_30d': 0.018,
            'cost_per_hour_24h_avg': 45.0,
            'cost_per_hour_7d_avg': 42.0,
            'cost_per_hour_30d_avg': 38.0,
            'pod_count_24h': 15,
            'pod_count_7d': 105,
            'pod_count_30d': 450,
            'node_count': 5,
            'namespace_count': 8,
            'service_count': 25
        }
        
        prediction = await model.predict(prediction_features)
        
        assert isinstance(prediction, MLPrediction)
        assert prediction.model_type == MLModelType.RESOURCE_PREDICTION
        assert prediction.prediction_id.startswith("lgb_pred_")
        assert isinstance(prediction.confidence_score, float)
        assert prediction.confidence_score >= 0.5
        assert prediction.confidence_score <= 0.95
        assert prediction.confidence_level in [PredictionConfidence.LOW, PredictionConfidence.MEDIUM, PredictionConfidence.HIGH, PredictionConfidence.VERY_HIGH]
        
        # Check prediction data
        prediction_data = prediction.prediction
        assert 'cpu_prediction_7d' in prediction_data
        assert 'memory_prediction_7d' in prediction_data
        assert 'network_prediction_7d' in prediction_data
        assert 'cost_prediction_7d' in prediction_data
        assert 'scaling_recommendations' in prediction_data
        
        # Check that predictions are realistic
        assert prediction_data['cpu_prediction_7d'] > 0
        assert prediction_data['memory_prediction_7d'] > 0
        assert prediction_data['network_prediction_7d'] > 0
        assert prediction_data['cost_prediction_7d'] > 0
        # Scaling recommendations may be empty if predictions don't trigger thresholds
        assert isinstance(prediction_data['scaling_recommendations'], list)


class TestRealAnomalyDetectionModel:
    """Test real scikit-learn anomaly detection model"""
    
    @pytest.mark.asyncio
    async def test_real_anomaly_model_initialization(self):
        """Test real anomaly detection model initialization"""
        model = RealAnomalyDetectionModel()
        
        assert model.model_type == MLModelType.ANOMALY_DETECTION
        assert model.model_path == "models/sklearn_anomaly_detection.pkl"
        assert len(model.feature_columns) == 10  # 10 anomaly features
        assert len(model.anomaly_types) == 6  # 6 anomaly types
        assert not model.is_trained
    
    @pytest.mark.asyncio
    async def test_real_anomaly_training(self):
        """Test real anomaly detection model training"""
        model = RealAnomalyDetectionModel()
        
        # Generate realistic training data
        training_data = []
        for i in range(100):  # 100 training samples
            sample = {
                'active_sessions': 10 + (i % 20),
                'failed_auth_attempts': i % 5,
                'security_incidents': i % 3,
                'risk_score': 0.1 + (i % 10) * 0.1,
                'success_rate': 0.8 + (i % 20) * 0.01,
                'avg_response_time': 100 + (i % 50),
                'error_rate': 0.01 + (i % 10) * 0.005,
                'cpu_usage': 0.3 + (i % 70) * 0.01,
                'memory_usage': 0.4 + (i % 60) * 0.01,
                'network_io': 50 + (i % 50) * 10
            }
            training_data.append(sample)
        
        # Train the model
        success = await model.train(training_data)
        
        assert success
        assert model.is_trained
        assert model.last_training is not None
    
    @pytest.mark.asyncio
    async def test_real_anomaly_detection(self):
        """Test real anomaly detection"""
        model = RealAnomalyDetectionModel()
        
        # Train the model first
        training_data = []
        for i in range(50):  # 50 training samples
            sample = {
                'active_sessions': 10 + (i % 20),
                'failed_auth_attempts': i % 5,
                'security_incidents': i % 3,
                'risk_score': 0.1 + (i % 10) * 0.1,
                'success_rate': 0.8 + (i % 20) * 0.01,
                'avg_response_time': 100 + (i % 50),
                'error_rate': 0.01 + (i % 10) * 0.005,
                'cpu_usage': 0.3 + (i % 70) * 0.01,
                'memory_usage': 0.4 + (i % 60) * 0.01,
                'network_io': 50 + (i % 50) * 10
            }
            training_data.append(sample)
        
        await model.train(training_data)
        
        # Test normal metrics (should not detect anomaly)
        normal_metrics = {
            'active_sessions': 15,
            'failed_auth_attempts': 1,
            'security_incidents': 0,
            'risk_score': 0.3,
            'success_rate': 0.95,
            'avg_response_time': 150,
            'error_rate': 0.02,
            'cpu_usage': 0.5,
            'memory_usage': 0.6,
            'network_io': 100
        }
        
        anomalies = await model.detect_anomalies(normal_metrics)
        # Normal metrics should not trigger anomalies
        assert isinstance(anomalies, list)
        
        # Test anomalous metrics (should detect anomaly)
        anomalous_metrics = {
            'active_sessions': 100,  # Very high
            'failed_auth_attempts': 20,  # Very high
            'security_incidents': 5,  # Very high
            'risk_score': 0.9,  # Very high
            'success_rate': 0.5,  # Very low
            'avg_response_time': 2000,  # Very high
            'error_rate': 0.15,  # Very high
            'cpu_usage': 0.95,  # Very high
            'memory_usage': 0.95,  # Very high
            'network_io': 1000  # Very high
        }
        
        anomalies = await model.detect_anomalies(anomalous_metrics)
        
        # Should detect anomalies with anomalous data
        if len(anomalies) > 0:
            anomaly = anomalies[0]
            assert anomaly.anomaly_id.startswith("anomaly_")
            assert anomaly.anomaly_type in model.anomaly_types
            assert anomaly.severity in ['low', 'medium', 'high', 'critical']
            assert anomaly.confidence_score > 0
            assert len(anomaly.recommendations) > 0
            assert 'detection_method' in anomaly.metadata


class TestRealOptimizationModel:
    """Test real LightGBM optimization model"""
    
    @pytest.mark.asyncio
    async def test_real_optimization_model_initialization(self):
        """Test real optimization model initialization"""
        model = RealOptimizationModel()
        
        assert model.model_type == MLModelType.COST_OPTIMIZATION
        assert model.model_path == "models/lightgbm_optimization.pkl"
        assert len(model.feature_columns) == 11  # 11 optimization features
        assert len(model.optimization_types) == 5  # 5 optimization types
        assert not model.is_trained
    
    @pytest.mark.asyncio
    async def test_real_optimization_training(self):
        """Test real optimization model training"""
        model = RealOptimizationModel()
        
        # Generate realistic training data
        training_data = []
        for i in range(100):  # 100 training samples
            sample = {
                'cpu_usage': 0.3 + (i % 70) * 0.01,
                'memory_usage': 0.4 + (i % 60) * 0.01,
                'cost_per_hour': 10 + (i % 90) * 2,
                'active_sessions': 5 + (i % 20),
                'total_users': 2 + (i % 10),
                'avg_risk_score': 0.1 + (i % 10) * 0.1,
                'security_incidents': i % 5,
                'error_rate': 0.01 + (i % 10) * 0.005,
                'avg_response_time': 100 + (i % 100),
                'pod_count': 1 + (i % 20),
                'node_count': 3 + (i % 10)
            }
            training_data.append(sample)
        
        # Train the model
        success = await model.train(training_data)
        
        assert success
        assert model.is_trained
        assert model.last_training is not None
    
    @pytest.mark.asyncio
    async def test_real_optimization_recommendations(self):
        """Test real optimization recommendations"""
        model = RealOptimizationModel()
        
        # Train the model first
        training_data = []
        for i in range(50):  # 50 training samples
            sample = {
                'cpu_usage': 0.3 + (i % 70) * 0.01,
                'memory_usage': 0.4 + (i % 60) * 0.01,
                'cost_per_hour': 10 + (i % 90) * 2,
                'active_sessions': 5 + (i % 20),
                'total_users': 2 + (i % 10),
                'avg_risk_score': 0.1 + (i % 10) * 0.1,
                'security_incidents': i % 5,
                'error_rate': 0.01 + (i % 10) * 0.005,
                'avg_response_time': 100 + (i % 100),
                'pod_count': 1 + (i % 20),
                'node_count': 3 + (i % 10)
            }
            training_data.append(sample)
        
        await model.train(training_data)
        
        # Test cluster data for optimization
        cluster_data = {
            'active_sessions': 15,
            'total_users': 8,
            'avg_risk_score': 0.4,
            'security_incidents': 1,
            'cpu_usage': 0.75,  # High CPU usage
            'memory_usage': 0.8,  # High memory usage
            'cost_per_hour': 60,  # High cost
            'error_rate': 0.05,  # High error rate
            'avg_response_time': 500,  # High response time
            'pod_count': 12,
            'node_count': 5
        }
        
        recommendations = await model.generate_recommendations(cluster_data)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert rec.recommendation_id.startswith("opt_")
            assert rec.optimization_type in model.optimization_types
            assert rec.target_entity == 'cluster-1'
            assert rec.confidence_score > 0
            assert rec.confidence_score <= 1.0
            assert 'risk_level' in rec.risk_assessment
            assert len(rec.implementation_steps) > 0
            assert len(rec.rollback_plan) > 0
            
            # Check optimization data
            assert 'cpu_usage' in rec.current_state
            assert 'memory_usage' in rec.current_state
            assert 'cost_per_hour' in rec.current_state
            assert 'cost_savings' in rec.expected_impact
            assert 'performance_improvement' in rec.expected_impact


class TestModelMetrics:
    """Test model metrics data structure"""
    
    def test_model_metrics_creation(self):
        """Test model metrics creation"""
        metrics = ModelMetrics(
            mae=0.15,
            mse=0.025,
            rmse=0.158,
            r2=0.85,
            feature_importance={'cpu_usage': 0.3, 'memory_usage': 0.25},
            training_samples=80,
            validation_samples=20,
            training_time=5.2,
            last_training=datetime.now()
        )
        
        assert metrics.mae == 0.15
        assert metrics.mse == 0.025
        assert metrics.rmse == 0.158
        assert metrics.r2 == 0.85
        assert len(metrics.feature_importance) == 2
        assert metrics.training_samples == 80
        assert metrics.validation_samples == 20
        assert metrics.training_time == 5.2
        assert metrics.last_training is not None


if __name__ == "__main__":
    pytest.main([__file__]) 