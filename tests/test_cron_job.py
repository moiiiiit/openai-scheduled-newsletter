import threading
import time

from openai_scheduled_newsletter import cron_job


def test_get_next_cron_time_basic():
    from datetime import datetime
    cron_expr = "0 8 * * 1"  # Monday 8am
    now = datetime(2025, 10, 20, 7, 0)  # Monday, 7am
    next_run = cron_job.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 20, 8, 0)  # noqa: S101x
    now = datetime(2025, 10, 20, 9, 0)
    next_run = cron_job.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 27, 8, 0)


def test_job_for_prompt_calls_generate(monkeypatch):
    called = {}
    prompt_obj = {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"}
    def fake_generate_newsletter_for_prompt(p, sender, bcc) -> None:
        called["prompt"] = p
        called["sender"] = sender
        called["bcc"] = bcc
    monkeypatch.setattr(cron_job, "generate_newsletter_for_prompt", fake_generate_newsletter_for_prompt)
    job = cron_job.job_for_prompt(prompt_obj)
    job("sender@example.com", ["a@example.com"])
    assert called["prompt"] == prompt_obj
    assert called["sender"] == "sender@example.com"
    assert called["bcc"] == ["a@example.com"]


def test_run_scheduler_starts_threads(monkeypatch):
    # Patch get_all_prompts to return two prompts
    prompts = [
        {"model": "model1", "prompt": "prompt1", "cron": "* * * * *"},
        {"model": "model2", "prompt": "prompt2", "cron": "* * * * *"},
    ]
    monkeypatch.setattr(cron_job, "get_all_prompts", lambda: prompts)
    # Patch run_cron_scheduler_for_prompt to just sleep a bit and set a flag
    started = []
    def fake_run_cron_scheduler_for_prompt(prompt_obj) -> None:
        started.append(prompt_obj["model"])
        time.sleep(0.1)
    monkeypatch.setattr(cron_job, "run_cron_scheduler_for_prompt", fake_run_cron_scheduler_for_prompt)
    # Run scheduler in a thread so we can stop it
    def run_sched() -> None:
        cron_job.run_scheduler()
    t = threading.Thread(target=run_sched, daemon=True)
    t.start()
    time.sleep(0.2)
    assert "model1" in started and "model2" in started
