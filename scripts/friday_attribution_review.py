#!/usr/bin/env python3
"""
Friday Attribution Review Generator

Pulls this week's (Mon 00:00 PT - Fri 16:00 PT) GHL lead activity, groups by
source, compares to the prior week, generates an HTML email, commits to
GitHub, and sends via Gmail to Graeham + Adrian.

Runs server-side on GitHub Actions because the GHL API is unreachable from
the Claude Code / Cowork sandbox (Cloudflare blocks services.leadconnectorhq.com).
"""

import os
import sys
import smtplib
import requests
import pytz
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# CONFIG
# ============================================================================

GHL_PIT = os.environ.get("GHL_PIT", "").strip()
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "").strip()
GMAIL_USERNAME = os.environ.get("GMAIL_USERNAME", "").strip()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
BRIEF_RECIPIENTS = os.environ.get("BRIEF_RECIPIENTS", "").strip()

if not all([GHL_PIT, GHL_LOCATION_ID, GMAIL_USERNAME, GMAIL_APP_PASSWORD]):
    print("::error::Missing required secrets: GHL_PIT, GHL_LOCATION_ID, GMAIL_USERNAME, GMAIL_APP_PASSWORD")
    sys.exit(1)

RECIPIENTS = [r.strip() for r in BRIEF_RECIPIENTS.split(",") if r.strip()] or \
    ["graehamwatts@gmail.com", "graehamwattsclientcare@gmail.com"]

GHL_API_BASE = "https://services.leadconnectorhq.com"
GHL_VERSION = "2021-07-28"
PT = pytz.timezone("US/Pacific")

# ============================================================================
# HELPERS
# ============================================================================

def ghl_headers():
    return {
        "Authorization": f"Bearer {GHL_PIT}",
        "Version": GHL_VERSION,
        "Content-Type": "application/json",
    }

