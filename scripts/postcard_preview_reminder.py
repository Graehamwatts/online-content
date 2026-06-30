#!/usr/bin/env python3
"""
Farming-postcard preview REMINDER + WATCHDOG — server-side safety net.

Why this exists: the postcard "hook options" preview used to be a LOCAL Claude Code
scheduled task, which only fires while the desktop app is open. On 2026-06-24 the app
was closed, the task missed its window, and the July 1 preview silently never sent —
discovered 5 days later with 2 days to the drop. This runs headless on GitHub's servers
(app-independent) and GUARANTEES the inbox hears about every due preview.

Two modes (env MODE):
  remind   (default) — fires the 8th/24th. Computes the drop date, and if no sent-marker
                       exists for that drop, sends the reminder + writes the marker.
                       Idempotent: keyed off the DROP date, so dual cron entries / manual
                       runs / retries never double-send.
  watchdog           — fires daily. If a drop is within 7 days and NO sent-marker exists,
                       sends an escalation (catches missed cron / bad date logic / failed
                       marker commit). Otherwise exits quietly.

Deterministic (no LLM). It tells Graeham + Peter a preview is due, links the live archive
+ last card, restates the 4 anti-repetition rules, and says to open Cowork and run the
`farming-postcard` skill (Workflow B) — or just reply and Claude builds the options.
Phase 2 (later, needs an LLM key secret) can have this Action generate the options itself.

Env: GMAIL_USERNAME, GMAIL_APP_PASSWORD (required to send).
     POSTCARD_RECIPIENTS (optional CSV; default Graeham + Peter).
     MODE = remind | watchdog (default remind).
     FORCE_TARGET = 'YYYY-MM-DD' (optional, manual override of the drop date).
     DRY_RUN = '1' to print instead of send (no marker written).
     GITHUB_RUN_URL (optional, embedded in emails for traceability).
Exit nonzero on any real failure (missing creds, all SMTP routes fail) so the workflow's
if:failure() step opens a GitHub Issue.
"""
import json, os, ssl, smtplib, sys, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ARCHIVE_URL = "https://graehamwatts.github.io/online-content/farming-postcards/"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ARCHIVE = os.path.join(HERE, "..", "farming-postcards", "archive.json")
STATE_DIR = os.path.join(HERE, "..", "automation_state", "farming_postcards")


def la_today():
    """Today's date in America/Los_Angeles (handles PT/PDT without external deps)."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).date()
    except Exception:
        # Fallback: UTC-7 approximation (PDT). Good enough for a date-only guard.
        return (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).date()


def next_drop(today: datetime.date) -> datetime.date:
    """The next upcoming drop date (1st or 15th), strictly >= today."""
    forced = os.environ.get("FORCE_TARGET", "").strip()
    if forced:
        return datetime.date.fromisoformat(forced)
    if today.day < 15:
        return today.replace(day=15)
    nxt = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return nxt


def drop_for_preview(today: datetime.date) -> datetime.date:
    """In remind mode: 8th -> the 15th this month; 24th -> the 1st next month."""
    forced = os.environ.get("FORCE_TARGET", "").strip()
    if forced:
        return datetime.date.fromisoformat(forced)
    if today.day <= 15:
        return today.replace(day=15)
    nxt = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return nxt


def marker_path(drop: datetime.date) -> str:
    return os.path.join(STATE_DIR, f"{drop.isoformat()}-preview.json")


def fmt(d: datetime.date) -> str:
    return d.strftime("%B %d, %Y").replace(" 0", " ")


def last_card():
    try:
        with open(REPO_ARCHIVE, encoding="utf-8") as f:
            cards = [c for c in json.load(f).get("cards", []) if c.get("mail_date")]
        cards.sort(key=lambda c: c["mail_date"], reverse=True)
        return cards[0] if cards else None
    except Exception as e:
        print(f"  (could not read archive.json: {e})", flush=True)
        return None


def build_email(drop: datetime.date, mode: str):
    slot = "15th-of-month" if drop.day == 15 else "1st-of-month"
    deadline = fmt(drop - datetime.timedelta(days=3))
    prev = last_card()
    prev_line = ""
    if prev:
        prev_line = (f'Last card on file: {prev.get("mail_date")} — {prev.get("archetype","?")} '
                     f'("{prev.get("front_headline","")}"), CTA: {prev.get("cta_type","?")}.')
    cadence = ("education / pride angle (Equity, Prop 19, Neighbor envy)" if drop.day == 1
               else "scarcity / timing angle (Buyer-tagged, Low-inventory, Quiet sale, Local proof)")
    run_url = os.environ.get("GITHUB_RUN_URL", "")
    escalation = mode == "watchdog"
    flag = "⚠️ ESCALATION — preview NOT sent" if escalation else "\U0001F4EC Postcard preview DUE"
    subject = f"{flag} — {slot} drop ({fmt(drop)}) — options by {deadline}"

    lead = ("A postcard drop is within 7 days and NO preview/reminder has been recorded for it. "
            "The scheduled reminder may have failed — generate the options now."
            if escalation else "A farming-postcard preview is due.")

    text = (f"{lead}\n\nDrop: {fmt(drop)} ({slot}).\nGenerate + pick options by: {deadline}.\n\n"
            f"To generate: open Cowork and run the farming-postcard skill (Workflow B), "
            f"or reply here and Claude will build the options.\n\nArchive: {ARCHIVE_URL}\n\n"
            f"Cadence lean: {cadence}.\nDifferentiation (must pass all 4): fresh archetype (3-card "
            f"cooldown); CTA destination differs from last 2 cards; no Zillow/algorithm villain for "
            f"2 cards after a villain card; core claim not repeated within 4 cards.\n")
    if prev_line:
        text += f"\n{prev_line}\n"
    if run_url:
        text += f"\nAction run: {run_url}\n"

    accent = "#B4232A" if escalation else "#C2A14E"
    html = f"""<div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:0 auto;color:#1A1D2E">
  <div style="border-left:6px solid {accent};padding:18px 22px;background:#FBF7EC;border-radius:4px">
    <div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:{accent};font-weight:700">{'Farming Postcard · ESCALATION' if escalation else 'Farming Postcard · Preview Due'}</div>
    <h2 style="font-family:Anton,Arial,sans-serif;margin:6px 0 4px;font-size:24px">{slot.replace('-',' ').title()} drop — {fmt(drop)}</h2>
    <p style="margin:6px 0;font-size:14px">{lead} Generate and pick options by <b>{deadline}</b>.</p>
    <p style="margin:14px 0 6px;font-size:14px"><b>To generate:</b> open Cowork and run the <b>farming-postcard</b> skill (Workflow B), or reply to this email and Claude will build the 3-5 fresh options.</p>
    <p style="margin:6px 0;font-size:13px">{prev_line}</p>
    <p style="margin:14px 0 4px;font-size:13px;color:#555"><b>Cadence lean:</b> {cadence}.</p>
    <p style="margin:4px 0;font-size:12px;color:#777"><b>Must pass all 4 differentiation axes:</b> fresh archetype (3-card cooldown) · CTA destination differs from last 2 cards · no Zillow/algorithm villain for 2 cards after a villain card · core claim not repeated within 4 cards.</p>
    <p style="margin:16px 0 0"><a href="{ARCHIVE_URL}" style="background:{accent};color:#fff;text-decoration:none;font-weight:700;font-size:12px;letter-spacing:1px;padding:10px 16px;border-radius:5px;text-transform:uppercase">Open the archive →</a></p>
    <p style="margin:16px 0 0;font-size:11px;color:#999">Automated {'watchdog escalation' if escalation else 'safety-net reminder'} (GitHub Action). Fires regardless of whether the desktop app is open — it replaced the local task that silently no-showed for July 1.{(' Run: '+run_url) if run_url else ''}</p>
  </div>
