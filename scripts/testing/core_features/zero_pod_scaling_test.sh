#!/bin/bash
# UPID CLI Zero-Pod Scaling Test
# Tests the core zero-pod scaling functionality

set -e

UPID_BINARY="upid"
LOG_FILE="zero_pod_test_$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

setup_test_workloads() {
    log "${BLUE}🔧 Setting up test workloads for zero-pod scaling${NC}"
    
    # Create test namespace
    kubectl create namespace zero-pod-test --dry-run=client -o yaml | kubectl apply -f -
    
    # Create active workload (should not be scaled to zero)
    kubectl create deployment active-app --image=nginx:alpine --replicas=3 -n zero-pod-test --dry-run=client -o yaml | kubectl apply -f -
    
    # Create idle workload (should be scaled to zero)
    kubectl create deployment idle-app --image=nginx:alpine --replicas=2 -n zero-pod-test --dry-run=client -o yaml | kubectl apply -f -
    
    # Set old timestamps for idle app
    kubectl patch deployment idle-app -n zero-pod-test -p '{"metadata":{"creationTimestamp":"2024-01-01T00:00:00Z"}}' --dry-run=client -o yaml | kubectl apply -f -
    
    log "${GREEN}✅ Test workloads created${NC}"
}

test_zero_pod_analysis() {
    log "${YELLOW}🔍 Testing zero-pod analysis${NC}"
    
    # Test idle detection
    $UPID_BINARY analyze idle --namespace zero-pod-test --detailed
    
    # Test zero-pod analysis
    $UPID_BINARY optimize zero-pod --analyze --namespace zero-pod-test
    
    # Test zero-pod simulation
    $UPID_BINARY optimize zero-pod --simulate --namespace zero-pod-test
    
    log "${GREEN}✅ Zero-pod analysis complete${NC}"
}

test_zero_pod_execution() {
    log "${YELLOW}⚡ Testing zero-pod execution${NC}"
    
    # Test safe execution
    $UPID_BINARY optimize zero-pod --execute --safe-mode --namespace zero-pod-test
    
    # Verify results
    kubectl get pods -n zero-pod-test
    
    log "${GREEN}✅ Zero-pod execution complete${NC}"
}

cleanup_test_workloads() {
    log "${BLUE}🧹 Cleaning up test workloads${NC}"
    
    kubectl delete namespace zero-pod-test 2>/dev/null || true
    
    log "${GREEN}✅ Cleanup complete${NC}"
}

main() {
    log "${PURPLE}🎯 UPID CLI Zero-Pod Scaling Test${NC}"
    log "====================================="
    
    if ! command -v kubectl &> /dev/null; then
        log "${RED}❌ kubectl not found. Cannot run zero-pod tests.${NC}"
        exit 1
    fi
    
    setup_test_workloads
    test_zero_pod_analysis
    test_zero_pod_execution
    cleanup_test_workloads
    
    log "${GREEN}🎉 Zero-pod scaling test complete!${NC}"
}

main "$@"