def week_window_pt():
    """Return (this_week, last_week) as (start_iso, end_iso, label) in PT.
    This week = Monday 00:00 PT through Friday 16:00 PT of the current week
    (or through 'now' if run mid-week / for a dry run)."""
    now_pt = datetime.now(PT)
    monday_this = (now_pt - timedelta(days=now_pt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_this = min(now_pt, monday_this + timedelta(days=4, hours=16))
    monday_last = monday_this - timedelta(days=7)
    end_last = monday_last + timedelta(days=4, hours=16)

    def iso(dt):
        return dt.astimezone(pytz.UTC).isoformat()

    label = f"{monday_this.strftime('%Y-%m-%d')}"
    return (iso(monday_this), iso(end_this)), (iso(monday_last), iso(end_last)), label

def ghl_get_paginated(endpoint, params=None):
    url = f"{GHL_API_BASE}{endpoint}"
    all_data = []
    page = 1
    limit = 100
    while True:
        p = (params or {}).copy()
        p["limit"] = limit
        p["offset"] = (page - 1) * limit
        try:
            resp = requests.get(url, params=p, headers=ghl_headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("opportunities") or data.get("contacts") or []
            if not items:
                break
            all_data.extend(items)
            if len(items) < limit:
                break
            page += 1
        except Exception as e:
            print(f"::warning::Error fetching {endpoint} page {page}: {e}")
            break
    return all_data

def ghl_post_paginated(endpoint, payload):
    url = f"{GHL_API_BASE}{endpoint}"
    all_data = []
    skip = 0
    limit = 100
    while True:
        p = payload.copy()
        p["limit"] = limit
        p["skip"] = skip
        try:
            resp = requests.post(url, json=p, headers=ghl_headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("contacts", [])
            if not items:
                break
            all_data.extend(items)
            if len(items) < limit:
                break
            skip += limit
        except Exception as e:
            print(f"::warning::Error posting to {endpoint} offset {skip}: {e}")
            break
    return all_data

SOURCE_BUCKETS = [
    "Organic Search / SEO", "Google Business Profile", "Paid Ads",
    "Social Organic", "Referral", "Direct / Website", "Cold", "Unknown",
]

def normalize_source(contact):
    source_field = None
    for field in ["contactSource", "source", "attributed_source", "utm_source"]:
        val = contact.get(field)
        if val:
            source_field = str(val).lower().strip()
            break
    custom_fields = contact.get("customFields", {})
    if not source_field and isinstance(custom_fields, dict):
        for key, val in custom_fields.items():
            if val and any(x in key.lower() for x in ["source", "utm", "attributed"]):
                source_field = str(val).lower().strip()
                break
    if not source_field:
        return "Unknown"
    if any(x in source_field for x in ["organic", "seo", "google search", "search", "google"]):
        return "Organic Search / SEO"
    if any(x in source_field for x in ["gmb", "google business", "maps", "local"]):
        return "Google Business Profile"
    if any(x in source_field for x in ["google ads", "meta ads", "facebook ads", "paid", "cpc", "ppc"]):
        return "Paid Ads"
    if any(x in source_field for x in ["instagram", "facebook", "tiktok", "youtube", "social"]):
        return "Social Organic"
    if any(x in source_field for x in ["referral", "sphere", "past client", "agent"]):
        return "Referral"
    if any(x in source_field for x in ["direct", "website", "form", "contact"]):
        return "Direct / Website"
    if any(x in source_field for x in ["cold", "manual"]):
        return "Cold"
    return "Unknown"

# ============================================================================
# PULL DATA
# ============================================================================

print("Pulling GHL data for this week vs last week...")
(this_start, this_end), (last_start, last_end), week_label = week_window_pt()
print(f"  This week: {this_start} to {this_end}")
print(f"  Last week: {last_start} to {last_end}")

all_contacts = ghl_post_paginated("/contacts/search", {
    "query": {"direction": "asc", "sortBy": "dateAdded"},
})
print(f"  Total contacts pulled: {len(all_contacts)}")

contact_source_map = {c.get("id"): normalize_source(c) for c in all_contacts}

all_opportunities = ghl_get_paginated("/opportunities/search", {"location_id": GHL_LOCATION_ID})
print(f"  Total opportunities pulled: {len(all_opportunities)}")

def in_window(iso_ts, start, end):
    return bool(iso_ts) and start <= iso_ts <= end

def week_slice(start, end):
    contacts = [c for c in all_contacts if in_window(c.get("dateAdded"), start, end)]
    opps_created = [o for o in all_opportunities if in_window(o.get("dateAdded"), start, end)]
    opps_won = [
        o for o in all_opportunities
        if "won" in (o.get("status") or "").lower()
        and in_window(o.get("dateUpdated") or o.get("dateAdded"), start, end)
    ]
    by_source = {b: [] for b in SOURCE_BUCKETS}
    for c in contacts:
        by_source[normalize_source(c)].append(c)
    opps_by_source = {b: 0 for b in SOURCE_BUCKETS}
    for o in opps_created:
        opps_by_source[contact_source_map.get(o.get("contactId"), "Unknown")] += 1
    wins_by_source = {b: 0 for b in SOURCE_BUCKETS}
    for o in opps_won:
        wins_by_source[contact_source_map.get(o.get("contactId"), "Unknown")] += 1
    return {
        "contacts": contacts, "opps_created": opps_created, "opps_won": opps_won,
        "by_source": by_source, "opps_by_source": opps_by_source, "wins_by_source": wins_by_source,
    }

this_week = week_slice(this_start, this_end)
last_week = week_slice(last_start, last_end)

# ============================================================================
# BUILD HTML EMAIL
# ============================================================================

def wow_arrow(this_count, last_count):
    if last_count == 0:
        return "→" if this_count == 0 else "↑ new"
    pct = round(((this_count - last_count) / last_count) * 100)
    if pct > 5:
        return f"↑ {pct}%"
    if pct < -5:
        return f"↓ {pct}%"
    return "→ flat"

total_leads = len(this_week["contacts"])
total_opps = len(this_week["opps_created"])
total_wins = len(this_week["opps_won"])
last_total_leads = len(last_week["contacts"])

status_class = "green" if total_leads >= last_total_leads else ("amber" if total_leads >= last_total_leads * 0.75 else "red")
status_text = f"{total_leads} leads this week vs {last_total_leads} last week ({wow_arrow(total_leads, last_total_leads)})"

active_sources = sorted(
    (b for b in SOURCE_BUCKETS if this_week["by_source"][b] or last_week["by_source"][b]),
    key=lambda b: len(this_week["by_source"][b]), reverse=True,
)
top_source = active_sources[0] if active_sources else "Unknown"

rows = ""
for b in active_sources:
    tc = len(this_week["by_source"][b])
    lc = len(last_week["by_source"][b])
    rows += f"""
        <tr>
            <td><span class="source-name">{b}</span></td>
            <td><span class="count-badge">{tc}</span></td>
            <td>{lc}</td>
            <td>{wow_arrow(tc, lc)}</td>
            <td>{this_week["opps_by_source"][b]}</td>
            <td>{this_week["wins_by_source"][b]}</td>
        </tr>"""

html_email = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Attribution Review</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','DM Sans',sans-serif; background:#f5f5f5; color:#0f1729; line-height:1.6; }}
.container {{ max-width:760px; margin:0 auto; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1); }}
.header {{ background:linear-gradient(135deg,#0f1729 0%,#1a2d4d 100%); color:#fff; padding:32px 24px; text-align:center; }}
.header h1 {{ font-size:24px; font-weight:600; margin-bottom:8px; }}
.header p {{ font-size:14px; opacity:0.9; }}
.status-strip {{ background:#27ae60; color:#fff; padding:12px 24px; font-weight:600; text-align:center; font-size:14px; }}
.status-strip.amber {{ background:#f39c12; }}
.status-strip.red {{ background:#e74c3c; }}
.content {{ padding:24px; }}
.kpi-cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:24px; }}
.kpi-card {{ background:#f8f9fa; border-radius:6px; padding:14px 8px; text-align:center; border-left:4px solid #f4b955; }}
.kpi-card .number {{ font-size:24px; font-weight:700; color:#0f1729; margin-bottom:4px; }}
.kpi-card .label {{ font-size:11px; color:#666; text-transform:uppercase; letter-spacing:0.5px; }}
.read-section {{ background:#f0f4f8; border-radius:6px; padding:16px; margin-bottom:24px; border-left:4px solid #f4b955; }}
.read-section h3 {{ font-size:12px; text-transform:uppercase; color:#666; margin-bottom:8px; letter-spacing:0.5px; }}
.read-section p {{ font-size:14px; }}
table {{ width:100%; border-collapse:collapse; margin-bottom:24px; font-size:12px; }}
th {{ background:#0f1729; color:#fff; padding:10px; text-align:left; font-weight:600; text-transform:uppercase; font-size:10px; letter-spacing:0.5px; }}
td {{ padding:10px; border-bottom:1px solid #e0e0e0; }}
tr:nth-child(even) {{ background:#f8f9fa; }}
.source-name {{ font-weight:600; color:#0f1729; }}
.count-badge {{ background:#f4b955; color:#0f1729; padding:3px 8px; border-radius:4px; font-weight:600; font-size:12px; display:inline-block; }}
.footer {{ background:#f8f9fa; padding:16px 24px; text-align:center; font-size:12px; color:#666; border-top:1px solid #e0e0e0; }}
.footer a {{ color:#0f1729; text-decoration:none; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Weekly Attribution Review</h1>
        <p>Week of {week_label}</p>
    </div>
    <div class="status-strip {status_class}">{status_text}</div>
    <div class="content">
        <div class="kpi-cards">
            <div class="kpi-card"><div class="number">{total_leads}</div><div class="label">New Leads</div></div>
            <div class="kpi-card"><div class="number">{total_opps}</div><div class="label">Opportunities</div></div>
            <div class="kpi-card"><div class="number">{total_wins}</div><div class="label">Closed Wins</div></div>
            <div class="kpi-card"><div class="number">{top_source.split(' / ')[0]}</div><div class="label">Top Source</div></div>
        </div>
        <div class="read-section">
            <h3>The Read</h3>
            <p>{total_leads} new leads this week across {len(active_sources)} active sources, {wow_arrow(total_leads, last_total_leads)} vs last week. Top source: {top_source}. {total_wins} closed win{'s' if total_wins != 1 else ''} this week.</p>
        </div>
        <table>
            <thead><tr><th>Source</th><th>Leads (this wk)</th><th>Leads (last wk)</th><th>WoW</th><th>Opps</th><th>Won</th></tr></thead>
            <tbody>{rows if rows else '<tr><td colspan="6">No lead activity this week.</td></tr>'}</tbody>
        </table>
    </div>
    <div class="footer">
        <p>Weekly Attribution Review &middot; Graeham's CRM automation</p>
        <p style="margin-top:8px;"><a href="https://graehamwatts.github.io/online-content/dashboards/attribution/">View Attribution Dashboards</a></p>
    </div>
</div>
</body>
</html>
"""

print("HTML email generated.")

# ============================================================================
# COMMIT
# ============================================================================

dashboard_dir = "dashboards/attribution"
os.makedirs(dashboard_dir, exist_ok=True)
output_file = f"{dashboard_dir}/{week_label}-weekly.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_email)
print(f"Wrote: {output_file}")

with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as out:
    out.write(f"week_label={week_label}\n")
    out.write(f"total_leads={total_leads}\n")
    out.write(f"total_wins={total_wins}\n")
    out.write(f"top_source={top_source}\n")

# ============================================================================
# SEND EMAIL
# ============================================================================

dry_run = os.environ.get("DRY_RUN", "") == "1"
if dry_run:
    print("DRY_RUN=1 set — skipping email send.")
else:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Weekly Attribution Review — Week of {week_label}"
        msg["From"] = GMAIL_USERNAME
        msg["To"] = ", ".join(RECIPIENTS)
        msg.attach(MIMEText(html_email, "html"))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {', '.join(RECIPIENTS)}")
    except Exception as e:
        print(f"::warning::Email send failed: {e}")
        print("Brief still committed to GitHub.")

print("Weekly Attribution Review complete.")
sys.exit(0)
