"""
UPID CLI - Main entry point
Enterprise-grade Kubernetes cost optimization platform with ML-powered insights
"""

import sys
import argparse
import json
import yaml
from typing import Optional, List, Dict, Any
from pathlib import Path

from .core.config import Config, get_config
from .core.auth import AuthManager
from .core.api_client import UPIDAPIClient

# Import centralized configuration
try:
    from ..upid_config import get_config as get_upid_config
    upid_config = get_upid_config()
except ImportError:
    upid_config = None


class UPIDCLI:
    """Main CLI class for UPID"""
    
    def __init__(self):
        self.config = get_config()
        self.auth_manager = AuthManager(self.config)
        self.api_client = UPIDAPIClient(self.config, self.auth_manager)
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        # Use centralized configuration if available
        if upid_config:
            description = upid_config.product.description
            homepage = upid_config.product.homepage
        else:
            description = "Universal Pod Intelligence Director - Enterprise-grade Kubernetes cost optimization platform"
            homepage = "https://github.com/kubilitics/upid-cli"
        
        parser = argparse.ArgumentParser(
            prog="upid",
            description=description,
            epilog=f"For more information, visit {homepage}"
        )
        
        # Global options
        # Use centralized version if available
        version_str = upid_config.full_version if upid_config else "UPID CLI 2.0.0"
        parser.add_argument("--version", action="version", version=version_str)
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
        parser.add_argument("--config", "-c", help="Configuration file path")
        parser.add_argument("--output", "-o", choices=["table", "json", "yaml", "csv"], 
                          default="table", help="Output format")
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Auth commands
        auth_parser = subparsers.add_parser("auth", help="Authentication commands")
        auth_subparsers = auth_parser.add_subparsers(dest="auth_command")
        
        # Login
        login_parser = auth_subparsers.add_parser("login", help="Login to UPID")
        login_parser.add_argument("email", help="User email")
        login_parser.add_argument("--password", help="User password (will prompt if not provided)")
        login_parser.add_argument("--server", help="Custom server URL")
        login_parser.add_argument("--sso", choices=["google", "github", "azure", "okta"], 
                                help="Use SSO provider")
        
        # Logout
        auth_subparsers.add_parser("logout", help="Logout from UPID")
        
        # Status
        auth_subparsers.add_parser("status", help="Show authentication status")
        
        # Clusters commands
        clusters_parser = subparsers.add_parser("clusters", help="Cluster management")
        clusters_subparsers = clusters_parser.add_subparsers(dest="clusters_command")
        
        # List clusters
        clusters_subparsers.add_parser("list", help="List clusters")
        
        # Get cluster
        get_cluster_parser = clusters_subparsers.add_parser("get", help="Get cluster details")
        get_cluster_parser.add_argument("cluster_id", help="Cluster ID")
        
        # Add cluster
        add_cluster_parser = clusters_subparsers.add_parser("add", help="Add cluster")
        add_cluster_parser.add_argument("name", help="Cluster name")
        add_cluster_parser.add_argument("--kubeconfig", help="Path to kubeconfig file")
        add_cluster_parser.add_argument("--context", help="Kubernetes context")
        
        # Analyze commands
        analyze_parser = subparsers.add_parser("analyze", help="Analysis commands")
        analyze_subparsers = analyze_parser.add_subparsers(dest="analyze_command")
        
        # Analyze cluster
        analyze_cluster_parser = analyze_subparsers.add_parser("cluster", help="Analyze cluster")
        analyze_cluster_parser.add_argument("cluster_id", help="Cluster ID")
        analyze_cluster_parser.add_argument("--time-range", default="24h", help="Time range for analysis")
        analyze_cluster_parser.add_argument("--detailed", action="store_true", help="Detailed analysis")
        analyze_cluster_parser.add_argument("--include-costs", action="store_true", help="Include cost analysis")
        
        # Analyze pod
        analyze_pod_parser = analyze_subparsers.add_parser("pod", help="Analyze specific pod")
        analyze_pod_parser.add_argument("cluster_id", help="Cluster ID")
        analyze_pod_parser.add_argument("pod_name", help="Pod name")
        analyze_pod_parser.add_argument("--namespace", default="default", help="Namespace")
        analyze_pod_parser.add_argument("--time-range", default="24h", help="Time range for analysis")
        
        # Find idle workloads
        idle_parser = analyze_subparsers.add_parser("idle", help="Find idle workloads")
        idle_parser.add_argument("cluster_id", help="Cluster ID")
        idle_parser.add_argument("--confidence", type=float, default=0.85, help="Confidence threshold")
        idle_parser.add_argument("--time-range", default="7d", help="Time range for analysis")
        
        # Analyze resources
        resources_parser = analyze_subparsers.add_parser("resources", help="Analyze resource usage")
        resources_parser.add_argument("cluster_id", help="Cluster ID")
        resources_parser.add_argument("--resource-type", default="all", help="Resource type to analyze")
        resources_parser.add_argument("--time-range", default="24h", help="Time range for analysis")
        
        # Analyze costs
        costs_parser = analyze_subparsers.add_parser("costs", help="Analyze cluster costs")
        costs_parser.add_argument("cluster_id", help="Cluster ID")
        costs_parser.add_argument("--time-range", default="30d", help="Time range for analysis")
        costs_parser.add_argument("--detailed", action="store_true", help="Detailed cost breakdown")
        
        # Analyze performance
        performance_parser = analyze_subparsers.add_parser("performance", help="Analyze cluster performance")
        performance_parser.add_argument("cluster_id", help="Cluster ID")
        performance_parser.add_argument("--time-range", default="24h", help="Time range for analysis")
        performance_parser.add_argument("--detailed", action="store_true", help="Detailed performance analysis")
        
        # Optimize commands
        optimize_parser = subparsers.add_parser("optimize", help="Optimization commands")
        optimize_subparsers = optimize_parser.add_subparsers(dest="optimize_command")
        
        # Simulate optimization
        simulate_parser = optimize_subparsers.add_parser("simulate", help="Simulate optimization")
        simulate_parser.add_argument("cluster_id", help="Cluster ID")
        simulate_parser.add_argument("strategy", help="Optimization strategy")
        simulate_parser.add_argument("--safety-level", choices=["low", "medium", "high"], 
                                   default="medium", help="Safety level")
        
        # Apply optimization
        apply_parser = optimize_subparsers.add_parser("apply", help="Apply optimization")
        apply_parser.add_argument("cluster_id", help="Cluster ID")
        apply_parser.add_argument("optimization_id", help="Optimization ID")
        apply_parser.add_argument("--confirm", action="store_true", help="Skip confirmation")
        
        # Auto optimize
        auto_parser = optimize_subparsers.add_parser("auto", help="Auto optimize cluster")
        auto_parser.add_argument("cluster_id", help="Cluster ID")
        auto_parser.add_argument("--safety-level", choices=["low", "medium", "high"], 
                               default="medium", help="Safety level")
        
        # Monitor commands
        monitor_parser = subparsers.add_parser("monitor", help="Monitoring commands")
        monitor_subparsers = monitor_parser.add_subparsers(dest="monitor_command")
        
        # Start monitoring
        start_monitor_parser = monitor_subparsers.add_parser("start", help="Start monitoring")
        start_monitor_parser.add_argument("cluster_id", help="Cluster ID")
        start_monitor_parser.add_argument("--interval", type=int, default=60, help="Monitoring interval (seconds)")
        
        # Stop monitoring
        stop_monitor_parser = monitor_subparsers.add_parser("stop", help="Stop monitoring")
        stop_monitor_parser.add_argument("cluster_id", help="Cluster ID")
        
        # Get alerts
        alerts_parser = monitor_subparsers.add_parser("alerts", help="Get monitoring alerts")
        alerts_parser.add_argument("cluster_id", help="Cluster ID")
        alerts_parser.add_argument("--severity", choices=["low", "medium", "high", "critical"], 
                                 help="Filter by severity")
        
        # Report commands
        report_parser = subparsers.add_parser("report", help="Reporting commands")
        report_subparsers = report_parser.add_subparsers(dest="report_command")
        
        # Generate report
        generate_parser = report_subparsers.add_parser("generate", help="Generate report")
        generate_parser.add_argument("cluster_id", help="Cluster ID")
        generate_parser.add_argument("report_type", help="Report type")
        generate_parser.add_argument("--time-range", default="30d", help="Time range for report")
        
        # List reports
        report_subparsers.add_parser("list", help="List available reports")
        
        # Get report
        get_report_parser = report_subparsers.add_parser("get", help="Get specific report")
        get_report_parser.add_argument("cluster_id", help="Cluster ID")
        get_report_parser.add_argument("report_id", help="Report ID")
        
        # AI commands
        ai_parser = subparsers.add_parser("ai", help="AI/ML commands")
        ai_subparsers = ai_parser.add_subparsers(dest="ai_command")
        
        # Get insights
        insights_parser = ai_subparsers.add_parser("insights", help="Get AI insights")
        insights_parser.add_argument("cluster_id", help="Cluster ID")
        
        # Predict scaling
        predict_scaling_parser = ai_subparsers.add_parser("predict-scaling", help="Predict scaling needs")
        predict_scaling_parser.add_argument("cluster_id", help="Cluster ID")
        predict_scaling_parser.add_argument("--horizon", type=int, default=7, help="Prediction horizon (days)")
        
        # Predict costs
        predict_costs_parser = ai_subparsers.add_parser("predict-costs", help="Predict future costs")
        predict_costs_parser.add_argument("cluster_id", help="Cluster ID")
        predict_costs_parser.add_argument("--horizon", type=int, default=30, help="Prediction horizon (days)")
        
        # Detect anomalies
        anomalies_parser = ai_subparsers.add_parser("anomalies", help="Detect anomalies")
        anomalies_parser.add_argument("cluster_id", help="Cluster ID")
        
        # Enterprise commands
        enterprise_parser = subparsers.add_parser("enterprise", help="Enterprise features")
        enterprise_subparsers = enterprise_parser.add_subparsers(dest="enterprise_command")
        
        # Sync enterprise data
        sync_parser = enterprise_subparsers.add_parser("sync", help="Sync enterprise data")
        sync_parser.add_argument("cluster_id", help="Cluster ID")
        
        # Get enterprise status
        enterprise_subparsers.add_parser("status", help="Get enterprise status")
        
        # System commands
        system_parser = subparsers.add_parser("system", help="System commands")
        system_subparsers = system_parser.add_subparsers(dest="system_command")
        
        # Health check
        system_subparsers.add_parser("health", help="System health check")
        
        # Get metrics
        system_subparsers.add_parser("metrics", help="Get system metrics")
        
        # Get version
        system_subparsers.add_parser("version", help="Get system version")
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with given arguments"""
        try:
            # Parse arguments
            parsed_args = self.parser.parse_args(args)
            
            # Update config from arguments
            if parsed_args.debug:
                self.config.debug = True
            if parsed_args.verbose:
                self.config.verbose = True
            if parsed_args.quiet:
                self.config.quiet = True
            if parsed_args.output:
                self.config.output_format = parsed_args.output
            
            # Handle commands
            if parsed_args.command == "auth":
                return self._handle_auth(parsed_args)
            elif parsed_args.command == "clusters":
                return self._handle_clusters(parsed_args)
            elif parsed_args.command == "analyze":
                return self._handle_analyze(parsed_args)
            elif parsed_args.command == "optimize":
                return self._handle_optimize(parsed_args)
            elif parsed_args.command == "monitor":
                return self._handle_monitor(parsed_args)
            elif parsed_args.command == "report":
                return self._handle_report(parsed_args)
            elif parsed_args.command == "ai":
                return self._handle_ai(parsed_args)
            elif parsed_args.command == "enterprise":
                return self._handle_enterprise(parsed_args)
            elif parsed_args.command == "system":
                return self._handle_system(parsed_args)
            else:
                self.parser.print_help()
                return 0
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 1
        except Exception as e:
            if self.config.debug:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {e}")
            return 1
    
    def _handle_auth(self, args) -> int:
        """Handle authentication commands"""
        if args.auth_command == "login":
            email = args.email
            password = args.password
            
            if not password:
                import getpass
                password = getpass.getpass("Password: ")
            
            if args.sso:
                success = self.auth_manager.sso_login(args.sso)
            else:
                success = self.auth_manager.login(email, password, args.server)
            
            if success:
                print("✅ Login successful!")
                return 0
            else:
                print("❌ Login failed!")
                return 1
        
        elif args.auth_command == "logout":
            success = self.auth_manager.logout()
            if success:
                print("✅ Logout successful!")
                return 0
            else:
                print("❌ Logout failed!")
                return 1
        
        elif args.auth_command == "status":
            if self.auth_manager.is_authenticated():
                user_info = self.auth_manager.get_user_info()
                if user_info:
                    print(f"✅ Authenticated as: {user_info.get('email', 'Unknown')}")
                    print(f"User ID: {user_info.get('user_id', 'Unknown')}")
                    if user_info.get('organization_id'):
                        print(f"Organization: {user_info.get('organization_id')}")
                else:
                    print("✅ Authenticated (user info unavailable)")
            else:
                print("❌ Not authenticated")
                return 1
            return 0
        
        return 0
    
    def _handle_clusters(self, args) -> int:
        """Handle cluster management commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.clusters_command == "list":
            response = self.api_client.list_clusters()
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to list clusters: {response.error_message}")
                return 1
        
        elif args.clusters_command == "get":
            response = self.api_client.get_cluster(args.cluster_id)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get cluster: {response.error_message}")
                return 1
        
        elif args.clusters_command == "add":
            cluster_data = {
                "name": args.name,
                "kubeconfig": args.kubeconfig,
                "context": args.context
            }
            response = self.api_client.add_cluster(cluster_data)
            if self.api_client.handle_response(response):
                print("✅ Cluster added successfully!")
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to add cluster: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_analyze(self, args) -> int:
        """Handle analysis commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.analyze_command == "cluster":
            params = {
                "time_range": args.time_range,
                "detailed": args.detailed,
                "include_costs": args.include_costs
            }
            response = self.api_client.analyze_cluster(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to analyze cluster: {response.error_message}")
                return 1
        
        elif args.analyze_command == "pod":
            params = {
                "time_range": args.time_range
            }
            response = self.api_client.analyze_pod(args.cluster_id, args.pod_name, args.namespace, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to analyze pod: {response.error_message}")
                return 1
        
        elif args.analyze_command == "idle":
            params = {
                "confidence": args.confidence,
                "time_range": args.time_range
            }
            response = self.api_client.find_idle_workloads(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to find idle workloads: {response.error_message}")
                return 1
        
        elif args.analyze_command == "resources":
            params = {
                "time_range": args.time_range
            }
            response = self.api_client.analyze_resources(args.cluster_id, args.resource_type, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to analyze resources: {response.error_message}")
                return 1
        
        elif args.analyze_command == "costs":
            params = {
                "time_range": args.time_range,
                "detailed": args.detailed
            }
            response = self.api_client.analyze_costs(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to analyze costs: {response.error_message}")
                return 1
        
        elif args.analyze_command == "performance":
            params = {
                "time_range": args.time_range,
                "detailed": args.detailed
            }
            response = self.api_client.analyze_performance(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to analyze performance: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_optimize(self, args) -> int:
        """Handle optimization commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.optimize_command == "simulate":
            params = {
                "safety_level": args.safety_level
            }
            response = self.api_client.simulate_optimization(args.cluster_id, args.strategy, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to simulate optimization: {response.error_message}")
                return 1
        
        elif args.optimize_command == "apply":
            if not args.confirm:
                confirm = input(f"Are you sure you want to apply optimization {args.optimization_id}? (y/N): ")
                if confirm.lower() != 'y':
                    print("Operation cancelled")
                    return 0
            
            response = self.api_client.apply_optimization(args.cluster_id, args.optimization_id)
            if self.api_client.handle_response(response):
                print("✅ Optimization applied successfully!")
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to apply optimization: {response.error_message}")
                return 1
        
        elif args.optimize_command == "auto":
            params = {
                "safety_level": args.safety_level
            }
            response = self.api_client.auto_optimize(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print("✅ Auto-optimization completed!")
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to auto-optimize: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_monitor(self, args) -> int:
        """Handle monitoring commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.monitor_command == "start":
            params = {
                "interval": args.interval
            }
            response = self.api_client.start_monitoring(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print("✅ Monitoring started successfully!")
                return 0
            else:
                print(f"❌ Failed to start monitoring: {response.error_message}")
                return 1
        
        elif args.monitor_command == "stop":
            response = self.api_client.stop_monitoring(args.cluster_id)
            if self.api_client.handle_response(response):
                print("✅ Monitoring stopped successfully!")
                return 0
            else:
                print(f"❌ Failed to stop monitoring: {response.error_message}")
                return 1
        
        elif args.monitor_command == "alerts":
            params = {}
            if args.severity:
                params["severity"] = args.severity
            response = self.api_client.get_alerts(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get alerts: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_report(self, args) -> int:
        """Handle reporting commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.report_command == "generate":
            params = {
                "time_range": args.time_range
            }
            response = self.api_client.generate_report(args.cluster_id, args.report_type, params)
            if self.api_client.handle_response(response):
                print("✅ Report generated successfully!")
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to generate report: {response.error_message}")
                return 1
        
        elif args.report_command == "list":
            response = self.api_client.get_reports(args.cluster_id)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to list reports: {response.error_message}")
                return 1
        
        elif args.report_command == "get":
            response = self.api_client.get_report(args.cluster_id, args.report_id)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get report: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_ai(self, args) -> int:
        """Handle AI/ML commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.ai_command == "insights":
            response = self.api_client.get_ai_insights(args.cluster_id)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get AI insights: {response.error_message}")
                return 1
        
        elif args.ai_command == "predict-scaling":
            params = {
                "horizon": args.horizon
            }
            response = self.api_client.predict_scaling(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to predict scaling: {response.error_message}")
                return 1
        
        elif args.ai_command == "predict-costs":
            params = {
                "horizon": args.horizon
            }
            response = self.api_client.predict_costs(args.cluster_id, params)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to predict costs: {response.error_message}")
                return 1
        
        elif args.ai_command == "anomalies":
            response = self.api_client.detect_anomalies(args.cluster_id)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to detect anomalies: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_enterprise(self, args) -> int:
        """Handle enterprise commands"""
        if not self.auth_manager.is_authenticated():
            print("❌ Authentication required. Please run 'upid auth login' first.")
            return 1
        
        if args.enterprise_command == "sync":
            response = self.api_client.sync_enterprise_data(args.cluster_id)
            if self.api_client.handle_response(response):
                print("✅ Enterprise data synced successfully!")
                return 0
            else:
                print(f"❌ Failed to sync enterprise data: {response.error_message}")
                return 1
        
        elif args.enterprise_command == "status":
            response = self.api_client.get_enterprise_status(args.cluster_id)
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get enterprise status: {response.error_message}")
                return 1
        
        return 0
    
    def _handle_system(self, args) -> int:
        """Handle system commands"""
        if args.system_command == "health":
            response = self.api_client.get_system_health()
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get system health: {response.error_message}")
                return 1
        
        elif args.system_command == "metrics":
            response = self.api_client.get_system_metrics()
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get system metrics: {response.error_message}")
                return 1
        
        elif args.system_command == "version":
            response = self.api_client.get_version()
            if self.api_client.handle_response(response):
                print(self.api_client.format_response(response))
                return 0
            else:
                print(f"❌ Failed to get version: {response.error_message}")
                return 1
        
        return 0


def cli():
    """Main CLI entry point"""
    cli_instance = UPIDCLI()
    return cli_instance.run()


def main():
    """Main entry point for Go integration"""
    cli_instance = UPIDCLI()
    return cli_instance.run()


if __name__ == "__main__":
    sys.exit(cli()) 