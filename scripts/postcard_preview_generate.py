#!/usr/bin/env python3
"""
Phase 2 — server-side GENERATION of farming-postcard hook options (per Fugu blueprint).

The GitHub Action calls this on the 8th/24th. It builds the 4-axis differentiation
constraints from the vendored history, asks Sakana/Fugu for candidate options (enum IDs
only, NO invented URLs), then PYTHON validates every candidate against the rules +
compliance. It tops up from the deterministic template bank if the LLM gives too few,
constructs the CTA URL/SMS server-side, emails the options, writes a durable artifact
before email and a sent-marker only after SMTP success.

Degrades gracefully:
  - no SAKANA key            -> template-only generation (still produces valid options)
  - Sakana error/bad JSON    -> one repair attempt, then template top-up
  - <3 valid after top-up    -> falls back to the deterministic REMINDER (handled by the
                                reminder script); here we exit nonzero so the workflow alerts.

Env: SAKANA_API_KEY (prod) | local key file fallback for testing.
     SAKANA_BASE_URL (default https://api.sakana.ai/v1), SAKANA_MODEL (default 'fugu').
     GMAIL_USERNAME, GMAIL_APP_PASSWORD, POSTCARD_RECIPIENTS.
     MODE=generate (default) | scheduled ; DRY_RUN=1 ; FORCE_TARGET=YYYY-MM-DD ;
     GITHUB_RUN_URL.
"""
import os, sys, json, ssl, smtplib, datetime, urllib.request, urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "farming-postcards")
ARCHIVE_URL = "https://graehamwatts.github.io/online-content/farming-postcards/"
BLOCKING_STATUS = {"shipped", "print_ready", "queued"}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def la_today():
    forced = os.environ.get("FORCE_TARGET", "").strip()
    if forced:
        # In tests we still want "today" derived; use the preview day implied by the drop.
        d = datetime.date.fromisoformat(forced)
        return d - datetime.timedelta(days=7)
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).date()
    except Exception:
        return (datetime.datetime.utcnow() - datetime.timedelta(hours=7)).date()


def drop_for_preview(today):
    forced = os.environ.get("FORCE_TARGET", "").strip()
    if forced:
        return datetime.date.fromisoformat(forced)
    if today.day <= 15:
        return today.replace(day=15)
    nxt = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return nxt


def build_constraints(history):
    cards = [c for c in history["cards"] if c.get("status") in BLOCKING_STATUS and c.get("drop_date")]
    cards.sort(key=lambda c: c["drop_date"], reverse=True)
    last3, last2, last4 = cards[:3], cards[:2], cards[:4]
    return {
        "blocked_archetypes": sorted({c["archetype"] for c in last3}),
        "blocked_cta_destination_ids": sorted({c["cta_destination_id"] for c in last2}),
        "zillow_algorithm_villain_blocked": any(c.get("villain_type") == "zillow_algorithm" for c in last2),
        "blocked_core_claim_slugs": sorted({c["core_claim_slug"] for c in last4}),
    }


def feasibility(libs, cons):
    arch = {a["id"] for a in libs["archetypes"]} - set(cons["blocked_archetypes"])
    claims = {c["id"] for c in libs["core_claims"]} - set(cons["blocked_core_claim_slugs"])
    ctas = {c["id"] for c in libs["cta_destinations"] if c.get("allowed")} - set(cons["blocked_cta_destination_ids"])
    problems = []
    if len(arch) < 3: problems.append("fewer than 3 available archetypes")
    if len(claims) < 3: problems.append("fewer than 3 available core claims")
    if len(ctas) < 1: problems.append("no available CTA destination")
    return arch, claims, ctas, problems


def resolve_key():
    k = os.environ.get("SAKANA_API_KEY", "").strip()
    if k:
        return k
    # local-testing fallback only (never committed; lives outside the repos)
    for p in [r"C:\Users\Graeham Watts\Documents\Claude\fugu\sakana-api-key.txt"]:
        if os.path.exists(p):
            v = open(p, encoding="utf-8").read().strip()
            if v and "PASTE_YOUR" not in v:
                return v
    return None


