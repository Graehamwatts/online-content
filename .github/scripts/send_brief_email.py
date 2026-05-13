#!/usr/bin/env python3
"""Send the generated brief HTML to graehamwatts@gmail.com via Gmail SMTP."""
import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

GMAIL_USER = os.environ.get("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
SUBJECT = os.environ.get("BRIEF_SUBJECT", "Daily Attribution Brief")
HTML_PATH = os.environ.get("BRIEF_HTML_PATH", "").strip()
TO_ADDR = "graehamwatts@gmail.com"

if not (GMAIL_USER and GMAIL_APP_PASSWORD and HTML_PATH):
    print("Email skipped — missing GMAIL_USER, GMAIL_APP_PASSWORD, or BRIEF_HTML_PATH.")
    raise SystemExit(0)

html_body = Path(HTML_PATH).read_text(encoding="utf-8")

msg = MIMEMultipart("alternative")
msg["Subject"] = SUBJECT
msg["From"] = GMAIL_USER
msg["To"] = TO_ADDR
msg.attach(MIMEText("Open this email in an HTML-capable client to view your brief.", "plain"))
msg.attach(MIMEText(html_body, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    s.sendmail(GMAIL_USER, [TO_ADDR], msg.as_string())
print(f"Sent: {SUBJECT}")
