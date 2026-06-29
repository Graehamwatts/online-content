#!/usr/bin/env python3
"""
PCFS Workflow Watchdog v2 — source-of-truth edition.

Replaces the old n8n-internal watchdog (workflow SMQMpqyKWQVBkiZs) that inferred
success by SEARCHING GMAIL — a flaky proxy that false-flagged workflows which had
actually run (e.g. Sharon notes on 2026-06-27/28). This version asks n8n's own
execution API "did this workflow have a SUCCESSFUL run today?" — the real record,
not the email. It runs as a GitHub Action (cloud, app-independent) so it can also
warn if n8n itself is unreachable — something a watchdog living inside n8n cannot.

Watches ONLY the cloud n8n workflows, which run regardless of any desktop app:
  - Sharon Daily Handwritten Notes (8am PT, every day)
  - CMA Daily Digest (9am PT, every day)
  - PCFS Daily Past Client Call Email (10am PT, weekdays)

It deliberately does NOT watch the app-dependent Claude-Code scheduled tasks
(e.g. the Monday CMA Autobuild) — those need a different, heartbeat-based check,
because the cloud cannot see the local Claude Code scheduler. Claiming to watch
them from here is exactly the kind of false signal we are removing.

Emails BRIEF_RECIPIENTS ONLY when something is actually wrong (a workflow that was
expected today either errored or never ran). A clean day sends nothing — the
GitHub Actions run history is the heartbeat.

Env: N8N_API_URL, N8N_API_KEY, GMAIL_USERNAME, GMAIL_APP_PASSWORD, BRIEF_RECIPIENTS.
"""
import json, os, ssl, smtplib, sys, urllib.request, urllib.error, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")  # Cloudflare blocks bare UAs

API_URL = os.environ["N8N_API_URL"].rstrip("/")
API_KEY = os.environ["N8N_API_KEY"]

# day-of-week: Mon=0 .. Sun=6 (datetime.weekday)
EVERY_DAY = {0, 1, 2, 3, 4, 5, 6}
WEEKDAYS = {0, 1, 2, 3, 4}

WATCHED = [
    {"name": "Sharon Daily Handwritten Notes",   "id": "7CxqNkCQAuw1noGL", "time": "8am PT",  "days": EVERY_DAY},
    {"name": "CMA Daily Digest",                  "id": "LHGnZC2X2KKXljB0", "time": "9am PT",  "days": EVERY_DAY},
    {"name": "PCFS Daily Past Client Call Email", "id": "whjMmVXawdg1Ingx", "time": "10am PT", "days": WEEKDAYS},
]


def api_get(path):
    """GET the n8n API with the browser UA + key. Retries once on transient error."""
    req = urllib.request.Request(API_URL + path,
                                 headers={"X-N8N-API-KEY": API_KEY, "Accept": "application/json", "User-Agent": UA})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def executions_today(wf_id, today_pt):
    """Return (had_success, had_error, last_started_pt) for this workflow's runs today (PT)."""
    data = api_get(f"/api/v1/executions?workflowId={wf_id}&limit=40")
    had_success = had_error = False
    last_started = None
    for ex in data.get("data", []):
        started = ex.get("startedAt") or ex.get("createdAt")
        if not started:
            continue
        dt = datetime.datetime.fromisoformat(started.replace("Z", "+00:00")).astimezone(PT)
        if dt.date() != today_pt:
            continue
        if last_started is None or dt > last_started:
            last_started = dt
        st = (ex.get("status") or "").lower()
        if st == "success":
            had_success = True
        elif st in ("error", "crashed", "failed"):
            had_error = True
    return had_success, had_error, last_started


