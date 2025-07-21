"""
Interactive Onboarding Commands for UPID CLI
Guides users through authentication setup with environment detection
"""

import click
import os
import webbrowser
import time
import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from rich.text import Text

from ..core.configurable_auth import ConfigurableAuthenticator
from ..core.config import Config

console = Console()

@click.group()
@click.pass_context
def onboarding(ctx):
    """Interactive onboarding for UPID CLI authentication"""
    pass

@onboarding.command()
@click.option('--force', is_flag=True, help='Force re-onboarding even if already configured')
@click.pass_context
def onboard(ctx, force):
    """Interactive onboarding wizard for UPID CLI authentication"""
    try:
        console.print("\n[bold blue]🚀 UPID CLI Onboarding Wizard[/bold blue]\n")
        console.print("Welcome to UPID CLI! Let's get you set up with authentication.\n")
        
        # Check if already configured
        if not force:
            authenticator = ConfigurableAuthenticator()
            auth_info = authenticator.get_auth_info()
            if auth_info['auth_type'] != 'kubectl' or any([
                os.getenv('UPID_AUTH_ENDPOINT'),
                os.getenv('UPID_AUTH_CLIENT_ID'),
                os.getenv('UPID_AUTH_USERNAME'),
                os.getenv('UPID_AUTH_TOKEN')
            ]):
                if Confirm.ask("Authentication already configured. Re-run onboarding?"):
                    force = True
                else:
                    console.print("[yellow]Onboarding skipped. Use 'upid onboarding status' to check current configuration.[/yellow]")
                    return
        
        # Step 1: Environment Detection
        env_info = detect_environment()
        console.print(f"\n[green]✅ Detected environment: {env_info['type']}[/green]")
        console.print(f"[green]   Details: {env_info['description']}[/green]")
        
        # Step 2: Authentication Method Selection
        auth_method = select_authentication_method(env_info)
        
        # Step 3: Configure Authentication
        config_result = configure_authentication(auth_method, env_info)
        
        # Step 4: Test Configuration
        test_result = test_authentication(config_result)
        
        # Step 5: Save Configuration
        if test_result['success']:
            save_configuration(config_result)
            show_success_message(config_result)
        else:
            show_troubleshooting_help(test_result)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Onboarding cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Onboarding failed: {e}[/red]")
        console.print("[yellow]Try running 'upid onboarding onboard --force' to start over.[/yellow]")

@onboarding.command()
@click.pass_context
def status(ctx):
    """Show current onboarding status and configuration"""
    try:
        authenticator = ConfigurableAuthenticator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking configuration...", total=None)
            
            auth_info = authenticator.get_auth_info()
            env_info = detect_environment()
            auth_result = authenticator.validate_auth()
            
            progress.update(task, description="Complete!")
        
        console.print("\n[bold blue]📊 Onboarding Status[/bold blue]\n")
        
        # Environment Status
        env_table = Table(title="Environment Detection")
        env_table.add_column("Property", style="cyan")
        env_table.add_column("Value", style="green")
        
        env_table.add_row("Environment Type", env_info['type'])
        env_table.add_row("Description", env_info['description'])
        env_table.add_row("Recommended Auth", env_info.get('recommended_auth', 'N/A'))
        
        console.print(env_table)
        
        # Authentication Status
        auth_table = Table(title="Authentication Configuration")
        auth_table.add_column("Property", style="cyan")
        auth_table.add_column("Value", style="green")
        
        auth_table.add_row("Auth Type", auth_info['auth_type'])
        auth_table.add_row("Status", "✅ Configured" if auth_result['success'] else "❌ Not Configured")
        auth_table.add_row("Method", auth_result.get('method', 'N/A'))
        
        if auth_result.get('user'):
            auth_table.add_row("User", auth_result['user'])
        
        if auth_result.get('context'):
            auth_table.add_row("Context", auth_result['context'])
        
        console.print(auth_table)
        
        # Configuration Details
        config_table = Table(title="Configuration Details")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        if auth_info['auth_endpoint']:
            config_table.add_row("Endpoint", auth_info['auth_endpoint'])
        if auth_info['auth_provider']:
            config_table.add_row("Provider", auth_info['auth_provider'])
        if auth_info['auth_username']:
            config_table.add_row("Username", auth_info['auth_username'])
        if auth_info['has_token']:
            config_table.add_row("Token", "✅ Present")
        if auth_info['has_cert']:
            config_table.add_row("Certificate", "✅ Present")
        
        console.print(config_table)
        
        # Next Steps
        if auth_result['success']:
            console.print("\n[green]✅ Authentication is working![/green]")
            console.print("\n[yellow]Next steps:[/yellow]")
            console.print("• Run 'upid cluster list' to see your clusters")
            console.print("• Run 'upid analyze <cluster>' to analyze resources")
            console.print("• Run 'upid optimize <cluster>' to optimize resources")
        else:
            console.print("\n[yellow]⚠️  Authentication needs configuration[/yellow]")
            console.print("\n[yellow]Next steps:[/yellow]")
            console.print("• Run 'upid onboarding onboard' to configure authentication")
            console.print("• Run 'upid configurable-auth help' for manual configuration")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error checking status: {e}[/red]")

