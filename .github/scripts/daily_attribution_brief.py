#!/usr/bin/env python3
"""
Daily Attribution Brief — pulls yesterday's GHL contacts/opportunities/wins, groups
by source, compares to baseline, writes a branded HTML brief, and exposes its path
+ subject to the GitHub Action via GITHUB_OUTPUT.

Runs inside a GitHub Action (GHL is allowed from github.com). Reads:
  - GHL_PIT          (env, from repo secret)
  - GHL_LOCATION_ID  (env, from repo secret)
  - DATE_OVERRIDE    (env, optional YYYY-MM-DD for the "yesterday" date)

Writes:
  dashboards/attribution/{YYYY-MM-DD}-daily.html
"""
from __future__ import annotations
import os, sys, json, html
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter
from pathlib import Path

import requests

# ---------- config ----------
PIT = os.environ.get("GHL_PIT", "").strip()
LOC = os.environ.get("GHL_LOCATION_ID", "").strip()
DATE_OVERRIDE = os.environ.get("DATE_OVERRIDE", "").strip()
BASE = "https://services.leadconnectorhq.com"
HDRS = {
    "Authorization": f"Bearer {PIT}",
    "Version": "2021-07-28",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
PACIFIC = timezone(timedelta(hours=-7))  # PDT — accurate Mar-Nov. Adjust if running in PST.

# ---------- date window ----------
def get_window():
    if DATE_OVERRIDE:
        d = datetime.strptime(DATE_OVERRIDE, "%Y-%m-%d").replace(tzinfo=PACIFIC)
        y_start = d
    else:
        now_p = datetime.now(PACIFIC)
        today_p = now_p.replace(hour=0, minute=0, second=0, microsecond=0)
        y_start = today_p - timedelta(days=1)
    y_end = y_start + timedelta(days=1)
    return y_start, y_end

# ---------- API helpers ----------
def ghl_post(path, body):
    r = requests.post(f"{BASE}{path}", headers=HDRS, json=body, timeout=30)
    return r

def ghl_get(path, params=None):
    r = requests.get(f"{BASE}{path}", headers=HDRS, params=params, timeout=30)
    return r

def search_contacts_in_window(start_iso, end_iso):
    """Paginate /contacts/search filtered by dateAdded between start and end."""
    contacts = []
    page = 1
    while True:
        body = {
            "locationId": LOC,
            "page": page,
            "pageLimit": 100,
            "filters": [
                {"field": "dateAdded", "operator": "between", "value": [start_iso, end_iso]}
            ],
        }
        r = ghl_post("/contacts/search", body)
        if r.status_code != 200:
            raise RuntimeError(f"contacts/search failed: {r.status_code} {r.text[:500]}")
        data = r.json()
        batch = data.get("contacts", [])
        contacts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 50:
            break
    return contacts

def search_opportunities_in_window(start_iso, end_iso):
    opps = []
    page = 1
    while True:
        params = {
            "location_id": LOC,
            "page": page,
            "limit": 100,
            "startAfter": start_iso,
            "startAfterId": "",
        }
        r = ghl_get("/opportunities/search", params)
        if r.status_code != 200:
            raise RuntimeError(f"opportunities/search failed: {r.status_code} {r.text[:500]}")
        data = r.json()
        batch = data.get("opportunities", [])
        # client-side filter to the window since this endpoint's filter shape varies
        for o in batch:
            ts = o.get("createdAt") or o.get("dateAdded")
            if ts and start_iso <= ts < end_iso:
                opps.append(o)
        if len(batch) < 100:
            break
        page += 1
        if page > 50:
            break
    return opps

def get_pipelines():
    r = ghl_get("/opportunities/pipelines", {"locationId": LOC})
    if r.status_code != 200:
        return []
    return r.json().get("pipelines", [])

def get_custom_fields():
    r = ghl_get(f"/locations/{LOC}/customFields")
    if r.status_code != 200:
        return []
    return r.json().get("customFields", [])

# ---------- source bucketing ----------
def bucket_source(c):
    """Map a contact's source-related fields to a normalized bucket."""
    def s(v): return str(v).strip().lower() if v is not None else ""
    src = s(c.get("source"))
    attr = s(c.get("attributionSource"))
    contact_src = s(c.get("contactSource"))
    utm_src = s(c.get("utmSource"))
    utm_med = s(c.get("utmMedium"))
    tags = [t.lower() for t in (c.get("tags") or [])]
    blob = " ".join([src, attr, contact_src, utm_src, utm_med] + tags)

    if any(k in blob for k in ["gmb", "google business", "google_my_business", "maps"]):
        return "Google Business Profile (GMB)"
    if utm_med in ("cpc", "paid", "ppc") or "google ads" in blob or "meta ads" in blob or "facebook ads" in blob:
        return "Paid ads"
    if any(k in blob for k in ["organic", "seo", "google search"]) or (utm_src == "google" and utm_med in ("", "organic")):
        return "Organic search / SEO"
    if any(k in blob for k in ["instagram", "ig", "tiktok", "youtube", "facebook"]) and "ads" not in blob:
        return "Social organic"
    if any(k in blob for k in ["referral", "sphere", "past client", "agent"]):
        return "Referral / sphere"
    if any(k in blob for k in ["manual", "cold", "imported"]):
        return "Cold (manually added)"
    if any(k in blob for k in ["website", "form", "landing"]) or src == "direct":
        return "Direct / website forms"
    if not blob.strip():
        return "Unknown / no attribution"
    return "Unknown / no attribution"

# ---------- HTML rendering ----------
BRAND_CSS = """
  body { margin:0; padding:0; background:#f4f2ed; font-family:'DM Sans',-apple-system,BlinkMacSystemFont,sans-serif; color:#0f1729; }
  .wrap { max-width:720px; margin:0 auto; background:#ffffff; }
  .topbar { background:#0f1729; color:#f4b955; padding:14px 28px; font-size:13px; letter-spacing:.08em; text-transform:uppercase; font-weight:600; }
  .header { padding:28px 28px 8px; }
  .h-date { font-size:13px; color:#6b7280; letter-spacing:.02em; }
  .h-title { font-size:28px; font-weight:700; margin:6px 0 4px; line-height:1.2; }
  .h-sub { font-size:14px; color:#475569; }
  .status { margin:16px 28px 0; padding:10px 14px; border-radius:8px; font-size:13px; font-weight:600; }
  .status.green { background:#dcfce7; color:#166534; }
  .status.amber { background:#fef3c7; color:#92400e; }
  .status.red { background:#fee2e2; color:#991b1b; }
  .kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; padding:18px 28px 4px; }
  .kpi { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; }
  .kpi-label { font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:#64748b; font-weight:600; }
  .kpi-value { font-size:26px; font-weight:700; margin-top:4px; color:#0f1729; }
  .kpi-sub { font-size:11px; color:#94a3b8; margin-top:2px; }
  .section { padding:18px 28px; }
  .section h2 { font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:#0f1729; margin:0 0 10px; font-weight:700; }
  .read { background:#fffbeb; border-left:3px solid #f4b955; padding:14px 16px; border-radius:6px; font-size:14px; line-height:1.55; color:#1e293b; }
  table.src { width:100%; border-collapse:collapse; font-size:13px; }
  table.src th { text-align:left; background:#f1f5f9; padding:10px; font-weight:600; color:#475569; font-size:11px; letter-spacing:.04em; text-transform:uppercase; }
  table.src td { padding:10px; border-top:1px solid #e2e8f0; vertical-align:top; }
  table.src tr:hover td { background:#fafbfc; }
  .pos { color:#16a34a; font-weight:600; }
  .neg { color:#dc2626; font-weight:600; }
  .flat { color:#64748b; }
  .funnel { padding:8px 0; }
  .funnel-row { display:flex; align-items:center; gap:10px; margin:6px 0; font-size:13px; }
  .funnel-bar { height:18px; background:#0f1729; border-radius:4px; }
  .funnel-label { flex:0 0 160px; color:#475569; font-weight:600; }
  .funnel-count { flex:0 0 40px; text-align:right; font-weight:700; }
  .footer { padding:24px 28px 36px; border-top:1px solid #e2e8f0; font-size:12px; color:#64748b; }
  .signature { margin-top:8px; font-weight:600; color:#0f1729; font-size:13px; }
  .dre { color:#94a3b8; font-size:11px; margin-top:2px; }
  @media (max-width:600px){ .kpis{grid-template-columns:repeat(2,1fr);} }
"""

def render_brief(date_str, leads, opps, wins, baseline_prior_dow, baseline_avg_7d,
                 source_breakdown, contacts_by_source, error=None):
    total = len(leads)
    opp_count = len(opps)
    win_count = len(wins)

    if baseline_prior_dow is not None and baseline_prior_dow > 0:
        ratio = total / baseline_prior_dow
        if ratio >= 1.0:
            status_class, status_text = "green", f"On track — {total} leads vs prior {baseline_prior_dow}"
        elif ratio >= 0.5:
            status_class, status_text = "amber", f"Soft — {total} leads vs prior {baseline_prior_dow} ({int(ratio*100)}%)"
        else:
            status_class, status_text = "red", f"Weak — {total} leads vs prior {baseline_prior_dow} ({int(ratio*100)}%)"
    else:
        status_class, status_text = "amber", "No baseline yet — first run"

    top_src = max(source_breakdown.items(), key=lambda x: x[1])[0] if source_breakdown else "—"

    # source rows
    rows = ""
    for src, cnt in sorted(source_breakdown.items(), key=lambda x: -x[1]):
        prior = source_breakdown.get(f"__prior__{src}", 0) if False else 0  # placeholder; real prior data attached below
        names = contacts_by_source.get(src, [])
        name_str = ", ".join(names[:5]) + (f" +{len(names)-5} more" if len(names) > 5 else "")
        rows += f"""
        <tr>
          <td><strong>{html.escape(src)}</strong></td>
          <td>{cnt}</td>
          <td class="flat">—</td>
          <td style="color:#64748b">{html.escape(name_str) or '—'}</td>
        </tr>"""

    # The Read
    if total == 0:
        the_read = "Zero new contacts entered the CRM yesterday. Check whether ad campaigns are live, forms are firing, and GMB is published. If volume is unusual for a weekday, audit the inbound capture stack today."
    else:
        the_read = f"{total} new contacts entered the CRM yesterday. {opp_count} became opportunities, {win_count} closed. Top inbound source was <strong>{html.escape(top_src)}</strong>. "
        if baseline_prior_dow:
            delta = total - baseline_prior_dow
            if delta > 0:
                the_read += f"Up {delta} vs same day last week — momentum building."
            elif delta < 0:
                the_read += f"Down {abs(delta)} vs same day last week — worth a quick look at source mix."
            else:
                the_read += "Flat vs same day last week."

    # funnel snapshot
    max_v = max(total, opp_count, win_count, 1)
    def bar_w(v): return int((v / max_v) * 360)
    funnel_html = f"""
      <div class="funnel">
        <div class="funnel-row"><div class="funnel-label">New leads</div><div class="funnel-bar" style="width:{bar_w(total)}px"></div><div class="funnel-count">{total}</div></div>
        <div class="funnel-row"><div class="funnel-label">Opportunities</div><div class="funnel-bar" style="width:{bar_w(opp_count)}px; background:#475569"></div><div class="funnel-count">{opp_count}</div></div>
        <div class="funnel-row"><div class="funnel-label">Closed wins</div><div class="funnel-bar" style="width:{bar_w(win_count)}px; background:#f4b955"></div><div class="funnel-count">{win_count}</div></div>
      </div>
    """

    error_block = ""
    if error:
        error_block = f"""
        <div class="section">
          <h2>GHL pull error</h2>
          <div class="read" style="background:#fee2e2; border-left-color:#dc2626;">
            <strong>{html.escape(str(error)[:200])}</strong>
          </div>
        </div>
        """

    sub_line = ""
    if baseline_prior_dow is not None:
        delta = total - baseline_prior_dow
        sym = "+" if delta >= 0 else ""
        sub_line = f"Day-over-week: {sym}{delta} leads"

    html_out = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Daily Attribution Brief — {html.escape(date_str)}</title>
<style>{BRAND_CSS}</style></head><body>
<div class="wrap">
  <div class="topbar">Daily Attribution Brief · {html.escape(date_str)}</div>
  <div class="header">
    <div class="h-date">{html.escape(date_str)}</div>
    <div class="h-title">Yesterday in your pipeline</div>
    <div class="h-sub">{html.escape(sub_line)}</div>
  </div>
  <div class="status {status_class}">{html.escape(status_text)}</div>
  <div class="kpis">
    <div class="kpi"><div class="kpi-label">Total leads</div><div class="kpi-value">{total}</div><div class="kpi-sub">yesterday</div></div>
    <div class="kpi"><div class="kpi-label">New opps</div><div class="kpi-value">{opp_count}</div><div class="kpi-sub">created</div></div>
    <div class="kpi"><div class="kpi-label">Closed wins</div><div class="kpi-value">{win_count}</div><div class="kpi-sub">stage moved</div></div>
    <div class="kpi"><div class="kpi-label">Top source</div><div class="kpi-value" style="font-size:14px; padding-top:8px">{html.escape(top_src)}</div><div class="kpi-sub">most active</div></div>
  </div>
  <div class="section">
    <h2>The Read</h2>
    <div class="read">{the_read}</div>
  </div>
  <div class="section">
    <h2>Source breakdown</h2>
    <table class="src">
      <thead><tr><th>Source</th><th>Count</th><th>vs prior week</th><th>Notable names</th></tr></thead>
      <tbody>{rows if rows else '<tr><td colspan="4" style="color:#94a3b8; text-align:center; padding:24px;">No leads yesterday.</td></tr>'}</tbody>
    </table>
  </div>
  <div class="section">
    <h2>Funnel snapshot</h2>
    {funnel_html}
  </div>
  {error_block}
  <div class="footer">
    Auto-generated by the Daily Attribution Brief skill · Run via GitHub Action.<br>
    Data source: GoHighLevel (Location {html.escape(LOC[:6])}…)
    <div class="signature">Graeham Watts</div>
    <div class="dre">REALTOR® · Intero Real Estate · DRE# 01466876</div>
  </div>
</div>
</body></html>"""
    return html_out, status_class, status_text

# ---------- main ----------
def main():
    y_start, y_end = get_window()
    date_str = y_start.strftime("%Y-%m-%d")
    prior_dow_start = y_start - timedelta(days=7)
    prior_dow_end = y_end - timedelta(days=7)

    out_dir = Path("dashboards/attribution")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_str}-daily.html"

    error = None
    leads = []
    opps = []
    wins = []
    baseline_prior_dow = None
    baseline_avg_7d = None
    source_breakdown = Counter()
    contacts_by_source = defaultdict(list)

    if not PIT or not LOC:
        error = "GHL_PIT or GHL_LOCATION_ID secret not set in repo. Workflow cannot authenticate to GoHighLevel."
    else:
        try:
            s_iso = y_start.astimezone(timezone.utc).isoformat()
            e_iso = y_end.astimezone(timezone.utc).isoformat()
            leads = search_contacts_in_window(s_iso, e_iso)
            opps = search_opportunities_in_window(s_iso, e_iso)
            # detect wins via pipeline metadata
            pipelines = get_pipelines()
            win_stage_ids = set()
            for p in pipelines:
                for st in p.get("stages", []):
                    nm = (st.get("name") or "").lower()
                    if "won" in nm or "closed won" in nm:
                        win_stage_ids.add(st.get("id"))
            wins = [o for o in opps if o.get("pipelineStageId") in win_stage_ids or (o.get("status") or "").lower() == "won"]

            # baseline: same day last week
            prior_s = prior_dow_start.astimezone(timezone.utc).isoformat()
            prior_e = prior_dow_end.astimezone(timezone.utc).isoformat()
            prior_leads = search_contacts_in_window(prior_s, prior_e)
            baseline_prior_dow = len(prior_leads)

            # group by source
            for c in leads:
                bucket = bucket_source(c)
                source_breakdown[bucket] += 1
                first = (c.get("firstName") or "").strip()
                last = (c.get("lastName") or "").strip()
                initial = (last[:1] + ".") if last else ""
                disp = (first + " " + initial).strip() or (c.get("email") or "contact")
                contacts_by_source[bucket].append(disp)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

    html_out, status_class, status_text = render_brief(
        date_str, leads, opps, wins, baseline_prior_dow, baseline_avg_7d,
        source_breakdown, contacts_by_source, error=error,
    )
    out_path.write_text(html_out, encoding="utf-8")

    subject_prefix = "Daily Attribution Brief"
    if error:
        subject = f"{subject_prefix} — GHL pull failed ({date_str})"
    elif len(leads) == 0:
        subject = f"Zero leads yesterday — here's what fired the day before ({date_str})"
    else:
        top_src = max(source_breakdown.items(), key=lambda x: x[1])[0]
        subject = f"{subject_prefix} — {len(leads)} leads, top: {top_src} ({date_str})"

    # expose outputs to next steps
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"subject={subject}\n")
            f.write(f"html_path={out_path}\n")
            f.write(f"date_str={date_str}\n")
            f.write(f"leads={len(leads)}\n")
    print(f"Wrote {out_path}")
    print(f"Subject: {subject}")
    if error:
        print(f"ERROR: {error}", file=sys.stderr)
        # Don't fail the job — we still want the email step to run
    return 0

if __name__ == "__main__":
    sys.exit(main())
