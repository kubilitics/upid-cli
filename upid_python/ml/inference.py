"""
UPID CLI - Model Inference
Real-time machine learning inference system
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import json

from ..core.metrics_collector import MetricsCollector, PodMetrics, ClusterMetrics
from ..core.resource_analyzer import ResourceAnalyzer
from .pipeline import MLPipeline, MLFeatures, MLPrediction
from .models.optimization import OptimizationModel
from .models.prediction import PredictionModel
from .models.anomaly import AnomalyDetectionModel

logger = logging.getLogger(__name__)


@dataclass
class InferenceRequest:
    """Inference request structure"""
    cluster_id: str
    namespace: Optional[str] = None
    workload_name: Optional[str] = None
    pod_name: Optional[str] = None
    model_type: str = "all"  # optimization, prediction, anomaly, all
    include_confidence: bool = True
    include_feature_importance: bool = True


@dataclass
class InferenceResponse:
    """Inference response structure"""
    request_id: str
    cluster_id: str
    timestamp: datetime
    predictions: Dict[str, MLPrediction]
    processing_time_ms: float
    model_versions: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class BatchInferenceRequest:
    """Batch inference request structure"""
    cluster_id: str
    namespaces: Optional[List[str]] = None
    workload_names: Optional[List[str]] = None
    model_types: List[str] = None  # Default to all
    max_workloads: Optional[int] = None
    include_confidence: bool = True


@dataclass
class BatchInferenceResponse:
    """Batch inference response structure"""
    request_id: str
    cluster_id: str
    timestamp: datetime
    total_workloads: int
    processed_workloads: int
    predictions: Dict[str, Dict[str, MLPrediction]]
    processing_time_ms: float
    summary: Dict[str, Any]


class ModelInference:
    """
    Real-time machine learning inference system for UPID platform
    
    Provides comprehensive inference capabilities:
    - Real-time predictions
    - Batch processing
    - Model versioning
    - Performance monitoring
    - Caching and optimization
    """
    
    def __init__(self, metrics_collector: MetricsCollector, resource_analyzer: ResourceAnalyzer):
        self.metrics_collector = metrics_collector
        self.resource_analyzer = resource_analyzer
        self.ml_pipeline = MLPipeline(metrics_collector, resource_analyzer)
        
        # Inference cache
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)
        
        # Performance metrics
        self.inference_count = 0
        self.average_processing_time = 0.0
        self.error_count = 0
        
        logger.info("🔧 Initializing model inference system")
    
    async def initialize(self) -> bool:
        """Initialize the inference system"""
        try:
            logger.info("🚀 Initializing inference system...")
            
            # Initialize ML pipeline
            await self.ml_pipeline.initialize()
            
            logger.info("✅ Inference system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize inference system: {e}")
            return False
    
    async def predict(self, request: InferenceRequest) -> InferenceResponse:
        """Make real-time predictions"""
        try:
            start_time = datetime.utcnow()
            
            # Generate request ID
            request_id = f"inf_{int(start_time.timestamp())}_{self.inference_count}"
            
            # Get current metrics
            cluster_metrics = await self.metrics_collector.collect_cluster_metrics()
            pod_metrics = await self.metrics_collector.collect_pod_metrics(
                namespace=request.namespace
            )
            
            # Filter pod metrics if specific workload/pod requested
            if request.workload_name:
                pod_metrics = [p for p in pod_metrics if request.workload_name in p.pod_name]
            elif request.pod_name:
                pod_metrics = [p for p in pod_metrics if p.pod_name == request.pod_name]
            
            # Extract features
            features_list = await self.ml_pipeline.extract_features(pod_metrics, cluster_metrics)
            
            # Make predictions
            predictions = {}
            
            if request.model_type in ["optimization", "all"]:
                for i, features in enumerate(features_list):
                    pred = await self.ml_pipeline.predict_optimization(features)
                    predictions[f"optimization_{i}"] = pred
            
            if request.model_type in ["prediction", "all"]:
                for i, features in enumerate(features_list):
                    pred = await self.ml_pipeline.predict_resource_usage(features)
                    predictions[f"prediction_{i}"] = pred
            
            if request.model_type in ["anomaly", "all"]:
                for i, features in enumerate(features_list):
                    pred = await self.ml_pipeline.detect_anomalies(features)
                    predictions[f"anomaly_{i}"] = pred
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update performance metrics
            self._update_performance_metrics(processing_time)
            
            # Get model versions
            model_versions = {
                "optimization": self.ml_pipeline.optimization_model.get_model_info().get("algorithm", "unknown"),
                "prediction": self.ml_pipeline.prediction_model.get_model_info().get("algorithm", "unknown"),
                "anomaly": self.ml_pipeline.anomaly_model.get_model_info().get("algorithm", "unknown")
            }
            
            response = InferenceResponse(
                request_id=request_id,
                cluster_id=request.cluster_id,
                timestamp=datetime.utcnow(),
                predictions=predictions,
                processing_time_ms=processing_time,
                model_versions=model_versions,
                metadata={
                    "feature_count": len(features_list),
                    "pod_count": len(pod_metrics),
                    "cluster_metrics": {
                        "cpu_usage": cluster_metrics.cpu_usage_percent,
                        "memory_usage": cluster_metrics.memory_usage_percent,
                        "pod_count": cluster_metrics.running_pods
                    }
                }
            )
            
            logger.info(f"✅ Inference completed: {len(predictions)} predictions in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Inference failed: {e}")
            self.error_count += 1
            raise
    
    async def batch_predict(self, request: BatchInferenceRequest) -> BatchInferenceResponse:
        """Make batch predictions for multiple workloads"""
        try:
            start_time = datetime.utcnow()
            
            # Generate request ID
            request_id = f"batch_{int(start_time.timestamp())}_{self.inference_count}"
            
            # Get cluster metrics
            cluster_metrics = await self.metrics_collector.collect_cluster_metrics()
            
            # Get all pod metrics
            all_pod_metrics = await self.metrics_collector.collect_pod_metrics()
            
            # Filter by namespaces if specified
            if request.namespaces:
                all_pod_metrics = [p for p in all_pod_metrics if p.namespace in request.namespaces]
            
            # Filter by workload names if specified
            if request.workload_names:
                filtered_metrics = []
                for pod in all_pod_metrics:
                    for workload_name in request.workload_names:
                        if workload_name in pod.pod_name:
                            filtered_metrics.append(pod)
                            break
                all_pod_metrics = filtered_metrics
            
            # Limit number of workloads if specified
            if request.max_workloads and len(all_pod_metrics) > request.max_workloads:
                all_pod_metrics = all_pod_metrics[:request.max_workloads]
            
            # Group pods by workload
            workload_groups = self._group_pods_by_workload(all_pod_metrics)
            
            # Make predictions for each workload
            all_predictions = {}
            processed_count = 0
            
            for workload_name, pods in workload_groups.items():
                try:
                    # Extract features for this workload
                    features_list = await self.ml_pipeline.extract_features(pods, cluster_metrics)
                    
                    workload_predictions = {}
                    
                    # Make predictions for each model type
                    model_types = request.model_types or ["optimization", "prediction", "anomaly"]
                    
                    for model_type in model_types:
                        if model_type == "optimization":
                            for i, features in enumerate(features_list):
                                pred = await self.ml_pipeline.predict_optimization(features)
                                workload_predictions[f"optimization_{i}"] = pred
                        
                        elif model_type == "prediction":
                            for i, features in enumerate(features_list):
                                pred = await self.ml_pipeline.predict_resource_usage(features)
                                workload_predictions[f"prediction_{i}"] = pred
                        
                        elif model_type == "anomaly":
                            for i, features in enumerate(features_list):
                                pred = await self.ml_pipeline.detect_anomalies(features)
                                workload_predictions[f"anomaly_{i}"] = pred
                    
                    all_predictions[workload_name] = workload_predictions
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process workload {workload_name}: {e}")
                    continue
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update performance metrics
            self._update_performance_metrics(processing_time)
            
            # Generate summary
            summary = self._generate_batch_summary(all_predictions)
            
            response = BatchInferenceResponse(
                request_id=request_id,
                cluster_id=request.cluster_id,
                timestamp=datetime.utcnow(),
                total_workloads=len(workload_groups),
                processed_workloads=processed_count,
                predictions=all_predictions,
                processing_time_ms=processing_time,
                summary=summary
            )
            
            logger.info(f"✅ Batch inference completed: {processed_count}/{len(workload_groups)} workloads in {processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Batch inference failed: {e}")
            self.error_count += 1
            raise
    
    def _group_pods_by_workload(self, pod_metrics: List[PodMetrics]) -> Dict[str, List[PodMetrics]]:
        """Group pods by workload name"""
        workload_groups = {}
        
        for pod in pod_metrics:
            # Extract workload name from pod name
            workload_name = self._extract_workload_name(pod.pod_name)
            
            if workload_name not in workload_groups:
                workload_groups[workload_name] = []
            
            workload_groups[workload_name].append(pod)
        
        return workload_groups
    
    def _extract_workload_name(self, pod_name: str) -> str:
        """Extract workload name from pod name"""
        # Remove pod-specific suffixes
        parts = pod_name.split('-')
        if len(parts) > 2:
            # Remove replica number and hash
            return '-'.join(parts[:-2])
        else:
            return pod_name
    
    def _generate_batch_summary(self, predictions: Dict[str, Dict[str, MLPrediction]]) -> Dict[str, Any]:
        """Generate summary of batch predictions"""
        summary = {
            "total_predictions": 0,
            "optimization_opportunities": 0,
            "anomalies_detected": 0,
            "average_confidence": 0.0,
            "model_breakdown": {}
        }
        
        total_confidence = 0.0
        confidence_count = 0
        
        for workload_name, workload_preds in predictions.items():
            summary["total_predictions"] += len(workload_preds)
            
            for pred_name, prediction in workload_preds.items():
                # Count optimization opportunities
                if "optimization" in pred_name and prediction.prediction_value > 0.5:
                    summary["optimization_opportunities"] += 1
                
                # Count anomalies
                if "anomaly" in pred_name and prediction.prediction_value:
                    summary["anomalies_detected"] += 1
                
                # Accumulate confidence
                if prediction.confidence > 0:
                    total_confidence += prediction.confidence
                    confidence_count += 1
                
                # Model breakdown
                model_type = prediction.model_name
                if model_type not in summary["model_breakdown"]:
                    summary["model_breakdown"][model_type] = 0
                summary["model_breakdown"][model_type] += 1
        
        if confidence_count > 0:
            summary["average_confidence"] = total_confidence / confidence_count
        
        return summary
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance metrics"""
        self.inference_count += 1
        
        # Update average processing time
        if self.inference_count == 1:
            self.average_processing_time = processing_time
        else:
            self.average_processing_time = (
                (self.average_processing_time * (self.inference_count - 1) + processing_time) /
                self.inference_count
            )
    
    async def get_inference_metrics(self) -> Dict[str, Any]:
        """Get inference performance metrics"""
        return {
            "total_inferences": self.inference_count,
            "average_processing_time_ms": self.average_processing_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.inference_count, 1),
            "cache_hit_rate": 0.0,  # TODO: Implement cache metrics
            "models_loaded": [
                "optimization_model",
                "prediction_model",
                "anomaly_model"
            ]
        }
    
    async def clear_cache(self):
        """Clear inference cache"""
        self._cache.clear()
        logger.info("✅ Inference cache cleared")
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            "optimization_model": {
                "status": "loaded" if self.ml_pipeline.optimization_model.is_trained else "not_loaded",
                "algorithm": self.ml_pipeline.optimization_model.get_model_info().get("algorithm", "unknown"),
                "feature_count": len(self.ml_pipeline.optimization_model.feature_names)
            },
            "prediction_model": {
                "status": "loaded" if self.ml_pipeline.prediction_model.is_trained else "not_loaded",
                "algorithm": self.ml_pipeline.prediction_model.get_model_info().get("algorithm", "unknown"),
                "feature_count": len(self.ml_pipeline.prediction_model.feature_names)
            },
            "anomaly_model": {
                "status": "loaded" if self.ml_pipeline.anomaly_model.is_trained else "not_loaded",
                "algorithm": self.ml_pipeline.anomaly_model.get_model_info().get("algorithm", "unknown"),
                "feature_count": len(self.ml_pipeline.anomaly_model.feature_names)
            }
        } 