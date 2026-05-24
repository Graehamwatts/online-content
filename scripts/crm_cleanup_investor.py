#!/usr/bin/env python3
"""
crm_cleanup_investor.py
-----------------------
One-shot cleanup: deletes all opportunities in the "Investor/Flipper" pipeline.
Does NOT touch contacts — only the pipeline opportunity record is deleted.

Env:  GHL_PIT, GHL_LOCATION_ID
      DRY_RUN=true  (default true — must explicitly set false to delete)
"""
import requests, os, sys, time
from datetime import datetime

GHL_PIT     = os.environ["GHL_PIT"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
GHL_BASE    = "https://services.leadconnectorhq.com"
GHL_VERSION = "2021-07-28"
DRY_RUN     = os.environ.get("DRY_RUN", "true").lower() != "false"

TARGET_PIPELINE_NAME = "Investor/Flipper"

headers = {
    "Authorization": f"Bearer {GHL_PIT}",
    "Version":       GHL_VERSION,
    "Content-Type":  "application/json",
}


def get_pipelines():
    r = requests.get(
        f"{GHL_BASE}/opportunities/pipelines",
        params={"locationId": LOCATION_ID},
        headers=headers, timeout=30,
    )
    r.raise_for_status()
    return r.json().get("pipelines", [])


def get_opps_in_pipeline(pipeline_id):
    opps = []
    start_after_ms = 0
    start_after_id = ""
    page = 0
    while True:
        page += 1
        params = {
            "location_id": LOCATION_ID,
            "pipeline_id": pipeline_id,
            "limit":       100,
        }
        if start_after_id:
            params["startAfter"]    = start_after_ms
            params["startAfterId"] = start_after_id
        r = requests.get(
            f"{GHL_BASE}/opportunities/search",
            params=params, headers=headers, timeout=30,
        )
        r.raise_for_status()
        batch = r.json().get("opportunities", [])
        if not batch:
            print(f"  Page {page}: done ({len(opps)} total)", flush=True)
            break
        opps.extend(batch)
        print(f"  Page {page}: +{len(batch)} = {len(opps)} total", flush=True)
        if len(batch) < 100:
            break
        last = batch[-1]
        cat  = last.get("createdAt", "")
        if cat:
            try:
                start_after_ms = int(
                    datetime.fromisoformat(cat.replace("Z", "+00:00")).timestamp() * 1000
                )
            except Exception:
                break
        start_after_id = last.get("id", "")
    return opps


def delete_opp(opp_id):
    r = requests.delete(
        f"{GHL_BASE}/opportunities/{opp_id}",
        headers=headers, timeout=30,
    )
    return r.status_code


# ─── Main ──────────────────────────────────────────────────────────────────

print(f"{'DRY RUN — no deletions' if DRY_RUN else 'LIVE RUN — WILL DELETE'}", flush=True)
print(f"Target pipeline: '{TARGET_PIPELINE_NAME}'", flush=True)

print("\nFetching pipelines...", flush=True)
pipelines       = get_pipelines()
target_pipeline = None
for p in pipelines:
    print(f"  {p.get('name')} ({p.get('id')})", flush=True)
    if p.get("name", "").strip().lower() == TARGET_PIPELINE_NAME.lower():
        target_pipeline = p

if not target_pipeline:
    print(f"\nERROR: Pipeline '{TARGET_PIPELINE_NAME}' not found!", flush=True)
    print(f"Available pipelines: {[p.get('name') for p in pipelines]}", flush=True)
    sys.exit(1)

pipeline_id = target_pipeline["id"]
print(f"\nFetching opportunities in '{target_pipeline['name']}'...", flush=True)
opps = get_opps_in_pipeline(pipeline_id)
print(f"\n{len(opps)} opportunities found.", flush=True)

if not opps:
    print("Nothing to delete. Exiting cleanly.", flush=True)
    sys.exit(0)

if DRY_RUN:
    print("\n=== DRY RUN PREVIEW (no changes made) ===", flush=True)
    show = opps[:15]
    for o in show:
        contact = (o.get("contact") or {})
        cname   = contact.get("name") or o.get("name") or "Unnamed"
        print(f"  Would delete opp {o['id']}  contact: {cname}", flush=True)
    if len(opps) > 15:
        print(f"  ... and {len(opps) - 15} more", flush=True)
    print(f"\nTo actually delete, re-run the workflow with dry_run = false.", flush=True)
    sys.exit(0)

# Live deletion
print(f"\nDeleting {len(opps)} opportunities (contacts preserved)...", flush=True)
deleted, failed = 0, 0
for i, o in enumerate(opps):
    opp_id = o.get("id", "")
    if not opp_id:
        continue
    code = delete_opp(opp_id)
    if code in (200, 204):
        deleted += 1
    else:
        failed += 1
        print(f"  FAILED {opp_id}: HTTP {code}", flush=True)
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{len(opps)} — {deleted} deleted, {failed} failed", flush=True)
        time.sleep(0.3)   # stay within GHL rate limits

print(f"\n=== DONE: {deleted} deleted, {failed} failed ===", flush=True)
if failed:
    sys.exit(1)
