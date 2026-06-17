#!/usr/bin/env python3
"""Morning Command Center — action-first daily brief for Graeham Watts.

Pulls live GoHighLevel data (direct PIT), builds an action-first HTML dashboard,
writes it to dashboards/command-center/{date}.html (+ latest.html), and emails it
to BRIEF_RECIPIENTS. Replaces the retired Daily Attribution Brief.

Env: GHL_PIT, GHL_LOCATION_ID, GMAIL_USERNAME, GMAIL_APP_PASSWORD, BRIEF_RECIPIENTS.
"""
import json, os, ssl, smtplib, sys, urllib.request, urllib.parse, datetime
from collections import Counter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

PIT = os.environ["GHL_PIT"]
LOC = os.environ["GHL_LOCATION_ID"]
BASE = "https://services.leadconnectorhq.com"
H = {"Authorization": f"Bearer {PIT}", "Version": "2021-07-28",
     "Content-Type": "application/json", "Accept": "application/json",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
NOW = datetime.datetime.now(datetime.timezone.utc)
PT = NOW.astimezone(datetime.timezone(datetime.timedelta(hours=-7)))
date_slug = PT.strftime("%Y-%m-%d")
date_label = PT.strftime("%A, %B ") + str(PT.day) + ", " + PT.strftime("%Y")

def get(path):
    req = urllib.request.Request(BASE + path, headers=H, method="GET")
    with urllib.request.urlopen(req, timeout=45) as r: return json.loads(r.read())
def post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), headers=H, method="POST")
    with urllib.request.urlopen(req, timeout=45) as r: return json.loads(r.read())
def days_ago(iso):
    if not iso: return None
    try:
        dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (NOW - dt).days
    except Exception: return None

# pipelines + stage map
pl = get(f"/opportunities/pipelines?locationId={LOC}").get("pipelines", [])
stage_name, stage_pipe = {}, {}
for p in pl:
    for s in p.get("stages", []):
        stage_name[s["id"]] = s.get("name", "")
        stage_pipe[s["id"]] = p.get("name", "")
def stages_matching(*subs):
    return {sid for sid, nm in stage_name.items() if any(x in nm.lower() for x in subs)}
UNCONTACTED = stages_matching("uncontacted")
APPT = stages_matching("appointment")
HOT = stages_matching("under contract", "active buyer", "active seller", "within 3 months")

def all_open_opps(cap=6000):
    out = []
    for page in range(1, 70):
        q = urllib.parse.urlencode({"location_id": LOC, "limit": 100, "status": "open", "page": page})
        d = get(f"/opportunities/search?{q}")
        batch = d.get("opportunities", [])
        if not batch: break
        out.extend(batch)
        if len(batch) < 100 or len(out) >= cap: break
    return out

print("Pulling open opportunities...", flush=True)
opens = all_open_opps()
print(f"  {len(opens)} open opps", flush=True)

def cname(o):
    c = o.get("contact") or {}
    return c.get("name") or o.get("name", "").replace(" - Lead", "").strip() or "—"
def cphone(o):
    return (o.get("contact") or {}).get("phone") or ""
def staleness(o):
    return days_ago(o.get("lastStageChangeAt") or o.get("updatedAt"))

uncontacted = sorted([o for o in opens if o.get("pipelineStageId") in UNCONTACTED], key=lambda o: -(staleness(o) or 0))
appts = [o for o in opens if o.get("pipelineStageId") in APPT]
hot = [o for o in opens if o.get("pipelineStageId") in HOT]
cold_all = sorted([o for o in hot if (staleness(o) or 0) >= 14], key=lambda o: -(staleness(o) or 0))
under_contract = [o for o in opens if "under contract" in stage_name.get(o.get("pipelineStageId"), "").lower()]

