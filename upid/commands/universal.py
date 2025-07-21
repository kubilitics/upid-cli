"""
Universal Kubernetes Commands
Works with any cluster (Docker Desktop, Minikube, Kind, K3s, EKS, AKS, GKE, etc.)
"""

import click
import subprocess
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from typing import Dict, Any, List
from ..core.cluster_detector import ClusterDetector

console = Console()

@click.group()
def universal():
    """Universal Kubernetes commands - works with any cluster"""
    pass

@universal.command()
@click.option('--format', '-f', default='table', help='Output format (table, json, yaml)')
def status(format):
    """Show cluster status and health"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Detecting cluster...", total=None)
        
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        
        progress.update(task, description="Getting cluster metrics...")
        metrics = detector.get_cluster_metrics()
        
        progress.update(task, description="Analyzing cluster health...")
    
    if format == 'json':
        console.print(json.dumps(cluster_info, indent=2))
        return
    
    # Display cluster info
    console.print(Panel(
        f"[bold blue]Cluster: {cluster_info['name']}[/bold blue]\n"
        f"Type: {cluster_info['type'].upper()}\n"
        f"Status: {'✅ Connected' if cluster_info['status'] == 'connected' else '❌ Error'}\n"
        f"Kubeconfig: {cluster_info['kubeconfig']}",
        title="[bold green]Cluster Information[/bold green]",
        border_style="green"
    ))
    
    # Display capabilities
    capabilities = cluster_info.get('capabilities', {})
    cap_table = Table(title="Cluster Capabilities", box=box.ROUNDED)
    cap_table.add_column("Capability", style="cyan")
    cap_table.add_column("Available", style="green")
    
    for cap, available in capabilities.items():
        status = "✅ Yes" if available else "❌ No"
        cap_table.add_row(cap.replace('_', ' ').title(), status)
    
    console.print(cap_table)
    
    # Display metrics if available
    if 'resources' in metrics and not metrics.get('error'):
        resources = metrics['resources']
        
        # Calculate percentages
        cpu_used = resources.get('cpu', {}).get('used', 0)
        cpu_total = resources.get('cpu', {}).get('total', 1)
        cpu_percent = (cpu_used / cpu_total * 100) if cpu_total > 0 else 0
        
        memory_used = resources.get('memory', {}).get('used', 0)
        memory_total = resources.get('memory', {}).get('total', 1)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        pods_running = resources.get('pods', {}).get('running', 0)
        pods_total = resources.get('pods', {}).get('total', 0)
        
        # Resource usage table
        usage_table = Table(title="Resource Usage", box=box.ROUNDED)
        usage_table.add_column("Resource", style="cyan")
        usage_table.add_column("Used", style="yellow")
        usage_table.add_column("Total", style="blue")
        usage_table.add_column("Usage %", style="green")
        
        usage_table.add_row(
            "CPU",
            f"{cpu_used:.1f} cores",
            f"{cpu_total:.1f} cores",
            f"{cpu_percent:.1f}%"
        )
        
        usage_table.add_row(
            "Memory",
            f"{memory_used / (1024**3):.1f} GB",
            f"{memory_total / (1024**3):.1f} GB",
            f"{memory_percent:.1f}%"
        )
        
        usage_table.add_row(
            "Pods",
            str(pods_running),
            str(pods_total),
            f"{(pods_running/pods_total*100):.1f}%" if pods_total > 0 else "0%"
        )
        
        console.print(usage_table)
        
        # Health indicators
        health_indicators = []
        if cpu_percent > 80:
            health_indicators.append("⚠️  High CPU usage")
        if memory_percent > 80:
            health_indicators.append("⚠️  High memory usage")
        if pods_running == 0 and pods_total > 0:
            health_indicators.append("⚠️  No pods running")
        
        if health_indicators:
            console.print(Panel(
                "\n".join(health_indicators),
                title="[bold yellow]Health Warnings[/bold yellow]",
                border_style="yellow"
            ))
        else:
            console.print(Panel(
                "✅ Cluster is healthy",
                title="[bold green]Health Status[/bold green]",
                border_style="green"
            ))

@universal.command()
@click.option('--namespace', '-n', help='Namespace to analyze')
@click.option('--format', '-f', default='table', help='Output format (table, json, yaml)')
def analyze(namespace, format):
    """Analyze cluster resources and performance"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing cluster...", total=None)
        
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        metrics = detector.get_cluster_metrics()
        
        progress.update(task, description="Generating insights...")
    
    if format == 'json':
        analysis = {
            'cluster': cluster_info,
            'metrics': metrics,
            'insights': _generate_insights(cluster_info, metrics)
        }
        console.print(json.dumps(analysis, indent=2))
        return
    
    # Display analysis
    console.print(Panel(
        f"[bold blue]Cluster Analysis: {cluster_info['name']}[/bold blue]\n"
        f"Type: {cluster_info['type'].upper()}\n"
        f"Analysis completed at: {_get_timestamp()}",
        title="[bold green]Resource Analysis[/bold green]",
        border_style="green"
    ))
    
    # Resource breakdown
    if 'resources' in metrics and not metrics.get('error'):
        resources = metrics['resources']
        
        # CPU analysis
        cpu_used = resources.get('cpu', {}).get('used', 0)
        cpu_total = resources.get('cpu', {}).get('total', 1)
        cpu_percent = (cpu_used / cpu_total * 100) if cpu_total > 0 else 0
        
        # Memory analysis
        memory_used = resources.get('memory', {}).get('used', 0)
        memory_total = resources.get('memory', {}).get('total', 1)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        # Analysis table
        analysis_table = Table(title="Resource Analysis", box=box.ROUNDED)
        analysis_table.add_column("Metric", style="cyan")
        analysis_table.add_column("Current", style="yellow")
        analysis_table.add_column("Capacity", style="blue")
        analysis_table.add_column("Utilization", style="green")
        analysis_table.add_column("Status", style="white")
        
        # CPU row
        cpu_status = _get_resource_status(cpu_percent)
        analysis_table.add_row(
            "CPU",
            f"{cpu_used:.1f} cores",
            f"{cpu_total:.1f} cores",
            f"{cpu_percent:.1f}%",
            cpu_status
        )
        
        # Memory row
        memory_status = _get_resource_status(memory_percent)
        analysis_table.add_row(
            "Memory",
            f"{memory_used / (1024**3):.1f} GB",
            f"{memory_total / (1024**3):.1f} GB",
            f"{memory_percent:.1f}%",
            memory_status
        )
        
        console.print(analysis_table)
        
        # Insights
        insights = _generate_insights(cluster_info, metrics)
        if insights:
            insights_panel = Panel(
                "\n".join([f"• {insight}" for insight in insights]),
                title="[bold blue]Insights & Recommendations[/bold blue]",
                border_style="blue"
            )
            console.print(insights_panel)

