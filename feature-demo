# UPID CLI Feature Demo Guide

**Purpose:**
This guide demonstrates the full power of UPID CLI, with a dedicated scenario and script for each major feature. Each section includes:
- **Feature Purpose**
- **Demo Script** (copy-paste ready)
- **How to Run**
- **Sample Input/Output**
- **What to Observe**

---

## Table of Contents
1. [Resource Optimization](#resource-optimization)
2. [Idle Pod Detection & Zero-Pod Scaling](#idle-pod-detection--zero-pod-scaling)
3. [Cost Analysis](#cost-analysis)
4. [Cluster Health & Universal Analysis](#cluster-health--universal-analysis)
5. [Reporting & Visualization](#reporting--visualization)
6. [Authentication & Multi-Cluster Management](#authentication--multi-cluster-management)
7. [Deployment Automation](#deployment-automation)

---

## 1. Resource Optimization

**Purpose:**
Show how UPID detects over-provisioned resources and recommends optimal CPU/memory settings.

**Demo Script:**
```bash
# demo_resource_optimization.sh
NS="upid-optimize"
kubectl create ns $NS || true
for i in {1..3}; do
  kubectl run opt-demo-$i --image=nginx --requests=cpu=500m,memory=512Mi --limits=cpu=1,memory=1Gi -n $NS
done
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
echo "Run: upid universal optimize --namespace $NS"
```

**How to Run:**
```bash
bash -c "$(cat <<'EOF'
NS="upid-optimize"
kubectl create ns $NS || true
for i in {1..3}; do
  kubectl run opt-demo-$i --image=nginx --requests=cpu=500m,memory=512Mi --limits=cpu=1,memory=1Gi -n $NS
done
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
EOF
)"
upid universal optimize --namespace upid-optimize
```

**Sample Output:**
```
[bold blue]Optimization Analysis: upid-optimize[/bold blue]
Found 3 optimization opportunities
- opt-demo-1: Reduce CPU/memory requests
- opt-demo-2: Reduce CPU/memory requests
- opt-demo-3: Reduce CPU/memory requests
```

**What to Observe:**
UPID will recommend lower resource requests/limits for the demo pods.

---

## 2. Idle Pod Detection & Zero-Pod Scaling

**Purpose:**
Demonstrate UPID's ability to detect idle pods and recommend scaling them to zero.

**Demo Script:**
```bash
# demo_idle_detection.sh
NS="upid-idle"
kubectl create ns $NS || true
kubectl create deployment active-demo --image=nginx -n $NS
kubectl create deployment idle-demo --image=nginx -n $NS
kubectl scale deployment idle-demo --replicas=0 -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s || true
echo "Run: upid universal analyze --namespace $NS"
```

**How to Run:**
```bash
bash -c "$(cat <<'EOF'
NS="upid-idle"
kubectl create ns $NS || true
kubectl create deployment active-demo --image=nginx -n $NS
kubectl create deployment idle-demo --image=nginx -n $NS
kubectl scale deployment idle-demo --replicas=0 -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s || true
EOF
)"
upid universal analyze --namespace upid-idle
```

**Sample Output:**
```
[bold blue]Cluster Analysis: upid-idle[/bold blue]
- active-demo: Running
- idle-demo: Idle (0 pods)
[bold green]Recommendation: Scale idle-demo to zero pods[/bold green]
```

**What to Observe:**
UPID will flag the `idle-demo` deployment as idle and recommend zero-pod scaling.

---

## 3. Cost Analysis

**Purpose:**
Show how UPID analyzes resource usage and provides cost breakdowns.

**Demo Script:**
```bash
# demo_cost_analysis.sh
NS="upid-cost"
kubectl create ns $NS || true
kubectl run cost-high --image=nginx --requests=cpu=1,memory=2Gi --limits=cpu=2,memory=4Gi -n $NS
kubectl run cost-low --image=nginx --requests=cpu=100m,memory=128Mi --limits=cpu=200m,memory=256Mi -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
echo "Run: upid universal report --namespace $NS --format table"
```

**How to Run:**
```bash
bash -c "$(cat <<'EOF'
NS="upid-cost"
kubectl create ns $NS || true
kubectl run cost-high --image=nginx --requests=cpu=1,memory=2Gi --limits=cpu=2,memory=4Gi -n $NS
kubectl run cost-low --image=nginx --requests=cpu=100m,memory=128Mi --limits=cpu=200m,memory=256Mi -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
EOF
)"
upid universal report --namespace upid-cost --format table
```

**Sample Output:**
```
[bold blue]Cost Report: upid-cost[/bold blue]
- cost-high: $12.00/month
- cost-low: $0.50/month
```

**What to Observe:**
UPID will show cost differences between high and low resource pods.

---

## 4. Cluster Health & Universal Analysis

**Purpose:**
Demonstrate UPID's universal cluster health and resource analysis.

**Demo Script:**
```bash
# demo_universal_analysis.sh
NS="upid-universal"
kubectl create ns $NS || true
kubectl create deployment universal-demo --image=nginx -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
echo "Run: upid universal status"
echo "Run: upid universal analyze --namespace $NS"
```

**How to Run:**
```bash
bash -c "$(cat <<'EOF'
NS="upid-universal"
kubectl create ns $NS || true
kubectl create deployment universal-demo --image=nginx -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
EOF
)"
upid universal status
upid universal analyze --namespace upid-universal
```

**Sample Output:**
```
[bold blue]Cluster: upid-universal[/bold blue]
Type: KUBERNETES
Status: ✅ Connected
[bold green]Resource Analysis[/bold green]
- universal-demo: Running
```

**What to Observe:**
UPID will display cluster health, capabilities, and resource analysis.

---

## 5. Reporting & Visualization

**Purpose:**
Showcase UPID's ability to generate detailed, shareable reports.

**Demo Script:**
```bash
# demo_reporting.sh
NS="upid-report"
kubectl create ns $NS || true
kubectl create deployment report-demo --image=nginx -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
echo "Run: upid universal report --namespace $NS --format html --output upid-report.html"
```

**How to Run:**
```bash
bash -c "$(cat <<'EOF'
NS="upid-report"
kubectl create ns $NS || true
kubectl create deployment report-demo --image=nginx -n $NS
kubectl wait --for=condition=Ready pods --all -n $NS --timeout=60s
EOF
)"
upid universal report --namespace upid-report --format html --output upid-report.html
# Open upid-report.html in your browser
```

**Sample Output:**
```
✅ Report saved to: upid-report.html
```

**What to Observe:**
A comprehensive HTML report with insights and recommendations.

---

## 6. Authentication & Multi-Cluster Management

**Purpose:**
Demonstrate UPID's authentication and multi-cluster features.

**Demo Script:**
```bash
# demo_multi_cluster.sh
# Assumes you have two kubeconfig contexts: cluster1 and cluster2
echo "Switching to cluster1 context..."
kubectl config use-context cluster1
upid universal status
echo "Switching to cluster2 context..."
kubectl config use-context cluster2
upid universal status
echo "Run: upid cluster list"
```

**How to Run:**
```bash
# Replace 'cluster1' and 'cluster2' with your actual context names
kubectl config use-context cluster1
upid universal status
kubectl config use-context cluster2
upid universal status
upid cluster list
```

**Sample Output:**
```
[bold blue]Cluster: cluster1[/bold blue]
Status: ✅ Connected
[bold blue]Cluster: cluster2[/bold blue]
Status: ✅ Connected
[bold green]Cluster List[/bold green]
- cluster1
- cluster2
```

**What to Observe:**
UPID will show status for multiple clusters and list all clusters.

---

## 7. Deployment Automation

**Purpose:**
Show how UPID can automate deployments and manage workloads.

**Demo Script:**
```bash
# demo_deployment_automation.sh
NS="upid-deploy"
kubectl create ns $NS || true
# Replace <cluster_id> with your actual cluster ID
upid deploy create <cluster_id> --name demo-app --namespace $NS --image nginx --replicas 2 --port 80 --wait
kubectl get deployments -n $NS
```

**How to Run:**
```bash
# Replace <cluster_id> with your actual cluster ID
NS="upid-deploy"
kubectl create ns $NS || true
upid deploy create <cluster_id> --name demo-app --namespace $NS --image nginx --replicas 2 --port 80 --wait
kubectl get deployments -n $NS
```

**Sample Output:**
```
✓ Deployment created successfully!
Name: demo-app
Namespace: upid-deploy
Replicas: 2
Status: creating
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
demo-app    2/2     2            2           1m
```

**What to Observe:**
UPID will create a deployment and you can verify it with `kubectl`.

---

## Cleanup
After each demo, clean up with:
```bash
kubectl delete ns <namespace>
```

---

# **Conclusion**
This suite demonstrates the full power of UPID CLI, with a clear, reproducible scenario for each feature. Keep this guide as your go-to reference for UPID demos, workshops, and onboarding! 
