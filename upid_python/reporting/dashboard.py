"""
UPID CLI - Business Intelligence Dashboard
Executive dashboard generation with rich CLI visualizations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.columns import Columns
from rich.bar import Bar
from rich.align import Align
import json

logger = logging.getLogger(__name__)

@dataclass
class DashboardMetrics:
    """Dashboard metrics data structure"""
    total_clusters: int
    total_pods: int
    total_cost: float
    total_savings: float
    cost_efficiency: float
    resource_utilization: float
    optimization_score: float
    alerts_count: int
    last_updated: datetime

@dataclass
class KPI:
    """Key Performance Indicator"""
    name: str
    value: float
    target: float
    unit: str
    status: str  # "good", "warning", "critical"
    trend: str   # "up", "down", "stable"
    description: str

@dataclass
class ROIAnalysis:
    """ROI Analysis data"""
    initial_investment: float
    monthly_savings: float
    total_savings: float
    roi_percentage: float
    payback_period_months: float
    npv: float
    irr: float
    breakeven_date: datetime

class DashboardGenerator:
    """Business Intelligence Dashboard Generator"""
    
    def __init__(self):
        self.console = Console()
        self.layout = None
        self.metrics = None
        
    async def generate_executive_dashboard(
        self, 
        cluster_data: List[Dict[str, Any]], 
        cost_data: List[Dict[str, Any]], 
        optimization_data: List[Dict[str, Any]]
    ) -> str:
        """Generate executive dashboard with rich CLI visualization"""
        try:
            logger.info("Generating executive dashboard")
            
            # Calculate metrics
            self.metrics = await self._calculate_metrics(cluster_data, cost_data, optimization_data)
            
            # Create layout
            self.layout = Layout()
            self.layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main"),
                Layout(name="footer", size=3)
            )
            
            self.layout["main"].split_row(
                Layout(name="left"),
                Layout(name="right")
            )
            
            self.layout["left"].split_column(
                Layout(name="overview"),
                Layout(name="kpis")
            )
            
            self.layout["right"].split_column(
                Layout(name="costs"),
                Layout(name="optimization")
            )
            
            # Populate sections
            await self._populate_header()
            await self._populate_overview()
            await self._populate_kpis()
            await self._populate_costs()
            await self._populate_optimization()
            await self._populate_footer()
            
            # Render dashboard
            dashboard_output = self.console.render(self.layout)
            logger.info("Executive dashboard generated successfully")
            return dashboard_output
            
        except Exception as e:
            logger.error(f"Error generating executive dashboard: {e}")
            return f"Error generating dashboard: {e}"
    
    async def generate_kpi_report(
        self, 
        cluster_data: List[Dict[str, Any]], 
        cost_data: List[Dict[str, Any]], 
        optimization_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive KPI report"""
        try:
            logger.info("Generating KPI report")
            
            # Calculate metrics
            metrics = await self._calculate_metrics(cluster_data, cost_data, optimization_data)
            
            # Define KPIs
            kpis = [
                KPI(
                    name="Cost Efficiency",
                    value=metrics.cost_efficiency,
                    target=85.0,
                    unit="%",
                    status="good" if metrics.cost_efficiency >= 80 else "warning",
                    trend="up",
                    description="Overall cost optimization efficiency"
                ),
                KPI(
                    name="Resource Utilization",
                    value=metrics.resource_utilization,
                    target=75.0,
                    unit="%",
                    status="good" if metrics.resource_utilization >= 70 else "warning",
                    trend="stable",
                    description="Average resource utilization across clusters"
                ),
                KPI(
                    name="Optimization Score",
                    value=metrics.optimization_score,
                    target=90.0,
                    unit="%",
                    status="good" if metrics.optimization_score >= 85 else "warning",
                    trend="up",
                    description="ML-powered optimization effectiveness"
                ),
                KPI(
                    name="Total Savings",
                    value=metrics.total_savings,
                    target=10000.0,
                    unit="$",
                    status="good" if metrics.total_savings >= 5000 else "warning",
                    trend="up",
                    description="Total cost savings achieved"
                ),
                KPI(
                    name="Active Alerts",
                    value=metrics.alerts_count,
                    target=0.0,
                    unit="",
                    status="good" if metrics.alerts_count == 0 else "critical",
                    trend="down",
                    description="Number of active system alerts"
                )
            ]
            
            # Generate KPI table
            kpi_table = Table(title="Key Performance Indicators")
            kpi_table.add_column("KPI", style="cyan")
            kpi_table.add_column("Value", style="green")
            kpi_table.add_column("Target", style="yellow")
            kpi_table.add_column("Status", style="magenta")
            kpi_table.add_column("Trend", style="blue")
            kpi_table.add_column("Description", style="white")
            
            for kpi in kpis:
                status_icon = "✅" if kpi.status == "good" else "⚠️" if kpi.status == "warning" else "❌"
                trend_icon = "📈" if kpi.trend == "up" else "📉" if kpi.trend == "down" else "➡️"
                
                kpi_table.add_row(
                    kpi.name,
                    f"{kpi.value:.2f} {kpi.unit}",
                    f"{kpi.target:.2f} {kpi.unit}",
                    f"{status_icon} {kpi.status}",
                    f"{trend_icon} {kpi.trend}",
                    kpi.description
                )
            
            # Render KPI table
            kpi_output = self.console.render(kpi_table)
            
            report = {
                "metrics": asdict(metrics),
                "kpis": [asdict(kpi) for kpi in kpis],
                "kpi_table": kpi_output,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("KPI report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating KPI report: {e}")
            return {"error": str(e)}
    
    async def generate_live_dashboard(
        self, 
        cluster_data: List[Dict[str, Any]], 
        cost_data: List[Dict[str, Any]], 
        optimization_data: List[Dict[str, Any]]
    ) -> None:
        """Generate live-updating dashboard"""
        try:
            logger.info("Starting live dashboard")
            
            with Live(self.layout, refresh_per_second=1) as live:
                while True:
                    # Update metrics
                    self.metrics = await self._calculate_metrics(cluster_data, cost_data, optimization_data)
                    
                    # Update layout
                    await self._populate_header()
                    await self._populate_overview()
                    await self._populate_kpis()
                    await self._populate_costs()
                    await self._populate_optimization()
                    await self._populate_footer()
                    
                    # Update live display
                    live.update(self.layout)
                    
                    # Wait before next update
                    await asyncio.sleep(5)
                    
        except KeyboardInterrupt:
            logger.info("Live dashboard stopped by user")
        except Exception as e:
            logger.error(f"Error in live dashboard: {e}")
    
    async def generate_custom_dashboard(
        self, 
        config: Dict[str, Any], 
        data: Dict[str, Any]
    ) -> str:
        """Generate custom dashboard based on configuration"""
        try:
            logger.info("Generating custom dashboard")
            
            # Create custom layout based on config
            layout = Layout()
            
            if config.get("layout_type") == "grid":
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="content"),
                    Layout(name="footer", size=2)
                )
                layout["content"].split_row(
                    Layout(name="left"),
                    Layout(name="right")
                )
            elif config.get("layout_type") == "single":
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="content"),
                    Layout(name="footer", size=2)
                )
            else:
                # Default layout
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="content"),
                    Layout(name="footer", size=2)
                )
            
            # Populate based on config
            if "header" in config:
                layout["header"].update(Panel(
                    config["header"].get("title", "Custom Dashboard"),
                    style="bold blue"
                ))
            
            if "content" in config:
                content_type = config["content"].get("type", "table")
                if content_type == "table":
                    table = Table(title=config["content"].get("title", "Data"))
                    for column in config["content"].get("columns", []):
                        table.add_column(column["name"], style=column.get("style", "white"))
                    
                    for row in data.get("rows", []):
                        table.add_row(*[str(cell) for cell in row])
                    
                    layout["content"].update(table)
                elif content_type == "metrics":
                    metrics_panel = Panel(
                        self._format_metrics(data.get("metrics", {})),
                        title=config["content"].get("title", "Metrics")
                    )
                    layout["content"].update(metrics_panel)
            
            if "footer" in config:
                layout["footer"].update(Panel(
                    config["footer"].get("text", f"Generated at {datetime.now()}"),
                    style="dim"
                ))
            
            # Render custom dashboard
            dashboard_output = self.console.render(layout)
            logger.info("Custom dashboard generated successfully")
            return dashboard_output
            
        except Exception as e:
            logger.error(f"Error generating custom dashboard: {e}")
            return f"Error generating custom dashboard: {e}"
    
    async def _calculate_metrics(
        self, 
        cluster_data: List[Dict[str, Any]], 
        cost_data: List[Dict[str, Any]], 
        optimization_data: List[Dict[str, Any]]
    ) -> DashboardMetrics:
        """Calculate dashboard metrics from data"""
        try:
            total_clusters = len(cluster_data)
            total_pods = sum(cluster.get("pod_count", 0) for cluster in cluster_data)
            total_cost = sum(cost.get("amount", 0) for cost in cost_data)
            total_savings = sum(opt.get("savings", 0) for opt in optimization_data)
            
            # Calculate efficiency metrics
            cost_efficiency = (total_savings / max(total_cost, 1)) * 100
            resource_utilization = sum(cluster.get("utilization", 0) for cluster in cluster_data) / max(total_clusters, 1)
            optimization_score = sum(opt.get("score", 0) for opt in optimization_data) / max(len(optimization_data), 1)
            
            # Count alerts
            alerts_count = sum(1 for cluster in cluster_data if cluster.get("alerts", 0) > 0)
            
            return DashboardMetrics(
                total_clusters=total_clusters,
                total_pods=total_pods,
                total_cost=total_cost,
                total_savings=total_savings,
                cost_efficiency=cost_efficiency,
                resource_utilization=resource_utilization,
                optimization_score=optimization_score,
                alerts_count=alerts_count,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return DashboardMetrics(
                total_clusters=0,
                total_pods=0,
                total_cost=0.0,
                total_savings=0.0,
                cost_efficiency=0.0,
                resource_utilization=0.0,
                optimization_score=0.0,
                alerts_count=0,
                last_updated=datetime.now()
            )
    
    async def _populate_header(self):
        """Populate dashboard header"""
        if self.layout and self.metrics:
            header_text = Text()
            header_text.append("UPID CLI - Business Intelligence Dashboard", style="bold blue")
            header_text.append("\n")
            header_text.append(f"Last Updated: {self.metrics.last_updated.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
            
            self.layout["header"].update(Panel(header_text, style="blue"))
    
    async def _populate_overview(self):
        """Populate overview section"""
        if self.layout and self.metrics:
            overview_table = Table(title="Overview")
            overview_table.add_column("Metric", style="cyan")
            overview_table.add_column("Value", style="green")
            
            overview_table.add_row("Total Clusters", str(self.metrics.total_clusters))
            overview_table.add_row("Total Pods", str(self.metrics.total_pods))
            overview_table.add_row("Total Cost", f"${self.metrics.total_cost:,.2f}")
            overview_table.add_row("Total Savings", f"${self.metrics.total_savings:,.2f}")
            overview_table.add_row("Cost Efficiency", f"{self.metrics.cost_efficiency:.1f}%")
            overview_table.add_row("Resource Utilization", f"{self.metrics.resource_utilization:.1f}%")
            overview_table.add_row("Optimization Score", f"{self.metrics.optimization_score:.1f}%")
            overview_table.add_row("Active Alerts", str(self.metrics.alerts_count))
            
            self.layout["overview"].update(overview_table)
    
    async def _populate_kpis(self):
        """Populate KPI section"""
        if self.layout and self.metrics:
            kpi_panel = Panel(
                f"Cost Efficiency: {self.metrics.cost_efficiency:.1f}%\n"
                f"Resource Utilization: {self.metrics.resource_utilization:.1f}%\n"
                f"Optimization Score: {self.metrics.optimization_score:.1f}%\n"
                f"Total Savings: ${self.metrics.total_savings:,.2f}",
                title="Key Performance Indicators",
                style="green"
            )
            self.layout["kpis"].update(kpi_panel)
    
    async def _populate_costs(self):
        """Populate costs section"""
        if self.layout and self.metrics:
            cost_bar = Bar(
                self.metrics.total_cost,
                self.metrics.total_cost + self.metrics.total_savings,
                width=40,
                color="red"
            )
            
            cost_panel = Panel(
                f"Current Cost: ${self.metrics.total_cost:,.2f}\n"
                f"Potential Savings: ${self.metrics.total_savings:,.2f}\n"
                f"Cost Trend: {cost_bar}",
                title="Cost Analysis",
                style="red"
            )
            self.layout["costs"].update(cost_panel)
    
    async def _populate_optimization(self):
        """Populate optimization section"""
        if self.layout and self.metrics:
            optimization_bar = Bar(
                self.metrics.optimization_score,
                100,
                width=40,
                color="green"
            )
            
            optimization_panel = Panel(
                f"Optimization Score: {self.metrics.optimization_score:.1f}%\n"
                f"Progress: {optimization_bar}\n"
                f"Active Alerts: {self.metrics.alerts_count}",
                title="Optimization Status",
                style="green"
            )
            self.layout["optimization"].update(optimization_panel)
    
    async def _populate_footer(self):
        """Populate dashboard footer"""
        if self.layout:
            footer_text = Text()
            footer_text.append("UPID CLI v2.0", style="dim")
            footer_text.append(" | ")
            footer_text.append("Business Intelligence Dashboard", style="dim")
            footer_text.append(" | ")
            footer_text.append("Enterprise Ready", style="bold green")
            
            self.layout["footer"].update(Panel(footer_text, style="dim"))
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for display"""
        formatted = []
        for key, value in metrics.items():
            if isinstance(value, float):
                formatted.append(f"{key}: {value:.2f}")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted) 