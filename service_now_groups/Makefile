.PHONY: help install test lint format clean build docs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest -v --cov=service_now_groups --cov-report=html --cov-report=term-missing

test-fast:  ## Run tests without coverage
	pytest -v

lint:  ## Run linting tools
	flake8 service_now_groups/
	black --check service_now_groups/
	isort --check-only service_now_groups/
	bandit -r service_now_groups/ -f json -o bandit-report.json

format:  ## Format code
	black service_now_groups/
	isort service_now_groups/

security:  ## Run security checks
	bandit -r service_now_groups/ -f json -o bandit-report.json
	safety check

type-check:  ## Run type checking
	mypy service_now_groups/

quality: format lint type-check security  ## Run all quality checks

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -f bandit-report.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: clean  ## Build package
	python -m build

docs:  ## Build documentation
	cd docs && make html

pre-commit:  ## Run pre-commit hooks
	pre-commit run --all-files

ci: quality test  ## Run CI checks (quality + tests) 