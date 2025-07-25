#!/usr/bin/env python3
"""
UPID CLI - Multi-Model Ensemble System
Phase 5: Advanced ML Enhancement - Task 5.3
Enterprise-grade ensemble learning with meta-learning and dynamic model selection
"""

import logging
import asyncio
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, Future
import threading

from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.ensemble import VotingClassifier, VotingRegressor, BaggingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import joblib

from ..core.metrics_collector import MetricsCollector
from ..core.resource_analyzer import ResourceAnalyzer
from .pipeline import MLPipeline, MLPrediction
from .realtime_training import RealtimeMLTrainingSystem, ModelPerformanceMetrics
from .advanced_feature_engineering import AdvancedFeatureEngineering

logger = logging.getLogger(__name__)


@dataclass
class EnsembleConfig:
    """Ensemble system configuration"""
    # Model selection
    base_models: List[str] = None
    ensemble_methods: List[str] = None
    enable_stacking: bool = True
    enable_voting: bool = True
    enable_boosting: bool = True
    
    # Meta-learning
    enable_meta_learning: bool = True
    meta_model_type: str = "random_forest"
    meta_features_enabled: bool = True
    
    # Dynamic selection
    enable_dynamic_selection: bool = True
    selection_window_size: int = 100
    selection_threshold: float = 0.05
    
    # Performance tracking
    min_samples_for_ensemble: int = 50
    performance_history_size: int = 1000
    rebalance_interval_hours: int = 6
    
    # Computational resources
    max_models_in_ensemble: int = 10
    parallel_prediction: bool = True
    prediction_timeout_seconds: float = 5.0
    
    def __post_init__(self):
        if self.base_models is None:
            self.base_models = [
                "random_forest", "logistic_regression", "svm", 
                "neural_network", "naive_bayes", "knn", "decision_tree"
            ]
        if self.ensemble_methods is None:
            self.ensemble_methods = ["voting", "stacking", "dynamic_selection"]


@dataclass
class ModelPerformanceTracker:
    """Tracks individual model performance"""
    model_name: str
    accuracy_scores: deque
    prediction_times: deque
    confidence_scores: deque
    error_rates: deque
    last_updated: datetime
    total_predictions: int
    successful_predictions: int
    
    def __post_init__(self):
        # Initialize deques with max length
        if not isinstance(self.accuracy_scores, deque):
            self.accuracy_scores = deque(maxlen=1000)
        if not isinstance(self.prediction_times, deque):
            self.prediction_times = deque(maxlen=1000)
        if not isinstance(self.confidence_scores, deque):
            self.confidence_scores = deque(maxlen=1000)
        if not isinstance(self.error_rates, deque):
            self.error_rates = deque(maxlen=1000)
    
    def add_performance_data(self, accuracy: float, prediction_time: float, 
                           confidence: float, error_rate: float):
        """Add new performance data point"""
        self.accuracy_scores.append(accuracy)
        self.prediction_times.append(prediction_time)
        self.confidence_scores.append(confidence)
        self.error_rates.append(error_rate)
        self.last_updated = datetime.utcnow()
        self.total_predictions += 1
        if error_rate < 0.1:  # Consider successful if error rate < 10%
            self.successful_predictions += 1
    
    def get_average_performance(self) -> Dict[str, float]:
        """Get average performance metrics"""
        return {
            'accuracy': np.mean(self.accuracy_scores) if self.accuracy_scores else 0.0,
            'prediction_time': np.mean(self.prediction_times) if self.prediction_times else 0.0,
            'confidence': np.mean(self.confidence_scores) if self.confidence_scores else 0.0,
            'error_rate': np.mean(self.error_rates) if self.error_rates else 0.0,
            'success_rate': self.successful_predictions / self.total_predictions if self.total_predictions > 0 else 0.0
        }


@dataclass
class EnsemblePrediction:
    """Ensemble prediction result"""
    final_prediction: Any
    confidence: float
    model_predictions: Dict[str, Any]
    model_confidences: Dict[str, float]
    model_weights: Dict[str, float]
    ensemble_method: str
    prediction_time: float
    metadata: Dict[str, Any]
    timestamp: datetime


