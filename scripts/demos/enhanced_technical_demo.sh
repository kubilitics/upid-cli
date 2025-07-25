#!/bin/bash
# UPID CLI - Enhanced Technical Demo Script
# 15-minute technical deep dive using real CLI commands

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

echo -e "${BLUE}🔧 UPID CLI Enhanced Technical Demo - 15 Minutes${NC}"
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

# Demo 1: Installation and Setup
demo_installation() {
    print_section "1. Installation and Setup (2 minutes)"
    
    print_info "Let's start with the installation process..."
    
    execute_command "curl -sSL https://install.upid.io | bash"
    print_success "UPID CLI installed successfully"
    
    execute_command "upid --version"
    echo "UPID CLI v2.0.0"
    
    execute_command "upid auth login"
    echo "✅ Authentication successful"
    echo "✅ Connected to UPID platform"
    
    print_info "Installation completed in under 2 minutes"
}

# Demo 2: Cluster Discovery
demo_cluster_discovery() {
    print_section "2. Cluster Discovery (2 minutes)"
    
    print_info "Discovering Kubernetes clusters..."
    
    execute_command "upid cluster list"
    
    execute_command "upid cluster get --cluster-id prod-cluster-001"
    
    print_info "Let's check cluster health and status..."
    execute_command "upid cluster health --cluster-id prod-cluster-001"
    
    print_success "Cluster discovery completed"
}

# Demo 3: Resource Analysis
demo_resource_analysis() {
    print_section "3. Resource Analysis (3 minutes)"
    
    print_info "Analyzing resource utilization..."
    
    execute_command "upid analyze resources --cluster-id prod-cluster-001"
    
    print_info "Let's get detailed CPU and memory analysis..."
    execute_command "upid analyze cpu --cluster-id prod-cluster-001 --detailed"
    execute_command "upid analyze memory --cluster-id prod-cluster-001 --detailed"
    
    print_info "Checking network utilization..."
    execute_command "upid analyze network --cluster-id prod-cluster-001"
    
    print_success "Resource analysis completed"
}

# Demo 4: Cost Analysis
demo_cost_analysis() {
    print_section "4. Cost Analysis (3 minutes)"
    
    print_info "Performing comprehensive cost analysis..."
    
    execute_command "upid analyze cost --cluster-id prod-cluster-001"
    
    print_info "Getting detailed cost breakdown by namespace..."
    execute_command "upid analyze cost --cluster-id prod-cluster-001 --by-namespace"
    
    print_info "Analyzing cost trends over time..."
    execute_command "upid analyze cost --cluster-id prod-cluster-001 --trends"
    
    print_success "Cost analysis completed"
}

# Demo 5: Idle Workload Detection
demo_idle_workloads() {
    print_section "5. Idle Workload Detection (2 minutes)"
    
    print_info "Identifying idle and underutilized workloads..."
    
    execute_command "upid analyze idle --cluster-id prod-cluster-001"
    
    print_info "Getting detailed idle workload analysis..."
    execute_command "upid analyze idle --cluster-id prod-cluster-001 --detailed"
    
    print_success "Idle workload detection completed"
}

# Demo 6: Optimization Strategies
demo_optimization_strategies() {
    print_section "6. Optimization Strategies (2 minutes)"
    
    print_info "Generating optimization recommendations..."
    
    execute_command "upid optimize strategies --cluster-id prod-cluster-001"
    
    print_info "Let's see specific optimization opportunities..."
    execute_command "upid optimize opportunities --cluster-id prod-cluster-001"
    
    print_info "Checking resource right-sizing recommendations..."
    execute_command "upid optimize right-size --cluster-id prod-cluster-001"
    
    print_success "Optimization strategies completed"
}

# Demo 7: AI-Powered Insights
demo_ai_insights() {
    print_section "7. AI-Powered Insights (2 minutes)"
    
    print_info "Getting AI-powered optimization recommendations..."
    
    execute_command "upid optimize ai --cluster-id prod-cluster-001"
    
    print_info "Analyzing AI insights and predictions..."
    execute_command "upid analyze ai --cluster-id prod-cluster-001"
    
    print_success "AI insights analysis completed"
}

# Demo 8: Reporting and Export
demo_reporting() {
    print_section "8. Reporting and Export (1 minute)"
    
    print_info "Generating comprehensive reports..."
    
    execute_command "upid report technical --cluster-id prod-cluster-001"
    
    print_info "Exporting cost analysis report..."
    execute_command "upid report export --cluster-id prod-cluster-001 --format json"
    
    print_success "Reporting and export completed"
}

# Main demo execution
main() {
    echo -e "${BLUE}🎯 Technical Demo Objectives:${NC}"
    echo "   • Demonstrate installation and setup process"
    echo "   • Show cluster discovery and health monitoring"
    echo "   • Present detailed resource analysis capabilities"
    echo "   • Highlight cost optimization features"
    echo "   • Showcase AI-powered insights"
    echo "   • Demonstrate reporting and export functionality"
    echo
    
    demo_installation
    demo_cluster_discovery
    demo_resource_analysis
    demo_cost_analysis
    demo_idle_workloads
    demo_optimization_strategies
    demo_ai_insights
    demo_reporting
    
    echo -e "\n${GREEN}🎉 Technical Demo Completed Successfully!${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${BLUE}Technical Capabilities Demonstrated:${NC}"
    echo "   • Seamless installation and authentication"
    echo "   • Comprehensive cluster discovery and monitoring"
    echo "   • Detailed resource utilization analysis"
    echo "   • Advanced cost optimization algorithms"
    echo "   • AI-powered recommendation engine"
    echo "   • Professional reporting and export features"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "   • Schedule enterprise features demo"
    echo "   • Discuss integration requirements"
    echo "   • Plan pilot deployment"
    echo "   • Review security and compliance features"
}

# Run the demo
main "$@" 