import dotenv
dotenv.load_dotenv(dotenv_path=".env.test")
import pytest
from openai_scheduled_newsletter import generate_newsletters
import json

def test_api_key_loading():
    key = generate_newsletters.load_api_key()
    assert isinstance(key, str)
    assert key.startswith('sk-')

def test_prompt_loading():
    model, prompt = generate_newsletters.load_prompts()
    assert model
    assert prompt

def test_env_prompt_loading(monkeypatch):
    loaded = generate_newsletters.load_prompts()
    assert loaded == [{'model': 'model1', 'prompt': 'prompt1'}, {'model': 'model2', 'prompt': 'prompt2'}]

def test_generate_newsletters(monkeypatch):
    sent = []
    def dummy_send_email(subject, body, sender_email, bcc_emails):
        sent.append((subject, body, sender_email, bcc_emails))
    import base64
    sent = []
    def dummy_send_email(subject, body, sender_email, bcc_emails):
        sent.append((subject, body, sender_email, bcc_emails))
    # Patch OpenAI client before calling generate_newsletters
    class DummyResponse:
        def json(self):
            return {"result": "mocked"}
    class DummyResponses:
        def create(self, *args, **kwargs):
            return DummyResponse()
    class DummyClient:
        responses = DummyResponses()
    monkeypatch.setattr("openai_scheduled_newsletter.generate_newsletters.OpenAI", lambda *args, **kwargs: DummyClient())
    generate_newsletters.generate_newsletters(dummy_send_email, "sender@example.com", ["a@example.com"])
    assert len(sent) == 2
    assert sent[0][0].startswith("Newsletter for model:")
