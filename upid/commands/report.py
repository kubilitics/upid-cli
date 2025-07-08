"""
Reporting commands for UPID CLI
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from ..core.config import Config
from ..core.api_client import UPIDAPIClient
from ..core.auth import AuthManager

console = Console()

@click.group()
def report():
    """Reporting commands"""
    pass

@report.command()
@click.argument('cluster_id')
@click.option('--period', '-p', default='30d', type=click.Choice(['7d', '30d', '90d']), help='Report period')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml', 'html']), help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def summary(ctx, cluster_id, period, format, output):
    """Generate comprehensive cluster summary report"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating summary report for cluster {cluster_id}...", total=None)
            report_data = api_client.generate_summary_report(cluster_id, period)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create comprehensive report
            console.print(f"\n[bold blue]Cluster Summary Report[/bold blue]")
            console.print(f"Cluster: {report_data.get('cluster_name', cluster_id)}")
            console.print(f"Period: {period}")
            console.print(f"Generated: {report_data.get('generated_at', 'N/A')}")
            console.print()
            
            # Resource Summary
            resource_table = Table(title="Resource Summary", box=box.ROUNDED)
            resource_table.add_column("Resource", style="cyan", no_wrap=True)
            resource_table.add_column("Used", style="yellow")
            resource_table.add_column("Total", style="green")
            resource_table.add_column("Utilization", style="blue")
            resource_table.add_column("Trend", style="white")
            
            resources = report_data.get('resources', {})
            for resource_type, data in resources.items():
                used = data.get('used', 0)
                total = data.get('total', 0)
                util = (used / total * 100) if total > 0 else 0
                trend = data.get('trend', 'N/A')
                
                resource_table.add_row(
                    resource_type.title(),
                    f"{used:.1f}",
                    f"{total:.1f}",
                    f"{util:.1f}%",
                    trend
                )
            
            console.print(resource_table)
            console.print()
            
            # Cost Summary
            cost_table = Table(title="Cost Summary", box=box.ROUNDED)
            cost_table.add_column("Category", style="cyan", no_wrap=True)
            cost_table.add_column("Current", style="yellow")
            cost_table.add_column("Previous", style="blue")
            cost_table.add_column("Change", style="green")
            cost_table.add_column("Trend", style="white")
            
            costs = report_data.get('costs', {})
            for category, data in costs.items():
                current = data.get('current', 0)
                previous = data.get('previous', 0)
                change = current - previous
                change_pct = (change / previous * 100) if previous > 0 else 0
                trend = data.get('trend', 'N/A')
                
                change_color = "green" if change <= 0 else "red"
                cost_table.add_row(
                    category.title(),
                    f"${current:.2f}",
                    f"${previous:.2f}",
                    f"[{change_color}]{change:+.2f} ({change_pct:+.1f}%)[/{change_color}]",
                    trend
                )
            
            console.print(cost_table)
            console.print()
            
            # Performance Summary
            perf_table = Table(title="Performance Summary", box=box.ROUNDED)
            perf_table.add_column("Metric", style="cyan", no_wrap=True)
            perf_table.add_column("Current", style="yellow")
            perf_table.add_column("Average", style="blue")
            perf_table.add_column("Peak", style="red")
            perf_table.add_column("Status", style="white")
            
            performance = report_data.get('performance', {})
            for metric, data in performance.items():
                current = data.get('current', 0)
                avg = data.get('average', 0)
                peak = data.get('peak', 0)
                status = data.get('status', 'N/A')
                
                perf_table.add_row(
                    metric.title(),
                    f"{current:.1f}",
                    f"{avg:.1f}",
                    f"{peak:.1f}",
                    status
                )
            
            console.print(perf_table)
            console.print()
            
            # Recommendations
            recommendations = report_data.get('recommendations', [])
            if recommendations:
                console.print("[bold]Recommendations:[/bold]")
                for i, rec in enumerate(recommendations, 1):
                    console.print(f"{i}. [yellow]{rec.get('title', 'N/A')}[/yellow]")
                    console.print(f"   {rec.get('description', 'N/A')}")
                    console.print(f"   Impact: [green]{rec.get('impact', 'N/A')}[/green]")
                    console.print(f"   Priority: [red]{rec.get('priority', 'N/A')}[/red]")
                    console.print()
            
        elif format == 'json':
            import json
            output_data = json.dumps(report_data, indent=2)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(output_data)
            
        elif format == 'yaml':
            import yaml
            output_data = yaml.dump(report_data, default_flow_style=False)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(output_data)
            
        elif format == 'html':
            # Generate HTML report
            html_content = generate_html_report(report_data, cluster_id, period)
            if output:
                with open(output, 'w') as f:
                    f.write(html_content)
                console.print(f"[green]HTML report saved to {output}[/green]")
            else:
                console.print("[yellow]HTML output requires --output parameter[/yellow]")
        
    except Exception as e:
        console.print(f"[red]✗ Failed to generate summary report: {str(e)}[/red]")
        raise click.Abort()

