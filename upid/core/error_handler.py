"""
UPID CLI Enhanced Error Handling System
Provides comprehensive error handling, recovery suggestions, and user-friendly messages
"""

import logging
import traceback
import sys
from typing import Optional, Dict, Any, List
from enum import Enum
import subprocess
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better organization"""
    KUBERNETES_CONNECTION = "kubernetes_connection"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    PERMISSIONS = "permissions"
    DATA_PROCESSING = "data_processing"
    ML_MODELS = "ml_models"
    OPTIMIZATION = "optimization"
    UNKNOWN = "unknown"

class UPIDError(Exception):
    """Base UPID error class with enhanced context"""
    
    def __init__(
        self, 
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.suggestions = suggestions or []
        self.context = context or {}
        super().__init__(message)

class KubernetesConnectionError(UPIDError):
    """Kubernetes connection related errors"""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None):
        default_suggestions = [
            "Check if kubectl is installed and configured",
            "Verify kubeconfig is valid: kubectl config view",
            "Test cluster connection: kubectl cluster-info",
            "Check if you have necessary permissions"
        ]
        super().__init__(
            message,
            ErrorCategory.KUBERNETES_CONNECTION,
            ErrorSeverity.ERROR,
            suggestions or default_suggestions,
            context
        )

class AuthenticationError(UPIDError):
    """Authentication related errors"""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None):
        default_suggestions = [
            "Run 'upid auth login' to authenticate",
            "Check if your authentication token is valid",
            "Verify your kubeconfig credentials",
            "Contact your administrator for access"
        ]
        super().__init__(
            message,
            ErrorCategory.AUTHENTICATION,
            ErrorSeverity.ERROR,
            suggestions or default_suggestions,
            context
        )

class ConfigurationError(UPIDError):
    """Configuration related errors"""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None):
        default_suggestions = [
            "Check your UPID configuration file",
            "Run 'upid config' to view current settings",
            "Reset configuration: rm ~/.upid/config.yaml",
            "Set required environment variables"
        ]
        super().__init__(
            message,
            ErrorCategory.CONFIGURATION,
            ErrorSeverity.ERROR,
            suggestions or default_suggestions,
            context
        )

class NetworkError(UPIDError):
    """Network related errors"""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None):
        default_suggestions = [
            "Check your internet connection",
            "Verify firewall settings",
            "Check if cluster API server is accessible",
            "Try running with --timeout option for longer wait"
        ]
        super().__init__(
            message,
            ErrorCategory.NETWORK,
            ErrorSeverity.ERROR,
            suggestions or default_suggestions,
            context
        )

class ErrorHandler:
    """Enhanced error handler with context-aware recovery suggestions"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.error_history: List[UPIDError] = []
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Handle and display errors with helpful suggestions"""
        
        # Convert standard exceptions to UPID errors
        upid_error = self._convert_to_upid_error(error, context)
        
        # Store in history
        self.error_history.append(upid_error)
        
        # Display error
        self._display_error(upid_error)
        
        # Log for debugging
        if self.debug_mode:
            self._log_debug_info(upid_error, error)
    
    def _convert_to_upid_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> UPIDError:
        """Convert standard exceptions to UPID errors with context"""
        
        if isinstance(error, UPIDError):
            return error
        
        error_msg = str(error)
        error_type = type(error).__name__
        
        # Kubernetes connection errors
        if any(keyword in error_msg.lower() for keyword in ['connection refused', 'kubectl', 'kubeconfig', 'cluster']):
            suggestions = self._get_kubernetes_suggestions(error_msg)
            return KubernetesConnectionError(f"Kubernetes connection failed: {error_msg}", suggestions, context)
        
        # Authentication errors
        if any(keyword in error_msg.lower() for keyword in ['unauthorized', 'forbidden', 'authentication', 'token']):
            suggestions = self._get_auth_suggestions(error_msg)
            return AuthenticationError(f"Authentication failed: {error_msg}", suggestions, context)
        
        # Network errors
        if any(keyword in error_msg.lower() for keyword in ['timeout', 'network', 'dns', 'connection']):
            suggestions = self._get_network_suggestions(error_msg)
            return NetworkError(f"Network error: {error_msg}", suggestions, context)
        
        # Configuration errors
        if any(keyword in error_msg.lower() for keyword in ['config', 'permission denied', 'file not found']):
            suggestions = self._get_config_suggestions(error_msg)
            return ConfigurationError(f"Configuration error: {error_msg}", suggestions, context)
        
        # Generic error
        return UPIDError(
            f"{error_type}: {error_msg}",
            ErrorCategory.UNKNOWN,
            ErrorSeverity.ERROR,
            ["Check command syntax and try again", "Use --help for command usage", "Enable debug mode with --verbose"],
            context
        )
    
    def _get_kubernetes_suggestions(self, error_msg: str) -> List[str]:
        """Get Kubernetes-specific suggestions"""
        suggestions = [
            "Verify kubectl is installed: kubectl version --client",
            "Check cluster connection: kubectl cluster-info",
            "Verify kubeconfig: kubectl config current-context",
            "Test permissions: kubectl auth can-i get pods"
        ]
        
        if 'connection refused' in error_msg.lower():
            suggestions.extend([
                "Check if your cluster is running",
                "Verify API server address in kubeconfig",
                "Check VPN connection if using remote cluster"
            ])
        
        if 'not found' in error_msg.lower():
            suggestions.extend([
                "Check if the namespace exists: kubectl get namespaces",
                "Verify resource names are correct",
                "Check if resources were deleted"
            ])
        
        return suggestions
    
    def _get_auth_suggestions(self, error_msg: str) -> List[str]:
        """Get authentication-specific suggestions"""
        suggestions = [
            "Run: upid auth login",
            "Check authentication status: upid auth status",
            "Verify your access permissions",
            "Contact your cluster administrator"
        ]
        
        if 'token' in error_msg.lower():
            suggestions.extend([
                "Refresh your authentication token",
                "Check token expiration",
                "Re-authenticate with your provider"
            ])
        
        return suggestions
    
    def _get_network_suggestions(self, error_msg: str) -> List[str]:
        """Get network-specific suggestions"""
        suggestions = [
            "Check internet connectivity",
            "Verify DNS resolution",
            "Check firewall settings",
            "Try with increased timeout: --timeout 60"
        ]
        
        if 'timeout' in error_msg.lower():
            suggestions.extend([
                "Increase command timeout",
                "Check network latency to cluster",
                "Verify cluster health"
            ])
        
        return suggestions
    
    def _get_config_suggestions(self, error_msg: str) -> List[str]:
        """Get configuration-specific suggestions"""
        suggestions = [
            "Check UPID configuration: upid config",
            "Verify file permissions",
            "Reset configuration if corrupted",
            "Check environment variables"
        ]
        
        if 'permission denied' in error_msg.lower():
            suggestions.extend([
                "Check file/directory permissions",
                "Run with appropriate user privileges",
                "Verify home directory access"
            ])
        
        return suggestions
    
    def _display_error(self, error: UPIDError) -> None:
        """Display error with rich formatting"""
        
        # Choose color based on severity
        color_map = {
            ErrorSeverity.INFO: "blue",
            ErrorSeverity.WARNING: "yellow", 
            ErrorSeverity.ERROR: "red",
            ErrorSeverity.CRITICAL: "bold red"
        }
        
        color = color_map.get(error.severity, "red")
        
        # Create error panel
        error_text = Text()
        error_text.append(f"❌ {error.message}", style=f"bold {color}")
        
        if error.context:
            error_text.append(f"\n\nContext: {error.context}", style="dim")
        
        if error.suggestions:
            error_text.append(f"\n\n💡 Suggestions:", style="bold green")
            for i, suggestion in enumerate(error.suggestions, 1):
                error_text.append(f"\n  {i}. {suggestion}", style="green")
        
        panel = Panel(
            error_text,
            title=f"[bold]{error.category.value.replace('_', ' ').title()} Error[/bold]",
            border_style=color,
            expand=False
        )
        
        console.print(panel)
    
    def _log_debug_info(self, upid_error: UPIDError, original_error: Exception) -> None:
        """Log detailed debug information"""
        logger.error(f"UPID Error: {upid_error.message}")
        logger.error(f"Category: {upid_error.category.value}")
        logger.error(f"Severity: {upid_error.severity.value}")
        logger.error(f"Context: {upid_error.context}")
        logger.error(f"Original error: {original_error}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check system prerequisites and return status"""
        results = {}
        
        # Check kubectl
        try:
            subprocess.run(['kubectl', 'version', '--client'], 
                         capture_output=True, check=True, timeout=10)
            results['kubectl'] = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            results['kubectl'] = False
        
        # Check cluster connectivity
        try:
            subprocess.run(['kubectl', 'cluster-info'], 
                         capture_output=True, check=True, timeout=10)
            results['cluster_connection'] = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            results['cluster_connection'] = False
        
        # Check Python dependencies
        try:
            import kubernetes
            import lightgbm
            import sklearn
            results['dependencies'] = True
        except ImportError:
            results['dependencies'] = False
        
        return results
    
    def suggest_quick_fixes(self, error_category: ErrorCategory) -> List[str]:
        """Suggest quick fixes based on error category"""
        
        quick_fixes = {
            ErrorCategory.KUBERNETES_CONNECTION: [
                "kubectl cluster-info",
                "kubectl config get-contexts", 
                "kubectl auth can-i get pods"
            ],
            ErrorCategory.AUTHENTICATION: [
                "upid auth status",
                "upid auth login",
                "kubectl config current-context"
            ],
            ErrorCategory.CONFIGURATION: [
                "upid config",
                "ls ~/.upid/",
                "env | grep UPID"
            ],
            ErrorCategory.NETWORK: [
                "ping 8.8.8.8",
                "nslookup kubernetes.default.svc.cluster.local",
                "kubectl get nodes"
            ]
        }
        
        return quick_fixes.get(error_category, ["upid --help"])
    
    def create_recovery_guide(self, error: UPIDError) -> str:
        """Create a detailed recovery guide"""
        
        guide = f"""
UPID CLI Recovery Guide
======================

Error: {error.message}
Category: {error.category.value}
Severity: {error.severity.value}

Step-by-step Recovery:
"""
        
        for i, suggestion in enumerate(error.suggestions, 1):
            guide += f"\n{i}. {suggestion}"
        
        guide += f"""

Quick Commands to Try:
"""
        
        quick_fixes = self.suggest_quick_fixes(error.category)
        for cmd in quick_fixes:
            guide += f"\n  $ {cmd}"
        
        guide += f"""

Need More Help?
- Run with --verbose for detailed debugging
- Check documentation: upid --help
- Report issues: https://github.com/your-org/upid-cli/issues

Environment Check:
"""
        
        prereqs = self.check_prerequisites()
        for check, status in prereqs.items():
            status_icon = "✅" if status else "❌"
            guide += f"\n  {status_icon} {check.replace('_', ' ').title()}: {'OK' if status else 'FAILED'}"
        
        return guide

# Global error handler instance
error_handler = ErrorHandler()

def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function for error handling"""
    error_handler.handle_error(error, context)

def safe_execute(func, *args, context: Optional[Dict[str, Any]] = None, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context)
        return None

def validate_prerequisites() -> bool:
    """Validate system prerequisites"""
    prereqs = error_handler.check_prerequisites()
    
    if not all(prereqs.values()):
        console.print("\n[red]❌ Prerequisites check failed:[/red]")
        for check, status in prereqs.items():
            status_icon = "✅" if status else "❌"
            console.print(f"  {status_icon} {check.replace('_', ' ').title()}")
        
        console.print("\n[yellow]Please fix the issues above before continuing.[/yellow]")
        return False
    
    console.print("[green]✅ All prerequisites satisfied[/green]")
    return True