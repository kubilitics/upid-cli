"""
UPID CLI - Mock Data System
Production-ready mock data generator for customer demonstrations
Provides realistic Kubernetes cluster data for immediate value demonstration
"""

import logging
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class ClusterStatus(str, Enum):
    """Cluster status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CONNECTING = "connecting"
    DISABLED = "disabled"


class CloudProvider(str, Enum):
    """Cloud provider enumeration"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "on-premise"


class WorkloadType(str, Enum):
    """Workload type enumeration"""
    DEPLOYMENT = "Deployment"
    STATEFULSET = "StatefulSet"
    DAEMONSET = "DaemonSet"
    JOB = "Job"
    CRONJOB = "CronJob"


class PodStatus(str, Enum):
    """Pod status enumeration"""
    RUNNING = "Running"
    PENDING = "Pending"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    UNKNOWN = "Unknown"


@dataclass
class MockCluster:
    """Mock Kubernetes cluster data"""
    id: str
    name: str
    status: ClusterStatus
    cloud_provider: CloudProvider
    region: str
    kubernetes_version: str
    node_count: int
    pod_count: int
    namespace_count: int
    health_score: float
    efficiency_score: float
    monthly_cost: float
    created_at: datetime
    last_seen: datetime
    tags: Dict[str, str]


@dataclass
class MockPod:
    """Mock Kubernetes pod data"""
    name: str
    namespace: str
    status: PodStatus
    node_name: str
    workload_type: WorkloadType
    workload_name: str
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str
    cpu_usage_percent: float
    memory_usage_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    restart_count: int
    age: timedelta
    labels: Dict[str, str]
    is_idle: bool
    idle_confidence: float
    estimated_monthly_cost: float
    potential_monthly_savings: float 


@dataclass
class MockNode:
    """Mock Kubernetes node data"""
    name: str
    status: str
    roles: List[str]
    version: str
    os_image: str
    kernel_version: str
    container_runtime: str
    cpu_capacity: str
    memory_capacity: str
    cpu_allocatable: str
    memory_allocatable: str
    cpu_usage_percent: float
    memory_usage_percent: float
    pod_count: int
    conditions: List[Dict[str, Any]]
    labels: Dict[str, str]
    created_at: datetime


@dataclass
class MockMetrics:
    """Mock metrics data"""
    timestamp: datetime
    cpu_usage_cores: float
    cpu_usage_percent: float
    memory_usage_bytes: int
    memory_usage_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    storage_usage_bytes: int
    pod_count: int
    node_count: int


@dataclass
class MockOptimization:
    """Mock optimization recommendation"""
    id: str
    type: str
    title: str
    description: str
    priority: str
    potential_savings: float
    risk_level: str
    confidence: float
    affected_resources: List[str]
    implementation_steps: List[str]
    estimated_duration: str
    created_at: datetime


@dataclass
class MockCostBreakdown:
    """Mock cost breakdown data"""
    cluster_id: str
    total_monthly_cost: float
    compute_cost: float
    storage_cost: float
    network_cost: float
    waste_cost: float
    optimization_potential: float
    cost_by_namespace: Dict[str, float]
    cost_by_workload: Dict[str, float]
    cost_trend_30_days: List[Dict[str, Any]]
    recommendations: List[str]


