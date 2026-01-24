"""Tests for the job main entry point."""
import pytest
import os


def test_main_requires_env_vars():
    """Test that main function requires necessary environment variables."""
    # Verify we have required env vars set by conftest
    assert os.environ.get("SENDER_EMAIL") == "test@example.com"
    assert os.environ.get("EMAILS_JSON") is not None
    assert os.environ.get("PROMPTS_JSON") is not None


def test_main_email_parsing():
    """Test email JSON parsing."""
    import json
    emails_json = os.environ.get("EMAILS_JSON")
    recipients = json.loads(emails_json)
    bcc_emails = [r["email"] for r in recipients]
    
    assert len(bcc_emails) > 0
    assert "user@example.com" in bcc_emails


def test_main_prompt_parsing():
    """Test prompt JSON parsing."""
    import json
    prompts_json = os.environ.get("PROMPTS_JSON")
    prompts = json.loads(prompts_json)
    
    assert len(prompts) > 0
    assert "model" in prompts[0] or "prompt" in prompts[0]
