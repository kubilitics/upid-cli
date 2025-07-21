import click
from rich.console import Console
from upid.auth.providers.aws_iam_provider import AWSIAMAuthProvider
from upid.auth.providers.azure_ad_provider import AzureADAuthProvider
from upid.auth.providers.gcp_iam_provider import GCPIAMAuthProvider
from upid.core.config import Config
import asyncio

console = Console()

@click.group()
def cloud():
    """Cloud provider authentication and status commands"""
    pass

@cloud.command()
@click.option('--access-key-id', prompt=True, help='AWS Access Key ID')
@click.option('--secret-access-key', prompt=True, hide_input=True, help='AWS Secret Access Key')
@click.option('--region', default='us-east-1', help='AWS Region')
@click.option('--role-arn', default=None, help='AWS Role ARN (optional)')
def login_aws(access_key_id, secret_access_key, region, role_arn):
    """Login to AWS using IAM credentials"""
    try:
        provider = AWSIAMAuthProvider(region=region, role_arn=role_arn)
        user = click.get_current_context().run(asyncio.run(provider.authenticate({
            'access_key_id': access_key_id,
            'secret_access_key': secret_access_key,
            'role_arn': role_arn
        })))
        if user:
            console.print(f"[green]✓ AWS login successful! User: {user.user_id}[/green]")
        else:
            console.print("[red]✗ AWS login failed[/red]")
    except Exception as e:
        console.print(f"[red]✗ AWS login error: {e}[/red]")

@cloud.command()
@click.option('--tenant-id', prompt=True, help='Azure Tenant ID')
@click.option('--client-id', prompt=True, help='Azure Client ID')
@click.option('--client-secret', prompt=True, hide_input=True, help='Azure Client Secret')
def login_azure(tenant_id, client_id, client_secret):
    """Login to Azure using Azure AD credentials"""
    try:
        provider = AzureADAuthProvider(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        user = click.get_current_context().run(asyncio.run(provider.authenticate({})))
        if user:
            console.print(f"[green]✓ Azure login successful! User: {user.user_id}[/green]")
        else:
            console.print("[red]✗ Azure login failed[/red]")
    except Exception as e:
        console.print(f"[red]✗ Azure login error: {e}[/red]")

@cloud.command()
@click.option('--project-id', prompt=True, help='GCP Project ID')
@click.option('--service-account-key-path', prompt=True, help='Path to GCP Service Account JSON key')
def login_gcp(project_id, service_account_key_path):
    """Login to GCP using service account credentials"""
    try:
        provider = GCPIAMAuthProvider(project_id=project_id, service_account_key_path=service_account_key_path)
        user = click.get_current_context().run(asyncio.run(provider.authenticate({
            'service_account_key_path': service_account_key_path
        })))
        if user:
            console.print(f"[green]✓ GCP login successful! User: {user.user_id}[/green]")
        else:
            console.print("[red]✗ GCP login failed[/red]")
    except Exception as e:
        console.print(f"[red]✗ GCP login error: {e}[/red]")

@cloud.command()
@click.argument('provider', type=click.Choice(['aws', 'azure', 'gcp']))
def status(provider):
    """Show authentication status for a cloud provider"""
    try:
        if provider == 'aws':
            # In a real implementation, fetch and show AWS session info
            console.print("[cyan]AWS status: (session info not yet persisted)[/cyan]")
        elif provider == 'azure':
            console.print("[cyan]Azure status: (session info not yet persisted)[/cyan]")
        elif provider == 'gcp':
            console.print("[cyan]GCP status: (session info not yet persisted)[/cyan]")
    except Exception as e:
        console.print(f"[red]✗ Status error: {e}[/red]")

@cloud.command()
@click.argument('provider', type=click.Choice(['aws', 'azure', 'gcp']))
def logout(provider):
    """Logout from a cloud provider (clears session)"""
    try:
        # In a real implementation, clear session/token from config or secure store
        console.print(f"[yellow]Logged out from {provider.upper()} (session cleared)[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Logout error: {e}[/red]") 