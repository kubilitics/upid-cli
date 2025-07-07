import sys
"""
Authentication commands for UPID CLI
"""

import click
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from ..core.auth import AuthManager
from ..core.config import Config

console = Console()

@click.group()
def auth():
    """Authentication commands"""
    pass

@auth.command()
@click.option('--email', '-e', help='Email address')
@click.option('--password', '-p', help='Password (will prompt if not provided)')
@click.option('--server', '-s', help='API server URL')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def login(email, password, server, verbose):
    """Login to UPID platform"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        # Get email if not provided
        if not email:
            email = click.prompt('Email')
        
        # Get password if not provided
        if not password:
            password = getpass.getpass('Password: ')
        
        # Show login attempt
        if verbose:
            console.print(f"[yellow]Attempting login to {server or config.get('api_url')}...[/yellow]")
        
        # Perform login
        token = auth_manager.login(email, password, server)
        
        # Get user info
        user = auth_manager.get_current_user()
        
        # Display success
        console.print(Panel(
            f"[green]✓ Login successful![/green]\n\n"
            f"Welcome, [bold]{user.get('name', 'User')}[/bold]!\n"
            f"Email: {user.get('email', email)}\n"
            f"Organization: {user.get('organization', 'N/A')}",
            title="[bold green]Authentication Successful[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Login failed: {str(e)}[/red]")
        raise click.Abort()

@auth.command()
def logout():
    """Logout from UPID platform"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[yellow]Not currently logged in[/yellow]")
            return
        
        # Get user info before logout
        user = auth_manager.get_current_user()
        user_name = user.get('name', 'User') if user else 'User'
        
        # Perform logout
        auth_manager.logout()
        
        console.print(Panel(
            f"[green]✓ Logout successful![/green]\n\n"
            f"Goodbye, [bold]{user_name}[/bold]!",
            title="[bold green]Logout Successful[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Logout failed: {str(e)}[/red]")
        raise click.Abort()

@auth.command()
def status():
    """Show authentication status"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        # Create status table
        table = Table(title="Authentication Status", box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        # Check authentication
        is_auth = auth_manager.is_authenticated()
        table.add_row("Authenticated", "✓ Yes" if is_auth else "✗ No")
        
        if is_auth:
            # Get user info
            user = auth_manager.get_current_user()
            if user:
                table.add_row("Name", user.get('name', 'N/A'))
                table.add_row("Email", user.get('email', 'N/A'))
                table.add_row("Organization", user.get('organization', 'N/A'))
                table.add_row("Roles", ", ".join(user.get('roles', [])))
                table.add_row("Permissions", ", ".join(user.get('permissions', [])))
            
            # Get token info
            token = auth_manager.get_token()
            if token:
                table.add_row("Token", f"{token[:10]}..." if len(token) > 10 else token)
        
        # API info
        table.add_row("API URL", config.get('api_url'))
        table.add_row("API Version", config.get('api_version'))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ Status check failed: {str(e)}[/red]")
        raise click.Abort()

@auth.command()
def refresh():
    """Refresh authentication token"""
    try:
        config = Config()
        auth_manager = AuthManager(config)
        
        if not auth_manager.is_authenticated():
            console.print("[yellow]Not currently logged in[/yellow]")
            return
        
        console.print("[yellow]Refreshing token...[/yellow]")
        
        # Refresh token
        new_token = auth_manager.refresh_token()
        
        console.print(Panel(
            f"[green]✓ Token refreshed successfully![/green]\n\n"
            f"New token: [bold]{new_token[:10]}...[/bold]",
            title="[bold green]Token Refresh[/bold green]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Token refresh failed: {str(e)}[/red]")
        raise click.Abort()

@auth.command()
@click.option('--name', required=True, help='Cluster name')
@click.option('--kubeconfig', default='~/.kube/config', help='Kubeconfig file path')
def configure_cluster(name, kubeconfig):
    """Configure cluster access"""
    config = Config()
    config.set('cluster_name', name)
    config.set('kubeconfig_path', kubeconfig)
    
    console.print(f"[green]✅ Cluster '{name}' configured successfully![/green]")

@auth.command()
def list_clusters():
    """List configured clusters"""
    config = Config()
    cluster_name = config.get('cluster_name', 'default')
    
    table = Table(title="Configured Clusters")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row(cluster_name, "✅ Active")
    
    console.print(table)
