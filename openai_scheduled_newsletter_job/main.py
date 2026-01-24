"""Job entry point - execute all newsletters once."""
import json
import os

from openai_scheduled_newsletter.generate_newsletters import (
    generate_newsletter_for_prompt,
    load_prompts,
)
from openai_scheduled_newsletter.logger import logger


def main():
    """Execute all newsletters once. This runs as a scheduled job in Azure ACI."""
    logger.info("[JOB] Starting newsletter generation...")

    # Validate required environment variables
    sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_email:
        raise ValueError("SENDER_EMAIL not found in environment variables")

    # Use BCC_EMAILS if available, fallback to EMAILS_JSON for backward compat
    bcc_emails_str = os.environ.get("BCC_EMAILS")
    if bcc_emails_str:
        bcc_emails = [e.strip() for e in bcc_emails_str.split(",")]
    else:
        # Fallback to EMAILS_JSON
        emails_json = os.environ.get("EMAILS_JSON")
        if emails_json:
            recipients = json.loads(emails_json)
            bcc_emails = [r["email"] for r in recipients]
        else:
            logger.warning("No BCC_EMAILS or EMAILS_JSON provided")
            bcc_emails = []

    # Generate newsletters for all prompts
    try:
        prompts = load_prompts()
        logger.info(f"[JOB] Found {len(prompts)} prompts to process")

        for prompt in prompts:
            try:
                logger.info(f"[JOB] Processing: {prompt.get('name', 'unknown')}")
                generate_newsletter_for_prompt(prompt, sender_email, bcc_emails)
            except Exception as e:
                logger.error(f"[ERROR] Failed to process prompt {prompt.get('name', 'unknown')}: {e}")

        logger.info("[JOB] Newsletter generation complete")
    except Exception as e:
        logger.error(f"[JOB] Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
