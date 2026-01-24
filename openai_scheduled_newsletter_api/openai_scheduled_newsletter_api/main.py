"""Entry point for the FastAPI application."""
from openai_scheduled_newsletter_api.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
