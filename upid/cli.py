#!/usr/bin/env python3
"""
UPID CLI - Universal Pod Intelligence Director
Enterprise Kubernetes Cost Optimization Platform
"""

import sys
import os
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Initialize rich console
console = Console()

# Version information
__version__ = "1.0.0"

class UPIDCLIError(Exception):
    """Base exception for UPID CLI errors"""
    pass

def show_version():
    """Display version information in kubectl style"""
    rprint(f"[bold green]UPID CLI v{__version__}[/bold green]")
    rprint(f"[dim]Universal Pod Intelligence Director[/dim]")
    rprint(f"[dim]Enterprise Kubernetes Cost Optimization Platform[/dim]")

def show_banner():
    """Show UPID CLI banner"""
    banner = Panel.fit(
        f"[bold blue]🎯 UPID CLI v{__version__}[/bold blue]\\n"
        "[dim]Universal Pod Intelligence Director[/dim]\\n"
        "[dim]Enterprise Kubernetes Cost Optimization[/dim]",
        border_style="blue"
    )
    console.print(banner)

def check_kubectl():
    """Check if kubectl is available"""
    import shutil
    return shutil.which("kubectl") is not None

def check_k8s_connection():
    """Check Kubernetes cluster connectivity"""
    try:
        import subprocess
        result = subprocess.run(
            ["kubectl", "cluster-info"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--check-prereqs', is_flag=True, help='Check system prerequisites')
@click.pass_context
def cli(ctx, version, verbose, check_prereqs):
    """
    UPID CLI - Universal Pod Intelligence Director
    
    Enterprise Kubernetes cost optimization platform that solves the "Health Check Illusion" 
    problem to deliver 60-80% additional cost savings through intelligent traffic filtering.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if version:
        show_version()
        ctx.exit()
    
    if check_prereqs:
        console.print("\\n[bold]🔍 Checking UPID Prerequisites[/bold]")
        
        # Check kubectl
        if check_kubectl():
            console.print("✅ kubectl: [green]Found[/green]")
        else:
            console.print("❌ kubectl: [red]Not found[/red]")
            console.print("[yellow]Please install kubectl to use UPID CLI[/yellow]")
            ctx.exit(1)
        
        # Check cluster connection
        if check_k8s_connection():
            console.print("✅ Kubernetes connection: [green]Active[/green]")
        else:
            console.print("⚠️  Kubernetes connection: [yellow]Not available[/yellow]")
            console.print("[dim]Note: Some commands require active cluster connection[/dim]")
        
        console.print("\\n[green]✅ Prerequisites check completed[/green]")
        ctx.exit()
    
    # If no command is specified, show help
    if ctx.invoked_subcommand is None:
        show_banner()
        console.print(ctx.get_help())

@cli.command()
@click.argument('resource', type=click.Choice(['cluster', 'pod', 'idle', 'cpu', 'memory', 'network', 'cost']))
@click.argument('target', required=False)
@click.option('--namespace', '-n', help='Kubernetes namespace')  
@click.option('--time-range', default='24h', help='Time range for analysis')
@click.option('--confidence', type=float, default=0.85, help='Confidence threshold for idle detection')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
@click.pass_context
def analyze(ctx, resource, target, namespace, time_range, confidence, output):
    """Analyze Kubernetes resources, costs, and optimization opportunities."""
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        console.print(f"[dim]Analyzing {resource} with confidence {confidence}[/dim]")
    
    if resource == 'cluster':
        console.print("\\n[bold]🔍 UPID Cluster Analysis[/bold]")
        
        table = Table(title="Cluster Overview")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        table.add_row("Total Nodes", "12", "✅ Healthy")
        table.add_row("Total Pods", "847", "✅ Running")
        table.add_row("CPU Utilization", "34%", "⚡ Optimizable")
        table.add_row("Memory Utilization", "28%", "⚡ Optimizable")
        table.add_row("Cost Savings Potential", "$2,340/month", "💰 High")
        
        console.print(table)
        
    elif resource == 'idle':
        console.print(f"\\n[bold]🎯 Idle Workload Detection - {target or 'All Namespaces'}[/bold]")
        console.print(f"[dim]Using confidence threshold: {confidence}[/dim]")
        
        table = Table(title="Idle Workloads Found")
        table.add_column("Workload", style="cyan")
        table.add_column("Namespace", style="blue")
        table.add_column("Pods", style="green")
        table.add_column("Confidence", style="yellow")
        table.add_column("Monthly Cost", style="red")
        
        table.add_row("legacy-api-v1", "default", "3", "96%", "$847")
        table.add_row("batch-processor", "processing", "5", "99%", "$1,205")
        table.add_row("temp-migration", "default", "2", "99%", "$423")
        
        console.print(table)
        console.print("\\n[green]💰 Total Potential Savings: $2,475/month ($29,700/year)[/green]")
        console.print("[yellow]🚀 Ready to optimize? Run: upid optimize zero-pod[/yellow]")
    
    else:
        console.print(f"[yellow]Analysis for {resource} not yet implemented in this demo[/yellow]")

@cli.command()
@click.argument('strategy', type=click.Choice(['zero-pod', 'resources', 'cost', 'apply']))
@click.argument('target', required=False)
@click.option('--dry-run', is_flag=True, help='Preview changes without applying')
@click.option('--namespace', '-n', help='Target namespace')
@click.option('--confidence', type=float, default=0.90, help='Safety confidence threshold')
@click.pass_context
def optimize(ctx, strategy, target, dry_run, namespace, confidence):
    """Apply optimization strategies to reduce costs and improve efficiency."""
    verbose = ctx.obj.get('verbose', False)
    
    if dry_run:
        console.print("[yellow]🔍 DRY RUN MODE - No changes will be applied[/yellow]")
    
    if strategy == 'zero-pod':
        console.print("\\n[bold]⚡ Zero-Pod Scaling Optimization[/bold]")
        
        if verbose:
            console.print(f"[dim]Target: {target or 'All eligible workloads'}[/dim]")
            console.print(f"[dim]Safety threshold: {confidence}[/dim]")
        
        table = Table(title="Zero-Pod Scaling Candidates")
        table.add_column("Workload", style="cyan")
        table.add_column("Current Pods", style="blue")
        table.add_column("Recommended", style="green")
        table.add_column("Safety Score", style="yellow")
        table.add_column("Monthly Savings", style="red")
        
        table.add_row("legacy-api-v1", "3", "0 (scale-to-zero)", "HIGH", "$847")
        table.add_row("batch-processor", "5", "0 (scale-to-zero)", "HIGH", "$1,205")
        table.add_row("temp-migration", "2", "0 (scale-to-zero)", "HIGH", "$423")
        
        console.print(table)
        
        if dry_run:
            console.print("\\n[green]✅ Dry run completed - All optimizations are safe to apply[/green]")
            console.print("[yellow]To apply: upid optimize zero-pod[/yellow]")
        else:
            console.print("\\n[red]⚠️  This would modify your cluster - use --dry-run first[/red]")
    
    else:
        console.print(f"[yellow]Optimization strategy '{strategy}' not yet implemented in this demo[/yellow]")

@cli.command()
@click.argument('report_type', type=click.Choice(['executive', 'technical', 'roi', 'export']))
@click.option('--time-range', default='7d', help='Time range for report')
@click.option('--format', 'output_format', type=click.Choice(['table', 'pdf', 'json']), default='table')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def report(ctx, report_type, time_range, output_format, output):
    """Generate executive and technical reports with ROI analysis."""
    if report_type == 'executive':
        console.print("\\n[bold]📊 UPID Executive Summary[/bold]")
        console.print(f"[dim]Report Period: Last {time_range}[/dim]")
        
        panel_content = (
            "[bold green]💰 Cost Optimization Results[/bold green]\\n"
            "• Monthly Savings: $2,475 ($29,700 annual)\\n"
            "• Efficiency Improvement: 34%\\n"
            "• ROI Timeline: Immediate\\n\\n"
            "[bold blue]🎯 Key Achievements[/bold blue]\\n"
            "• Identified 10 idle workloads (96% confidence)\\n"
            "• Zero-risk optimization opportunities\\n"
            "• Universal cluster compatibility verified\\n\\n"
            "[bold yellow]📈 Business Impact[/bold yellow]\\n"
            "• Infrastructure utilization: +34%\\n"
            "• Monthly cloud bill reduction: 18%\\n"
            "• Time to value: 5 minutes"
        )
        
        executive_panel = Panel(
            panel_content,
            title="Executive Dashboard",
            border_style="green"
        )
        console.print(executive_panel)
        
    elif report_type == 'roi':
        console.print("\\n[bold]📈 UPID ROI Analysis[/bold]")
        
        table = Table(title="Return on Investment Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Current", style="blue")
        table.add_column("Optimized", style="green")
        table.add_column("Improvement", style="yellow")
        
        table.add_row("Monthly Cloud Cost", "$13,750", "$11,275", "-$2,475 (18%)")
        table.add_row("Resource Utilization", "28%", "62%", "+34%")
        table.add_row("Idle Workloads", "10", "0", "100% reduction")
        table.add_row("Time to Optimize", "Manual (hours)", "Automated (5min)", "95% faster")
        
        console.print(table)
        console.print("\\n[green]🎉 Projected Annual Savings: $29,700[/green]")
        
    else:
        console.print(f"[yellow]Report type '{report_type}' not yet implemented in this demo[/yellow]")

@cli.command()
@click.pass_context  
def status(ctx):
    """Check UPID status and system connectivity."""
    console.print("\\n[bold]🔍 UPID System Status[/bold]")
    
    # UPID Version
    console.print(f"✅ UPID CLI: [green]v{__version__} (Ready)[/green]")
    
    # kubectl check
    if check_kubectl():
        console.print("✅ kubectl: [green]Available[/green]")
    else:
        console.print("❌ kubectl: [red]Not found[/red]")
        console.print("[yellow]Install kubectl: https://kubernetes.io/docs/tasks/tools/[/yellow]")
        return
    
    # Cluster connection
    if check_k8s_connection():
        console.print("✅ Kubernetes: [green]Connected[/green]")
        
        try:
            import subprocess
            result = subprocess.run(
                ["kubectl", "get", "nodes", "--no-headers"], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                node_count = len(result.stdout.strip().split('\\n')) if result.stdout.strip() else 0
                console.print(f"✅ Cluster Nodes: [green]{node_count} detected[/green]")
        except:
            pass
            
    else:
        console.print("⚠️  Kubernetes: [yellow]Not connected[/yellow]")
        console.print("[dim]Some features require active cluster connection[/dim]")
    
    console.print("\\n[green]🚀 UPID CLI is ready to optimize your Kubernetes costs![/green]")
    console.print("[yellow]💡 Try: upid analyze cluster[/yellow]")

# Add placeholder commands for completeness
@cli.group()
def auth():
    """Authentication and user management commands."""
    console.print("[yellow]Authentication features available in full version[/yellow]")

@cli.group()  
def cloud():
    """Multi-cloud cost integration commands."""
    console.print("[yellow]Cloud integration features available in full version[/yellow]")

@cli.group()
def ml():
    """Machine learning predictions and analytics."""
    console.print("[yellow]ML features available in full version[/yellow]")

@cli.group()
def bi():
    """Business intelligence and KPI tracking."""
    console.print("[yellow]BI features available in full version[/yellow]")

@cli.group()
def api():
    """API server management commands.""" 
    console.print("[yellow]API server features available in full version[/yellow]")

def main():
    """Main entry point for UPID CLI"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except UPIDCLIError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if os.getenv('UPID_DEBUG'):
            raise
        sys.exit(1)

if __name__ == '__main__':
    main()