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
    from .commands import cluster, analyze, optimize, deploy, report, universal, intelligence, storage, cloud
    from .commands.auth_universal import auth
    from .commands.configurable_auth import configurable_auth
    from .commands.onboarding import onboarding
    from .commands.billing import billing
    from .core.config import Config
    from .core.auth import AuthManager
    from .core.api_client import UPIDAPIClient
    from upid.auth.universal_auth import UniversalAuthManager
    from upid.commands.cloud import cloud
except ImportError:
    # Fallback for PyInstaller
    from upid.commands import cluster, analyze, optimize, deploy, report, universal, intelligence, storage, cloud
    from upid.commands.auth_universal import auth
    from upid.commands.configurable_auth import configurable_auth
    from upid.commands.onboarding import onboarding
    from upid.commands.billing import billing
    from upid.core.config import Config
    from upid.core.auth import AuthManager
    from upid.core.api_client import UPIDAPIClient
    from upid.auth.universal_auth import UniversalAuthManager
    from upid.commands.cloud import cloud

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

import click
from upid.commands.auth_universal import auth
from upid.commands.configurable_auth import configurable_auth
from upid.commands.onboarding import onboarding
from upid.commands.cluster import cluster
from upid.commands.analyze import analyze
from upid.commands.optimize import optimize
from upid.commands.deploy import deploy
from upid.commands.report import report
from upid.commands.universal import universal
from upid.commands.billing import billing
from upid.commands.intelligence import intelligence
from upid.commands.storage import storage
from upid.commands.cloud import cloud

def print_version(ctx, param, value):
    if value:
        click.echo('UPID CLI v1.0.0')
        ctx.exit()

@click.group()
@click.option('--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version, help='Show the UPID CLI version and exit.')
def cli():
    """
    UPID CLI - Kubernetes Resource Optimization Platform
    Optimize your Kubernetes clusters for cost, performance, and efficiency.
    """
    pass

cli.add_command(auth)
cli.add_command(configurable_auth)
cli.add_command(onboarding)
cli.add_command(cluster)
cli.add_command(analyze)
cli.add_command(optimize)
cli.add_command(deploy)
cli.add_command(report)
cli.add_command(universal)
cli.add_command(billing)
cli.add_command(intelligence)
cli.add_command(storage)
cli.add_command(cloud, name='cloud')

# Add status command
@cli.command()
def status():
    """Show UPID CLI status"""
    click.echo('UPID CLI Status: OK')

# Add config command
@cli.command()
def config():
    """Show UPID CLI configuration"""
    click.echo('UPID CLI Configuration: (config details here)')

# Add demo command
@cli.command()
def demo():
    """Run UPID CLI demo"""
    click.echo('UPID CLI Demo: (demo output here)')

if __name__ == '__main__':
    cli()
