#!/bin/bash
# UPID CLI ML Intelligence Test
# Tests the ML-powered intelligence features

set -e

UPID_BINARY="upid"
LOG_FILE="ml_intelligence_test_$(date +%Y%m%d_%H%M%S).log"

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

test_ml_analysis() {
    log "${BLUE}🧠 Testing ML Intelligence Analysis${NC}"
    log "====================================="
    
    # Test ML analysis
    log "${YELLOW}Running ML intelligence analysis...${NC}"
    $UPID_BINARY intelligence analyze --cluster $(kubectl config current-context 2>/dev/null || echo "default")
    
    log "${GREEN}✅ ML analysis complete${NC}"
}

test_ml_predictions() {
    log "${BLUE}📈 Testing ML Predictions${NC}"
    log "============================"
    
    # Test resource predictions
    log "${YELLOW}Testing resource usage predictions...${NC}"
    $UPID_BINARY intelligence predict --time-range 7d --detailed
    
    # Test cost predictions
    log "${YELLOW}Testing cost predictions...${NC}"
    $UPID_BINARY intelligence predict --time-range 30d --cost-analysis
    
    log "${GREEN}✅ ML predictions complete${NC}"
}

test_ml_optimization() {
    log "${BLUE}⚡ Testing ML Optimization${NC}"
    log "============================="
    
    # Test ML optimization recommendations
    log "${YELLOW}Testing ML optimization recommendations...${NC}"
    $UPID_BINARY intelligence optimize --confidence 0.8
    
    # Test high confidence optimization
    log "${YELLOW}Testing high confidence optimization...${NC}"
    $UPID_BINARY intelligence optimize --confidence 0.95 --detailed
    
    log "${GREEN}✅ ML optimization complete${NC}"
}

test_business_intelligence() {
    log "${BLUE}💼 Testing Business Intelligence${NC}"
    log "==================================="
    
    # Test ROI analysis
    log "${YELLOW}Testing ROI analysis...${NC}"
    $UPID_BINARY intelligence business --roi-analysis
    
    # Test KPI tracking
    log "${YELLOW}Testing KPI tracking...${NC}"
    $UPID_BINARY intelligence business --kpi-tracking
    
    # Test business impact analysis
    log "${YELLOW}Testing business impact analysis...${NC}"
    $UPID_BINARY intelligence business --impact-analysis
    
    log "${GREEN}✅ Business intelligence complete${NC}"
}

test_ml_model_validation() {
    log "${BLUE}🔍 Testing ML Model Validation${NC}"
    log "=================================="
    
    # Test model loading
    log "${YELLOW}Validating ML model loading...${NC}"
    $UPID_BINARY intelligence analyze --validate-models
    
    # Test prediction accuracy
    log "${YELLOW}Testing prediction accuracy...${NC}"
    $UPID_BINARY intelligence predict --accuracy-test
    
    log "${GREEN}✅ ML model validation complete${NC}"
}

main() {
    log "${PURPLE}🎯 UPID CLI ML Intelligence Test${NC}"
    log "====================================="
    
    test_ml_analysis
    test_ml_predictions
    test_ml_optimization
    test_business_intelligence
    test_ml_model_validation
    
    log ""
    log "${GREEN}🎉 ML Intelligence Test Complete!${NC}"
    log ""
    log "${CYAN}📊 ML Features Validated:${NC}"
    log "  ✅ Resource usage prediction"
    log "  ✅ Cost prediction"
    log "  ✅ Optimization recommendations"
    log "  ✅ Business impact analysis"
    log "  ✅ ROI calculation"
    log "  ✅ KPI tracking"
    log "  ✅ Model accuracy validation"
}

main "$@"
