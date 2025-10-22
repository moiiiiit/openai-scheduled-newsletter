from .logger import logger
import smtplib
from email.message import EmailMessage
import os

def send_email(subject, body, sender_email, bcc_emails):
    logger.info(f"Preparing email: subject={subject}, sender={sender_email}, bcc={bcc_emails}")
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = sender_email
    msg['Bcc'] = ', '.join(bcc_emails)
    msg.set_content(body)

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_username = os.environ.get("SENDER_EMAIL", sender_email)
    smtp_password = os.environ.get("SENDER_EMAIL_APP_PASSWORD")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
        logger.info(f"Email sent to {bcc_emails}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
