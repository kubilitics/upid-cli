"""
UPID CLI - AWS Resource Mapper
EKS resource mapping and cost attribution
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


@dataclass
class EKSResource:
    """EKS resource information"""
    resource_id: str
    resource_type: str
    name: str
    namespace: str
    region: str
    instance_type: Optional[str] = None
    storage_size: Optional[float] = None
    tags: Dict[str, str] = None


@dataclass
class EKSNodeGroup:
    """EKS node group information"""
    nodegroup_name: str
    cluster_name: str
    node_role: str
    subnets: List[str]
    instance_types: List[str]
    scaling_config: Dict[str, Any]
    status: str
    created_at: datetime
    tags: Dict[str, str] = None


class AWSResourceMapper:
    """
    AWS resource mapper for EKS clusters
    
    Provides comprehensive EKS resource mapping capabilities:
    - Node group mapping and analysis
    - Storage resource identification
    - Network resource mapping
    - Cost attribution to Kubernetes resources
    - Resource tagging and organization
    """
    
    def __init__(self, aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_region: str = "us-east-1"):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        
        # AWS clients
        self.eks_client = None
        self.ec2_client = None
        self.ec2_resource = None
        
        # Resource cache
        self.resource_cache: Dict[str, Any] = {}
        self.cache_ttl = 1800  # 30 minutes
        
        logger.info("🔧 Initializing AWS resource mapper")
    
    async def initialize(self) -> bool:
        """Initialize AWS resource mapper"""
        try:
            logger.info("🚀 Initializing AWS resource mapper...")
            
            # Initialize AWS clients
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            
            self.eks_client = session.client('eks')
            self.ec2_client = session.client('ec2')
            self.ec2_resource = session.resource('ec2')
            
            # Test connectivity
            if not await self._test_connectivity():
                logger.error("❌ Failed to connect to AWS services")
                return False
            
            logger.info("✅ AWS resource mapper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS resource mapper: {e}")
            return False
    
    async def _test_connectivity(self) -> bool:
        """Test AWS service connectivity"""
        try:
            # Test EKS access
            self.eks_client.list_clusters()
            
            # Test EC2 access
            self.ec2_client.describe_regions(MaxResults=1)
            
            logger.info("✅ AWS service connectivity verified")
            return True
            
        except ClientError as e:
            logger.error(f"❌ AWS connectivity test failed: {e}")
            return False
    
    async def get_cluster_resources(self, cluster_name: str) -> List[EKSResource]:
        """Get all resources for an EKS cluster"""
        try:
            logger.info(f"🔍 Mapping resources for EKS cluster: {cluster_name}")
            
            resources = []
            
            # Get node groups
            node_groups = await self._get_node_groups(cluster_name)
            for node_group in node_groups:
                # Map node group to resources
                node_resources = await self._map_node_group_resources(cluster_name, node_group)
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
    
    async def _get_node_groups(self, cluster_name: str) -> List[EKSNodeGroup]:
        """Get node groups for a cluster"""
        try:
            response = self.eks_client.list_nodegroups(clusterName=cluster_name)
            
            node_groups = []
            for nodegroup_name in response['nodegroups']:
                details = self.eks_client.describe_nodegroup(
                    clusterName=cluster_name,
                    nodegroupName=nodegroup_name
                )
                
                nodegroup = details['nodegroup']
                node_groups.append(EKSNodeGroup(
                    nodegroup_name=nodegroup['nodegroupName'],
                    cluster_name=cluster_name,
                    node_role=nodegroup['nodeRole'],
                    subnets=nodegroup['subnets'],
                    instance_types=nodegroup['instanceTypes'],
                    scaling_config=nodegroup['scalingConfig'],
                    status=nodegroup['status'],
                    created_at=nodegroup['createdAt'],
                    tags=nodegroup.get('tags', {})
                ))
            
            return node_groups
            
        except ClientError as e:
            logger.error(f"❌ Failed to get node groups: {e}")
            return []
    
    async def _map_node_group_resources(self, cluster_name: str, 
                                      node_group: EKSNodeGroup) -> List[EKSResource]:
        """Map node group to individual resources"""
        try:
            resources = []
            
            # Get EC2 instances for this node group
            instances = self.ec2_client.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:kubernetes.io/cluster/' + cluster_name,
                        'Values': ['owned']
                    },
                    {
                        'Name': 'instance-state-name',
                        'Values': ['running', 'pending']
                    }
                ]
            )
            
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    # Check if instance belongs to this node group
                    node_group_tag = f"kubernetes.io/cluster/{cluster_name}/nodegroup/{node_group.nodegroup_name}"
                    
                    if any(tag['Key'] == node_group_tag and tag['Value'] == 'owned' 
                          for tag in instance.get('Tags', [])):
                        
                        resources.append(EKSResource(
                            resource_id=instance['InstanceId'],
                            resource_type='ec2_instance',
                            name=instance['InstanceId'],
                            namespace='kube-system',  # Node resources are in kube-system
                            region=instance['Placement']['AvailabilityZone'][:-1],  # Remove last char for region
                            instance_type=instance['InstanceType'],
                            tags={tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        ))
            
            return resources
            
        except ClientError as e:
            logger.error(f"❌ Failed to map node group resources: {e}")
            return []
    
    async def _get_storage_resources(self, cluster_name: str) -> List[EKSResource]:
        """Get storage resources for a cluster"""
        try:
            resources = []
            
            # Get EBS volumes
            volumes = self.ec2_client.describe_volumes(
                Filters=[
                    {
                        'Name': 'tag:kubernetes.io/cluster/' + cluster_name,
                        'Values': ['owned']
                    }
                ]
            )
            
            for volume in volumes['Volumes']:
                resources.append(EKSResource(
                    resource_id=volume['VolumeId'],
                    resource_type='ebs_volume',
                    name=volume['VolumeId'],
                    namespace='kube-system',
                    region=volume['AvailabilityZone'][:-1],
                    storage_size=volume['Size'],
                    tags={tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
                ))
            
            return resources
            
        except ClientError as e:
            logger.error(f"❌ Failed to get storage resources: {e}")
            return []
    
    async def _get_network_resources(self, cluster_name: str) -> List[EKSResource]:
        """Get network resources for a cluster"""
        try:
            resources = []
            
            # Get load balancers
            elbv2_client = boto3.client('elbv2')
            load_balancers = elbv2_client.describe_load_balancers()
            
            for lb in load_balancers['LoadBalancers']:
                # Check if load balancer is associated with the cluster
                if any(tag['Key'] == f'kubernetes.io/cluster/{cluster_name}' 
                      for tag in lb.get('Tags', [])):
                    
                    resources.append(EKSResource(
                        resource_id=lb['LoadBalancerArn'],
                        resource_type='load_balancer',
                        name=lb['LoadBalancerName'],
                        namespace='kube-system',
                        region=lb['AvailabilityZones'][0]['ZoneName'][:-1],
                        tags={tag['Key']: tag['Value'] for tag in lb.get('Tags', [])}
                    ))
            
            return resources
            
        except ClientError as e:
            logger.error(f"❌ Failed to get network resources: {e}")
            return []
    
    async def get_resource_cost_attribution(self, cluster_name: str, 
                                          resources: List[EKSResource]) -> Dict[str, float]:
        """Get cost attribution for resources"""
        try:
            logger.info(f"💰 Calculating cost attribution for {len(resources)} resources")
            
            cost_attribution = {}
            
            for resource in resources:
                if resource.resource_type == 'ec2_instance':
                    # Get EC2 instance cost
                    cost = await self._get_ec2_instance_cost(resource.resource_id)
                    cost_attribution[resource.resource_id] = cost
                    
                elif resource.resource_type == 'ebs_volume':
                    # Get EBS volume cost
                    cost = await self._get_ebs_volume_cost(resource.resource_id)
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
    
    async def _get_ec2_instance_cost(self, instance_id: str) -> float:
        """Get EC2 instance cost"""
        try:
            # This is a simplified calculation
            # In production, would use Cost Explorer API
            instance = self.ec2_resource.Instance(instance_id)
            
            # Get instance type pricing (simplified)
            instance_type = instance.instance_type
            pricing = {
                't3.medium': 0.0416,  # $0.0416 per hour
                't3.large': 0.0832,   # $0.0832 per hour
                'm5.large': 0.096,    # $0.096 per hour
                'c5.large': 0.085,    # $0.085 per hour
            }
            
            hourly_cost = pricing.get(instance_type, 0.05)  # Default $0.05/hour
            return hourly_cost * 24 * 30  # Monthly cost
            
        except Exception as e:
            logger.error(f"❌ Failed to get EC2 instance cost: {e}")
            return 0.0
    
    async def _get_ebs_volume_cost(self, volume_id: str) -> float:
        """Get EBS volume cost"""
        try:
            volume = self.ec2_resource.Volume(volume_id)
            
            # EBS pricing (simplified)
            # gp2: $0.10 per GB per month
            # io1: $0.125 per GB per month
            volume_type = volume.volume_type
            size_gb = volume.size
            
            pricing = {
                'gp2': 0.10,
                'io1': 0.125,
                'gp3': 0.08,
            }
            
            monthly_cost_per_gb = pricing.get(volume_type, 0.10)
            return monthly_cost_per_gb * size_gb
            
        except Exception as e:
            logger.error(f"❌ Failed to get EBS volume cost: {e}")
            return 0.0
    
    async def _get_load_balancer_cost(self, lb_arn: str) -> float:
        """Get load balancer cost"""
        try:
            # ALB/NLB pricing (simplified)
            # ALB: $16.20 per month + $0.0225 per hour
            # NLB: $16.20 per month + $0.0225 per hour
            
            # Simplified calculation
            base_cost = 16.20  # Monthly base cost
            hourly_cost = 0.0225 * 24 * 30  # Monthly hourly cost
            return base_cost + hourly_cost
            
        except Exception as e:
            logger.error(f"❌ Failed to get load balancer cost: {e}")
            return 0.0
    
    async def get_resource_utilization(self, cluster_name: str, 
                                     resources: List[EKSResource]) -> Dict[str, Dict[str, float]]:
        """Get resource utilization metrics"""
        try:
            logger.info(f"📊 Getting utilization for {len(resources)} resources")
            
            utilization = {}
            
            for resource in resources:
                if resource.resource_type == 'ec2_instance':
                    # Get CloudWatch metrics for EC2 instance
                    metrics = await self._get_ec2_utilization(resource.resource_id)
                    utilization[resource.resource_id] = metrics
                    
                elif resource.resource_type == 'ebs_volume':
                    # Get EBS volume utilization
                    metrics = await self._get_ebs_utilization(resource.resource_id)
                    utilization[resource.resource_id] = metrics
            
            logger.info(f"✅ Retrieved utilization for {len(utilization)} resources")
            return utilization
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource utilization: {e}")
            return {}
    
    async def _get_ec2_utilization(self, instance_id: str) -> Dict[str, float]:
        """Get EC2 instance utilization"""
        try:
            cloudwatch = boto3.client('cloudwatch')
            
            # Get CPU utilization
            cpu_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.utcnow() - timedelta(hours=1),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            
            cpu_utilization = 0.0
            if cpu_response['Datapoints']:
                cpu_utilization = cpu_response['Datapoints'][-1]['Average']
            
            # Get memory utilization (requires custom metrics)
            memory_utilization = 0.0  # Would need custom CloudWatch metrics
            
            return {
                'cpu_utilization': cpu_utilization,
                'memory_utilization': memory_utilization,
                'network_utilization': 0.0  # Would need custom metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get EC2 utilization: {e}")
            return {'cpu_utilization': 0.0, 'memory_utilization': 0.0, 'network_utilization': 0.0}
    
    async def _get_ebs_utilization(self, volume_id: str) -> Dict[str, float]:
        """Get EBS volume utilization"""
        try:
            cloudwatch = boto3.client('cloudwatch')
            
            # Get volume read/write operations
            read_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EBS',
                MetricName='VolumeReadOps',
                Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
                StartTime=datetime.utcnow() - timedelta(hours=1),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Sum']
            )
            
            write_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EBS',
                MetricName='VolumeWriteOps',
                Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
                StartTime=datetime.utcnow() - timedelta(hours=1),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Sum']
            )
            
            read_ops = 0.0
            if read_response['Datapoints']:
                read_ops = read_response['Datapoints'][-1]['Sum']
            
            write_ops = 0.0
            if write_response['Datapoints']:
                write_ops = write_response['Datapoints'][-1]['Sum']
            
            return {
                'read_operations': read_ops,
                'write_operations': write_ops,
                'volume_utilization': 0.0  # Would need custom metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get EBS utilization: {e}")
            return {'read_operations': 0.0, 'write_operations': 0.0, 'volume_utilization': 0.0} 