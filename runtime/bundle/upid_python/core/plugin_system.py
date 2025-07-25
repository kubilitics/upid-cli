"""
Integration & Plugin System for UPID CLI
Provides webhook system, plugin architecture, third-party integrations, and API versioning
"""

import os
import sys
import json
import time
import importlib
import inspect
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import requests
from pathlib import Path
import yaml
import hashlib

# Optional imports with fallbacks
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None


class PluginType(Enum):
    """Plugin type enumeration"""
    WEBHOOK = "webhook"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"
    REPORTING = "reporting"
    CUSTOM = "custom"


class WebhookEvent(Enum):
    """Webhook event types"""
    OPTIMIZATION_COMPLETED = "optimization_completed"
    CLUSTER_HEALTH_CHANGED = "cluster_health_changed"
    COST_THRESHOLD_EXCEEDED = "cost_threshold_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    USER_ACTION = "user_action"
    SYSTEM_ALERT = "system_alert"


@dataclass
class PluginInfo:
    """Plugin information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    entry_point: str
    config_schema: Dict[str, Any]
    dependencies: List[str]
    enabled: bool = True
    last_updated: datetime = None


@dataclass
class WebhookConfig:
    """Webhook configuration"""
    url: str
    events: List[WebhookEvent]
    headers: Dict[str, str]
    timeout: int = 30
    retry_count: int = 3
    enabled: bool = True
    secret: str = None


@dataclass
class APIVersion:
    """API version information"""
    version: str
    status: str  # "stable", "beta", "deprecated"
    release_date: datetime
    deprecation_date: Optional[datetime] = None
    breaking_changes: List[str] = None
    new_features: List[str] = None


class PluginManager:
    """Plugin management system"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_hooks: Dict[str, List[Callable]] = {}
        
        # Load plugins
        self._discover_plugins()
        self._load_plugins()
    
    def _discover_plugins(self):
        """Discover available plugins"""
        if not self.plugins_dir.exists():
            return
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_file = plugin_dir / "manifest.yaml"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = yaml.safe_load(f)
                        
                        plugin_info = PluginInfo(
                            name=manifest.get('name', plugin_dir.name),
                            version=manifest.get('version', '1.0.0'),
                            description=manifest.get('description', ''),
                            author=manifest.get('author', ''),
                            plugin_type=PluginType(manifest.get('type', 'custom')),
                            entry_point=manifest.get('entry_point', 'main.py'),
                            config_schema=manifest.get('config_schema', {}),
                            dependencies=manifest.get('dependencies', []),
                            enabled=manifest.get('enabled', True),
                            last_updated=datetime.now()
                        )
                        
                        self.plugins[plugin_info.name] = plugin_info
                        self.logger.info(f"Discovered plugin: {plugin_info.name} v{plugin_info.version}")
                        
                    except Exception as e:
                        self.logger.error(f"Error loading plugin manifest {manifest_file}: {e}")
    
    def _load_plugins(self):
        """Load enabled plugins"""
        for plugin_name, plugin_info in self.plugins.items():
            if plugin_info.enabled:
                try:
                    self._load_plugin(plugin_name, plugin_info)
                except Exception as e:
                    self.logger.error(f"Error loading plugin {plugin_name}: {e}")
    
    def _load_plugin(self, plugin_name: str, plugin_info: PluginInfo):
        """Load a specific plugin"""
        plugin_path = self.plugins_dir / plugin_name / plugin_info.entry_point
        
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin entry point not found: {plugin_path}")
        
        # Add plugin directory to Python path
        plugin_dir = self.plugins_dir / plugin_name
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))
        
        # Import plugin module
        module_name = plugin_info.entry_point.replace('.py', '')
        plugin_module = importlib.import_module(module_name)
        
        # Look for plugin class or function
        plugin_instance = None
        if hasattr(plugin_module, 'Plugin'):
            plugin_class = getattr(plugin_module, 'Plugin')
            plugin_instance = plugin_class()
        elif hasattr(plugin_module, 'main'):
            plugin_instance = getattr(plugin_module, 'main')
        
        if plugin_instance:
            self.loaded_plugins[plugin_name] = plugin_instance
            self.logger.info(f"Loaded plugin: {plugin_name}")
        else:
            raise ValueError(f"No plugin class or main function found in {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get a loaded plugin instance"""
        return self.loaded_plugins.get(plugin_name)
    
    def call_plugin_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call a plugin hook and return results"""
        results = []
        
        for plugin_name, plugin_instance in self.loaded_plugins.items():
            if hasattr(plugin_instance, hook_name):
                try:
                    hook_method = getattr(plugin_instance, hook_name)
                    result = hook_method(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error calling hook {hook_name} on plugin {plugin_name}: {e}")
        
        return results
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all plugins"""
        return list(self.plugins.values())
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            try:
                self._load_plugin(plugin_name, self.plugins[plugin_name])
                return True
            except Exception as e:
                self.logger.error(f"Error enabling plugin {plugin_name}: {e}")
                return False
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            if plugin_name in self.loaded_plugins:
                del self.loaded_plugins[plugin_name]
            return True
        return False


class WebhookManager:
    """Webhook management system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.webhook_history: List[Dict[str, Any]] = []
        self.event_handlers: Dict[WebhookEvent, List[Callable]] = {}
        
        # Start background webhook processing
        threading.Thread(target=self._process_webhook_queue, daemon=True).start()
    
    def register_webhook(self, webhook_id: str, config: WebhookConfig):
        """Register a webhook"""
        self.webhooks[webhook_id] = config
        self.logger.info(f"Registered webhook: {webhook_id} -> {config.url}")
    
    def unregister_webhook(self, webhook_id: str):
        """Unregister a webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            self.logger.info(f"Unregistered webhook: {webhook_id}")
    
    def register_event_handler(self, event: WebhookEvent, handler: Callable):
        """Register an event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def trigger_event(self, event: WebhookEvent, data: Dict[str, Any]):
        """Trigger a webhook event"""
        event_data = {
            'event': event.value,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Call event handlers
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
        
        # Send webhooks
        for webhook_id, webhook_config in self.webhooks.items():
            if event in webhook_config.events and webhook_config.enabled:
                self._send_webhook(webhook_id, webhook_config, event_data)
    
    def _send_webhook(self, webhook_id: str, config: WebhookConfig, data: Dict[str, Any]):
        """Send a webhook"""
        try:
            headers = config.headers.copy()
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] = 'UPID-CLI/1.0'
            
            if config.secret:
                # Add signature
                payload = json.dumps(data)
                signature = hashlib.sha256(f"{payload}{config.secret}".encode()).hexdigest()
                headers['X-UPID-Signature'] = signature
            
            response = requests.post(
                config.url,
                json=data,
                headers=headers,
                timeout=config.timeout
            )
            
            webhook_record = {
                'webhook_id': webhook_id,
                'url': config.url,
                'event': data['event'],
                'timestamp': datetime.now().isoformat(),
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300
            }
            
            self.webhook_history.append(webhook_record)
            
            if webhook_record['success']:
                self.logger.info(f"Webhook {webhook_id} sent successfully")
            else:
                self.logger.warning(f"Webhook {webhook_id} failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending webhook {webhook_id}: {e}")
            
            webhook_record = {
                'webhook_id': webhook_id,
                'url': config.url,
                'event': data['event'],
                'timestamp': datetime.now().isoformat(),
                'status_code': None,
                'success': False,
                'error': str(e)
            }
            
            self.webhook_history.append(webhook_record)
    
    def _process_webhook_queue(self):
        """Background task for processing webhook queue"""
        while True:
            try:
                # Process any pending webhooks
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in webhook queue processing: {e}")
                time.sleep(1)
    
    def get_webhook_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get webhook history"""
        return self.webhook_history[-limit:]
    
    def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook statistics"""
        total_webhooks = len(self.webhook_history)
        successful_webhooks = sum(1 for w in self.webhook_history if w.get('success', False))
        
        return {
            'total_webhooks': total_webhooks,
            'successful_webhooks': successful_webhooks,
            'success_rate': (successful_webhooks / total_webhooks * 100) if total_webhooks > 0 else 0,
            'active_webhooks': len([w for w in self.webhooks.values() if w.enabled])
        }


class IntegrationManager:
    """Third-party integration management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.integrations: Dict[str, Dict[str, Any]] = {}
        self.integration_configs: Dict[str, Dict[str, Any]] = {}
        
        # Load integration configurations
        self._load_integration_configs()
    
    def _load_integration_configs(self):
        """Load integration configurations"""
        config_file = Path("config/integrations.yaml")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    configs = yaml.safe_load(f)
                
                for integration_name, config in configs.items():
                    self.integration_configs[integration_name] = config
                    self.logger.info(f"Loaded integration config: {integration_name}")
                    
            except Exception as e:
                self.logger.error(f"Error loading integration configs: {e}")
    
    def register_integration(self, name: str, config: Dict[str, Any]):
        """Register an integration"""
        self.integrations[name] = {
            'name': name,
            'config': config,
            'enabled': config.get('enabled', True),
            'last_updated': datetime.now()
        }
        self.logger.info(f"Registered integration: {name}")
    
    def get_integration(self, name: str) -> Optional[Dict[str, Any]]:
        """Get integration information"""
        return self.integrations.get(name)
    
    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all integrations"""
        return list(self.integrations.values())
    
    def enable_integration(self, name: str) -> bool:
        """Enable an integration"""
        if name in self.integrations:
            self.integrations[name]['enabled'] = True
            self.integrations[name]['last_updated'] = datetime.now()
            return True
        return False
    
    def disable_integration(self, name: str) -> bool:
        """Disable an integration"""
        if name in self.integrations:
            self.integrations[name]['enabled'] = False
            self.integrations[name]['last_updated'] = datetime.now()
            return True
        return False
    
    def call_integration(self, name: str, method: str, *args, **kwargs) -> Any:
        """Call an integration method"""
        integration = self.get_integration(name)
        if not integration or not integration['enabled']:
            raise ValueError(f"Integration {name} not found or disabled")
        
        # This would typically call the actual integration
        # For now, we'll just log the call
        self.logger.info(f"Calling integration {name}.{method} with args: {args}, kwargs: {kwargs}")
        return {"status": "success", "integration": name, "method": method}


class APIVersionManager:
    """API version management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.versions: Dict[str, APIVersion] = {}
        self.current_version = "v1"
        self.deprecated_versions: List[str] = []
        
        # Initialize with default versions
        self._initialize_versions()
    
    def _initialize_versions(self):
        """Initialize API versions"""
        self.versions = {
            "v1": APIVersion(
                version="v1",
                status="stable",
                release_date=datetime.now(),
                breaking_changes=[],
                new_features=["Initial API release"]
            ),
            "v2": APIVersion(
                version="v2",
                status="beta",
                release_date=datetime.now(),
                breaking_changes=["Changed response format", "New authentication method"],
                new_features=["Enhanced optimization", "Real-time monitoring"]
            )
        }
    
    def get_version_info(self, version: str) -> Optional[APIVersion]:
        """Get version information"""
        return self.versions.get(version)
    
    def list_versions(self) -> List[APIVersion]:
        """List all API versions"""
        return list(self.versions.values())
    
    def get_current_version(self) -> str:
        """Get current API version"""
        return self.current_version
    
    def set_current_version(self, version: str):
        """Set current API version"""
        if version in self.versions:
            self.current_version = version
            self.logger.info(f"Set current API version to: {version}")
        else:
            raise ValueError(f"Unknown API version: {version}")
    
    def deprecate_version(self, version: str, deprecation_date: datetime):
        """Deprecate an API version"""
        if version in self.versions:
            self.versions[version].status = "deprecated"
            self.versions[version].deprecation_date = deprecation_date
            self.deprecated_versions.append(version)
            self.logger.warning(f"Deprecated API version: {version}")
    
    def add_version(self, version: str, status: str = "beta", breaking_changes: List[str] = None, new_features: List[str] = None):
        """Add a new API version"""
        self.versions[version] = APIVersion(
            version=version,
            status=status,
            release_date=datetime.now(),
            breaking_changes=breaking_changes or [],
            new_features=new_features or []
        )
        self.logger.info(f"Added new API version: {version}")


# Global instances
plugin_manager = PluginManager()
webhook_manager = WebhookManager()
integration_manager = IntegrationManager()
api_version_manager = APIVersionManager() 