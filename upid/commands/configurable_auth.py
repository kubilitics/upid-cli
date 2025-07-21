"""
Configurable Authentication Commands for UPID CLI
Allows organizations to configure authentication endpoints via environment variables
"""

import click
import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.configurable_auth import ConfigurableAuthenticator

console = Console()

@click.group()
@click.pass_context
def configurable_auth(ctx):
    """Configurable authentication for UPID CLI"""
    pass

@configurable_auth.command()
@click.pass_context
def status(ctx):
    """Show current authentication configuration and status"""
    try:
        authenticator = ConfigurableAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking authentication...", total=None)
            
            # Get auth info
            auth_info = authenticator.get_auth_info()
            
            # Validate authentication
            auth_result = authenticator.validate_auth()
            
            progress.update(task, description="Complete!")
        
        console.print("\n[bold blue]🔐 Configurable Authentication Status[/bold blue]\n")
        
        # Configuration table
        config_table = Table(title="Authentication Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("Auth Type", auth_info['auth_type'])
        config_table.add_row("Auth Endpoint", auth_info['auth_endpoint'] or "N/A")
        config_table.add_row("Auth Provider", auth_info['auth_provider'] or "N/A")
        config_table.add_row("Username", auth_info['auth_username'] or "N/A")
        config_table.add_row("Has Token", "✅ Yes" if auth_info['has_token'] else "❌ No")
        config_table.add_row("Has Certificate", "✅ Yes" if auth_info['has_cert'] else "❌ No")
        config_table.add_row("Has Key", "✅ Yes" if auth_info['has_key'] else "❌ No")
        config_table.add_row("Has CA", "✅ Yes" if auth_info['has_ca'] else "❌ No")
        
        console.print(config_table)
        
        # Status table
        status_table = Table(title="Authentication Status")
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="green")
        
        status_table.add_row("Status", "✅ Authenticated" if auth_result['success'] else "❌ Not Authenticated")
        status_table.add_row("Method", auth_result.get('method', 'N/A'))
        
        if auth_result.get('user'):
            status_table.add_row("User", auth_result['user'])
        
        if auth_result.get('context'):
            status_table.add_row("Context", auth_result['context'])
        
        if auth_result.get('error'):
            status_table.add_row("Error", f"❌ {auth_result['error']}")
        
        console.print(status_table)
        
        # Environment variables info
        env_table = Table(title="Environment Variables")
        env_table.add_column("Variable", style="cyan")
        env_table.add_column("Value", style="green")
        
        auth_vars = [
            'UPID_AUTH_TYPE',
            'UPID_AUTH_ENDPOINT',
            'UPID_AUTH_CLIENT_ID',
            'UPID_AUTH_CLIENT_SECRET',
            'UPID_AUTH_USERNAME',
            'UPID_AUTH_PASSWORD',
            'UPID_AUTH_TOKEN',
            'UPID_AUTH_CERT_PATH',
            'UPID_AUTH_KEY_PATH',
            'UPID_AUTH_CA_PATH',
            'UPID_AUTH_PROVIDER',
            'UPID_AUTH_SCOPE',
            'UPID_AUTH_AUDIENCE',
            'UPID_AUTH_ISSUER',
            'UPID_AUTH_TENANT_ID',
            'UPID_AUTH_REDIRECT_URI',
            'UPID_AUTH_CUSTOM_HEADERS',
            'UPID_AUTH_CUSTOM_PARAMS'
        ]
        
        for var in auth_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'PASSWORD' in var or 'SECRET' in var or 'TOKEN' in var:
                    value = '*' * min(len(value), 8)
                elif len(value) > 50:
                    value = value[:47] + '...'
                env_table.add_row(var, value)
            else:
                env_table.add_row(var, "Not set")
        
        console.print(env_table)
        
    except Exception as e:
        console.print(f"\n[red]❌ Error checking authentication status: {e}[/red]")

@configurable_auth.command()
@click.option('--auth-type', '-t', 
              type=click.Choice(['kubectl', 'oidc', 'saml', 'ldap', 'custom']),
              default='kubectl',
              help='Authentication type')
