"""
UPID CLI - Universal Pod Intelligence Director
Enterprise-grade Kubernetes cost optimization platform
"""

__version__ = "1.0.0"
__title__ = "UPID CLI"
__author__ = "UPID Team"
__description__ = "Universal Pod Intelligence Director - Kubernetes optimization platform"

# Export main components
from .cli import cli

__all__ = ["cli", "__version__"]