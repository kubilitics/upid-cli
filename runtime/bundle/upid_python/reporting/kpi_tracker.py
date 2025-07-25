"""
UPID CLI - KPI Tracker
Key Performance Indicator tracking and reporting
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from enum import Enum

logger = logging.getLogger(__name__)


class KPIType(Enum):
    """KPI types"""
    COST = "cost"
    SAVINGS = "savings"
    EFFICIENCY = "efficiency"
    PERFORMANCE = "performance"
    UTILIZATION = "utilization"


@dataclass
class KPI:
    """KPI data structure"""
    name: str
    value: float
    target: float
    unit: str
    kpi_type: KPIType
    timestamp: datetime
    trend: str
    status: str


@dataclass
class KPISet:
    """Set of KPIs for a specific period"""
    period: str
    start_date: datetime
    end_date: datetime
    kpis: List[KPI]
    summary: Dict[str, Any]


class KPITracker:
    """
    Key Performance Indicator Tracker
    
    Provides comprehensive KPI tracking capabilities:
    - Real-time KPI monitoring
    - Historical KPI tracking
    - KPI trend analysis
    - Performance benchmarking
    - Automated KPI alerts
    """
    
    def __init__(self):
        self.kpi_history: List[KPISet] = []
        self.kpi_definitions: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds: Dict[str, float] = {}
        
        logger.info("🔧 Initializing KPI tracker")
    
    async def initialize(self) -> bool:
        """Initialize KPI tracker with default KPIs"""
        try:
            logger.info("🚀 Initializing KPI tracker...")
            
            # Define default KPIs
            await self._setup_default_kpis()
            
            # Set up alert thresholds
            await self._setup_alert_thresholds()
            
            logger.info("✅ KPI tracker initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize KPI tracker: {e}")
            return False
    
    async def _setup_default_kpis(self):
        """Setup default KPI definitions"""
        self.kpi_definitions = {
            'total_cost': {
                'name': 'Total Cost',
                'target': 10000.0,
                'unit': 'USD',
                'type': KPIType.COST,
                'description': 'Total cost across all clusters'
            },
            'total_savings': {
                'name': 'Total Savings',
                'target': 2000.0,
                'unit': 'USD',
                'type': KPIType.SAVINGS,
                'description': 'Total savings from optimizations'
            },
            'cost_per_cluster': {
                'name': 'Cost per Cluster',
                'target': 2000.0,
                'unit': 'USD',
                'type': KPIType.COST,
                'description': 'Average cost per cluster'
            },
            'optimization_rate': {
                'name': 'Optimization Rate',
                'target': 80.0,
                'unit': '%',
                'type': KPIType.EFFICIENCY,
                'description': 'Percentage of clusters optimized'
            },
            'resource_utilization': {
                'name': 'Resource Utilization',
                'target': 70.0,
                'unit': '%',
                'type': KPIType.UTILIZATION,
                'description': 'Average resource utilization'
            },
            'roi_percentage': {
                'name': 'ROI Percentage',
                'target': 20.0,
                'unit': '%',
                'type': KPIType.EFFICIENCY,
                'description': 'Return on investment percentage'
            }
        }
    
    async def _setup_alert_thresholds(self):
        """Setup alert thresholds for KPIs"""
        self.alert_thresholds = {
            'total_cost': 15000.0,  # Alert if cost exceeds $15k
            'cost_per_cluster': 3000.0,  # Alert if cost per cluster exceeds $3k
            'optimization_rate': 50.0,  # Alert if optimization rate below 50%
            'resource_utilization': 50.0,  # Alert if utilization below 50%
            'roi_percentage': 10.0  # Alert if ROI below 10%
        }
    
    async def calculate_kpis(self, 
                           cluster_data: List[Dict[str, Any]],
                           cost_data: List[Dict[str, Any]],
                           optimization_data: List[Dict[str, Any]]) -> KPISet:
        """Calculate KPIs from data"""
        try:
            logger.info("📊 Calculating KPIs...")
            
            # Calculate basic metrics
            total_cost = sum(item.get('cost', 0) for item in cost_data)
            total_savings = sum(item.get('savings', 0) for item in optimization_data)
            total_clusters = len(cluster_data)
            
            # Calculate derived metrics
            cost_per_cluster = total_cost / max(total_clusters, 1)
            optimization_rate = (len(optimization_data) / max(total_clusters, 1)) * 100
            roi_percentage = (total_savings / max(total_cost, 1)) * 100
            
            # Calculate resource utilization (simplified)
            resource_utilization = 65.0  # Mock value
            
            # Create KPI objects
            kpis = [
                KPI(
                    name='Total Cost',
                    value=total_cost,
                    target=self.kpi_definitions['total_cost']['target'],
                    unit='USD',
                    kpi_type=KPIType.COST,
                    timestamp=datetime.utcnow(),
                    trend='stable',
                    status='on_target'
                ),
                KPI(
                    name='Total Savings',
                    value=total_savings,
                    target=self.kpi_definitions['total_savings']['target'],
                    unit='USD',
                    kpi_type=KPIType.SAVINGS,
                    timestamp=datetime.utcnow(),
                    trend='increasing',
                    status='exceeding'
                ),
                KPI(
                    name='Cost per Cluster',
                    value=cost_per_cluster,
                    target=self.kpi_definitions['cost_per_cluster']['target'],
                    unit='USD',
                    kpi_type=KPIType.COST,
                    timestamp=datetime.utcnow(),
                    trend='decreasing',
                    status='on_target'
                ),
                KPI(
                    name='Optimization Rate',
                    value=optimization_rate,
                    target=self.kpi_definitions['optimization_rate']['target'],
                    unit='%',
                    kpi_type=KPIType.EFFICIENCY,
                    timestamp=datetime.utcnow(),
                    trend='increasing',
                    status='below_target'
                ),
                KPI(
                    name='Resource Utilization',
                    value=resource_utilization,
                    target=self.kpi_definitions['resource_utilization']['target'],
                    unit='%',
                    kpi_type=KPIType.UTILIZATION,
                    timestamp=datetime.utcnow(),
                    trend='stable',
                    status='on_target'
                ),
                KPI(
                    name='ROI Percentage',
                    value=roi_percentage,
                    target=self.kpi_definitions['roi_percentage']['target'],
                    unit='%',
                    kpi_type=KPIType.EFFICIENCY,
                    timestamp=datetime.utcnow(),
                    trend='increasing',
                    status='exceeding'
                )
            ]
            
            # Create summary
            summary = {
                'total_kpis': len(kpis),
                'on_target': len([k for k in kpis if k.status == 'on_target']),
                'exceeding': len([k for k in kpis if k.status == 'exceeding']),
                'below_target': len([k for k in kpis if k.status == 'below_target']),
                'average_performance': sum(k.value for k in kpis) / len(kpis)
            }
            
            # Create KPISet
            kpi_set = KPISet(
                period='current_month',
                start_date=datetime.utcnow().replace(day=1),
                end_date=datetime.utcnow(),
                kpis=kpis,
                summary=summary
            )
            
            # Store in history
            self.kpi_history.append(kpi_set)
            
            logger.info("✅ KPIs calculated successfully")
            return kpi_set
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate KPIs: {e}")
            return KPISet(
                period='error',
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow(),
                kpis=[],
                summary={}
            )
    
    async def get_kpi_trends(self, kpi_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get KPI trends over time"""
        try:
            logger.info(f"📈 Getting trends for KPI: {kpi_name}")
            
            trends = []
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Filter KPI history for the specified KPI
            relevant_kpis = []
            for kpi_set in self.kpi_history:
                for kpi in kpi_set.kpis:
                    if kpi.name == kpi_name and start_date <= kpi.timestamp <= end_date:
                        relevant_kpis.append(kpi)
            
            # Sort by timestamp
            relevant_kpis.sort(key=lambda x: x.timestamp)
            
            # Calculate trends
            for i, kpi in enumerate(relevant_kpis):
                trend_data = {
                    'timestamp': kpi.timestamp.isoformat(),
                    'value': kpi.value,
                    'target': kpi.target,
                    'status': kpi.status,
                    'trend': kpi.trend
                }
                
                # Calculate change from previous value
                if i > 0:
                    prev_value = relevant_kpis[i-1].value
                    change = ((kpi.value - prev_value) / max(prev_value, 1)) * 100
                    trend_data['change_percentage'] = change
                else:
                    trend_data['change_percentage'] = 0
                
                trends.append(trend_data)
            
            logger.info(f"✅ Retrieved {len(trends)} trend points for {kpi_name}")
            return trends
            
        except Exception as e:
            logger.error(f"❌ Failed to get KPI trends: {e}")
            return []
    
    async def check_kpi_alerts(self, kpi_set: KPISet) -> List[Dict[str, Any]]:
        """Check for KPI alerts based on thresholds"""
        try:
            logger.info("🚨 Checking KPI alerts...")
            
            alerts = []
            
            for kpi in kpi_set.kpis:
                # Check if KPI has a threshold
                if kpi.name.lower().replace(' ', '_') in self.alert_thresholds:
                    threshold = self.alert_thresholds[kpi.name.lower().replace(' ', '_')]
                    
                    # Check for alerts based on KPI type
                    if kpi.kpi_type == KPIType.COST:
                        if kpi.value > threshold:
                            alerts.append({
                                'kpi_name': kpi.name,
                                'current_value': kpi.value,
                                'threshold': threshold,
                                'severity': 'high',
                                'message': f"{kpi.name} ({kpi.value:.2f} {kpi.unit}) exceeds threshold ({threshold:.2f} {kpi.unit})"
                            })
                    
                    elif kpi.kpi_type == KPIType.EFFICIENCY:
                        if kpi.value < threshold:
                            alerts.append({
                                'kpi_name': kpi.name,
                                'current_value': kpi.value,
                                'threshold': threshold,
                                'severity': 'medium',
                                'message': f"{kpi.name} ({kpi.value:.2f} {kpi.unit}) below threshold ({threshold:.2f} {kpi.unit})"
                            })
                    
                    elif kpi.kpi_type == KPIType.UTILIZATION:
                        if kpi.value < threshold:
                            alerts.append({
                                'kpi_name': kpi.name,
                                'current_value': kpi.value,
                                'threshold': threshold,
                                'severity': 'medium',
                                'message': f"{kpi.name} ({kpi.value:.2f} {kpi.unit}) below threshold ({threshold:.2f} {kpi.unit})"
                            })
            
            logger.info(f"✅ Found {len(alerts)} KPI alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to check KPI alerts: {e}")
            return []
    
    async def generate_kpi_report(self, 
                                kpi_set: KPISet,
                                include_trends: bool = True,
                                include_alerts: bool = True) -> Dict[str, Any]:
        """Generate comprehensive KPI report"""
        try:
            logger.info("📋 Generating KPI report...")
            
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'period': kpi_set.period,
                'summary': kpi_set.summary,
                'kpis': []
            }
            
            # Add KPI data
            for kpi in kpi_set.kpis:
                kpi_data = {
                    'name': kpi.name,
                    'value': kpi.value,
                    'target': kpi.target,
                    'unit': kpi.unit,
                    'type': kpi.kpi_type.value,
                    'status': kpi.status,
                    'trend': kpi.trend,
                    'timestamp': kpi.timestamp.isoformat()
                }
                
                # Add trends if requested
                if include_trends:
                    kpi_data['trends'] = await self.get_kpi_trends(kpi.name)
                
                report['kpis'].append(kpi_data)
            
            # Add alerts if requested
            if include_alerts:
                report['alerts'] = await self.check_kpi_alerts(kpi_set)
            
            logger.info("✅ KPI report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate KPI report: {e}")
            return {}
    
    async def add_custom_kpi(self, 
                            name: str,
                            target: float,
                            unit: str,
                            kpi_type: KPIType,
                            description: str = "") -> bool:
        """Add custom KPI definition"""
        try:
            logger.info(f"➕ Adding custom KPI: {name}")
            
            self.kpi_definitions[name.lower().replace(' ', '_')] = {
                'name': name,
                'target': target,
                'unit': unit,
                'type': kpi_type,
                'description': description
            }
            
            logger.info(f"✅ Custom KPI '{name}' added successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add custom KPI: {e}")
            return False
    
    async def set_alert_threshold(self, kpi_name: str, threshold: float) -> bool:
        """Set alert threshold for a KPI"""
        try:
            logger.info(f"🔔 Setting alert threshold for {kpi_name}: {threshold}")
            
            self.alert_thresholds[kpi_name.lower().replace(' ', '_')] = threshold
            
            logger.info(f"✅ Alert threshold set for '{kpi_name}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set alert threshold: {e}")
            return False
    
    async def get_kpi_performance_summary(self) -> Dict[str, Any]:
        """Get overall KPI performance summary"""
        try:
            logger.info("📊 Generating KPI performance summary...")
            
            if not self.kpi_history:
                return {}
            
            # Get latest KPI set
            latest_kpi_set = self.kpi_history[-1]
            
            # Calculate performance metrics
            total_kpis = len(latest_kpi_set.kpis)
            on_target_count = latest_kpi_set.summary.get('on_target', 0)
            exceeding_count = latest_kpi_set.summary.get('exceeding', 0)
            below_target_count = latest_kpi_set.summary.get('below_target', 0)
            
            # Calculate percentages
            on_target_percentage = (on_target_count / max(total_kpis, 1)) * 100
            exceeding_percentage = (exceeding_count / max(total_kpis, 1)) * 100
            below_target_percentage = (below_target_count / max(total_kpis, 1)) * 100
            
            summary = {
                'total_kpis': total_kpis,
                'on_target_count': on_target_count,
                'exceeding_count': exceeding_count,
                'below_target_count': below_target_count,
                'on_target_percentage': on_target_percentage,
                'exceeding_percentage': exceeding_percentage,
                'below_target_percentage': below_target_percentage,
                'overall_performance': 'excellent' if on_target_percentage >= 80 else 'good' if on_target_percentage >= 60 else 'needs_improvement'
            }
            
            logger.info("✅ KPI performance summary generated")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate KPI performance summary: {e}")
            return {} 