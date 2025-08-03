.PHONY: help install install-dev test test-cov lint format clean build docs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	python3 setup.py install

venv: ## Create a virtual environment
	python3 -m venv .venv

install-dev: venv ## Install the package with development dependencies
	. .venv/bin/activate && python3 -m pip install -e ".[dev]"

test: install-dev ## Run tests
	. .venv/bin/activate && python3 -m pytest

test-cov: install-dev ## Run tests with coverage
	. .venv/bin/activate && python3 -m pytest --cov=src/notify2 --cov-report=term-missing --cov-report=html

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

docs: ## Build documentation
	# Add documentation building commands here when needed
	@echo "Documentation building not yet implemented"

test-cli: ## Test the CLI commands
	notify2 --help
	notify2 test --help
	notify2 send --help
	notify2 photo --help
	notify2 document --help
	notify2 setup --help
	notify2 info --help 