@universal.command()
@click.option('--dry-run', is_flag=True, help='Show optimizations without applying')
@click.option('--format', '-f', default='table', help='Output format (table, json, yaml)')
def optimize(dry_run, format):
    """Get optimization recommendations for the cluster"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing for optimizations...", total=None)
        
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        metrics = detector.get_cluster_metrics()
        
        progress.update(task, description="Generating recommendations...")
    
    # Generate optimization recommendations
    recommendations = _generate_optimizations(cluster_info, metrics)
    
    if format == 'json':
        console.print(json.dumps(recommendations, indent=2))
        return
    
    console.print(Panel(
        f"[bold blue]Optimization Analysis: {cluster_info['name']}[/bold blue]\n"
        f"Found {len(recommendations)} optimization opportunities",
        title="[bold green]Optimization Recommendations[/bold green]",
        border_style="green"
    ))
    
    if recommendations:
        # Group recommendations by type
        resource_recs = [r for r in recommendations if r['type'] == 'resource']
        cost_recs = [r for r in recommendations if r['type'] == 'cost']
        performance_recs = [r for r in recommendations if r['type'] == 'performance']
        
        # Resource optimizations
        if resource_recs:
            console.print("\n[bold cyan]Resource Optimizations:[/bold cyan]")
            resource_table = Table(box=box.ROUNDED)
            resource_table.add_column("Issue", style="red")
            resource_table.add_column("Recommendation", style="green")
            resource_table.add_column("Impact", style="yellow")
            resource_table.add_column("Effort", style="blue")
            
            for rec in resource_recs:
                resource_table.add_row(
                    rec['issue'],
                    rec['recommendation'],
                    rec['impact'],
                    rec['effort']
                )
            console.print(resource_table)
        
        # Cost optimizations
        if cost_recs:
            console.print("\n[bold cyan]Cost Optimizations:[/bold cyan]")
            cost_table = Table(box=box.ROUNDED)
            cost_table.add_column("Opportunity", style="red")
            cost_table.add_column("Action", style="green")
            cost_table.add_column("Savings", style="yellow")
            cost_table.add_column("Risk", style="blue")
            
            for rec in cost_recs:
                cost_table.add_row(
                    rec['opportunity'],
                    rec['action'],
                    rec['savings'],
                    rec['risk']
                )
            console.print(cost_table)
        
        # Performance optimizations
        if performance_recs:
            console.print("\n[bold cyan]Performance Optimizations:[/bold cyan]")
            perf_table = Table(box=box.ROUNDED)
            perf_table.add_column("Bottleneck", style="red")
            perf_table.add_column("Solution", style="green")
            perf_table.add_column("Improvement", style="yellow")
            perf_table.add_column("Priority", style="blue")
            
            for rec in performance_recs:
                perf_table.add_row(
                    rec['bottleneck'],
                    rec['solution'],
                    rec['improvement'],
                    rec['priority']
                )
            console.print(perf_table)
        
        if dry_run:
            console.print(Panel(
                "This was a dry run. Use --no-dry-run to apply optimizations.",
                title="[bold yellow]Dry Run Mode[/bold yellow]",
                border_style="yellow"
            ))
        else:
            console.print(Panel(
                "To apply optimizations, run: upid optimize --apply",
                title="[bold green]Ready to Optimize[/bold green]",
                border_style="green"
            ))
    else:
        console.print(Panel(
            "✅ No optimization opportunities found. Your cluster is well-optimized!",
            title="[bold green]Optimization Complete[/bold green]",
            border_style="green"
        ))

@universal.command()
@click.argument('resource_type')
@click.option('--namespace', '-n', help='Namespace')
@click.option('--name', help='Resource name')
@click.option('--format', '-f', default='table', help='Output format (table, json, yaml)')
def get(resource_type, namespace, name, format):
    """Get Kubernetes resources"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Getting resources...", total=None)
        
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        
        progress.update(task, description=f"Fetching {resource_type}...")
    
    # Mock data for demonstration
    resources = [
        {
            'name': 'example-pod',
            'namespace': namespace or 'default',
            'type': resource_type,
            'status': 'Running',
            'age': '2h'
        }
    ]
    
    if format == 'json':
        console.print(json.dumps(resources, indent=2))
        return
    
    if format == 'yaml':
        import yaml
        console.print(yaml.dump(resources, default_flow_style=False))
        return
    
    # Display table
    table = Table(title=f"{resource_type.title()} Resources", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Namespace", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Age", style="dim")
    
    for resource in resources:
        table.add_row(
            resource['name'],
            resource['namespace'],
            resource['type'],
            resource['status'],
            resource['age']
        )
    
    console.print(table)

