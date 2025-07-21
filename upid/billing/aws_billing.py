"""
AWS Billing Integration for UPID CLI
Implements real AWS Cost Explorer API integration for EKS and EC2 cost analysis
"""

import boto3
from typing import List, Dict, Any, Optional
import datetime

class AWSBillingClient:
    """
    AWS Billing Client for real-time cost data collection
    """
    def __init__(self, aws_access_key_id: Optional[str] = None, aws_secret_access_key: Optional[str] = None, aws_session_token: Optional[str] = None, region_name: str = 'us-east-1'):
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name
        )
        self.ce = self.session.client('ce')  # Cost Explorer
        self.eks = self.session.client('eks')
        self.ec2 = self.session.client('ec2')

    def get_eks_clusters(self) -> List[str]:
        """List all EKS clusters in the account"""
        clusters = []
        paginator = self.eks.get_paginator('list_clusters')
        for page in paginator.paginate():
            clusters.extend(page.get('clusters', []))
        return clusters

    def get_eks_cost(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get EKS cost for the given period (YYYY-MM-DD)"""
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                'Dimensions': {
                    'Key': 'Service',
                    'Values': ['Amazon Elastic Kubernetes Service']
                }
            }
        )
        return response

    def get_ec2_cost(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get EC2 cost for the given period (YYYY-MM-DD)"""
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                'Dimensions': {
                    'Key': 'Service',
                    'Values': ['Amazon Elastic Compute Cloud - Compute']
                }
            }
        )
        return response

    def get_node_group_cost(self, eks_cluster_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get cost for EC2 node groups in a specific EKS cluster"""
        # This requires mapping EC2 instances to EKS node groups
        # For now, return EC2 cost as a proxy
        return self.get_ec2_cost(start_date, end_date)

    def get_account_cost_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get total AWS account cost summary for the period"""
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        return response

    @staticmethod
    def get_default_dates(days: int = 7) -> (str, str):
        """Get default start and end dates for the last N days"""
        end = datetime.date.today()
        start = end - datetime.timedelta(days=days)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d') 