@onboarding.command()
@click.pass_context
def help(ctx):
    """Show comprehensive help for onboarding"""
    console.print("\n[bold blue]📖 UPID CLI Onboarding Help[/bold blue]\n")
    
    help_text = """
    UPID CLI Onboarding provides an interactive wizard to set up authentication:
    
    [bold]Commands:[/bold]
    • upid onboarding onboard    - Interactive onboarding wizard
    • upid onboarding status     - Show current onboarding status
    • upid onboarding help       - Show this help
    
    [bold]Onboarding Process:[/bold]
    1. Environment Detection - Automatically detects your environment
    2. Authentication Selection - Choose the best auth method for you
    3. Configuration - Enter required credentials and settings
    4. Testing - Validates your authentication setup
    5. Saving - Saves configuration for future use
    
    [bold]Supported Authentication Methods:[/bold]
    • kubectl - For individuals with Kubernetes cluster access
    • OIDC/SSO - For enterprise with Azure, Google, Okta, etc.
    • SAML - For enterprise with SAML providers
    • LDAP/AD - For enterprise with Active Directory
    • Custom - For organizations with custom auth systems
    
    [bold]Examples:[/bold]
    
    [yellow]For Individuals:[/yellow]
    upid onboarding onboard
    
    [yellow]For Enterprise (Azure AD):[/yellow]
    upid onboarding onboard --auth-type oidc --provider azure
    
    [yellow]For Enterprise (SAML):[/yellow]
    upid onboarding onboard --auth-type saml --provider okta
    
    [bold]Environment Variables:[/bold]
    The onboarding process can set these environment variables:
    • UPID_AUTH_TYPE - Authentication type
    • UPID_AUTH_ENDPOINT - Authentication endpoint
    • UPID_AUTH_CLIENT_ID - Client ID for OIDC/SAML
    • UPID_AUTH_CLIENT_SECRET - Client secret
    • UPID_AUTH_USERNAME - Username for LDAP
    • UPID_AUTH_PASSWORD - Password for LDAP
    • UPID_AUTH_PROVIDER - Authentication provider
    • And many more...
    
    [bold]Next Steps After Onboarding:[/bold]
    • Run 'upid cluster list' to see your clusters
    • Run 'upid analyze <cluster>' to analyze resources
    • Run 'upid optimize <cluster>' to optimize resources
    • Run 'upid onboarding status' to check configuration
    
    [bold]Troubleshooting:[/bold]
    • Run 'upid onboarding onboard --force' to reconfigure
    • Run 'upid configurable-auth help' for manual configuration
    • Check 'upid onboarding status' for current configuration
    """
    
    console.print(Panel(help_text, title="Onboarding Guide", border_style="blue"))

