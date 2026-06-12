#!/usr/bin/env python3
"""
crm_diagnostic.py - Inspect what the "open opportunities" actually are
and verify contact dateAdded accuracy.
"""
import requests, os, json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import pytz

PT = pytz.timezone("America/Los_Angeles")
GHL_PIT = os.environ["GHL_PIT"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
GHL_BASE = os.environ.get("GHL_API_BASE", "https://services.leadconnectorhq.com")
GHL_VERSION = os.environ.get("GHL_VERSION", "2021-07-28")

headers = {
    "Authorization": f"Bearer {GHL_PIT}",
    "Version": GHL_VERSION,
    "Content-Type": "application/json",
}
now_utc = datetime.now(timezone.utc)

# --- Pipeline map ---
print("=== PIPELINES ===", flush=True)
r = requests.get(f"{GHL_BASE}/opportunities/pipelines",
                 params={"locationId": LOCATION_ID}, headers=headers, timeout=30)
pipelines = r.json().get("pipelines", []) if r.status_code == 200 else []
stage_map = {}
for pipe in pipelines:
    pname = pipe.get("name", "?")
    stages = pipe.get("stages", [])
    print(f"  Pipeline: '{pname}' ({len(stages)} stages)", flush=True)
    for s in stages:
        stage_map[s.get("id","")] = {"name": s.get("name","?"), "pipeline": pname}
        print(f"    Stage: '{s.get('name','?')}'", flush=True)

# --- Sample the first 200 open opportunities ---
print("\n=== SAMPLING OPEN OPPORTUNITIES (first 200) ===", flush=True)
two_yr_ms = int((now_utc - timedelta(days=730)).timestamp() * 1000)
params = {"location_id": LOCATION_ID, "startAfter": two_yr_ms,
          "startAfterId": "", "limit": 100}
r1 = requests.get(f"{GHL_BASE}/opportunities/search", params=params, headers=headers, timeout=30)
batch1 = r1.json().get("opportunities", []) if r1.status_code == 200 else []

# page 2
if batch1:
    last = batch1[-1]
    last_cat = last.get("createdAt","")
    last_ms = int(datetime.fromisoformat(last_cat.replace("Z","+00:00")).timestamp()*1000) if last_cat else two_yr_ms
    params2 = {"location_id": LOCATION_ID, "startAfter": last_ms,
               "startAfterId": last.get("id",""), "limit": 100}
    r2 = requests.get(f"{GHL_BASE}/opportunities/search", params=params2, headers=headers, timeout=30)
    batch2 = r2.json().get("opportunities", []) if r2.status_code == 200 else []
else:
    batch2 = []

all_sample = batch1 + batch2
print(f"Sampled {len(all_sample)} opportunities", flush=True)

# Breakdown by status
status_counts = defaultdict(int)
pipeline_counts = defaultdict(int)
value_buckets = {"$0": 0, "$1-$999": 0, "$1K-$49K": 0, "$50K+": 0}
age_buckets = {"<7 days": 0, "7-30 days": 0, "30-90 days": 0, "90-365 days": 0, "1yr+": 0}
has_name = 0
no_value = 0

for o in all_sample:
    status = (o.get("status") or "unknown").lower()
    status_counts[status] += 1
    
    sid = o.get("pipelineStageId","")
    sinfo = stage_map.get(sid, {"name":"Unknown Stage","pipeline":"Unknown Pipeline"})
    pipeline_counts[f"{sinfo['pipeline']} → {sinfo['name']}"] += 1
    
    val = float(o.get("monetaryValue") or 0)
    if val == 0: value_buckets["$0"] += 1; no_value += 1
    elif val < 1000: value_buckets["$1-$999"] += 1
    elif val < 50000: value_buckets["$1K-$49K"] += 1
    else: value_buckets["$50K+"] += 1
    
    cat = o.get("createdAt","")
    if cat:
        try:
            age = (now_utc - datetime.fromisoformat(cat.replace("Z","+00:00"))).days
            if age < 7: age_buckets["<7 days"] += 1
            elif age < 30: age_buckets["7-30 days"] += 1
            elif age < 90: age_buckets["30-90 days"] += 1
            elif age < 365: age_buckets["90-365 days"] += 1
            else: age_buckets["1yr+"] += 1
        except: pass
    
    name = o.get("name") or o.get("contactName") or ""
    if name: has_name += 1

print("\n-- Status breakdown --", flush=True)
for k, v in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}", flush=True)

print("\n-- Pipeline/Stage breakdown (top 15) --", flush=True)
for k, v in sorted(pipeline_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {v:3d}  {k}", flush=True)

print("\n-- Monetary value distribution --", flush=True)
for k, v in value_buckets.items():
    print(f"  {k}: {v}", flush=True)
print(f"  (no_value total: {no_value})", flush=True)

print("\n-- Age distribution --", flush=True)
for k, v in age_buckets.items():
    print(f"  {k}: {v}", flush=True)

# Show 10 sample records
print("\n-- 10 sample open opportunities --", flush=True)
open_sample = [o for o in all_sample if (o.get("status") or "").lower() not in ("won","lost")][:10]
for o in open_sample:
    sid = o.get("pipelineStageId","")
    sinfo = stage_map.get(sid, {"name":"?","pipeline":"?"})
    val = float(o.get("monetaryValue") or 0)
    cat = o.get("createdAt","") or ""
    age = ""
    if cat:
        try:
            age = f"{(now_utc - datetime.fromisoformat(cat.replace('Z','+00:00'))).days}d old"
        except: pass
    last = o.get("lastStatusChangeAt") or o.get("updatedAt") or ""
    last_age = ""
    if last:
        try:
            last_age = f"last touched {(now_utc - datetime.fromisoformat(last.replace('Z','+00:00'))).days}d ago"
        except: pass
    name = o.get("name") or o.get("contactName") or "(no name)"
    print(f"  '{name}' | {sinfo['pipeline']} → {sinfo['name']} | ${val:,.0f} | {age} | {last_age}", flush=True)

# --- Check contact dateAdded accuracy ---
print("\n=== CONTACT dateAdded ACCURACY CHECK ===", flush=True)
week_start = (datetime.now(PT) - timedelta(days=datetime.now(PT).weekday())).replace(
    hour=0, minute=0, second=0, microsecond=0)
week_start_ms = int(week_start.astimezone(timezone.utc).timestamp() * 1000)

params_c = {"locationId": LOCATION_ID, "startAfter": week_start_ms,
            "startAfterId": "", "limit": 100}
rc = requests.get(f"{GHL_BASE}/contacts", params=params_c, headers=headers, timeout=30)
contacts_batch = rc.json().get("contacts", []) if rc.status_code == 200 else []

print(f"First 100 contacts returned with startAfter=week_start_ms ({week_start.date()}):", flush=True)
date_dist = defaultdict(int)
for c in contacts_batch:
    da = c.get("dateAdded","")
    if da:
        try:
            d = datetime.fromisoformat(da.replace("Z","+00:00"))
            date_dist[d.strftime("%Y-%m-%d")] += 1
        except: pass
    else:
        date_dist["no-date"] += 1

for dt_str in sorted(date_dist.keys(), reverse=True)[:20]:
    print(f"  {dt_str}: {date_dist[dt_str]}", flush=True)

print("\nDone.", flush=True)
