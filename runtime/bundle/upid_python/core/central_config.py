#!/usr/bin/env python3
"""
UPID CLI - Central Configuration Loader
Provides easy access to centralized configuration across all modules
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global configuration cache
_config_cache: Optional[object] = None


def get_upid_config():
    """Get the global UPID configuration with caching"""
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    try:
        # Try to import from parent level
        from ...upid_config import get_config
        _config_cache = get_config()
        return _config_cache
    except ImportError:
        try:
            # Try alternative import path
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from upid_config import get_config
            _config_cache = get_config()
            return _config_cache
        except ImportError:
            logger.warning("Could not load centralized configuration, using fallback values")
            return None


def get_version() -> str:
    """Get product version"""
    config = get_upid_config()
    return config.version if config else "2.0.0"


def get_author() -> str:
    """Get product author"""
    config = get_upid_config()
    return config.author if config else "UPID Team"


def get_author_email() -> str:
    """Get author email"""
    config = get_upid_config()
    return config.author_email if config else "hello@kubilitics.com"


def get_product_name() -> str:
    """Get product name"""
    config = get_upid_config()
    return config.product.name if config else "UPID CLI"


def get_description() -> str:
    """Get product description"""
    config = get_upid_config()
    return config.product.description if config else "Universal Pod Intelligence Director"


def get_homepage() -> str:
    """Get product homepage"""
    config = get_upid_config()
    return config.product.homepage if config else "https://upid.io"


def get_repository() -> str:
    """Get product repository"""
    config = get_upid_config()
    return config.product.repository if config else "https://github.com/upid/upid-cli"


def get_support_email() -> str:
    """Get support email"""
    config = get_upid_config()
    return config.product.support_email if config else "support@upid.io"


def get_full_version() -> str:
    """Get full version string"""
    config = get_upid_config()
    return config.full_version if config else f"{get_product_name()} v{get_version()}"


def get_api_base_url() -> str:
    """Get API base URL"""
    config = get_upid_config()
    return config.api_base_url if config else "http://localhost:8000/api/v2"


def is_mock_mode() -> bool:
    """Check if mock mode is enabled"""
    config = get_upid_config()
    return config.mock_data.enabled if config else False


def get_mock_scenario() -> str:
    """Get mock data scenario"""
    config = get_upid_config()
    return config.mock_data.scenario if config else "production"


# Convenience decorator for modules that need configuration
def with_config(func):
    """Decorator to inject configuration into function calls"""
    def wrapper(*args, **kwargs):
        if 'config' not in kwargs:
            kwargs['config'] = get_upid_config()
        return func(*args, **kwargs)
    return wrapper


# Module metadata helper
def get_module_metadata():
    """Get standardized module metadata"""
    return {
        "__version__": get_version(),
        "__author__": get_author(),
        "__email__": get_author_email(),
    }


def update_module_globals(module_globals: dict):
    """Update module globals with centralized configuration values"""
    metadata = get_module_metadata()
    for key, value in metadata.items():
        if key in module_globals:
            module_globals[key] = value


# Export all functions for easy import
__all__ = [
    "get_upid_config",
    "get_version",
    "get_author", 
    "get_author_email",
    "get_product_name",
    "get_description",
    "get_homepage",
    "get_repository",
    "get_support_email",
    "get_full_version",
    "get_api_base_url",
    "is_mock_mode",
    "get_mock_scenario",
    "with_config",
    "get_module_metadata",
    "update_module_globals"
]