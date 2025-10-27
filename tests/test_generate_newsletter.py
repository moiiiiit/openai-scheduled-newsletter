import dotenv

dotenv.load_dotenv(dotenv_path=".env.test")
import json

from openai_scheduled_newsletter import generate_newsletters


def test_api_key_loading() -> None:
    key = generate_newsletters.load_api_key()
    assert isinstance(key, str)
    assert key.startswith("sk-")


def test_prompt_loading() -> None:
    model, prompt = generate_newsletters.load_prompts()
    assert model
    assert prompt


def test_env_prompt_loading(monkeypatch) -> None:
    prompts = [
        {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
    ]
    monkeypatch.setenv("PROMPTS_JSON", json.dumps(prompts))
    loaded = generate_newsletters.load_prompts()
    assert loaded == prompts


def test_generate_newsletters(monkeypatch) -> None:
    sent = []
    def dummy_send_email(subject: str, body: str, sender_email: str, bcc_emails: list) -> None:
        sent.append((subject, body, sender_email, bcc_emails))
    # Patch OpenAI client before calling generate_newsletters
    class DummyResponse:
        def output_text(self) -> dict:
            return {"result": "mocked"}

    class DummyResponses:
        def create(self, *args, **kwargs) -> "DummyResponse":
            return DummyResponse()

    class DummyClient:
        responses = DummyResponses()

    monkeypatch.setattr("openai_scheduled_newsletter.generate_newsletters.OpenAI", lambda *args, **kwargs: DummyClient())
    # Patch load_prompts to return prompts with 'cron' field
    monkeypatch.setattr(
        generate_newsletters,
        "load_prompts",
        lambda: [
            {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
        ],
    )
    monkeypatch.setattr(
        generate_newsletters,
        "send_email",
        dummy_send_email,
    )
    generate_newsletters.generate_newsletter_for_prompt({"model": "model1", "prompt": "prompt1"}, "sender@example.com", ["a@example.com"])
    assert len(sent) == 1
    assert sent[0][0].startswith("Newsletter for model:")


def test_generate_newsletters_multiple_prompts(monkeypatch) -> None:
    sent = []
    def dummy_send_email(subject: str, body: str, sender_email: str, bcc_emails: list) -> None:
        sent.append((subject, body, sender_email, bcc_emails))
    # Patch load_prompts to return multiple prompts with different crons
    monkeypatch.setattr(
        generate_newsletters,
        "load_prompts",
        lambda: [
            {"model": "model1", "prompt": "prompt1", "cron": "0 8 * * 1"},
            {"model": "model2", "prompt": "prompt2", "cron": "30 9 * * 2"},
        ],
    )
    # Patch call_openai_api to return dummy data
    monkeypatch.setattr(
        generate_newsletters,
        "call_openai_api",
        lambda api_key, model, prompt: f"dummy result for {model}",
    )
    monkeypatch.setattr(
        generate_newsletters,
        "send_email",
        dummy_send_email,
    )
    prompts = [
        {"model": "model1", "prompt": "prompt1"},
        {"model": "model2", "prompt": "prompt2"},
    ]
    for prompt in prompts:
        generate_newsletters.generate_newsletter_for_prompt(prompt, "sender@example.com", ["a@example.com"])
    assert len(sent) == 2
    assert sent[0][0].startswith("Newsletter for model:")
    assert sent[1][0].startswith("Newsletter for model:")