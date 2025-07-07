"""
Utility functions for UPID CLI
"""

import os
import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_duration(seconds: int) -> str:
    """Format duration to human readable string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.1f}%"

def format_cost(cost: float) -> str:
    """Format cost in dollars"""
    return f"${cost:.2f}"

def create_table(title: str, columns: List[str]) -> Table:
    """Create a rich table"""
    table = Table(title=title)
    for column in columns:
        table.add_column(column, style="cyan")
    return table

def print_json(data: Dict[str, Any]) -> None:
    """Print data as JSON"""
    console.print_json(json.dumps(data, indent=2))

def print_yaml(data: Dict[str, Any]) -> None:
    """Print data as YAML"""
    console.print(yaml.dump(data, default_flow_style=False))

def print_table(data: List[Dict[str, Any]], title: str = "Data") -> None:
    """Print data as table"""
    if not data:
        console.print(f"[yellow]No data to display for {title}[/yellow]")
        return
    
    columns = list(data[0].keys())
    table = create_table(title, columns)
    
    for row in data:
        table.add_row(*[str(row.get(col, '')) for col in columns])
    
    console.print(table)

def show_progress(description: str):
    """Show progress spinner"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )

def validate_cluster_name(name: str) -> bool:
    """Validate cluster name"""
    if not name or len(name) < 3:
        return False
    if not name.replace('-', '').replace('_', '').isalnum():
        return False
    return True

def validate_namespace(name: str) -> bool:
    """Validate namespace name"""
    if not name or len(name) < 1:
        return False
    if not name.replace('-', '').replace('_', '').isalnum():
        return False
    return True

def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    duration_str = duration_str.lower()
    
    if duration_str.endswith('s'):
        return int(duration_str[:-1])
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    elif duration_str.endswith('d'):
        return int(duration_str[:-1]) * 86400
    else:
        # Assume minutes
        return int(duration_str) * 60

def calculate_savings(current_cost: float, optimized_cost: float) -> Dict[str, Any]:
    """Calculate cost savings"""
    savings_amount = current_cost - optimized_cost
    savings_percentage = (savings_amount / current_cost) * 100 if current_cost > 0 else 0
    
    return {
        'current_cost': current_cost,
        'optimized_cost': optimized_cost,
        'savings_amount': savings_amount,
        'savings_percentage': savings_percentage
    }

def format_zero_pod_recommendation(recommendation: Dict[str, Any]) -> Dict[str, Any]:
    """Format zero-pod recommendation for display"""
    return {
        'namespace': recommendation.get('namespace', ''),
        'deployment': recommendation.get('deployment', ''),
        'current_replicas': recommendation.get('current_replicas', 0),
        'recommended_replicas': recommendation.get('recommended_replicas', 0),
        'idle_time': format_duration(recommendation.get('idle_time_seconds', 0)),
        'savings': format_cost(recommendation.get('estimated_savings', 0)),
        'risk_level': recommendation.get('risk_level', 'low')
    }
