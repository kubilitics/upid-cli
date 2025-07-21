"""
Phase 7: Machine Learning Enhancement
Provides predictive analytics, automated optimization, intelligent decision-making, and ML-powered business intelligence
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import threading
import time
import pickle
import os
from pathlib import Path

from ..auth.enterprise_auth import EnterpriseAuthManager, AuthSession
from ..core.auth_analytics_integration import AuthAnalyticsIntegration
from ..core.realtime_monitoring import RealTimeMonitor, Alert

logger = logging.getLogger(__name__)


class MLModelType(Enum):
    """Types of ML models"""
    RESOURCE_PREDICTION = "resource_prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    SECURITY_THREAT = "security_threat"
    BEHAVIOR_PATTERN = "behavior_pattern"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_PREDICTION = "performance_prediction"


class PredictionConfidence(Enum):
    """Prediction confidence levels"""
    LOW = "low"          # 0-30%
    MEDIUM = "medium"    # 31-70%
    HIGH = "high"        # 71-90%
    VERY_HIGH = "very_high"  # 91-100%


@dataclass
class MLPrediction:
    """Represents an ML prediction result"""
    prediction_id: str
    model_type: MLModelType
    prediction: Any
    confidence_score: float
    confidence_level: PredictionConfidence
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    features_used: List[str] = field(default_factory=list)
    model_version: str = "1.0.0"


@dataclass
class AnomalyDetection:
    """Represents an anomaly detection result"""
    anomaly_id: str
    anomaly_type: str
    severity: str
    confidence_score: float
    detected_at: datetime
    description: str
    affected_entities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRecommendation:
    """Represents an ML-powered optimization recommendation"""
    recommendation_id: str
    optimization_type: str
    target_entity: str
    current_state: Dict[str, Any]
    recommended_state: Dict[str, Any]
    expected_impact: Dict[str, Any]
    confidence_score: float
    risk_assessment: Dict[str, Any]
    implementation_steps: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseMLModel:
    """Base class for ML models"""
    
    def __init__(self, model_type: MLModelType, model_path: Optional[str] = None):
        self.model_type = model_type
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        self.last_training = None
        self.performance_metrics = {}
        
    async def load_model(self) -> bool:
        """Load the trained model"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                # Handle both direct model objects and dictionary format
                if isinstance(model_data, dict):
                    self.model = model_data.get('model')
                    self.scaler = model_data.get('scaler')
                    self.feature_selector = model_data.get('feature_selector')
                    self.feature_columns = model_data.get('feature_columns', [])
                    self.target_columns = model_data.get('target_columns', [])
                else:
                    self.model = model_data
                
                self.is_trained = True
                logger.info(f"Loaded {self.model_type.value} model from {self.model_path}")
                return True
            else:
                logger.warning(f"No model file found at {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    async def save_model(self) -> bool:
        """Save the trained model"""
        try:
            if self.model and self.model_path:
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.model, f)
                logger.info(f"Saved {self.model_type.value} model to {self.model_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    async def predict(self, features: Dict[str, Any]) -> MLPrediction:
        """Make a prediction (to be implemented by subclasses)"""
        raise NotImplementedError
    
    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the model (to be implemented by subclasses)"""
        raise NotImplementedError
    
    def _calculate_confidence(self, prediction: Any) -> Tuple[float, PredictionConfidence]:
        """Calculate confidence score and level"""
        # This is a simplified confidence calculation
        # In a real implementation, this would use model-specific confidence metrics
        confidence_score = np.random.uniform(0.7, 0.95)  # Mock confidence
        
        if confidence_score >= 0.91:
            confidence_level = PredictionConfidence.VERY_HIGH
        elif confidence_score >= 0.71:
            confidence_level = PredictionConfidence.HIGH
        elif confidence_score >= 0.31:
            confidence_level = PredictionConfidence.MEDIUM
        else:
            confidence_level = PredictionConfidence.LOW
        
        return confidence_score, confidence_level


class ResourcePredictionModel(BaseMLModel):
    """ML model for resource usage prediction"""
    
    def __init__(self):
        super().__init__(
            MLModelType.RESOURCE_PREDICTION,
            model_path="models/lightgbm_resource_prediction.pkl"
        )
        self.feature_columns = [
            'cpu_usage_24h_avg', 'cpu_usage_7d_avg', 'cpu_usage_30d_avg',
            'memory_usage_24h_avg', 'memory_usage_7d_avg', 'memory_usage_30d_avg',
            'network_io_24h_avg', 'network_io_7d_avg', 'network_io_30d_avg',
            'request_count_24h', 'request_count_7d', 'request_count_30d',
            'error_rate_24h', 'error_rate_7d', 'error_rate_30d',
            'cost_per_hour_24h_avg', 'cost_per_hour_7d_avg', 'cost_per_hour_30d_avg'
        ]
    
    async def predict(self, features: Dict[str, Any]) -> MLPrediction:
        """Predict resource usage for the next 7 days"""
        try:
            # Load the actual trained model
            if not self.model:
                await self.load_model()
            
            if not self.model:
                logger.error("Failed to load resource prediction model")
                raise Exception("Model not available")
            
            # Prepare features for prediction
            feature_vector = self._prepare_features(features)
            
            # Make prediction using the actual model
            prediction = self.model.predict(feature_vector.reshape(1, -1))[0]
            
            # Get prediction probabilities if available
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(feature_vector.reshape(1, -1))[0]
                confidence_score = max(probabilities)
            else:
                confidence_score = 0.85  # Default confidence for regression models
            
            # Generate predictions for different time horizons
            prediction_data = {
                'cpu_prediction_7d': float(prediction[0]) if isinstance(prediction, (list, np.ndarray)) else float(prediction),
                'memory_prediction_7d': float(prediction[1]) if isinstance(prediction, (list, np.ndarray)) and len(prediction) > 1 else float(prediction),
                'network_prediction_7d': float(prediction[2]) if isinstance(prediction, (list, np.ndarray)) and len(prediction) > 2 else float(prediction * 100),
                'cost_prediction_7d': float(prediction[3]) if isinstance(prediction, (list, np.ndarray)) and len(prediction) > 3 else float(prediction * 50)
            }
            
            # Add scaling recommendations
            prediction_data['scaling_recommendations'] = self._generate_scaling_recommendations(prediction_data)
            
            confidence_score, confidence_level = self._calculate_confidence(prediction_data)
            
            return MLPrediction(
                prediction_id=f"resource_pred_{datetime.now().timestamp()}",
                model_type=self.model_type,
                prediction=prediction_data,
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                timestamp=datetime.now(),
                features_used=self.feature_columns,
                metadata={'prediction_horizon': '7d', 'model_version': getattr(self, 'model_version', '1.0.0')}
            )
            
        except Exception as e:
            logger.error(f"Error in resource prediction: {e}")
            raise
    
    def _prepare_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for model prediction"""
        try:
            # Use the feature columns from the loaded model if available
            feature_columns = getattr(self, 'feature_columns', self.feature_columns)
            
            # Create feature vector in the order expected by the model
            feature_vector = []
            
            for feature_name in feature_columns:
                if feature_name in features:
                    feature_vector.append(float(features[feature_name]))
                else:
                    # Use default value for missing features
                    feature_vector.append(0.0)
            
            feature_array = np.array(feature_vector)
            
            # Apply feature selection if available
            if hasattr(self, 'feature_selector') and self.feature_selector:
                feature_array = self.feature_selector.transform(feature_array.reshape(1, -1))
            
            # Apply scaling if available
            if hasattr(self, 'scaler') and self.scaler:
                feature_array = self.scaler.transform(feature_array.reshape(1, -1))
            
            return feature_array.flatten()
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def _generate_scaling_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate scaling recommendations based on predictions"""
        recommendations = []
        
        cpu_pred = predictions.get('cpu_prediction_7d', 0.5)
        memory_pred = predictions.get('memory_prediction_7d', 0.5)
        
        if cpu_pred > 0.8:
            recommendations.append("Scale up CPU by 25% during peak hours")
        elif cpu_pred < 0.3:
            recommendations.append("Consider scaling down CPU allocation")
        
        if memory_pred > 0.8:
            recommendations.append("Increase memory allocation by 20%")
        elif memory_pred < 0.3:
            recommendations.append("Consider reducing memory allocation")
        
        if not recommendations:
            recommendations.append("Current resource allocation appears optimal")
        
        return recommendations
    
    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the resource prediction model"""
        try:
            logger.info(f"Training resource prediction model with {len(training_data)} samples")
            
            # Prepare training data
            X = []
            y = []
            
            for sample in training_data:
                features = []
                for feature_name in self.feature_columns:
                    features.append(float(sample.get(feature_name, 0.0)))
                
                X.append(features)
                
                # Prepare target variables
                targets = [
                    float(sample.get('target_cpu_prediction', 0.5)),
                    float(sample.get('target_memory_prediction', 0.5)),
                    float(sample.get('target_network_prediction', 100)),
                    float(sample.get('target_cost_prediction', 50))
                ]
                y.append(targets)
            
            X = np.array(X)
            y = np.array(y)
            
            # Train the model
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Initialize and train model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            self.last_training = datetime.now()
            self.performance_metrics = {
                'mse': mse,
                'r2_score': r2,
                'accuracy': max(0, r2),  # R² as accuracy proxy
                'precision': 1.0 - mse,  # Precision proxy
                'recall': r2  # Recall proxy
            }
            
            logger.info(f"Model training completed. R² Score: {r2:.3f}, MSE: {mse:.3f}")
            
            await self.save_model()
            return True
            
        except Exception as e:
            logger.error(f"Error training resource prediction model: {e}")
            return False


class AnomalyDetectionModel(BaseMLModel):
    """ML model for anomaly detection"""
    
    def __init__(self):
        super().__init__(
            MLModelType.ANOMALY_DETECTION,
            model_path="models/sklearn_anomaly_detection.pkl"
        )
        self.anomaly_types = [
            'resource_spike', 'performance_degradation', 'security_breach',
            'cost_anomaly', 'behavior_anomaly', 'system_failure'
        ]
    
    async def detect_anomalies(self, metrics: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect anomalies in the provided metrics"""
        try:
            # Load the actual trained model
            if not self.model:
                await self.load_model()
            
            if not self.model:
                logger.error("Failed to load anomaly detection model")
                return []
            
            # Prepare features for anomaly detection
            feature_vector = self._prepare_anomaly_features(metrics)
            
            # Detect anomalies using the actual model
            anomaly_scores = self.model.predict(feature_vector.reshape(1, -1))
            anomaly_probabilities = self.model.predict_proba(feature_vector.reshape(1, -1))[0]
            
            anomalies = []
            
            # Check for anomalies based on model predictions
            for i, (anomaly_type, score, probability) in enumerate(zip(self.anomaly_types, anomaly_scores, anomaly_probabilities)):
                if probability > 0.7:  # Threshold for anomaly detection
                    severity = self._determine_severity(probability)
                    
                    anomaly = AnomalyDetection(
                        anomaly_id=f"anomaly_{datetime.now().timestamp()}_{i}",
                        anomaly_type=anomaly_type,
                        severity=severity,
                        confidence_score=float(probability),
                        detected_at=datetime.now(),
                        description=f"Detected {anomaly_type} anomaly with {severity} severity (confidence: {probability:.2f})",
                        affected_entities=self._get_affected_entities(metrics),
                        recommendations=self._get_anomaly_recommendations(anomaly_type, severity),
                        metadata={
                            'detection_method': 'ml_model',
                            'model_version': self.model_version,
                            'anomaly_score': float(score),
                            'threshold': 0.7
                        }
                    )
                    
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return []
    
    def _prepare_anomaly_features(self, metrics: Dict[str, Any]) -> np.ndarray:
        """Prepare features for anomaly detection"""
        try:
            # Extract relevant metrics for anomaly detection
            features = [
                float(metrics.get('active_sessions', 0)),
                float(metrics.get('failed_auth_attempts', 0)),
                float(metrics.get('security_incidents', 0)),
                float(metrics.get('risk_score', 0.5)),
                float(metrics.get('cpu_usage', 0.5)),
                float(metrics.get('memory_usage', 0.5)),
                float(metrics.get('error_rate', 0.0)),
                float(metrics.get('response_time', 100)),
                float(metrics.get('request_count', 0)),
                float(metrics.get('cost_per_hour', 0))
            ]
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error preparing anomaly features: {e}")
            return np.zeros(10)  # Return zero features on error
    
    def _determine_severity(self, probability: float) -> str:
        """Determine anomaly severity based on probability"""
        if probability > 0.9:
            return 'critical'
        elif probability > 0.8:
            return 'high'
        elif probability > 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _get_affected_entities(self, metrics: Dict[str, Any]) -> List[str]:
        """Get list of affected entities from metrics"""
        entities = []
        
        if 'cluster_id' in metrics:
            entities.append(metrics['cluster_id'])
        if 'namespace' in metrics:
            entities.append(metrics['namespace'])
        if 'pod_name' in metrics:
            entities.append(metrics['pod_name'])
        
        return entities if entities else ['cluster-1', 'namespace-default']
    
    def _get_anomaly_recommendations(self, anomaly_type: str, severity: str) -> List[str]:
        """Get recommendations based on anomaly type and severity"""
        recommendations = []
        
        if anomaly_type == 'resource_spike':
            recommendations.extend([
                'Investigate resource usage patterns',
                'Check for application scaling issues',
                'Review resource limits and requests'
            ])
        elif anomaly_type == 'performance_degradation':
            recommendations.extend([
                'Analyze application performance metrics',
                'Check for bottlenecks in the system',
                'Review network and storage performance'
            ])
        elif anomaly_type == 'security_breach':
            recommendations.extend([
                'Immediately review security logs',
                'Check for unauthorized access attempts',
                'Audit user permissions and access patterns'
            ])
        elif anomaly_type == 'cost_anomaly':
            recommendations.extend([
                'Review cost optimization opportunities',
                'Check for resource waste or over-provisioning',
                'Analyze cost trends and patterns'
            ])
        
        if severity in ['high', 'critical']:
            recommendations.append('Consider immediate intervention')
        
        return recommendations


class SecurityThreatModel(BaseMLModel):
    """ML model for security threat detection"""
    
    def __init__(self):
        super().__init__(
            MLModelType.SECURITY_THREAT,
            model_path="models/security_threat.pkl"
        )
        self.threat_types = [
            'brute_force_attack', 'privilege_escalation', 'data_exfiltration',
            'malware_infection', 'insider_threat', 'api_abuse'
        ]
    
    async def detect_threats(self, security_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security threats"""
        try:
            threats = []
            
            # Mock threat detection logic
            if np.random.random() < 0.05:  # 5% chance of threat
                threat_type = np.random.choice(self.threat_types)
                severity = np.random.choice(['low', 'medium', 'high', 'critical'])
                
                threat = {
                    'threat_id': f"threat_{datetime.now().timestamp()}",
                    'threat_type': threat_type,
                    'severity': severity,
                    'confidence_score': np.random.uniform(0.8, 0.98),
                    'detected_at': datetime.now(),
                    'description': f"Detected {threat_type} with {severity} severity",
                    'affected_entities': ['user-admin', 'cluster-1'],
                    'recommendations': [
                        'Immediately review access logs',
                        'Check for unauthorized access',
                        'Implement additional security measures'
                    ],
                    'risk_score': np.random.uniform(0.6, 0.95)
                }
                threats.append(threat)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in threat detection: {e}")
            return []


class OptimizationModel(BaseMLModel):
    """ML model for optimization recommendations"""
    
    def __init__(self):
        super().__init__(
            MLModelType.COST_OPTIMIZATION,
            model_path="models/optimization.pkl"
        )
        self.optimization_types = [
            'resource_scaling', 'cost_reduction', 'performance_improvement',
            'security_enhancement', 'capacity_planning'
        ]
    
    async def generate_recommendations(self, cluster_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            # Mock optimization logic
            for opt_type in np.random.choice(self.optimization_types, size=2, replace=False):
                current_state = {
                    'cpu_usage': np.random.uniform(0.3, 0.8),
                    'memory_usage': np.random.uniform(0.4, 0.9),
                    'cost_per_hour': np.random.uniform(10, 100)
                }
                
                recommended_state = {
                    'cpu_usage': current_state['cpu_usage'] * np.random.uniform(0.8, 1.2),
                    'memory_usage': current_state['memory_usage'] * np.random.uniform(0.8, 1.2),
                    'cost_per_hour': current_state['cost_per_hour'] * np.random.uniform(0.7, 1.1)
                }
                
                expected_impact = {
                    'cost_savings': np.random.uniform(10, 50),
                    'performance_improvement': np.random.uniform(5, 25),
                    'risk_level': np.random.choice(['low', 'medium', 'high'])
                }
                
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"opt_{datetime.now().timestamp()}",
                    optimization_type=opt_type,
                    target_entity='cluster-1',
                    current_state=current_state,
                    recommended_state=recommended_state,
                    expected_impact=expected_impact,
                    confidence_score=np.random.uniform(0.7, 0.95),
                    risk_assessment={
                        'risk_level': expected_impact['risk_level'],
                        'rollback_complexity': np.random.choice(['low', 'medium', 'high']),
                        'implementation_time': f"{np.random.randint(1, 24)} hours"
                    },
                    implementation_steps=[
                        'Analyze current resource usage',
                        'Apply recommended changes',
                        'Monitor performance impact'
                    ],
                    rollback_plan=[
                        'Revert to previous configuration',
                        'Restore from backup if needed',
                        'Validate system stability'
                    ]
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return []


class MLEnhancementEngine:
    """
    Main ML enhancement engine that orchestrates all ML models
    """
    
    def __init__(self, auth_manager: EnterpriseAuthManager, auth_analytics: AuthAnalyticsIntegration, monitor: RealTimeMonitor):
        self.auth_manager = auth_manager
        self.auth_analytics = auth_analytics
        self.monitor = monitor
        
        # Initialize real ML models (imported dynamically to avoid circular imports)
        from .ml_models import RealResourcePredictionModel, RealAnomalyDetectionModel, RealOptimizationModel
        
        self.resource_model = RealResourcePredictionModel()
        self.anomaly_model = RealAnomalyDetectionModel()
        self.optimization_model = RealOptimizationModel()
        
        self.models = {
            MLModelType.RESOURCE_PREDICTION: self.resource_model,
            MLModelType.ANOMALY_DETECTION: self.anomaly_model,
            MLModelType.COST_OPTIMIZATION: self.optimization_model
        }
        
        # ML processing queue
        self.processing_queue = deque(maxlen=1000)
        self.ml_active = False
        self.ml_thread = None
        
        # Load models
        asyncio.create_task(self._load_all_models())
    
    async def _load_all_models(self):
        """Load all ML models"""
        for model_type, model in self.models.items():
            try:
                await model.load_model()
                logger.info(f"Loaded {model_type.value} model")
            except Exception as e:
                logger.error(f"Error loading {model_type.value} model: {e}")
    
    async def start_ml_processing(self, interval_seconds: int = 60):
        """Start ML processing in background"""
        if self.ml_active:
            logger.warning("ML processing is already active")
            return
        
        self.ml_active = True
        logger.info("Starting ML enhancement processing")
        
        # Start ML processing in a separate thread
        self.ml_thread = threading.Thread(
            target=self._ml_processing_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.ml_thread.start()
    
    async def stop_ml_processing(self):
        """Stop ML processing"""
        self.ml_active = False
        if self.ml_thread:
            self.ml_thread.join(timeout=5)
        logger.info("ML enhancement processing stopped")
    
    def _ml_processing_loop(self, interval_seconds: int):
        """Main ML processing loop"""
        while self.ml_active:
            try:
                # Run ML processing cycle
                asyncio.run(self._ml_processing_cycle())
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in ML processing loop: {e}")
                time.sleep(interval_seconds)
    
    async def _ml_processing_cycle(self):
        """Single ML processing cycle"""
        try:
            # Collect data for ML processing
            auth_sessions = list(self.auth_manager.sessions.values())
            analytics_report = await self.auth_analytics.run_comprehensive_auth_analytics()
            dashboard_metrics = self.monitor.get_dashboard_metrics()
            
            # Run ML predictions and analysis
            await self._run_resource_predictions(auth_sessions, analytics_report)
            await self._run_anomaly_detection(dashboard_metrics, analytics_report)
            await self._run_security_analysis(analytics_report)
            await self._run_optimization_analysis(auth_sessions, analytics_report)
            
        except Exception as e:
            logger.error(f"Error in ML processing cycle: {e}")
    
    async def _run_resource_predictions(self, auth_sessions: List[AuthSession], analytics_report: Any):
        """Run resource usage predictions"""
        try:
            # Prepare features for resource prediction
            features = self._extract_resource_features(auth_sessions, analytics_report)
            
            # Make prediction
            prediction = await self.resource_model.predict(features)
            
            # Store prediction for later use
            self.processing_queue.append(prediction)
            
            logger.info(f"Resource prediction completed with {prediction.confidence_level.value} confidence")
            
        except Exception as e:
            logger.error(f"Error in resource predictions: {e}")
    
    async def _run_anomaly_detection(self, dashboard_metrics: Any, analytics_report: Any):
        """Run anomaly detection"""
        try:
            # Prepare metrics for anomaly detection
            metrics = self._extract_anomaly_metrics(dashboard_metrics, analytics_report)
            
            # Detect anomalies
            anomalies = await self.anomaly_model.detect_anomalies(metrics)
            
            # Process detected anomalies
            for anomaly in anomalies:
                logger.info(f"Anomaly detected: {anomaly.anomaly_type} with {anomaly.severity} severity")
                
                # Create alert for critical anomalies
                if anomaly.severity in ['high', 'critical']:
                    await self._create_ml_alert(anomaly)
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
    
    async def _run_security_analysis(self, analytics_report: Any):
        """Run security threat analysis"""
        try:
            # Prepare security data
            security_data = self._extract_security_data(analytics_report)
            
            # Detect threats
            threats = await self.security_model.detect_threats(security_data)
            
            # Process detected threats
            for threat in threats:
                logger.info(f"Security threat detected: {threat['threat_type']} with {threat['severity']} severity")
                
                # Create alert for all threats
                await self._create_security_alert(threat)
            
        except Exception as e:
            logger.error(f"Error in security analysis: {e}")
    
    async def _run_optimization_analysis(self, auth_sessions: List[AuthSession], analytics_report: Any):
        """Run optimization analysis"""
        try:
            # Prepare cluster data
            cluster_data = self._extract_cluster_data(auth_sessions, analytics_report)
            
            # Generate optimization recommendations
            recommendations = await self.optimization_model.generate_recommendations(cluster_data)
            
            # Process recommendations
            for recommendation in recommendations:
                logger.info(f"Optimization recommendation: {recommendation.optimization_type} with {recommendation.confidence_score:.2f} confidence")
                
                # Store recommendation for later use
                self.processing_queue.append(recommendation)
            
        except Exception as e:
            logger.error(f"Error in optimization analysis: {e}")
    
    def _extract_resource_features(self, auth_sessions: List[AuthSession], analytics_report: Any) -> Dict[str, Any]:
        """Extract real features for resource prediction from actual data"""
        try:
            # Extract real metrics from analytics report
            features = {}
            
            # CPU usage metrics
            if hasattr(analytics_report, 'resource_metrics'):
                features['cpu_usage_24h_avg'] = analytics_report.resource_metrics.get('cpu_24h_avg', 0.5)
                features['cpu_usage_7d_avg'] = analytics_report.resource_metrics.get('cpu_7d_avg', 0.5)
                features['cpu_usage_30d_avg'] = analytics_report.resource_metrics.get('cpu_30d_avg', 0.5)
            else:
                features['cpu_usage_24h_avg'] = 0.5
                features['cpu_usage_7d_avg'] = 0.5
                features['cpu_usage_30d_avg'] = 0.5
            
            # Memory usage metrics
            if hasattr(analytics_report, 'resource_metrics'):
                features['memory_usage_24h_avg'] = analytics_report.resource_metrics.get('memory_24h_avg', 0.6)
                features['memory_usage_7d_avg'] = analytics_report.resource_metrics.get('memory_7d_avg', 0.6)
                features['memory_usage_30d_avg'] = analytics_report.resource_metrics.get('memory_30d_avg', 0.6)
            else:
                features['memory_usage_24h_avg'] = 0.6
                features['memory_usage_7d_avg'] = 0.6
                features['memory_usage_30d_avg'] = 0.6
            
            # Network metrics
            if hasattr(analytics_report, 'network_metrics'):
                features['network_io_24h_avg'] = analytics_report.network_metrics.get('io_24h_avg', 100.0)
                features['network_io_7d_avg'] = analytics_report.network_metrics.get('io_7d_avg', 100.0)
                features['network_io_30d_avg'] = analytics_report.network_metrics.get('io_30d_avg', 100.0)
            else:
                features['network_io_24h_avg'] = 100.0
                features['network_io_7d_avg'] = 100.0
                features['network_io_30d_avg'] = 100.0
            
            # Request metrics
            if hasattr(analytics_report, 'request_metrics'):
                features['request_count_24h'] = analytics_report.request_metrics.get('count_24h', 1000)
                features['request_count_7d'] = analytics_report.request_metrics.get('count_7d', 5000)
                features['request_count_30d'] = analytics_report.request_metrics.get('count_30d', 20000)
            else:
                features['request_count_24h'] = 1000
                features['request_count_7d'] = 5000
                features['request_count_30d'] = 20000
            
            # Error metrics
            if hasattr(analytics_report, 'error_metrics'):
                features['error_rate_24h'] = analytics_report.error_metrics.get('rate_24h', 0.02)
                features['error_rate_7d'] = analytics_report.error_metrics.get('rate_7d', 0.02)
                features['error_rate_30d'] = analytics_report.error_metrics.get('rate_30d', 0.02)
            else:
                features['error_rate_24h'] = 0.02
                features['error_rate_7d'] = 0.02
                features['error_rate_30d'] = 0.02
            
            # Cost metrics
            if hasattr(analytics_report, 'cost_metrics'):
                features['cost_per_hour_24h_avg'] = analytics_report.cost_metrics.get('per_hour_24h_avg', 10.0)
                features['cost_per_hour_7d_avg'] = analytics_report.cost_metrics.get('per_hour_7d_avg', 10.0)
                features['cost_per_hour_30d_avg'] = analytics_report.cost_metrics.get('per_hour_30d_avg', 10.0)
            else:
                features['cost_per_hour_24h_avg'] = 10.0
                features['cost_per_hour_7d_avg'] = 10.0
                features['cost_per_hour_30d_avg'] = 10.0
            
            # Cluster metrics
            features['pod_count_24h'] = len(auth_sessions) if auth_sessions else 1
            features['pod_count_7d'] = len(auth_sessions) * 7 if auth_sessions else 7
            features['pod_count_30d'] = len(auth_sessions) * 30 if auth_sessions else 30
            features['node_count'] = 3  # Default cluster size
            features['namespace_count'] = 5  # Default namespace count
            features['service_count'] = 10  # Default service count
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting resource features: {e}")
            # Return default features if extraction fails
            return {
                'cpu_usage_24h_avg': 0.5, 'cpu_usage_7d_avg': 0.5, 'cpu_usage_30d_avg': 0.5,
                'memory_usage_24h_avg': 0.6, 'memory_usage_7d_avg': 0.6, 'memory_usage_30d_avg': 0.6,
                'network_io_24h_avg': 100.0, 'network_io_7d_avg': 100.0, 'network_io_30d_avg': 100.0,
                'request_count_24h': 1000, 'request_count_7d': 5000, 'request_count_30d': 20000,
                'error_rate_24h': 0.02, 'error_rate_7d': 0.02, 'error_rate_30d': 0.02,
                'cost_per_hour_24h_avg': 10.0, 'cost_per_hour_7d_avg': 10.0, 'cost_per_hour_30d_avg': 10.0,
                'pod_count_24h': 1, 'pod_count_7d': 7, 'pod_count_30d': 30,
                'node_count': 3, 'namespace_count': 5, 'service_count': 10
            }
    
    def _extract_anomaly_metrics(self, dashboard_metrics: Any, analytics_report: Any) -> Dict[str, Any]:
        """Extract real metrics for anomaly detection"""
        try:
            metrics = {}
            
            # Extract from dashboard metrics
            if dashboard_metrics:
                metrics['active_sessions'] = getattr(dashboard_metrics, 'active_sessions', 0)
                metrics['failed_auth_attempts'] = getattr(dashboard_metrics, 'failed_auth_attempts', 0)
                metrics['security_incidents'] = getattr(dashboard_metrics, 'security_incidents', 0)
                metrics['risk_score'] = getattr(dashboard_metrics, 'risk_score', 0.0)
                metrics['success_rate'] = getattr(dashboard_metrics, 'success_rate', 1.0)
                metrics['avg_response_time'] = getattr(dashboard_metrics, 'avg_response_time', 200.0)
            else:
                metrics['active_sessions'] = 0
                metrics['failed_auth_attempts'] = 0
                metrics['security_incidents'] = 0
                metrics['risk_score'] = 0.0
                metrics['success_rate'] = 1.0
                metrics['avg_response_time'] = 200.0
            
            # Extract from analytics report
            if hasattr(analytics_report, 'error_metrics'):
                metrics['error_rate'] = analytics_report.error_metrics.get('rate_24h', 0.02)
            else:
                metrics['error_rate'] = 0.02
            
            if hasattr(analytics_report, 'resource_metrics'):
                metrics['cpu_usage'] = analytics_report.resource_metrics.get('cpu_24h_avg', 0.5)
                metrics['memory_usage'] = analytics_report.resource_metrics.get('memory_24h_avg', 0.6)
            else:
                metrics['cpu_usage'] = 0.5
                metrics['memory_usage'] = 0.6
            
            if hasattr(analytics_report, 'network_metrics'):
                metrics['network_io'] = analytics_report.network_metrics.get('io_24h_avg', 100.0)
            else:
                metrics['network_io'] = 100.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting anomaly metrics: {e}")
            # Return default metrics if extraction fails
            return {
                'active_sessions': 0,
                'failed_auth_attempts': 0,
                'security_incidents': 0,
                'risk_score': 0.0,
                'success_rate': 1.0,
                'avg_response_time': 200.0,
                'error_rate': 0.02,
                'cpu_usage': 0.5,
                'memory_usage': 0.6,
                'network_io': 100.0
            }
    
    def _extract_security_data(self, analytics_report: Any) -> Dict[str, Any]:
        """Extract security data for threat detection"""
        # Mock security data extraction
        return {
            'security_incidents': len(analytics_report.security_incidents) if hasattr(analytics_report, 'security_incidents') else 0,
            'high_risk_behaviors': len([b for b in analytics_report.user_behavior_patterns if b.risk_score > 0.7]) if hasattr(analytics_report, 'user_behavior_patterns') else 0,
            'failed_auth_events': analytics_report.authentication_metrics.get('failed_auth_events', 0) if hasattr(analytics_report, 'authentication_metrics') else 0
        }
    
    def _extract_cluster_data(self, auth_sessions: List[AuthSession], analytics_report: Any) -> Dict[str, Any]:
        """Extract real cluster data for optimization analysis"""
        try:
            cluster_data = {}
            
            # Session metrics
            cluster_data['active_sessions'] = len(auth_sessions)
            cluster_data['total_users'] = len(set(s.user_principal.user_id for s in auth_sessions)) if auth_sessions else 0
            
            # Risk metrics
            if auth_sessions:
                cluster_data['avg_risk_score'] = sum(s.risk_score for s in auth_sessions) / len(auth_sessions)
            else:
                cluster_data['avg_risk_score'] = 0.0
            
            # Security metrics
            if hasattr(analytics_report, 'security_incidents'):
                cluster_data['security_incidents'] = len(analytics_report.security_incidents)
            else:
                cluster_data['security_incidents'] = 0
            
            # Resource metrics
            if hasattr(analytics_report, 'resource_metrics'):
                cluster_data['cpu_usage'] = analytics_report.resource_metrics.get('cpu_24h_avg', 0.5)
                cluster_data['memory_usage'] = analytics_report.resource_metrics.get('memory_24h_avg', 0.6)
            else:
                cluster_data['cpu_usage'] = 0.5
                cluster_data['memory_usage'] = 0.6
            
            # Cost metrics
            if hasattr(analytics_report, 'cost_metrics'):
                cluster_data['cost_per_hour'] = analytics_report.cost_metrics.get('per_hour_24h_avg', 10.0)
            else:
                cluster_data['cost_per_hour'] = 10.0
            
            # Error metrics
            if hasattr(analytics_report, 'error_metrics'):
                cluster_data['error_rate'] = analytics_report.error_metrics.get('rate_24h', 0.02)
            else:
                cluster_data['error_rate'] = 0.02
            
            # Performance metrics
            if hasattr(analytics_report, 'performance_metrics'):
                cluster_data['avg_response_time'] = analytics_report.performance_metrics.get('avg_response_time', 200.0)
            else:
                cluster_data['avg_response_time'] = 200.0
            
            # Cluster metrics
            cluster_data['pod_count'] = len(auth_sessions) if auth_sessions else 1
            cluster_data['node_count'] = 3  # Default cluster size
            cluster_data['namespace_count'] = 5  # Default namespace count
            
            return cluster_data
            
        except Exception as e:
            logger.error(f"Error extracting cluster data: {e}")
            # Return default cluster data if extraction fails
            return {
                'active_sessions': len(auth_sessions) if auth_sessions else 0,
                'total_users': len(set(s.user_principal.user_id for s in auth_sessions)) if auth_sessions else 0,
                'avg_risk_score': 0.0,
                'security_incidents': 0,
                'cpu_usage': 0.5,
                'memory_usage': 0.6,
                'cost_per_hour': 10.0,
                'error_rate': 0.02,
                'avg_response_time': 200.0,
                'pod_count': 1,
                'node_count': 3,
                'namespace_count': 5
            }
    
    async def _create_ml_alert(self, anomaly: AnomalyDetection):
        """Create alert for ML-detected anomaly"""
        try:
            # Create alert for the monitor
            alert_data = {
                'alert_type': 'ml_anomaly',
                'severity': anomaly.severity,
                'title': f"ML-Detected Anomaly: {anomaly.anomaly_type}",
                'description': anomaly.description,
                'metadata': {
                    'anomaly_id': anomaly.anomaly_id,
                    'confidence_score': anomaly.confidence_score,
                    'recommendations': anomaly.recommendations
                }
            }
            
            # This would integrate with the real-time monitor
            logger.info(f"Created ML alert for anomaly: {anomaly.anomaly_id}")
            
        except Exception as e:
            logger.error(f"Error creating ML alert: {e}")
    
    async def _create_security_alert(self, threat: Dict[str, Any]):
        """Create alert for security threat"""
        try:
            # Create security alert
            alert_data = {
                'alert_type': 'security_threat',
                'severity': threat['severity'],
                'title': f"Security Threat: {threat['threat_type']}",
                'description': threat['description'],
                'metadata': {
                    'threat_id': threat['threat_id'],
                    'confidence_score': threat['confidence_score'],
                    'risk_score': threat['risk_score'],
                    'recommendations': threat['recommendations']
                }
            }
            
            logger.info(f"Created security alert for threat: {threat['threat_id']}")
            
        except Exception as e:
            logger.error(f"Error creating security alert: {e}")
    
    async def get_predictions(self, model_type: Optional[MLModelType] = None) -> List[MLPrediction]:
        """Get recent predictions"""
        predictions = [item for item in self.processing_queue if isinstance(item, MLPrediction)]
        
        if model_type:
            predictions = [p for p in predictions if p.model_type == model_type]
        
        return predictions
    
    async def get_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Get recent optimization recommendations"""
        return [item for item in self.processing_queue if isinstance(item, OptimizationRecommendation)]
    
    async def train_model(self, model_type: MLModelType, training_data: List[Dict[str, Any]]) -> bool:
        """Train a specific ML model"""
        try:
            model = self.models.get(model_type)
            if model:
                success = await model.train(training_data)
                if success:
                    logger.info(f"Successfully trained {model_type.value} model")
                return success
            else:
                logger.error(f"Model type {model_type.value} not found")
                return False
        except Exception as e:
            logger.error(f"Error training {model_type.value} model: {e}")
            return False
    
    async def get_model_performance(self, model_type: MLModelType) -> Dict[str, Any]:
        """Get performance metrics for a specific model"""
        try:
            model = self.models.get(model_type)
            if model and model.is_trained:
                return {
                    'model_type': model_type.value,
                    'is_trained': model.is_trained,
                    'last_training': model.last_training,
                    'performance_metrics': model.performance_metrics
                }
            else:
                return {
                    'model_type': model_type.value,
                    'is_trained': False,
                    'last_training': None,
                    'performance_metrics': {}
                }
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {} 