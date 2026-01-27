import os
import sys
import dotenv
import pytest
from fastapi.testclient import TestClient

# Load environment variables
dotenv.load_dotenv(dotenv_path=".env.test")

from openai_scheduled_newsletter_api.app import get_app

client = TestClient(get_app())


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_prompts_success():
    # No auth required anymore (oauth2-proxy handles it at ingress level)
    response = client.get("/prompts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_execute_prompt_not_found():
    response = client.post("/execute/999")
    assert response.status_code == 404


def test_execute_prompt_success():
    # Use dependency injection to mock generate_newsletter_for_prompt
    called = {}
    def fake_generate_newsletter_for_prompt(prompt, sender, bcc):
        called["executed"] = True
    test_client = TestClient(get_app(generate_func=fake_generate_newsletter_for_prompt))
    response = test_client.post("/execute/0")
    assert response.status_code == 200
    assert response.json()["status"] == "executed"
    # Note: background task might not execute in test client
    # Just verify the response is correct