def sakana_chat(prompt, model, timeout=180):
    key = resolve_key()
    if not key:
        return None
    base = os.environ.get("SAKANA_BASE_URL", "https://api.sakana.ai/v1")
    body = {"model": model, "messages": [
        {"role": "system", "content": "You are a direct-response real-estate copywriter. Return STRICT JSON only, no markdown."},
        {"role": "user", "content": prompt}]}
    req = urllib.request.Request(base + "/chat/completions",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  sakana call failed: {e}", flush=True)
        return None


def extract_json(text):
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):] if "{" in t else t
    try:
        return json.loads(t)
    except Exception:
        a, b = t.find("{"), t.rfind("}")
        if a >= 0 and b > a:
            try:
                return json.loads(t[a:b + 1])
            except Exception:
                return None
    return None


def gen_prompt(drop, slot, libs, cons, arch_avail, claim_avail, cta_avail):
    return f"""Generate 7 candidate hook options for a real-estate farming postcard.
Agent: Graeham Watts, REALTOR, East Palo Alto / Peninsula. Drop date: {drop} ({slot} slot).

Choose ONLY from these allowed enum IDs (do NOT invent values, do NOT write URLs):
- archetype (allowed): {sorted(arch_avail)}
- core_claim_slug (allowed): {sorted(claim_avail)}
- cta_destination_id (allowed): {sorted(cta_avail)}
- villain_type: ["none","zillow_algorithm","old_marketing"]

HARD RULES (any violation = discarded):
- archetype must NOT be in {cons['blocked_archetypes']}
- cta_destination_id must NOT be in {cons['blocked_cta_destination_ids']}
- core_claim_slug must NOT be in {cons['blocked_core_claim_slugs']}
- {"Zillow/algorithm villain is BLOCKED this round — villain_type must be 'none' or 'old_marketing' and copy must not mention Zillow/Zestimate/algorithm/AVM/estimate." if cons['zillow_algorithm_villain_blocked'] else "Zillow/algorithm villain is allowed this round."}
- No guaranteed sale, guaranteed buyer, or guaranteed price.
- Each candidate must have a distinct archetype AND distinct core_claim_slug from the others.

Return STRICT JSON: {{"candidates":[{{"archetype","core_claim_slug","villain_type","cta_destination_id","headline","subheadline","hook_summary","back_outline":["..."]}}]}}
Headlines: punchy, <= 9 words, glance-readable. Any option breaking a rule will be discarded, so comply exactly."""


def text_has_banned(opt, terms):
    blob = " ".join([opt.get("headline", ""), opt.get("subheadline", ""), opt.get("hook_summary", ""),
                     " ".join(opt.get("back_outline", []) or [])]).lower()
    return any(t in blob for t in terms)


def validate(opt, cons, libs):
    arch_ids = {a["id"] for a in libs["archetypes"]}
    claim_ids = {c["id"] for c in libs["core_claims"]}
    cta_ids = {c["id"] for c in libs["cta_destinations"] if c.get("allowed")}
    r = []
    if opt.get("archetype") not in arch_ids: r.append("bad archetype")
    if opt.get("archetype") in cons["blocked_archetypes"]: r.append("archetype on cooldown")
    if opt.get("core_claim_slug") not in claim_ids: r.append("bad claim")
    if opt.get("core_claim_slug") in cons["blocked_core_claim_slugs"]: r.append("claim on cooldown")
    if opt.get("cta_destination_id") not in cta_ids: r.append("bad cta")
    if opt.get("cta_destination_id") in cons["blocked_cta_destination_ids"]: r.append("cta on cooldown")
    if opt.get("villain_type") not in libs["villain_types"]: r.append("bad villain")
    if cons["zillow_algorithm_villain_blocked"]:
        if opt.get("villain_type") == "zillow_algorithm": r.append("villain cooldown")
        if text_has_banned(opt, libs["banned_villain_terms"]): r.append("banned villain term in copy")
    if not (opt.get("headline") or "").strip(): r.append("empty headline")
    if text_has_banned(opt, libs["compliance_bans"]): r.append("compliance: guarantee language")
    return r


