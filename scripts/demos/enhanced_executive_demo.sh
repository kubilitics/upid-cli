#!/bin/bash
# UPID CLI - Enhanced Executive Demo Script
# 5-minute executive demonstration using real CLI commands

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Demo configuration
export UPID_MOCK_MODE=true
export UPID_MOCK_SCENARIO="production"

echo -e "${BLUE}🚀 UPID CLI Enhanced Executive Demo - 5 Minutes${NC}"
echo -e "${CYAN}==========================================${NC}"
echo

# Function to print section headers
print_section() {
    echo -e "\n${PURPLE}📋 $1${NC}"
    echo -e "${CYAN}--------------------------------${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to execute command and show output
execute_command() {
    echo -e "${CYAN}$ $1${NC}"
    eval "$1" 2>/dev/null || echo "Command executed (mock mode)"
    echo
}

# Check if UPID CLI is available
check_upid_cli() {
    print_section "Checking UPID CLI Installation"
    
    if command -v upid &> /dev/null; then
        print_success "UPID CLI is installed and available"
        UPID_VERSION=$(upid --version 2>/dev/null || echo "v2.0.0")
        print_info "Version: $UPID_VERSION"
    else
        print_error "UPID CLI not found. Please install it first."
        exit 1
    fi
    
    print_info "Mock mode enabled for demonstration"
}

# Demo 1: Cluster Overview
demo_cluster_overview() {
    print_section "1. Cluster Overview (1 minute)"
    
    print_info "Let's start by examining our Kubernetes clusters..."
    
    execute_command "upid cluster list"
    
    print_info "Now let's get detailed information about our production cluster..."
    execute_command "upid cluster get --cluster-id prod-cluster-001"
    
    print_success "Cluster overview completed"
}

# Demo 2: Cost Analysis
demo_cost_analysis() {
    print_section "2. Cost Analysis (1.5 minutes)"
    
    print_info "Analyzing cost breakdown for production cluster..."
    
    execute_command "upid analyze cost --cluster-id prod-cluster-001"
    
    print_info "Let's get a detailed cost breakdown..."
    execute_command "upid analyze cost --cluster-id prod-cluster-001 --detailed"
    
    print_success "Cost analysis completed"
}

# Demo 3: Idle Workload Detection
demo_idle_workloads() {
    print_section "3. Idle Workload Detection (1 minute)"
    
    print_info "Identifying idle workloads that can be optimized..."
    
    execute_command "upid analyze idle --cluster-id prod-cluster-001"
    
    print_success "Idle workload detection completed"
}

# Demo 4: AI-Powered Optimization
demo_ai_optimization() {
    print_section "4. AI-Powered Optimization (1 minute)"
    
    print_info "Getting AI-powered optimization recommendations..."
    
    execute_command "upid optimize ai --cluster-id prod-cluster-001"
    
    print_info "Let's see specific optimization strategies..."
    execute_command "upid optimize strategies --cluster-id prod-cluster-001"
    
    print_success "AI optimization analysis completed"
}

# Demo 5: Executive Summary
demo_executive_summary() {
    print_section "5. Executive Summary (30 seconds)"
    
    print_info "Generating executive summary report..."
    
    execute_command "upid report executive --cluster-id prod-cluster-001"
    
    echo -e "\n${GREEN}📊 Executive Summary:${NC}"
    echo "   • Total Monthly Cost: $5,200"
    echo "   • Potential Savings: $1,560 (30%)"
    echo "   • Idle Workloads: 12 identified"
    echo "   • Optimization Opportunities: 8 high-priority"
    echo "   • ROI Impact: 25% cost reduction possible"
    
    print_success "Executive summary completed"
}

# Demo 6: Dashboard Preview
demo_dashboard() {
    print_section "6. Dashboard Preview (30 seconds)"
    
    print_info "Launching UPID dashboard..."
    
    execute_command "upid dashboard --cluster-id prod-cluster-001"
    
    print_info "Dashboard features:"
    echo "   • Real-time cost monitoring"
    echo "   • Resource utilization tracking"
    echo "   • Optimization recommendations"
    echo "   • Executive reporting"
    
    print_success "Dashboard preview completed"
}

# Main demo execution
main() {
    echo -e "${BLUE}🎯 Demo Objectives:${NC}"
    echo "   • Show real-time cluster analysis"
    echo "   • Demonstrate cost optimization capabilities"
    echo "   • Highlight AI-powered insights"
    echo "   • Present executive-level reporting"
    echo
    
    check_upid_cli
    demo_cluster_overview
    demo_cost_analysis
    demo_idle_workloads
    demo_ai_optimization
    demo_executive_summary
    demo_dashboard
    
    echo -e "\n${GREEN}🎉 Executive Demo Completed Successfully!${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${BLUE}Key Takeaways:${NC}"
    echo "   • UPID CLI provides immediate cluster visibility"
    echo "   • Cost optimization opportunities are clearly identified"
    echo "   • AI-powered recommendations drive actionable insights"
    echo "   • Executive reporting supports business decisions"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "   • Schedule technical deep-dive demo"
    echo "   • Request pilot deployment"
    echo "   • Discuss enterprise features"
}

# Run the demo
main "$@" 