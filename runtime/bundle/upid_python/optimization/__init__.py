"""
UPID CLI - Optimization Engine
Enterprise-grade Kubernetes optimization and cost reduction system
"""

__version__ = "1.0.0"
__author__ = "UPID Team"
__email__ = "support@upid.io"

from .zero_pod_scaler import ZeroPodScaler
from .resource_rightsizer import ResourceRightsizer
from .cost_optimizer import CostOptimizer
from .safety_manager import SafetyManager
from .optimization_engine import OptimizationEngine

__all__ = [
    "ZeroPodScaler",
    "ResourceRightsizer", 
    "CostOptimizer",
    "SafetyManager",
    "OptimizationEngine"
] 