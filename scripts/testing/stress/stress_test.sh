#!/bin/bash
# UPID CLI Stress Testing Script
# Tests UPID CLI under extreme conditions

set -e

UPID_BINARY="upid"
LOG_FILE="stress_test_$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

test_rapid_commands() {
    local num_commands="${1:-50}"
    
    log "${YELLOW}⚡ Testing rapid command execution: $num_commands commands${NC}"
    
    local failures=0
    for i in $(seq 1 $num_commands); do
        if ! $UPID_BINARY --help >/dev/null 2>&1; then
            ((failures++))
        fi
    done
    
    local success_rate=$(( (num_commands - failures) * 100 / num_commands ))
    log "Success rate: ${success_rate}%"
    
    if [ $success_rate -ge 95 ]; then
        log "${GREEN}✅ Rapid command test passed${NC}"
        return 0
    else
        log "${RED}❌ Rapid command test failed${NC}"
        return 1
    fi
}

test_error_handling() {
    log "${YELLOW}🛡️ Testing error handling${NC}"
    
    local failures=0
    
    # Test invalid commands
    if $UPID_BINARY invalid-command 2>/dev/null; then
        ((failures++))
    fi
    
    # Test invalid options
    if $UPID_BINARY --invalid-option 2>/dev/null; then
        ((failures++))
    fi
    
    # Test invalid arguments
    if $UPID_BINARY analyze invalid-resource 2>/dev/null; then
        ((failures++))
    fi
    
    if [ $failures -eq 0 ]; then
        log "${GREEN}✅ Error handling test passed${NC}"
        return 0
    else
        log "${RED}❌ Error handling test failed${NC}"
        return 1
    fi
}

test_resource_limits() {
    log "${YELLOW}📊 Testing resource limits${NC}"
    
    # Test with limited memory
    if command -v ulimit &> /dev/null; then
        ulimit -v 50000000  # 50MB virtual memory limit
        if $UPID_BINARY --help >/dev/null 2>&1; then
            log "${GREEN}✅ Memory limit test passed${NC}"
        else
            log "${RED}❌ Memory limit test failed${NC}"
            return 1
        fi
        ulimit -v unlimited
    fi
    
    return 0
}

test_concurrent_stress() {
    local num_processes="${1:-20}"
    
    log "${YELLOW}🔥 Testing concurrent stress: $num_processes processes${NC}"
    
    local failures=0
    for i in $(seq 1 $num_processes); do
        $UPID_BINARY analyze resources &
        $UPID_BINARY optimize zero-pod --analyze &
        $UPID_BINARY intelligence analyze &
    done
    
    wait
    
    log "${GREEN}✅ Concurrent stress test completed${NC}"
    return 0
}

main() {
    log "🔥 UPID CLI Stress Testing"
    log "========================="
    
    # Test rapid command execution
    test_rapid_commands 50
    
    # Test error handling
    test_error_handling
    
    # Test resource limits
    test_resource_limits
    
    # Test concurrent stress
    test_concurrent_stress 20
    
    log "${GREEN}✅ Stress testing complete!${NC}"
}

main "$@"
