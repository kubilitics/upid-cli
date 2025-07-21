#!/usr/bin/env python3
"""
Real environment test runner for UPID CLI
Runs integration, performance, and stress tests with real clusters
"""
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional


def run_command(cmd: List[str], description: str, timeout: int = 300) -> Dict:
    """Run a command and return results"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ {description} completed successfully ({execution_time:.2f}s)")
        if result.stdout:
            print(f"Output: {result.stdout[:200]}...")
        
        return {
            "success": True,
            "execution_time": execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"❌ {description} failed ({execution_time:.2f}s)")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        
        return {
            "success": False,
            "execution_time": execution_time,
            "stdout": e.stdout,
            "stderr": e.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after {timeout}s")
        return {
            "success": False,
            "execution_time": timeout,
            "stdout": "",
            "stderr": "Command timed out"
        }


def run_real_integration_tests():
    """Run real integration tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/real_integration/", 
        "-v", 
        "--tb=short",
        "-m", "real_cli",
        "--cov=upid",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/real_integration",
        "--cov-report=xml:coverage/real_integration.xml",
        "--durations=10"
    ]
    return run_command(cmd, "Real Integration Tests", timeout=600)


def run_real_performance_tests():
    """Run real performance tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/real_performance/", 
        "-v", 
        "--tb=short",
        "-m", "performance",
        "--durations=20",
        "--benchmark-only"
    ]
    return run_command(cmd, "Real Performance Tests", timeout=900)


def run_real_stress_tests():
    """Run real stress tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/real_performance/test_performance_benchmarks.py::TestPerformanceBenchmarks::test_stress_test",
        "-v", 
        "--tb=short",
        "-m", "performance",
        "--durations=30"
    ]
    return run_command(cmd, "Real Stress Tests", timeout=1200)


