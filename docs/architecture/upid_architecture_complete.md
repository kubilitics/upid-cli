        # UPID Complete Architecture & Implementation Guide

## 🏗️ **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                UPID PLATFORM                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           CLI Interface Layer                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Local Mode    │  │  Authenticated  │  │   SaaS Mode     │                │
│  │ (no auth req'd) │  │   CLI Mode      │  │ (web dashboard) │                │
│  │ Docker Desktop  │  │  EKS/GKE/AKS   │  │ Multi-tenant    │                │
│  │ minikube, k3s   │  │    kubectl      │  │    Portal       │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Authentication & Authorization Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Auto-Detect    │  │   K8s RBAC      │  │   UPID RBAC     │                │
│  │  - Local K8s    │  │  - ServiceAcct  │  │  - Multi-tenant │                │
│  │  - Cloud Config │  │  - Namespace    │  │  - Org/Team     │                │
│  │  - No Auth      │  │  - ClusterRole  │  │  - Custom Perms │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           Core Intelligence Engine                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Metrics        │  │   Analysis      │  │  Optimization   │                │
│  │  Collection     │  │   Engine        │  │   Engine        │                │
│  │                 │  │                 │  │                 │                │
│  │ • Pod Metrics   │  │ • Idle Detection│  │ • Resource Opt  │                │
│  │ • Node Metrics  │  │ • Cost Analysis │  │ • Zero Scaling  │                │
│  │ • Business Logs │  │ • Pattern ML    │  │ • Safety Checks │                │
│  │ • Request Data  │  │ • Confidence    │  │ • Rollback      │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Data Storage & Processing Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Time-Series    │  │   Metadata      │  │   Cache Layer   │                │
│  │   Database      │  │   Database      │  │                 │                │
│  │                 │  │                 │  │                 │                │
│  │ • TimescaleDB   │  │ • PostgreSQL    │  │ • Redis         │                │
│  │ • 90-day data   │  │ • User/Tenant   │  │ • Query Cache   │                │
│  │ • Compression   │  │ • RBAC Rules    │  │ • Session Store │                │
│  │ • Partitioning  │  │ • Audit Logs    │  │ • Rate Limiting │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                      Cloud Provider Integration Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │      AWS        │  │      GCP        │  │     Azure       │                │
│  │                 │  │                 │  │                 │                │
│  │ • Cost Explorer │  │ • Billing API   │  │ • Cost Mgmt API │                │
│  │ • EKS Detection │  │ • GKE Detection │  │ • AKS Detection │                │
│  │ • EC2 Pricing   │  │ • GCE Pricing   │  │ • VM Pricing    │                │
│  │ • IAM Roles     │  │ • IAM Binding   │  │ • RBAC          │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Kubernetes Integration Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Cluster Auto   │  │   Metrics API   │  │   Resource API  │                │
│  │   Detection     │  │                 │  │                 │                │
│  │                 │  │                 │  │                 │                │
│  │ • EKS/GKE/AKS   │  │ • metrics.k8s   │  │ • Core API      │                │
│  │ • Local K8s     │  │ • Prometheus    │  │ • Apps API      │                │
│  │ • Cloud Labels  │  │ • cAdvisor      │  │ • Custom Rsrc   │                │
│  │ • Node Metadata │  │ • Kubelet       │  │ • Events API    │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Flow Diagram                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  User Command: upid analyze pod nginx-123                                      │
│       │                                                                        │
│       ▼                                                                        │
│  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│  │   Auth Check    │────────▶│  Cluster Detect │────────▶│ Permission Check│  │
│  │                 │         │                 │         │                 │  │
│  │ • Local detect  │         │ • Cloud provider│         │ • Namespace     │  │
│  │ • Cloud config  │         │ • K8s version   │         │ • Resource      │  │
│  │ • UPID token    │         │ • Node labels   │         │ • Action        │  │
│  └─────────────────┘         └─────────────────┘         └─────────────────┘  │
│       │                             │                             │            │
│       ▼                             ▼                             ▼            │
│  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│  │  Metrics Fetch  │────────▶│   Cost Fetch    │────────▶│   Intelligence  │  │
│  │                 │         │                 │         │    Analysis     │  │
│  │ • Pod metrics   │         │ • Cloud billing │         │                 │  │
│  │ • Node metrics  │         │ • Instance costs│         │ • Idle detect   │  │
│  │ • Request logs  │         │ • Pricing APIs  │         │ • Cost calc     │  │
│  │ • Business data │         │ • Usage data    │         │ • Optimization  │  │
│  └─────────────────┘         └─────────────────┘         └─────────────────┘  │
│       │                             │                             │            │
│       ▼                             ▼                             ▼            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                        Response Generation                               │  │
│  │                                                                         │  │
│  │  • Confidence scoring                                                   │  │
│  │  • Actionable recommendations                                           │  │
│  │  • Cost savings calculations                                            │  │
│  │  • Risk assessment                                                      │  │
│  │  • Next steps suggestions                                               │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                          │
│                                     ▼                                          │
│                           CLI/Dashboard Output                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **Major Features Architecture**

### **1. Universal Authentication & Multi-Tenancy**

```python
# auth/universal_auth.py
class UniversalAuthenticator:
    """
    Handles all authentication scenarios automatically
    """
    
    def __init__(self):
        self.local_detector = LocalKubernetesDetector()
        self.cloud_detector = CloudKubernetesDetector()
        self.rbac_enforcer = RBACEnforcer()
        
    async def authenticate_user(self, context: CommandContext) -> AuthResult:
        """
        Universal authentication flow
        """
        # Step 1: Detect environment
        env_info = await self.detect_environment()
        
        # Step 2: Choose authentication strategy
        if env_info.is_local_cluster:
            return await self.authenticate_local(env_info)
        elif env_info.has_cloud_config:
            return await self.authenticate_cloud(env_info)
        else:
            return await self.authenticate_upid_saas(context)
    
    async def detect_environment(self) -> EnvironmentInfo:
        """
        Auto-detect Kubernetes environment
        """
        # Check for local clusters first
        local_info = await self.local_detector.detect()
        if local_info.detected:
            return EnvironmentInfo(
                is_local_cluster=True,
                cluster_type=local_info.cluster_type,  # docker-desktop, minikube, k3s, kind
                kubeconfig_path=local_info.kubeconfig_path,
                auth_required=False
            )
        
        # Check for cloud clusters
        cloud_info = await self.cloud_detector.detect()
        if cloud_info.detected:
            return EnvironmentInfo(
                is_local_cluster=False,
                cluster_type=cloud_info.cluster_type,  # eks, gke, aks
                cloud_provider=cloud_info.provider,
                kubeconfig_path=cloud_info.kubeconfig_path,
                auth_required=cloud_info.auth_required
            )
        
        # No cluster detected - prompt for UPID SaaS
        return EnvironmentInfo(
            is_local_cluster=False,
            cluster_type="unknown",
            auth_required=True,
            requires_setup=True
        )

class LocalKubernetesDetector:
    """
    Detect local Kubernetes environments
    """
    
    async def detect(self) -> LocalDetectionResult:
        """
        Detect local Kubernetes clusters
        """
        detectors = [
            self.detect_docker_desktop,
            self.detect_minikube,
            self.detect_k3s,
            self.detect_kind,
            self.detect_microk8s
        ]
        
        for detector in detectors:
            result = await detector()
            if result.detected:
                return result
        
        return LocalDetectionResult(detected=False)
    
    async def detect_docker_desktop(self) -> LocalDetectionResult:
        """
        Detect Docker Desktop Kubernetes
        """
        try:
            # Check kubeconfig for docker-desktop context
            config = await self.load_kubeconfig()
            
            for context in config.contexts:
                if 'docker-desktop' in context.name.lower():
                    # Test connection
                    if await self.test_connection(context):
                        return LocalDetectionResult(
                            detected=True,
                            cluster_type="docker-desktop",
                            context_name=context.name,
                            kubeconfig_path=config.path,
                            requires_auth=False,
                            local_access=True
                        )
        except Exception as e:
            logger.debug(f"Docker Desktop detection failed: {e}")
        
        return LocalDetectionResult(detected=False)
    
    async def detect_minikube(self) -> LocalDetectionResult:
        """
        Detect Minikube cluster
        """
        try:
            # Check if minikube command exists
            result = subprocess.run(['minikube', 'status'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and 'Running' in result.stdout:
                # Get minikube kubeconfig
                kubeconfig_path = subprocess.run(
                    ['minikube', 'config', 'view', 'kubeconfig'],
                    capture_output=True, text=True
                ).stdout.strip()
                
                return LocalDetectionResult(
                    detected=True,
                    cluster_type="minikube",
                    context_name="minikube",
                    kubeconfig_path=kubeconfig_path,
                    requires_auth=False,
                    local_access=True
                )
        except Exception as e:
            logger.debug(f"Minikube detection failed: {e}")
        
        return LocalDetectionResult(detected=False)
    
    async def detect_k3s(self) -> LocalDetectionResult:
        """
        Detect K3s cluster
        """
        try:
            # Check for K3s kubeconfig
            k3s_config_paths = [
                '/etc/rancher/k3s/k3s.yaml',
                os.path.expanduser('~/.kube/k3s-config'),
                os.path.expanduser('~/.k3s/config')
            ]
            
            for config_path in k3s_config_paths:
                if os.path.exists(config_path):
                    if await self.test_k3s_connection(config_path):
                        return LocalDetectionResult(
                            detected=True,
                            cluster_type="k3s",
                            context_name="default",
                            kubeconfig_path=config_path,
                            requires_auth=False,
                            local_access=True
                        )
        except Exception as e:
            logger.debug(f"K3s detection failed: {e}")
        
        return LocalDetectionResult(detected=False)

class CloudKubernetesDetector:
    """
    Detect cloud-managed Kubernetes clusters
    """
    
    async def detect(self) -> CloudDetectionResult:
        """
        Detect cloud Kubernetes clusters
        """
        detectors = [
            self.detect_eks,
            self.detect_gke,
            self.detect_aks,
            self.detect_openshift
        ]
        
        for detector in detectors:
            result = await detector()
            if result.detected:
                return result
        
        return CloudDetectionResult(detected=False)
    
    async def detect_eks(self) -> CloudDetectionResult:
        """
        Detect Amazon EKS cluster
        """
        try:
            # Check current kubeconfig context
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            if current_context and 'eks' in current_context.lower():
                # Parse EKS cluster info from context
                cluster_info = await self.parse_eks_context(current_context)
                
                # Test connection
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="eks",
                        cloud_provider="aws",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.region,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via AWS CLI
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"EKS detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
    
    async def detect_gke(self) -> CloudDetectionResult:
        """
        Detect Google GKE cluster
        """
        try:
            # Check for GKE context pattern
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            # GKE contexts usually follow pattern: gke_project_zone_cluster
            if current_context and current_context.startswith('gke_'):
                cluster_info = await self.parse_gke_context(current_context)
                
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="gke",
                        cloud_provider="gcp",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.zone,
                        project_id=cluster_info.project_id,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via gcloud
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"GKE detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
    
    async def detect_aks(self) -> CloudDetectionResult:
        """
        Detect Azure AKS cluster
        """
        try:
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            # Check if context uses Azure authentication
            context_config = await self.get_context_config(current_context)
            
            if self.is_azure_context(context_config):
                cluster_info = await self.parse_aks_context(current_context)
                
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="aks",
                        cloud_provider="azure",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.region,
                        resource_group=cluster_info.resource_group,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via az CLI
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"AKS detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
```

### **2. RBAC & Permission System**

```python
# auth/rbac_system.py
class RBACEnforcer:
    """
    Comprehensive RBAC enforcement for UPID
    """
    
    def __init__(self):
        self.k8s_rbac = KubernetesRBACAnalyzer()
        self.upid_rbac = UPIDRBACManager()
        
    async def check_permissions(self, user: AuthenticatedUser, 
                              action: Action, 
                              resource: Resource) -> PermissionResult:
        """
        Check if user has permission to perform action on resource
        """
        # For local clusters - allow all operations
        if user.auth_type == "local":
            return PermissionResult(
                allowed=True,
                reason="Local cluster access - full permissions"
            )
        
        # For cloud clusters - check Kubernetes RBAC
        if user.auth_type == "kubernetes":
            k8s_result = await self.k8s_rbac.check_permission(
                user.k8s_user, action, resource
            )
            
            if not k8s_result.allowed:
                return PermissionResult(
                    allowed=False,
                    reason=f"Kubernetes RBAC denied: {k8s_result.reason}",
                    required_permissions=k8s_result.required_permissions
                )
        
        # For UPID SaaS - check UPID RBAC
        if user.auth_type == "upid":
            upid_result = await self.upid_rbac.check_permission(
                user.upid_user, action, resource
            )
            
            if not upid_result.allowed:
                return PermissionResult(
                    allowed=False,
                    reason=f"UPID RBAC denied: {upid_result.reason}",
                    required_permissions=upid_result.required_permissions
                )
        
        return PermissionResult(allowed=True)

class KubernetesRBACAnalyzer:
    """
    Analyze and enforce Kubernetes RBAC permissions
    """
    
    async def check_permission(self, k8s_user: KubernetesUser, 
                             action: Action, 
                             resource: Resource) -> RBACResult:
        """
        Check Kubernetes RBAC permissions
        """
        # Get user's effective permissions
        permissions = await self.get_user_permissions(k8s_user)
        
        # Check namespace-level permissions
        if resource.namespace:
            namespace_perms = permissions.namespace_permissions.get(resource.namespace, [])
            if self.action_allowed(action, resource, namespace_perms):
                return RBACResult(
                    allowed=True,
                    source="namespace_rbac",
                    permissions_used=namespace_perms
                )
        
        # Check cluster-level permissions
        cluster_perms = permissions.cluster_permissions
        if self.action_allowed(action, resource, cluster_perms):
            return RBACResult(
                allowed=True,
                source="cluster_rbac", 
                permissions_used=cluster_perms
            )
        
        # Permission denied
        required_perms = self.get_required_permissions(action, resource)
        return RBACResult(
            allowed=False,
            reason=f"Missing permissions for {action.name} on {resource.type}",
            required_permissions=required_perms,
            available_namespaces=list(permissions.namespace_permissions.keys())
        )
    
    async def get_user_permissions(self, k8s_user: KubernetesUser) -> UserPermissions:
        """
        Get effective permissions for Kubernetes user
        """
        # Use Kubernetes SubjectAccessReview API to check permissions
        permissions = UserPermissions()
        
        # Check cluster-level permissions
        cluster_resources = ['nodes', 'persistentvolumes', 'clusterroles']
        for resource in cluster_resources:
            for verb in ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']:
                if await self.can_user_perform(k8s_user, verb, resource):
                    permissions.cluster_permissions.append(
                        Permission(verb=verb, resource=resource)
                    )
        
        # Check namespace-level permissions for each accessible namespace
        namespaces = await self.get_accessible_namespaces(k8s_user)
        
        for namespace in namespaces:
            ns_permissions = []
            namespace_resources = ['pods', 'deployments', 'services', 'configmaps']
            
            for resource in namespace_resources:
                for verb in ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']:
                    if await self.can_user_perform(k8s_user, verb, resource, namespace):
                        ns_permissions.append(
                            Permission(verb=verb, resource=resource, namespace=namespace)
                        )
            
            if ns_permissions:
                permissions.namespace_permissions[namespace] = ns_permissions
        
        return permissions
    
    async def get_accessible_namespaces(self, k8s_user: KubernetesUser) -> List[str]:
        """
        Get list of namespaces user has access to
        """
        accessible_namespaces = []
        
        # Get all namespaces
        all_namespaces = await self.k8s_client.list_namespaces()
        
        # Check access to each namespace
        for namespace in all_namespaces:
            if await self.can_user_perform(k8s_user, 'get', 'pods', namespace.name):
                accessible_namespaces.append(namespace.name)
        
        return accessible_namespaces
    
    async def can_user_perform(self, k8s_user: KubernetesUser, 
                             verb: str, resource: str, 
                             namespace: str = None) -> bool:
        """
        Check if user can perform specific action using SubjectAccessReview
        """
        try:
            # Create SubjectAccessReview
            review = client.V1SubjectAccessReview(
                spec=client.V1SubjectAccessReviewSpec(
                    user=k8s_user.username,
                    groups=k8s_user.groups,
                    resource_attributes=client.V1ResourceAttributes(
                        verb=verb,
                        resource=resource,
                        namespace=namespace
                    )
                )
            )
            
            # Submit review
            result = await self.k8s_client.create_subject_access_review(review)
            
            return result.status.allowed
            
        except Exception as e:
            logger.debug(f"Permission check failed: {e}")
            return False
    
    def get_required_permissions(self, action: Action, resource: Resource) -> List[Permission]:
        """
        Get required permissions for UPID actions
        """
        permission_map = {
            "analyze_pod": [
                Permission(verb="get", resource="pods"),
                Permission(verb="get", resource="nodes"),  # for cost calculation
                Permission(verb="list", resource="events")  # for analysis
            ],
            "analyze_deployment": [
                Permission(verb="get", resource="deployments"),
                Permission(verb="list", resource="pods"),
                Permission(verb="get", resource="replicasets")
            ],
            "optimize_pod": [
                Permission(verb="get", resource="pods"),
                Permission(verb="patch", resource="pods"),  # for resource updates
                Permission(verb="patch", resource="deployments")  # for scaling
            ],
            "zero_scale": [
                Permission(verb="get", resource="deployments"),
                Permission(verb="patch", resource="deployments"),  # for scaling to 0
                Permission(verb="create", resource="configmaps")  # for rollback data
            ]
        }
        
        return permission_map.get(action.name, [])

# UPID Custom RBAC for SaaS mode
class UPIDRBACManager:
    """
    UPID-specific RBAC for multi-tenant SaaS
    """
    
    def __init__(self):
        self.db = DatabaseManager()
    
    async def check_permission(self, upid_user: UPIDUser, 
                             action: Action, 
                             resource: Resource) -> RBACResult:
        """
        Check UPID-specific permissions
        """
        # Get user roles and permissions
        user_roles = await self.db.get_user_roles(upid_user.user_id)
        
        # Check organization-level permissions
        if resource.organization_id != upid_user.organization_id:
            return RBACResult(
                allowed=False,
                reason="Resource belongs to different organization"
            )
        
        # Check team-level permissions
        if resource.team_id and resource.team_id not in upid_user.team_ids:
            return RBACResult(
                allowed=False,
                reason="User not member of resource team"
            )
        
        # Check action permissions
        required_permission = self.get_required_upid_permission(action)
        
        for role in user_roles:
            if required_permission in role.permissions:
                return RBACResult(
                    allowed=True,
                    source="upid_rbac",
                    role_used=role.name
                )
        
        return RBACResult(
            allowed=False,
            reason=f"Missing permission: {required_permission}",
            required_permissions=[required_permission]
        )
    
    def get_required_upid_permission(self, action: Action) -> str:
        """
        Map UPID actions to permission strings
        """
        permission_map = {
            "analyze_pod": "upid:analyze:read",
            "analyze_deployment": "upid:analyze:read", 
            "analyze_cluster": "upid:analyze:read",
            "optimize_pod": "upid:optimize:execute",
            "zero_scale": "upid:optimize:execute",
            "view_costs": "upid:costs:read",
            "manage_users": "upid:admin:users",
            "manage_billing": "upid:admin:billing"
        }
        
        return permission_map.get(action.name, "upid:read")

# UPID RBAC Roles Definition
UPID_ROLES = {
    "viewer": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read"
        ],
        "description": "Read-only access to analysis and costs"
    },
    "operator": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read",
            "upid:optimize:execute"
        ],
        "description": "Can analyze and execute optimizations"
    },
    "admin": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read", 
            "upid:optimize:execute",
            "upid:admin:users",
            "upid:admin:settings"
        ],
        "description": "Full administrative access"
    },
    "billing_admin": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read",
            "upid:admin:billing",
            "upid:admin:users"
        ],
        "description": "Billing and user management access"
    }
}
```

### **3. Metrics Collection Architecture**

```python
# metrics/collection_engine.py
class UniversalMetricsCollector:
    """
    Universal metrics collection that works with any Kubernetes cluster
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.collectors = self.initialize_collectors()
        
        def initialize_collectors(self) -> List[MetricsCollector]:
        """
        Initialize appropriate metrics collectors based on cluster capabilities
        """
        collectors = []
        
        # Core Kubernetes API collector (always available)
        collectors.append(KubernetesAPICollector(self.cluster_info))
        
        # Metrics Server collector (if available)
        if self.cluster_info.has_metrics_server:
            collectors.append(MetricsServerCollector(self.cluster_info))
        
        # Prometheus collector (if available)
        if self.cluster_info.has_prometheus:
            collectors.append(PrometheusCollector(self.cluster_info))
        
        # Cloud-specific collectors
        if self.cluster_info.cloud_provider == "aws":
            collectors.append(AWSCloudWatchCollector(self.cluster_info))
        elif self.cluster_info.cloud_provider == "gcp":
            collectors.append(GCPMonitoringCollector(self.cluster_info))
        elif self.cluster_info.cloud_provider == "azure":
            collectors.append(AzureMonitorCollector(self.cluster_info))
        
        # Kubelet collector (direct node access)
        collectors.append(KubeletCollector(self.cluster_info))
        
        return collectors
    
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect comprehensive pod metrics from all available sources
        """
        metrics_tasks = []
        
        for collector in self.collectors:
            if collector.supports_pod_metrics():
                task = collector.collect_pod_metrics(pod_id, time_range)
                metrics_tasks.append(task)
        
        # Collect from all sources in parallel
        metrics_results = await asyncio.gather(*metrics_tasks, return_exceptions=True)
        
        # Merge metrics from all successful collectors
        merged_metrics = PodMetrics()
        
        for i, result in enumerate(metrics_results):
            if isinstance(result, Exception):
                logger.warning(f"Collector {self.collectors[i]} failed: {result}")
                continue
            
            merged_metrics = self.merge_pod_metrics(merged_metrics, result)
        
        # Enhance with business metrics
        business_metrics = await self.collect_business_metrics(pod_id, time_range)
        merged_metrics.business_data = business_metrics
        
        return merged_metrics

class KubernetesAPICollector:
    """
    Collect metrics using core Kubernetes APIs (always available)
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.k8s_client = cluster_info.k8s_client
        
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect pod metrics from Kubernetes API
        """
        # Get pod information
        pod = await self.k8s_client.read_namespaced_pod(
            name=pod_id.name, 
            namespace=pod_id.namespace
        )
        
        # Get pod events
        events = await self.k8s_client.list_namespaced_event(
            namespace=pod_id.namespace,
            field_selector=f"involvedObject.name={pod_id.name}"
        )
        
        # Get resource requests and limits
        resources = self.extract_resource_specs(pod)
        
        # Get pod logs for request analysis
        logs = await self.collect_pod_logs(pod_id, time_range)
        
        return PodMetrics(
            pod_id=pod_id,
            resource_requests=resources.requests,
            resource_limits=resources.limits,
            events=[self.convert_event(e) for e in events.items],
            logs=logs,
            collection_source="kubernetes_api",
            timestamp=datetime.utcnow()
        )
    
    async def collect_pod_logs(self, pod_id: PodIdentifier, 
                             time_range: TimeRange) -> List[LogEntry]:
        """
        Collect pod logs for business activity analysis
        """
        try:
            # Calculate log lines to fetch (estimate)
            duration_hours = (time_range.end - time_range.start).total_seconds() / 3600
            estimated_lines = min(10000, int(duration_hours * 1000))  # ~1000 lines/hour max
            
            # Fetch logs
            log_response = await self.k8s_client.read_namespaced_pod_log(
                name=pod_id.name,
                namespace=pod_id.namespace,
                tail_lines=estimated_lines,
                timestamps=True
            )
            
            # Parse logs into structured format
            return self.parse_logs(log_response, time_range)
            
        except Exception as e:
            logger.warning(f"Failed to collect logs for {pod_id}: {e}")
            return []
    
    def parse_logs(self, log_text: str, time_range: TimeRange) -> List[LogEntry]:
        """
        Parse pod logs to extract request information
        """
        log_entries = []
        
        for line in log_text.split('\n'):
            if not line.strip():
                continue
                
            try:
                # Extract timestamp and message
                timestamp_str, message = line.split(' ', 1)
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                # Filter by time range
                if timestamp < time_range.start or timestamp > time_range.end:
                    continue
                
                # Parse HTTP requests from common log formats
                request_info = self.extract_request_info(message)
                
                log_entries.append(LogEntry(
                    timestamp=timestamp,
                    message=message,
                    request_info=request_info
                ))
                
            except Exception as e:
                # Skip malformed log lines
                continue
        
        return log_entries
    
    def extract_request_info(self, log_message: str) -> Optional[RequestInfo]:
        """
        Extract HTTP request information from log message
        """
        # Common log patterns
        patterns = [
            # Apache/Nginx style: "GET /api/users HTTP/1.1" 200 1234
            r'\"?([A-Z]+)\s+([^\s]+)\s+HTTP/[\d\.]+\"?\s+(\d+)\s+(\d+)',
            # Application logs: method=GET path=/api/users status=200
            r'method=([A-Z]+).*?path=([^\s]+).*?status=(\d+)',
            # JSON logs: {"method":"GET","path":"/api/users","status":200}
            r'\"method\":\"([A-Z]+)\".*?\"path\":\"([^\"]+)\".*?\"status\":(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_message)
            if match:
                method, path, status = match.groups()[:3]
                return RequestInfo(
                    method=method,
                    path=path,
                    status_code=int(status),
                    user_agent=self.extract_user_agent(log_message),
                    source_ip=self.extract_source_ip(log_message)
                )
        
        return None

class MetricsServerCollector:
    """
    Collect metrics from Kubernetes Metrics Server
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.metrics_client = cluster_info.metrics_client
        
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect current resource usage from metrics server
        """
        try:
            # Get current pod metrics
            pod_metrics = await self.metrics_client.list_namespaced_pod_metrics(
                namespace=pod_id.namespace
            )
            
            # Find metrics for our specific pod
            for pod_metric in pod_metrics.items:
                if pod_metric.metadata.name == pod_id.name:
                    return self.convert_metrics_server_data(pod_metric, pod_id)
            
            # Pod not found in metrics
            logger.warning(f"Pod {pod_id} not found in metrics server")
            return PodMetrics(pod_id=pod_id, collection_source="metrics_server")
            
        except Exception as e:
            logger.error(f"Failed to collect metrics server data: {e}")
            return PodMetrics(pod_id=pod_id, collection_source="metrics_server")
    
    def convert_metrics_server_data(self, metrics_data, pod_id: PodIdentifier) -> PodMetrics:
        """
        Convert metrics server data to UPID format
        """
        containers_metrics = []
        
        for container in metrics_data.containers:
            cpu_usage = self.parse_cpu_usage(container.usage.get('cpu', '0'))
            memory_usage = self.parse_memory_usage(container.usage.get('memory', '0'))
            
            containers_metrics.append(ContainerMetrics(
                name=container.name,
                cpu_usage_cores=cpu_usage,
                memory_usage_bytes=memory_usage,
                timestamp=datetime.utcnow()
            ))
        
        return PodMetrics(
            pod_id=pod_id,
            containers=containers_metrics,
            collection_source="metrics_server",
            timestamp=datetime.utcnow()
        )

class PrometheusCollector:
    """
    Collect metrics from Prometheus (if available)
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.prometheus_url = self.discover_prometheus_endpoint()
        
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect historical metrics from Prometheus
        """
        queries = {
            'cpu_usage': f'rate(container_cpu_usage_seconds_total{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}[5m])',
            'memory_usage': f'container_memory_usage_bytes{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}',
            'network_rx': f'rate(container_network_receive_bytes_total{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}[5m])',
            'network_tx': f'rate(container_network_transmit_bytes_total{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}[5m])',
            'fs_usage': f'container_fs_usage_bytes{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}'
        }
        
        # Execute queries in parallel
        query_tasks = []
        for metric_name, query in queries.items():
            task = self.execute_prometheus_query(query, time_range)
            query_tasks.append((metric_name, task))
        
        # Collect results
        metrics_data = {}
        for metric_name, task in query_tasks:
            try:
                result = await task
                metrics_data[metric_name] = result
            except Exception as e:
                logger.warning(f"Prometheus query failed for {metric_name}: {e}")
                metrics_data[metric_name] = []
        
        return self.convert_prometheus_data(metrics_data, pod_id)
    
    async def execute_prometheus_query(self, query: str, 
                                     time_range: TimeRange) -> List[PrometheusDataPoint]:
        """
        Execute Prometheus range query
        """
        params = {
            'query': query,
            'start': time_range.start.timestamp(),
            'end': time_range.end.timestamp(),
            'step': '60s'  # 1-minute resolution
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.prometheus_url}/api/v1/query_range", 
                                 params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_prometheus_response(data)
                else:
                    raise Exception(f"Prometheus query failed: {response.status}")
    
    def discover_prometheus_endpoint(self) -> str:
        """
        Auto-discover Prometheus endpoint
        """
        # Common Prometheus service names and namespaces
        prometheus_services = [
            ("prometheus-server", "monitoring"),
            ("prometheus-server", "prometheus"),
            ("prometheus", "monitoring"),
            ("prometheus", "kube-system"),
            ("prometheus-operator-prometheus", "monitoring")
        ]
        
        for service_name, namespace in prometheus_services:
            try:
                service = self.cluster_info.k8s_client.read_namespaced_service(
                    name=service_name, namespace=namespace
                )
                
                # Construct URL
                port = service.spec.ports[0].port
                return f"http://{service_name}.{namespace}.svc.cluster.local:{port}"
                
            except Exception:
                continue
        
        # Default fallback
        return "http://prometheus-server.monitoring.svc.cluster.local:80"

class BusinessMetricsCollector:
    """
    Collect business-relevant metrics from application logs and external sources
    """
    
    def __init__(self):
        self.request_patterns = self.compile_request_patterns()
        
    async def collect_business_metrics(self, pod_id: PodIdentifier, 
                                     time_range: TimeRange) -> BusinessMetrics:
        """
        Analyze logs to extract business activity metrics
        """
        # Get pod logs
        logs = await self.get_pod_logs(pod_id, time_range)
        
        # Analyze request patterns
        requests = self.extract_requests_from_logs(logs)
        
        # Filter business requests
        business_requests = self.filter_business_requests(requests)
        
        # Calculate business metrics
        return BusinessMetrics(
            total_requests=len(requests),
            business_requests=len(business_requests),
            business_request_ratio=len(business_requests) / max(len(requests), 1),
            request_patterns=self.analyze_request_patterns(business_requests),
            revenue_indicators=self.extract_revenue_indicators(business_requests),
            user_activity=self.analyze_user_activity(business_requests)
        )
    
    def filter_business_requests(self, requests: List[RequestInfo]) -> List[RequestInfo]:
        """
        Filter out non-business requests (health checks, monitoring, etc.)
        """
        business_requests = []
        
        for request in requests:
            if self.is_business_request(request):
                business_requests.append(request)
        
        return business_requests
    
    def is_business_request(self, request: RequestInfo) -> bool:
        """
        Determine if request represents actual business activity
        """
        # Filter out health checks
        health_check_paths = [
            '/health', '/ping', '/status', '/ready', '/live',
            '/healthz', '/readiness', '/liveness', '/metrics'
        ]
        
        if request.path.lower() in health_check_paths:
            return False
        
        # Filter out monitoring systems
        monitoring_user_agents = [
            'kube-probe', 'prometheus', 'grafana',
            'datadog', 'newrelic', 'pingdom'
        ]
        
        if request.user_agent:
            for agent in monitoring_user_agents:
                if agent.lower() in request.user_agent.lower():
                    return False
        
        # Filter out load balancer health checks
        lb_user_agents = [
            'ELB-HealthChecker', 'GoogleHC', 'Azure-HealthCheck',
            'kube-proxy', 'ingress-nginx'
        ]
        
        if request.user_agent:
            for agent in lb_user_agents:
                if agent in request.user_agent:
                    return False
        
        # Filter out internal service calls (heuristic)
        if request.user_agent and 'go-http-client' in request.user_agent:
            return False
        
        # This is likely a business request
        return True
```

### **4. Cloud Provider Billing Integration**

```python
# billing/cloud_billing.py
class CloudBillingIntegrator:
    """
    Universal cloud billing integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.billing_client = self.initialize_billing_client()
        
    def initialize_billing_client(self):
        """
        Initialize appropriate billing client based on cloud provider
        """
        if self.cluster_info.cloud_provider == "aws":
            return AWSBillingClient(self.cluster_info)
        elif self.cluster_info.cloud_provider == "gcp":
            return GCPBillingClient(self.cluster_info)
        elif self.cluster_info.cloud_provider == "azure":
            return AzureBillingClient(self.cluster_info)
        else:
            return GenericBillingClient(self.cluster_info)
    
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get actual cluster costs from cloud provider
        """
        return await self.billing_client.get_cluster_costs(time_range)

class AWSBillingClient:
    """
    AWS Cost Explorer integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.cost_explorer = boto3.client('ce', region_name=cluster_info.region)
        self.ec2_client = boto3.client('ec2', region_name=cluster_info.region)
        
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get EKS cluster costs from AWS Cost Explorer
        """
        # Get cluster node group information
        node_groups = await self.get_cluster_node_groups()
        
        # Build cost filter for cluster resources
        cost_filter = self.build_cluster_cost_filter(node_groups)
        
        # Query Cost Explorer
        response = await self.query_cost_explorer(cost_filter, time_range)
        
        # Parse and structure cost data
        return self.parse_aws_cost_response(response, node_groups)
    
    async def get_cluster_node_groups(self) -> List[NodeGroup]:
        """
        Get EKS cluster node groups and their instances
        """
        node_groups = []
        
        # Get cluster nodes
        nodes = await self.cluster_info.k8s_client.list_node()
        
        for node in nodes.items:
            # Extract AWS instance information from node
            instance_id = self.extract_instance_id(node)
            instance_type = self.extract_instance_type(node)
            availability_zone = self.extract_availability_zone(node)
            
            if instance_id:
                # Get instance details from EC2
                instance_details = await self.get_instance_details(instance_id)
                
                node_groups.append(NodeGroup(
                    node_name=node.metadata.name,
                    instance_id=instance_id,
                    instance_type=instance_type,
                    availability_zone=availability_zone,
                    instance_details=instance_details
                ))
        
        return node_groups
    
    def extract_instance_id(self, node) -> str:
        """
        Extract EC2 instance ID from Kubernetes node
        """
        # Check node annotations and labels
        if 'node.kubernetes.io/instance-id' in node.metadata.annotations:
            return node.metadata.annotations['node.kubernetes.io/instance-id']
        
        # Parse from provider ID
        provider_id = getattr(node.spec, 'provider_id', '')
        if provider_id.startswith('aws:///'):
            return provider_id.split('/')[-1]
        
        return None
    
    async def query_cost_explorer(self, cost_filter: dict, 
                                time_range: TimeRange) -> dict:
        """
        Query AWS Cost Explorer API
        """
        # Convert time range to AWS format
        start_date = time_range.start.strftime('%Y-%m-%d')
        end_date = time_range.end.strftime('%Y-%m-%d')
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}
                ],
                Filter=cost_filter
            )
        )
        
        return response
    
    def build_cluster_cost_filter(self, node_groups: List[NodeGroup]) -> dict:
        """
        Build Cost Explorer filter for cluster resources
        """
        # Get all instance IDs in cluster
        instance_ids = [ng.instance_id for ng in node_groups if ng.instance_id]
        
        if not instance_ids:
            # Fallback to cluster tag filter
            return {
                'Tags': {
                    'Key': 'kubernetes.io/cluster/' + self.cluster_info.cluster_name,
                    'Values': ['owned', 'shared']
                }
            }
        
        # Filter by instance IDs
        return {
            'Dimensions': {
                'Key': 'RESOURCE_ID',
                'Values': instance_ids
            }
        }

class GCPBillingClient:
    """
    GCP Cloud Billing integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.billing_client = self.initialize_gcp_billing()
        
    def initialize_gcp_billing(self):
        """
        Initialize GCP billing client
        """
        from google.cloud import billing_v1
        return billing_v1.CloudBillingClient()
    
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get GKE cluster costs from GCP Billing API
        """
        # Get cluster node information
        nodes = await self.get_cluster_nodes()
        
        # Build billing query
        query = self.build_gcp_billing_query(nodes, time_range)
        
        # Execute billing query
        response = await self.execute_billing_query(query)
        
        # Parse response
        return self.parse_gcp_billing_response(response, nodes)
    
    def build_gcp_billing_query(self, nodes: List[dict], 
                               time_range: TimeRange) -> dict:
        """
        Build GCP billing query for cluster resources
        """
        # Extract instance names from nodes
        instance_names = []
        for node in nodes:
            instance_name = self.extract_gcp_instance_name(node)
            if instance_name:
                instance_names.append(instance_name)
        
        return {
            'project_id': self.cluster_info.project_id,
            'time_range': {
                'start_time': time_range.start.isoformat(),
                'end_time': time_range.end.isoformat()
            },
            'filter': f'service.description="Compute Engine" AND resource.labels.instance_name=("{"|".join(instance_names)}")'
        }

class AzureBillingClient:
    """
    Azure Cost Management integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.cost_client = self.initialize_azure_cost_client()
        
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get AKS cluster costs from Azure Cost Management API
        """
        # Get cluster resource group and node resource group
        resource_groups = await self.get_cluster_resource_groups()
        
        # Build cost query
        query = self.build_azure_cost_query(resource_groups, time_range)
        
        # Execute cost query
        response = await self.execute_azure_cost_query(query)
        
        # Parse response
        return self.parse_azure_cost_response(response, resource_groups)

# Cost attribution engine
class CostAttributionEngine:
    """
    Attribute cloud costs to specific pods and workloads
    """
    
    def __init__(self, billing_client: CloudBillingClient):
        self.billing_client = billing_client
        
    async def calculate_pod_cost(self, pod_id: PodIdentifier, 
                               pod_metrics: PodMetrics,
                               time_range: TimeRange) -> PodCostBreakdown:
        """
        Calculate precise cost attribution for a pod
        """
        # Get cluster costs
        cluster_costs = await self.billing_client.get_cluster_costs(time_range)
        
        # Get pod's node
        pod_node = await self.get_pod_node(pod_id)
        
        # Get node costs
        node_costs = cluster_costs.get_node_costs(pod_node.name)
        
        # Calculate pod's resource allocation ratio
        allocation_ratio = self.calculate_allocation_ratio(pod_metrics, pod_node)
        
        # Calculate pod costs
        return PodCostBreakdown(
            pod_id=pod_id,
            node_name=pod_node.name,
            hourly_cost=node_costs.hourly_cost * allocation_ratio,
            daily_cost=node_costs.daily_cost * allocation_ratio,
            monthly_projection=node_costs.monthly_cost * allocation_ratio,
            allocation_ratio=allocation_ratio,
            cost_drivers=self.identify_cost_drivers(pod_metrics, node_costs)
        )
    
    def calculate_allocation_ratio(self, pod_metrics: PodMetrics, 
                                 node: NodeInfo) -> float:
        """
        Calculate pod's fair share of node costs
        """
        # CPU allocation ratio
        cpu_ratio = pod_metrics.cpu_request / node.allocatable_cpu
        
        # Memory allocation ratio  
        memory_ratio = pod_metrics.memory_request / node.allocatable_memory
        
        # Weighted average (CPU typically more expensive)
        weighted_ratio = (cpu_ratio * 0.6) + (memory_ratio * 0.4)
        
        return min(weighted_ratio, 1.0)  # Cap at 100%
```

### **5. Implementation Plan & Timeline**

```python
# implementation/plan.py
IMPLEMENTATION_PHASES = {
    "Phase 1: Foundation (Weeks 1-4)": {
        "Week 1": {
            "Universal Authentication System": [
                "Implement LocalKubernetesDetector",
                "Implement CloudKubernetesDetector", 
                "Create UniversalAuthenticator",
                "Add auto-detection for docker-desktop, minikube, k3s, kind"
            ],
            "Core Kubernetes Integration": [
                "Create KubernetesAPICollector",
                "Implement cluster capabilities detection",
                "Add RBAC permission checking",
                "Test with local clusters"
            ]
        },
        "Week 2": {
            "Cloud Provider Detection": [
                "Implement EKS detection and authentication",
                "Implement GKE detection and authentication", 
                "Implement AKS detection and authentication",
                "Add cloud credentials validation"
            ],
            "Metrics Collection": [
                "Create MetricsServerCollector",
                "Implement KubeletCollector",
                "Add PrometheusCollector (if available)",
                "Create unified metrics interface"
            ]
        },
        "Week 3": {
            "Billing Integration": [
                "Implement AWS Cost Explorer client",
                "Implement GCP Billing API client",
                "Implement Azure Cost Management client",
                "Create cost attribution engine"
            ],
            "Database Foundation": [
                "Set up TimescaleDB for time-series data",
                "Create PostgreSQL for metadata",
                "Implement data models and schemas",
                "Add data compression and partitioning"
            ]
        },
        "Week 4": {
            "Basic CLI Commands": [
                "Implement 'upid analyze pod' command",
                "Implement 'upid analyze deployment' command",
                "Implement 'upid analyze cluster' command", 
                "Add authentication flow to CLI"
            ],
            "Testing & Validation": [
                "Test with local Kubernetes clusters",
                "Test with cloud Kubernetes clusters",
                "Validate cost calculations",
                "End-to-end testing"
            ]
        }
    },
    
    "Phase 2: Intelligence (Weeks 5-8)": {
        "Week 5": {
            "Pod Idle Detection": [
                "Implement multi-factor idle detection algorithm",
                "Add business request filtering",
                "Create confidence scoring system",
                "Add pattern recognition"
            ],
            "Business Correlation": [
                "Implement log parsing for request extraction",
                "Add business activity correlation",
                "Create revenue attribution logic",
                "Add user impact scoring"
            ]
        },
        "Week 6": {
            "Advanced Analytics": [
                "Implement time-series analysis",
                "Add trend detection algorithms",
                "Create predictive modeling",
                "Add anomaly detection"
            ],
            "Cost Optimization": [
                "Implement resource rightsizing recommendations",
                "Add waste identification algorithms",
                "Create optimization priority scoring",
                "Add ROI calculation engine"
            ]
        },
        "Week 7": {
            "Zero Pod Scaling": [
                "Implement zero-pod scaling engine",
                "Add safety validation system",
                "Create rollback mechanisms",
                "Add traffic monitoring"
            ],
            "Optimization Safety": [
                "Implement comprehensive safety checks",
                "Add dependency analysis",
                "Create impact assessment",
                "Add approval workflows"
            ]
        },
        "Week 8": {
            "Enhanced CLI Experience": [
                "Add intelligent auto-completion",
                "Implement real-time dashboard",
                "Create interactive optimization mode",
                "Add progress indicators and feedback"
            ],
            "Integration Testing": [
                "Test optimization workflows",
                "Validate safety mechanisms",
                "Performance testing",
                "Security testing"
            ]
        }
    },
    
    "Phase 3: Production (Weeks 9-12)": {
        "Week 9": {
            "Multi-tenancy & RBAC": [
                "Implement UPID RBAC system",
                "Add organization and team management",
                "Create fine-grained permissions",
                "Add audit logging"
            ],
            "FastAPI Backend": [
                "Create REST API endpoints",
                "Implement WebSocket for real-time data",
                "Add API authentication and authorization",
                "Create API documentation"
            ]
        },
        "Week 10": {
            "Performance Optimization": [
                "Optimize database queries",
                "Implement caching layers",
                "Add connection pooling",
                "Performance tuning"
            ],
            "Monitoring & Observability": [
                "Add Prometheus metrics",
                "Implement structured logging",
                "Create health checks",
                "Add error tracking"
            ]
        # UPID Complete Architecture & Implementation Guide

## 🏗️ **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                UPID PLATFORM                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           CLI Interface Layer                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Local Mode    │  │  Authenticated  │  │   SaaS Mode     │                │
│  │ (no auth req'd) │  │   CLI Mode      │  │ (web dashboard) │                │
│  │ Docker Desktop  │  │  EKS/GKE/AKS   │  │ Multi-tenant    │                │
│  │ minikube, k3s   │  │    kubectl      │  │    Portal       │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Authentication & Authorization Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Auto-Detect    │  │   K8s RBAC      │  │   UPID RBAC     │                │
│  │  - Local K8s    │  │  - ServiceAcct  │  │  - Multi-tenant │                │
│  │  - Cloud Config │  │  - Namespace    │  │  - Org/Team     │                │
│  │  - No Auth      │  │  - ClusterRole  │  │  - Custom Perms │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           Core Intelligence Engine                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Metrics        │  │   Analysis      │  │  Optimization   │                │
│  │  Collection     │  │   Engine        │  │   Engine        │                │
│  │                 │  │                 │  │                 │                │
│  │ • Pod Metrics   │  │ • Idle Detection│  │ • Resource Opt  │                │
│  │ • Node Metrics  │  │ • Cost Analysis │  │ • Zero Scaling  │                │
│  │ • Business Logs │  │ • Pattern ML    │  │ • Safety Checks │                │
│  │ • Request Data  │  │ • Confidence    │  │ • Rollback      │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Data Storage & Processing Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Time-Series    │  │   Metadata      │  │   Cache Layer   │                │
│  │   Database      │  │   Database      │  │                 │                │
│  │                 │  │                 │  │                 │                │
│  │ • TimescaleDB   │  │ • PostgreSQL    │  │ • Redis         │                │
│  │ • 90-day data   │  │ • User/Tenant   │  │ • Query Cache   │                │
│  │ • Compression   │  │ • RBAC Rules    │  │ • Session Store │                │
│  │ • Partitioning  │  │ • Audit Logs    │  │ • Rate Limiting │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                      Cloud Provider Integration Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │      AWS        │  │      GCP        │  │     Azure       │                │
│  │                 │  │                 │  │                 │                │
│  │ • Cost Explorer │  │ • Billing API   │  │ • Cost Mgmt API │                │
│  │ • EKS Detection │  │ • GKE Detection │  │ • AKS Detection │                │
│  │ • EC2 Pricing   │  │ • GCE Pricing   │  │ • VM Pricing    │                │
│  │ • IAM Roles     │  │ • IAM Binding   │  │ • RBAC          │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Kubernetes Integration Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Cluster Auto   │  │   Metrics API   │  │   Resource API  │                │
│  │   Detection     │  │                 │  │                 │                │
│  │                 │  │                 │  │                 │                │
│  │ • EKS/GKE/AKS   │  │ • metrics.k8s   │  │ • Core API      │                │
│  │ • Local K8s     │  │ • Prometheus    │  │ • Apps API      │                │
│  │ • Cloud Labels  │  │ • cAdvisor      │  │ • Custom Rsrc   │                │
│  │ • Node Metadata │  │ • Kubelet       │  │ • Events API    │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Flow Diagram                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  User Command: upid analyze pod nginx-123                                      │
│       │                                                                        │
│       ▼                                                                        │
│  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│  │   Auth Check    │────────▶│  Cluster Detect │────────▶│ Permission Check│  │
│  │                 │         │                 │         │                 │  │
│  │ • Local detect  │         │ • Cloud provider│         │ • Namespace     │  │
│  │ • Cloud config  │         │ • K8s version   │         │ • Resource      │  │
│  │ • UPID token    │         │ • Node labels   │         │ • Action        │  │
│  └─────────────────┘         └─────────────────┘         └─────────────────┘  │
│       │                             │                             │            │
│       ▼                             ▼                             ▼            │
│  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│  │  Metrics Fetch  │────────▶│   Cost Fetch    │────────▶│   Intelligence  │  │
│  │                 │         │                 │         │    Analysis     │  │
│  │ • Pod metrics   │         │ • Cloud billing │         │                 │  │
│  │ • Node metrics  │         │ • Instance costs│         │ • Idle detect   │  │
│  │ • Request logs  │         │ • Pricing APIs  │         │ • Cost calc     │  │
│  │ • Business data │         │ • Usage data    │         │ • Optimization  │  │
│  └─────────────────┘         └─────────────────┘         └─────────────────┘  │
│       │                             │                             │            │
│       ▼                             ▼                             ▼            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                        Response Generation                               │  │
│  │                                                                         │  │
│  │  • Confidence scoring                                                   │  │
│  │  • Actionable recommendations                                           │  │
│  │  • Cost savings calculations                                            │  │
│  │  • Risk assessment                                                      │  │
│  │  • Next steps suggestions                                               │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                          │
│                                     ▼                                          │
│                           CLI/Dashboard Output                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **Major Features Architecture**

### **1. Universal Authentication & Multi-Tenancy**

```python
# auth/universal_auth.py
class UniversalAuthenticator:
    """
    Handles all authentication scenarios automatically
    """
    
    def __init__(self):
        self.local_detector = LocalKubernetesDetector()
        self.cloud_detector = CloudKubernetesDetector()
        self.rbac_enforcer = RBACEnforcer()
        
    async def authenticate_user(self, context: CommandContext) -> AuthResult:
        """
        Universal authentication flow
        """
        # Step 1: Detect environment
        env_info = await self.detect_environment()
        
        # Step 2: Choose authentication strategy
        if env_info.is_local_cluster:
            return await self.authenticate_local(env_info)
        elif env_info.has_cloud_config:
            return await self.authenticate_cloud(env_info)
        else:
            return await self.authenticate_upid_saas(context)
    
    async def detect_environment(self) -> EnvironmentInfo:
        """
        Auto-detect Kubernetes environment
        """
        # Check for local clusters first
        local_info = await self.local_detector.detect()
        if local_info.detected:
            return EnvironmentInfo(
                is_local_cluster=True,
                cluster_type=local_info.cluster_type,  # docker-desktop, minikube, k3s, kind
                kubeconfig_path=local_info.kubeconfig_path,
                auth_required=False
            )
        
        # Check for cloud clusters
        cloud_info = await self.cloud_detector.detect()
        if cloud_info.detected:
            return EnvironmentInfo(
                is_local_cluster=False,
                cluster_type=cloud_info.cluster_type,  # eks, gke, aks
                cloud_provider=cloud_info.provider,
                kubeconfig_path=cloud_info.kubeconfig_path,
                auth_required=cloud_info.auth_required
            )
        
        # No cluster detected - prompt for UPID SaaS
        return EnvironmentInfo(
            is_local_cluster=False,
            cluster_type="unknown",
            auth_required=True,
            requires_setup=True
        )

class LocalKubernetesDetector:
    """
    Detect local Kubernetes environments
    """
    
    async def detect(self) -> LocalDetectionResult:
        """
        Detect local Kubernetes clusters
        """
        detectors = [
            self.detect_docker_desktop,
            self.detect_minikube,
            self.detect_k3s,
            self.detect_kind,
            self.detect_microk8s
        ]
        
        for detector in detectors:
            result = await detector()
            if result.detected:
                return result
        
        return LocalDetectionResult(detected=False)
    
    async def detect_docker_desktop(self) -> LocalDetectionResult:
        """
        Detect Docker Desktop Kubernetes
        """
        try:
            # Check kubeconfig for docker-desktop context
            config = await self.load_kubeconfig()
            
            for context in config.contexts:
                if 'docker-desktop' in context.name.lower():
                    # Test connection
                    if await self.test_connection(context):
                        return LocalDetectionResult(
                            detected=True,
                            cluster_type="docker-desktop",
                            context_name=context.name,
                            kubeconfig_path=config.path,
                            requires_auth=False,
                            local_access=True
                        )
        except Exception as e:
            logger.debug(f"Docker Desktop detection failed: {e}")
        
        return LocalDetectionResult(detected=False)
    
    async def detect_minikube(self) -> LocalDetectionResult:
        """
        Detect Minikube cluster
        """
        try:
            # Check if minikube command exists
            result = subprocess.run(['minikube', 'status'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and 'Running' in result.stdout:
                # Get minikube kubeconfig
                kubeconfig_path = subprocess.run(
                    ['minikube', 'config', 'view', 'kubeconfig'],
                    capture_output=True, text=True
                ).stdout.strip()
                
                return LocalDetectionResult(
                    detected=True,
                    cluster_type="minikube",
                    context_name="minikube",
                    kubeconfig_path=kubeconfig_path,
                    requires_auth=False,
                    local_access=True
                )
        except Exception as e:
            logger.debug(f"Minikube detection failed: {e}")
        
        return LocalDetectionResult(detected=False)
    
    async def detect_k3s(self) -> LocalDetectionResult:
        """
        Detect K3s cluster
        """
        try:
            # Check for K3s kubeconfig
            k3s_config_paths = [
                '/etc/rancher/k3s/k3s.yaml',
                os.path.expanduser('~/.kube/k3s-config'),
                os.path.expanduser('~/.k3s/config')
            ]
            
            for config_path in k3s_config_paths:
                if os.path.exists(config_path):
                    if await self.test_k3s_connection(config_path):
                        return LocalDetectionResult(
                            detected=True,
                            cluster_type="k3s",
                            context_name="default",
                            kubeconfig_path=config_path,
                            requires_auth=False,
                            local_access=True
                        )
        except Exception as e:
            logger.debug(f"K3s detection failed: {e}")
        
        return LocalDetectionResult(detected=False)

class CloudKubernetesDetector:
    """
    Detect cloud-managed Kubernetes clusters
    """
    
    async def detect(self) -> CloudDetectionResult:
        """
        Detect cloud Kubernetes clusters
        """
        detectors = [
            self.detect_eks,
            self.detect_gke,
            self.detect_aks,
            self.detect_openshift
        ]
        
        for detector in detectors:
            result = await detector()
            if result.detected:
                return result
        
        return CloudDetectionResult(detected=False)
    
    async def detect_eks(self) -> CloudDetectionResult:
        """
        Detect Amazon EKS cluster
        """
        try:
            # Check current kubeconfig context
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            if current_context and 'eks' in current_context.lower():
                # Parse EKS cluster info from context
                cluster_info = await self.parse_eks_context(current_context)
                
                # Test connection
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="eks",
                        cloud_provider="aws",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.region,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via AWS CLI
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"EKS detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
    
    async def detect_gke(self) -> CloudDetectionResult:
        """
        Detect Google GKE cluster
        """
        try:
            # Check for GKE context pattern
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            # GKE contexts usually follow pattern: gke_project_zone_cluster
            if current_context and current_context.startswith('gke_'):
                cluster_info = await self.parse_gke_context(current_context)
                
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="gke",
                        cloud_provider="gcp",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.zone,
                        project_id=cluster_info.project_id,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via gcloud
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"GKE detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
    
    async def detect_aks(self) -> CloudDetectionResult:
        """
        Detect Azure AKS cluster
        """
        try:
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            # Check if context uses Azure authentication
            context_config = await self.get_context_config(current_context)
            
            if self.is_azure_context(context_config):
                cluster_info = await self.parse_aks_context(current_context)
                
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="aks",
                        cloud_provider="azure",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.region,
                        resource_group=cluster_info.resource_group,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via az CLI
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"AKS detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
```

### **2. RBAC & Permission System**

```python
# auth/rbac_system.py
class RBACEnforcer:
    """
    Comprehensive RBAC enforcement for UPID
    """
    
    def __init__(self):
        self.k8s_rbac = KubernetesRBACAnalyzer()
        self.upid_rbac = UPIDRBACManager()
        
    async def check_permissions(self, user: AuthenticatedUser, 
                              action: Action, 
                              resource: Resource) -> PermissionResult:
        """
        Check if user has permission to perform action on resource
        """
        # For local clusters - allow all operations
        if user.auth_type == "local":
            return PermissionResult(
                allowed=True,
                reason="Local cluster access - full permissions"
            )
        
        # For cloud clusters - check Kubernetes RBAC
        if user.auth_type == "kubernetes":
            k8s_result = await self.k8s_rbac.check_permission(
                user.k8s_user, action, resource
            )
            
            if not k8s_result.allowed:
                return PermissionResult(
                    allowed=False,
                    reason=f"Kubernetes RBAC denied: {k8s_result.reason}",
                    required_permissions=k8s_result.required_permissions
                )
        
        # For UPID SaaS - check UPID RBAC
        if user.auth_type == "upid":
            upid_result = await self.upid_rbac.check_permission(
                user.upid_user, action, resource
            )
            
            if not upid_result.allowed:
                return PermissionResult(
                    allowed=False,
                    reason=f"UPID RBAC denied: {upid_result.reason}",
                    required_permissions=upid_result.required_permissions
                )
        
        return PermissionResult(allowed=True)

class KubernetesRBACAnalyzer:
    """
    Analyze and enforce Kubernetes RBAC permissions
    """
    
    async def check_permission(self, k8s_user: KubernetesUser, 
                             action: Action, 
                             resource: Resource) -> RBACResult:
        """
        Check Kubernetes RBAC permissions
        """
        # Get user's effective permissions
        permissions = await self.get_user_permissions(k8s_user)
        
        # Check namespace-level permissions
        if resource.namespace:
            namespace_perms = permissions.namespace_permissions.get(resource.namespace, [])
            if self.action_allowed(action, resource, namespace_perms):
                return RBACResult(
                    allowed=True,
                    source="namespace_rbac",
                    permissions_used=namespace_perms
                )
        
        # Check cluster-level permissions
        cluster_perms = permissions.cluster_permissions
        if self.action_allowed(action, resource, cluster_perms):
            return RBACResult(
                allowed=True,
                source="cluster_rbac", 
                permissions_used=cluster_perms
            )
        
        # Permission denied
        required_perms = self.get_required_permissions(action, resource)
        return RBACResult(
            allowed=False,
            reason=f"Missing permissions for {action.name} on {resource.type}",
            required_permissions=required_perms,
            available_namespaces=list(permissions.namespace_permissions.keys())
        )
    
    async def get_user_permissions(self, k8s_user: KubernetesUser) -> UserPermissions:
        """
        Get effective permissions for Kubernetes user
        """
        # Use Kubernetes SubjectAccessReview API to check permissions
        permissions = UserPermissions()
        
        # Check cluster-level permissions
        cluster_resources = ['nodes', 'persistentvolumes', 'clusterroles']
        for resource in cluster_resources:
            for verb in ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']:
                if await self.can_user_perform(k8s_user, verb, resource):
                    permissions.cluster_permissions.append(
                        Permission(verb=verb, resource=resource)
                    )
        
        # Check namespace-level permissions for each accessible namespace
        namespaces = await self.get_accessible_namespaces(k8s_user)
        
        for namespace in namespaces:
            ns_permissions = []
            namespace_resources = ['pods', 'deployments', 'services', 'configmaps']
            
            for resource in namespace_resources:
                for verb in ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']:
                    if await self.can_user_perform(k8s_user, verb, resource, namespace):
                        ns_permissions.append(
                            Permission(verb=verb, resource=resource, namespace=namespace)
                        )
            
            if ns_permissions:
                permissions.namespace_permissions[namespace] = ns_permissions
        
        return permissions
    
    async def get_accessible_namespaces(self, k8s_user: KubernetesUser) -> List[str]:
        """
        Get list of namespaces user has access to
        """
        accessible_namespaces = []
        
        # Get all namespaces
        all_namespaces = await self.k8s_client.list_namespaces()
        
        # Check access to each namespace
        for namespace in all_namespaces:
            if await self.can_user_perform(k8s_user, 'get', 'pods', namespace.name):
                accessible_namespaces.append(namespace.name)
        
        return accessible_namespaces
    
    async def can_user_perform(self, k8s_user: KubernetesUser, 
                             verb: str, resource: str, 
                             namespace: str = None) -> bool:
        """
        Check if user can perform specific action using SubjectAccessReview
        """
        try:
            # Create SubjectAccessReview
            review = client.V1SubjectAccessReview(
                spec=client.V1SubjectAccessReviewSpec(
                    user=k8s_user.username,
                    groups=k8s_user.groups,
                    resource_attributes=client.V1ResourceAttributes(
                        verb=verb,
                        resource=resource,
                        namespace=namespace
                    )
                )
            )
            
            # Submit review
            result = await self.k8s_client.create_subject_access_review(review)
            
            return result.status.allowed
            
        except Exception as e:
            logger.debug(f"Permission check failed: {e}")
            return False
    
    def get_required_permissions(self, action: Action, resource: Resource) -> List[Permission]:
        """
        Get required permissions for UPID actions
        """
        permission_map = {
            "analyze_pod": [
                Permission(verb="get", resource="pods"),
                Permission(verb="get", resource="nodes"),  # for cost calculation
                Permission(verb="list", resource="events")  # for analysis
            ],
            "analyze_deployment": [
                Permission(verb="get", resource="deployments"),
                Permission(verb="list", resource="pods"),
                Permission(verb="get", resource="replicasets")
            ],
            "optimize_pod": [
                Permission(verb="get", resource="pods"),
                Permission(verb="patch", resource="pods"),  # for resource updates
                Permission(verb="patch", resource="deployments")  # for scaling
            ],
            "zero_scale": [
                Permission(verb="get", resource="deployments"),
                Permission(verb="patch", resource="deployments"),  # for scaling to 0
                Permission(verb="create", resource="configmaps")  # for rollback data
            ]
        }
        
        return permission_map.get(action.name, [])

# UPID Custom RBAC for SaaS mode
class UPIDRBACManager:
    """
    UPID-specific RBAC for multi-tenant SaaS
    """
    
    def __init__(self):
        self.db = DatabaseManager()
    
    async def check_permission(self, upid_user: UPIDUser, 
                             action: Action, 
                             resource: Resource) -> RBACResult:
        """
        Check UPID-specific permissions
        """
        # Get user roles and permissions
        user_roles = await self.db.get_user_roles(upid_user.user_id)
        
        # Check organization-level permissions
        if resource.organization_id != upid_user.organization_id:
            return RBACResult(
                allowed=False,
                reason="Resource belongs to different organization"
            )
        
        # Check team-level permissions
        if resource.team_id and resource.team_id not in upid_user.team_ids:
            return RBACResult(
                allowed=False,
                reason="User not member of resource team"
            )
        
        # Check action permissions
        required_permission = self.get_required_upid_permission(action)
        
        for role in user_roles:
            if required_permission in role.permissions:
                return RBACResult(
                    allowed=True,
                    source="upid_rbac",
                    role_used=role.name
                )
        
        return RBACResult(
            allowed=False,
            reason=f"Missing permission: {required_permission}",
            required_permissions=[required_permission]
        )
    
    def get_required_upid_permission(self, action: Action) -> str:
        """
        Map UPID actions to permission strings
        """
        permission_map = {
            "analyze_pod": "upid:analyze:read",
            "analyze_deployment": "upid:analyze:read", 
            "analyze_cluster": "upid:analyze:read",
            "optimize_pod": "upid:optimize:execute",
            "zero_scale": "upid:optimize:execute",
            "view_costs": "upid:costs:read",
            "manage_users": "upid:admin:users",
            "manage_billing": "upid:admin:billing"
        }
        
        return permission_map.get(action.name, "upid:read")

# UPID RBAC Roles Definition
UPID_ROLES = {
    "viewer": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read"
        ],
        "description": "Read-only access to analysis and costs"
    },
    "operator": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read",
            "upid:optimize:execute"
        ],
        "description": "Can analyze and execute optimizations"
    },
    "admin": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read", 
            "upid:optimize:execute",
            "upid:admin:users",
            "upid:admin:settings"
        ],
        "description": "Full administrative access"
    },
    "billing_admin": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read",
            "upid:admin:billing",
            "upid:admin:users"
        ],
        "description": "Billing and user management access"
    }
}
```

### **3. Metrics Collection Architecture**

```python
# metrics/collection_engine.py
class UniversalMetricsCollector:
    """
    Universal metrics collection that works with any Kubernetes cluster
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.collectors = self.initialize_collectors()
        
    def initialize_

        },
        "Week 11": {
            "Enterprise Features": [
                "Implement multi-cluster support",
                "Add advanced security features",
                "Create compliance reporting",
                "Add enterprise authentication (SAML/OIDC)"
            ],
            "SaaS Platform": [
                "Create web dashboard",
                "Implement user management",
                "Add billing integration",
                "Create customer onboarding"
            ]
        },
        "Week 12": {
            "Production Deployment": [
                "Create Kubernetes deployment manifests",
                "Set up CI/CD pipelines",
                "Configure monitoring and alerting",
                "Production testing"
            ],
            "Documentation & Launch": [
                "Complete user documentation",
                "Create API documentation",
                "Prepare launch materials",
                "Beta customer onboarding"
            ]
        }
    }
}
```

### **6. Core Libraries & Dependencies**

```python
# requirements/core_libraries.py
CORE_DEPENDENCIES = {
    "Kubernetes Integration": {
        "kubernetes": "28.1.0",  # Official Kubernetes Python client
        "kubernetes-asyncio": "28.1.0",  # Async support for K8s client
        "pyyaml": "6.0.1",  # For kubeconfig parsing
        "urllib3": "1.26.18"  # HTTP client for K8s API
    },
    
    "Cloud Provider SDKs": {
        "boto3": "1.34.0",  # AWS SDK
        "botocore": "1.34.0",  # AWS core library
        "google-cloud-billing": "1.12.0",  # GCP Billing API
        "google-cloud-monitoring": "2.16.0",  # GCP Monitoring
        "google-auth": "2.23.4",  # GCP authentication
        "azure-mgmt-costmanagement": "4.0.1",  # Azure Cost Management
        "azure-mgmt-monitor": "6.0.2",  # Azure Monitor
        "azure-identity": "1.15.0"  # Azure authentication
    },
    
    "FastAPI & Web Framework": {
        "fastapi": "0.104.1",  # Modern web framework
        "uvicorn": "0.24.0",  # ASGI server
        "gunicorn": "21.2.0",  # Production WSGI server
        "websockets": "12.0",  # WebSocket support
        "python-multipart": "0.0.6",  # File uploads
        "jinja2": "3.1.2"  # Template engine
    },
    
    "Database & Storage": {
        "asyncpg": "0.29.0",  # Async PostgreSQL driver
        "psycopg2-binary": "2.9.9",  # PostgreSQL adapter
        "redis": "5.0.1",  # Redis client
        "aioredis": "2.0.1",  # Async Redis client
        "sqlalchemy": "2.0.23",  # ORM
        "alembic": "1.13.1"  # Database migrations
    },
    
    "Data Processing & Analytics": {
        "pandas": "2.1.4",  # Data manipulation
        "numpy": "1.25.2",  # Numerical computing
        "scipy": "1.11.4",  # Scientific computing
        "scikit-learn": "1.3.2",  # Machine learning
        "prometheus-client": "0.19.0",  # Metrics collection
        "aiohttp": "3.9.1"  # Async HTTP client
    },
    
    "Authentication & Security": {
        "pyjwt": "2.8.0",  # JWT tokens
        "cryptography": "41.0.8",  # Encryption
        "bcrypt": "4.1.2",  # Password hashing
        "python-jose": "3.3.0",  # JWT utilities
        "passlib": "1.7.4"  # Password utilities
    },
    
    "CLI & User Interface": {
        "typer": "0.9.0",  # CLI framework
        "rich": "13.7.0",  # Rich text and beautiful formatting
        "click": "8.1.7",  # CLI utilities
        "tabulate": "0.9.0",  # Table formatting
        "colorama": "0.4.6"  # Cross-platform colored terminal
    },
    
    "Utilities & Helpers": {
        "pydantic": "2.5.2",  # Data validation
        "python-dotenv": "1.0.0",  # Environment variables
        "structlog": "23.2.0",  # Structured logging
        "tenacity": "8.2.3",  # Retry logic
        "httpx": "0.25.2",  # Modern HTTP client
        "dateparser": "1.2.0"  # Date parsing
    },
    
    "Testing & Development": {
        "pytest": "7.4.3",  # Testing framework
        "pytest-asyncio": "0.21.1",  # Async testing
        "pytest-cov": "4.1.0",  # Coverage reporting
        "black": "23.11.0",  # Code formatting
        "isort": "5.12.0",  # Import sorting
        "mypy": "1.7.1",  # Type checking
        "pre-commit": "3.6.0"  # Git hooks
    }
}

# Create requirements.txt
def generate_requirements_txt():
    """
    Generate requirements.txt from dependencies
    """
    requirements = []
    
    for category, packages in CORE_DEPENDENCIES.items():
        requirements.append(f"# {category}")
        for package, version in packages.items():
            requirements.append(f"{package}=={version}")
        requirements.append("")  # Empty line
    
    return "\n".join(requirements)

# Optional dependencies for different deployment scenarios
OPTIONAL_DEPENDENCIES = {
    "local_development": [
        "jupyter==1.0.0",  # For data analysis
        "matplotlib==3.8.2",  # Plotting
        "seaborn==0.13.0"  # Statistical visualization
    ],
    
    "production": [
        "sentry-sdk==1.39.2",  # Error tracking
        "newrelic==9.2.0",  # APM monitoring
        "datadog==0.48.0"  # Infrastructure monitoring
    ],
    
    "enterprise": [
        "ldap3==2.9.1",  # LDAP authentication
        "python-saml==1.15.0",  # SAML authentication
        "oauthlib==3.2.2"  # OAuth support
    ]
}
```

### **7. Authentication Flow Details**

```python
# auth/authentication_flows.py
class AuthenticationFlowManager:
    """
    Manages different authentication flows based on environment
    """
    
    def __init__(self):
        self.local_flow = LocalAuthFlow()
        self.cloud_flow = CloudAuthFlow()
        self.saas_flow = SaaSAuthFlow()
    
    async def authenticate(self, command_context: CommandContext) -> AuthResult:
        """
        Main authentication entry point
        """
        # Check for explicit authentication mode
        if command_context.has_flag("--local"):
            return await self.local_flow.authenticate(command_context)
        
        if command_context.has_token():
            return await self.saas_flow.authenticate(command_context)
        
        # Auto-detect environment and authenticate
        env_detection = await self.detect_environment()
        
        if env_detection.is_local_cluster:
            return await self.local_flow.authenticate(command_context)
        elif env_detection.has_cloud_credentials:
            return await self.cloud_flow.authenticate(command_context)
        else:
            return await self.saas_flow.authenticate(command_context)

class LocalAuthFlow:
    """
    Authentication flow for local Kubernetes clusters
    """
    
    async def authenticate(self, command_context: CommandContext) -> AuthResult:
        """
        Authenticate for local clusters (no auth required)
        """
        # Detect local cluster type
        cluster_type = await self.detect_local_cluster_type()
        
        if not cluster_type:
            raise AuthenticationError(
                "No local Kubernetes cluster detected. "
                "Please start Docker Desktop, minikube, k3s, or kind."
            )
        
        # Load kubeconfig
        kubeconfig_path = await self.find_kubeconfig(cluster_type)
        k8s_client = await self.create_k8s_client(kubeconfig_path)
        
        # Test connection
        try:
            await k8s_client.list_node()
        except Exception as e:
            raise AuthenticationError(f"Cannot connect to {cluster_type}: {e}")
        
        return AuthResult(
            auth_type="local",
            cluster_type=cluster_type,
            k8s_client=k8s_client,
            permissions=LocalPermissions(),  # Full permissions for local
            user_info=LocalUser(cluster_type=cluster_type)
        )
    
    async def detect_local_cluster_type(self) -> Optional[str]:
        """
        Detect which local Kubernetes cluster is running
        """
        detectors = {
            "docker-desktop": self.check_docker_desktop,
            "minikube": self.check_minikube,
            "k3s": self.check_k3s,
            "kind": self.check_kind,
            "microk8s": self.check_microk8s
        }
        
        for cluster_type, detector in detectors.items():
            if await detector():
                return cluster_type
        
        return None
    
    async def check_docker_desktop(self) -> bool:
        """
        Check if Docker Desktop Kubernetes is running
        """
        try:
            # Check if docker-desktop context exists and is accessible
            result = subprocess.run([
                "kubectl", "config", "get-contexts", "docker-desktop"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Try to connect
                test_result = subprocess.run([
                    "kubectl", "--context=docker-desktop", "get", "nodes"
                ], capture_output=True, text=True, timeout=5)
                
                return test_result.returncode == 0
        except Exception:
            pass
        
        return False
    
    async def check_minikube(self) -> bool:
        """
        Check if minikube is running
        """
        try:
            result = subprocess.run([
                "minikube", "status"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0 and "Running" in result.stdout
        except Exception:
            return False
    
    async def check_k3s(self) -> bool:
        """
        Check if k3s is running
        """
        try:
            # Check if k3s kubeconfig exists and cluster is accessible
            k3s_config_paths = [
                "/etc/rancher/k3s/k3s.yaml",
                os.path.expanduser("~/.kube/k3s-config")
            ]
            
            for config_path in k3s_config_paths:
                if os.path.exists(config_path):
                    test_result = subprocess.run([
                        "kubectl", "--kubeconfig", config_path, "get", "nodes"
                    ], capture_output=True, text=True, timeout=5)
                    
                    if test_result.returncode == 0:
                        return True
        except Exception:
            pass
        
        return False
    
    async def check_kind(self) -> bool:
        """
        Check if kind cluster is running
        """
        try:
            # List kind clusters
            result = subprocess.run([
                "kind", "get", "clusters"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                # At least one kind cluster exists, test connectivity
                test_result = subprocess.run([
                    "kubectl", "get", "nodes"
                ], capture_output=True, text=True, timeout=5)
                
                return test_result.returncode == 0
        except Exception:
            pass
        
        return False

class CloudAuthFlow:
    """
    Authentication flow for cloud-managed Kubernetes clusters
    """
    
    async def authenticate(self, command_context: CommandContext) -> AuthResult:
        """
        Authenticate for cloud clusters using existing cloud credentials
        """
        # Detect cloud provider
        cloud_info = await self.detect_cloud_cluster()
        
        if not cloud_info:
            raise AuthenticationError(
                "No cloud Kubernetes cluster detected. "
                "Please configure kubectl for your EKS/GKE/AKS cluster."
            )
        
        # Validate cloud credentials
        await self.validate_cloud_credentials(cloud_info)
        
        # Create authenticated clients
        k8s_client = await self.create_k8s_client(cloud_info.kubeconfig_path)
        billing_client = await self.create_billing_client(cloud_info)
        
        # Get user permissions from Kubernetes RBAC
        permissions = await self.get_k8s_permissions(k8s_client, cloud_info)
        
        return AuthResult(
            auth_type="kubernetes",
            cluster_type=cloud_info.cluster_type,
            cloud_provider=cloud_info.cloud_provider,
            k8s_client=k8s_client,
            billing_client=billing_client,
            permissions=permissions,
            user_info=CloudUser(
                cluster_name=cloud_info.cluster_name,
                cloud_provider=cloud_info.cloud_provider
            )
        )
    
    async def detect_cloud_cluster(self) -> Optional[CloudClusterInfo]:
        """
        Detect which cloud cluster is configured
        """
        # Get current kubectl context
        try:
            result = subprocess.run([
                "kubectl", "config", "current-context"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            current_context = result.stdout.strip()
            
            # Determine cloud provider from context name
            if "eks" in current_context.lower() or current_context.startswith("arn:aws"):
                return await self.parse_eks_context(current_context)
            elif current_context.startswith("gke_"):
                return await self.parse_gke_context(current_context)
            elif "aks" in current_context.lower() or "azure" in current_context.lower():
                return await self.parse_aks_context(current_context)
            
        except Exception as e:
            logger.debug(f"Failed to detect cloud cluster: {e}")
        
        return None
    
    async def validate_cloud_credentials(self, cloud_info: CloudClusterInfo):
        """
        Validate that cloud credentials are properly configured
        """
        if cloud_info.cloud_provider == "aws":
            await self.validate_aws_credentials()
        elif cloud_info.cloud_provider == "gcp":
            await self.validate_gcp_credentials()
        elif cloud_info.cloud_provider == "azure":
            await self.validate_azure_credentials()
    
    async def validate_aws_credentials(self):
        """
        Validate AWS credentials
        """
        try:
            import boto3
            
            # Test AWS credentials
            sts = boto3.client('sts')
            sts.get_caller_identity()
            
        except Exception as e:
            raise AuthenticationError(
                f"AWS credentials not configured or invalid: {e}\n"
                "Please run 'aws configure' or set up AWS credentials."
            )
    
    async def get_k8s_permissions(self, k8s_client, cloud_info: CloudClusterInfo) -> KubernetesPermissions:
        """
        Get user's actual Kubernetes permissions
        """
        rbac_analyzer = KubernetesRBACAnalyzer(k8s_client)
        
        # Get current user info
        user_info = await self.get_current_k8s_user(k8s_client)
        
        # Analyze permissions
        permissions = await rbac_analyzer.get_user_permissions(user_info)
        
        return permissions

class SaaSAuthFlow:
    """
    Authentication flow for UPID SaaS platform
    """
    
    async def authenticate(self, command_context: CommandContext) -> AuthResult:
        """
        Authenticate for UPID SaaS platform
        """
        # Check for existing token
        token = command_context.get_token() or self.get_stored_token()
        
        if token:
            # Validate existing token
            try:
                user_info = await self.validate_token(token)
                return await self.create_saas_auth_result(user_info, token)
            except TokenExpiredError:
                logger.info("Token expired, re-authenticating...")
            except InvalidTokenError:
                logger.warning("Invalid token, re-authenticating...")
        
        # Perform login flow
        return await self.perform_login_flow(command_context)
    
    async def perform_login_flow(self, command_context: CommandContext) -> AuthResult:
        """
        Perform interactive login flow
        """
        # Check if running in non-interactive mode
        if command_context.is_non_interactive():
            raise AuthenticationError(
                "UPID authentication required. Please run 'upid login' first or "
                "set UPID_TOKEN environment variable."
            )
        
        # Interactive login
        print("🔐 UPID Authentication Required")
        print("Please visit: https://app.upid.io/auth/cli")
        
        # Generate device code
        device_code = await self.generate_device_code()
        
        print(f"Enter this code: {device_code.user_code}")
        print("Waiting for authentication...")
        
        # Poll for completion
        token = await self.poll_for_token(device_code.device_code)
        
        # Store token for future use
        self.store_token(token)
        
        # Validate and return auth result
        user_info = await self.validate_token(token)
        return await self.create_saas_auth_result(user_info, token)
```

### **8. RBAC Guidelines & Rules**

```python
# auth/rbac_guidelines.py
UPID_RBAC_GUIDELINES = {
    "Core Principles": {
        "Principle of Least Privilege": "Users get minimum permissions needed for their role",
        "Defense in Depth": "Multiple layers of permission checking",
        "Fail Secure": "Deny access when permissions are unclear",
        "Audit Everything": "Log all permission checks and access attempts"
    },
    
    "Permission Inheritance": {
        "Local Clusters": "Full permissions (trusted environment)",
        "Cloud Clusters": "Respect existing Kubernetes RBAC",
        "UPID SaaS": "Custom RBAC with organization/team boundaries"
    },
    
    "RBAC Rules Implementation": [
        "Always check authentication before authorization",
        "Cache permission results for performance (5-minute TTL)",
        "Re-validate permissions on sensitive operations",
        "Provide clear error messages when access denied",
        "Allow users to check their own permissions",
        "Support permission debugging for admins"
    ]
}

class UPIDRBACRules:
    """
    UPID RBAC rules and enforcement
    """
    
    # Resource types that UPID works with
    RESOURCE_TYPES = [
        "pods", "deployments", "replicasets", "daemonsets", "statefulsets",
        "services", "ingresses", "configmaps", "secrets", "nodes",
        "namespaces", "persistentvolumes", "persistentvolumeclaims"
    ]
    
    # Actions that UPID performs
    ACTIONS = [
        "get", "list", "watch",  # Read operations
        "update", "patch",       # Modification operations
        "create", "delete"       # Create/destroy operations
    ]
    
    # UPID-specific permissions
    UPID_PERMISSIONS = {
        # Analysis permissions
        "upid:analyze:read": "Can view analysis results",
        "upid:analyze:execute": "Can trigger new analyses", 
        
        # Cost permissions
        "upid:costs:read": "Can view cost information",
        "upid:costs:manage": "Can manage cost allocation and budgets",
        
        # Optimization permissions
        "upid:optimize:read": "Can view optimization recommendations",
        "upid:optimize:execute": "Can execute optimizations",
        "upid:optimize:approve": "Can approve high-risk optimizations",
        
        # Administration permissions
        "upid:admin:users": "Can manage users and permissions",
        "upid:admin:clusters": "Can add/remove clusters",
        "upid:admin:billing": "Can manage billing and subscriptions",
        "upid:admin:settings": "Can modify system settings"
    }
    
    @staticmethod
    def get_required_k8s_permissions(action: str, resource_type: str) -> List[Permission]:
        """
        Get required Kubernetes permissions for UPID operations
        """
        base_permissions = [
            Permission(verb="get", resource=resource_type),
            Permission(verb="list", resource=resource_type)
        ]
        
        # Add additional permissions based on action
        if action in ["optimize", "scale"]:
            base_permissions.extend([
                Permission(verb="patch", resource=resource_type),
                Permission(verb="update", resource=resource_type)
            ])
        
        # Always need node access for cost calculation
        if resource_type in ["pods", "deployments"]:
            base_permissions.extend([
                Permission(verb="get", resource="nodes"),
                Permission(verb="list", resource="nodes")
            ])
        
        # Events access for analysis
        base_permissions.append(
            Permission(verb="list", resource="events")
        )
        
        return base_permissions
    
    @staticmethod
    def check_namespace_access(user_permissions: UserPermissions, 
                             namespace: str, 
                             required_action: str) -> bool:
        """
        Check if user has access to specific namespace
        """
        # Check if user has cluster-wide permissions
        for perm in user_permissions.cluster_permissions:
            if perm.verb == required_action and perm.resource == "*":
                return True
        
        # Check namespace-specific permissions
        namespace_perms = user_permissions.namespace_permissions.get(namespace, [])
        
        for perm in namespace_perms:
            if perm.verb == required_action:
                return True
        
        return False
    
    @staticmethod
    def filter_accessible_resources(user_permissions: UserPermissions,
                                  resources: List[KubernetesResource]) -> List[KubernetesResource]:
        """
        Filter resources to only those user can access
        """
        accessible = []
        
        for resource in resources:
            if UPIDRBACRules.check_namespace_access(
                user_permissions, 
                resource.namespace, 
                "get"
            ):
                accessible.append(resource)
        
        return accessible

# Example RBAC configuration for different scenarios
RBAC_SCENARIOS = {
    "Local Development": {
        "description": "Developer using local cluster (docker-desktop, minikube, etc.)",
        "permissions": "FULL",
        "rationale": "Local clusters are trusted development environments",
        "restrictions": "None"
    },
    
    "Cloud Developer": {
        "description": "Developer with kubectl access to cloud cluster",
        "permissions": "INHERIT_FROM_KUBERNETES",
        "kubernetes_requirements": [
            "get/list pods, deployments, services in assigned namespaces",
            "get/list nodes (for cost calculation)",
            "list events (for analysis)"
        ],
        "restrictions": "Limited to namespaces with existing access"
    },
    
    "Cloud Operator": {
        "description": "Platform engineer with optimization permissions",
        "permissions": "INHERIT_FROM_KUBERNETES + OPTIMIZATION",
        "kubernetes_requirements": [
            "get/list/patch pods, deployments in managed namespaces",
            "get/list nodes",
            "create/update configmaps (for rollback data)"
        ],
        "restrictions": "Can optimize but cannot access billing data"
    },
    
    "Namespace User": {
        "description": "User with access to specific namespaces only",
        "example": "User with access to 5 out of 10 namespaces",
        "permissions": "NAMESPACE_SCOPED",
        "behavior": [
            "upid analyze cluster - shows only accessible namespaces",
            "upid analyze pod - works only for pods in accessible namespaces", 
            "upid optimize - can only optimize accessible resources",
            "Cost attribution - shows costs only for accessible resources"
        ]
    },
    
    "SaaS Team Member": {
        "description": "User in UPID SaaS platform",
        "permissions": "UPID_RBAC",
        "scoping": "Organization and team boundaries",
        "roles": ["Viewer", "Operator", "Admin", "Billing Admin"]
    }
}
```

### **9. When Commands Work Without --local Flag**

```python
# auth/command_resolution.py
class CommandAuthResolver:
    """
    Determines when UPID commands work without explicit authentication flags
    """
    
    async def should_use_local_auth(self, command_context: CommandContext) -> bool:
        """
        Determine if command should use local authentication automatically
        """
        # Explicit flags take precedence
        if command_context.has_flag("--local"):
            return True
        
        if command_context.has_flag("--cloud") or command_context.has_token():
            return False
        
        # Auto-detection logic
        detection_result = await self.detect_optimal_auth_method()
        
        return detection_result.should_use_local
    
    async def detect_optimal_auth_method(self) -> AuthMethodDetection:
        """
        Detect the optimal authentication method
        """
        # Check for local clusters first (highest priority)
        local_clusters = await self.detect_local_clusters()
        
        # Check for cloud clusters
        cloud_clusters = await self.detect_cloud_clusters()
        
        # Check for UPID tokens
        upid_token = self.check_upid_token()
        
        # Decision logic
        if local_clusters and not cloud_clusters:
            # Only local clusters available
            return AuthMethodDetection(
                should_use_local=True,
                reason="Only local clusters detected",
                detected_clusters=local_clusters
            )
        
        if cloud_clusters and not local_clusters:
            # Only cloud clusters available
            return AuthMethodDetection(
                should_use_local=False,
                reason="Only cloud clusters detected", 
                detected_clusters=cloud_clusters
            )
        
        if local_clusters and cloud_clusters:
            # Both available - prefer cloud if it's the current context
            current_context = await self.get_current_kubectl_context()
            
            for cluster in cloud_clusters:
                if cluster.context_name == current_context:
                    return AuthMethodDetection(
                        should_use_local=False,
                        reason="Current kubectl context is cloud cluster",
                        detected_clusters=cloud_clusters
                    )
            
            # Fallback to local
            return AuthMethodDetection(
                should_use_local=True,
                reason="Local cluster preferred when both available",
                detected_clusters=local_clusters
            )
        
        # No clusters detected
        if upid_token:
            return AuthMethodDetection(
                should_use_local=False,
                reason="No local clusters, using UPID SaaS",
                requires_saas_auth=True
            )
        
        # Nothing detected - prompt user
        return AuthMethodDetection(
            should_use_local=False,
            reason="No clusters detected, authentication required",
            requires_setup=True
        )

# Command behavior matrix
COMMAND_AUTH_MATRIX = {
    "Local Cluster Only": {
        "docker-desktop": "Auto-detect, no --local flag needed",
        "minikube": "Auto-detect, no --local flag needed", 
        "k3s": "Auto-detect, no --local flag needed",
        "kind": "Auto-detect, no --local flag needed"
    },
    
    "Cloud Cluster Only": {
        "eks_with_aws_cli": "Auto-detect, no flags needed",
        "gke_with_gcloud": "Auto-detect, no flags needed",
        "aks_with_az_cli": "Auto-detect, no flags needed"
    },
    
    "Mixed Environment": {
        "local + cloud": "Prefer current kubectl context",
        "multiple_cloud": "Use current kubectl context",
        "no_current_context": "Prompt user to select"
    },
    
    "SaaS Mode": {
        "no_local_clusters": "Auto-redirect to SaaS authentication",
        "upid_token_set": "Use SaaS mode automatically",
        "explicit_saas": "Use --saas flag"
    }
}
```

### **10. Complete CLI Usage Examples**

```bash
# Different authentication scenarios and when they work automatically

# 1. Local Development (works without any flags)
$ upid analyze pod nginx-123
# Auto-detects docker-desktop/minikube and uses local auth

# 2. Cloud Cluster with Configured kubectl (works without flags)
$ aws eks update-kubeconfig --name my-cluster --region us-west-2
$ upid analyze deployment frontend
# Auto-detects EKS cluster and uses AWS credentials

# 3. GKE with gcloud (works without flags)
$ gcloud container clusters get-credentials my-cluster --zone us-central1-a
$ upid analyze cluster
# Auto-detects GKE cluster and uses gcloud credentials

# 4. Multiple clusters - uses current context
$ kubectl config use-context production-cluster
$ upid analyze pod api-service
# Uses production-cluster context automatically

# 5. Force local mode
$ upid analyze pod nginx-123 --local
# Forces local authentication even if cloud clusters are available

# 6. Force cloud mode
$ upid analyze pod nginx-123 --cloud
# Forces cloud authentication even if local clusters are available

# 7. SaaS mode with token
$ export UPID_TOKEN="your-token-here"
$ upid analyze pod nginx-123
# Uses SaaS mode automatically

# 8. SaaS mode with login
$ upid login
$ upid analyze deployment api
# Token stored after login, uses SaaS mode

# 9. Namespace-scoped user
$ upid analyze cluster
# Shows only namespaces user has access to:
# ✅ frontend (accessible)
# ✅ backend (accessible) 
# ✅ monitoring (accessible)
# ❌ admin (no access)
# ❌ kube-system (no access)

# 10. Mixed environment disambiguation
$ upid analyze pod nginx-123
# If both local and cloud available:
# "Multiple clusters detected. Using current kubectl context: gke_project_zone_cluster"
# "To use local cluster instead, run: upid analyze pod nginx-123 --local"
```

This comprehensive architecture and implementation guide provides your team with everything needed to build UPID with universal authentication, intelligent cloud detection, proper RBAC enforcement, and seamless user experience across all Kubernetes environments.    def initialize_collectors(self) -> List[MetricsCollector]:
        """
        Initialize appropriate metrics collectors based on cluster capabilities
        """
        collectors = []
        
        # Core Kubernetes API collector (always available)
        collectors.append(KubernetesAPICollector(self.cluster_info))
        
        # Metrics Server collector (if available)
        if self.cluster_info.has_metrics_server:
            collectors.append(MetricsServerCollector(self.cluster_info))
        
        # Prometheus collector (if available)
        if self.cluster_info.has_prometheus:
            collectors.append(PrometheusCollector(self.cluster_info))
        
        # Cloud-specific collectors
        if self.cluster_info.cloud_provider == "aws":
            collectors.append(AWSCloudWatchCollector(self.cluster_info))
        elif self.cluster_info.cloud_provider == "gcp":
            collectors.append(GCPMonitoringCollector(self.cluster_info))
        elif self.cluster_info.cloud_provider == "azure":
            collectors.append(AzureMonitorCollector(self.cluster_info))
        
        # Kubelet collector (direct node access)
        collectors.append(KubeletCollector(self.cluster_info))
        
        return collectors
    
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect comprehensive pod metrics from all available sources
        """
        metrics_tasks = []
        
        for collector in self.collectors:
            if collector.supports_pod_metrics():
                task = collector.collect_pod_metrics(pod_id, time_range)
                metrics_tasks.append(task)
        
        # Collect from all sources in parallel
        metrics_results = await asyncio.gather(*metrics_tasks, return_exceptions=True)
        
        # Merge metrics from all successful collectors
        merged_metrics = PodMetrics()
        
        for i, result in enumerate(metrics_results):
            if isinstance(result, Exception):
                logger.warning(f"Collector {self.collectors[i]} failed: {result}")
                continue
            
            merged_metrics = self.merge_pod_metrics(merged_metrics, result)
        
        # Enhance with business metrics
        business_metrics = await self.collect_business_metrics(pod_id, time_range)
        merged_metrics.business_data = business_metrics
        
        return merged_metrics

