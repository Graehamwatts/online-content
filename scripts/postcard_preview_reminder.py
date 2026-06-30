#!/usr/bin/env python3
"""
Farming-postcard preview REMINDER — server-side safety net.

Why this exists: the postcard "hook options" preview used to be a LOCAL Claude Code
scheduled task, which only fires while the desktop app is open. On 2026-06-24 the app
was closed, the task missed its window, and the July 1 preview silently never sent —
discovered 5 days later with 2 days to the drop. This GitHub Action runs headless on
GitHub's servers (app-independent) on the 8th and 24th and GUARANTEES a reminder lands
in the inbox, so a missed preview can never again pass unnoticed.

It is deterministic (no LLM, no cross-repo reads required) — it tells Graeham + Peter a
preview is due, links the live archive + the last card shipped, restates the
anti-repetition rules, and tells them to open Cowork and run the `farming-postcard`
skill (Workflow B) to generate the actual 3-5 options. Phase 2 (later) can add an LLM
API key secret so this Action generates the options itself.

Env: GMAIL_USERNAME, GMAIL_APP_PASSWORD (required for send).
     POSTCARD_RECIPIENTS (optional CSV; defaults to Graeham + Peter).
     FORCE_TARGET (optional 'YYYY-MM-DD' to override computed drop date, for manual runs).
"""
import json, os, ssl, smtplib, sys, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ARCHIVE_URL = "https://graehamwatts.github.io/online-content/farming-postcards/"
REPO_ARCHIVE = os.path.join(os.path.dirname(__file__), "..", "farming-postcards", "archive.json")


def compute_target(today: datetime.date) -> str:
    """8th -> the 15th of this month; 24th -> the 1st of next month; else nearest upcoming."""
    forced = os.environ.get("FORCE_TARGET", "").strip()
    if forced:
        return forced
    d = today.day
    if d <= 8:
        return today.replace(day=15).isoformat()
    if d <= 24:
        # roll to the 1st of next month
        nxt = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        return nxt.isoformat()
    # after the 24th, next drop is the 15th of next month
    nxt = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return nxt.replace(day=15).isoformat()


def last_card():
    """Best-effort: surface the most recently dated card from the archive."""
    try:
        with open(REPO_ARCHIVE, encoding="utf-8") as f:
            cards = json.load(f).get("cards", [])
        cards = [c for c in cards if c.get("mail_date")]
        cards.sort(key=lambda c: c["mail_date"], reverse=True)
        return cards[0] if cards else None
    except Exception as e:
        print(f"  (could not read archive.json: {e})", flush=True)
        return None


