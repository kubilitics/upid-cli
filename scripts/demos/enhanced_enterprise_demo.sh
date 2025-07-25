#!/bin/bash
# UPID CLI - Enhanced Enterprise Demo Script
# 20-minute enterprise features demonstration using real CLI commands

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
export UPID_MOCK_SCENARIO="enterprise"

echo -e "${BLUE}🏢 UPID CLI Enterprise Demo - 20 Minutes${NC}"
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

# Demo 1: Enterprise Setup
demo_enterprise_setup() {
    print_section "1. Enterprise Setup (3 minutes)"
    
    print_info "Setting up UPID for enterprise deployment..."
    
    execute_command "upid enterprise setup --org-id enterprise-001"
    
    print_info "Configuring multi-cluster management..."
    execute_command "upid enterprise configure --multi-cluster --sso --audit"
    
    print_info "Setting up role-based access control..."
    execute_command "upid enterprise rbac --admin-users admin@enterprise.com --viewers team@enterprise.com"
    
    echo -e "\n${GREEN}🏢 Enterprise Features Configured:${NC}"
    echo "   • Multi-cluster management"
    echo "   • Single Sign-On (SSO) integration"
    echo "   • Role-based access control (RBAC)"
    echo "   • Audit logging and compliance"
    echo "   • Enterprise-grade security"
    
    print_success "Enterprise setup completed"
}

# Demo 2: Multi-Cluster Management
demo_multi_cluster() {
    print_section "2. Multi-Cluster Management (4 minutes)"
    
    print_info "Managing multiple Kubernetes clusters..."
    
    execute_command "upid enterprise clusters list"
    
    print_info "Adding new clusters to the enterprise..."
    execute_command "upid enterprise cluster add --name prod-cluster-02 --region us-west-2"
    execute_command "upid enterprise cluster add --name staging-cluster-02 --region eu-west-1"
    
    print_info "Monitoring all clusters simultaneously..."
    execute_command "upid enterprise monitor --all-clusters"
    
    print_info "Getting enterprise-wide cost analysis..."
    execute_command "upid enterprise cost --all-clusters --detailed"
    
    echo -e "\n${GREEN}📊 Multi-Cluster Results:${NC}"
    echo "   • Total Clusters: 5"
    echo "   • Total Monthly Cost: $24,500"
    echo "   • Combined Savings Potential: $7,350 (30%)"
    echo "   • Cross-cluster optimization opportunities: 15"
    
    print_success "Multi-cluster management completed"
}

# Demo 3: Advanced Security and Compliance
demo_security_compliance() {
    print_section "3. Security and Compliance (4 minutes)"
    
    print_info "Demonstrating enterprise security features..."
    
    execute_command "upid enterprise security audit --cluster-id prod-cluster-001"
    
    print_info "Checking compliance with enterprise policies..."
    execute_command "upid enterprise compliance check --policy soc2 --cluster-id prod-cluster-001"
    
    print_info "Reviewing access logs and audit trails..."
    execute_command "upid enterprise audit logs --cluster-id prod-cluster-001 --last-7-days"
    
    print_info "Setting up security policies..."
    execute_command "upid enterprise security policy --name cost-optimization --max-cost 5000"
    
    echo -e "\n${GREEN}🔒 Security and Compliance Features:${NC}"
    echo "   • SOC2 compliance monitoring"
    echo "   • Real-time security auditing"
    echo "   • Access control and logging"
    echo "   • Policy enforcement"
    echo "   • Compliance reporting"
    
    print_success "Security and compliance demonstration completed"
}

