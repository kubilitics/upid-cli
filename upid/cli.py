#!/usr/bin/env python3
"""
UPID CLI - Main entry point
Kubernetes Resource Optimization Platform
"""

import click
import sys
import warnings

# Suppress urllib3 warnings for cleaner output
warnings.filterwarnings("ignore", category=Warning)

from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from pathlib import Path
try:
    from .commands import auth, cluster, analyze, optimize, deploy, report, universal
    from .core.config import Config
    from .core.auth import AuthManager
    from .core.api_client import UPIDAPIClient
except ImportError:
    # Fallback for PyInstaller
    from upid.commands import auth, cluster, analyze, optimize, deploy, report, universal
    from upid.core.config import Config
    from upid.core.auth import AuthManager
    from upid.core.api_client import UPIDAPIClient

console = Console()

class CustomGroup(click.Group):
    def main(self, *args, **kwargs):
        try:
            return super().main(*args, **kwargs)
        except click.exceptions.NoSuchOption as e:
            console.print(f"\n[red]❌ Unknown option: {e.option_name}[/red]")
            console.print("[yellow]Use '--help' to see available options.[/yellow]")
            sys.exit(2)
        except click.exceptions.UsageError as e:
            if 'No such command' in str(e):
                cmd = str(e).split("No such command ")[-1].strip("' .")
                console.print(f"\n[red]❌ Unknown command: {cmd}[/red]")
                console.print("[yellow]Use '--help' to see available commands.[/yellow]")
                sys.exit(2)
            raise

@click.group(cls=CustomGroup)
@click.option('--config', '-c', help='Configuration file path')
@click.option('--local', is_flag=True, help='Enable local mode for testing without authentication')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.version_option('1.0.0', '--version', '-V', message='UPID CLI v%(version)s\nKubernetes Resource Optimization Platform\n© 2024 Kubilitics - hello@kubilitics.com')
@click.pass_context
def cli(ctx, config, local, verbose):
    """
    UPID CLI - Kubernetes Resource Optimization Platform
    
    Optimize your Kubernetes clusters for cost, performance, and efficiency.
    """
    # Initialize configuration
    ctx.obj = {}
    ctx.obj['config'] = Config(config)
    
    # Enable local mode if requested
    if local:
        ctx.obj['config'].enable_local_mode()
        console.print("[yellow]🔧 Local mode enabled - running without authentication[/yellow]")
    
    # Set verbose logging
    if verbose:
        ctx.obj['config'].set('log_level', 'DEBUG')
    
    # Initialize auth manager and API client
    ctx.obj['auth_manager'] = AuthManager(ctx.obj['config'])
    ctx.obj['api_client'] = UPIDAPIClient(ctx.obj['config'], ctx.obj['auth_manager'])

# Add command groups
cli.add_command(auth.auth)
cli.add_command(cluster.cluster)
cli.add_command(analyze.analyze)
cli.add_command(optimize.optimize)
cli.add_command(deploy.deploy)
cli.add_command(report.report)
cli.add_command(universal.universal)

@cli.command()
@click.pass_context
def status(ctx):
    """Show current CLI status and configuration"""
    config = ctx.obj['config']
    auth_manager = ctx.obj['auth_manager']
    
    console.print("\n[bold blue]🔍 UPID CLI Status[/bold blue]\n")
    
    # Configuration status
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("API URL", config.get('api_url', 'Not set'))
    table.add_row("API Version", config.get('api_version', 'v1'))
    table.add_row("Local Mode", "✅ Enabled" if config.is_local_mode() else "❌ Disabled")
    table.add_row("Timeout", str(config.get('timeout', 30)) + "s")
    table.add_row("Log Level", config.get('log_level', 'INFO'))
    
    console.print(table)
    
    # Authentication status
    if config.is_local_mode():
        console.print("\n[green]✅ Local mode active - no authentication required[/green]")
    else:
        is_authenticated = auth_manager.is_authenticated()
        if is_authenticated:
            user = auth_manager.get_current_user()
            console.print(f"\n[green]✅ Authenticated as: {user.get('name', 'Unknown')}[/green]")
        else:
            console.print("\n[yellow]⚠️  Not authenticated - run 'upid auth login'[/yellow]")
    
    # Cluster status
    try:
        clusters = ctx.obj['api_client'].get_clusters()
        if clusters:
            console.print(f"\n[green]📊 Connected to {len(clusters)} cluster(s)[/green]")
        else:
            console.print("\n[yellow]📊 No clusters found[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error connecting to clusters: {e}[/red]")

@cli.command()
@click.pass_context
def config(ctx):
    """Manage UPID CLI configuration"""
    config_obj = ctx.obj['config']
    
    console.print("\n[bold blue]⚙️  UPID CLI Configuration[/bold blue]\n")
    
    # Show current configuration
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("API URL", config_obj.get('api_url', 'Not set'))
    table.add_row("API Version", config_obj.get('api_version', 'v1'))
    table.add_row("Local Mode", "✅ Enabled" if config_obj.is_local_mode() else "❌ Disabled")
    table.add_row("Timeout", str(config_obj.get('timeout', 30)) + "s")
    table.add_row("Log Level", config_obj.get('log_level', 'INFO'))
    
    console.print(table)
    
    console.print("\n[yellow]Use 'upid init' to modify configuration[/yellow]")

@cli.command()
@click.pass_context
def init(ctx):
    """Initialize UPID CLI configuration"""
    config = ctx.obj['config']
    
    console.print("\n[bold blue]🚀 UPID CLI Initialization[/bold blue]\n")
    
    # Ask for configuration
    api_url = Prompt.ask(
        "Enter API URL", 
        default=config.get('api_url', 'https://api.upid.io')
    )
    
    local_mode = Confirm.ask(
        "Enable local mode for testing without authentication?",
        default=False
    )
    
    # Update configuration
    config.set('api_url', api_url)
    if local_mode:
        config.enable_local_mode()
        console.print("[green]✅ Local mode enabled[/green]")
    else:
        config.disable_local_mode()
        console.print("[green]✅ Production mode enabled[/green]")
    
    console.print(f"\n[green]✅ Configuration saved to {config.config_file}[/green]")
    
    if not local_mode:
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Run 'upid auth login' to authenticate")
        console.print("2. Run 'upid cluster list' to see your clusters")
        console.print("3. Run 'upid analyze <cluster>' to analyze resources")

@cli.command()
@click.pass_context
def demo(ctx):
    """Run a demo of UPID CLI features"""
    console.print("\n[bold blue]🎬 UPID CLI Demo[/bold blue]\n")
    
    # Check if local mode is enabled
    if not ctx.obj['config'].is_local_mode():
        console.print("[yellow]⚠️  Demo works best in local mode. Run with --local flag.[/yellow]\n")
    
    # Demo steps
    steps = [
        "1. Show CLI status",
        "2. List clusters",
        "3. Analyze cluster resources",
        "4. Get optimization recommendations",
        "5. Generate cost report"
    ]
    
    for step in steps:
        console.print(f"[cyan]{step}[/cyan]")
    
    console.print("\n[green]✅ Demo completed![/green]")

def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(0)
    except click.Abort:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        sys.exit(1)
    except click.UsageError as e:
        # Suppress urllib3 warnings for cleaner error output
        import warnings
        warnings.filterwarnings("ignore", category=Warning)
        console.print(f"\n[red]❌ Usage error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        # Suppress urllib3 warnings for cleaner error output
        import warnings
        warnings.filterwarnings("ignore", category=Warning)
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        console.print("[yellow]💡 Try running with --verbose for more details[/yellow]")
        sys.exit(1)

if __name__ == '__main__':
    main()
