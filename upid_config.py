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
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """Product information and configuration"""
    name: str = "UPID CLI"
    description: str = "Universal Prometheus Infrastructure Discovery - Kubernetes Cost Optimization CLI"
    version: str = "1.0.0"
    build_version: str = "1.0.0-production"
    api_version: str = "v1"
    author: str = "UPID Development Team"
    repository: str = "https://github.com/kubilitics/upid-cli"
    documentation: str = "https://github.com/kubilitics/upid-cli/docs"
    support_email: str = "support@upid.io"
    license: str = "MIT"
    copyright: str = "© 2025 UPID Development Team"
    
    # Build information
    build_date: Optional[str] = None
    build_commit: Optional[str] = None
    build_platform: Optional[str] = None
    
    # Feature flags
    enable_ml: bool = True
    enable_enterprise: bool = True
    enable_multi_cloud: bool = True
    enable_security: bool = True
    enable_analytics: bool = True
    enable_optimization: bool = True
    enable_reporting: bool = True
    enable_dashboard: bool = True
    enable_api: bool = True
    enable_plugin_system: bool = True
    
    # Configuration paths
    config_dir: str = "~/.upid"
    data_dir: str = "~/.upid/data"
    log_dir: str = "~/.upid/logs"
    cache_dir: str = "~/.upid/cache"
    plugin_dir: str = "~/.upid/plugins"
    
    # Default settings
    default_namespace: str = "default"
    default_time_range: str = "24h"
    default_output_format: str = "table"
    default_safety_threshold: float = 0.85
    default_dry_run: bool = True
    
    # API settings
    api_host: str = "localhost"
    api_port: int = 8000
    api_timeout: int = 30
    api_max_workers: int = 4
    
    # Database settings
    db_url: str = "sqlite:///~/.upid/data/upid.db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Security settings
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_expiry_hours: int = 24
    mfa_enabled: bool = True
    sso_enabled: bool = True
    
    # Cloud provider settings
    aws_region: str = "us-west-2"
    gcp_project: str = ""
    azure_subscription: str = ""
    
    # Optimization settings
    optimization_enabled: bool = True
    zero_pod_scaling: bool = True
    resource_rightsizing: bool = True
    cost_optimization: bool = True
    safety_checks: bool = True
    
    # Analytics settings
    analytics_enabled: bool = True
    ml_enabled: bool = True
    prediction_horizon_days: int = 7
    anomaly_detection: bool = True
    
    # Reporting settings
    reporting_enabled: bool = True
    executive_reports: bool = True
    technical_reports: bool = True
    cost_reports: bool = True
    performance_reports: bool = True
    
    # Monitoring settings
    monitoring_enabled: bool = True
    real_time_monitoring: bool = True
    alerting_enabled: bool = True
    metrics_retention_days: int = 365
    
    # Plugin system settings
    plugin_system_enabled: bool = True
    plugin_auto_load: bool = True
    plugin_validation: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_rotation: bool = True
    log_max_size_mb: int = 100
    log_backup_count: int = 5
    
    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    
    # Development settings
    debug_mode: bool = False
    development_mode: bool = False
    test_mode: bool = False
    mock_data_enabled: bool = False
    
    # Enterprise settings
    enterprise_enabled: bool = True
    multi_tenant: bool = True
    audit_logging: bool = True
    compliance_mode: bool = True
    
    # CI/CD settings
    ci_cd_enabled: bool = True
    automated_testing: bool = True
    deployment_validation: bool = True
    gitops_integration: bool = True

# Global product instance
product_info = ProductInfo()

def get_version() -> str:
    """Get the current version"""
    return product_info.version

def get_build_version() -> str:
    """Get the build version"""
    return product_info.build_version

def get_api_version() -> str:
    """Get the API version"""
    return product_info.api_version

def get_product_name() -> str:
    """Get the product name"""
    return product_info.name

def get_product_description() -> str:
    """Get the product description"""
    return product_info.description

def is_enterprise_enabled() -> bool:
    """Check if enterprise features are enabled"""
    return product_info.enterprise_enabled

