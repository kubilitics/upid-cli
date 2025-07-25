"""
UPID CLI - ML Pipeline
Enterprise-grade machine learning pipeline for Kubernetes optimization
"""

import logging
import asyncio
import json
import pickle
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

from ..core.metrics_collector import MetricsCollector, NodeMetrics, PodMetrics, ClusterMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from .models.optimization import OptimizationModel
from .models.prediction import PredictionModel
from .models.anomaly import AnomalyDetectionModel

logger = logging.getLogger(__name__)


@dataclass
class MLFeatures:
    """ML features extracted from Kubernetes metrics"""
    # Pod-level features
    cpu_usage_percent: float
    memory_usage_percent: float
    network_activity: float
    restart_count: int
    age_hours: float
    idle_duration_hours: float
    
    # Workload-level features
    workload_type: str
    namespace: str
    replica_count: int
    resource_requests_cpu: float
    resource_requests_memory: float
    resource_limits_cpu: float
    resource_limits_memory: float
    
    # Cluster-level features
    cluster_cpu_utilization: float
    cluster_memory_utilization: float
    cluster_pod_density: float
    cluster_efficiency_score: float
    
    # Time-based features
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    is_business_hours: bool


@dataclass
class MLPrediction:
    """ML model prediction results"""
    model_name: str
    prediction_type: str
    confidence: float
    prediction_value: Union[float, str, bool]
    feature_importance: Dict[str, float]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class MLPipelineMetrics:
    """ML pipeline performance metrics"""
    total_predictions: int
    average_confidence: float
    model_accuracy: Dict[str, float]
    processing_time_ms: float
    cache_hit_rate: float
    last_training: datetime
    models_loaded: List[str]


