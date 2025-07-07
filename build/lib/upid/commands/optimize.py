"""
Optimization commands for UPID CLI
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..core.config import Config
from ..core.api_client import UPIDAPIClient
from ..core.auth import AuthManager

console = Console()

@click.group()
def optimize():
    """Optimization commands"""
    pass

@optimize.command()
@click.argument('cluster_id')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def resources(cluster_id, dry_run, format):
    """Optimize cluster resources"""
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
            task = progress.add_task(f"Analyzing resource optimization for cluster {cluster_id}...", total=None)
            recommendations = api_client.get_resource_optimizations(cluster_id)
            progress.update(task, completed=True)
        
        if not recommendations:
            console.print("[yellow]No resource optimization recommendations found[/yellow]")
            return
        
        if format == 'table':
            # Create recommendations table
            rec_table = Table(title="Resource Optimization Recommendations", box=box.ROUNDED)
            rec_table.add_column("Type", style="cyan", no_wrap=True)
            rec_table.add_column("Resource", style="white")
            rec_table.add_column("Current", style="yellow")
            rec_table.add_column("Recommended", style="green")
            rec_table.add_column("Savings", style="blue")
            rec_table.add_column("Impact", style="red")
            
            total_savings = 0
            
            for rec in recommendations:
                savings = rec.get('savings', 0)
                total_savings += savings
                
                rec_table.add_row(
                    rec.get('type', 'N/A'),
                    rec.get('resource', 'N/A'),
                    rec.get('current_value', 'N/A'),
                    rec.get('recommended_value', 'N/A'),
                    f"${savings:.2f}",
                    rec.get('impact', 'N/A')
                )
            
            console.print(rec_table)
            
            # Show summary
            console.print(Panel(
                f"[bold]Total Potential Savings: ${total_savings:.2f}[/bold]\n"
                f"Recommendations: {len(recommendations)}",
                title="[bold green]Optimization Summary[/bold green]",
                border_style="green"
            ))
            
            # Apply optimizations if not dry run
            if not dry_run and recommendations:
                if click.confirm("Apply these optimizations?"):
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Applying optimizations...", total=None)
                        result = api_client.apply_resource_optimizations(cluster_id, recommendations)
                        progress.update(task, completed=True)
                    
                    console.print(Panel(
                        f"[green]✓ Optimizations applied successfully![/green]\n\n"
                        f"Applied: {result.get('applied_count', 0)} recommendations\n"
                        f"Actual savings: ${result.get('actual_savings', 0):.2f}",
                        title="[bold green]Optimization Applied[/bold green]",
                        border_style="green"
                    ))
            
        elif format == 'json':
            import json
            console.print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to optimize resources: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def costs(cluster_id, dry_run, format):
    """Optimize cluster costs"""
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
            task = progress.add_task(f"Analyzing cost optimization for cluster {cluster_id}...", total=None)
            recommendations = api_client.get_cost_optimizations(cluster_id)
            progress.update(task, completed=True)
        
        if not recommendations:
            console.print("[yellow]No cost optimization recommendations found[/yellow]")
            return
        
        if format == 'table':
            # Create recommendations table
            rec_table = Table(title="Cost Optimization Recommendations", box=box.ROUNDED)
            rec_table.add_column("Category", style="cyan", no_wrap=True)
            rec_table.add_column("Action", style="white")
            rec_table.add_column("Current Cost", style="yellow")
            rec_table.add_column("Optimized Cost", style="green")
            rec_table.add_column("Savings", style="blue")
            rec_table.add_column("Priority", style="red")
            
            total_savings = 0
            
            for rec in recommendations:
                savings = rec.get('savings', 0)
                total_savings += savings
                
                rec_table.add_row(
                    rec.get('category', 'N/A'),
                    rec.get('action', 'N/A'),
                    f"${rec.get('current_cost', 0):.2f}",
                    f"${rec.get('optimized_cost', 0):.2f}",
                    f"${savings:.2f}",
                    rec.get('priority', 'N/A')
                )
            
            console.print(rec_table)
            
            # Show summary
            console.print(Panel(
                f"[bold]Total Potential Savings: ${total_savings:.2f}[/bold]\n"
                f"Recommendations: {len(recommendations)}",
                title="[bold green]Cost Optimization Summary[/bold green]",
                border_style="green"
            ))
            
            # Apply optimizations if not dry run
            if not dry_run and recommendations:
                if click.confirm("Apply these cost optimizations?"):
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Applying cost optimizations...", total=None)
                        result = api_client.apply_cost_optimizations(cluster_id, recommendations)
                        progress.update(task, completed=True)
                    
                    console.print(Panel(
                        f"[green]✓ Cost optimizations applied successfully![/green]\n\n"
                        f"Applied: {result.get('applied_count', 0)} recommendations\n"
                        f"Actual savings: ${result.get('actual_savings', 0):.2f}",
                        title="[bold green]Cost Optimization Applied[/bold green]",
                        border_style="green"
                    ))
            
        elif format == 'json':
            import json
            console.print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to optimize costs: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--namespace', '-n', help='Target namespace (default: all)')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def zero_pod(cluster_id, namespace, dry_run, format):
    """Optimize using zero-pod scaling"""
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
            task = progress.add_task(f"Analyzing zero-pod scaling for cluster {cluster_id}...", total=None)
            recommendations = api_client.get_zero_pod_recommendations(cluster_id, namespace)
            progress.update(task, completed=True)
        
        if not recommendations:
            console.print("[yellow]No zero-pod scaling recommendations found[/yellow]")
            return
        
        if format == 'table':
            # Create recommendations table
            rec_table = Table(title="Zero-Pod Scaling Recommendations", box=box.ROUNDED)
            rec_table.add_column("Namespace", style="cyan", no_wrap=True)
            rec_table.add_column("Deployment", style="white")
            rec_table.add_column("Current Replicas", style="yellow")
            rec_table.add_column("Idle Time", style="blue")
            rec_table.add_column("Savings", style="green")
            rec_table.add_column("Risk", style="red")
            
            total_savings = 0
            
            for rec in recommendations:
                savings = rec.get('savings', 0)
                total_savings += savings
                
                rec_table.add_row(
                    rec.get('namespace', 'N/A'),
                    rec.get('deployment', 'N/A'),
                    str(rec.get('current_replicas', 0)),
                    rec.get('idle_time', 'N/A'),
                    f"${savings:.2f}",
                    rec.get('risk_level', 'N/A')
                )
            
            console.print(rec_table)
            
            # Show summary
            console.print(Panel(
                f"[bold]Total Potential Savings: ${total_savings:.2f}[/bold]\n"
                f"Recommendations: {len(recommendations)}",
                title="[bold green]Zero-Pod Scaling Summary[/bold green]",
                border_style="green"
            ))
            
            # Apply optimizations if not dry run
            if not dry_run and recommendations:
                if click.confirm("Apply zero-pod scaling optimizations?"):
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Applying zero-pod scaling...", total=None)
                        result = api_client.apply_zero_pod_optimizations(cluster_id, recommendations)
                        progress.update(task, completed=True)
                    
                    console.print(Panel(
                        f"[green]✓ Zero-pod scaling applied successfully![/green]\n\n"
                        f"Applied: {result.get('applied_count', 0)} recommendations\n"
                        f"Actual savings: ${result.get('actual_savings', 0):.2f}",
                        title="[bold green]Zero-Pod Scaling Applied[/bold green]",
                        border_style="green"
                    ))
            
        elif format == 'json':
            import json
            console.print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to optimize zero-pod scaling: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--auto', '-a', is_flag=True, help='Enable automatic optimization')
@click.option('--schedule', '-s', help='Optimization schedule (cron format)')
def auto(cluster_id, auto, schedule):
    """Configure automatic optimization"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        api_client = UPIDAPIClient(config, auth_manager)
        
        if auto:
            # Enable auto optimization
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Enabling automatic optimization...", total=None)
                result = api_client.enable_auto_optimization(cluster_id, schedule)
                progress.update(task, completed=True)
            
            console.print(Panel(
                f"[green]✓ Automatic optimization enabled![/green]\n\n"
                f"Schedule: {result.get('schedule', schedule or 'default')}\n"
                f"Next run: {result.get('next_run', 'N/A')}",
                title="[bold green]Auto Optimization Enabled[/bold green]",
                border_style="green"
            ))
        else:
            # Disable auto optimization
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Disabling automatic optimization...", total=None)
                result = api_client.disable_auto_optimization(cluster_id)
                progress.update(task, completed=True)
            
            console.print(Panel(
                f"[green]✓ Automatic optimization disabled![/green]",
                title="[bold green]Auto Optimization Disabled[/bold green]",
                border_style="green"
            ))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to configure auto optimization: {str(e)}[/red]")
        raise click.Abort()
