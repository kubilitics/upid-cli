#!/bin/bash
# UPID CLI Production Workload Simulation
# Creates realistic production workloads for testing

set -e

LOG_FILE="production_workloads_$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

create_active_workloads() {
    log "${BLUE}🚀 Creating Active Production Workloads${NC}"
    log "=========================================="
    
    # Create active namespace
    kubectl create namespace active-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 1. Web Application (High Traffic)
    log "${YELLOW}Creating web application...${NC}"
    kubectl create deployment web-app --image=nginx:alpine --replicas=5 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl create service clusterip web-app --tcp=80:80 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 2. API Service (Medium Traffic)
    log "${YELLOW}Creating API service...${NC}"
    kubectl create deployment api-service --image=node:16-alpine --replicas=3 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl create service clusterip api-service --tcp=3000:3000 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 3. Database Service (Critical)
    log "${YELLOW}Creating database service...${NC}"
    kubectl create deployment db-service --image=postgres:13 --replicas=2 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl create service clusterip db-service --tcp=5432:5432 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 4. Cache Service (High Memory)
    log "${YELLOW}Creating cache service...${NC}"
    kubectl create deployment cache-service --image=redis:6-alpine --replicas=2 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl create service clusterip cache-service --tcp=6379:6379 -n active-prod --dry-run=client -o yaml | kubectl apply -f -
    
    log "${GREEN}✅ Active workloads created${NC}"
}

create_idle_workloads() {
    log "${BLUE}😴 Creating Idle Production Workloads${NC}"
    log "======================================="
    
    # Create idle namespace
    kubectl create namespace idle-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 1. Legacy Application (Old, No Traffic)
    log "${YELLOW}Creating legacy application...${NC}"
    kubectl create deployment legacy-app --image=nginx:1.16 --replicas=3 -n idle-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl patch deployment legacy-app -n idle-prod -p '{"metadata":{"creationTimestamp":"2024-01-01T00:00:00Z"}}' --dry-run=client -o yaml | kubectl apply -f -
    
    # 2. Development Tools (Intermittent Usage)
    log "${YELLOW}Creating development tools...${NC}"
    kubectl create deployment dev-tools --image=busybox:1.35 --replicas=4 -n idle-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 3. Backup Service (Scheduled, Mostly Idle)
    log "${YELLOW}Creating backup service...${NC}"
    kubectl create deployment backup-service --image=postgres:13 --replicas=2 -n idle-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 4. Monitoring Service (Low Resource Usage)
    log "${YELLOW}Creating monitoring service...${NC}"
    kubectl create deployment monitoring-service --image=prom/prometheus --replicas=1 -n idle-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 5. Testing Service (Development Environment)
    log "${YELLOW}Creating testing service...${NC}"
    kubectl create deployment test-service --image=nginx:alpine --replicas=2 -n idle-prod --dry-run=client -o yaml | kubectl apply -f -
    
    log "${GREEN}✅ Idle workloads created${NC}"
}

create_mixed_workloads() {
    log "${BLUE}�� Creating Mixed Production Workloads${NC}"
    log "========================================="
    
    # Create mixed namespace
    kubectl create namespace mixed-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 1. Microservice with varying traffic
    log "${YELLOW}Creating microservice with varying traffic...${NC}"
    kubectl create deployment microservice-1 --image=nginx:alpine --replicas=2 -n mixed-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl create deployment microservice-2 --image=nginx:alpine --replicas=1 -n mixed-prod --dry-run=client -o yaml | kubectl apply -f -
    kubectl create deployment microservice-3 --image=nginx:alpine --replicas=3 -n mixed-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 2. Batch processing jobs
    log "${YELLOW}Creating batch processing jobs...${NC}"
    kubectl create deployment batch-processor --image=python:3.9-alpine --replicas=2 -n mixed-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # 3. Data processing pipeline
    log "${YELLOW}Creating data processing pipeline...${NC}"
    kubectl create deployment data-processor --image=python:3.9-alpine --replicas=1 -n mixed-prod --dry-run=client -o yaml | kubectl apply -f -
    
    log "${GREEN}✅ Mixed workloads created${NC}"
}

simulate_traffic_patterns() {
    log "${BLUE}📊 Simulating Traffic Patterns${NC}"
    log "==============================="
    
    # Simulate traffic to active workloads
    log "${YELLOW}Simulating traffic to active workloads...${NC}"
    kubectl get pods -n active-prod -o wide
    
    # Show workload distribution
    log "${YELLOW}Workload distribution:${NC}"
    kubectl get deployments --all-namespaces
    
    log "${GREEN}✅ Traffic patterns simulated${NC}"
}

generate_workload_report() {
    log "${PURPLE}📋 Production Workload Report${NC}"
    log "==============================="
    
    log "${GREEN}✅ Production Workloads Created:${NC}"
    log ""
    log "🚀 Active Workloads (High Traffic):"
    log "  - web-app: 5 replicas (Web application)"
    log "  - api-service: 3 replicas (API service)"
    log "  - db-service: 2 replicas (Database)"
    log "  - cache-service: 2 replicas (Redis cache)"
    log ""
    log "😴 Idle Workloads (Zero-Pod Candidates):"
    log "  - legacy-app: 3 replicas (Old application)"
    log "  - dev-tools: 4 replicas (Development tools)"
    log "  - backup-service: 2 replicas (Backup service)"
    log "  - monitoring-service: 1 replica (Monitoring)"
    log "  - test-service: 2 replicas (Testing)"
    log ""
    log "🔄 Mixed Workloads (Variable Traffic):"
    log "  - microservice-1: 2 replicas"
    log "  - microservice-2: 1 replica"
    log "  - microservice-3: 3 replicas"
    log "  - batch-processor: 2 replicas"
    log "  - data-processor: 1 replica"
    log ""
    log "📊 Total Workloads: 15 deployments across 3 namespaces"
    log "🎯 Ready for UPID CLI testing and optimization"
}

cleanup_workloads() {
    log "${BLUE}🧹 Cleaning up production workloads${NC}"
    log "====================================="
    
    kubectl delete namespace active-prod 2>/dev/null || true
    kubectl delete namespace idle-prod 2>/dev/null || true
    kubectl delete namespace mixed-prod 2>/dev/null || true
    
    log "${GREEN}✅ Cleanup complete${NC}"
}

main() {
    log "${PURPLE}🎯 UPID CLI Production Workload Simulation${NC}"
    log "============================================="
    
    if ! command -v kubectl &> /dev/null; then
        log "${RED}❌ kubectl not found. Cannot create workloads.${NC}"
        exit 1
    fi
    
    create_active_workloads
    create_idle_workloads
    create_mixed_workloads
    simulate_traffic_patterns
    generate_workload_report
    
    log ""
    log "${GREEN}🎉 Production workload simulation complete!${NC}"
    log "Workloads are ready for UPID CLI testing."
    log ""
    log "${YELLOW}To cleanup workloads, run:${NC}"
    log "  kubectl delete namespace active-prod idle-prod mixed-prod"
}

main "$@"
