#!/usr/bin/env python3
"""
UPID CLI - Intelligent Model Selection Framework
Phase 5: Advanced ML Enhancement - Task 5.4
Enterprise-grade automated model selection with optimization and adaptive learning
"""

import logging
import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import itertools

from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.model_selection import (
    GridSearchCV, RandomizedSearchCV, cross_val_score, 
    StratifiedKFold, KFold, validation_curve
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, classification_report,
    confusion_matrix, roc_auc_score
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler

from ..core.metrics_collector import MetricsCollector
from ..core.resource_analyzer import ResourceAnalyzer
from .ensemble_system import MultiModelEnsembleSystem
from .advanced_feature_engineering import AdvancedFeatureEngineering

logger = logging.getLogger(__name__)


@dataclass
class ModelSelectionConfig:
    """Model selection configuration"""
    # Selection criteria
    primary_metric: str = "accuracy"
    secondary_metrics: List[str] = None
    optimization_direction: str = "maximize"  # maximize or minimize
    
    # Search strategy
    search_strategy: str = "optuna"  # optuna, grid_search, random_search, adaptive
    max_trials: int = 100
    optimization_timeout_minutes: int = 60
    cv_folds: int = 5
    
    # Model pool
    candidate_models: List[str] = None
    exclude_models: List[str] = None
    enable_neural_networks: bool = True
    enable_ensemble_models: bool = True
    
    # Performance thresholds
    min_accuracy_threshold: float = 0.7
    max_training_time_seconds: float = 300
    max_prediction_time_ms: float = 100
    min_samples_per_class: int = 10
    
    # Adaptive selection
    enable_adaptive_selection: bool = True
    adaptation_window_size: int = 1000
    performance_degradation_threshold: float = 0.05
    
    # Resource constraints
    max_memory_usage_mb: int = 2048
    max_cpu_cores: int = 4
    enable_early_stopping: bool = True
    
    def __post_init__(self):
        if self.secondary_metrics is None:
            self.secondary_metrics = ["precision", "recall", "f1"]
        if self.candidate_models is None:
            self.candidate_models = [
                "random_forest", "gradient_boosting", "logistic_regression",
                "svm", "neural_network", "naive_bayes", "knn", "decision_tree"
            ]
        if self.exclude_models is None:
            self.exclude_models = []


@dataclass
class ModelCandidate:
    """Model candidate with configuration"""
    model_name: str
    model_class: type
    hyperparameter_space: Dict[str, Any]
    default_params: Dict[str, Any]
    training_time_estimate: float
    memory_usage_estimate: float
    complexity_score: float
    suitable_for_small_data: bool
    suitable_for_large_data: bool


@dataclass
class ModelEvaluation:
    """Model evaluation results"""
    model_name: str
    model_params: Dict[str, Any]
    cv_scores: Dict[str, List[float]]
    mean_scores: Dict[str, float]
    std_scores: Dict[str, float]
    training_time: float
    prediction_time: float
    memory_usage: float
    model_complexity: float
    feature_importance: Optional[Dict[str, float]]
    validation_curve_data: Optional[Dict[str, Any]]
    timestamp: datetime
    
    def get_combined_score(self, weights: Dict[str, float] = None) -> float:
        """Calculate combined performance score"""
        if weights is None:
            weights = {"accuracy": 0.4, "precision": 0.2, "recall": 0.2, "f1": 0.2}
        
        combined_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in self.mean_scores:
                combined_score += self.mean_scores[metric] * weight
                total_weight += weight
        
        return combined_score / total_weight if total_weight > 0 else 0.0


@dataclass
class SelectionResult:
    """Model selection result"""
    best_model_name: str
    best_model_params: Dict[str, Any]
    best_model_evaluation: ModelEvaluation
    all_evaluations: List[ModelEvaluation]
    selection_strategy: str
    selection_time: float
    recommendations: List[str]
    confidence_score: float
    timestamp: datetime


class HyperparameterOptimizer:
    """Advanced hyperparameter optimization"""
    
    def __init__(self, config: ModelSelectionConfig):
        self.config = config
        self.study_cache: Dict[str, optuna.Study] = {}
        
    def get_hyperparameter_space(self, model_name: str) -> Dict[str, Any]:
        """Get hyperparameter search space for model"""
        spaces = {
            "random_forest": {
                "n_estimators": [50, 100, 200, 300],
                "max_depth": [3, 5, 10, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2", None]
            },
            "gradient_boosting": {
                "n_estimators": [50, 100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "subsample": [0.8, 0.9, 1.0],
                "max_features": ["sqrt", "log2", None]
            },
            "logistic_regression": {
                "C": [0.01, 0.1, 1.0, 10.0, 100.0],
                "penalty": ["l1", "l2", "elasticnet"],
                "solver": ["liblinear", "saga"],
                "max_iter": [1000, 2000, 5000]
            },
            "svm": {
                "C": [0.1, 1.0, 10.0, 100.0],
                "kernel": ["rbf", "poly", "sigmoid"],
                "gamma": ["scale", "auto", 0.01, 0.1, 1.0],
                "degree": [2, 3, 4]  # for poly kernel
            },
            "neural_network": {
                "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50), (100, 100)],
                "activation": ["relu", "tanh", "logistic"],
                "solver": ["adam", "lbfgs"],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate": ["constant", "adaptive"]
            },
            "knn": {
                "n_neighbors": [3, 5, 7, 9, 11],
                "weights": ["uniform", "distance"],
                "algorithm": ["auto", "ball_tree", "kd_tree"],
                "metric": ["euclidean", "manhattan", "minkowski"]
            },
            "decision_tree": {
                "max_depth": [3, 5, 10, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "criterion": ["gini", "entropy"],
                "splitter": ["best", "random"]
            }
        }
        
        return spaces.get(model_name, {})
    
    def optimize_with_optuna(self, model_class: type, X: np.ndarray, y: np.ndarray,
                           model_name: str, cv_folds: int = 5) -> Tuple[Dict[str, Any], float]:
        """Optimize hyperparameters using Optuna"""
        
        def objective(trial):
            # Sample hyperparameters
            params = {}
            space = self.get_hyperparameter_space(model_name)
            
            for param_name, param_values in space.items():
                if isinstance(param_values, list):
                    if all(isinstance(v, (int, float)) for v in param_values if v is not None):
                        # Numerical parameter
                        numeric_values = [v for v in param_values if v is not None]
                        if numeric_values:
                            if all(isinstance(v, int) for v in numeric_values):
                                params[param_name] = trial.suggest_int(
                                    param_name, min(numeric_values), max(numeric_values)
                                )
                            else:
                                params[param_name] = trial.suggest_float(
                                    param_name, min(numeric_values), max(numeric_values)
                                )
                    else:
                        # Categorical parameter
                        params[param_name] = trial.suggest_categorical(param_name, param_values)
            
            try:
                # Create and evaluate model
                model = model_class(**params)
                
                # Cross-validation
                cv_scores = cross_val_score(
                    model, X, y, cv=cv_folds, 
                    scoring=self.config.primary_metric.replace('accuracy', 'accuracy'),
                    n_jobs=-1
                )
                
                return np.mean(cv_scores)
                
            except Exception as e:
                logger.warning(f"Trial failed for {model_name}: {e}")
                return 0.0
        
        # Create or get cached study
        study_key = f"{model_name}_{len(X)}_{len(y)}"
        if study_key not in self.study_cache:
            direction = "maximize" if self.config.optimization_direction == "maximize" else "minimize"
            
            self.study_cache[study_key] = optuna.create_study(
                direction=direction,
                sampler=TPESampler(),
                pruner=MedianPruner() if self.config.enable_early_stopping else None
            )
        
        study = self.study_cache[study_key]
        
        # Optimize
        study.optimize(
            objective, 
            n_trials=self.config.max_trials,
            timeout=self.config.optimization_timeout_minutes * 60
        )
        
        best_params = study.best_params
        best_score = study.best_value
        
        return best_params, best_score
    
    def optimize_with_grid_search(self, model_class: type, X: np.ndarray, y: np.ndarray,
                                model_name: str, cv_folds: int = 5) -> Tuple[Dict[str, Any], float]:
        """Optimize hyperparameters using GridSearchCV"""
        
        space = self.get_hyperparameter_space(model_name)
        
        # Limit search space for grid search
        limited_space = {}
        for param, values in space.items():
            if isinstance(values, list):
                # Take subset to make grid search feasible
                limited_space[param] = values[:min(len(values), 3)]
        
        if not limited_space:
            return {}, 0.0
        
        try:
            model = model_class()
            
            grid_search = GridSearchCV(
                model, limited_space, 
                cv=cv_folds,
                scoring=self.config.primary_metric.replace('accuracy', 'accuracy'),
                n_jobs=-1,
                timeout=self.config.optimization_timeout_minutes * 60
            )
            
            grid_search.fit(X, y)
            
            return grid_search.best_params_, grid_search.best_score_
            
        except Exception as e:
            logger.warning(f"Grid search failed for {model_name}: {e}")
            return {}, 0.0


class ModelRegistry:
    """Registry of available models and their configurations"""
    
    def __init__(self):
        self.candidates: Dict[str, ModelCandidate] = {}
        self._initialize_candidates()
    
    def _initialize_candidates(self):
        """Initialize model candidates"""
        
        self.candidates = {
            "random_forest": ModelCandidate(
                model_name="random_forest",
                model_class=RandomForestClassifier,
                hyperparameter_space={},
                default_params={"n_estimators": 100, "random_state": 42},
                training_time_estimate=10.0,
                memory_usage_estimate=500.0,
                complexity_score=0.7,
                suitable_for_small_data=True,
                suitable_for_large_data=True
            ),
            "gradient_boosting": ModelCandidate(
                model_name="gradient_boosting",
                model_class=GradientBoostingClassifier,
                hyperparameter_space={},
                default_params={"n_estimators": 100, "random_state": 42},
                training_time_estimate=20.0,
                memory_usage_estimate=600.0,
                complexity_score=0.8,
                suitable_for_small_data=True,
                suitable_for_large_data=True
            ),
            "logistic_regression": ModelCandidate(
                model_name="logistic_regression",
                model_class=LogisticRegression,
                hyperparameter_space={},
                default_params={"random_state": 42, "max_iter": 1000},
                training_time_estimate=2.0,
                memory_usage_estimate=100.0,
                complexity_score=0.3,
                suitable_for_small_data=True,
                suitable_for_large_data=True
            ),
            "svm": ModelCandidate(
                model_name="svm",
                model_class=SVC,
                hyperparameter_space={},
                default_params={"probability": True, "random_state": 42},
                training_time_estimate=15.0,
                memory_usage_estimate=800.0,
                complexity_score=0.9,
                suitable_for_small_data=True,
                suitable_for_large_data=False
            ),
            "neural_network": ModelCandidate(
                model_name="neural_network",
                model_class=MLPClassifier,
                hyperparameter_space={},
                default_params={"random_state": 42, "max_iter": 500},
                training_time_estimate=30.0,
                memory_usage_estimate=1000.0,
                complexity_score=0.95,
                suitable_for_small_data=False,
                suitable_for_large_data=True
            ),
            "naive_bayes": ModelCandidate(
                model_name="naive_bayes",
                model_class=GaussianNB,
                hyperparameter_space={},
                default_params={},
                training_time_estimate=1.0,
                memory_usage_estimate=50.0,
                complexity_score=0.2,
                suitable_for_small_data=True,
                suitable_for_large_data=True
            ),
            "knn": ModelCandidate(
                model_name="knn",
                model_class=KNeighborsClassifier,
                hyperparameter_space={},
                default_params={"n_neighbors": 5},
                training_time_estimate=1.0,
                memory_usage_estimate=200.0,
                complexity_score=0.4,
                suitable_for_small_data=True,
                suitable_for_large_data=False
            ),
            "decision_tree": ModelCandidate(
                model_name="decision_tree",
                model_class=DecisionTreeClassifier,
                hyperparameter_space={},
                default_params={"random_state": 42},
                training_time_estimate=5.0,
                memory_usage_estimate=300.0,
                complexity_score=0.6,
                suitable_for_small_data=True,
                suitable_for_large_data=True
            )
        }
    
    def get_suitable_candidates(self, data_size: int, 
                              resource_constraints: Dict[str, float]) -> List[ModelCandidate]:
        """Get suitable model candidates based on data size and constraints"""
        
        suitable_candidates = []
        is_small_data = data_size < 1000
        is_large_data = data_size > 10000
        
        for candidate in self.candidates.values():
            # Check data size suitability
            if is_small_data and not candidate.suitable_for_small_data:
                continue
            if is_large_data and not candidate.suitable_for_large_data:
                continue
            
            # Check resource constraints
            max_memory = resource_constraints.get("max_memory_mb", float('inf'))
            max_time = resource_constraints.get("max_training_time", float('inf'))
            
            if candidate.memory_usage_estimate > max_memory:
                continue
            if candidate.training_time_estimate > max_time:
                continue
            
            suitable_candidates.append(candidate)
        
        return suitable_candidates
    
    def get_candidate(self, model_name: str) -> Optional[ModelCandidate]:
        """Get specific model candidate"""
        return self.candidates.get(model_name)


class PerformancePredictor:
    """Predicts model performance before training"""
    
    def __init__(self):
        self.performance_history: Dict[str, List[Dict]] = defaultdict(list)
    
    def predict_performance(self, model_name: str, data_characteristics: Dict[str, Any]) -> Dict[str, float]:
        """Predict model performance based on data characteristics"""
        
        # Default predictions
        predictions = {
            "accuracy": 0.8,
            "training_time": 10.0,
            "memory_usage": 500.0,
            "confidence": 0.5
        }
        
        # Get historical performance
        if model_name in self.performance_history and self.performance_history[model_name]:
            recent_performance = self.performance_history[model_name][-10:]
            
            predictions["accuracy"] = np.mean([p["accuracy"] for p in recent_performance])
            predictions["training_time"] = np.mean([p["training_time"] for p in recent_performance])
            predictions["memory_usage"] = np.mean([p["memory_usage"] for p in recent_performance])
            predictions["confidence"] = min(len(recent_performance) / 10, 1.0)
        
        # Adjust based on data characteristics
        n_samples = data_characteristics.get("n_samples", 1000)
        n_features = data_characteristics.get("n_features", 10)
        n_classes = data_characteristics.get("n_classes", 2)
        
        # Adjust training time based on data size
        size_factor = np.log10(max(n_samples, 1)) / 3.0  # Normalized log scale
        predictions["training_time"] *= size_factor
        
        # Adjust memory usage based on features
        feature_factor = np.sqrt(max(n_features, 1)) / 10.0
        predictions["memory_usage"] *= feature_factor
        
        # Adjust accuracy based on complexity
        if n_classes > 2:
            predictions["accuracy"] *= 0.9  # Multi-class is typically harder
        
        return predictions
    
    def update_performance_history(self, model_name: str, actual_performance: Dict[str, Any]):
        """Update performance history with actual results"""
        self.performance_history[model_name].append(actual_performance)
        
        # Keep only recent history
        if len(self.performance_history[model_name]) > 100:
            self.performance_history[model_name] = self.performance_history[model_name][-100:]


class IntelligentModelSelection:
    """
    Intelligent model selection framework with advanced optimization
    
    Features:
    - Automated model selection based on data characteristics
    - Advanced hyperparameter optimization (Optuna, Grid Search)
    - Performance prediction and resource-aware selection
    - Adaptive selection based on historical performance
    - Multi-objective optimization
    - Real-time model switching
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.config = ModelSelectionConfig()
        
        # Components
        self.model_registry = ModelRegistry()
        self.hyperparameter_optimizer = HyperparameterOptimizer(self.config)
        self.performance_predictor = PerformancePredictor()
        
        # Selection history
        self.selection_history: List[SelectionResult] = []
        self.active_models: Dict[str, BaseEstimator] = {}
        self.performance_tracking: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_cpu_cores)
        
        logger.info("🔧 Initializing intelligent model selection framework")
    
    async def select_best_model(self, X: np.ndarray, y: np.ndarray, 
                              task_type: str = "classification") -> SelectionResult:
        """Select best model using intelligent selection"""
        try:
            start_time = time.time()
            logger.info(f"🎯 Starting intelligent model selection for {task_type} task...")
            
            # Analyze data characteristics
            data_characteristics = self._analyze_data_characteristics(X, y)
            logger.info(f"📊 Data characteristics: {data_characteristics}")
            
            # Get suitable model candidates
            resource_constraints = {
                "max_memory_mb": self.config.max_memory_usage_mb,
                "max_training_time": self.config.max_training_time_seconds
            }
            
            candidates = self.model_registry.get_suitable_candidates(
                len(X), resource_constraints
            )
            
            # Filter candidates based on configuration
            filtered_candidates = [
                c for c in candidates 
                if c.model_name in self.config.candidate_models
                and c.model_name not in self.config.exclude_models
            ]
            
            if not filtered_candidates:
                logger.warning("No suitable model candidates found")
                return SelectionResult(
                    best_model_name="random_forest",
                    best_model_params={},
                    best_model_evaluation=None,
                    all_evaluations=[],
                    selection_strategy="fallback",
                    selection_time=time.time() - start_time,
                    recommendations=["Use default Random Forest"],
                    confidence_score=0.3,
                    timestamp=datetime.utcnow()
                )
            
            logger.info(f"🔍 Evaluating {len(filtered_candidates)} model candidates...")
            
            # Evaluate models in parallel
            evaluation_futures = []
            for candidate in filtered_candidates:
                future = self.executor.submit(
                    self._evaluate_model_candidate, 
                    candidate, X, y, data_characteristics
                )
                evaluation_futures.append((candidate.model_name, future))
            
            # Collect evaluation results
            evaluations = []
            for model_name, future in evaluation_futures:
                try:
                    evaluation = future.result(timeout=self.config.max_training_time_seconds + 60)
                    if evaluation:
                        evaluations.append(evaluation)
                        logger.info(f"✅ {model_name} evaluated: {evaluation.mean_scores.get('accuracy', 0):.3f}")
                except Exception as e:
                    logger.warning(f"❌ Evaluation failed for {model_name}: {e}")
            
            if not evaluations:
                logger.error("All model evaluations failed")
                return SelectionResult(
                    best_model_name="random_forest",
                    best_model_params={},
                    best_model_evaluation=None,
                    all_evaluations=[],
                    selection_strategy="error_fallback",
                    selection_time=time.time() - start_time,
                    recommendations=["All evaluations failed, using fallback"],
                    confidence_score=0.1,
                    timestamp=datetime.utcnow()
                )
            
            # Select best model using multi-objective optimization
            best_evaluation = self._select_best_evaluation(evaluations, data_characteristics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(evaluations, best_evaluation)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(evaluations, best_evaluation)
            
            selection_result = SelectionResult(
                best_model_name=best_evaluation.model_name,
                best_model_params=best_evaluation.model_params,
                best_model_evaluation=best_evaluation,
                all_evaluations=evaluations,
                selection_strategy=self.config.search_strategy,
                selection_time=time.time() - start_time,
                recommendations=recommendations,
                confidence_score=confidence_score,
                timestamp=datetime.utcnow()
            )
            
            # Update selection history
            self.selection_history.append(selection_result)
            
            logger.info(f"🏆 Best model selected: {best_evaluation.model_name} "
                       f"(accuracy: {best_evaluation.mean_scores.get('accuracy', 0):.3f})")
            
            return selection_result
            
        except Exception as e:
            logger.error(f"❌ Model selection failed: {e}")
            raise
    
    def _analyze_data_characteristics(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Analyze data characteristics for model selection"""
        
        characteristics = {
            "n_samples": len(X),
            "n_features": X.shape[1] if len(X.shape) > 1 else 1,
            "n_classes": len(np.unique(y)),
            "class_balance": self._calculate_class_balance(y),
            "feature_correlations": self._calculate_feature_correlations(X),
            "data_sparsity": self._calculate_sparsity(X),
            "outlier_ratio": self._calculate_outlier_ratio(X),
            "noise_level": self._estimate_noise_level(X, y),
            "linearity_score": self._estimate_linearity(X, y),
            "complexity_score": self._estimate_complexity(X, y)
        }
        
        return characteristics
    
    def _calculate_class_balance(self, y: np.ndarray) -> float:
        """Calculate class balance score (0 = imbalanced, 1 = balanced)"""
        unique, counts = np.unique(y, return_counts=True)
        if len(unique) <= 1:
            return 1.0
        
        min_count = np.min(counts)
        max_count = np.max(counts)
        return min_count / max_count if max_count > 0 else 0.0
    
    def _calculate_feature_correlations(self, X: np.ndarray) -> float:
        """Calculate average feature correlation"""
        if X.shape[1] < 2:
            return 0.0
        
        try:
            corr_matrix = np.corrcoef(X.T)
            # Get upper triangle (excluding diagonal)
            upper_triangle = corr_matrix[np.triu_indices_from(corr_matrix, k=1)]
            return np.mean(np.abs(upper_triangle))
        except:
            return 0.0
    
    def _calculate_sparsity(self, X: np.ndarray) -> float:
        """Calculate data sparsity ratio"""
        if X.size == 0:
            return 0.0
        
        zero_count = np.count_nonzero(X == 0)
        return zero_count / X.size
    
    def _calculate_outlier_ratio(self, X: np.ndarray) -> float:
        """Calculate outlier ratio using IQR method"""
        if X.size == 0:
            return 0.0
        
        try:
            Q1 = np.percentile(X, 25, axis=0)
            Q3 = np.percentile(X, 75, axis=0)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (X < lower_bound) | (X > upper_bound)
            return np.sum(outliers) / X.size
        except:
            return 0.0
    
    def _estimate_noise_level(self, X: np.ndarray, y: np.ndarray) -> float:
        """Estimate noise level in the data"""
        try:
            from sklearn.neighbors import KNeighborsClassifier
            
            if len(X) < 10:
                return 0.5
            
            # Use k-NN to estimate noise
            knn = KNeighborsClassifier(n_neighbors=min(5, len(X)//2))
            scores = cross_val_score(knn, X, y, cv=min(3, len(X)//5))
            
            # Higher accuracy = lower noise
            return 1.0 - np.mean(scores)
        except:
            return 0.5
    
    def _estimate_linearity(self, X: np.ndarray, y: np.ndarray) -> float:
        """Estimate linearity of the relationship"""
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.ensemble import RandomForestClassifier
            
            if len(X) < 10:
                return 0.5
            
            # Compare linear vs non-linear performance
            linear_model = LogisticRegression(random_state=42, max_iter=1000)
            nonlinear_model = RandomForestClassifier(n_estimators=50, random_state=42)
            
            linear_scores = cross_val_score(linear_model, X, y, cv=min(3, len(X)//5))
            nonlinear_scores = cross_val_score(nonlinear_model, X, y, cv=min(3, len(X)//5))
            
            linear_acc = np.mean(linear_scores)
            nonlinear_acc = np.mean(nonlinear_scores)
            
            # If linear performs well relative to non-linear, data is more linear
            if nonlinear_acc > 0:
                return linear_acc / nonlinear_acc
            else:
                return 0.5
        except:
            return 0.5
    
    def _estimate_complexity(self, X: np.ndarray, y: np.ndarray) -> float:
        """Estimate problem complexity"""
        characteristics = {
            "size_complexity": min(len(X) / 10000, 1.0),
            "feature_complexity": min(X.shape[1] / 100, 1.0) if len(X.shape) > 1 else 0.1,
            "class_complexity": min(len(np.unique(y)) / 10, 1.0)
        }
        
        return np.mean(list(characteristics.values()))
    
    def _evaluate_model_candidate(self, candidate: ModelCandidate, X: np.ndarray, y: np.ndarray,
                                data_characteristics: Dict[str, Any]) -> Optional[ModelEvaluation]:
        """Evaluate a single model candidate"""
        
        try:
            start_time = time.time()
            
            # Optimize hyperparameters
            if self.config.search_strategy == "optuna":
                best_params, best_score = self.hyperparameter_optimizer.optimize_with_optuna(
                    candidate.model_class, X, y, candidate.model_name, self.config.cv_folds
                )
            elif self.config.search_strategy == "grid_search":
                best_params, best_score = self.hyperparameter_optimizer.optimize_with_grid_search(
                    candidate.model_class, X, y, candidate.model_name, self.config.cv_folds
                )
            else:
                # Use default parameters
                best_params = candidate.default_params
                best_score = 0.0
            
            # Create model with best parameters
            model_params = {**candidate.default_params, **best_params}
            model = candidate.model_class(**model_params)
            
            # Perform cross-validation with multiple metrics
            cv_scores = {}
            metrics = [self.config.primary_metric] + self.config.secondary_metrics
            
            for metric in metrics:
                if metric == "accuracy":
                    scores = cross_val_score(model, X, y, cv=self.config.cv_folds, scoring="accuracy")
                elif metric == "precision":
                    scores = cross_val_score(model, X, y, cv=self.config.cv_folds, scoring="precision_weighted")
                elif metric == "recall":
                    scores = cross_val_score(model, X, y, cv=self.config.cv_folds, scoring="recall_weighted")
                elif metric == "f1":
                    scores = cross_val_score(model, X, y, cv=self.config.cv_folds, scoring="f1_weighted")
                else:
                    scores = cross_val_score(model, X, y, cv=self.config.cv_folds)
                
                cv_scores[metric] = scores.tolist()
            
            # Calculate mean and std scores
            mean_scores = {metric: np.mean(scores) for metric, scores in cv_scores.items()}
            std_scores = {metric: np.std(scores) for metric, scores in cv_scores.items()}
            
            # Measure training and prediction time
            train_start = time.time()
            model.fit(X, y)
            training_time = time.time() - train_start
            
            pred_start = time.time()
            _ = model.predict(X[:min(100, len(X))])  # Sample prediction
            prediction_time = (time.time() - pred_start) * 1000  # Convert to ms
            
            # Estimate memory usage (simplified)
            memory_usage = candidate.memory_usage_estimate
            
            # Get feature importance if available
            feature_importance = None
            if hasattr(model, 'feature_importances_'):
                feature_importance = {
                    f"feature_{i}": importance 
                    for i, importance in enumerate(model.feature_importances_)
                }
            elif hasattr(model, 'coef_'):
                feature_importance = {
                    f"feature_{i}": abs(coef) 
                    for i, coef in enumerate(model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_)
                }
            
            evaluation = ModelEvaluation(
                model_name=candidate.model_name,
                model_params=model_params,
                cv_scores=cv_scores,
                mean_scores=mean_scores,
                std_scores=std_scores,
                training_time=training_time,
                prediction_time=prediction_time,
                memory_usage=memory_usage,
                model_complexity=candidate.complexity_score,
                feature_importance=feature_importance,
                validation_curve_data=None,  # Could add later
                timestamp=datetime.utcnow()
            )
            
            # Update performance predictor
            self.performance_predictor.update_performance_history(
                candidate.model_name, {
                    "accuracy": mean_scores.get("accuracy", 0),
                    "training_time": training_time,
                    "memory_usage": memory_usage
                }
            )
            
            return evaluation
            
        except Exception as e:
            logger.warning(f"Model evaluation failed for {candidate.model_name}: {e}")
            return None
    
    def _select_best_evaluation(self, evaluations: List[ModelEvaluation], 
                              data_characteristics: Dict[str, Any]) -> ModelEvaluation:
        """Select best model using multi-objective optimization"""
        
        if len(evaluations) == 1:
            return evaluations[0]
        
        # Define weights for different criteria
        weights = {
            "accuracy": 0.4,
            "speed": 0.2,
            "memory": 0.2,
            "stability": 0.2
        }
        
        # Adjust weights based on data characteristics
        if data_characteristics["n_samples"] > 10000:
            weights["speed"] += 0.1  # Prioritize speed for large datasets
            weights["accuracy"] -= 0.1
        
        if data_characteristics["complexity_score"] > 0.7:
            weights["accuracy"] += 0.1  # Prioritize accuracy for complex problems
            weights["memory"] -= 0.1
        
        # Calculate scores for each evaluation
        best_evaluation = None
        best_score = -float('inf')
        
        for evaluation in evaluations:
            # Performance score
            accuracy_score = evaluation.mean_scores.get(self.config.primary_metric, 0)
            
            # Speed score (inverse of time, normalized)
            max_time = max(e.training_time + e.prediction_time for e in evaluations)
            speed_score = 1.0 - ((evaluation.training_time + evaluation.prediction_time) / max_time)
            
            # Memory score (inverse of usage, normalized)
            max_memory = max(e.memory_usage for e in evaluations)
            memory_score = 1.0 - (evaluation.memory_usage / max_memory)
            
            # Stability score (inverse of std deviation)
            std_score = 1.0 - evaluation.std_scores.get(self.config.primary_metric, 0)
            
            # Combined score
            combined_score = (
                accuracy_score * weights["accuracy"] +
                speed_score * weights["speed"] +
                memory_score * weights["memory"] +
                std_score * weights["stability"]
            )
            
            if combined_score > best_score:
                best_score = combined_score
                best_evaluation = evaluation
        
        return best_evaluation
    
    def _generate_recommendations(self, evaluations: List[ModelEvaluation], 
                                best_evaluation: ModelEvaluation) -> List[str]:
        """Generate recommendations based on evaluation results"""
        
        recommendations = []
        
        # Performance recommendations
        if best_evaluation.mean_scores.get("accuracy", 0) < self.config.min_accuracy_threshold:
            recommendations.append(
                f"Consider feature engineering or more data - accuracy {best_evaluation.mean_scores.get('accuracy', 0):.3f} "
                f"below threshold {self.config.min_accuracy_threshold}"
            )
        
        # Speed recommendations
        if best_evaluation.training_time > self.config.max_training_time_seconds:
            recommendations.append(
                f"Training time {best_evaluation.training_time:.1f}s exceeds limit - "
                "consider simpler models or data sampling"
            )
        
        if best_evaluation.prediction_time > self.config.max_prediction_time_ms:
            recommendations.append(
                f"Prediction time {best_evaluation.prediction_time:.1f}ms exceeds limit - "
                "consider model optimization"
            )
        
        # Alternative model recommendations
        sorted_evals = sorted(evaluations, 
                            key=lambda e: e.mean_scores.get(self.config.primary_metric, 0), 
                            reverse=True)
        
        if len(sorted_evals) > 1:
            second_best = sorted_evals[1]
            perf_diff = (best_evaluation.mean_scores.get(self.config.primary_metric, 0) - 
                        second_best.mean_scores.get(self.config.primary_metric, 0))
            
            if perf_diff < 0.02:  # Very close performance
                if second_best.training_time < best_evaluation.training_time * 0.8:
                    recommendations.append(
                        f"Consider {second_best.model_name} for faster training with similar accuracy"
                    )
        
        # Data-specific recommendations
        if len(evaluations) > 0:
            avg_accuracy = np.mean([e.mean_scores.get("accuracy", 0) for e in evaluations])
            if avg_accuracy < 0.7:
                recommendations.append("Low overall performance - consider data quality assessment")
        
        return recommendations
    
    def _calculate_confidence_score(self, evaluations: List[ModelEvaluation], 
                                  best_evaluation: ModelEvaluation) -> float:
        """Calculate confidence in the selection"""
        
        if len(evaluations) <= 1:
            return 0.5
        
        # Factors affecting confidence
        factors = []
        
        # Performance gap between best and second best
        sorted_evals = sorted(evaluations, 
                            key=lambda e: e.mean_scores.get(self.config.primary_metric, 0), 
                            reverse=True)
        
        if len(sorted_evals) >= 2:
            performance_gap = (sorted_evals[0].mean_scores.get(self.config.primary_metric, 0) - 
                             sorted_evals[1].mean_scores.get(self.config.primary_metric, 0))
            factors.append(min(performance_gap * 10, 1.0))  # Scale to [0, 1]
        
        # Stability (low standard deviation)
        std_score = 1.0 - best_evaluation.std_scores.get(self.config.primary_metric, 0)
        factors.append(max(std_score, 0.0))
        
        # Number of models evaluated
        diversity_score = min(len(evaluations) / 5, 1.0)
        factors.append(diversity_score)
        
        # Performance above threshold
        performance_score = best_evaluation.mean_scores.get(self.config.primary_metric, 0)
        threshold_score = min(performance_score / self.config.min_accuracy_threshold, 1.0)
        factors.append(threshold_score)
        
        return np.mean(factors)
    
    async def adaptive_model_switching(self, current_model_name: str, 
                                     recent_performance: List[float]) -> Optional[str]:
        """Adaptively switch models based on performance degradation"""
        
        if not self.config.enable_adaptive_selection or len(recent_performance) < 10:
            return None
        
        # Calculate performance trend
        recent_avg = np.mean(recent_performance[-10:])
        older_avg = np.mean(recent_performance[-20:-10]) if len(recent_performance) >= 20 else recent_avg
        
        performance_degradation = older_avg - recent_avg
        
        if performance_degradation > self.config.performance_degradation_threshold:
            logger.info(f"Performance degradation detected: {performance_degradation:.3f}")
            
            # Find alternative model from history
            for result in reversed(self.selection_history):
                if result.best_model_name != current_model_name:
                    alt_evaluation = result.best_model_evaluation
                    if (alt_evaluation and 
                        alt_evaluation.mean_scores.get(self.config.primary_metric, 0) > recent_avg):
                        
                        logger.info(f"Switching to {result.best_model_name} based on historical performance")
                        return result.best_model_name
            
        return None
    
    async def get_selection_summary(self) -> Dict[str, Any]:
        """Get comprehensive selection framework summary"""
        
        # Recent selection statistics
        recent_selections = self.selection_history[-10:] if self.selection_history else []
        
        model_usage = defaultdict(int)
        avg_selection_time = 0.0
        avg_confidence = 0.0
        
        for result in recent_selections:
            model_usage[result.best_model_name] += 1
            avg_selection_time += result.selection_time
            avg_confidence += result.confidence_score
        
        if recent_selections:
            avg_selection_time /= len(recent_selections)
            avg_confidence /= len(recent_selections)
        
        return {
            "config": asdict(self.config),
            "total_selections": len(self.selection_history),
            "recent_model_usage": dict(model_usage),
            "average_selection_time": avg_selection_time,
            "average_confidence": avg_confidence,
            "available_models": list(self.model_registry.candidates.keys()),
            "performance_predictor_data": {
                model: len(history) for model, history in self.performance_predictor.performance_history.items()
            },
            "last_selection": asdict(self.selection_history[-1]) if self.selection_history else None
        }
    
    async def shutdown(self):
        """Shutdown the selection framework"""
        logger.info("🛑 Shutting down intelligent model selection framework...")
        
        self.executor.shutdown(wait=True)
        
        logger.info("✅ Intelligent model selection framework shutdown complete")


# Export main classes
__all__ = [
    'IntelligentModelSelection',
    'ModelSelectionConfig',
    'SelectionResult',
    'ModelEvaluation',
    'ModelCandidate',
    'HyperparameterOptimizer',
    'ModelRegistry',
    'PerformancePredictor'
]