class KubernetesAPICollector:
    """
    Collect metrics using core Kubernetes APIs (always available)
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.k8s_client = cluster_info.k8s_client
        
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect pod metrics from Kubernetes API
        """
        # Get pod information
        pod = await self.k8s_client.read_namespaced_pod(
            name=pod_id.name, 
            namespace=pod_id.namespace
        )
        
        # Get pod events
        events = await self.k8s_client.list_namespaced_event(
            namespace=pod_id.namespace,
            field_selector=f"involvedObject.name={pod_id.name}"
        )
        
        # Get resource requests and limits
        resources = self.extract_resource_specs(pod)
        
        # Get pod logs for request analysis
        logs = await self.collect_pod_logs(pod_id, time_range)
        
        return PodMetrics(
            pod_id=pod_id,
            resource_requests=resources.requests,
            resource_limits=resources.limits,
            events=[self.convert_event(e) for e in events.items],
            logs=logs,
            collection_source="kubernetes_api",
            timestamp=datetime.utcnow()
        )
    
    async def collect_pod_logs(self, pod_id: PodIdentifier, 
                             time_range: TimeRange) -> List[LogEntry]:
        """
        Collect pod logs for business activity analysis
        """
        try:
            # Calculate log lines to fetch (estimate)
            duration_hours = (time_range.end - time_range.start).total_seconds() / 3600
            estimated_lines = min(10000, int(duration_hours * 1000))  # ~1000 lines/hour max
            
            # Fetch logs
            log_response = await self.k8s_client.read_namespaced_pod_log(
                name=pod_id.name,
                namespace=pod_id.namespace,
                tail_lines=estimated_lines,
                timestamps=True
            )
            
            # Parse logs into structured format
            return self.parse_logs(log_response, time_range)
            
        except Exception as e:
            logger.warning(f"Failed to collect logs for {pod_id}: {e}")
            return []
    
    def parse_logs(self, log_text: str, time_range: TimeRange) -> List[LogEntry]:
        """
        Parse pod logs to extract request information
        """
        log_entries = []
        
        for line in log_text.split('\n'):
            if not line.strip():
                continue
                
            try:
                # Extract timestamp and message
                timestamp_str, message = line.split(' ', 1)
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                # Filter by time range
                if timestamp < time_range.start or timestamp > time_range.end:
                    continue
                
                # Parse HTTP requests from common log formats
                request_info = self.extract_request_info(message)
                
                log_entries.append(LogEntry(
                    timestamp=timestamp,
                    message=message,
                    request_info=request_info
                ))
                
            except Exception as e:
                # Skip malformed log lines
                continue
        
        return log_entries
    
    def extract_request_info(self, log_message: str) -> Optional[RequestInfo]:
        """
        Extract HTTP request information from log message
        """
        # Common log patterns
        patterns = [
            # Apache/Nginx style: "GET /api/users HTTP/1.1" 200 1234
            r'\"?([A-Z]+)\s+([^\s]+)\s+HTTP/[\d\.]+\"?\s+(\d+)\s+(\d+)',
            # Application logs: method=GET path=/api/users status=200
            r'method=([A-Z]+).*?path=([^\s]+).*?status=(\d+)',
            # JSON logs: {"method":"GET","path":"/api/users","status":200}
            r'\"method\":\"([A-Z]+)\".*?\"path\":\"([^\"]+)\".*?\"status\":(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_message)
            if match:
                method, path, status = match.groups()[:3]
                return RequestInfo(
                    method=method,
                    path=path,
                    status_code=int(status),
                    user_agent=self.extract_user_agent(log_message),
                    source_ip=self.extract_source_ip(log_message)
                )
        
        return None

class MetricsServerCollector:
    """
    Collect metrics from Kubernetes Metrics Server
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.metrics_client = cluster_info.metrics_client
        
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect current resource usage from metrics server
        """
        try:
            # Get current pod metrics
            pod_metrics = await self.metrics_client.list_namespaced_pod_metrics(
                namespace=pod_id.namespace
            )
            
            # Find metrics for our specific pod
            for pod_metric in pod_metrics.items:
                if pod_metric.metadata.name == pod_id.name:
                    return self.convert_metrics_server_data(pod_metric, pod_id)
            
            # Pod not found in metrics
            logger.warning(f"Pod {pod_id} not found in metrics server")
            return PodMetrics(pod_id=pod_id, collection_source="metrics_server")
            
        except Exception as e:
            logger.error(f"Failed to collect metrics server data: {e}")
            return PodMetrics(pod_id=pod_id, collection_source="metrics_server")
    
    def convert_metrics_server_data(self, metrics_data, pod_id: PodIdentifier) -> PodMetrics:
        """
        Convert metrics server data to UPID format
        """
        containers_metrics = []
        
        for container in metrics_data.containers:
            cpu_usage = self.parse_cpu_usage(container.usage.get('cpu', '0'))
            memory_usage = self.parse_memory_usage(container.usage.get('memory', '0'))
            
            containers_metrics.append(ContainerMetrics(
                name=container.name,
                cpu_usage_cores=cpu_usage,
                memory_usage_bytes=memory_usage,
                timestamp=datetime.utcnow()
            ))
        
        return PodMetrics(
            pod_id=pod_id,
            containers=containers_metrics,
            collection_source="metrics_server",
            timestamp=datetime.utcnow()
        )

class PrometheusCollector:
    """
    Collect metrics from Prometheus (if available)
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.prometheus_url = self.discover_prometheus_endpoint()
        
    async def collect_pod_metrics(self, pod_id: PodIdentifier, 
                                time_range: TimeRange) -> PodMetrics:
        """
        Collect historical metrics from Prometheus
        """
        queries = {
            'cpu_usage': f'rate(container_cpu_usage_seconds_total{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}[5m])',
            'memory_usage': f'container_memory_usage_bytes{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}',
            'network_rx': f'rate(container_network_receive_bytes_total{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}[5m])',
            'network_tx': f'rate(container_network_transmit_bytes_total{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}[5m])',
            'fs_usage': f'container_fs_usage_bytes{{pod="{pod_id.name}",namespace="{pod_id.namespace}"}}'
        }
        
        # Execute queries in parallel
        query_tasks = []
        for metric_name, query in queries.items():
            task = self.execute_prometheus_query(query, time_range)
            query_tasks.append((metric_name, task))
        
        # Collect results
        metrics_data = {}
        for metric_name, task in query_tasks:
            try:
                result = await task
                metrics_data[metric_name] = result
            except Exception as e:
                logger.warning(f"Prometheus query failed for {metric_name}: {e}")
                metrics_data[metric_name] = []
        
        return self.convert_prometheus_data(metrics_data, pod_id)
    
    async def execute_prometheus_query(self, query: str, 
                                     time_range: TimeRange) -> List[PrometheusDataPoint]:
        """
        Execute Prometheus range query
        """
        params = {
            'query': query,
            'start': time_range.start.timestamp(),
            'end': time_range.end.timestamp(),
            'step': '60s'  # 1-minute resolution
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.prometheus_url}/api/v1/query_range", 
                                 params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_prometheus_response(data)
                else:
                    raise Exception(f"Prometheus query failed: {response.status}")
    
    def discover_prometheus_endpoint(self) -> str:
        """
        Auto-discover Prometheus endpoint
        """
        # Common Prometheus service names and namespaces
        prometheus_services = [
            ("prometheus-server", "monitoring"),
            ("prometheus-server", "prometheus"),
            ("prometheus", "monitoring"),
            ("prometheus", "kube-system"),
            ("prometheus-operator-prometheus", "monitoring")
        ]
        
        for service_name, namespace in prometheus_services:
            try:
                service = self.cluster_info.k8s_client.read_namespaced_service(
                    name=service_name, namespace=namespace
                )
                
                # Construct URL
                port = service.spec.ports[0].port
                return f"http://{service_name}.{namespace}.svc.cluster.local:{port}"
                
            except Exception:
                continue
        
        # Default fallback
        return "http://prometheus-server.monitoring.svc.cluster.local:80"

class BusinessMetricsCollector:
    """
    Collect business-relevant metrics from application logs and external sources
    """
    
    def __init__(self):
        self.request_patterns = self.compile_request_patterns()
        
    async def collect_business_metrics(self, pod_id: PodIdentifier, 
                                     time_range: TimeRange) -> BusinessMetrics:
        """
        Analyze logs to extract business activity metrics
        """
        # Get pod logs
        logs = await self.get_pod_logs(pod_id, time_range)
        
        # Analyze request patterns
        requests = self.extract_requests_from_logs(logs)
        
        # Filter business requests
        business_requests = self.filter_business_requests(requests)
        
        # Calculate business metrics
        return BusinessMetrics(
            total_requests=len(requests),
            business_requests=len(business_requests),
            business_request_ratio=len(business_requests) / max(len(requests), 1),
            request_patterns=self.analyze_request_patterns(business_requests),
            revenue_indicators=self.extract_revenue_indicators(business_requests),
            user_activity=self.analyze_user_activity(business_requests)
        )
    
    def filter_business_requests(self, requests: List[RequestInfo]) -> List[RequestInfo]:
        """
        Filter out non-business requests (health checks, monitoring, etc.)
        """
        business_requests = []
        
        for request in requests:
            if self.is_business_request(request):
                business_requests.append(request)
        
        return business_requests
    
    def is_business_request(self, request: RequestInfo) -> bool:
        """
        Determine if request represents actual business activity
        """
        # Filter out health checks
        health_check_paths = [
            '/health', '/ping', '/status', '/ready', '/live',
            '/healthz', '/readiness', '/liveness', '/metrics'
        ]
        
        if request.path.lower() in health_check_paths:
            return False
        
        # Filter out monitoring systems
        monitoring_user_agents = [
            'kube-probe', 'prometheus', 'grafana',
            'datadog', 'newrelic', 'pingdom'
        ]
        
        if request.user_agent:
            for agent in monitoring_user_agents:
                if agent.lower() in request.user_agent.lower():
                    return False
        
        # Filter out load balancer health checks
        lb_user_agents = [
            'ELB-HealthChecker', 'GoogleHC', 'Azure-HealthCheck',
            'kube-proxy', 'ingress-nginx'
        ]
        
        if request.user_agent:
            for agent in lb_user_agents:
                if agent in request.user_agent:
                    return False
        
        # Filter out internal service calls (heuristic)
        if request.user_agent and 'go-http-client' in request.user_agent:
            return False
        
        # This is likely a business request
        return True
```

### **4. Cloud Provider Billing Integration**

```python
# billing/cloud_billing.py
class CloudBillingIntegrator:
    """
    Universal cloud billing integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.billing_client = self.initialize_billing_client()
        
    def initialize_billing_client(self):
        """
        Initialize appropriate billing client based on cloud provider
        """
        if self.cluster_info.cloud_provider == "aws":
            return AWSBillingClient(self.cluster_info)
        elif self.cluster_info.cloud_provider == "gcp":
            return GCPBillingClient(self.cluster_info)
        elif self.cluster_info.cloud_provider == "azure":
            return AzureBillingClient(self.cluster_info)
        else:
            return GenericBillingClient(self.cluster_info)
    
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get actual cluster costs from cloud provider
        """
        return await self.billing_client.get_cluster_costs(time_range)

class AWSBillingClient:
    """
    AWS Cost Explorer integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.cost_explorer = boto3.client('ce', region_name=cluster_info.region)
        self.ec2_client = boto3.client('ec2', region_name=cluster_info.region)
        
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get EKS cluster costs from AWS Cost Explorer
        """
        # Get cluster node group information
        node_groups = await self.get_cluster_node_groups()
        
        # Build cost filter for cluster resources
        cost_filter = self.build_cluster_cost_filter(node_groups)
        
        # Query Cost Explorer
        response = await self.query_cost_explorer(cost_filter, time_range)
        
        # Parse and structure cost data
        return self.parse_aws_cost_response(response, node_groups)
    
    async def get_cluster_node_groups(self) -> List[NodeGroup]:
        """
        Get EKS cluster node groups and their instances
        """
        node_groups = []
        
        # Get cluster nodes
        nodes = await self.cluster_info.k8s_client.list_node()
        
        for node in nodes.items:
            # Extract AWS instance information from node
            instance_id = self.extract_instance_id(node)
            instance_type = self.extract_instance_type(node)
            availability_zone = self.extract_availability_zone(node)
            
            if instance_id:
                # Get instance details from EC2
                instance_details = await self.get_instance_details(instance_id)
                
                node_groups.append(NodeGroup(
                    node_name=node.metadata.name,
                    instance_id=instance_id,
                    instance_type=instance_type,
                    availability_zone=availability_zone,
                    instance_details=instance_details
                ))
        
        return node_groups
    
    def extract_instance_id(self, node) -> str:
        """
        Extract EC2 instance ID from Kubernetes node
        """
        # Check node annotations and labels
        if 'node.kubernetes.io/instance-id' in node.metadata.annotations:
            return node.metadata.annotations['node.kubernetes.io/instance-id']
        
        # Parse from provider ID
        provider_id = getattr(node.spec, 'provider_id', '')
        if provider_id.startswith('aws:///'):
            return provider_id.split('/')[-1]
        
        return None
    
    async def query_cost_explorer(self, cost_filter: dict, 
                                time_range: TimeRange) -> dict:
        """
        Query AWS Cost Explorer API
        """
        # Convert time range to AWS format
        start_date = time_range.start.strftime('%Y-%m-%d')
        end_date = time_range.end.strftime('%Y-%m-%d')
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}
                ],
                Filter=cost_filter
            )
        )
        
        return response
    
    def build_cluster_cost_filter(self, node_groups: List[NodeGroup]) -> dict:
        """
        Build Cost Explorer filter for cluster resources
        """
        # Get all instance IDs in cluster
        instance_ids = [ng.instance_id for ng in node_groups if ng.instance_id]
        
        if not instance_ids:
            # Fallback to cluster tag filter
            return {
                'Tags': {
                    'Key': 'kubernetes.io/cluster/' + self.cluster_info.cluster_name,
                    'Values': ['owned', 'shared']
                }
            }
        
        # Filter by instance IDs
        return {
            'Dimensions': {
                'Key': 'RESOURCE_ID',
                'Values': instance_ids
            }
        }

class GCPBillingClient:
    """
    GCP Cloud Billing integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.billing_client = self.initialize_gcp_billing()
        
    def initialize_gcp_billing(self):
        """
        Initialize GCP billing client
        """
        from google.cloud import billing_v1
        return billing_v1.CloudBillingClient()
    
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get GKE cluster costs from GCP Billing API
        """
        # Get cluster node information
        nodes = await self.get_cluster_nodes()
        
        # Build billing query
        query = self.build_gcp_billing_query(nodes, time_range)
        
        # Execute billing query
        response = await self.execute_billing_query(query)
        
        # Parse response
        return self.parse_gcp_billing_response(response, nodes)
    
    def build_gcp_billing_query(self, nodes: List[dict], 
                               time_range: TimeRange) -> dict:
        """
        Build GCP billing query for cluster resources
        """
        # Extract instance names from nodes
        instance_names = []
        for node in nodes:
            instance_name = self.extract_gcp_instance_name(node)
            if instance_name:
                instance_names.append(instance_name)
        
        return {
            'project_id': self.cluster_info.project_id,
            'time_range': {
                'start_time': time_range.start.isoformat(),
                'end_time': time_range.end.isoformat()
            },
            'filter': f'service.description="Compute Engine" AND resource.labels.instance_name=("{"|".join(instance_names)}")'
        }

class AzureBillingClient:
    """
    Azure Cost Management integration
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.cost_client = self.initialize_azure_cost_client()
        
    async def get_cluster_costs(self, time_range: TimeRange) -> ClusterCostBreakdown:
        """
        Get AKS cluster costs from Azure Cost Management API
        """
        # Get cluster resource group and node resource group
        resource_groups = await self.get_cluster_resource_groups()
        
        # Build cost query
        query = self.build_azure_cost_query(resource_groups, time_range)
        
        # Execute cost query
        response = await self.execute_azure_cost_query(query)
        
        # Parse response
        return self.parse_azure_cost_response(response, resource_groups)

# Cost attribution engine
class CostAttributionEngine:
    """
    Attribute cloud costs to specific pods and workloads
    """
    
    def __init__(self, billing_client: CloudBillingClient):
        self.billing_client = billing_client
        
    async def calculate_pod_cost(self, pod_id: PodIdentifier, 
                               pod_metrics: PodMetrics,
                               time_range: TimeRange) -> PodCostBreakdown:
        """
        Calculate precise cost attribution for a pod
        """
        # Get cluster costs
        cluster_costs = await self.billing_client.get_cluster_costs(time_range)
        
        # Get pod's node
        pod_node = await self.get_pod_node(pod_id)
        
        # Get node costs
        node_costs = cluster_costs.get_node_costs(pod_node.name)
        
        # Calculate pod's resource allocation ratio
        allocation_ratio = self.calculate_allocation_ratio(pod_metrics, pod_node)
        
        # Calculate pod costs
        return PodCostBreakdown(
            pod_id=pod_id,
            node_name=pod_node.name,
            hourly_cost=node_costs.hourly_cost * allocation_ratio,
            daily_cost=node_costs.daily_cost * allocation_ratio,
            monthly_projection=node_costs.monthly_cost * allocation_ratio,
            allocation_ratio=allocation_ratio,
            cost_drivers=self.identify_cost_drivers(pod_metrics, node_costs)
        )
    
    def calculate_allocation_ratio(self, pod_metrics: PodMetrics, 
                                 node: NodeInfo) -> float:
        """
        Calculate pod's fair share of node costs
        """
        # CPU allocation ratio
        cpu_ratio = pod_metrics.cpu_request / node.allocatable_cpu
        
        # Memory allocation ratio  
        memory_ratio = pod_metrics.memory_request / node.allocatable_memory
        
        # Weighted average (CPU typically more expensive)
        weighted_ratio = (cpu_ratio * 0.6) + (memory_ratio * 0.4)
        
        return min(weighted_ratio, 1.0)  # Cap at 100%
```

### **5. Implementation Plan & Timeline**

```python
# implementation/plan.py
IMPLEMENTATION_PHASES = {
    "Phase 1: Foundation (Weeks 1-4)": {
        "Week 1": {
            "Universal Authentication System": [
                "Implement LocalKubernetesDetector",
                "Implement CloudKubernetesDetector", 
                "Create UniversalAuthenticator",
                "Add auto-detection for docker-desktop, minikube, k3s, kind"
            ],
            "Core Kubernetes Integration": [
                "Create KubernetesAPICollector",
                "Implement cluster capabilities detection",
                "Add RBAC permission checking",
                "Test with local clusters"
            ]
        },
        "Week 2": {
            "Cloud Provider Detection": [
                "Implement EKS detection and authentication",
                "Implement GKE detection and authentication", 
                "Implement AKS detection and authentication",
                "Add cloud credentials validation"
            ],
            "Metrics Collection": [
                "Create MetricsServerCollector",
                "Implement KubeletCollector",
                "Add PrometheusCollector (if available)",
                "Create unified metrics interface"
            ]
        },
        "Week 3": {
            "Billing Integration": [
                "Implement AWS Cost Explorer client",
                "Implement GCP Billing API client",
                "Implement Azure Cost Management client",
                "Create cost attribution engine"
            ],
            "Database Foundation": [
                "Set up TimescaleDB for time-series data",
                "Create PostgreSQL for metadata",
                "Implement data models and schemas",
                "Add data compression and partitioning"
            ]
        },
        "Week 4": {
            "Basic CLI Commands": [
                "Implement 'upid analyze pod' command",
                "Implement 'upid analyze deployment' command",
                "Implement 'upid analyze cluster' command", 
                "Add authentication flow to CLI"
            ],
            "Testing & Validation": [
                "Test with local Kubernetes clusters",
                "Test with cloud Kubernetes clusters",
                "Validate cost calculations",
                "End-to-end testing"
            ]
        }
    },
    
    "Phase 2: Intelligence (Weeks 5-8)": {
        "Week 5": {
            "Pod Idle Detection": [
                "Implement multi-factor idle detection algorithm",
                "Add business request filtering",
                "Create confidence scoring system",
                "Add pattern recognition"
            ],
            "Business Correlation": [
                "Implement log parsing for request extraction",
                "Add business activity correlation",
                "Create revenue attribution logic",
                "Add user impact scoring"
            ]
        },
        "Week 6": {
            "Advanced Analytics": [
                "Implement time-series analysis",
                "Add trend detection algorithms",
                "Create predictive modeling",
                "Add anomaly detection"
            ],
            "Cost Optimization": [
                "Implement resource rightsizing recommendations",
                "Add waste identification algorithms",
                "Create optimization priority scoring",
                "Add ROI calculation engine"
            ]
        },
        "Week 7": {
            "Zero Pod Scaling": [
                "Implement zero-pod scaling engine",
                "Add safety validation system",
                "Create rollback mechanisms",
                "Add traffic monitoring"
            ],
            "Optimization Safety": [
                "Implement comprehensive safety checks",
                "Add dependency analysis",
                "Create impact assessment",
                "Add approval workflows"
            ]
        },
        "Week 8": {
            "Enhanced CLI Experience": [
                "Add intelligent auto-completion",
                "Implement real-time dashboard",
                "Create interactive optimization mode",
                "Add progress indicators and feedback"
            ],
            "Integration Testing": [
                "Test optimization workflows",
                "Validate safety mechanisms",
                "Performance testing",
                "Security testing"
            ]
        }
    },
    
    "Phase 3: Production (Weeks 9-12)": {
        "Week 9": {
            "Multi-tenancy & RBAC": [
                "Implement UPID RBAC system",
                "Add organization and team management",
                "Create fine-grained permissions",
                "Add audit logging"
            ],
            "FastAPI Backend": [
                "Create REST API endpoints",
                "Implement WebSocket for real-time data",
                "Add API authentication and authorization",
                "Create API documentation"
            ]
        },
        "Week 10": {
            "Performance Optimization": [
                "Optimize database queries",
                "Implement caching layers",
                "Add connection pooling",
                "Performance tuning"
            ],
            "Monitoring & Observability": [
                "Add Prometheus metrics",
                "Implement structured logging",
                "Create health checks",
                "Add error tracking"
            ]
        # UPID Complete Architecture & Implementation Guide

## 🏗️ **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                UPID PLATFORM                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           CLI Interface Layer                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Local Mode    │  │  Authenticated  │  │   SaaS Mode     │                │
│  │ (no auth req'd) │  │   CLI Mode      │  │ (web dashboard) │                │
│  │ Docker Desktop  │  │  EKS/GKE/AKS   │  │ Multi-tenant    │                │
│  │ minikube, k3s   │  │    kubectl      │  │    Portal       │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Authentication & Authorization Layer                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Auto-Detect    │  │   K8s RBAC      │  │   UPID RBAC     │                │
│  │  - Local K8s    │  │  - ServiceAcct  │  │  - Multi-tenant │                │
│  │  - Cloud Config │  │  - Namespace    │  │  - Org/Team     │                │
│  │  - No Auth      │  │  - ClusterRole  │  │  - Custom Perms │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           Core Intelligence Engine                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Metrics        │  │   Analysis      │  │  Optimization   │                │
│  │  Collection     │  │   Engine        │  │   Engine        │                │
│  │                 │  │                 │  │                 │                │
│  │ • Pod Metrics   │  │ • Idle Detection│  │ • Resource Opt  │                │
│  │ • Node Metrics  │  │ • Cost Analysis │  │ • Zero Scaling  │                │
│  │ • Business Logs │  │ • Pattern ML    │  │ • Safety Checks │                │
│  │ • Request Data  │  │ • Confidence    │  │ • Rollback      │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Data Storage & Processing Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Time-Series    │  │   Metadata      │  │   Cache Layer   │                │
│  │   Database      │  │   Database      │  │                 │                │
│  │                 │  │                 │  │                 │                │
│  │ • TimescaleDB   │  │ • PostgreSQL    │  │ • Redis         │                │
│  │ • 90-day data   │  │ • User/Tenant   │  │ • Query Cache   │                │
│  │ • Compression   │  │ • RBAC Rules    │  │ • Session Store │                │
│  │ • Partitioning  │  │ • Audit Logs    │  │ • Rate Limiting │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                      Cloud Provider Integration Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │      AWS        │  │      GCP        │  │     Azure       │                │
│  │                 │  │                 │  │                 │                │
│  │ • Cost Explorer │  │ • Billing API   │  │ • Cost Mgmt API │                │
│  │ • EKS Detection │  │ • GKE Detection │  │ • AKS Detection │                │
│  │ • EC2 Pricing   │  │ • GCE Pricing   │  │ • VM Pricing    │                │
│  │ • IAM Roles     │  │ • IAM Binding   │  │ • RBAC          │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                        Kubernetes Integration Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │  Cluster Auto   │  │   Metrics API   │  │   Resource API  │                │
│  │   Detection     │  │                 │  │                 │                │
│  │                 │  │                 │  │                 │                │
│  │ • EKS/GKE/AKS   │  │ • metrics.k8s   │  │ • Core API      │                │
│  │ • Local K8s     │  │ • Prometheus    │  │ • Apps API      │                │
│  │ • Cloud Labels  │  │ • cAdvisor      │  │ • Custom Rsrc   │                │
│  │ • Node Metadata │  │ • Kubelet       │  │ • Events API    │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Flow Diagram                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  User Command: upid analyze pod nginx-123                                      │
│       │                                                                        │
│       ▼                                                                        │
│  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│  │   Auth Check    │────────▶│  Cluster Detect │────────▶│ Permission Check│  │
│  │                 │         │                 │         │                 │  │
│  │ • Local detect  │         │ • Cloud provider│         │ • Namespace     │  │
│  │ • Cloud config  │         │ • K8s version   │         │ • Resource      │  │
│  │ • UPID token    │         │ • Node labels   │         │ • Action        │  │
│  └─────────────────┘         └─────────────────┘         └─────────────────┘  │
│       │                             │                             │            │
│       ▼                             ▼                             ▼            │
│  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐  │
│  │  Metrics Fetch  │────────▶│   Cost Fetch    │────────▶│   Intelligence  │  │
│  │                 │         │                 │         │    Analysis     │  │
│  │ • Pod metrics   │         │ • Cloud billing │         │                 │  │
│  │ • Node metrics  │         │ • Instance costs│         │ • Idle detect   │  │
│  │ • Request logs  │         │ • Pricing APIs  │         │ • Cost calc     │  │
│  │ • Business data │         │ • Usage data    │         │ • Optimization  │  │
│  └─────────────────┘         └─────────────────┘         └─────────────────┘  │
│       │                             │                             │            │
│       ▼                             ▼                             ▼            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                        Response Generation                               │  │
│  │                                                                         │  │
│  │  • Confidence scoring                                                   │  │
│  │  • Actionable recommendations                                           │  │
│  │  • Cost savings calculations                                            │  │
│  │  • Risk assessment                                                      │  │
│  │  • Next steps suggestions                                               │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                          │
│                                     ▼                                          │
│                           CLI/Dashboard Output                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **Major Features Architecture**

### **1. Universal Authentication & Multi-Tenancy**

```python
# auth/universal_auth.py
class UniversalAuthenticator:
    """
    Handles all authentication scenarios automatically
    """
    
    def __init__(self):
        self.local_detector = LocalKubernetesDetector()
        self.cloud_detector = CloudKubernetesDetector()
        self.rbac_enforcer = RBACEnforcer()
        
    async def authenticate_user(self, context: CommandContext) -> AuthResult:
        """
        Universal authentication flow
        """
        # Step 1: Detect environment
        env_info = await self.detect_environment()
        
        # Step 2: Choose authentication strategy
        if env_info.is_local_cluster:
            return await self.authenticate_local(env_info)
        elif env_info.has_cloud_config:
            return await self.authenticate_cloud(env_info)
        else:
            return await self.authenticate_upid_saas(context)
    
    async def detect_environment(self) -> EnvironmentInfo:
        """
        Auto-detect Kubernetes environment
        """
        # Check for local clusters first
        local_info = await self.local_detector.detect()
        if local_info.detected:
            return EnvironmentInfo(
                is_local_cluster=True,
                cluster_type=local_info.cluster_type,  # docker-desktop, minikube, k3s, kind
                kubeconfig_path=local_info.kubeconfig_path,
                auth_required=False
            )
        
        # Check for cloud clusters
        cloud_info = await self.cloud_detector.detect()
        if cloud_info.detected:
            return EnvironmentInfo(
                is_local_cluster=False,
                cluster_type=cloud_info.cluster_type,  # eks, gke, aks
                cloud_provider=cloud_info.provider,
                kubeconfig_path=cloud_info.kubeconfig_path,
                auth_required=cloud_info.auth_required
            )
        
        # No cluster detected - prompt for UPID SaaS
        return EnvironmentInfo(
            is_local_cluster=False,
            cluster_type="unknown",
            auth_required=True,
            requires_setup=True
        )

class LocalKubernetesDetector:
    """
    Detect local Kubernetes environments
    """
    
    async def detect(self) -> LocalDetectionResult:
        """
        Detect local Kubernetes clusters
        """
        detectors = [
            self.detect_docker_desktop,
            self.detect_minikube,
            self.detect_k3s,
            self.detect_kind,
            self.detect_microk8s
        ]
        
        for detector in detectors:
            result = await detector()
            if result.detected:
                return result
        
        return LocalDetectionResult(detected=False)
    
    async def detect_docker_desktop(self) -> LocalDetectionResult:
        """
        Detect Docker Desktop Kubernetes
        """
        try:
            # Check kubeconfig for docker-desktop context
            config = await self.load_kubeconfig()
            
            for context in config.contexts:
                if 'docker-desktop' in context.name.lower():
                    # Test connection
                    if await self.test_connection(context):
                        return LocalDetectionResult(
                            detected=True,
                            cluster_type="docker-desktop",
                            context_name=context.name,
                            kubeconfig_path=config.path,
                            requires_auth=False,
                            local_access=True
                        )
        except Exception as e:
            logger.debug(f"Docker Desktop detection failed: {e}")
        
        return LocalDetectionResult(detected=False)
    
    async def detect_minikube(self) -> LocalDetectionResult:
        """
        Detect Minikube cluster
        """
        try:
            # Check if minikube command exists
            result = subprocess.run(['minikube', 'status'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and 'Running' in result.stdout:
                # Get minikube kubeconfig
                kubeconfig_path = subprocess.run(
                    ['minikube', 'config', 'view', 'kubeconfig'],
                    capture_output=True, text=True
                ).stdout.strip()
                
                return LocalDetectionResult(
                    detected=True,
                    cluster_type="minikube",
                    context_name="minikube",
                    kubeconfig_path=kubeconfig_path,
                    requires_auth=False,
                    local_access=True
                )
        except Exception as e:
            logger.debug(f"Minikube detection failed: {e}")
        
        return LocalDetectionResult(detected=False)
    
    async def detect_k3s(self) -> LocalDetectionResult:
        """
        Detect K3s cluster
        """
        try:
            # Check for K3s kubeconfig
            k3s_config_paths = [
                '/etc/rancher/k3s/k3s.yaml',
                os.path.expanduser('~/.kube/k3s-config'),
                os.path.expanduser('~/.k3s/config')
            ]
            
            for config_path in k3s_config_paths:
                if os.path.exists(config_path):
                    if await self.test_k3s_connection(config_path):
                        return LocalDetectionResult(
                            detected=True,
                            cluster_type="k3s",
                            context_name="default",
                            kubeconfig_path=config_path,
                            requires_auth=False,
                            local_access=True
                        )
        except Exception as e:
            logger.debug(f"K3s detection failed: {e}")
        
        return LocalDetectionResult(detected=False)

class CloudKubernetesDetector:
    """
    Detect cloud-managed Kubernetes clusters
    """
    
    async def detect(self) -> CloudDetectionResult:
        """
        Detect cloud Kubernetes clusters
        """
        detectors = [
            self.detect_eks,
            self.detect_gke,
            self.detect_aks,
            self.detect_openshift
        ]
        
        for detector in detectors:
            result = await detector()
            if result.detected:
                return result
        
        return CloudDetectionResult(detected=False)
    
    async def detect_eks(self) -> CloudDetectionResult:
        """
        Detect Amazon EKS cluster
        """
        try:
            # Check current kubeconfig context
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            if current_context and 'eks' in current_context.lower():
                # Parse EKS cluster info from context
                cluster_info = await self.parse_eks_context(current_context)
                
                # Test connection
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="eks",
                        cloud_provider="aws",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.region,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via AWS CLI
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"EKS detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
    
    async def detect_gke(self) -> CloudDetectionResult:
        """
        Detect Google GKE cluster
        """
        try:
            # Check for GKE context pattern
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            # GKE contexts usually follow pattern: gke_project_zone_cluster
            if current_context and current_context.startswith('gke_'):
                cluster_info = await self.parse_gke_context(current_context)
                
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="gke",
                        cloud_provider="gcp",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.zone,
                        project_id=cluster_info.project_id,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via gcloud
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"GKE detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
    
    async def detect_aks(self) -> CloudDetectionResult:
        """
        Detect Azure AKS cluster
        """
        try:
            config = await self.load_kubeconfig()
            current_context = config.current_context
            
            # Check if context uses Azure authentication
            context_config = await self.get_context_config(current_context)
            
            if self.is_azure_context(context_config):
                cluster_info = await self.parse_aks_context(current_context)
                
                if await self.test_connection(current_context):
                    return CloudDetectionResult(
                        detected=True,
                        cluster_type="aks",
                        cloud_provider="azure",
                        cluster_name=cluster_info.cluster_name,
                        region=cluster_info.region,
                        resource_group=cluster_info.resource_group,
                        context_name=current_context,
                        auth_required=False,  # Already authenticated via az CLI
                        cloud_credentials_available=True
                    )
        except Exception as e:
            logger.debug(f"AKS detection failed: {e}")
        
        return CloudDetectionResult(detected=False)
```

### **2. RBAC & Permission System**

```python
# auth/rbac_system.py
class RBACEnforcer:
    """
    Comprehensive RBAC enforcement for UPID
    """
    
    def __init__(self):
        self.k8s_rbac = KubernetesRBACAnalyzer()
        self.upid_rbac = UPIDRBACManager()
        
    async def check_permissions(self, user: AuthenticatedUser, 
                              action: Action, 
                              resource: Resource) -> PermissionResult:
        """
        Check if user has permission to perform action on resource
        """
        # For local clusters - allow all operations
        if user.auth_type == "local":
            return PermissionResult(
                allowed=True,
                reason="Local cluster access - full permissions"
            )
        
        # For cloud clusters - check Kubernetes RBAC
        if user.auth_type == "kubernetes":
            k8s_result = await self.k8s_rbac.check_permission(
                user.k8s_user, action, resource
            )
            
            if not k8s_result.allowed:
                return PermissionResult(
                    allowed=False,
                    reason=f"Kubernetes RBAC denied: {k8s_result.reason}",
                    required_permissions=k8s_result.required_permissions
                )
        
        # For UPID SaaS - check UPID RBAC
        if user.auth_type == "upid":
            upid_result = await self.upid_rbac.check_permission(
                user.upid_user, action, resource
            )
            
            if not upid_result.allowed:
                return PermissionResult(
                    allowed=False,
                    reason=f"UPID RBAC denied: {upid_result.reason}",
                    required_permissions=upid_result.required_permissions
                )
        
        return PermissionResult(allowed=True)

class KubernetesRBACAnalyzer:
    """
    Analyze and enforce Kubernetes RBAC permissions
    """
    
    async def check_permission(self, k8s_user: KubernetesUser, 
                             action: Action, 
                             resource: Resource) -> RBACResult:
        """
        Check Kubernetes RBAC permissions
        """
        # Get user's effective permissions
        permissions = await self.get_user_permissions(k8s_user)
        
        # Check namespace-level permissions
        if resource.namespace:
            namespace_perms = permissions.namespace_permissions.get(resource.namespace, [])
            if self.action_allowed(action, resource, namespace_perms):
                return RBACResult(
                    allowed=True,
                    source="namespace_rbac",
                    permissions_used=namespace_perms
                )
        
        # Check cluster-level permissions
        cluster_perms = permissions.cluster_permissions
        if self.action_allowed(action, resource, cluster_perms):
            return RBACResult(
                allowed=True,
                source="cluster_rbac", 
                permissions_used=cluster_perms
            )
        
        # Permission denied
        required_perms = self.get_required_permissions(action, resource)
        return RBACResult(
            allowed=False,
            reason=f"Missing permissions for {action.name} on {resource.type}",
            required_permissions=required_perms,
            available_namespaces=list(permissions.namespace_permissions.keys())
        )
    
    async def get_user_permissions(self, k8s_user: KubernetesUser) -> UserPermissions:
        """
        Get effective permissions for Kubernetes user
        """
        # Use Kubernetes SubjectAccessReview API to check permissions
        permissions = UserPermissions()
        
        # Check cluster-level permissions
        cluster_resources = ['nodes', 'persistentvolumes', 'clusterroles']
        for resource in cluster_resources:
            for verb in ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']:
                if await self.can_user_perform(k8s_user, verb, resource):
                    permissions.cluster_permissions.append(
                        Permission(verb=verb, resource=resource)
                    )
        
        # Check namespace-level permissions for each accessible namespace
        namespaces = await self.get_accessible_namespaces(k8s_user)
        
        for namespace in namespaces:
            ns_permissions = []
            namespace_resources = ['pods', 'deployments', 'services', 'configmaps']
            
            for resource in namespace_resources:
                for verb in ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']:
                    if await self.can_user_perform(k8s_user, verb, resource, namespace):
                        ns_permissions.append(
                            Permission(verb=verb, resource=resource, namespace=namespace)
                        )
            
            if ns_permissions:
                permissions.namespace_permissions[namespace] = ns_permissions
        
        return permissions
    
    async def get_accessible_namespaces(self, k8s_user: KubernetesUser) -> List[str]:
        """
        Get list of namespaces user has access to
        """
        accessible_namespaces = []
        
        # Get all namespaces
        all_namespaces = await self.k8s_client.list_namespaces()
        
        # Check access to each namespace
        for namespace in all_namespaces:
            if await self.can_user_perform(k8s_user, 'get', 'pods', namespace.name):
                accessible_namespaces.append(namespace.name)
        
        return accessible_namespaces
    
    async def can_user_perform(self, k8s_user: KubernetesUser, 
                             verb: str, resource: str, 
                             namespace: str = None) -> bool:
        """
        Check if user can perform specific action using SubjectAccessReview
        """
        try:
            # Create SubjectAccessReview
            review = client.V1SubjectAccessReview(
                spec=client.V1SubjectAccessReviewSpec(
                    user=k8s_user.username,
                    groups=k8s_user.groups,
                    resource_attributes=client.V1ResourceAttributes(
                        verb=verb,
                        resource=resource,
                        namespace=namespace
                    )
                )
            )
            
            # Submit review
            result = await self.k8s_client.create_subject_access_review(review)
            
            return result.status.allowed
            
        except Exception as e:
            logger.debug(f"Permission check failed: {e}")
            return False
    
    def get_required_permissions(self, action: Action, resource: Resource) -> List[Permission]:
        """
        Get required permissions for UPID actions
        """
        permission_map = {
            "analyze_pod": [
                Permission(verb="get", resource="pods"),
                Permission(verb="get", resource="nodes"),  # for cost calculation
                Permission(verb="list", resource="events")  # for analysis
            ],
            "analyze_deployment": [
                Permission(verb="get", resource="deployments"),
                Permission(verb="list", resource="pods"),
                Permission(verb="get", resource="replicasets")
            ],
            "optimize_pod": [
                Permission(verb="get", resource="pods"),
                Permission(verb="patch", resource="pods"),  # for resource updates
                Permission(verb="patch", resource="deployments")  # for scaling
            ],
            "zero_scale": [
                Permission(verb="get", resource="deployments"),
                Permission(verb="patch", resource="deployments"),  # for scaling to 0
                Permission(verb="create", resource="configmaps")  # for rollback data
            ]
        }
        
        return permission_map.get(action.name, [])

# UPID Custom RBAC for SaaS mode
class UPIDRBACManager:
    """
    UPID-specific RBAC for multi-tenant SaaS
    """
    
    def __init__(self):
        self.db = DatabaseManager()
    
    async def check_permission(self, upid_user: UPIDUser, 
                             action: Action, 
                             resource: Resource) -> RBACResult:
        """
        Check UPID-specific permissions
        """
        # Get user roles and permissions
        user_roles = await self.db.get_user_roles(upid_user.user_id)
        
        # Check organization-level permissions
        if resource.organization_id != upid_user.organization_id:
            return RBACResult(
                allowed=False,
                reason="Resource belongs to different organization"
            )
        
        # Check team-level permissions
        if resource.team_id and resource.team_id not in upid_user.team_ids:
            return RBACResult(
                allowed=False,
                reason="User not member of resource team"
            )
        
        # Check action permissions
        required_permission = self.get_required_upid_permission(action)
        
        for role in user_roles:
            if required_permission in role.permissions:
                return RBACResult(
                    allowed=True,
                    source="upid_rbac",
                    role_used=role.name
                )
        
        return RBACResult(
            allowed=False,
            reason=f"Missing permission: {required_permission}",
            required_permissions=[required_permission]
        )
    
    def get_required_upid_permission(self, action: Action) -> str:
        """
        Map UPID actions to permission strings
        """
        permission_map = {
            "analyze_pod": "upid:analyze:read",
            "analyze_deployment": "upid:analyze:read", 
            "analyze_cluster": "upid:analyze:read",
            "optimize_pod": "upid:optimize:execute",
            "zero_scale": "upid:optimize:execute",
            "view_costs": "upid:costs:read",
            "manage_users": "upid:admin:users",
            "manage_billing": "upid:admin:billing"
        }
        
        return permission_map.get(action.name, "upid:read")

# UPID RBAC Roles Definition
UPID_ROLES = {
    "viewer": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read"
        ],
        "description": "Read-only access to analysis and costs"
    },
    "operator": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read",
            "upid:optimize:execute"
        ],
        "description": "Can analyze and execute optimizations"
    },
    "admin": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read", 
            "upid:optimize:execute",
            "upid:admin:users",
            "upid:admin:settings"
        ],
        "description": "Full administrative access"
    },
    "billing_admin": {
        "permissions": [
            "upid:analyze:read",
            "upid:costs:read",
            "upid:admin:billing",
            "upid:admin:users"
        ],
        "description": "Billing and user management access"
    }
}
```

### **3. Metrics Collection Architecture**

```python
# metrics/collection_engine.py
class UniversalMetricsCollector:
    """
    Universal metrics collection that works with any Kubernetes cluster
    """
    
    def __init__(self, cluster_info: ClusterInfo):
        self.cluster_info = cluster_info
        self.collectors = self.initialize_collectors()
        
    def initialize_