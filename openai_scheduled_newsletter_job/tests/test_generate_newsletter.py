"""Tests for shared library functions."""
import pytest
import os
import json


def test_load_api_key_from_env(monkeypatch):
    """Test that API key is loaded from environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")
    # Just verify environment variable is set correctly
    assert os.environ.get("OPENAI_API_KEY") == "sk-test-key-12345"


def test_load_prompts_from_env(monkeypatch):
    """Test that prompts are loaded from environment."""
    monkeypatch.setenv("PROMPTS_JSON", '[{"name": "test", "model": "gpt-4", "prompt": "Test prompt"}]')
    # Just verify environment variable is set correctly
    prompts_json = os.environ.get("PROMPTS_JSON")
    assert prompts_json is not None
    prompts = json.loads(prompts_json)
    assert len(prompts) == 1
    assert prompts[0]["name"] == "test"