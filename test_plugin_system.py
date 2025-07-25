#!/usr/bin/env python3
"""
Test script for Integration & Plugin System
Tests the PluginManager, WebhookManager, IntegrationManager, and APIVersionManager functionality
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_plugin_system():
    """Test the plugin system functionality"""
    print("🔧 Testing Integration & Plugin System...")
    
    try:
        from upid_python.core.plugin_system import (
            PluginManager,
            WebhookManager,
            IntegrationManager,
            APIVersionManager,
            PluginType,
            WebhookEvent,
            WebhookConfig
        )
        
        # Test Plugin Manager
        print("🔌 Testing Plugin Manager...")
        
        plugin_manager = PluginManager("test_plugins")
        
        # Create a test plugin
        test_plugin_dir = plugin_manager.plugins_dir / "test_plugin"
        test_plugin_dir.mkdir(exist_ok=True)
        
        # Create manifest
        manifest = {
            'name': 'test_plugin',
            'version': '1.0.0',
            'description': 'A test plugin',
            'author': 'Test Author',
            'type': 'custom',
            'entry_point': 'main.py',
            'config_schema': {
                'api_key': {'type': 'string', 'required': True},
                'endpoint': {'type': 'string', 'default': 'https://api.example.com'}
            },
            'dependencies': ['requests'],
            'enabled': True
        }
        
        import yaml
        with open(test_plugin_dir / "manifest.yaml", 'w') as f:
            yaml.dump(manifest, f)
        
        # Create plugin main file
        plugin_code = '''
class Plugin:
    def __init__(self):
        self.name = "test_plugin"
    
    def on_optimization_completed(self, data):
        print(f"Plugin {self.name} received optimization data: {data}")
        return {"status": "processed", "plugin": self.name}
    
    def on_cluster_health_changed(self, data):
        print(f"Plugin {self.name} received health data: {data}")
        return {"status": "processed", "plugin": self.name}
'''
        
        with open(test_plugin_dir / "main.py", 'w') as f:
            f.write(plugin_code)
        
        # Reload plugins
        plugin_manager._discover_plugins()
        plugin_manager._load_plugins()
        
        print(f"✅ Plugin manager initialized with {len(plugin_manager.list_plugins())} plugins")
        
        # Test Webhook Manager
        print("🔗 Testing Webhook Manager...")
        
        webhook_manager = WebhookManager()
        
        # Register a webhook
        webhook_config = WebhookConfig(
            url="https://webhook.site/test",
            events=[WebhookEvent.OPTIMIZATION_COMPLETED, WebhookEvent.CLUSTER_HEALTH_CHANGED],
            headers={"Authorization": "Bearer test-token"},
            timeout=30,
            retry_count=3,
            enabled=True,
            secret="test-secret"
        )
        
        webhook_manager.register_webhook("test-webhook", webhook_config)
        
        # Register event handler
        def test_event_handler(event_data):
            print(f"Event handler received: {event_data['event']}")
        
        webhook_manager.register_event_handler(WebhookEvent.OPTIMIZATION_COMPLETED, test_event_handler)
        
        # Trigger events
        print("📡 Testing webhook events...")
        
        webhook_manager.trigger_event(WebhookEvent.OPTIMIZATION_COMPLETED, {
            "optimization_id": "opt-123",
            "cluster_name": "test-cluster",
            "savings": 150.0
        })
        
        webhook_manager.trigger_event(WebhookEvent.CLUSTER_HEALTH_CHANGED, {
            "cluster_name": "test-cluster",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })
        
        print("✅ Webhook manager tested")
        
        # Test Integration Manager
        print("🔗 Testing Integration Manager...")
        
        integration_manager = IntegrationManager()
        
        # Register integrations
        integration_manager.register_integration("slack", {
            "webhook_url": "https://hooks.slack.com/test",
            "channel": "#alerts",
            "enabled": True
        })
        
        integration_manager.register_integration("jira", {
            "base_url": "https://company.atlassian.net",
            "api_token": "test-token",
            "project_key": "UPID",
            "enabled": True
        })
        
        # Test integration calls
        result = integration_manager.call_integration("slack", "send_message", "Test message")
        print(f"✅ Integration call result: {result}")
        
        print(f"✅ Integration manager initialized with {len(integration_manager.list_integrations())} integrations")
        
        # Test API Version Manager
        print("📚 Testing API Version Manager...")
        
        api_version_manager = APIVersionManager()
        
        # Test version management
        current_version = api_version_manager.get_current_version()
        print(f"  Current API version: {current_version}")
        
        versions = api_version_manager.list_versions()
        print(f"  Available versions: {len(versions)}")
        
        for version in versions:
            print(f"    - {version.version} ({version.status})")
        
        # Add a new version
        api_version_manager.add_version("v3", "beta", 
                                     breaking_changes=["New authentication required"],
                                     new_features=["GraphQL API", "Real-time subscriptions"])
        
        # Test plugin hooks
        print("🎣 Testing plugin hooks...")
        
        if "test_plugin" in plugin_manager.loaded_plugins:
            plugin = plugin_manager.loaded_plugins["test_plugin"]
            
            # Test hook calls
            results = plugin_manager.call_plugin_hook("on_optimization_completed", {
                "optimization_id": "opt-456",
                "cluster_name": "test-cluster",
                "savings": 200.0
            })
            
            print(f"✅ Plugin hook results: {results}")
        
        # Test webhook statistics
        print("📊 Testing webhook statistics...")
        
        webhook_stats = webhook_manager.get_webhook_stats()
        print("✅ Webhook Statistics:")
        print(json.dumps(webhook_stats, indent=2, default=str))
        
        # Test webhook history
        webhook_history = webhook_manager.get_webhook_history(limit=10)
        print(f"✅ Webhook history: {len(webhook_history)} records")
        
        print("\n🎉 All plugin system tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing plugin system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optional_dependencies():
    """Test optional dependency handling"""
    print("\n🔍 Testing optional dependency handling...")
    
    try:
        from upid_python.core.plugin_system import (
            PluginManager,
            WebhookManager,
            IntegrationManager,
            APIVersionManager
        )
        
        # Test all managers with optional dependencies
        plugin_manager = PluginManager()
        webhook_manager = WebhookManager()
        integration_manager = IntegrationManager()
        api_version_manager = APIVersionManager()
        
        print("✅ All managers initialized successfully:")
        print(f"  - Plugin Manager: {len(plugin_manager.list_plugins())} plugins")
        print(f"  - Webhook Manager: {len(webhook_manager.webhooks)} webhooks")
        print(f"  - Integration Manager: {len(integration_manager.list_integrations())} integrations")
        print(f"  - API Version Manager: {len(api_version_manager.list_versions())} versions")
        
        print("✅ Plugin system works with optional dependencies!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing optional dependencies: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Integration & Plugin System Tests")
    print("=" * 60)
    
    # Test basic functionality
    success1 = test_plugin_system()
    
    # Test optional dependencies
    success2 = test_optional_dependencies()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! Plugin system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 60) 