def main():
    now_pt = datetime.datetime.now(PT)
    today_pt = now_pt.date()
    dow = now_pt.weekday()
    today_str = now_pt.strftime("%A, %B %-d, %Y") if os.name != "nt" else now_pt.strftime("%A, %B %d, %Y")

    # Is n8n itself reachable? If not, that's the loudest possible failure.
    n8n_down = False
    try:
        api_get("/api/v1/workflows?limit=1")
    except Exception as e:  # noqa: BLE001
        n8n_down = True
        n8n_err = str(e)

    results = []
    if not n8n_down:
        for wf in WATCHED:
            if dow not in wf["days"]:
                results.append({**wf, "state": "not_expected"})
                continue
            try:
                ok, err, last = executions_today(wf["id"], today_pt)
            except Exception as e:  # noqa: BLE001
                results.append({**wf, "state": "check_failed", "detail": str(e)})
                continue
            if ok:
                results.append({**wf, "state": "ok", "last": last})
            elif err:
                results.append({**wf, "state": "errored", "last": last})
            else:
                results.append({**wf, "state": "missed"})

    problems = [r for r in results if r["state"] in ("missed", "errored", "check_failed")]
    expected = [r for r in results if r["state"] != "not_expected"]
    ok_ones = [r for r in results if r["state"] == "ok"]

    # Log everything (visible in the Actions run)
    print(f"PCFS Watchdog v2 — {today_str} (PT)", flush=True)
    if n8n_down:
        print(f"  n8n API UNREACHABLE: {n8n_err}", flush=True)
    for r in results:
        line = f"  [{r['state']}] {r['name']} ({r['time']})"
        if r.get("last"):
            line += f" last run {r['last'].strftime('%I:%M %p PT')}"
        if r.get("detail"):
            line += f" — {r['detail']}"
        print(line, flush=True)

    # Decide whether to alert
    alert = n8n_down or bool(problems)
    if not alert:
        print(f"All {len(expected)} expected workflows ran today. No alert sent.", flush=True)
        _emit_output(False, 0)
        return

    # Build the alert email
    if n8n_down:
        status = "🚨 n8n is UNREACHABLE"
        summary = (f"The watchdog could not reach n8n's API ({API_URL}). None of today's "
                   f"PCFS cloud workflows can be confirmed. This usually means an n8n cloud "
                   f"outage or an expired API key. Error: {n8n_err}")
    else:
        n = len(problems)
        status = f"🚨 {n} PCFS workflow{'s' if n != 1 else ''} need attention"
        summary = (f"{n} cloud workflow{'s' if n != 1 else ''} expected today ({today_str}) "
                   f"did not record a successful run. {len(ok_ones)} of {len(expected)} ran clean.")

    rows = []
    for r in results:
        if r["state"] == "ok":
            badge, color = "✅ ran", "#16a34a"
            extra = f"last run {r['last'].strftime('%-I:%M %p PT') if os.name!='nt' else r['last'].strftime('%I:%M %p PT')}" if r.get("last") else ""
        elif r["state"] == "missed":
            badge, color = "❌ no run today", "#dc2626"; extra = "no execution recorded"
        elif r["state"] == "errored":
            badge, color = "⚠️ errored", "#d97706"; extra = "ran but the execution failed — open it in n8n"
        elif r["state"] == "check_failed":
            badge, color = "❓ couldn't check", "#6b7280"; extra = r.get("detail", "")
        else:
            badge, color = "· not scheduled today", "#9ca3af"; extra = ""
        rows.append(
            f'<tr><td style="padding:8px 12px;border-bottom:1px solid #eee">'
            f'<b>{r["name"]}</b><br><span style="color:#888;font-size:12px">{r["time"]}</span></td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #eee;color:{color};font-weight:600;white-space:nowrap">{badge}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #eee;color:#666;font-size:13px">{extra}</td></tr>')

    fix = ("Open the n8n <b>Executions</b> list for the flagged workflow — the most recent "
           "errored run shows the failing node + reason. After fixing, re-run it from "
           "Executions → the workflow → Execute.") if not n8n_down else (
           "Check n8n cloud status and the API key. If n8n is up, the key in the "
           "<code>N8N_API_KEY</code> GitHub secret may have been rotated.")

    html = f"""<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;color:#222;max-width:680px;padding:8px">
  <div style="background:#dc2626;color:#fff;padding:14px 18px;border-radius:6px;margin-bottom:16px">
    <div style="font-size:12px;opacity:.9;letter-spacing:1px;text-transform:uppercase">PCFS Workflow Watchdog · {today_str}</div>
    <div style="font-size:22px;font-weight:700;margin-top:4px">{status}</div>
    <div style="font-size:14px;margin-top:6px;opacity:.95">{summary}</div>
  </div>
  <table style="border-collapse:collapse;width:100%;margin:8px 0 18px">{''.join(rows)}</table>
  <h3 style="margin:0 0 6px">🛠️ Fix</h3>
  <p style="margin:4px 0;color:#333">{fix}</p>
  <hr style="margin:22px 0 12px;border:none;border-top:1px solid #eee">
  <p style="color:#888;font-size:11px;margin:0">
    PCFS Workflow Watchdog v2 · GitHub Action <code>pcfs-watchdog.yml</code> · runs daily ~12pm PT.
    Detection = n8n execution records (the real source of truth), not Gmail search.
    Covers the cloud n8n workflows only; the Monday CMA Autobuild is an app-dependent
    Claude-Code task watched separately.
  </p>
</div>"""

    _send(status, today_str, summary, html)
    _emit_output(True, len(problems))


def _send(status, today_str, summary, html):
    user = os.environ.get("GMAIL_USERNAME"); pw = os.environ.get("GMAIL_APP_PASSWORD")
    rcpts = [r.strip() for r in os.environ.get("BRIEF_RECIPIENTS", "").split(",") if r.strip()]
    if not (user and pw and rcpts):
        print("::warning::Email skipped — GMAIL_USERNAME/GMAIL_APP_PASSWORD/BRIEF_RECIPIENTS not all set")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{status} ({today_str})"
    msg["From"] = user; msg["To"] = ", ".join(rcpts)
    msg.attach(MIMEText(summary, "plain"))
    msg.attach(MIMEText(html, "html"))
    ctx = ssl.create_default_context()
    for host, port, mode in [("smtp.gmail.com", 587, "starttls"), ("smtp.gmail.com", 465, "ssl")]:
        try:
            if mode == "starttls":
                s = smtplib.SMTP(host, port, timeout=30); s.starttls(context=ctx)
            else:
                s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
            s.login(user, pw); s.sendmail(user, rcpts, msg.as_string()); s.quit()
            print(f"Alert emailed to {', '.join(rcpts)} via {host}:{port}", flush=True)
            return
        except Exception as e:  # noqa: BLE001
            print(f"  {host}:{port} failed: {e}", flush=True)
    print("::error::Watchdog alert email failed on all SMTP routes"); sys.exit(1)


def _emit_output(alerted, n_problems):
    go = os.environ.get("GITHUB_OUTPUT")
    if go:
        with open(go, "a") as f:
            f.write(f"alerted={'true' if alerted else 'false'}\nproblems={n_problems}\n")


if __name__ == "__main__":
    main()