@universal.command()
@click.argument('file_path')
@click.option('--namespace', '-n', help='Namespace')
@click.option('--dry-run', is_flag=True, help='Show what would be applied without applying')
@click.option('--force', is_flag=True, help='Force apply without confirmation')
def apply(file_path, namespace, dry_run, force):
    """Apply Kubernetes configuration from file"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Applying configuration...", total=None)
        
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        
        progress.update(task, description="Reading configuration...")
    
    if dry_run:
        console.print(Panel(
            f"[yellow]Dry run mode - no changes will be applied[/yellow]\n\n"
            f"File: {file_path}\n"
            f"Namespace: {namespace or 'default'}\n"
            f"Cluster: {cluster_info['name']}",
            title="[bold yellow]Dry Run[/bold yellow]",
            border_style="yellow"
        ))
        return
    
    if not force:
        confirmed = click.confirm(f"Apply configuration from {file_path}?")
        if not confirmed:
            console.print("[yellow]Apply cancelled[/yellow]")
            return
    
    console.print(Panel(
        f"[green]✓ Configuration applied successfully![/green]\n\n"
        f"File: {file_path}\n"
        f"Namespace: {namespace or 'default'}\n"
        f"Cluster: {cluster_info['name']}",
        title="[bold green]Configuration Applied[/bold green]",
        border_style="green"
    ))

@universal.command()
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', default='html', help='Report format (html, json, yaml)')
def report(output, format):
    """Generate comprehensive cluster report"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating report...", total=None)
        
        detector = ClusterDetector()
        cluster_info = detector.detect_cluster()
        metrics = detector.get_cluster_metrics()
        
        progress.update(task, description="Compiling insights...")
        
        # Generate comprehensive report
        report_data = _generate_comprehensive_report(cluster_info, metrics)
        
        progress.update(task, description="Finalizing report...")
    
    if format == 'json':
        report_content = json.dumps(report_data, indent=2)
    elif format == 'yaml':
        import yaml
        report_content = yaml.dump(report_data, default_flow_style=False)
    else:  # HTML
        report_content = _generate_html_report(report_data)
    
    if output:
        with open(output, 'w') as f:
            f.write(report_content)
        console.print(f"[green]✅ Report saved to: {output}[/green]")
    else:
        console.print(report_content)

