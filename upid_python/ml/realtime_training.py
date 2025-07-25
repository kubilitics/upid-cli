#!/usr/bin/env python3
"""
UPID CLI - Real-time ML Model Training System
Phase 5: Advanced ML Enhancement - Task 5.1
Enterprise-grade adaptive learning with online training and drift detection
"""

import logging
import asyncio
import threading
import time
import json
import pickle
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib

from ..core.metrics_collector import MetricsCollector, PodMetrics, ClusterMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from .pipeline import MLPipeline, MLFeatures, MLPrediction
from .training import ModelTrainer, TrainingMetrics
from .models.optimization import OptimizationModel
from .models.prediction import PredictionModel
from .models.anomaly import AnomalyDetectionModel

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformanceMetrics:
    """Real-time model performance tracking"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    prediction_count: int
    error_rate: float
    confidence_avg: float
    latency_ms: float
    last_updated: datetime
    drift_score: float
    drift_detected: bool


@dataclass
class TrainingTrigger:
    """Training trigger configuration"""
    trigger_type: str  # performance, drift, schedule, manual
    threshold_value: float
    current_value: float
    triggered: bool
    last_trigger: Optional[datetime]
    trigger_count: int


@dataclass
class OnlineTrainingConfig:
    """Online training configuration"""
    batch_size: int = 1000
    learning_rate: float = 0.01
    drift_threshold: float = 0.1
    performance_threshold: float = 0.8
    retrain_interval_hours: int = 24
    max_training_samples: int = 100000
    feature_importance_threshold: float = 0.05
    model_comparison_window: int = 10
    enable_adaptive_learning: bool = True
    enable_drift_detection: bool = True
    enable_auto_retrain: bool = True


@dataclass
class ModelVersion:
    """Model version tracking"""
    model_id: str
    version: str
    model_type: str
    creation_time: datetime
    performance_metrics: ModelPerformanceMetrics
    model_path: str
    config_hash: str
    training_data_hash: str
    is_active: bool
    rollback_available: bool


class ModelDriftDetector:
    """Detects model drift using statistical methods"""
    
    def __init__(self, window_size: int = 1000, threshold: float = 0.1):
        self.window_size = window_size
        self.threshold = threshold
        self.reference_data = deque(maxlen=window_size)
        self.current_data = deque(maxlen=window_size)
        
    def add_reference_sample(self, features: np.ndarray):
        """Add sample to reference distribution"""
        self.reference_data.append(features)
    
    def add_current_sample(self, features: np.ndarray):
        """Add sample to current distribution"""
        self.current_data.append(features)
    
    def detect_drift(self) -> Tuple[bool, float]:
        """Detect drift using KL divergence"""
        if len(self.reference_data) < 100 or len(self.current_data) < 100:
            return False, 0.0
        
        try:
            # Calculate feature distributions
            ref_array = np.array(list(self.reference_data))
            curr_array = np.array(list(self.current_data))
            
            # KL divergence approximation
            drift_score = self._calculate_kl_divergence(ref_array, curr_array)
            drift_detected = drift_score > self.threshold
            
            return drift_detected, drift_score
            
        except Exception as e:
            logger.warning(f"Drift detection error: {e}")
            return False, 0.0
    
    def _calculate_kl_divergence(self, ref_data: np.ndarray, curr_data: np.ndarray) -> float:
        """Calculate KL divergence between distributions"""
        try:
            # Simple implementation using histograms
            kl_sum = 0.0
            
            for i in range(ref_data.shape[1]):
                ref_hist, bins = np.histogram(ref_data[:, i], bins=20, density=True)
                curr_hist, _ = np.histogram(curr_data[:, i], bins=bins, density=True)
                
                # Add small epsilon to avoid log(0)
                ref_hist += 1e-10
                curr_hist += 1e-10
                
                # KL divergence
                kl = np.sum(curr_hist * np.log(curr_hist / ref_hist))
                kl_sum += kl
            
            return kl_sum / ref_data.shape[1]
            
        except Exception as e:
            logger.warning(f"KL divergence calculation error: {e}")
            return 0.0


class AdaptiveLearningEngine:
    """Adaptive learning engine with online training capabilities"""
    
    def __init__(self, config: OnlineTrainingConfig):
        self.config = config
        self.training_buffer = deque(maxlen=config.max_training_samples)
        self.performance_history = deque(maxlen=config.model_comparison_window)
        self.learning_rate = config.learning_rate
        
    def add_training_sample(self, features: np.ndarray, target: Any, prediction: Any, confidence: float):
        """Add new training sample"""
        sample = {
            'features': features,
            'target': target,
            'prediction': prediction,
            'confidence': confidence,
            'timestamp': datetime.utcnow(),
            'correct': prediction == target
        }
        self.training_buffer.append(sample)
    
    def should_trigger_training(self, current_performance: float) -> bool:
        """Determine if adaptive training should be triggered"""
        if not self.config.enable_adaptive_learning:
            return False
        
        # Performance-based trigger
        if current_performance < self.config.performance_threshold:
            return True
        
        # Sample size trigger
        if len(self.training_buffer) >= self.config.batch_size:
            return True
        
        return False
    
    def get_training_batch(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get batch for online training"""
        if len(self.training_buffer) < self.config.batch_size:
            # Use all available samples
            samples = list(self.training_buffer)
        else:
            # Use recent samples with some older ones for stability
            recent_count = int(self.config.batch_size * 0.8)
            older_count = self.config.batch_size - recent_count
            
            recent_samples = list(self.training_buffer)[-recent_count:]
            older_samples = list(self.training_buffer)[:-recent_count][-older_count:]
            
            samples = recent_samples + older_samples
        
        features = np.array([s['features'] for s in samples])
        targets = np.array([s['target'] for s in samples])
        
        return features, targets
    
    def update_learning_rate(self, performance_trend: float):
        """Adaptively update learning rate based on performance"""
        if performance_trend > 0:
            # Performance improving, slightly increase learning rate
            self.learning_rate = min(self.learning_rate * 1.05, 0.1)
        elif performance_trend < -0.05:
            # Performance declining, decrease learning rate
            self.learning_rate = max(self.learning_rate * 0.9, 0.001)


