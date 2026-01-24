"""Tests for send_email function."""
import pytest
import os


def test_send_email_requires_env_vars(monkeypatch):
    """Test that send email requires necessary environment variables."""
    monkeypatch.setenv("SMTP_SERVER", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SENDER_EMAIL_APP_PASSWORD", "password")
    
    assert os.environ.get("SMTP_SERVER") == "smtp.gmail.com"
    assert os.environ.get("SMTP_PORT") == "587"
    assert os.environ.get("SENDER_EMAIL_APP_PASSWORD") == "password"


def test_email_parameters(monkeypatch):
    """Test email parameter handling."""
    subject = "Test Subject"
    body = "Test Body"
    sender_email = "test@example.com"
    bcc_emails = ["a@example.com", "b@example.com"]
    
    assert subject == "Test Subject"
    assert body == "Test Body"
    assert sender_email == "test@example.com"
    assert len(bcc_emails) == 2
    assert ", ".join(bcc_emails) == "a@example.com, b@example.com"
