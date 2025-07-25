"""
UPID CLI - Cloud Cost Manager
Unified cloud cost management and analysis system
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from enum import Enum

from .aws.billing import AWSBillingClient, EKSCostBreakdown
from .aws.resources import AWSResourceMapper
from .gcp.billing import GCPBillingClient, GKECostBreakdown
from .gcp.resources import GCPResourceMapper
from .azure.billing import AzureBillingClient, AKSCostBreakdown
from .azure.resources import AzureResourceMapper

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


@dataclass
class CloudCostBreakdown:
    """Unified cloud cost breakdown"""
    provider: CloudProvider
    cluster_name: str
    node_costs: float
    storage_costs: float
    network_costs: float
    other_costs: float
    total_cost: float
    period_start: datetime
    period_end: datetime
    currency: str = "USD"


@dataclass
class CrossCloudComparison:
    """Cross-cloud cost comparison"""
    cluster_name: str
    aws_cost: Optional[float] = None
    gcp_cost: Optional[float] = None
    azure_cost: Optional[float] = None
    recommended_provider: Optional[CloudProvider] = None
    potential_savings: Optional[float] = None


class CloudCostManager:
    """
    Unified cloud cost management system
    
    Provides comprehensive multi-cloud cost analysis capabilities:
    - Multi-cloud cost aggregation
    - Cross-cloud cost comparison
    - Resource cost attribution
    - Cost optimization recommendations
    - ROI calculations
    """
    
    def __init__(self):
        # Cloud provider clients
        self.aws_billing = None
        self.aws_resources = None
        self.gcp_billing = None
        self.gcp_resources = None
        self.azure_billing = None
        self.azure_resources = None
        
        # Configuration
        self.enabled_providers: List[CloudProvider] = []
        self.cost_cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour
        
        logger.info("🔧 Initializing cloud cost manager")
    
    async def initialize(self, 
                        aws_config: Optional[Dict[str, Any]] = None,
                        gcp_config: Optional[Dict[str, Any]] = None,
                        azure_config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize cloud cost manager with provider configurations"""
        try:
            logger.info("🚀 Initializing cloud cost manager...")
            
            # Initialize AWS if configured
            if aws_config:
                await self._initialize_aws(aws_config)
                self.enabled_providers.append(CloudProvider.AWS)
            
            # Initialize GCP if configured
            if gcp_config:
                await self._initialize_gcp(gcp_config)
                self.enabled_providers.append(CloudProvider.GCP)
            
            # Initialize Azure if configured
            if azure_config:
                await self._initialize_azure(azure_config)
                self.enabled_providers.append(CloudProvider.AZURE)
            
            if not self.enabled_providers:
                logger.warning("⚠️ No cloud providers configured")
                return False
            
            logger.info(f"✅ Cloud cost manager initialized with providers: {[p.value for p in self.enabled_providers]}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cloud cost manager: {e}")
            return False
    
    async def _initialize_aws(self, config: Dict[str, Any]):
        """Initialize AWS clients"""
        try:
            self.aws_billing = AWSBillingClient(
                aws_access_key_id=config.get('aws_access_key_id'),
                aws_secret_access_key=config.get('aws_secret_access_key'),
                aws_region=config.get('aws_region', 'us-east-1')
            )
            
            self.aws_resources = AWSResourceMapper(
                aws_access_key_id=config.get('aws_access_key_id'),
                aws_secret_access_key=config.get('aws_secret_access_key'),
                aws_region=config.get('aws_region', 'us-east-1')
            )
            
            await self.aws_billing.initialize()
            await self.aws_resources.initialize()
            
            logger.info("✅ AWS clients initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS clients: {e}")
            raise
    
    async def _initialize_gcp(self, config: Dict[str, Any]):
        """Initialize GCP clients"""
        try:
            self.gcp_billing = GCPBillingClient(
                project_id=config.get('project_id'),
                billing_account_id=config.get('billing_account_id')
            )
            
            self.gcp_resources = GCPResourceMapper(
                project_id=config.get('project_id')
            )
            
            await self.gcp_billing.initialize()
            await self.gcp_resources.initialize()
            
            logger.info("✅ GCP clients initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCP clients: {e}")
            raise
    
    async def _initialize_azure(self, config: Dict[str, Any]):
        """Initialize Azure clients"""
        try:
            self.azure_billing = AzureBillingClient(
                subscription_id=config.get('subscription_id'),
                tenant_id=config.get('tenant_id')
            )
            
            self.azure_resources = AzureResourceMapper(
                subscription_id=config.get('subscription_id')
            )
            
            await self.azure_billing.initialize()
            await self.azure_resources.initialize()
            
            logger.info("✅ Azure clients initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure clients: {e}")
            raise
    
    async def get_cluster_costs(self, cluster_name: str, 
                              provider: CloudProvider,
                              start_date: datetime, 
                              end_date: datetime) -> Optional[CloudCostBreakdown]:
        """Get cluster costs for a specific provider"""
        try:
            logger.info(f"💰 Getting costs for {cluster_name} on {provider.value}")
            
            if provider == CloudProvider.AWS and self.aws_billing:
                breakdown = await self.aws_billing.get_eks_cluster_costs(cluster_name, start_date, end_date)
                if breakdown:
                    return CloudCostBreakdown(
                        provider=provider,
                        cluster_name=breakdown.cluster_name,
                        node_costs=breakdown.node_costs,
                        storage_costs=breakdown.storage_costs,
                        network_costs=breakdown.network_costs,
                        other_costs=breakdown.other_costs,
                        total_cost=breakdown.total_cost,
                        period_start=breakdown.period_start,
                        period_end=breakdown.period_end
                    )
                    
            elif provider == CloudProvider.GCP and self.gcp_billing:
                breakdown = await self.gcp_billing.get_gke_cluster_costs(cluster_name, start_date, end_date)
                if breakdown:
                    return CloudCostBreakdown(
                        provider=provider,
                        cluster_name=breakdown.cluster_name,
                        node_costs=breakdown.node_costs,
                        storage_costs=breakdown.storage_costs,
                        network_costs=breakdown.network_costs,
                        other_costs=breakdown.other_costs,
                        total_cost=breakdown.total_cost,
                        period_start=breakdown.period_start,
                        period_end=breakdown.period_end
                    )
                    
            elif provider == CloudProvider.AZURE and self.azure_billing:
                breakdown = await self.azure_billing.get_aks_cluster_costs(cluster_name, start_date, end_date)
                if breakdown:
                    return CloudCostBreakdown(
                        provider=provider,
                        cluster_name=breakdown.cluster_name,
                        node_costs=breakdown.node_costs,
                        storage_costs=breakdown.storage_costs,
                        network_costs=breakdown.network_costs,
                        other_costs=breakdown.other_costs,
                        total_cost=breakdown.total_cost,
                        period_start=breakdown.period_start,
                        period_end=breakdown.period_end
                    )
            
            logger.warning(f"⚠️ No cost data available for {cluster_name} on {provider.value}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster costs: {e}")
            return None
    
    async def get_cross_cloud_comparison(self, cluster_name: str,
                                       start_date: datetime,
                                       end_date: datetime) -> CrossCloudComparison:
        """Compare costs across different cloud providers"""
        try:
            logger.info(f"🔍 Comparing costs for {cluster_name} across cloud providers")
            
            comparison = CrossCloudComparison(cluster_name=cluster_name)
            costs = {}
            
            # Get costs for each enabled provider
            for provider in self.enabled_providers:
                breakdown = await self.get_cluster_costs(cluster_name, provider, start_date, end_date)
                if breakdown:
                    costs[provider] = breakdown.total_cost
                    
                    if provider == CloudProvider.AWS:
                        comparison.aws_cost = breakdown.total_cost
                    elif provider == CloudProvider.GCP:
                        comparison.gcp_cost = breakdown.total_cost
                    elif provider == CloudProvider.AZURE:
                        comparison.azure_cost = breakdown.total_cost
            
            # Find the most cost-effective provider
            if costs:
                min_cost = min(costs.values())
                max_cost = max(costs.values())
                comparison.recommended_provider = min(costs, key=costs.get)
                comparison.potential_savings = max_cost - min_cost
            
            logger.info(f"✅ Cross-cloud comparison completed for {cluster_name}")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Failed to get cross-cloud comparison: {e}")
            return CrossCloudComparison(cluster_name=cluster_name)
    
    async def get_cost_recommendations(self, cluster_name: str,
                                     provider: CloudProvider) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations for a specific provider"""
        try:
            logger.info(f"💡 Getting cost recommendations for {cluster_name} on {provider.value}")
            
            if provider == CloudProvider.AWS and self.aws_billing:
                return await self.aws_billing.get_cost_recommendations(cluster_name)
            elif provider == CloudProvider.GCP and self.gcp_billing:
                return await self.gcp_billing.get_cost_recommendations(cluster_name)
            elif provider == CloudProvider.AZURE and self.azure_billing:
                return await self.azure_billing.get_cost_recommendations(cluster_name)
            
            logger.warning(f"⚠️ No recommendations available for {provider.value}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get cost recommendations: {e}")
            return []
    
    async def get_cost_trends(self, cluster_name: str,
                             provider: CloudProvider,
                             days: int = 30) -> List[Dict[str, Any]]:
        """Get cost trends for a specific provider"""
        try:
            logger.info(f"📈 Getting cost trends for {cluster_name} on {provider.value}")
            
            if provider == CloudProvider.AWS and self.aws_billing:
                return await self.aws_billing.get_cost_trends(cluster_name, days)
            elif provider == CloudProvider.GCP and self.gcp_billing:
                return await self.gcp_billing.get_cost_trends(cluster_name, days)
            elif provider == CloudProvider.AZURE and self.azure_billing:
                return await self.azure_billing.get_cost_trends(cluster_name, days)
            
            logger.warning(f"⚠️ No trend data available for {provider.value}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get cost trends: {e}")
            return []
    
    async def get_resource_costs(self, resource_ids: List[str],
                               provider: CloudProvider,
                               start_date: datetime,
                               end_date: datetime) -> Dict[str, float]:
        """Get costs for specific resources on a provider"""
        try:
            logger.info(f"💰 Getting resource costs for {len(resource_ids)} resources on {provider.value}")
            
            if provider == CloudProvider.AWS and self.aws_billing:
                return await self.aws_billing.get_resource_costs(resource_ids, start_date, end_date)
            elif provider == CloudProvider.GCP and self.gcp_billing:
                return await self.gcp_billing.get_resource_costs(resource_ids, start_date, end_date)
            elif provider == CloudProvider.AZURE and self.azure_billing:
                return await self.azure_billing.get_resource_costs(resource_ids, start_date, end_date)
            
            logger.warning(f"⚠️ No resource cost data available for {provider.value}")
            return {}
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource costs: {e}")
            return {}
    
    async def get_cluster_resources(self, cluster_name: str,
                                  provider: CloudProvider) -> List[Dict[str, Any]]:
        """Get cluster resources for a specific provider"""
        try:
            logger.info(f"🔍 Getting resources for {cluster_name} on {provider.value}")
            
            if provider == CloudProvider.AWS and self.aws_resources:
                resources = await self.aws_resources.get_cluster_resources(cluster_name)
                return [self._convert_aws_resource(r) for r in resources]
            elif provider == CloudProvider.GCP and self.gcp_resources:
                resources = await self.gcp_resources.get_cluster_resources(cluster_name)
                return [self._convert_gcp_resource(r) for r in resources]
            elif provider == CloudProvider.AZURE and self.azure_resources:
                resources = await self.azure_resources.get_cluster_resources(cluster_name)
                return [self._convert_azure_resource(r) for r in resources]
            
            logger.warning(f"⚠️ No resource data available for {provider.value}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster resources: {e}")
            return []
    
    def _convert_aws_resource(self, resource) -> Dict[str, Any]:
        """Convert AWS resource to unified format"""
        return {
            'resource_id': resource.resource_id,
            'resource_type': resource.resource_type,
            'name': resource.name,
            'namespace': resource.namespace,
            'location': resource.region,
            'instance_type': resource.instance_type,
            'storage_size': resource.storage_size,
            'tags': resource.tags
        }
    
    def _convert_gcp_resource(self, resource) -> Dict[str, Any]:
        """Convert GCP resource to unified format"""
        return {
            'resource_id': resource.resource_id,
            'resource_type': resource.resource_type,
            'name': resource.name,
            'namespace': resource.namespace,
            'location': resource.location,
            'machine_type': resource.machine_type,
            'disk_size': resource.disk_size,
            'labels': resource.labels
        }
    
    def _convert_azure_resource(self, resource) -> Dict[str, Any]:
        """Convert Azure resource to unified format"""
        return {
            'resource_id': resource.resource_id,
            'resource_type': resource.resource_type,
            'name': resource.name,
            'namespace': resource.namespace,
            'location': resource.location,
            'vm_size': resource.vm_size,
            'disk_size': resource.disk_size,
            'tags': resource.tags
        }
    
    async def get_roi_analysis(self, cluster_name: str,
                              provider: CloudProvider,
                              optimization_savings: float) -> Dict[str, Any]:
        """Calculate ROI for cost optimizations"""
        try:
            logger.info(f"📊 Calculating ROI for {cluster_name} on {provider.value}")
            
            # Get current costs
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            breakdown = await self.get_cluster_costs(cluster_name, provider, start_date, end_date)
            if not breakdown:
                return {}
            
            current_monthly_cost = breakdown.total_cost
            optimized_monthly_cost = current_monthly_cost - optimization_savings
            annual_savings = optimization_savings * 12
            roi_percentage = (optimization_savings / current_monthly_cost) * 100
            
            return {
                'cluster_name': cluster_name,
                'provider': provider.value,
                'current_monthly_cost': current_monthly_cost,
                'optimized_monthly_cost': optimized_monthly_cost,
                'monthly_savings': optimization_savings,
                'annual_savings': annual_savings,
                'roi_percentage': roi_percentage,
                'payback_period_months': 1.0  # Immediate savings
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate ROI: {e}")
            return {} 