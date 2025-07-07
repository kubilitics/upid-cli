"""
Cluster management commands for UPID CLI
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
def cluster():
    """Cluster management commands"""
    pass

@cluster.command()
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def list(format, verbose):
    """List all clusters"""
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
            task = progress.add_task("Fetching clusters...", total=None)
            clusters = api_client.get_clusters()
            progress.update(task, completed=True)
        
        if not clusters:
            console.print("[yellow]No clusters found[/yellow]")
            return
        
        if format == 'table':
            # Create table
            table = Table(title="Clusters", box=box.ROUNDED)
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="white")
            table.add_column("Region", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Nodes", style="yellow")
            table.add_column("Pods", style="yellow")
            table.add_column("Created", style="dim")
            
            for cluster in clusters:
                status_color = "green" if cluster.get('status') == 'healthy' else "red"
                table.add_row(
                    cluster.get('cluster_id', 'N/A'),
                    cluster.get('name', 'N/A'),
                    cluster.get('region', 'N/A'),
                    f"[{status_color}]{cluster.get('status', 'N/A')}[/{status_color}]",
                    str(cluster.get('nodes_count', 0)),
                    str(cluster.get('pods_count', 0)),
                    cluster.get('created_at', 'N/A')
                )
            
            console.print(table)
            
        elif format == 'json':
            import json
            console.print(json.dumps(clusters, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(clusters, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to list clusters: {str(e)}[/red]")
        raise click.Abort()

@cluster.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
def get(cluster_id, format):
    """Get detailed information about a cluster"""
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
            task = progress.add_task(f"Fetching cluster {cluster_id}...", total=None)
            cluster = api_client.get_cluster(cluster_id)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create detailed table
            table = Table(title=f"Cluster: {cluster.get('name', cluster_id)}", box=box.ROUNDED)
            table.add_column("Property", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")
            
            table.add_row("ID", cluster.get('cluster_id', 'N/A'))
            table.add_row("Name", cluster.get('name', 'N/A'))
            table.add_row("Region", cluster.get('region', 'N/A'))
            table.add_row("Status", cluster.get('status', 'N/A'))
            table.add_row("Nodes Count", str(cluster.get('nodes_count', 0)))
            table.add_row("Pods Count", str(cluster.get('pods_count', 0)))
            table.add_row("Created", cluster.get('created_at', 'N/A'))
            table.add_row("Updated", cluster.get('updated_at', 'N/A'))
            
            # Add additional info if available
            if 'version' in cluster:
                table.add_row("Kubernetes Version", cluster['version'])
            if 'platform' in cluster:
                table.add_row("Platform", cluster['platform'])
            if 'cost' in cluster:
                table.add_row("Monthly Cost", f"${cluster['cost']:.2f}")
            
            console.print(table)
            
        elif format == 'json':
            import json
            console.print(json.dumps(cluster, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(cluster, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to get cluster {cluster_id}: {str(e)}[/red]")
        raise click.Abort()

@cluster.command()
@click.option('--name', '-n', required=True, help='Cluster name')
@click.option('--region', '-r', required=True, help='Cluster region')
@click.option('--platform', '-p', default='aws', type=click.Choice(['aws', 'gcp', 'azure']), help='Cloud platform')
@click.option('--nodes', default=3, help='Number of nodes')
@click.option('--node-type', default='t3.medium', help='Node instance type')
@click.option('--wait', '-w', is_flag=True, help='Wait for cluster creation to complete')
def create(name, region, platform, nodes, node_type, wait):
    """Create a new cluster"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        api_client = UPIDAPIClient(config, auth_manager)
        
        # Prepare cluster data
        cluster_data = {
            'name': name,
            'region': region,
            'platform': platform,
            'nodes_count': nodes,
            'node_type': node_type,
            'version': '1.24'  # Default Kubernetes version
        }
        
        console.print(f"[yellow]Creating cluster '{name}' in {region}...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating cluster...", total=None)
            cluster = api_client.create_cluster(cluster_data)
            progress.update(task, completed=True)
        
        console.print(Panel(
            f"[green]✓ Cluster created successfully![/green]\n\n"
            f"Cluster ID: [bold]{cluster.get('cluster_id', 'N/A')}[/bold]\n"
            f"Name: {cluster.get('name', name)}\n"
            f"Region: {cluster.get('region', region)}\n"
            f"Status: {cluster.get('status', 'creating')}",
            title="[bold green]Cluster Created[/bold green]",
            border_style="green"
        ))
        
        if wait:
            console.print("[yellow]Waiting for cluster to be ready...[/yellow]")
            # TODO: Implement wait logic with status polling
        
    except Exception as e:
        console.print(f"[red]✗ Failed to create cluster: {str(e)}[/red]")
        raise click.Abort()

@cluster.command()
@click.argument('cluster_id')
@click.option('--force', '-f', is_flag=True, help='Force deletion without confirmation')
def delete(cluster_id, force):
    """Delete a cluster"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        api_client = UPIDAPIClient(config, auth_manager)
        
        # Get cluster info for confirmation
        try:
            cluster = api_client.get_cluster(cluster_id)
            cluster_name = cluster.get('name', cluster_id)
        except:
            cluster_name = cluster_id
        
        # Confirm deletion
        if not force:
            if not click.confirm(f"Are you sure you want to delete cluster '{cluster_name}' ({cluster_id})?"):
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        console.print(f"[yellow]Deleting cluster '{cluster_name}'...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Deleting cluster...", total=None)
            api_client.delete_cluster(cluster_id)
            progress.update(task, completed=True)
        
        console.print(Panel(
            f"[green]✓ Cluster deleted successfully![/green]\n\n"
            f"Cluster ID: [bold]{cluster_id}[/bold]\n"
            f"Name: {cluster_name}",
            title="[bold green]Cluster Deleted[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to delete cluster {cluster_id}: {str(e)}[/red]")
        raise click.Abort()
