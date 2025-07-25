# UPID CLI Makefile
# Provides convenient commands for development and testing

.PHONY: help install install-dev test test-unit test-integration test-k8s test-api test-all lint type-check format security clean setup report coverage docs binary build-binary install-binary release-binary

# Default target
help:
	@echo "UPID CLI Development Commands"
	@echo "============================="
	@echo ""
	@echo "Installation:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-k8s     - Run Kubernetes tests only"
	@echo "  test-api     - Run API tests only"
	@echo "  test-all     - Run all tests with coverage"
	@echo ""
	@echo "Binary Build:"
	@echo "  binary       - Build standalone binary (like kubectl)"
	@echo "  build-binary - Build binary for current platform"
	@echo "  install-binary - Install binary to system"
	@echo "  release-binary - Create release packages"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run code linting"
	@echo "  type-check   - Run type checking"
	@echo "  format       - Check code formatting"
	@echo "  security     - Run security checks"
	@echo ""
	@echo "Utilities:"
	@echo "  setup        - Setup test environment"
	@echo "  report       - Generate test reports"
	@echo "  coverage     - Generate coverage reports"
	@echo "  docs         - Generate documentation"
	@echo "  clean        - Clean build artifacts"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Testing
test:
	python tests/run_tests.py

test-unit:
	python tests/run_tests.py --unit

test-integration:
	python tests/run_tests.py --integration

test-k8s:
	python tests/run_tests.py --k8s

test-api:
	python tests/run_tests.py --api

test-all:
	python tests/run_tests.py --all

# Binary Build
binary: build-binary install-binary
	@echo "Binary build and installation completed!"

build-binary:
	@echo "Building UPID CLI Go binaries..."
	@./build_go_binary.sh

install-binary:
	@echo "Installing UPID CLI binary..."
	@if [ -f "dist/upid-$(shell uname -s | tr '[:upper:]' '[:lower:]')-$(shell uname -m)" ]; then \
		sudo cp "dist/upid-$(shell uname -s | tr '[:upper:]' '[:lower:]')-$(shell uname -m)" /usr/local/bin/upid; \
		echo "✅ UPID CLI installed to /usr/local/bin/upid"; \
	elif [ -f "dist/upid-$(shell uname -s | tr '[:upper:]' '[:lower:]')-$(shell uname -m).exe" ]; then \
		echo "Windows binary found. Please install manually."; \
	else \
		echo "Binary not found. Run 'make build-binary' first."; \
	fi

release-binary: build-binary
	@echo "Creating release packages..."
	@echo "✅ Release packages created in 'dist' directory"

# Code Quality
lint:
	python tests/run_tests.py --lint

type-check:
	python tests/run_tests.py --type-check

format:
	python tests/run_tests.py --format

security:
	python tests/run_tests.py --security

# Utilities
setup:
	python tests/run_tests.py --setup

report:
	python tests/run_tests.py --report

coverage:
	pytest tests/ --cov=upid --cov-report=html --cov-report=term-missing

docs:
	@echo "Generating documentation..."
	@mkdir -p docs
	@python -c "import upid; help(upid)" > docs/api.txt 2>/dev/null || echo "Documentation generation failed"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf coverage/
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf security_report.json
	rm -rf binaries/
	rm -rf release/
	rm -rf temp/
	rm -f upid.spec
	rm -f install.sh
	rm -f install.bat
	rm -f Dockerfile.binary
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# Development shortcuts
dev-setup: install-dev setup
	@echo "Development environment setup complete!"

quick-test: test-unit lint type-check
	@echo "Quick test suite completed!"

full-test: test-all security
	@echo "Full test suite completed!"

# Docker commands (if needed)
docker-build:
	docker build -t upid-cli .

docker-test:
	docker run --rm upid-cli python tests/run_tests.py --unit

docker-binary:
	docker build -f Dockerfile.binary -t upid-cli-binary .

# CI/CD helpers
ci-test:
	python tests/run_tests.py --all --no-cov-on-fail

ci-lint:
	python tests/run_tests.py --lint --type-check --format

# Performance testing
perf-test:
	python tests/run_tests.py --performance

stress-test:
	python tests/run_tests.py --stress

# Zero-pod specific tests
test-zero-pod:
	python tests/run_tests.py --zero-pod

# Kubernetes specific
k8s-setup:
	@echo "Setting up Kubernetes test environment..."
	kind create cluster --name upid-test || true
	kubectl cluster-info

k8s-cleanup:
	@echo "Cleaning up Kubernetes test environment..."
	kind delete cluster --name upid-test || true

# Documentation
readme:
	@echo "Generating README..."
	@python -c "
