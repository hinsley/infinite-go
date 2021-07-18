# Utilities for sending emails.

from typing import List

import json

import smtplib
import email
import email.mime.text


with open("config.json") as f:
    cfg = json.load(f)

def send_email(subject: str, body: str, to_addrs: List[str]):
    """
    Send an email.

    Args:
        subject: Subject of the email.
        body: Body of the email.
        to_addrs: List of addresses to send the email to.
    """
    # Create the email message.
    msg = email.mime.text.MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = cfg["email"]["address"]
    msg["To"] = ", ".join(to_addrs)

    # Send the email.
    with smtplib.SMTP(cfg["email"]["hostname"], cfg["email"]["port"]) as s:
        s.starttls()
        s.login(cfg["email"]["address"], cfg["email"]["password"])
        s.sendmail(cfg["email"]["address"], to_addrs, msg.as_string())
