"""
Predictive Analytics Engine
Uses machine learning to predict resource needs, scaling patterns, and potential issues.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictions that can be made."""
    RESOURCE_USAGE = "resource_usage"
    SCALING_NEED = "scaling_need"
    FAILURE_RISK = "failure_risk"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class Prediction:
    """Represents a prediction with confidence and metadata."""
    prediction_type: PredictionType
    target_metric: str
    predicted_value: float
    confidence: float  # 0 to 1
    time_horizon: timedelta
    timestamp: datetime
    description: str
    factors: List[str]
    recommendations: List[str]


@dataclass
class AnomalyDetection:
    """Represents an anomaly detection result."""
    metric_name: str
    current_value: float
    expected_range: Tuple[float, float]
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    recommendations: List[str]


class PredictiveAnalyticsEngine:
    """
    Predictive Analytics Engine using ML to predict resource needs and issues.
    """
    
    def __init__(self):
        self.prediction_horizon = timedelta(hours=24)
        self.confidence_threshold = 0.7
        self.anomaly_threshold = 2.0  # Standard deviations
        self.historical_data: Dict[str, List[float]] = {}
        
    async def predict_resource_usage(
        self, 
        current_metrics: Dict[str, Any],
        historical_data: Dict[str, List[float]]
    ) -> List[Prediction]:
        """
        Predict future resource usage based on current and historical data.
        
        Args:
            current_metrics: Current Kubernetes metrics
            historical_data: Historical metrics data
            
        Returns:
            List of resource usage predictions
        """
        logger.info("Starting resource usage prediction")
        
        predictions = []
        
        # Predict CPU usage
        if 'cpu_usage' in current_metrics:
            cpu_prediction = await self._predict_cpu_usage(
                current_metrics['cpu_usage'], historical_data.get('cpu', [])
            )
            if cpu_prediction:
                predictions.append(cpu_prediction)
        
        # Predict memory usage
        if 'memory_usage' in current_metrics:
            memory_prediction = await self._predict_memory_usage(
                current_metrics['memory_usage'], historical_data.get('memory', [])
            )
            if memory_prediction:
                predictions.append(memory_prediction)
        
        # Predict pod scaling needs
        if 'pod_count' in current_metrics:
            scaling_prediction = await self._predict_scaling_needs(
                current_metrics['pod_count'], historical_data.get('pods', [])
            )
            if scaling_prediction:
                predictions.append(scaling_prediction)
        
        logger.info(f"Generated {len(predictions)} resource usage predictions")
        return predictions
    
    async def _predict_cpu_usage(
        self, 
        current_cpu: Dict[str, Any], 
        historical_cpu: List[float]
    ) -> Optional[Prediction]:
        """Predict future CPU usage."""
        if not historical_cpu or 'average' not in current_cpu:
            return None
        
        current_avg = current_cpu['average']
        
        # Simple trend analysis
        if len(historical_cpu) >= 3:
            recent_trend = self._calculate_trend(historical_cpu[-3:])
            predicted_value = current_avg + (recent_trend * 24)  # 24-hour prediction
            
            confidence = self._calculate_confidence(historical_cpu, current_avg)
            
            if confidence > self.confidence_threshold:
                return Prediction(
                    prediction_type=PredictionType.RESOURCE_USAGE,
                    target_metric="CPU Usage",
                    predicted_value=max(0, min(100, predicted_value)),
                    confidence=confidence,
                    time_horizon=timedelta(hours=24),
                    timestamp=datetime.now(),
                    description=f"CPU usage predicted to be {predicted_value:.1f}% in 24 hours",
                    factors=["Historical trend", "Current utilization", "Time patterns"],
                    recommendations=[
                        "Monitor CPU trends closely",
                        "Prepare scaling resources if needed",
                        "Optimize resource allocation"
                    ]
                )
        
        return None
    
    async def _predict_memory_usage(
        self, 
        current_memory: Dict[str, Any], 
        historical_memory: List[float]
    ) -> Optional[Prediction]:
        """Predict future memory usage."""
        if not historical_memory or 'average' not in current_memory:
            return None
        
        current_avg = current_memory['average']
        
        # Memory prediction with leak detection
        if len(historical_memory) >= 5:
            recent_trend = self._calculate_trend(historical_memory[-5:])
            predicted_value = current_avg + (recent_trend * 24)
            
            confidence = self._calculate_confidence(historical_memory, current_avg)
            
            if confidence > self.confidence_threshold:
                return Prediction(
                    prediction_type=PredictionType.RESOURCE_USAGE,
                    target_metric="Memory Usage",
                    predicted_value=max(0, min(100, predicted_value)),
                    confidence=confidence,
                    time_horizon=timedelta(hours=24),
                    timestamp=datetime.now(),
                    description=f"Memory usage predicted to be {predicted_value:.1f}% in 24 hours",
                    factors=["Memory trends", "Potential leaks", "Usage patterns"],
                    recommendations=[
                        "Monitor for memory leaks",
                        "Prepare memory scaling",
                        "Optimize memory allocation"
                    ]
                )
        
        return None
    
    async def _predict_scaling_needs(
        self, 
        current_pods: Dict[str, Any], 
        historical_pods: List[float]
    ) -> Optional[Prediction]:
        """Predict scaling needs based on pod count trends."""
        if not historical_pods or 'count' not in current_pods:
            return None
        
        current_count = current_pods['count']
        
        if len(historical_pods) >= 3:
            recent_trend = self._calculate_trend(historical_pods[-3:])
            predicted_count = current_count + (recent_trend * 24)
            
            confidence = self._calculate_confidence(historical_pods, current_count)
            
            if confidence > self.confidence_threshold:
                scaling_needed = predicted_count > current_count * 1.2  # 20% increase threshold
                
                return Prediction(
                    prediction_type=PredictionType.SCALING_NEED,
                    target_metric="Pod Count",
                    predicted_value=max(1, predicted_count),
                    confidence=confidence,
                    time_horizon=timedelta(hours=24),
                    timestamp=datetime.now(),
                    description=f"Pod count predicted to be {predicted_count:.0f} in 24 hours",
                    factors=["Traffic patterns", "Resource utilization", "Historical scaling"],
                    recommendations=[
                        "Prepare horizontal scaling" if scaling_needed else "Monitor scaling needs",
                        "Review autoscaling policies",
                        "Optimize pod resource requests"
                    ]
                )
        
        return None
    
    async def detect_anomalies(
        self, 
        current_metrics: Dict[str, Any],
        historical_data: Dict[str, List[float]]
    ) -> List[AnomalyDetection]:
        """
        Detect anomalies in current metrics compared to historical patterns.
        
        Args:
            current_metrics: Current Kubernetes metrics
            historical_data: Historical metrics data
            
        Returns:
            List of detected anomalies
        """
        logger.info("Starting anomaly detection")
        
        anomalies = []
        
        # Detect CPU anomalies
        if 'cpu_usage' in current_metrics and 'cpu' in historical_data:
            cpu_anomaly = await self._detect_cpu_anomaly(
                current_metrics['cpu_usage'], historical_data['cpu']
            )
            if cpu_anomaly:
                anomalies.append(cpu_anomaly)
        
        # Detect memory anomalies
        if 'memory_usage' in current_metrics and 'memory' in historical_data:
            memory_anomaly = await self._detect_memory_anomaly(
                current_metrics['memory_usage'], historical_data['memory']
            )
            if memory_anomaly:
                anomalies.append(memory_anomaly)
        
        # Detect error rate anomalies
        if 'error_rate' in current_metrics and 'errors' in historical_data:
            error_anomaly = await self._detect_error_anomaly(
                current_metrics['error_rate'], historical_data['errors']
            )
            if error_anomaly:
                anomalies.append(error_anomaly)
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    async def _detect_cpu_anomaly(
        self, 
        current_cpu: Dict[str, Any], 
        historical_cpu: List[float]
    ) -> Optional[AnomalyDetection]:
        """Detect CPU usage anomalies."""
        if not historical_cpu or 'average' not in current_cpu:
            return None
        
        current_avg = current_cpu['average']
        mean_cpu = sum(historical_cpu) / len(historical_cpu)
        std_cpu = self._calculate_std(historical_cpu)
        
        if std_cpu == 0:
            return None
        
        z_score = abs(current_avg - mean_cpu) / std_cpu
        
        if z_score > self.anomaly_threshold:
            severity = self._get_severity(z_score)
            return AnomalyDetection(
                metric_name="CPU Usage",
                current_value=current_avg,
                expected_range=(mean_cpu - 2*std_cpu, mean_cpu + 2*std_cpu),
                severity=severity,
                confidence=min(0.95, z_score / 5.0),
                description=f"CPU usage anomaly detected: {current_avg:.1f}% (expected ~{mean_cpu:.1f}%)",
                recommendations=[
                    "Investigate CPU spike causes",
                    "Check for resource-intensive processes",
                    "Consider scaling if sustained"
                ]
            )
        
        return None
    
    async def _detect_memory_anomaly(
        self, 
        current_memory: Dict[str, Any], 
        historical_memory: List[float]
    ) -> Optional[AnomalyDetection]:
        """Detect memory usage anomalies."""
        if not historical_memory or 'average' not in current_memory:
            return None
        
        current_avg = current_memory['average']
        mean_memory = sum(historical_memory) / len(historical_memory)
        std_memory = self._calculate_std(historical_memory)
        
        if std_memory == 0:
            return None
        
        z_score = abs(current_avg - mean_memory) / std_memory
        
        if z_score > self.anomaly_threshold:
            severity = self._get_severity(z_score)
            return AnomalyDetection(
                metric_name="Memory Usage",
                current_value=current_avg,
                expected_range=(mean_memory - 2*std_memory, mean_memory + 2*std_memory),
                severity=severity,
                confidence=min(0.95, z_score / 5.0),
                description=f"Memory usage anomaly detected: {current_avg:.1f}% (expected ~{mean_memory:.1f}%)",
                recommendations=[
                    "Check for memory leaks",
                    "Investigate memory spike causes",
                    "Consider memory scaling"
                ]
            )
        
        return None
    
    async def _detect_error_anomaly(
        self, 
        current_errors: Dict[str, Any], 
        historical_errors: List[float]
    ) -> Optional[AnomalyDetection]:
        """Detect error rate anomalies."""
        if not historical_errors or 'rate' not in current_errors:
            return None
        
        current_rate = current_errors['rate']
        mean_errors = sum(historical_errors) / len(historical_errors)
        std_errors = self._calculate_std(historical_errors)
        
        if std_errors == 0:
            return None
        
        z_score = abs(current_rate - mean_errors) / std_errors
        
        if z_score > self.anomaly_threshold:
            severity = self._get_severity(z_score)
            return AnomalyDetection(
                metric_name="Error Rate",
                current_value=current_rate,
                expected_range=(mean_errors - 2*std_errors, mean_errors + 2*std_errors),
                severity=severity,
                confidence=min(0.95, z_score / 5.0),
                description=f"Error rate anomaly detected: {current_rate:.2f}% (expected ~{mean_errors:.2f}%)",
                recommendations=[
                    "Investigate error spike causes",
                    "Check application logs",
                    "Review error handling"
                ]
            )
        
        return None
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend from recent values."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        x_values = list(range(len(values)))
        y_values = values
        
        n = len(values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def _calculate_confidence(self, historical: List[float], current: float) -> float:
        """Calculate confidence based on data consistency."""
        if not historical:
            return 0.5
        
        # Calculate coefficient of variation
        mean = sum(historical) / len(historical)
        std = self._calculate_std(historical)
        
        if mean == 0:
            return 0.5
        
        cv = std / mean
        
        # Lower CV = higher confidence
        confidence = max(0.1, min(0.95, 1.0 - cv))
        
        # Adjust based on data volume
        volume_factor = min(1.0, len(historical) / 10.0)
        confidence *= volume_factor
        
        return confidence
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    def _get_severity(self, z_score: float) -> str:
        """Get severity level based on z-score."""
        if z_score > 4.0:
            return "critical"
        elif z_score > 3.0:
            return "high"
        elif z_score > 2.0:
            return "medium"
        else:
            return "low"
    
    async def generate_predictive_report(
        self, 
        predictions: List[Prediction],
        anomalies: List[AnomalyDetection]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive predictive analytics report.
        
        Args:
            predictions: List of predictions
            anomalies: List of detected anomalies
            
        Returns:
            Dictionary containing the predictive report
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "total": len(predictions),
                "high_confidence": len([p for p in predictions if p.confidence > 0.8]),
                "by_type": {
                    pred_type.value: len([p for p in predictions if p.prediction_type == pred_type])
                    for pred_type in PredictionType
                },
                "details": [
                    {
                        "type": pred.prediction_type.value,
                        "target": pred.target_metric,
                        "predicted_value": pred.predicted_value,
                        "confidence": pred.confidence,
                        "description": pred.description,
                        "recommendations": pred.recommendations
                    }
                    for pred in predictions
                ]
            },
            "anomalies": {
                "total": len(anomalies),
                "critical": len([a for a in anomalies if a.severity == "critical"]),
                "high": len([a for a in anomalies if a.severity == "high"]),
                "medium": len([a for a in anomalies if a.severity == "medium"]),
                "low": len([a for a in anomalies if a.severity == "low"]),
                "details": [
                    {
                        "metric": anomaly.metric_name,
                        "current_value": anomaly.current_value,
                        "expected_range": anomaly.expected_range,
                        "severity": anomaly.severity,
                        "confidence": anomaly.confidence,
                        "description": anomaly.description,
                        "recommendations": anomaly.recommendations
                    }
                    for anomaly in anomalies
                ]
            },
            "summary": {
                "status": "healthy" if len(anomalies) == 0 else "needs_attention",
                "key_insights": [
                    f"Generated {len(predictions)} predictions",
                    f"Detected {len(anomalies)} anomalies",
                    f"{len([a for a in anomalies if a.severity in ['high', 'critical']])} high-severity issues"
                ]
            }
        } 