@click.option('--endpoint', '-e', help='Authentication endpoint URL')
@click.option('--client-id', help='Client ID for OIDC/SAML')
@click.option('--client-secret', help='Client secret for OIDC/SAML')
@click.option('--username', '-u', help='Username for authentication')
@click.option('--password', '-p', help='Password for authentication')
@click.option('--token', help='Authentication token')
@click.option('--provider', help='Authentication provider (azure, aws, gcp, okta, auth0, etc.)')
@click.option('--scope', help='OIDC scope')
@click.option('--audience', help='OIDC audience')
@click.option('--issuer', help='OIDC issuer')
@click.option('--tenant-id', help='Tenant ID for SAML')
@click.option('--redirect-uri', help='OIDC redirect URI')
@click.option('--cert-path', help='Certificate path for kubectl')
@click.option('--key-path', help='Key path for kubectl')
@click.option('--ca-path', help='CA certificate path for kubectl')
@click.option('--custom-headers', help='Custom headers as JSON string')
@click.option('--custom-params', help='Custom parameters as JSON string')
@click.pass_context
def configure(ctx, auth_type, endpoint, client_id, client_secret, username, password, 
              token, provider, scope, audience, issuer, tenant_id, redirect_uri,
              cert_path, key_path, ca_path, custom_headers, custom_params):
    """Configure authentication settings"""
    try:
        console.print("\n[bold blue]⚙️  Configurable Authentication Setup[/bold blue]\n")
        
        # Show current configuration
        authenticator = ConfigurableAuthenticator()
        auth_info = authenticator.get_auth_info()
        
        console.print("[yellow]Current Configuration:[/yellow]")
        console.print(f"  Auth Type: {auth_info['auth_type']}")
        console.print(f"  Endpoint: {auth_info['auth_endpoint'] or 'N/A'}")
        console.print(f"  Provider: {auth_info['auth_provider'] or 'N/A'}")
        
        # Show configuration options
        console.print(f"\n[yellow]New Configuration:[/yellow]")
        console.print(f"  Auth Type: {auth_type}")
        if endpoint:
            console.print(f"  Endpoint: {endpoint}")
        if client_id:
            console.print(f"  Client ID: {client_id}")
        if provider:
            console.print(f"  Provider: {provider}")
        
        # Generate environment variable commands
        env_commands = []
        env_commands.append(f"export UPID_AUTH_TYPE={auth_type}")
        
        if endpoint:
            env_commands.append(f"export UPID_AUTH_ENDPOINT={endpoint}")
        
        if client_id:
            env_commands.append(f"export UPID_AUTH_CLIENT_ID={client_id}")
        
        if client_secret:
            env_commands.append(f"export UPID_AUTH_CLIENT_SECRET={client_secret}")
        
        if username:
            env_commands.append(f"export UPID_AUTH_USERNAME={username}")
        
        if password:
            env_commands.append(f"export UPID_AUTH_PASSWORD={password}")
        
        if token:
            env_commands.append(f"export UPID_AUTH_TOKEN={token}")
        
        if provider:
            env_commands.append(f"export UPID_AUTH_PROVIDER={provider}")
        
        if scope:
            env_commands.append(f"export UPID_AUTH_SCOPE={scope}")
        
        if audience:
            env_commands.append(f"export UPID_AUTH_AUDIENCE={audience}")
        
        if issuer:
            env_commands.append(f"export UPID_AUTH_ISSUER={issuer}")
        
        if tenant_id:
            env_commands.append(f"export UPID_AUTH_TENANT_ID={tenant_id}")
        
        if redirect_uri:
            env_commands.append(f"export UPID_AUTH_REDIRECT_URI={redirect_uri}")
        
        if cert_path:
            env_commands.append(f"export UPID_AUTH_CERT_PATH={cert_path}")
        
        if key_path:
            env_commands.append(f"export UPID_AUTH_KEY_PATH={key_path}")
        
        if ca_path:
            env_commands.append(f"export UPID_AUTH_CA_PATH={ca_path}")
        
        if custom_headers:
            env_commands.append(f"export UPID_AUTH_CUSTOM_HEADERS='{custom_headers}'")
        
        if custom_params:
            env_commands.append(f"export UPID_AUTH_CUSTOM_PARAMS='{custom_params}'")
        
        # Display commands
        console.print("\n[green]Environment Variables to Set:[/green]")
        for cmd in env_commands:
            console.print(f"  {cmd}")
        
        # Test configuration
        if Confirm.ask("\nTest the new configuration?"):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Testing authentication...", total=None)
                
                # Create new authenticator with updated config
                os.environ['UPID_AUTH_TYPE'] = auth_type
                if endpoint:
                    os.environ['UPID_AUTH_ENDPOINT'] = endpoint
                if client_id:
                    os.environ['UPID_AUTH_CLIENT_ID'] = client_id
                if client_secret:
                    os.environ['UPID_AUTH_CLIENT_SECRET'] = client_secret
                if username:
                    os.environ['UPID_AUTH_USERNAME'] = username
                if password:
                    os.environ['UPID_AUTH_PASSWORD'] = password
                if token:
                    os.environ['UPID_AUTH_TOKEN'] = token
                if provider:
                    os.environ['UPID_AUTH_PROVIDER'] = provider
                if scope:
                    os.environ['UPID_AUTH_SCOPE'] = scope
                if audience:
                    os.environ['UPID_AUTH_AUDIENCE'] = audience
                if issuer:
                    os.environ['UPID_AUTH_ISSUER'] = issuer
                if tenant_id:
                    os.environ['UPID_AUTH_TENANT_ID'] = tenant_id
                if redirect_uri:
                    os.environ['UPID_AUTH_REDIRECT_URI'] = redirect_uri
                if cert_path:
                    os.environ['UPID_AUTH_CERT_PATH'] = cert_path
                if key_path:
                    os.environ['UPID_AUTH_KEY_PATH'] = key_path
                if ca_path:
                    os.environ['UPID_AUTH_CA_PATH'] = ca_path
                if custom_headers:
                    os.environ['UPID_AUTH_CUSTOM_HEADERS'] = custom_headers
                if custom_params:
                    os.environ['UPID_AUTH_CUSTOM_PARAMS'] = custom_params
                
                new_authenticator = ConfigurableAuthenticator()
                auth_result = new_authenticator.validate_auth()
                
                progress.update(task, description="Complete!")
            
            if auth_result['success']:
                console.print(f"\n[green]✅ Authentication successful![/green]")
                console.print(f"[green]Method: {auth_result.get('method', 'N/A')}[/green]")
                if auth_result.get('user'):
                    console.print(f"[green]User: {auth_result['user']}[/green]")
                if auth_result.get('context'):
                    console.print(f"[green]Context: {auth_result['context']}[/green]")
            else:
                console.print(f"\n[red]❌ Authentication failed: {auth_result.get('error', 'Unknown error')}[/red]")
        
        # Save to file option
        if Confirm.ask("\nSave configuration to a file?"):
            filename = Prompt.ask("Enter filename", default="upid_auth_config.sh")
            
            with open(filename, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# UPID Authentication Configuration\n")
                f.write("# Generated by UPID CLI\n\n")
                for cmd in env_commands:
                    f.write(f"{cmd}\n")
            
            console.print(f"\n[green]✅ Configuration saved to {filename}[/green]")
            console.print(f"[yellow]To use this configuration:[/yellow]")
            console.print(f"  source {filename}")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error configuring authentication: {e}[/red]")

@configurable_auth.command()
@click.pass_context
def test(ctx):
    """Test current authentication configuration"""
    try:
        authenticator = ConfigurableAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Testing authentication...", total=None)
            
            auth_result = authenticator.validate_auth()
            
            progress.update(task, description="Complete!")
        
        console.print("\n[bold blue]🧪 Authentication Test Results[/bold blue]\n")
        
        if auth_result['success']:
            console.print("[green]✅ Authentication successful![/green]")
            
            result_table = Table(title="Authentication Details")
            result_table.add_column("Property", style="cyan")
            result_table.add_column("Value", style="green")
            
            result_table.add_row("Status", "✅ Success")
            result_table.add_row("Auth Type", auth_result['auth_type'])
            result_table.add_row("Method", auth_result.get('method', 'N/A'))
            
            if auth_result.get('user'):
                result_table.add_row("User", auth_result['user'])
            
            if auth_result.get('context'):
                result_table.add_row("Context", auth_result['context'])
            
            if auth_result.get('token'):
                result_table.add_row("Token", "✅ Present")
            
            console.print(result_table)
            
            console.print("\n[yellow]Next steps:[/yellow]")
            console.print("• Run 'upid cluster list' to see your clusters")
            console.print("• Run 'upid analyze <cluster>' to analyze resources")
            console.print("• Run 'upid optimize <cluster>' to optimize resources")
        
        else:
            console.print("[red]❌ Authentication failed![/red]")
            
            error_table = Table(title="Error Details")
            error_table.add_column("Property", style="cyan")
            error_table.add_column("Value", style="red")
            
            error_table.add_row("Status", "❌ Failed")
            error_table.add_row("Auth Type", auth_result['auth_type'])
            error_table.add_row("Error", auth_result.get('error', 'Unknown error'))
            
            console.print(error_table)
            
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("• Check your environment variables")
            console.print("• Verify authentication endpoint is accessible")
            console.print("• Ensure credentials are correct")
            console.print("• For kubectl: ensure kubectl is configured")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error testing authentication: {e}[/red]")

@configurable_auth.command()
@click.pass_context
def reset(ctx):
    """Reset authentication configuration to defaults (kubectl)"""
    try:
        console.print("\n[bold blue]🔄 Reset Authentication Configuration[/bold blue]\n")
        
        # List current environment variables
        auth_vars = [
            'UPID_AUTH_TYPE',
            'UPID_AUTH_ENDPOINT',
            'UPID_AUTH_CLIENT_ID',
            'UPID_AUTH_CLIENT_SECRET',
            'UPID_AUTH_USERNAME',
            'UPID_AUTH_PASSWORD',
            'UPID_AUTH_TOKEN',
            'UPID_AUTH_CERT_PATH',
            'UPID_AUTH_KEY_PATH',
            'UPID_AUTH_CA_PATH',
            'UPID_AUTH_PROVIDER',
            'UPID_AUTH_SCOPE',
            'UPID_AUTH_AUDIENCE',
            'UPID_AUTH_ISSUER',
            'UPID_AUTH_TENANT_ID',
            'UPID_AUTH_REDIRECT_URI',
            'UPID_AUTH_CUSTOM_HEADERS',
            'UPID_AUTH_CUSTOM_PARAMS'
        ]
        
        current_vars = []
        for var in auth_vars:
            if os.getenv(var):
                current_vars.append(var)
        
        if current_vars:
            console.print("[yellow]Current authentication environment variables:[/yellow]")
            for var in current_vars:
                console.print(f"  {var}")
            
            if Confirm.ask("\nUnset these variables?"):
                for var in current_vars:
                    if var in os.environ:
                        del os.environ[var]
                
                console.print("[green]✅ Environment variables unset[/green]")
                
                # Test default configuration
                authenticator = ConfigurableAuthenticator()
                auth_result = authenticator.validate_auth()
                
                if auth_result['success']:
                    console.print("[green]✅ Default kubectl authentication working[/green]")
                else:
                    console.print(f"[red]❌ Default authentication failed: {auth_result.get('error')}[/red]")
        else:
            console.print("[yellow]No authentication environment variables set[/yellow]")
            console.print("[green]✅ Already using default kubectl authentication[/green]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error resetting authentication: {e}[/red]")

@configurable_auth.command()
@click.pass_context
def help(ctx):
    """Show help for configurable authentication"""
    console.print("\n[bold blue]📖 Configurable Authentication Help[/bold blue]\n")
    
    help_text = """
    UPID CLI supports multiple authentication methods via environment variables:
    
    [bold]1. Kubectl Authentication (Default for Individuals)[/bold]
    • No configuration required if kubectl is set up
    • Uses existing kubeconfig and cluster access
    • Perfect for individual users with kubectl access
    
    [bold]2. OIDC Authentication (Enterprise)[/bold]
    • Set UPID_AUTH_TYPE=oidc
    • Set UPID_AUTH_ENDPOINT=<oidc_endpoint>
    • Set UPID_AUTH_CLIENT_ID=<client_id>
    • Set UPID_AUTH_CLIENT_SECRET=<client_secret>
    • Optional: UPID_AUTH_SCOPE, UPID_AUTH_AUDIENCE, UPID_AUTH_ISSUER
    
    [bold]3. SAML Authentication (Enterprise)[/bold]
    • Set UPID_AUTH_TYPE=saml
    • Set UPID_AUTH_ENDPOINT=<saml_endpoint>
    • Set UPID_AUTH_CLIENT_ID=<client_id>
    • Set UPID_AUTH_CLIENT_SECRET=<client_secret>
    • Optional: UPID_AUTH_PROVIDER, UPID_AUTH_TENANT_ID
    
    [bold]4. LDAP Authentication (Enterprise)[/bold]
    • Set UPID_AUTH_TYPE=ldap
    • Set UPID_AUTH_ENDPOINT=<ldap_endpoint>
    • Set UPID_AUTH_USERNAME=<username>
    • Set UPID_AUTH_PASSWORD=<password>
    • Optional: UPID_AUTH_PROVIDER
    
    [bold]5. Custom Authentication (Enterprise)[/bold]
    • Set UPID_AUTH_TYPE=custom
    • Set UPID_AUTH_ENDPOINT=<custom_endpoint>
    • Set UPID_AUTH_CUSTOM_HEADERS='{"header": "value"}'
    • Set UPID_AUTH_CUSTOM_PARAMS='{"param": "value"}'
    
    [bold]Examples:[/bold]
    
    [yellow]For Azure AD OIDC:[/yellow]
    export UPID_AUTH_TYPE=oidc
    export UPID_AUTH_ENDPOINT=https://login.microsoftonline.com/<tenant_id>/oauth2/v2.0/token
    export UPID_AUTH_CLIENT_ID=<client_id>
    export UPID_AUTH_CLIENT_SECRET=<client_secret>
    export UPID_AUTH_SCOPE="openid profile email"
    export UPID_AUTH_AUDIENCE=<api_audience>
    
    [yellow]For AWS IAM:[/yellow]
    export UPID_AUTH_TYPE=oidc
    export UPID_AUTH_ENDPOINT=https://cognito-idp.<region>.amazonaws.com/<user_pool_id>/oauth2/token
    export UPID_AUTH_CLIENT_ID=<client_id>
    export UPID_AUTH_CLIENT_SECRET=<client_secret>
    export UPID_AUTH_PROVIDER=aws
    
    [yellow]For Google Cloud:[/yellow]
    export UPID_AUTH_TYPE=oidc
    export UPID_AUTH_ENDPOINT=https://oauth2.googleapis.com/token
    export UPID_AUTH_CLIENT_ID=<client_id>
    export UPID_AUTH_CLIENT_SECRET=<client_secret>
    export UPID_AUTH_PROVIDER=gcp
    
    [yellow]For kubectl (Individual Users):[/yellow]
    # No environment variables needed if kubectl is configured
    # Just run: upid configurable-auth test
    
    [bold]Commands:[/bold]
    • upid configurable-auth status    - Show current configuration
    • upid configurable-auth configure - Configure authentication
    • upid configurable-auth test      - Test authentication
    • upid configurable-auth reset     - Reset to defaults
    • upid configurable-auth help      - Show this help
    """
    
    console.print(Panel(help_text, title="Configurable Authentication Guide", border_style="blue")) 