def is_ml_enabled() -> bool:
    """Check if ML features are enabled"""
    return product_info.ml_enabled

def is_optimization_enabled() -> bool:
    """Check if optimization features are enabled"""
    return product_info.optimization_enabled

def is_reporting_enabled() -> bool:
    """Check if reporting features are enabled"""
    return product_info.reporting_enabled

def is_monitoring_enabled() -> bool:
    """Check if monitoring features are enabled"""
    return product_info.monitoring_enabled

def is_plugin_system_enabled() -> bool:
    """Check if plugin system is enabled"""
    return product_info.plugin_system_enabled

def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return product_info.debug_mode

def is_development_mode() -> bool:
    """Check if development mode is enabled"""
    return product_info.development_mode

def is_test_mode() -> bool:
    """Check if test mode is enabled"""
    return product_info.test_mode

def is_mock_data_enabled() -> bool:
    """Check if mock data is enabled"""
    return product_info.mock_data_enabled

def get_default_safety_threshold() -> float:
    """Get the default safety threshold"""
    return product_info.default_safety_threshold

def get_default_dry_run() -> bool:
    """Get the default dry run setting"""
    return product_info.default_dry_run

def get_api_settings() -> dict:
    """Get API settings"""
    return {
        "host": product_info.api_host,
        "port": product_info.api_port,
        "timeout": product_info.api_timeout,
        "max_workers": product_info.api_max_workers
    }

def get_database_settings() -> dict:
    """Get database settings"""
    return {
        "url": product_info.db_url,
        "pool_size": product_info.db_pool_size,
        "max_overflow": product_info.db_max_overflow
    }

def get_security_settings() -> dict:
    """Get security settings"""
    return {
        "jwt_secret": product_info.jwt_secret,
        "jwt_expiry_hours": product_info.jwt_expiry_hours,
        "mfa_enabled": product_info.mfa_enabled,
        "sso_enabled": product_info.sso_enabled
    }

def get_cloud_settings() -> dict:
    """Get cloud provider settings"""
    return {
        "aws_region": product_info.aws_region,
        "gcp_project": product_info.gcp_project,
        "azure_subscription": product_info.azure_subscription
    }

def get_optimization_settings() -> dict:
    """Get optimization settings"""
    return {
        "enabled": product_info.optimization_enabled,
        "zero_pod_scaling": product_info.zero_pod_scaling,
        "resource_rightsizing": product_info.resource_rightsizing,
        "cost_optimization": product_info.cost_optimization,
        "safety_checks": product_info.safety_checks
    }

def get_analytics_settings() -> dict:
    """Get analytics settings"""
    return {
        "enabled": product_info.analytics_enabled,
        "ml_enabled": product_info.ml_enabled,
        "prediction_horizon_days": product_info.prediction_horizon_days,
        "anomaly_detection": product_info.anomaly_detection
    }

def get_reporting_settings() -> dict:
    """Get reporting settings"""
    return {
        "enabled": product_info.reporting_enabled,
        "executive_reports": product_info.executive_reports,
        "technical_reports": product_info.technical_reports,
        "cost_reports": product_info.cost_reports,
        "performance_reports": product_info.performance_reports
    }

def get_monitoring_settings() -> dict:
    """Get monitoring settings"""
    return {
        "enabled": product_info.monitoring_enabled,
        "real_time_monitoring": product_info.real_time_monitoring,
        "alerting_enabled": product_info.alerting_enabled,
        "metrics_retention_days": product_info.metrics_retention_days
    }

def get_plugin_settings() -> dict:
    """Get plugin system settings"""
    return {
        "enabled": product_info.plugin_system_enabled,
        "auto_load": product_info.plugin_auto_load,
        "validation": product_info.plugin_validation
    }

def get_logging_settings() -> dict:
    """Get logging settings"""
    return {
        "level": product_info.log_level,
        "format": product_info.log_format,
        "rotation": product_info.log_rotation,
        "max_size_mb": product_info.log_max_size_mb,
        "backup_count": product_info.log_backup_count
    }

