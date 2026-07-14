import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app


def send_email(to, subject, html, attachment_path=None):
    cfg = current_app.config
    msg = MIMEMultipart()
    msg["From"] = cfg["MAIL_SENDER"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=5) as s:
            s.send_message(msg)
        return True
    except Exception as e:  # Mailhog down / unreachable — don't fail the job
        current_app.logger.warning(f"Email to {to} not sent: {e}")
        return False
