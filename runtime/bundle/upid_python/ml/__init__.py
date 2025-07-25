"""
UPID CLI - Machine Learning Module
Enterprise-grade ML pipeline for Kubernetes optimization and cost prediction
"""

__version__ = "1.0.0"
__author__ = "UPID Team"
__email__ = "support@upid.io"

from .pipeline import MLPipeline
from .training import ModelTrainer
from .inference import ModelInference
from .models.optimization import OptimizationModel
from .models.prediction import PredictionModel
from .models.anomaly import AnomalyDetectionModel

__all__ = [
    "MLPipeline",
    "ModelTrainer", 
    "ModelInference",
    "OptimizationModel",
    "PredictionModel",
    "AnomalyDetectionModel"
] 