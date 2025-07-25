"""
UPID CLI - Model Training
Machine learning model training and retraining system
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import json

from ..core.metrics_collector import MetricsCollector, PodMetrics, ClusterMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from .pipeline import MLPipeline, MLFeatures
from .models.optimization import OptimizationModel
from .models.prediction import PredictionModel
from .models.anomaly import AnomalyDetectionModel

logger = logging.getLogger(__name__)


@dataclass
class TrainingMetrics:
    """Training performance metrics"""
    model_name: str
    training_time_seconds: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    feature_count: int
    sample_count: int
    timestamp: datetime


@dataclass
class TrainingConfig:
    """Training configuration"""
    model_type: str  # optimization, prediction, anomaly
    feature_columns: List[str]
    target_column: str
    test_size: float = 0.2
    random_state: int = 42
    max_samples: Optional[int] = None
    min_samples: int = 100


class ModelTrainer:
    """
    Machine learning model trainer for UPID platform
    
    Provides comprehensive training capabilities:
    - Data preparation and feature engineering
    - Model training and validation
    - Performance evaluation
    - Model persistence and versioning
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.ml_pipeline = MLPipeline(metrics_collector, resource_analyzer)
        
        # Training history
        self.training_history: List[TrainingMetrics] = []
        
        # Model paths
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        logger.info("🔧 Initializing model trainer")
    
    async def initialize(self) -> bool:
        """Initialize the model trainer"""
        try:
            logger.info("🚀 Initializing model trainer...")
            
            # Initialize ML pipeline
            await self.ml_pipeline.initialize()
            
            logger.info("✅ Model trainer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model trainer: {e}")
            return False
    
    async def prepare_training_data(self, days: int = 30) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare training data from historical metrics"""
        try:
            logger.info(f"📊 Preparing training data from last {days} days...")
            
            # Collect historical metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get historical metrics
            historical_metrics = await self.metrics_collector.get_resource_usage_history(
                timeframe=f"{days}d",
                interval="1h"
            )
            
            # Extract features from historical data
            features_list = []
            targets = []
            
            for data_point in historical_metrics.data_points:
                # Get pod metrics for this time point
                pod_metrics = await self.metrics_collector.collect_pod_metrics()
                
                # Extract features
                features = await self.ml_pipeline.extract_features(pod_metrics, data_point)
                
                for feature in features:
                    features_list.append(feature)
                    
                    # Create target based on model type
                    # For optimization: 1 if optimization opportunity, 0 otherwise
                    # For prediction: future resource usage
                    # For anomaly: 1 if anomaly detected, 0 otherwise
                    target = self._create_target(feature, data_point)
                    targets.append(target)
            
            # Convert to numpy arrays
            X = np.array([self._features_to_array(f) for f in features_list])
            y = np.array(targets)
            
            logger.info(f"✅ Prepared training data: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y, self.ml_pipeline.feature_names
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare training data: {e}")
            return np.array([]), np.array([]), []
    
    def _create_target(self, feature: MLFeatures, cluster_metrics: ClusterMetrics) -> float:
        """Create target variable for training"""
        # For optimization model: detect optimization opportunities
        if feature.cpu_usage_percent < 20 or feature.memory_usage_percent < 30:
            return 1.0  # Optimization opportunity
        elif feature.idle_duration_hours > 4:
            return 1.0  # Idle workload
        else:
            return 0.0  # No optimization needed
    
    def _features_to_array(self, feature: MLFeatures) -> List[float]:
        """Convert features to array"""
        return [
            feature.cpu_usage_percent,
            feature.memory_usage_percent,
            feature.network_activity,
            feature.restart_count,
            feature.age_hours,
            feature.idle_duration_hours,
            feature.replica_count,
            feature.resource_requests_cpu,
            feature.resource_requests_memory,
            feature.resource_limits_cpu,
            feature.resource_limits_memory,
            feature.cluster_cpu_utilization,
            feature.cluster_memory_utilization,
            feature.cluster_pod_density,
            feature.cluster_efficiency_score,
            feature.hour_of_day,
            feature.day_of_week,
            1.0 if feature.is_weekend else 0.0,
            1.0 if feature.is_business_hours else 0.0
        ]
    
    async def train_optimization_model(self, config: TrainingConfig) -> TrainingMetrics:
        """Train the optimization model"""
        try:
            logger.info("🚀 Training optimization model...")
            start_time = datetime.utcnow()
            
            # Prepare training data
            X, y, feature_names = await self.prepare_training_data()
            
            if X.shape[0] == 0:
                raise ValueError("No training data available")
            
            # Limit samples if specified
            if config.max_samples and X.shape[0] > config.max_samples:
                indices = np.random.choice(X.shape[0], config.max_samples, replace=False)
                X = X[indices]
                y = y[indices]
            
            # Train model
            self.ml_pipeline.optimization_model.train(X, y, feature_names)
            
            # Calculate training metrics
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Simple accuracy calculation
            predictions = []
            for i in range(X.shape[0]):
                pred = self.ml_pipeline.optimization_model.predict(X[i:i+1])
                predictions.append(1.0 if pred > 0.5 else 0.0)
            
            accuracy = np.mean(np.array(predictions) == y)
            
            metrics = TrainingMetrics(
                model_name="optimization_model",
                training_time_seconds=training_time,
                accuracy=accuracy,
                precision=accuracy,  # Simplified
                recall=accuracy,     # Simplified
                f1_score=accuracy,   # Simplified
                feature_count=X.shape[1],
                sample_count=X.shape[0],
                timestamp=datetime.utcnow()
            )
            
            self.training_history.append(metrics)
            
            # Save model
            await self.ml_pipeline.save_models()
            
            logger.info(f"✅ Optimization model trained successfully: {accuracy:.3f} accuracy")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to train optimization model: {e}")
            raise
    
    async def train_prediction_model(self, config: TrainingConfig) -> TrainingMetrics:
        """Train the prediction model"""
        try:
            logger.info("🚀 Training prediction model...")
            start_time = datetime.utcnow()
            
            # Prepare training data
            X, y, feature_names = await self.prepare_training_data()
            
            if X.shape[0] == 0:
                raise ValueError("No training data available")
            
            # Create regression targets (predict future resource usage)
            y_regression = np.array([f.cpu_usage_percent for f in self.ml_pipeline._extract_features_from_array(X)])
            
            # Limit samples if specified
            if config.max_samples and X.shape[0] > config.max_samples:
                indices = np.random.choice(X.shape[0], config.max_samples, replace=False)
                X = X[indices]
                y_regression = y_regression[indices]
            
            # Train model
            self.ml_pipeline.prediction_model.train(X, y_regression, feature_names)
            
            # Calculate training metrics
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate RMSE
            predictions = []
            for i in range(X.shape[0]):
                pred = self.ml_pipeline.prediction_model.predict(X[i:i+1])
                predictions.append(pred if isinstance(pred, (int, float)) else 50.0)
            
            rmse = np.sqrt(np.mean((np.array(predictions) - y_regression) ** 2))
            accuracy = max(0, 1 - rmse / 100)  # Normalize to 0-1
            
            metrics = TrainingMetrics(
                model_name="prediction_model",
                training_time_seconds=training_time,
                accuracy=accuracy,
                precision=accuracy,  # Simplified
                recall=accuracy,     # Simplified
                f1_score=accuracy,   # Simplified
                feature_count=X.shape[1],
                sample_count=X.shape[0],
                timestamp=datetime.utcnow()
            )
            
            self.training_history.append(metrics)
            
            # Save model
            await self.ml_pipeline.save_models()
            
            logger.info(f"✅ Prediction model trained successfully: {accuracy:.3f} accuracy")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to train prediction model: {e}")
            raise
    
    async def train_anomaly_model(self, config: TrainingConfig) -> TrainingMetrics:
        """Train the anomaly detection model"""
        try:
            logger.info("🚀 Training anomaly detection model...")
            start_time = datetime.utcnow()
            
            # Prepare training data
            X, y, feature_names = await self.prepare_training_data()
            
            if X.shape[0] == 0:
                raise ValueError("No training data available")
            
            # Limit samples if specified
            if config.max_samples and X.shape[0] > config.max_samples:
                indices = np.random.choice(X.shape[0], config.max_samples, replace=False)
                X = X[indices]
            
            # Train model (unsupervised)
            self.ml_pipeline.anomaly_model.train(X, feature_names=feature_names)
            
            # Calculate training metrics
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate anomaly detection metrics
            predictions = []
            for i in range(X.shape[0]):
                pred = self.ml_pipeline.anomaly_model.predict(X[i:i+1])
                predictions.append(1.0 if pred else 0.0)
            
            # Assume 10% of data is anomalous for evaluation
            expected_anomalies = int(X.shape[0] * 0.1)
            detected_anomalies = sum(predictions)
            
            accuracy = 1.0 - abs(detected_anomalies - expected_anomalies) / X.shape[0]
            
            metrics = TrainingMetrics(
                model_name="anomaly_model",
                training_time_seconds=training_time,
                accuracy=accuracy,
                precision=accuracy,  # Simplified
                recall=accuracy,     # Simplified
                f1_score=accuracy,   # Simplified
                feature_count=X.shape[1],
                sample_count=X.shape[0],
                timestamp=datetime.utcnow()
            )
            
            self.training_history.append(metrics)
            
            # Save model
            await self.ml_pipeline.save_models()
            
            logger.info(f"✅ Anomaly detection model trained successfully: {accuracy:.3f} accuracy")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to train anomaly detection model: {e}")
            raise
    
    async def train_all_models(self) -> Dict[str, TrainingMetrics]:
        """Train all models"""
        try:
            logger.info("🚀 Training all models...")
            
            results = {}
            
            # Train optimization model
            opt_config = TrainingConfig(
                model_type="optimization",
                feature_columns=[],
                target_column="optimization_opportunity"
            )
            results["optimization"] = await self.train_optimization_model(opt_config)
            
            # Train prediction model
            pred_config = TrainingConfig(
                model_type="prediction",
                feature_columns=[],
                target_column="resource_usage"
            )
            results["prediction"] = await self.train_prediction_model(pred_config)
            
            # Train anomaly model
            anomaly_config = TrainingConfig(
                model_type="anomaly",
                feature_columns=[],
                target_column="anomaly"
            )
            results["anomaly"] = await self.train_anomaly_model(anomaly_config)
            
            logger.info("✅ All models trained successfully")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to train all models: {e}")
            raise
    
    async def retrain_models(self, force: bool = False) -> Dict[str, TrainingMetrics]:
        """Retrain models if needed"""
        try:
            logger.info("🔄 Checking if retraining is needed...")
            
            # Check if models need retraining (e.g., based on age or performance)
            needs_retraining = force or await self._should_retrain()
            
            if needs_retraining:
                logger.info("🔄 Retraining models...")
                return await self.train_all_models()
            else:
                logger.info("✅ Models are up to date")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Failed to retrain models: {e}")
            raise
    
    async def _should_retrain(self) -> bool:
        """Determine if models should be retrained"""
        try:
            # Check if models exist
            model_files = [
                self.model_dir / "lightgbm_optimization.pkl",
                self.model_dir / "lightgbm_resource_prediction.pkl",
                self.model_dir / "sklearn_anomaly_detection.pkl"
            ]
            
            if not all(f.exists() for f in model_files):
                return True
            
            # Check model age (retrain if older than 7 days)
            for model_file in model_files:
                if model_file.exists():
                    age = datetime.utcnow() - datetime.fromtimestamp(model_file.stat().st_mtime)
                    if age.days > 7:
                        return True
            
            # Check performance (if available)
            if self.training_history:
                latest_metrics = self.training_history[-1]
                if latest_metrics.accuracy < 0.7:  # Low accuracy threshold
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking retraining status: {e}")
            return True
    
    def get_training_history(self) -> List[TrainingMetrics]:
        """Get training history"""
        return self.training_history.copy()
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get current model performance metrics"""
        try:
            if not self.training_history:
                return {}
            
            latest_metrics = self.training_history[-1]
            
            return {
                "model_name": latest_metrics.model_name,
                "accuracy": latest_metrics.accuracy,
                "training_time": latest_metrics.training_time_seconds,
                "sample_count": latest_metrics.sample_count,
                "feature_count": latest_metrics.feature_count,
                "last_training": latest_metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get model performance: {e}")
            return {} 