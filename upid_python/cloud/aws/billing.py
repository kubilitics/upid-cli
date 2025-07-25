"""
UPID CLI - AWS Billing Client
AWS Cost Explorer integration for Kubernetes cost analysis
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


@dataclass
class AWSCostData:
    """AWS cost data structure"""
    service: str
    region: str
    cost: float
    usage_amount: float
    usage_unit: str
    start_date: datetime
    end_date: datetime
    tags: Dict[str, str] = None


@dataclass
class EKSCostBreakdown:
    """EKS cost breakdown"""
    cluster_name: str
    node_costs: float
    storage_costs: float
    network_costs: float
    other_costs: float
    total_cost: float
    period_start: datetime
    period_end: datetime


class AWSBillingClient:
    """
    AWS Cost Explorer client for Kubernetes cost analysis
    
    Provides comprehensive AWS cost analysis capabilities:
    - Real-time cost data retrieval
    - EKS-specific cost breakdown
    - Resource cost attribution
    - Cost trend analysis
    - Tag-based cost allocation
    """
    
    def __init__(self, aws_access_key_id: Optional[str] = None, 
                 aws_secret_access_key: Optional[str] = None,
                 aws_region: str = "us-east-1"):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        
        # AWS clients
        self.ce_client = None
        self.ec2_client = None
        self.eks_client = None
        
        # Cost data cache
        self.cost_cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour
        
        logger.info("🔧 Initializing AWS billing client")
    
    async def initialize(self) -> bool:
        """Initialize AWS billing client"""
        try:
            logger.info("🚀 Initializing AWS billing client...")
            
            # Initialize AWS clients
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            
            self.ce_client = session.client('ce')
            self.ec2_client = session.client('ec2')
            self.eks_client = session.client('eks')
            
            # Test connectivity
            if not await self._test_connectivity():
                logger.error("❌ Failed to connect to AWS services")
                return False
            
            logger.info("✅ AWS billing client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS billing client: {e}")
            return False
    
    async def _test_connectivity(self) -> bool:
        """Test AWS service connectivity"""
        try:
            # Test Cost Explorer access
            self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'End': datetime.utcnow().strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            
            logger.info("✅ AWS Cost Explorer connectivity verified")
            return True
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"❌ AWS connectivity test failed: {e}")
            return False
    
    async def get_eks_cluster_costs(self, cluster_name: str, 
                                   start_date: datetime, 
                                   end_date: datetime) -> Optional[EKSCostBreakdown]:
        """Get EKS cluster cost breakdown"""
        try:
            logger.info(f"💰 Retrieving costs for EKS cluster: {cluster_name}")
            
            # Get cluster details
            cluster_details = await self._get_cluster_details(cluster_name)
            if not cluster_details:
                logger.error(f"❌ Failed to get cluster details for {cluster_name}")
                return None
            
            # Get cost data for EKS services
            cost_data = await self._get_eks_cost_data(cluster_name, start_date, end_date)
            if not cost_data:
                logger.warning(f"⚠️ No cost data found for cluster {cluster_name}")
                return None
            
            # Calculate cost breakdown
            breakdown = await self._calculate_eks_cost_breakdown(cluster_name, cost_data, cluster_details)
            
            logger.info(f"✅ Retrieved cost breakdown for {cluster_name}: ${breakdown.total_cost:.2f}")
            return breakdown
            
        except Exception as e:
            logger.error(f"❌ Failed to get EKS cluster costs: {e}")
            return None
    
    async def _get_cluster_details(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """Get EKS cluster details"""
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            return response['cluster']
        except ClientError as e:
            logger.error(f"❌ Failed to get cluster details: {e}")
            return None
    
    async def _get_eks_cost_data(self, cluster_name: str, 
                                start_date: datetime, 
                                end_date: datetime) -> Optional[List[AWSCostData]]:
        """Get EKS-related cost data"""
        try:
            # Get cost data for EKS and related services
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ],
                Filter={
                    'Or': [
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Container Service for Kubernetes']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon EC2']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon EBS']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['AWS Data Transfer']}}
                    ]
                }
            )
            
            cost_data = []
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    keys = group['Keys']
                    service = keys[0].split('$')[1] if '$' in keys[0] else keys[0]
                    region = keys[1].split('$')[1] if '$' in keys[1] else keys[1]
                    
                    cost_data.append(AWSCostData(
                        service=service,
                        region=region,
                        cost=float(group['Metrics']['UnblendedCost']['Amount']),
                        usage_amount=float(group['Metrics']['UsageQuantity']['Amount']),
                        usage_unit=group['Metrics']['UsageQuantity']['Unit'],
                        start_date=datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d'),
                        end_date=datetime.strptime(result['TimePeriod']['End'], '%Y-%m-%d')
                    ))
            
            return cost_data
            
        except ClientError as e:
            logger.error(f"❌ Failed to get EKS cost data: {e}")
            return None
    
    async def _calculate_eks_cost_breakdown(self, cluster_name: str, 
                                          cost_data: List[AWSCostData],
                                          cluster_details: Dict[str, Any]) -> EKSCostBreakdown:
        """Calculate EKS cost breakdown"""
        node_costs = 0.0
        storage_costs = 0.0
        network_costs = 0.0
        other_costs = 0.0
        
        for data in cost_data:
            if data.service == "Amazon EC2":
                node_costs += data.cost
            elif data.service == "Amazon EBS":
                storage_costs += data.cost
            elif data.service == "AWS Data Transfer":
                network_costs += data.cost
            elif data.service == "Amazon Elastic Container Service for Kubernetes":
                other_costs += data.cost
            else:
                other_costs += data.cost
        
        total_cost = node_costs + storage_costs + network_costs + other_costs
        
        return EKSCostBreakdown(
            cluster_name=cluster_name,
            node_costs=node_costs,
            storage_costs=storage_costs,
            network_costs=network_costs,
            other_costs=other_costs,
            total_cost=total_cost,
            period_start=min(data.start_date for data in cost_data),
            period_end=max(data.end_date for data in cost_data)
        )
    
    async def get_resource_costs(self, resource_ids: List[str], 
                               start_date: datetime, 
                               end_date: datetime) -> Dict[str, float]:
        """Get costs for specific resources"""
        try:
            logger.info(f"💰 Retrieving costs for {len(resource_ids)} resources")
            
            resource_costs = {}
            
            for resource_id in resource_ids:
                response = self.ce_client.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date.strftime('%Y-%m-%d'),
                        'End': end_date.strftime('%Y-%m-%d')
                    },
                    Granularity='DAILY',
                    Metrics=['UnblendedCost'],
                    Filter={
                        'Dimensions': {
                            'Key': 'RESOURCE_ID',
                            'Values': [resource_id]
                        }
                    }
                )
                
                total_cost = 0.0
                for result in response['ResultsByTime']:
                    for group in result['Groups']:
                        total_cost += float(group['Metrics']['UnblendedCost']['Amount'])
                
                resource_costs[resource_id] = total_cost
            
            logger.info(f"✅ Retrieved costs for {len(resource_costs)} resources")
            return resource_costs
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource costs: {e}")
            return {}
    
    async def get_cost_trends(self, cluster_name: str, 
                             days: int = 30) -> List[Dict[str, Any]]:
        """Get cost trends for a cluster"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                Filter={
                    'Or': [
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Container Service for Kubernetes']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon EC2']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon EBS']}}
                    ]
                }
            )
            
            trends = []
            for result in response['ResultsByTime']:
                date = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d')
                cost = 0.0
                
                for group in result['Groups']:
                    cost += float(group['Metrics']['UnblendedCost']['Amount'])
                
                trends.append({
                    'date': date,
                    'cost': cost,
                    'cluster': cluster_name
                })
            
            logger.info(f"✅ Retrieved cost trends for {cluster_name}")
            return trends
            
        except Exception as e:
            logger.error(f"❌ Failed to get cost trends: {e}")
            return []
    
    async def get_cost_recommendations(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        try:
            logger.info(f"💡 Generating cost recommendations for {cluster_name}")
            
            # Get current cost breakdown
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            breakdown = await self.get_eks_cluster_costs(cluster_name, start_date, end_date)
            if not breakdown:
                return []
            
            recommendations = []
            
            # Node optimization recommendations
            if breakdown.node_costs > breakdown.total_cost * 0.6:  # More than 60% on nodes
                recommendations.append({
                    'type': 'node_optimization',
                    'priority': 'high',
                    'description': 'High node costs detected. Consider right-sizing or spot instances.',
                    'potential_savings': breakdown.node_costs * 0.2,  # 20% potential savings
                    'impact': 'medium'
                })
            
            # Storage optimization recommendations
            if breakdown.storage_costs > breakdown.total_cost * 0.2:  # More than 20% on storage
                recommendations.append({
                    'type': 'storage_optimization',
                    'priority': 'medium',
                    'description': 'High storage costs detected. Consider EBS optimization.',
                    'potential_savings': breakdown.storage_costs * 0.15,  # 15% potential savings
                    'impact': 'low'
                })
            
            # Network optimization recommendations
            if breakdown.network_costs > breakdown.total_cost * 0.1:  # More than 10% on network
                recommendations.append({
                    'type': 'network_optimization',
                    'priority': 'low',
                    'description': 'High network costs detected. Consider data transfer optimization.',
                    'potential_savings': breakdown.network_costs * 0.1,  # 10% potential savings
                    'impact': 'low'
                })
            
            logger.info(f"✅ Generated {len(recommendations)} cost recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to get cost recommendations: {e}")
            return [] 