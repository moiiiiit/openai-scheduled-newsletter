import dotenv
dotenv.load_dotenv(dotenv_path=".env.test")
import datetime
import datetime
import pytest
from openai_scheduled_newsletter import main
from openai_scheduled_newsletter import main as main_mod
import openai_scheduled_newsletter.generate_newsletters as gn

def test_get_next_cron_time():
    from datetime import datetime, timedelta
    cron_expr = "0 8 * * 1"  # Monday 8am
    now = datetime(2025, 10, 20, 7, 0)  # Monday, 7am
    next_run = main.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 20, 8, 0)
    # If now is after 8am, next Monday
    now = datetime(2025, 10, 20, 9, 0)
    next_run = main.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 27, 8, 0)

def test_job_runs(monkeypatch):
    sent = []
    def dummy_send_email(subject, body, sender_email, bcc_emails):
        sent.append((subject, body, sender_email, bcc_emails))

    class DummyResponse:
        def output_text(self):
            return {"result": "mocked"}
    class DummyResponses:
        def create(self, *args, **kwargs):
            return DummyResponse()
    class DummyClient:
        responses = DummyResponses()
    monkeypatch.setattr("openai_scheduled_newsletter.generate_newsletters.OpenAI", lambda *args, **kwargs: DummyClient())

    main_mod.generate_newsletters = gn.generate_newsletters
    main_mod._sender_email = "sender@example.com"
    main_mod._bcc_emails = ["a@example.com", "b@example.com"]
    main_mod.job = lambda: gn.generate_newsletters(dummy_send_email, main_mod._sender_email, main_mod._bcc_emails)
    main_mod.job()
    assert len(sent) == 2
    assert sent[0][2] == "sender@example.com"
