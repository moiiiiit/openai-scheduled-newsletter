
from openai_scheduled_newsletter.send_email import send_email


def test_send_email_function_exists() -> None:
    assert callable(send_email)

def test_send_email_sends(monkeypatch) -> None:
    sent = {}
    class DummySMTP:
        def __init__(self, host: str, port: int | None = None) -> None:
            pass
        def __enter__(self) -> "DummySMTP":
            return self
        def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
            pass
        def starttls(self) -> None:
            pass
        def login(self, username: str, password: str) -> None:
            pass
        def send_message(self, msg: dict) -> None:
            sent["msg"] = msg

    monkeypatch.setattr("smtplib.SMTP", DummySMTP)

    subject = "Test Subject"
    body = "Test Body"
    sender_email = "test@example.com"
    bcc_emails = ["a@example.com", "b@example.com"]
    send_email(subject, body, sender_email, bcc_emails)
    assert sent["msg"]["Subject"] == subject
    assert sent["msg"]["From"] == sender_email
    assert sent["msg"]["Bcc"] == ", ".join(bcc_emails)