class ModelVersionManager:
    """Manages model versions and rollback capabilities"""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model_dir.mkdir(exist_ok=True)
        self.versions: Dict[str, List[ModelVersion]] = defaultdict(list)
        self.active_models: Dict[str, ModelVersion] = {}
        
    def save_model_version(self, model: BaseEstimator, model_type: str, 
                          performance_metrics: ModelPerformanceMetrics,
                          config_hash: str, training_data_hash: str) -> ModelVersion:
        """Save new model version"""
        version_id = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        model_id = f"{model_type}_{version_id}"
        model_path = self.model_dir / f"{model_id}.pkl"
        
        # Save model
        joblib.dump(model, model_path)
        
        # Create version record
        version = ModelVersion(
            model_id=model_id,
            version=version_id,
            model_type=model_type,
            creation_time=datetime.utcnow(),
            performance_metrics=performance_metrics,
            model_path=str(model_path),
            config_hash=config_hash,
            training_data_hash=training_data_hash,
            is_active=False,
            rollback_available=True
        )
        
        self.versions[model_type].append(version)
        
        # Keep only last 10 versions per model type
        if len(self.versions[model_type]) > 10:
            old_version = self.versions[model_type].pop(0)
            try:
                Path(old_version.model_path).unlink()
            except FileNotFoundError:
                pass
        
        return version
    
    def activate_model_version(self, model_type: str, version: ModelVersion) -> bool:
        """Activate a specific model version"""
        try:
            # Deactivate current active model
            if model_type in self.active_models:
                self.active_models[model_type].is_active = False
            
            # Activate new version
            version.is_active = True
            self.active_models[model_type] = version
            
            logger.info(f"Activated model {version.model_id} for type {model_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate model version: {e}")
            return False
    
    def rollback_model(self, model_type: str) -> Optional[ModelVersion]:
        """Rollback to previous model version"""
        if model_type not in self.versions or len(self.versions[model_type]) < 2:
            logger.warning(f"No rollback available for model type {model_type}")
            return None
        
        # Find current active version
        current_active = None
        for version in self.versions[model_type]:
            if version.is_active:
                current_active = version
                break
        
        if not current_active:
            logger.warning(f"No active model found for type {model_type}")
            return None
        
        # Find previous version
        current_idx = self.versions[model_type].index(current_active)
        if current_idx == 0:
            logger.warning(f"No previous version available for rollback")
            return None
        
        previous_version = self.versions[model_type][current_idx - 1]
        
        # Activate previous version
        if self.activate_model_version(model_type, previous_version):
            logger.info(f"Rolled back to model {previous_version.model_id}")
            return previous_version
        
        return None
    
    def get_active_model(self, model_type: str) -> Optional[BaseEstimator]:
        """Get currently active model"""
        if model_type not in self.active_models:
            return None
        
        version = self.active_models[model_type]
        try:
            return joblib.load(version.model_path)
        except Exception as e:
            logger.error(f"Failed to load active model: {e}")
            return None


