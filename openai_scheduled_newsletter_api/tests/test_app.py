import os
import sys
import dotenv
import base64
import pytest
from fastapi.testclient import TestClient

# Load environment variables
dotenv.load_dotenv(dotenv_path=".env.test")

from openai_scheduled_newsletter_api.app import get_app

API_PASSWORD = os.environ.get("API_PASSWORD", "changeme")
client = TestClient(get_app())


def basic_auth_header(password: str = API_PASSWORD):
    token = base64.b64encode(f"user:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_prompts_auth_required():
    response = client.get("/prompts")
    assert response.status_code == 401


def test_prompts_success():
    response = client.get("/prompts", headers=basic_auth_header())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_execute_prompt_auth_required():
    response = client.post("/execute/0")
    assert response.status_code == 401


def test_execute_prompt_not_found():
    response = client.post("/execute/999", headers=basic_auth_header())
    assert response.status_code == 404


def test_execute_prompt_success():
    # Use dependency injection to mock generate_newsletter_for_prompt
    called = {}
    def fake_generate_newsletter_for_prompt(prompt, sender, bcc):
        called["executed"] = True
    test_client = TestClient(get_app(generate_func=fake_generate_newsletter_for_prompt))
    response = test_client.post("/execute/0", headers=basic_auth_header())
    assert response.status_code == 200
    assert response.json()["status"] == "executed"
    assert called["executed"] is True
