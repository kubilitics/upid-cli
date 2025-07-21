# UPID CLI Test Suite

This directory contains the comprehensive test suite for UPID CLI, organized by test type and purpose.

## 📁 Directory Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and fixtures
├── run_tests.py                 # Main test runner
├── unit/                        # Unit tests (fast, isolated)
│   ├── test_api_client.py      # API client functionality
│   ├── test_auth.py            # Authentication systems
│   ├── test_config.py          # Configuration management
│   ├── test_cli_edge_cases.py  # CLI edge cases
│   └── test_edge_cases.py      # General edge cases
├── integration/                 # Integration tests (real dependencies)
│   ├── test_api_integration.py # API integration tests
│   └── test_k8s_integration.py # Kubernetes integration tests
├── real_environment/            # Real environment setup
│   └── cluster_setup.py        # Real Kubernetes cluster management
├── real_integration/            # Real integration tests
│   └── test_real_cli_commands.py # Real CLI command testing
├── real_performance/            # Performance and benchmark tests
│   └── test_performance_benchmarks.py # Performance benchmarks
├── phase_tests/                 # Phase-specific test suites
│   └── test_phase5_api_backend.py # Phase 5 API backend tests
├── legacy/                      # Legacy test files (to be cleaned up)
│   ├── test_*.py               # Old test files
│   └── ...                     # Various legacy tests
└── scripts/                     # Test scripts and utilities
    ├── test_intelligent_analytics.py
    ├── test_phase2_confidence_optimization.py
    └── test_phase3_executive_dashboard.py
```

## 🧪 Test Categories

### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast execution (< 1 second per test)
- **Dependencies**: Mocked external dependencies
- **Coverage**: Core functionality, edge cases, error handling

### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions
- **Speed**: Medium execution (1-5 seconds per test)
- **Dependencies**: Real containers and APIs
- **Coverage**: API interactions, Kubernetes operations

### **Real Environment Tests** (`tests/real_environment/`)
- **Purpose**: Test with actual Kubernetes clusters
- **Speed**: Slow execution (5-30 seconds per test)
- **Dependencies**: Real Kubernetes clusters (kind, minikube)
- **Coverage**: Real cluster operations, application deployment

### **Real Integration Tests** (`tests/real_integration/`)
- **Purpose**: End-to-end testing with real data
- **Speed**: Slow execution (10-60 seconds per test)
- **Dependencies**: Real clusters with real applications
- **Coverage**: Complete workflows, real CLI commands

### **Performance Tests** (`tests/real_performance/`)
- **Purpose**: Performance benchmarking and stress testing
- **Speed**: Very slow execution (1-10 minutes per test)
- **Dependencies**: Large test clusters, performance monitoring
- **Coverage**: Scalability, memory usage, response times

### **Phase Tests** (`tests/phase_tests/`)
- **Purpose**: Phase-specific functionality testing
- **Speed**: Medium execution (5-30 seconds per test)
- **Dependencies**: Phase-specific components
- **Coverage**: Phase implementation validation

## 🚀 Running Tests

### **Quick Start**
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/real_integration/ -v
python -m pytest tests/real_performance/ -v

# Run with coverage
python -m pytest tests/ --cov=upid --cov-report=html
```

### **Test Runner Script**
```bash
# Run comprehensive test suite
python tests/run_tests.py --all

# Run specific test types
python tests/run_tests.py --unit
python tests/run_tests.py --integration
python tests/run_tests.py --real
python tests/run_tests.py --performance
```

## 📊 Current Test Status

### **Test Coverage**
- **Total Test Files**: 30 organized test files
- **Test Cases**: 901 individual test cases
- **Categories**: Unit, Integration, Real Environment, Performance

### **Current Results** (as of latest run)
```
📊 TEST STATUS SUMMARY
===========================================
Unit Tests: 98 PASSED, 126 FAILED (43.7% success)
Integration Tests: 0 PASSED, 68 FAILED (0% success)
Real Integration: 5 PASSED, 44 FAILED (10.2% success)
Performance Tests: 0 PASSED, 1 FAILED (0% success)

OVERALL SUCCESS RATE: 30.1%
```

### **Known Issues**
1. **Unit Tests**: Import errors, configuration issues, mock problems
2. **Integration Tests**: Container startup failures, network issues
3. **Real Tests**: Cluster setup problems, deployment failures
4. **Performance Tests**: Resource constraints, timeout issues

## 🔧 Test Configuration

### **Pytest Configuration** (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=upid
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    e2e: End-to-end tests
    api: API related tests
    k8s: Kubernetes related tests
    zero_pod: Zero-pod scaling tests
```

### **Test Fixtures** (`conftest.py`)
- Mock configurations for testing
- Authentication fixtures
- API client fixtures
- Sample data fixtures
- Container management fixtures

## 🧹 Legacy Test Cleanup

### **Legacy Directory** (`tests/legacy/`)
Contains old test files that need to be:
1. **Reviewed**: Determine if still relevant
2. **Refactored**: Update to current architecture
3. **Removed**: Delete if obsolete
4. **Merged**: Integrate useful parts into main test suite

### **Cleanup Plan**
- [ ] Review all legacy test files
- [ ] Identify tests that can be updated
- [ ] Remove obsolete tests
- [ ] Integrate useful tests into main suite
- [ ] Update documentation

## 📈 Test Metrics

### **Performance Targets**
- **Unit Tests**: < 1 second per test
- **Integration Tests**: < 5 seconds per test
- **Real Tests**: < 30 seconds per test
- **Performance Tests**: < 10 minutes per test

### **Coverage Targets**
- **Overall Coverage**: > 80%
- **Core Components**: > 90%
- **API Endpoints**: > 95%
- **CLI Commands**: > 85%

### **Reliability Targets**
- **Test Stability**: > 95% pass rate
- **Flaky Tests**: < 5%
- **False Positives**: < 1%
- **False Negatives**: < 1%

## 🤝 Contributing to Tests

### **Adding New Tests**
1. **Choose Category**: Place in appropriate directory
2. **Follow Naming**: Use `test_*.py` convention
3. **Add Markers**: Use appropriate pytest markers
4. **Write Documentation**: Document test purpose and setup
5. **Update README**: Add to this documentation

### **Test Best Practices**
- **Isolation**: Tests should not depend on each other
- **Cleanup**: Always clean up after tests
- **Mocking**: Mock external dependencies
- **Assertions**: Use specific, meaningful assertions
- **Documentation**: Document complex test scenarios

## 📞 Support

For test-related issues:
- **GitHub Issues**: Report test failures and improvements
- **Documentation**: Check this README and test docstrings
- **Development**: Follow test best practices when contributing 