def select(candidates, cons, libs, want=4):
    valid, seen_arch, seen_claim = [], set(), set()
    for o in candidates:
        if validate(o, cons, libs):
            continue
        if o["archetype"] in seen_arch or o["core_claim_slug"] in seen_claim:
            continue
        valid.append(o); seen_arch.add(o["archetype"]); seen_claim.add(o["core_claim_slug"])
        if len(valid) >= want:
            break
    return valid


def template_topup(have, cons, libs, want=3):
    bank = load("template_bank.json")["templates"]
    seen_arch = {o["archetype"] for o in have}
    seen_claim = {o["core_claim_slug"] for o in have}
    cta_avail = [c for c in libs["cta_destinations"] if c.get("allowed") and c["id"] not in cons["blocked_cta_destination_ids"]]
    out = list(have)
    for t in bank:
        if len(out) >= want:
            break
        if t["archetype"] in cons["blocked_archetypes"] or t["archetype"] in seen_arch:
            continue
        if t["core_claim_slug"] in cons["blocked_core_claim_slugs"] or t["core_claim_slug"] in seen_claim:
            continue
        cta = cta_avail[0]["id"] if cta_avail else "sms_keyword"
        o = {"archetype": t["archetype"], "core_claim_slug": t["core_claim_slug"],
             "villain_type": t.get("villain_type", "none"), "cta_destination_id": cta,
             "headline": t["headline"], "subheadline": t.get("subheadline", ""),
             "hook_summary": "Deterministic template fallback.", "back_outline": t.get("back_outline", []),
             "source": "template"}
        if not validate(o, cons, libs):
            out.append(o); seen_arch.add(o["archetype"]); seen_claim.add(o["core_claim_slug"])
    return out


def cta_render(dest_id, libs, drop, letter):
    dest = next((c for c in libs["cta_destinations"] if c["id"] == dest_id), None)
    if not dest:
        return {"type": "sms", "value": f"SMSTO:{libs['phone']}:GRAEHAM", "label": "Call or text Graeham"}
    if dest.get("canonical_url"):
        url = (f"{dest['canonical_url']}?utm_source=postcard&utm_medium=qr&utm_campaign={drop}"
               f"&utm_content={letter}&drop_date={drop}&cta_destination_id={dest_id}&qr_id={drop}-{letter}")
        return {"type": "url", "value": url, "label": dest["label"]}
    kw = dest.get("sms_keyword", "GRAEHAM")
    return {"type": "sms", "value": f"SMSTO:{libs['phone']}:{kw}", "label": f'Text "{kw}" to {libs["phone"]}'}


