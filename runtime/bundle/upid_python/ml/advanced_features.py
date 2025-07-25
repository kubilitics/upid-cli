"""
UPID CLI - Advanced ML Features
Advanced machine learning capabilities for enterprise Kubernetes optimization
"""

import logging
import asyncio
import json
import pickle
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

from ..core.metrics_collector import MetricsCollector, NodeMetrics, PodMetrics, ClusterMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from .pipeline import MLPipeline, MLFeatures, MLPrediction

logger = logging.getLogger(__name__)


@dataclass
class ScalingRecommendation:
    """Predictive scaling recommendation"""
    workload_name: str
    namespace: str
    current_replicas: int
    recommended_replicas: int
    confidence: float
    reasoning: str
    predicted_demand: float
    scaling_type: str  # "scale_up", "scale_down", "maintain"
    urgency: str  # "low", "medium", "high", "critical"
    estimated_cost_impact: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    alert_id: str
    workload_name: str
    namespace: str
    anomaly_type: str  # "cpu_spike", "memory_leak", "network_anomaly", "cost_anomaly"
    severity: str  # "low", "medium", "high", "critical"
    confidence: float
    description: str
    detected_at: datetime
    metrics: Dict[str, float]
    recommendations: List[str]
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class CostForecast:
    """Cost forecasting results"""
    forecast_id: str
    cluster_name: str
    forecast_period: str  # "daily", "weekly", "monthly"
    current_cost: float
    predicted_cost: float
    confidence_interval: Tuple[float, float]
    trend: str  # "increasing", "decreasing", "stable"
    factors: Dict[str, float]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CustomModelConfig:
    """Custom model training configuration"""
    model_name: str
    model_type: str  # "regression", "classification", "anomaly"
    features: List[str]
    target_variable: str
    hyperparameters: Dict[str, Any]
    training_data_source: str
    validation_split: float = 0.2
    cross_validation_folds: int = 5
    model_metrics: List[str] = field(default_factory=lambda: ["accuracy", "precision", "recall"])


