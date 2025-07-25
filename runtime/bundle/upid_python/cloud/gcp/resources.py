"""
UPID CLI - GCP Resource Mapper
GKE resource mapping and cost attribution
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from google.cloud import container_v1
from google.cloud import compute_v1
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)


@dataclass
class GKEResource:
    """GKE resource information"""
    resource_id: str
    resource_type: str
    name: str
    namespace: str
    location: str
    machine_type: Optional[str] = None
    disk_size: Optional[float] = None
    labels: Dict[str, str] = None


@dataclass
class GKENodePool:
    """GKE node pool information"""
    node_pool_name: str
    cluster_name: str
    node_count: int
    machine_type: str
    disk_size_gb: int
    locations: List[str]
    autoscaling: Dict[str, Any]
    status: str
    created_at: datetime
    labels: Dict[str, str] = None


class GCPResourceMapper:
    """
    GCP resource mapper for GKE clusters
    
    Provides comprehensive GKE resource mapping capabilities:
    - Node pool mapping and analysis
    - Storage resource identification
    - Network resource mapping
    - Cost attribution to Kubernetes resources
    - Resource labeling and organization
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        
        # GCP clients
        self.container_client = None
        self.compute_client = None
        
        # Resource cache
        self.resource_cache: Dict[str, Any] = {}
        self.cache_ttl = 1800  # 30 minutes
        
        logger.info("🔧 Initializing GCP resource mapper")
    
    async def initialize(self) -> bool:
        """Initialize GCP resource mapper"""
        try:
            logger.info("🚀 Initializing GCP resource mapper...")
            
            # Initialize GCP clients
            self.container_client = container_v1.ClusterManagerClient()
            self.compute_client = compute_v1.InstancesClient()
            
            # Test connectivity
            if not await self._test_connectivity():
                logger.error("❌ Failed to connect to GCP services")
                return False
            
            logger.info("✅ GCP resource mapper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCP resource mapper: {e}")
            return False
    
    async def _test_connectivity(self) -> bool:
        """Test GCP service connectivity"""
        try:
            # Test container API access
            self.container_client.list_clusters(parent=f"projects/{self.project_id}/locations/-")
            
            # Test compute API access
            self.compute_client.list(project=self.project_id, zone="us-central1-a", max_results=1)
            
            logger.info("✅ GCP service connectivity verified")
            return True
            
        except GoogleAPIError as e:
            logger.error(f"❌ GCP connectivity test failed: {e}")
            return False
    
    async def get_cluster_resources(self, cluster_name: str) -> List[GKEResource]:
        """Get all resources for a GKE cluster"""
        try:
            logger.info(f"🔍 Mapping resources for GKE cluster: {cluster_name}")
            
            resources = []
            
            # Get node pools
            node_pools = await self._get_node_pools(cluster_name)
            for node_pool in node_pools:
                # Map node pool to resources
                node_resources = await self._map_node_pool_resources(cluster_name, node_pool)
                resources.extend(node_resources)
            
            # Get storage resources
            storage_resources = await self._get_storage_resources(cluster_name)
            resources.extend(storage_resources)
            
            # Get network resources
            network_resources = await self._get_network_resources(cluster_name)
            resources.extend(network_resources)
            
            logger.info(f"✅ Mapped {len(resources)} resources for cluster {cluster_name}")
            return resources
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster resources: {e}")
            return []
    
    async def _get_node_pools(self, cluster_name: str) -> List[GKENodePool]:
        """Get node pools for a cluster"""
        try:
            # List clusters to find the one with matching name
            clusters = self.container_client.list_clusters(parent=f"projects/{self.project_id}/locations/-")
            
            for cluster in clusters:
                if cluster.name == cluster_name:
                    node_pools = []
                    for pool in cluster.node_pools:
                        node_pools.append(GKENodePool(
                            node_pool_name=pool.name,
                            cluster_name=cluster_name,
                            node_count=pool.initial_node_count,
                            machine_type=pool.config.machine_type,
                            disk_size_gb=pool.config.disk_size_gb,
                            locations=pool.locations,
                            autoscaling={
                                'enabled': pool.autoscaling.enabled if pool.autoscaling else False,
                                'min_node_count': pool.autoscaling.min_node_count if pool.autoscaling else 0,
                                'max_node_count': pool.autoscaling.max_node_count if pool.autoscaling else 0
                            },
                            status=pool.status,
                            created_at=pool.create_time,
                            labels=dict(pool.config.labels) if pool.config.labels else {}
                        ))
                    return node_pools
            
            return []
            
        except GoogleAPIError as e:
            logger.error(f"❌ Failed to get node pools: {e}")
            return []
    
    async def _map_node_pool_resources(self, cluster_name: str, 
                                     node_pool: GKENodePool) -> List[GKEResource]:
        """Map node pool to individual resources"""
        try:
            resources = []
            
            # Get Compute Engine instances for this node pool
            # This is a simplified implementation
            # In production, would query actual instances
            
            # Mock instance mapping
            for i in range(node_pool.node_count):
                instance_name = f"gke-{cluster_name}-{node_pool.node_pool_name}-{i}"
                
                resources.append(GKEResource(
                    resource_id=instance_name,
                    resource_type='compute_instance',
                    name=instance_name,
                    namespace='kube-system',
                    location=node_pool.locations[0] if node_pool.locations else 'us-central1',
                    machine_type=node_pool.machine_type,
                    disk_size=node_pool.disk_size_gb,
                    labels=node_pool.labels
                ))
            
            return resources
            
        except Exception as e:
            logger.error(f"❌ Failed to map node pool resources: {e}")
            return []
    
    async def _get_storage_resources(self, cluster_name: str) -> List[GKEResource]:
        """Get storage resources for a cluster"""
        try:
            resources = []
            
            # Get persistent disks
            # This is a simplified implementation
            # In production, would query actual disks
            
            # Mock storage resources
            storage_resources = [
                {
                    'id': f'disk-{cluster_name}-storage-1',
                    'name': f'disk-{cluster_name}-storage-1',
                    'size_gb': 100,
                    'type': 'pd-standard'
                },
                {
                    'id': f'disk-{cluster_name}-storage-2',
                    'name': f'disk-{cluster_name}-storage-2',
                    'size_gb': 200,
                    'type': 'pd-ssd'
                }
            ]
            
            for disk in storage_resources:
                resources.append(GKEResource(
                    resource_id=disk['id'],
                    resource_type='persistent_disk',
                    name=disk['name'],
                    namespace='kube-system',
                    location='us-central1',
                    disk_size=disk['size_gb'],
                    labels={'cluster': cluster_name}
                ))
            
            return resources
            
        except Exception as e:
            logger.error(f"❌ Failed to get storage resources: {e}")
            return []
    
    async def _get_network_resources(self, cluster_name: str) -> List[GKEResource]:
        """Get network resources for a cluster"""
        try:
            resources = []
            
            # Get load balancers
            # This is a simplified implementation
            # In production, would query actual load balancers
            
            # Mock network resources
            network_resources = [
                {
                    'id': f'lb-{cluster_name}-ingress',
                    'name': f'lb-{cluster_name}-ingress',
                    'type': 'load_balancer'
                }
            ]
            
            for lb in network_resources:
                resources.append(GKEResource(
                    resource_id=lb['id'],
                    resource_type=lb['type'],
                    name=lb['name'],
                    namespace='kube-system',
                    location='us-central1',
                    labels={'cluster': cluster_name}
                ))
            
            return resources
            
        except Exception as e:
            logger.error(f"❌ Failed to get network resources: {e}")
            return []
    
    async def get_resource_cost_attribution(self, cluster_name: str, 
                                          resources: List[GKEResource]) -> Dict[str, float]:
        """Get cost attribution for resources"""
        try:
            logger.info(f"💰 Calculating cost attribution for {len(resources)} resources")
            
            cost_attribution = {}
            
            for resource in resources:
                if resource.resource_type == 'compute_instance':
                    # Get Compute Engine instance cost
                    cost = await self._get_compute_instance_cost(resource.resource_id, resource.machine_type)
                    cost_attribution[resource.resource_id] = cost
                    
                elif resource.resource_type == 'persistent_disk':
                    # Get persistent disk cost
                    cost = await self._get_persistent_disk_cost(resource.resource_id, resource.disk_size)
                    cost_attribution[resource.resource_id] = cost
                    
                elif resource.resource_type == 'load_balancer':
                    # Get load balancer cost
                    cost = await self._get_load_balancer_cost(resource.resource_id)
                    cost_attribution[resource.resource_id] = cost
            
            logger.info(f"✅ Calculated cost attribution for {len(cost_attribution)} resources")
            return cost_attribution
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource cost attribution: {e}")
            return {}
    
    async def _get_compute_instance_cost(self, instance_id: str, machine_type: str) -> float:
        """Get Compute Engine instance cost"""
        try:
            # GCP pricing (simplified)
            pricing = {
                'e2-medium': 0.0335,  # $0.0335 per hour
                'e2-standard-2': 0.067,  # $0.067 per hour
                'n1-standard-1': 0.0475,  # $0.0475 per hour
                'n1-standard-2': 0.095,   # $0.095 per hour
            }
            
            hourly_cost = pricing.get(machine_type, 0.05)  # Default $0.05/hour
            return hourly_cost * 24 * 30  # Monthly cost
            
        except Exception as e:
            logger.error(f"❌ Failed to get Compute Engine instance cost: {e}")
            return 0.0
    
    async def _get_persistent_disk_cost(self, disk_id: str, size_gb: float) -> float:
        """Get persistent disk cost"""
        try:
            # GCP persistent disk pricing (simplified)
            # pd-standard: $0.04 per GB per month
            # pd-ssd: $0.17 per GB per month
            
            # Simplified calculation
            monthly_cost_per_gb = 0.04  # pd-standard
            return monthly_cost_per_gb * size_gb
            
        except Exception as e:
            logger.error(f"❌ Failed to get persistent disk cost: {e}")
            return 0.0
    
    async def _get_load_balancer_cost(self, lb_id: str) -> float:
        """Get load balancer cost"""
        try:
            # GCP load balancer pricing (simplified)
            # Network load balancer: $18.25 per month + $0.006 per hour
            
            # Simplified calculation
            base_cost = 18.25  # Monthly base cost
            hourly_cost = 0.006 * 24 * 30  # Monthly hourly cost
            return base_cost + hourly_cost
            
        except Exception as e:
            logger.error(f"❌ Failed to get load balancer cost: {e}")
            return 0.0
    
    async def get_resource_utilization(self, cluster_name: str, 
                                     resources: List[GKEResource]) -> Dict[str, Dict[str, float]]:
        """Get resource utilization metrics"""
        try:
            logger.info(f"📊 Getting utilization for {len(resources)} resources")
            
            utilization = {}
            
            for resource in resources:
                if resource.resource_type == 'compute_instance':
                    # Get Cloud Monitoring metrics for Compute Engine instance
                    metrics = await self._get_compute_utilization(resource.resource_id)
                    utilization[resource.resource_id] = metrics
                    
                elif resource.resource_type == 'persistent_disk':
                    # Get persistent disk utilization
                    metrics = await self._get_disk_utilization(resource.resource_id)
                    utilization[resource.resource_id] = metrics
            
            logger.info(f"✅ Retrieved utilization for {len(utilization)} resources")
            return utilization
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource utilization: {e}")
            return {}
    
    async def _get_compute_utilization(self, instance_id: str) -> Dict[str, float]:
        """Get Compute Engine instance utilization"""
        try:
            # This is a simplified implementation
            # In production, would use Cloud Monitoring API
            
            # Mock utilization data
            return {
                'cpu_utilization': 45.2,
                'memory_utilization': 67.8,
                'network_utilization': 23.1
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get Compute Engine utilization: {e}")
            return {'cpu_utilization': 0.0, 'memory_utilization': 0.0, 'network_utilization': 0.0}
    
    async def _get_disk_utilization(self, disk_id: str) -> Dict[str, float]:
        """Get persistent disk utilization"""
        try:
            # This is a simplified implementation
            # In production, would use Cloud Monitoring API
            
            # Mock utilization data
            return {
                'read_operations': 1250.0,
                'write_operations': 890.0,
                'disk_utilization': 45.6
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get disk utilization: {e}")
            return {'read_operations': 0.0, 'write_operations': 0.0, 'disk_utilization': 0.0} 