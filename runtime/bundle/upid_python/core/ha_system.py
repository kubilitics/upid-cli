"""
High Availability & Scaling System for UPID CLI
Provides API server clustering, database replication, load balancing, and graceful failover
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import socket
import requests
import random

# Optional imports with fallbacks
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import consul
    CONSUL_AVAILABLE = True
except ImportError:
    CONSUL_AVAILABLE = False
    consul = None


class NodeStatus(Enum):
    """Node status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ClusterRole(Enum):
    """Cluster role enumeration"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    STANDBY = "standby"


@dataclass
class NodeInfo:
    """Node information for clustering"""
    node_id: str
    host: str
    port: int
    role: ClusterRole
    status: NodeStatus
    last_heartbeat: datetime
    capabilities: List[str]
    load_factor: float
    version: str
    metadata: Dict[str, Any]


@dataclass
class ClusterConfig:
    """Cluster configuration"""
    cluster_name: str
    node_id: str
    host: str
    port: int
    discovery_interval: int = 30
    heartbeat_interval: int = 10
    health_check_interval: int = 15
    failover_timeout: int = 60
    max_nodes: int = 10
    load_balancing_strategy: str = "round_robin"


@dataclass
class LoadBalancerStats:
    """Load balancer statistics"""
    total_requests: int
    active_connections: int
    healthy_nodes: int
    unhealthy_nodes: int
    last_health_check: datetime
    average_response_time: float
    error_rate: float


class HighAvailabilitySystem:
    """High Availability and Scaling System"""
    
    def __init__(self, config: ClusterConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Node management
        self.nodes: Dict[str, NodeInfo] = {}
        self.current_node_id = config.node_id
        self.current_role = ClusterRole.SECONDARY
        
        # Load balancing
        self.load_balancer_stats = LoadBalancerStats(
            total_requests=0,
            active_connections=0,
            healthy_nodes=0,
            unhealthy_nodes=0,
            last_health_check=datetime.now(),
            average_response_time=0.0,
            error_rate=0.0
        )
        
        # Health monitoring
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.failover_history: List[Dict[str, Any]] = []
        
        # Initialize components
        self._setup_redis()
        self._setup_consul()
        self._start_background_tasks()
    
    def _setup_redis(self):
        """Setup Redis for distributed state management"""
        if REDIS_AVAILABLE:
            try:
                redis_host = os.getenv('REDIS_HOST', 'localhost')
                redis_port = int(os.getenv('REDIS_PORT', 6379))
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                self.redis_client.ping()
                self.logger.info("Redis connection established")
            except Exception as e:
                self.logger.warning(f"Redis not available: {e}")
                self.redis_client = None
        else:
            self.logger.warning("Redis not available - using in-memory state")
            self.redis_client = None
    
    def _setup_consul(self):
        """Setup Consul for service discovery"""
        if CONSUL_AVAILABLE:
            try:
                consul_host = os.getenv('CONSUL_HOST', 'localhost')
                consul_port = int(os.getenv('CONSUL_PORT', 8500))
                self.consul_client = consul.Consul(
                    host=consul_host,
                    port=consul_port
                )
                self.consul_client.agent.self()
                self.logger.info("Consul connection established")
            except Exception as e:
                self.logger.warning(f"Consul not available: {e}")
                self.consul_client = None
        else:
            self.logger.warning("Consul not available - using local service discovery")
            self.consul_client = None
    
    def _start_background_tasks(self):
        """Start background tasks for HA management"""
        threading.Thread(target=self._discovery_loop, daemon=True).start()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        threading.Thread(target=self._health_monitoring_loop, daemon=True).start()
        threading.Thread(target=self._load_balancer_monitoring_loop, daemon=True).start()
    
    def _discovery_loop(self):
        """Background task for node discovery"""
        while True:
            try:
                self._discover_nodes()
                time.sleep(self.config.discovery_interval)
            except Exception as e:
                self.logger.error(f"Error in node discovery: {e}")
                time.sleep(self.config.discovery_interval)
    
    def _heartbeat_loop(self):
        """Background task for heartbeat"""
        while True:
            try:
                self._send_heartbeat()
                time.sleep(self.config.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Error in heartbeat: {e}")
                time.sleep(self.config.heartbeat_interval)
    
    def _health_monitoring_loop(self):
        """Background task for health monitoring"""
        while True:
            try:
                self._check_node_health()
                time.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                time.sleep(self.config.health_check_interval)
    
    def _load_balancer_monitoring_loop(self):
        """Background task for load balancer monitoring"""
        while True:
            try:
                self._update_load_balancer_stats()
                time.sleep(30)
            except Exception as e:
                self.logger.error(f"Error in load balancer monitoring: {e}")
                time.sleep(30)
    
    def _discover_nodes(self):
        """Discover other nodes in the cluster"""
        if self.consul_client:
            try:
                services = self.consul_client.catalog.services()[1]
                for service_name, tags in services.items():
                    if 'upid-cli' in service_name:
                        nodes = self.consul_client.catalog.service(service_name)[1]
                        for node in nodes:
                            node_info = NodeInfo(
                                node_id=node['Node'],
                                host=node['Address'],
                                port=node['ServicePort'],
                                role=ClusterRole.SECONDARY,
                                status=NodeStatus.UNKNOWN,
                                last_heartbeat=datetime.now(),
                                capabilities=node.get('ServiceTags', []),
                                load_factor=0.0,
                                version=node.get('ServiceMeta', {}).get('version', 'unknown'),
                                metadata=node.get('ServiceMeta', {})
                            )
                            self.nodes[node['Node']] = node_info
            except Exception as e:
                self.logger.error(f"Error discovering nodes via Consul: {e}")
        elif self.redis_client:
            try:
                node_keys = self.redis_client.keys("upid:node:*")
                for key in node_keys:
                    node_data = self.redis_client.hgetall(key)
                    if node_data:
                        node_info = NodeInfo(
                            node_id=node_data.get('node_id', 'unknown'),
                            host=node_data.get('host', 'localhost'),
                            port=int(node_data.get('port', 8000)),
                            role=ClusterRole(node_data.get('role', 'secondary')),
                            status=NodeStatus(node_data.get('status', 'unknown')),
                            last_heartbeat=datetime.fromisoformat(node_data.get('last_heartbeat', datetime.now().isoformat())),
                            capabilities=json.loads(node_data.get('capabilities', '[]')),
                            load_factor=float(node_data.get('load_factor', 0.0)),
                            version=node_data.get('version', 'unknown'),
                            metadata=json.loads(node_data.get('metadata', '{}'))
                        )
                        self.nodes[node_info.node_id] = node_info
            except Exception as e:
                self.logger.error(f"Error discovering nodes via Redis: {e}")
    
    def _send_heartbeat(self):
        """Send heartbeat to other nodes"""
        heartbeat_data = {
            'node_id': self.current_node_id,
            'host': self.config.host,
            'port': self.config.port,
            'role': self.current_role.value,
            'status': NodeStatus.HEALTHY.value,
            'last_heartbeat': datetime.now().isoformat(),
            'capabilities': ['api_server', 'database', 'ml_pipeline'],
            'load_factor': self._calculate_load_factor(),
            'version': '1.0.0',
            'metadata': {
                'uptime': time.time(),
                'memory_usage': self._get_memory_usage(),
                'cpu_usage': self._get_cpu_usage()
            }
        }
        
        if self.redis_client:
            try:
                key = f"upid:node:{self.current_node_id}"
                self.redis_client.hmset(key, heartbeat_data)
                self.redis_client.expire(key, 120)
            except Exception as e:
                self.logger.error(f"Error sending heartbeat to Redis: {e}")
        
        if self.consul_client:
            try:
                self.consul_client.agent.service.register(
                    name='upid-cli',
                    service_id=self.current_node_id,
                    address=self.config.host,
                    port=self.config.port,
                    tags=['api_server', 'database', 'ml_pipeline'],
                    meta={
                        'version': '1.0.0',
                        'role': self.current_role.value,
                        'status': NodeStatus.HEALTHY.value
                    }
                )
            except Exception as e:
                self.logger.error(f"Error registering with Consul: {e}")
    
    def _check_node_health(self):
        """Check health of all nodes"""
        current_time = datetime.now()
        
        for node_id, node_info in self.nodes.items():
            if node_id == self.current_node_id:
                continue
            
            try:
                health_url = f"http://{node_info.host}:{node_info.port}/health"
                response = requests.get(health_url, timeout=5)
                
                if response.status_code == 200:
                    node_info.status = NodeStatus.HEALTHY
                    node_info.last_heartbeat = current_time
                else:
                    node_info.status = NodeStatus.DEGRADED
                    
            except Exception as e:
                time_since_heartbeat = (current_time - node_info.last_heartbeat).total_seconds()
                
                if time_since_heartbeat > self.config.failover_timeout:
                    node_info.status = NodeStatus.UNHEALTHY
                    self._handle_node_failure(node_id, node_info)
                else:
                    node_info.status = NodeStatus.DEGRADED
        
        self._update_load_balancer_stats()
    
    def _handle_node_failure(self, node_id: str, node_info: NodeInfo):
        """Handle node failure and initiate failover if needed"""
        self.logger.warning(f"Node {node_id} failed: {node_info.host}:{node_info.port}")
        
        failover_event = {
            'timestamp': datetime.now().isoformat(),
            'failed_node': node_id,
            'node_info': asdict(node_info),
            'trigger': 'health_check_timeout',
            'action': 'mark_unhealthy'
        }
        self.failover_history.append(failover_event)
        
        if node_info.role == ClusterRole.PRIMARY:
            self._promote_primary()
    
    def _promote_primary(self):
        """Promote a secondary node to primary"""
        healthy_secondaries = [
            node for node in self.nodes.values()
            if node.role == ClusterRole.SECONDARY and node.status == NodeStatus.HEALTHY
        ]
        
        if healthy_secondaries:
            new_primary = min(healthy_secondaries, key=lambda x: x.load_factor)
            new_primary.role = ClusterRole.PRIMARY
            
            self.logger.info(f"Promoting node {new_primary.node_id} to primary")
            
            if self.redis_client:
                try:
                    key = f"upid:node:{new_primary.node_id}"
                    self.redis_client.hset(key, 'role', ClusterRole.PRIMARY.value)
                except Exception as e:
                    self.logger.error(f"Error updating primary in Redis: {e}")
            
            if self.consul_client:
                try:
                    self.consul_client.agent.service.register(
                        name='upid-cli-primary',
                        service_id=new_primary.node_id,
                        address=new_primary.host,
                        port=new_primary.port,
                        tags=['primary', 'api_server'],
                        meta={'role': 'primary'}
                    )
                except Exception as e:
                    self.logger.error(f"Error updating primary in Consul: {e}")
    
    def _calculate_load_factor(self) -> float:
        """Calculate current load factor"""
        active_connections = self.load_balancer_stats.active_connections
        avg_response_time = self.load_balancer_stats.average_response_time
        load_factor = min(1.0, (active_connections / 100.0) + (avg_response_time / 1000.0))
        return load_factor
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
    
    def _update_load_balancer_stats(self):
        """Update load balancer statistics"""
        healthy_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.HEALTHY)
        unhealthy_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.UNHEALTHY)
        
        self.load_balancer_stats.healthy_nodes = healthy_nodes
        self.load_balancer_stats.unhealthy_nodes = unhealthy_nodes
        self.load_balancer_stats.last_health_check = datetime.now()
    
    def get_healthy_nodes(self) -> List[NodeInfo]:
        """Get list of healthy nodes"""
        return [node for node in self.nodes.values() if node.status == NodeStatus.HEALTHY]
    
    def get_primary_node(self) -> Optional[NodeInfo]:
        """Get the current primary node"""
        for node in self.nodes.values():
            if node.role == ClusterRole.PRIMARY and node.status == NodeStatus.HEALTHY:
                return node
        return None
    
    def select_node_for_request(self, request_type: str = "api") -> Optional[NodeInfo]:
        """Select a node for handling a request based on load balancing strategy"""
        healthy_nodes = self.get_healthy_nodes()
        
        if not healthy_nodes:
            return None
        
        if self.config.load_balancing_strategy == "round_robin":
            return random.choice(healthy_nodes)
        elif self.config.load_balancing_strategy == "least_connections":
            return min(healthy_nodes, key=lambda x: x.load_factor)
        elif self.config.load_balancing_strategy == "weighted":
            total_weight = sum(1.0 / (node.load_factor + 0.1) for node in healthy_nodes)
            if total_weight == 0:
                return random.choice(healthy_nodes)
            weights = [(1.0 / (node.load_factor + 0.1)) / total_weight for node in healthy_nodes]
            return random.choices(healthy_nodes, weights=weights)[0]
        else:
            return random.choice(healthy_nodes)
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        return {
            'cluster_name': self.config.cluster_name,
            'current_node': {
                'node_id': self.current_node_id,
                'role': self.current_role.value,
                'host': self.config.host,
                'port': self.config.port
            },
            'nodes': {
                node_id: asdict(node_info) for node_id, node_info in self.nodes.items()
            },
            'load_balancer': asdict(self.load_balancer_stats),
            'failover_history': self.failover_history[-10:],
            'cluster_health': {
                'total_nodes': len(self.nodes),
                'healthy_nodes': self.load_balancer_stats.healthy_nodes,
                'unhealthy_nodes': self.load_balancer_stats.unhealthy_nodes,
                'primary_node': self.get_primary_node().node_id if self.get_primary_node() else None
            }
        }


class DatabaseReplicationManager:
    """Database replication and failover management"""
    
    def __init__(self, primary_db_url: str, replica_db_urls: List[str]):
        self.primary_db_url = primary_db_url
        self.replica_db_urls = replica_db_urls
        self.current_primary = primary_db_url
        self.healthy_replicas: List[str] = []
        self.logger = logging.getLogger(__name__)
        
        threading.Thread(target=self._monitor_replicas, daemon=True).start()
    
    def _monitor_replicas(self):
        """Monitor replica health"""
        while True:
            try:
                self._check_replica_health()
                time.sleep(30)
            except Exception as e:
                self.logger.error(f"Error monitoring replicas: {e}")
                time.sleep(30)
    
    def _check_replica_health(self):
        """Check health of all database replicas"""
        self.healthy_replicas = []
        
        for replica_url in self.replica_db_urls:
            try:
                import sqlite3
                conn = sqlite3.connect(replica_url, timeout=5)
                conn.close()
                self.healthy_replicas.append(replica_url)
            except Exception as e:
                self.logger.warning(f"Replica {replica_url} is unhealthy: {e}")
    
    def get_read_replica(self) -> str:
        """Get a healthy read replica"""
        if self.healthy_replicas:
            return random.choice(self.healthy_replicas)
        else:
            return self.current_primary
    
    def get_write_primary(self) -> str:
        """Get the current write primary"""
        return self.current_primary
    
    def failover_primary(self, new_primary: str):
        """Failover to a new primary database"""
        self.logger.warning(f"Failing over from {self.current_primary} to {new_primary}")
        self.current_primary = new_primary


class LoadBalancer:
    """Load balancer for distributing requests"""
    
    def __init__(self, ha_system: HighAvailabilitySystem):
        self.ha_system = ha_system
        self.logger = logging.getLogger(__name__)
        self.request_history: List[Dict[str, Any]] = []
    
    def route_request(self, request_type: str, request_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Route a request to an appropriate node"""
        selected_node = self.ha_system.select_node_for_request(request_type)
        
        if not selected_node:
            raise Exception("No healthy nodes available")
        
        request_record = {
            'timestamp': datetime.now().isoformat(),
            'request_type': request_type,
            'target_node': selected_node.node_id,
            'target_host': selected_node.host,
            'target_port': selected_node.port
        }
        self.request_history.append(request_record)
        
        self.ha_system.load_balancer_stats.total_requests += 1
        self.ha_system.load_balancer_stats.active_connections += 1
        
        return f"http://{selected_node.host}:{selected_node.port}", request_data
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            'stats': asdict(self.ha_system.load_balancer_stats),
            'request_history': self.request_history[-100:],
            'node_distribution': self._get_node_distribution()
        }
    
    def _get_node_distribution(self) -> Dict[str, int]:
        """Get request distribution across nodes"""
        distribution = {}
        for record in self.request_history[-1000:]:
            node_id = record['target_node']
            distribution[node_id] = distribution.get(node_id, 0) + 1
        return distribution


def create_ha_system(cluster_name: str = "upid-cluster", node_id: str = None) -> HighAvailabilitySystem:
    """Create a high availability system instance"""
    if node_id is None:
        node_id = f"node-{socket.gethostname()}-{os.getpid()}"
    
    config = ClusterConfig(
        cluster_name=cluster_name,
        node_id=node_id,
        host=socket.gethostname(),
        port=int(os.getenv('API_PORT', 8000))
    )
    
    return HighAvailabilitySystem(config) 