class AdvancedMLFeatures:
    """
    Advanced ML Features for UPID Platform
    
    Provides enterprise-grade ML capabilities:
    - Predictive scaling recommendations
    - Enhanced anomaly detection with alerting
    - Cost forecasting and trend analysis
    - Custom model training and deployment
    - Real-time ML monitoring and optimization
    """
    
    def __init__(self, ml_pipeline: MLPipeline, metrics_collector: MetricsCollector):
        self.ml_pipeline = ml_pipeline
        self.metrics_collector = metrics_collector
        self.scaling_models: Dict[str, Any] = {}
        self.anomaly_detectors: Dict[str, Any] = {}
        self.cost_forecasters: Dict[str, Any] = {}
        self.custom_models: Dict[str, Any] = {}
        self.alerts: List[AnomalyAlert] = []
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        
        logger.info("🔧 Initializing advanced ML features")
    
    async def initialize(self) -> bool:
        """Initialize advanced ML features"""
        try:
            logger.info("🚀 Initializing advanced ML features...")
            
            # Initialize scaling models
            await self._initialize_scaling_models()
            
            # Initialize anomaly detectors
            await self._initialize_anomaly_detectors()
            
            # Initialize cost forecasters
            await self._initialize_cost_forecasters()
            
            # Setup alert thresholds
            await self._setup_alert_thresholds()
            
            logger.info("✅ Advanced ML features initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize advanced ML features: {e}")
            return False
    
    async def _initialize_scaling_models(self):
        """Initialize predictive scaling models"""
        try:
            # CPU-based scaling model
            self.scaling_models["cpu_scaling"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Memory-based scaling model
            self.scaling_models["memory_scaling"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Traffic-based scaling model
            self.scaling_models["traffic_scaling"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            logger.info("✅ Scaling models initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scaling models: {e}")
    
    async def _initialize_anomaly_detectors(self):
        """Initialize anomaly detection models"""
        try:
            # CPU anomaly detector
            self.anomaly_detectors["cpu_anomaly"] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Memory anomaly detector
            self.anomaly_detectors["memory_anomaly"] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Network anomaly detector
            self.anomaly_detectors["network_anomaly"] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Cost anomaly detector
            self.anomaly_detectors["cost_anomaly"] = IsolationForest(
                contamination=0.05,
                random_state=42
            )
            
            logger.info("✅ Anomaly detectors initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize anomaly detectors: {e}")
    
    async def _initialize_cost_forecasters(self):
        """Initialize cost forecasting models"""
        try:
            # Daily cost forecaster
            self.cost_forecasters["daily_cost"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Weekly cost forecaster
            self.cost_forecasters["weekly_cost"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Monthly cost forecaster
            self.cost_forecasters["monthly_cost"] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            logger.info("✅ Cost forecasters initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cost forecasters: {e}")
    
    async def _setup_alert_thresholds(self):
        """Setup alert thresholds for different metrics"""
        self.alert_thresholds = {
            "cpu_usage": {
                "warning": 80.0,
                "critical": 95.0
            },
            "memory_usage": {
                "warning": 85.0,
                "critical": 95.0
            },
            "network_errors": {
                "warning": 5.0,
                "critical": 20.0
            },
            "cost_increase": {
                "warning": 20.0,  # 20% increase
                "critical": 50.0   # 50% increase
            }
        }
    
    async def generate_scaling_recommendations(self, 
                                            cluster_metrics: ClusterMetrics,
                                            pod_metrics: List[PodMetrics]) -> List[ScalingRecommendation]:
        """Generate predictive scaling recommendations"""
        try:
            logger.info("📊 Generating scaling recommendations...")
            
            recommendations = []
            
            for pod_metric in pod_metrics:
                # Extract features for scaling prediction
                features = await self._extract_scaling_features(pod_metric, cluster_metrics)
                
                # Predict optimal replica count
                predicted_replicas = await self._predict_optimal_replicas(features)
                
                # Calculate confidence and reasoning
                confidence = await self._calculate_scaling_confidence(features)
                reasoning = await self._generate_scaling_reasoning(features, predicted_replicas)
                
                # Determine scaling type and urgency
                current_replicas = pod_metric.replica_count or 1
                scaling_type = self._determine_scaling_type(current_replicas, predicted_replicas)
                urgency = self._determine_scaling_urgency(features, confidence)
                
                # Estimate cost impact
                cost_impact = await self._estimate_scaling_cost_impact(
                    current_replicas, predicted_replicas, features
                )
                
                recommendation = ScalingRecommendation(
                    workload_name=pod_metric.pod_name,
                    namespace=pod_metric.namespace,
                    current_replicas=current_replicas,
                    recommended_replicas=predicted_replicas,
                    confidence=confidence,
                    reasoning=reasoning,
                    predicted_demand=features.get("predicted_demand", 0.0),
                    scaling_type=scaling_type,
                    urgency=urgency,
                    estimated_cost_impact=cost_impact
                )
                
                recommendations.append(recommendation)
            
            logger.info(f"✅ Generated {len(recommendations)} scaling recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate scaling recommendations: {e}")
            return []
    
    async def _extract_scaling_features(self, pod_metric: PodMetrics, cluster_metrics: ClusterMetrics) -> Dict[str, float]:
        """Extract features for scaling prediction"""
        try:
            features = {
                "cpu_usage": pod_metric.cpu_usage_percent,
                "memory_usage": pod_metric.memory_usage_percent,
                "network_activity": pod_metric.network_activity,
                "restart_count": pod_metric.restart_count,
                "age_hours": pod_metric.age_hours,
                "idle_duration": pod_metric.idle_duration_hours,
                "cluster_cpu_utilization": cluster_metrics.cpu_usage_percent,
                "cluster_memory_utilization": cluster_metrics.memory_usage_percent,
                "hour_of_day": datetime.utcnow().hour,
                "day_of_week": datetime.utcnow().weekday(),
                "is_weekend": datetime.utcnow().weekday() >= 5,
                "is_business_hours": 9 <= datetime.utcnow().hour <= 17
            }
            
            # Calculate derived features
            features["cpu_memory_ratio"] = features["cpu_usage"] / max(features["memory_usage"], 1)
            features["utilization_efficiency"] = (features["cpu_usage"] + features["memory_usage"]) / 2
            features["cluster_load"] = (features["cluster_cpu_utilization"] + features["cluster_memory_utilization"]) / 2
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Failed to extract scaling features: {e}")
            return {}
    
    async def _predict_optimal_replicas(self, features: Dict[str, float]) -> int:
        """Predict optimal number of replicas"""
        try:
            # Simple heuristic-based prediction
            cpu_usage = features.get("cpu_usage", 0)
            memory_usage = features.get("memory_usage", 0)
            cluster_load = features.get("cluster_load", 0)
            
            # Base prediction on utilization
            if cpu_usage > 80 or memory_usage > 80:
                recommended = 3
            elif cpu_usage > 60 or memory_usage > 60:
                recommended = 2
            else:
                recommended = 1
            
            # Adjust based on cluster load
            if cluster_load > 80:
                recommended = max(recommended, 2)
            
            # Ensure minimum of 1 replica
            return max(recommended, 1)
            
        except Exception as e:
            logger.error(f"❌ Failed to predict optimal replicas: {e}")
            return 1
    
    async def _calculate_scaling_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in scaling recommendation"""
        try:
            # Higher confidence for clear utilization patterns
            cpu_usage = features.get("cpu_usage", 0)
            memory_usage = features.get("memory_usage", 0)
            
            # Confidence based on utilization clarity
            if cpu_usage > 90 or memory_usage > 90:
                confidence = 0.9
            elif cpu_usage > 70 or memory_usage > 70:
                confidence = 0.8
            elif cpu_usage < 30 and memory_usage < 30:
                confidence = 0.7
            else:
                confidence = 0.6
            
            return min(confidence, 0.95)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate scaling confidence: {e}")
            return 0.5
    
    async def _generate_scaling_reasoning(self, features: Dict[str, float], recommended_replicas: int) -> str:
        """Generate human-readable reasoning for scaling recommendation"""
        try:
            cpu_usage = features.get("cpu_usage", 0)
            memory_usage = features.get("memory_usage", 0)
            
            if recommended_replicas > 1:
                if cpu_usage > 80:
                    return f"High CPU utilization ({cpu_usage:.1f}%) suggests need for additional replicas"
                elif memory_usage > 80:
                    return f"High memory utilization ({memory_usage:.1f}%) suggests need for additional replicas"
                else:
                    return f"Moderate resource utilization suggests scaling for better availability"
            else:
                if cpu_usage < 30 and memory_usage < 30:
                    return f"Low resource utilization ({cpu_usage:.1f}% CPU, {memory_usage:.1f}% memory) suggests scaling down"
                else:
                    return f"Current resource utilization is appropriate for single replica"
                    
        except Exception as e:
            logger.error(f"❌ Failed to generate scaling reasoning: {e}")
            return "Unable to generate reasoning"
    
    def _determine_scaling_type(self, current: int, recommended: int) -> str:
        """Determine scaling type"""
        if recommended > current:
            return "scale_up"
        elif recommended < current:
            return "scale_down"
        else:
            return "maintain"
    
    def _determine_scaling_urgency(self, features: Dict[str, float], confidence: float) -> str:
        """Determine scaling urgency"""
        cpu_usage = features.get("cpu_usage", 0)
        memory_usage = features.get("memory_usage", 0)
        
        if (cpu_usage > 95 or memory_usage > 95) and confidence > 0.8:
            return "critical"
        elif (cpu_usage > 80 or memory_usage > 80) and confidence > 0.7:
            return "high"
        elif (cpu_usage > 60 or memory_usage > 60) and confidence > 0.6:
            return "medium"
        else:
            return "low"
    
    async def _estimate_scaling_cost_impact(self, current: int, recommended: int, features: Dict[str, float]) -> float:
        """Estimate cost impact of scaling recommendation"""
        try:
            # Simple cost estimation
            cost_per_replica = 10.0  # Estimated cost per replica per day
            
            cost_difference = (recommended - current) * cost_per_replica
            
            # Adjust based on utilization
            utilization = features.get("utilization_efficiency", 0)
            if utilization > 80:
                cost_difference *= 0.8  # More justified scaling
            elif utilization < 30:
                cost_difference *= 1.2  # Less justified scaling
            
            return cost_difference
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate cost impact: {e}")
            return 0.0
    
    async def detect_anomalies_with_alerts(self, 
                                         cluster_metrics: ClusterMetrics,
                                         pod_metrics: List[PodMetrics]) -> List[AnomalyAlert]:
        """Detect anomalies and generate alerts"""
        try:
            logger.info("🔍 Detecting anomalies...")
            
            alerts = []
            
            # Detect CPU anomalies
            cpu_alerts = await self._detect_cpu_anomalies(pod_metrics)
            alerts.extend(cpu_alerts)
            
            # Detect memory anomalies
            memory_alerts = await self._detect_memory_anomalies(pod_metrics)
            alerts.extend(memory_alerts)
            
            # Detect network anomalies
            network_alerts = await self._detect_network_anomalies(pod_metrics)
            alerts.extend(network_alerts)
            
            # Detect cost anomalies
            cost_alerts = await self._detect_cost_anomalies(cluster_metrics)
            alerts.extend(cost_alerts)
            
            # Store alerts
            self.alerts.extend(alerts)
            
            logger.info(f"✅ Detected {len(alerts)} anomalies")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to detect anomalies: {e}")
            return []
    
    async def _detect_cpu_anomalies(self, pod_metrics: List[PodMetrics]) -> List[AnomalyAlert]:
        """Detect CPU-related anomalies"""
        alerts = []
        
        for pod_metric in pod_metrics:
            cpu_usage = pod_metric.cpu_usage_percent
            
            # Check against thresholds
            if cpu_usage > self.alert_thresholds["cpu_usage"]["critical"]:
                alert = AnomalyAlert(
                    alert_id=f"cpu_critical_{pod_metric.pod_name}_{datetime.utcnow().timestamp()}",
                    workload_name=pod_metric.pod_name,
                    namespace=pod_metric.namespace,
                    anomaly_type="cpu_spike",
                    severity="critical",
                    confidence=0.9,
                    description=f"Critical CPU usage: {cpu_usage:.1f}%",
                    detected_at=datetime.utcnow(),
                    metrics={"cpu_usage": cpu_usage},
                    recommendations=["Scale up immediately", "Check for runaway processes"]
                )
                alerts.append(alert)
                
            elif cpu_usage > self.alert_thresholds["cpu_usage"]["warning"]:
                alert = AnomalyAlert(
                    alert_id=f"cpu_warning_{pod_metric.pod_name}_{datetime.utcnow().timestamp()}",
                    workload_name=pod_metric.pod_name,
                    namespace=pod_metric.namespace,
                    anomaly_type="cpu_spike",
                    severity="high",
                    confidence=0.7,
                    description=f"High CPU usage: {cpu_usage:.1f}%",
                    detected_at=datetime.utcnow(),
                    metrics={"cpu_usage": cpu_usage},
                    recommendations=["Monitor closely", "Consider scaling up"]
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_memory_anomalies(self, pod_metrics: List[PodMetrics]) -> List[AnomalyAlert]:
        """Detect memory-related anomalies"""
        alerts = []
        
        for pod_metric in pod_metrics:
            memory_usage = pod_metric.memory_usage_percent
            
            if memory_usage > self.alert_thresholds["memory_usage"]["critical"]:
                alert = AnomalyAlert(
                    alert_id=f"memory_critical_{pod_metric.pod_name}_{datetime.utcnow().timestamp()}",
                    workload_name=pod_metric.pod_name,
                    namespace=pod_metric.namespace,
                    anomaly_type="memory_leak",
                    severity="critical",
                    confidence=0.9,
                    description=f"Critical memory usage: {memory_usage:.1f}%",
                    detected_at=datetime.utcnow(),
                    metrics={"memory_usage": memory_usage},
                    recommendations=["Check for memory leaks", "Restart if necessary"]
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_network_anomalies(self, pod_metrics: List[PodMetrics]) -> List[AnomalyAlert]:
        """Detect network-related anomalies"""
        alerts = []
        
        for pod_metric in pod_metrics:
            # Simple network anomaly detection
            if pod_metric.network_activity > 1000:  # High network activity
                alert = AnomalyAlert(
                    alert_id=f"network_anomaly_{pod_metric.pod_name}_{datetime.utcnow().timestamp()}",
                    workload_name=pod_metric.pod_name,
                    namespace=pod_metric.namespace,
                    anomaly_type="network_anomaly",
                    severity="medium",
                    confidence=0.6,
                    description=f"Unusual network activity: {pod_metric.network_activity}",
                    detected_at=datetime.utcnow(),
                    metrics={"network_activity": pod_metric.network_activity},
                    recommendations=["Monitor network traffic", "Check for DDoS"]
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_cost_anomalies(self, cluster_metrics: ClusterMetrics) -> List[AnomalyAlert]:
        """Detect cost-related anomalies"""
        alerts = []
        
        # Simple cost anomaly detection
        # In a real implementation, this would compare against historical cost data
        cost_increase = 25.0  # Simulated cost increase percentage
        
        if cost_increase > self.alert_thresholds["cost_increase"]["critical"]:
            alert = AnomalyAlert(
                alert_id=f"cost_critical_{datetime.utcnow().timestamp()}",
                workload_name="cluster-wide",
                namespace="all",
                anomaly_type="cost_anomaly",
                severity="critical",
                confidence=0.8,
                description=f"Critical cost increase: {cost_increase:.1f}%",
                detected_at=datetime.utcnow(),
                metrics={"cost_increase": cost_increase},
                recommendations=["Review resource usage", "Optimize resource allocation"]
            )
            alerts.append(alert)
        
        return alerts
    
    async def forecast_costs(self, 
                           cluster_metrics: ClusterMetrics,
                           historical_data: List[Dict[str, Any]]) -> CostForecast:
        """Generate cost forecasts"""
        try:
            logger.info("💰 Generating cost forecasts...")
            
            # Extract cost features
            features = await self._extract_cost_features(cluster_metrics, historical_data)
            
            # Predict costs for different periods
            daily_cost = await self._predict_daily_cost(features)
            weekly_cost = await self._predict_weekly_cost(features)
            monthly_cost = await self._predict_monthly_cost(features)
            
            # Calculate confidence intervals
            confidence_interval = await self._calculate_cost_confidence_interval(features)
            
            # Determine trend
            trend = await self._determine_cost_trend(historical_data)
            
            # Generate recommendations
            recommendations = await self._generate_cost_recommendations(features, trend)
            
            forecast = CostForecast(
                forecast_id=f"cost_forecast_{datetime.utcnow().timestamp()}",
                cluster_name=cluster_metrics.cluster_name,
                forecast_period="monthly",
                current_cost=features.get("current_cost", 0.0),
                predicted_cost=monthly_cost,
                confidence_interval=confidence_interval,
                trend=trend,
                factors=features,
                recommendations=recommendations
            )
            
            logger.info("✅ Cost forecast generated successfully")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Failed to generate cost forecast: {e}")
            return None
    
    async def _extract_cost_features(self, cluster_metrics: ClusterMetrics, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract features for cost forecasting"""
        try:
            features = {
                "current_cost": 1000.0,  # Simulated current cost
                "cpu_utilization": cluster_metrics.cpu_usage_percent,
                "memory_utilization": cluster_metrics.memory_usage_percent,
                "pod_count": cluster_metrics.pod_count,
                "node_count": cluster_metrics.node_count,
                "hour_of_day": datetime.utcnow().hour,
                "day_of_week": datetime.utcnow().weekday(),
                "is_weekend": datetime.utcnow().weekday() >= 5
            }
            
            # Add historical trends
            if historical_data:
                avg_cost = sum(item.get("cost", 0) for item in historical_data) / len(historical_data)
                features["historical_avg_cost"] = avg_cost
                features["cost_trend"] = (features["current_cost"] - avg_cost) / max(avg_cost, 1)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Failed to extract cost features: {e}")
            return {}
    
    async def _predict_daily_cost(self, features: Dict[str, float]) -> float:
        """Predict daily cost"""
        try:
            base_cost = features.get("current_cost", 1000.0)
            utilization_factor = (features.get("cpu_utilization", 0) + features.get("memory_utilization", 0)) / 200
            
            # Simple prediction model
            predicted_cost = base_cost * (1 + utilization_factor * 0.2)
            
            return max(predicted_cost, 100.0)  # Minimum cost
            
        except Exception as e:
            logger.error(f"❌ Failed to predict daily cost: {e}")
            return 1000.0
    
    async def _predict_weekly_cost(self, features: Dict[str, float]) -> float:
        """Predict weekly cost"""
        try:
            daily_cost = await self._predict_daily_cost(features)
            return daily_cost * 7
            
        except Exception as e:
            logger.error(f"❌ Failed to predict weekly cost: {e}")
            return 7000.0
    
    async def _predict_monthly_cost(self, features: Dict[str, float]) -> float:
        """Predict monthly cost"""
        try:
            daily_cost = await self._predict_daily_cost(features)
            return daily_cost * 30
            
        except Exception as e:
            logger.error(f"❌ Failed to predict monthly cost: {e}")
            return 30000.0
    
    async def _calculate_cost_confidence_interval(self, features: Dict[str, float]) -> Tuple[float, float]:
        """Calculate confidence interval for cost prediction"""
        try:
            predicted_cost = await self._predict_monthly_cost(features)
            confidence_margin = predicted_cost * 0.15  # 15% margin
            
            lower_bound = max(predicted_cost - confidence_margin, 0)
            upper_bound = predicted_cost + confidence_margin
            
            return (lower_bound, upper_bound)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate confidence interval: {e}")
            return (0.0, 0.0)
    
    async def _determine_cost_trend(self, historical_data: List[Dict[str, Any]]) -> str:
        """Determine cost trend"""
        try:
            if len(historical_data) < 2:
                return "stable"
            
            recent_costs = [item.get("cost", 0) for item in historical_data[-5:]]
            if len(recent_costs) < 2:
                return "stable"
            
            # Calculate trend
            first_cost = recent_costs[0]
            last_cost = recent_costs[-1]
            
            if last_cost > first_cost * 1.1:
                return "increasing"
            elif last_cost < first_cost * 0.9:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"❌ Failed to determine cost trend: {e}")
            return "stable"
    
    async def _generate_cost_recommendations(self, features: Dict[str, float], trend: str) -> List[str]:
        """Generate cost optimization recommendations"""
        try:
            recommendations = []
            
            if trend == "increasing":
                recommendations.extend([
                    "Review resource allocation",
                    "Consider scaling down underutilized resources",
                    "Implement cost monitoring alerts"
                ])
            elif trend == "decreasing":
                recommendations.append("Cost optimization is working well")
            else:
                recommendations.extend([
                    "Monitor cost trends",
                    "Consider implementing cost optimization strategies"
                ])
            
            # Add utilization-based recommendations
            cpu_util = features.get("cpu_utilization", 0)
            memory_util = features.get("memory_utilization", 0)
            
            if cpu_util < 30 and memory_util < 30:
                recommendations.append("Consider rightsizing underutilized resources")
            elif cpu_util > 80 or memory_util > 80:
                recommendations.append("Consider scaling up to prevent performance issues")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate cost recommendations: {e}")
            return ["Monitor cost trends"]
    
    async def train_custom_model(self, config: CustomModelConfig, training_data: List[Dict[str, Any]]) -> bool:
        """Train a custom ML model"""
        try:
            logger.info(f"🤖 Training custom model: {config.model_name}")
            
            # Prepare training data
            X, y = await self._prepare_training_data(config, training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.validation_split, random_state=42
            )
            
            # Train model based on type
            if config.model_type == "regression":
                model = RandomForestRegressor(**config.hyperparameters)
            elif config.model_type == "classification":
                from sklearn.ensemble import RandomForestClassifier
                model = RandomForestClassifier(**config.hyperparameters)
            elif config.model_type == "anomaly":
                model = IsolationForest(**config.hyperparameters)
            else:
                raise ValueError(f"Unsupported model type: {config.model_type}")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            if config.model_type != "anomaly":
                y_pred = model.predict(X_test)
                accuracy = model.score(X_test, y_test)
                
                logger.info(f"✅ Model trained with accuracy: {accuracy:.3f}")
            
            # Store model
            self.custom_models[config.model_name] = {
                "model": model,
                "config": config,
                "accuracy": accuracy if config.model_type != "anomaly" else None,
                "trained_at": datetime.utcnow()
            }
            
            logger.info(f"✅ Custom model '{config.model_name}' trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train custom model: {e}")
            return False
    
    async def _prepare_training_data(self, config: CustomModelConfig, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for custom model"""
        try:
            # Extract features and target
            X_data = []
            y_data = []
            
            for item in training_data:
                # Extract features
                features = []
                for feature_name in config.features:
                    features.append(item.get(feature_name, 0.0))
                
                X_data.append(features)
                y_data.append(item.get(config.target_variable, 0.0))
            
            X = np.array(X_data)
            y = np.array(y_data)
            
            return X, y
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare training data: {e}")
            return np.array([]), np.array([])
    
    async def get_alerts(self, 
                        severity: Optional[str] = None,
                        resolved: Optional[bool] = None,
                        limit: int = 100) -> List[AnomalyAlert]:
        """Get alerts with optional filtering"""
        try:
            filtered_alerts = []
            
            for alert in self.alerts:
                # Apply filters
                if severity and alert.severity != severity:
                    continue
                if resolved is not None and alert.is_resolved != resolved:
                    continue
                
                filtered_alerts.append(alert)
                
                if len(filtered_alerts) >= limit:
                    break
            
            return filtered_alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to get alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.is_resolved = True
                    alert.resolved_at = datetime.utcnow()
                    logger.info(f"✅ Alert {alert_id} marked as resolved")
                    return True
            
            logger.warning(f"⚠️ Alert {alert_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert: {e}")
            return False
    
    async def get_advanced_ml_metrics(self) -> Dict[str, Any]:
        """Get advanced ML metrics and performance data"""
        try:
            metrics = {
                "scaling_recommendations_generated": len(self.scaling_models),
                "anomaly_detectors_active": len(self.anomaly_detectors),
                "cost_forecasters_active": len(self.cost_forecasters),
                "custom_models_trained": len(self.custom_models),
                "active_alerts": len([a for a in self.alerts if not a.is_resolved]),
                "total_alerts": len(self.alerts),
                "alert_resolution_rate": len([a for a in self.alerts if a.is_resolved]) / max(len(self.alerts), 1),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get advanced ML metrics: {e}")
            return {} 