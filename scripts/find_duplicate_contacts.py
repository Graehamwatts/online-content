#!/usr/bin/env python3
"""
Find duplicate contacts in GHL by matching email and phone number.
"""
import requests, json, time, sys, os
from collections import defaultdict

GHL_PIT     = os.environ["GHL_PIT"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
GHL_BASE    = "https://services.leadconnectorhq.com"
headers = {"Authorization": f"Bearer {GHL_PIT}", "Version": "2021-07-28"}

email_map = defaultdict(list)
phone_map = defaultdict(list)

def extract_phones(c):
    raw = c.get("phone")
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        result = []
        for p in raw:
            if isinstance(p, str):
                result.append(p)
            elif isinstance(p, dict):
                n = p.get("number") or p.get("value","")
                if n: result.append(n)
        return result
    return []

page, start_after_id, total = 0, "", 0
print("Scanning contacts...", flush=True)

while True:
    page += 1
    params = {"locationId": LOCATION_ID, "limit": 100}
    if start_after_id:
        params["startAfterId"] = start_after_id
    r = requests.get(f"{GHL_BASE}/contacts/", params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text[:200]}")
        break
    batch = r.json().get("contacts", [])
    if not batch:
        break
    total += len(batch)
    for c in batch:
        name    = (c.get("contactName") or f"{c.get('firstName','')} {c.get('lastName','')}").strip()
        cid     = c["id"]
        email   = (c.get("email") or "").strip().lower()
        phones  = extract_phones(c)
        created = (c.get("dateAdded") or "")[:10]
        info = {"id": cid, "name": name, "created": created, "email": email}
        if email:
            email_map[email].append(info)
        for ph in phones:
            norm = "".join(d for d in ph if d.isdigit())
            if len(norm) >= 10:
                phone_map[norm[-10:]].append(info)
    if len(batch) < 100:
        break
    start_after_id = batch[-1]["id"]
    if page % 10 == 0:
        print(f"  page {page}: {total} contacts scanned", flush=True)
    time.sleep(0.05)

print(f"\nTotal contacts scanned: {total}", flush=True)

email_dupes = {e: cs for e, cs in email_map.items() if len(cs) > 1 and e}
phone_dupes = {p: cs for p, cs in phone_map.items() if len(cs) > 1}

print(f"\n=== EMAIL DUPLICATES: {len(email_dupes)} shared emails ===")
for email, contacts in sorted(email_dupes.items(), key=lambda x: -len(x[1]))[:30]:
    print(f"\n  Email: {email}  ({len(contacts)} contacts)")
    for c in contacts:
        print(f"    {c['id']:<25} {c['name']:<35} added:{c['created']}")

print(f"\n=== PHONE DUPLICATES: {len(phone_dupes)} shared phones ===")
for phone, contacts in sorted(phone_dupes.items(), key=lambda x: -len(x[1]))[:30]:
    print(f"\n  Phone: ...{phone}  ({len(contacts)} contacts)")
    for c in contacts:
        print(f"    {c['id']:<25} {c['name']:<35} added:{c['created']} email:{c['email']}")

print(f"\nSummary: {len(email_dupes)} duplicate email groups, {len(phone_dupes)} duplicate phone groups")
