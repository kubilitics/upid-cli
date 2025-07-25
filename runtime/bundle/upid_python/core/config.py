"""
Configuration management for UPID CLI
Handles settings, environment variables, and user preferences
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Config:
    """Configuration management for UPID CLI"""
    
    # API Configuration
    api_url: str = "https://api.upid.io"
    api_timeout: int = 30
    api_retries: int = 3
    
    # Authentication
    auth_token: Optional[str] = None
    auth_refresh_token: Optional[str] = None
    auth_expires_at: Optional[datetime] = None
    
    # Output Configuration
    output_format: str = "table"  # table, json, yaml, csv
    verbose: bool = False
    debug: bool = False
    quiet: bool = False
    
    # Cluster Configuration
    default_cluster: Optional[str] = None
    default_namespace: str = "default"
    
    # Analysis Configuration
    analysis_timeout: int = 300  # 5 minutes
    analysis_confidence_threshold: float = 0.85
    analysis_include_costs: bool = True
    
    # Optimization Configuration
    optimization_safety_level: str = "medium"  # low, medium, high
    optimization_auto_confirm: bool = False
    optimization_max_parallel: int = 5
    
    # Monitoring Configuration
    monitoring_interval: int = 60  # seconds
    monitoring_alerts_enabled: bool = True
    monitoring_retention_days: int = 30
    
    # Enterprise Features
    enterprise_enabled: bool = False
    enterprise_org_id: Optional[str] = None
    enterprise_sso_enabled: bool = False
    
    # ML/AI Configuration
    ml_models_enabled: bool = True
    ml_prediction_horizon: int = 7  # days
    ml_anomaly_detection: bool = True
    
    # Mock Mode Configuration
    mock_mode: bool = False
    mock_scenario: str = "production"  # production, staging, development
    
    # File paths
    config_file: Optional[Path] = None
    cache_dir: Optional[Path] = None
    log_file: Optional[Path] = None
    
    def __post_init__(self):
        """Initialize configuration after object creation"""
        self._load_from_environment()
        self._setup_paths()
        self._load_from_file()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'UPID_API_URL': 'api_url',
            'UPID_API_TIMEOUT': 'api_timeout',
            'UPID_AUTH_TOKEN': 'auth_token',
            'UPID_OUTPUT_FORMAT': 'output_format',
            'UPID_VERBOSE': 'verbose',
            'UPID_DEBUG': 'debug',
            'UPID_QUIET': 'quiet',
            'UPID_DEFAULT_CLUSTER': 'default_cluster',
            'UPID_DEFAULT_NAMESPACE': 'default_namespace',
            'UPID_ANALYSIS_TIMEOUT': 'analysis_timeout',
            'UPID_ANALYSIS_CONFIDENCE': 'analysis_confidence_threshold',
            'UPID_OPTIMIZATION_SAFETY': 'optimization_safety_level',
            'UPID_MONITORING_INTERVAL': 'monitoring_interval',
            'UPID_ENTERPRISE_ENABLED': 'enterprise_enabled',
            'UPID_ML_ENABLED': 'ml_models_enabled',
            'UPID_MOCK_MODE': 'mock_mode',
            'UPID_MOCK_SCENARIO': 'mock_scenario',
        }
        
        for env_var, attr_name in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert types appropriately
                if attr_name in ['api_timeout', 'api_retries', 'analysis_timeout', 
                               'optimization_max_parallel', 'monitoring_interval', 
                               'monitoring_retention_days', 'ml_prediction_horizon']:
                    try:
                        setattr(self, attr_name, int(value))
                    except ValueError:
                        pass
                elif attr_name in ['analysis_confidence_threshold']:
                    try:
                        setattr(self, attr_name, float(value))
                    except ValueError:
                        pass
                elif attr_name in ['verbose', 'debug', 'quiet', 'analysis_include_costs',
                                 'optimization_auto_confirm', 'monitoring_alerts_enabled',
                                 'enterprise_enabled', 'enterprise_sso_enabled',
                                 'ml_models_enabled', 'ml_anomaly_detection']:
                    setattr(self, attr_name, value.lower() in ['true', '1', 'yes'])
                else:
                    setattr(self, attr_name, value)
    
    def _setup_paths(self):
        """Setup configuration and cache directories"""
        home = Path.home()
        upid_dir = home / ".upid"
        upid_dir.mkdir(exist_ok=True)
        
        if self.config_file is None:
            self.config_file = upid_dir / "config.yaml"
        
        if self.cache_dir is None:
            self.cache_dir = upid_dir / "cache"
            self.cache_dir.mkdir(exist_ok=True)
        
        if self.log_file is None:
            self.log_file = upid_dir / "upid.log"
    
    def _load_from_file(self):
        """Load configuration from file"""
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.suffix == '.json':
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f)
                
                if data:
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                if self.debug:
                    print(f"Warning: Failed to load config file: {e}")
    
    def save(self):
        """Save current configuration to file"""
        if self.config_file:
            try:
                # Convert to dict, excluding non-serializable objects
                config_dict = {}
                for key, value in self.__dict__.items():
                    if key not in ['config_file', 'cache_dir', 'log_file']:
                        if isinstance(value, datetime):
                            config_dict[key] = value.isoformat()
                        elif isinstance(value, Path):
                            config_dict[key] = str(value)
                        else:
                            config_dict[key] = value
                
                with open(self.config_file, 'w') as f:
                    yaml.dump(config_dict, f, default_flow_style=False)
            except Exception as e:
                if self.debug:
                    print(f"Warning: Failed to save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        if hasattr(self, key):
            setattr(self, key, value)
            self.save()
        else:
            raise ValueError(f"Unknown configuration key: {key}")
    
    def reset(self):
        """Reset configuration to defaults"""
        # Create a new instance with defaults
        new_config = Config()
        for key, value in new_config.__dict__.items():
            if key not in ['config_file', 'cache_dir', 'log_file']:
                setattr(self, key, value)
        self.save()
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Validate API URL
        if not self.api_url.startswith(('http://', 'https://')):
            errors.append("api_url must be a valid HTTP/HTTPS URL")
        
        # Validate timeout values
        if self.api_timeout <= 0:
            errors.append("api_timeout must be positive")
        
        if self.analysis_timeout <= 0:
            errors.append("analysis_timeout must be positive")
        
        # Validate confidence threshold
        if not 0.0 <= self.analysis_confidence_threshold <= 1.0:
            errors.append("analysis_confidence_threshold must be between 0.0 and 1.0")
        
        # Validate safety level
        if self.optimization_safety_level not in ['low', 'medium', 'high']:
            errors.append("optimization_safety_level must be one of: low, medium, high")
        
        # Validate output format
        if self.output_format not in ['table', 'json', 'yaml', 'csv']:
            errors.append("output_format must be one of: table, json, yaml, csv")
        
        if errors:
            if self.debug:
                for error in errors:
                    print(f"Configuration error: {error}")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if key not in ['config_file', 'cache_dir', 'log_file']:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Path):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"UPID Config (API: {self.api_url}, Format: {self.output_format})"


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config):
    """Set global configuration instance"""
    global _global_config
    _global_config = config 