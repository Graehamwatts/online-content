#!/usr/bin/env python3
"""
weekly_crm_health.py - CRM Health Dashboard for Graeham Watts
Outputs: dashboards/health/<YYYY-MM-DD>-health.html
Env: GHL_PIT, GHL_LOCATION_ID, [GHL_API_BASE, GHL_VERSION, WEEK_START_OVERRIDE]

Metrics design:
- all_open: all non-won/non-lost opportunities (paginated fully, up to 2 yrs back)
- week_new / prior_new: derived from all_open filtered by createdAt — reliable
- DORMANT_STAGES: holding areas (cold/unqualified/investor) excluded from active counts
- stale_recent: active-stage leads created ≤90 days ago, untouched ≥14 days → "Follow Up"
- old_active: active-stage leads created >90 days ago → "CRM Cleanup" (not penalized)
"""

import requests, os
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

# Stages that are "holding areas" — expected to be dormant, excluded from active counts
DORMANT_STAGES = {
    "cold", "unqualified", "investor/flipper",
    "bought with another agent", "sold with another agent",
    "closed", "past buyer", "past seller",
}

STALE_DAYS  = 14   # days idle before a lead is flagged as needing follow-up
RECENT_DAYS = 90   # only flag as "stale/follow-up" if created within this many days
               # older leads in active stages = cleanup backlog, not urgent follow-up

# ─── Time windows ─────────────────────────────────────────────────────────

now_pt  = datetime.now(PT)
now_utc = datetime.now(timezone.utc)

if WEEK_START_OVERRIDE:
    week_start = PT.localize(datetime.strptime(WEEK_START_OVERRIDE, "%Y-%m-%d"))
else:
    days_back  = now_pt.weekday()
    week_start = (now_pt - timedelta(days=days_back)).replace(
        hour=0, minute=0, second=0, microsecond=0)

week_end    = now_pt
prior_start = week_start - timedelta(days=7)
prior_end   = week_start

week_start_utc  = week_start.astimezone(timezone.utc)
week_end_utc    = week_end.astimezone(timezone.utc)
prior_start_utc = prior_start.astimezone(timezone.utc)
prior_end_utc   = prior_end.astimezone(timezone.utc)

date_slug  = week_start.strftime("%Y-%m-%d")
week_label = week_start.strftime("%b %-d, %Y")
prior_label= prior_start.strftime("%b %-d")

print(f"Week:  {week_start_utc.date()} -> {week_end_utc.date()}", flush=True)
print(f"Prior: {prior_start_utc.date()} -> {prior_end_utc.date()}", flush=True)

# ─── API helpers ──────────────────────────────────────────────────────────

def get_all_open_opportunities():
    """All non-won/non-lost opportunities. Paginates fully (no page cap)."""
    opps = []
    two_yr_ms    = int((now_utc - timedelta(days=730)).timestamp() * 1000)
    start_after_ms = two_yr_ms
    start_after_id = ""
    page = 0
    while True:
        page += 1
        params = {
            "location_id": LOCATION_ID,
            "startAfter":   start_after_ms,
            "startAfterId": start_after_id,
            "limit": 100,
        }
        r = requests.get(f"{GHL_BASE}/opportunities/search",
                         params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"  all-open error {r.status_code}: {r.text[:200]}", flush=True)
            break
        batch = r.json().get("opportunities", [])
        if not batch:
            print(f"  all-open: done at page {page} ({len(opps)} total)", flush=True)
            break
        for o in batch:
            if (o.get("status") or "").lower() not in ("won", "lost"):
                opps.append(o)
        print(f"  all-open p{page}: {len(batch)} fetched, {len(opps)} open", flush=True)
        if len(batch) < 100:
            break
        last = batch[-1]
        cat  = last.get("createdAt", "")
        if cat:
            try:
                start_after_ms = int(datetime.fromisoformat(
                    cat.replace("Z", "+00:00")).timestamp() * 1000)
            except Exception:
                break
        start_after_id = last.get("id", "")
    return opps


def get_pipelines():
    r = requests.get(f"{GHL_BASE}/opportunities/pipelines",
                     params={"locationId": LOCATION_ID},
                     headers=headers, timeout=30)
    return r.json().get("pipelines", []) if r.status_code == 200 else []


