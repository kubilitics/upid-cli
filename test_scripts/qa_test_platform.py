#!/usr/bin/env python3
"""
UPID CLI - Comprehensive QA Testing Platform
============================================

This script tests every command in UPID CLI and generates a detailed QA report.
It validates functionality, expected outputs, and business value for each command.

Usage: python test_scripts/qa_test_platform.py [--binary-path PATH] [--output-format json|html|markdown]
"""

import subprocess
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import argparse

class TestStatus(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    SKIP = "⏭️ SKIP"
    WARNING = "⚠️ WARNING"

@dataclass
class CommandTest:
    """Represents a single command test case"""
    command: str
    description: str
    business_value: str
    why_this_command: str
    expected_output: str
    actual_output: str = ""
    status: TestStatus = TestStatus.SKIP
    execution_time: float = 0.0
    error_message: str = ""

class UPIDQATester:
    """Comprehensive QA testing platform for UPID CLI"""
    
    def __init__(self, binary_path: str = "./dist/upid-darwin-arm64"):
        self.binary_path = binary_path
        self.test_results: List[CommandTest] = []
        self.start_time = time.time()
        
    def run_command(self, command: str, timeout: int = 30) -> tuple[str, str, float]:
        """Execute a command and return output, error, and execution time"""
        start_time = time.time()
        try:
            result = subprocess.run(
                [self.binary_path] + command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            execution_time = time.time() - start_time
            return result.stdout, result.stderr, execution_time
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return "", f"Command timed out after {timeout}s", execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            return "", str(e), execution_time
    
    def test_command(self, test_case: CommandTest) -> CommandTest:
        """Execute a single command test"""
        print(f"Testing: {test_case.command}")
        
        stdout, stderr, exec_time = self.run_command(test_case.command)
        test_case.actual_output = stdout + stderr
        test_case.execution_time = exec_time
        
        # Determine test status
        if "error" in stderr.lower() or "failed" in stderr.lower():
            test_case.status = TestStatus.FAIL
            test_case.error_message = stderr
        elif test_case.expected_output and test_case.expected_output.lower() in test_case.actual_output.lower():
            test_case.status = TestStatus.PASS
        elif stdout and not stderr:
            test_case.status = TestStatus.PASS
        else:
            test_case.status = TestStatus.WARNING
            
        return test_case
    
    def define_test_cases(self) -> List[CommandTest]:
        """Define all test cases for UPID CLI commands"""
        return [
            # ============================================================================
            # CORE CLI COMMANDS
            # ============================================================================
            
            CommandTest(
                command="--help",
                description="Display CLI help information",
                business_value="Enables users to understand available commands and options",
                why_this_command="Essential for user onboarding and command discovery",
                expected_output="Usage:",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="--version",
                description="Display CLI version information",
                business_value="Helps users identify installed version and check for updates",
                why_this_command="Critical for version management and support troubleshooting",
                expected_output="upid",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # STATUS COMMANDS
            # ============================================================================
            
            CommandTest(
                command="--local status",
                description="Show current CLI status and configuration in local mode",
                business_value="Provides system health check and configuration overview",
                why_this_command="Essential for troubleshooting and system monitoring",
                expected_output="UPID CLI Status",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="status",
                description="Show current CLI status and configuration",
                business_value="Provides system health check and authentication status",
                why_this_command="Critical for user awareness of system state",
                expected_output="UPID CLI Status",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # AUTHENTICATION COMMANDS
            # ============================================================================
            
            CommandTest(
                command="auth login --help",
                description="Display authentication login help",
                business_value="Guides users through secure authentication process",
                why_this_command="Essential for secure access to UPID services",
                expected_output="login",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="auth logout --help",
                description="Display authentication logout help",
                business_value="Enables secure session termination",
                why_this_command="Important for security and session management",
                expected_output="logout",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="auth status --help",
                description="Display authentication status help",
                business_value="Shows current authentication state",
                why_this_command="Helps users understand their login status",
                expected_output="status",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # CLUSTER MANAGEMENT COMMANDS
            # ============================================================================
            
            CommandTest(
                command="cluster --help",
                description="Display cluster management help",
                business_value="Enables multi-cluster management and discovery",
                why_this_command="Core functionality for Kubernetes cluster operations",
                expected_output="cluster",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="cluster list --help",
                description="Display cluster listing help",
                business_value="Shows all available Kubernetes clusters",
                why_this_command="Essential for cluster discovery and management",
                expected_output="list",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="cluster get --help",
                description="Display cluster details help",
                business_value="Provides detailed information about specific clusters",
                why_this_command="Enables deep cluster analysis and troubleshooting",
                expected_output="get",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="--local cluster list",
                description="List clusters in local mode",
                business_value="Demonstrates cluster discovery without authentication",
                why_this_command="Enables testing and demo scenarios",
                expected_output="cluster",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # ANALYSIS COMMANDS
            # ============================================================================
            
            CommandTest(
                command="analyze --help",
                description="Display analysis commands help",
                business_value="Provides comprehensive cluster analysis capabilities",
                why_this_command="Core feature for resource optimization insights",
                expected_output="analyze",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="analyze resources --help",
                description="Display resource analysis help",
                business_value="Identifies resource usage patterns and optimization opportunities",
                why_this_command="Critical for cost optimization and performance tuning",
                expected_output="resources",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="analyze cost --help",
                description="Display cost analysis help",
                business_value="Provides detailed cost breakdown and savings opportunities",
                why_this_command="Essential for financial optimization and budgeting",
                expected_output="cost",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="analyze performance --help",
                description="Display performance analysis help",
                business_value="Identifies performance bottlenecks and optimization opportunities",
                why_this_command="Critical for application performance and user experience",
                expected_output="performance",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # OPTIMIZATION COMMANDS
            # ============================================================================
            
            CommandTest(
                command="optimize --help",
                description="Display optimization commands help",
                business_value="Enables automated resource optimization and cost savings",
                why_this_command="Core value proposition for cost reduction",
                expected_output="optimize",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="optimize resources --help",
                description="Display resource optimization help",
                business_value="Right-sizes resources for optimal cost-performance ratio",
                why_this_command="Primary optimization method for immediate savings",
                expected_output="resources",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="optimize costs --help",
                description="Display cost optimization help",
                business_value="Identifies and implements cost-saving strategies",
                why_this_command="Direct impact on infrastructure spending",
                expected_output="costs",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="optimize zero-pod --help",
                description="Display zero-pod scaling help",
                business_value="Scales idle pods to zero for maximum cost savings",
                why_this_command="Advanced optimization for idle resource elimination",
                expected_output="zero-pod",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="optimize auto --help",
                description="Display auto-optimization help",
                business_value="Enables automated optimization scheduling",
                why_this_command="Set-and-forget optimization for continuous savings",
                expected_output="auto",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # REPORTING COMMANDS
            # ============================================================================
            
            CommandTest(
                command="report --help",
                description="Display reporting commands help",
                business_value="Provides comprehensive insights and analytics",
                why_this_command="Essential for decision-making and stakeholder communication",
                expected_output="report",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="report cost --help",
                description="Display cost reporting help",
                business_value="Generates detailed cost analysis and savings reports",
                why_this_command="Critical for financial planning and ROI demonstration",
                expected_output="cost",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="report performance --help",
                description="Display performance reporting help",
                business_value="Provides performance metrics and optimization insights",
                why_this_command="Essential for performance monitoring and improvement",
                expected_output="performance",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="report summary --help",
                description="Display summary reporting help",
                business_value="Provides executive-level overview and key metrics",
                why_this_command="Critical for stakeholder communication and decision-making",
                expected_output="summary",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # DEPLOYMENT COMMANDS
            # ============================================================================
            
            CommandTest(
                command="deploy --help",
                description="Display deployment commands help",
                business_value="Enables safe application deployment with rollback capabilities",
                why_this_command="Critical for application lifecycle management",
                expected_output="deploy",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="deploy rollback --help",
                description="Display deployment rollback help",
                business_value="Provides instant rollback for failed deployments",
                why_this_command="Essential for risk mitigation and zero-downtime deployments",
                expected_output="rollback",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="deploy status --help",
                description="Display deployment status help",
                business_value="Shows current deployment health and status",
                why_this_command="Critical for deployment monitoring and troubleshooting",
                expected_output="status",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # UNIVERSAL COMMANDS
            # ============================================================================
            
            CommandTest(
                command="universal --help",
                description="Display universal Kubernetes commands help",
                business_value="Provides cross-cluster Kubernetes operations",
                why_this_command="Enables multi-cluster management and operations",
                expected_output="universal",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="universal get --help",
                description="Display universal get command help",
                business_value="Retrieves resources across multiple clusters",
                why_this_command="Essential for multi-cluster resource management",
                expected_output="get",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="universal apply --help",
                description="Display universal apply command help",
                business_value="Applies configurations across multiple clusters",
                why_this_command="Enables consistent multi-cluster deployments",
                expected_output="apply",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # CONFIGURATION COMMANDS
            # ============================================================================
            
            CommandTest(
                command="init --help",
                description="Display initialization help",
                business_value="Sets up UPID CLI configuration and environment",
                why_this_command="Essential for first-time setup and configuration",
                expected_output="init",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="config --help",
                description="Display configuration help",
                business_value="Manages CLI configuration and settings",
                why_this_command="Enables customization and environment-specific settings",
                expected_output="config",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # DEMO COMMANDS
            # ============================================================================
            
            CommandTest(
                command="demo",
                description="Run UPID CLI demo",
                business_value="Demonstrates key features and capabilities",
                why_this_command="Essential for user onboarding and feature showcase",
                expected_output="UPID CLI Demo",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="demo --help",
                description="Display demo help",
                business_value="Shows available demo options and features",
                why_this_command="Helps users understand demo capabilities",
                expected_output="demo",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # LOCAL MODE COMMANDS
            # ============================================================================
            
            CommandTest(
                command="--local --help",
                description="Display local mode help",
                business_value="Enables testing without authentication",
                why_this_command="Essential for development and testing scenarios",
                expected_output="local",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="--verbose --help",
                description="Display verbose mode help",
                business_value="Provides detailed output for debugging",
                why_this_command="Critical for troubleshooting and development",
                expected_output="verbose",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            # ============================================================================
            # ERROR HANDLING TESTS
            # ============================================================================
            
            CommandTest(
                command="invalid-command",
                description="Test invalid command handling",
                business_value="Ensures graceful error handling and user guidance",
                why_this_command="Critical for user experience and error recovery",
                expected_output="error",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="--invalid-option",
                description="Test invalid option handling",
                business_value="Ensures proper error messages for invalid inputs",
                why_this_command="Essential for user guidance and error prevention",
                expected_output="error",
                actual_output="",
                status=TestStatus.SKIP
            ),
            
            CommandTest(
                command="cluster get invalid-cluster",
                description="Test invalid cluster handling",
                business_value="Ensures proper error handling for non-existent resources",
                why_this_command="Critical for robust error handling",
                expected_output="error",
                actual_output="",
                status=TestStatus.SKIP
            ),
        ]
    
    def run_all_tests(self) -> List[CommandTest]:
        """Execute all test cases"""
        print("🚀 UPID CLI - Comprehensive QA Testing Platform")
        print("=" * 60)
        print(f"Testing binary: {self.binary_path}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        test_cases = self.define_test_cases()
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"[{i}/{total_tests}] Testing: {test_case.command}")
            result = self.test_command(test_case)
            self.test_results.append(result)
            
            # Print immediate result
            print(f"   Status: {result.status.value}")
            if result.status == TestStatus.FAIL:
                print(f"   Error: {result.error_message[:100]}...")
            print()
        
        return self.test_results
    
    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate comprehensive QA report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t.status == TestStatus.PASS])
        failed_tests = len([t for t in self.test_results if t.status == TestStatus.FAIL])
        warning_tests = len([t for t in self.test_results if t.status == TestStatus.WARNING])
        skipped_tests = len([t for t in self.test_results if t.status == TestStatus.SKIP])
        
        execution_time = time.time() - self.start_time
        
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        else:
            return self._generate_markdown_report()
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown format report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t.status == TestStatus.PASS])
        failed_tests = len([t for t in self.test_results if t.status == TestStatus.FAIL])
        warning_tests = len([t for t in self.test_results if t.status == TestStatus.WARNING])
        skipped_tests = len([t for t in self.test_results if t.status == TestStatus.SKIP])
        
        execution_time = time.time() - self.start_time
        
        report = f"""# UPID CLI - Comprehensive QA Test Report

## 📊 Executive Summary

- **Total Tests**: {total_tests}
- **✅ Passed**: {passed_tests}
- **❌ Failed**: {failed_tests}
- **⚠️ Warnings**: {warning_tests}
- **⏭️ Skipped**: {skipped_tests}
- **Success Rate**: {(passed_tests/total_tests*100):.1f}%
- **Execution Time**: {execution_time:.2f}s
- **Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Test Results by Category

### Core CLI Commands
"""
        
        # Group tests by category
        categories = {
            "Core CLI": ["--help", "--version"],
            "Status": ["status", "--local status"],
            "Authentication": ["auth login", "auth logout", "auth status"],
            "Cluster Management": ["cluster", "cluster list", "cluster get"],
            "Analysis": ["analyze", "analyze resources", "analyze cost", "analyze performance"],
            "Optimization": ["optimize", "optimize resources", "optimize costs", "optimize zero-pod", "optimize auto"],
            "Reporting": ["report", "report cost", "report performance", "report summary"],
            "Deployment": ["deploy", "deploy rollback", "deploy status"],
            "Universal": ["universal", "universal get", "universal apply"],
            "Configuration": ["init", "config"],
            "Demo": ["demo"],
            "Local Mode": ["--local", "--verbose"],
            "Error Handling": ["invalid-command", "--invalid-option", "cluster get invalid-cluster"]
        }
        
        for category, commands in categories.items():
            category_tests = [t for t in self.test_results if any(cmd in t.command for cmd in commands)]
            passed = len([t for t in category_tests if t.status == TestStatus.PASS])
            failed = len([t for t in category_tests if t.status == TestStatus.FAIL])
            warning = len([t for t in category_tests if t.status == TestStatus.WARNING])
            
            report += f"""
#### {category}
- **Tests**: {len(category_tests)}
- **✅ Passed**: {passed}
- **❌ Failed**: {failed}
- **⚠️ Warnings**: {warning}
"""
        
        report += """
## 📋 Detailed Test Results

| Command | Description | Business Value | Status | Execution Time |
|---------|-------------|----------------|--------|----------------|
"""
        
        for test in self.test_results:
            status_icon = {
                TestStatus.PASS: "✅",
                TestStatus.FAIL: "❌",
                TestStatus.WARNING: "⚠️",
                TestStatus.SKIP: "⏭️"
            }[test.status]
            
            report += f"| `{test.command}` | {test.description} | {test.business_value} | {status_icon} {test.status.name} | {test.execution_time:.2f}s |\n"
        
        report += f"""
## 🔍 Detailed Analysis

### ✅ Passed Tests ({passed_tests})
"""
        
        for test in self.test_results:
            if test.status == TestStatus.PASS:
                report += f"- **`{test.command}`**: {test.description}\n"
        
        if failed_tests > 0:
            report += f"""
### ❌ Failed Tests ({failed_tests})
"""
            for test in self.test_results:
                if test.status == TestStatus.FAIL:
                    report += f"- **`{test.command}`**: {test.description}\n"
                    report += f"  - Error: {test.error_message[:200]}...\n"
        
        if warning_tests > 0:
            report += f"""
### ⚠️ Warning Tests ({warning_tests})
"""
            for test in self.test_results:
                if test.status == TestStatus.WARNING:
                    report += f"- **`{test.command}`**: {test.description}\n"
        
        report += f"""
## 🎯 Business Impact Analysis

### High-Value Commands (Core Functionality)
- Cluster Management: {len([t for t in self.test_results if 'cluster' in t.command and t.status == TestStatus.PASS])}/{len([t for t in self.test_results if 'cluster' in t.command])} working
- Analysis Commands: {len([t for t in self.test_results if 'analyze' in t.command and t.status == TestStatus.PASS])}/{len([t for t in self.test_results if 'analyze' in t.command])} working
- Optimization Commands: {len([t for t in self.test_results if 'optimize' in t.command and t.status == TestStatus.PASS])}/{len([t for t in self.test_results if 'optimize' in t.command])} working
- Reporting Commands: {len([t for t in self.test_results if 'report' in t.command and t.status == TestStatus.PASS])}/{len([t for t in self.test_results if 'report' in t.command])} working

### Production Readiness Assessment
- **Core Functionality**: {'✅ READY' if passed_tests/total_tests > 0.8 else '❌ NEEDS WORK'}
- **Error Handling**: {'✅ ROBUST' if len([t for t in self.test_results if 'error' in t.command.lower() and t.status == TestStatus.PASS]) > 0 else '❌ NEEDS IMPROVEMENT'}
- **User Experience**: {'✅ EXCELLENT' if warning_tests == 0 else '⚠️ NEEDS ATTENTION'}

## 🚀 Recommendations

### Immediate Actions
"""
        
        if failed_tests > 0:
            report += "- Fix failed tests before production release\n"
        if warning_tests > 0:
            report += "- Address warning tests for better user experience\n"
        if passed_tests/total_tests < 0.9:
            report += "- Improve test coverage to reach 90%+ success rate\n"
        
        report += """
### Production Readiness
- **✅ READY FOR PRODUCTION** if success rate > 90% and no critical failures
- **⚠️ NEEDS REVIEW** if success rate < 90% or critical functionality failing
- **❌ NOT READY** if core functionality failing

---
*Report generated by UPID CLI QA Testing Platform*
"""
        
        return report
    
    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        report_data = {
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len([t for t in self.test_results if t.status == TestStatus.PASS]),
                "failed": len([t for t in self.test_results if t.status == TestStatus.FAIL]),
                "warnings": len([t for t in self.test_results if t.status == TestStatus.WARNING]),
                "skipped": len([t for t in self.test_results if t.status == TestStatus.SKIP]),
                "success_rate": len([t for t in self.test_results if t.status == TestStatus.PASS]) / len(self.test_results) * 100,
                "execution_time": time.time() - self.start_time,
                "test_date": datetime.now().isoformat()
            },
            "tests": [
                {
                    "command": t.command,
                    "description": t.description,
                    "business_value": t.business_value,
                    "why_this_command": t.why_this_command,
                    "expected_output": t.expected_output,
                    "actual_output": t.actual_output,
                    "status": t.status.name,
                    "execution_time": t.execution_time,
                    "error_message": t.error_message
                }
                for t in self.test_results
            ]
        }
        return json.dumps(report_data, indent=2)
    
    def _generate_html_report(self) -> str:
        """Generate HTML format report"""
        # This would be a comprehensive HTML report with styling
        # For brevity, returning a simple HTML structure
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>UPID CLI QA Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>UPID CLI - QA Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {len(self.test_results)}</p>
        <p class="pass">Passed: {len([t for t in self.test_results if t.status == TestStatus.PASS])}</p>
        <p class="fail">Failed: {len([t for t in self.test_results if t.status == TestStatus.FAIL])}</p>
        <p class="warning">Warnings: {len([t for t in self.test_results if t.status == TestStatus.WARNING])}</p>
    </div>
    <h2>Detailed Results</h2>
    <table>
        <tr><th>Command</th><th>Status</th><th>Description</th></tr>
        {''.join(f'<tr><td>{t.command}</td><td class="{t.status.name.lower()}">{t.status.value}</td><td>{t.description}</td></tr>' for t in self.test_results)}
    </table>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="UPID CLI QA Testing Platform")
    parser.add_argument("--binary-path", default="./releases/upid-darwin-arm64", 
                       help="Path to UPID CLI binary")
    parser.add_argument("--output-format", choices=["json", "html", "markdown"], 
                       default="markdown", help="Output format for report")
    parser.add_argument("--output-file", help="Output file path")
    
    args = parser.parse_args()
    
    # Check if binary exists
    if not os.path.exists(args.binary_path):
        print(f"❌ Error: Binary not found at {args.binary_path}")
        sys.exit(1)
    
    # Run QA tests
    tester = UPIDQATester(args.binary_path)
    results = tester.run_all_tests()
    
    # Generate report
    report = tester.generate_report(args.output_format)
    
    # Output report
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(report)
        print(f"✅ Report saved to: {args.output_file}")
    else:
        print("\n" + "="*60)
        print("📋 QA TEST REPORT")
        print("="*60)
        print(report)

if __name__ == "__main__":
    main() 