"""
Configuration management for UPID CLI
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class Config:
    """Configuration manager for UPID CLI"""
    
    DEFAULTS = {
        'api_url': 'https://api.upid.io',
        'api_version': 'v1',
        'timeout': 30,
        'verbose': False,
        'output_format': 'table',
        'color_output': True,
        'optimization_strategy': 'balanced',
        'safety_level': 'strict',
        'cost_model': 'aws',
        'currency': 'USD',
        'default_cluster': None,
        'notification_channels': [],
        'local_mode': False,
        'auth_token': None,
        'user_email': None,
        'organization': None,
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.upid/config.yaml")
        self.config_dir = Path(self.config_path).parent
        self._config_file = Path(self.config_path)
        self._config = self._load_config()
        # Force api_url to default if not set or set to export.upid.io
        if not self._config.get('api_url') or self._config.get('api_url') == 'https://export.upid.io':
            self._config['api_url'] = self.DEFAULTS['api_url']
        self.auth_file = str(self.config_dir / 'auth.json')
        self._auth = {}
        self.notification_channels = self._config.get('notification_channels', [])
    
    @property
    def config_file(self) -> Path:
        return self._config_file
    
    @config_file.setter
    def config_file(self, value: Path):
        self._config_file = value
        # Reload config from the new file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    if str(self.config_file).endswith('.json'):
                        return json.load(f)
                    else:
                        return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'api_url': os.getenv('UPID_API_URL', 'https://api.upid.io'),
            'api_version': os.getenv('UPID_API_VERSION', 'v1'),
            'api_key': os.getenv('UPID_API_KEY', ''),
            'cluster_name': os.getenv('UPID_CLUSTER_NAME', 'default'),
            'auth_token': '',
            'default_cluster': '',
            'optimization_strategy': 'balanced',
            'safety_level': 'strict',
            'cost_model': 'aws',
            'currency': 'USD',
            'verbose': False,
            'output_format': 'table',
            'color_output': True,
            'timeout': 30,
            'notification_channels': [],
            'zero_pod': {
                'enabled': True,
                'idle_threshold': '30m',
                'min_replicas': 0,
                'max_replicas': 10
            },
            'optimization': {
                'cpu_threshold': 0.8,
                'memory_threshold': 0.8,
                'cost_savings_threshold': 0.2
            },
            'local_mode': False,
            'user_email': None,
            'organization': None,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        if key == 'optimization_strategy' and not value:
            return 'balanced'
        if key == 'safety_level' and not value:
            return 'strict'
        if key == 'cost_model' and not value:
            return 'aws'
        if key == 'currency' and not value:
            return 'USD'
        if key == 'output_format' and not value:
            return 'table'
        if key == 'api_version' and not value:
            return 'v1'
        if key == 'api_url' and not value:
            return 'https://api.upid.io'
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def reload_config(self) -> None:
        """Reload configuration from file"""
        self._config = self._load_config()
    
    # Methods expected by tests
    def set_auth_token(self, token: str) -> None:
        self._config['auth_token'] = token
        self.save_config()
    def get_auth_token(self) -> Optional[str]:
        token = self._config.get('auth_token', None)
        if not token:
            return None
        return token
    def set_default_cluster(self, cluster: str) -> None:
        self._config['default_cluster'] = cluster
        self.save_config()
    def set_optimization_strategy(self, strategy: str) -> None:
        self._config['optimization_strategy'] = strategy
        self.save_config()
    def set_safety_level(self, level: str) -> None:
        self._config['safety_level'] = level
        self.save_config()
    def set_cost_model(self, model: str) -> None:
        self._config['cost_model'] = model
        self.save_config()
    def set_currency(self, currency: str) -> None:
        self._config['currency'] = currency
        self.save_config()
    def set_verbose(self, verbose: bool) -> None:
        self._config['verbose'] = verbose
        self.save_config()
    def set_output_format(self, fmt: str) -> None:
        self._config['output_format'] = fmt
        self.save_config()
    def set_color_output(self, color: bool) -> None:
        self._config['color_output'] = color
        self.save_config()
    def set_timeout(self, timeout: int) -> None:
        self._config['timeout'] = timeout
        self.save_config()
    def add_notification_channel(self, channel: str) -> None:
        channels = self._config.get('notification_channels', [])
        if channel not in channels:
            channels.append(channel)
            self._config['notification_channels'] = channels
            self.save_config()
    def export_config(self, export_path: str) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    def import_config(self, import_path: str) -> None:
        with open(import_path, 'r') as f:
            self._config = json.load(f)
        self.save_config()
    def reset(self) -> None:
        self._config = self._get_default_config()
        self.save_config()
    # For test compatibility
    def get_api_url(self) -> str:
        return self.get('api_url', 'https://api.upid.io')
    def get_api_key(self) -> str:
        return self.get('api_key', '')
    def get_cluster_name(self) -> str:
        return self.get('cluster_name', 'default')
    def is_debug(self) -> bool:
        return self.get('debug', False)

    def is_authenticated(self):
        token = self.get_auth_token()
        return bool(token)

    def reset_config(self):
        self._config = self._get_default_config()
        self._auth = {}
        self.save_config()
        self.save_auth()

    def get_default_cluster(self):
        return self._config.get('default_cluster')

    def get_optimization_strategy(self):
        return self._config.get('optimization_strategy') or 'balanced'

    def get_safety_level(self):
        return self._config.get('safety_level') or 'strict'

    def get_cost_model(self):
        return self._config.get('cost_model') or 'aws'

    def get_currency(self):
        return self._config.get('currency') or 'USD'

    def is_verbose(self):
        return self._config.get('verbose', False)

    def get_output_format(self):
        return self._config.get('output_format') or 'table'

    def is_color_output(self):
        return self._config.get('color_output', True)

    def get_timeout(self):
        return self._config.get('timeout')

    def get_notification_channels(self):
        return self._config.get('notification_channels', [])

    def remove_notification_channel(self, channel):
        channels = self._config.get('notification_channels', [])
        if channel in channels:
            channels.remove(channel)
            self._config['notification_channels'] = channels
            self.save_config()

    def save_auth(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(str(self.auth_file), 'w') as f:
                json.dump(self._auth, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save auth: {e}")

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(str(self.config_file), 'r') as f:
                    self._config = json.load(f)
            except Exception:
                self._config = self._get_default_config()
        else:
            self._config = self._get_default_config()

    def load_auth(self):
        if Path(self.auth_file).exists():
            try:
                with open(str(self.auth_file), 'r') as f:
                    self._auth = json.load(f)
            except Exception:
                self._auth = {}
        else:
            self._auth = {}

    def clear_auth_token(self):
        self._config['auth_token'] = ''
        self.save_config()

    def is_local_mode(self) -> bool:
        """Check if local mode is enabled"""
        return self._config.get('local_mode', False)

    def enable_local_mode(self) -> None:
        """Enable local mode for testing"""
        self._config['local_mode'] = True
        self.save_config()

    def disable_local_mode(self) -> None:
        """Disable local mode"""
        self._config['local_mode'] = False
        self.save_config()
