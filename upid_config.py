#!/usr/bin/env python3
"""
UPID CLI - Centralized Configuration System
Provides centralized management of product metadata, version info, and configuration
Enables seamless product releases by changing values in one place
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """Product information and metadata"""
    name: str = "UPID CLI"
    description: str = "Universal Prometheus Infrastructure Discovery - Kubernetes Cost Optimization CLI"
    version: str = "1.0.0"
    build_version: str = "1.0.0-stable"
    api_version: str = "v2"
    author: str = "UPID Development Team"
    author_email: str = "dev@upid.io"
    maintainer: str = "UPID Team"
    maintainer_email: str = "support@upid.io"
    license: str = "MIT"
    homepage: str = "https://upid.io"
    repository: str = "https://github.com/upid/upid-cli"
    documentation: str = "https://docs.upid.io"
    support_email: str = "support@upid.io"
    sales_email: str = "sales@upid.io"
    copyright_year: str = "2024"
    copyright_notice: str = "© 2024 UPID Development Team. All rights reserved."


@dataclass
class APIConfig:
    """API configuration settings"""
    base_url: str = "http://localhost:8000"
    api_prefix: str = "/api/v2"
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    refresh_token_expiry_days: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    default_url: str = "sqlite:///upid.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False


@dataclass
class KubernetesConfig:
    """Kubernetes client configuration"""
    config_file: str = "~/.kube/config"
    context: Optional[str] = None
    namespace: str = "default"
    timeout_seconds: int = 60
    request_timeout: int = 30
    verify_ssl: bool = True
    debug: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_enabled: bool = True
    file_path: str = "upid.log"
    file_max_bytes: int = 10485760  # 10MB
    file_backup_count: int = 5
    console_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    secret_key: str = "upid-secret-key-change-in-production"
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    session_timeout_minutes: int = 60
    max_failed_login_attempts: int = 5
    lockout_duration_minutes: int = 15


@dataclass
class MockDataConfig:
    """Mock data configuration settings"""
    enabled: bool = False
    scenario: str = "production"
    seed: int = 42
    cache_enabled: bool = True
    cache_ttl_minutes: int = 15


@dataclass
class UIConfig:
    """User interface configuration"""
    theme: str = "auto"  # auto, light, dark
    color_enabled: bool = True
    progress_bars: bool = True
    table_format: str = "table"  # table, json, yaml, csv
    max_table_rows: int = 100
    show_timestamps: bool = True
    timezone: str = "UTC"


@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality"""
    ai_optimization: bool = True
    cost_analysis: bool = True
    idle_detection: bool = True
    anomaly_detection: bool = True
    auto_scaling: bool = True
    multi_cluster: bool = True
    cloud_billing: bool = True
    dashboard: bool = True
    telemetry: bool = False
    plugins: bool = False


