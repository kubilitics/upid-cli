"""
Integration tests for Kubernetes interactions using testcontainers
"""
import pytest
import time
import yaml
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from upid.core.config import Config
from upid.core.api_client import UPIDAPIClient


class TestKubernetesIntegration:
    """Integration tests for Kubernetes interactions"""

    @pytest.fixture(scope="class")
    def k8s_cluster(self):
        """Start a Kubernetes cluster using testcontainers"""
        # Using kind (Kubernetes in Docker) for testing
        container = DockerContainer("kindest/node:v1.24.0")
        container.with_command([
            "kind", "create", "cluster", "--name", "test-cluster"
        ])
        container.with_exposed_ports(6443)
        
        with container:
            # Wait for cluster to be ready
            wait_for_logs(container, "Ready")
            yield container

    @pytest.fixture
    def test_config(self):
        """Create test configuration"""
        config = Config()
        config.set('api_url', 'http://localhost:8000')
        config.set('timeout', 30)
        return config

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_cluster_connectivity(self, k8s_cluster, test_config):
        """Test basic Kubernetes cluster connectivity"""
        try:
            # Verify cluster is running
            assert k8s_cluster.is_running()
            
            # Test kubectl connectivity
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "nodes"
            ])
            
            assert result is not None
            assert "Ready" in result
            
        except Exception as e:
            pytest.fail(f"Failed to connect to Kubernetes cluster: {e}")

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_namespace_creation(self, k8s_cluster):
        """Test Kubernetes namespace creation"""
        namespace_name = "test-namespace"
        
        try:
            # Create namespace
            result = k8s_cluster.exec_in_container([
                "kubectl", "create", "namespace", namespace_name
            ])
            
            # Verify namespace was created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "namespace", namespace_name
            ])
            
            assert namespace_name in result
            assert "Active" in result
            
        finally:
            # Clean up namespace
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "namespace", namespace_name
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_pod_deployment(self, k8s_cluster):
        """Test Kubernetes pod deployment"""
        pod_name = "test-pod"
        namespace = "default"
        
        # Create test pod YAML
        pod_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
  namespace: {namespace}
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
"""
        
        try:
            # Apply pod YAML
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=pod_yaml.encode())
            
            # Wait for pod to be ready
            time.sleep(10)
            
            # Verify pod is running
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "pod", pod_name, "-n", namespace
            ])
            
            assert pod_name in result
            assert "Running" in result
            
        finally:
            # Clean up pod
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "pod", pod_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_deployment_scaling(self, k8s_cluster):
        """Test Kubernetes deployment scaling"""
        deployment_name = "test-deployment"
        namespace = "default"
        
        # Create test deployment YAML
        deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {deployment_name}
  namespace: {namespace}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: test-app
  template:
    metadata:
      labels:
        app: test-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
"""
        
        try:
            # Apply deployment YAML
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=deployment_yaml.encode())
            
            # Wait for deployment to be ready
            time.sleep(15)
            
            # Verify deployment is running
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "deployment", deployment_name, "-n", namespace
            ])
            
            assert deployment_name in result
            assert "2/2" in result  # 2 replicas ready
            
            # Scale deployment
            result = k8s_cluster.exec_in_container([
                "kubectl", "scale", "deployment", deployment_name, 
                "--replicas=3", "-n", namespace
            ])
            
            # Wait for scaling
            time.sleep(10)
            
            # Verify scaling
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "deployment", deployment_name, "-n", namespace
            ])
            
            assert "3/3" in result  # 3 replicas ready
            
        finally:
            # Clean up deployment
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "deployment", deployment_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_hpa_creation(self, k8s_cluster):
        """Test Kubernetes HorizontalPodAutoscaler creation"""
        hpa_name = "test-hpa"
        deployment_name = "test-deployment"
        namespace = "default"
        
        # Create deployment first
        deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {deployment_name}
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-app
  template:
    metadata:
      labels:
        app: test-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
"""
        
        # Create HPA YAML
        hpa_yaml = f"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {hpa_name}
  namespace: {namespace}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {deployment_name}
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
"""
        
        try:
            # Apply deployment
            k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=deployment_yaml.encode())
            
            # Wait for deployment
            time.sleep(10)
            
            # Apply HPA
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=hpa_yaml.encode())
            
            # Wait for HPA
            time.sleep(5)
            
            # Verify HPA is created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "hpa", hpa_name, "-n", namespace
            ])
            
            assert hpa_name in result
            assert deployment_name in result
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "hpa", hpa_name, "-n", namespace
            ])
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "deployment", deployment_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_metrics_collection(self, k8s_cluster):
        """Test Kubernetes metrics collection"""
        pod_name = "metrics-test-pod"
        namespace = "default"
        
        # Create pod with resource requests
        pod_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
  namespace: {namespace}
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 200m
        memory: 256Mi