def contacts_since(days):
    gte = (NOW - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    out, sa = [], None
    for _ in range(12):
        body = {"locationId": LOC, "pageLimit": 100,
                "sort": [{"field": "dateAdded", "direction": "desc"}],
                "filters": [{"field": "dateAdded", "operator": "range", "value": {"gte": gte}}]}
        if sa: body["searchAfter"] = sa
        d = post("/contacts/search", body)
        b = d.get("contacts", [])
        out.extend(b)
        if len(b) < 100: break
        sa = b[-1].get("searchAfter")
        if not sa: break
    return out
new7 = contacts_since(7)
new1 = [c for c in new7 if (days_ago(c.get("dateAdded")) or 99) < 1]
def csrc(c): return str(c.get("source") or "Unknown")
src7 = Counter(csrc(c) for c in new7)
def nm2(c): return ((c.get("firstName") or "") + " " + (c.get("lastName") or "")).strip() or c.get("email") or "—"

GOLD, INK, BG, CARD, LINE, MUTE = "#C9A052", "#0f1729", "#060d1a", "#0f1729", "#1e293b", "#94a3b8"
def chip(n, label, color=GOLD):
    return (f'<div style="background:{CARD};border:1px solid {LINE};border-radius:10px;padding:14px 12px;text-align:center">'
            f'<div style="font-size:26px;font-weight:800;color:{color}">{n}</div>'
            f'<div style="font-size:11px;color:{MUTE};margin-top:3px;text-transform:uppercase;letter-spacing:.04em">{label}</div></div>')
def tbl(headers, rows_html, empty):
    if not rows_html: return f'<div style="color:{MUTE};font-size:13px;padding:6px 0">{empty}</div>'
    th = "".join(f'<th style="text-align:left;padding:8px 10px;background:#162032;color:{MUTE};font-size:11px;text-transform:uppercase;letter-spacing:.04em">{h}</th>' for h in headers)
    return f'<table style="width:100%;border-collapse:collapse"><thead><tr>{th}</tr></thead><tbody>{rows_html}</tbody></table>'
def section(title, sub, inner):
    return (f'<div style="background:{CARD};border:1px solid {LINE};border-radius:12px;padding:18px 20px;margin-bottom:14px">'
            f'<h2 style="font-size:14px;font-weight:800;color:{GOLD};margin:0 0 2px;text-transform:uppercase;letter-spacing:.05em">{title}</h2>'
            f'<div style="font-size:12px;color:{MUTE};margin-bottom:12px">{sub}</div>{inner}</div>')

def td(v, extra=""): return f'<td style="padding:8px 10px;border-bottom:1px solid {LINE};{extra}">{v}</td>'
unc_rows = "".join(f"<tr>{td(cname(o),'font-weight:600')}{td(o.get('source') or '—','color:'+MUTE+';font-size:12px')}{td(str(staleness(o) or 0)+'d waiting','color:#ef9a9a;font-size:12px')}</tr>" for o in uncontacted[:15])
appt_rows = "".join(f"<tr>{td(cname(o),'font-weight:600')}{td(stage_pipe.get(o.get('pipelineStageId'),''),'color:'+MUTE+';font-size:12px')}{td(cphone(o),'color:'+MUTE+';font-size:12px')}</tr>" for o in appts[:15])
cold_rows = "".join(f"<tr>{td(cname(o),'font-weight:600')}{td(stage_name.get(o.get('pipelineStageId'),''),'color:'+MUTE+';font-size:12px')}{td(str(staleness(o))+'d cold','color:#f4b955;font-size:12px')}</tr>" for o in cold_all[:8])
new_rows = "".join(f"<tr>{td(nm2(c))}{td(csrc(c),'color:'+MUTE+';font-size:12px')}{td((c.get('dateAdded') or '')[:10],'color:'+MUTE+';font-size:12px')}</tr>" for c in new7[:20])
src_rows = "".join(f"<tr>{td(s)}{td(str(n),'text-align:right;font-weight:700;color:'+GOLD)}</tr>" for s, n in src7.most_common())

def stage_count(*subs):
    sids = stages_matching(*subs); return sum(1 for o in opens if o.get("pipelineStageId") in sids)
snap = [("New / uncontacted", len(uncontacted)), ("Appointments set", len(appts)),
        ("Active buyers", stage_count("active buyer")), ("Active sellers", stage_count("active seller")),
        ("Buyers within 3 mo", stage_count("buyer – within 3 months", "buyer - within 3 months")),
        ("Sellers within 3 mo", stage_count("seller – within 3 months", "seller - within 3 months")),
        ("Under contract", len(under_contract))]
snap_html = "".join(f"<tr>{td(lbl)}{td(str(n),'text-align:right;font-weight:700;color:'+GOLD)}</tr>" for lbl, n in snap)

action_total = len(uncontacted) + len(appts) + len(cold_all)
cold_sub = f"Active buyers/sellers with no movement in 14+ days. Showing the 8 most overdue of {len(cold_all)} total — work the rest from the Monday CRM report."
html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Morning Command Center · {date_label}</title></head>
<body style="margin:0;background:{BG};font-family:'DM Sans',Segoe UI,Arial,sans-serif;color:#e2e8f0">
<div style="max-width:720px;margin:0 auto;padding:22px 16px">
  <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;color:{MUTE};margin-bottom:14px">
    <span><b style="color:{GOLD}">Morning Command Center</b> · Graeham Watts</span><span>{date_label}</span></div>
  <div style="background:linear-gradient(135deg,{INK},#162032);border:1px solid {LINE};border-radius:12px;padding:20px;margin-bottom:14px">
    <div style="font-size:20px;font-weight:800;color:#f1f5f9">{action_total} thing{'s' if action_total != 1 else ''} need you today</div>
    <div style="font-size:13px;color:{MUTE};margin-top:3px">{len(uncontacted)} new to call · {len(appts)} appointment{'s' if len(appts) != 1 else ''} · {len(cold_all)} going cold</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px">
    {chip(len(new1), "New leads · 24h")}{chip(len(new7), "New leads · 7d")}{chip(len(opens), "Open opps")}{chip(len(under_contract), "Under contract", "#22c55e")}
  </div>
  {section("🔴 New &amp; uncontacted — call first", "Opportunities sitting in an uncontacted stage. Longest-waiting first.", tbl(["Name", "Source", "Waiting"], unc_rows, "No uncontacted leads — you're clear. ✅"))}
  {section("📅 Appointments on the board", "Scheduled / rescheduled appointments to prep + confirm.", tbl(["Name", "Pipeline", "Phone"], appt_rows, "No appointments on the board."))}
  {section("🟠 Going cold — rescue", cold_sub, tbl(["Name", "Stage", "Cold"], cold_rows, "Nothing going cold. ✅"))}
  {section("🆕 New leads this week", f"{len(new1)} in last 24h, {len(new7)} in last 7 days.", tbl(["Name", "Source", "Added"], new_rows, "No new leads in the last 7 days."))}
  {section("📊 Pipeline snapshot", "Where everyone sits right now (open opportunities).", tbl(["Stage", "Count"], snap_html, ""))}
  {section("📈 Lead sources · last 7 days", "Where this week's leads came from.", tbl(["Source", "Leads"], src_rows, "No new leads this week."))}
  <div style="text-align:center;color:#475569;font-size:12px;padding:16px 0">
    Graeham Watts · Intero Real Estate · DRE# 01466876<br>
    {len(opens)} open opportunities · generated {PT.strftime('%Y-%m-%d %H:%M PT')}
  </div>
</div></body></html>"""

outdir = "dashboards/command-center"
os.makedirs(outdir, exist_ok=True)
for fn in (f"{date_slug}.html", "latest.html"):
    with open(os.path.join(outdir, fn), "w", encoding="utf-8") as f:
        f.write(html)
print(f"Wrote {outdir}/{date_slug}.html (+latest.html)", flush=True)

# email
user = os.environ.get("GMAIL_USERNAME"); pw = os.environ.get("GMAIL_APP_PASSWORD")
rcpts = [r.strip() for r in os.environ.get("BRIEF_RECIPIENTS", "").split(",") if r.strip()]
if user and pw and rcpts:
    url = f"https://graehamwatts.github.io/online-content/dashboards/command-center/{date_slug}.html"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☀️ Morning Command Center — {action_total} action items ({len(uncontacted)} to call, {len(appts)} appts, {len(cold_all)} cold)"
    msg["From"] = user; msg["To"] = ", ".join(rcpts)
    msg.attach(MIMEText(f"{action_total} things need you today. {len(uncontacted)} to call, {len(appts)} appointments, {len(cold_all)} going cold. Dashboard: {url}", "plain"))
    msg.attach(MIMEText(html.replace("</body>", f'<div style="text-align:center;padding:0 0 16px"><a href="{url}" style="color:#C9A052;font-size:12px">View in browser →</a></div></body>'), "html"))
    ctx = ssl.create_default_context()
    sent = False
    for host, port, mode in [("smtp.gmail.com", 587, "starttls"), ("smtp.gmail.com", 465, "ssl")]:
        try:
            if mode == "starttls":
                s = smtplib.SMTP(host, port, timeout=30); s.starttls(context=ctx)
            else:
                s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
            s.login(user, pw); s.sendmail(user, rcpts, msg.as_string()); s.quit()
            print(f"Emailed Command Center to {', '.join(rcpts)} via {host}:{port}", flush=True); sent = True; break
        except Exception as e:
            print(f"  {host}:{port} failed: {e}", flush=True)
    if not sent:
        print("::error::Command Center email failed on all SMTP routes"); sys.exit(1)
else:
    print("::warning::Email skipped — GMAIL_USERNAME/GMAIL_APP_PASSWORD/BRIEF_RECIPIENTS not all set")

# GITHUB_OUTPUT for the workflow
go = os.environ.get("GITHUB_OUTPUT")
if go:
    with open(go, "a") as f:
        f.write(f"date_slug={date_slug}\naction_total={action_total}\n")
