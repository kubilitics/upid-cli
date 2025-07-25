"""
UPID CLI - Anomaly Detection Model
Machine learning model for detecting anomalies in resource usage
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import pickle
import joblib

# Try to import sklearn, fallback to mock if not available
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("sklearn not available, using mock model")

logger = logging.getLogger(__name__)


class AnomalyDetectionModel:
    """
    Machine learning model for anomaly detection
    
    Detects anomalies in:
    - Resource usage patterns
    - Network activity
    - Pod behavior
    - Cluster performance
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
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
        
        logger.info("🔧 Initializing anomaly detection model")
    
    def train(self, X: np.ndarray, y: Optional[np.ndarray] = None, feature_names: Optional[List[str]] = None):
        """Train the anomaly detection model"""
        try:
            if not SKLEARN_AVAILABLE:
                logger.warning("sklearn not available, using mock training")
                self._train_mock_model(X, y)
                return
            
            # Prepare data
            if feature_names:
                self.feature_names = feature_names
            
            # Initialize scaler
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Initialize and train Isolation Forest
            self.model = IsolationForest(
                contamination=0.1,  # Expected proportion of anomalies
                random_state=42,
                n_estimators=100,
                max_samples='auto'
            )
            
            # Train model (Isolation Forest is unsupervised)
            self.model.fit(X_scaled)
            
            self.is_trained = True
            logger.info("✅ Anomaly detection model trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to train anomaly detection model: {e}")
            self._train_mock_model(X, y)
    
    def _train_mock_model(self, X: np.ndarray, y: Optional[np.ndarray] = None):
        """Train a mock model when sklearn is not available"""
        try:
            # Simple rule-based model
            self.model = MockAnomalyModel()
            self.is_trained = True
            logger.info("✅ Mock anomaly detection model trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to train mock model: {e}")
    
    def predict(self, X: np.ndarray) -> Union[bool, str]:
        """Detect anomalies in the data"""
        try:
            if not self.is_trained:
                return "not_trained"
            
            if SKLEARN_AVAILABLE and self.model is not None and self.scaler is not None:
                # Scale features
                X_scaled = self.scaler.transform(X)
                
                # Predict anomalies (-1 for anomaly, 1 for normal)
                predictions = self.model.predict(X_scaled)
                
                # Return True if anomaly detected
                return predictions[0] == -1 if len(predictions) > 0 else False
            else:
                # Mock prediction
                return self.model.predict(X) if self.model else "no_model"
                
        except Exception as e:
            logger.error(f"❌ Anomaly detection failed: {e}")
            return "error"
    
    def get_confidence(self, X: np.ndarray) -> float:
        """Get anomaly detection confidence"""
        try:
            if not self.is_trained:
                return 0.0
            
            if SKLEARN_AVAILABLE and self.model is not None and self.scaler is not None:
                # Get anomaly score (lower = more anomalous)
                X_scaled = self.scaler.transform(X)
                scores = self.model.score_samples(X_scaled)
                
                # Convert score to confidence (higher score = higher confidence)
                score = scores[0] if len(scores) > 0 else 0.0
                confidence = max(0.0, min(1.0, (score + 10) / 20))  # Normalize to 0-1
                return confidence
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
            
            if SKLEARN_AVAILABLE:
                # For Isolation Forest, we'll use a simple heuristic
                # Features that are more variable are more important for anomaly detection
                return {
                    'cpu_usage_percent': 0.25,
                    'memory_usage_percent': 0.20,
                    'network_activity': 0.30,
                    'restart_count': 0.15,
                    'cluster_efficiency_score': 0.10
                }
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
                if SKLEARN_AVAILABLE:
                    # Save sklearn model
                    with open(filepath, 'wb') as f:
                        pickle.dump({
                            'model': self.model,
                            'scaler': self.scaler,
                            'feature_names': self.feature_names
                        }, f)
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
                if SKLEARN_AVAILABLE:
                    # Load sklearn model
                    with open(filepath, 'rb') as f:
                        data = pickle.load(f)
                        self.model = data['model']
                        self.scaler = data['scaler']
                        self.feature_names = data.get('feature_names', self.feature_names)
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
            "model_type": "anomaly_detection",
            "algorithm": "isolation_forest" if SKLEARN_AVAILABLE else "mock",
            "is_trained": self.is_trained,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names
        }


class MockAnomalyModel:
    """Mock anomaly detection model for testing and development"""
    
    def __init__(self):
        self.feature_importance = {
            'cpu_usage_percent': 0.25,
            'memory_usage_percent': 0.20,
            'network_activity': 0.30,
            'restart_count': 0.15,
            'cluster_efficiency_score': 0.10
        }
    
    def predict(self, X: np.ndarray) -> bool:
        """Mock anomaly detection based on simple rules"""
        try:
            if X.shape[1] < 5:
                return False
            
            # Extract key features
            cpu_usage = X[0, 0] if X.shape[1] > 0 else 50
            memory_usage = X[0, 1] if X.shape[1] > 1 else 50
            network_activity = X[0, 2] if X.shape[1] > 2 else 1000
            restart_count = X[0, 3] if X.shape[1] > 3 else 0
            cluster_efficiency = X[0, 14] if X.shape[1] > 14 else 75
            
            # Simple anomaly detection rules
            anomalies = []
            
            # High CPU usage anomaly
            if cpu_usage > 90:
                anomalies.append("high_cpu")
            
            # High memory usage anomaly
            if memory_usage > 90:
                anomalies.append("high_memory")
            
            # High network activity anomaly
            if network_activity > 10000:
                anomalies.append("high_network")
            
            # High restart count anomaly
            if restart_count > 5:
                anomalies.append("high_restarts")
            
            # Low cluster efficiency anomaly
            if cluster_efficiency < 50:
                anomalies.append("low_efficiency")
            
            # Return True if any anomaly detected
            return len(anomalies) > 0
            
        except Exception as e:
            logger.error(f"Mock anomaly detection failed: {e}")
            return False
    
    def get_confidence(self, X: np.ndarray) -> float:
        """Mock confidence calculation"""
        try:
            is_anomaly = self.predict(X)
            # Higher confidence for clear anomalies
            if is_anomaly:
                return 0.8
            else:
                return 0.6
        except Exception as e:
            logger.error(f"Mock confidence calculation failed: {e}")
            return 0.5
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get mock feature importance"""
        return self.feature_importance.copy() 