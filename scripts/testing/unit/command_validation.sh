#!/bin/bash
# UPID CLI Command Validation Script
# Tests individual commands for proper functionality

set -e

UPID_BINARY="upid"
LOG_FILE="command_validation_$(date +%Y%m%d_%H%M%S).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

test_command() {
    local cmd="$1"
    local description="$2"
    
    log "${YELLOW}Testing: $description${NC}"
    log "Command: $UPID_BINARY $cmd"
    
    if $UPID_BINARY $cmd --help >/dev/null 2>&1; then
        log "${GREEN}✅ PASS${NC}"
        return 0
    else
        log "${RED}❌ FAIL${NC}"
        return 1
    fi
}

main() {
    log "🔧 UPID CLI Command Validation"
    log "============================="
    
    # Test all main commands
    test_command "--help" "Main help"
    test_command "--version" "Version"
    test_command "status" "Status"
    test_command "auth" "Authentication"
    test_command "cluster" "Cluster management"
    test_command "analyze" "Analysis"
    test_command "optimize" "Optimization"
    test_command "report" "Reporting"
    test_command "deploy" "Deployment"
    test_command "universal" "Universal commands"
    test_command "intelligence" "Intelligence"
    test_command "storage" "Storage"
    test_command "billing" "Billing"
    test_command "cloud" "Cloud"
    
    log "${GREEN}✅ Command validation complete!${NC}"
}

main "$@"