def get_performance_settings() -> dict:
    """Get performance settings"""
    return {
        "max_concurrent_requests": product_info.max_concurrent_requests,
        "request_timeout_seconds": product_info.request_timeout_seconds,
        "cache_enabled": product_info.cache_enabled,
        "cache_ttl_seconds": product_info.cache_ttl_seconds
    }

def get_enterprise_settings() -> dict:
    """Get enterprise settings"""
    return {
        "enabled": product_info.enterprise_enabled,
        "multi_tenant": product_info.multi_tenant,
        "audit_logging": product_info.audit_logging,
        "compliance_mode": product_info.compliance_mode
    }

def get_cicd_settings() -> dict:
    """Get CI/CD settings"""
    return {
        "enabled": product_info.ci_cd_enabled,
        "automated_testing": product_info.automated_testing,
        "deployment_validation": product_info.deployment_validation,
        "gitops_integration": product_info.gitops_integration
    }

def get_paths() -> dict:
    """Get configuration paths"""
    return {
        "config_dir": product_info.config_dir,
        "data_dir": product_info.data_dir,
        "log_dir": product_info.log_dir,
        "cache_dir": product_info.cache_dir,
        "plugin_dir": product_info.plugin_dir
    }

def get_defaults() -> dict:
    """Get default settings"""
    return {
        "namespace": product_info.default_namespace,
        "time_range": product_info.default_time_range,
        "output_format": product_info.default_output_format,
        "safety_threshold": product_info.default_safety_threshold,
        "dry_run": product_info.default_dry_run
    }

def get_feature_flags() -> dict:
    """Get feature flags"""
    return {
        "enable_ml": product_info.enable_ml,
        "enable_enterprise": product_info.enable_enterprise,
        "enable_multi_cloud": product_info.enable_multi_cloud,
        "enable_security": product_info.enable_security,
        "enable_analytics": product_info.enable_analytics,
        "enable_optimization": product_info.enable_optimization,
        "enable_reporting": product_info.enable_reporting,
        "enable_dashboard": product_info.enable_dashboard,
        "enable_api": product_info.enable_api,
        "enable_plugin_system": product_info.enable_plugin_system
    }

def get_build_info() -> dict:
    """Get build information"""
    return {
        "version": product_info.version,
        "build_version": product_info.build_version,
        "build_date": product_info.build_date,
        "build_commit": product_info.build_commit,
        "build_platform": product_info.build_platform
    }

def update_build_info(build_date: str = None, build_commit: str = None, build_platform: str = None):
    """Update build information"""
    if build_date:
        product_info.build_date = build_date
    if build_commit:
        product_info.build_commit = build_commit
    if build_platform:
        product_info.build_platform = build_platform

def set_version(version: str):
    """Set the version"""
    product_info.version = version
    product_info.build_version = f"{version}-production"

def set_build_version(build_version: str):
    """Set the build version"""
    product_info.build_version = build_version

def set_api_version(api_version: str):
    """Set the API version"""
    product_info.api_version = api_version

def set_debug_mode(enabled: bool):
    """Set debug mode"""
    product_info.debug_mode = enabled

def set_development_mode(enabled: bool):
    """Set development mode"""
    product_info.development_mode = enabled

def set_test_mode(enabled: bool):
    """Set test mode"""
    product_info.test_mode = enabled

def set_mock_data_enabled(enabled: bool):
    """Set mock data enabled"""
    product_info.mock_data_enabled = enabled

def set_safety_threshold(threshold: float):
    """Set the safety threshold"""
    product_info.default_safety_threshold = threshold

def set_dry_run_default(enabled: bool):
    """Set the default dry run setting"""
    product_info.default_dry_run = enabled

def set_api_settings(host: str = None, port: int = None, timeout: int = None, max_workers: int = None):
    """Set API settings"""
    if host:
        product_info.api_host = host
    if port:
        product_info.api_port = port
    if timeout:
        product_info.api_timeout = timeout
    if max_workers:
        product_info.api_max_workers = max_workers

