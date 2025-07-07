#!/bin/bash

# UPID CLI Binary Test Script
# This script tests if the UPID binary is working correctly

echo "🧪 UPID CLI Binary Test"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test command
test_command() {
    local command="$1"
    local description="$2"
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Command: $command"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Function to test command with output
test_command_with_output() {
    local command="$1"
    local description="$2"
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Command: $command"
    
    if output=$(eval "$command" 2>&1); then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "Output: $output"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Error: $output"
        return 1
    fi
}

# Check if binary exists
echo -e "\n${YELLOW}Checking binary location...${NC}"
if [ -f "./dist/upid-darwin-arm64" ]; then
    echo -e "${GREEN}✅ Binary found at ./dist/upid-darwin-arm64${NC}"
    BINARY_PATH="./dist/upid-darwin-arm64"
elif [ -f "/usr/local/bin/upid" ]; then
    echo -e "${GREEN}✅ Binary found at /usr/local/bin/upid${NC}"
    BINARY_PATH="/usr/local/bin/upid"
else
    echo -e "${RED}❌ Binary not found!${NC}"
    echo "Please build the binary first: python build_binary_fixed.py"
    exit 1
fi

# Test basic functionality
echo -e "\n${YELLOW}Testing basic functionality...${NC}"

test_command "$BINARY_PATH --help" "Help command"
test_command "$BINARY_PATH status" "Status command"
test_command "$BINARY_PATH demo" "Demo command"

# Test universal commands (if kubectl is available)
if command -v kubectl &> /dev/null; then
    echo -e "\n${YELLOW}Testing with Kubernetes cluster...${NC}"
    
    # Check if cluster is accessible
    if kubectl cluster-info > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Kubernetes cluster accessible${NC}"
        
        test_command "$BINARY_PATH universal status" "Universal status"
        test_command "$BINARY_PATH universal analyze" "Universal analyze"
        test_command "$BINARY_PATH universal optimize" "Universal optimize"
        test_command "$BINARY_PATH universal report" "Universal report"
    else
        echo -e "${YELLOW}⚠️  Kubernetes cluster not accessible${NC}"
        echo "Universal commands will be skipped"
    fi
else
    echo -e "${YELLOW}⚠️  kubectl not found${NC}"
    echo "Universal commands will be skipped"
fi

# Test output formats
echo -e "\n${YELLOW}Testing output formats...${NC}"
test_command "$BINARY_PATH status --format json" "JSON output format"
test_command "$BINARY_PATH status --format yaml" "YAML output format"

# Summary
echo -e "\n${YELLOW}Test Summary${NC}"
echo "==========="
echo "Binary location: $BINARY_PATH"
echo "Binary size: $(ls -lh $BINARY_PATH | awk '{print $5}')"
echo "Binary permissions: $(ls -l $BINARY_PATH | awk '{print $1}')"

echo -e "\n${GREEN}🎉 Binary test completed!${NC}"
echo "If all tests passed, the UPID CLI binary is working correctly."
echo "You can now share this binary with others for testing." 