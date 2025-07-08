"""
Deployment commands for UPID CLI
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
def deploy():
    """Deployment commands"""
    pass

@deploy.command()
@click.argument('cluster_id')
@click.option('--name', '-n', required=True, help='Deployment name')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--image', '-i', required=True, help='Container image')
@click.option('--replicas', '-r', default=1, help='Number of replicas')
@click.option('--port', '-p', default=80, help='Container port')
@click.option('--env', '-e', multiple=True, help='Environment variables (key=value)')
@click.option('--wait', '-w', is_flag=True, help='Wait for deployment to be ready')
@click.pass_context
def create(ctx, cluster_id, name, namespace, image, replicas, port, env, wait):
    """Create a new deployment"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        # Prepare deployment data
        deployment_data = {
            'name': name,
            'namespace': namespace,
            'image': image,
            'replicas': replicas,
            'port': port,
            'environment': dict(e.split('=', 1) for e in env if '=' in e)
        }
        
        console.print(f"[yellow]Creating deployment '{name}' in namespace '{namespace}'...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating deployment...", total=None)
            deployment = api_client.create_deployment(cluster_id, deployment_data)
            progress.update(task, completed=True)
        
        console.print(Panel(
            f"[green]✓ Deployment created successfully![/green]\n\n"
            f"Name: [bold]{deployment.get('name', name)}[/bold]\n"
            f"Namespace: {deployment.get('namespace', namespace)}\n"
            f"Replicas: {deployment.get('replicas', replicas)}\n"
            f"Status: {deployment.get('status', 'creating')}",
            title="[bold green]Deployment Created[/bold green]",
            border_style="green"
        ))
        
        if wait:
            console.print("[yellow]Waiting for deployment to be ready...[/yellow]")
            # TODO: Implement wait logic with status polling
        
    except Exception as e:
        console.print(f"[red]✗ Failed to create deployment: {str(e)}[/red]")
        raise click.Abort()

