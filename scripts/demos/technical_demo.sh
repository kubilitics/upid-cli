#!/bin/bash
# UPID CLI - Technical Demo Script
# 15-minute technical deep dive demonstration

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

echo -e "${BLUE}🔧 UPID CLI Technical Demo - 15 Minutes${NC}"
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

# Function to simulate command execution
simulate_command() {
    echo -e "${CYAN}$ $1${NC}"
    sleep 1
}

# Demo 1: Installation and Setup
demo_installation() {
    print_section "1. Installation and Setup (2 minutes)"
    
    print_info "Let's start with the installation process..."
    
    simulate_command "curl -sSL https://install.upid.io | bash"
    print_success "UPID CLI installed successfully"
    
    simulate_command "upid --version"
    echo "UPID CLI v2.0.0"
    
    simulate_command "upid auth login"
    echo "✅ Authentication successful"
    echo "✅ Connected to UPID platform"
    
    print_info "Installation completed in under 2 minutes"
}

# Demo 2: Cluster Discovery
demo_cluster_discovery() {
    print_section "2. Cluster Discovery (2 minutes)"
    
    print_info "Discovering Kubernetes clusters..."
    simulate_loading
    
    simulate_command "upid cluster list"
    echo "📊 Found 3 clusters:"
    echo "   • production-cluster-01 (Healthy) - 150 pods"
    echo "   • staging-cluster-01 (Healthy) - 80 pods"
    echo "   • development-cluster-01 (Warning) - 40 pods"
    
    simulate_command "upid cluster get production-cluster-01"
    echo "🔍 Cluster Details:"
    echo "   • Kubernetes Version: 1.28.2"
    echo "   • Nodes: 12 (8 worker, 4 control-plane)"
    echo "   • Namespaces: 15"
    echo "   • Health Score: 92%"
    echo "   • Efficiency Score: 78%"
    
    print_success "Cluster discovery completed"
}

# Demo 3: Resource Analysis
demo_resource_analysis() {
    print_section "3. Resource Analysis (3 minutes)"
    
    print_info "Analyzing resource utilization..."
    simulate_loading
    
    simulate_command "upid analyze cluster production-cluster-01 --detailed"
    echo "📊 Resource Analysis Results:"
    echo "   • Total Pods: 150"
    echo "   • Idle Pods: 2 (1.33%)"
    echo "   • CPU Utilization: 46.37%"
    echo "   • Memory Utilization: 53.82%"
    echo "   • Network I/O: 2.1 GB/s"
    echo "   • Storage Usage: 1.2 TB"
    
    simulate_command "upid analyze idle production-cluster-01 --confidence 0.7"
    echo "💤 Idle Workload Analysis:"
    echo "   • web-frontend-123 (Development)"
    echo "     - CPU Usage: 8.2%"
    echo "     - Memory Usage: 12.1%"
    echo "     - Network: 0.1 MB/s"
    echo "     - Potential Savings: $176/month"
    echo "     - Confidence: 87%"
    
    print_success "Resource analysis completed"
}

# Demo 4: Cost Analysis
demo_cost_analysis() {
    print_section "4. Cost Analysis (3 minutes)"
    
    print_info "Analyzing cost breakdown..."
    simulate_loading
    
    simulate_command "upid analyze costs production-cluster-01"
    echo "💰 Cost Breakdown:"
    echo "   • Compute: $3,178 (70%)"
    echo "   • Storage: $635 (14%)"
    echo "   • Network: $318 (7%)"
    echo "   • Waste: $642 (14%)"
    echo "   • Total: $4,773/month"
    
    simulate_command "upid analyze costs production-cluster-01 --trend 30d"
    echo "📈 30-Day Cost Trend:"
    echo "   • Average Daily Cost: $159"
    echo "   • Peak Usage: $185 (Weekdays)"
    echo "   • Low Usage: $120 (Weekends)"
    echo "   • Trend: Stable (+2.3%)"
    
    print_warning "14% of costs are wasted on idle resources"
    print_info "Optimization potential: $466/month"
}

