"""
Real Kubernetes cluster setup for testing
Provides actual clusters with real applications and monitoring
"""
import subprocess
import time
import yaml
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClusterConfig:
    """Configuration for a test cluster"""
    name: str
    provider: str  # 'kind', 'minikube', 'k3s'
    version: str
    nodes: int = 1
    memory: str = "4GB"
    cpu: str = "2"
    disk_size: str = "20GB"
    extra_config: Dict = None

@dataclass
class ApplicationConfig:
    """Configuration for test applications"""
    name: str
    namespace: str
    replicas: int = 1
    image: str = "nginx:alpine"
    ports: List[int] = None
    resources: Dict = None
    environment: Dict = None

class RealClusterManager:
    """Manages real Kubernetes clusters for testing"""
    
    def __init__(self, base_dir: str = "/tmp/upid-test-clusters"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.clusters = {}
        self.applications = {}
        
    def create_kind_cluster(self, config: ClusterConfig) -> bool:
        """Create a kind cluster for testing"""
        try:
            logger.info(f"Creating kind cluster: {config.name}")
            
            # Create kind config
            kind_config = {
                "kind": "Cluster",
                "apiVersion": "kind.x-k8s.io/v1alpha4",
                "nodes": [
                    {
                        "role": "control-plane",
                        "kubeadmConfigPatches": [
                            "kind: InitConfiguration\nnodeRegistration:\n  kubeletExtraArgs:\n    node-labels: \"ingress-ready=true\"\n"
                        ],
                        "extraPortMappings": [
                            {"containerPort": 80, "hostPort": 80, "protocol": "TCP"},
                            {"containerPort": 443, "hostPort": 443, "protocol": "TCP"}
                        ]
                    }
                ]
            }
            
            # Add worker nodes if specified
            for i in range(config.nodes - 1):
                kind_config["nodes"].append({"role": "worker"})
            
            # Write config to file
            config_file = self.base_dir / f"{config.name}-kind-config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(kind_config, f)
            
            # Create cluster
            cmd = [
                "kind", "create", "cluster",
                "--name", config.name,
                "--config", str(config_file),
                "--image", f"kindest/node:{config.version}"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Kind cluster {config.name} created successfully")
            
            # Store cluster info
            self.clusters[config.name] = {
                "provider": "kind",
                "config": config,
                "kubeconfig": self._get_kind_kubeconfig(config.name),
                "status": "running"
            }
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create kind cluster {config.name}: {e}")
            return False
    
    def create_minikube_cluster(self, config: ClusterConfig) -> bool:
        """Create a minikube cluster for testing"""
        try:
            logger.info(f"Creating minikube cluster: {config.name}")
            
            cmd = [
                "minikube", "start",
                "--profile", config.name,
                "--kubernetes-version", config.version,
                "--memory", config.memory,
                "--cpus", config.cpu,
                "--disk-size", config.disk_size,
                "--driver", "docker"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Minikube cluster {config.name} created successfully")
            
            # Store cluster info
            self.clusters[config.name] = {
                "provider": "minikube",
                "config": config,
                "kubeconfig": self._get_minikube_kubeconfig(config.name),
                "status": "running"
            }
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create minikube cluster {config.name}: {e}")
            return False
    
    def deploy_test_applications(self, cluster_name: str, apps: List[ApplicationConfig]) -> bool:
        """Deploy test applications to a cluster"""
        try:
            logger.info(f"Deploying {len(apps)} applications to cluster {cluster_name}")
            
            if cluster_name not in self.clusters:
                raise ValueError(f"Cluster {cluster_name} not found")
            
            cluster = self.clusters[cluster_name]
            kubeconfig = cluster["kubeconfig"]
            
            for app in apps:
                # Create namespace
                self._run_kubectl(cluster_name, ["create", "namespace", app.namespace], ignore_errors=True)
                
                # Create deployment
                deployment = self._create_deployment_yaml(app)
                self._apply_yaml(cluster_name, deployment)
                
                # Create service if ports specified
                if app.ports:
                    service = self._create_service_yaml(app)
                    self._apply_yaml(cluster_name, service)
                
                # Store application info
                if cluster_name not in self.applications:
                    self.applications[cluster_name] = []
                self.applications[cluster_name].append({
                    "name": app.name,
                    "namespace": app.namespace,
                    "config": app
                })
            
            logger.info(f"Successfully deployed {len(apps)} applications to {cluster_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy applications to {cluster_name}: {e}")
            return False
    
    def setup_monitoring(self, cluster_name: str) -> bool:
        """Setup monitoring stack (Prometheus, Grafana)"""
        try:
            logger.info(f"Setting up monitoring for cluster {cluster_name}")
            
            # Create monitoring namespace
            self._run_kubectl(cluster_name, ["create", "namespace", "monitoring"], ignore_errors=True)
            
            # Deploy Prometheus
            prometheus_yaml = self._get_prometheus_yaml()
            self._apply_yaml(cluster_name, prometheus_yaml)
            
            # Deploy Grafana
            grafana_yaml = self._get_grafana_yaml()
            self._apply_yaml(cluster_name, grafana_yaml)
            
            # Wait for monitoring to be ready
            time.sleep(30)
            
            logger.info(f"Monitoring setup completed for {cluster_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup monitoring for {cluster_name}: {e}")
            return False
    
    def generate_test_data(self, cluster_name: str, duration_hours: int = 24) -> bool:
        """Generate realistic test data for analysis"""
        try:
            logger.info(f"Generating test data for cluster {cluster_name}")
            
            # Deploy load generator
            load_gen_yaml = self._get_load_generator_yaml(duration_hours)
            self._apply_yaml(cluster_name, load_gen_yaml)
            
            # Deploy batch jobs
            batch_jobs_yaml = self._get_batch_jobs_yaml()
            self._apply_yaml(cluster_name, batch_jobs_yaml)
            
            # Deploy idle applications
            idle_apps_yaml = self._get_idle_applications_yaml()
            self._apply_yaml(cluster_name, idle_apps_yaml)
            
            logger.info(f"Test data generation completed for {cluster_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate test data for {cluster_name}: {e}")
            return False
    
    def cleanup_cluster(self, cluster_name: str) -> bool:
        """Clean up a test cluster"""
        try:
            logger.info(f"Cleaning up cluster {cluster_name}")
            
            if cluster_name not in self.clusters:
                logger.warning(f"Cluster {cluster_name} not found")
                return True
            
            cluster = self.clusters[cluster_name]
            
            if cluster["provider"] == "kind":
                cmd = ["kind", "delete", "cluster", "--name", cluster_name]
            elif cluster["provider"] == "minikube":
                cmd = ["minikube", "delete", "--profile", cluster_name]
            else:
                raise ValueError(f"Unknown provider: {cluster['provider']}")
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Remove from tracking
            del self.clusters[cluster_name]
            if cluster_name in self.applications:
                del self.applications[cluster_name]
            
            logger.info(f"Cluster {cluster_name} cleaned up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup cluster {cluster_name}: {e}")
            return False
    
    def get_cluster_info(self, cluster_name: str) -> Dict:
        """Get information about a cluster"""
        if cluster_name not in self.clusters:
            return None
        
        cluster = self.clusters[cluster_name]
        
        # Get node info
        nodes = self._run_kubectl(cluster_name, ["get", "nodes", "-o", "json"])
        node_data = json.loads(nodes) if nodes else {"items": []}
        
        # Get pod info
        pods = self._run_kubectl(cluster_name, ["get", "pods", "--all-namespaces", "-o", "json"])
        pod_data = json.loads(pods) if pods else {"items": []}
        
        return {
            "name": cluster_name,
            "provider": cluster["provider"],
            "status": cluster["status"],
            "nodes": len(node_data["items"]),
            "pods": len(pod_data["items"]),
            "applications": self.applications.get(cluster_name, [])
        }
    
    def _get_kind_kubeconfig(self, cluster_name: str) -> str:
        """Get kubeconfig for kind cluster"""
        cmd = ["kind", "get", "kubeconfig", "--name", cluster_name]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    
    def _get_minikube_kubeconfig(self, cluster_name: str) -> str:
        """Get kubeconfig for minikube cluster"""
        cmd = ["minikube", "kubectl", "--profile", cluster_name, "config", "view", "--raw"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    
    def _run_kubectl(self, cluster_name: str, args: List[str], ignore_errors: bool = False) -> Optional[str]:
        """Run kubectl command on a cluster"""
        cluster = self.clusters[cluster_name]
        
        if cluster["provider"] == "kind":
            cmd = ["kind", "export", "kubeconfig", "--name", cluster_name]
            subprocess.run(cmd, check=True, capture_output=True)
            kubectl_cmd = ["kubectl"] + args
        elif cluster["provider"] == "minikube":
            kubectl_cmd = ["minikube", "kubectl", "--profile", cluster_name] + args
        else:
            raise ValueError(f"Unknown provider: {cluster['provider']}")
        
        try:
            result = subprocess.run(kubectl_cmd, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            if not ignore_errors:
                raise
            return None
    
    def _apply_yaml(self, cluster_name: str, yaml_content: str) -> bool:
        """Apply YAML to cluster"""
        try:
            # Write YAML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_content)
                temp_file = f.name
            
            # Apply YAML
            self._run_kubectl(cluster_name, ["apply", "-f", temp_file])
            
            # Clean up temp file
            os.unlink(temp_file)
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply YAML to {cluster_name}: {e}")
            return False
    
    def _create_deployment_yaml(self, app: ApplicationConfig) -> str:
        """Create deployment YAML for an application"""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": app.name,
                "namespace": app.namespace
            },
            "spec": {
                "replicas": app.replicas,
                "selector": {
                    "matchLabels": {
                        "app": app.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": app.name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": app.name,
                                "image": app.image,
                                "ports": [{"containerPort": port} for port in (app.ports or [80])]
                            }
                        ]
                    }
                }
            }
        }
        
        # Add resources if specified
        if app.resources:
            deployment["spec"]["template"]["spec"]["containers"][0]["resources"] = app.resources
        
        # Add environment variables if specified
        if app.environment:
            deployment["spec"]["template"]["spec"]["containers"][0]["env"] = [
                {"name": k, "value": v} for k, v in app.environment.items()
            ]
        
        return yaml.dump(deployment)
    
    def _create_service_yaml(self, app: ApplicationConfig) -> str:
        """Create service YAML for an application"""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{app.name}-service",
                "namespace": app.namespace
            },
            "spec": {
                "selector": {
                    "app": app.name
                },
                "ports": [
                    {
                        "port": port,
                        "targetPort": port,
                        "protocol": "TCP"
                    } for port in (app.ports or [80])
                ],
                "type": "ClusterIP"
            }
        }
        
        return yaml.dump(service)
    
    def _get_prometheus_yaml(self) -> str:
        """Get Prometheus deployment YAML"""
        return """
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
  namespace: monitoring
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: ClusterIP
"""
    
    def _get_grafana_yaml(self) -> str:
        """Get Grafana deployment YAML"""
        return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
