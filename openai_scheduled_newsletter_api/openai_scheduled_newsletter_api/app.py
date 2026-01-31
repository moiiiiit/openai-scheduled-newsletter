from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
import os
from typing import Callable, Optional, Any

from openai_scheduled_newsletter.generate_newsletters import get_all_prompts, generate_newsletter_for_prompt


def get_authenticated_user(request: Request) -> dict:
    """Extract authenticated user info from oauth2-proxy headers."""
    user = {
        "email": request.headers.get("X-Auth-Request-Email", "unknown"),
        "user": request.headers.get("X-Auth-Request-User", "unknown"),
        "groups": request.headers.get("X-Auth-Request-Groups", "").split(",") if request.headers.get("X-Auth-Request-Groups") else [],
    }
    return user


def get_app(generate_func: Optional[Callable[[Any, str, list], None]] = None) -> FastAPI:
    app = FastAPI(title="OpenAI Newsletter API")
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "test@example.com")
    
    bcc_emails = []
    bcc_emails_str = os.environ.get("BCC_EMAILS")
    if bcc_emails_str:
        bcc_emails = [e.strip() for e in bcc_emails_str.split(",") if e.strip()]

    if generate_func is None:
        generate_func = generate_newsletter_for_prompt

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.get("/user")
    def get_user(request: Request):
        """Return authenticated user info from oauth2-proxy."""
        user = get_authenticated_user(request)
        return user

    @app.get("/prompts")
    def list_prompts():
        """Return all configured prompts."""
        return get_all_prompts()

    @app.post("/execute/{prompt_idx}")
    def execute_prompt(
        prompt_idx: int,
        background_tasks: BackgroundTasks,
        request: Request,
    ):
        """Schedule prompt execution asynchronously and return immediately."""
        # Require authentication via oauth2-proxy
        user = get_authenticated_user(request)
        if user["email"] == "unknown":
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        prompts = get_all_prompts()
        if not (0 <= prompt_idx < len(prompts)):
            raise HTTPException(status_code=404, detail="Prompt not found")
        prompt = prompts[prompt_idx]
        sender = SENDER_EMAIL or "test@example.com"
        bcc = bcc_emails or ["test@example.com"]
        background_tasks.add_task(generate_func, prompt, sender, bcc)
        return {"status": "executed", "prompt": prompt, "user": user["email"]}

    return app


app = get_app()
