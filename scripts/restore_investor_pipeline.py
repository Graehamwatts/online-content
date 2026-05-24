#!/usr/bin/env python3
"""
restore_investor_pipeline.py — v3
Finds contacts added Oct 2025–Feb 2026 (bulk import window) with no current
open opp, and re-adds them to the Investor/Flipper pipeline.
Uses page-number pagination with a hard 300-page safety cap.
"""
import requests, json, time, sys, os

GHL_PIT              = os.environ["GHL_PIT"]
LOCATION_ID          = os.environ["GHL_LOCATION_ID"]
GHL_BASE             = "https://services.leadconnectorhq.com"
INVESTOR_PIPELINE_ID = "rUTHO8xdJSctaCdMRnwR"
INVESTOR_STAGE_ID    = "aaa5d136-a2df-4b75-91f1-266a76f2dfe5"
DRY_RUN              = os.environ.get("DRY_RUN", "true").lower() != "false"
MAX_PAGES            = 300

# Only target contacts from the bulk investor import window
DATE_FROM = "2025-10"   # YYYY-MM inclusive
DATE_TO   = "2026-02"   # YYYY-MM inclusive

headers = {
    "Authorization": f"Bearer {GHL_PIT}",
    "Version":       "2021-07-28",
    "Content-Type":  "application/json",
}

print(f"{'DRY RUN — no changes' if DRY_RUN else 'LIVE — will create opportunities'}", flush=True)
print(f"Targeting contacts added {DATE_FROM} – {DATE_TO}", flush=True)

# ── Step 1: collect all contact IDs that currently have ANY opp ──────────────
print("\nStep 1: collecting contacts with existing opportunities...", flush=True)
active_contact_ids = set()
page = 0
start_after_id = ""
start_after_ms = 0

while page < MAX_PAGES:
    page += 1
    params = {"location_id": LOCATION_ID, "limit": 100}
    if start_after_id:
        params["startAfter"]   = start_after_ms
        params["startAfterId"] = start_after_id

    r = requests.get(f"{GHL_BASE}/opportunities/search",
                     params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"  opp error {r.status_code}: {r.text[:200]}", flush=True)
        break

    data  = r.json()
    batch = data.get("opportunities", [])
    if not batch:
        break

    for o in batch:
        cid = (o.get("contact") or {}).get("id") or o.get("contactId", "")
        if cid:
            active_contact_ids.add(cid)

    if page % 5 == 0:
        print(f"  opp page {page}: {len(active_contact_ids)} contacts with opps", flush=True)

    meta               = data.get("meta", {})
    start_after_id_new = meta.get("startAfterId", "")
    if start_after_id_new:
        start_after_ms = meta.get("startAfter", 0) or 0
        start_after_id = start_after_id_new
    elif len(batch) == 100:
        from datetime import datetime
        last = batch[-1]
        try:
            start_after_ms = int(
                datetime.fromisoformat(
                    last["createdAt"].replace("Z", "+00:00")
                ).timestamp() * 1000
            )
            new_id = last.get("id", "")
            if new_id == start_after_id:
                print("  cursor stalled — stopping opp pagination", flush=True)
                break
            start_after_id = new_id
        except Exception as e:
            print(f"  cursor error: {e} — stopping", flush=True)
            break
    else:
        break

    time.sleep(0.1)

print(f"Contacts with existing opps: {len(active_contact_ids)}", flush=True)

# ── Step 2: scan contacts, find orphaned ones in the import window ───────────
print(f"\nStep 2: scanning contacts added {DATE_FROM}–{DATE_TO} with no opp...", flush=True)
orphaned  = []
seen_ids  = set()

for page_num in range(1, MAX_PAGES + 1):
    params = {"locationId": LOCATION_ID, "limit": 100, "page": page_num}
    r = requests.get(f"{GHL_BASE}/contacts/", params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"  contacts error {r.status_code}: {r.text[:200]}", flush=True)
        break

    batch = r.json().get("contacts", [])
    if not batch:
        break

    new_this_page = 0
    for c in batch:
        cid = c["id"]
        if cid in seen_ids:
            continue
        seen_ids.add(cid)
        new_this_page += 1

        created_month = (c.get("dateAdded") or "")[:7]   # "YYYY-MM"
        if not (DATE_FROM <= created_month <= DATE_TO):
            continue   # outside import window — skip

        if cid not in active_contact_ids:
            name = (
                c.get("contactName") or
                f"{c.get('firstName','').strip()} {c.get('lastName','').strip()}"
            ).strip()
            orphaned.append({
                "id":      cid,
                "name":    name or "No Name",
                "created": (c.get("dateAdded") or "")[:10],
            })

    if page_num % 5 == 0:
        print(f"  contact page {page_num}: {len(seen_ids)} scanned, {len(orphaned)} in window with no opp", flush=True)

    if new_this_page == 0 or len(batch) < 100:
        break
    time.sleep(0.1)

print(f"\nTotal contacts scanned: {len(seen_ids)}", flush=True)
print(f"Contacts in import window with no opp: {len(orphaned)}", flush=True)
for c in orphaned[:20]:
    print(f"  {c['name']:<35} added:{c['created']}", flush=True)
if len(orphaned) > 20:
    print(f"  ... and {len(orphaned)-20} more", flush=True)

if not orphaned:
    print("\nNothing to restore. Exiting.", flush=True)
    sys.exit(0)

if DRY_RUN:
    print(f"\nDRY RUN complete — would restore {len(orphaned)} contacts to Investor/Flipper.", flush=True)
    sys.exit(0)

# ── Step 3: create opp for each orphaned contact ─────────────────────────────
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
