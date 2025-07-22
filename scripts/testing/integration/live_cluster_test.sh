#!/bin/bash
# UPID CLI Live Cluster Integration Test
# Tests UPID CLI with real Kubernetes cluster

set -e

UPID_BINARY="upid"
NAMESPACE="default"
LOG_FILE="live_cluster_test_$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

test_live_command() {
    local cmd="$1"
    local description="$2"
    local timeout="${3:-60}"
    
    log "${YELLOW}🔍 LIVE TEST: $description${NC}"
    log "Command: $UPID_BINARY $cmd"
    
    if timeout $timeout $UPID_BINARY $cmd >/dev/null 2>&1; then
        log "${GREEN}✅ LIVE TEST PASS${NC}"
        return 0
    else
        log "${RED}❌ LIVE TEST FAIL${NC}"
        return 1
    fi
}

setup_test_environment() {
    log "${BLUE}🔧 Setting up test environment...${NC}"
    
    # Check kubectl availability
    if ! command -v kubectl &> /dev/null; then
        log "${RED}❌ kubectl not found. Cannot run live tests.${NC}"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log "${RED}❌ Cannot connect to Kubernetes cluster.${NC}"
        exit 1
    fi
    
    log "${GREEN}✅ Kubernetes cluster connected${NC}"
    
    # Create test workloads
    kubectl create deployment test-app --image=nginx:alpine --replicas=3 --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
    kubectl create deployment idle-app --image=nginx:alpine --replicas=5 --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
    
    log "${GREEN}✅ Test workloads created${NC}"
}

cleanup_test_environment() {
    log "${BLUE}🧹 Cleaning up test environment...${NC}"
    
    kubectl delete deployment test-app 2>/dev/null || true
    kubectl delete deployment idle-app 2>/dev/null || true
    
    log "${GREEN}✅ Test environment cleaned up${NC}"
}

main() {
    log "🚀 UPID CLI Live Cluster Integration Test"
    log "========================================="
    
    setup_test_environment
    
    # Test analysis commands
    test_live_command "analyze resources --namespace $NAMESPACE" "Resource analysis"
    test_live_command "analyze cost --namespace $NAMESPACE" "Cost analysis"
    test_live_command "analyze performance --namespace $NAMESPACE" "Performance analysis"
    
    # Test optimization commands
    test_live_command "optimize resources --analyze --namespace $NAMESPACE" "Resource optimization analysis"
    test_live_command "optimize costs --analyze --namespace $NAMESPACE" "Cost optimization analysis"
    test_live_command "optimize zero-pod --analyze --namespace $NAMESPACE" "Zero-pod scaling analysis"
    
    # Test intelligence commands
    test_live_command "intelligence analyze" "ML intelligence analysis"
    test_live_command "intelligence predict --time-range 7d" "ML predictions"
    test_live_command "intelligence optimize --confidence 0.8" "ML optimization"
    
    # Test reporting commands
    test_live_command "report summary" "Summary reporting"
    test_live_command "report cost" "Cost reporting"
    test_live_command "report performance" "Performance reporting"
    
    cleanup_test_environment
    
    log "${GREEN}✅ Live cluster integration test complete!${NC}"
}

main "$@"
