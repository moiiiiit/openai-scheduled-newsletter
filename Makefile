.PHONY: help test test-api test-job install clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies for all services"
	@echo "  make test         - Run all unit tests (API + Job)"
	@echo "  make test-api     - Run API unit tests only"
	@echo "  make test-job     - Run Job unit tests only"
	@echo "  make clean        - Remove __pycache__, .pytest_cache, etc."

install:
	cd openai_scheduled_newsletter_api && poetry install
	cd openai_scheduled_newsletter_job && poetry install

test: test-api test-job
	@echo "\n✓ All tests passed!"

test-api:
	@echo "Running API tests..."
	cd openai_scheduled_newsletter_api && poetry run python -m pytest -v tests/

test-job:
	@echo "Running Job tests..."
	cd openai_scheduled_newsletter_job && poetry run python -m pytest -v tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
