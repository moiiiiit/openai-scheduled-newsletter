import json
import os
import threading
import time
from datetime import datetime

from croniter import croniter

from .generate_newsletters import generate_newsletter_for_prompt, get_all_prompts
from .logger import logger


# Helper to get sender and bcc emails from environment
def get_sender_and_bcc():
    sender_email = os.environ.get("SENDER_EMAIL")
    if not sender_email:
        raise ValueError("SENDER_EMAIL not found in environment variables")
    emails_json = os.environ.get("EMAILS_JSON")
    if not emails_json:
        raise ValueError("EMAILS_JSON not found in environment variables")
    recipients = json.loads(emails_json)
    bcc_emails = [r["email"] for r in recipients]
    return sender_email, bcc_emails


def get_next_cron_time(cron_expr, base_time=None):
    if base_time is None:
        base_time = datetime.now()
    return croniter(cron_expr, base_time).get_next(datetime)


def job_for_prompt(prompt_obj):
    def single_prompt_newsletter(sender_email, bcc_emails):
        generate_newsletter_for_prompt(prompt_obj, sender_email, bcc_emails)
    return single_prompt_newsletter


def run_scheduler():
    prompts = get_all_prompts()
    threads = []
    for prompt_obj in prompts:
        t = threading.Thread(target=run_cron_scheduler_for_prompt, args=(prompt_obj,), daemon=True)
        t.start()
        threads.append(t)
    # Keep main thread alive
    while True:
        time.sleep(60)

def run_cron_scheduler_for_prompt(prompt_obj):
    cron_expr = prompt_obj.get("cron", "0 8 * * 1")
    logger.info(f"Scheduler job scheduled for model={prompt_obj.get('model')} with cron: {cron_expr}")
    next_run = get_next_cron_time(cron_expr)
    sender_email, bcc_emails = get_sender_and_bcc()
    while True:
        now = datetime.now()
        if now >= next_run:
            job_for_prompt(prompt_obj)(sender_email, bcc_emails)
            logger.info(f"Job executed for model={prompt_obj.get('model')} at {now}")
            next_run = get_next_cron_time(cron_expr, now)
        time.sleep(30)