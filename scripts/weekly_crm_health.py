#!/usr/bin/env python3
"""
weekly_crm_health.py - Combined CRM Health Dashboard for Graeham Watts
Outputs: dashboards/health/<YYYY-MM-DD>-health.html
Env: GHL_PIT, GHL_LOCATION_ID, [GHL_API_BASE, GHL_VERSION, WEEK_START_OVERRIDE]
"""

import requests, os, sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import pytz

PT = pytz.timezone("America/Los_Angeles")
GHL_PIT = os.environ["GHL_PIT"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
GHL_BASE = os.environ.get("GHL_API_BASE", "https://services.leadconnectorhq.com")
GHL_VERSION = os.environ.get("GHL_VERSION", "2021-07-28")
WEEK_START_OVERRIDE = os.environ.get("WEEK_START_OVERRIDE", "").strip()
GITHUB_OUTPUT = os.environ.get("GITHUB_OUTPUT", "")

headers = {
    "Authorization": f"Bearer {GHL_PIT}",
    "Version": GHL_VERSION,
    "Content-Type": "application/json",
}

# --- Time windows ---

now_pt = datetime.now(PT)

if WEEK_START_OVERRIDE:
    week_start = PT.localize(datetime.strptime(WEEK_START_OVERRIDE, "%Y-%m-%d"))
else:
    days_since_monday = now_pt.weekday()
    week_start = (now_pt - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

week_end = now_pt
prior_start = week_start - timedelta(days=7)
prior_end = week_start

week_start_utc = week_start.astimezone(timezone.utc)
week_end_utc = week_end.astimezone(timezone.utc)
prior_start_utc = prior_start.astimezone(timezone.utc)
prior_end_utc = prior_end.astimezone(timezone.utc)

date_slug = week_start.strftime("%Y-%m-%d")
week_label = week_start.strftime("%b %-d, %Y")
prior_label = prior_start.strftime("%b %-d")

print(f"Week:  {week_start_utc.date()} -> {week_end_utc.date()}", flush=True)
print(f"Prior: {prior_start_utc.date()} -> {prior_end_utc.date()}", flush=True)

# --- API helpers ---

def get_contacts(start_dt, end_dt, label=""):
    contacts = []
    start_after_ms = int(start_dt.timestamp() * 1000)
    start_after_id = ""
    MAX_PAGES = 20
    for page in range(1, MAX_PAGES + 1):
        params = {
            "locationId": LOCATION_ID,
            "startAfter": start_after_ms,
            "startAfterId": start_after_id,
            "limit": 100,
        }
        r = requests.get(f"{GHL_BASE}/contacts", params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"  {label} contacts error {r.status_code}: {r.text[:200]}", flush=True)
            break
        batch = r.json().get("contacts", [])
        if not batch:
            break
        past_window = False
        for c in batch:
            da = c.get("dateAdded", "")
            if da:
                try:
                    cdt = datetime.fromisoformat(da.replace("Z", "+00:00"))
                    if cdt >= end_dt:
                        past_window = True
                        break
                    contacts.append(c)
                except Exception:
                    pass
        print(f"  {label} contacts p{page}: {len(batch)} fetched, {len(contacts)} in window", flush=True)
        if past_window or len(batch) < 100:
            break
        last = batch[-1]
        last_da = last.get("dateAdded", "")
        if last_da:
            try:
                start_after_ms = int(datetime.fromisoformat(last_da.replace("Z", "+00:00")).timestamp() * 1000)
            except Exception:
                break
        start_after_id = last.get("id", "")
    return contacts


def get_opportunities_in_window(start_dt, end_dt, label=""):
    opps = []
    start_ms = int(start_dt.timestamp() * 1000)
    start_after_id = None
    MAX_PAGES = 10
    for _page in range(MAX_PAGES):
        params = {
            "location_id": LOCATION_ID,
            "startAfter": start_ms,
            "startAfterId": start_after_id or "",
            "limit": 100,
        }
        r = requests.get(f"{GHL_BASE}/opportunities/search", params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"  {label} opps error {r.status_code}: {r.text[:200]}", flush=True)
            break
        batch = r.json().get("opportunities", [])
        past_window = False
        for o in batch:
            cat = o.get("createdAt", "")
            if cat:
                try:
                    odt = datetime.fromisoformat(cat.replace("Z", "+00:00"))
                    if odt >= end_dt:
                        past_window = True
                        break
                    if odt >= start_dt:
                        opps.append(o)
                except Exception:
                    pass
        print(f"  {label} opps batch {_page+1}: {len(batch)} fetched, {len(opps)} in window", flush=True)
        if past_window or len(batch) < 100:
            break
        start_after_id = batch[-1].get("id") if batch else None
    return opps


def get_all_open_opportunities():
    opps = []
    two_yr_ms = int((datetime.now(timezone.utc) - timedelta(days=730)).timestamp() * 1000)
    start_after_ms = two_yr_ms
    start_after_id = ""
    MAX_PAGES = 50
    for page in range(1, MAX_PAGES + 1):
        params = {
            "location_id": LOCATION_ID,
            "startAfter": start_after_ms,
            "startAfterId": start_after_id,
            "limit": 100,
        }
        r = requests.get(f"{GHL_BASE}/opportunities/search", params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"  All-opps error {r.status_code}: {r.text[:200]}", flush=True)
            break
        batch = r.json().get("opportunities", [])
        if not batch:
            break
        for o in batch:
            status = (o.get("status") or "").lower()
            if status not in ("won", "lost"):
                opps.append(o)
        print(f"  All-opps page {page}: {len(batch)} fetched, {len(opps)} open so far", flush=True)
        if len(batch) < 100:
            break
        last = batch[-1]
        cat = last.get("createdAt", "")
        if cat:
            try:
                start_after_ms = int(datetime.fromisoformat(cat.replace("Z", "+00:00")).timestamp() * 1000)
            except Exception:
                break
        start_after_id = last.get("id", "")
    return opps


def get_pipelines():
    r = requests.get(
        f"{GHL_BASE}/opportunities/pipelines",
        params={"locationId": LOCATION_ID},
        headers=headers,
        timeout=30,
    )
    if r.status_code == 200:
        return r.json().get("pipelines", [])
    print(f"Pipelines error {r.status_code}", flush=True)
    return []


# --- Fetch ---

print("Fetching this week contacts...", flush=True)
week_contacts = get_contacts(week_start_utc, week_end_utc, "this-wk")

print("Fetching prior week contacts...", flush=True)
prior_contacts = get_contacts(prior_start_utc, prior_end_utc, "prior-wk")

print("Fetching this week opportunities...", flush=True)
week_opps = get_opportunities_in_window(week_start_utc, week_end_utc, "this-wk")

print("Fetching prior week opportunities...", flush=True)
prior_opps = get_opportunities_in_window(prior_start_utc, prior_end_utc, "prior-wk")

print("Fetching all open opportunities...", flush=True)
all_open_opps = get_all_open_opportunities()

print("Fetching pipelines...", flush=True)
pipelines = get_pipelines()

print(f"Summary: contacts={len(week_contacts)}, opps={len(week_opps)}, all-open={len(all_open_opps)}", flush=True)

# --- Stage map ---

stage_map = {}
for pipe in pipelines:
    pname = pipe.get("name", "Unknown Pipeline")
    for stage in pipe.get("stages", []):
        stage_map[stage.get("id", "")] = {
            "name": stage.get("name", "Unknown Stage"),
            "pipeline": pname,
        }

# --- Source bucketing ---

SOURCE_ALIASES = {
    "google": "Google Ads",
    "adwords": "Google Ads",
    "facebook": "Facebook / Meta",
    "instagram": "Facebook / Meta",
    "meta": "Facebook / Meta",
    "zillow": "Zillow",
    "referral": "Referral",
    "past client": "Referral",
    "sphere": "Referral",
    "seo": "Organic / SEO",
    "organic": "Organic / SEO",
    "youtube": "YouTube",
    "email": "Email / Newsletter",
    "newsletter": "Email / Newsletter",
    "sign call": "Sign Call",
    "direct mail": "Direct Mail",
    "cold call": "Cold Outreach",
    "linkedin": "LinkedIn",
}

def bucket_source(c):
    src = (c.get("source") or c.get("leadSource") or "").strip().lower()
    if not src:
        for tag in [t.lower() for t in (c.get("tags") or [])]:
            for k, v in SOURCE_ALIASES.items():
                if k in tag:
                    return v
        return "Unknown"
    for k, v in SOURCE_ALIASES.items():
        if k in src:
            return v
    return src.title() if src else "Unknown"

week_by_source = defaultdict(int)
for c in week_contacts:
    week_by_source[bucket_source(c)] += 1

prior_by_source = defaultdict(int)
for c in prior_contacts:
    prior_by_source[bucket_source(c)] += 1

# --- Opp stats ---

def is_win(o):
    return (o.get("status") or "").lower() == "won"

week_wins = [o for o in week_opps if is_win(o)]
prior_wins = [o for o in prior_opps if is_win(o)]
prior_opps_count = len(prior_opps)
open_pipeline_value = sum(float(o.get("monetaryValue") or 0) for o in all_open_opps)

# --- Pipeline health + stale deals ---

now_utc = datetime.now(timezone.utc)
STALE_DAYS = 14

stage_buckets = defaultdict(list)
stale_deals = []

for o in all_open_opps:
    sid = o.get("pipelineStageId", "")
    sinfo = stage_map.get(sid, {"name": "Unknown Stage", "pipeline": "Unknown"})
    stage_buckets[sinfo["name"]].append(o)
    last_changed = (
        o.get("lastStatusChangeAt") or o.get("updatedAt") or o.get("createdAt") or ""
    )
    if last_changed:
        try:
            ldt = datetime.fromisoformat(last_changed.replace("Z", "+00:00"))
            days_idle = (now_utc - ldt).days
            if days_idle >= STALE_DAYS:
                stale_deals.append({
                    "id": o.get("id", ""),
                    "name": o.get("name") or o.get("contactName") or "Unnamed Deal",
                    "stage": sinfo["name"],
                    "value": float(o.get("monetaryValue") or 0),
                    "days_idle": days_idle,
                })
        except Exception:
            pass

stale_deals.sort(key=lambda x: x["days_idle"], reverse=True)

# --- Orphaned contacts ---

opp_contact_ids = set()
for o in all_open_opps + week_opps:
    cid = o.get("contactId") or ""
    if cid:
        opp_contact_ids.add(cid)
orphaned_contacts = [c for c in week_contacts if c.get("id") not in opp_contact_ids]

# --- Declining sources ---

declining_sources = []
for src, prior_count in prior_by_source.items():
    this_count = week_by_source.get(src, 0)
    if prior_count >= 2 and this_count < prior_count * 0.5:
        declining_sources.append({
            "source": src,
            "this_week": this_count,
            "prior_week": prior_count,
            "drop_pct": int((prior_count - this_count) / prior_count * 100),
        })
declining_sources.sort(key=lambda x: x["drop_pct"], reverse=True)

# --- Health score ---

total_leads = len(week_contacts)
total_prior = len(prior_contacts)
total_opps = len(week_opps)
total_wins = len(week_wins)

score = 50
if total_leads > 0:
    score += 10
if total_prior > 0 and total_leads >= total_prior:
    score += 5
if total_leads > 0:
    conv = total_opps / total_leads
    score += 10 if conv >= 0.20 else (5 if conv >= 0.10 else 0)
if total_wins > 0:
    score += 10
if open_pipeline_value >= 500000:
    score += 5
score -= min(len(stale_deals) * 3, 20)
score -= min(len(orphaned_contacts) * 2, 10)
score -= min(len(declining_sources) * 3, 10)
score = max(0, min(100, score))

if score >= 80:
    grade, grade_color, score_label = "A", "#22c55e", "Strong Week"
elif score >= 65:
    grade, grade_color, score_label = "B", "#84cc16", "On Track"
elif score >= 50:
    grade, grade_color, score_label = "C", "#f4b955", "Watch Closely"
elif score >= 35:
    grade, grade_color, score_label = "D", "#f97316", "Needs Attention"
else:
    grade, grade_color, score_label = "F", "#ef4444", "Critical"

print(f"Health score: {score} ({grade}) - {score_label}", flush=True)

# --- Attention callouts ---

attention_items = []
if total_leads == 0:
    attention_items.append({
        "icon": "&#128680;",
        "title": "No new leads this week",
        "detail": "Check lead sources, ad spend, and GHL integrations",
        "color": "#ef4444",
    })
if orphaned_contacts:
    n = len(orphaned_contacts)
    attention_items.append({
        "icon": "&#128100;",
        "title": f"{n} new lead{'s' if n > 1 else ''} with no opportunity record",
        "detail": "These contacts entered this week but have no open deal - follow up today",
        "color": "#ef4444",
    })
if stale_deals:
    worst = stale_deals[0]
    n = len(stale_deals)
    attention_items.append({
        "icon": "&#9200;",
        "title": f"{n} deal{'s' if n > 1 else ''} untouched for {STALE_DAYS}+ days",
        "detail": f"Oldest: {worst['name']} - {worst['days_idle']}d in \"{worst['stage']}\"",
        "color": "#f97316",
    })
if declining_sources:
    s = declining_sources[0]
    attention_items.append({
        "icon": "&#128200;",
        "title": f"{s['source']} down {s['drop_pct']}% vs prior week",
        "detail": f"{s['prior_week']} leads last week vs {s['this_week']} this week",
        "color": "#f4b955",
    })

# --- HTML helpers ---

def delta_badge(val, prior):
    diff = val - prior
    if diff > 0:
        return f'<span style="color:#22c55e;font-size:11px">&#9650; +{diff}</span>'
    elif diff < 0:
        return f'<span style="color:#ef4444;font-size:11px">&#9660; {diff}</span>'
    return '<span style="color:#334155;font-size:11px">&#8212;</span>'

def funnel_row(label, count, of_total, color):
    pct = (count / of_total * 100) if of_total > 0 else 0
    bar_w = max(pct, 1)
    return (
        '<div style="margin-bottom:14px">'
        '<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px">'
        f'<span style="color:#e2e8f0;font-weight:500">{label}</span>'
        f'<span style="color:#64748b">{count} &nbsp;<span style="color:{color}">{pct:.0f}%</span></span>'
        '</div>'
        '<div style="background:#162032;border-radius:4px;height:10px">'
        f'<div style="background:{color};width:{bar_w:.1f}%;height:10px;border-radius:4px"></div>'
        '</div></div>'
    )

# --- Build HTML sections ---

# Attention
if attention_items:
    attention_html = ""
    for i, item in enumerate(attention_items):
        border = "border-bottom:1px solid #1a2540;" if i < len(attention_items) - 1 else ""
        attention_html += (
            f'<div style="display:flex;gap:12px;align-items:flex-start;padding:12px 0;{border}">'
            f'<div style="font-size:20px;flex-shrink:0;margin-top:1px">{item["icon"]}</div>'
            '<div>'
            f'<div style="font-weight:600;color:{item["color"]};font-size:14px">{item["title"]}</div>'
            f'<div style="color:#64748b;font-size:13px;margin-top:3px">{item["detail"]}</div>'
            '</div></div>'
        )
else:
    attention_html = '<p style="color:#22c55e;text-align:center;padding:16px 0;font-size:14px">&#10003; All clear - no immediate action needed</p>'

# Pipeline by stage
stale_ids = {d["id"] for d in stale_deals}
pipeline_rows = ""
for stage_name, deals in sorted(stage_buckets.items(), key=lambda x: -len(x[1])):
    total_val = sum(float(d.get("monetaryValue") or 0) for d in deals)
    val_str = f"${total_val:,.0f}" if total_val else "&mdash;"
    n_stale = sum(1 for d in deals if d.get("id") in stale_ids)
    stale_badge = (
        f' <span style="background:#f9731618;color:#f97316;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:600">{n_stale} stale</span>'
        if n_stale else ""
    )
    pipeline_rows += (
        f'<tr><td style="padding:10px 12px;color:#e2e8f0">{stage_name}{stale_badge}</td>'
        f'<td style="padding:10px 12px;text-align:center;color:#f4b955;font-weight:700">{len(deals)}</td>'
        f'<td style="padding:10px 12px;text-align:right;color:#64748b;font-size:13px">{val_str}</td></tr>'
    )
if not pipeline_rows:
    pipeline_rows = '<tr><td colspan="3" style="padding:20px;color:#475569;text-align:center">No open deals found</td></tr>'

# Stale deals table
stale_rows = ""
for d in stale_deals[:12]:
    val_str = f"${d['value']:,.0f}" if d['value'] else "&mdash;"
    idle_color = "#ef4444" if d["days_idle"] >= 30 else "#f97316"
    stale_rows += (
        f'<tr>'
        f'<td style="padding:10px 12px;color:#e2e8f0;font-weight:500">{d["name"]}</td>'
        f'<td style="padding:10px 12px;color:#64748b;font-size:13px">{d["stage"]}</td>'
        f'<td style="padding:10px 12px;text-align:center;color:{idle_color};font-weight:700">{d["days_idle"]}d</td>'
        f'<td style="padding:10px 12px;text-align:right;color:#64748b;font-size:13px">{val_str}</td>'
        f'</tr>'
    )
if not stale_rows:
    stale_rows = '<tr><td colspan="4" style="padding:20px;color:#22c55e;text-align:center">&#10003; No stale deals - nice work</td></tr>'

# Source attribution rows
source_rows = ""
for src in sorted(week_by_source, key=lambda s: -week_by_source[s]):
    count = week_by_source[src]
    prior_count = prior_by_source.get(src, 0)
    diff = count - prior_count
    if diff > 0:
        wow = f'<span style="color:#22c55e;font-weight:600">+{diff}</span>'
    elif diff < 0:
        wow = f'<span style="color:#ef4444">{diff}</span>'
    else:
        wow = '<span style="color:#334155">&mdash;</span>'
    source_rows += (
        f'<tr>'
        f'<td style="padding:10px 12px;color:#e2e8f0;font-weight:500">{src}</td>'
        f'<td style="padding:10px 12px;text-align:center;color:#f4b955;font-weight:700">{count}</td>'
        f'<td style="padding:10px 12px;text-align:center">{wow}</td>'
        f'</tr>'
    )
if not source_rows:
    source_rows = '<tr><td colspan="3" style="padding:20px;color:#475569;text-align:center">No leads this week</td></tr>'

# Funnel
funnel_total = max(total_leads, 1)
funnel_html = (
    funnel_row("New Leads", total_leads, funnel_total, "#6366f1")
    + funnel_row("Opportunities Created", total_opps, funnel_total, "#f4b955")
    + funnel_row("Closed Won", total_wins, funnel_total, "#22c55e")
)
conv_str = f"{total_opps/total_leads*100:.0f}%" if total_leads > 0 else "&mdash;"
win_str = f"{total_wins/total_leads*100:.0f}%" if total_leads > 0 else "&mdash;"

# Open pipeline display
open_val_display = f"${open_pipeline_value/1000:.0f}K" if open_pipeline_value >= 1000 else f"${open_pipeline_value:,.0f}"

# --- Render HTML ---

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CRM Health &middot; Week of """ + week_label + """</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#060d1a;color:#e2e8f0;font-family:'DM Sans',sans-serif;padding:16px;-webkit-font-smoothing:antialiased}
.wrap{max-width:800px;margin:0 auto}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:10px 0 18px;font-size:12px;color:#334155;letter-spacing:.03em}
.header{text-align:center;padding:20px 0 16px}
.header h1{font-size:22px;font-weight:700;color:#f4b955;letter-spacing:-.02em}
.header .sub{font-size:13px;color:#475569;margin-top:6px}
.score-card{background:linear-gradient(135deg,#0f1729 0%,#111e35 100%);border:1px solid #1e293b;border-radius:14px;padding:32px 24px;text-align:center;margin-bottom:14px;position:relative;overflow:hidden}
.score-num{font-size:80px;font-weight:700;line-height:1;letter-spacing:-.04em;color:""" + grade_color + """}
.score-grade{display:inline-block;font-size:14px;font-weight:700;padding:4px 14px;border-radius:20px;margin-top:8px;color:""" + grade_color + """;background:""" + grade_color + """18}
.score-label{font-size:14px;color:#64748b;margin-top:10px}
.bar{position:absolute;top:0;left:0;right:0;height:3px;background:""" + grade_color + """}
.kpi-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:14px}
@media(min-width:520px){.kpi-grid{grid-template-columns:repeat(4,1fr)}}
.kpi{background:#0f1729;border:1px solid #1a2540;border-radius:10px;padding:16px 12px;text-align:center}
.kpi .num{font-size:26px;font-weight:700;color:#f4b955;letter-spacing:-.03em}
.kpi .lbl{font-size:11px;color:#475569;margin-top:5px;text-transform:uppercase;letter-spacing:.05em}
.kpi .wow{margin-top:5px;min-height:16px}
.section{background:#0f1729;border:1px solid #1a2540;border-radius:10px;padding:20px;margin-bottom:14px}
.section h2{font-size:12px;font-weight:700;color:#f4b955;margin-bottom:14px;text-transform:uppercase;letter-spacing:.08em}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:9px 12px;background:#0a1322;color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:.05em;font-weight:600}
tr:not(:last-child) td{border-bottom:1px solid #0e1a2e}
.footer{text-align:center;padding:28px 0 12px;color:#334155;font-size:12px;line-height:1.8}
</style>
</head>
<body>
<div class="wrap">

  <div class="topbar">
    <span>GRAEHAM WATTS &middot; INTERO REAL ESTATE</span>
    <span>Generated """ + now_pt.strftime('%b %-d %Y %H:%M PT') + """</span>
  </div>

  <div class="header">
    <h1>Weekly CRM Health</h1>
    <div class="sub">Week of """ + week_label + """ &nbsp;&middot;&nbsp; Prior: week of """ + prior_label + """</div>
  </div>

  <div class="score-card">
    <div class="bar"></div>
    <div class="score-num">""" + str(score) + """</div>
    <div class="score-grade">Grade """ + grade + """</div>
    <div class="score-label">""" + score_label + """</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi">
      <div class="num">""" + str(total_leads) + """</div>
      <div class="lbl">New Leads</div>
      <div class="wow">""" + delta_badge(total_leads, total_prior) + """</div>
    </div>
    <div class="kpi">
      <div class="num">""" + str(total_opps) + """</div>
      <div class="lbl">New Opps</div>
      <div class="wow">""" + delta_badge(total_opps, prior_opps_count) + """</div>
    </div>
    <div class="kpi">
      <div class="num">""" + str(total_wins) + """</div>
      <div class="lbl">Wins</div>
      <div class="wow">""" + delta_badge(total_wins, len(prior_wins)) + """</div>
    </div>
    <div class="kpi">
      <div class="num">""" + open_val_display + """</div>
      <div class="lbl">Open Pipeline</div>
      <div class="wow"><span style="color:#334155;font-size:11px">""" + str(len(all_open_opps)) + """ deals</span></div>
    </div>
  </div>

  <div class="section">
    <h2>&#9889; Attention Needed</h2>
    """ + attention_html + """
  </div>

  <div class="section">
    <h2>&#128293; Open Pipeline by Stage</h2>
    <table>
      <thead><tr>
        <th>Stage</th>
        <th style="text-align:center">Deals</th>
        <th style="text-align:right">Value</th>
      </tr></thead>
      <tbody>""" + pipeline_rows + """</tbody>
    </table>
  </div>

  <div class="section">
    <h2>&#9200; Stale Deals (""" + str(STALE_DAYS) + """+ Days Untouched)</h2>
    <table>
      <thead><tr>
        <th>Deal / Contact</th>
        <th>Stage</th>
        <th style="text-align:center">Idle</th>
        <th style="text-align:right">Value</th>
      </tr></thead>
      <tbody>""" + stale_rows + """</tbody>
    </table>
  </div>

  <div class="section">
    <h2>&#128202; Lead Attribution This Week</h2>
    <table>
      <thead><tr>
        <th>Source</th>
        <th style="text-align:center">Leads</th>
        <th style="text-align:center">vs Prior Wk</th>
      </tr></thead>
      <tbody>""" + source_rows + """</tbody>
    </table>
  </div>

  <div class="section">
    <h2>&#127919; Conversion Funnel</h2>
    """ + funnel_html + """
    <div style="display:flex;gap:20px;margin-top:16px;padding-top:14px;border-top:1px solid #0e1a2e;flex-wrap:wrap">
      <div style="font-size:13px;color:#64748b">Lead&rarr;Opp: <strong style="color:#f4b955">""" + conv_str + """</strong></div>
      <div style="font-size:13px;color:#64748b">Lead&rarr;Win: <strong style="color:#22c55e">""" + win_str + """</strong></div>
      <div style="font-size:13px;color:#64748b">Prior week leads: <strong style="color:#94a3b8">""" + str(total_prior) + """</strong></div>
    </div>
  </div>

  <div class="footer">
    Graeham Watts &nbsp;&middot;&nbsp; Intero Real Estate &nbsp;&middot;&nbsp; graehamwatts@gmail.com<br>
    CRM Health Dashboard &nbsp;&middot;&nbsp; """ + now_pt.strftime('%Y-%m-%d %H:%M PT') + """
  </div>

</div>
</body>
</html>"""

# --- Write output ---

output_path = f"dashboards/health/{date_slug}-health.html"
os.makedirs("dashboards/health", exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Wrote {output_path} ({len(html):,} chars)", flush=True)

if GITHUB_OUTPUT:
    with open(GITHUB_OUTPUT, "a") as go:
        go.write(f"output_path={output_path}\n")
        go.write(f"date_slug={date_slug}\n")
        go.write(f"health_score={score}\n")
        go.write(f"grade={grade}\n")
        go.write(f"total_leads={total_leads}\n")
        go.write(f"stale_count={len(stale_deals)}\n")
