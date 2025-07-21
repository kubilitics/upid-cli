"""
Unified Billing Interface for UPID CLI
Provides provider-agnostic cost calculation and cross-cloud cost comparison
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from .aws_billing import AWSBillingClient
from .gcp_billing import GCPBillingClient
from .azure_billing import AzureBillingClient

@dataclass
class CostData:
    """Standardized cost data structure"""
    provider: str
    service: str
    cluster_name: Optional[str]
    cost: float
    currency: str
    period_start: str
    period_end: str
    details: Dict[str, Any]

@dataclass
class CostSummary:
    """Unified cost summary across providers"""
    total_cost: float
    currency: str
    provider_breakdown: Dict[str, float]
    service_breakdown: Dict[str, float]
    period_start: str
    period_end: str

class CloudBillingIntegrator:
    """
    Unified billing integrator for cross-cloud cost analysis
    """
    
    def __init__(self):
        self.aws_client: Optional[AWSBillingClient] = None
        self.gcp_client: Optional[GCPBillingClient] = None
        self.azure_client: Optional[AzureBillingClient] = None
        self.providers = []
    
    def add_aws_provider(self, aws_access_key_id: Optional[str] = None, 
                        aws_secret_access_key: Optional[str] = None,
                        aws_session_token: Optional[str] = None,
                        region_name: str = 'us-east-1'):
        """Add AWS billing provider"""
        try:
            self.aws_client = AWSBillingClient(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name
            )
            self.providers.append('aws')
            return True
        except Exception as e:
            print(f"Failed to initialize AWS billing client: {e}")
            return False
    
    def add_gcp_provider(self, project_id: str, credentials_path: Optional[str] = None):
        """Add GCP billing provider"""
        try:
            self.gcp_client = GCPBillingClient(project_id, credentials_path)
            self.providers.append('gcp')
            return True
        except Exception as e:
            print(f"Failed to initialize GCP billing client: {e}")
            return False
    
    def add_azure_provider(self, subscription_id: str, resource_group: Optional[str] = None):
        """Add Azure billing provider"""
        try:
            self.azure_client = AzureBillingClient(subscription_id, resource_group)
            self.providers.append('azure')
            return True
        except Exception as e:
            print(f"Failed to initialize Azure billing client: {e}")
            return False
    
    def get_all_clusters(self) -> Dict[str, List[str]]:
        """Get all clusters across all providers"""
        clusters = {}
        
        if self.aws_client:
            try:
                clusters['aws'] = self.aws_client.get_eks_clusters()
            except Exception as e:
                print(f"Failed to get AWS clusters: {e}")
                clusters['aws'] = []
        
        if self.gcp_client:
            try:
                clusters['gcp'] = self.gcp_client.get_gke_clusters()
            except Exception as e:
                print(f"Failed to get GCP clusters: {e}")
                clusters['gcp'] = []
        
        if self.azure_client:
            try:
                clusters['azure'] = self.azure_client.get_aks_clusters()
            except Exception as e:
                print(f"Failed to get Azure clusters: {e}")
                clusters['azure'] = []
        
        return clusters
    
    def get_provider_cost(self, provider: str, start_date: str, end_date: str) -> List[CostData]:
        """Get cost data for a specific provider"""
        costs = []
        
        if provider == 'aws' and self.aws_client:
            try:
                # EKS costs
                eks_cost = self.aws_client.get_eks_cost(start_date, end_date)
                costs.append(CostData(
                    provider='aws',
                    service='eks',
                    cluster_name=None,
                    cost=eks_cost.get('total_cost', 0.0),
                    currency=eks_cost.get('currency', 'USD'),
                    period_start=start_date,
                    period_end=end_date,
                    details=eks_cost
                ))
                
                # EC2 costs
                ec2_cost = self.aws_client.get_ec2_cost(start_date, end_date)
                costs.append(CostData(
                    provider='aws',
                    service='ec2',
                    cluster_name=None,
                    cost=ec2_cost.get('total_cost', 0.0),
                    currency=ec2_cost.get('currency', 'USD'),
                    period_start=start_date,
                    period_end=end_date,
                    details=ec2_cost
                ))
            except Exception as e:
                print(f"Failed to get AWS costs: {e}")
        
        elif provider == 'gcp' and self.gcp_client:
            try:
                # GKE costs
                gke_cost = self.gcp_client.get_gke_cost(start_date, end_date)
                costs.append(CostData(
                    provider='gcp',
                    service='gke',
                    cluster_name=None,
                    cost=gke_cost.get('total_cost', 0.0),
                    currency=gke_cost.get('currency', 'USD'),
                    period_start=start_date,
                    period_end=end_date,
                    details=gke_cost
                ))
                
                # Compute Engine costs
                compute_cost = self.gcp_client.get_compute_engine_cost(start_date, end_date)
                costs.append(CostData(
                    provider='gcp',
                    service='compute',
                    cluster_name=None,
                    cost=compute_cost.get('total_cost', 0.0),
                    currency=compute_cost.get('currency', 'USD'),
                    period_start=start_date,
                    period_end=end_date,
                    details=compute_cost
                ))
            except Exception as e:
                print(f"Failed to get GCP costs: {e}")
        
        elif provider == 'azure' and self.azure_client:
            try:
                # AKS costs
                aks_cost = self.azure_client.get_aks_cost(start_date, end_date)
                costs.append(CostData(
                    provider='azure',
                    service='aks',
                    cluster_name=None,
                    cost=aks_cost.get('total_cost', 0.0),
                    currency=aks_cost.get('currency', 'USD'),
                    period_start=start_date,
                    period_end=end_date,
                    details=aks_cost
                ))
                
                # VM costs
                vm_cost = self.azure_client.get_vm_cost(start_date, end_date)
                costs.append(CostData(
                    provider='azure',
                    service='vm',
                    cluster_name=None,
                    cost=vm_cost.get('total_cost', 0.0),
                    currency=vm_cost.get('currency', 'USD'),
                    period_start=start_date,
                    period_end=end_date,
                    details=vm_cost
                ))
            except Exception as e:
                print(f"Failed to get Azure costs: {e}")
        
        return costs
    
    def get_unified_cost_summary(self, start_date: str, end_date: str) -> CostSummary:
        """Get unified cost summary across all providers"""
        all_costs = []
        
        for provider in self.providers:
            provider_costs = self.get_provider_cost(provider, start_date, end_date)
            all_costs.extend(provider_costs)
        
        # Calculate totals
        total_cost = sum(cost.cost for cost in all_costs)
        provider_breakdown = {}
        service_breakdown = {}
        
        for cost in all_costs:
            # Provider breakdown
            if cost.provider not in provider_breakdown:
                provider_breakdown[cost.provider] = 0.0
            provider_breakdown[cost.provider] += cost.cost
            
            # Service breakdown
            service_key = f"{cost.provider}_{cost.service}"
            if service_key not in service_breakdown:
                service_breakdown[service_key] = 0.0
            service_breakdown[service_key] += cost.cost
        
        return CostSummary(
            total_cost=total_cost,
            currency='USD',
            provider_breakdown=provider_breakdown,
            service_breakdown=service_breakdown,
            period_start=start_date,
            period_end=end_date
        )
    
    def compare_provider_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Compare costs across providers"""
        summary = self.get_unified_cost_summary(start_date, end_date)
        
        comparison = {
            'total_cost': summary.total_cost,
            'currency': summary.currency,
            'period': {'start': start_date, 'end': end_date},
            'provider_comparison': summary.provider_breakdown,
            'service_comparison': summary.service_breakdown,
            'recommendations': []
        }
        
        # Generate recommendations
        if len(summary.provider_breakdown) > 1:
            min_provider = min(summary.provider_breakdown, key=summary.provider_breakdown.get)
            max_provider = max(summary.provider_breakdown, key=summary.provider_breakdown.get)
            
            if summary.provider_breakdown[max_provider] > 0:
                savings = summary.provider_breakdown[max_provider] - summary.provider_breakdown[min_provider]
                comparison['recommendations'].append({
                    'type': 'cost_optimization',
                    'message': f"Consider migrating from {max_provider} to {min_provider} for potential savings of ${savings:.2f}",
                    'savings': savings
                })
        
        return comparison
    
    @staticmethod
    def get_default_dates(days: int = 7) -> (str, str):
        """Get default start and end dates for the last N days"""
        end = datetime.today()
        start = end - timedelta(days=days)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d') 