

from .cron_job import run_scheduler
from .generate_newsletters import generate_newsletters
from .send_email import send_email
import os
import json

# Cache sender_email and bcc_emails at module level
_sender_email = os.environ.get('SENDER_EMAIL')
if not _sender_email:
    raise ValueError("SENDER_EMAIL not found in environment variables")
_emails_json = os.environ.get('EMAILS_JSON')
if not _emails_json:
    raise ValueError("EMAILS_JSON not found in environment variables")
_recipients = json.loads(_emails_json)
_bcc_emails = [r['email'] for r in _recipients]

def main():
    run_scheduler()

if __name__ == "__main__":
    import sys
    if "--run-now" in sys.argv:
        generate_newsletters(send_email, _sender_email, _bcc_emails)
    else:
        main()