class BaseModelFactory:
    """Factory for creating base models"""
    
    @staticmethod
    def create_model(model_type: str, task_type: str = "classification") -> BaseEstimator:
        """Create model instance based on type and task"""
        
        if task_type == "classification":
            models = {
                "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "logistic_regression": LogisticRegression(random_state=42, max_iter=1000),
                "svm": SVC(probability=True, random_state=42),
                "neural_network": MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500),
                "naive_bayes": GaussianNB(),
                "knn": KNeighborsClassifier(n_neighbors=5),
                "decision_tree": DecisionTreeClassifier(random_state=42)
            }
        else:  # regression
            models = {
                "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "linear_regression": LinearRegression(),
                "svm": SVR(),
                "neural_network": MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500),
                "knn": KNeighborsRegressor(n_neighbors=5),
                "decision_tree": DecisionTreeRegressor(random_state=42)
            }
        
        if model_type not in models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return models[model_type]


class MetaLearner:
    """Meta-learner for ensemble optimization"""
    
    def __init__(self, meta_model_type: str = "random_forest"):
        self.meta_model_type = meta_model_type
        self.meta_model = None
        self.feature_names = []
        self.is_trained = False
        
    def extract_meta_features(self, base_predictions: Dict[str, Any], 
                            base_confidences: Dict[str, float],
                            base_features: np.ndarray) -> np.ndarray:
        """Extract meta-features for ensemble learning"""
        meta_features = []
        
        # Base model predictions as features
        for model_name in sorted(base_predictions.keys()):
            prediction = base_predictions[model_name]
            confidence = base_confidences[model_name]
            
            # Convert prediction to numerical feature
            if isinstance(prediction, (int, float)):
                meta_features.extend([prediction, confidence])
            elif isinstance(prediction, bool):
                meta_features.extend([float(prediction), confidence])
            else:
                # For categorical predictions, use one-hot encoding
                meta_features.extend([hash(str(prediction)) % 1000, confidence])
        
        # Agreement metrics
        predictions_list = list(base_predictions.values())
        if len(predictions_list) > 1:
            # Prediction agreement rate
            most_common = max(set(predictions_list), key=predictions_list.count)
            agreement_rate = predictions_list.count(most_common) / len(predictions_list)
            meta_features.append(agreement_rate)
            
            # Confidence variance
            confidences = list(base_confidences.values())
            confidence_variance = np.var(confidences)
            meta_features.append(confidence_variance)
        else:
            meta_features.extend([1.0, 0.0])
        
        # Input feature statistics
        if base_features is not None and len(base_features) > 0:
            meta_features.extend([
                np.mean(base_features),
                np.std(base_features),
                np.min(base_features),
                np.max(base_features)
            ])
        else:
            meta_features.extend([0.0, 0.0, 0.0, 0.0])
        
        return np.array(meta_features)
    
    def train_meta_model(self, meta_features_list: List[np.ndarray], 
                        best_model_labels: List[str]) -> bool:
        """Train meta-model to select best base model"""
        try:
            if len(meta_features_list) < 10:
                logger.warning("Insufficient meta-training data")
                return False
            
            X_meta = np.array(meta_features_list)
            y_meta = np.array(best_model_labels)
            
            # Create meta-model
            if self.meta_model_type == "random_forest":
                self.meta_model = RandomForestClassifier(n_estimators=50, random_state=42)
            elif self.meta_model_type == "logistic_regression":
                self.meta_model = LogisticRegression(random_state=42, max_iter=1000)
            else:
                self.meta_model = RandomForestClassifier(n_estimators=50, random_state=42)
            
            # Train meta-model
            self.meta_model.fit(X_meta, y_meta)
            self.is_trained = True
            
            logger.info(f"✅ Meta-model trained with {len(meta_features_list)} samples")
            return True
            
        except Exception as e:
            logger.error(f"❌ Meta-model training failed: {e}")
            return False
    
    def predict_best_model(self, meta_features: np.ndarray) -> Tuple[str, float]:
        """Predict which base model should perform best"""
        if not self.is_trained or self.meta_model is None:
            return "random_forest", 0.5  # Default fallback
        
        try:
            prediction = self.meta_model.predict([meta_features])[0]
            
            # Get prediction probability if available
            if hasattr(self.meta_model, 'predict_proba'):
                probabilities = self.meta_model.predict_proba([meta_features])[0]
                confidence = np.max(probabilities)
            else:
                confidence = 0.7  # Default confidence
            
            return prediction, confidence
            
        except Exception as e:
            logger.warning(f"Meta-model prediction failed: {e}")
            return "random_forest", 0.5