import upid
with open('README.md', 'w') as f:
    f.write('# UPID CLI\n\n')
    f.write('Kubernetes Resource Optimization Platform\n\n')
    f.write('## Installation\n\n')
    f.write('```bash\npip install upid-cli\n```\n\n')
    f.write('## Usage\n\n')
    f.write('```bash\nupid --help\n```\n')
"

# Package management
build:
	python setup.py sdist bdist_wheel

upload:
	twine upload dist/*

# Git helpers
pre-commit: lint type-check format test-unit
	@echo "Pre-commit checks passed!"

git-hooks:
	@echo "Installing git hooks..."
	@mkdir -p .git/hooks
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo 'make pre-commit' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed!"

# Environment setup
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "source venv/bin/activate  # Linux/Mac"
	@echo "venv\\Scripts\\activate     # Windows"

# Monitoring and debugging
logs:
	@echo "Recent test logs:"
	@find . -name "*.log" -exec tail -n 20 {} \; 2>/dev/null || echo "No log files found"

debug:
	@echo "Debug information:"
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Docker version: $(shell docker --version 2>/dev/null || echo 'Docker not installed')"
	@echo "Kubectl version: $(shell kubectl version --client 2>/dev/null || echo 'Kubectl not installed')"

# Helpers for specific test types
test-config:
	pytest tests/unit/test_config.py -v

test-auth:
	pytest tests/unit/test_auth.py -v

test-api:
	pytest tests/unit/test_api_client.py -v

test-integration-api:
	pytest tests/integration/test_api_integration.py -v

test-integration-k8s:
	pytest tests/integration/test_k8s_integration.py -v

# Parallel testing
test-parallel:
	pytest tests/ -n auto

# Coverage with specific thresholds
coverage-strict:
	pytest tests/ --cov=upid --cov-fail-under=90 --cov-report=html --cov-report=term-missing

# Test with specific markers
test-slow:
	pytest tests/ -m "slow" -v

test-fast:
	pytest tests/ -m "not slow" -v

# Integration test helpers
test-containers:
	docker ps -a
	@echo "Container status checked"

test-network:
	@echo "Testing network connectivity..."
	curl -f http://localhost:8000 > /dev/null 2>&1 || echo "No local server running"

# Development workflow
dev-workflow: dev-setup quick-test
	@echo "Development workflow completed!"

ci-workflow: ci-lint ci-test
	@echo "CI workflow completed!"

# Release helpers
release-check: test-all security coverage-strict
	@echo "Release checks completed!"

release-prep: clean build
	@echo "Release preparation completed!"

# Binary-specific helpers
binary-linux:
	@echo "Building Linux binary..."
	@if [ "$(shell uname)" = "Linux" ]; then \
		python build_binary.py; \
	else \
		echo "Cross-compilation not supported. Run on Linux."; \
	fi

binary-macos:
	@echo "Building macOS binary..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		python build_binary.py; \
	else \
		echo "Cross-compilation not supported. Run on macOS."; \
	fi

binary-windows:
	@echo "Building Windows binary..."
	@if [ "$(shell uname)" = "MINGW" ] || [ "$(shell uname)" = "MSYS" ]; then \
		python build_binary.py; \
	else \
		echo "Cross-compilation not supported. Run on Windows."; \
	fi

binary-all: binary-linux binary-macos binary-windows
	@echo "All platform binaries built!"

# Help for specific tasks
help-test:
	@echo "Test Commands:"
	@echo "  test-unit        - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-k8s         - Run Kubernetes tests"
	@echo "  test-api         - Run API tests"
	@echo "  test-all         - Run all tests"
	@echo "  test-parallel    - Run tests in parallel"
	@echo "  test-slow        - Run slow tests only"
	@echo "  test-fast        - Run fast tests only"

help-dev:
	@echo "Development Commands:"
	@echo "  dev-setup        - Setup development environment"
	@echo "  dev-workflow     - Run development workflow"
	@echo "  quick-test       - Run quick test suite"
	@echo "  full-test        - Run full test suite"
	@echo "  pre-commit       - Run pre-commit checks"
	@echo "  git-hooks        - Install git hooks"

help-binary:
	@echo "Binary Commands:"
	@echo "  binary           - Build and install binary"
	@echo "  build-binary     - Build binary for current platform"
	@echo "  install-binary   - Install binary to system"
	@echo "  release-binary   - Create release packages"
	@echo "  binary-linux     - Build Linux binary"
	@echo "  binary-macos     - Build macOS binary"
	@echo "  binary-windows   - Build Windows binary"
	@echo "  binary-all       - Build all platform binaries"

help-ci:
	@echo "CI/CD Commands:"
	@echo "  ci-test          - Run CI tests"
	@echo "  ci-lint          - Run CI linting"
	@echo "  ci-workflow      - Run CI workflow"
	@echo "  release-check    - Run release checks"
	@echo "  release-prep     - Prepare for release" 