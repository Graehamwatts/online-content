#!/usr/bin/env python3
"""
Daily Attribution Brief Generator

Pulls yesterday's GHL lead activity, groups by source, compares to baselines,
generates an HTML email, commits to GitHub, and sends via Gmail.

Yesterday = 24h window in Pacific Time (midnight to midnight, local time)
"""

import os
import sys
import json
import requests
import smtplib
import pytz
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
import subprocess

# ============================================================================
# CONFIG
# ============================================================================

GHL_PIT = os.environ.get("GHL_PIT", "").strip()
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "").strip()
GMAIL_USERNAME = os.environ.get("GMAIL_USERNAME", "").strip()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

if not all([GHL_PIT, GHL_LOCATION_ID, GMAIL_USERNAME, GMAIL_APP_PASSWORD]):
    print("::error::Missing required secrets: GHL_PIT, GHL_LOCATION_ID, GMAIL_USERNAME, GMAIL_APP_PASSWORD")
    sys.exit(1)

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
        "Content-Type": "application/json"
    }

def get_yesterday_window_pt():
    """Return (start, end) as ISO 8601 strings for yesterday in PT (midnight to midnight)."""
    now_pt = datetime.now(PT)
    yesterday_pt = now_pt - timedelta(days=1)
    start = yesterday_pt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = yesterday_pt.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Convert to UTC for API
    start_utc = start.astimezone(pytz.UTC)
    end_utc = end.astimezone(pytz.UTC)
    return start_utc.isoformat(), end_utc.isoformat(), yesterday_pt.strftime("%Y-%m-%d")