def run_real_cli_commands():
    """Run real CLI command tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/real_integration/test_real_cli_commands.py", 
        "-v", 
        "--tb=short",
        "-m", "real_cli",
        "--durations=15"
    ]
    return run_command(cmd, "Real CLI Command Tests", timeout=600)


def run_real_environment_setup():
    """Test real environment setup"""
    cmd = [
        "python", "-c", 
        "from tests.real_environment.cluster_setup import RealClusterManager, ClusterConfig; "
        "manager = RealClusterManager(); "
        "config = ClusterConfig(name='test-setup', provider='kind', version='v1.24.0'); "
        "print('Real environment setup test completed')"
    ]
    return run_command(cmd, "Real Environment Setup Test", timeout=300)


def run_real_cluster_operations():
    """Test real cluster operations"""
    cmd = [
        "python", "-c", 
        "from tests.real_environment.cluster_setup import RealClusterManager, ClusterConfig, ApplicationConfig; "
        "manager = RealClusterManager(); "
        "config = ClusterConfig(name='test-ops', provider='kind', version='v1.24.0'); "
        "success = manager.create_kind_cluster(config); "
        "print(f'Cluster creation: {success}'); "
        "if success: "
        "  apps = [ApplicationConfig(name='test-app', namespace='default', replicas=1, image='nginx:alpine')]; "
        "  deploy_success = manager.deploy_test_applications('test-ops', apps); "
        "  print(f'App deployment: {deploy_success}'); "
        "  manager.cleanup_cluster('test-ops'); "
        "print('Real cluster operations test completed')"
    ]
    return run_command(cmd, "Real Cluster Operations Test", timeout=600)


def run_real_monitoring_setup():
    """Test real monitoring setup"""
    cmd = [
        "python", "-c", 
        "from tests.real_environment.cluster_setup import RealClusterManager, ClusterConfig; "
        "manager = RealClusterManager(); "
        "config = ClusterConfig(name='test-monitoring', provider='kind', version='v1.24.0'); "
        "success = manager.create_kind_cluster(config); "
        "print(f'Cluster creation: {success}'); "
        "if success: "
        "  monitoring_success = manager.setup_monitoring('test-monitoring'); "
        "  print(f'Monitoring setup: {monitoring_success}'); "
        "  manager.cleanup_cluster('test-monitoring'); "
        "print('Real monitoring setup test completed')"
    ]
    return run_command(cmd, "Real Monitoring Setup Test", timeout=600)


def run_real_data_generation():
    """Test real data generation"""
    cmd = [
        "python", "-c", 
        "from tests.real_environment.cluster_setup import RealClusterManager, ClusterConfig; "
        "manager = RealClusterManager(); "
        "config = ClusterConfig(name='test-data', provider='kind', version='v1.24.0'); "
        "success = manager.create_kind_cluster(config); "
        "print(f'Cluster creation: {success}'); "
        "if success: "
        "  data_success = manager.generate_test_data('test-data', duration_hours=1); "
        "  print(f'Data generation: {data_success}'); "
        "  manager.cleanup_cluster('test-data'); "
        "print('Real data generation test completed')"
    ]
    return run_command(cmd, "Real Data Generation Test", timeout=600)


def run_real_benchmarks():
    """Run real performance benchmarks"""
    benchmarks = [
        ("CLI Startup", ["python", "-m", "upid.cli", "--local", "--help"]),
        ("Analyze Resources", ["python", "-m", "upid.cli", "--local", "analyze", "resources", "test-cluster", "--format", "json"]),
        ("Analyze Cost", ["python", "-m", "upid.cli", "--local", "analyze", "cost", "test-cluster", "--format", "json"]),
        ("Cluster List", ["python", "-m", "upid.cli", "--local", "cluster", "list", "--format", "json"]),
        ("Report Dashboard", ["python", "-m", "upid.cli", "--local", "report", "dashboard", "--cluster", "test-cluster", "--format", "json"])
    ]
    
    results = {}
    
    for benchmark_name, cmd in benchmarks:
        print(f"\n📊 Running benchmark: {benchmark_name}")
        
        times = []
        for i in range(3):  # Run 3 times for average
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            end_time = time.time()
            
            if result.returncode == 0:
                execution_time = end_time - start_time
                times.append(execution_time)
                print(f"  Run {i+1}: {execution_time:.2f}s")
            else:
                print(f"  Run {i+1}: Failed")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            results[benchmark_name] = {
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "success": True
            }
            
            print(f"  Average: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)")
        else:
            results[benchmark_name] = {"success": False}
            print(f"  All runs failed")
    
    return results


def generate_real_test_report(results: Dict):
    """Generate a comprehensive test report"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r.get("success", False)),
            "failed": sum(1 for r in results.values() if not r.get("success", False))
        },
        "results": results
    }
    
    # Save report
    report_file = Path("reports/real_test_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Test report saved to: {report_file}")
    
    # Print summary
    print(f"\n🎯 REAL TEST SUMMARY")
    print(f"══════════════════════════════════════════════════════════════")
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success Rate: {report['summary']['passed']/report['summary']['total_tests']*100:.1f}%")
    
    # Print detailed results
    print(f"\n📊 DETAILED RESULTS")
    print(f"══════════════════════════════════════════════════════════════")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
        time_info = f" ({result.get('execution_time', 0):.2f}s)" if result.get("execution_time") else ""
        print(f"{status} {test_name}{time_info}")
    
    return report


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Real Environment Test Runner")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--stress", action="store_true", help="Run stress tests")
    parser.add_argument("--cli", action="store_true", help="Run CLI command tests")
    parser.add_argument("--setup", action="store_true", help="Test environment setup")
    parser.add_argument("--operations", action="store_true", help="Test cluster operations")
    parser.add_argument("--monitoring", action="store_true", help="Test monitoring setup")
    parser.add_argument("--data", action="store_true", help="Test data generation")
    parser.add_argument("--benchmarks", action="store_true", help="Run performance benchmarks")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    print("🚀 UPID CLI Real Environment Test Runner")
    print("══════════════════════════════════════════════════════════════")
    
    results = {}
    
    # Run selected tests
    if args.all or args.integration:
        results["Real Integration Tests"] = run_real_integration_tests()
    
    if args.all or args.performance:
        results["Real Performance Tests"] = run_real_performance_tests()
    
    if args.all or args.stress:
        results["Real Stress Tests"] = run_real_stress_tests()
    
    if args.all or args.cli:
        results["Real CLI Command Tests"] = run_real_cli_commands()
    
    if args.all or args.setup:
        results["Real Environment Setup"] = run_real_environment_setup()
    
    if args.all or args.operations:
        results["Real Cluster Operations"] = run_real_cluster_operations()
    
    if args.all or args.monitoring:
        results["Real Monitoring Setup"] = run_real_monitoring_setup()
    
    if args.all or args.data:
        results["Real Data Generation"] = run_real_data_generation()
    
    if args.all or args.benchmarks:
        benchmark_results = run_real_benchmarks()
        for name, result in benchmark_results.items():
            results[f"Benchmark: {name}"] = result
    
    # If no specific tests selected, run all
    if not any([args.integration, args.performance, args.stress, args.cli, 
                args.setup, args.operations, args.monitoring, args.data, 
                args.benchmarks, args.all]):
        print("No specific tests selected, running all tests...")
        results["Real Integration Tests"] = run_real_integration_tests()
        results["Real Performance Tests"] = run_real_performance_tests()
        results["Real CLI Command Tests"] = run_real_cli_commands()
        results["Real Environment Setup"] = run_real_environment_setup()
        results["Real Cluster Operations"] = run_real_cluster_operations()
        results["Real Monitoring Setup"] = run_real_monitoring_setup()
        results["Real Data Generation"] = run_real_data_generation()
    
    # Generate report
    if results:
        generate_real_test_report(results)
    else:
        print("No tests were run.")
    
    print(f"\n🎉 Real environment testing completed!")


if __name__ == "__main__":
    main() 