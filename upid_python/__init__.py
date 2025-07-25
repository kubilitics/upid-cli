"""
UPID CLI - Universal Pod Intelligence Director
Enterprise-grade Kubernetes cost optimization platform with ML-powered insights
"""

# Import centralized configuration
try:
    from ..upid_config import get_version, get_author, get_author_email
    __version__ = get_version()
    __author__ = get_author()
    __email__ = get_author_email()
except ImportError:
    # Fallback values if config system not available
    __version__ = "2.0.0"
    __author__ = "UPID Team"
    __email__ = "hello@kubilitics.com"

from .cli import cli
from .core.config import Config
from .core.auth import AuthManager
from .core.api_client import UPIDAPIClient

__all__ = [
    "cli",
    "Config", 
    "AuthManager",
    "UPIDAPIClient"
] 