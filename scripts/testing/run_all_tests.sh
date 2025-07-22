#!/bin/bash
# UPID CLI Comprehensive Testing Suite
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
    log "${PURPLE}🎯 UPID CLI COMPREHENSIVE TESTING SUITE${NC}"
    log "============================================="
    log ""
    
    # Make all scripts executable
    chmod +x scripts/testing/*.sh
    chmod +x scripts/testing/*/*.sh
    
    # Run God Range Test (main comprehensive test)
    log "${BLUE}1. Running God Range Test...${NC}"
    ./scripts/testing/god_range_test.sh
    
    log ""
    
    # Run Unit Tests
    log "${BLUE}2. Running Unit Tests...${NC}"
    ./scripts/testing/unit/command_validation.sh
    
    log ""
    
    # Run Integration Tests
    log "${BLUE}3. Running Integration Tests...${NC}"
    ./scripts/testing/integration/live_cluster_test.sh
    
    log ""
    
    # Run Performance Tests
    log "${BLUE}4. Running Performance Tests...${NC}"
    ./scripts/testing/performance/load_test.sh
    
    log ""
    
    # Run Stress Tests
    log "${BLUE}5. Running Stress Tests...${NC}"
    ./scripts/testing/stress/stress_test.sh
    
    log ""
    
    # Run Customer Validation
    log "${BLUE}6. Running Customer Validation...${NC}"
    ./scripts/testing/validation/customer_validation.sh
    
    log ""
    log "${GREEN}🎉 ALL TESTS COMPLETE!${NC}"
    log ""
    log "📋 Test Results:"
    log "  - God Range Test: Comprehensive feature testing"
    log "  - Unit Tests: Individual command validation"
    log "  - Integration Tests: Live cluster testing"
    log "  - Performance Tests: Load and response time testing"
    log "  - Stress Tests: Extreme condition testing"
    log "  - Customer Validation: Real-world scenario testing"
    log ""
    log "📊 Check individual log files for detailed results"
}

main "$@"
