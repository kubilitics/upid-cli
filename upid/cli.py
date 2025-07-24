#!/usr/bin/env python3
"""
UPID CLI - Main entry point
Kubernetes Resource Optimization Platform
"""

import click
import sys
import warnings
import os
from typing import Optional

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
    from .core.error_handler import error_handler, handle_error, validate_prerequisites
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
    from upid.core.error_handler import error_handler, handle_error, validate_prerequisites
    from upid.auth.universal_auth import UniversalAuthManager
    from upid.commands.cloud import cloud

console = Console()

class CustomGroup(click.Group):
    def main(self, *args, **kwargs):
        try:
            return super().main(*args, **kwargs)
        except click.exceptions.NoSuchOption as e:
            console.print(f"\n[red]❌ Unknown option: {e.option_name}[/red]")
            console.print("[yellow]💡 Use '--help' to see available options.[/yellow]")
            sys.exit(2)
        except click.exceptions.UsageError as e:
            if 'No such command' in str(e):
                cmd = str(e).split("No such command ")[-1].strip("' .")
                console.print(f"\n[red]❌ Unknown command: {cmd}[/red]")
                console.print("[yellow]💡 Use '--help' to see available commands.[/yellow]")
                console.print("[blue]ℹ️  Popular commands: upid analyze, upid optimize, upid auth status[/blue]")
                sys.exit(2)
            raise
        except Exception as e:
            handle_error(e, {"command": " ".join(sys.argv)})
            sys.exit(1)

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

@click.group(cls=CustomGroup)
@click.option('--version', is_flag=True, is_eager=True, expose_value=False, callback=print_version, help='Show the UPID CLI version and exit.')
@click.option('--verbose', is_flag=True, help='Enable verbose output and detailed error messages.')
@click.option('--check-prereqs', is_flag=True, help='Check system prerequisites before running commands.')
@click.pass_context
def cli(ctx, verbose, check_prereqs):
    """
    UPID CLI - Kubernetes Resource Optimization Platform
    
    🚀 Optimize your Kubernetes clusters for cost, performance, and efficiency.
    
    💡 Quick Start:
      upid analyze cluster        # Analyze your cluster
      upid optimize zero-pod      # Find cost savings
      upid auth status           # Check authentication
    
    🔗 If kubectl works, UPID works!
    """
    # Set debug mode
    if verbose:
        error_handler.debug_mode = True
        os.environ['UPID_VERBOSE'] = '1'
    
    # Check prerequisites if requested
    if check_prereqs:
        if not validate_prerequisites():
            sys.exit(1)
    
    # Ensure context exists
    ctx.ensure_object(dict)

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

def main():
    """Main entry point for UPID CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        handle_error(e, {"entry_point": "main"})
        sys.exit(1)

if __name__ == '__main__':
    main()
