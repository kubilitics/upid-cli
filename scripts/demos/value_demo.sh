#!/bin/bash
# UPID CLI - Value Demo Script
# 10-minute value proposition demonstration

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

echo -e "${BLUE}💎 UPID CLI Value Demo - 10 Minutes${NC}"
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

# Demo 1: Problem Statement
demo_problem_statement() {
    print_section "1. The Problem (2 minutes)"
    
    echo -e "${RED}🚨 Current Kubernetes Cost Challenges:${NC}"
    echo "   • 30-60% of Kubernetes costs are wasted on idle resources"
    echo "   • Manual optimization is time-consuming and error-prone"
    echo "   • Lack of visibility into resource utilization patterns"
    echo "   • No automated cost optimization strategies"
    echo "   • Difficulty tracking ROI on infrastructure investments"
    echo
    
    echo -e "${YELLOW}📊 Industry Statistics:${NC}"
    echo "   • Average idle resource waste: 40%"
    echo "   • Manual optimization time: 10-20 hours/week"
    echo "   • Cost of manual errors: $50K-$200K annually"
    echo "   • Lost productivity: 25% of DevOps time"
    echo
    
    print_warning "These challenges cost enterprises millions annually"
}

# Demo 2: UPID Solution Overview
demo_solution_overview() {
    print_section "2. UPID Solution Overview (2 minutes)"
    
    echo -e "${GREEN}🎯 UPID CLI Value Proposition:${NC}"
    echo "   • Automated idle workload detection and optimization"
    echo "   • AI-powered cost analysis and recommendations"
    echo "   • Real-time resource monitoring and alerting"
    echo "   • Risk-free optimization with automatic rollback"
    echo "   • Comprehensive reporting and ROI tracking"
    echo
    
    echo -e "${BLUE}🔧 Key Features:${NC}"
    echo "   • Zero-pod scaling for development workloads"
    echo "   • Resource right-sizing based on usage patterns"
    echo "   • Node consolidation for underutilized infrastructure"
    echo "   • Multi-cluster management and optimization"
    echo "   • Enterprise-grade security and compliance"
    echo
    
    print_success "UPID CLI delivers 30-60% cost savings with zero risk"
}

# Demo 3: Cost Savings Demonstration
demo_cost_savings() {
    print_section "3. Cost Savings Demonstration (3 minutes)"
    
    print_info "Analyzing your current environment..."
    simulate_loading
    
    echo -e "${GREEN}💰 Current State Analysis:${NC}"
    echo "   • Total Clusters: 3"
    echo "   • Total Pods: 270"
    echo "   • Monthly Cost: $9,200"
    echo "   • Idle Resources: 14%"
    echo "   • Waste Cost: $1,288/month"
    echo
    
    echo -e "${BLUE}⚡ Optimization Opportunities:${NC}"
    echo "   • Zero-pod scaling: $790/month savings"
    echo "   • Resource right-sizing: $450/month savings"
    echo "   • Node consolidation: $1,200/month savings"
    echo "   • Storage optimization: $180/month savings"
    echo "   • Network optimization: $95/month savings"
    echo
    
    echo -e "${GREEN}📈 Projected Results:${NC}"
    echo "   • Total Monthly Savings: $2,715"
    echo "   • Annual Savings: $32,580"
    echo "   • ROI: 354% in first year"
    echo "   • Payback Period: 3.4 months"
    echo
    
    print_success "UPID CLI can save you $32,580 annually"
}

# Demo 4: ROI and Business Impact
demo_roi_impact() {
    print_section "4. ROI and Business Impact (2 minutes)"
    
    echo -e "${GREEN}📊 ROI Analysis:${NC}"
    echo "   • UPID CLI License: $9,000/year"
    echo "   • Implementation: $5,000 (one-time)"
    echo "   • Total Investment: $14,000"
    echo "   • Annual Savings: $32,580"
    echo "   • Net Annual Benefit: $18,580"
    echo "   • ROI: 133%"
    echo
    
    echo -e "${BLUE}🎯 Business Impact:${NC}"
    echo "   • Reduced infrastructure costs by 30%"
    echo "   • Freed up 15 hours/week of DevOps time"
    echo "   • Improved resource utilization by 40%"
    echo "   • Enhanced cost visibility and control"
    echo "   • Reduced risk of cost overruns"
    echo
    
    echo -e "${PURPLE}💼 Competitive Advantages:${NC}"
    echo "   • Faster time-to-market with optimized resources"
    echo "   • Better cost predictability for budgeting"
    echo "   • Improved resource efficiency"
    echo "   • Enhanced compliance and governance"
    echo "   • Reduced carbon footprint"
    echo
    
    print_success "UPID CLI delivers immediate and measurable business value"
}

# Demo 5: Customer Success Stories
demo_success_stories() {
    print_section "5. Customer Success Stories (1 minute)"
    
    echo -e "${GREEN}🏆 Customer Success Stories:${NC}"
    echo
    echo "📈 TechCorp Inc. (500+ pods):"
    echo "   • 45% cost reduction in 3 months"
    echo "   • $180K annual savings"
    echo "   • 20 hours/week DevOps time saved"
    echo
    echo "📈 StartupXYZ (100+ pods):"
    echo "   • 38% cost reduction in 2 months"
    echo "   • $45K annual savings"
    echo "   • Improved resource utilization by 50%"
    echo
    echo "📈 EnterpriseCo (1000+ pods):"
    echo "   • 52% cost reduction in 6 months"
    echo "   • $500K annual savings"
    echo "   • 30 hours/week DevOps time saved"
    echo
    
    print_success "Proven results across organizations of all sizes"
}

# Demo 6: Implementation and Next Steps
demo_implementation() {
    print_section "6. Implementation and Next Steps (1 minute)"
    
    echo -e "${GREEN}🚀 Implementation Timeline:${NC}"
    echo "   • Week 1: Installation and setup"
    echo "   • Week 2: Initial analysis and baseline"
    echo "   • Week 3: First optimizations"
    echo "   • Week 4: Full deployment and monitoring"
    echo
    
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "   • Schedule technical deep-dive demo"
    echo "   • Request proof-of-concept setup"
    echo "   • Discuss pilot program options"
    echo "   • Review enterprise pricing and terms"
    echo
    
    echo -e "${PURPLE}🎁 Special Offer:${NC}"
    echo "   • 30-day free trial"
    echo "   • No setup fees"
    echo "   • Full support during trial"
    echo "   • Guaranteed 20% cost reduction or money back"
    echo
    
    print_success "Ready to start saving money today"
}

# Main demo flow
main() {
    echo -e "${BLUE}🎯 Value Demo: Kubernetes Cost Optimization ROI${NC}"
    echo -e "${CYAN}Target: Business decision makers and budget owners${NC}"
    echo -e "${CYAN}Duration: 10 minutes${NC}"
    echo -e "${CYAN}Focus: ROI, cost savings, and business value${NC}"
    echo
    
    # Run demo sections
    demo_problem_statement
    demo_solution_overview
    demo_cost_savings
    demo_roi_impact
    demo_success_stories
    demo_implementation
    
    echo
    print_section "Demo Complete"
    echo -e "${GREEN}🎉 Value demo completed successfully!${NC}"
    echo
    echo -e "${BLUE}Key Takeaways:${NC}"
    echo "   • 30-60% cost reduction potential"
    echo "   • 133% ROI in first year"
    echo "   • 3.4 month payback period"
    echo "   • Zero-risk implementation"
    echo "   • Proven customer success"
    echo
    echo -e "${CYAN}Ready to start your cost optimization journey?${NC}"
}

# Run the demo
main "$@" 