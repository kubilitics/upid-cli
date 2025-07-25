#!/bin/bash
# UPID CLI - Executive Demo Script
# 5-minute executive demonstration showcasing core value proposition

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
DEMO_CLUSTER_ID="81ad6174-7d57-4e98-bc3e-e3b8786f4829"
DEMO_SCENARIO="production"

echo -e "${BLUE}🚀 UPID CLI Executive Demo - 5 Minutes${NC}"
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

# Function to simulate loading
simulate_loading() {
    echo -n "Loading"
    for i in {1..3}; do
        sleep 0.5
        echo -n "."
    done
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
}

# Demo 1: Cluster Overview
demo_cluster_overview() {
    print_section "1. Cluster Overview (1 minute)"
    
    print_info "Let's start by examining our Kubernetes clusters..."
    simulate_loading
    
    # Simulate cluster list
    echo -e "${GREEN}📊 Found 3 clusters in your environment:${NC}"
    echo "   • production-cluster-01 (Healthy) - 150 pods, $5,200/month"
    echo "   • staging-cluster-01 (Healthy) - 80 pods, $2,800/month"
    echo "   • development-cluster-01 (Warning) - 40 pods, $1,200/month"
    echo
    print_success "Total monthly cost: $9,200"
    print_warning "Potential for significant cost optimization"
}

# Demo 2: Cost Analysis
demo_cost_analysis() {
    print_section "2. Cost Analysis (1.5 minutes)"
    
    print_info "Analyzing cost breakdown for production cluster..."
    simulate_loading
    
    echo -e "${GREEN}💰 Cost Breakdown:${NC}"
    echo "   • Compute: $3,178 (70%)"
    echo "   • Storage: $635 (14%)"
    echo "   • Network: $318 (7%)"
    echo "   • Waste: $642 (14%)"
    echo
    print_warning "14% of costs are wasted on idle resources"
    print_info "Optimization potential: $466/month per cluster"
}

# Demo 3: Idle Workload Detection
demo_idle_detection() {
    print_section "3. Idle Workload Detection (1 minute)"
    
    print_info "Scanning for idle workloads..."
    simulate_loading
    
    echo -e "${GREEN}💤 Found 2 idle workloads:${NC}"
    echo "   • web-frontend-123 (Development) - $176/month savings"
    echo "   • api-backend-456 (Staging) - $177/month savings"
    echo
    print_success "Total potential savings: $353/month"
    print_info "Confidence level: 85%+"
}

# Demo 4: Optimization Recommendations
demo_optimization_recommendations() {
    print_section "4. AI-Powered Optimization (1 minute)"
    
    print_info "Generating optimization recommendations..."
    simulate_loading
    
    echo -e "${GREEN}⚡ Top 3 Optimization Strategies:${NC}"
    echo "   • Zero-pod scaling: $790/month savings (Low risk)"
    echo "   • Resource right-sizing: $450/month savings (Medium risk)"
    echo "   • Node consolidation: $1,200/month savings (Medium risk)"
    echo
    print_success "Total potential savings: $2,440/month"
    print_info "ROI: 300%+ in first year"
}

# Demo 5: Executive Summary
demo_executive_summary() {
    print_section "5. Executive Summary (30 seconds)"
    
    echo -e "${GREEN}📈 Key Metrics:${NC}"
    echo "   • Current monthly cost: $9,200"
    echo "   • Potential monthly savings: $2,440"
    echo "   • Savings percentage: 26.5%"
    echo "   • Annual savings: $29,280"
    echo "   • Payback period: 4 months"
    echo
    print_success "UPID CLI can reduce your Kubernetes costs by 26.5%"
    print_info "That's $29,280 in annual savings!"
}

# Main demo flow
main() {
    echo -e "${BLUE}🎯 Executive Demo: Kubernetes Cost Optimization${NC}"
    echo -e "${CYAN}Target: C-level executives and decision makers${NC}"
    echo -e "${CYAN}Duration: 5 minutes${NC}"
    echo -e "${CYAN}Focus: ROI, cost savings, and business value${NC}"
    echo
    
    # Run demo sections
    check_upid_cli
    demo_cluster_overview
    demo_cost_analysis
    demo_idle_detection
    demo_optimization_recommendations
    demo_executive_summary
    
    echo
    print_section "Demo Complete"
    echo -e "${GREEN}🎉 Executive demo completed successfully!${NC}"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "   • Schedule technical deep-dive demo"
    echo "   • Request pilot program setup"
    echo "   • Discuss enterprise pricing"
    echo
    echo -e "${CYAN}Thank you for your time!${NC}"
}

# Run the demo
main "$@" 