#!/bin/bash

# UPID CLI - QA Test Runner
# This script runs comprehensive QA tests on UPID CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 UPID CLI - QA Testing Platform${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Default values
BINARY_PATH="./releases/upid-darwin-arm64"
OUTPUT_FORMAT="markdown"
OUTPUT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --binary-path)
            BINARY_PATH="$2"
            shift 2
            ;;
        --output-format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --output-file)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --binary-path PATH    Path to UPID CLI binary (default: ./releases/upid-darwin-arm64)"
            echo "  --output-format FORMAT Output format: json, html, markdown (default: markdown)"
            echo "  --output-file FILE    Save report to file"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run with default settings"
            echo "  $0 --binary-path ./upid              # Test specific binary"
            echo "  $0 --output-format json              # Generate JSON report"
            echo "  $0 --output-file qa_report.md        # Save report to file"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if binary exists
if [[ ! -f "$BINARY_PATH" ]]; then
    echo -e "${RED}❌ Error: Binary not found at $BINARY_PATH${NC}"
    echo "Available binaries:"
    ls -la releases/ 2>/dev/null || echo "No releases directory found"
    exit 1
fi

# Check if Python script exists
if [[ ! -f "test_scripts/qa_test_platform.py" ]]; then
    echo -e "${RED}❌ Error: QA test script not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Binary found: $BINARY_PATH${NC}"
echo -e "${GREEN}✅ QA test script found${NC}"
echo ""

# Build command
CMD="python test_scripts/qa_test_platform.py --binary-path \"$BINARY_PATH\" --output-format $OUTPUT_FORMAT"

if [[ -n "$OUTPUT_FILE" ]]; then
    CMD="$CMD --output-file \"$OUTPUT_FILE\""
fi

echo -e "${YELLOW}Running QA tests...${NC}"
echo "Command: $CMD"
echo ""

# Run the tests
eval $CMD

echo ""
echo -e "${GREEN}✅ QA tests completed!${NC}"

if [[ -n "$OUTPUT_FILE" ]]; then
    echo -e "${GREEN}📄 Report saved to: $OUTPUT_FILE${NC}"
fi 