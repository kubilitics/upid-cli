#!/usr/bin/env python3
"""
UPID CLI - Advanced Feature Engineering System
Phase 5: Advanced ML Enhancement - Task 5.2
Enterprise-grade feature engineering with automated feature discovery and selection
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
from collections import defaultdict, Counter
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, RFE
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PolynomialFeatures
from sklearn.decomposition import PCA, FastICA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mutual_info_score
import scipy.stats as stats

from ..core.metrics_collector import MetricsCollector, PodMetrics, ClusterMetrics, NodeMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from .pipeline import MLFeatures

logger = logging.getLogger(__name__)


@dataclass
class FeatureImportance:
    """Feature importance metrics"""
    feature_name: str
    importance_score: float
    importance_type: str  # mutual_info, correlation, random_forest, statistical
    rank: int
    p_value: Optional[float]
    selected: bool
    timestamp: datetime


@dataclass
class FeatureEngineringConfig:
    """Advanced feature engineering configuration"""
    # Feature selection
    enable_automated_selection: bool = True
    max_features: int = 100
    selection_methods: List[str] = None
    importance_threshold: float = 0.01
    
    # Feature generation
    enable_polynomial_features: bool = True
    polynomial_degree: int = 2
    enable_interaction_features: bool = True
    enable_temporal_features: bool = True
    enable_statistical_features: bool = True
    
    # Dimensionality reduction
    enable_pca: bool = True
    pca_variance_threshold: float = 0.95
    enable_ica: bool = False
    
    # Feature scaling
    scaling_method: str = "standard"  # standard, minmax, robust
    
    # Advanced features
    enable_domain_specific: bool = True
    enable_anomaly_features: bool = True
    enable_trend_features: bool = True
    lookback_window_hours: int = 24
    
    def __post_init__(self):
        if self.selection_methods is None:
            self.selection_methods = ["mutual_info", "random_forest", "statistical"]


@dataclass
class TimeSeries:
    """Time series data structure"""
    timestamps: np.ndarray
    values: np.ndarray
    feature_name: str
    
    def get_trend(self) -> float:
        """Calculate trend using linear regression slope"""
        if len(self.values) < 2:
            return 0.0
        
        x = np.arange(len(self.values))
        slope, _, _, _, _ = stats.linregress(x, self.values)
        return slope
    
    def get_volatility(self) -> float:
        """Calculate volatility as coefficient of variation"""
        if len(self.values) < 2:
            return 0.0
        
        mean_val = np.mean(self.values)
        if mean_val == 0:
            return 0.0
        
        return np.std(self.values) / mean_val
    
    def get_seasonal_components(self, period: int = 24) -> Dict[str, float]:
        """Extract seasonal components"""
        if len(self.values) < period * 2:
            return {"trend": 0.0, "seasonal_strength": 0.0}
        
        # Simple seasonal decomposition
        seasonal_pattern = []
        for i in range(period):
            pattern_values = self.values[i::period]
            if len(pattern_values) > 0:
                seasonal_pattern.append(np.mean(pattern_values))
        
        seasonal_strength = np.std(seasonal_pattern) if len(seasonal_pattern) > 1 else 0.0
        
        return {
            "trend": self.get_trend(),
            "seasonal_strength": seasonal_strength
        }


class KubernetesFeatureExtractor:
    """Extracts Kubernetes-specific features"""
    
    def __init__(self):
        self.pod_patterns = {
            'web': ['nginx', 'apache', 'frontend', 'web'],
            'database': ['mysql', 'postgres', 'mongo', 'redis'],
            'analytics': ['spark', 'kafka', 'elasticsearch', 'kibana'],
            'ci_cd': ['jenkins', 'gitlab', 'drone', 'tekton'],
            'monitoring': ['prometheus', 'grafana', 'jaeger', 'zipkin']
        }
    
    def extract_workload_features(self, pod_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workload-specific features"""
        features = {}
        
        # Workload type classification
        pod_name = pod_data.get('name', '').lower()
        workload_category = 'unknown'
        
        for category, patterns in self.pod_patterns.items():
            if any(pattern in pod_name for pattern in patterns):
                workload_category = category
                break
        
        features['workload_category'] = workload_category
        
        # Resource efficiency metrics
        cpu_request = pod_data.get('cpu_request', 0)
        cpu_usage = pod_data.get('cpu_usage', 0)
        memory_request = pod_data.get('memory_request', 0)
        memory_usage = pod_data.get('memory_usage', 0)
        
        # CPU efficiency
        features['cpu_efficiency'] = (cpu_usage / cpu_request) if cpu_request > 0 else 0
        features['memory_efficiency'] = (memory_usage / memory_request) if memory_request > 0 else 0
        
        # Over/under provisioning indicators
        features['cpu_overprovisioned'] = 1 if cpu_request > cpu_usage * 2 else 0
        features['memory_overprovisioned'] = 1 if memory_request > memory_usage * 2 else 0
        features['cpu_underprovisioned'] = 1 if cpu_usage > cpu_request * 0.9 else 0
        features['memory_underprovisioned'] = 1 if memory_usage > memory_request * 0.9 else 0
        
        # Stability indicators
        features['restart_frequency'] = pod_data.get('restart_count', 0) / max(pod_data.get('age_hours', 1), 1)
        features['is_stable'] = 1 if features['restart_frequency'] < 0.1 else 0
        
        # Network activity level
        network_rx = pod_data.get('network_rx_bytes', 0)
        network_tx = pod_data.get('network_tx_bytes', 0)
        features['network_activity_level'] = min((network_rx + network_tx) / 1024 / 1024, 1000)  # MB
        
        return features
    
    def extract_namespace_features(self, namespace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract namespace-level features"""
        features = {}
        
        # Resource density
        total_pods = namespace_data.get('pod_count', 1)
        total_cpu = namespace_data.get('total_cpu_request', 0)
        total_memory = namespace_data.get('total_memory_request', 0)
        
        features['namespace_pod_density'] = total_pods
        features['namespace_cpu_density'] = total_cpu / total_pods if total_pods > 0 else 0
        features['namespace_memory_density'] = total_memory / total_pods if total_pods > 0 else 0
        
        # Namespace type inference
        namespace_name = namespace_data.get('name', '').lower()
        if any(env in namespace_name for env in ['prod', 'production']):
            features['namespace_type'] = 'production'
        elif any(env in namespace_name for env in ['dev', 'development']):
            features['namespace_type'] = 'development'
        elif any(env in namespace_name for env in ['stage', 'staging']):
            features['namespace_type'] = 'staging'
        else:
            features['namespace_type'] = 'other'
        
        return features
    
    def extract_cluster_features(self, cluster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cluster-level features"""
        features = {}
        
        # Cluster health indicators
        total_nodes = cluster_data.get('node_count', 1)
        ready_nodes = cluster_data.get('ready_nodes', total_nodes)
        features['cluster_health_ratio'] = ready_nodes / total_nodes if total_nodes > 0 else 1
        
        # Resource utilization distribution
        node_cpu_utilizations = cluster_data.get('node_cpu_utilizations', [])
        if node_cpu_utilizations:
            features['cluster_cpu_variance'] = np.var(node_cpu_utilizations)
            features['cluster_cpu_skewness'] = stats.skew(node_cpu_utilizations)
        else:
            features['cluster_cpu_variance'] = 0
            features['cluster_cpu_skewness'] = 0
        
        # Load balancing effectiveness
        node_pod_counts = cluster_data.get('node_pod_counts', [])
        if node_pod_counts and len(node_pod_counts) > 1:
            features['pod_distribution_variance'] = np.var(node_pod_counts)
        else:
            features['pod_distribution_variance'] = 0
        
        return features


class TimeSeriesFeatureExtractor:
    """Extracts time-series features from historical data"""
    
    def __init__(self, lookback_hours: int = 24):
        self.lookback_hours = lookback_hours
    
    def extract_temporal_features(self, time_series: TimeSeries) -> Dict[str, float]:
        """Extract comprehensive temporal features"""
        features = {}
        
        if len(time_series.values) < 2:
            return {}
        
        values = time_series.values
        
        # Basic statistical features
        features[f'{time_series.feature_name}_mean'] = np.mean(values)
        features[f'{time_series.feature_name}_std'] = np.std(values)
        features[f'{time_series.feature_name}_min'] = np.min(values)
        features[f'{time_series.feature_name}_max'] = np.max(values)
        features[f'{time_series.feature_name}_median'] = np.median(values)
        features[f'{time_series.feature_name}_range'] = np.max(values) - np.min(values)
        
        # Percentiles
        features[f'{time_series.feature_name}_p25'] = np.percentile(values, 25)
        features[f'{time_series.feature_name}_p75'] = np.percentile(values, 75)
        features[f'{time_series.feature_name}_p95'] = np.percentile(values, 95)
        
        # Trend and volatility
        features[f'{time_series.feature_name}_trend'] = time_series.get_trend()
        features[f'{time_series.feature_name}_volatility'] = time_series.get_volatility()
        
        # Change rates
        if len(values) > 1:
            changes = np.diff(values)
            features[f'{time_series.feature_name}_mean_change'] = np.mean(changes)
            features[f'{time_series.feature_name}_std_change'] = np.std(changes)
            features[f'{time_series.feature_name}_positive_changes'] = np.sum(changes > 0) / len(changes)
        
        # Seasonal components
        seasonal_components = time_series.get_seasonal_components()
        for key, value in seasonal_components.items():
            features[f'{time_series.feature_name}_{key}'] = value
        
        # Anomaly indicators
        z_scores = np.abs(stats.zscore(values))
        features[f'{time_series.feature_name}_anomaly_count'] = np.sum(z_scores > 2)
        features[f'{time_series.feature_name}_anomaly_ratio'] = np.sum(z_scores > 2) / len(values)
        
        # Stability indicators
        features[f'{time_series.feature_name}_coefficient_of_variation'] = time_series.get_volatility()
        
        return features
    
    def extract_fourier_features(self, time_series: TimeSeries, n_components: int = 5) -> Dict[str, float]:
        """Extract Fourier transform features"""
        features = {}
        
        if len(time_series.values) < 10:
            return features
        
        # Compute FFT
        fft_values = np.fft.fft(time_series.values)
        fft_magnitude = np.abs(fft_values)
        fft_frequencies = np.fft.fftfreq(len(time_series.values))
        
        # Dominant frequencies
        dominant_indices = np.argsort(fft_magnitude)[-n_components:]
        
        for i, idx in enumerate(dominant_indices):
            features[f'{time_series.feature_name}_dominant_freq_{i}'] = fft_frequencies[idx]
            features[f'{time_series.feature_name}_dominant_magnitude_{i}'] = fft_magnitude[idx]
        
        # Spectral properties
        features[f'{time_series.feature_name}_spectral_centroid'] = np.sum(fft_frequencies * fft_magnitude) / np.sum(fft_magnitude)
        features[f'{time_series.feature_name}_spectral_bandwidth'] = np.sqrt(np.sum(((fft_frequencies - features[f'{time_series.feature_name}_spectral_centroid']) ** 2) * fft_magnitude) / np.sum(fft_magnitude))
        
        return features


class StatisticalFeatureExtractor:
    """Extracts statistical features and relationships"""
    
    def extract_distribution_features(self, data: np.ndarray, feature_name: str) -> Dict[str, float]:
        """Extract distribution-based features"""
        features = {}
        
        if len(data) < 2:
            return features
        
        # Moments
        features[f'{feature_name}_skewness'] = stats.skew(data)
        features[f'{feature_name}_kurtosis'] = stats.kurtosis(data)
        
        # Distribution tests
        try:
            # Normality test
            _, p_normal = stats.normaltest(data)
            features[f'{feature_name}_is_normal'] = 1 if p_normal > 0.05 else 0
            features[f'{feature_name}_normality_p_value'] = p_normal
        except:
            features[f'{feature_name}_is_normal'] = 0
            features[f'{feature_name}_normality_p_value'] = 0
        
        # Entropy
        hist, _ = np.histogram(data, bins=min(50, len(data)//10))
        hist = hist / np.sum(hist)  # Normalize
        entropy = -np.sum(hist * np.log(hist + 1e-10))
        features[f'{feature_name}_entropy'] = entropy
        
        return features
    
    def extract_correlation_features(self, data_dict: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Extract correlation-based features"""
        features = {}
        
        feature_names = list(data_dict.keys())
        
        for i, name1 in enumerate(feature_names):
            for j, name2 in enumerate(feature_names[i+1:], i+1):
                try:
                    correlation, p_value = stats.pearsonr(data_dict[name1], data_dict[name2])
                    features[f'correlation_{name1}_{name2}'] = correlation
                    features[f'correlation_p_value_{name1}_{name2}'] = p_value
                    
                    # Mutual information
                    mi_score = mutual_info_score(
                        data_dict[name1].astype(int) % 10,  # Discretize for MI
                        data_dict[name2].astype(int) % 10
                    )
                    features[f'mutual_info_{name1}_{name2}'] = mi_score
                    
                except:
                    features[f'correlation_{name1}_{name2}'] = 0
                    features[f'correlation_p_value_{name1}_{name2}'] = 1
                    features[f'mutual_info_{name1}_{name2}'] = 0
        
        return features


class FeatureSelector:
    """Advanced feature selection with multiple methods"""
    
    def __init__(self, config: FeatureEngineringConfig):
        self.config = config
        self.feature_importance_history: List[FeatureImportance] = []
    
    def select_features(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Tuple[np.ndarray, List[str], List[FeatureImportance]]:
        """Select best features using multiple methods"""
        importance_scores = {}
        
        # Method 1: Mutual Information
        if 'mutual_info' in self.config.selection_methods:
            mi_scores = mutual_info_classif(X, y)
            for i, score in enumerate(mi_scores):
                importance_scores[feature_names[i]] = importance_scores.get(feature_names[i], 0) + score
        
        # Method 2: Random Forest Feature Importance
        if 'random_forest' in self.config.selection_methods:
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            for i, importance in enumerate(rf.feature_importances_):
                importance_scores[feature_names[i]] = importance_scores.get(feature_names[i], 0) + importance
        
        # Method 3: Statistical Tests
        if 'statistical' in self.config.selection_methods:
            f_scores, p_values = f_classif(X, y)
            for i, score in enumerate(f_scores):
                importance_scores[feature_names[i]] = importance_scores.get(feature_names[i], 0) + score / 1000  # Normalize
        
        # Create importance objects
        feature_importances = []
        for i, feature_name in enumerate(feature_names):
            importance = FeatureImportance(
                feature_name=feature_name,
                importance_score=importance_scores.get(feature_name, 0),
                importance_type='combined',
                rank=0,  # Will be set after sorting
                p_value=None,
                selected=False,
                timestamp=datetime.utcnow()
            )
            feature_importances.append(importance)
        
        # Sort by importance
        feature_importances.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Set ranks and select features
        selected_features = []
        selected_indices = []
        
        for rank, importance in enumerate(feature_importances):
            importance.rank = rank + 1
            
            if (rank < self.config.max_features and 
                importance.importance_score > self.config.importance_threshold):
                importance.selected = True
                selected_features.append(importance.feature_name)
                selected_indices.append(feature_names.index(importance.feature_name))
        
        # Update history
        self.feature_importance_history.extend(feature_importances)
        
        # Return selected features
        X_selected = X[:, selected_indices]
        
        return X_selected, selected_features, feature_importances


class AdvancedFeatureEngineering:
    """
    Advanced feature engineering system for ML pipeline
    
    Features:
    - Automated feature discovery and generation
    - Time-series feature extraction
    - Domain-specific Kubernetes features
    - Statistical feature relationships
    - Intelligent feature selection
    - Polynomial and interaction features
    - Dimensionality reduction
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.config = FeatureEngineringConfig()
        
        # Feature extractors
        self.k8s_extractor = KubernetesFeatureExtractor()
        self.timeseries_extractor = TimeSeriesFeatureExtractor(self.config.lookback_window_hours)
        self.statistical_extractor = StatisticalFeatureExtractor()
        self.feature_selector = FeatureSelector(self.config)
        
        # Feature cache
        self.feature_cache: Dict[str, Any] = {}
        self.feature_metadata: Dict[str, Dict] = {}
        
        logger.info("🔧 Initializing advanced feature engineering system")
    
    async def extract_comprehensive_features(self, cluster_data: Dict[str, Any]) -> Tuple[np.ndarray, List[str]]:
        """Extract comprehensive feature set from cluster data"""
        try:
            logger.info("🚀 Extracting comprehensive features...")
            
            all_features = {}
            
            # Extract basic ML features
            basic_features = await self._extract_basic_features(cluster_data)
            all_features.update(basic_features)
            
            # Extract Kubernetes-specific features
            if self.config.enable_domain_specific:
                k8s_features = await self._extract_kubernetes_features(cluster_data)
                all_features.update(k8s_features)
            
            # Extract time-series features
            if self.config.enable_temporal_features:
                temporal_features = await self._extract_temporal_features(cluster_data)
                all_features.update(temporal_features)
            
            # Extract statistical features
            if self.config.enable_statistical_features:
                statistical_features = await self._extract_statistical_features(cluster_data)
                all_features.update(statistical_features)
            
            # Generate polynomial features
            if self.config.enable_polynomial_features:
                poly_features = self._generate_polynomial_features(all_features)
                all_features.update(poly_features)
            
            # Generate interaction features
            if self.config.enable_interaction_features:
                interaction_features = self._generate_interaction_features(all_features)
                all_features.update(interaction_features)
            
            # Convert to arrays
            feature_names = list(all_features.keys())
            feature_matrix = np.array([list(all_features.values())]).T
            
            # Handle NaN values
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=1e6, neginf=-1e6)
            
            logger.info(f"✅ Extracted {len(feature_names)} features")
            return feature_matrix, feature_names
            
        except Exception as e:
            logger.error(f"❌ Feature extraction failed: {e}")
            return np.array([]), []
    
    async def _extract_basic_features(self, cluster_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract basic ML features"""
        features = {}
        
        # Pod-level features
        for pod in cluster_data.get('pods', []):
            pod_features = {
                'cpu_usage_percent': pod.get('cpu_usage_percent', 0),
                'memory_usage_percent': pod.get('memory_usage_percent', 0),
                'network_activity': pod.get('network_rx_bytes', 0) + pod.get('network_tx_bytes', 0),
                'restart_count': pod.get('restart_count', 0),
                'age_hours': pod.get('age_hours', 0),
            }
            
            # Aggregate pod features
            for key, value in pod_features.items():
                if f'avg_{key}' not in features:
                    features[f'avg_{key}'] = []
                features[f'avg_{key}'].append(value)
        
        # Convert lists to aggregated values
        for key in list(features.keys()):
            if isinstance(features[key], list):
                values = features[key]
                if values:
                    features[key] = np.mean(values)
                    features[f'max_{key}'] = np.max(values)
                    features[f'min_{key}'] = np.min(values)
                    features[f'std_{key}'] = np.std(values)
                else:
                    features[key] = 0
        
        return features
    
    async def _extract_kubernetes_features(self, cluster_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract Kubernetes-specific features"""
        features = {}
        
        # Cluster-level features
        cluster_features = self.k8s_extractor.extract_cluster_features(cluster_data)
        features.update(cluster_features)
        
        # Namespace-level features aggregated
        namespace_features = defaultdict(list)
        for namespace in cluster_data.get('namespaces', []):
            ns_features = self.k8s_extractor.extract_namespace_features(namespace)
            for key, value in ns_features.items():
                if isinstance(value, (int, float)):
                    namespace_features[key].append(value)
        
        # Aggregate namespace features
        for key, values in namespace_features.items():
            if values:
                features[f'namespace_{key}_avg'] = np.mean(values)
                features[f'namespace_{key}_std'] = np.std(values)
        
        # Workload-level features aggregated
        workload_features = defaultdict(list)
        for pod in cluster_data.get('pods', []):
            pod_features = self.k8s_extractor.extract_workload_features(pod)
            for key, value in pod_features.items():
                if isinstance(value, (int, float)):
                    workload_features[key].append(value)
        
        # Aggregate workload features
        for key, values in workload_features.items():
            if values:
                features[f'workload_{key}_avg'] = np.mean(values)
                features[f'workload_{key}_std'] = np.std(values)
        
        return features
    
    async def _extract_temporal_features(self, cluster_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract time-series features"""
        features = {}
        
        # Get historical metrics
        historical_metrics = cluster_data.get('historical_metrics', {})
        
        for metric_name, metric_data in historical_metrics.items():
            if isinstance(metric_data, dict) and 'timestamps' in metric_data and 'values' in metric_data:
                time_series = TimeSeries(
                    timestamps=np.array(metric_data['timestamps']),
                    values=np.array(metric_data['values']),
                    feature_name=metric_name
                )
                
                # Extract temporal features
                temporal_features = self.timeseries_extractor.extract_temporal_features(time_series)
                features.update(temporal_features)
                
                # Extract Fourier features
                fourier_features = self.timeseries_extractor.extract_fourier_features(time_series)
                features.update(fourier_features)
        
        return features
    
    async def _extract_statistical_features(self, cluster_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract statistical features"""
        features = {}
        
        # Collect data for correlation analysis
        correlation_data = {}
        
        # Pod metrics for correlation
        pod_cpu_usage = []
        pod_memory_usage = []
        pod_network_activity = []
        
        for pod in cluster_data.get('pods', []):
            pod_cpu_usage.append(pod.get('cpu_usage_percent', 0))
            pod_memory_usage.append(pod.get('memory_usage_percent', 0))
            pod_network_activity.append(pod.get('network_rx_bytes', 0) + pod.get('network_tx_bytes', 0))
        
        if pod_cpu_usage:
            correlation_data['cpu_usage'] = np.array(pod_cpu_usage)
            correlation_data['memory_usage'] = np.array(pod_memory_usage)
            correlation_data['network_activity'] = np.array(pod_network_activity)
            
            # Extract distribution features
            for name, data in correlation_data.items():
                dist_features = self.statistical_extractor.extract_distribution_features(data, name)
                features.update(dist_features)
            
            # Extract correlation features
            corr_features = self.statistical_extractor.extract_correlation_features(correlation_data)
            features.update(corr_features)
        
        return features
    
    def _generate_polynomial_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Generate polynomial features"""
        poly_features = {}
        
        # Select numerical features only
        numerical_features = {k: v for k, v in features.items() if isinstance(v, (int, float))}
        
        if len(numerical_features) < 2:
            return poly_features
        
        # Create polynomial features for selected important features
        important_features = list(numerical_features.keys())[:20]  # Limit to prevent explosion
        
        for i, feature1 in enumerate(important_features):
            # Squared features
            poly_features[f'{feature1}_squared'] = features[feature1] ** 2
            
            # Interaction features with next few features
            for j, feature2 in enumerate(important_features[i+1:i+4]):  # Limit interactions
                poly_features[f'{feature1}_x_{feature2}'] = features[feature1] * features[feature2]
        
        return poly_features
    
    def _generate_interaction_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Generate interaction features"""
        interaction_features = {}
        
        # Define meaningful interaction groups for Kubernetes
        interaction_groups = {
            'resource_efficiency': ['cpu_usage_percent', 'memory_usage_percent', 'cpu_efficiency', 'memory_efficiency'],
            'stability_performance': ['restart_count', 'age_hours', 'network_activity'],
            'cluster_health': ['cluster_health_ratio', 'cluster_cpu_variance', 'pod_distribution_variance']
        }
        
        for group_name, feature_group in interaction_groups.items():
            available_features = [f for f in feature_group if f in features]
            
            if len(available_features) >= 2:
                # Create ratio features
                for i, feat1 in enumerate(available_features):
                    for feat2 in available_features[i+1:]:
                        if features[feat2] != 0:
                            interaction_features[f'{feat1}_ratio_{feat2}'] = features[feat1] / features[feat2]
                
                # Create combined features
                if len(available_features) >= 3:
                    combined_value = np.mean([features[f] for f in available_features])
                    interaction_features[f'{group_name}_combined'] = combined_value
        
        return interaction_features
    
    async def apply_feature_selection(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Tuple[np.ndarray, List[str], List[FeatureImportance]]:
        """Apply intelligent feature selection"""
        if not self.config.enable_automated_selection:
            return X, feature_names, []
        
        logger.info(f"🎯 Applying feature selection to {len(feature_names)} features...")
        
        X_selected, selected_features, importances = self.feature_selector.select_features(X, y, feature_names)
        
        logger.info(f"✅ Selected {len(selected_features)} features out of {len(feature_names)}")
        
        return X_selected, selected_features, importances
    
    async def apply_dimensionality_reduction(self, X: np.ndarray, feature_names: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Apply dimensionality reduction"""
        reduced_features = []
        
        # PCA
        if self.config.enable_pca and X.shape[1] > 10:
            pca = PCA()
            X_pca = pca.fit_transform(X)
            
            # Select components that explain desired variance
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            n_components = np.argmax(cumulative_variance >= self.config.pca_variance_threshold) + 1
            n_components = min(n_components, X.shape[1])
            
            X_pca_selected = X_pca[:, :n_components]
            pca_feature_names = [f'pca_component_{i}' for i in range(n_components)]
            
            reduced_features.append((X_pca_selected, pca_feature_names))
        
        # ICA
        if self.config.enable_ica and X.shape[1] > 5:
            n_components = min(X.shape[1], 10)  # Limit ICA components
            ica = FastICA(n_components=n_components, random_state=42)
            X_ica = ica.fit_transform(X)
            ica_feature_names = [f'ica_component_{i}' for i in range(n_components)]
            
            reduced_features.append((X_ica, ica_feature_names))
        
        # Combine original and reduced features
        if reduced_features:
            all_X = [X]
            all_names = [feature_names]
            
            for reduced_X, reduced_names in reduced_features:
                all_X.append(reduced_X)
                all_names.extend(reduced_names)
            
            X_combined = np.hstack(all_X)
            names_combined = feature_names + [name for _, names in reduced_features for name in names]
            
            return X_combined, names_combined
        
        return X, feature_names
    
    async def transform_features(self, X: np.ndarray, fit_scaler: bool = True) -> np.ndarray:
        """Apply feature scaling and transformation"""
        if self.config.scaling_method == "standard":
            scaler = StandardScaler()
        elif self.config.scaling_method == "minmax":
            scaler = MinMaxScaler()
        elif self.config.scaling_method == "robust":
            scaler = RobustScaler()
        else:
            return X
        
        if fit_scaler:
            X_scaled = scaler.fit_transform(X)
            # Cache scaler for future use
            self.feature_cache['scaler'] = scaler
        else:
            # Use cached scaler
            scaler = self.feature_cache.get('scaler')
            if scaler:
                X_scaled = scaler.transform(X)
            else:
                X_scaled = X
        
        return X_scaled
    
    async def get_feature_engineering_summary(self) -> Dict[str, Any]:
        """Get comprehensive feature engineering summary"""
        return {
            'config': asdict(self.config),
            'feature_importance_history': [asdict(imp) for imp in self.feature_selector.feature_importance_history],
            'feature_cache_keys': list(self.feature_cache.keys()),
            'feature_metadata': self.feature_metadata,
            'extractors_status': {
                'kubernetes': bool(self.k8s_extractor),
                'timeseries': bool(self.timeseries_extractor),
                'statistical': bool(self.statistical_extractor)
            }
        }
    
    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update feature engineering configuration"""
        try:
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Update dependent components
            self.feature_selector = FeatureSelector(self.config)
            self.timeseries_extractor = TimeSeriesFeatureExtractor(self.config.lookback_window_hours)
            
            logger.info("✅ Feature engineering configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update configuration: {e}")
            return False


# Export main classes
__all__ = [
    'AdvancedFeatureEngineering',
    'FeatureEngineringConfig',
    'KubernetesFeatureExtractor',
    'TimeSeriesFeatureExtractor',
    'StatisticalFeatureExtractor',
    'FeatureSelector',
    'FeatureImportance'
]