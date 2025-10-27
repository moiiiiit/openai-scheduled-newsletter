import uvicorn
import json
import os
import threading
from .cron_job import run_scheduler
from .generate_newsletters import generate_newsletter_for_prompt, get_all_prompts

# Cache sender_email and bcc_emails at module level
_sender_email = os.environ.get("SENDER_EMAIL")
if not _sender_email:
    raise ValueError("SENDER_EMAIL not found in environment variables")
_emails_json = os.environ.get("EMAILS_JSON")
if not _emails_json:
    raise ValueError("EMAILS_JSON not found in environment variables")
_recipients = json.loads(_emails_json)
_bcc_emails = [r["email"] for r in _recipients]


def main():
    print("[ENV] SENDER_EMAIL:", os.environ.get("SENDER_EMAIL"))
    print("[ENV] EMAILS_JSON:", os.environ.get("EMAILS_JSON"))
    print("[ENV] PROMPTS_JSON:", os.environ.get("PROMPTS_JSON"))
    print("[ENV] OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))

    def start_api():
        uvicorn.run("openai_scheduled_newsletter.api:app", host="0.0.0.0", port=8000, reload=False)
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    run_scheduler()


def generate_all_newsletters(sender_email, bcc_emails):
    prompts = get_all_prompts()
    for prompt in prompts:
        generate_newsletter_for_prompt(prompt, sender_email, bcc_emails)


if __name__ == "__main__":
    import sys
    if "--run-now" in sys.argv:
        generate_all_newsletters(_sender_email, _bcc_emails)
    else:
        main()
