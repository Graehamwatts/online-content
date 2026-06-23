#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict
import base64

# Configuration
GHL_PIT = os.getenv('GHL_PIT', '').strip()
GHL_LOCATION_ID = os.getenv('GHL_LOCATION_ID', '').strip()
GMAIL_USERNAME = os.getenv('GMAIL_USERNAME', '').strip()
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '').strip()

GHL_API_BASE = 'https://services.leadconnectorhq.com'
GHL_HEADERS = {
    'Authorization': f'Bearer {GHL_PIT}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}

# Pacific timezone
PT = timezone(timedelta(hours=-7))
today_pt = datetime.now(PT)
yesterday_pt = today_pt - timedelta(days=1)
yesterday_date = yesterday_pt.date()

print(f"[{datetime.now().isoformat()}] Starting daily attribution brief for {yesterday_date}")

# Skip if weekend
if yesterday_date.weekday() >= 5:  # Saturday=5, Sunday=6
    print(f"Yesterday is weekend ({yesterday_date.strftime('%A')}), skipping")
    exit(0)

# Validation
if not GHL_PIT or not GHL_LOCATION_ID or not GMAIL_USERNAME or not GMAIL_APP_PASSWORD:
    print("ERROR: Missing required environment variables")
    exit(1)

def fetch_contacts_created_yesterday():
    """Fetch all contacts created yesterday"""
    # Yesterday midnight to midnight PT
    start_time = int(yesterday_pt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    end_time = int(yesterday_pt.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp() * 1000)
    
    contacts = []
    limit = 100
    offset = 0
    
    while True:
        url = f"{GHL_API_BASE}/contacts/search?locationId={GHL_LOCATION_ID}&limit={limit}&skip={offset}"
        payload = {
            "query": {
                "campaignId": None
            },
            "sort": "-dateAdded"
        }
        
        try:
            response = requests.post(url, json=payload, headers=GHL_HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            batch = data.get('contacts', [])
            if not batch:
                break
            
            # Filter by creation date
            for contact in batch:
                date_added = contact.get('dateAdded', 0) / 1000  # Convert to seconds
                if start_time <= date_added * 1000 <= end_time:
                    contacts.append(contact)
            
            offset += limit
        except Exception as e:
            print(f"ERROR fetching contacts: {e}")
            break
    
    return contacts

def fetch_opportunities_created_yesterday():
    """Fetch opportunities created yesterday"""
    start_time = int(yesterday_pt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    end_time = int(yesterday_pt.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp() * 1000)
    
    opps = []
    limit = 100
    offset = 0
    
    while True:
        url = f"{GHL_API_BASE}/opportunities/search?locationId={GHL_LOCATION_ID}&limit={limit}&skip={offset}"
        
        try:
            response = requests.get(url, headers=GHL_HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            batch = data.get('opportunities', [])
            if not batch:
                break
            
            # Filter by creation date
            for opp in batch:
                created_at = opp.get('createdAt', 0) / 1000
                if start_time <= created_at * 1000 <= end_time:
                    opps.append(opp)
            
            offset += limit
        except Exception as e:
            print(f"ERROR fetching opportunities: {e}")
            break
    
    return opps

def extract_source(contact):
    """Extract attribution source from contact"""
    # Check various source fields in priority order
    source_fields = [
        'attributionSource',
        'contactSource',
        contact.get('customFields', {}).get('source'),
        contact.get('customFields', {}).get('utm_source'),
    ]
    
    tags = contact.get('tags', [])
    
    for field in source_fields:
        if field:
            return str(field).lower()
    
    if tags:
        return f"tag:{tags[0]}"
    
    return "unknown"

def categorize_source(source_raw):
    """Categorize raw source into buckets"""
    source = source_raw.lower() if source_raw else ""
    
    buckets = {
        "organic_search": ["organic", "google", "seo", "search"],
        "gmb": ["gmb", "google business", "maps", "google maps"],
        "paid_ads": ["google ads", "meta ads", "facebook ads", "cpc", "paid", "ppc"],
        "social_organic": ["instagram", "IG", "facebook", "fb", "youtube", "yt", "tiktok"],
        "referral": ["referral", "sphere", "past client", "agent referral"],
        "direct": ["direct", "website", "form", "contact form"],
        "cold": ["cold", "manual"],
    }
    
    for bucket, keywords in buckets.items():
        for keyword in keywords:
            if keyword in source:
                return bucket
    
    return "unknown"

def build_html_brief(contacts, opps, yesterday_date):
    """Build HTML email brief"""
    
    # Categorize leads
    sources = defaultdict(list)
    for contact in contacts:
        raw_source = extract_source(contact)
        category = categorize_source(raw_source)
        sources[category].append({
            'name': contact.get('firstName', '') + ' ' + contact.get('lastName', ''),
            'email': contact.get('email', ''),
            'raw_source': raw_source
        })
    
    total_leads = len(contacts)
    total_opps = len(opps)
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: "DM Sans", sans-serif; color: #0f1729; margin: 0; padding: 0; }}
        .container {{ max-width: 720px; margin: 0 auto; background: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #0f1729 0%, #1a2a4a 100%); color: white; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .subheader {{ font-size: 14px; opacity: 0.9; margin-top: 5px; }}
        .kpi-row {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; padding: 20px; background: #f8f9fa; }}
        .kpi {{ background: white; padding: 15px; border-radius: 4px; text-align: center; border-left: 4px solid #f4b955; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: #0f1729; }}
        .kpi-label {{ font-size: 12px; color: #666; margin-top: 5px; text-transform: uppercase; }}
        .status-green {{ border-left-color: #22c55e; }}
        .status-amber {{ border-left-color: #f4b955; }}
        .status-red {{ border-left-color: #ef4444; }}
        .section {{ padding: 20px; }}
        .section-title {{ font-size: 16px; font-weight: 600; color: #0f1729; margin-bottom: 12px; border-bottom: 2px solid #f4b955; padding-bottom: 8px; }}
        .source-row {{ display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .source-name {{ font-weight: 500; }}
        .source-count {{ text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background: #f4b955; color: #0f1729; padding: 10px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #e5e7eb; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .footer {{ background: #0f1729; color: white; padding: 15px; text-align: center; font-size: 12px; }}
        .footer p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Daily Attribution Brief</h1>
            <div class="subheader">{yesterday_date.strftime('%A, %B %d, %Y')}</div>
        </div>
        
        <div class="kpi-row">
            <div class="kpi">
                <div class="kpi-value">{total_leads}</div>
                <div class="kpi-label">New Leads</div>
            </div>
            <div class="kpi">
                <div class="kpi-value">{total_opps}</div>
                <div class="kpi-label">Opportunities</div>
            </div>
            <div class="kpi">
                <div class="kpi-value">-</div>
                <div class="kpi-label">Closed Wins</div>
            </div>
            <div class="kpi">
                <div class="kpi-value">{max(sources.items(), key=lambda x: len(x[1]))[0] if sources else 'N/A'}</div>
                <div class="kpi-label">Top Source</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Source Breakdown</div>
            <table>
                <tr>
                    <th>Source</th>
                    <th>Count</th>
                    <th>% of Total</th>
                </tr>
"""
    
    for source, leads in sorted(sources.items(), key=lambda x: -len(x[1])):
        pct = (len(leads) / total_leads * 100) if total_leads > 0 else 0
        html += f"""                <tr>
                    <td>{source.replace('_', ' ').title()}</td>
                    <td>{len(leads)}</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""
    
    html += """            </table>
        </div>
        
        <div class="footer">
            <p>Daily Attribution Brief</p>
            <p>Generated by Property OS Analytics</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def send_email(subject, html_body, recipient):
    """Send email via Gmail"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
        
        print(f"[OK] Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False

# Main execution
try:
    print("Fetching contacts...")
    contacts = fetch_contacts_created_yesterday()
    print(f"Found {len(contacts)} contacts created yesterday")
    
    print("Fetching opportunities...")
    opps = fetch_opportunities_created_yesterday()
    print(f"Found {len(opps)} opportunities created yesterday")
    
    if len(contacts) == 0:
        print("[WARN] No leads found yesterday")
        subject = f"Daily Attribution Brief — {yesterday_date.strftime('%m/%d')} (No leads)"
        html = f"<p>No leads were captured yesterday ({yesterday_date.strftime('%A, %B %d, %Y')}).</p>"
    else:
        subject = f"Daily Attribution Brief — {yesterday_date.strftime('%m/%d')} ({len(contacts)} leads)"
        html = build_html_brief(contacts, opps, yesterday_date)
    
    # Save to file
    os.makedirs('dashboards/attribution', exist_ok=True)
    html_file = f"dashboards/attribution/{yesterday_date.isoformat()}-daily.html"
    with open(html_file, 'w') as f:
        f.write(html)
    print(f"[OK] Saved HTML to {html_file}")
    
    # Send email
    if GMAIL_USERNAME and GMAIL_APP_PASSWORD:
        send_email(subject, html, "graehamwatts@gmail.com")
    else:
        print("[WARN] Gmail credentials not configured, skipping email")
    
    print(f"[SUCCESS] Daily attribution brief completed for {yesterday_date}")

except Exception as e:
    print(f"[FATAL] {e}")
    import traceback
    traceback.print_exc()
    exit(1)
