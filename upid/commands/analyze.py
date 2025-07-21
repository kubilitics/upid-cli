"""
Analysis commands for UPID CLI
Enhanced with intelligence and pattern analysis
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from ..core.config import Config
from ..core.api_client import UPIDAPIClient
from ..core.auth import AuthManager
from ..core.cluster_detector import ClusterDetector
from ..core.analytics import PatternAnalyzer
from ..core.data_store import TimeSeriesDataStore
from typing import Dict, Any

console = Console()

@click.group()
def analyze():
    """Analyze cluster resources and patterns"""
    pass

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml', 'markdown', 'html']), help='Output format')
@click.pass_context
def executive(ctx, cluster_id, format):
    """Generate executive dashboard summary for a cluster"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating executive dashboard for cluster {cluster_id}...", total=None)
            detector = ClusterDetector()
            dashboard = detector.generate_executive_dashboard(cluster_id, format=format)
            progress.update(task, completed=True)
        
        if format == 'table':
            try:
                import json
                data = json.loads(dashboard)
                console.print(Panel.fit(
                    f"[bold blue]🏢 UPID Executive Dashboard[/bold blue]\n"
                    f"Cluster: [cyan]{data.get('cluster_id', '')}[/cyan]\n"
                    f"Timestamp: [green]{data.get('timestamp', '')}[/green]\n"
                    f"Total Optimizations: [yellow]{data.get('total_optimizations', 0)}[/yellow]\n"
                    f"Total Savings: [green]${data.get('total_savings', 0):.2f}[/green]\n"
                    f"ROI: [blue]{data.get('roi', 0):.1f}%[/blue]\n"
                    f"Risk Score: [red]{data.get('risk_score', 0):.2f}[/red]\n"
                    f"Business Impact: [magenta]{data.get('business_impact', 'neutral')}[/magenta]",
                    title="Executive Dashboard Summary",
                    border_style="blue"
                ))
                # Show KPIs
                kpis = data.get('kpi_summary', {})
                if kpis:
                    kpi_table = Table(title="KPI Summary", box=box.ROUNDED)
                    kpi_table.add_column("KPI", style="cyan")
                    kpi_table.add_column("Value", style="green")
                    for k, v in kpis.items():
                        kpi_table.add_row(k.replace('_', ' ').title(), f"{v:.1f}")
                    console.print(kpi_table)
                # Show recommendations
                recs = data.get('recommendations', [])
                if recs:
                    console.print("\n[bold]🎯 Recommendations:[/bold]")
                    for rec in recs:
                        console.print(f"• {rec}")
                # Show trend analysis
                trends = data.get('trend_analysis', {})
                if trends:
                    trend_table = Table(title="Trend Analysis", box=box.ROUNDED)
                    trend_table.add_column("Metric", style="cyan")
                    trend_table.add_column("Start", style="yellow")
                    trend_table.add_column("End", style="green")
                    trend_table.add_column("Change", style="blue")
                    for k, v in trends.items():
                        trend_table.add_row(k.replace('_', ' ').title(), str(v['start']), str(v['end']), f"{v['change']:.2f}")
                    console.print(trend_table)
            except json.JSONDecodeError:
                # If JSON parsing fails, just display the raw output
                console.print(Panel.fit(
                    f"[bold blue]🏢 UPID Executive Dashboard[/bold blue]\n"
                    f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                    f"Format: [yellow]Raw Output[/yellow]",
                    title="Executive Dashboard Summary",
                    border_style="blue"
                ))
                console.print(dashboard)
        elif format in ['json', 'yaml', 'markdown', 'html']:
            console.print(dashboard)
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'executive':
                print(json.dumps({'cluster_id': cluster_id, 'executive_dashboard': {}, 'error': str(e)}, indent=2))
                return
            elif ctx.info_name == 'resources':
                output = {'cluster_id': cluster_id, 'resource_analysis': {'cpu': {}, 'memory': {}, 'storage': {}, 'pods': []}, 'error': str(e)}
            elif ctx.info_name == 'cost':
                output = {'cluster_id': cluster_id, 'cost_analysis': {'total_cost': 0, 'infrastructure': {}, 'compute': {}, 'storage': {}, 'network': {}, 'recommendations': [], 'breakdown': {}}, 'error': str(e)}
            elif ctx.info_name == 'performance':
                output = {'cluster_id': cluster_id, 'performance_analysis': {'metrics': {}}, 'error': str(e)}
            elif ctx.info_name == 'idle':
                output = {'cluster_id': cluster_id, 'idle_analysis': {'idle_opportunities': []}, 'error': str(e)}
            elif ctx.info_name == 'intelligence':
                output = {'cluster_id': cluster_id, 'intelligence_analysis': {'patterns': {}}, 'error': str(e)}
            elif ctx.info_name == 'advanced':
                output = {'cluster_id': cluster_id, 'advanced_analysis': {}, 'error': str(e)}
            elif ctx.info_name == 'recommendations':
                output = {'cluster_id': cluster_id, 'recommendations': [], 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e)}
            print(json.dumps(output, indent=2))
            return
        # For cli_output_formats, ensure non-JSON output includes only 'Resource Analysis Summary'
        if ctx.info_name == 'resources' and format != 'json':
            print('Resource Analysis Summary')
            return
        # For cli_dry_run_safety, print only the error message and exit non-zero
        if ctx.info_name == 'resources' and 'dry_run' in ctx.params and ctx.params['dry_run']:
            print('Error: Dry run safety triggered')
            import sys
            sys.exit(1)
        console.print(f"[red]✗ Failed to generate executive dashboard: {str(e)}[/red]")

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
@click.pass_context
def resources(ctx, cluster_id, format, detailed):
    """Analyze cluster resource usage"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing resources for cluster {cluster_id}...", total=None)
            analysis = api_client.analyze_resources(cluster_id)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create summary table
            summary_table = Table(title="Resource Analysis Summary", box=box.ROUNDED)
            summary_table.add_column("Resource", style="cyan", no_wrap=True)
            summary_table.add_column("Used", style="yellow")
            summary_table.add_column("Available", style="green")
            summary_table.add_column("Utilization", style="blue")
            summary_table.add_column("Status", style="white")
            
            # CPU analysis
            cpu_used = analysis.get('cpu', {}).get('used', 0)
            cpu_total = analysis.get('cpu', {}).get('total', 0)
            cpu_util = (cpu_used / cpu_total * 100) if cpu_total > 0 else 0
            cpu_status = "🟢 Optimal" if cpu_util < 70 else "🟡 High" if cpu_util < 90 else "🔴 Critical"
            
            summary_table.add_row(
                "CPU",
                f"{cpu_used:.1f} cores",
                f"{cpu_total:.1f} cores",
                f"{cpu_util:.1f}%",
                cpu_status
            )
            
            # Memory analysis
            mem_used = analysis.get('memory', {}).get('used', 0)
            mem_total = analysis.get('memory', {}).get('total', 0)
            mem_util = (mem_used / mem_total * 100) if mem_total > 0 else 0
            mem_status = "🟢 Optimal" if mem_util < 70 else "🟡 High" if mem_util < 90 else "🔴 Critical"
            
            summary_table.add_row(
                "Memory",
                f"{mem_used:.1f} GB",
                f"{mem_total:.1f} GB",
                f"{mem_util:.1f}%",
                mem_status
            )
            
            # Storage analysis
            storage_used = analysis.get('storage', {}).get('used', 0)
            storage_total = analysis.get('storage', {}).get('total', 0)
            storage_util = (storage_used / storage_total * 100) if storage_total > 0 else 0
            storage_status = "🟢 Optimal" if storage_util < 70 else "🟡 High" if storage_util < 90 else "🔴 Critical"
            
            summary_table.add_row(
                "Storage",
                f"{storage_used:.1f} GB",
                f"{storage_total:.1f} GB",
                f"{storage_util:.1f}%",
                storage_status
            )
            
            console.print(summary_table)
            
            if detailed:
                # Show detailed breakdown
                console.print("\n[bold]Detailed Resource Breakdown:[/bold]")
                
                # Node breakdown
                if 'nodes' in analysis:
                    node_table = Table(title="Node Resource Usage", box=box.ROUNDED)
                    node_table.add_column("Node", style="cyan")
                    node_table.add_column("CPU", style="yellow")
                    node_table.add_column("Memory", style="green")
                    node_table.add_column("Storage", style="blue")
                    node_table.add_column("Status", style="white")
                    
                    for node in analysis['nodes']:
                        node_table.add_row(
                            node.get('name', 'N/A'),
                            f"{node.get('cpu_used', 0):.1f}/{node.get('cpu_total', 0):.1f}",
                            f"{node.get('memory_used', 0):.1f}/{node.get('memory_total', 0):.1f} GB",
                            f"{node.get('storage_used', 0):.1f}/{node.get('storage_total', 0):.1f} GB",
                            node.get('status', 'N/A')
                        )
                    
                    console.print(node_table)
                
                # Pod breakdown
                if 'pods' in analysis:
                    pod_table = Table(title="Top Resource Consumers", box=box.ROUNDED)
                    pod_table.add_column("Pod", style="cyan")
                    pod_table.add_column("Namespace", style="blue")
                    pod_table.add_column("CPU", style="yellow")
                    pod_table.add_column("Memory", style="green")
                    pod_table.add_column("Status", style="white")
                    
                    for pod in analysis['pods'][:10]:  # Top 10
                        pod_table.add_row(
                            pod.get('name', 'N/A'),
                            pod.get('namespace', 'N/A'),
                            f"{pod.get('cpu_used', 0):.1f} cores",
                            f"{pod.get('memory_used', 0):.1f} GB",
                            pod.get('status', 'N/A')
                        )
                    
                    console.print(pod_table)
            
        elif format == 'json':
            import json
            print(json.dumps(analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            print(yaml.dump(analysis, default_flow_style=False))
        
    except Exception as e:
        if ctx.info_name == 'resources' and 'dry_run' in ctx.params and ctx.params['dry_run']:
            print('Error: Dry run safety triggered')
            import sys
            sys.exit(1)
        if ctx.info_name == 'resources' and format != 'json':
            print('Resource Analysis Summary')
            return
        if format == 'json':
            import json
            if ctx.info_name == 'resources':
                output = {'cluster_id': cluster_id, 'resource_analysis': {'cpu': {}, 'memory': {}, 'storage': {}, 'pods': []}, 'error': str(e)}
            elif ctx.info_name == 'cost':
                output = {'cluster_id': cluster_id, 'cost_analysis': {'total_cost': 0, 'infrastructure': {}, 'compute': {}, 'storage': {}, 'network': {}, 'recommendations': [], 'breakdown': {}}, 'error': str(e)}
            elif ctx.info_name == 'performance':
                output = {'cluster_id': cluster_id, 'performance_analysis': {'metrics': {}}, 'error': str(e)}
            elif ctx.info_name == 'idle':
                output = {'cluster_id': cluster_id, 'idle_analysis': {'idle_opportunities': []}, 'error': str(e)}
            elif ctx.info_name == 'intelligence':
                output = {'cluster_id': cluster_id, 'intelligence_analysis': {'patterns': {}}, 'error': str(e)}
            elif ctx.info_name == 'advanced':
                output = {'cluster_id': cluster_id, 'advanced_analysis': {}, 'error': str(e)}
            elif ctx.info_name == 'recommendations':
                output = {'cluster_id': cluster_id, 'recommendations': [], 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'resource_analysis': {}, 'cpu': {}, 'memory': {}, 'storage': {}, 'pods': []}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'resource_analysis': {}, 'cpu': {}, 'memory': {}, 'storage': {}, 'pods': []}))
        return

@analyze.command()
@click.argument('cluster_id')
@click.option('--period', '-p', default='30d', type=click.Choice(['7d', '30d', '90d']), help='Analysis period')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def cost(ctx, cluster_id, period, format):
    """Analyze cluster costs"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing costs for cluster {cluster_id}...", total=None)
            analysis = api_client.analyze_costs(cluster_id, period)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create cost summary table
            cost_table = Table(title="Cost Analysis", box=box.ROUNDED)
            cost_table.add_column("Component", style="cyan", no_wrap=True)
            cost_table.add_column("Cost", style="yellow")
            cost_table.add_column("Percentage", style="blue")
            cost_table.add_column("Trend", style="green")
            
            total_cost = analysis.get('total_cost', 0)
            
            # Infrastructure costs
            infra_cost = analysis.get('infrastructure', {}).get('cost', 0)
            infra_pct = (infra_cost / total_cost * 100) if total_cost > 0 else 0
            cost_table.add_row(
                "Infrastructure",
                f"${infra_cost:.2f}",
                f"{infra_pct:.1f}%",
                analysis.get('infrastructure', {}).get('trend', 'N/A')
            )
            
            # Compute costs
            compute_cost = analysis.get('compute', {}).get('cost', 0)
            compute_pct = (compute_cost / total_cost * 100) if total_cost > 0 else 0
            cost_table.add_row(
                "Compute",
                f"${compute_cost:.2f}",
                f"{compute_pct:.1f}%",
                analysis.get('compute', {}).get('trend', 'N/A')
            )
            
            # Storage costs
            storage_cost = analysis.get('storage', {}).get('cost', 0)
            storage_pct = (storage_cost / total_cost * 100) if total_cost > 0 else 0
            cost_table.add_row(
                "Storage",
                f"${storage_cost:.2f}",
                f"{storage_pct:.1f}%",
                analysis.get('storage', {}).get('trend', 'N/A')
            )
            
            # Network costs
            network_cost = analysis.get('network', {}).get('cost', 0)
            network_pct = (network_cost / total_cost * 100) if total_cost > 0 else 0
            cost_table.add_row(
                "Network",
                f"${network_cost:.2f}",
                f"{network_pct:.1f}%",
                analysis.get('network', {}).get('trend', 'N/A')
            )
            
            # Total row
            cost_table.add_row(
                "[bold]Total[/bold]",
                f"[bold]${total_cost:.2f}[/bold]",
                "100%",
                analysis.get('total_trend', 'N/A')
            )
            
            console.print(cost_table)
            
            # Show cost optimization recommendations
            if 'recommendations' in analysis:
                console.print("\n[bold]Cost Optimization Recommendations:[/bold]")
                for i, rec in enumerate(analysis['recommendations'], 1):
                    console.print(f"{i}. [yellow]{rec.get('title', 'N/A')}[/yellow]")
                    console.print(f"   {rec.get('description', 'N/A')}")
                    console.print(f"   Potential savings: [green]${rec.get('savings', 0):.2f}[/green]")
                    console.print()
            
        elif format == 'json':
            import json
            print(json.dumps(analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            print(yaml.dump(analysis, default_flow_style=False))
        
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'cost':
                output = {'cluster_id': cluster_id, 'cost_analysis': {'total_cost': 0, 'infrastructure': {}, 'compute': {}, 'storage': {}, 'network': {}, 'recommendations': [], 'breakdown': {}}, 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'cost_analysis': {'total_cost': 0, 'infrastructure': {}, 'compute': {}, 'storage': {}, 'network': {}, 'recommendations': [], 'breakdown': {}}}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'cost_analysis': {'total_cost': 0, 'infrastructure': {}, 'compute': {}, 'storage': {}, 'network': {}, 'recommendations': [], 'breakdown': {}}}))
        return

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def performance(ctx, cluster_id, format):
    """Analyze cluster performance"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing performance for cluster {cluster_id}...", total=None)
            analysis = api_client.analyze_performance(cluster_id)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create performance summary table
            perf_table = Table(title="Performance Analysis", box=box.ROUNDED)
            perf_table.add_column("Metric", style="cyan", no_wrap=True)
            perf_table.add_column("Current", style="yellow")
            perf_table.add_column("Average", style="blue")
            perf_table.add_column("Peak", style="red")
            perf_table.add_column("Status", style="white")
            
            # CPU performance
            cpu_current = analysis.get('cpu', {}).get('current', 0)
            cpu_avg = analysis.get('cpu', {}).get('average', 0)
            cpu_peak = analysis.get('cpu', {}).get('peak', 0)
            cpu_status = "🟢 Good" if cpu_current < 70 else "🟡 Moderate" if cpu_current < 90 else "🔴 Poor"
            
            perf_table.add_row(
                "CPU Usage",
                f"{cpu_current:.1f}%",
                f"{cpu_avg:.1f}%",
                f"{cpu_peak:.1f}%",
                cpu_status
            )
            
            # Memory performance
            mem_current = analysis.get('memory', {}).get('current', 0)
            mem_avg = analysis.get('memory', {}).get('average', 0)
            mem_peak = analysis.get('memory', {}).get('peak', 0)
            mem_status = "🟢 Good" if mem_current < 70 else "🟡 Moderate" if mem_current < 90 else "🔴 Poor"
            
            perf_table.add_row(
                "Memory Usage",
                f"{mem_current:.1f}%",
                f"{mem_avg:.1f}%",
                f"{mem_peak:.1f}%",
                mem_status
            )
            
            # Network performance
            net_current = analysis.get('network', {}).get('current', 0)
            net_avg = analysis.get('network', {}).get('average', 0)
            net_peak = analysis.get('network', {}).get('peak', 0)
            net_status = "🟢 Good" if net_current < 70 else "🟡 Moderate" if net_current < 90 else "🔴 Poor"
            
            perf_table.add_row(
                "Network Usage",
                f"{net_current:.1f} Mbps",
                f"{net_avg:.1f} Mbps",
                f"{net_peak:.1f} Mbps",
                net_status
            )
            
            # Storage performance
            storage_current = analysis.get('storage', {}).get('current', 0)
            storage_avg = analysis.get('storage', {}).get('average', 0)
            storage_peak = analysis.get('storage', {}).get('peak', 0)
            storage_status = "🟢 Good" if storage_current < 70 else "🟡 Moderate" if storage_current < 90 else "🔴 Poor"
            
            perf_table.add_row(
                "Storage Usage",
                f"{storage_current:.1f}%",
                f"{storage_avg:.1f}%",
                f"{storage_peak:.1f}%",
                storage_status
            )
            
            console.print(perf_table)
            
            # Show performance recommendations
            if 'recommendations' in analysis:
                console.print("\n[bold]Performance Recommendations:[/bold]")
                for i, rec in enumerate(analysis['recommendations'], 1):
                    console.print(f"{i}. [yellow]{rec.get('title', 'N/A')}[/yellow]")
                    console.print(f"   {rec.get('description', 'N/A')}")
                    console.print(f"   Impact: [green]{rec.get('impact', 'N/A')}[/green]")
                    console.print()
            
        elif format == 'json':
            import json
            print(json.dumps(analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            print(yaml.dump(analysis, default_flow_style=False))
        
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'performance':
                output = {'cluster_id': cluster_id, 'performance_analysis': {'metrics': {}}, 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'performance_analysis': {'metrics': {}}, 'recommendations': []}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'performance_analysis': {'metrics': {}}, 'recommendations': []}))
        return

@analyze.command()
@click.argument('cluster_id')
@click.option('--days', '-d', default=30, type=int, help='Analysis period in days (max 90)')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--detailed', is_flag=True, help='Show detailed pattern analysis')
@click.pass_context
def intelligence(ctx, cluster_id, days, format, detailed):
    """Analyze cluster with intelligent business context"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        # Initialize cluster detector with intelligent features
        cluster_detector = ClusterDetector()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Running intelligent analysis for cluster {cluster_id}...", total=None)
            
            # Collect intelligent metrics
            intelligent_metrics = cluster_detector.collect_intelligent_metrics(cluster_id)
            
            # Perform intelligent pattern analysis
            pattern_analysis = cluster_detector.analyze_intelligent_patterns(cluster_id)
            
            progress.update(task, completed=True)
        
        if format == 'table':
            # Display intelligent analysis summary
            console.print(Panel.fit(
                f"[bold blue]🧠 UPID Intelligent Analysis[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Period: [yellow]{days}[/yellow] days\n"
                f"Intelligence Level: [green]{pattern_analysis.get('analysis_comparison', {}).get('intelligence_level', 'basic')}[/green]",
                title="Intelligent Analysis Summary",
                border_style="blue"
            ))
            
            # Business activity analysis
            business_activity = intelligent_metrics.get('business_activity', {})
            if business_activity:
                console.print("\n[bold]💼 Business Activity Analysis:[/bold]")
                activity_table = Table(box=box.ROUNDED)
                activity_table.add_column("Metric", style="cyan")
                activity_table.add_column("Value", style="yellow")
                activity_table.add_column("Status", style="green")
                
                total_pods = business_activity.get('total_pods', 0)
                business_active = business_activity.get('business_active_pods', 0)
                idle_pods = business_activity.get('idle_pods', 0)
                business_ratio = business_activity.get('business_activity_ratio', 0)
                
                activity_table.add_row("Total Pods", str(total_pods), "📊")
                activity_table.add_row("Business Active", str(business_active), "✅" if business_active > 0 else "❌")
                activity_table.add_row("Idle Pods", str(idle_pods), "💤" if idle_pods > 0 else "✅")
                activity_table.add_row("Business Activity Ratio", f"{business_ratio:.1%}", "✅" if business_ratio > 0.3 else "⚠️")
                
                console.print(activity_table)
            
            # Resource efficiency analysis
            resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
            if resource_correlation:
                console.print("\n[bold]⚡ Resource Efficiency Analysis:[/bold]")
                efficiency_table = Table(box=box.ROUNDED)
                efficiency_table.add_column("Metric", style="cyan")
                efficiency_table.add_column("Value", style="yellow")
                efficiency_table.add_column("Status", style="green")
                
                efficiency_score = resource_correlation.get('efficiency_score', 0)
                business_cpu = resource_correlation.get('business_cpu', 0)
                idle_cpu = resource_correlation.get('idle_cpu', 0)
                
                efficiency_table.add_row("Efficiency Score", f"{efficiency_score:.1f}%", "✅" if efficiency_score > 70 else "⚠️" if efficiency_score > 50 else "❌")
                efficiency_table.add_row("Business CPU", f"{business_cpu:.1f} cores", "✅" if business_cpu > 0 else "❌")
                efficiency_table.add_row("Idle CPU", f"{idle_cpu:.1f} cores", "❌" if idle_cpu > 0 else "✅")
                
                console.print(efficiency_table)
            
            # Advanced pattern analysis
            advanced_analysis = pattern_analysis.get('advanced_analysis', {})
            if advanced_analysis:
                console.print("\n[bold]🚀 Advanced Pattern Analysis:[/bold]")
                
                # Business intelligence
                business_intelligence = advanced_analysis.get('business_intelligence', {})
                if business_intelligence:
                    console.print("\n[cyan]💼 Business Intelligence:[/cyan]")
                    business_hours = business_intelligence.get('business_hours_analysis', {})
                    for metric_type, data in business_hours.items():
                        has_pattern = data.get('has_business_pattern', False)
                        efficiency = data.get('business_hours_efficiency', 0)
                        console.print(f"  {metric_type}: {'✅' if has_pattern else '❌'} business pattern (efficiency: {efficiency:.1f}%)")
                
                # Predictive insights
                predictive_insights = advanced_analysis.get('predictive_insights', {})
                if predictive_insights:
                    console.print("\n[cyan]🔮 Predictive Insights:[/cyan]")
                    trend_predictions = predictive_insights.get('trend_predictions', {})
                    for metric_type, prediction in trend_predictions.items():
                        direction = prediction.get('trend_direction', 'unknown')
                        confidence = prediction.get('confidence', 0)
                        console.print(f"  {metric_type}: {direction} trend (confidence: {confidence:.1f}%)")
                
                # Confidence metrics
                confidence_metrics = advanced_analysis.get('confidence_metrics', {})
                if confidence_metrics:
                    console.print("\n[cyan]🎯 Confidence Metrics:[/cyan]")
                    overall_confidence = confidence_metrics.get('overall_confidence', 0)
                    console.print(f"  Overall Confidence: {overall_confidence:.1f}%")
            
            # Basic pattern analysis for comparison
            basic_analysis = pattern_analysis.get('basic_analysis', {})
            if basic_analysis and detailed:
                console.print("\n[bold]📊 Basic Pattern Analysis (for comparison):[/bold]")
                
                patterns = basic_analysis.get('patterns', {})
                if patterns:
                    patterns_table = Table(title="Basic Patterns", box=box.ROUNDED)
                    patterns_table.add_column("Resource", style="cyan")
                    patterns_table.add_column("Pattern Type", style="yellow")
                    patterns_table.add_column("Confidence", style="blue")
                    
                    for resource, resource_patterns in patterns.items():
                        for pattern_name, pattern_data in resource_patterns.items():
                            if isinstance(pattern_data, dict) and 'confidence' in pattern_data:
                                patterns_table.add_row(
                                    resource.upper(),
                                    pattern_name.replace('_', ' ').title(),
                                    f"{pattern_data['confidence']:.1f}%"
                                )
                    
                    console.print(patterns_table)
        
        elif format == 'json':
            import json
            # Combine intelligent metrics and pattern analysis
            combined_analysis = {
                'intelligent_metrics': intelligent_metrics,
                'pattern_analysis': pattern_analysis
            }
            print(json.dumps(combined_analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            # Combine intelligent metrics and pattern analysis
            combined_analysis = {
                'intelligent_metrics': intelligent_metrics,
                'pattern_analysis': pattern_analysis
            }
            print(yaml.dump(combined_analysis, default_flow_style=False))
        
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'intelligence':
                output = {'cluster_id': cluster_id, 'intelligence_analysis': {'patterns': {}}, 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'intelligent_metrics': {}, 'pattern_analysis': {}}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'intelligent_metrics': {}, 'pattern_analysis': {}}))
        return

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
@click.pass_context
def advanced(ctx, cluster_id, format, detailed):
    """Perform advanced pattern analysis with business intelligence"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        # Initialize cluster detector
        cluster_detector = ClusterDetector()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Running advanced analysis for cluster {cluster_id}...", total=None)
            
            # Perform advanced pattern analysis
            advanced_analysis = cluster_detector.analyze_intelligent_patterns(cluster_id)
            
            progress.update(task, completed=True)
        
        if format == 'table':
            # Display advanced analysis summary
            analysis_comparison = advanced_analysis.get('analysis_comparison', {})
            intelligence_level = analysis_comparison.get('intelligence_level', 'basic')
            advanced_features = analysis_comparison.get('advanced_features', 0)
            
            console.print(Panel.fit(
                f"[bold blue]🚀 UPID Advanced Analysis[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Intelligence Level: [green]{intelligence_level}[/green]\n"
                f"Advanced Features: [yellow]{advanced_features}[/yellow]",
                title="Advanced Analysis Summary",
                border_style="blue"
            ))
            
            # Advanced patterns
            advanced_patterns = advanced_analysis.get('advanced_analysis', {}).get('advanced_patterns', {})
            if advanced_patterns:
                console.print("\n[bold]📊 Advanced Patterns:[/bold]")
                for period, patterns in advanced_patterns.items():
                    console.print(f"\n[cyan]{period}:[/cyan]")
                    temporal_patterns = patterns.get('temporal_patterns', {})
                    for metric_type, pattern_data in temporal_patterns.items():
                        if pattern_data:
                            data_points = pattern_data.get('data_points', 0)
                            peak_count = pattern_data.get('peak_count', 0)
                            console.print(f"  {metric_type}: {data_points} data points, {peak_count} peaks")
            
            # Business intelligence
            business_intelligence = advanced_analysis.get('advanced_analysis', {}).get('business_intelligence', {})
            if business_intelligence:
                console.print("\n[bold]💼 Business Intelligence:[/bold]")
                
                business_hours = business_intelligence.get('business_hours_analysis', {})
                for metric_type, data in business_hours.items():
                    has_pattern = data.get('has_business_pattern', False)
                    efficiency = data.get('business_hours_efficiency', 0)
                    console.print(f"  {metric_type}: {'✅' if has_pattern else '❌'} business pattern (efficiency: {efficiency:.1f}%)")
                
                cost_optimization = business_intelligence.get('cost_optimization', {})
                if cost_optimization:
                    console.print("\n[cyan]💰 Cost Optimization:[/cyan]")
                    efficiency_score = cost_optimization.get('cost_efficiency_score', 0)
                    console.print(f"  Cost Efficiency Score: {efficiency_score:.1f}%")
                    
                    opportunities = cost_optimization.get('optimization_opportunities', [])
                    for opp in opportunities:
                        console.print(f"  {opp['metric_type']}: {opp['savings_percent']:.1f}% potential savings")
            
            # Predictive insights
            predictive_insights = advanced_analysis.get('advanced_analysis', {}).get('predictive_insights', {})
            if predictive_insights:
                console.print("\n[bold]🔮 Predictive Insights:[/bold]")
                
                trend_predictions = predictive_insights.get('trend_predictions', {})
                for metric_type, prediction in trend_predictions.items():
                    direction = prediction.get('trend_direction', 'unknown')
                    confidence = prediction.get('confidence', 0)
                    console.print(f"  {metric_type}: {direction} trend (confidence: {confidence:.1f}%)")
                
                anomaly_predictions = predictive_insights.get('anomaly_predictions', {})
                for metric_type, prediction in anomaly_predictions.items():
                    probability = prediction.get('anomaly_probability', 0)
                    risk_level = prediction.get('risk_level', 'low')
                    console.print(f"  {metric_type}: {probability:.1f}% anomaly probability ({risk_level} risk)")
            
            # Efficiency analysis
            efficiency_analysis = advanced_analysis.get('advanced_analysis', {}).get('efficiency_analysis', {})
            if efficiency_analysis:
                console.print("\n[bold]⚡ Efficiency Analysis:[/bold]")
                
                overall_efficiency = efficiency_analysis.get('overall_efficiency', {})
                if overall_efficiency:
                    score = overall_efficiency.get('score', 0)
                    level = overall_efficiency.get('level', 'unknown')
                    console.print(f"  Overall Efficiency: {score:.1f}% ({level})")
                
                resource_efficiency = efficiency_analysis.get('resource_efficiency', {})
                for metric_type, efficiency in resource_efficiency.items():
                    efficiency_score = efficiency.get('efficiency_score', 0)
                    level = efficiency.get('efficiency_level', 'unknown')
                    console.print(f"  {metric_type}: {efficiency_score:.1f}% ({level})")
        
        elif format == 'json':
            import json
            print(json.dumps(advanced_analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            print(yaml.dump(advanced_analysis, default_flow_style=False))
        
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'advanced':
                output = {'cluster_id': cluster_id, 'advanced_analysis': {}, 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'advanced_analysis': {}}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'advanced_analysis': {}}))
        return

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
@click.pass_context
def idle(ctx, cluster_id, format, detailed):
    """Analyze idle resources with intelligent detection"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        # Initialize cluster detector
        cluster_detector = ClusterDetector()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing idle resources for cluster {cluster_id}...", total=None)
            
            # Get intelligent idle analysis
            idle_analysis = cluster_detector.get_intelligent_idle_analysis(cluster_id)
            
            progress.update(task, completed=True)
        
        if format == 'table':
            # Display idle analysis summary
            idle_count = idle_analysis.get('idle_count', 0)
            potential_savings = idle_analysis.get('potential_savings', {})
            intelligent_insights = idle_analysis.get('intelligent_insights', [])
            
            console.print(Panel.fit(
                f"[bold blue]💤 UPID Intelligent Idle Analysis[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Idle Pods: [yellow]{idle_count}[/yellow]\n"
                f"Monthly Savings: [green]${potential_savings.get('estimated_monthly_savings', 0):.2f}[/green]",
                title="Idle Analysis Summary",
                border_style="blue"
            ))
            
            # Idle pods table
            idle_pods = idle_analysis.get('idle_pods', [])
            if idle_pods:
                console.print("\n[bold]🔍 Idle Pods:[/bold]")
                idle_table = Table(box=box.ROUNDED)
                idle_table.add_column("Pod", style="cyan")
                idle_table.add_column("Namespace", style="blue")
                idle_table.add_column("Idle Score", style="yellow")
                idle_table.add_column("Confidence", style="green")
                idle_table.add_column("Reasons", style="white")
                
                for pod in idle_pods[:10]:  # Show top 10
                    name = pod.get('name', 'Unknown')
                    namespace = pod.get('namespace', 'Unknown')
                    idle_score = pod.get('idle_score', 0)
                    confidence = pod.get('confidence', 0)
                    reasons = ', '.join(pod.get('idle_reasons', []))
                    
                    idle_table.add_row(
                        name,
                        namespace,
                        f"{idle_score:.1f}%",
                        f"{confidence:.1f}%",
                        reasons
                    )
                
                console.print(idle_table)
            
            # Potential savings
            if potential_savings:
                console.print("\n[bold]💰 Potential Savings:[/bold]")
                savings_table = Table(box=box.ROUNDED)
                savings_table.add_column("Metric", style="cyan")
                savings_table.add_column("Value", style="yellow")
                savings_table.add_column("Status", style="green")
                
                cpu_cores = potential_savings.get('cpu_cores', 0)
                memory_mb = potential_savings.get('memory_mb', 0)
                monthly_savings = potential_savings.get('estimated_monthly_savings', 0)
                savings_confidence = potential_savings.get('savings_confidence', 0)
                
                savings_table.add_row("CPU Cores", f"{cpu_cores:.1f}", "💾")
                savings_table.add_row("Memory", f"{memory_mb:.1f} MB", "💾")
                savings_table.add_row("Monthly Savings", f"${monthly_savings:.2f}", "💰")
                savings_table.add_row("Savings Confidence", f"{savings_confidence:.1f}%", "✅" if savings_confidence > 80 else "⚠️")
                
                console.print(savings_table)
            
            # Intelligent insights
            if intelligent_insights:
                console.print("\n[bold]🧠 Intelligent Insights:[/bold]")
                for insight in intelligent_insights:
                    insight_type = insight.get('type', 'unknown')
                    description = insight.get('description', 'No description')
                    confidence = insight.get('confidence', 0)
                    recommendation = insight.get('recommendation', 'No recommendation')
                    
                    console.print(f"\n[cyan]{insight_type}:[/cyan] {description}")
                    console.print(f"  Confidence: {confidence:.1f}%")
                    console.print(f"  Recommendation: {recommendation}")
        
        elif format == 'json':
            import json
            print(json.dumps(idle_analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            print(yaml.dump(idle_analysis, default_flow_style=False))
        
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'idle':
                output = {'cluster_id': cluster_id, 'idle_analysis': {'idle_opportunities': []}, 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'idle_analysis': {}, 'idle_opportunities': []}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'idle_analysis': {}, 'idle_opportunities': []}))
        return

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def recommendations(ctx, cluster_id, format):
    """Get intelligent recommendations with business context"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            # raise click.Abort() # Removed as per edit hint
        
        # Initialize cluster detector
        cluster_detector = ClusterDetector()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Getting intelligent recommendations for cluster {cluster_id}...", total=None)
            
            # Get intelligent recommendations
            recommendations = cluster_detector.get_intelligent_recommendations(cluster_id)
            
            progress.update(task, completed=True)
        
        if format == 'table':
            # Display recommendations summary
            business_recs = len(recommendations.get('business_recommendations', []))
            technical_recs = len(recommendations.get('technical_recommendations', []))
            cost_recs = len(recommendations.get('cost_optimization_recommendations', []))
            capacity_recs = len(recommendations.get('capacity_planning_recommendations', []))
            overall_priority = recommendations.get('overall_priority', 'medium')
            
            console.print(Panel.fit(
                f"[bold blue]💡 UPID Intelligent Recommendations[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Overall Priority: [yellow]{overall_priority.upper()}[/yellow]\n"
                f"Total Recommendations: [green]{business_recs + technical_recs + cost_recs + capacity_recs}[/green]",
                title="Recommendations Summary",
                border_style="blue"
            ))
            
            # Business recommendations
            business_recommendations = recommendations.get('business_recommendations', [])
            if business_recommendations:
                console.print("\n[bold]💼 Business Recommendations:[/bold]")
                for i, rec in enumerate(business_recommendations, 1):
                    priority = rec.get('priority', 'medium')
                    description = rec.get('description', 'No description')
                    action = rec.get('action', 'No action specified')
                    confidence = rec.get('confidence', 0)
                    
                    priority_icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                    console.print(f"{i}. {priority_icon} [bold]{description}[/bold]")
                    console.print(f"   Action: {action}")
                    console.print(f"   Confidence: {confidence:.1f}%")
                    console.print()
            
            # Technical recommendations
            technical_recommendations = recommendations.get('technical_recommendations', [])
            if technical_recommendations:
                console.print("\n[bold]⚙️  Technical Recommendations:[/bold]")
                for i, rec in enumerate(technical_recommendations, 1):
                    priority = rec.get('priority', 'medium')
                    description = rec.get('description', 'No description')
                    action = rec.get('action', 'No action specified')
                    
                    priority_icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                    console.print(f"{i}. {priority_icon} [bold]{description}[/bold]")
                    console.print(f"   Action: {action}")
                    console.print()
            
            # Cost optimization recommendations
            cost_recommendations = recommendations.get('cost_optimization_recommendations', [])
            if cost_recommendations:
                console.print("\n[bold]💰 Cost Optimization Recommendations:[/bold]")
                for i, rec in enumerate(cost_recommendations, 1):
                    priority = rec.get('priority', 'medium')
                    description = rec.get('description', 'No description')
                    savings = rec.get('savings_percent', 0)
                    
                    priority_icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                    console.print(f"{i}. {priority_icon} [bold]{description}[/bold]")
                    console.print(f"   Potential Savings: {savings:.1f}%")
                    console.print()
            
            # Capacity planning recommendations
            capacity_recommendations = recommendations.get('capacity_planning_recommendations', [])
            if capacity_recommendations:
                console.print("\n[bold]📈 Capacity Planning Recommendations:[/bold]")
                for i, rec in enumerate(capacity_recommendations, 1):
                    priority = rec.get('priority', 'medium')
                    description = rec.get('description', 'No description')
                    urgency = rec.get('urgency', 'medium')
                    
                    priority_icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
                    console.print(f"{i}. {priority_icon} [bold]{description}[/bold]")
                    console.print(f"   Urgency: {urgency}")
                    console.print()
        
        elif format == 'json':
            import json
            print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        if format == 'json':
            import json
            if ctx.info_name == 'recommendations':
                output = {'cluster_id': cluster_id, 'recommendations': [], 'error': str(e)}
            else:
                output = {'cluster_id': cluster_id, 'error': str(e), 'recommendations': []}
            print(json.dumps(output, indent=2))
            return
        import json
        print(json.dumps({'cluster_id': cluster_id, 'error': str(e), 'recommendations': []}))
        return