class MockDataGenerator:
    """Production-ready mock data generator for UPID CLI demonstrations"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize mock data generator"""
        if seed:
            random.seed(seed)
        self.logger = logging.getLogger(__name__)
        self._load_realistic_data()
    
    def _load_realistic_data(self):
        """Load realistic data patterns for mock generation"""
        self.cluster_names = [
            "production-cluster-01", "staging-cluster-01", "development-cluster-01",
            "production-cluster-02", "staging-cluster-02", "development-cluster-02",
            "production-cluster-03", "staging-cluster-03", "development-cluster-03"
        ]
        
        self.workload_names = [
            "web-frontend", "api-backend", "database", "cache-redis", "monitoring",
            "logging", "ingress-controller", "cert-manager", "prometheus", "grafana",
            "elasticsearch", "kibana", "jenkins", "sonarqube", "nexus",
            "postgres", "mysql", "mongodb", "rabbitmq", "kafka",
            "nginx", "apache", "tomcat", "spring-boot", "django",
            "flask", "fastapi", "express", "react", "vue"
        ]
        
        self.namespaces = [
            "production", "staging", "development", "monitoring", "logging",
            "ingress", "cert-manager", "kube-system", "default", "tools"
        ]
        
        self.node_names = [
            "worker-node-01", "worker-node-02", "worker-node-03", "worker-node-04",
            "worker-node-05", "worker-node-06", "worker-node-07", "worker-node-08",
            "control-plane-01", "control-plane-02", "control-plane-03"
        ]
    
    def generate_clusters(self, count: int = 3) -> List[MockCluster]:
        """Generate realistic mock clusters"""
        clusters = []
        
        for i in range(count):
            cluster_id = str(uuid.uuid4())
            name = self.cluster_names[i % len(self.cluster_names)]
            
            # Determine cluster characteristics based on name
            if "production" in name:
                status = ClusterStatus.HEALTHY
                health_score = random.uniform(85.0, 98.0)
                efficiency_score = random.uniform(65.0, 85.0)
                monthly_cost = random.uniform(5000.0, 15000.0)
                node_count = random.randint(8, 20)
                pod_count = random.randint(50, 200)
                namespace_count = random.randint(8, 15)
                cloud_provider = random.choice([CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE])
            elif "staging" in name:
                status = ClusterStatus.HEALTHY
                health_score = random.uniform(75.0, 90.0)
                efficiency_score = random.uniform(45.0, 70.0)
                monthly_cost = random.uniform(2000.0, 6000.0)
                node_count = random.randint(4, 12)
                pod_count = random.randint(20, 80)
                namespace_count = random.randint(5, 10)
                cloud_provider = random.choice([CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE])
            else:  # development
                status = ClusterStatus.WARNING
                health_score = random.uniform(60.0, 80.0)
                efficiency_score = random.uniform(30.0, 55.0)
                monthly_cost = random.uniform(800.0, 2500.0)
                node_count = random.randint(2, 6)
                pod_count = random.randint(10, 40)
                namespace_count = random.randint(3, 8)
                cloud_provider = random.choice([CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE, CloudProvider.ON_PREMISE])
            
            cluster = MockCluster(
                id=cluster_id,
                name=name,
                status=status,
                cloud_provider=cloud_provider,
                region=random.choice(["us-west-2", "us-east-1", "eu-west-1", "ap-southeast-1"]),
                kubernetes_version=f"1.{random.randint(24, 28)}.{random.randint(0, 10)}",
                node_count=node_count,
                pod_count=pod_count,
                namespace_count=namespace_count,
                health_score=health_score,
                efficiency_score=efficiency_score,
                monthly_cost=monthly_cost,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                last_seen=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
                tags={
                    "environment": "production" if "production" in name else "staging" if "staging" in name else "development",
                    "team": random.choice(["platform", "backend", "frontend", "devops", "data"]),
                    "cost-center": f"CC-{random.randint(1000, 9999)}"
                }
            )
            clusters.append(cluster)
        
        return clusters
    
    def generate_pods(self, cluster_id: str, count: int = 50) -> List[MockPod]:
        """Generate realistic mock pods"""
        pods = []
        
        for i in range(count):
            # Determine pod characteristics
            workload_type = random.choice(list(WorkloadType))
            workload_name = random.choice(self.workload_names)
            namespace = random.choice(self.namespaces)
            node_name = random.choice(self.node_names)
            
            # Generate realistic resource specifications
            cpu_request = f"{random.randint(100, 2000)}m"
            cpu_limit = f"{random.randint(200, 4000)}m"
            memory_request = f"{random.randint(128, 2048)}Mi"
            memory_limit = f"{random.randint(256, 4096)}Mi"
            
            # Generate realistic usage patterns
            cpu_usage_percent = random.uniform(5.0, 85.0)
            memory_usage_percent = random.uniform(10.0, 90.0)
            
            # Determine if pod is idle based on usage patterns
            is_idle = cpu_usage_percent < 15.0 and memory_usage_percent < 20.0
            idle_confidence = random.uniform(0.7, 0.95) if is_idle else random.uniform(0.1, 0.3)
            
            # Calculate costs and savings
            estimated_monthly_cost = random.uniform(50.0, 500.0)
            potential_monthly_savings = estimated_monthly_cost * 0.6 if is_idle else 0.0
            
            pod = MockPod(
                name=f"{workload_name}-{random.randint(1, 999)}",
                namespace=namespace,
                status=PodStatus.RUNNING,
                node_name=node_name,
                workload_type=workload_type,
                workload_name=workload_name,
                cpu_request=cpu_request,
                cpu_limit=cpu_limit,
                memory_request=memory_request,
                memory_limit=memory_limit,
                cpu_usage_percent=cpu_usage_percent,
                memory_usage_percent=memory_usage_percent,
                network_rx_bytes=random.randint(1024, 1073741824),  # 1KB to 1GB
                network_tx_bytes=random.randint(512, 536870912),     # 512B to 512MB
                restart_count=random.randint(0, 5),
                age=timedelta(days=random.randint(1, 30)),
                labels={
                    "app": workload_name,
                    "environment": "production" if "production" in namespace else "staging" if "staging" in namespace else "development",
                    "team": random.choice(["platform", "backend", "frontend", "devops", "data"])
                },
                is_idle=is_idle,
                idle_confidence=idle_confidence,
                estimated_monthly_cost=estimated_monthly_cost,
                potential_monthly_savings=potential_monthly_savings
            )
            pods.append(pod)
        
        return pods
    
    def generate_nodes(self, count: int = 8) -> List[MockNode]:
        """Generate realistic mock nodes"""
        nodes = []
        
        for i in range(count):
            node_name = self.node_names[i % len(self.node_names)]
            
            # Generate realistic node specifications
            cpu_capacity = f"{random.randint(4, 32)}"
            memory_capacity = f"{random.randint(8, 128)}Gi"
            cpu_allocatable = f"{random.randint(3, 30)}"
            memory_allocatable = f"{random.randint(6, 120)}Gi"
            
            # Generate realistic usage patterns
            cpu_usage_percent = random.uniform(20.0, 80.0)
            memory_usage_percent = random.uniform(30.0, 85.0)
            pod_count = random.randint(5, 110)
            
            node = MockNode(
                name=node_name,
                status="Ready",
                roles=["worker"] if "worker" in node_name else ["control-plane"],
                version=f"1.{random.randint(24, 28)}.{random.randint(0, 10)}",
                os_image="Ubuntu 20.04.3 LTS",
                kernel_version="5.4.0-74-generic",
                container_runtime="containerd://1.6.8",
                cpu_capacity=cpu_capacity,
                memory_capacity=memory_capacity,
                cpu_allocatable=cpu_allocatable,
                memory_allocatable=memory_allocatable,
                cpu_usage_percent=cpu_usage_percent,
                memory_usage_percent=memory_usage_percent,
                pod_count=pod_count,
                conditions=[
                    {"type": "Ready", "status": "True", "lastHeartbeatTime": datetime.utcnow().isoformat()},
                    {"type": "MemoryPressure", "status": "False", "lastHeartbeatTime": datetime.utcnow().isoformat()},
                    {"type": "DiskPressure", "status": "False", "lastHeartbeatTime": datetime.utcnow().isoformat()},
                    {"type": "PIDPressure", "status": "False", "lastHeartbeatTime": datetime.utcnow().isoformat()}
                ],
                labels={
                    "node-role.kubernetes.io/worker": "true" if "worker" in node_name else "false",
                    "node-role.kubernetes.io/control-plane": "true" if "control-plane" in node_name else "false",
                    "kubernetes.io/os": "linux",
                    "kubernetes.io/arch": "amd64"
                },
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            nodes.append(node)
        
        return nodes
    
    def generate_metrics(self, cluster_id: str, hours: int = 24) -> List[MockMetrics]:
        """Generate realistic mock metrics over time"""
        metrics = []
        end_time = datetime.utcnow()
        
        for i in range(hours):
            timestamp = end_time - timedelta(hours=i)
            
            # Generate realistic metrics with some variation
            base_cpu_usage = random.uniform(40.0, 70.0)
            base_memory_usage = random.uniform(50.0, 80.0)
            
            # Add some time-based variation (lower usage at night)
            hour_of_day = timestamp.hour
            if 2 <= hour_of_day <= 6:  # Night time
                cpu_multiplier = 0.3
                memory_multiplier = 0.4
            elif 9 <= hour_of_day <= 17:  # Business hours
                cpu_multiplier = 1.2
                memory_multiplier = 1.1
            else:  # Evening
                cpu_multiplier = 0.8
                memory_multiplier = 0.9
            
            metric = MockMetrics(
                timestamp=timestamp,
                cpu_usage_cores=random.uniform(2.0, 8.0) * cpu_multiplier,
                cpu_usage_percent=base_cpu_usage * cpu_multiplier,
                memory_usage_bytes=random.randint(8589934592, 34359738368),  # 8GB to 32GB
                memory_usage_percent=base_memory_usage * memory_multiplier,
                network_rx_bytes=random.randint(1073741824, 10737418240),  # 1GB to 10GB
                network_tx_bytes=random.randint(536870912, 5368709120),     # 512MB to 5GB
                storage_usage_bytes=random.randint(21474836480, 107374182400),  # 20GB to 100GB
                pod_count=random.randint(30, 150),
                node_count=random.randint(6, 12)
            )
            metrics.append(metric)
        
        return metrics
    
    def generate_optimizations(self, cluster_id: str, count: int = 10) -> List[MockOptimization]:
        """Generate realistic mock optimization recommendations"""
        optimizations = []
        
        optimization_types = [
            "zero_pod_scaling", "resource_right_sizing", "node_consolidation",
            "cost_optimization", "performance_optimization", "security_optimization"
        ]
        
        for i in range(count):
            opt_type = random.choice(optimization_types)
            
            if opt_type == "zero_pod_scaling":
                title = "Enable zero-pod scaling for idle workloads"
                description = "Scale idle pods to zero during off-hours to reduce costs"
                potential_savings = random.uniform(200.0, 800.0)
                risk_level = "low"
                confidence = random.uniform(0.85, 0.95)
            elif opt_type == "resource_right_sizing":
                title = "Optimize resource requests and limits"
                description = "Adjust CPU and memory requests based on actual usage patterns"
                potential_savings = random.uniform(150.0, 600.0)
                risk_level = "medium"
                confidence = random.uniform(0.75, 0.90)
            elif opt_type == "node_consolidation":
                title = "Consolidate underutilized nodes"
                description = "Migrate pods to reduce node count and infrastructure costs"
                potential_savings = random.uniform(500.0, 2000.0)
                risk_level = "medium"
                confidence = random.uniform(0.70, 0.85)
            else:
                title = f"Optimize {opt_type.replace('_', ' ')}"
                description = f"Apply {opt_type.replace('_', ' ')} optimizations"
                potential_savings = random.uniform(100.0, 400.0)
                risk_level = random.choice(["low", "medium", "high"])
                confidence = random.uniform(0.60, 0.85)
            
            optimization = MockOptimization(
                id=str(uuid.uuid4()),
                type=opt_type,
                title=title,
                description=description,
                priority=random.choice(["high", "medium", "low"]),
                potential_savings=potential_savings,
                risk_level=risk_level,
                confidence=confidence,
                affected_resources=[f"pod-{random.randint(1, 100)}" for _ in range(random.randint(1, 5))],
                implementation_steps=[
                    "Analyze current resource usage",
                    "Identify optimization opportunities",
                    "Apply changes in staging environment",
                    "Monitor performance impact",
                    "Roll out to production"
                ],
                estimated_duration=f"{random.randint(1, 4)} hours",
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            optimizations.append(optimization)
        
        return optimizations
    
    def generate_cost_breakdown(self, cluster_id: str) -> MockCostBreakdown:
        """Generate realistic mock cost breakdown"""
        total_monthly_cost = random.uniform(2000.0, 12000.0)
        
        # Calculate cost components
        compute_cost = total_monthly_cost * random.uniform(0.6, 0.8)
        storage_cost = total_monthly_cost * random.uniform(0.1, 0.2)
        network_cost = total_monthly_cost * random.uniform(0.05, 0.15)
        waste_cost = total_monthly_cost * random.uniform(0.1, 0.3)
        optimization_potential = waste_cost * random.uniform(0.6, 0.9)
        
        # Generate cost by namespace
        cost_by_namespace = {}
        for namespace in self.namespaces[:6]:  # Use first 6 namespaces
            cost_by_namespace[namespace] = random.uniform(100.0, 2000.0)
        
        # Generate cost by workload type
        cost_by_workload = {
            "Deployment": total_monthly_cost * random.uniform(0.4, 0.6),
            "StatefulSet": total_monthly_cost * random.uniform(0.2, 0.3),
            "DaemonSet": total_monthly_cost * random.uniform(0.1, 0.2),
            "Job": total_monthly_cost * random.uniform(0.05, 0.1)
        }
        
        # Generate 30-day cost trend
        cost_trend_30_days = []
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=30-i)
            cost = total_monthly_cost + random.uniform(-500.0, 500.0)
            cost_trend_30_days.append({
                "date": date.strftime("%Y-%m-%d"),
                "cost": round(cost, 2)
            })
        
        # Generate recommendations
        recommendations = [
            "Enable zero-pod scaling for development workloads",
            "Optimize resource requests based on usage patterns",
            "Consolidate underutilized nodes",
            "Implement cost allocation tags",
            "Set up cost alerts and budgets"
        ]
        
        return MockCostBreakdown(
            cluster_id=cluster_id,
            total_monthly_cost=total_monthly_cost,
            compute_cost=compute_cost,
            storage_cost=storage_cost,
            network_cost=network_cost,
            waste_cost=waste_cost,
            optimization_potential=optimization_potential,
            cost_by_namespace=cost_by_namespace,
            cost_by_workload=cost_by_workload,
            cost_trend_30_days=cost_trend_30_days,
            recommendations=recommendations
        )
    
    def generate_demo_scenario(self, scenario_type: str = "production") -> Dict[str, Any]:
        """Generate complete demo scenario data"""
        if scenario_type == "production":
            cluster_count = 3
            pods_per_cluster = 150
            nodes_per_cluster = 12
        elif scenario_type == "staging":
            cluster_count = 2
            pods_per_cluster = 80
            nodes_per_cluster = 8
        else:  # development
            cluster_count = 1
            pods_per_cluster = 40
            nodes_per_cluster = 4
        
        clusters = self.generate_clusters(cluster_count)
        scenario_data = {
            "scenario_type": scenario_type,
            "clusters": [asdict(cluster) for cluster in clusters],
            "pods": {},
            "nodes": {},
            "metrics": {},
            "optimizations": {},
            "cost_breakdowns": {}
        }
        
        for cluster in clusters:
            cluster_id = cluster.id
            scenario_data["pods"][cluster_id] = [asdict(pod) for pod in self.generate_pods(cluster_id, pods_per_cluster)]
            scenario_data["nodes"][cluster_id] = [asdict(node) for node in self.generate_nodes(nodes_per_cluster)]
            scenario_data["metrics"][cluster_id] = [asdict(metric) for metric in self.generate_metrics(cluster_id, 24)]
            scenario_data["optimizations"][cluster_id] = [asdict(opt) for opt in self.generate_optimizations(cluster_id, 15)]
            scenario_data["cost_breakdowns"][cluster_id] = asdict(self.generate_cost_breakdown(cluster_id))
        
        return scenario_data
    
    def get_summary_stats(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for demo scenario"""
        total_clusters = len(scenario_data["clusters"])
        total_pods = sum(len(pods) for pods in scenario_data["pods"].values())
        total_nodes = sum(len(nodes) for nodes in scenario_data["nodes"].values())
        
        # Calculate idle pods
        idle_pods = 0
        total_savings_potential = 0.0
        
        for cluster_pods in scenario_data["pods"].values():
            for pod in cluster_pods:
                if pod.get("is_idle", False):
                    idle_pods += 1
                    total_savings_potential += pod.get("potential_monthly_savings", 0.0)
        
        # Calculate total monthly cost
        total_monthly_cost = sum(
            breakdown.get("total_monthly_cost", 0.0) 
            for breakdown in scenario_data["cost_breakdowns"].values()
        )
        
        return {
            "total_clusters": total_clusters,
            "total_pods": total_pods,
            "total_nodes": total_nodes,
            "idle_pods": idle_pods,
            "idle_pod_percentage": round((idle_pods / total_pods) * 100, 2) if total_pods > 0 else 0,
            "total_monthly_cost": round(total_monthly_cost, 2),
            "total_savings_potential": round(total_savings_potential, 2),
            "savings_percentage": round((total_savings_potential / total_monthly_cost) * 100, 2) if total_monthly_cost > 0 else 0
        }


# Global mock data generator instance
mock_data_generator = MockDataGenerator(seed=42)


def get_mock_data_generator() -> MockDataGenerator:
    """Get the global mock data generator instance"""
    return mock_data_generator


def generate_demo_data(scenario_type: str = "production") -> Dict[str, Any]:
    """Generate demo data for the specified scenario"""
    generator = get_mock_data_generator()
    return generator.generate_demo_scenario(scenario_type)


def get_demo_summary(scenario_type: str = "production") -> Dict[str, Any]:
    """Get summary statistics for demo scenario"""
    generator = get_mock_data_generator()
    scenario_data = generator.generate_demo_scenario(scenario_type)
    return generator.get_summary_stats(scenario_data) 