"""
Cloud Kubernetes Cluster Detector
Detects cloud Kubernetes clusters (EKS, GKE, AKS, etc.)
"""

import os
import subprocess
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CloudClusterInfo:
    """Information about detected cloud cluster"""
    detected: bool
    cluster_type: str
    provider: str
    kubeconfig_path: Optional[str] = None
    context_name: Optional[str] = None
    cluster_name: Optional[str] = None
    region: Optional[str] = None
    project_id: Optional[str] = None
    resource_group: Optional[str] = None
    auth_required: bool = True
    status: str = "unknown"

class CloudKubernetesDetector:
    """
    Detects cloud Kubernetes clusters
    """
    
    def __init__(self):
        self.supported_providers = ['aws', 'gcp', 'azure', 'digitalocean', 'linode']
    
    async def detect(self) -> CloudClusterInfo:
        """
        Detect cloud Kubernetes clusters
        """
        try:
            # Check for AWS EKS
            eks_info = await self._detect_eks()
            if eks_info.detected:
                return eks_info
            
            # Check for GCP GKE
            gke_info = await self._detect_gke()
            if gke_info.detected:
                return gke_info
            
            # Check for Azure AKS
            aks_info = await self._detect_aks()
            if aks_info.detected:
                return aks_info
            
            # Check for DigitalOcean
            do_info = await self._detect_digitalocean()
            if do_info.detected:
                return do_info
            
            # Check for Linode
            linode_info = await self._detect_linode()
            if linode_info.detected:
                return linode_info
            
            return CloudClusterInfo(detected=False, cluster_type="none", provider="none")
            
        except Exception as e:
            logger.error(f"Cloud cluster detection failed: {e}")
            return CloudClusterInfo(detected=False, cluster_type="error", provider="error")
    
    async def _detect_eks(self) -> CloudClusterInfo:
        """
        Detect AWS EKS clusters
        """
        try:
            # Check if AWS CLI is available
            if not self._check_aws_cli():
                return CloudClusterInfo(detected=False, cluster_type="eks", provider="aws")
            
            # Check if kubectl is available
            if not self._check_kubectl():
                return CloudClusterInfo(detected=False, cluster_type="eks", provider="aws")
            
            # Get EKS clusters
            result = subprocess.run(
                ['aws', 'eks', 'list-clusters'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse cluster list
                clusters = self._parse_aws_clusters(result.stdout)
                if clusters:
                    # Get the first cluster
                    cluster_name = clusters[0]
                    
                    # Get cluster info
                    cluster_info = await self._get_eks_cluster_info(cluster_name)
                    if cluster_info:
                        return CloudClusterInfo(
                            detected=True,
                            cluster_type="eks",
                            provider="aws",
                            kubeconfig_path=os.path.expanduser("~/.kube/config"),
                            context_name=f"arn:aws:eks:{cluster_info['region']}:{cluster_info['account']}:cluster/{cluster_name}",
                            cluster_name=cluster_name,
                            region=cluster_info['region'],
                            status="running"
                        )
            
            return CloudClusterInfo(detected=False, cluster_type="eks", provider="aws")
            
        except Exception as e:
            logger.debug(f"EKS detection failed: {e}")
            return CloudClusterInfo(detected=False, cluster_type="eks", provider="aws")
    
    async def _detect_gke(self) -> CloudClusterInfo:
        """
        Detect GCP GKE clusters
        """
        try:
            # Check if gcloud is available
            if not self._check_gcloud():
                return CloudClusterInfo(detected=False, cluster_type="gke", provider="gcp")
            
            # Check if kubectl is available
            if not self._check_kubectl():
                return CloudClusterInfo(detected=False, cluster_type="gke", provider="gcp")
            
            # Get GKE clusters
            result = subprocess.run(
                ['gcloud', 'container', 'clusters', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse cluster list
                clusters = self._parse_gcp_clusters(result.stdout)
                if clusters:
                    # Get the first cluster
                    cluster_info = clusters[0]
                    
                    return CloudClusterInfo(
                        detected=True,
                        cluster_type="gke",
                        provider="gcp",
                        kubeconfig_path=os.path.expanduser("~/.kube/config"),
                        context_name=f"gke_{cluster_info['project']}_{cluster_info['zone']}_{cluster_info['name']}",
                        cluster_name=cluster_info['name'],
                        region=cluster_info['zone'],
                        project_id=cluster_info['project'],
                        status="running"
                    )
            
            return CloudClusterInfo(detected=False, cluster_type="gke", provider="gcp")
            
        except Exception as e:
            logger.debug(f"GKE detection failed: {e}")
            return CloudClusterInfo(detected=False, cluster_type="gke", provider="gcp")
    
    async def _detect_aks(self) -> CloudClusterInfo:
        """
        Detect Azure AKS clusters
        """
        try:
            # Check if Azure CLI is available
            if not self._check_azure_cli():
                return CloudClusterInfo(detected=False, cluster_type="aks", provider="azure")
            
            # Check if kubectl is available
            if not self._check_kubectl():
                return CloudClusterInfo(detected=False, cluster_type="aks", provider="azure")
            
            # Get AKS clusters
            result = subprocess.run(
                ['az', 'aks', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse cluster list
                clusters = self._parse_azure_clusters(result.stdout)
                if clusters:
                    # Get the first cluster
                    cluster_info = clusters[0]
                    
                    return CloudClusterInfo(
                        detected=True,
                        cluster_type="aks",
                        provider="azure",
                        kubeconfig_path=os.path.expanduser("~/.kube/config"),
                        context_name=f"{cluster_info['resourceGroup']}_{cluster_info['name']}",
                        cluster_name=cluster_info['name'],
                        region=cluster_info['location'],
                        resource_group=cluster_info['resourceGroup'],
                        status="running"
                    )
            
            return CloudClusterInfo(detected=False, cluster_type="aks", provider="azure")
            
        except Exception as e:
            logger.debug(f"AKS detection failed: {e}")
            return CloudClusterInfo(detected=False, cluster_type="aks", provider="azure")
    
    async def _detect_digitalocean(self) -> CloudClusterInfo:
        """
        Detect DigitalOcean Kubernetes clusters
        """
        try:
            # Check if doctl is available
            if not self._check_doctl():
                return CloudClusterInfo(detected=False, cluster_type="doks", provider="digitalocean")
            
            # Get DigitalOcean clusters
            result = subprocess.run(
                ['doctl', 'kubernetes', 'cluster', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse cluster list
                clusters = self._parse_do_clusters(result.stdout)
                if clusters:
                    # Get the first cluster
                    cluster_info = clusters[0]
                    
                    return CloudClusterInfo(
                        detected=True,
                        cluster_type="doks",
                        provider="digitalocean",
                        kubeconfig_path=os.path.expanduser("~/.kube/config"),
                        context_name=f"do-{cluster_info['region']}-{cluster_info['name']}",
                        cluster_name=cluster_info['name'],
                        region=cluster_info['region'],
                        status="running"
                    )
            
            return CloudClusterInfo(detected=False, cluster_type="doks", provider="digitalocean")
            
        except Exception as e:
            logger.debug(f"DigitalOcean detection failed: {e}")
            return CloudClusterInfo(detected=False, cluster_type="doks", provider="digitalocean")
    
    async def _detect_linode(self) -> CloudClusterInfo:
        """
        Detect Linode Kubernetes clusters
        """
        try:
            # Check if linode-cli is available
            if not self._check_linode_cli():
                return CloudClusterInfo(detected=False, cluster_type="lke", provider="linode")
            
            # Get Linode clusters
            result = subprocess.run(
                ['linode-cli', 'lke', 'cluster-list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse cluster list
                clusters = self._parse_linode_clusters(result.stdout)
                if clusters:
                    # Get the first cluster
                    cluster_info = clusters[0]
                    
                    return CloudClusterInfo(
                        detected=True,
                        cluster_type="lke",
                        provider="linode",
                        kubeconfig_path=os.path.expanduser("~/.kube/config"),
                        context_name=f"linode-{cluster_info['region']}-{cluster_info['label']}",
                        cluster_name=cluster_info['label'],
                        region=cluster_info['region'],
                        status="running"
                    )
            
            return CloudClusterInfo(detected=False, cluster_type="lke", provider="linode")
            
        except Exception as e:
            logger.debug(f"Linode detection failed: {e}")
            return CloudClusterInfo(detected=False, cluster_type="lke", provider="linode")
    
    def _check_aws_cli(self) -> bool:
        """Check if AWS CLI is available"""
        try:
            result = subprocess.run(['aws', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_gcloud(self) -> bool:
        """Check if gcloud is available"""
        try:
            result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_azure_cli(self) -> bool:
        """Check if Azure CLI is available"""
        try:
            result = subprocess.run(['az', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_doctl(self) -> bool:
        """Check if doctl is available"""
        try:
            result = subprocess.run(['doctl', 'version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_linode_cli(self) -> bool:
        """Check if linode-cli is available"""
        try:
            result = subprocess.run(['linode-cli', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_kubectl(self) -> bool:
        """Check if kubectl is available"""
        try:
            result = subprocess.run(['kubectl', 'version', '--client'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _parse_aws_clusters(self, output: str) -> list:
        """Parse AWS EKS cluster list"""
        try:
            import json
            data = json.loads(output)
            return data.get('clusters', [])
        except Exception:
            return []
    
    def _parse_gcp_clusters(self, output: str) -> list:
        """Parse GCP GKE cluster list"""
        clusters = []
        lines = output.strip().split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    clusters.append({
                        'name': parts[0],
                        'zone': parts[1],
                        'master_version': parts[2],
                        'project': parts[3] if len(parts) > 3 else 'default'
                    })
        return clusters
    
    def _parse_azure_clusters(self, output: str) -> list:
        """Parse Azure AKS cluster list"""
        try:
            import json
            data = json.loads(output)
            return data
        except Exception:
            return []
    
    def _parse_do_clusters(self, output: str) -> list:
        """Parse DigitalOcean cluster list"""
        clusters = []
        lines = output.strip().split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    clusters.append({
                        'name': parts[0],
                        'region': parts[1],
                        'version': parts[2]
                    })
        return clusters
    
    def _parse_linode_clusters(self, output: str) -> list:
        """Parse Linode cluster list"""
        try:
            import json
            data = json.loads(output)
            return data.get('data', [])
        except Exception:
            return []
    
    async def _get_eks_cluster_info(self, cluster_name: str) -> Optional[dict]:
        """Get EKS cluster information"""
        try:
            result = subprocess.run(
                ['aws', 'eks', 'describe-cluster', '--name', cluster_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                cluster = data.get('cluster', {})
                return {
                    'region': cluster.get('arn', '').split(':')[3],
                    'account': cluster.get('arn', '').split(':')[4]
                }
        except Exception as e:
            logger.debug(f"Failed to get EKS cluster info: {e}")
        
        return None 