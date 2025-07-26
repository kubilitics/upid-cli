#!/bin/bash

# UPID Demo - Monitoring Setup Script
# Sets up metrics-server and monitoring tools for comprehensive demo

set -e

echo "🔧 Setting up monitoring infrastructure for UPID demo..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    log_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

log_info "Connected to Kubernetes cluster successfully"

# Install metrics-server for resource monitoring
log_info "Installing metrics-server..."

# Check if metrics-server is already installed
if kubectl get deployment metrics-server -n kube-system &> /dev/null; then
    log_warning "metrics-server already exists in kube-system namespace"
else
    # Install metrics-server with insecure settings for demo
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        - --kubelet-insecure-tls
        - --kubelet-skip-tls-verify
        image: k8s.gcr.io/metrics-server/metrics-server:v0.6.1
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 3
          httpGet:
            path: /livez
            port: https
            scheme: HTTPS
          periodSeconds: 10
        name: metrics-server
        ports:
        - containerPort: 4443
          name: https
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          httpGet:
            path: /readyz
            port: https
            scheme: HTTPS
          initialDelaySeconds: 20
          periodSeconds: 10
        resources:
          requests:
            cpu: 100m
            memory: 200Mi
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
        volumeMounts:
        - mountPath: /tmp
          name: tmp-dir
      nodeSelector:
        kubernetes.io/os: linux
      priorityClassName: system-cluster-critical
      serviceAccountName: metrics-server
      volumes:
      - emptyDir: {}
        name: tmp-dir
---
apiVersion: v1
kind: Service
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: https
  selector:
    k8s-app: metrics-server
---
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
    rbac.authorization.k8s.io/aggregate-to-view: "true"
  name: system:aggregated-metrics-reader
rules:
- apiGroups:
  - metrics.k8s.io
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
rules:
- apiGroups:
  - ""
  resources:
  - nodes/metrics
  verbs:
  - get
- apiGroups:
  - ""
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server:system:auth-delegator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:metrics-server
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server-auth-reader
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: extension-apiserver-authentication-reader
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
EOF

    log_success "metrics-server installed successfully"
fi

# Wait for metrics-server to be ready
log_info "Waiting for metrics-server to be ready..."
kubectl wait --for=condition=ready pod -l k8s-app=metrics-server -n kube-system --timeout=120s

# Test metrics-server functionality
log_info "Testing metrics-server functionality..."
sleep 30  # Allow time for metrics collection

if kubectl top nodes &> /dev/null; then
    log_success "metrics-server is working correctly!"
    echo "Node metrics:"
    kubectl top nodes
    echo
else
    log_warning "metrics-server may need more time to collect metrics"
    log_info "You can test it later with: kubectl top nodes"
fi

# Create monitoring utilities
log_info "Creating monitoring utilities..."

# Create a monitoring script
cat > /tmp/monitor-resources.sh << 'EOF'
#!/bin/bash

echo "=== Kubernetes Resource Monitoring ==="
echo "Timestamp: $(date)"
echo

echo "🖥️  Node Resources:"
kubectl top nodes 2>/dev/null || echo "Metrics not ready yet"
echo

echo "📊 Pod Resources (Top 10):"
kubectl top pods --all-namespaces --sort-by=cpu 2>/dev/null | head -11 || echo "Pod metrics not ready yet"
echo

echo "🏷️  Pods by Namespace:"
for ns in $(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}'); do
    count=$(kubectl get pods -n $ns --no-headers 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "  $ns: $count pods"
    fi
done
echo

echo "💰 Resource Requests Summary:"
kubectl describe nodes | grep -A 5 "Allocated resources:" | grep -E "(cpu|memory)" || echo "Node description not available"
echo

echo "🔄 HPA Status:"
kubectl get hpa --all-namespaces 2>/dev/null || echo "No HPA configured"
echo

echo "=================================="
EOF

chmod +x /tmp/monitor-resources.sh

log_success "Monitoring setup completed!"
echo
log_info "Available monitoring commands:"
echo "  • kubectl top nodes                    - Node resource usage"
echo "  • kubectl top pods --all-namespaces   - Pod resource usage"
echo "  • /tmp/monitor-resources.sh           - Comprehensive monitoring report"
echo "  • watch kubectl get pods --all-namespaces  - Real-time pod status"
echo
log_info "Setup complete! You can now proceed with the UPID demo."