def set_database_settings(url: str = None, pool_size: int = None, max_overflow: int = None):
    """Set database settings"""
    if url:
        product_info.db_url = url
    if pool_size:
        product_info.db_pool_size = pool_size
    if max_overflow:
        product_info.db_max_overflow = max_overflow

def set_security_settings(jwt_secret: str = None, jwt_expiry_hours: int = None, mfa_enabled: bool = None, sso_enabled: bool = None):
    """Set security settings"""
    if jwt_secret:
        product_info.jwt_secret = jwt_secret
    if jwt_expiry_hours:
        product_info.jwt_expiry_hours = jwt_expiry_hours
    if mfa_enabled is not None:
        product_info.mfa_enabled = mfa_enabled
    if sso_enabled is not None:
        product_info.sso_enabled = sso_enabled

def set_cloud_settings(aws_region: str = None, gcp_project: str = None, azure_subscription: str = None):
    """Set cloud provider settings"""
    if aws_region:
        product_info.aws_region = aws_region
    if gcp_project:
        product_info.gcp_project = gcp_project
    if azure_subscription:
        product_info.azure_subscription = azure_subscription

def set_optimization_settings(enabled: bool = None, zero_pod_scaling: bool = None, resource_rightsizing: bool = None, cost_optimization: bool = None, safety_checks: bool = None):
    """Set optimization settings"""
    if enabled is not None:
        product_info.optimization_enabled = enabled
    if zero_pod_scaling is not None:
        product_info.zero_pod_scaling = zero_pod_scaling
    if resource_rightsizing is not None:
        product_info.resource_rightsizing = resource_rightsizing
    if cost_optimization is not None:
        product_info.cost_optimization = cost_optimization
    if safety_checks is not None:
        product_info.safety_checks = safety_checks

def set_analytics_settings(enabled: bool = None, ml_enabled: bool = None, prediction_horizon_days: int = None, anomaly_detection: bool = None):
    """Set analytics settings"""
    if enabled is not None:
        product_info.analytics_enabled = enabled
    if ml_enabled is not None:
        product_info.ml_enabled = ml_enabled
    if prediction_horizon_days:
        product_info.prediction_horizon_days = prediction_horizon_days
    if anomaly_detection is not None:
        product_info.anomaly_detection = anomaly_detection

def set_reporting_settings(enabled: bool = None, executive_reports: bool = None, technical_reports: bool = None, cost_reports: bool = None, performance_reports: bool = None):
    """Set reporting settings"""
    if enabled is not None:
        product_info.reporting_enabled = enabled
    if executive_reports is not None:
        product_info.executive_reports = executive_reports
    if technical_reports is not None:
        product_info.technical_reports = technical_reports
    if cost_reports is not None:
        product_info.cost_reports = cost_reports
    if performance_reports is not None:
        product_info.performance_reports = performance_reports

def set_monitoring_settings(enabled: bool = None, real_time_monitoring: bool = None, alerting_enabled: bool = None, metrics_retention_days: int = None):
    """Set monitoring settings"""
    if enabled is not None:
        product_info.monitoring_enabled = enabled
    if real_time_monitoring is not None:
        product_info.real_time_monitoring = real_time_monitoring
    if alerting_enabled is not None:
        product_info.alerting_enabled = alerting_enabled
    if metrics_retention_days:
        product_info.metrics_retention_days = metrics_retention_days

def set_plugin_settings(enabled: bool = None, auto_load: bool = None, validation: bool = None):
    """Set plugin system settings"""
    if enabled is not None:
        product_info.plugin_system_enabled = enabled
    if auto_load is not None:
        product_info.plugin_auto_load = auto_load
    if validation is not None:
        product_info.plugin_validation = validation

def set_logging_settings(level: str = None, format: str = None, rotation: bool = None, max_size_mb: int = None, backup_count: int = None):
    """Set logging settings"""
    if level:
        product_info.log_level = level
    if format:
        product_info.log_format = format
    if rotation is not None:
        product_info.log_rotation = rotation
    if max_size_mb:
        product_info.log_max_size_mb = max_size_mb
    if backup_count:
        product_info.log_backup_count = backup_count