class DynamicModelSelector:
    """Dynamically selects best models based on recent performance"""
    
    def __init__(self, window_size: int = 100, threshold: float = 0.05):
        self.window_size = window_size
        self.threshold = threshold
        self.performance_history: Dict[str, ModelPerformanceTracker] = {}
        
    def update_performance(self, model_name: str, accuracy: float, 
                         prediction_time: float, confidence: float, error_rate: float):
        """Update model performance history"""
        if model_name not in self.performance_history:
            self.performance_history[model_name] = ModelPerformanceTracker(
                model_name=model_name,
                accuracy_scores=deque(maxlen=self.window_size),
                prediction_times=deque(maxlen=self.window_size),
                confidence_scores=deque(maxlen=self.window_size),
                error_rates=deque(maxlen=self.window_size),
                last_updated=datetime.utcnow(),
                total_predictions=0,
                successful_predictions=0
            )
        
        self.performance_history[model_name].add_performance_data(
            accuracy, prediction_time, confidence, error_rate
        )
    
    def select_best_models(self, max_models: int = 5) -> List[str]:
        """Select best performing models"""
        if not self.performance_history:
            return []
        
        # Calculate combined performance scores
        model_scores = {}
        
        for model_name, tracker in self.performance_history.items():
            if len(tracker.accuracy_scores) < 10:  # Need minimum data
                continue
            
            perf = tracker.get_average_performance()
            
            # Combined score: accuracy + (1 - error_rate) + confidence - (prediction_time penalty)
            time_penalty = min(perf['prediction_time'] / 1000.0, 0.5)  # Cap time penalty
            combined_score = (
                perf['accuracy'] * 0.4 +
                (1 - perf['error_rate']) * 0.3 +
                perf['confidence'] * 0.2 +
                perf['success_rate'] * 0.1 -
                time_penalty
            )
            
            model_scores[model_name] = combined_score
        
        # Sort by score and select top models
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        best_models = [model for model, score in sorted_models[:max_models]]
        
        return best_models
    
    def should_retrain_ensemble(self) -> bool:
        """Determine if ensemble should be retrained based on performance trends"""
        if len(self.performance_history) < 2:
            return False
        
        # Check if any model's performance has significantly changed
        for tracker in self.performance_history.values():
            if len(tracker.accuracy_scores) < 20:
                continue
            
            # Compare recent vs older performance
            recent_accuracy = np.mean(list(tracker.accuracy_scores)[-10:])
            older_accuracy = np.mean(list(tracker.accuracy_scores)[-20:-10])
            
            performance_change = abs(recent_accuracy - older_accuracy)
            if performance_change > self.threshold:
                return True
        
        return False


