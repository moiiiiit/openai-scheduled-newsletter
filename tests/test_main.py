import dotenv
dotenv.load_dotenv(dotenv_path=".env.test")
import schedule
import datetime
import datetime
import pytest
from deepseek_daily_newsletter import main
from deepseek_daily_newsletter import main as main_mod
import deepseek_daily_newsletter.generate_newsletters as gn

def test_job_scheduled():
    schedule.clear()
    main.setup_scheduler()
    jobs = schedule.get_jobs()
    # Check for a job scheduled every Monday at 08:00
    found = False
    for job in jobs:
        if job.unit == 'weeks' and job.at_time == datetime.time(8, 0) and job.start_day == 'monday':
            found = True
    assert found, "No job scheduled for Monday at 08:00"

def test_job_runs(monkeypatch):
    sent = []
    def dummy_send_email(subject, body, sender_email, bcc_emails):
        sent.append((subject, body, sender_email, bcc_emails))

    # Patch OpenAI client
    class DummyResponse:
        def json(self):
            return {"result": "mocked"}
    class DummyCompletions:
        def create(self, *args, **kwargs):
            return DummyResponse()
    class DummyChat:
        completions = DummyCompletions()
    monkeypatch.setattr(gn, "client", type("DummyClient", (), {"chat": DummyChat()})())

    main_mod.generate_newsletters = gn.generate_newsletters
    main_mod._sender_email = "sender@example.com"
    main_mod._bcc_emails = ["a@example.com", "b@example.com"]
    main_mod.job = lambda: gn.generate_newsletters(dummy_send_email, main_mod._sender_email, main_mod._bcc_emails)
    main_mod.job()
    assert len(sent) == 2
    assert sent[0][2] == "sender@example.com"
