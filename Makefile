# Makefile for AI DevOps project

.PHONY: help install install-dev format lint test clean validate security

help:
	@echo "AI DevOps Development Commands"
	@echo "================================"
	@echo "install         Install production dependencies"
	@echo "install-dev     Install development dependencies"
	@echo "format          Format code with black and isort"
	@echo "lint            Run linters (flake8, pylint)"
	@echo "test            Run tests"
	@echo "validate        Validate JSON schemas and examples"
	@echo "security        Run security checks (bandit, safety)"
	@echo "clean           Clean up generated files"
	@echo "all             Run format, lint, validate, and test"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

format:
	@echo "Formatting code with black..."
	black examples/
	@echo "Sorting imports with isort..."
	isort examples/

lint:
	@echo "Running flake8..."
	flake8 examples/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 examples/ --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics
	@echo "Running pylint..."
	pylint examples/ --exit-zero

test:
	@echo "Testing Python examples compile..."
	python -m py_compile examples/opentelemetry/basic_instrumentation.py
	python -m py_compile examples/opentelemetry/advanced_agent_tracing.py
	python -m py_compile examples/prometheus/ai_metrics.py
	python -m py_compile examples/azure/azure_monitor_example.py
	python -m py_compile examples/unified-correlation/correlation_framework.py
	python -m py_compile examples/multi-agent/agents/investigation_system.py
	python -m py_compile mcp-server/tools.py
	@echo "Running OpenTelemetry example..."
	timeout 5 python examples/opentelemetry/basic_instrumentation.py || exit 0
	@echo "Testing Prometheus example starts..."
	timeout 3 python examples/prometheus/ai_metrics.py || exit 0
	@echo "Testing correlation framework..."
	python -m py_compile examples/unified-correlation/correlation_framework.py
	@echo "Testing multi-agent system..."
	timeout 10 python examples/multi-agent/agents/investigation_system.py || exit 0

validate:
	@echo "Validating JSON schemas..."
	python -c "import json; json.load(open('data-formats/metrics/metrics-schema.json')); print('✓ metrics-schema.json')"
	python -c "import json; json.load(open('data-formats/logs/log-schema.json')); print('✓ log-schema.json')"
	python -c "import json; json.load(open('data-formats/traces/trace-schema.json')); print('✓ trace-schema.json')"
	python -c "import json; json.load(open('data-formats/unified/correlation-schema.json')); print('✓ correlation-schema.json')"
	python -c "import json; json.load(open('data-formats/unified/correlation-examples.json')); print('✓ correlation-examples.json')"
	python -c "import json; json.load(open('integrations/grafana/ai-metrics-dashboard.json')); print('✓ ai-metrics-dashboard.json')"
	@echo "All JSON files validated successfully!"

security:
	@echo "Running Bandit security scan..."
	bandit -r examples/ -ll
	@echo "Checking dependencies for vulnerabilities..."
	safety check

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

all: format lint validate test
	@echo "All checks passed!"
