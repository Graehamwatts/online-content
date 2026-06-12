# TEMPORARY: Friday Weekly Attribution Review data pull.
# This file temporarily replaces crm_diagnostic.py for one workflow_dispatch run
# (the GHL API is not reachable from the Cowork sandbox; only repo-scope PAT available,
# so we reuse this manual-dispatch workflow instead of creating a new one).
# The original crm_diagnostic.py is restored immediately after the run.
import requests, json, os, sys, time
from datetime import datetime, timedelta, timezone

GHL_PIT = os.environ["GHL_PIT"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
GHL_BASE = "https://services.leadconnectorhq.com"
headers = {
    "Authorization": f"Bearer {GHL_PIT}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
}

# Windows (computed in UTC; PT = UTC-7 in June/PDT)
# Current week: Mon 2026-06-08 00:00 PT -> Fri 2026-06-12 16:00 PT
# Prior week:   Mon 2026-06-01 00:00 PT -> Fri 2026-06-05 16:00 PT
PDT = timezone(timedelta(hours=-7))
cur_start = datetime(2026, 6, 8, 0, 0, tzinfo=PDT).astimezone(timezone.utc)
cur_end = datetime(2026, 6, 12, 16, 0, tzinfo=PDT).astimezone(timezone.utc)
pri_start = datetime(2026, 6, 1, 0, 0, tzinfo=PDT).astimezone(timezone.utc)
pri_end = datetime(2026, 6, 5, 16, 0, tzinfo=PDT).astimezone(timezone.utc)

ERRORS = []

def get_custom_fields():
    r = requests.get(f"{GHL_BASE}/locations/{LOCATION_ID}/customFields", headers=headers, timeout=30)
    if r.status_code != 200:
        ERRORS.append(f"customFields {r.status_code}: {r.text[:200]}")
        return {}
    return {f["id"]: f.get("name", "") for f in r.json().get("customFields", [])}

def get_pipelines():
    r = requests.get(f"{GHL_BASE}/opportunities/pipelines", params={"locationId": LOCATION_ID}, headers=headers, timeout=30)
    if r.status_code != 200:
        ERRORS.append(f"pipelines {r.status_code}: {r.text[:200]}")
        return []
    out = []
    for p in r.json().get("pipelines", []):
        out.append({"id": p.get("id"), "name": p.get("name"),
                    "stages": [{"id": s["id"], "name": s.get("name", ""), "pos": s.get("position")} for s in p.get("stages", [])]})
    return out

def slim_contact(c, cf_map):
    utm = {}
    for cf in (c.get("customFields") or []):
        fn = cf_map.get(cf.get("id", ""), "").lower()
        if "utm" in fn:
            utm[fn] = str(cf.get("value") or "")
    return {
        "id": c.get("id"),
        "dateAdded": c.get("dateAdded", ""),
        "firstName": c.get("firstName") or "",
        "lastInitial": (c.get("lastName") or "")[:1],
        "source": c.get("source") or "",
        "attributionSource": (c.get("attributionSource") or {}).get("sessionSource", "") if isinstance(c.get("attributionSource"), dict) else str(c.get("attributionSource") or ""),
        "contactSource": c.get("contactSource") or "",
        "tags": c.get("tags") or [],
        "utm": utm,
    }

def get_contacts(start_dt, end_dt, cf_map, label):
    contacts = []
    gte = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    lt = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    search_after = None
    cap_hit = True
    for page in range(1, 21):
        body = {"locationId": LOCATION_ID, "pageLimit": 100,
                "filters": [{"field": "dateAdded", "operator": "range", "value": {"gte": gte, "lt": lt}}],
                "sort": [{"field": "dateAdded", "direction": "desc"}]}
        if search_after:
            body["searchAfter"] = search_after
        r = requests.post(f"{GHL_BASE}/contacts/search", headers=headers, json=body, timeout=30)
        if r.status_code != 200:
            ERRORS.append(f"contacts/search [{label}] {r.status_code}: {r.text[:300]}")
            cap_hit = False
            break
        batch = r.json().get("contacts", [])
        if not batch:
            cap_hit = False
            break
        done = False
        for c in batch:
            da = c.get("dateAdded", "")
            try:
                cdt = datetime.fromisoformat(da.replace("Z", "+00:00"))
            except Exception:
                continue
            if cdt >= end_dt:
                continue
            if cdt < start_dt:
                done = True
                break
            contacts.append(slim_contact(c, cf_map))
        print(f"  [{label}] contacts page {page}: {len(batch)} fetched, {len(contacts)} in window", flush=True)
        if done or len(batch) < 100:
            cap_hit = False
            break
        search_after = batch[-1].get("searchAfter")
        if not search_after:
            cap_hit = False
            break
    if cap_hit:
        ERRORS.append(f"contacts [{label}] hit page cap — count untrustworthy")
    return contacts

def slim_opp(o):
    return {
        "id": o.get("id"),
        "name": o.get("name") or "",
        "createdAt": o.get("createdAt", ""),
        "updatedAt": o.get("updatedAt", ""),
        "lastStageChangeAt": o.get("lastStageChangeAt", "") or o.get("lastStatusChangeAt", ""),
        "status": o.get("status", ""),
        "pipelineId": o.get("pipelineId", ""),
        "pipelineStageId": o.get("pipelineStageId", ""),
        "monetaryValue": o.get("monetaryValue") or 0,
        "contactId": o.get("contactId") or (o.get("contact") or {}).get("id", ""),
    }

def get_opportunities(start_dt, end_dt, label):
    opps, start_after_id = [], None
    start_ms = int(start_dt.timestamp() * 1000)
    for page in range(10):
        params = {"location_id": LOCATION_ID, "startAfter": start_ms,
                  "startAfterId": start_after_id or "", "limit": 100}
        r = requests.get(f"{GHL_BASE}/opportunities/search", params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            ERRORS.append(f"opps/search [{label}] {r.status_code}: {r.text[:200]}")
            break
        batch = r.json().get("opportunities", [])
        past = False
        for o in batch:
            try:
                odt = datetime.fromisoformat(o.get("createdAt", "").replace("Z", "+00:00"))
            except Exception:
                continue
            if odt >= end_dt:
                past = True
                break
            if odt >= start_dt:
                opps.append(slim_opp(o))
        print(f"  [{label}] opps page {page+1}: {len(batch)} fetched, {len(opps)} in window", flush=True)
        if past or len(batch) < 100:
            break
        start_after_id = batch[-1].get("id") if batch else None
    return opps

def get_contact_by_id(cid, cf_map):
    r = requests.get(f"{GHL_BASE}/contacts/{cid}", headers=headers, timeout=30)
    if r.status_code != 200:
        return None
    return slim_contact(r.json().get("contact", {}), cf_map)

print("Pulling custom fields...", flush=True)
cf_map = get_custom_fields()
print(f"  {len(cf_map)} custom fields", flush=True)
print("Pulling pipelines...", flush=True)
pipelines = get_pipelines()

print("Pulling current-week data...", flush=True)
cur_contacts = get_contacts(cur_start, cur_end, cf_map, "cur")
cur_opps = get_opportunities(cur_start, cur_end, "cur")
print("Pulling prior-week data...", flush=True)
pri_contacts = get_contacts(pri_start, pri_end, cf_map, "pri")
pri_opps = get_opportunities(pri_start, pri_end, "pri")

# Resolve sources for opp contacts not already in the contact pulls (cap 60 lookups)
known = {c["id"] for c in cur_contacts} | {c["id"] for c in pri_contacts}
need = []
for o in cur_opps + pri_opps:
    if o["contactId"] and o["contactId"] not in known and o["contactId"] not in [n for n in need]:
        need.append(o["contactId"])
extra_contacts = {}
for cid in need[:60]:
    sc = get_contact_by_id(cid, cf_map)
    if sc:
        extra_contacts[cid] = sc
    time.sleep(0.15)
print(f"Resolved {len(extra_contacts)} extra opp contacts", flush=True)

payload = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "windows": {
        "cur": [cur_start.isoformat(), cur_end.isoformat()],
        "pri": [pri_start.isoformat(), pri_end.isoformat()],
    },
    "pipelines": pipelines,
    "cur": {"contacts": cur_contacts, "opps": cur_opps},
    "pri": {"contacts": pri_contacts, "opps": pri_opps},
    "extra_contacts": extra_contacts,
    "errors": ERRORS,
}
print("===ATTRIB_JSON_START===", flush=True)
print(json.dumps(payload, separators=(",", ":")), flush=True)
print("===ATTRIB_JSON_END===", flush=True)