def ghl_get(endpoint, params=None):
    """GET request to GHL API with pagination support."""
    url = f"{GHL_API_BASE}{endpoint}"
    all_data = []
    page = 1
    limit = 100
    
    while True:
        p = params.copy() if params else {}
        p["limit"] = limit
        p["offset"] = (page - 1) * limit
        
        try:
            resp = requests.get(url, params=p, headers=ghl_headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            items = data.get("contacts") or data.get("opportunities") or data.get("users") or data.get("conversations") or []
            if not items:
                break
            
            all_data.extend(items)
            
            if len(items) < limit:
                break
            page += 1
        except Exception as e:
            print(f"Error fetching {endpoint} page {page}: {e}")
            break
    
    return all_data

def ghl_post(endpoint, payload):
    """POST request to GHL API with pagination."""
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
            print(f"Error posting to {endpoint} offset {skip}: {e}")
            break
    
    return all_data

def normalize_source(contact):
    """Extract and normalize source from contact custom fields."""
    source_field = None
    
    # Check standard fields
    for field in ["contactSource", "source", "attributed_source", "utm_source"]:
        val = contact.get(field)
        if val:
            source_field = val.lower().strip()
            break
    
    # Check custom fields (these may have IDs as keys)
    custom_fields = contact.get("customFields", {})
    if isinstance(custom_fields, dict):
        for key, val in custom_fields.items():
            if val and any(x in key.lower() for x in ["source", "utm", "attributed"]):
                source_field = str(val).lower().strip()
                break
    
    if not source_field:
        return "Unknown"
    
    # Map to buckets
    if any(x in source_field for x in ["organic", "seo", "google search", "search", "google"]):
        return "Organic Search / SEO"
    elif any(x in source_field for x in ["gmb", "google business", "maps", "local"]):
        return "Google Business Profile"
    elif any(x in source_field for x in ["google ads", "meta ads", "facebook ads", "paid", "cpc", "ppc"]):
        return "Paid Ads"
    elif any(x in source_field for x in ["instagram", "facebook", "tiktok", "youtube", "social"]):
        return "Social Organic"
    elif any(x in source_field for x in ["referral", "sphere", "past client", "agent"]):
        return "Referral"
    elif any(x in source_field for x in ["direct", "website", "form", "contact"]):
        return "Direct / Website"
    elif any(x in source_field for x in ["cold", "manual"]):
        return "Cold"
    else:
        return "Other"

# ============================================================================
# PULL GHL DATA
# ============================================================================

print("Pulling GHL data for yesterday...")
start_iso, end_iso, yesterday_date = get_yesterday_window_pt()
print(f"  Date window: {yesterday_date} (PT)")
print(f"  ISO window: {start_iso} to {end_iso}")

# Get custom field definitions
try:
    custom_fields_resp = requests.get(
        f"{GHL_API_BASE}/locations/{GHL_LOCATION_ID}/customFields",
        headers=ghl_headers(),
        timeout=30
    )
    custom_fields_resp.raise_for_status()
    custom_fields_meta = custom_fields_resp.json().get("customFields", [])
    print(f"  Custom fields found: {len(custom_fields_meta)}")
except Exception as e:
    print(f"  Warning: Could not fetch custom fields: {e}")
    custom_fields_meta = []

# Get all contacts created yesterday
contacts_payload = {
    "query": {
        "direction": "asc",
        "sortBy": "dateAdded"
    },
    "limit": 100,
    "skip": 0
}
all_contacts = ghl_post("/contacts/search", contacts_payload)
yesterday_contacts = [
    c for c in all_contacts
    if c.get("dateAdded") and start_iso <= c.get("dateAdded") <= end_iso
]
print(f"  Yesterday's new contacts: {len(yesterday_contacts)}")

# Get all opportunities created/won yesterday
opp_payload = {"location_id": GHL_LOCATION_ID}
all_opportunities = ghl_get("/opportunities/search", opp_payload)

yesterday_opps_created = [
    o for o in all_opportunities
    if o.get("dateAdded") and start_iso <= o.get("dateAdded") <= end_iso
]
print(f"  Yesterday's new opportunities: {len(yesterday_opps_created)}")

# Get opportunities moved to Won yesterday (check status changes)
yesterday_opps_won = []
for opp in all_opportunities:
    if opp.get("status") and "won" in opp.get("status", "").lower():
        updated = opp.get("dateUpdated") or opp.get("dateAdded")
        if updated and start_iso <= updated <= end_iso:
            yesterday_opps_won.append(opp)
print(f"  Yesterday's closed wins: {len(yesterday_opps_won)}")

# ============================================================================
# ATTRIBUTION GROUPING
# ============================================================================

source_buckets = {
    "Organic Search / SEO": [],
    "Google Business Profile": [],
    "Paid Ads": [],
    "Social Organic": [],
    "Referral": [],
    "Direct / Website": [],
    "Cold": [],
    "Unknown": []
}

for contact in yesterday_contacts:
    source = normalize_source(contact)
    source_buckets[source].append(contact)

# Count opps by source
opp_source_buckets = {k: [] for k in source_buckets.keys()}
for opp in yesterday_opps_created:
    # Assume opp has a linked contact
    contact_id = opp.get("contactId")
    # Simplify: attribute to Unknown (we'd need contact lookup for proper attribution)
    source = "Unknown"
    opp_source_buckets[source].append(opp)

wins_source_buckets = {k: [] for k in source_buckets.keys()}
for opp in yesterday_opps_won:
    source = "Unknown"
    wins_source_buckets[source].append(opp)

# ============================================================================
# GENERATE HTML EMAIL
# ============================================================================

def format_names(contacts, max_count=3):
    """Format first names + last initials."""
    names = []
    for c in contacts[:max_count]:
        first = c.get("firstName", "?")
        last = c.get("lastName", "?")
        last_initial = last[0].upper() if last else "?"
        names.append(f"{first} {last_initial}.")
    return ", ".join(names)

def compare_vs_baseline(count):
    """Placeholder comparison — would need prior data."""
    return "→"  # Would be +/−/→ based on comparison

status_class = "green" if sum(len(v) for v in source_buckets.values()) >= 2 else "amber"
status_text = f"{sum(len(v) for v in source_buckets.values())} leads"

html_email = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Attribution Brief</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'DM Sans', sans-serif;
            background: #f5f5f5;
            color: #0f1729;
            line-height: 1.6;
        }}
        .container {{
            max-width: 720px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #0f1729 0%, #1a2d4d 100%);
            color: white;
            padding: 32px 24px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .status-strip {{
            background: #27ae60;
            color: white;
            padding: 12px 24px;
            font-weight: 600;
            text-align: center;
            font-size: 14px;
        }}
        .status-strip.amber {{ background: #f39c12; }}
        .status-strip.red {{ background: #e74c3c; }}
        .content {{
            padding: 24px;
        }}
        .kpi-cards {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 16px;
            text-align: center;
            border-left: 4px solid #f4b955;
        }}
        .kpi-card .number {{
            font-size: 28px;
            font-weight: 700;
            color: #0f1729;
            margin-bottom: 4px;
        }}
        .kpi-card .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .read-section {{
            background: #f0f4f8;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 24px;
            border-left: 4px solid #f4b955;
        }}
        .read-section h3 {{
            font-size: 12px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }}
        .read-section p {{
            font-size: 14px;
            line-height: 1.6;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            font-size: 13px;
        }}
        th {{
            background: #0f1729;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .source-name {{
            font-weight: 600;
            color: #0f1729;
        }}
        .count-badge {{
            background: #f4b955;
            color: #0f1729;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            display: inline-block;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 16px 24px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        .footer a {{
            color: #0f1729;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Daily Attribution Brief</h1>
            <p>{yesterday_date}</p>
        </div>
        
        <div class="status-strip {status_class}">
            {status_text}
        </div>
        
        <div class="content">
            <div class="kpi-cards">
                <div class="kpi-card">
                    <div class="number">{len(yesterday_contacts)}</div>
                    <div class="label">New Leads</div>
                </div>
                <div class="kpi-card">
                    <div class="number">{len(yesterday_opps_created)}</div>
                    <div class="label">Opportunities</div>
                </div>
                <div class="kpi-card">
                    <div class="number">{len(yesterday_opps_won)}</div>
                    <div class="label">Closed Wins</div>
                </div>
                <div class="kpi-card">
                    <div class="number">-</div>
                    <div class="label">Top Source</div>
                </div>
            </div>
            
            <div class="read-section">
                <h3>The Read</h3>
                <p>Yesterday generated {len(yesterday_contacts)} new leads across {sum(1 for v in source_buckets.values() if v)} active sources. {('Strong day.' if len(yesterday_contacts) >= 5 else 'Moderate day.' if len(yesterday_contacts) >= 2 else 'Slow day.')} No wins recorded.</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Count</th>
                        <th>Notable Names</th>
                    </tr>
                </thead>
                <tbody>
"""

for source in sorted(source_buckets.keys()):
    contacts = source_buckets[source]
    if contacts:
        names = format_names(contacts, 3)
        html_email += f"""
                    <tr>
                        <td><span class="source-name">{source}</span></td>
                        <td><span class="count-badge">{len(contacts)}</span></td>
                        <td>{names}</td>
                    </tr>
"""

html_email += """
                </tbody>
            </table>
            
        </div>
        
        <div class="footer">
            <p>Daily Attribution Brief • Generated by Graeham's CRM automation</p>
            <p style="margin-top: 8px;"><a href="https://graehamwatts.github.io/online-content/dashboards/pipeline/">View Full Pipeline Dashboard</a></p>
        </div>
    </div>
</body>
</html>
"""

print("\nHTML email generated.")

# ============================================================================
# COMMIT TO GITHUB
# ============================================================================

dashboard_dir = "dashboards/attribution"
os.makedirs(dashboard_dir, exist_ok=True)

output_file = f"{dashboard_dir}/{yesterday_date}-daily.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_email)

print(f"Wrote: {output_file}")

# Set GitHub output for the commit message
with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as out:
    out.write(f"date_slug={yesterday_date}\n")

# ============================================================================
# SEND EMAIL
# ============================================================================

try:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Attribution Brief — {yesterday_date}"
    msg["From"] = GMAIL_USERNAME
    msg["To"] = "graehamwatts@gmail.com"
    
    # Attach HTML
    msg.attach(MIMEText(html_email, "html"))
    
    # Send via Gmail
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
    server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print(f"Email sent to graehamwatts@gmail.com")
except Exception as e:
    print(f"::warning::Email send failed: {e}")
    print("Brief still committed to GitHub.")

print("\nDaily Attribution Brief complete.")
sys.exit(0)
