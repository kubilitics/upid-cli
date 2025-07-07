#!/usr/bin/env python3
"""
Test runner for UPID CLI
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def run_unit_tests():
    """Run unit tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/", 
        "-v", 
        "--tb=short",
        "--cov=upid",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/unit",
        "--cov-report=xml:coverage/unit.xml"
    ]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/integration/", 
        "-v", 
        "--tb=short",
        "-m", "integration",
        "--cov=upid",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/integration",
        "--cov-report=xml:coverage/integration.xml"
    ]
    return run_command(cmd, "Integration Tests")


def run_k8s_tests():
    """Run Kubernetes integration tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/integration/test_k8s_integration.py", 
        "-v", 
        "--tb=short",
        "-m", "k8s",
        "--cov=upid",
        "--cov-report=term-missing"
    ]
    return run_command(cmd, "Kubernetes Integration Tests")


def run_api_tests():
    """Run API integration tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/integration/test_api_integration.py", 
        "-v", 
        "--tb=short",
        "-m", "api",
        "--cov=upid",
        "--cov-report=term-missing"
    ]
    return run_command(cmd, "API Integration Tests")


def run_zero_pod_tests():
    """Run zero-pod scaling tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "-m", "zero_pod",
        "--cov=upid",
        "--cov-report=term-missing"
    ]
    return run_command(cmd, "Zero-Pod Scaling Tests")


def run_all_tests():
    """Run all tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--cov=upid",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml"
    ]
    return run_command(cmd, "All Tests")


def run_linting():
    """Run code linting"""
    cmd = [
        "python", "-m", "flake8", 
        "upid/", 
        "--max-line-length=100",
        "--ignore=E203,W503"
    ]
    return run_command(cmd, "Code Linting")


def run_type_checking():
    """Run type checking"""
    cmd = [
        "python", "-m", "mypy", 
        "upid/", 
        "--ignore-missing-imports",
        "--no-strict-optional"
    ]
    return run_command(cmd, "Type Checking")


def run_formatting_check():
    """Run code formatting check"""
    cmd = [
        "python", "-m", "black", 
        "--check", 
        "--diff",
        "upid/"
    ]
    return run_command(cmd, "Code Formatting Check")


def run_security_check():
    """Run security checks"""
    cmd = [
        "python", "-m", "bandit", 
        "-r", 
        "upid/",
        "-f", "json",
        "-o", "security_report.json"
    ]
    return run_command(cmd, "Security Check")


def run_performance_tests():
    """Run performance tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "-m", "performance",
        "--durations=10"
    ]
    return run_command(cmd, "Performance Tests")


def run_stress_tests():
    """Run stress tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "-m", "stress",
        "--durations=30"
    ]
    return run_command(cmd, "Stress Tests")


def setup_test_environment():
    """Setup test environment"""
    print("🔧 Setting up test environment...")
    
    # Create necessary directories
    Path("htmlcov").mkdir(exist_ok=True)
    Path("coverage").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    
    # Install test dependencies
    cmd = [
        "pip", "install", "-r", "requirements-dev.txt"
    ]
    return run_command(cmd, "Installing Test Dependencies")


def generate_test_report():
    """Generate test report"""
    print("📊 Generating test report...")
    
    # Combine coverage reports
    cmd = [
        "python", "-m", "coverage", "combine", 
        "coverage/unit.xml", 
        "coverage/integration.xml"
    ]
    run_command(cmd, "Combining Coverage Reports")
    
    # Generate HTML report
    cmd = [
        "python", "-m", "coverage", "html", 
        "--directory=htmlcov/combined"
    ]
    return run_command(cmd, "Generating Combined HTML Report")


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="UPID CLI Test Runner")
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="Run integration tests only"
    )
    parser.add_argument(
        "--k8s", 
        action="store_true", 
        help="Run Kubernetes tests only"
    )
    parser.add_argument(
        "--api", 
        action="store_true", 
        help="Run API tests only"
    )
    parser.add_argument(
        "--zero-pod", 
        action="store_true", 
        help="Run zero-pod scaling tests only"
    )
    parser.add_argument(
        "--lint", 
        action="store_true", 
        help="Run linting only"
    )
    parser.add_argument(
        "--type-check", 
        action="store_true", 
        help="Run type checking only"
    )
    parser.add_argument(
        "--format", 
        action="store_true", 
        help="Run formatting check only"
    )
    parser.add_argument(
        "--security", 
        action="store_true", 
        help="Run security checks only"
    )
    parser.add_argument(
        "--performance", 
        action="store_true", 
        help="Run performance tests only"
    )
    parser.add_argument(
        "--stress", 
        action="store_true", 
        help="Run stress tests only"
    )
    parser.add_argument(
        "--setup", 
        action="store_true", 
        help="Setup test environment only"
    )
    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Generate test report only"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Run all tests and checks"
    )
    
    args = parser.parse_args()
    
    # Setup environment if requested
    if args.setup:
        setup_test_environment()
        return
    
    # Generate report if requested
    if args.report:
        generate_test_report()
        return
    
    # Run specific test types
    success = True
    
    if args.unit:
        success &= run_unit_tests()
    elif args.integration:
        success &= run_integration_tests()
    elif args.k8s:
        success &= run_k8s_tests()
    elif args.api:
        success &= run_api_tests()
    elif args.zero_pod:
        success &= run_zero_pod_tests()
    elif args.lint:
        success &= run_linting()
    elif args.type_check:
        success &= run_type_checking()
    elif args.format:
        success &= run_formatting_check()
    elif args.security:
        success &= run_security_check()
    elif args.performance:
        success &= run_performance_tests()
    elif args.stress:
        success &= run_stress_tests()
    elif args.all:
        # Run all tests and checks
        success &= setup_test_environment()
        success &= run_linting()
        success &= run_type_checking()
        success &= run_formatting_check()
        success &= run_security_check()
        success &= run_unit_tests()
        success &= run_integration_tests()
        success &= run_performance_tests()
        success &= generate_test_report()
    else:
        # Default: run all tests
        success &= run_all_tests()
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 