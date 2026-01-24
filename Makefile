.PHONY: help test test-api test-job run-api run-job install clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies for all services"
	@echo "  make test         - Run all unit tests (API + Job)"
	@echo "  make test-api     - Run API unit tests only"
	@echo "  make test-job     - Run Job unit tests only"
	@echo "  make run-api      - Start the API locally (uvicorn on :8000)"
	@echo "  make run-job      - Run the one-shot job locally"
	@echo "  make clean        - Remove __pycache__, .pytest_cache, etc."

install:
	cd openai_scheduled_newsletter_api && poetry install --with dev
	cd openai_scheduled_newsletter_job && poetry install --with dev

test: test-api test-job
	@echo "\n✓ All tests passed!"

test-api:
	@echo "Running API tests..."
	cd openai_scheduled_newsletter_api && poetry run python -m pytest -v tests/

test-job:
	@echo "Running Job tests..."
	cd openai_scheduled_newsletter_job && poetry run python -m pytest -v tests/

run-api:
	@echo "Starting API on http://0.0.0.0:8000"
	cd openai_scheduled_newsletter_api && poetry run uvicorn openai_scheduled_newsletter_api.main:app --host 0.0.0.0 --port 8000

run-job:
	@echo "Running newsletter job once"
	cd openai_scheduled_newsletter_job && poetry run python main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
