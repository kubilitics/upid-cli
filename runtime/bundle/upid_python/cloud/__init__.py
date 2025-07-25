"""
UPID CLI - Cloud Cost Integration
Enterprise-grade cloud billing and cost management for Kubernetes clusters
"""

# Import centralized configuration
try:
    from ...upid_config import get_version, get_author, get_config
    config = get_config()
    __version__ = get_version()
    __author__ = get_author()
    __email__ = config.product.support_email
except ImportError:
    # Fallback values if config system not available
    __version__ = "1.0.0"
    __author__ = "UPID Team"
    __email__ = "support@upid.io"

from .aws.billing import AWSBillingClient
from .aws.resources import AWSResourceMapper
from .gcp.billing import GCPBillingClient
from .gcp.resources import GCPResourceMapper
from .azure.billing import AzureBillingClient
from .azure.resources import AzureResourceMapper
from .cost_manager import CloudCostManager

__all__ = [
    "AWSBillingClient",
    "AWSResourceMapper",
    "GCPBillingClient", 
    "GCPResourceMapper",
    "AzureBillingClient",
    "AzureResourceMapper",
    "CloudCostManager"
] 