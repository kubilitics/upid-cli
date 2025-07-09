"""
Universal Authentication Commands for UPID CLI
Integrates with the universal authentication system
"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..auth import UniversalAuthenticator
from ..auth.universal_auth import EnvironmentInfo, AuthResult

console = Console()

@click.group()
@click.pass_context
def auth(ctx):
    """Universal authentication for UPID CLI"""
    pass

@auth.command()
@click.option('--namespace', '-n', default='default', help='Namespace to check permissions')
@click.pass_context
async def status(ctx, namespace):
    """Show authentication status and permissions"""
    try:
        authenticator = UniversalAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking authentication status...", total=None)
            
            # Detect environment
            env_info = await authenticator.detect_environment()
            
            # Check authentication
            auth_result = await authenticator.authenticate_user(ctx.obj)
            
            progress.update(task, description="Checking RBAC permissions...")
            
            # Check RBAC permissions
            rbac_info = await authenticator.rbac_enforcer.check_user_permissions(namespace)
            
            progress.update(task, description="Complete!")
        
        # Display results
        console.print("\n[bold blue]🔐 Authentication Status[/bold blue]\n")
        
        # Environment info
        env_table = Table(title="Environment Detection")
        env_table.add_column("Property", style="cyan")
        env_table.add_column("Value", style="green")
        
        env_table.add_row("Cluster Type", env_info.cluster_type)
        env_table.add_row("Is Local", "✅ Yes" if env_info.is_local_cluster else "❌ No")
        env_table.add_row("Cloud Provider", env_info.cloud_provider or "N/A")
        env_table.add_row("Cluster Name", env_info.cluster_name or "N/A")
        env_table.add_row("Context", env_info.context_name or "N/A")
        env_table.add_row("Region", env_info.region or "N/A")
        
        console.print(env_table)
        
        # Authentication status
        auth_table = Table(title="Authentication Status")
        auth_table.add_column("Property", style="cyan")
        auth_table.add_column("Value", style="green")
        
        auth_table.add_row("Status", "✅ Authenticated" if auth_result.success else "❌ Not Authenticated")
        auth_table.add_row("Method", auth_result.auth_method)
        auth_table.add_row("Requires Action", "⚠️ Yes" if auth_result.requires_action else "✅ No")
        
        if auth_result.error_message:
            auth_table.add_row("Error", f"❌ {auth_result.error_message}")
        
        console.print(auth_table)
        
        # RBAC permissions
        rbac_table = Table(title=f"RBAC Permissions (Namespace: {namespace})")
        rbac_table.add_column("Capability", style="cyan")
        rbac_table.add_column("Status", style="green")
        
        rbac_table.add_row("Read", "✅ Allowed" if rbac_info.can_read else "❌ Denied")
        rbac_table.add_row("Write", "✅ Allowed" if rbac_info.can_write else "❌ Denied")
        rbac_table.add_row("Delete", "✅ Allowed" if rbac_info.can_delete else "❌ Denied")
        rbac_table.add_row("Exec", "✅ Allowed" if rbac_info.can_exec else "❌ Denied")
        
        console.print(rbac_table)
        
        # User info
        if rbac_info.user != "unknown":
            user_table = Table(title="User Information")
            user_table.add_column("Property", style="cyan")
            user_table.add_column("Value", style="green")
            
            user_table.add_row("User", rbac_info.user)
            user_table.add_row("Roles", ", ".join(rbac_info.roles) if rbac_info.roles else "None")
            user_table.add_row("Permissions", str(len(rbac_info.permissions)))
            
            console.print(user_table)
        
    except Exception as e:
        console.print(f"\n[red]❌ Error checking authentication status: {e}[/red]")

@auth.command()
@click.option('--cluster-type', '-t', help='Specify cluster type (local, eks, gke, aks, etc.)')
@click.option('--context', '-c', help='Specify kubectl context')
@click.option('--namespace', '-n', default='default', help='Namespace to authenticate')
@click.pass_context
async def login(ctx, cluster_type, context, namespace):
    """Authenticate with Kubernetes cluster"""
    try:
        authenticator = UniversalAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Detecting environment...", total=None)
            
            # Detect environment
            env_info = await authenticator.detect_environment()
            
            progress.update(task, description="Authenticating...")
            
            # Authenticate
            auth_result = await authenticator.authenticate_user(ctx.obj)
            
            progress.update(task, description="Checking permissions...")
            
            # Check permissions
            rbac_info = await authenticator.rbac_enforcer.check_user_permissions(namespace)
            
            progress.update(task, description="Complete!")
        
        if auth_result.success:
            console.print(f"\n[green]✅ Successfully authenticated![/green]")
            console.print(f"[green]Cluster: {env_info.cluster_name or 'Unknown'}[/green]")
            console.print(f"[green]User: {rbac_info.user}[/green]")
            console.print(f"[green]Namespace: {namespace}[/green]")
            
            if rbac_info.can_read:
                console.print("\n[yellow]Next steps:[/yellow]")
                console.print("• Run 'upid cluster list' to see your clusters")
                console.print("• Run 'upid analyze <cluster>' to analyze resources")
                console.print("• Run 'upid optimize <cluster>' to optimize resources")
        else:
            console.print(f"\n[red]❌ Authentication failed: {auth_result.error_message}[/red]")
            
            if auth_result.requires_action:
                console.print("\n[yellow]Troubleshooting:[/yellow]")
                console.print("• Ensure kubectl is installed and configured")
                console.print("• Check your kubeconfig file")
                console.print("• Verify cluster connectivity")
                console.print("• Check RBAC permissions")
        
    except Exception as e:
        console.print(f"\n[red]❌ Authentication error: {e}[/red]")

@auth.command()
@click.option('--namespace', '-n', default='default', help='Namespace to check')
@click.pass_context
async def permissions(ctx, namespace):
    """Check detailed permissions for current user"""
    try:
        authenticator = UniversalAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking permissions...", total=None)
            
            # Get detailed permissions
            permissions = await authenticator.rbac_enforcer.get_namespace_permissions(namespace)
            
            progress.update(task, description="Complete!")
        
        console.print(f"\n[bold blue]🔐 RBAC Permissions - Namespace: {namespace}[/bold blue]\n")
        
        # User info
        user_table = Table(title="User Information")
        user_table.add_column("Property", style="cyan")
        user_table.add_column("Value", style="green")
        
        user_table.add_row("User", permissions['user'])
        user_table.add_row("Namespace", permissions['namespace'])
        user_table.add_row("Roles", ", ".join(permissions['roles']) if permissions['roles'] else "None")
        user_table.add_row("Total Permissions", str(len(permissions['permissions'])))
        
        console.print(user_table)
        
        # Capabilities
        caps_table = Table(title="Capabilities")
        caps_table.add_column("Capability", style="cyan")
        caps_table.add_column("Status", style="green")
        
        for cap, allowed in permissions['capabilities'].items():
            status = "✅ Allowed" if allowed else "❌ Denied"
            caps_table.add_row(cap.title(), status)
        
        console.print(caps_table)
        
        # Detailed permissions
        if permissions['permissions']:
            perm_table = Table(title="Detailed Permissions")
            perm_table.add_column("Permission", style="cyan")
            
            for perm in sorted(permissions['permissions']):
                perm_table.add_row(perm)
            
            console.print(perm_table)
        
    except Exception as e:
        console.print(f"\n[red]❌ Error checking permissions: {e}[/red]")

@auth.command()
@click.argument('resource')
@click.argument('action')
@click.option('--namespace', '-n', default='default', help='Namespace to check')
@click.pass_context
async def can_i(ctx, resource, action, namespace):
    """Check if user can perform action on resource"""
    try:
        authenticator = UniversalAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking permission...", total=None)
            
            # Check specific permission
            permission_check = await authenticator.rbac_enforcer.check_resource_permission(
                resource, action, namespace
            )
            
            progress.update(task, description="Complete!")
        
        console.print(f"\n[bold blue]🔐 Permission Check[/bold blue]\n")
        
        # Permission result
        result_table = Table(title="Permission Result")
        result_table.add_column("Property", style="cyan")
        result_table.add_column("Value", style="green")
        
        result_table.add_row("Action", action)
        result_table.add_row("Resource", resource)
        result_table.add_row("Namespace", namespace)
        result_table.add_row("Allowed", "✅ Yes" if permission_check.allowed else "❌ No")
        result_table.add_row("Reason", permission_check.reason)
        
        console.print(result_table)
        
        # Required permissions
        if permission_check.required_permissions:
            req_table = Table(title="Required Permissions")
            req_table.add_column("Permission", style="cyan")
            
            for perm in permission_check.required_permissions:
                req_table.add_row(perm)
            
            console.print(req_table)
        
        # User permissions
        if permission_check.user_permissions:
            user_table = Table(title="User Permissions")
            user_table.add_column("Permission", style="cyan")
            
            for perm in permission_check.user_permissions:
                user_table.add_row(perm)
            
            console.print(user_table)
        
    except Exception as e:
        console.print(f"\n[red]❌ Error checking permission: {e}[/red]")

@auth.command()
@click.pass_context
async def logout(ctx):
    """Logout from current authentication"""
    try:
        console.print("\n[bold blue]🔐 Logout[/bold blue]\n")
        
        # Clear any stored tokens
        if 'auth_manager' in ctx.obj:
            ctx.obj['auth_manager'].clear_token()
        
        console.print("[green]✅ Successfully logged out[/green]")
        console.print("[yellow]Authentication tokens cleared[/yellow]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error during logout: {e}[/red]")

@auth.command()
@click.pass_context
async def setup(ctx):
    """Setup authentication for different environments"""
    try:
        console.print("\n[bold blue]🔧 Authentication Setup[/bold blue]\n")
        
        # Ask for environment type
        env_type = Prompt.ask(
            "Select environment type",
            choices=["local", "aws", "gcp", "azure", "digitalocean", "linode", "other"],
            default="local"
        )
        
        console.print(f"\n[yellow]Setting up authentication for {env_type}...[/yellow]")
        
        if env_type == "local":
            console.print("\n[green]Local Environment Setup:[/green]")
            console.print("1. Ensure kubectl is installed")
            console.print("2. Configure your kubeconfig")
            console.print("3. Run 'upid auth login' to authenticate")
            
        elif env_type == "aws":
            console.print("\n[green]AWS EKS Setup:[/green]")
            console.print("1. Install AWS CLI")
            console.print("2. Configure AWS credentials")
            console.print("3. Install kubectl")
            console.print("4. Run 'aws eks update-kubeconfig --name <cluster-name>'")
            console.print("5. Run 'upid auth login' to authenticate")
            
        elif env_type == "gcp":
            console.print("\n[green]GCP GKE Setup:[/green]")
            console.print("1. Install gcloud CLI")
            console.print("2. Authenticate with 'gcloud auth login'")
            console.print("3. Set project with 'gcloud config set project <project-id>'")
            console.print("4. Install kubectl")
            console.print("5. Run 'gcloud container clusters get-credentials <cluster-name>'")
            console.print("6. Run 'upid auth login' to authenticate")
            
        elif env_type == "azure":
            console.print("\n[green]Azure AKS Setup:[/green]")
            console.print("1. Install Azure CLI")
            console.print("2. Authenticate with 'az login'")
            console.print("3. Set subscription with 'az account set --subscription <subscription-id>'")
            console.print("4. Install kubectl")
            console.print("5. Run 'az aks get-credentials --resource-group <rg> --name <cluster-name>'")
            console.print("6. Run 'upid auth login' to authenticate")
            
        else:
            console.print(f"\n[yellow]Setup for {env_type} not yet implemented[/yellow]")
            console.print("Please refer to your cloud provider's documentation")
        
        console.print(f"\n[green]✅ Setup instructions provided for {env_type}[/green]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error during setup: {e}[/red]")

# Helper function to run async commands
def run_async_command(coro):
    """Run async command in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

# Wrap async commands for Click
def async_command(f):
    """Decorator to make async commands work with Click"""
    def wrapper(*args, **kwargs):
        return run_async_command(f(*args, **kwargs))
    return wrapper

# Apply async wrapper to commands
status = async_command(status)
login = async_command(login)
permissions = async_command(permissions)
can_i = async_command(can_i)
logout = async_command(logout)
setup = async_command(setup) 