def main():
    today = la_today()
    drop = drop_for_preview(today)
    drop_s = drop.isoformat()
    slot = "1st-of-month" if drop.day == 1 else "15th-of-month"
    sent_marker = os.path.join(DATA, "sent", f"{drop_s}.json")
    dry = os.environ.get("DRY_RUN") == "1"

    if os.path.exists(sent_marker) and not dry:
        print(f"sent marker exists for {drop_s} — idempotent skip."); return

    libs = load("libraries.json")
    history = load("history.json")
    cons = build_constraints(history)
    arch_avail, claim_avail, cta_avail, problems = feasibility(libs, cons)
    print(f"drop={drop_s} slot={slot}", flush=True)
    print(f"constraints={json.dumps(cons)}", flush=True)
    if problems:
        print(f"::error::infeasible constraints: {problems}"); sys.exit(1)

    model = os.environ.get("SAKANA_MODEL", "fugu")
    prompt = gen_prompt(drop_s, slot, libs, cons, arch_avail, claim_avail, cta_avail)
    raw = sakana_chat(prompt, model)
    parsed = extract_json(raw)
    candidates = (parsed or {}).get("candidates", []) if isinstance(parsed, dict) else []
    print(f"sakana returned {len(candidates)} raw candidates (model={model}, key={'yes' if resolve_key() else 'NO'})", flush=True)

    chosen = select(candidates, cons, libs, want=5)
    print(f"{len(chosen)} valid after LLM validation", flush=True)
    if len(chosen) < 3:
        chosen = template_topup(chosen, cons, libs, want=3)
        print(f"{len(chosen)} after template top-up", flush=True)
    if len(chosen) < 3:
        print("::error::could not assemble 3 valid options — falling back to reminder"); sys.exit(1)

    # attach CTA + letter
    for i, o in enumerate(chosen):
        letter = chr(ord("A") + i)
        o["id"] = f"{drop_s}-{letter}"
        o["cta"] = cta_render(o["cta_destination_id"], libs, drop_s, letter)
        o.setdefault("source", "llm")

    artifact = {"schema_version": "postcard_preview_options.v1", "drop_date": drop_s, "slot": slot,
                "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
                "generator": {"provider": "sakana_fugu", "model": model, "had_key": bool(resolve_key())},
                "constraints": cons, "options": chosen}

    if dry:
        print(json.dumps(artifact, indent=2)[:4000]); print("...[DRY RUN — no email, no commit]"); return

    # write artifact BEFORE email
    os.makedirs(os.path.join(DATA, "previews", drop_s), exist_ok=True)
    with open(os.path.join(DATA, "previews", drop_s, "options.json"), "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    # email
    subject = f"\U0001F4EC Postcard options ready — {slot} drop ({drop_s})"
    rows = ""
    for o in chosen:
        rows += (f"<div style='border-left:4px solid #C2A14E;background:#FBF7EC;padding:12px 16px;margin:10px 0;border-radius:4px'>"
                 f"<b>{o['id']}</b> — <b>{o['archetype']}</b><br>"
                 f"<span style='font-size:18px;font-family:Anton,Arial'>{o['headline']}</span><br>"
                 f"<i>{o.get('subheadline','')}</i><br>CTA: {o['cta']['label']}<br>"
                 f"<small>{o.get('hook_summary','')}</small></div>")
    html = f"<div style='font-family:Inter,Arial;max-width:600px;margin:0 auto'><h2>Postcard options — {slot} drop {drop_s}</h2><p>Reply with the letter you want, or tweak any of them.</p>{rows}<p style='font-size:11px;color:#888'>Auto-generated server-side (Sakana + rule validation). Archive: {ARCHIVE_URL}</p></div>"
    text = f"Postcard options for {drop_s} ({slot}):\n\n" + "\n".join(
        f"{o['id']} [{o['archetype']}] {o['headline']} | CTA: {o['cta']['label']}" for o in chosen)

    user = os.environ.get("GMAIL_USERNAME"); pw = os.environ.get("GMAIL_APP_PASSWORD")
    rcpts = [r.strip() for r in os.environ.get("POSTCARD_RECIPIENTS", "").split(",") if r.strip()] or \
            ["graehamwatts@gmail.com", "graehamwattsvideo@gmail.com"]
    if not (user and pw):
        print("::error::GMAIL creds missing — options artifact written, email not sent"); sys.exit(1)
    msg = MIMEMultipart("alternative"); msg["Subject"] = subject; msg["From"] = user; msg["To"] = ", ".join(rcpts)
    msg.attach(MIMEText(text, "plain")); msg.attach(MIMEText(html, "html"))
    ctx = ssl.create_default_context(); sent = False
    for host, port, mode in [("smtp.gmail.com", 587, "starttls"), ("smtp.gmail.com", 465, "ssl")]:
        try:
            s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) if mode == "ssl" else smtplib.SMTP(host, port, timeout=30)
            if mode == "starttls": s.starttls(context=ctx)
            s.login(user, pw); s.sendmail(user, rcpts, msg.as_string()); s.quit(); sent = True; break
        except Exception as e:
            print(f"  {host}:{port} failed: {e}", flush=True)
    if not sent:
        print("::error::SMTP failed — artifact kept, NO sent marker written"); sys.exit(1)
    # sent marker ONLY after SMTP success
    os.makedirs(os.path.join(DATA, "sent"), exist_ok=True)
    with open(sent_marker, "w", encoding="utf-8") as f:
        json.dump({"drop": drop_s, "sent_at": datetime.datetime.utcnow().isoformat() + "Z",
                   "recipients": rcpts, "option_ids": [o["id"] for o in chosen]}, f, indent=2)
    print(f"Sent {len(chosen)} options for {drop_s} to {rcpts}", flush=True)


if __name__ == "__main__":
    main()
