import dotenv
dotenv.load_dotenv(dotenv_path=".env.test")
import pytest
import smtplib
from deepseek_daily_newsletter.send_email import send_email

def test_send_email_function_exists():
    assert callable(send_email)

def test_send_email_sends(monkeypatch):
    sent = {}
    class DummySMTP:
        def __init__(self, host, port=None): pass
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def starttls(self): pass
        def login(self, username, password): pass
        def send_message(self, msg):
            sent['msg'] = msg

    monkeypatch.setattr("smtplib.SMTP", DummySMTP)

    subject = "Test Subject"
    body = "Test Body"
    sender_email = "test@example.com"
    bcc_emails = ["a@example.com", "b@example.com"]
    send_email(subject, body, sender_email, bcc_emails)
    assert sent['msg']['Subject'] == subject
    assert sent['msg']['From'] == sender_email
    assert sent['msg']['Bcc'] == ", ".join(bcc_emails)