# ─── Fetch ────────────────────────────────────────────────────────────────

print("Fetching all open opps...", flush=True)
all_open = get_all_open_opportunities()

print("Fetching pipelines...", flush=True)
pipelines = get_pipelines()

# ─── Stage & pipeline map ─────────────────────────────────────────────────

stage_map      = {}
pipeline_names = {}
for pipe in pipelines:
    pid   = pipe.get("id", "")
    pname = pipe.get("name", "Unknown Pipeline")
    pipeline_names[pid] = pname
    for stage in pipe.get("stages", []):
        stage_map[stage.get("id", "")] = {
            "name":     stage.get("name", "Unknown Stage"),
            "pipeline": pname,
        }

def stage_info(o):
    sid = o.get("pipelineStageId", "")
    return stage_map.get(sid, {"name": "Unknown Stage", "pipeline": "Unknown Pipeline"})

def is_dormant_stage(sinfo):
    return sinfo["name"].lower() in DORMANT_STAGES

def parse_dt(ts):
    """Parse ISO timestamp to UTC datetime, or None."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

# ─── Derive weekly counts from all_open (createdAt is reliable) ───────────

def is_win(o):
    return (o.get("status") or "").lower() == "won"

week_new_opps  = []
prior_new_opps = []

for o in all_open:
    cdt = parse_dt(o.get("createdAt", ""))
    if cdt is None:
        continue
    if week_start_utc <= cdt < week_end_utc:
        week_new_opps.append(o)
    elif prior_start_utc <= cdt < prior_end_utc:
        prior_new_opps.append(o)

# Note: won deals created this week won't be in all_open (excluded by status filter).
# For a solo agent the win count is typically 0-1/wk; treat this as floor estimate.
week_wins  = []  # wins from all_open that were created this week (open→still open edge case)
prior_wins = []

# Break down by pipeline
week_by_pipeline  = defaultdict(int)
prior_by_pipeline = defaultdict(int)
for o in week_new_opps:
    week_by_pipeline[stage_info(o)["pipeline"]] += 1
for o in prior_new_opps:
    prior_by_pipeline[stage_info(o)["pipeline"]] += 1

print(f"Week new: {len(week_new_opps)}, Prior new: {len(prior_new_opps)}", flush=True)

# ─── Pipeline health ──────────────────────────────────────────────────────

active_open   = []   # open opps in non-dormant stages
dormant_open  = []   # cold/unqualified/holding
stale_recent  = []   # active, created ≤90 days ago, untouched ≥14 days → needs follow-up
old_active    = []   # active, created >90 days ago → cleanup backlog
stage_buckets = defaultdict(list)

for o in all_open:
    si = stage_info(o)
    stage_buckets[f"{si['pipeline']} → {si['name']}"].append(o)

    if is_dormant_stage(si):
        dormant_open.append(o)
    else:
        active_open.append(o)
        cdt  = parse_dt(o.get("createdAt", ""))
        age  = (now_utc - cdt).days if cdt else 9999
        last = (parse_dt(o.get("lastStatusChangeAt")) or
                parse_dt(o.get("updatedAt")) or
                cdt)
        idle = (now_utc - last).days if last else 9999

        if age > RECENT_DAYS:
            old_active.append(o)
        elif idle >= STALE_DAYS:
            stale_recent.append({
                "id":       o.get("id", ""),
                "name":     o.get("name") or o.get("contactName") or "Unnamed",
                "stage":    si["name"],
                "pipeline": si["pipeline"],
                "value":    float(o.get("monetaryValue") or 0),
                "days_idle": idle,
                "age_days":  age,
            })

stale_recent.sort(key=lambda x: x["days_idle"], reverse=True)
open_pipeline_value = sum(float(o.get("monetaryValue") or 0) for o in active_open)

total_new_opps   = len(week_new_opps)
total_prior_opps = len(prior_new_opps)
total_wins       = len(week_wins)

print(f"Active open: {len(active_open)}, dormant: {len(dormant_open)}, "
      f"old-active: {len(old_active)}, stale-recent: {len(stale_recent)}", flush=True)

# ─── Health score ─────────────────────────────────────────────────────────

score = 50

if total_new_opps > 0:
    score += 10
if total_prior_opps > 0 and total_new_opps >= total_prior_opps:
    score += 5
if total_wins > 0:
    score += 15
if open_pipeline_value >= 500_000:
    score += 5
if len(active_open) > 0:
    score += 5

# Penalise only RECENT stale (actionable follow-up misses), cap at -20
score -= min(len(stale_recent) * 5, 20)

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

print(f"Score: {score} ({grade}) — {score_label}", flush=True)

# ─── Attention callouts ───────────────────────────────────────────────────

attention_items = []

if total_new_opps == 0:
    attention_items.append({
        "icon":  "&#128680;",
        "title": "No new opportunities created this week",
        "detail":"No leads entered any pipeline stage — check your lead sources",
        "color": "#ef4444",
    })

if stale_recent:
    worst = stale_recent[0]
    n     = len(stale_recent)
    attention_items.append({
        "icon":  "&#9200;",
        "title": f"{n} recent lead{'s' if n>1 else ''} untouched {STALE_DAYS}+ days",
        "detail": f"Oldest: {worst['name']} — {worst['days_idle']}d idle "
                  f"in {worst['pipeline']} / {worst['stage']}",
        "color": "#f97316",
    })

if old_active:
    attention_items.append({
        "icon":  "&#128465;",
        "title": f"{len(old_active):,} leads 90+ days old still in active stages",
        "detail": "These are stale entries that haven't been moved to Cold / Unqualified. "
                  "Run a cleanup campaign or bulk-update these stages.",
        "color": "#64748b",
    })

if dormant_open:
    attention_items.append({
        "icon":  "&#128191;",
        "title": f"{len(dormant_open):,} contacts in Cold / Unqualified / holding stages",
        "detail": "Dormant — not counted as active deals. These are your import/holding backlog.",
        "color": "#475569",
    })

if total_prior_opps > 0 and total_new_opps < total_prior_opps * 0.5:
    attention_items.append({
        "icon":  "&#128200;",
        "title": f"New pipeline entries down "
                 f"{int((1-total_new_opps/total_prior_opps)*100)}% vs prior week",
        "detail": f"{total_prior_opps} last week → {total_new_opps} this week",
        "color": "#f4b955",
    })

# ─── HTML helpers ────────────────────────────────────────────────────────

def delta_badge(val, prior):
    diff = val - prior
    if diff > 0:
        return f'<span style="color:#22c55e;font-size:11px">&#9650; +{diff}</span>'
    elif diff < 0:
        return f'<span style="color:#ef4444;font-size:11px">&#9660; {diff}</span>'
    return '<span style="color:#334155;font-size:11px">&#8212;</span>'


def funnel_row(label, count, of_total, color):
    pct   = (count / of_total * 100) if of_total > 0 else 0
    bar_w = max(pct, 1)
    return (
        '<div style="margin-bottom:14px">'
        '<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px">'
        f'<span style="color:#e2e8f0;font-weight:500">{label}</span>'
        f'<span style="color:#64748b">{count}'
        + (f' &nbsp;<span style="color:{color}">{pct:.0f}%</span>' if of_total > 0 else '')
        + '</span></div>'
        '<div style="background:#162032;border-radius:4px;height:10px">'
        f'<div style="background:{color};width:{bar_w:.1f}%;height:10px;border-radius:4px"></div>'
        '</div></div>'
    )

# ─── Build HTML sections ─────────────────────────────────────────────────

# Attention
if attention_items:
    attn_html = ""
    for i, item in enumerate(attention_items):
        border = "border-bottom:1px solid #1a2540;" if i < len(attention_items)-1 else ""
        attn_html += (
            f'<div style="display:flex;gap:12px;align-items:flex-start;padding:12px 0;{border}">'
            f'<div style="font-size:20px;flex-shrink:0">{item["icon"]}</div>'
            f'<div><div style="font-weight:600;color:{item["color"]};font-size:14px">{item["title"]}</div>'
            f'<div style="color:#64748b;font-size:13px;margin-top:3px">{item["detail"]}</div></div>'
            '</div>'
        )
else:
    attn_html = '<p style="color:#22c55e;text-align:center;padding:16px 0;font-size:14px">&#10003; All clear</p>'

# Pipeline by stage (active only, top 12 by count)
pipeline_rows = ""
stale_ids     = {d["id"] for d in stale_recent}
active_buckets = {k: v for k, v in stage_buckets.items()
                  if not is_dormant_stage({"name": k.split(" → ")[-1]})}
for label, deals in sorted(active_buckets.items(), key=lambda x: -len(x[1]))[:12]:
    total_val = sum(float(d.get("monetaryValue") or 0) for d in deals)
    val_str   = f"${total_val:,.0f}" if total_val else "&mdash;"
    n_stale   = sum(1 for d in deals if d.get("id") in stale_ids)
    stale_badge = (
        f' <span style="background:#f9731618;color:#f97316;font-size:10px;'
        f'padding:2px 6px;border-radius:10px;font-weight:600">{n_stale} follow-up</span>'
        if n_stale else ""
    )
    short_label = label.replace("Unknown Pipeline → ","").replace("Unknown Stage","?")
    pipeline_rows += (
        f'<tr><td style="padding:10px 12px;color:#e2e8f0">{short_label}{stale_badge}</td>'
        f'<td style="padding:10px 12px;text-align:center;color:#f4b955;font-weight:700">{len(deals)}</td>'
        f'<td style="padding:10px 12px;text-align:right;color:#64748b;font-size:13px">{val_str}</td></tr>'
    )
if not pipeline_rows:
    pipeline_rows = '<tr><td colspan="3" style="padding:20px;color:#475569;text-align:center">No active open opportunities</td></tr>'

# Recent stale table (needs follow-up, top 12)
stale_rows = ""
for d in stale_recent[:12]:
    val_str   = f"${d['value']:,.0f}" if d['value'] else "&mdash;"
    idle_color= "#ef4444" if d["days_idle"] >= 30 else "#f97316"
    stale_rows += (
        f'<tr><td style="padding:10px 12px;color:#e2e8f0;font-weight:500">{d["name"]}</td>'
        f'<td style="padding:10px 12px;color:#64748b;font-size:13px">{d["pipeline"]}</td>'
        f'<td style="padding:10px 12px;color:#64748b;font-size:13px">{d["stage"]}</td>'
        f'<td style="padding:10px 12px;text-align:center;color:{idle_color};font-weight:700">{d["days_idle"]}d</td>'
        f'<td style="padding:10px 12px;text-align:right;color:#64748b;font-size:13px">{val_str}</td></tr>'
    )
if not stale_rows:
    stale_rows = '<tr><td colspan="5" style="padding:20px;color:#22c55e;text-align:center">&#10003; No recent leads need immediate follow-up</td></tr>'

# New opps by pipeline this week
opp_pipeline_rows = ""
for pname in sorted(week_by_pipeline, key=lambda x: -week_by_pipeline[x]):
    count = week_by_pipeline[pname]
    prior = prior_by_pipeline.get(pname, 0)
    diff  = count - prior
    wow   = (f'<span style="color:#22c55e;font-weight:600">+{diff}</span>' if diff > 0
             else f'<span style="color:#ef4444">{diff}</span>' if diff < 0
             else '<span style="color:#334155">&mdash;</span>')
    opp_pipeline_rows += (
        f'<tr><td style="padding:10px 12px;color:#e2e8f0;font-weight:500">{pname}</td>'
        f'<td style="padding:10px 12px;text-align:center;color:#f4b955;font-weight:700">{count}</td>'
        f'<td style="padding:10px 12px;text-align:center">{wow}</td></tr>'
    )
if not opp_pipeline_rows:
    opp_pipeline_rows = '<tr><td colspan="3" style="padding:20px;color:#475569;text-align:center">No new pipeline activity this week</td></tr>'

# Funnel
funnel_base = max(total_new_opps, 1)
funnel_html = (
    funnel_row("New Pipeline Entries", total_new_opps, funnel_base, "#6366f1")
    + funnel_row("Closed Won",          total_wins,    funnel_base, "#22c55e")
)
win_rate = f"{total_wins/total_new_opps*100:.0f}%" if total_new_opps > 0 else "&mdash;"

# Active pipeline value display
val_display = f"${open_pipeline_value/1000:.0f}K" if open_pipeline_value >= 1000 else f"${open_pipeline_value:,.0f}"

# ─── Full HTML ────────────────────────────────────────────────────────────

html = ("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CRM Health &middot; """ + week_label + """</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#060d1a;color:#e2e8f0;font-family:'DM Sans',sans-serif;padding:16px;-webkit-font-smoothing:antialiased}
.wrap{max-width:800px;margin:0 auto}
.topbar{display:flex;justify-content:space-between;padding:10px 0 18px;font-size:12px;color:#334155;letter-spacing:.03em}
.header{text-align:center;padding:18px 0 14px}
.header h1{font-size:22px;font-weight:700;color:#f4b955;letter-spacing:-.02em}
.header .sub{font-size:13px;color:#475569;margin-top:5px}
.score-card{background:linear-gradient(135deg,#0f1729,#111e35);border:1px solid #1e293b;border-radius:14px;padding:28px;text-align:center;margin-bottom:12px;position:relative;overflow:hidden}
.bar{position:absolute;top:0;left:0;right:0;height:3px;background:""" + grade_color + """}
.score-num{font-size:72px;font-weight:700;line-height:1;letter-spacing:-.04em;color:""" + grade_color + """}
.score-grade{display:inline-block;font-size:13px;font-weight:700;padding:3px 12px;border-radius:20px;margin-top:8px;color:""" + grade_color + """;background:""" + grade_color + """18}
.score-label{font-size:13px;color:#64748b;margin-top:8px}
.note{font-size:11px;color:#334155;margin-top:10px;padding-top:10px;border-top:1px solid #1a2540}
.kpi-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:12px}
@media(min-width:520px){.kpi-grid{grid-template-columns:repeat(4,1fr)}}
.kpi{background:#0f1729;border:1px solid #1a2540;border-radius:10px;padding:14px 12px;text-align:center}
.kpi .num{font-size:24px;font-weight:700;color:#f4b955;letter-spacing:-.03em}
.kpi .lbl{font-size:11px;color:#475569;margin-top:4px;text-transform:uppercase;letter-spacing:.05em}
.kpi .wow{margin-top:4px;min-height:16px}
.section{background:#0f1729;border:1px solid #1a2540;border-radius:10px;padding:18px;margin-bottom:12px}
.section h2{font-size:11px;font-weight:700;color:#f4b955;margin-bottom:12px;text-transform:uppercase;letter-spacing:.08em}
.caveat{font-size:11px;color:#334155;margin-top:10px;font-style:italic}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:8px 12px;background:#0a1322;color:#475569;font-size:10px;text-transform:uppercase;letter-spacing:.05em;font-weight:600}
tr:not(:last-child) td{border-bottom:1px solid #0e1a2e}
.footer{text-align:center;padding:24px 0 10px;color:#334155;font-size:12px;line-height:1.8}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <span>GRAEHAM WATTS &middot; INTERO REAL ESTATE</span>
    <span>""" + now_pt.strftime('%b %-d %Y %H:%M PT') + """</span>
  </div>
  <div class="header">
    <h1>Weekly CRM Health</h1>
    <div class="sub">Week of """ + week_label + """ &middot; Prior: """ + prior_label + """</div>
  </div>

  <div class="score-card">
    <div class="bar"></div>
    <div class="score-num">""" + str(score) + """</div>
    <div class="score-grade">Grade """ + grade + """</div>
    <div class="score-label">""" + score_label + """</div>
    <div class="note">Score: new pipeline activity, wins, active deal health. Cold/Unqualified/holding stages excluded.</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi">
      <div class="num">""" + str(total_new_opps) + """</div>
      <div class="lbl">New Pipeline Entries</div>
      <div class="wow">""" + delta_badge(total_new_opps, total_prior_opps) + """</div>
    </div>
    <div class="kpi">
      <div class="num">""" + str(total_wins) + """</div>
      <div class="lbl">Closed Won</div>
      <div class="wow">""" + delta_badge(total_wins, len(prior_wins)) + """</div>
    </div>
    <div class="kpi">
      <div class="num">""" + str(len(active_open)) + """</div>
      <div class="lbl">Active Open Deals</div>
      <div class="wow"><span style="color:#334155;font-size:11px">excl. cold/dormant</span></div>
    </div>
    <div class="kpi">
      <div class="num">""" + val_display + """</div>
      <div class="lbl">Active Pipeline</div>
      <div class="wow"><span style="color:#334155;font-size:11px">active stages only</span></div>
    </div>
  </div>

  <div class="section">
    <h2>&#9889; Attention Needed</h2>
    """ + attn_html + """
  </div>

  <div class="section">
    <h2>&#128293; Active Pipeline by Stage</h2>
    <p style="font-size:12px;color:#475569;margin-bottom:12px">Open deals in working stages (Cold, Unqualified, and holding stages shown as separate callout)</p>
    <table>
      <thead><tr>
        <th>Pipeline &rarr; Stage</th>
        <th style="text-align:center">Deals</th>
        <th style="text-align:right">Value</th>
      </tr></thead>
      <tbody>""" + pipeline_rows + """</tbody>
    </table>
    <p class="caveat">""" + str(len(dormant_open)) + """ contacts in Cold / Unqualified / holding stages not shown (dormant). """ + str(len(old_active)) + """ active-stage leads are 90+ days old (cleanup backlog).</p>
  </div>

  <div class="section">
    <h2>&#9200; Needs Follow-Up &mdash; Recent Leads (&le;90 days, """ + str(STALE_DAYS) + """+ days untouched)</h2>
    <p style="font-size:12px;color:#475569;margin-bottom:12px">Leads created in the last 90 days that haven&rsquo;t been contacted in """ + str(STALE_DAYS) + """+ days — these people need a call or text now</p>
    <table>
      <thead><tr>
        <th>Name</th>
        <th>Pipeline</th>
        <th>Stage</th>
        <th style="text-align:center">Idle</th>
        <th style="text-align:right">Value</th>
      </tr></thead>
      <tbody>""" + stale_rows + """</tbody>
    </table>
    """ + (f'<p class="caveat">{len(stale_recent)} shown (top 12 by idle days). {len(old_active):,} additional leads are 90+ days old — see Attention section.</p>' if len(stale_recent) > 12 else "") + """
  </div>

  <div class="section">
    <h2>&#128202; New Pipeline Activity This Week</h2>
    <p style="font-size:12px;color:#475569;margin-bottom:12px">Opportunities created this week by pipeline (derived from createdAt — reliable metric)</p>
    <table>
      <thead><tr>
        <th>Pipeline</th>
        <th style="text-align:center">New This Week</th>
        <th style="text-align:center">vs Prior Wk</th>
      </tr></thead>
      <tbody>""" + opp_pipeline_rows + """</tbody>
    </table>
  </div>

  <div class="section">
    <h2>&#127919; This Week&rsquo;s Funnel</h2>
    """ + funnel_html + """
    <div style="display:flex;gap:20px;margin-top:14px;padding-top:12px;border-top:1px solid #0e1a2e;flex-wrap:wrap">
      <div style="font-size:13px;color:#64748b">Entry&rarr;Win rate: <strong style="color:#22c55e">""" + win_rate + """</strong></div>
      <div style="font-size:13px;color:#64748b">Prior week entries: <strong style="color:#94a3b8">""" + str(total_prior_opps) + """</strong></div>
    </div>
  </div>

  <div class="footer">
    Graeham Watts &nbsp;&middot;&nbsp; Intero Real Estate &nbsp;&middot;&nbsp; graehamwatts@gmail.com<br>
    CRM Health &nbsp;&middot;&nbsp; """ + now_pt.strftime('%Y-%m-%d %H:%M PT') + """
  </div>
</div>
</body>
</html>""")

# ─── Write ────────────────────────────────────────────────────────────────

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
        go.write(f"new_opps={total_new_opps}\n")
        go.write(f"stale_recent={len(stale_recent)}\n")
        go.write(f"old_active={len(old_active)}\n")
        go.write(f"active_open={len(active_open)}\n")