@deploy.command()
@click.argument('cluster_id')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def list(ctx, cluster_id, namespace, format):
    """List deployments"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Fetching deployments from namespace '{namespace}'...", total=None)
            deployments = api_client.get_deployments(cluster_id, namespace)
            progress.update(task, completed=True)
        
        if not deployments:
            console.print(f"[yellow]No deployments found in namespace '{namespace}'[/yellow]")
            return
        
        if format == 'table':
            # Create deployments table
            table = Table(title=f"Deployments in {namespace}", box=box.ROUNDED)
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Replicas", style="yellow")
            table.add_column("Available", style="green")
            table.add_column("Status", style="white")
            table.add_column("Age", style="dim")
            
            for deployment in deployments:
                status_color = "green" if deployment.get('status') == 'ready' else "red"
                table.add_row(
                    deployment.get('name', 'N/A'),
                    str(deployment.get('replicas', 0)),
                    str(deployment.get('available', 0)),
                    f"[{status_color}]{deployment.get('status', 'N/A')}[/{status_color}]",
                    deployment.get('age', 'N/A')
                )
            
            console.print(table)
            
        elif format == 'json':
            import json
            console.print(json.dumps(deployments, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(deployments, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to list deployments: {str(e)}[/red]")
        raise click.Abort()

@deploy.command()
@click.argument('cluster_id')
@click.argument('deployment_name')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def get(ctx, cluster_id, deployment_name, namespace, format):
    """Get deployment details"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Fetching deployment '{deployment_name}'...", total=None)
            deployment = api_client.get_deployment(cluster_id, deployment_name, namespace)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create detailed table
            table = Table(title=f"Deployment: {deployment.get('name', deployment_name)}", box=box.ROUNDED)
            table.add_column("Property", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            table.add_row("Name", deployment.get('name', 'N/A'))
            table.add_row("Namespace", deployment.get('namespace', 'N/A'))
            table.add_row("Replicas", str(deployment.get('replicas', 0)))
            table.add_row("Available", str(deployment.get('available', 0)))
            table.add_row("Status", deployment.get('status', 'N/A'))
            table.add_row("Image", deployment.get('image', 'N/A'))
            table.add_row("Port", str(deployment.get('port', 0)))
            table.add_row("Age", deployment.get('age', 'N/A'))
            
            # Add environment variables if any
            env_vars = deployment.get('environment', {})
            if env_vars:
                table.add_row("Environment Variables", str(len(env_vars)))
                for key, value in env_vars.items():
                    table.add_row(f"  {key}", value)
            
            console.print(table)
            
        elif format == 'json':
            import json
            console.print(json.dumps(deployment, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(deployment, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to get deployment: {str(e)}[/red]")
        raise click.Abort()

@deploy.command()
@click.argument('cluster_id')
@click.argument('deployment_name')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--replicas', '-r', required=True, type=int, help='Number of replicas')
@click.pass_context
def scale(ctx, cluster_id, deployment_name, namespace, replicas):
    """Scale deployment"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        console.print(f"[yellow]Scaling deployment '{deployment_name}' to {replicas} replicas...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scaling deployment...", total=None)
            result = api_client.scale_deployment(cluster_id, deployment_name, namespace, replicas)
            progress.update(task, completed=True)
        
        console.print(Panel(
            f"[green]✓ Deployment scaled successfully![/green]\n\n"
            f"Name: [bold]{deployment_name}[/bold]\n"
            f"Namespace: {namespace}\n"
            f"New replicas: {replicas}\n"
            f"Status: {result.get('status', 'scaling')}",
            title="[bold green]Deployment Scaled[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to scale deployment: {str(e)}[/red]")
        raise click.Abort()

@deploy.command()
@click.argument('cluster_id')
@click.argument('deployment_name')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--revision', '-r', help='Revision to rollback to (default: previous)')
@click.option('--force', '-f', is_flag=True, help='Force rollback without confirmation')
@click.pass_context
def rollback(ctx, cluster_id, deployment_name, namespace, revision, force):
    """Rollback deployment to previous version"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        if not force:
            confirmed = click.confirm(f"Rollback deployment '{deployment_name}' to previous version?")
            if not confirmed:
                console.print("[yellow]Rollback cancelled[/yellow]")
                return
        
        console.print(f"[yellow]Rolling back deployment '{deployment_name}'...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Rolling back deployment...", total=None)
            result = api_client.rollback_deployment(cluster_id, deployment_name, namespace, revision)
            progress.update(task, completed=True)
        
        console.print(Panel(
            f"[green]✓ Deployment rolled back successfully![/green]\n\n"
            f"Name: [bold]{deployment_name}[/bold]\n"
            f"Namespace: {namespace}\n"
            f"Revision: {result.get('revision', 'previous')}\n"
            f"Status: {result.get('status', 'rolling back')}",
            title="[bold green]Deployment Rolled Back[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to rollback deployment: {str(e)}[/red]")
        raise click.Abort()

@deploy.command()
@click.argument('cluster_id')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def status(ctx, cluster_id, namespace, format):
    """Show deployment status"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Fetching deployment status from namespace '{namespace}'...", total=None)
            status_data = api_client.get_deployment_status(cluster_id, namespace)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create status table
            table = Table(title=f"Deployment Status in {namespace}", box=box.ROUNDED)
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Ready", style="green")
            table.add_column("Available", style="yellow")
            table.add_column("Replicas", style="dim")
            table.add_column("Updated", style="dim")
            
            for deployment in status_data.get('deployments', []):
                status_color = "green" if deployment.get('status') == 'ready' else "red"
                table.add_row(
                    deployment.get('name', 'N/A'),
                    f"[{status_color}]{deployment.get('status', 'N/A')}[/{status_color}]",
                    str(deployment.get('ready', 0)),
                    str(deployment.get('available', 0)),
                    str(deployment.get('replicas', 0)),
                    deployment.get('updated', 'N/A')
                )
            
            console.print(table)
            
        elif format == 'json':
            import json
            console.print(json.dumps(status_data, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(status_data, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to get deployment status: {str(e)}[/red]")
        raise click.Abort()

@deploy.command()
@click.argument('cluster_id')
@click.argument('deployment_name')
@click.option('--namespace', '-ns', default='default', help='Namespace')
@click.option('--force', '-f', is_flag=True, help='Force deletion without confirmation')
@click.pass_context
def delete(ctx, cluster_id, deployment_name, namespace, force):
    """Delete deployment"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        # Confirm deletion
        if not force:
            if not click.confirm(f"Are you sure you want to delete deployment '{deployment_name}' in namespace '{namespace}'?"):
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        console.print(f"[yellow]Deleting deployment '{deployment_name}'...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Deleting deployment...", total=None)
            api_client.delete_deployment(cluster_id, deployment_name, namespace)
            progress.update(task, completed=True)
        
        console.print(Panel(
            f"[green]✓ Deployment deleted successfully![/green]\n\n"
            f"Name: [bold]{deployment_name}[/bold]\n"
            f"Namespace: {namespace}",
            title="[bold green]Deployment Deleted[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to delete deployment: {str(e)}[/red]")
        raise click.Abort()
