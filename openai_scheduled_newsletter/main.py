from .logger import logger

import time
import threading
from croniter import croniter
from datetime import datetime
import os
import json
from .generate_newsletters import generate_newsletters
from .send_email import send_email

# Cache sender_email and bcc_emails at module level
_sender_email = os.environ.get('SENDER_EMAIL')
if not _sender_email:
    raise ValueError("SENDER_EMAIL not found in environment variables")
_emails_json = os.environ.get('EMAILS_JSON')
if not _emails_json:
    raise ValueError("EMAILS_JSON not found in environment variables")
_recipients = json.loads(_emails_json)
_bcc_emails = [r['email'] for r in _recipients]

def job():
    generate_newsletters(send_email, _sender_email, _bcc_emails)

def get_next_cron_time(cron_expr, base_time=None):
    if base_time is None:
        base_time = datetime.now()
    return croniter(cron_expr, base_time).get_next(datetime)

def run_cron_scheduler():
    cron_expr = os.environ.get("SCHEDULE_CRON", "0 8 * * 1")  # Default: Monday 8am
    logger.info(f"Scheduler job scheduled with cron: {cron_expr}")
    next_run = get_next_cron_time(cron_expr)
    while True:
        now = datetime.now()
        if now >= next_run:
            job()
            logger.info(f"Job executed at {now}")
            next_run = get_next_cron_time(cron_expr, now)
        time.sleep(30)

def run_scheduler():
    run_cron_scheduler()

def main():
    run_scheduler()

if __name__ == "__main__":
    import sys
    if "--run-now" in sys.argv:
        from .generate_newsletters import generate_newsletters
        from .send_email import send_email
        generate_newsletters(send_email, _sender_email, _bcc_emails)
    else:
        main()
