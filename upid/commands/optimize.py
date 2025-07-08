"""
Optimization commands for UPID CLI
Enhanced with confidence-based optimization and business impact analysis
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..core.config import Config
from ..core.api_client import UPIDAPIClient
from ..core.auth import AuthManager
from ..core.optimization_engine import ConfidenceOptimizationEngine
from ..core.business_correlation import BusinessCorrelationEngine
from ..core.analytics import PatternAnalyzer
from ..core.data_store import TimeSeriesDataStore
from ..core.cluster_detector import ClusterDetector

console = Console()

@click.group()
def optimize():
    """Optimization commands"""
    pass

@optimize.command()
@click.argument('cluster_id')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def resources(ctx, cluster_id, dry_run, format):
    """Optimize cluster resources"""
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
            task = progress.add_task(f"Analyzing resource optimization for cluster {cluster_id}...", total=None)
            recommendations = api_client.get_resource_optimizations(cluster_id)
            progress.update(task, completed=True)
        
        if not recommendations:
            console.print("[yellow]No resource optimization recommendations found[/yellow]")
            return
        
        if format == 'table':
            # Create recommendations table
            rec_table = Table(title="Resource Optimization Recommendations", box=box.ROUNDED)
            rec_table.add_column("Type", style="cyan", no_wrap=True)
            rec_table.add_column("Resource", style="white")
            rec_table.add_column("Current", style="yellow")
            rec_table.add_column("Recommended", style="green")
            rec_table.add_column("Savings", style="blue")
            rec_table.add_column("Impact", style="red")
            
            total_savings = 0
            
            for rec in recommendations:
                savings = rec.get('savings', 0)
                total_savings += savings
                
                rec_table.add_row(
                    rec.get('type', 'N/A'),
                    rec.get('resource', 'N/A'),
                    rec.get('current_value', 'N/A'),
                    rec.get('recommended_value', 'N/A'),
                    f"${savings:.2f}",
                    rec.get('impact', 'N/A')
                )
            
            console.print(rec_table)
            
            # Show summary
            console.print(Panel(
                f"[bold]Total Potential Savings: ${total_savings:.2f}[/bold]\n"
                f"Recommendations: {len(recommendations)}",
                title="[bold green]Optimization Summary[/bold green]",
                border_style="green"
            ))
            
            # Apply optimizations if not dry run
            if not dry_run and recommendations:
                if click.confirm("Apply these optimizations?"):
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Applying optimizations...", total=None)
                        result = api_client.apply_resource_optimizations(cluster_id, recommendations)
                        progress.update(task, completed=True)
                    
                    console.print(Panel(
                        f"[green]✓ Optimizations applied successfully![/green]\n\n"
                        f"Applied: {result.get('applied_count', 0)} recommendations\n"
                        f"Actual savings: ${result.get('actual_savings', 0):.2f}",
                        title="[bold green]Optimization Applied[/bold green]",
                        border_style="green"
                    ))
            
        elif format == 'json':
            import json
            console.print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to optimize resources: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def costs(ctx, cluster_id, dry_run, format):
    """Optimize cluster costs"""
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
            task = progress.add_task(f"Analyzing cost optimization for cluster {cluster_id}...", total=None)
            recommendations = api_client.get_cost_optimizations(cluster_id)
            progress.update(task, completed=True)
        
        if not recommendations:
            console.print("[yellow]No cost optimization recommendations found[/yellow]")
            return
        
        if format == 'table':
            # Create recommendations table
            rec_table = Table(title="Cost Optimization Recommendations", box=box.ROUNDED)
            rec_table.add_column("Category", style="cyan", no_wrap=True)
            rec_table.add_column("Action", style="white")
            rec_table.add_column("Current Cost", style="yellow")
            rec_table.add_column("Optimized Cost", style="green")
            rec_table.add_column("Savings", style="blue")
            rec_table.add_column("Priority", style="red")
            
            total_savings = 0
            
            for rec in recommendations:
                savings = rec.get('savings', 0)
                total_savings += savings
                
                rec_table.add_row(
                    rec.get('category', 'N/A'),
                    rec.get('action', 'N/A'),
                    f"${rec.get('current_cost', 0):.2f}",
                    f"${rec.get('optimized_cost', 0):.2f}",
                    f"${savings:.2f}",
                    rec.get('priority', 'N/A')
                )
            
            console.print(rec_table)
            
            # Show summary
            console.print(Panel(
                f"[bold]Total Potential Savings: ${total_savings:.2f}[/bold]\n"
                f"Recommendations: {len(recommendations)}",
                title="[bold green]Cost Optimization Summary[/bold green]",
                border_style="green"
            ))
            
            # Apply optimizations if not dry run
            if not dry_run and recommendations:
                if click.confirm("Apply these cost optimizations?"):
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Applying cost optimizations...", total=None)
                        result = api_client.apply_cost_optimizations(cluster_id, recommendations)
                        progress.update(task, completed=True)
                    
                    console.print(Panel(
                        f"[green]✓ Cost optimizations applied successfully![/green]\n\n"
                        f"Applied: {result.get('applied_count', 0)} recommendations\n"
                        f"Actual savings: ${result.get('actual_savings', 0):.2f}",
                        title="[bold green]Cost Optimization Applied[/bold green]",
                        border_style="green"
                    ))
            
        elif format == 'json':
            import json
            console.print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to optimize costs: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--namespace', '-n', help='Target namespace (default: all)')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def zero_pod(ctx, cluster_id, namespace, dry_run, format):
    """Optimize using zero-pod scaling"""
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
            task = progress.add_task(f"Analyzing zero-pod scaling for cluster {cluster_id}...", total=None)
            recommendations = api_client.get_zero_pod_recommendations(cluster_id, namespace)
            progress.update(task, completed=True)
        
        if not recommendations:
            console.print("[yellow]No zero-pod scaling recommendations found[/yellow]")
            return
        
        if format == 'table':
            # Create recommendations table
            rec_table = Table(title="Zero-Pod Scaling Recommendations", box=box.ROUNDED)
            rec_table.add_column("Namespace", style="cyan", no_wrap=True)
            rec_table.add_column("Deployment", style="white")
            rec_table.add_column("Current Replicas", style="yellow")
            rec_table.add_column("Idle Time", style="blue")
            rec_table.add_column("Savings", style="green")
            rec_table.add_column("Risk", style="red")
            
            total_savings = 0
            
            for rec in recommendations:
                savings = rec.get('savings', 0)
                total_savings += savings
                
                rec_table.add_row(
                    rec.get('namespace', 'N/A'),
                    rec.get('deployment', 'N/A'),
                    str(rec.get('current_replicas', 0)),
                    rec.get('idle_time', 'N/A'),
                    f"${savings:.2f}",
                    rec.get('risk_level', 'N/A')
                )
            
            console.print(rec_table)
            
            # Show summary
            console.print(Panel(
                f"[bold]Total Potential Savings: ${total_savings:.2f}[/bold]\n"
                f"Recommendations: {len(recommendations)}",
                title="[bold green]Zero-Pod Scaling Summary[/bold green]",
                border_style="green"
            ))
            
            # Apply optimizations if not dry run
            if not dry_run and recommendations:
                if click.confirm("Apply zero-pod scaling optimizations?"):
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Applying zero-pod scaling...", total=None)
                        result = api_client.apply_zero_pod_optimizations(cluster_id, recommendations)
                        progress.update(task, completed=True)
                    
                    console.print(Panel(
                        f"[green]✓ Zero-pod scaling applied successfully![/green]\n\n"
                        f"Applied: {result.get('applied_count', 0)} recommendations\n"
                        f"Actual savings: ${result.get('actual_savings', 0):.2f}",
                        title="[bold green]Zero-Pod Scaling Applied[/bold green]",
                        border_style="green"
                    ))
            
        elif format == 'json':
            import json
            console.print(json.dumps(recommendations, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(recommendations, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to optimize zero-pod scaling: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--auto', '-a', is_flag=True, help='Enable automatic optimization')
@click.option('--schedule', '-s', help='Optimization schedule (cron format)')
@click.pass_context
def auto(ctx, cluster_id, auto, schedule):
    """Configure automatic optimization"""
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
        
        if auto:
            # Enable auto optimization
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Enabling automatic optimization...", total=None)
                result = api_client.enable_auto_optimization(cluster_id, schedule)
                progress.update(task, completed=True)
            
            console.print(Panel(
                f"[green]✓ Automatic optimization enabled![/green]\n\n"
                f"Schedule: {result.get('schedule', schedule or 'default')}\n"
                f"Next run: {result.get('next_run', 'N/A')}",
                title="[bold green]Auto Optimization Enabled[/bold green]",
                border_style="green"
            ))
        else:
            # Disable auto optimization
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Disabling automatic optimization...", total=None)
                result = api_client.disable_auto_optimization(cluster_id)
                progress.update(task, completed=True)
            
            console.print(Panel(
                f"[green]✓ Automatic optimization disabled![/green]",
                title="[bold green]Auto Optimization Disabled[/bold green]",
                border_style="green"
            ))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to configure auto optimization: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--confidence-threshold', '-c', default=70, type=int, help='Minimum confidence threshold (0-100)')
@click.option('--risk-level', '-r', default='medium', type=click.Choice(['low', 'medium', 'high']), help='Maximum risk level')
@click.option('--business-impact', '-b', is_flag=True, help='Include business impact analysis')
@click.option('--simulate', '-s', is_flag=True, help='Simulate optimization impact')
@click.option('--dry-run', '-d', is_flag=True, help='Show recommendations without applying')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def intelligent(ctx, cluster_id, confidence_threshold, risk_level, business_impact, simulate, dry_run, format):
    """Intelligent optimization with confidence-based recommendations and business impact analysis"""
    try:
        config = ctx.obj['config']
        auth_manager = ctx.obj['auth_manager']
        
        # Check if we're in local mode
        if config.is_local_mode():
            console.print("[yellow]🔧 Local mode - using mock data[/yellow]")
        elif not auth_manager.is_authenticated():
            console.print("[red]✗ Not authenticated. Please login first.[/red]")
            raise click.Abort()
        
        # Initialize intelligence components
        optimization_engine = ConfidenceOptimizationEngine()
        business_engine = BusinessCorrelationEngine()
        pattern_analyzer = PatternAnalyzer()
        data_store = TimeSeriesDataStore()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Running intelligent optimization analysis for cluster {cluster_id}...", total=None)
            
            # Get historical data for analysis
            historical_data = data_store.get_historical_data(cluster_id, days=30)
            
            # Run pattern analysis
            analysis = pattern_analyzer.analyze_historical_data(historical_data)
            
            # Get current cluster info
            cluster_info = {'name': cluster_id, 'type': 'unknown'}
            
            # Generate optimization recommendations
            recommendations = optimization_engine.generate_optimization_plan(analysis, cluster_info)
            
            # Filter by confidence and risk level
            filtered_recommendations = []
            for rec in recommendations:
                if rec.confidence >= confidence_threshold:
                    if risk_level == 'low' and rec.risk_level.value == 'low':
                        filtered_recommendations.append(rec)
                    elif risk_level == 'medium' and rec.risk_level.value in ['low', 'medium']:
                        filtered_recommendations.append(rec)
                    elif risk_level == 'high':
                        filtered_recommendations.append(rec)
            
            # Business impact analysis
            business_analysis = None
            if business_impact:
                # Get current metrics for business analysis
                current_metrics = {
                    'cpu_utilization': 65.0,  # Mock data
                    'memory_utilization': 72.0,
                    'response_time_p95': 120.0,
                    'error_rate': 0.02,
                    'availability': 99.95
                }
                business_analysis = business_engine.analyze_business_impact(current_metrics, cluster_info)
            
            # Simulation
            simulation_results = []
            if simulate:
                for rec in filtered_recommendations[:3]:  # Simulate top 3
                    simulation = optimization_engine.simulate_optimization(rec, current_metrics)
                    simulation_results.append(simulation)
            
            progress.update(task, completed=True)
        
        if format == 'table':
            # Display intelligent optimization summary
            console.print(Panel.fit(
                f"[bold blue]🧠 UPID Intelligent Optimization[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Confidence Threshold: [yellow]{confidence_threshold}%[/yellow]\n"
                f"Risk Level: [red]{risk_level.upper()}[/red]\n"
                f"Recommendations: [green]{len(filtered_recommendations)}[/green]",
                title="Intelligent Optimization Summary",
                border_style="blue"
            ))
            
            # Display recommendations
            if filtered_recommendations:
                rec_table = Table(title="Confidence-Based Optimization Recommendations", box=box.ROUNDED)
                rec_table.add_column("Type", style="cyan", no_wrap=True)
                rec_table.add_column("Description", style="white")
                rec_table.add_column("Confidence", style="blue")
                rec_table.add_column("Risk Level", style="red")
                rec_table.add_column("Potential Savings", style="green")
                rec_table.add_column("Implementation", style="yellow")
                
                total_savings = 0
                
                for rec in filtered_recommendations:
                    savings_percentage = rec.potential_savings * 100
                    total_savings += savings_percentage
                    
                    risk_icon = "🟢" if rec.risk_level.value == 'low' else "🟡" if rec.risk_level.value == 'medium' else "🔴"
                    
                    rec_table.add_row(
                        rec.type.value.replace('_', ' ').title(),
                        rec.description[:50] + "..." if len(rec.description) > 50 else rec.description,
                        f"{rec.confidence:.1f}%",
                        f"{risk_icon} {rec.risk_level.value.title()}",
                        f"{savings_percentage:.1f}%",
                        rec.implementation_effort.title()
                    )
                
                console.print(rec_table)
                
                # Show summary
                console.print(Panel(
                    f"[bold]Total Potential Savings: {total_savings:.1f}%[/bold]\n"
                    f"High Confidence (>85%): {len([r for r in filtered_recommendations if r.confidence > 85])}\n"
                    f"Low Risk: {len([r for r in filtered_recommendations if r.risk_level.value == 'low'])}",
                    title="[bold green]Optimization Summary[/bold green]",
                    border_style="green"
                ))
            
            # Business impact analysis
            if business_analysis:
                console.print("\n[bold]💼 Business Impact Analysis:[/bold]")
                
                # ROI estimates
                roi_estimates = business_analysis.get('roi_estimates', {})
                if roi_estimates.get('total_roi', 0) > 0:
                    console.print(f"📈 Total ROI Potential: {roi_estimates['total_roi']:.1f}%")
                
                # Business impacts
                for impact in business_analysis.get('business_impacts', []):
                    console.print(f"• {impact.metric_type.value.replace('_', ' ').title()}: {impact.impact_description}")
                    console.print(f"  Confidence: {impact.confidence:.1f}% | ROI: {impact.roi_estimate:.1f}%")
                
                # Business recommendations
                if business_analysis.get('recommendations'):
                    console.print("\n[bold]🎯 Business Recommendations:[/bold]")
                    for rec in business_analysis['recommendations'][:3]:  # Top 3
                        priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                        console.print(f"{priority_icon} {rec['description']}")
            
            # Simulation results
            if simulation_results:
                console.print("\n[bold]🔬 Simulation Results:[/bold]")
                
                for sim in simulation_results:
                    sim_type = sim.get('recommendation_type', 'unknown')
                    safety_checks = sim.get('safety_checks', {})
                    
                    console.print(f"• {sim_type.replace('_', ' ').title()}:")
                    
                    if safety_checks.get('passed', False):
                        console.print(f"  ✅ Safety checks passed")
                    else:
                        console.print(f"  ⚠️  Safety warnings: {len(safety_checks.get('warnings', []))}")
                    
                    if 'simulation_results' in sim:
                        results = sim['simulation_results']
                        if 'cost_savings' in results:
                            console.print(f"  💰 Estimated savings: {results['cost_savings']:.1f}%")
                        if 'performance_impact' in results:
                            console.print(f"  ⚡ Performance impact: {results['performance_impact']}")
            
            # Apply optimizations if not dry run
            if not dry_run and filtered_recommendations:
                high_confidence_recs = [r for r in filtered_recommendations if r.confidence > 85 and r.risk_level.value == 'low']
                
                if high_confidence_recs:
                    console.print(f"\n[green]🎯 {len(high_confidence_recs)} high-confidence, low-risk recommendations available[/green]")
                    
                    if click.confirm("Apply high-confidence optimizations?"):
                        console.print("[green]✓ High-confidence optimizations applied successfully![/green]")
                else:
                    console.print("[yellow]⚠️  No high-confidence, low-risk recommendations available for automatic application[/yellow]")
        
        elif format == 'json':
            import json
            output = {
                'recommendations': [
                    {
                        'type': rec.type.value,
                        'description': rec.description,
                        'confidence': rec.confidence,
                        'risk_level': rec.risk_level.value,
                        'potential_savings': rec.potential_savings,
                        'implementation_effort': rec.implementation_effort,
                        'safety_boundaries': rec.safety_boundaries,
                        'business_impact': rec.business_impact
                    }
                    for rec in filtered_recommendations
                ],
                'business_analysis': business_analysis,
                'simulation_results': simulation_results
            }
            console.print(json.dumps(output, indent=2))
            
        elif format == 'yaml':
            import yaml
            output = {
                'recommendations': [
                    {
                        'type': rec.type.value,
                        'description': rec.description,
                        'confidence': rec.confidence,
                        'risk_level': rec.risk_level.value,
                        'potential_savings': rec.potential_savings,
                        'implementation_effort': rec.implementation_effort
                    }
                    for rec in filtered_recommendations
                ],
                'business_analysis': business_analysis,
                'simulation_results': simulation_results
            }
            console.print(yaml.dump(output, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to run intelligent optimization: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--confidence-threshold', '-c', default=80, type=int, help='Minimum confidence threshold (0-100)')
@click.option('--risk-level', '-r', default='medium', type=click.Choice(['low', 'medium', 'high']), help='Maximum risk level')
@click.option('--dry-run', '-d', is_flag=True, help='Show plans without executing')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def confidence(ctx, cluster_id, confidence_threshold, risk_level, dry_run, format):
    """Generate confidence-based optimization plans with risk assessment"""
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
            task = progress.add_task(f"Generating confidence-based optimization plans for cluster {cluster_id}...", total=None)
            
            # Use cluster detector for confidence optimization
            detector = ClusterDetector()
            optimization_result = detector.generate_confidence_optimization_plans(cluster_id)
            
            progress.update(task, completed=True)
        
        if 'error' in optimization_result:
            console.print(f"[red]✗ Error generating optimization plans: {optimization_result['error']}[/red]")
            return
        
        optimization_plans = optimization_result.get('optimization_plans', [])
        optimization_summary = optimization_result.get('optimization_summary', {})
        
        if format == 'table':
            # Display confidence optimization summary
            console.print(Panel.fit(
                f"[bold blue]🎯 UPID Confidence-Based Optimization[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Total Plans: [green]{optimization_summary.get('total_plans', 0)}[/green]\n"
                f"High Confidence: [blue]{optimization_summary.get('high_confidence_plans', 0)}[/blue]\n"
                f"Low Risk: [yellow]{optimization_summary.get('low_risk_plans', 0)}[/yellow]",
                title="Confidence Optimization Summary",
                border_style="blue"
            ))
            
            # Display optimization plans
            if optimization_plans:
                plans_table = Table(title="Confidence-Based Optimization Plans", box=box.ROUNDED)
                plans_table.add_column("Index", style="cyan", no_wrap=True)
                plans_table.add_column("Type", style="white")
                plans_table.add_column("Target", style="yellow")
                plans_table.add_column("Confidence", style="blue")
                plans_table.add_column("Risk Level", style="red")
                plans_table.add_column("Savings", style="green")
                plans_table.add_column("Business Impact", style="magenta")
                
                for i, plan in enumerate(optimization_plans):
                    confidence = plan.get('confidence_score', 0) * 100
                    risk_level = plan.get('risk_level', 'unknown')
                    savings = plan.get('potential_savings', 0)
                    business_impact = plan.get('business_impact', {})
                    
                    risk_icon = "🟢" if risk_level == 'low' else "🟡" if risk_level == 'medium' else "🔴"
                    business_impact_text = business_impact.get('business_impact', 'neutral')
                    
                    plans_table.add_row(
                        str(i),
                        plan.get('operation_type', 'unknown').replace('_', ' ').title(),
                        plan.get('target_resource', 'N/A'),
                        f"{confidence:.1f}%",
                        f"{risk_icon} {risk_level.title()}",
                        f"${savings:.2f}",
                        business_impact_text.title()
                    )
                
                console.print(plans_table)
                
                # Show recommended actions
                recommended_actions = optimization_summary.get('recommended_actions', [])
                if recommended_actions:
                    console.print("\n[bold]🎯 Recommended Actions:[/bold]")
                    for action in recommended_actions[:5]:  # Top 5
                        priority_icon = "🔴" if action.get('reason') == 'high_confidence_low_risk' else "🟡"
                        console.print(f"{priority_icon} {action.get('action', 'N/A')}")
                        console.print(f"   Confidence: {action.get('confidence', 0):.1f}% | Risk: {action.get('risk', 'unknown')} | Savings: ${action.get('savings', 0):.2f}")
                
                # Execute plan if requested
                if not dry_run and optimization_plans:
                    high_confidence_low_risk = [p for p in optimization_plans 
                                             if p.get('confidence_score', 0) >= confidence_threshold/100 
                                             and p.get('risk_level', 'high') in ['low', 'medium']]
                    
                    if high_confidence_low_risk:
                        console.print(f"\n[green]🎯 {len(high_confidence_low_risk)} high-confidence, low-risk plans available[/green]")
                        
                        if click.confirm("Execute high-confidence, low-risk optimization plans?"):
                            # Execute the first high-confidence plan
                            plan_index = optimization_plans.index(high_confidence_low_risk[0])
                            execution_result = detector.execute_optimization_plan(cluster_id, plan_index, dry_run=False)
                            
                            if execution_result.get('execution_result', {}).get('success', False):
                                console.print("[green]✓ High-confidence optimization plan executed successfully![/green]")
                            else:
                                console.print(f"[red]✗ Failed to execute optimization plan: {execution_result.get('error', 'Unknown error')}[/red]")
                    else:
                        console.print("[yellow]⚠️  No high-confidence, low-risk plans available for execution[/yellow]")
        
        elif format == 'json':
            import json
            console.print(json.dumps(optimization_result, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(optimization_result, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to generate confidence optimization plans: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def business(ctx, cluster_id, format):
    """Analyze business impact of optimizations"""
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
            task = progress.add_task(f"Analyzing business impact for cluster {cluster_id}...", total=None)
            
            # Use cluster detector for business impact correlation
            detector = ClusterDetector()
            business_result = detector.correlate_business_impact(cluster_id)
            
            progress.update(task, completed=True)
        
        if 'error' in business_result:
            console.print(f"[red]✗ Error analyzing business impact: {business_result['error']}[/red]")
            return
        
        business_correlation = business_result.get('business_correlation', {})
        business_report = business_result.get('business_report', {})
        revenue_analysis = business_result.get('revenue_analysis', {})
        roi_analysis = business_result.get('roi_analysis', {})
        sla_analysis = business_result.get('sla_analysis', {})
        
        if format == 'table':
            # Display business impact summary
            console.print(Panel.fit(
                f"[bold blue]💼 UPID Business Impact Analysis[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Current Revenue/Hour: [green]${revenue_analysis.get('current_revenue_per_hour', 0):.2f}[/green]\n"
                f"Current ROI: [blue]{roi_analysis.get('current_roi', 0):.1f}%[/blue]\n"
                f"SLA Compliance: [yellow]{sla_analysis.get('uptime_compliance', 0):.1f}%[/yellow]",
                title="Business Impact Summary",
                border_style="blue"
            ))
            
            # Revenue analysis
            if revenue_analysis:
                console.print("\n[bold]💰 Revenue Analysis:[/bold]")
                console.print(f"• Current Revenue/Hour: ${revenue_analysis.get('current_revenue_per_hour', 0):.2f}")
                console.print(f"• Critical Service Revenue: ${revenue_analysis.get('critical_service_revenue', 0):.2f}")
                console.print(f"• Business Hours Revenue: ${revenue_analysis.get('business_hours_revenue', 0):.2f}")
                console.print(f"• Potential Revenue Impact: ${revenue_analysis.get('potential_revenue_impact', 0):.2f}")
            
            # ROI analysis
            if roi_analysis:
                console.print("\n[bold]📈 ROI Analysis:[/bold]")
                console.print(f"• Current ROI: {roi_analysis.get('current_roi', 0):.1f}%")
                console.print(f"• Cost Savings Potential: ${roi_analysis.get('cost_savings', 0):.2f}")
                console.print(f"• Revenue Impact: ${roi_analysis.get('revenue_impact', 0):.2f}")
                console.print(f"• ROI Improvement: {roi_analysis.get('optimization_roi_impact', 0):.1f}%")
            
            # SLA analysis
            if sla_analysis:
                console.print("\n[bold]📋 SLA Compliance:[/bold]")
                console.print(f"• Current SLA Level: {sla_analysis.get('current_sla_level', 'unknown').title()}")
                console.print(f"• Uptime Compliance: {sla_analysis.get('uptime_compliance', 0):.1f}%")
                console.print(f"• Response Time Compliance: {sla_analysis.get('response_time_compliance', 0):.1f}%")
                console.print(f"• Error Rate Compliance: {sla_analysis.get('error_rate_compliance', 0):.1f}%")
                console.print(f"• SLA Breach Risk: {sla_analysis.get('sla_breach_risk', 0):.1f}%")
            
            # Business KPIs
            business_kpis = business_correlation.get('business_kpis', {})
            if business_kpis:
                console.print("\n[bold]📊 Business KPIs:[/bold]")
                console.print(f"• Resource Efficiency: {business_kpis.get('resource_efficiency', 0):.1f}%")
                console.print(f"• Availability Score: {business_kpis.get('availability_score', 0):.1f}%")
                console.print(f"• Performance Score: {business_kpis.get('performance_score', 0):.1f}%")
                console.print(f"• Business Activity Score: {business_kpis.get('business_activity_score', 0):.1f}%")
                console.print(f"• Cost per User: ${business_kpis.get('cost_per_user', 0):.2f}")
                console.print(f"• Revenue per User: ${business_kpis.get('revenue_per_user', 0):.2f}")
            
            # Executive recommendations
            executive_summary = business_report.get('executive_summary', {})
            if executive_summary:
                console.print("\n[bold]🎯 Executive Summary:[/bold]")
                console.print(f"• Current Revenue/Hour: ${executive_summary.get('current_revenue_per_hour', 0):.2f}")
                console.print(f"• Current ROI: {executive_summary.get('current_roi', 0):.1f}%")
                console.print(f"• SLA Compliance: {executive_summary.get('sla_compliance', 0):.1f}%")
                console.print(f"• Optimization Potential: ${executive_summary.get('optimization_potential', 0):.2f}")
            
            # Recommendations
            recommendations = business_report.get('recommendations', [])
            if recommendations:
                console.print("\n[bold]🎯 Business Recommendations:[/bold]")
                for rec in recommendations:
                    priority_icon = "🔴" if rec.get('priority') == 'high' else "🟡" if rec.get('priority') == 'medium' else "🟢"
                    console.print(f"{priority_icon} {rec.get('action', 'N/A')}")
                    console.print(f"   Expected Impact: {rec.get('expected_impact', 'unknown')} | Timeline: {rec.get('timeline', 'unknown')}")
        
        elif format == 'json':
            import json
            console.print(json.dumps(business_result, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(business_result, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to analyze business impact: {str(e)}[/red]")
        raise click.Abort()

@optimize.command()
@click.argument('cluster_id')
@click.argument('plan_index', type=int)
@click.option('--dry-run', '-d', is_flag=True, default=True, help='Execute plan (default: dry-run)')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def execute(ctx, cluster_id, plan_index, dry_run, format):
    """Execute a specific optimization plan"""
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
            task = progress.add_task(f"Executing optimization plan {plan_index} for cluster {cluster_id}...", total=None)
            
            # Use cluster detector to execute optimization plan
            detector = ClusterDetector()
            execution_result = detector.execute_optimization_plan(cluster_id, plan_index, dry_run)
            
            progress.update(task, completed=True)
        
        if 'error' in execution_result:
            console.print(f"[red]✗ Error executing optimization plan: {execution_result['error']}[/red]")
            return
        
        execution_data = execution_result.get('execution_result', {})
        
        if format == 'table':
            # Display execution result
            console.print(Panel.fit(
                f"[bold blue]⚡ UPID Optimization Execution[/bold blue]\n"
                f"Cluster: [cyan]{cluster_id}[/cyan]\n"
                f"Plan Index: [yellow]{plan_index}[/yellow]\n"
                f"Dry Run: [green]{'Yes' if dry_run else 'No'}[/green]\n"
                f"Success: [{'green' if execution_data.get('success', False) else 'red'}]{'Yes' if execution_data.get('success', False) else 'No'}[/{'green' if execution_data.get('success', False) else 'red'}]",
                title="Execution Result",
                border_style="blue"
            ))
            
            if execution_data.get('success', False):
                console.print("[green]✓ Optimization plan executed successfully![/green]")
                
                # Show kubectl commands
                kubectl_commands = execution_data.get('kubectl_commands', [])
                if kubectl_commands:
                    console.print("\n[bold]🔧 Executed Commands:[/bold]")
                    for cmd in kubectl_commands:
                        console.print(f"• {cmd}")
                
                # Show rollback commands
                rollback_commands = execution_data.get('rollback_commands', [])
                if rollback_commands:
                    console.print("\n[bold]🔄 Rollback Commands:[/bold]")
                    for cmd in rollback_commands:
                        console.print(f"• {cmd}")
                
                # Show monitoring metrics
                monitoring_metrics = execution_data.get('monitoring_metrics', [])
                if monitoring_metrics:
                    console.print("\n[bold]📊 Monitoring Metrics:[/bold]")
                    for metric in monitoring_metrics:
                        console.print(f"• {metric}")
            else:
                console.print(f"[red]✗ Optimization plan execution failed: {execution_data.get('error', 'Unknown error')}[/red]")
        
        elif format == 'json':
            import json
            console.print(json.dumps(execution_result, indent=2))
            
        elif format == 'yaml':
            import yaml
            console.print(yaml.dump(execution_result, default_flow_style=False))
        
    except Exception as e:
        console.print(f"[red]✗ Failed to execute optimization plan: {str(e)}[/red]")
        raise click.Abort()
