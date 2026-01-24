"""Job entry point - execute all newsletters once."""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared'))
from openai_scheduled_newsletter.generate_newsletters import generate_newsletter_for_prompt, get_all_prompts


def main():
    """Execute all newsletters once. This runs as a scheduled job in Azure ACI."""
    print("[ENV] SENDER_EMAIL:", os.environ.get("SENDER_EMAIL"))
    print("[ENV] EMAILS_JSON:", os.environ.get("EMAILS_JSON"))
    print("[ENV] PROMPTS_JSON:", os.environ.get("PROMPTS_JSON"))
    print("[ENV] OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))
    print("[JOB] Starting newsletter generation...")

    # Validate required environment variables
    sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_email:
        raise ValueError("SENDER_EMAIL not found in environment variables")
    
    emails_json = os.environ.get("EMAILS_JSON")
    if not emails_json:
        raise ValueError("EMAILS_JSON not found in environment variables")
    
    recipients = json.loads(emails_json)
    bcc_emails = [r["email"] for r in recipients]

    # Generate newsletters for all prompts
    prompts = get_all_prompts()
    print(f"[JOB] Found {len(prompts)} prompts to process")
    
    for prompt in prompts:
        try:
            print(f"[JOB] Processing: {prompt.get('name', 'unknown')}")
            generate_newsletter_for_prompt(prompt, sender_email, bcc_emails)
        except Exception as e:
            print(f"[ERROR] Failed to process prompt {prompt.get('name', 'unknown')}: {e}")
    
    print("[JOB] Newsletter generation complete")


def generate_all_newsletters(sender_email, bcc_emails):
    prompts = get_all_prompts()
    for prompt in prompts:
        generate_newsletter_for_prompt(prompt, sender_email, bcc_emails)


if __name__ == "__main__":
    main()
