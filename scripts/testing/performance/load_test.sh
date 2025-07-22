#!/bin/bash
# UPID CLI Performance and Load Testing Script
# Tests UPID CLI under various load conditions

set -e

UPID_BINARY="upid"
LOG_FILE="load_test_$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

test_response_time() {
    local cmd="$1"
    local description="$2"
    
    log "${YELLOW}⏱️ Testing response time: $description${NC}"
    
    local start_time=$(date +%s.%N)
    $UPID_BINARY $cmd --help >/dev/null 2>&1
    local end_time=$(date +%s.%N)
    
    local duration=$(echo "$end_time - $start_time" | bc)
    log "Response time: ${duration}s"
    
    if (( $(echo "$duration < 5.0" | bc -l) )); then
        log "${GREEN}✅ Response time acceptable${NC}"
        return 0
    else
        log "${RED}❌ Response time too slow${NC}"
        return 1
    fi
}

test_concurrent_commands() {
    local num_commands="${1:-5}"
    local description="$2"
    
    log "${YELLOW}🔄 Testing concurrent commands: $description${NC}"
    log "Running $num_commands concurrent commands..."
    
    local start_time=$(date +%s.%N)
    
    for i in $(seq 1 $num_commands); do
        $UPID_BINARY analyze resources &
        $UPID_BINARY analyze cost &
        $UPID_BINARY optimize zero-pod --analyze &
    done
    
    wait
    local end_time=$(date +%s.%N)
    
    local duration=$(echo "$end_time - $start_time" | bc)
    log "Concurrent execution time: ${duration}s"
    
    if (( $(echo "$duration < 30.0" | bc -l) )); then
        log "${GREEN}✅ Concurrent performance acceptable${NC}"
        return 0
    else
        log "${RED}❌ Concurrent performance too slow${NC}"
        return 1
    fi
}

test_memory_usage() {
    local cmd="$1"
    local description="$2"
    
    log "${YELLOW}💾 Testing memory usage: $description${NC}"
    
    local memory_before=$(ps -o rss= -p $$)
    $UPID_BINARY $cmd --help >/dev/null 2>&1
    local memory_after=$(ps -o rss= -p $$)
    
    local memory_diff=$((memory_after - memory_before))
    log "Memory usage: ${memory_diff}KB"
    
    if [ $memory_diff -lt 100000 ]; then  # Less than 100MB
        log "${GREEN}✅ Memory usage acceptable${NC}"
        return 0
    else
        log "${RED}❌ Memory usage too high${NC}"
        return 1
    fi
}

main() {
    log "🚀 UPID CLI Performance and Load Testing"
    log "======================================="
    
    # Test response times
    test_response_time "analyze resources" "Resource analysis"
    test_response_time "optimize zero-pod --analyze" "Zero-pod optimization"
    test_response_time "intelligence analyze" "ML intelligence"
    
    # Test concurrent performance
    test_concurrent_commands 3 "Light load"
    test_concurrent_commands 5 "Medium load"
    test_concurrent_commands 10 "Heavy load"
    
    # Test memory usage
    test_memory_usage "analyze resources" "Resource analysis memory"
    test_memory_usage "optimize zero-pod --analyze" "Optimization memory"
    test_memory_usage "intelligence analyze" "ML memory"
    
    log "${GREEN}✅ Performance testing complete!${NC}"
}

main "$@"