@report.command()
@click.argument('cluster_id')
@click.option('--period', '-p', default='30d', type=click.Choice(['7d', '30d', '90d']), help='Report period')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def cost(ctx, cluster_id, period, format, output):
    """Generate detailed cost report"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating cost report for cluster {cluster_id}...", total=None)
            report_data = api_client.generate_cost_report(cluster_id, period)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create detailed cost report
            console.print(f"\n[bold blue]Cost Analysis Report[/bold blue]")
            console.print(f"Cluster: {report_data.get('cluster_name', cluster_id)}")
            console.print(f"Period: {period}")
            console.print(f"Total Cost: ${report_data.get('total_cost', 0):.2f}")
            console.print()
            
            # Cost breakdown by service
            service_table = Table(title="Cost by Service", box=box.ROUNDED)
            service_table.add_column("Service", style="cyan", no_wrap=True)
            service_table.add_column("Cost", style="yellow")
            service_table.add_column("Percentage", style="blue")
            service_table.add_column("Trend", style="green")
            
            services = report_data.get('services', {})
            total_cost = report_data.get('total_cost', 0)
            
            for service, data in services.items():
                cost = data.get('cost', 0)
                pct = (cost / total_cost * 100) if total_cost > 0 else 0
                trend = data.get('trend', 'N/A')
                
                service_table.add_row(
                    service.title(),
                    f"${cost:.2f}",
                    f"{pct:.1f}%",
                    trend
                )
            
            console.print(service_table)
            console.print()
            
            # Cost optimization opportunities
            opportunities = report_data.get('optimization_opportunities', [])
            if opportunities:
                opp_table = Table(title="Optimization Opportunities", box=box.ROUNDED)
                opp_table.add_column("Opportunity", style="cyan", no_wrap=True)
                opp_table.add_column("Current Cost", style="yellow")
                opp_table.add_column("Potential Savings", style="green")
                opp_table.add_column("Implementation", style="blue")
                
                total_savings = 0
                for opp in opportunities:
                    savings = opp.get('savings', 0)
                    total_savings += savings
                    
                    opp_table.add_row(
                        opp.get('title', 'N/A'),
                        f"${opp.get('current_cost', 0):.2f}",
                        f"${savings:.2f}",
                        opp.get('implementation', 'N/A')
                    )
                
                console.print(opp_table)
                console.print(f"\n[bold]Total potential savings: ${total_savings:.2f}[/bold]")
                console.print()
            
        elif format == 'json':
            import json
            output_data = json.dumps(report_data, indent=2)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(output_data)
            
        elif format == 'yaml':
            import yaml
            output_data = yaml.dump(report_data, default_flow_style=False)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(output_data)
        
    except Exception as e:
        console.print(f"[red]✗ Failed to generate cost report: {str(e)}[/red]")
        raise click.Abort()

@report.command()
@click.argument('cluster_id')
@click.option('--period', '-p', default='30d', type=click.Choice(['7d', '30d', '90d']), help='Report period')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def performance(ctx, cluster_id, period, format, output):
    """Generate detailed performance report"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        api_client = ctx.obj['api_client']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Generating performance report for cluster {cluster_id}...", total=None)
            report_data = api_client.generate_performance_report(cluster_id, period)
            progress.update(task, completed=True)
        
        if format == 'table':
            # Create detailed performance report
            console.print(f"\n[bold blue]Performance Analysis Report[/bold blue]")
            console.print(f"Cluster: {report_data.get('cluster_name', cluster_id)}")
            console.print(f"Period: {period}")
            console.print()
            
            # Performance metrics
            metrics_table = Table(title="Performance Metrics", box=box.ROUNDED)
            metrics_table.add_column("Metric", style="cyan", no_wrap=True)
            metrics_table.add_column("Current", style="yellow")
            metrics_table.add_column("Average", style="blue")
            metrics_table.add_column("Peak", style="red")
            metrics_table.add_column("Status", style="white")
            
            metrics = report_data.get('metrics', {})
            for metric, data in metrics.items():
                current = data.get('current', 0)
                avg = data.get('average', 0)
                peak = data.get('peak', 0)
                status = data.get('status', 'N/A')
                
                metrics_table.add_row(
                    metric.title(),
                    f"{current:.1f}",
                    f"{avg:.1f}",
                    f"{peak:.1f}",
                    status
                )
            
            console.print(metrics_table)
            console.print()
            
            # Performance issues
            issues = report_data.get('issues', [])
            if issues:
                issues_table = Table(title="Performance Issues", box=box.ROUNDED)
                issues_table.add_column("Issue", style="cyan", no_wrap=True)
                issues_table.add_column("Severity", style="red")
                issues_table.add_column("Impact", style="yellow")
                issues_table.add_column("Recommendation", style="green")
                
                for issue in issues:
                    issues_table.add_row(
                        issue.get('title', 'N/A'),
                        issue.get('severity', 'N/A'),
                        issue.get('impact', 'N/A'),
                        issue.get('recommendation', 'N/A')
                    )
                
                console.print(issues_table)
                console.print()
            
        elif format == 'json':
            import json
            output_data = json.dumps(report_data, indent=2)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(output_data)
            
        elif format == 'yaml':
            import yaml
            output_data = yaml.dump(report_data, default_flow_style=False)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(output_data)
        
    except Exception as e:
        console.print(f"[red]✗ Failed to generate performance report: {str(e)}[/red]")
        raise click.Abort()

