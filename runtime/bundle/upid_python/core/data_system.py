"""
UPID CLI - Production Data System
Unified, production-ready data ingestion and processing for UPID platform
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

from .k8s_client import KubernetesClient, NodeInfo, PodInfo, ClusterMetrics
from .metrics_collector import MetricsCollector, NodeMetrics, PodMetrics
from .resource_analyzer import ResourceAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class DataSystemMetrics:
    """Metrics about the data system performance"""
    total_clusters: int
    total_nodes: int
    total_pods: int
    total_namespaces: int
    data_freshness_seconds: int
    cache_hit_rate: float
    last_update: datetime
    status: str


class DataSystem:
    """
    Production-ready data system for UPID CLI
    Provides unified access to real Kubernetes cluster, node, pod, and metrics data
    Extensible for cost, optimization, and business intelligence integration
    """
    
    def __init__(self, k8s_client: KubernetesClient, metrics_collector: Optional[MetricsCollector] = None):
        self.k8s_client = k8s_client
        self.metrics_collector = metrics_collector or MetricsCollector(k8s_client)
        self.resource_analyzer = ResourceAnalyzer(k8s_client, self.metrics_collector)
        
        # Cache for performance
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)
        self._last_update = datetime.utcnow()
        
        logger.info("🔧 Initializing UPID production data system")

    async def initialize(self) -> bool:
        """Initialize the data system and test connectivity"""
        try:
            logger.info("🚀 Initializing UPID data system...")
            
            # Test Kubernetes connectivity
            if not await self.k8s_client.connect():
                logger.error("❌ Failed to connect to Kubernetes cluster")
                return False
            
            # Test metrics collection
            try:
                await self.metrics_collector.collect_cluster_metrics()
                logger.info("✅ Metrics collection system ready")
            except Exception as e:
                logger.warning(f"⚠️ Metrics collection not available: {e}")
            
            self._last_update = datetime.utcnow()
            logger.info("✅ UPID data system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize data system: {e}")
            return False

    async def get_cluster_info(self) -> Dict[str, Any]:
        """Fetch real cluster info (version, nodes, namespaces, capacity, etc.)"""
        cache_key = "cluster_info"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            data = await self.k8s_client.get_cluster_info()
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get cluster info: {e}")
            return {"error": str(e), "status": "failed"}

    async def get_nodes(self) -> List[NodeInfo]:
        """Fetch real node info"""
        cache_key = "nodes"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            data = await self.k8s_client.list_nodes()
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get nodes: {e}")
            return []

    async def get_pods(self, namespace: Optional[str] = None) -> List[PodInfo]:
        """Fetch real pod info"""
        cache_key = f"pods_{namespace or 'all'}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            data = await self.k8s_client.list_pods(namespace=namespace)
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get pods: {e}")
            return []

    async def get_node_metrics(self) -> List[NodeMetrics]:
        """Fetch real node metrics"""
        cache_key = "node_metrics"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            data = await self.metrics_collector.collect_node_metrics()
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get node metrics: {e}")
            return []

    async def get_pod_metrics(self, namespace: Optional[str] = None) -> List[PodMetrics]:
        """Fetch real pod metrics"""
        cache_key = f"pod_metrics_{namespace or 'all'}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            data = await self.metrics_collector.collect_pod_metrics(namespace=namespace)
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get pod metrics: {e}")
            return []

    async def get_cluster_metrics(self) -> ClusterMetrics:
        """Fetch real cluster-wide metrics"""
        cache_key = "cluster_metrics"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            data = await self.metrics_collector.collect_cluster_metrics()
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get cluster metrics: {e}")
            # Return empty metrics on error
            return ClusterMetrics(
                cluster_name="unknown",
                timestamp=datetime.utcnow(),
                total_nodes=0,
                ready_nodes=0,
                total_pods=0,
                running_pods=0,
                pending_pods=0,
                failed_pods=0,
                total_namespaces=0,
                cpu_capacity_cores=0.0,
                cpu_usage_cores=0.0,
                cpu_usage_percent=0.0,
                memory_capacity_bytes=0,
                memory_usage_bytes=0,
                memory_usage_percent=0.0
            )

    async def get_cost_data(self) -> Dict[str, Any]:
        """Fetch cost data with real resource analysis"""
        try:
            logger.info("💰 Collecting cost data...")
            
            # Get cluster metrics for cost calculation
            cluster_metrics = await self.get_cluster_metrics()
            pod_metrics = await self.get_pod_metrics()
            
            # Calculate costs based on resource usage
            cpu_cost_per_hour = 0.10  # $0.10 per CPU core per hour
            memory_cost_per_gb_hour = 0.05  # $0.05 per GB per hour
            
            total_cpu_cost = cluster_metrics.cpu_usage_cores * cpu_cost_per_hour * 24 * 30  # Monthly
            total_memory_cost = (cluster_metrics.memory_usage_bytes / (1024**3)) * memory_cost_per_gb_hour * 24 * 30
            
            # Calculate waste costs
            total_cpu_requests = sum(pm.cpu_requests_millicores for pm in pod_metrics) / 1000.0
            total_memory_requests = sum(pm.memory_requests_bytes for pm in pod_metrics) / (1024**3)
            
            cpu_waste = max(0, cluster_metrics.cpu_capacity_cores - total_cpu_requests)
            memory_waste = max(0, (cluster_metrics.memory_capacity_bytes / (1024**3)) - total_memory_requests)
            
            waste_cost = (
                cpu_waste * cpu_cost_per_hour * 24 * 30 +
                memory_waste * memory_cost_per_gb_hour * 24 * 30
            )
            
            total_cost = total_cpu_cost + total_memory_cost
            efficiency_score = max(0, 100 - (waste_cost / max(total_cost, 1)) * 100) if total_cost > 0 else 0
            
            cost_data = {
                "total_monthly_cost": total_cost,
                "cpu_cost": total_cpu_cost,
                "memory_cost": total_memory_cost,
                "waste_cost": waste_cost,
                "potential_savings": waste_cost,
                "cost_per_pod": total_cost / max(len(pod_metrics), 1),
                "efficiency_score": efficiency_score,
                "currency": "USD",
                "period": "monthly",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Cost analysis complete: ${cost_data['total_monthly_cost']:.2f} monthly")
            return cost_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get cost data: {e}")
            return {"error": str(e), "status": "failed"}

    async def get_optimization_data(self) -> Dict[str, Any]:
        """Fetch optimization recommendations based on real data"""
        try:
            logger.info("🔧 Collecting optimization data...")
            
            # Get resource analysis
            idle_workloads = await self.resource_analyzer.analyze_idle_workloads()
            efficiency_report = await self.resource_analyzer.calculate_resource_efficiency()
            cost_breakdown = await self.resource_analyzer.cost_analysis()
            
            # Extract resource efficiency from the report
            resource_efficiency = efficiency_report.resource_efficiency if hasattr(efficiency_report, 'resource_efficiency') else []
            
            # Get cost data for calculations
            cost_data = await self.get_cost_data()
            total_cost = cost_data.get("total_monthly_cost", 0) if "error" not in cost_data else 0
            
            # Generate optimization recommendations
            recommendations = []
            
            # CPU optimization recommendations
            if resource_efficiency:
                for efficiency in resource_efficiency:
                    if efficiency.resource_type == "cpu" and efficiency.efficiency_percent < 70:
                        # Calculate potential savings based on waste percentage
                        waste_cost = (efficiency.waste_percent / 100) * total_cost if total_cost > 0 else 0
                        recommendations.append({
                            "type": "cpu_optimization",
                            "priority": "high" if efficiency.efficiency_percent < 50 else "medium",
                            "description": f"CPU efficiency is {efficiency.efficiency_percent:.1f}%. Consider right-sizing pods.",
                            "potential_savings": waste_cost,
                            "action": "right_size_pods"
                        })
            
            # Idle workload recommendations
            if idle_workloads:
                recommendations.append({
                    "type": "idle_workload_cleanup",
                    "priority": "high",
                    "description": f"Found {len(idle_workloads)} idle workloads that can be removed.",
                    "potential_savings": sum(w.get("estimated_cost", 0) for w in idle_workloads),
                    "action": "remove_idle_workloads",
                    "workloads": idle_workloads
                })
            
            # Memory optimization recommendations
            if resource_efficiency:
                for efficiency in resource_efficiency:
                    if efficiency.resource_type == "memory" and efficiency.efficiency_percent < 75:
                        # Calculate potential savings based on waste percentage
                        waste_cost = (efficiency.waste_percent / 100) * total_cost if total_cost > 0 else 0
                        recommendations.append({
                            "type": "memory_optimization",
                            "priority": "medium",
                            "description": f"Memory efficiency is {efficiency.efficiency_percent:.1f}%. Consider memory limits.",
                            "potential_savings": waste_cost,
                            "action": "optimize_memory_limits"
                        })
            
            optimization_data = {
                "recommendations": recommendations,
                "total_potential_savings": sum(r.get("potential_savings", 0) for r in recommendations),
                "priority_count": {
                    "high": len([r for r in recommendations if r["priority"] == "high"]),
                    "medium": len([r for r in recommendations if r["priority"] == "medium"]),
                    "low": len([r for r in recommendations if r["priority"] == "low"])
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Optimization analysis complete: {len(recommendations)} recommendations")
            return optimization_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get optimization data: {e}")
            return {"error": str(e), "status": "failed"}

    async def get_business_intelligence(self) -> Dict[str, Any]:
        """Fetch business intelligence data and KPIs"""
        try:
            logger.info("📊 Collecting business intelligence data...")
            
            # Get all data sources
            cluster_metrics = await self.get_cluster_metrics()
            cost_data = await self.get_cost_data()
            optimization_data = await self.get_optimization_data()
            
            # Calculate KPIs
            resource_utilization = (cluster_metrics.cpu_usage_percent + cluster_metrics.memory_usage_percent) / 2
            cost_efficiency = cost_data.get("efficiency_score", 0)
            potential_savings = optimization_data.get("total_potential_savings", 0)
            
            # Calculate ROI (simplified)
            total_cost = cost_data.get("total_monthly_cost", 0)
            roi_percentage = (potential_savings / max(total_cost, 1)) * 100 if total_cost > 0 else 0
            
            bi_data = {
                "kpis": {
                    "resource_utilization": resource_utilization,
                    "cost_efficiency": cost_efficiency,
                    "potential_savings": potential_savings,
                    "roi_percentage": roi_percentage,
                    "cluster_health": cluster_metrics.ready_nodes / max(cluster_metrics.total_nodes, 1) * 100
                },
                "trends": {
                    "cost_trend": "stable",  # Would be calculated from historical data
                    "utilization_trend": "increasing" if resource_utilization > 70 else "stable",
                    "efficiency_trend": "improving" if cost_efficiency > 80 else "declining"
                },
                "alerts": [
                    {"type": "high_cost", "message": "Monthly cost exceeds budget", "severity": "medium"} if total_cost > 1000 else None,
                    {"type": "low_efficiency", "message": "Resource efficiency below 70%", "severity": "high"} if cost_efficiency < 70 else None
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Remove None values from alerts
            bi_data["alerts"] = [alert for alert in bi_data["alerts"] if alert is not None]
            
            logger.info(f"✅ Business intelligence complete: {len(bi_data['alerts'])} alerts")
            return bi_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get business intelligence: {e}")
            return {"error": str(e), "status": "failed"}

    async def get_comprehensive_data(self) -> Dict[str, Any]:
        """Get comprehensive data snapshot for analysis and reporting"""
        try:
            logger.info("📋 Collecting comprehensive data snapshot...")
            
            # Collect all data in parallel
            tasks = [
                self.get_cluster_info(),
                self.get_nodes(),
                self.get_pods(),
                self.get_cluster_metrics(),
                self.get_cost_data(),
                self.get_optimization_data(),
                self.get_business_intelligence()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            data = {
                "cluster_info": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "nodes": results[1] if not isinstance(results[1], Exception) else [],
                "pods": results[2] if not isinstance(results[2], Exception) else [],
                "cluster_metrics": results[3] if not isinstance(results[3], Exception) else None,
                "cost_data": results[4] if not isinstance(results[4], Exception) else {"error": str(results[4])},
                "optimization_data": results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])},
                "business_intelligence": results[6] if not isinstance(results[6], Exception) else {"error": str(results[6])},
                "timestamp": datetime.utcnow().isoformat(),
                "data_freshness_seconds": (datetime.utcnow() - self._last_update).total_seconds()
            }
            
            logger.info("✅ Comprehensive data snapshot complete")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get comprehensive data: {e}")
            return {"error": str(e), "status": "failed"}

    def get_system_metrics(self) -> DataSystemMetrics:
        """Get metrics about the data system performance"""
        cache_hit_rate = len([k for k, v in self._cache.items() if self._is_cache_valid(k)]) / max(len(self._cache), 1)
        
        return DataSystemMetrics(
            total_clusters=1,  # Single cluster for now
            total_nodes=len(self._cache.get("nodes", {}).get("data", [])),
            total_pods=len(self._cache.get("pods_all", {}).get("data", [])),
            total_namespaces=len(set(pod.namespace for pod in self._cache.get("pods_all", {}).get("data", []))),
            data_freshness_seconds=int((datetime.utcnow() - self._last_update).total_seconds()),
            cache_hit_rate=cache_hit_rate,
            last_update=self._last_update,
            status="healthy" if cache_hit_rate > 0.5 else "degraded"
        )

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_entry = self._cache[cache_key]
        age = datetime.utcnow() - cache_entry["timestamp"]
        return age < self._cache_ttl

    def _cache_data(self, cache_key: str, data: Any):
        """Cache data with timestamp"""
        self._cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.info("🗑️ Data system cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache"""
        return {
            "cache_entries": len(self._cache),
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60,
            "cache_keys": list(self._cache.keys()),
            "valid_entries": len([k for k in self._cache.keys() if self._is_cache_valid(k)])
        } 