class MLPipeline:
    """
    Enterprise-grade ML pipeline for UPID platform
    
    Provides comprehensive ML capabilities:
    - Feature engineering from Kubernetes metrics
    - Model training and retraining
    - Real-time predictions
    - Anomaly detection
    - Optimization recommendations
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        
        # Initialize models
        self.optimization_model = OptimizationModel()
        self.prediction_model = PredictionModel()
        self.anomaly_model = AnomalyDetectionModel()
        
        # Feature engineering components
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Cache for performance
        self._cache = {}
        self._cache_ttl = timedelta(minutes=10)
        
        # Pipeline metrics
        self.metrics = MLPipelineMetrics(
            total_predictions=0,
            average_confidence=0.0,
            model_accuracy={},
            processing_time_ms=0.0,
            cache_hit_rate=0.0,
            last_training=datetime.utcnow(),
            models_loaded=[]
        )
        
        # Model paths
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        logger.info("🔧 Initializing UPID ML pipeline")
    
    async def initialize(self) -> bool:
        """Initialize the ML pipeline and load models"""
        try:
            logger.info("🚀 Initializing ML pipeline...")
            
            # Load existing models
            await self._load_models()
            
            # Initialize feature engineering
            await self._initialize_feature_engineering()
            
            # Test pipeline
            await self._test_pipeline()
            
            self.metrics.models_loaded = [
                "optimization_model",
                "prediction_model", 
                "anomaly_model"
            ]
            
            logger.info("✅ ML pipeline initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML pipeline: {e}")
            return False
    
    async def _load_models(self):
        """Load pre-trained models"""
        try:
            # Load optimization model
            if (self.model_dir / "lightgbm_optimization.pkl").exists():
                self.optimization_model.load_model(self.model_dir / "lightgbm_optimization.pkl")
                logger.info("✅ Loaded optimization model")
            
            # Load prediction model
            if (self.model_dir / "lightgbm_resource_prediction.pkl").exists():
                self.prediction_model.load_model(self.model_dir / "lightgbm_resource_prediction.pkl")
                logger.info("✅ Loaded prediction model")
            
            # Load anomaly model
            if (self.model_dir / "sklearn_anomaly_detection.pkl").exists():
                self.anomaly_model.load_model(self.model_dir / "sklearn_anomaly_detection.pkl")
                logger.info("✅ Loaded anomaly detection model")
                
        except Exception as e:
            logger.warning(f"⚠️ Some models could not be loaded: {e}")
    
    async def _initialize_feature_engineering(self):
        """Initialize feature engineering components"""
        try:
            # Load scaler if exists
            scaler_path = self.model_dir / "feature_scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("✅ Loaded feature scaler")
            
            # Load label encoder if exists
            encoder_path = self.model_dir / "label_encoder.pkl"
            if encoder_path.exists():
                self.label_encoder = joblib.load(encoder_path)
                logger.info("✅ Loaded label encoder")
                
        except Exception as e:
            logger.warning(f"⚠️ Feature engineering components could not be loaded: {e}")
    
    async def _test_pipeline(self):
        """Test the ML pipeline with sample data"""
        try:
            # Create sample features
            sample_features = MLFeatures(
                cpu_usage_percent=50.0,
                memory_usage_percent=60.0,
                network_activity=1000.0,
                restart_count=0,
                age_hours=24.0,
                idle_duration_hours=2.0,
                workload_type="deployment",
                namespace="default",
                replica_count=3,
                resource_requests_cpu=0.5,
                resource_requests_memory=512.0,
                resource_limits_cpu=1.0,
                resource_limits_memory=1024.0,
                cluster_cpu_utilization=70.0,
                cluster_memory_utilization=80.0,
                cluster_pod_density=0.8,
                cluster_efficiency_score=75.0,
                hour_of_day=14,
                day_of_week=2,
                is_weekend=False,
                is_business_hours=True
            )
            
            # Test predictions
            await self.predict_optimization(sample_features)
            await self.predict_resource_usage(sample_features)
            await self.detect_anomalies(sample_features)
            
            logger.info("✅ ML pipeline test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ ML pipeline test failed: {e}")
            raise
    
    async def extract_features(self, pod_metrics: List[PodMetrics], cluster_metrics: ClusterMetrics) -> List[MLFeatures]:
        """Extract ML features from Kubernetes metrics"""
        features = []
        
        try:
            for pod in pod_metrics:
                # Calculate derived features
                age_hours = (datetime.utcnow() - pod.timestamp).total_seconds() / 3600
                idle_duration = max(0, age_hours - 2)  # Assume 2 hours of activity
                
                # Determine business hours
                hour = pod.timestamp.hour
                day = pod.timestamp.weekday()
                is_business_hours = 9 <= hour <= 17 and day < 5
                is_weekend = day >= 5
                
                # Calculate resource utilization percentages
                cpu_percent = (pod.cpu_usage_millicores / 1000) / max(pod.cpu_limits_millicores / 1000, 0.001) * 100
                memory_percent = pod.memory_usage_bytes / max(pod.memory_limits_bytes, 1) * 100
                
                # Network activity (bytes per hour)
                network_activity = (pod.network_rx_bytes or 0) + (pod.network_tx_bytes or 0)
                
                feature = MLFeatures(
                    cpu_usage_percent=cpu_percent,
                    memory_usage_percent=memory_percent,
                    network_activity=network_activity,
                    restart_count=pod.restart_count,
                    age_hours=age_hours,
                    idle_duration_hours=idle_duration,
                    workload_type=self._extract_workload_type(pod.pod_name),
                    namespace=pod.namespace,
                    replica_count=1,  # Will be enhanced with workload info
                    resource_requests_cpu=pod.cpu_requests_millicores / 1000,
                    resource_requests_memory=pod.memory_requests_bytes / (1024 * 1024),  # MB
                    resource_limits_cpu=pod.cpu_limits_millicores / 1000,
                    resource_limits_memory=pod.memory_limits_bytes / (1024 * 1024),  # MB
                    cluster_cpu_utilization=cluster_metrics.cpu_usage_percent,
                    cluster_memory_utilization=cluster_metrics.memory_usage_percent,
                    cluster_pod_density=cluster_metrics.running_pods / max(cluster_metrics.total_pods, 1),
                    cluster_efficiency_score=cluster_metrics.cluster_efficiency_score,
                    hour_of_day=hour,
                    day_of_week=day,
                    is_weekend=is_weekend,
                    is_business_hours=is_business_hours
                )
                
                features.append(feature)
            
            logger.info(f"✅ Extracted {len(features)} feature sets")
            return features
            
        except Exception as e:
            logger.error(f"❌ Feature extraction failed: {e}")
            return []
    
    def _extract_workload_type(self, pod_name: str) -> str:
        """Extract workload type from pod name"""
        if "deployment" in pod_name.lower():
            return "deployment"
        elif "statefulset" in pod_name.lower():
            return "statefulset"
        elif "daemonset" in pod_name.lower():
            return "daemonset"
        elif "job" in pod_name.lower():
            return "job"
        else:
            return "deployment"  # Default
    
    async def predict_optimization(self, features: MLFeatures) -> MLPrediction:
        """Predict optimization opportunities"""
        try:
            start_time = datetime.utcnow()
            
            # Convert features to model input
            feature_vector = self._features_to_vector(features)
            
            # Make prediction
            prediction = self.optimization_model.predict(feature_vector)
            
            # Calculate confidence
            confidence = self.optimization_model.get_confidence(feature_vector)
            
            # Get feature importance
            importance = self.optimization_model.get_feature_importance()
            
            # Update metrics
            self._update_metrics(confidence)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MLPrediction(
                model_name="optimization_model",
                prediction_type="optimization_opportunity",
                confidence=confidence,
                prediction_value=prediction,
                feature_importance=importance,
                timestamp=datetime.utcnow(),
                metadata={"processing_time_ms": processing_time}
            )
            
        except Exception as e:
            logger.error(f"❌ Optimization prediction failed: {e}")
            return MLPrediction(
                model_name="optimization_model",
                prediction_type="optimization_opportunity",
                confidence=0.0,
                prediction_value="error",
                feature_importance={},
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
    
    async def predict_resource_usage(self, features: MLFeatures) -> MLPrediction:
        """Predict future resource usage"""
        try:
            start_time = datetime.utcnow()
            
            # Convert features to model input
            feature_vector = self._features_to_vector(features)
            
            # Make prediction
            prediction = self.prediction_model.predict(feature_vector)
            
            # Calculate confidence
            confidence = self.prediction_model.get_confidence(feature_vector)
            
            # Get feature importance
            importance = self.prediction_model.get_feature_importance()
            
            # Update metrics
            self._update_metrics(confidence)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MLPrediction(
                model_name="prediction_model",
                prediction_type="resource_usage",
                confidence=confidence,
                prediction_value=prediction,
                feature_importance=importance,
                timestamp=datetime.utcnow(),
                metadata={"processing_time_ms": processing_time}
            )
            
        except Exception as e:
            logger.error(f"❌ Resource usage prediction failed: {e}")
            return MLPrediction(
                model_name="prediction_model",
                prediction_type="resource_usage",
                confidence=0.0,
                prediction_value="error",
                feature_importance={},
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
    
    async def detect_anomalies(self, features: MLFeatures) -> MLPrediction:
        """Detect anomalies in resource usage"""
        try:
            start_time = datetime.utcnow()
            
            # Convert features to model input
            feature_vector = self._features_to_vector(features)
            
            # Make prediction
            prediction = self.anomaly_model.predict(feature_vector)
            
            # Calculate confidence
            confidence = self.anomaly_model.get_confidence(feature_vector)
            
            # Get feature importance
            importance = self.anomaly_model.get_feature_importance()
            
            # Update metrics
            self._update_metrics(confidence)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MLPrediction(
                model_name="anomaly_model",
                prediction_type="anomaly_detection",
                confidence=confidence,
                prediction_value=prediction,
                feature_importance=importance,
                timestamp=datetime.utcnow(),
                metadata={"processing_time_ms": processing_time}
            )
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection failed: {e}")
            return MLPrediction(
                model_name="anomaly_model",
                prediction_type="anomaly_detection",
                confidence=0.0,
                prediction_value="error",
                feature_importance={},
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
    
    def _features_to_vector(self, features: MLFeatures) -> np.ndarray:
        """Convert features to numpy array for model input"""
        # Convert dataclass to dict
        feature_dict = asdict(features)
        
        # Remove non-numeric fields
        numeric_features = []
        feature_names = []
        
        for key, value in feature_dict.items():
            if isinstance(value, (int, float)):
                numeric_features.append(value)
                feature_names.append(key)
            elif isinstance(value, bool):
                numeric_features.append(1.0 if value else 0.0)
                feature_names.append(key)
            elif isinstance(value, str):
                # Encode categorical variables
                try:
                    encoded = self.label_encoder.transform([value])[0]
                    numeric_features.append(float(encoded))
                    feature_names.append(key)
                except:
                    # If encoder not fitted, use simple hash
                    numeric_features.append(hash(value) % 100)
                    feature_names.append(key)
        
        return np.array(numeric_features).reshape(1, -1)
    
    def _update_metrics(self, confidence: float):
        """Update pipeline metrics"""
        self.metrics.total_predictions += 1
        self.metrics.average_confidence = (
            (self.metrics.average_confidence * (self.metrics.total_predictions - 1) + confidence) /
            self.metrics.total_predictions
        )
    
    async def get_pipeline_metrics(self) -> MLPipelineMetrics:
        """Get ML pipeline performance metrics"""
        return self.metrics
    
    async def save_models(self):
        """Save all models to disk"""
        try:
            # Save models
            self.optimization_model.save_model(self.model_dir / "lightgbm_optimization.pkl")
            self.prediction_model.save_model(self.model_dir / "lightgbm_resource_prediction.pkl")
            self.anomaly_model.save_model(self.model_dir / "sklearn_anomaly_detection.pkl")
            
            # Save feature engineering components
            joblib.dump(self.scaler, self.model_dir / "feature_scaler.pkl")
            joblib.dump(self.label_encoder, self.model_dir / "label_encoder.pkl")
            
            logger.info("✅ All models saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")
    
    async def load_models(self):
        """Load all models from disk"""
        try:
            await self._load_models()
            await self._initialize_feature_engineering()
            logger.info("✅ All models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}") 