</div>"""
    return subject, text, html


def send(subject, text, html):
    user = os.environ.get("GMAIL_USERNAME"); pw = os.environ.get("GMAIL_APP_PASSWORD")
    rcpts = [r.strip() for r in os.environ.get("POSTCARD_RECIPIENTS", "").split(",") if r.strip()]
    if not rcpts:
        rcpts = ["graehamwatts@gmail.com", "graehamwattsvideo@gmail.com"]
    if os.environ.get("DRY_RUN") == "1":
        print(f"[DRY_RUN] would send to {rcpts}\n  SUBJECT: {subject}\n--- text ---\n{text}", flush=True)
        return rcpts
    if not (user and pw):
        print("::error::GMAIL_USERNAME/GMAIL_APP_PASSWORD not set — cannot send"); sys.exit(1)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = user; msg["To"] = ", ".join(rcpts)
    msg.attach(MIMEText(text, "plain")); msg.attach(MIMEText(html, "html"))
    ctx = ssl.create_default_context()
    for host, port, mode in [("smtp.gmail.com", 587, "starttls"), ("smtp.gmail.com", 465, "ssl")]:
        try:
            s = smtplib.SMTP(host, port, timeout=30); s.starttls(context=ctx) if mode == "starttls" else None
            if mode == "ssl":
                s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
            s.login(user, pw); s.sendmail(user, rcpts, msg.as_string()); s.quit()
            print(f"Sent to {', '.join(rcpts)} via {host}:{port}", flush=True)
            return rcpts
        except Exception as e:
            print(f"  {host}:{port} failed: {e}", flush=True)
    print("::error::email failed on all SMTP routes"); sys.exit(1)


def write_marker(drop, rcpts):
    os.makedirs(STATE_DIR, exist_ok=True)
    rec = {"drop": drop.isoformat(), "status": "reminder_sent",
           "sent_at": datetime.datetime.utcnow().isoformat() + "Z",
           "recipients": rcpts, "source": os.environ.get("MODE", "remind"),
           "run_url": os.environ.get("GITHUB_RUN_URL", "")}
    with open(marker_path(drop), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
    print(f"Wrote marker {marker_path(drop)}", flush=True)


def main():
    mode = os.environ.get("MODE", "remind").strip().lower()
    today = la_today()
    if mode == "watchdog":
        drop = next_drop(today)
        days = (drop - today).days
        if days > 7:
            print(f"watchdog: next drop {drop} is {days}d out (>7) — nothing to do.", flush=True); return
        if os.path.exists(marker_path(drop)):
            print(f"watchdog: marker exists for {drop} — preview already handled, OK.", flush=True); return
        print(f"watchdog: drop {drop} is {days}d out and NO marker — escalating.", flush=True)
        subject, text, html = build_email(drop, "watchdog")
        send(subject, text, html)
        return
    # remind
    drop = drop_for_preview(today)
    if os.path.exists(marker_path(drop)) and os.environ.get("DRY_RUN") != "1":
        print(f"remind: marker already exists for {drop} — idempotent skip.", flush=True); return
    subject, text, html = build_email(drop, "remind")
    rcpts = send(subject, text, html)
    if os.environ.get("DRY_RUN") != "1":
        write_marker(drop, rcpts)


if __name__ == "__main__":
    main()