def generate_html_report(report_data, cluster_id, period):
    """Generate HTML report content"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UPID Cluster Report - {cluster_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .metric {{ margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>UPID Cluster Report</h1>
            <p><strong>Cluster:</strong> {report_data.get('cluster_name', cluster_id)}</p>
            <p><strong>Period:</strong> {period}</p>
            <p><strong>Generated:</strong> {report_data.get('generated_at', 'N/A')}</p>
        </div>
        
        <div class="section">
            <h2>Resource Summary</h2>
            <table>
                <tr><th>Resource</th><th>Used</th><th>Total</th><th>Utilization</th></tr>
    """
    
    resources = report_data.get('resources', {})
    for resource_type, data in resources.items():
        used = data.get('used', 0)
        total = data.get('total', 0)
        util = (used / total * 100) if total > 0 else 0
        html_template += f"""
                <tr>
                    <td>{resource_type.title()}</td>
                    <td>{used:.1f}</td>
                    <td>{total:.1f}</td>
                    <td>{util:.1f}%</td>
                </tr>
        """
    
    html_template += """
            </table>
        </div>
        
        <div class="section">
            <h2>Cost Summary</h2>
            <table>
                <tr><th>Category</th><th>Current</th><th>Previous</th><th>Change</th></tr>
    """
    
    costs = report_data.get('costs', {})
    for category, data in costs.items():
        current = data.get('current', 0)
        previous = data.get('previous', 0)
        change = current - previous
        change_pct = (change / previous * 100) if previous > 0 else 0
        html_template += f"""
                <tr>
                    <td>{category.title()}</td>
                    <td>${current:.2f}</td>
                    <td>${previous:.2f}</td>
                    <td>{change:+.2f} ({change_pct:+.1f}%)</td>
                </tr>
        """
    
    html_template += """
            </table>
        </div>
    </body>
    </html>
    """
    
    return html_template