class EnsembleStrategy:
    """Base class for ensemble strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    def combine_predictions(self, predictions: Dict[str, Any], 
                          confidences: Dict[str, float],
                          weights: Optional[Dict[str, float]] = None) -> Tuple[Any, float]:
        """Combine predictions from multiple models"""
        raise NotImplementedError


class VotingStrategy(EnsembleStrategy):
    """Voting ensemble strategy"""
    
    def __init__(self, voting_type: str = "soft"):
        super().__init__("voting")
        self.voting_type = voting_type
    
    def combine_predictions(self, predictions: Dict[str, Any], 
                          confidences: Dict[str, float],
                          weights: Optional[Dict[str, float]] = None) -> Tuple[Any, float]:
        """Combine predictions using voting"""
        
        if not predictions:
            return None, 0.0
        
        if weights is None:
            weights = {model: 1.0 for model in predictions.keys()}
        
        if self.voting_type == "hard":
            # Hard voting - majority vote
            prediction_list = []
            for model, pred in predictions.items():
                weight = weights.get(model, 1.0)
                prediction_list.extend([pred] * int(weight * 10))
            
            if prediction_list:
                final_prediction = max(set(prediction_list), key=prediction_list.count)
                confidence = prediction_list.count(final_prediction) / len(prediction_list)
            else:
                final_prediction = list(predictions.values())[0]
                confidence = 0.5
                
        else:
            # Soft voting - weighted average
            if all(isinstance(p, (int, float)) for p in predictions.values()):
                # Numerical predictions
                weighted_sum = sum(predictions[model] * weights.get(model, 1.0) 
                                 for model in predictions)
                total_weight = sum(weights.get(model, 1.0) for model in predictions)
                final_prediction = weighted_sum / total_weight if total_weight > 0 else 0
                
                # Confidence as weighted average
                weighted_confidence = sum(confidences[model] * weights.get(model, 1.0) 
                                        for model in confidences)
                confidence = weighted_confidence / total_weight if total_weight > 0 else 0
            else:
                # Categorical predictions - use hard voting
                return self.combine_predictions(predictions, confidences, weights)
        
        return final_prediction, confidence


class StackingStrategy(EnsembleStrategy):
    """Stacking ensemble strategy"""
    
    def __init__(self):
        super().__init__("stacking")
        self.meta_model = None
        self.is_trained = False
    
    def train_meta_model(self, base_predictions_list: List[Dict[str, Any]], 
                        true_labels: List[Any]) -> bool:
        """Train meta-model for stacking"""
        try:
            if len(base_predictions_list) < 10:
                return False
            
            # Prepare meta-features
            meta_features = []
            for predictions in base_predictions_list:
                features = []
                for model_name in sorted(predictions.keys()):
                    pred = predictions[model_name]
                    if isinstance(pred, (int, float)):
                        features.append(pred)
                    elif isinstance(pred, bool):
                        features.append(float(pred))
                    else:
                        features.append(hash(str(pred)) % 1000)
                meta_features.append(features)
            
            X_meta = np.array(meta_features)
            y_meta = np.array(true_labels)
            
            # Train meta-model
            if len(set(true_labels)) <= 2:
                self.meta_model = LogisticRegression(random_state=42, max_iter=1000)
            else:
                self.meta_model = RandomForestClassifier(n_estimators=50, random_state=42)
            
            self.meta_model.fit(X_meta, y_meta)
            self.is_trained = True
            
            return True
            
        except Exception as e:
            logger.error(f"Stacking meta-model training failed: {e}")
            return False
    
    def combine_predictions(self, predictions: Dict[str, Any], 
                          confidences: Dict[str, float],
                          weights: Optional[Dict[str, float]] = None) -> Tuple[Any, float]:
        """Combine predictions using stacking"""
        
        if not self.is_trained or self.meta_model is None:
            # Fallback to voting
            voting_strategy = VotingStrategy("soft")
            return voting_strategy.combine_predictions(predictions, confidences, weights)
        
        try:
            # Prepare meta-features
            features = []
            for model_name in sorted(predictions.keys()):
                pred = predictions[model_name]
                if isinstance(pred, (int, float)):
                    features.append(pred)
                elif isinstance(pred, bool):
                    features.append(float(pred))
                else:
                    features.append(hash(str(pred)) % 1000)
            
            # Get meta-model prediction
            meta_features = np.array(features).reshape(1, -1)
            final_prediction = self.meta_model.predict(meta_features)[0]
            
            # Get confidence if available
            if hasattr(self.meta_model, 'predict_proba'):
                probabilities = self.meta_model.predict_proba(meta_features)[0]
                confidence = np.max(probabilities)
            else:
                confidence = np.mean(list(confidences.values()))
            
            return final_prediction, confidence
            
        except Exception as e:
            logger.warning(f"Stacking prediction failed: {e}")
            # Fallback to voting
            voting_strategy = VotingStrategy("soft")
            return voting_strategy.combine_predictions(predictions, confidences, weights)


class MultiModelEnsembleSystem:
    """
    Multi-model ensemble system with advanced features
    
    Features:
    - Multiple ensemble strategies (voting, stacking, dynamic selection)
    - Meta-learning for optimal model selection
    - Dynamic model performance tracking
    - Parallel prediction execution
    - Automated ensemble rebalancing
    - Real-time performance monitoring
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.config = EnsembleConfig()
        
        # Core components
        self.feature_engineering = AdvancedFeatureEngineering(metrics_collector, resource_analyzer)
        self.realtime_training = RealtimeMLTrainingSystem(metrics_collector, resource_analyzer)
        
        # Base models
        self.base_models: Dict[str, BaseEstimator] = {}
        self.model_factory = BaseModelFactory()
        
        # Ensemble strategies
        self.strategies: Dict[str, EnsembleStrategy] = {
            "voting": VotingStrategy("soft"),
            "stacking": StackingStrategy()
        }
        
        # Meta-learning and selection
        self.meta_learner = MetaLearner(self.config.meta_model_type)
        self.dynamic_selector = DynamicModelSelector(
            self.config.selection_window_size,
            self.config.selection_threshold
        )
        
        # Performance tracking
        self.ensemble_performance_history: deque = deque(maxlen=self.config.performance_history_size)
        self.prediction_cache: Dict[str, Any] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_models_in_ensemble)
        self.rebalancing_active = False
        self.rebalancing_thread: Optional[threading.Thread] = None
        
        logger.info("🔧 Initializing multi-model ensemble system")
    
    async def initialize(self) -> bool:
        """Initialize the ensemble system"""
        try:
            logger.info("🚀 Initializing multi-model ensemble system...")
            
            # Initialize components
            await self.feature_engineering.initialize()
            await self.realtime_training.initialize()
            
            # Initialize base models
            await self._initialize_base_models()
            
            # Start rebalancing thread
            self.rebalancing_active = True
            self.rebalancing_thread = threading.Thread(target=self._rebalancing_loop, daemon=True)
            self.rebalancing_thread.start()
            
            logger.info("✅ Multi-model ensemble system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ensemble system: {e}")
            return False
    
    async def _initialize_base_models(self):
        """Initialize base models"""
        for model_type in self.config.base_models:
            try:
                model = self.model_factory.create_model(model_type, "classification")
                self.base_models[model_type] = model
                logger.info(f"✅ Initialized {model_type} model")
            except Exception as e:
                logger.warning(f"Failed to initialize {model_type}: {e}")
    
    def _rebalancing_loop(self):
        """Background rebalancing loop"""
        while self.rebalancing_active:
            try:
                # Check if ensemble needs rebalancing
                if self.dynamic_selector.should_retrain_ensemble():
                    asyncio.run(self._rebalance_ensemble())
                
                # Sleep for rebalancing interval
                time.sleep(self.config.rebalance_interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in rebalancing loop: {e}")
                time.sleep(3600)  # Sleep 1 hour on error
    
    async def _rebalance_ensemble(self):
        """Rebalance ensemble based on performance"""
        try:
            logger.info("🔄 Rebalancing ensemble...")
            
            # Select best performing models
            best_models = self.dynamic_selector.select_best_models(self.config.max_models_in_ensemble)
            
            if best_models:
                # Update active models
                new_base_models = {}
                for model_name in best_models:
                    if model_name in self.base_models:
                        new_base_models[model_name] = self.base_models[model_name]
                
                self.base_models = new_base_models
                logger.info(f"✅ Ensemble rebalanced with models: {list(self.base_models.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Ensemble rebalancing failed: {e}")
    
    async def train_ensemble(self, X: np.ndarray, y: np.ndarray, 
                           task_type: str = "classification") -> bool:
        """Train all models in the ensemble"""
        try:
            logger.info(f"🎯 Training ensemble with {len(self.base_models)} models...")
            
            if len(X) < self.config.min_samples_for_ensemble:
                logger.warning(f"Insufficient training samples: {len(X)}")
                return False
            
            # Train base models in parallel
            training_futures = []
            
            for model_name, model in self.base_models.items():
                future = self.executor.submit(self._train_single_model, model, X, y, model_name)
                training_futures.append((model_name, future))
            
            # Wait for training completion
            trained_models = {}
            for model_name, future in training_futures:
                try:
                    trained_model = future.result(timeout=300)  # 5 minute timeout
                    if trained_model is not None:
                        trained_models[model_name] = trained_model
                except Exception as e:
                    logger.warning(f"Training failed for {model_name}: {e}")
            
            # Update base models
            self.base_models.update(trained_models)
            
            # Train ensemble strategies
            await self._train_ensemble_strategies(X, y)
            
            logger.info(f"✅ Ensemble training completed with {len(trained_models)} models")
            return len(trained_models) > 0
            
        except Exception as e:
            logger.error(f"❌ Ensemble training failed: {e}")
            return False
    
    def _train_single_model(self, model: BaseEstimator, X: np.ndarray, y: np.ndarray, model_name: str) -> Optional[BaseEstimator]:
        """Train a single model (runs in thread)"""
        try:
            model.fit(X, y)
            
            # Evaluate model performance
            if len(X) > 10:
                scores = cross_val_score(model, X, y, cv=min(5, len(X)//10))
                accuracy = np.mean(scores)
                logger.info(f"✅ {model_name} trained with accuracy: {accuracy:.3f}")
            
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to train {model_name}: {e}")
            return None
    
    async def _train_ensemble_strategies(self, X: np.ndarray, y: np.ndarray):
        """Train ensemble strategies"""
        try:
            # Generate base model predictions for meta-learning
            base_predictions_list = []
            
            for i in range(min(len(X), 100)):  # Use subset for meta-training
                sample_X = X[i:i+1]
                sample_y = y[i]
                
                predictions = {}
                for model_name, model in self.base_models.items():
                    try:
                        pred = model.predict(sample_X)[0]
                        predictions[model_name] = pred
                    except:
                        continue
                
                if predictions:
                    base_predictions_list.append(predictions)
            
            # Train stacking strategy
            if "stacking" in self.config.ensemble_methods and base_predictions_list:
                stacking_strategy = self.strategies["stacking"]
                true_labels = y[:len(base_predictions_list)]
                stacking_strategy.train_meta_model(base_predictions_list, true_labels)
            
        except Exception as e:
            logger.warning(f"Ensemble strategy training failed: {e}")
    
    async def predict_ensemble(self, X: np.ndarray, 
                             ensemble_method: str = "voting") -> List[EnsemblePrediction]:
        """Make ensemble predictions"""
        try:
            start_time = time.time()
            
            predictions = []
            
            for sample in X:
                sample_X = sample.reshape(1, -1)
                
                # Get base model predictions
                base_predictions = {}
                base_confidences = {}
                prediction_futures = []
                
                if self.config.parallel_prediction:
                    # Parallel prediction
                    for model_name, model in self.base_models.items():
                        future = self.executor.submit(self._predict_single_model, model, sample_X, model_name)
                        prediction_futures.append((model_name, future))
                    
                    # Collect results
                    for model_name, future in prediction_futures:
                        try:
                            pred, conf = future.result(timeout=self.config.prediction_timeout_seconds)
                            base_predictions[model_name] = pred
                            base_confidences[model_name] = conf
                        except Exception as e:
                            logger.warning(f"Prediction failed for {model_name}: {e}")
                else:
                    # Sequential prediction
                    for model_name, model in self.base_models.items():
                        try:
                            pred, conf = self._predict_single_model(model, sample_X, model_name)
                            base_predictions[model_name] = pred
                            base_confidences[model_name] = conf
                        except Exception as e:
                            logger.warning(f"Prediction failed for {model_name}: {e}")
                
                if not base_predictions:
                    continue
                
                # Combine predictions using selected strategy
                if ensemble_method == "dynamic_selection":
                    final_pred, final_conf = await self._dynamic_selection_prediction(
                        base_predictions, base_confidences, sample_X
                    )
                elif ensemble_method == "meta_learning":
                    final_pred, final_conf = await self._meta_learning_prediction(
                        base_predictions, base_confidences, sample_X
                    )
                else:
                    # Use specified strategy
                    strategy = self.strategies.get(ensemble_method, self.strategies["voting"])
                    final_pred, final_conf = strategy.combine_predictions(
                        base_predictions, base_confidences
                    )
                
                # Create ensemble prediction
                ensemble_pred = EnsemblePrediction(
                    final_prediction=final_pred,
                    confidence=final_conf,
                    model_predictions=base_predictions,
                    model_confidences=base_confidences,
                    model_weights={model: 1.0 for model in base_predictions.keys()},
                    ensemble_method=ensemble_method,
                    prediction_time=time.time() - start_time,
                    metadata={
                        "num_base_models": len(base_predictions),
                        "prediction_agreement": len(set(base_predictions.values())) == 1
                    },
                    timestamp=datetime.utcnow()
                )
                
                predictions.append(ensemble_pred)
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Ensemble prediction failed: {e}")
            return []
    
    def _predict_single_model(self, model: BaseEstimator, X: np.ndarray, model_name: str) -> Tuple[Any, float]:
        """Predict with a single model (runs in thread)"""
        try:
            prediction = model.predict(X)[0]
            
            # Get confidence if available
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(X)[0]
                confidence = np.max(probabilities)
            elif hasattr(model, 'decision_function'):
                decision_scores = model.decision_function(X)[0]
                confidence = min(abs(decision_scores), 1.0)
            else:
                confidence = 0.7  # Default confidence
            
            return prediction, confidence
            
        except Exception as e:
            logger.warning(f"Single model prediction failed for {model_name}: {e}")
            return None, 0.0
    
    async def _dynamic_selection_prediction(self, base_predictions: Dict[str, Any], 
                                          base_confidences: Dict[str, float],
                                          sample_X: np.ndarray) -> Tuple[Any, float]:
        """Make prediction using dynamic model selection"""
        
        # Select best model based on recent performance
        best_models = self.dynamic_selector.select_best_models(3)
        
        if not best_models:
            # Fallback to voting
            voting_strategy = VotingStrategy("soft")
            return voting_strategy.combine_predictions(base_predictions, base_confidences)
        
        # Use only best models
        filtered_predictions = {model: base_predictions[model] for model in best_models if model in base_predictions}
        filtered_confidences = {model: base_confidences[model] for model in best_models if model in base_confidences}
        
        if not filtered_predictions:
            # Fallback to all models
            filtered_predictions = base_predictions
            filtered_confidences = base_confidences
        
        # Use voting on selected models
        voting_strategy = VotingStrategy("soft")
        return voting_strategy.combine_predictions(filtered_predictions, filtered_confidences)
    
    async def _meta_learning_prediction(self, base_predictions: Dict[str, Any], 
                                      base_confidences: Dict[str, float],
                                      sample_X: np.ndarray) -> Tuple[Any, float]:
        """Make prediction using meta-learning"""
        
        if not self.config.enable_meta_learning:
            # Fallback to voting
            voting_strategy = VotingStrategy("soft")
            return voting_strategy.combine_predictions(base_predictions, base_confidences)
        
        try:
            # Extract meta-features
            meta_features = self.meta_learner.extract_meta_features(
                base_predictions, base_confidences, sample_X
            )
            
            # Get meta-learner recommendation
            best_model, meta_confidence = self.meta_learner.predict_best_model(meta_features)
            
            # Use recommended model if available and confidence is high
            if best_model in base_predictions and meta_confidence > 0.7:
                return base_predictions[best_model], base_confidences.get(best_model, 0.5)
            else:
                # Fallback to voting
                voting_strategy = VotingStrategy("soft")
                return voting_strategy.combine_predictions(base_predictions, base_confidences)
                
        except Exception as e:
            logger.warning(f"Meta-learning prediction failed: {e}")
            # Fallback to voting
            voting_strategy = VotingStrategy("soft")
            return voting_strategy.combine_predictions(base_predictions, base_confidences)
    
    async def update_model_performance(self, model_name: str, prediction: Any, 
                                     actual: Any, confidence: float, prediction_time: float):
        """Update model performance tracking"""
        try:
            accuracy = 1.0 if prediction == actual else 0.0
            error_rate = 0.0 if prediction == actual else 1.0
            
            # Update dynamic selector
            self.dynamic_selector.update_performance(
                model_name, accuracy, prediction_time, confidence, error_rate
            )
            
            # Update ensemble performance history
            self.ensemble_performance_history.append({
                'model_name': model_name,
                'accuracy': accuracy,
                'prediction_time': prediction_time,
                'confidence': confidence,
                'error_rate': error_rate,
                'timestamp': datetime.utcnow()
            })
            
        except Exception as e:
            logger.warning(f"Failed to update performance for {model_name}: {e}")
    
    async def get_ensemble_status(self) -> Dict[str, Any]:
        """Get comprehensive ensemble system status"""
        
        # Model performance summary
        performance_summary = {}
        for model_name, tracker in self.dynamic_selector.performance_history.items():
            performance_summary[model_name] = {
                'average_performance': tracker.get_average_performance(),
                'total_predictions': tracker.total_predictions,
                'last_updated': tracker.last_updated.isoformat()
            }
        
        return {
            'config': asdict(self.config),
            'active_models': list(self.base_models.keys()),
            'ensemble_strategies': list(self.strategies.keys()),
            'performance_summary': performance_summary,
            'meta_learner_trained': self.meta_learner.is_trained,
            'recent_predictions': len(self.ensemble_performance_history),
            'rebalancing_active': self.rebalancing_active,
            'system_uptime': datetime.utcnow().isoformat()
        }
    
    async def optimize_ensemble_config(self, optimization_data: Dict[str, Any]) -> bool:
        """Optimize ensemble configuration based on performance data"""
        try:
            # Analyze performance trends
            if len(self.ensemble_performance_history) < 100:
                logger.warning("Insufficient data for ensemble optimization")
                return False
            
            # Get recent performance data
            recent_data = list(self.ensemble_performance_history)[-100:]
            
            # Calculate average metrics
            avg_accuracy = np.mean([d['accuracy'] for d in recent_data])
            avg_prediction_time = np.mean([d['prediction_time'] for d in recent_data])
            
            # Optimize based on performance
            if avg_accuracy < 0.8:
                # Low accuracy - try more models
                self.config.max_models_in_ensemble = min(
                    self.config.max_models_in_ensemble + 2, 15
                )
            elif avg_accuracy > 0.95 and avg_prediction_time > 1.0:
                # High accuracy but slow - reduce models
                self.config.max_models_in_ensemble = max(
                    self.config.max_models_in_ensemble - 1, 3
                )
            
            if avg_prediction_time > 2.0:
                # Slow predictions - enable more parallel processing
                self.config.parallel_prediction = True
                self.config.prediction_timeout_seconds = max(
                    self.config.prediction_timeout_seconds - 0.5, 1.0
                )
            
            logger.info("✅ Ensemble configuration optimized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ensemble optimization failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the ensemble system"""
        logger.info("🛑 Shutting down multi-model ensemble system...")
        
        self.rebalancing_active = False
        if self.rebalancing_thread:
            self.rebalancing_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        
        await self.feature_engineering.shutdown() if hasattr(self.feature_engineering, 'shutdown') else None
        await self.realtime_training.shutdown()
        
        logger.info("✅ Multi-model ensemble system shutdown complete")


# Export main classes
__all__ = [
    'MultiModelEnsembleSystem',
    'EnsembleConfig',
    'EnsemblePrediction',
    'VotingStrategy',
    'StackingStrategy',
    'MetaLearner',
    'DynamicModelSelector'
]