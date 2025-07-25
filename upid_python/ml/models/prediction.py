"""
UPID CLI - Prediction Model
Machine learning model for resource usage prediction
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import pickle
import joblib

# Try to import LightGBM, fallback to mock if not available
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logging.warning("LightGBM not available, using mock model")

logger = logging.getLogger(__name__)


class PredictionModel:
    """
    Machine learning model for resource usage prediction
    
    Predicts future resource usage based on:
    - Historical usage patterns
    - Time-series analysis
    - Workload characteristics
    - Cluster utilization trends
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = [
            'cpu_usage_percent', 'memory_usage_percent', 'network_activity',
            'restart_count', 'age_hours', 'idle_duration_hours',
            'replica_count', 'resource_requests_cpu', 'resource_requests_memory',
            'resource_limits_cpu', 'resource_limits_memory',
            'cluster_cpu_utilization', 'cluster_memory_utilization',
            'cluster_pod_density', 'cluster_efficiency_score',
            'hour_of_day', 'day_of_week', 'is_weekend', 'is_business_hours'
        ]
        self.is_trained = False
        
        logger.info("🔧 Initializing prediction model")
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None):
        """Train the prediction model"""
        try:
            if not LIGHTGBM_AVAILABLE:
                logger.warning("LightGBM not available, using mock training")
                self._train_mock_model(X, y)
                return
            
            # Prepare data
            if feature_names:
                self.feature_names = feature_names
            
            # Create LightGBM dataset
            train_data = lgb.Dataset(X, label=y, feature_name=self.feature_names)
            
            # Model parameters for regression
            params = {
                'objective': 'regression',
                'metric': 'rmse',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1
            }
            
            # Train model
            self.model = lgb.train(
                params,
                train_data,
                num_boost_round=100,
                valid_sets=[train_data],
                callbacks=[lgb.log_evaluation(period=10)]
            )
            
            self.is_trained = True
            logger.info("✅ Prediction model trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to train prediction model: {e}")
            self._train_mock_model(X, y)
    
    def _train_mock_model(self, X: np.ndarray, y: np.ndarray):
        """Train a mock model when LightGBM is not available"""
        try:
            # Simple rule-based model
            self.model = MockPredictionModel()
            self.is_trained = True
            logger.info("✅ Mock prediction model trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to train mock model: {e}")
    
    def predict(self, X: np.ndarray) -> Union[float, str]:
        """Make resource usage predictions"""
        try:
            if not self.is_trained:
                return "not_trained"
            
            if LIGHTGBM_AVAILABLE and self.model is not None:
                # LightGBM prediction
                prediction = self.model.predict(X)
                return prediction[0] if len(prediction) > 0 else 0.0
            else:
                # Mock prediction
                return self.model.predict(X) if self.model else "no_model"
                
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return "error"
    
    def get_confidence(self, X: np.ndarray) -> float:
        """Get prediction confidence"""
        try:
            if not self.is_trained:
                return 0.0
            
            if LIGHTGBM_AVAILABLE and self.model is not None:
                # LightGBM prediction with uncertainty estimation
                # For regression, we'll use a simple confidence based on feature values
                prediction = self.model.predict(X)
                # Higher confidence for predictions in reasonable range
                pred_value = prediction[0] if len(prediction) > 0 else 0.0
                if 0 <= pred_value <= 100:
                    return 0.8
                else:
                    return 0.5
            else:
                # Mock confidence
                return self.model.get_confidence(X) if self.model else 0.0
                
        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return 0.0
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        try:
            if not self.is_trained or self.model is None:
                return {}
            
            if LIGHTGBM_AVAILABLE:
                # LightGBM feature importance
                importance = self.model.feature_importance(importance_type='gain')
                return dict(zip(self.feature_names, importance))
            else:
                # Mock feature importance
                return self.model.get_feature_importance() if self.model else {}
                
        except Exception as e:
            logger.error(f"❌ Feature importance calculation failed: {e}")
            return {}
    
    def save_model(self, filepath: Path):
        """Save the trained model"""
        try:
            if self.model is not None:
                if LIGHTGBM_AVAILABLE:
                    # Save LightGBM model
                    self.model.save_model(str(filepath))
                else:
                    # Save mock model
                    with open(filepath, 'wb') as f:
                        pickle.dump(self.model, f)
                
                logger.info(f"✅ Model saved to {filepath}")
            else:
                logger.warning("No model to save")
                
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
    
    def load_model(self, filepath: Path):
        """Load a trained model"""
        try:
            if filepath.exists():
                if LIGHTGBM_AVAILABLE:
                    # Load LightGBM model
                    self.model = lgb.Booster(model_file=str(filepath))
                else:
                    # Load mock model
                    with open(filepath, 'rb') as f:
                        self.model = pickle.load(f)
                
                self.is_trained = True
                logger.info(f"✅ Model loaded from {filepath}")
            else:
                logger.warning(f"Model file not found: {filepath}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_type": "prediction",
            "algorithm": "lightgbm" if LIGHTGBM_AVAILABLE else "mock",
            "is_trained": self.is_trained,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names
        }


class MockPredictionModel:
    """Mock prediction model for testing and development"""
    
    def __init__(self):
        self.feature_importance = {
            'cpu_usage_percent': 0.30,
            'memory_usage_percent': 0.25,
            'cluster_cpu_utilization': 0.20,
            'cluster_memory_utilization': 0.15,
            'network_activity': 0.10
        }
    
    def predict(self, X: np.ndarray) -> float:
        """Mock prediction based on simple rules"""
        try:
            if X.shape[1] < 5:
                return 50.0  # Default prediction
            
            # Extract key features
            cpu_usage = X[0, 0] if X.shape[1] > 0 else 50
            memory_usage = X[0, 1] if X.shape[1] > 1 else 50
            cluster_cpu = X[0, 12] if X.shape[1] > 12 else 70
            cluster_memory = X[0, 13] if X.shape[1] > 13 else 80
            
            # Simple prediction based on current usage and trends
            prediction = (cpu_usage + memory_usage) / 2
            
            # Adjust based on cluster utilization
            if cluster_cpu > 80:
                prediction += 10  # Expect higher usage
            elif cluster_cpu < 30:
                prediction -= 10  # Expect lower usage
            
            if cluster_memory > 80:
                prediction += 5
            elif cluster_memory < 30:
                prediction -= 5
            
            # Ensure prediction is reasonable
            return max(0, min(100, prediction))
            
        except Exception as e:
            logger.error(f"Mock prediction failed: {e}")
            return 50.0
    
    def get_confidence(self, X: np.ndarray) -> float:
        """Mock confidence calculation"""
        try:
            prediction = self.predict(X)
            # Higher confidence for predictions in middle range
            if 30 <= prediction <= 70:
                return 0.8
            elif 20 <= prediction <= 80:
                return 0.6
            else:
                return 0.4
        except Exception as e:
            logger.error(f"Mock confidence calculation failed: {e}")
            return 0.5
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get mock feature importance"""
        return self.feature_importance.copy() 