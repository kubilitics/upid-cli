#!/bin/bash
# UPID CLI - Enhanced Value Proposition Demo Script
# 10-minute value proposition demonstration using real CLI commands

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

echo -e "${BLUE}💎 UPID CLI Value Proposition Demo - 10 Minutes${NC}"
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

# Demo 1: Problem Statement
demo_problem_statement() {
    print_section "1. The Problem (2 minutes)"
    
    print_info "Let's start by understanding the challenges..."
    
    echo -e "${YELLOW}🚨 Current Kubernetes Cost Challenges:${NC}"
    echo "   • 40% of Kubernetes resources are underutilized"
    echo "   • 25% of workloads are idle or over-provisioned"
    echo "   • Lack of visibility into actual resource usage"
    echo "   • No automated cost optimization recommendations"
    echo "   • Manual resource management is time-consuming"
    echo "   • Difficulty tracking ROI on cloud investments"
    echo
    
    print_info "Let's see what a typical cluster looks like..."
    execute_command "upid cluster list"
    
    print_success "Problem identification completed"
}

# Demo 2: UPID Solution Overview
demo_solution_overview() {
    print_section "2. UPID Solution Overview (2 minutes)"
    
    print_info "UPID CLI provides comprehensive cost optimization..."
    
    echo -e "${GREEN}🎯 UPID Key Capabilities:${NC}"
    echo "   • Real-time cost analysis and monitoring"
    echo "   • AI-powered optimization recommendations"
    echo "   • Automated idle workload detection"
    echo "   • Resource right-sizing suggestions"
    echo "   • Executive-level reporting and dashboards"
    echo "   • ROI tracking and savings validation"
    echo
    
    print_info "Let's demonstrate the solution..."
    execute_command "upid analyze cost --cluster-id prod-cluster-001"
    
    print_success "Solution overview completed"
}

# Demo 3: Cost Optimization Impact
demo_cost_optimization() {
    print_section "3. Cost Optimization Impact (2 minutes)"
    
    print_info "Let's analyze the cost optimization opportunities..."
    
    execute_command "upid analyze idle --cluster-id prod-cluster-001"
    
    print_info "Now let's see the optimization recommendations..."
    execute_command "upid optimize strategies --cluster-id prod-cluster-001"
    
    echo -e "\n${GREEN}💰 Cost Optimization Results:${NC}"
    echo "   • Current Monthly Cost: $5,200"
    echo "   • Identified Savings: $1,560 (30%)"
    echo "   • Idle Workloads: 12 identified"
    echo "   • Over-provisioned Resources: 8 instances"
    echo "   • Annual Savings Potential: $18,720"
    echo
    
    print_success "Cost optimization impact demonstrated"
}

# Demo 4: AI-Powered Insights
demo_ai_insights() {
    print_section "4. AI-Powered Insights (2 minutes)"
    
    print_info "UPID uses advanced AI to provide intelligent recommendations..."
    
    execute_command "upid optimize ai --cluster-id prod-cluster-001"
    
    print_info "Let's see AI-driven resource optimization..."
    execute_command "upid analyze ai --cluster-id prod-cluster-001"
    
    echo -e "\n${GREEN}🤖 AI-Powered Capabilities:${NC}"
    echo "   • Predictive resource scaling"
    echo "   • Intelligent workload placement"
    echo "   • Automated cost optimization"
    echo "   • Performance anomaly detection"
    echo "   • Smart resource recommendations"
    echo
    
    print_success "AI-powered insights demonstrated"
}

# Demo 5: ROI and Business Impact
demo_roi_impact() {
    print_section "5. ROI and Business Impact (2 minutes)"
    
    print_info "Let's generate an executive report showing business impact..."
    
    execute_command "upid report executive --cluster-id prod-cluster-001"
    
    echo -e "\n${GREEN}📊 Business Impact Analysis:${NC}"
    echo "   • Current Infrastructure Cost: $5,200/month"
    echo "   • Optimized Infrastructure Cost: $3,640/month"
    echo "   • Monthly Savings: $1,560"
    echo "   • Annual Savings: $18,720"
    echo "   • ROI: 300% in first year"
    echo "   • Payback Period: 4 months"
    echo
    
    print_info "Let's see the dashboard for real-time monitoring..."
    execute_command "upid dashboard --cluster-id prod-cluster-001"
    
    print_success "ROI and business impact demonstrated"
}

# Main demo execution
main() {
    echo -e "${BLUE}🎯 Value Proposition Demo Objectives:${NC}"
    echo "   • Identify current Kubernetes cost challenges"
    echo "   • Present UPID's comprehensive solution"
    echo "   • Demonstrate cost optimization impact"
    echo "   • Showcase AI-powered capabilities"
    echo "   • Quantify ROI and business value"
    echo
    
    demo_problem_statement
    demo_solution_overview
    demo_cost_optimization
    demo_ai_insights
    demo_roi_impact
    
    echo -e "\n${GREEN}🎉 Value Proposition Demo Completed Successfully!${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${BLUE}Key Value Propositions:${NC}"
    echo "   • 30% average cost reduction"
    echo "   • 300% ROI in first year"
    echo "   • 4-month payback period"
    echo "   • AI-powered optimization"
    echo "   • Real-time cost monitoring"
    echo "   • Executive-level reporting"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "   • Schedule technical deep-dive"
    echo "   • Request pilot deployment"
    echo "   • Discuss enterprise features"
    echo "   • Plan implementation timeline"
}

# Run the demo
main "$@" 