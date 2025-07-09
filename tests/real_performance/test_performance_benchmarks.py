"""
Performance benchmarks for UPID CLI
Tests response times, memory usage, and scalability with real data
"""
import pytest
import time
import psutil
import subprocess
import json
import statistics
from typing import Dict, List, Tuple
from pathlib import Path
from tests.real_environment.cluster_setup import RealClusterManager, ClusterConfig, ApplicationConfig


class TestPerformanceBenchmarks:
    """Performance benchmarks for UPID CLI"""
    
    @pytest.fixture(scope="class")
    def cluster_manager(self):
        """Setup cluster manager for performance testing"""
        return RealClusterManager()
    
    @pytest.fixture(scope="class")
    def performance_cluster(self, cluster_manager):
        """Create a performance test cluster"""
        config = ClusterConfig(
            name="perf-test-cluster",
            provider="kind",
            version="v1.24.0",
            nodes=2,
            memory="8GB",
            cpu="4"
        )
        
        # Create cluster
        success = cluster_manager.create_kind_cluster(config)
        if not success:
            pytest.skip("Failed to create performance test cluster")
        
        # Deploy multiple applications for performance testing
        apps = []
        for i in range(10):  # 10 applications
            apps.append(ApplicationConfig(
                name=f"app-{i}",
                namespace="default",
                replicas=3,
                image="nginx:alpine",
                ports=[80],
                resources={
                    "requests": {"cpu": "100m", "memory": "128Mi"},
                    "limits": {"cpu": "200m", "memory": "256Mi"}
                }
            ))
        
        cluster_manager.deploy_test_applications("perf-test-cluster", apps)
        
        # Generate extensive test data
        cluster_manager.generate_test_data("perf-test-cluster", duration_hours=48)
        
        yield "perf-test-cluster"
        
        # Cleanup
        cluster_manager.cleanup_cluster("perf-test-cluster")
    
    def _measure_command_performance(self, args: List[str], iterations: int = 5) -> Dict:
        """Measure performance of a CLI command"""
        times = []
        memory_usage = []
        
        for i in range(iterations):
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Measure command execution time
            start_time = time.time()
            
            cmd = ["python", "-m", "upid.cli", "--local"] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = final_memory - initial_memory
            
            times.append(execution_time)
            memory_usage.append(memory_delta)
            
            # Small delay between iterations
            time.sleep(1)
        
        return {
            "execution_times": times,
            "memory_usage": memory_usage,
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev_time": statistics.stdev(times) if len(times) > 1 else 0,
            "avg_memory": statistics.mean(memory_usage),
            "max_memory": max(memory_usage),
            "success": result.returncode == 0
        }
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_analyze_resources_performance(self, performance_cluster):
        """Benchmark analyze resources command performance"""
        result = self._measure_command_performance([
            "analyze", "resources", performance_cluster, "--format", "json"
        ])
        
        assert result["success"]
        
        # Performance assertions
        assert result["avg_time"] < 10.0, f"Average time {result['avg_time']:.2f}s exceeds 10s limit"
        assert result["max_time"] < 15.0, f"Max time {result['max_time']:.2f}s exceeds 15s limit"
        assert result["avg_memory"] < 500, f"Average memory {result['avg_memory']:.2f}MB exceeds 500MB limit"
        assert result["max_memory"] < 1000, f"Max memory {result['max_memory']:.2f}MB exceeds 1GB limit"
        
        print(f"Analyze Resources Performance:")
        print(f"  Average Time: {result['avg_time']:.2f}s")
        print(f"  Max Time: {result['max_time']:.2f}s")
        print(f"  Average Memory: {result['avg_memory']:.2f}MB")
        print(f"  Max Memory: {result['max_memory']:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_analyze_cost_performance(self, performance_cluster):
        """Benchmark analyze cost command performance"""
        result = self._measure_command_performance([
            "analyze", "cost", performance_cluster, "--format", "json"
        ])
        
        assert result["success"]
        
        # Performance assertions
        assert result["avg_time"] < 8.0, f"Average time {result['avg_time']:.2f}s exceeds 8s limit"
        assert result["max_time"] < 12.0, f"Max time {result['max_time']:.2f}s exceeds 12s limit"
        assert result["avg_memory"] < 400, f"Average memory {result['avg_memory']:.2f}MB exceeds 400MB limit"
        
        print(f"Analyze Cost Performance:")
        print(f"  Average Time: {result['avg_time']:.2f}s")
        print(f"  Max Time: {result['max_time']:.2f}s")
        print(f"  Average Memory: {result['avg_memory']:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_analyze_performance_performance(self, performance_cluster):
        """Benchmark analyze performance command performance"""
        result = self._measure_command_performance([
            "analyze", "performance", performance_cluster, "--format", "json"
        ])
        
        assert result["success"]
        
        # Performance assertions
        assert result["avg_time"] < 12.0, f"Average time {result['avg_time']:.2f}s exceeds 12s limit"
        assert result["max_time"] < 18.0, f"Max time {result['max_time']:.2f}s exceeds 18s limit"
        assert result["avg_memory"] < 600, f"Average memory {result['avg_memory']:.2f}MB exceeds 600MB limit"
        
        print(f"Analyze Performance Command Performance:")
        print(f"  Average Time: {result['avg_time']:.2f}s")
        print(f"  Max Time: {result['max_time']:.2f}s")
        print(f"  Average Memory: {result['avg_memory']:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_optimize_resources_performance(self, performance_cluster):
        """Benchmark optimize resources command performance"""
        result = self._measure_command_performance([
            "optimize", "resources", performance_cluster, "--dry-run", "--format", "json"
        ])
        
        assert result["success"]
        
        # Performance assertions
        assert result["avg_time"] < 15.0, f"Average time {result['avg_time']:.2f}s exceeds 15s limit"
        assert result["max_time"] < 25.0, f"Max time {result['max_time']:.2f}s exceeds 25s limit"
        assert result["avg_memory"] < 800, f"Average memory {result['avg_memory']:.2f}MB exceeds 800MB limit"
        
        print(f"Optimize Resources Performance:")
        print(f"  Average Time: {result['avg_time']:.2f}s")
        print(f"  Max Time: {result['max_time']:.2f}s")
        print(f"  Average Memory: {result['avg_memory']:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_optimize_costs_performance(self, performance_cluster):
        """Benchmark optimize costs command performance"""
        result = self._measure_command_performance([
            "optimize", "costs", performance_cluster, "--dry-run", "--format", "json"
        ])
        
        assert result["success"]
        
        # Performance assertions
        assert result["avg_time"] < 12.0, f"Average time {result['avg_time']:.2f}s exceeds 12s limit"
        assert result["max_time"] < 20.0, f"Max time {result['max_time']:.2f}s exceeds 20s limit"
        assert result["avg_memory"] < 600, f"Average memory {result['avg_memory']:.2f}MB exceeds 600MB limit"
        
        print(f"Optimize Costs Performance:")
        print(f"  Average Time: {result['avg_time']:.2f}s")
        print(f"  Max Time: {result['max_time']:.2f}s")
        print(f"  Average Memory: {result['avg_memory']:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_report_dashboard_performance(self, performance_cluster):
        """Benchmark report dashboard command performance"""
        result = self._measure_command_performance([
            "report", "dashboard", "--cluster", performance_cluster, "--format", "json"
        ])
        
        assert result["success"]
        
        # Performance assertions
        assert result["avg_time"] < 10.0, f"Average time {result['avg_time']:.2f}s exceeds 10s limit"
        assert result["max_time"] < 15.0, f"Max time {result['max_time']:.2f}s exceeds 15s limit"
        assert result["avg_memory"] < 500, f"Average memory {result['avg_memory']:.2f}MB exceeds 500MB limit"
        
        print(f"Report Dashboard Performance:")
        print(f"  Average Time: {result['avg_time']:.2f}s")
        print(f"  Max Time: {result['max_time']:.2f}s")
        print(f"  Average Memory: {result['avg_memory']:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_cli_startup_performance(self):
        """Benchmark CLI startup performance"""
        times = []
        
        for i in range(10):
            start_time = time.time()
            
            result = subprocess.run(
                ["python", "-m", "upid.cli", "--local", "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            end_time = time.time()
            startup_time = end_time - start_time
            times.append(startup_time)
            
            assert result.returncode == 0
        
        avg_startup = statistics.mean(times)
        max_startup = max(times)
        
        # Startup performance assertions
        assert avg_startup < 2.0, f"Average startup time {avg_startup:.2f}s exceeds 2s limit"
        assert max_startup < 3.0, f"Max startup time {max_startup:.2f}s exceeds 3s limit"
        
        print(f"CLI Startup Performance:")
        print(f"  Average Time: {avg_startup:.2f}s")
        print(f"  Max Time: {max_startup:.2f}s")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_concurrent_commands_performance(self, performance_cluster):
        """Benchmark concurrent command execution"""
        import concurrent.futures
        import threading
        
        def run_command(cmd_args):
            """Run a single command"""
            start_time = time.time()
            result = subprocess.run(
                ["python", "-m", "upid.cli", "--local"] + cmd_args,
                capture_output=True,
                text=True,
                timeout=60
            )
            end_time = time.time()
            return {
                "success": result.returncode == 0,
                "time": end_time - start_time
            }
        
        # Define commands to run concurrently
        commands = [
            ["analyze", "resources", performance_cluster, "--format", "json"],
            ["analyze", "cost", performance_cluster, "--format", "json"],
            ["analyze", "performance", performance_cluster, "--format", "json"],
            ["cluster", "list", "--format", "json"],
            ["report", "dashboard", "--cluster", performance_cluster, "--format", "json"]
        ]
        
        # Run commands concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_command, cmd) for cmd in commands]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_results = [r for r in results if r["success"]]
        times = [r["time"] for r in successful_results]
        
        assert len(successful_results) >= 4, f"Only {len(successful_results)}/5 commands succeeded"
        
        avg_concurrent_time = statistics.mean(times)
        max_concurrent_time = max(times)
        
        # Concurrent performance assertions
        assert avg_concurrent_time < 20.0, f"Average concurrent time {avg_concurrent_time:.2f}s exceeds 20s limit"
        assert max_concurrent_time < 30.0, f"Max concurrent time {max_concurrent_time:.2f}s exceeds 30s limit"
        
        print(f"Concurrent Commands Performance:")
        print(f"  Successful Commands: {len(successful_results)}/5")
        print(f"  Average Time: {avg_concurrent_time:.2f}s")
        print(f"  Max Time: {max_concurrent_time:.2f}s")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_memory_scalability(self, performance_cluster):
        """Test memory usage scalability with different data sizes"""
        # Test with different levels of detail
        scenarios = [
            ("basic", ["analyze", "resources", performance_cluster, "--format", "json"]),
            ("detailed", ["analyze", "resources", performance_cluster, "--detailed", "--format", "json"]),
            ("intelligence", ["analyze", "intelligence", performance_cluster, "--format", "json"]),
            ("advanced", ["analyze", "advanced", performance_cluster, "--format", "json"])
        ]
        
        memory_usage = {}
        
        for scenario_name, cmd_args in scenarios:
            result = self._measure_command_performance(cmd_args, iterations=3)
            memory_usage[scenario_name] = result["avg_memory"]
        
        # Scalability assertions
        assert memory_usage["basic"] < 300, f"Basic analysis memory {memory_usage['basic']:.2f}MB too high"
        assert memory_usage["detailed"] < 600, f"Detailed analysis memory {memory_usage['detailed']:.2f}MB too high"
        assert memory_usage["intelligence"] < 800, f"Intelligence analysis memory {memory_usage['intelligence']:.2f}MB too high"
        assert memory_usage["advanced"] < 1000, f"Advanced analysis memory {memory_usage['advanced']:.2f}MB too high"
        
        print(f"Memory Scalability:")
        for scenario, memory in memory_usage.items():
            print(f"  {scenario.capitalize()}: {memory:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_cpu_usage_performance(self, performance_cluster):
        """Test CPU usage during command execution"""
        import psutil
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Run a resource-intensive command
        start_time = time.time()
        process = subprocess.Popen(
            ["python", "-m", "upid.cli", "--local", "analyze", "intelligence", performance_cluster, "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor CPU usage during execution
        cpu_samples = []
        while process.poll() is None:
            cpu_samples.append(psutil.cpu_percent(interval=0.5))
            if time.time() - start_time > 60:  # Timeout after 60 seconds
                process.terminate()
                break
        
        process.wait()
        execution_time = time.time() - start_time
        
        # Analyze CPU usage
        if cpu_samples:
            avg_cpu = statistics.mean(cpu_samples)
            max_cpu = max(cpu_samples)
            
            # CPU usage assertions
            assert avg_cpu < 80, f"Average CPU usage {avg_cpu:.1f}% exceeds 80% limit"
            assert max_cpu < 95, f"Max CPU usage {max_cpu:.1f}% exceeds 95% limit"
            assert execution_time < 60, f"Execution time {execution_time:.2f}s exceeds 60s limit"
            
            print(f"CPU Usage Performance:")
            print(f"  Average CPU: {avg_cpu:.1f}%")
            print(f"  Max CPU: {max_cpu:.1f}%")
            print(f"  Execution Time: {execution_time:.2f}s")
        else:
            pytest.skip("No CPU samples collected")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_network_performance(self, performance_cluster):
        """Test network performance for API calls"""
        import psutil
        
        # Get initial network stats
        initial_net = psutil.net_io_counters()
        
        # Run command that makes API calls
        start_time = time.time()
        result = subprocess.run(
            ["python", "-m", "upid.cli", "--local", "analyze", "resources", performance_cluster, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Get final network stats
        final_net = psutil.net_io_counters()
        
        # Calculate network usage
        bytes_sent = final_net.bytes_sent - initial_net.bytes_sent
        bytes_recv = final_net.bytes_recv - initial_net.bytes_recv
        
        # Network performance assertions
        assert execution_time < 15, f"Network operation time {execution_time:.2f}s exceeds 15s limit"
        assert bytes_sent < 10 * 1024 * 1024, f"Bytes sent {bytes_sent/1024/1024:.2f}MB exceeds 10MB limit"
        assert bytes_recv < 50 * 1024 * 1024, f"Bytes received {bytes_recv/1024/1024:.2f}MB exceeds 50MB limit"
        
        print(f"Network Performance:")
        print(f"  Execution Time: {execution_time:.2f}s")
        print(f"  Bytes Sent: {bytes_sent/1024/1024:.2f}MB")
        print(f"  Bytes Received: {bytes_recv/1024/1024:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_stress_test(self, performance_cluster):
        """Stress test with multiple rapid commands"""
        import concurrent.futures
        import random
        
        def stress_command():
            """Run a random command for stress testing"""
            commands = [
                ["analyze", "resources", performance_cluster, "--format", "json"],
                ["analyze", "cost", performance_cluster, "--format", "json"],
                ["cluster", "list", "--format", "json"],
                ["report", "dashboard", "--cluster", performance_cluster, "--format", "json"]
            ]
            
            cmd = random.choice(commands)
            start_time = time.time()
            result = subprocess.run(
                ["python", "-m", "upid.cli", "--local"] + cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            end_time = time.time()
            
            return {
                "success": result.returncode == 0,
                "time": end_time - start_time,
                "command": " ".join(cmd)
            }
        
        # Run 20 concurrent commands
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(stress_command) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze stress test results
        successful_results = [r for r in results if r["success"]]
        times = [r["time"] for r in successful_results]
        
        success_rate = len(successful_results) / len(results) * 100
        avg_stress_time = statistics.mean(times) if times else 0
        max_stress_time = max(times) if times else 0
        
        # Stress test assertions
        assert success_rate >= 80, f"Success rate {success_rate:.1f}% below 80% threshold"
        assert avg_stress_time < 25, f"Average stress time {avg_stress_time:.2f}s exceeds 25s limit"
        assert max_stress_time < 45, f"Max stress time {max_stress_time:.2f}s exceeds 45s limit"
        
        print(f"Stress Test Results:")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Average Time: {avg_stress_time:.2f}s")
        print(f"  Max Time: {max_stress_time:.2f}s")
        print(f"  Successful Commands: {len(successful_results)}/20")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_output_format_performance(self, performance_cluster):
        """Test performance of different output formats"""
        formats = ["table", "json", "yaml", "detailed"]
        format_performance = {}
        
        for output_format in formats:
            result = self._measure_command_performance([
                "analyze", "resources", performance_cluster, "--format", output_format
            ], iterations=3)
            format_performance[output_format] = result["avg_time"]
        
        # Format performance assertions
        assert format_performance["table"] < 8, f"Table format time {format_performance['table']:.2f}s too high"
        assert format_performance["json"] < 10, f"JSON format time {format_performance['json']:.2f}s too high"
        assert format_performance["yaml"] < 12, f"YAML format time {format_performance['yaml']:.2f}s too high"
        assert format_performance["detailed"] < 15, f"Detailed format time {format_performance['detailed']:.2f}s too high"
        
        print(f"Output Format Performance:")
        for fmt, time_taken in format_performance.items():
            print(f"  {fmt.capitalize()}: {time_taken:.2f}s")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_error_recovery_performance(self, performance_cluster):
        """Test performance of error recovery scenarios"""
        # Test invalid cluster handling
        start_time = time.time()
        result = subprocess.run(
            ["python", "-m", "upid.cli", "--local", "analyze", "resources", "invalid-cluster"],
            capture_output=True,
            text=True,
            timeout=10
        )
        error_time = time.time() - start_time
        
        # Error recovery assertions
        assert result.returncode != 0, "Invalid cluster should fail"
        assert error_time < 5, f"Error recovery time {error_time:.2f}s exceeds 5s limit"
        
        print(f"Error Recovery Performance:")
        print(f"  Error Recovery Time: {error_time:.2f}s")
        print(f"  Expected Failure: ✅")
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_memory_leak_detection(self, performance_cluster):
        """Test for memory leaks during repeated operations"""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Run the same command multiple times
        for i in range(10):
            result = subprocess.run(
                ["python", "-m", "upid.cli", "--local", "analyze", "resources", performance_cluster, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0
            
            # Force garbage collection after each iteration
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory leak assertions
        assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB exceeds 100MB limit (potential leak)"
        
        print(f"Memory Leak Detection:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Final Memory: {final_memory:.2f}MB")
        print(f"  Memory Increase: {memory_increase:.2f}MB")
        print(f"  Leak Detected: {'❌' if memory_increase > 100 else '✅'}") 