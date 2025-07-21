"""
Local Kubernetes Cluster Detector
Detects local Kubernetes clusters (minikube, kind, k3s, etc.)
"""

import os
import subprocess
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class LocalClusterInfo:
    """Information about detected local cluster"""
    detected: bool
    cluster_type: str
    kubeconfig_path: Optional[str] = None
    context_name: Optional[str] = None
    cluster_name: Optional[str] = None
    status: str = "unknown"

class LocalKubernetesDetector:
    """
    Detects local Kubernetes clusters
    """
    
    def __init__(self):
        self.kubeconfig_paths = [
            os.path.expanduser("~/.kube/config"),
            os.path.expanduser("~/.kube/config.local"),
            "/etc/rancher/k3s/k3s.yaml",  # k3s
            os.path.expanduser("~/.minikube/profiles/minikube/kubeconfig"),  # minikube
        ]
    
    async def detect(self) -> LocalClusterInfo:
        """
        Detect local Kubernetes clusters
        """
        try:
            # Check for kubectl availability
            if not self._check_kubectl():
                return LocalClusterInfo(detected=False, cluster_type="none")
            
            # Check for local clusters
            cluster_info = await self._detect_local_clusters()
            if cluster_info.detected:
                return cluster_info
            
            # Check for kubeconfig files
            kubeconfig_info = await self._detect_kubeconfig()
            if kubeconfig_info.detected:
                return kubeconfig_info
            
            return LocalClusterInfo(detected=False, cluster_type="none")
            
        except Exception as e:
            logger.error(f"Local cluster detection failed: {e}")
            return LocalClusterInfo(detected=False, cluster_type="error")
    
    def _check_kubectl(self) -> bool:
        """
        Check if kubectl is available
        """
        try:
            result = subprocess.run(
                ['kubectl', 'version', '--client'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def _detect_local_clusters(self) -> LocalClusterInfo:
        """
        Detect specific local cluster types
        """
        # Check for minikube
        minikube_info = await self._detect_minikube()
        if minikube_info.detected:
            return minikube_info
        
        # Check for kind
        kind_info = await self._detect_kind()
        if kind_info.detected:
            return kind_info
        
        # Check for k3s
        k3s_info = await self._detect_k3s()
        if k3s_info.detected:
            return k3s_info
        
        # Check for Docker Desktop
        docker_info = await self._detect_docker_desktop()
        if docker_info.detected:
            return docker_info
        
        return LocalClusterInfo(detected=False, cluster_type="none")
    
    async def _detect_minikube(self) -> LocalClusterInfo:
        """
        Detect minikube cluster
        """
        try:
            # Check if minikube is installed
            result = subprocess.run(
                ['minikube', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse minikube status
                status_output = result.stdout
                if "Running" in status_output:
                    # Get minikube kubeconfig
                    kubeconfig_path = os.path.expanduser("~/.minikube/profiles/minikube/kubeconfig")
                    
                    return LocalClusterInfo(
                        detected=True,
                        cluster_type="minikube",
                        kubeconfig_path=kubeconfig_path,
                        context_name="minikube",
                        cluster_name="minikube",
                        status="running"
                    )
            
            return LocalClusterInfo(detected=False, cluster_type="minikube")
            
        except Exception as e:
            logger.debug(f"Minikube detection failed: {e}")
            return LocalClusterInfo(detected=False, cluster_type="minikube")
    
    async def _detect_kind(self) -> LocalClusterInfo:
        """
        Detect kind cluster
        """
        try:
            # Check if kind is installed
            result = subprocess.run(
                ['kind', 'get', 'clusters'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Get the first cluster name
                cluster_name = result.stdout.strip().split('\n')[0]
                
                return LocalClusterInfo(
                    detected=True,
                    cluster_type="kind",
                    kubeconfig_path=os.path.expanduser("~/.kube/config"),
                    context_name=f"kind-{cluster_name}",
                    cluster_name=cluster_name,
                    status="running"
                )
            
            return LocalClusterInfo(detected=False, cluster_type="kind")
            
        except Exception as e:
            logger.debug(f"Kind detection failed: {e}")
            return LocalClusterInfo(detected=False, cluster_type="kind")
    
    async def _detect_k3s(self) -> LocalClusterInfo:
        """
        Detect k3s cluster
        """
        try:
            # Check for k3s kubeconfig
            k3s_config = "/etc/rancher/k3s/k3s.yaml"
            if os.path.exists(k3s_config):
                # Test connection
                result = subprocess.run(
                    ['kubectl', '--kubeconfig', k3s_config, 'cluster-info'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return LocalClusterInfo(
                        detected=True,
                        cluster_type="k3s",
                        kubeconfig_path=k3s_config,
                        context_name="default",
                        cluster_name="k3s",
                        status="running"
                    )
            
            return LocalClusterInfo(detected=False, cluster_type="k3s")
            
        except Exception as e:
            logger.debug(f"K3s detection failed: {e}")
            return LocalClusterInfo(detected=False, cluster_type="k3s")
    
    async def _detect_docker_desktop(self) -> LocalClusterInfo:
        """
        Detect Docker Desktop Kubernetes
        """
        try:
            # Check if Docker Desktop Kubernetes is enabled
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Check if it's Docker Desktop
                if "docker-desktop" in result.stdout or "docker-desktop" in result.stderr:
                    return LocalClusterInfo(
                        detected=True,
                        cluster_type="docker-desktop",
                        kubeconfig_path=os.path.expanduser("~/.kube/config"),
                        context_name="docker-desktop",
                        cluster_name="docker-desktop",
                        status="running"
                    )
            
            return LocalClusterInfo(detected=False, cluster_type="docker-desktop")
            
        except Exception as e:
            logger.debug(f"Docker Desktop detection failed: {e}")
            return LocalClusterInfo(detected=False, cluster_type="docker-desktop")
    
    async def _detect_kubeconfig(self) -> LocalClusterInfo:
        """
        Detect any available kubeconfig
        """
        for kubeconfig_path in self.kubeconfig_paths:
            if os.path.exists(kubeconfig_path):
                try:
                    # Test the kubeconfig
                    result = subprocess.run(
                        ['kubectl', '--kubeconfig', kubeconfig_path, 'cluster-info'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        return LocalClusterInfo(
                            detected=True,
                            cluster_type="local",
                            kubeconfig_path=kubeconfig_path,
                            context_name="default",
                            cluster_name="local",
                            status="running"
                        )
                except Exception as e:
                    logger.debug(f"Kubeconfig test failed for {kubeconfig_path}: {e}")
                    continue
        
        return LocalClusterInfo(detected=False, cluster_type="none") 