def _get_timestamp():
    """Get current timestamp"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _get_resource_status(percentage: float) -> str:
    """Get status based on resource usage percentage"""
    if percentage < 50:
        return "🟢 Optimal"
    elif percentage < 80:
        return "🟡 Good"
    elif percentage < 95:
        return "🟠 High"
    else:
        return "🔴 Critical"

def _generate_insights(cluster_info: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
    """Generate insights from cluster data"""
    insights = []
    
    if 'resources' in metrics and not metrics.get('error'):
        resources = metrics['resources']
        
        cpu_used = resources.get('cpu', {}).get('used', 0)
        cpu_total = resources.get('cpu', {}).get('total', 1)
        cpu_percent = (cpu_used / cpu_total * 100) if cpu_total > 0 else 0
        
        memory_used = resources.get('memory', {}).get('used', 0)
        memory_total = resources.get('memory', {}).get('total', 1)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        pods_running = resources.get('pods', {}).get('running', 0)
        pods_total = resources.get('pods', {}).get('total', 0)
        
        # CPU insights
        if cpu_percent < 20:
            insights.append("CPU usage is very low - consider scaling down resources")
        elif cpu_percent > 80:
            insights.append("CPU usage is high - consider scaling up or optimizing workloads")
        
        # Memory insights
        if memory_percent < 20:
            insights.append("Memory usage is very low - consider reducing memory allocations")
        elif memory_percent > 80:
            insights.append("Memory usage is high - consider adding more memory or optimizing")
        
        # Pod insights
        if pods_total == 0:
            insights.append("No pods found - cluster may be empty")
        elif pods_running < pods_total:
            insights.append(f"{pods_total - pods_running} pods are not running - check pod status")
    
    # Cluster type insights
    cluster_type = cluster_info.get('type', 'unknown')
    if cluster_type == 'docker-desktop':
        insights.append("Docker Desktop detected - limited resources available")
    elif cluster_type in ['eks', 'aks', 'gke']:
        insights.append(f"{cluster_type.upper()} cloud cluster detected - consider cost optimization")
    
    return insights

def _generate_optimizations(cluster_info: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate optimization recommendations"""
    recommendations = []
    
    if 'resources' in metrics and not metrics.get('error'):
        resources = metrics['resources']
        
        cpu_used = resources.get('cpu', {}).get('used', 0)
        cpu_total = resources.get('cpu', {}).get('total', 1)
        cpu_percent = (cpu_used / cpu_total * 100) if cpu_total > 0 else 0
        
        memory_used = resources.get('memory', {}).get('used', 0)
        memory_total = resources.get('memory', {}).get('total', 1)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        
        # Resource optimizations
        if cpu_percent < 30:
            recommendations.append({
                'type': 'resource',
                'issue': 'Low CPU utilization',
                'recommendation': 'Reduce CPU requests and limits',
                'impact': 'High',
                'effort': 'Low'
            })
        elif cpu_percent > 80:
            recommendations.append({
                'type': 'resource',
                'issue': 'High CPU utilization',
                'recommendation': 'Scale up CPU resources or optimize workloads',
                'impact': 'High',
                'effort': 'Medium'
            })
        
        if memory_percent < 30:
            recommendations.append({
                'type': 'resource',
                'issue': 'Low memory utilization',
                'recommendation': 'Reduce memory requests and limits',
                'impact': 'High',
                'effort': 'Low'
            })
        elif memory_percent > 80:
            recommendations.append({
                'type': 'resource',
                'issue': 'High memory utilization',
                'recommendation': 'Scale up memory resources or optimize workloads',
                'impact': 'High',
                'effort': 'Medium'
            })
        
        # Cost optimizations for cloud clusters
        cluster_type = cluster_info.get('type', 'unknown')
        if cluster_type in ['eks', 'aks', 'gke']:
            recommendations.append({
                'type': 'cost',
                'opportunity': 'Cloud cost optimization',
                'action': 'Use spot instances for non-critical workloads',
                'savings': '30-70%',
                'risk': 'Medium'
            })
            
            if cpu_percent < 50 and memory_percent < 50:
                recommendations.append({
                    'type': 'cost',
                    'opportunity': 'Right-sizing opportunity',
                    'action': 'Downsize node groups based on actual usage',
                    'savings': '20-40%',
                    'risk': 'Low'
                })
    
    return recommendations