# Demo 5: Optimization Strategies
demo_optimization_strategies() {
    print_section "5. Optimization Strategies (3 minutes)"
    
    print_info "Generating optimization recommendations..."
    simulate_loading
    
    simulate_command "upid optimize strategies production-cluster-01"
    echo "⚡ Available Optimization Strategies:"
    echo "   • Zero-pod scaling: $790/month savings (Low risk)"
    echo "   • Resource right-sizing: $450/month savings (Medium risk)"
    echo "   • Node consolidation: $1,200/month savings (Medium risk)"
    echo "   • Storage optimization: $180/month savings (Low risk)"
    echo "   • Network optimization: $95/month savings (Low risk)"
    
    simulate_command "upid optimize simulate production-cluster-01 --strategy zero-pod-scaling"
    echo "🎯 Zero-Pod Scaling Simulation:"
    echo "   • Affected Pods: 2"
    echo "   • Potential Savings: $790/month"
    echo "   • Risk Level: Low"
    echo "   • Confidence: 87%"
    echo "   • Estimated Duration: 2 hours"
    echo "   • Rollback Plan: Available"
    
    print_success "Optimization strategies generated"
}

# Demo 6: AI Insights
demo_ai_insights() {
    print_section "6. AI-Powered Insights (2 minutes)"
    
    print_info "Generating AI insights..."
    simulate_loading
    
    simulate_command "upid ai insights production-cluster-01"
    echo "🤖 AI Insights:"
    echo "   • High idle workload detected (Confidence: 92%)"
    echo "     - Found 15 idle pods that could be scaled to zero"
    echo "     - Potential savings: $450/month"
    echo ""
    echo "   • Resource underutilization (Confidence: 87%)"
    echo "     - CPU usage consistently below 30% on 8 nodes"
    echo "     - Potential savings: $800/month"
    echo ""
    echo "   • Security best practices (Confidence: 78%)"
    echo "     - Consider implementing network policies"
    echo "     - No immediate cost impact"
    
    print_success "AI insights generated"
}

# Demo 7: Reporting
demo_reporting() {
    print_section "7. Reporting and Export (2 minutes)"
    
    print_info "Generating comprehensive reports..."
    simulate_loading
    
    simulate_command "upid report generate production-cluster-01 --type cost"
    echo "📋 Cost Report Generated:"
    echo "   • Report ID: report_475202"
    echo "   • Generated: $(date)"
    echo "   • Format: PDF"
    echo "   • Size: 2.3 MB"
    
    simulate_command "upid report export report_475202 --format json"
    echo "📊 JSON Export:"
    echo "   • Cost breakdown by namespace"
    echo "   • 30-day cost trend"
    echo "   • Optimization recommendations"
    echo "   • ROI calculations"
    
    print_success "Reports generated and exported"
}

# Demo 8: Technical Summary
demo_technical_summary() {
    print_section "8. Technical Summary (1 minute)"
    
    echo -e "${GREEN}🔧 Technical Capabilities Demonstrated:${NC}"
    echo "   ✅ Multi-cluster management"
    echo "   ✅ Real-time resource monitoring"
    echo "   ✅ Intelligent idle workload detection"
    echo "   ✅ Detailed cost analysis and trending"
    echo "   ✅ AI-powered optimization recommendations"
    echo "   ✅ Risk assessment and simulation"
    echo "   ✅ Comprehensive reporting and export"
    echo "   ✅ RESTful API integration"
    echo "   ✅ Kubernetes native integration"
    echo "   ✅ Enterprise-grade security"
    
    echo
    echo -e "${BLUE}📈 Performance Metrics:${NC}"
    echo "   • Analysis Speed: < 30 seconds per cluster"
    echo "   • Accuracy: 95%+ for idle detection"
    echo "   • Scalability: 1000+ clusters supported"
    echo "   • API Response Time: < 200ms"
    echo "   • Resource Usage: < 100MB RAM"
    
    print_success "Technical demo completed successfully"
}

# Main demo flow
main() {
    echo -e "${BLUE}🎯 Technical Demo: Deep Dive into UPID CLI${NC}"
    echo -e "${CYAN}Target: DevOps engineers, SREs, and technical leads${NC}"
    echo -e "${CYAN}Duration: 15 minutes${NC}"
    echo -e "${CYAN}Focus: Technical capabilities, implementation, and integration${NC}"
    echo
    
    # Run demo sections
    demo_installation
    demo_cluster_discovery
    demo_resource_analysis
    demo_cost_analysis
    demo_optimization_strategies
    demo_ai_insights
    demo_reporting
    demo_technical_summary
    
    echo
    print_section "Demo Complete"
    echo -e "${GREEN}🎉 Technical demo completed successfully!${NC}"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "   • Schedule proof-of-concept deployment"
    echo "   • Request technical documentation"
    echo "   • Discuss integration requirements"
    echo "   • Plan pilot program"
    echo
    echo -e "${CYAN}Thank you for your time!${NC}"
}

# Run the demo
main "$@" 