"""
GCP Billing Integration for UPID CLI
Implements real Google Cloud Billing API integration for GKE cost analysis
"""

from google.cloud import billing_v1
from google.cloud import container_v1
from google.cloud import compute_v1
from google.cloud import bigquery
from typing import List, Dict, Any, Optional
import datetime

class GCPBillingClient:
    """
    GCP Billing Client for real-time cost data collection
    """
    def __init__(self, project_id: str, billing_account_id: str, credentials_path: Optional[str] = None):
        self.project_id = project_id
        self.billing_account_id = billing_account_id
        self.billing_client = billing_v1.CloudBillingClient.from_service_account_file(credentials_path) if credentials_path else billing_v1.CloudBillingClient()
        self.container_client = container_v1.ClusterManagerClient.from_service_account_file(credentials_path) if credentials_path else container_v1.ClusterManagerClient()
        self.compute_client = compute_v1.InstancesClient.from_service_account_file(credentials_path) if credentials_path else compute_v1.InstancesClient()
        self.bq_client = bigquery.Client.from_service_account_json(credentials_path) if credentials_path else bigquery.Client()

    def get_gke_clusters(self) -> List[str]:
        clusters = []
        parent = f"projects/{self.project_id}/locations/-"
        request = container_v1.ListClustersRequest(parent=parent)
        page_result = self.container_client.list_clusters(request=request)
        for cluster in page_result:
            clusters.append(cluster.name)
        return clusters

    def get_gke_cost(self, start_date: str, end_date: str) -> Dict[str, Any]:
        # Query BigQuery billing export for GKE costs
        query = f'''
            SELECT
                service.description AS service,
                sku.description AS sku,
                SUM(cost) AS total_cost,
                currency,
                usage_start_time
            FROM `{self.project_id}.billing.gcp_billing_export_v1_*`
            WHERE service.description = 'Kubernetes Engine'
              AND usage_start_time >= '{start_date}'
              AND usage_start_time < '{end_date}'
            GROUP BY service, sku, currency, usage_start_time
            ORDER BY usage_start_time
        '''
        query_job = self.bq_client.query(query)
        results = [dict(row) for row in query_job]
        total_cost = sum(row['total_cost'] for row in results)
        currency = results[0]['currency'] if results else 'USD'
        return {
            "costs": results,
            "total_cost": total_cost,
            "currency": currency,
            "period": {"start": start_date, "end": end_date}
        }

    def get_compute_engine_cost(self, start_date: str, end_date: str) -> Dict[str, Any]:
        # Query BigQuery billing export for Compute Engine costs
        query = f'''
            SELECT
                service.description AS service,
                sku.description AS sku,
                SUM(cost) AS total_cost,
                currency,
                usage_start_time
            FROM `{self.project_id}.billing.gcp_billing_export_v1_*`
            WHERE service.description = 'Compute Engine'
              AND usage_start_time >= '{start_date}'
              AND usage_start_time < '{end_date}'
            GROUP BY service, sku, currency, usage_start_time
            ORDER BY usage_start_time
        '''
        query_job = self.bq_client.query(query)
        results = [dict(row) for row in query_job]
        total_cost = sum(row['total_cost'] for row in results)
        currency = results[0]['currency'] if results else 'USD'
        return {
            "costs": results,
            "total_cost": total_cost,
            "currency": currency,
            "period": {"start": start_date, "end": end_date}
        }

    def get_node_pool_cost(self, gke_cluster_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        # This requires mapping Compute Engine instances to GKE node pools
        # For now, return Compute Engine cost as a proxy
        return self.get_compute_engine_cost(start_date, end_date)

    def get_project_cost_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        # Query BigQuery billing export for total project cost
        query = f'''
            SELECT
                SUM(cost) AS total_cost,
                currency
            FROM `{self.project_id}.billing.gcp_billing_export_v1_*`
            WHERE usage_start_time >= '{start_date}'
              AND usage_start_time < '{end_date}'
            GROUP BY currency
        '''
        query_job = self.bq_client.query(query)
        results = [dict(row) for row in query_job]
        total_cost = results[0]['total_cost'] if results else 0.0
        currency = results[0]['currency'] if results else 'USD'
        return {
            "costs": results,
            "total_cost": total_cost,
            "currency": currency,
            "period": {"start": start_date, "end": end_date}
        }

    @staticmethod
    def get_default_dates(days: int = 7) -> (str, str):
        end = datetime.date.today()
        start = end - datetime.timedelta(days=days)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d') 