def set_performance_settings(max_concurrent_requests: int = None, request_timeout_seconds: int = None, cache_enabled: bool = None, cache_ttl_seconds: int = None):
    """Set performance settings"""
    if max_concurrent_requests:
        product_info.max_concurrent_requests = max_concurrent_requests
    if request_timeout_seconds:
        product_info.request_timeout_seconds = request_timeout_seconds
    if cache_enabled is not None:
        product_info.cache_enabled = cache_enabled
    if cache_ttl_seconds:
        product_info.cache_ttl_seconds = cache_ttl_seconds

def set_enterprise_settings(enabled: bool = None, multi_tenant: bool = None, audit_logging: bool = None, compliance_mode: bool = None):
    """Set enterprise settings"""
    if enabled is not None:
        product_info.enterprise_enabled = enabled
    if multi_tenant is not None:
        product_info.multi_tenant = multi_tenant
    if audit_logging is not None:
        product_info.audit_logging = audit_logging
    if compliance_mode is not None:
        product_info.compliance_mode = compliance_mode

def set_cicd_settings(enabled: bool = None, automated_testing: bool = None, deployment_validation: bool = None, gitops_integration: bool = None):
    """Set CI/CD settings"""
    if enabled is not None:
        product_info.ci_cd_enabled = enabled
    if automated_testing is not None:
        product_info.automated_testing = automated_testing
    if deployment_validation is not None:
        product_info.deployment_validation = deployment_validation
    if gitops_integration is not None:
        product_info.gitops_integration = gitops_integration

def set_paths(config_dir: str = None, data_dir: str = None, log_dir: str = None, cache_dir: str = None, plugin_dir: str = None):
    """Set configuration paths"""
    if config_dir:
        product_info.config_dir = config_dir
    if data_dir:
        product_info.data_dir = data_dir
    if log_dir:
        product_info.log_dir = log_dir
    if cache_dir:
        product_info.cache_dir = cache_dir
    if plugin_dir:
        product_info.plugin_dir = plugin_dir

def set_defaults(namespace: str = None, time_range: str = None, output_format: str = None, safety_threshold: float = None, dry_run: bool = None):
    """Set default settings"""
    if namespace:
        product_info.default_namespace = namespace
    if time_range:
        product_info.default_time_range = time_range
    if output_format:
        product_info.default_output_format = output_format
    if safety_threshold:
        product_info.default_safety_threshold = safety_threshold
    if dry_run is not None:
        product_info.default_dry_run = dry_run

def set_feature_flags(enable_ml: bool = None, enable_enterprise: bool = None, enable_multi_cloud: bool = None, enable_security: bool = None, enable_analytics: bool = None, enable_optimization: bool = None, enable_reporting: bool = None, enable_dashboard: bool = None, enable_api: bool = None, enable_plugin_system: bool = None):
    """Set feature flags"""
    if enable_ml is not None:
        product_info.enable_ml = enable_ml
    if enable_enterprise is not None:
        product_info.enable_enterprise = enable_enterprise
    if enable_multi_cloud is not None:
        product_info.enable_multi_cloud = enable_multi_cloud
    if enable_security is not None:
        product_info.enable_security = enable_security
    if enable_analytics is not None:
        product_info.enable_analytics = enable_analytics
    if enable_optimization is not None:
        product_info.enable_optimization = enable_optimization
    if enable_reporting is not None:
        product_info.enable_reporting = enable_reporting
    if enable_dashboard is not None:
        product_info.enable_dashboard = enable_dashboard
    if enable_api is not None:
        product_info.enable_api = enable_api
    if enable_plugin_system is not None:
        product_info.enable_plugin_system = enable_plugin_system

