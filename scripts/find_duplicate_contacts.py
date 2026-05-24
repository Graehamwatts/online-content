#!/usr/bin/env python3
"""
find_duplicate_contacts.py — uses page-number pagination, no cursor loops
"""
import requests, json, time, sys, os
from collections import defaultdict

GHL_PIT     = os.environ["GHL_PIT"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
GHL_BASE    = "https://services.leadconnectorhq.com"
headers     = {"Authorization": f"Bearer {GHL_PIT}", "Version": "2021-07-28"}

email_map = defaultdict(list)
phone_map = defaultdict(list)
seen_ids  = set()
total     = 0
MAX_PAGES = 300

def extract_phones(c):
    raw = c.get("phone")
    if not raw: return []
    if isinstance(raw, str): return [raw]
    if isinstance(raw, list):
        out = []
        for p in raw:
            if isinstance(p, str): out.append(p)
            elif isinstance(p, dict):
                n = p.get("number") or p.get("value","")
                if n: out.append(n)
        return out
    return []

print("Scanning contacts for duplicates...", flush=True)

for page_num in range(1, MAX_PAGES + 1):
    params = {"locationId": LOCATION_ID, "limit": 100, "page": page_num}
    r = requests.get(f"{GHL_BASE}/contacts/", params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text[:200]}", flush=True)
        break
    batch = r.json().get("contacts", [])
    if not batch:
        break

    new_this_page = 0
    for c in batch:
        cid = c["id"]
        if cid in seen_ids: continue
        seen_ids.add(cid)
        new_this_page += 1
        total += 1

        name    = (c.get("contactName") or f"{c.get('firstName','')} {c.get('lastName','')}").strip()
        email   = (c.get("email") or "").strip().lower()
        phones  = extract_phones(c)
        created = (c.get("dateAdded") or "")[:10]
        info    = {"id": cid, "name": name, "created": created, "email": email}

        if email:
            email_map[email].append(info)
        for ph in phones:
            norm = "".join(d for d in ph if d.isdigit())
            if len(norm) >= 10:
                phone_map[norm[-10:]].append(info)

    if page_num % 5 == 0:
        print(f"  page {page_num}: {total} contacts scanned", flush=True)

    if new_this_page == 0 or len(batch) < 100:
        break
    time.sleep(0.1)

print(f"\nTotal contacts scanned: {total}", flush=True)

email_dupes = {e: cs for e, cs in email_map.items() if len(cs) > 1 and e}
phone_dupes = {p: cs for p, cs in phone_map.items() if len(cs) > 1}

print(f"\n=== EMAIL DUPLICATES: {len(email_dupes)} groups ===")
for email, contacts in sorted(email_dupes.items(), key=lambda x: -len(x[1]))[:30]:
    print(f"\n  {email}  ({len(contacts)} contacts)")
    for c in contacts:
        print(f"    {c['id']:<25} {c['name']:<35} added:{c['created']}")

print(f"\n=== PHONE DUPLICATES: {len(phone_dupes)} groups ===")
for phone, contacts in sorted(phone_dupes.items(), key=lambda x: -len(x[1]))[:30]:
    print(f"\n  ...{phone}  ({len(contacts)} contacts)")
    for c in contacts:
        print(f"    {c['id']:<25} {c['name']:<35} added:{c['created']} | {c['email']}")

print(f"\nSummary: {len(email_dupes)} duplicate email groups, {len(phone_dupes)} duplicate phone groups", flush=True)
