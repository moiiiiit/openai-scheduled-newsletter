import pytest
import os
import sys

# Add shared library to path BEFORE any other imports
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared'))
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Auto-set environment variables for all job tests"""
    monkeypatch.setenv("PROMPTS_JSON", '[{"name": "test", "model": "gpt-4", "prompt": "Test prompt", "cron": "0 8 * * 1"}]')
    monkeypatch.setenv("SENDER_EMAIL", "test@example.com")
    monkeypatch.setenv("EMAILS_JSON", '[{"name": "User", "email": "user@example.com"}]')
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")
    monkeypatch.setenv("SMTP_SERVER", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SENDER_EMAIL_APP_PASSWORD", "test-password")
