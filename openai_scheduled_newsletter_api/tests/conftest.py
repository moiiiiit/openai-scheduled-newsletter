import pytest
import os

@pytest.fixture(autouse=True)
def set_env_vars():
    """Auto-set environment variables for all API tests"""
    os.environ["PROMPTS_JSON"] = '[{"name": "test", "model": "gpt-4", "prompt": "Test prompt", "cron": "0 8 * * 1"}]'
    os.environ["SENDER_EMAIL"] = "test@example.com"
    os.environ["EMAILS_JSON"] = '[{"name": "User", "email": "user@example.com"}]'
    os.environ["API_PASSWORD"] = "changeme"
    yield
    # Cleanup if needed