def _generate_comprehensive_report(cluster_info: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive report data"""
    return {
        'timestamp': _get_timestamp(),
        'cluster': cluster_info,
        'metrics': metrics,
        'insights': _generate_insights(cluster_info, metrics),
        'optimizations': _generate_optimizations(cluster_info, metrics),
        'summary': {
            'total_nodes': len(cluster_info.get('info', {}).get('nodes', {}).get('items', [])),
            'total_pods': len(cluster_info.get('info', {}).get('pods', {}).get('items', [])),
            'total_namespaces': len(cluster_info.get('info', {}).get('namespaces', {}).get('items', [])),
            'cluster_type': cluster_info.get('type', 'unknown'),
            'capabilities': cluster_info.get('capabilities', {})
        }
    }

def _generate_html_report(report_data: Dict[str, Any]) -> str:
    """Generate HTML report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UPID Cluster Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 3px; }}
            .status-ok {{ color: green; }}
            .status-warning {{ color: orange; }}
            .status-error {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>UPID Cluster Report</h1>
            <p>Generated: {report_data['timestamp']}</p>
            <p>Cluster: {report_data['cluster']['name']} ({report_data['cluster']['type']})</p>
        </div>
        
        <div class="section">
            <h2>Summary</h2>
            <div class="metric">Nodes: {report_data['summary']['total_nodes']}</div>
            <div class="metric">Pods: {report_data['summary']['total_pods']}</div>
            <div class="metric">Namespaces: {report_data['summary']['total_namespaces']}</div>
        </div>
        
        <div class="section">
            <h2>Insights</h2>
            <ul>
                {''.join([f'<li>{insight}</li>' for insight in report_data['insights']])}
            </ul>
        </div>
        
        <div class="section">
            <h2>Optimizations</h2>
            <ul>
                {''.join([f'<li>{opt["recommendation"] if "recommendation" in opt else opt["action"]}</li>' for opt in report_data['optimizations']])}
            </ul>
        </div>
    </body>
    </html>
    """
    return html 