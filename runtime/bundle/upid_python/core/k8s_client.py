"""
UPID CLI - Native Kubernetes Client
Enterprise-grade Kubernetes API client wrapper for UPID platform
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import yaml

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.client import Configuration
from kubernetes.stream import stream
import urllib3

# Disable SSL warnings for development clusters
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


@dataclass
class ClusterConfig:
    """Kubernetes cluster configuration"""
    name: str
    endpoint: str
    token: Optional[str] = None
    kubeconfig_path: Optional[str] = None
    context: Optional[str] = None
    verify_ssl: bool = True
    timeout: int = 30
    
    
@dataclass
class NodeInfo:
    """Kubernetes node information"""
    name: str
    status: str
    roles: List[str]
    version: str
    os_image: str
    kernel_version: str
    container_runtime: str
    capacity: Dict[str, str]
    allocatable: Dict[str, str]
    conditions: List[Dict[str, Any]]
    labels: Dict[str, str]
    annotations: Dict[str, str]
    created_at: datetime


@dataclass
class PodInfo:
    """Kubernetes pod information"""
    name: str
    namespace: str
    status: str
    phase: str
    node_name: Optional[str]
    pod_ip: Optional[str]
    host_ip: Optional[str]
    containers: List[Dict[str, Any]]
    labels: Dict[str, str]
    annotations: Dict[str, str]
    created_at: datetime
    resource_requests: Dict[str, str]
    resource_limits: Dict[str, str]


@dataclass
class ClusterMetrics:
    """Kubernetes cluster metrics"""
    cluster_name: str
    total_nodes: int
    ready_nodes: int
    total_pods: int
    running_pods: int
    total_namespaces: int
    cpu_capacity: str
    memory_capacity: str
    cpu_allocatable: str
    memory_allocatable: str
    cpu_usage_percent: float
    memory_usage_percent: float
    timestamp: datetime


class KubernetesClientError(Exception):
    """Custom exception for Kubernetes client errors"""
    pass


class KubernetesClient:
    """
    Native Kubernetes API client wrapper for UPID platform
    
    Provides enterprise-grade Kubernetes integration with:
    - Connection pooling and retry logic
    - Comprehensive resource management
    - Metrics collection and analysis
    - Multi-cluster support
    - Secure authentication handling
    """
    
    def __init__(self, cluster_config: Optional[ClusterConfig] = None):
        """
        Initialize Kubernetes client
        
        Args:
            cluster_config: Optional cluster configuration. If None, uses default kubeconfig
        """
        self.cluster_config = cluster_config
        self.api_client: Optional[client.ApiClient] = None
        self.core_v1: Optional[client.CoreV1Api] = None
        self.apps_v1: Optional[client.AppsV1Api] = None
        self.networking_v1: Optional[client.NetworkingV1Api] = None
        self.rbac_v1: Optional[client.RbacAuthorizationV1Api] = None
        self.metrics_v1beta1: Optional[client.CustomObjectsApi] = None
        self._connected = False
        
        logger.info("🔧 Initializing UPID Kubernetes client")
        
    async def connect(self) -> bool:
        """
        Connect to Kubernetes cluster
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("🔗 Connecting to Kubernetes cluster...")
            
            if self.cluster_config:
                await self._connect_with_config()
            else:
                await self._connect_with_kubeconfig()
            
            # Initialize API clients
            self.core_v1 = client.CoreV1Api(self.api_client)
            self.apps_v1 = client.AppsV1Api(self.api_client)
            self.networking_v1 = client.NetworkingV1Api(self.api_client)
            self.rbac_v1 = client.RbacAuthorizationV1Api(self.api_client)
            self.metrics_v1beta1 = client.CustomObjectsApi(self.api_client)
            
            # Test connection
            await self._test_connection()
            
            self._connected = True
            logger.info("✅ Successfully connected to Kubernetes cluster")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kubernetes cluster: {e}")
            self._connected = False
            return False
    
    async def _connect_with_config(self):
        """Connect using provided cluster configuration"""
        if not self.cluster_config:
            raise KubernetesClientError("Cluster configuration is required")
        
        # Create custom configuration
        configuration = Configuration()
        configuration.host = self.cluster_config.endpoint
        
        if self.cluster_config.token:
            configuration.api_key = {"authorization": f"Bearer {self.cluster_config.token}"}
        
        configuration.verify_ssl = self.cluster_config.verify_ssl
        
        if not self.cluster_config.verify_ssl:
            configuration.ssl_ca_cert = None
            
        # Create API client with custom configuration
        self.api_client = client.ApiClient(configuration)
        
    async def _connect_with_kubeconfig(self):
        """Connect using kubeconfig file"""
        try:
            # Try to load in-cluster config first (for pods running in K8s)
            config.load_incluster_config()
            logger.info("🏠 Using in-cluster Kubernetes configuration")
        except config.ConfigException:
            try:
                # Load from kubeconfig file
                if self.cluster_config and self.cluster_config.kubeconfig_path:
                    config.load_kube_config(
                        config_file=self.cluster_config.kubeconfig_path,
                        context=self.cluster_config.context
                    )
                else:
                    config.load_kube_config(context=self.cluster_config.context if self.cluster_config else None)
                logger.info("📁 Using kubeconfig file")
            except config.ConfigException as e:
                raise KubernetesClientError(f"Could not load Kubernetes configuration: {e}")
        
        self.api_client = client.ApiClient()
    
    async def _test_connection(self):
        """Test connection to Kubernetes cluster"""
        try:
            # Simple API call to test connectivity
            await asyncio.get_event_loop().run_in_executor(
                None, self.core_v1.get_api_resources
            )
        except ApiException as e:
            raise KubernetesClientError(f"Failed to connect to Kubernetes API: {e}")
    
    def _ensure_connected(self):
        """Ensure client is connected to cluster"""
        if not self._connected:
            raise KubernetesClientError("Not connected to Kubernetes cluster. Call connect() first.")
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get comprehensive cluster information
        
        Returns:
            Dict containing cluster info, version, and basic metrics
        """
        self._ensure_connected()
        
        try:
            logger.info("📊 Retrieving cluster information...")
            
            # Get cluster version
            version_info = await asyncio.get_event_loop().run_in_executor(
                None, self.core_v1.get_api_versions
            )
            
            # Get nodes
            nodes = await self.list_nodes()
            
            # Get namespaces
            namespaces = await asyncio.get_event_loop().run_in_executor(
                None, self.core_v1.list_namespace
            )
            
            # Calculate cluster metrics
            total_cpu_capacity = 0
            total_memory_capacity = 0
            ready_nodes = 0
            
            for node in nodes:
                if node.status.lower() == "ready":
                    ready_nodes += 1
                
                # Parse CPU and memory capacity
                cpu_capacity = node.capacity.get("cpu", "0")
                memory_capacity = node.capacity.get("memory", "0Ki")
                
                # Convert to standard units (millicores for CPU, bytes for memory)
                try:
                    total_cpu_capacity += self._parse_cpu_quantity(cpu_capacity)
                    total_memory_capacity += self._parse_memory_quantity(memory_capacity)
                except ValueError:
                    logger.warning(f"Could not parse capacity for node {node.name}")
            
            cluster_info = {
                "cluster_name": self.cluster_config.name if self.cluster_config else "default",
                "api_versions": version_info.versions,
                "total_nodes": len(nodes),
                "ready_nodes": ready_nodes,
                "total_namespaces": len(namespaces.items),
                "cpu_capacity_millicores": total_cpu_capacity,
                "memory_capacity_bytes": total_memory_capacity,
                "kubernetes_version": nodes[0].version if nodes else "unknown",
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"✅ Retrieved cluster info: {len(nodes)} nodes, {len(namespaces.items)} namespaces")
            return cluster_info
            
        except ApiException as e:
            logger.error(f"❌ Failed to get cluster info: {e}")
            raise KubernetesClientError(f"Failed to get cluster info: {e}")
    
    async def list_nodes(self) -> List[NodeInfo]:
        """
        List all nodes in the cluster
        
        Returns:
            List of NodeInfo objects
        """
        self._ensure_connected()
        
        try:
            logger.info("📋 Listing cluster nodes...")
            
            nodes_list = await asyncio.get_event_loop().run_in_executor(
                None, self.core_v1.list_node
            )
            
            nodes = []
            for node in nodes_list.items:
                # Parse node roles from labels
                roles = []
                if node.metadata.labels:
                    for label_key in node.metadata.labels:
                        if label_key.startswith("node-role.kubernetes.io/"):
                            role = label_key.split("/", 1)[1]
                            if role:
                                roles.append(role)
                
                # Get node status
                node_status = "Unknown"
                for condition in node.status.conditions or []:
                    if condition.type == "Ready":
                        node_status = "Ready" if condition.status == "True" else "NotReady"
                        break
                
                # Parse system info
                system_info = node.status.node_info
                
                node_info = NodeInfo(
                    name=node.metadata.name,
                    status=node_status,
                    roles=roles or ["<none>"],
                    version=system_info.kubelet_version if system_info else "unknown",
                    os_image=system_info.os_image if system_info else "unknown",
                    kernel_version=system_info.kernel_version if system_info else "unknown",
                    container_runtime=system_info.container_runtime_version if system_info else "unknown",
                    capacity=dict(node.status.capacity or {}),
                    allocatable=dict(node.status.allocatable or {}),
                    conditions=[{
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason,
                        "message": c.message
                    } for c in (node.status.conditions or [])],
                    labels=dict(node.metadata.labels or {}),
                    annotations=dict(node.metadata.annotations or {}),
                    created_at=node.metadata.creation_timestamp
                )
                
                nodes.append(node_info)
            
            logger.info(f"✅ Listed {len(nodes)} nodes")
            return nodes
            
        except ApiException as e:
            logger.error(f"❌ Failed to list nodes: {e}")
            raise KubernetesClientError(f"Failed to list nodes: {e}")
    
    async def list_pods(self, namespace: Optional[str] = None, label_selector: Optional[str] = None) -> List[PodInfo]:
        """
        List pods in cluster or specific namespace
        
        Args:
            namespace: Optional namespace filter
            label_selector: Optional label selector filter
            
        Returns:
            List of PodInfo objects
        """
        self._ensure_connected()
        
        try:
            logger.info(f"📋 Listing pods{f' in namespace {namespace}' if namespace else ' cluster-wide'}...")
            
            if namespace:
                pods_list = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.core_v1.list_namespaced_pod(
                        namespace=namespace,
                        label_selector=label_selector
                    )
                )
            else:
                pods_list = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.core_v1.list_pod_for_all_namespaces(
                        label_selector=label_selector
                    )
                )
            
            pods = []
            for pod in pods_list.items:
                # Calculate resource requests and limits
                resource_requests = {"cpu": "0", "memory": "0"}
                resource_limits = {"cpu": "0", "memory": "0"}
                
                containers_info = []
                
                for container in pod.spec.containers or []:
                    container_info = {
                        "name": container.name,
                        "image": container.image,
                        "ready": False,
                        "restart_count": 0
                    }
                    
                    # Update resource requests and limits
                    if container.resources:
                        if container.resources.requests:
                            requests = container.resources.requests
                            if "cpu" in requests:
                                resource_requests["cpu"] = requests["cpu"]
                            if "memory" in requests:
                                resource_requests["memory"] = requests["memory"]
                        
                        if container.resources.limits:
                            limits = container.resources.limits
                            if "cpu" in limits:
                                resource_limits["cpu"] = limits["cpu"]
                            if "memory" in limits:
                                resource_limits["memory"] = limits["memory"]
                    
                    containers_info.append(container_info)
                
                # Update container status info if available
                if pod.status.container_statuses:
                    for i, container_status in enumerate(pod.status.container_statuses):
                        if i < len(containers_info):
                            containers_info[i]["ready"] = container_status.ready
                            containers_info[i]["restart_count"] = container_status.restart_count
                
                pod_info = PodInfo(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    status=pod.status.phase or "Unknown",
                    phase=pod.status.phase or "Unknown",
                    node_name=pod.spec.node_name,
                    pod_ip=pod.status.pod_ip,
                    host_ip=pod.status.host_ip,
                    containers=containers_info,
                    labels=dict(pod.metadata.labels or {}),
                    annotations=dict(pod.metadata.annotations or {}),
                    created_at=pod.metadata.creation_timestamp,
                    resource_requests=resource_requests,
                    resource_limits=resource_limits
                )
                
                pods.append(pod_info)
            
            logger.info(f"✅ Listed {len(pods)} pods")
            return pods
            
        except ApiException as e:
            logger.error(f"❌ Failed to list pods: {e}")
            raise KubernetesClientError(f"Failed to list pods: {e}")
    
    async def get_cluster_metrics(self) -> ClusterMetrics:
        """
        Get comprehensive cluster metrics
        
        Returns:
            ClusterMetrics object with resource usage information
        """
        self._ensure_connected()
        
        try:
            logger.info("📊 Collecting cluster metrics...")
            
            # Get basic cluster info
            cluster_info = await self.get_cluster_info()
            nodes = await self.list_nodes()
            pods = await self.list_pods()
            
            # Calculate pod statistics
            running_pods = len([p for p in pods if p.phase.lower() == "running"])
            
            # Calculate resource usage (simplified - in production would use metrics server)
            total_cpu_requests = 0
            total_memory_requests = 0
            
            for pod in pods:
                try:
                    cpu_request = self._parse_cpu_quantity(pod.resource_requests.get("cpu", "0"))
                    memory_request = self._parse_memory_quantity(pod.resource_requests.get("memory", "0"))
                    total_cpu_requests += cpu_request
                    total_memory_requests += memory_request
                except ValueError:
                    continue
            
            # Calculate usage percentages
            cpu_capacity = cluster_info.get("cpu_capacity_millicores", 1)
            memory_capacity = cluster_info.get("memory_capacity_bytes", 1)
            
            cpu_usage_percent = (total_cpu_requests / max(cpu_capacity, 1)) * 100
            memory_usage_percent = (total_memory_requests / max(memory_capacity, 1)) * 100
            
            metrics = ClusterMetrics(
                cluster_name=cluster_info["cluster_name"],
                total_nodes=cluster_info["total_nodes"],
                ready_nodes=cluster_info["ready_nodes"],
                total_pods=len(pods),
                running_pods=running_pods,
                total_namespaces=cluster_info["total_namespaces"],
                cpu_capacity=f"{cpu_capacity}m",
                memory_capacity=f"{memory_capacity}",
                cpu_allocatable=f"{cpu_capacity}m",  # Simplified
                memory_allocatable=f"{memory_capacity}",  # Simplified
                cpu_usage_percent=min(cpu_usage_percent, 100.0),
                memory_usage_percent=min(memory_usage_percent, 100.0),
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"✅ Collected cluster metrics: {metrics.cpu_usage_percent:.1f}% CPU, {metrics.memory_usage_percent:.1f}% memory")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster metrics: {e}")
            raise KubernetesClientError(f"Failed to get cluster metrics: {e}")
    
    def _parse_cpu_quantity(self, cpu_str: str) -> int:
        """Parse Kubernetes CPU quantity to millicores"""
        if not cpu_str or cpu_str == "0":
            return 0
        
        cpu_str = cpu_str.strip()
        
        if cpu_str.endswith("m"):
            return int(cpu_str[:-1])
        elif cpu_str.endswith("u"):
            return int(cpu_str[:-1]) // 1000
        else:
            return int(float(cpu_str) * 1000)
    
    def _parse_memory_quantity(self, memory_str: str) -> int:
        """Parse Kubernetes memory quantity to bytes"""
        if not memory_str or memory_str == "0":
            return 0
        
        memory_str = memory_str.strip()
        
        # Handle different units
        multipliers = {
            "Ki": 1024,
            "Mi": 1024 ** 2,
            "Gi": 1024 ** 3,
            "Ti": 1024 ** 4,
            "K": 1000,
            "M": 1000 ** 2,
            "G": 1000 ** 3,
            "T": 1000 ** 4,
        }
        
        for suffix, multiplier in multipliers.items():
            if memory_str.endswith(suffix):
                return int(float(memory_str[:-len(suffix)]) * multiplier)
        
        # Default to bytes
        return int(memory_str)
    
    async def create_namespace(self, name: str, labels: Optional[Dict[str, str]] = None) -> bool:
        """
        Create a new namespace
        
        Args:
            name: Namespace name
            labels: Optional namespace labels
            
        Returns:
            bool: True if successful
        """
        self._ensure_connected()
        
        try:
            logger.info(f"🆕 Creating namespace: {name}")
            
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=name,
                    labels=labels or {}
                )
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.core_v1.create_namespace(namespace)
            )
            
            logger.info(f"✅ Created namespace: {name}")
            return True
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"📋 Namespace {name} already exists")
                return True
            logger.error(f"❌ Failed to create namespace {name}: {e}")
            raise KubernetesClientError(f"Failed to create namespace {name}: {e}")
    
    async def delete_namespace(self, name: str) -> bool:
        """
        Delete a namespace
        
        Args:
            name: Namespace name
            
        Returns:
            bool: True if successful
        """
        self._ensure_connected()
        
        try:
            logger.info(f"🗑️ Deleting namespace: {name}")
            
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.core_v1.delete_namespace(name)
            )
            
            logger.info(f"✅ Deleted namespace: {name}")
            return True
            
        except ApiException as e:
            if e.status == 404:  # Not found
                logger.info(f"📋 Namespace {name} not found")
                return True
            logger.error(f"❌ Failed to delete namespace {name}: {e}")
            raise KubernetesClientError(f"Failed to delete namespace {name}: {e}")
    
    async def close(self):
        """Close the Kubernetes client connection"""
        if self.api_client:
            await asyncio.get_event_loop().run_in_executor(
                None, self.api_client.close
            )
            self._connected = False
            logger.info("🔒 Closed Kubernetes client connection")
    
    def __enter__(self):
        return self
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()