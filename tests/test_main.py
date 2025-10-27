import dotenv
dotenv.load_dotenv(dotenv_path=".env.test")

import datetime
import pytest
import openai_scheduled_newsletter.generate_newsletters as gn
from openai_scheduled_newsletter import cron_job

def test_get_next_cron_time():
    from datetime import datetime, timedelta
    cron_expr = "0 8 * * 1"  # Monday 8am
    now = datetime(2025, 10, 20, 7, 0)  # Monday, 7am
    next_run = cron_job.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 20, 8, 0)
    # If now is after 8am, next Monday
    now = datetime(2025, 10, 20, 9, 0)
    next_run = cron_job.get_next_cron_time(cron_expr, now)
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

    # Patch load_prompts to return prompts with 'cron' field
    monkeypatch.setattr(
        gn,
        "load_prompts",
        lambda: [
            {'model': 'model1', 'prompt': 'prompt1', 'cron': '0 8 * * 1'},
        ]
    )
    # Simulate the job logic using cron_job's sender/bcc logic
    sender_email = "sender@example.com"
    bcc_emails = ["a@example.com"]
    gn.generate_newsletters(dummy_send_email, sender_email, bcc_emails)
    assert len(sent) == 1
    assert sent[0][2] == "sender@example.com"

def test_job_runs_multiple_prompts(monkeypatch):
    sent = []
    def dummy_send_email(subject, body, sender_email, bcc_emails):
        sent.append((subject, body, sender_email, bcc_emails))
    import openai_scheduled_newsletter.generate_newsletters as gn
    monkeypatch.setattr(
        gn,
        "load_prompts",
        lambda: [
            {'model': 'model1', 'prompt': 'prompt1', 'cron': '0 8 * * 1'},
            {'model': 'model2', 'prompt': 'prompt2', 'cron': '30 9 * * 2'}
        ]
    )
    monkeypatch.setattr(
        gn,
        "call_openai_api",
        lambda api_key, model, prompt: f"dummy result for {model}"
    )
    sender_email = "sender@example.com"
    bcc_emails = ["a@example.com"]
    gn.generate_newsletters(dummy_send_email, sender_email, bcc_emails)
    assert len(sent) == 2
    assert sent[0][2] == "sender@example.com"
    assert sent[1][2] == "sender@example.com"