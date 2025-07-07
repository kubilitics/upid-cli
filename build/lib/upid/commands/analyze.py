"""
Analysis commands for UPID CLI
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

console = Console()

@click.group()
def analyze():
    """Analysis commands"""
    pass

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
def resources(cluster_id, format, detailed):
    """Analyze cluster resource usage"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        api_client = UPIDAPIClient(config, auth_manager)
        
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
            console.print(json.dumps(analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(analysis, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to analyze resources: {str(e)}[/red]")
        raise click.Abort()

@analyze.command()
@click.argument('cluster_id')
@click.option('--period', '-p', default='30d', type=click.Choice(['7d', '30d', '90d']), help='Analysis period')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def cost(cluster_id, period, format):
    """Analyze cluster costs"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        api_client = UPIDAPIClient(config, auth_manager)
        
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
            console.print(json.dumps(analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(analysis, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to analyze costs: {str(e)}[/red]")
        raise click.Abort()

@analyze.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def performance(cluster_id, format):
    """Analyze cluster performance"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        api_client = UPIDAPIClient(config, auth_manager)
        
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
            console.print(json.dumps(analysis, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(analysis, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to analyze performance: {str(e)}[/red]")
        raise click.Abort()