def detect_environment():
    """Detect the user's environment and suggest authentication method"""
    
    # Check for kubectl
    kubectl_available = False
    kubectl_context = None
    try:
        result = subprocess.run(['kubectl', 'version', '--client'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            kubectl_available = True
            
            # Get current context
            result = subprocess.run(['kubectl', 'config', 'current-context'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                kubectl_context = result.stdout.strip()
    except:
        pass
    
    # Check for cloud providers
    cloud_providers = []
    
    # Check AWS
    if os.getenv('AWS_PROFILE') or os.getenv('AWS_ACCESS_KEY_ID'):
        cloud_providers.append('aws')
    
    # Check Azure
    if os.getenv('AZURE_CLIENT_ID') or os.getenv('AZURE_TENANT_ID'):
        cloud_providers.append('azure')
    
    # Check GCP
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('GCP_PROJECT'):
        cloud_providers.append('gcp')
    
    # Check for enterprise environment variables
    enterprise_auth = any([
        os.getenv('UPID_AUTH_TYPE'),
        os.getenv('UPID_AUTH_ENDPOINT'),
        os.getenv('UPID_AUTH_CLIENT_ID'),
        os.getenv('UPID_AUTH_USERNAME'),
        os.getenv('UPID_AUTH_TOKEN')
    ])
    
    # Determine environment type
    if enterprise_auth:
        return {
            'type': 'enterprise',
            'description': 'Enterprise environment with custom authentication',
            'recommended_auth': 'custom',
            'kubectl_available': kubectl_available,
            'kubectl_context': kubectl_context,
            'cloud_providers': cloud_providers
        }
    elif kubectl_available:
        if cloud_providers:
            return {
                'type': 'cloud_kubernetes',
                'description': f'Cloud Kubernetes environment ({", ".join(cloud_providers)}) with kubectl access',
                'recommended_auth': 'kubectl',
                'kubectl_available': True,
                'kubectl_context': kubectl_context,
                'cloud_providers': cloud_providers
            }
        else:
            return {
                'type': 'local_kubernetes',
                'description': 'Local Kubernetes environment with kubectl access',
                'recommended_auth': 'kubectl',
                'kubectl_available': True,
                'kubectl_context': kubectl_context,
                'cloud_providers': []
            }
    else:
        return {
            'type': 'unknown',
            'description': 'Unknown environment - no kubectl or enterprise auth detected',
            'recommended_auth': 'manual',
            'kubectl_available': False,
            'kubectl_context': None,
            'cloud_providers': cloud_providers
        }

def select_authentication_method(env_info):
    """Guide user through authentication method selection"""
    
    console.print("\n[bold blue]🔐 Authentication Method Selection[/bold blue]\n")
    
    # Show recommended method
    recommended = env_info.get('recommended_auth', 'manual')
    console.print(f"[yellow]Recommended method: {recommended.upper()}[/yellow]")
    
    # Show available options
    options = []
    
    if env_info['kubectl_available']:
        options.append(('kubectl', 'Kubectl Authentication (for individuals with cluster access)'))
    
    options.extend([
        ('oidc', 'OIDC/SSO Authentication (for enterprise with Azure, Google, Okta, etc.)'),
        ('saml', 'SAML Authentication (for enterprise with SAML providers)'),
        ('ldap', 'LDAP/Active Directory Authentication (for enterprise)'),
        ('custom', 'Custom Authentication (for organizations with custom auth systems)'),
        ('manual', 'Manual Configuration (advanced users)')
    ])
    
    # Display options
    console.print("\n[cyan]Available authentication methods:[/cyan]")
    for i, (method, description) in enumerate(options, 1):
        marker = "⭐" if method == recommended else "  "
        console.print(f"{marker} {i}. {description}")
    
    # Get user choice
    while True:
        try:
            choice = IntPrompt.ask(
                "\nSelect authentication method",
                default=options.index((recommended, '')) + 1 if recommended in [opt[0] for opt in options] else 1
            )
            
            if 1 <= choice <= len(options):
                selected_method = options[choice - 1][0]
                console.print(f"\n[green]✅ Selected: {selected_method.upper()}[/green]")
                return selected_method
            else:
                console.print("[red]Invalid choice. Please select a valid option.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")

def configure_authentication(method, env_info):
    """Configure the selected authentication method"""
    
    console.print(f"\n[bold blue]⚙️  Configuring {method.upper()} Authentication[/bold blue]\n")
    
    if method == 'kubectl':
        return configure_kubectl_auth(env_info)
    elif method == 'oidc':
        return configure_oidc_auth(env_info)
    elif method == 'saml':
        return configure_saml_auth(env_info)
    elif method == 'ldap':
        return configure_ldap_auth(env_info)
    elif method == 'custom':
        return configure_custom_auth(env_info)
    else:
        return configure_manual_auth(env_info)

def configure_kubectl_auth(env_info):
    """Configure kubectl authentication"""
    
    console.print("[yellow]Configuring kubectl authentication...[/yellow]")
    
    # Test kubectl connection
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Testing kubectl connection...", total=None)
        
        try:
            result = subprocess.run(['kubectl', 'cluster-info'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                progress.update(task, description="✅ kubectl connection successful")
                
                # Get current context and user
                context_result = subprocess.run(['kubectl', 'config', 'current-context'], 
                                             capture_output=True, text=True, timeout=5)
                user_result = subprocess.run(['kubectl', 'whoami'], 
                                          capture_output=True, text=True, timeout=5)
                
                context = context_result.stdout.strip() if context_result.returncode == 0 else 'unknown'
                user = user_result.stdout.strip() if user_result.returncode == 0 else 'unknown'
                
                return {
                    'method': 'kubectl',
                    'success': True,
                    'context': context,
                    'user': user,
                    'config': {
                        'UPID_AUTH_TYPE': 'kubectl'
                    }
                }
            else:
                progress.update(task, description="❌ kubectl connection failed")
                return {
                    'method': 'kubectl',
                    'success': False,
                    'error': 'Failed to connect to Kubernetes cluster',
                    'config': {
                        'UPID_AUTH_TYPE': 'kubectl'
                    }
                }
        
        except Exception as e:
            progress.update(task, description=f"❌ Error: {str(e)}")
            return {
                'method': 'kubectl',
                'success': False,
                'error': str(e),
                'config': {
                    'UPID_AUTH_TYPE': 'kubectl'
                }
            }

def configure_oidc_auth(env_info):
    """Configure OIDC authentication with browser flow"""
    
    console.print("[yellow]Configuring OIDC authentication...[/yellow]")
    
    # Get OIDC provider
    providers = [
        ('azure', 'Azure Active Directory'),
        ('google', 'Google Cloud'),
        ('aws', 'AWS Cognito'),
        ('okta', 'Okta'),
        ('auth0', 'Auth0'),
        ('custom', 'Custom OIDC Provider')
    ]
    
    console.print("\n[cyan]Select your OIDC provider:[/cyan]")
    for i, (provider, name) in enumerate(providers, 1):
        console.print(f"  {i}. {name}")
    
    while True:
        try:
            choice = IntPrompt.ask("Select provider", default=1)
            if 1 <= choice <= len(providers):
                selected_provider = providers[choice - 1][0]
                break
            else:
                console.print("[red]Invalid choice. Please select a valid option.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    # Get configuration details
    if selected_provider == 'custom':
        endpoint = Prompt.ask("Enter OIDC endpoint URL")
        client_id = Prompt.ask("Enter client ID")
        client_secret = Prompt.ask("Enter client secret", password=True)
        scope = Prompt.ask("Enter scope", default="openid profile email")
        audience = Prompt.ask("Enter audience (optional)")
    else:
        # Pre-configured endpoints for common providers
        provider_configs = {
            'azure': {
                'endpoint': 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
                'scope': 'openid profile email',
                'audience': 'api://your-api-audience'
            },
            'google': {
                'endpoint': 'https://oauth2.googleapis.com/token',
                'scope': 'openid profile email',
                'audience': 'your-project-id'
            },
            'aws': {
                'endpoint': 'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/oauth2/token',
                'scope': 'openid profile email',
                'audience': None
            },
            'okta': {
                'endpoint': 'https://{domain}.okta.com/oauth2/v1/token',
                'scope': 'openid profile email',
                'audience': 'api://default'
            },
            'auth0': {
                'endpoint': 'https://{domain}.auth0.com/oauth/token',
                'scope': 'openid profile email',
                'audience': 'your-api-audience'
            }
        }
        
        config = provider_configs[selected_provider]
        endpoint = Prompt.ask("Enter OIDC endpoint URL", default=config['endpoint'])
        client_id = Prompt.ask("Enter client ID")
        client_secret = Prompt.ask("Enter client secret", password=True)
        scope = Prompt.ask("Enter scope", default=config['scope'])
        audience = Prompt.ask("Enter audience (optional)", default=config.get('audience', ''))
    
    # Configure environment variables
    config = {
        'UPID_AUTH_TYPE': 'oidc',
        'UPID_AUTH_ENDPOINT': endpoint,
        'UPID_AUTH_CLIENT_ID': client_id,
        'UPID_AUTH_CLIENT_SECRET': client_secret,
        'UPID_AUTH_SCOPE': scope,
        'UPID_AUTH_PROVIDER': selected_provider
    }
    
    if audience:
        config['UPID_AUTH_AUDIENCE'] = audience
    
    # Set environment variables for testing
    for key, value in config.items():
        os.environ[key] = value
    
    return {
        'method': 'oidc',
        'success': True,
        'provider': selected_provider,
        'config': config
    }

def configure_saml_auth(env_info):
    """Configure SAML authentication"""
    
    console.print("[yellow]Configuring SAML authentication...[/yellow]")
    
    # Get SAML configuration
    endpoint = Prompt.ask("Enter SAML endpoint URL")
    client_id = Prompt.ask("Enter client ID")
    client_secret = Prompt.ask("Enter client secret", password=True)
    provider = Prompt.ask("Enter provider name (optional)")
    tenant_id = Prompt.ask("Enter tenant ID (optional)")
    
    config = {
        'UPID_AUTH_TYPE': 'saml',
        'UPID_AUTH_ENDPOINT': endpoint,
        'UPID_AUTH_CLIENT_ID': client_id,
        'UPID_AUTH_CLIENT_SECRET': client_secret
    }
    
    if provider:
        config['UPID_AUTH_PROVIDER'] = provider
    if tenant_id:
        config['UPID_AUTH_TENANT_ID'] = tenant_id
    
    # Set environment variables for testing
    for key, value in config.items():
        os.environ[key] = value
    
    return {
        'method': 'saml',
        'success': True,
        'config': config
    }

def configure_ldap_auth(env_info):
    """Configure LDAP authentication"""
    
    console.print("[yellow]Configuring LDAP authentication...[/yellow]")
    
    # Get LDAP configuration
    endpoint = Prompt.ask("Enter LDAP endpoint URL")
    username = Prompt.ask("Enter username")
    password = Prompt.ask("Enter password", password=True)
    provider = Prompt.ask("Enter provider name (optional)")
    
    config = {
        'UPID_AUTH_TYPE': 'ldap',
        'UPID_AUTH_ENDPOINT': endpoint,
        'UPID_AUTH_USERNAME': username,
        'UPID_AUTH_PASSWORD': password
    }
    
    if provider:
        config['UPID_AUTH_PROVIDER'] = provider
    
    # Set environment variables for testing
    for key, value in config.items():
        os.environ[key] = value
    
    return {
        'method': 'ldap',
        'success': True,
        'config': config
    }

def configure_custom_auth(env_info):
    """Configure custom authentication"""
    
    console.print("[yellow]Configuring custom authentication...[/yellow]")
    
    # Get custom configuration
    endpoint = Prompt.ask("Enter authentication endpoint URL")
    
    use_headers = Confirm.ask("Use custom headers?")
    custom_headers = {}
    if use_headers:
        console.print("[yellow]Enter custom headers (key=value format, empty line to finish):[/yellow]")
        while True:
            header = Prompt.ask("Header")
            if not header:
                break
            if '=' in header:
                key, value = header.split('=', 1)
                custom_headers[key.strip()] = value.strip()
    
    use_params = Confirm.ask("Use custom parameters?")
    custom_params = {}
    if use_params:
        console.print("[yellow]Enter custom parameters (key=value format, empty line to finish):[/yellow]")
        while True:
            param = Prompt.ask("Parameter")
            if not param:
                break
            if '=' in param:
                key, value = param.split('=', 1)
                custom_params[key.strip()] = value.strip()
    
    config = {
        'UPID_AUTH_TYPE': 'custom',
        'UPID_AUTH_ENDPOINT': endpoint
    }
    
    if custom_headers:
        config['UPID_AUTH_CUSTOM_HEADERS'] = json.dumps(custom_headers)
    if custom_params:
        config['UPID_AUTH_CUSTOM_PARAMS'] = json.dumps(custom_params)
    
    # Set environment variables for testing
    for key, value in config.items():
        os.environ[key] = value
    
    return {
        'method': 'custom',
        'success': True,
        'config': config
    }

def configure_manual_auth(env_info):
    """Configure manual authentication"""
    
    console.print("[yellow]Manual configuration mode...[/yellow]")
    console.print("[yellow]You can set environment variables manually or use 'upid configurable-auth configure'[/yellow]")
    
    return {
        'method': 'manual',
        'success': False,
        'config': {}
    }

def test_authentication(config_result):
    """Test the configured authentication"""
    
    console.print(f"\n[bold blue]🧪 Testing {config_result['method'].upper()} Authentication[/bold blue]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Testing authentication...", total=None)
        
        try:
            authenticator = ConfigurableAuthenticator()
            auth_result = authenticator.validate_auth()
            
            progress.update(task, description="Complete!")
            
            if auth_result['success']:
                console.print("[green]✅ Authentication successful![/green]")
                return {
                    'success': True,
                    'method': auth_result.get('method', config_result['method']),
                    'user': auth_result.get('user'),
                    'context': auth_result.get('context')
                }
            else:
                console.print(f"[red]❌ Authentication failed: {auth_result.get('error', 'Unknown error')}[/red]")
                return {
                    'success': False,
                    'error': auth_result.get('error', 'Unknown error'),
                    'method': config_result['method']
                }
        
        except Exception as e:
            progress.update(task, description=f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': config_result['method']
            }

def save_configuration(config_result):
    """Save the configuration"""
    
    console.print(f"\n[bold blue]💾 Saving Configuration[/bold blue]\n")
    
    # Ask user how to save
    save_options = [
        ('env_file', 'Save to environment file (.env)'),
        ('shell_script', 'Generate shell script with export commands'),
        ('config_file', 'Save to UPID config file'),
        ('manual', 'Show manual instructions')
    ]
    
    console.print("[cyan]How would you like to save the configuration?[/cyan]")
    for i, (option, description) in enumerate(save_options, 1):
        console.print(f"  {i}. {description}")
    
    while True:
        try:
            choice = IntPrompt.ask("Select option", default=1)
            if 1 <= choice <= len(save_options):
                selected_option = save_options[choice - 1][0]
                break
            else:
                console.print("[red]Invalid choice. Please select a valid option.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
    
    if selected_option == 'env_file':
        save_to_env_file(config_result['config'])
    elif selected_option == 'shell_script':
        save_to_shell_script(config_result['config'])
    elif selected_option == 'config_file':
        save_to_config_file(config_result['config'])
    else:
        show_manual_instructions(config_result['config'])

def save_to_env_file(config):
    """Save configuration to .env file"""
    
    env_file = Path('.env')
    
    with open(env_file, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    
    console.print(f"[green]✅ Configuration saved to {env_file}[/green]")
    console.print(f"[yellow]To use: source {env_file}[/yellow]")

def save_to_shell_script(config):
    """Generate shell script with export commands"""
    
    script_file = Path('upid_auth_config.sh')
    
    with open(script_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# UPID Authentication Configuration\n")
        f.write("# Generated by UPID CLI Onboarding\n\n")
        for key, value in config.items():
            f.write(f"export {key}={value}\n")
    
    # Make executable
    script_file.chmod(0o755)
    
    console.print(f"[green]✅ Configuration saved to {script_file}[/green]")
    console.print(f"[yellow]To use: source {script_file}[/yellow]")

def save_to_config_file(config):
    """Save configuration to UPID config file"""
    
    try:
        upid_config = Config()
        
        # Save auth configuration
        for key, value in config.items():
            if key.startswith('UPID_AUTH_'):
                config_key = key.replace('UPID_AUTH_', '').lower()
                upid_config.set(f'auth_{config_key}', value)
        
        console.print("[green]✅ Configuration saved to UPID config file[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to save to config file: {e}[/red]")

def show_manual_instructions(config):
    """Show manual instructions for setting environment variables"""
    
    console.print("\n[bold blue]📝 Manual Configuration Instructions[/bold blue]\n")
    
    console.print("[yellow]Set these environment variables in your shell:[/yellow]")
    for key, value in config.items():
        console.print(f"export {key}={value}")
    
    console.print(f"\n[yellow]Or add them to your shell profile (~/.bashrc, ~/.zshrc, etc.)[/yellow]")

def show_success_message(config_result):
    """Show success message after onboarding"""
    
    console.print("\n" + "="*60)
    console.print("[bold green]🎉 Onboarding Complete![/bold green]")
    console.print("="*60)
    
    console.print(f"\n[green]✅ Authentication method: {config_result['method'].upper()}[/green]")
    
    if config_result.get('user'):
        console.print(f"[green]✅ User: {config_result['user']}[/green]")
    
    if config_result.get('context'):
        console.print(f"[green]✅ Context: {config_result['context']}[/green]")
    
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("• Run 'upid cluster list' to see your clusters")
    console.print("• Run 'upid analyze <cluster>' to analyze resources")
    console.print("• Run 'upid optimize <cluster>' to optimize resources")
    console.print("• Run 'upid onboarding status' to check configuration")
    
    console.print("\n[cyan]Need help?[/cyan]")
    console.print("• Run 'upid onboarding onboard --force' to reconfigure")
    console.print("• Run 'upid configurable-auth help' for manual configuration")
    console.print("• Check documentation at: https://docs.upid.io")

def show_troubleshooting_help(test_result):
    """Show troubleshooting help if authentication failed"""
    
    console.print("\n" + "="*60)
    console.print("[bold red]❌ Authentication Failed[/bold red]")
    console.print("="*60)
    
    console.print(f"\n[red]Error: {test_result.get('error', 'Unknown error')}[/red]")
    console.print(f"[red]Method: {test_result.get('method', 'Unknown')}[/red]")
    
    console.print("\n[yellow]Troubleshooting steps:[/yellow]")
    
    if test_result.get('method') == 'kubectl':
        console.print("• Ensure kubectl is installed and configured")
        console.print("• Check your kubeconfig file")
        console.print("• Test with 'kubectl cluster-info'")
        console.print("• Verify cluster connectivity")
    
    elif test_result.get('method') in ['oidc', 'saml']:
        console.print("• Verify endpoint URL is correct")
        console.print("• Check client ID and secret")
        console.print("• Ensure redirect URI is configured")
        console.print("• Verify scope and audience settings")
    
    elif test_result.get('method') == 'ldap':
        console.print("• Verify endpoint URL is accessible")
        console.print("• Check username and password")
        console.print("• Ensure LDAP server is running")
    
    console.print("\n[cyan]Try again:[/cyan]")
    console.print("• Run 'upid onboarding onboard --force' to reconfigure")
    console.print("• Run 'upid configurable-auth configure' for manual setup")
    console.print("• Check 'upid configurable-auth help' for more options") 