---
apiVersion: v1
kind: Service
metadata:
  name: grafana-service
  namespace: monitoring
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
"""
    
    def _get_load_generator_yaml(self, duration_hours: int) -> str:
        """Get load generator YAML"""
        return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: load-generator
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: load-generator
  template:
    metadata:
      labels:
        app: load-generator
    spec:
      containers:
      - name: load-generator
        image: busybox:latest
        command:
        - /bin/sh
        - -c
        - |
          while true; do
            wget -q -O- http://nginx-service.default.svc.cluster.local || true
            sleep 5
          done
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
"""
    
    def _get_batch_jobs_yaml(self) -> str:
        """Get batch jobs YAML"""
        return """
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-job-1
  namespace: default
spec:
  template:
    spec:
      containers:
      - name: batch-job
        image: busybox:latest
        command:
        - /bin/sh
        - -c
        - |
          echo "Processing batch job..."
          sleep 30
          echo "Batch job completed"
      restartPolicy: Never
  backoffLimit: 3
---
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-job-2
  namespace: default
spec:
  template:
    spec:
      containers:
      - name: batch-job
        image: busybox:latest
        command:
        - /bin/sh
        - -c
        - |
          echo "Processing another batch job..."
          sleep 45
          echo "Second batch job completed"
      restartPolicy: Never
  backoffLimit: 3
"""
    
    def _get_idle_applications_yaml(self) -> str:
        """Get idle applications YAML"""
        return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: idle-app-1
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: idle-app-1
  template:
    metadata:
      labels:
        app: idle-app-1
    spec:
      containers:
      - name: idle-app
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: idle-app-2
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: idle-app-2
  template:
    metadata:
      labels:
        app: idle-app-2
    spec:
      containers:
      - name: idle-app
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
""" 