from .logger import logger
from .generate_newsletters import load_prompts, call_openai_api
from .send_email import send_email
import os
import json
import time
from croniter import croniter
from datetime import datetime
import threading

# Cache sender_email and bcc_emails at module level
_sender_email = os.environ.get('SENDER_EMAIL')
if not _sender_email:
    raise ValueError("SENDER_EMAIL not found in environment variables")
_emails_json = os.environ.get('EMAILS_JSON')
if not _emails_json:
    raise ValueError("EMAILS_JSON not found in environment variables")
_recipients = json.loads(_emails_json)
_bcc_emails = [r['email'] for r in _recipients]

def get_next_cron_time(cron_expr, base_time=None):
    if base_time is None:
        base_time = datetime.now()
    return croniter(cron_expr, base_time).get_next(datetime)

def job_for_prompt(prompt_obj):
    def single_prompt_newsletter(send_email_func, sender_email, bcc_emails):
        api_key = os.environ.get('OPENAI_API_KEY')
        model = prompt_obj['model']
        prompt = prompt_obj['prompt']
        logger.info(f"Generating newsletter for model={model} (cron={prompt_obj.get('cron')})")
        try:
            result = call_openai_api(api_key, model, prompt)
        except Exception as e:
            logger.error(f"Error for model={model}: {e}")
            result = {"error": str(e)}
        if result and not (isinstance(result, dict) and "error" in result):
            subject = f"Newsletter for model: {model}"
            body = str(result)
            try:
                send_email_func(subject, body, sender_email, bcc_emails)
                logger.info(f"Newsletter sent for model={model}")
            except Exception as e:
                logger.error(f"Email send failed for model={model}: {e}")
        else:
            logger.error(f"Skipping email for model={model} due to error: {result}")
    return single_prompt_newsletter

def run_cron_scheduler_for_prompt(prompt_obj):
    cron_expr = prompt_obj.get('cron', "0 8 * * 1")
    logger.info(f"Scheduler job scheduled for model={prompt_obj.get('model')} with cron: {cron_expr}")
    next_run = get_next_cron_time(cron_expr)
    while True:
        now = datetime.now()
        if now >= next_run:
            job_for_prompt(prompt_obj)(send_email, _sender_email, _bcc_emails)
            logger.info(f"Job executed for model={prompt_obj.get('model')} at {now}")
            next_run = get_next_cron_time(cron_expr, now)
        time.sleep(30)

def run_scheduler():
    prompts = load_prompts()
    threads = []
    for prompt_obj in prompts:
        t = threading.Thread(target=run_cron_scheduler_for_prompt, args=(prompt_obj,), daemon=True)
        t.start()
        threads.append(t)
    # Keep main thread alive
    while True:
        time.sleep(60)
