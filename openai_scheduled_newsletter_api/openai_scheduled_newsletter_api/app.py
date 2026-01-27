from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
import os
import secrets
from typing import Callable, Optional, Any

from openai_scheduled_newsletter.generate_newsletters import get_all_prompts, generate_newsletter_for_prompt


def get_app(generate_func: Optional[Callable[[Any, str, list], None]] = None) -> FastAPI:
    app = FastAPI(title="OpenAI Newsletter API")
    security = HTTPBasic()
    API_PASSWORD = os.environ.get("API_PASSWORD", "changeme")
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "test@example.com")
    
    bcc_emails = []
    bcc_emails_str = os.environ.get("BCC_EMAILS")
    if bcc_emails_str:
        bcc_emails = [e.strip() for e in bcc_emails_str.split(",") if e.strip()]

    if generate_func is None:
        generate_func = generate_newsletter_for_prompt

    def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
        correct = secrets.compare_digest(credentials.password, API_PASSWORD)
        if not correct:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.get("/prompts")
    def list_prompts(username: str = Depends(verify_password)):
        """Return all configured prompts."""
        return get_all_prompts()

    @app.post("/execute/{prompt_idx}")
    def execute_prompt(prompt_idx: int, username: str = Depends(verify_password)):
        """Execute a prompt by its index in the prompt list."""
        prompts = get_all_prompts()
        if not (0 <= prompt_idx < len(prompts)):
            raise HTTPException(status_code=404, detail="Prompt not found")
        prompt = prompts[prompt_idx]
        sender = SENDER_EMAIL or "test@example.com"
        bcc = bcc_emails or ["test@example.com"]
        generate_func(prompt, sender, bcc)
        return {"status": "executed", "prompt": prompt}

    return app


app = get_app()
