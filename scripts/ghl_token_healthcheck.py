#!/usr/bin/env python3
"""Weekly GHL token health check. Pings GHL with the stored PIT; if it's not
200 (token rotated/revoked/expired), emails an alert with fix steps. Stays
SILENT when healthy so it never adds inbox noise. Env: GHL_PIT, GHL_LOCATION_ID,
GMAIL_USERNAME, GMAIL_APP_PASSWORD, BRIEF_RECIPIENTS."""
import os, ssl, smtplib, urllib.request
from email.mime.text import MIMEText

PIT = os.environ["GHL_PIT"]; LOC = os.environ["GHL_LOCATION_ID"]
H = {"Authorization": f"Bearer {PIT}", "Version": "2021-07-28", "Accept": "application/json",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
url = f"https://services.leadconnectorhq.com/opportunities/pipelines?locationId={LOC}"
code = None
try:
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=30) as r:
        code = r.status
except urllib.error.HTTPError as e:
    code = e.code
except Exception as e:
    code = f"ERR {e}"

print(f"GHL token health: HTTP {code}")
if code == 200:
    raise SystemExit(0)  # healthy — silent

user = os.environ.get("GMAIL_USERNAME"); pw = os.environ.get("GMAIL_APP_PASSWORD")
rcpts = [r.strip() for r in os.environ.get("BRIEF_RECIPIENTS", "").split(",") if r.strip()]
if user and pw and rcpts:
    body = (f"<h2 style='color:#b91c1c'>⚠️ GoHighLevel token is not working (HTTP {code})</h2>"
            "<p>Your daily Command Center and other GHL reports can't pull data until this is fixed. "
            "The token was almost certainly rotated in GHL without updating the saved copy.</p>"
            "<p><b>2-minute fix:</b> GoHighLevel → Settings → Private Integrations → <b>Claude Audit Agent</b> → "
            "<b>Rotate and expire this token now</b> → copy the new <code>pit-…</code> token, then tell Claude "
            "\"here's the new GHL token\" (or paste it into Documents\Claude\Skills\ghl-pit.txt line 1) and ask Claude to update the GitHub secret.</p>")
    msg = MIMEText(body, "html"); msg["Subject"] = f"⚠️ GHL token DOWN (HTTP {code}) — reports paused until fixed"
    msg["From"] = user; msg["To"] = ", ".join(rcpts)
    ctx = ssl.create_default_context()
    try:
        s = smtplib.SMTP("smtp.gmail.com", 587, timeout=30); s.starttls(context=ctx)
        s.login(user, pw); s.sendmail(user, rcpts, msg.as_string()); s.quit()
        print(f"Alert emailed to {', '.join(rcpts)}")
    except Exception as e:
        print(f"::error::token down AND alert email failed: {e}")
raise SystemExit(1)