def main():
    today = datetime.date.today()
    target = compute_target(today)
    target_d = datetime.date.fromisoformat(target)
    slot = "15th-of-month" if target_d.day == 15 else "1st-of-month"
    pretty = target_d.strftime("%B %-d, %Y") if os.name != "nt" else target_d.strftime("%B %d, %Y").replace(" 0", " ")
    deadline = (target_d - datetime.timedelta(days=3)).strftime("%B %d, %Y").replace(" 0", " ")

    prev = last_card()
    prev_line = ""
    if prev:
        prev_line = (f'Last card on file: <b>{prev.get("mail_date")}</b> — '
                     f'{prev.get("archetype","?")} ("{prev.get("front_headline","")}"), '
                     f'CTA: {prev.get("cta_type","?")}.')

    cadence = ("education / pride angle (Equity, Prop 19, Neighbor envy)" if target_d.day == 1
               else "scarcity / timing angle (Buyer-tagged, Low-inventory, Quiet sale, Local proof)")

    subject = f"\U0001F4EC Postcard preview DUE — {slot} drop ({pretty}) — generate options by {deadline}"

    text = (f"A farming-postcard preview is due.\n\n"
            f"Drop: {pretty} ({slot}).\n"
            f"Generate + pick options by: {deadline}.\n\n"
            f"To generate: open Cowork and run the farming-postcard skill (Workflow B), "
            f"or just reply here and Claude will build the options.\n\n"
            f"Archive: {ARCHIVE_URL}\n\n"
            f"Cadence lean for this slot: {cadence}.\n"
            f"Differentiation rules (must pass all 4): fresh archetype (3-card cooldown), "
            f"CTA destination differs from last 2 cards, no Zillow/algorithm villain for 2 cards "
            f"after any villain card, core claim not repeated within 4 cards.\n")
    if prev:
        text += f"\n{prev_line.replace('<b>','').replace('</b>','')}\n"

    html = f"""<div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:0 auto;color:#1A1D2E">
  <div style="border-left:6px solid #C2A14E;padding:18px 22px;background:#FBF7EC;border-radius:4px">
    <div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#A88638;font-weight:700">Farming Postcard · Preview Due</div>
    <h2 style="font-family:Anton,Arial,sans-serif;margin:6px 0 4px;font-size:24px">{slot.replace('-',' ').title()} drop — {pretty}</h2>
    <p style="margin:6px 0;font-size:14px">Generate and pick your options by <b>{deadline}</b> to stay on the print timeline.</p>
    <p style="margin:14px 0 6px;font-size:14px"><b>To generate:</b> open Cowork and run the <b>farming-postcard</b> skill (Workflow B), or reply to this email and Claude will build the 3-5 fresh options.</p>
    <p style="margin:6px 0;font-size:13px">{prev_line}</p>
    <p style="margin:14px 0 4px;font-size:13px;color:#555"><b>Cadence lean:</b> {cadence}.</p>
    <p style="margin:4px 0;font-size:12px;color:#777"><b>Must pass all 4 differentiation axes:</b> fresh archetype (3-card cooldown) · CTA destination differs from last 2 cards · no Zillow/algorithm villain for 2 cards after a villain card · core claim not repeated within 4 cards.</p>
    <p style="margin:16px 0 0"><a href="{ARCHIVE_URL}" style="background:#C2A14E;color:#000;text-decoration:none;font-weight:700;font-size:12px;letter-spacing:1px;padding:10px 16px;border-radius:5px;text-transform:uppercase">Open the archive →</a></p>
    <p style="margin:16px 0 0;font-size:11px;color:#999">Automated safety-net reminder (GitHub Action). Fires the 8th &amp; 24th regardless of whether the desktop app is open — it replaced the local task that silently no-showed for July 1.</p>
  </div>
</div>"""

    user = os.environ.get("GMAIL_USERNAME"); pw = os.environ.get("GMAIL_APP_PASSWORD")
    rcpts = [r.strip() for r in os.environ.get("POSTCARD_RECIPIENTS", "").split(",") if r.strip()]
    if not rcpts:
        rcpts = ["graehamwatts@gmail.com", "graehamwattsvideo@gmail.com"]

    print(f"Target drop={target} slot={slot} deadline={deadline} recipients={rcpts}", flush=True)

    if not (user and pw):
        print("::error::GMAIL_USERNAME/GMAIL_APP_PASSWORD not set — cannot send reminder"); sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = user; msg["To"] = ", ".join(rcpts)
    msg.attach(MIMEText(text, "plain")); msg.attach(MIMEText(html, "html"))

    ctx = ssl.create_default_context(); sent = False
    for host, port, mode in [("smtp.gmail.com", 587, "starttls"), ("smtp.gmail.com", 465, "ssl")]:
        try:
            if mode == "starttls":
                s = smtplib.SMTP(host, port, timeout=30); s.starttls(context=ctx)
            else:
                s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
            s.login(user, pw); s.sendmail(user, rcpts, msg.as_string()); s.quit()
            print(f"Sent postcard reminder to {', '.join(rcpts)} via {host}:{port}", flush=True); sent = True; break
        except Exception as e:
            print(f"  {host}:{port} failed: {e}", flush=True)
    if not sent:
        print("::error::Postcard reminder email failed on all SMTP routes"); sys.exit(1)


if __name__ == "__main__":
    main()
