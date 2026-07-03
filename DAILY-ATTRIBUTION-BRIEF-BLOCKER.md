# Daily Attribution Brief — Execution Blocker (CORRECTED)

**Status**: ❌ **BLOCKED** — GoHighLevel Private Integration Token is a placeholder (HTTP 401)
**Date**: 2026-07-03 (Friday, 7:15 AM PT)
**Scheduled Task**: `daily-attribution-brief` (Mon–Fri, 7:15 AM PT)

> **This supersedes the 2026-06-30 version of this doc, which was wrong.**
> That version blamed a missing GitHub `workflow` token scope. That was a
> misdiagnosis. The workflow file is already present in the repo. The real and
> only blocker is that **no valid GHL token has ever been set.**

---

## The real root cause

`.claude-credentials/ghl-pit.txt` line 1 still contains the literal setup
placeholder — `pit-PASTE_YOUR_..._TOKEN_...HERE` — not a real key. GoHighLevel
therefore rejects every request:

```
GET /opportunities/pipelines  →  HTTP 401
{"statusCode":401,"message":"Invalid Private Integration token"}
```

The same unfilled placeholder is almost certainly why every prior run failed
too — the earlier runs just misattributed it to GitHub permissions.

## The fix (2 minutes, requires Graeham — only he can mint the token)

1. GoHighLevel → Settings → Private Integrations → open "Claude Attribution"
   (or Create New Integration) → grant READ scopes for Contacts + Opportunities.
2. Copy the `pit-…` key.
3. Paste it as **line 1** of `.claude-credentials/ghl-pit.txt` (and the
   `Documents\Claude\Skills\ghl-pit.txt` copy so both match), replacing the
   placeholder.
4. Re-run the task. It will pull live data.

---

## What was verified on 2026-07-03 (corrects the old assumptions)

- **The sandbox CAN reach GHL.** A direct call to
  `services.leadconnectorhq.com` returned a real **401 auth response**, not a
  `403 blocked-by-allowlist`. The old "sandbox proxy blocks GHL, so we must
  fire a GitHub Action" premise is **stale** — the brief can run entirely from
  the sandbox once a real token exists. No GitHub Action is required.
- **Client signature matters.** Bare `python urllib` triggers Cloudflare
  **error 1010** on the API paths. `curl` (and any browser-style User-Agent /
  TLS fingerprint) passes cleanly. Any local pull script should use a
  browser-style client, not bare urllib.
- **The old workflow's email step is fake** — `.github/workflows/daily-attribution-brief.yml`
  ends with `echo "Email would be sent…"`, so even a green Action never emailed.
  Prefer the Gmail connector (draft) or SMTP with `GMAIL_APP_PASSWORD`.

## Recommended go-forward architecture

Run the whole brief from the sandbox: read the (real) PIT from
`.claude-credentials/ghl-pit.txt` → pull contacts/opps/pipelines with a
browser-style client → build HTML → push to `dashboards/attribution/` with the
`repo`-scope token (content files only, no `workflow` scope needed) → email via
the Gmail connector. The GitHub Action becomes unnecessary.

---

**Bottom line**: This is not an infrastructure, network, or GitHub-permission
problem. One real GHL token, pasted into one file, unblocks everything.