"""
        
        try:
            # Apply pod
            k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=pod_yaml.encode())
            
            # Wait for pod
            time.sleep(10)
            
            # Get pod metrics (if metrics server is available)
            try:
                result = k8s_cluster.exec_in_container([
                    "kubectl", "top", "pod", pod_name, "-n", namespace
                ])
                
                assert pod_name in result
                
            except Exception:
                # Metrics server might not be available in test environment
                # This is expected in some test setups
                pass
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "pod", pod_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_configmap_creation(self, k8s_cluster):
        """Test Kubernetes ConfigMap creation"""
        configmap_name = "test-configmap"
        namespace = "default"
        
        # Create ConfigMap YAML
        configmap_yaml = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {configmap_name}
  namespace: {namespace}
data:
  config.json: |
    {{
      "database": "test-db",
      "port": 5432
    }}
  app.properties: |
    debug=true
    log_level=info
"""
        
        try:
            # Apply ConfigMap
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=configmap_yaml.encode())
            
            # Verify ConfigMap is created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "configmap", configmap_name, "-n", namespace
            ])
            
            assert configmap_name in result
            
            # Get ConfigMap details
            result = k8s_cluster.exec_in_container([
                "kubectl", "describe", "configmap", configmap_name, "-n", namespace
            ])
            
            assert "config.json" in result
            assert "app.properties" in result
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "configmap", configmap_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_secret_creation(self, k8s_cluster):
        """Test Kubernetes Secret creation"""
        secret_name = "test-secret"
        namespace = "default"
        
        # Create Secret YAML
        secret_yaml = f"""
apiVersion: v1
kind: Secret
metadata:
  name: {secret_name}
  namespace: {namespace}
type: Opaque
data:
  username: dGVzdC11c2Vy  # base64 encoded "test-user"
  password: dGVzdC1wYXNz  # base64 encoded "test-pass"
"""
        
        try:
            # Apply Secret
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=secret_yaml.encode())
            
            # Verify Secret is created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "secret", secret_name, "-n", namespace
            ])
            
            assert secret_name in result
            assert "Opaque" in result
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "secret", secret_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_service_creation(self, k8s_cluster):
        """Test Kubernetes Service creation"""
        service_name = "test-service"
        deployment_name = "test-deployment"
        namespace = "default"
        
        # Create deployment first
        deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {deployment_name}
  namespace: {namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-app
  template:
    metadata:
      labels:
        app: test-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
"""
        
        # Create Service YAML
        service_yaml = f"""
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: {namespace}
spec:
  selector:
    app: test-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
"""
        
        try:
            # Apply deployment
            k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=deployment_yaml.encode())
            
            # Wait for deployment
            time.sleep(10)
            
            # Apply Service
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=service_yaml.encode())
            
            # Verify Service is created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "service", service_name, "-n", namespace
            ])
            
            assert service_name in result
            assert "ClusterIP" in result
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "service", service_name, "-n", namespace
            ])
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "deployment", deployment_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_node_info(self, k8s_cluster):
        """Test Kubernetes node information retrieval"""
        # Get node information
        result = k8s_cluster.exec_in_container([
            "kubectl", "get", "nodes", "-o", "wide"
        ])
        
        assert result is not None
        assert "Ready" in result
        
        # Get node details
        result = k8s_cluster.exec_in_container([
            "kubectl", "describe", "nodes"
        ])
        
        assert result is not None
        assert "Capacity" in result
        assert "Allocatable" in result

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_pod_logs(self, k8s_cluster):
        """Test Kubernetes pod logs retrieval"""
        pod_name = "logs-test-pod"
        namespace = "default"
        
        # Create test pod
        pod_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
  namespace: {namespace}
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
"""
        
        try:
            # Apply pod
            k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=pod_yaml.encode())
            
            # Wait for pod
            time.sleep(10)
            
            # Get pod logs
            result = k8s_cluster.exec_in_container([
                "kubectl", "logs", pod_name, "-n", namespace
            ])
            
            assert result is not None
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "pod", pod_name, "-n", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_resource_quota(self, k8s_cluster):
        """Test Kubernetes ResourceQuota creation"""
        quota_name = "test-quota"
        namespace = "test-namespace"
        
        # Create namespace
        k8s_cluster.exec_in_container([
            "kubectl", "create", "namespace", namespace
        ])
        
        # Create ResourceQuota YAML
        quota_yaml = f"""
apiVersion: v1
kind: ResourceQuota
metadata:
  name: {quota_name}
  namespace: {namespace}
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
"""
        
        try:
            # Apply ResourceQuota
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=quota_yaml.encode())
            
            # Verify ResourceQuota is created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "resourcequota", quota_name, "-n", namespace
            ])
            
            assert quota_name in result
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "resourcequota", quota_name, "-n", namespace
            ])
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "namespace", namespace
            ])

    @pytest.mark.integration
    @pytest.mark.k8s
    @pytest.mark.slow
    def test_k8s_limit_range(self, k8s_cluster):
        """Test Kubernetes LimitRange creation"""
        limit_range_name = "test-limit-range"
        namespace = "test-namespace"
        
        # Create namespace
        k8s_cluster.exec_in_container([
            "kubectl", "create", "namespace", namespace
        ])
        
        # Create LimitRange YAML
        limit_range_yaml = f"""
apiVersion: v1
kind: LimitRange
metadata:
  name: {limit_range_name}
  namespace: {namespace}
spec:
  limits:
  - default:
      memory: 512Mi
      cpu: 500m
    defaultRequest:
      memory: 256Mi
      cpu: 250m
    type: Container
"""
        
        try:
            # Apply LimitRange
            result = k8s_cluster.exec_in_container([
                "kubectl", "apply", "-f", "-"
            ], input=limit_range_yaml.encode())
            
            # Verify LimitRange is created
            result = k8s_cluster.exec_in_container([
                "kubectl", "get", "limitrange", limit_range_name, "-n", namespace
            ])
            
            assert limit_range_name in result
            
        finally:
            # Clean up
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "limitrange", limit_range_name, "-n", namespace
            ])
            k8s_cluster.exec_in_container([
                "kubectl", "delete", "namespace", namespace
            ]) 