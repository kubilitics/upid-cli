"""
UPID Billing CLI Commands
Provides real cloud billing analytics and cost comparison
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from upid.billing import CloudBillingIntegrator

console = Console()

@click.group()
@click.pass_context
def billing(ctx):
    """Cloud billing analytics and cost comparison"""
    if 'billing_integrator' not in ctx.obj:
        ctx.obj['billing_integrator'] = CloudBillingIntegrator()

@billing.command()
@click.pass_context
def clusters(ctx):
    """List all clusters and their providers"""
    integrator = ctx.obj['billing_integrator']
    clusters = integrator.get_all_clusters()
    table = Table(title="Kubernetes Clusters by Provider")
    table.add_column("Provider", style="cyan")
    table.add_column("Clusters", style="green")
    for provider, clist in clusters.items():
        table.add_row(provider, ", ".join(clist) if clist else "None")
    console.print(table)

@billing.command()
@click.option('--days', default=7, help='Number of days for cost summary')
@click.pass_context
def summary(ctx, days):
    """Show unified cost summary across all providers"""
    integrator = ctx.obj['billing_integrator']
    start_date, end_date = integrator.get_default_dates(days)
    summary = integrator.get_unified_cost_summary(start_date, end_date)
    table = Table(title=f"Unified Cost Summary ({start_date} to {end_date})")
    table.add_column("Provider", style="cyan")
    table.add_column("Cost (USD)", style="green")
    for provider, cost in summary.provider_breakdown.items():
        table.add_row(provider, f"${cost:.2f}")
    table.add_row("[bold]Total[/bold]", f"[bold]${summary.total_cost:.2f}[/bold]")
    console.print(table)

@billing.command()
@click.option('--days', default=7, help='Number of days for comparison')
@click.pass_context
def compare(ctx, days):
    """Compare costs across providers and show recommendations"""
    integrator = ctx.obj['billing_integrator']
    start_date, end_date = integrator.get_default_dates(days)
    comparison = integrator.compare_provider_costs(start_date, end_date)
    table = Table(title=f"Provider Cost Comparison ({start_date} to {end_date})")
    table.add_column("Provider", style="cyan")
    table.add_column("Cost (USD)", style="green")
    for provider, cost in comparison['provider_comparison'].items():
        table.add_row(provider, f"${cost:.2f}")
    table.add_row("[bold]Total[/bold]", f"[bold]${comparison['total_cost']:.2f}[/bold]")
    console.print(table)
    if comparison['recommendations']:
        for rec in comparison['recommendations']:
            console.print(Panel(f"[yellow]{rec['message']}[/yellow]", title="Recommendation"))
    else:
        console.print("[green]No recommendations. Costs are balanced across providers.[/green]") 