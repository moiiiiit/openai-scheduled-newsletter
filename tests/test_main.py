import openai_scheduled_newsletter.generate_newsletters as gn
from openai_scheduled_newsletter import cron_job


def test_get_next_cron_time() -> None:
    from datetime import datetime
    cron_expr = "0 8 * * 1"  # Monday 8am
    now = datetime(2025, 10, 20, 7, 0)  # Monday, 7am
    next_run = cron_job.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 20, 8, 0)
    # If now is after 8am, next Monday
    now = datetime(2025, 10, 20, 9, 0)
    next_run = cron_job.get_next_cron_time(cron_expr, now)
    assert next_run == datetime(2025, 10, 27, 8, 0)


def test_job_runs(monkeypatch) -> None:
    sent = []
    def dummy_send_email(subject: str, body: str, sender_email: str, bcc_emails: list) -> None:
        sent.append((subject, body, sender_email, bcc_emails))

    class DummyResponse:
        def output_text(self) -> dict:
            return {"result": "mocked"}
    class DummyResponses:
        def create(self, *args, **kwargs) -> "DummyResponse":
            return DummyResponse()
    class DummyClient:
        responses = DummyResponses()
    monkeypatch.setattr("openai_scheduled_newsletter.generate_newsletters.OpenAI", lambda *args, **kwargs: DummyClient())

    # Patch get_all_prompts to return prompts with 'cron' field
    monkeypatch.setattr(
        gn,
        "get_all_prompts",
        lambda: [
            {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
        ],
    )
    # Simulate the job logic using cron_job's sender/bcc logic
    sender_email = "sender@example.com"
    bcc_emails = ["a@example.com"]
    monkeypatch.setattr(
        gn,
        "send_email",
        dummy_send_email,
    )
    from openai_scheduled_newsletter import main as main_mod
    monkeypatch.setattr(main_mod, "get_all_prompts", lambda: [
        {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
    ])
    def fake_generate_newsletter_for_prompt(prompt: dict, sender: str, bcc: list) -> None:
        dummy_send_email("subject", "body", sender, bcc)
    monkeypatch.setattr(main_mod, "generate_newsletter_for_prompt", fake_generate_newsletter_for_prompt)
    main_mod.generate_all_newsletters(sender_email, bcc_emails)
    assert len(sent) == 1
    assert sent[0][2] == "sender@example.com"


def test_job_runs_multiple_prompts(monkeypatch) -> None:
    sent = []
    from openai_scheduled_newsletter import main as main_mod
    monkeypatch.setattr(main_mod, "get_all_prompts", lambda: [
        {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
        {"model": "model2", "prompt": "prompt2", "cron": "30 9 * * 2"},
    ])
    sender_email = "sender@example.com"
    bcc_emails = ["a@example.com"]
    def fake_generate_newsletter_for_prompt(prompt: dict, sender: str, bcc: list) -> None:
        sent.append(("subject", "body", sender, bcc))
    monkeypatch.setattr(main_mod, "generate_newsletter_for_prompt", fake_generate_newsletter_for_prompt)
    main_mod.generate_all_newsletters(sender_email, bcc_emails)
    assert len(sent) == 2
    assert sent[0][2] == "sender@example.com"
    assert sent[1][2] == "sender@example.com"


def test_generate_all_newsletters(monkeypatch) -> None:
    from openai_scheduled_newsletter import main
    called = []
    prompts = [
        {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
        {"model": "model2", "prompt": "prompt2", "cron": "30 9 * * 2"},
    ]
    monkeypatch.setattr(main, "get_all_prompts", lambda: prompts)
    def fake_generate_newsletter_for_prompt(prompt: dict, sender: str, bcc: list) -> None:
        called.append((prompt, sender, bcc))
    monkeypatch.setattr(main, "generate_newsletter_for_prompt", fake_generate_newsletter_for_prompt)
    main.generate_all_newsletters("sender@example.com", ["a@example.com"])
    assert len(called) == 2
    assert called[0][0]["model"] == "model1"
    assert called[1][0]["model"] == "model2"