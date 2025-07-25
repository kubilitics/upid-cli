"""
UPID CLI - Mock API Server
Production-ready mock API server for customer demonstrations
Provides realistic API responses for immediate CLI functionality
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from .mock_data import (
    MockDataGenerator, generate_demo_data, get_demo_summary,
    MockCluster, MockPod, MockNode, MockMetrics, MockOptimization, MockCostBreakdown
)

logger = logging.getLogger(__name__)


class MockAPIResponse:
    """Mock API response wrapper"""
    
    def __init__(self, status_code: int, data: Any, success: bool = True, error_message: Optional[str] = None):
        self.status_code = status_code
        self.data = data
        self.success = success
        self.error_message = error_message
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "status_code": self.status_code,
            "success": self.success,
            "data": self.data,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert response to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class MockAPIServer:
    """Production-ready mock API server for UPID CLI demonstrations"""
    
    def __init__(self, scenario_type: str = "production"):
        """Initialize mock API server"""
        self.scenario_type = scenario_type
        self.data_generator = MockDataGenerator(seed=42)
        self.demo_data = generate_demo_data(scenario_type)
        self.logger = logging.getLogger(__name__)
        
        # Simulate realistic response times
        self.min_response_time = 0.1  # 100ms
        self.max_response_time = 0.5  # 500ms
    
    def _simulate_response_time(self):
        """Simulate realistic API response time"""
        time.sleep(random.uniform(self.min_response_time, self.max_response_time))
    
    def _get_cluster_by_id(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get cluster by ID from demo data"""
        for cluster in self.demo_data["clusters"]:
            if cluster["id"] == cluster_id:
                return cluster
        return None
    
    def _get_pods_by_cluster(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Get pods for a specific cluster"""
        return self.demo_data["pods"].get(cluster_id, [])
    
    def _get_nodes_by_cluster(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Get nodes for a specific cluster"""
        return self.demo_data["nodes"].get(cluster_id, [])
    
    def _get_optimizations_by_cluster(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Get optimizations for a specific cluster"""
        return self.demo_data["optimizations"].get(cluster_id, [])
    
    def _get_cost_breakdown_by_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get cost breakdown for a specific cluster"""
        return self.demo_data["cost_breakdowns"].get(cluster_id)
    
    def _get_metrics_by_cluster(self, cluster_id: str) -> List[Dict[str, Any]]:
        """Get metrics for a specific cluster"""
        return self.demo_data["metrics"].get(cluster_id, [])
    
    def authenticate(self, credentials: Dict[str, Any]) -> MockAPIResponse:
        """Mock authentication endpoint"""
        self._simulate_response_time()
        
        email = credentials.get("email", "")
        password = credentials.get("password", "")
        
        # Simulate authentication logic with specific valid credentials
        valid_credentials = {
            "admin@upid.io": "admin123",
            "demo@upid.io": "demo123",
            "test@upid.io": "test123"
        }
        
        if email in valid_credentials and valid_credentials[email] == password:
            return MockAPIResponse(
                status_code=200,
                data={
                    "access_token": f"mock_token_{random.randint(100000, 999999)}",
                    "refresh_token": f"mock_refresh_{random.randint(100000, 999999)}",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                    "user": {
                        "id": str(random.randint(1000, 9999)),
                        "email": email,
                        "name": "Demo User",
                        "role": "admin",
                        "organization": {
                            "id": str(random.randint(1000, 9999)),
                            "name": "Demo Organization"
                        }
                    }
                }
            )
        else:
            return MockAPIResponse(
                status_code=401,
                data=None,
                success=False,
                error_message="Invalid credentials"
            )
    
    def list_clusters(self, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock list clusters endpoint"""
        self._simulate_response_time()
        
        clusters = self.demo_data["clusters"]
        
        # Apply filters if provided
        if params:
            if "status" in params:
                clusters = [c for c in clusters if c["status"] == params["status"]]
            if "cloud_provider" in params:
                clusters = [c for c in clusters if c["cloud_provider"] == params["cloud_provider"]]
        
        return MockAPIResponse(
            status_code=200,
            data={
                "clusters": clusters,
                "total": len(clusters),
                "summary": {
                    "healthy": len([c for c in clusters if c["status"] == "healthy"]),
                    "warning": len([c for c in clusters if c["status"] == "warning"]),
                    "error": len([c for c in clusters if c["status"] == "error"])
                }
            }
        )
    
    def get_cluster(self, cluster_id: str) -> MockAPIResponse:
        """Mock get cluster endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        return MockAPIResponse(
            status_code=200,
            data=cluster
        )
    
    def analyze_cluster(self, cluster_id: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock analyze cluster endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        pods = self._get_pods_by_cluster(cluster_id)
        nodes = self._get_nodes_by_cluster(cluster_id)
        optimizations = self._get_optimizations_by_cluster(cluster_id)
        cost_breakdown = self._get_cost_breakdown_by_cluster(cluster_id)
        
        # Calculate analysis metrics
        total_pods = len(pods)
        idle_pods = len([p for p in pods if p.get("is_idle", False)])
        idle_percentage = (idle_pods / total_pods * 100) if total_pods > 0 else 0
        
        total_savings = sum(p.get("potential_monthly_savings", 0) for p in pods)
        monthly_cost = cost_breakdown.get("total_monthly_cost", 0) if cost_breakdown else 0
        savings_percentage = (total_savings / monthly_cost * 100) if monthly_cost > 0 else 0
        
        analysis_data = {
            "cluster": cluster,
            "summary": {
                "total_pods": total_pods,
                "idle_pods": idle_pods,
                "idle_percentage": round(idle_percentage, 2),
                "total_nodes": len(nodes),
                "monthly_cost": monthly_cost,
                "potential_savings": round(total_savings, 2),
                "savings_percentage": round(savings_percentage, 2)
            },
            "pods": pods[:20] if params and not params.get("detailed", False) else pods,  # Limit for non-detailed
            "nodes": nodes,
            "optimizations": optimizations[:10],  # Top 10 optimizations
            "cost_breakdown": cost_breakdown,
            "health_score": cluster.get("health_score", 0),
            "efficiency_score": cluster.get("efficiency_score", 0),
            "recommendations": [
                "Enable zero-pod scaling for development workloads",
                "Optimize resource requests based on usage patterns",
                "Consolidate underutilized nodes",
                "Implement cost allocation tags"
            ]
        }
        
        return MockAPIResponse(
            status_code=200,
            data=analysis_data
        )
    
    def find_idle_workloads(self, cluster_id: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock find idle workloads endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        pods = self._get_pods_by_cluster(cluster_id)
        idle_pods = [p for p in pods if p.get("is_idle", False)]
        
        # Apply confidence threshold if provided
        confidence_threshold = params.get("confidence_threshold", 0.7) if params else 0.7
        filtered_pods = [p for p in idle_pods if p.get("idle_confidence", 0) >= confidence_threshold]
        
        total_savings = sum(p.get("potential_monthly_savings", 0) for p in filtered_pods)
        
        return MockAPIResponse(
            status_code=200,
            data={
                "cluster": cluster,
                "idle_workloads": filtered_pods,
                "total_idle": len(filtered_pods),
                "total_savings": round(total_savings, 2),
                "confidence_threshold": confidence_threshold,
                "analysis": {
                    "cpu_threshold": 15.0,
                    "memory_threshold": 20.0,
                    "network_threshold": 1.0,  # MB
                    "idle_detection_method": "usage_pattern_analysis"
                }
            }
        )
    
    def analyze_costs(self, cluster_id: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock analyze costs endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        cost_breakdown = self._get_cost_breakdown_by_cluster(cluster_id)
        if not cost_breakdown:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cost data not available for cluster {cluster_id}"
            )
        
        return MockAPIResponse(
            status_code=200,
            data={
                "cluster": cluster,
                "cost_breakdown": cost_breakdown,
                "analysis": {
                    "cost_efficiency_score": random.uniform(60.0, 85.0),
                    "waste_percentage": round(cost_breakdown.get("waste_cost", 0) / cost_breakdown.get("total_monthly_cost", 1) * 100, 2),
                    "optimization_opportunities": len(self._get_optimizations_by_cluster(cluster_id)),
                    "trend": "increasing" if random.choice([True, False]) else "stable"
                }
            }
        )
    
    def get_optimization_strategies(self, cluster_id: str) -> MockAPIResponse:
        """Mock get optimization strategies endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        optimizations = self._get_optimizations_by_cluster(cluster_id)
        
        return MockAPIResponse(
            status_code=200,
            data={
                "cluster": cluster,
                "strategies": optimizations,
                "total_strategies": len(optimizations),
                "total_potential_savings": sum(o.get("potential_savings", 0) for o in optimizations),
                "priority_breakdown": {
                    "high": len([o for o in optimizations if o.get("priority") == "high"]),
                    "medium": len([o for o in optimizations if o.get("priority") == "medium"]),
                    "low": len([o for o in optimizations if o.get("priority") == "low"])
                }
            }
        )
    
    def simulate_optimization(self, cluster_id: str, strategy: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock simulate optimization endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        # Generate simulation results based on strategy
        if strategy == "zero_pod_scaling":
            potential_savings = random.uniform(200.0, 800.0)
            affected_pods = random.randint(5, 20)
            risk_level = "low"
        elif strategy == "resource_right_sizing":
            potential_savings = random.uniform(150.0, 600.0)
            affected_pods = random.randint(10, 30)
            risk_level = "medium"
        elif strategy == "node_consolidation":
            potential_savings = random.uniform(500.0, 2000.0)
            affected_pods = random.randint(20, 50)
            risk_level = "medium"
        else:
            potential_savings = random.uniform(100.0, 400.0)
            affected_pods = random.randint(5, 15)
            risk_level = "low"
        
        simulation_data = {
            "cluster": cluster,
            "strategy": strategy,
            "simulation_id": f"sim_{random.randint(100000, 999999)}",
            "results": {
                "potential_savings": round(potential_savings, 2),
                "affected_pods": affected_pods,
                "risk_level": risk_level,
                "confidence": random.uniform(0.75, 0.95),
                "estimated_duration": f"{random.randint(1, 4)} hours",
                "rollback_plan": "Automatic rollback available",
                "performance_impact": "Minimal"
            },
            "steps": [
                "Analyze current resource usage",
                "Identify optimization opportunities",
                "Apply changes in staging environment",
                "Monitor performance impact",
                "Roll out to production"
            ]
        }
        
        return MockAPIResponse(
            status_code=200,
            data=simulation_data
        )
    
    def apply_optimization(self, cluster_id: str, optimization_id: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock apply optimization endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        # Simulate optimization application
        auto_confirm = params.get("auto_confirm", False) if params else False
        
        if not auto_confirm:
            return MockAPIResponse(
                status_code=400,
                data=None,
                success=False,
                error_message="Auto-confirm required for optimization application"
            )
        
        application_data = {
            "cluster": cluster,
            "optimization_id": optimization_id,
            "status": "applied",
            "applied_at": datetime.utcnow().isoformat(),
            "estimated_savings": random.uniform(100.0, 500.0),
            "affected_resources": [f"pod-{random.randint(1, 100)}" for _ in range(random.randint(1, 5))],
            "rollback_available": True,
            "monitoring_enabled": True
        }
        
        return MockAPIResponse(
            status_code=200,
            data=application_data
        )
    
    def get_metrics(self, cluster_id: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock get metrics endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        metrics = self._get_metrics_by_cluster(cluster_id)
        
        # Apply time range filter if provided
        if params and "time_range" in params:
            hours = {"1h": 1, "6h": 6, "24h": 24, "7d": 168}.get(params["time_range"], 24)
            metrics = metrics[:hours]
        
        return MockAPIResponse(
            status_code=200,
            data={
                "cluster": cluster,
                "metrics": metrics,
                "summary": {
                    "avg_cpu_usage": round(sum(m.get("cpu_usage_percent", 0) for m in metrics) / len(metrics), 2) if metrics else 0,
                    "avg_memory_usage": round(sum(m.get("memory_usage_percent", 0) for m in metrics) / len(metrics), 2) if metrics else 0,
                    "total_metrics": len(metrics)
                }
            }
        )
    
    def generate_report(self, cluster_id: str, report_type: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock generate report endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        report_id = f"report_{random.randint(100000, 999999)}"
        
        if report_type == "cost":
            cost_breakdown = self._get_cost_breakdown_by_cluster(cluster_id)
            report_data = {
                "report_type": "cost",
                "cluster": cluster,
                "cost_breakdown": cost_breakdown,
                "recommendations": [
                    "Enable zero-pod scaling for development workloads",
                    "Optimize resource requests based on usage patterns",
                    "Consolidate underutilized nodes"
                ]
            }
        elif report_type == "performance":
            metrics = self._get_metrics_by_cluster(cluster_id)
            report_data = {
                "report_type": "performance",
                "cluster": cluster,
                "metrics": metrics,
                "performance_score": random.uniform(70.0, 95.0),
                "bottlenecks": [
                    "High CPU usage on worker nodes",
                    "Memory pressure on control plane",
                    "Network congestion during peak hours"
                ]
            }
        else:  # optimization
            optimizations = self._get_optimizations_by_cluster(cluster_id)
            report_data = {
                "report_type": "optimization",
                "cluster": cluster,
                "optimizations": optimizations,
                "total_potential_savings": sum(o.get("potential_savings", 0) for o in optimizations),
                "implementation_priority": "high" if random.choice([True, False]) else "medium"
            }
        
        report_data["report_id"] = report_id
        report_data["generated_at"] = datetime.utcnow().isoformat()
        
        return MockAPIResponse(
            status_code=200,
            data=report_data
        )
    
    def get_ai_insights(self, cluster_id: str, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
        """Mock AI insights endpoint"""
        self._simulate_response_time()
        
        cluster = self._get_cluster_by_id(cluster_id)
        if not cluster:
            return MockAPIResponse(
                status_code=404,
                data=None,
                success=False,
                error_message=f"Cluster {cluster_id} not found"
            )
        
        insights = [
            {
                "type": "cost_optimization",
                "title": "High idle workload detected",
                "description": "Found 15 idle pods that could be scaled to zero during off-hours",
                "confidence": 0.92,
                "potential_savings": random.uniform(200.0, 500.0),
                "priority": "high"
            },
            {
                "type": "performance",
                "title": "Resource underutilization",
                "description": "CPU usage is consistently below 30% on 8 nodes",
                "confidence": 0.87,
                "potential_savings": random.uniform(300.0, 800.0),
                "priority": "medium"
            },
            {
                "type": "security",
                "title": "Security best practices",
                "description": "Consider implementing network policies for better security",
                "confidence": 0.78,
                "potential_savings": 0.0,
                "priority": "low"
            }
        ]
        
        return MockAPIResponse(
            status_code=200,
            data={
                "cluster": cluster,
                "insights": insights,
                "total_insights": len(insights),
                "ai_model_version": "v2.1.0",
                "last_updated": datetime.utcnow().isoformat()
            }
        )


# Global mock API server instance
mock_api_server = MockAPIServer("production")


def get_mock_api_server(scenario_type: str = "production") -> MockAPIServer:
    """Get the global mock API server instance"""
    if scenario_type == "production":
        return mock_api_server
    else:
        return MockAPIServer(scenario_type)


def mock_api_call(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> MockAPIResponse:
    """Make a mock API call to the specified endpoint"""
    server = get_mock_api_server()
    
    # Route to appropriate method based on endpoint
    if endpoint == "/api/v1/auth/login" and method == "POST":
        return server.authenticate(data or {})
    elif endpoint == "/api/v1/clusters" and method == "GET":
        return server.list_clusters(params)
    elif endpoint.startswith("/api/v1/clusters/") and method == "GET":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.get_cluster(cluster_id)
    elif endpoint.startswith("/api/v1/analyze/cluster/") and method == "POST":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.analyze_cluster(cluster_id, data)
    elif endpoint.startswith("/api/v1/analyze/idle/") and method == "POST":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.find_idle_workloads(cluster_id, data)
    elif endpoint.startswith("/api/v1/analyze/costs/") and method == "POST":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.analyze_costs(cluster_id, data)
    elif endpoint.startswith("/api/v1/optimize/strategies/") and method == "GET":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.get_optimization_strategies(cluster_id)
    elif endpoint.startswith("/api/v1/optimize/simulate/") and method == "POST":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        strategy = data.get("strategy", "zero_pod_scaling") if data else "zero_pod_scaling"
        return server.simulate_optimization(cluster_id, strategy, data)
    elif endpoint.startswith("/api/v1/optimize/apply/") and method == "POST":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        optimization_id = data.get("optimization_id", "opt_123") if data else "opt_123"
        return server.apply_optimization(cluster_id, optimization_id, data)
    elif endpoint.startswith("/api/v1/metrics/") and method == "GET":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.get_metrics(cluster_id, params)
    elif endpoint.startswith("/api/v1/reports/") and method == "POST":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        report_type = data.get("report_type", "cost") if data else "cost"
        return server.generate_report(cluster_id, report_type, data)
    elif endpoint.startswith("/api/v1/ai/insights/") and method == "GET":
        # Extract cluster ID from URL path
        parts = endpoint.split("/")
        cluster_id = parts[-1] if parts[-1] else parts[-2]
        return server.get_ai_insights(cluster_id, params)
    else:
        return MockAPIResponse(
            status_code=404,
            data=None,
            success=False,
            error_message=f"Endpoint {endpoint} not found"
        ) 