class ABTestingFramework:
    """A/B testing framework for model comparison"""
    
    def __init__(self, traffic_split: float = 0.5):
        self.traffic_split = traffic_split
        self.model_a_metrics = defaultdict(list)
        self.model_b_metrics = defaultdict(list)
        self.current_test: Optional[Dict[str, Any]] = None
        
    def start_ab_test(self, model_a: BaseEstimator, model_b: BaseEstimator, 
                     test_name: str, duration_hours: int = 24) -> bool:
        """Start A/B test between two models"""
        self.current_test = {
            'test_name': test_name,
            'model_a': model_a,
            'model_b': model_b,
            'start_time': datetime.utcnow(),
            'end_time': datetime.utcnow() + timedelta(hours=duration_hours),
            'traffic_split': self.traffic_split
        }
        
        # Clear previous metrics
        self.model_a_metrics.clear()
        self.model_b_metrics.clear()
        
        logger.info(f"Started A/B test: {test_name}")
        return True
    
    def route_prediction(self, features: np.ndarray) -> Tuple[str, Any]:
        """Route prediction to A or B model"""
        if not self.current_test:
            raise ValueError("No active A/B test")
        
        # Simple hash-based routing for consistency
        feature_hash = hashlib.md5(features.tobytes()).hexdigest()
        hash_val = int(feature_hash[:8], 16) / (2**32)
        
        if hash_val < self.traffic_split:
            model = self.current_test['model_a']
            variant = 'A'
        else:
            model = self.current_test['model_b']
            variant = 'B'
        
        prediction = model.predict([features])[0]
        return variant, prediction
    
    def record_result(self, variant: str, prediction: Any, actual: Any, 
                     latency_ms: float, confidence: float):
        """Record prediction result for A/B test"""
        result = {
            'prediction': prediction,
            'actual': actual,
            'latency_ms': latency_ms,
            'confidence': confidence,
            'correct': prediction == actual,
            'timestamp': datetime.utcnow()
        }
        
        if variant == 'A':
            self.model_a_metrics['results'].append(result)
        else:
            self.model_b_metrics['results'].append(result)
    
    def get_test_results(self) -> Dict[str, Any]:
        """Get A/B test results and statistics"""
        if not self.current_test:
            return {}
        
        def calculate_metrics(results: List[Dict]) -> Dict[str, float]:
            if not results:
                return {}
            
            correct_predictions = sum(1 for r in results if r['correct'])
            total_predictions = len(results)
            avg_latency = sum(r['latency_ms'] for r in results) / total_predictions
            avg_confidence = sum(r['confidence'] for r in results) / total_predictions
            
            return {
                'accuracy': correct_predictions / total_predictions if total_predictions > 0 else 0,
                'total_predictions': total_predictions,
                'avg_latency_ms': avg_latency,
                'avg_confidence': avg_confidence
            }
        
        model_a_results = calculate_metrics(self.model_a_metrics.get('results', []))
        model_b_results = calculate_metrics(self.model_b_metrics.get('results', []))
        
        # Statistical significance test (simplified)
        significance = self._calculate_significance(
            model_a_results.get('accuracy', 0),
            model_b_results.get('accuracy', 0),
            model_a_results.get('total_predictions', 0),
            model_b_results.get('total_predictions', 0)
        )
        
        return {
            'test_name': self.current_test['test_name'],
            'start_time': self.current_test['start_time'],
            'end_time': self.current_test['end_time'],
            'traffic_split': self.current_test['traffic_split'],
            'model_a_metrics': model_a_results,
            'model_b_metrics': model_b_results,
            'statistical_significance': significance,
            'recommended_model': 'A' if model_a_results.get('accuracy', 0) > model_b_results.get('accuracy', 0) else 'B'
        }
    
    def _calculate_significance(self, acc_a: float, acc_b: float, n_a: int, n_b: int) -> float:
        """Calculate statistical significance (simplified z-test)"""
        if n_a < 30 or n_b < 30:
            return 0.0
        
        try:
            p_pooled = (acc_a * n_a + acc_b * n_b) / (n_a + n_b)
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b))
            z_score = abs(acc_a - acc_b) / se
            
            # Convert z-score to p-value approximation
            p_value = 2 * (1 - 0.5 * (1 + np.tanh(z_score * np.sqrt(2/np.pi))))
            return 1 - p_value
            
        except Exception:
            return 0.0