def get_all_settings() -> dict:
    """Get all settings"""
    return {
        "product_info": {
            "name": product_info.name,
            "description": product_info.description,
            "version": product_info.version,
            "build_version": product_info.build_version,
            "api_version": product_info.api_version,
            "author": product_info.author,
            "repository": product_info.repository,
            "documentation": product_info.documentation,
            "support_email": product_info.support_email,
            "license": product_info.license,
            "copyright": product_info.copyright
        },
        "build_info": get_build_info(),
        "api_settings": get_api_settings(),
        "database_settings": get_database_settings(),
        "security_settings": get_security_settings(),
        "cloud_settings": get_cloud_settings(),
        "optimization_settings": get_optimization_settings(),
        "analytics_settings": get_analytics_settings(),
        "reporting_settings": get_reporting_settings(),
        "monitoring_settings": get_monitoring_settings(),
        "plugin_settings": get_plugin_settings(),
        "logging_settings": get_logging_settings(),
        "performance_settings": get_performance_settings(),
        "enterprise_settings": get_enterprise_settings(),
        "cicd_settings": get_cicd_settings(),
        "paths": get_paths(),
        "defaults": get_defaults(),
        "feature_flags": get_feature_flags()
    }

def print_product_info():
    """Print product information"""
    print(f"Product: {product_info.name}")
    print(f"Description: {product_info.description}")
    print(f"Version: {product_info.version}")
    print(f"Build Version: {product_info.build_version}")
    print(f"API Version: {product_info.api_version}")
    print(f"Author: {product_info.author}")
    print(f"Repository: {product_info.repository}")
    print(f"Documentation: {product_info.documentation}")
    print(f"Support Email: {product_info.support_email}")
    print(f"License: {product_info.license}")
    print(f"Copyright: {product_info.copyright}")

def print_build_info():
    """Print build information"""
    print(f"Version: {product_info.version}")
    print(f"Build Version: {product_info.build_version}")
    print(f"Build Date: {product_info.build_date}")
    print(f"Build Commit: {product_info.build_commit}")
    print(f"Build Platform: {product_info.build_platform}")

def print_feature_flags():
    """Print feature flags"""
    print("Feature Flags:")
    print(f"  ML Enabled: {product_info.enable_ml}")
    print(f"  Enterprise Enabled: {product_info.enable_enterprise}")
    print(f"  Multi-Cloud Enabled: {product_info.enable_multi_cloud}")
    print(f"  Security Enabled: {product_info.enable_security}")
    print(f"  Analytics Enabled: {product_info.enable_analytics}")
    print(f"  Optimization Enabled: {product_info.enable_optimization}")
    print(f"  Reporting Enabled: {product_info.enable_reporting}")
    print(f"  Dashboard Enabled: {product_info.enable_dashboard}")
    print(f"  API Enabled: {product_info.enable_api}")
    print(f"  Plugin System Enabled: {product_info.enable_plugin_system}")

def print_settings():
    """Print all settings"""
    print("UPID CLI Settings:")
    print("=" * 50)
    print_product_info()
    print()
    print_build_info()
    print()
    print_feature_flags()
    print()
    print("API Settings:")
    for key, value in get_api_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Database Settings:")
    for key, value in get_database_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Security Settings:")
    for key, value in get_security_settings().items():
        if key == "jwt_secret":
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
    print()
    print("Cloud Settings:")
    for key, value in get_cloud_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Optimization Settings:")
    for key, value in get_optimization_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Analytics Settings:")
    for key, value in get_analytics_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Reporting Settings:")
    for key, value in get_reporting_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Monitoring Settings:")
    for key, value in get_monitoring_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Plugin Settings:")
    for key, value in get_plugin_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Logging Settings:")
    for key, value in get_logging_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Performance Settings:")
    for key, value in get_performance_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Enterprise Settings:")
    for key, value in get_enterprise_settings().items():
        print(f"  {key}: {value}")
    print()
    print("CI/CD Settings:")
    for key, value in get_cicd_settings().items():
        print(f"  {key}: {value}")
    print()
    print("Paths:")
    for key, value in get_paths().items():
        print(f"  {key}: {value}")
    print()
    print("Defaults:")
    for key, value in get_defaults().items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    print_settings()