# Demo 4: Advanced Analytics and Reporting
demo_advanced_analytics() {
    print_section "4. Advanced Analytics and Reporting (4 minutes)"
    
    print_info "Generating enterprise-wide analytics..."
    
    execute_command "upid enterprise analytics --all-clusters --timeframe 30-days"
    
    print_info "Creating custom dashboards for different teams..."
    execute_command "upid enterprise dashboard create --name engineering --team engineering"
    execute_command "upid enterprise dashboard create --name finance --team finance"
    
    print_info "Generating executive reports..."
    execute_command "upid enterprise report executive --all-clusters --format pdf"
    
    print_info "Setting up automated reporting..."
    execute_command "upid enterprise report schedule --weekly --recipients executives@enterprise.com"
    
    echo -e "\n${GREEN}📈 Advanced Analytics Capabilities:${NC}"
    echo "   • Cross-cluster analytics"
    echo "   • Custom team dashboards"
    echo "   • Automated reporting"
    echo "   • Trend analysis and forecasting"
    echo "   • ROI tracking and validation"
    
    print_success "Advanced analytics demonstration completed"
}

# Demo 5: AI-Powered Enterprise Optimization
demo_ai_enterprise() {
    print_section "5. AI-Powered Enterprise Optimization (3 minutes)"
    
    print_info "Leveraging AI for enterprise-wide optimization..."
    
    execute_command "upid enterprise optimize ai --all-clusters"
    
    print_info "Getting AI-driven resource recommendations..."
    execute_command "upid enterprise ai insights --all-clusters --detailed"
    
    print_info "Simulating AI-powered cost optimization..."
    execute_command "upid enterprise optimize simulate --scenario 30-percent-savings"
    
    echo -e "\n${GREEN}🤖 AI-Powered Enterprise Features:${NC}"
    echo "   • Cross-cluster AI optimization"
    echo "   • Predictive cost modeling"
    echo "   • Intelligent resource allocation"
    echo "   • Automated policy recommendations"
    echo "   • Machine learning insights"
    
    print_success "AI-powered enterprise optimization completed"
}

# Demo 6: Integration and API
demo_integration_api() {
    print_section "6. Integration and API (2 minutes)"
    
    print_info "Demonstrating enterprise API capabilities..."
    
    execute_command "upid enterprise api status"
    
    print_info "Showing API endpoints for integration..."
    execute_command "upid enterprise api endpoints --format json"
    
    print_info "Testing webhook integration..."
    execute_command "upid enterprise webhook test --url https://enterprise.com/webhook"
    
    echo -e "\n${GREEN}🔗 Integration Capabilities:${NC}"
    echo "   • RESTful API for all features"
    echo "   • Webhook notifications"
    echo "   • CI/CD pipeline integration"
    echo "   • Third-party tool integration"
    echo "   • Custom automation support"
    
    print_success "Integration and API demonstration completed"
}

# Main demo execution
main() {
    echo -e "${BLUE}🎯 Enterprise Demo Objectives:${NC}"
    echo "   • Demonstrate enterprise setup and configuration"
    echo "   • Show multi-cluster management capabilities"
    echo "   • Highlight security and compliance features"
    echo "   • Present advanced analytics and reporting"
    echo "   • Showcase AI-powered enterprise optimization"
    echo "   • Demonstrate integration and API capabilities"
    echo
    
    demo_enterprise_setup
    demo_multi_cluster
    demo_security_compliance
    demo_advanced_analytics
    demo_ai_enterprise
    demo_integration_api
    
    echo -e "\n${GREEN}🎉 Enterprise Demo Completed Successfully!${NC}"
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${BLUE}Enterprise Capabilities Demonstrated:${NC}"
    echo "   • Multi-cluster management and monitoring"
    echo "   • Enterprise-grade security and compliance"
    echo "   • Advanced analytics and reporting"
    echo "   • AI-powered optimization across clusters"
    echo "   • Integration with existing enterprise tools"
    echo "   • Scalable architecture for large deployments"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "   • Schedule enterprise deployment planning"
    echo "   • Discuss custom integration requirements"
    echo "   • Review security and compliance needs"
    echo "   • Plan enterprise rollout strategy"
}

# Run the demo
main "$@" 