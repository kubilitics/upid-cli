#!/bin/bash
# UPID CLI Complete Test Suite Runner
# Runs all testing scripts in sequence

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() {
    echo -e "$1"
}

main() {
    log "${PURPLE}🎯 UPID CLI COMPLETE TEST SUITE${NC}"
    log "====================================="
    log ""
    
    # Make all scripts executable
    chmod +x scripts/testing/*.sh
    chmod +x scripts/testing/*/*.sh
    
    # Run main product testing
    log "${BLUE}1. Running Main Product Testing...${NC}"
    ./scripts/testing/upid_product_testing.sh
    
    log ""
    
    # Run core features testing
    log "${BLUE}2. Running Core Features Testing...${NC}"
    ./scripts/testing/core_features/zero_pod_scaling_test.sh
    ./scripts/testing/core_features/ml_intelligence_test.sh
    
    log ""
    
    # Run workload simulation
    log "${BLUE}3. Running Workload Simulation...${NC}"
    ./scripts/testing/workload_simulation/production_workloads.sh
    
    log ""
    
    # Run performance validation
    log "${BLUE}4. Running Performance Validation...${NC}"
    ./scripts/testing/performance_validation/performance_test.sh
    
    log ""
    
    # Run enterprise features testing
    log "${BLUE}5. Running Enterprise Features Testing...${NC}"
    ./scripts/testing/enterprise_demo/enterprise_features_test.sh
    
    log ""
    log "${GREEN}🎉 COMPLETE TEST SUITE FINISHED!${NC}"
    log ""
    log "📋 Test Results Summary:"
    log "  - Main Product Testing: Core functionality validation"
    log "  - Core Features Testing: Zero-pod scaling and ML intelligence"
    log "  - Workload Simulation: Production workload creation"
    log "  - Performance Validation: Performance and scalability testing"
    log "  - Enterprise Features Testing: Enterprise-grade capabilities"
    log ""
    log "📊 Check individual log files for detailed results"
}

main "$@"
