#!/usr/bin/env python3
"""
restore_investor_pipeline.py
Finds contacts created Oct2025–Feb2026 with no current open opportunity
and re-adds them to the Investor/Flipper pipeline.
Env: GHL_PIT, GHL_LOCATION_ID, DRY_RUN (default true)
"""
import requests, json, time, sys, os
from datetime import datetime, timezone

GHL_PIT              = os.environ["GHL_PIT"]
LOCATION_ID          = os.environ["GHL_LOCATION_ID"]
GHL_BASE             = "https://services.leadconnectorhq.com"
INVESTOR_PIPELINE_ID = "rUTHO8xdJSctaCdMRnwR"
INVESTOR_STAGE_ID    = "aaa5d136-a2df-4b75-91f1-266a76f2dfe5"
DRY_RUN              = os.environ.get("DRY_RUN", "true").lower() != "false"

headers = {
    "Authorization": f"Bearer {GHL_PIT}",
    "Version":       "2021-07-28",
    "Content-Type":  "application/json",
}

print(f"{'DRY RUN — no changes' if DRY_RUN else 'LIVE — will create opportunities'}", flush=True)

# ── Step 1: collect contact IDs that already have an open opp ───────────────
print("\nStep 1: collecting contacts with active opportunities...", flush=True)
active_contact_ids = set()
start_after_ms, start_after_id, page = 0, "", 0
while True:
    page += 1
    params = {"location_id": LOCATION_ID, "limit": 100}
    if start_after_id:
        params.update({"startAfter": start_after_ms, "startAfterId": start_after_id})
    r = requests.get(f"{GHL_BASE}/opportunities/search",
                     params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"  opp error {r.status_code}", flush=True)
        break
    batch = r.json().get("opportunities", [])
    if not batch:
        break
    for o in batch:
        cid = (o.get("contact") or {}).get("id") or o.get("contactId", "")
        if cid:
            active_contact_ids.add(cid)
    if len(batch) < 100:
        break
    last = batch[-1]
    try:
        start_after_ms = int(
            datetime.fromisoformat(last["createdAt"].replace("Z", "+00:00")).timestamp() * 1000
        )
    except Exception:
        break
    start_after_id = last.get("id", "")
    if page % 10 == 0:
        print(f"  opp page {page}: {len(active_contact_ids)} contacts with opps", flush=True)

print(f"Contacts with existing opps: {len(active_contact_ids)}", flush=True)

# ── Step 2: scan all contacts, find orphaned ones in the import window ───────
print("\nStep 2: scanning contacts for orphaned entries (Oct 2025 – Feb 2026)...", flush=True)
orphaned = []
page, start_after_id = 0, ""
while True:
    page += 1
    params = {"locationId": LOCATION_ID, "limit": 100}
    if start_after_id:
        params["startAfterId"] = start_after_id
    r = requests.get(f"{GHL_BASE}/contacts/",
                     params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"  contacts error {r.status_code}: {r.text[:200]}", flush=True)
        break
    batch = r.json().get("contacts", [])
    if not batch:
        break
    for c in batch:
        created = (c.get("dateAdded") or "")[:7]   # "YYYY-MM"
        if "2025-10" <= created <= "2026-02" and c["id"] not in active_contact_ids:
            orphaned.append({
                "id":      c["id"],
                "name":    (
                    c.get("contactName") or
                    f"{c.get('firstName','').strip()} {c.get('lastName','').strip()}"
                ).strip(),
                "created": (c.get("dateAdded") or "")[:10],
            })
    if len(batch) < 100:
        break
    start_after_id = batch[-1]["id"]
    if page % 10 == 0:
        print(f"  contact page {page}: {len(orphaned)} orphaned so far", flush=True)
    time.sleep(0.05)

print(f"\nOrphaned contacts in import window: {len(orphaned)}", flush=True)
for c in orphaned[:15]:
    print(f"  {c['name']:<35} {c['created']}", flush=True)
if len(orphaned) > 15:
    print(f"  ... and {len(orphaned)-15} more", flush=True)

if not orphaned:
    print("Nothing to restore. Exiting.", flush=True)
    sys.exit(0)

if DRY_RUN:
    print(f"\nDRY RUN complete: would re-add {len(orphaned)} contacts to Investor/Flipper.", flush=True)
    sys.exit(0)

# ── Step 3: create opportunity for each orphaned contact ─────────────────────
print(f"\nStep 3: creating {len(orphaned)} Investor/Flipper opportunities...", flush=True)
created_count, failed = 0, 0
for i, c in enumerate(orphaned):
    payload = {
        "title":           c["name"],
        "pipelineId":      INVESTOR_PIPELINE_ID,
        "pipelineStageId": INVESTOR_STAGE_ID,
        "contactId":       c["id"],
        "locationId":      LOCATION_ID,
        "status":          "open",
    }
    r = requests.post(f"{GHL_BASE}/opportunities/",
                      json=payload, headers=headers, timeout=15)
    if r.status_code in (200, 201):
        created_count += 1
    else:
        failed += 1
        if failed <= 5:
            print(f"  FAIL {c['name']}: HTTP {r.status_code} {r.text[:80]}", flush=True)
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{len(orphaned)}: {created_count} created, {failed} failed", flush=True)
        time.sleep(0.3)

print(f"\nDone: {created_count} restored, {failed} failed", flush=True)
if failed:
    sys.exit(1)