class RealtimeMLTrainingSystem:
    """
    Real-time ML model training system with advanced features
    
    Features:
    - Online/incremental learning
    - Model drift detection
    - Automatic retraining triggers
    - A/B testing framework
    - Model versioning and rollback
    - Performance monitoring
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.ml_pipeline = MLPipeline(metrics_collector, resource_analyzer)
        self.model_trainer = ModelTrainer(metrics_collector, resource_analyzer)
        
        # Configuration
        self.config = OnlineTrainingConfig()
        
        # Components
        self.drift_detectors: Dict[str, ModelDriftDetector] = {}
        self.adaptive_engines: Dict[str, AdaptiveLearningEngine] = {}
        self.version_manager = ModelVersionManager(Path("models/versions"))
        self.ab_framework = ABTestingFramework()
        
        # Performance tracking
        self.performance_metrics: Dict[str, ModelPerformanceMetrics] = {}
        self.training_triggers: Dict[str, List[TrainingTrigger]] = defaultdict(list)
        
        # Threading
        self.training_executor = ThreadPoolExecutor(max_workers=2)
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("🔧 Initializing real-time ML training system")
    
    async def initialize(self) -> bool:
        """Initialize the real-time training system"""
        try:
            logger.info("🚀 Initializing real-time ML training system...")
            
            # Initialize components
            await self.ml_pipeline.initialize()
            await self.model_trainer.initialize()
            
            # Initialize drift detectors and adaptive engines for each model type
            model_types = ['optimization', 'prediction', 'anomaly']
            for model_type in model_types:
                self.drift_detectors[model_type] = ModelDriftDetector(
                    window_size=1000,
                    threshold=self.config.drift_threshold
                )
                self.adaptive_engines[model_type] = AdaptiveLearningEngine(self.config)
            
            # Start monitoring thread
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("✅ Real-time ML training system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize real-time training system: {e}")
            return False
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for training triggers
                asyncio.run(self._check_training_triggers())
                
                # Monitor model performance
                asyncio.run(self._monitor_model_performance())
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    async def _check_training_triggers(self):
        """Check if any models need retraining"""
        for model_type in self.performance_metrics:
            metrics = self.performance_metrics[model_type]
            
            # Performance-based trigger
            if metrics.accuracy < self.config.performance_threshold:
                await self._trigger_retraining(model_type, 'performance', metrics.accuracy)
            
            # Drift-based trigger
            if metrics.drift_detected:
                await self._trigger_retraining(model_type, 'drift', metrics.drift_score)
            
            # Schedule-based trigger
            time_since_training = datetime.utcnow() - metrics.last_updated
            if time_since_training.total_seconds() > self.config.retrain_interval_hours * 3600:
                await self._trigger_retraining(model_type, 'schedule', time_since_training.total_seconds())
    
    async def _trigger_retraining(self, model_type: str, trigger_type: str, trigger_value: float):
        """Trigger model retraining"""
        if not self.config.enable_auto_retrain:
            return
        
        logger.info(f"🔄 Triggering retraining for {model_type} model (trigger: {trigger_type})")
        
        # Record trigger
        trigger = TrainingTrigger(
            trigger_type=trigger_type,
            threshold_value=getattr(self.config, f"{trigger_type}_threshold", 0.0),
            current_value=trigger_value,
            triggered=True,
            last_trigger=datetime.utcnow(),
            trigger_count=len(self.training_triggers[model_type]) + 1
        )
        self.training_triggers[model_type].append(trigger)
        
        # Submit retraining task
        future = self.training_executor.submit(self._retrain_model, model_type)
        
        # Handle result asynchronously
        def handle_result(fut):
            try:
                result = fut.result()
                if result:
                    logger.info(f"✅ Retraining completed for {model_type}")
                else:
                    logger.error(f"❌ Retraining failed for {model_type}")
            except Exception as e:
                logger.error(f"❌ Retraining error for {model_type}: {e}")
        
        future.add_done_callback(handle_result)
    
    def _retrain_model(self, model_type: str) -> bool:
        """Retrain model (runs in thread)"""
        try:
            # Get training data from adaptive engine
            adaptive_engine = self.adaptive_engines[model_type]
            features, targets = adaptive_engine.get_training_batch()
            
            if len(features) < 100:
                logger.warning(f"Insufficient training data for {model_type}")
                return False
            
            # Create new model based on type
            if model_type == 'optimization':
                model = OptimizationModel()
            elif model_type == 'prediction':
                model = PredictionModel()
            elif model_type == 'anomaly':
                model = AnomalyDetectionModel()
            else:
                logger.error(f"Unknown model type: {model_type}")
                return False
            
            # Train model
            model.fit(features, targets)
            
            # Evaluate performance
            predictions = model.predict(features)
            accuracy = accuracy_score(targets, predictions)
            
            # Create performance metrics
            performance_metrics = ModelPerformanceMetrics(
                model_name=f"{model_type}_realtime",
                accuracy=accuracy,
                precision=precision_score(targets, predictions, average='weighted', zero_division=0),
                recall=recall_score(targets, predictions, average='weighted', zero_division=0),
                f1_score=f1_score(targets, predictions, average='weighted', zero_division=0),
                prediction_count=len(predictions),
                error_rate=1 - accuracy,
                confidence_avg=0.85,  # Placeholder
                latency_ms=10.0,  # Placeholder
                last_updated=datetime.utcnow(),
                drift_score=0.0,
                drift_detected=False
            )
            
            # Save new model version
            config_hash = hashlib.md5(json.dumps(asdict(self.config)).encode()).hexdigest()
            data_hash = hashlib.md5(features.tobytes()).hexdigest()
            
            new_version = self.version_manager.save_model_version(
                model, model_type, performance_metrics, config_hash, data_hash
            )
            
            # Compare with current model performance
            current_performance = self.performance_metrics.get(model_type)
            if not current_performance or new_version.performance_metrics.accuracy > current_performance.accuracy:
                # Activate new model
                self.version_manager.activate_model_version(model_type, new_version)
                self.performance_metrics[model_type] = new_version.performance_metrics
                logger.info(f"Activated new {model_type} model with accuracy {accuracy:.3f}")
            else:
                logger.info(f"New {model_type} model performance not better, keeping current model")
            
            return True
            
        except Exception as e:
            logger.error(f"Error retraining {model_type} model: {e}")
            return False
    
    async def _monitor_model_performance(self):
        """Monitor real-time model performance"""
        for model_type in self.drift_detectors:
            try:
                # Get recent predictions and check for drift
                drift_detector = self.drift_detectors[model_type]
                
                # Simulate getting recent prediction features
                # In real implementation, this would come from actual predictions
                recent_features = np.random.randn(100, 10)  # Placeholder
                
                for features in recent_features:
                    drift_detector.add_current_sample(features)
                
                # Check for drift
                drift_detected, drift_score = drift_detector.detect_drift()
                
                # Update performance metrics
                if model_type in self.performance_metrics:
                    self.performance_metrics[model_type].drift_score = drift_score
                    self.performance_metrics[model_type].drift_detected = drift_detected
                
            except Exception as e:
                logger.warning(f"Error monitoring {model_type}: {e}")
    
    async def add_prediction_feedback(self, model_type: str, features: np.ndarray, 
                                   prediction: Any, actual: Any, confidence: float):
        """Add prediction feedback for online learning"""
        try:
            # Add to adaptive learning engine
            adaptive_engine = self.adaptive_engines[model_type]
            adaptive_engine.add_training_sample(features, actual, prediction, confidence)
            
            # Add to drift detector
            drift_detector = self.drift_detectors[model_type]
            drift_detector.add_current_sample(features)
            
            # Check if adaptive training should be triggered
            current_performance = self.performance_metrics.get(model_type)
            if current_performance and adaptive_engine.should_trigger_training(current_performance.accuracy):
                await self._trigger_retraining(model_type, 'adaptive', current_performance.accuracy)
            
        except Exception as e:
            logger.error(f"Error adding prediction feedback: {e}")
    
    async def start_ab_test(self, model_type: str, candidate_model: BaseEstimator, 
                          test_name: str, duration_hours: int = 24) -> bool:
        """Start A/B test for model comparison"""
        try:
            current_model = self.version_manager.get_active_model(model_type)
            if not current_model:
                logger.error(f"No active model found for type {model_type}")
                return False
            
            success = self.ab_framework.start_ab_test(
                current_model, candidate_model, test_name, duration_hours
            )
            
            if success:
                logger.info(f"Started A/B test '{test_name}' for {model_type} model")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting A/B test: {e}")
            return False
    
    async def get_ab_test_results(self) -> Dict[str, Any]:
        """Get current A/B test results"""
        return self.ab_framework.get_test_results()
    
    async def rollback_model(self, model_type: str) -> bool:
        """Rollback to previous model version"""
        try:
            previous_version = self.version_manager.rollback_model(model_type)
            if previous_version:
                self.performance_metrics[model_type] = previous_version.performance_metrics
                logger.info(f"Rolled back {model_type} model to version {previous_version.version}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error rolling back model: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'config': asdict(self.config),
            'performance_metrics': {k: asdict(v) for k, v in self.performance_metrics.items()},
            'training_triggers': {k: [asdict(t) for t in v] for k, v in self.training_triggers.items()},
            'active_models': {k: asdict(v) for k, v in self.version_manager.active_models.items()},
            'ab_test_status': await self.get_ab_test_results(),
            'monitoring_active': self.monitoring_active,
            'system_uptime': datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the training system"""
        logger.info("🛑 Shutting down real-time ML training system...")
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.training_executor.shutdown(wait=True)
        
        logger.info("✅ Real-time ML training system shutdown complete")


# Export main classes
__all__ = [
    'RealtimeMLTrainingSystem',
    'OnlineTrainingConfig',
    'ModelPerformanceMetrics',
    'ModelVersionManager',
    'ABTestingFramework',
    'ModelDriftDetector',
    'AdaptiveLearningEngine'
]