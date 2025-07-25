#!/usr/bin/env python3
"""
UPID CLI - Advanced ML Integration
Phase 7: Advanced Features - Task 7.1
Enterprise-grade ML enhancement with advanced prediction models, anomaly detection, and optimization
"""

import logging
import asyncio
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import aiohttp
import subprocess
import tempfile
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import joblib
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import lightgbm as lgb
import xgboost as xgb

from upid_python.auth.enterprise_auth import EnterpriseAuthManager, AuthSession, UserPrincipal
from .auth_analytics_integration import AuthAnalyticsIntegration
from .realtime_monitoring import RealTimeMonitor

logger = logging.getLogger(__name__)


class MLModelType(str, Enum):
    """ML model types"""
    RESOURCE_PREDICTION = "resource_prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    SECURITY_THREAT = "security_threat"
    OPTIMIZATION = "optimization"
    COST_FORECASTING = "cost_forecasting"
    PERFORMANCE_PREDICTION = "performance_prediction"


class PredictionConfidence(str, Enum):
    """Prediction confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class MLPrediction:
    """ML prediction result"""
    model_type: MLModelType
    prediction_value: float
    confidence: PredictionConfidence
    confidence_score: float
    features_used: List[str]
    prediction_timestamp: datetime
    model_version: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    anomaly_type: str
    severity: str
    confidence: float
    detected_at: datetime
    affected_resources: List[str]
    description: str
    recommended_action: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_type: str
    priority: str
    expected_savings: float
    implementation_cost: float
    roi_percentage: float
    affected_resources: List[str]
    description: str
    implementation_steps: List[str]
    risk_assessment: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseMLModel:
    """Base ML model class"""
    
    def __init__(self, model_type: MLModelType, model_path: Optional[str] = None):
        self.model_type = model_type
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.last_training = None
        self.performance_metrics = {}
        self.feature_names = []
        
        logger.info(f"🔧 Initializing {model_type.value} model")
    
    async def load_model(self) -> bool:
        """Load trained model from file"""
        try:
            if self.model_path and Path(self.model_path).exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data.get('scaler', StandardScaler())
                    self.is_trained = model_data.get('is_trained', False)
                    self.last_training = model_data.get('last_training')
                    self.performance_metrics = model_data.get('performance_metrics', {})
                    self.feature_names = model_data.get('feature_names', [])
                
                logger.info(f"✅ Loaded {self.model_type.value} model from {self.model_path}")
                return True
            else:
                logger.warning(f"⚠️ Model file not found: {self.model_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    async def save_model(self, model_path: Optional[str] = None) -> bool:
        """Save trained model to file"""
        try:
            if not self.is_trained:
                logger.warning("⚠️ Cannot save untrained model")
                return False
            
            save_path = model_path or self.model_path
            if not save_path:
                logger.error("❌ No model path specified")
                return False
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'last_training': self.last_training,
                'performance_metrics': self.performance_metrics,
                'feature_names': self.feature_names
            }
            
            with open(save_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"✅ Saved {self.model_type.value} model to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return False
    
    async def train(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None) -> bool:
        """Train the model"""
        try:
            if X.shape[0] == 0:
                logger.warning("⚠️ No training data provided")
                return False
            
            # Store feature names
            self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model (to be implemented by subclasses)
            success = await self._train_model(X_scaled, y)
            
            if success:
                self.is_trained = True
                self.last_training = datetime.now()
                logger.info(f"✅ Trained {self.model_type.value} model")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to train model: {e}")
            return False
    
    async def predict(self, X: np.ndarray) -> Tuple[float, float]:
        """Make prediction and return (prediction, confidence)"""
        try:
            if not self.is_trained or self.model is None:
                logger.warning("⚠️ Model not trained")
                return 0.0, 0.0
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            prediction = await self._predict_model(X_scaled)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(X_scaled)
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"❌ Failed to make prediction: {e}")
            return 0.0, 0.0
    
    async def _train_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train the specific model (to be implemented by subclasses)"""
        raise NotImplementedError
    
    async def _predict_model(self, X: np.ndarray) -> float:
        """Make prediction with the specific model (to be implemented by subclasses)"""
        raise NotImplementedError
    
    async def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate prediction confidence (to be implemented by subclasses)"""
        return 0.5  # Default confidence


class ResourcePredictionModel(BaseMLModel):
    """Resource prediction model"""
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__(MLModelType.RESOURCE_PREDICTION, model_path)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    async def _train_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train resource prediction model"""
        try:
            self.model.fit(X, y)
            
            # Calculate performance metrics
            y_pred = self.model.predict(X)
            self.performance_metrics = {
                'mse': mean_squared_error(y, y_pred),
                'mae': mean_absolute_error(y, y_pred),
                'r2': self.model.score(X, y)
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train resource prediction model: {e}")
            return False
    
    async def _predict_model(self, X: np.ndarray) -> float:
        """Make resource prediction"""
        try:
            return float(self.model.predict(X)[0])
        except Exception as e:
            logger.error(f"❌ Failed to make resource prediction: {e}")
            return 0.0
    
    async def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate prediction confidence using model variance"""
        try:
            # Use random forest's prediction variance for confidence
            predictions = []
            for estimator in self.model.estimators_:
                predictions.append(estimator.predict(X)[0])
            
            # Calculate confidence based on prediction variance
            variance = np.var(predictions)
            confidence = max(0.0, min(1.0, 1.0 - variance / 100.0))
            return confidence
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate confidence: {e}")
            return 0.5


class AnomalyDetectionModel(BaseMLModel):
    """Anomaly detection model"""
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__(MLModelType.ANOMALY_DETECTION, model_path)
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.threshold = -0.5  # Anomaly threshold
    
    async def _train_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train anomaly detection model"""
        try:
            # For anomaly detection, we only need X (no labels)
            self.model.fit(X)
            
            # Calculate performance metrics
            scores = self.model.score_samples(X)
            self.performance_metrics = {
                'mean_score': np.mean(scores),
                'std_score': np.std(scores),
                'anomaly_threshold': self.threshold
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train anomaly detection model: {e}")
            return False
    
    async def _predict_model(self, X: np.ndarray) -> float:
        """Make anomaly prediction (returns anomaly score)"""
        try:
            return float(self.model.score_samples(X)[0])
        except Exception as e:
            logger.error(f"❌ Failed to make anomaly prediction: {e}")
            return 0.0
    
    async def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate anomaly confidence"""
        try:
            score = await self._predict_model(X)
            # Higher negative scores indicate higher confidence in anomaly
            confidence = max(0.0, min(1.0, abs(score) / 2.0))
            return confidence
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate anomaly confidence: {e}")
            return 0.5
    
    async def detect_anomaly(self, X: np.ndarray) -> Tuple[bool, float, float]:
        """Detect anomaly and return (is_anomaly, score, confidence)"""
        try:
            score, confidence = await self.predict(X)
            is_anomaly = score < self.threshold
            return is_anomaly, score, confidence
            
        except Exception as e:
            logger.error(f"❌ Failed to detect anomaly: {e}")
            return False, 0.0, 0.0


class SecurityThreatModel(BaseMLModel):
    """Security threat detection model"""
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__(MLModelType.SECURITY_THREAT, model_path)
        self.model = lgb.LGBMClassifier(random_state=42)
    
    async def _train_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train security threat model"""
        try:
            self.model.fit(X, y)
            
            # Calculate performance metrics
            y_pred = self.model.predict(X)
            y_pred_proba = self.model.predict_proba(X)
            
            self.performance_metrics = {
                'accuracy': np.mean(y_pred == y),
                'threat_detection_rate': np.mean(y_pred[y == 1] == 1),
                'false_positive_rate': np.mean(y_pred[y == 0] == 1)
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train security threat model: {e}")
            return False
    
    async def _predict_model(self, X: np.ndarray) -> float:
        """Make security threat prediction"""
        try:
            # Return probability of threat
            proba = self.model.predict_proba(X)[0]
            return float(proba[1])  # Probability of threat class
        except Exception as e:
            logger.error(f"❌ Failed to make security threat prediction: {e}")
            return 0.0
    
    async def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate threat detection confidence"""
        try:
            proba = self.model.predict_proba(X)[0]
            # Confidence based on probability distribution
            confidence = max(proba)
            return confidence
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate threat confidence: {e}")
            return 0.5


class OptimizationModel(BaseMLModel):
    """Optimization recommendation model"""
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__(MLModelType.OPTIMIZATION, model_path)
        self.model = xgb.XGBRegressor(random_state=42)
    
    async def _train_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train optimization model"""
        try:
            self.model.fit(X, y)
            
            # Calculate performance metrics
            y_pred = self.model.predict(X)
            self.performance_metrics = {
                'mse': mean_squared_error(y, y_pred),
                'mae': mean_absolute_error(y, y_pred),
                'r2': self.model.score(X, y)
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train optimization model: {e}")
            return False
    
    async def _predict_model(self, X: np.ndarray) -> float:
        """Make optimization prediction"""
        try:
            return float(self.model.predict(X)[0])
        except Exception as e:
            logger.error(f"❌ Failed to make optimization prediction: {e}")
            return 0.0
    
    async def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate optimization confidence"""
        try:
            # Use feature importance for confidence
            importance = self.model.feature_importances_
            confidence = np.mean(importance)
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate optimization confidence: {e}")
            return 0.5


class MLEnhancementEngine:
    """
    Advanced ML Enhancement Engine for UPID CLI
    
    Features:
    - Advanced prediction models
    - Anomaly detection
    - Security threat detection
    - Optimization recommendations
    - Real-time ML processing
    - Model management and versioning
    """
    
    def __init__(self, auth_manager: EnterpriseAuthManager, 
                 auth_analytics: AuthAnalyticsIntegration,
                 monitor: RealTimeMonitor):
        self.auth_manager = auth_manager
        self.auth_analytics = auth_analytics
        self.monitor = monitor
        
        # ML models
        self.models: Dict[MLModelType, BaseMLModel] = {}
        
        # Processing state
        self.is_processing = False
        self.processing_thread = None
        self.processing_interval = 300  # 5 minutes
        
        # Prediction cache
        self.prediction_cache: Dict[str, MLPrediction] = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        logger.info("🔧 Initializing ML Enhancement Engine")
    
    async def initialize(self) -> bool:
        """Initialize ML Enhancement Engine"""
        try:
            logger.info("🚀 Initializing ML Enhancement Engine...")
            
            # Load all models
            await self._load_all_models()
            
            # Start ML processing
            await self._start_ml_processing()
            
            logger.info("✅ ML Enhancement Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML Enhancement Engine: {e}")
            return False
    
    async def _load_all_models(self):
        """Load all ML models"""
        logger.info("🔧 Loading ML models...")
        
        # Initialize models
        models_config = {
            MLModelType.RESOURCE_PREDICTION: ResourcePredictionModel,
            MLModelType.ANOMALY_DETECTION: AnomalyDetectionModel,
            MLModelType.SECURITY_THREAT: SecurityThreatModel,
            MLModelType.OPTIMIZATION: OptimizationModel
        }
        
        for model_type, model_class in models_config.items():
            model_path = f"models/{model_type.value}_model.pkl"
            model = model_class(model_path)
            
            # Try to load existing model
            loaded = await model.load_model()
            if not loaded:
                logger.info(f"📝 No existing model found for {model_type.value}, will train when data available")
            
            self.models[model_type] = model
        
        logger.info(f"✅ Loaded {len(self.models)} ML models")
    
    async def _start_ml_processing(self):
        """Start ML processing thread"""
        if self.is_processing:
            logger.warning("⚠️ ML processing already running")
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._ml_processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logger.info("🔄 Started ML processing thread")
    
    def _ml_processing_loop(self):
        """ML processing loop"""
        while self.is_processing:
            try:
                # Run ML processing cycle
                asyncio.run(self._ml_processing_cycle())
                
                # Wait for next cycle
                time.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"❌ ML processing error: {e}")
                time.sleep(60)  # Wait before retry
    
    async def _ml_processing_cycle(self):
        """Run one ML processing cycle"""
        try:
            logger.debug("🔄 Running ML processing cycle...")
            
            # Get current session for context
            current_session = await self.auth_manager.get_current_session()
            if not current_session:
                logger.debug("No active session for ML processing")
                return
            
            # Get real-time data
            metrics = await self.monitor.get_dashboard_metrics()
            if not metrics:
                logger.debug("No metrics available for ML processing")
                return
            
            # Extract features for ML
            features = await self._extract_features(metrics)
            if features is None:
                return
            
            # Run predictions for each model
            for model_type, model in self.models.items():
                if model.is_trained:
                    await self._run_model_prediction(model_type, model, features)
            
            # Run auth analytics integration
            await self.auth_analytics.run_comprehensive_auth_analytics(current_session)
            
            logger.debug("✅ ML processing cycle completed")
            
        except Exception as e:
            logger.error(f"❌ ML processing cycle failed: {e}")
    
    async def _extract_features(self, metrics: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features from metrics for ML models"""
        try:
            # Extract relevant features from metrics
            features = []
            
            # Resource utilization features
            if 'cpu_utilization' in metrics:
                features.extend([
                    metrics['cpu_utilization'],
                    metrics.get('memory_utilization', 0.0),
                    metrics.get('network_utilization', 0.0)
                ])
            
            # Cost features
            if 'cost_per_hour' in metrics:
                features.extend([
                    metrics['cost_per_hour'],
                    metrics.get('cost_trend', 0.0),
                    metrics.get('savings_potential', 0.0)
                ])
            
            # Performance features
            if 'response_time' in metrics:
                features.extend([
                    metrics['response_time'],
                    metrics.get('throughput', 0.0),
                    metrics.get('error_rate', 0.0)
                ])
            
            # Security features
            if 'security_score' in metrics:
                features.extend([
                    metrics['security_score'],
                    metrics.get('vulnerability_count', 0.0),
                    metrics.get('compliance_score', 0.0)
                ])
            
            if not features:
                logger.warning("⚠️ No features extracted from metrics")
                return None
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"❌ Failed to extract features: {e}")
            return None
    
    async def _run_model_prediction(self, model_type: MLModelType, model: BaseMLModel, features: np.ndarray):
        """Run prediction for a specific model"""
        try:
            prediction_value, confidence = await model.predict(features)
            
            # Determine confidence level
            if confidence >= 0.8:
                confidence_level = PredictionConfidence.VERY_HIGH
            elif confidence >= 0.6:
                confidence_level = PredictionConfidence.HIGH
            elif confidence >= 0.4:
                confidence_level = PredictionConfidence.MEDIUM
            else:
                confidence_level = PredictionConfidence.LOW
            
            # Create prediction result
            prediction = MLPrediction(
                model_type=model_type,
                prediction_value=prediction_value,
                confidence=confidence_level,
                confidence_score=confidence,
                features_used=model.feature_names,
                prediction_timestamp=datetime.now(),
                model_version="1.0.0"
            )
            
            # Cache prediction
            cache_key = f"{model_type.value}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            self.prediction_cache[cache_key] = prediction
            
            logger.debug(f"✅ {model_type.value} prediction: {prediction_value:.3f} (confidence: {confidence:.3f})")
            
        except Exception as e:
            logger.error(f"❌ Failed to run {model_type.value} prediction: {e}")
    
    async def get_predictions(self, model_type: Optional[MLModelType] = None) -> List[MLPrediction]:
        """Get recent predictions"""
        try:
            if model_type:
                # Filter by model type
                predictions = [
                    pred for pred in self.prediction_cache.values()
                    if pred.model_type == model_type
                ]
            else:
                # Return all predictions
                predictions = list(self.prediction_cache.values())
            
            # Sort by timestamp (newest first)
            predictions.sort(key=lambda x: x.prediction_timestamp, reverse=True)
            
            return predictions[:10]  # Return last 10 predictions
            
        except Exception as e:
            logger.error(f"❌ Failed to get predictions: {e}")
            return []
    
    async def get_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Get optimization recommendations based on ML predictions"""
        try:
            recommendations = []
            
            # Get recent optimization predictions
            opt_predictions = await self.get_predictions(MLModelType.OPTIMIZATION)
            
            for pred in opt_predictions:
                if pred.confidence_score > 0.6:  # Only high-confidence predictions
                    recommendation = OptimizationRecommendation(
                        recommendation_type="ml_optimization",
                        priority="high" if pred.confidence_score > 0.8 else "medium",
                        expected_savings=pred.prediction_value * 100,  # Convert to percentage
                        implementation_cost=pred.prediction_value * 10,  # Estimate
                        roi_percentage=pred.prediction_value * 1000,  # Estimate ROI
                        affected_resources=["cpu", "memory", "storage"],
                        description=f"ML-based optimization with {pred.confidence_score:.1%} confidence",
                        implementation_steps=[
                            "Analyze current resource usage",
                            "Apply ML optimization recommendations",
                            "Monitor performance impact",
                            "Validate cost savings"
                        ],
                        risk_assessment="low" if pred.confidence_score > 0.8 else "medium"
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get optimization recommendations: {e}")
            return []
    
    async def train_model(self, model_type: MLModelType, X: np.ndarray, y: np.ndarray, 
                         feature_names: List[str] = None) -> bool:
        """Train a specific model"""
        try:
            if model_type not in self.models:
                logger.error(f"❌ Model type {model_type.value} not found")
                return False
            
            model = self.models[model_type]
            success = await model.train(X, y, feature_names)
            
            if success:
                # Save the trained model
                await model.save_model()
                logger.info(f"✅ Trained and saved {model_type.value} model")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to train {model_type.value} model: {e}")
            return False
    
    async def get_model_performance(self, model_type: MLModelType) -> Dict[str, Any]:
        """Get performance metrics for a specific model"""
        try:
            if model_type not in self.models:
                return {"error": f"Model type {model_type.value} not found"}
            
            model = self.models[model_type]
            
            return {
                "model_type": model_type.value,
                "is_trained": model.is_trained,
                "last_training": model.last_training.isoformat() if model.last_training else None,
                "performance_metrics": model.performance_metrics,
                "feature_count": len(model.feature_names),
                "feature_names": model.feature_names
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get model performance: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Shutdown ML Enhancement Engine"""
        logger.info("🛑 Shutting down ML Enhancement Engine...")
        
        # Stop processing thread
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("✅ ML Enhancement Engine shutdown complete") 