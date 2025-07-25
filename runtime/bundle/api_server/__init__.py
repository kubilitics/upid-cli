"""
UPID CLI API Server
Enterprise Kubernetes Cost Optimization Platform

This package contains the FastAPI backend server for UPID CLI,
providing REST API endpoints for cluster analysis, optimization,
and business intelligence reporting.
"""

# Import centralized configuration
try:
    from ..upid_config import get_version, get_author, get_config
    config = get_config()
    __version__ = get_version()
    __author__ = get_author()
    __email__ = config.product.support_email
except ImportError:
    # Fallback values if config system not available
    __version__ = "1.0.0"
    __author__ = "UPID Development Team"
    __email__ = "support@upid.io"

# API Server metadata
try:
    from ..upid_config import get_config
    config = get_config()
    API_TITLE = f"{config.product.name} API Server"
    API_DESCRIPTION = config.product.description
    API_VERSION = config.product.api_version
except ImportError:
    API_TITLE = "UPID CLI API Server"
    API_DESCRIPTION = "Enterprise Kubernetes Cost Optimization Platform"
    API_VERSION = __version__