@dataclass
class UPIDConfig:
    """Master UPID configuration containing all settings"""
    product: ProductInfo
    api: APIConfig
    database: DatabaseConfig
    kubernetes: KubernetesConfig
    logging: LoggingConfig
    security: SecurityConfig
    mock_data: MockDataConfig
    ui: UIConfig
    features: FeatureFlags
    
    @property
    def version(self) -> str:
        """Get product version"""
        return self.product.version
    
    @property
    def author(self) -> str:
        """Get product author"""
        return self.product.author
    
    @property
    def author_email(self) -> str:
        """Get author email"""
        return self.product.author_email
    
    @property
    def full_version(self) -> str:
        """Get full version string"""
        return f"{self.product.name} v{self.product.version}"
    
    @property
    def api_base_url(self) -> str:
        """Get complete API base URL"""
        return f"{self.api.base_url}{self.api.api_prefix}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class ConfigurationManager:
    """Centralized configuration manager for UPID CLI"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self._config: Optional[UPIDConfig] = None
        self._config_file = config_file or self._get_default_config_file()
        self._env_prefix = "UPID_"
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path"""
        # Try multiple locations in order of preference
        config_locations = [
            os.environ.get("UPID_CONFIG_FILE"),
            os.path.expanduser("~/.upid/config.json"),
            "/etc/upid/config.json",
            "./upid_config.json"
        ]
        
        for location in config_locations:
            if location and Path(location).exists():
                return location
        
        # Return the user config location as default
        return os.path.expanduser("~/.upid/config.json")
    
    def load_config(self) -> UPIDConfig:
        """Load configuration from file and environment variables"""
        if self._config is not None:
            return self._config
        
        # Start with default configuration
        config_dict = self._get_default_config()
        
        # Override with file configuration if exists
        if Path(self._config_file).exists():
            try:
                with open(self._config_file, 'r') as f:
                    file_config = json.load(f)
                    config_dict = self._deep_merge(config_dict, file_config)
                self.logger.debug(f"Loaded configuration from {self._config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file {self._config_file}: {e}")
        
        # Override with environment variables
        env_config = self._load_from_environment()
        config_dict = self._deep_merge(config_dict, env_config)
        
        # Create configuration object
        self._config = self._dict_to_config(config_dict)
        return self._config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration as dictionary"""
        return {
            "product": asdict(ProductInfo()),
            "api": asdict(APIConfig()),
            "database": asdict(DatabaseConfig()),
            "kubernetes": asdict(KubernetesConfig()),
            "logging": asdict(LoggingConfig()),
            "security": asdict(SecurityConfig()),
            "mock_data": asdict(MockDataConfig()),
            "ui": asdict(UIConfig()),
            "features": asdict(FeatureFlags())
        }
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration values from environment variables"""
        env_config = {}
        
        # Define environment variable mappings
        env_mappings = {
            f"{self._env_prefix}VERSION": ["product", "version"],
            f"{self._env_prefix}BUILD_VERSION": ["product", "build_version"],
            f"{self._env_prefix}AUTHOR": ["product", "author"],
            f"{self._env_prefix}AUTHOR_EMAIL": ["product", "author_email"],
            f"{self._env_prefix}API_BASE_URL": ["api", "base_url"],
            f"{self._env_prefix}API_TIMEOUT": ["api", "timeout_seconds"],
            f"{self._env_prefix}DATABASE_URL": ["database", "default_url"],
            f"{self._env_prefix}KUBECONFIG": ["kubernetes", "config_file"],
            f"{self._env_prefix}KUBE_CONTEXT": ["kubernetes", "context"],
            f"{self._env_prefix}KUBE_NAMESPACE": ["kubernetes", "namespace"],
            f"{self._env_prefix}LOG_LEVEL": ["logging", "level"],
            f"{self._env_prefix}LOG_FILE": ["logging", "file_path"],
            f"{self._env_prefix}SECRET_KEY": ["security", "secret_key"],
            f"{self._env_prefix}MOCK_MODE": ["mock_data", "enabled"],
            f"{self._env_prefix}MOCK_SCENARIO": ["mock_data", "scenario"],
            f"{self._env_prefix}UI_THEME": ["ui", "theme"],
            f"{self._env_prefix}UI_COLOR": ["ui", "color_enabled"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert string values to appropriate types
                value = self._convert_env_value(value)
                self._set_nested_value(env_config, config_path, value)
        
        return env_config
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], path: list, value: Any):
        """Set nested dictionary value using path list"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> UPIDConfig:
        """Convert dictionary to UPIDConfig object"""
        return UPIDConfig(
            product=ProductInfo(**config_dict["product"]),
            api=APIConfig(**config_dict["api"]),
            database=DatabaseConfig(**config_dict["database"]),
            kubernetes=KubernetesConfig(**config_dict["kubernetes"]),
            logging=LoggingConfig(**config_dict["logging"]),
            security=SecurityConfig(**config_dict["security"]),
            mock_data=MockDataConfig(**config_dict["mock_data"]),
            ui=UIConfig(**config_dict["ui"]),
            features=FeatureFlags(**config_dict["features"])
        )
    
    def save_config(self, config: Optional[UPIDConfig] = None) -> bool:
        """Save configuration to file"""
        config = config or self._config
        if config is None:
            self.logger.error("No configuration to save")
            return False
        
        try:
            # Ensure directory exists
            config_dir = Path(self._config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self._config_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2, default=str)
            
            self.logger.info(f"Configuration saved to {self._config_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_config(self) -> UPIDConfig:
        """Get current configuration (loads if not already loaded)"""
        return self.load_config()
    
    def reload_config(self) -> UPIDConfig:
        """Reload configuration from file and environment"""
        self._config = None
        return self.load_config()
    
    def update_config(self, **kwargs) -> bool:
        """Update configuration values and save"""
        config = self.get_config()
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")
        
        return self.save_config(config)


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager(config_file: Optional[str] = None) -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_file)
    return _config_manager


def get_config() -> UPIDConfig:
    """Get current UPID configuration"""
    return get_config_manager().get_config()


def get_version() -> str:
    """Get UPID version"""
    return get_config().version


def get_author() -> str:
    """Get UPID author"""
    return get_config().author


def get_author_email() -> str:
    """Get UPID author email"""
    return get_config().author_email


def get_full_version() -> str:
    """Get full UPID version string"""
    return get_config().full_version


def get_api_base_url() -> str:
    """Get API base URL"""
    return get_config().api_base_url


def get_product_info() -> ProductInfo:
    """Get product information"""
    return get_config().product


def is_mock_mode() -> bool:
    """Check if mock mode is enabled"""
    return get_config().mock_data.enabled


def get_mock_scenario() -> str:
    """Get mock data scenario"""
    return get_config().mock_data.scenario


# Convenience functions for CLI usage
def print_version_info():
    """Print version information"""
    config = get_config()
    print(f"{config.product.name} {config.product.version}")
    print(f"Build: {config.product.build_version}")
    print(f"Author: {config.product.author} <{config.product.author_email}>")
    print(f"Homepage: {config.product.homepage}")
    print(f"License: {config.product.license}")


def print_config_info():
    """Print configuration information"""
    config = get_config()
    print("UPID Configuration:")
    print(f"  Config File: {get_config_manager()._config_file}")
    print(f"  Version: {config.version}")
    print(f"  API URL: {config.api_base_url}")
    print(f"  Mock Mode: {'Enabled' if config.mock_data.enabled else 'Disabled'}")
    print(f"  Log Level: {config.logging.level}")
    print(f"  Theme: {config.ui.theme}")


if __name__ == "__main__":
    # Test configuration system
    print("Testing UPID Configuration System")
    print("=" * 50)
    
    config = get_config()
    print_version_info()
    print()
    print_config_info()
    print()
    print("Configuration JSON:")
    print(config.to_json())