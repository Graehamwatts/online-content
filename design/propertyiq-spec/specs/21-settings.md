# 21 · Settings Suite & Notifications

**Purpose:** The governance heart of the platform: locked brand identity, the autonomy/permission matrix per playbook step, spend/rate caps with live meters, integration health, channel registry, sequences/templates registry, notification preferences + the in-app notification center, data-retention display — and the kill switch where it can be found in a panic.

**Primary users:** Agent/owner. Admin-scoped panels (delegation grants, promotion sign-off, kill switch) are owner-only; team members get read-only or hidden panels per role.

**Entry points:** ⚙ Settings in the persistent left rail / top nav of every agent screen; notification bell (top bar, app-wide) opens the Notification Center panel of this suite; deep links from Approvals (delegation, autonomy promotion), from degraded-integration banners anywhere in the app ("repair task" links), from spend cards (envelope config), from onboarding wizard completion (Tab 23 hands its choices here for later editing).

**Exit points:** Emergency stop → confirmation modal (scope selector) → global halt; integration repair task → provider OAuth flow; autonomy promotion approval → logged to Admin Console; sequences registry → template editor; notification item → the originating screen (ledger deep link); nothing here navigates outside the app except OAuth consents.

## Layout

**Desktop:**
- **Header (sitehead):** avatar · "Settings" · subtitle listing sections "Identity · Autonomy · Channels · Integrations · Limits · Notifications" · right nav: **⏻ Emergency stop** in crit-red, always visible (draft: "where it can be found in a panic").
- **Left rail (section nav):** Identity & Brand / Automation & Autonomy / Limits & Meters / Integrations / Channels / Sequences & Templates / Lead Sources / Notifications / Data Retention / Calling Hours & Voice / Billing. [Draft renders a 2-column card grid summary; the build expands each card into a section — deepening, not contradicting.]
- **Main:** the selected section's panel. Default landing = the 2-column overview grid of the six draft cards, each clicking through to its section.
- **Mobile (375px):** overview cards stack single-column; Emergency stop stays in the sticky header; autonomy matrix table scrolls horizontally inside its own container; notification center is a full-screen sheet from the bell.

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| Emergency stop control | Kill switch: scope selector (global / this tenant / this user) + confirmation; halts all Wattson execution <5s — Temporal cancel/pause + connector.stop() on every active connector + emergency policy flag (blocks new step admission) + active ElevenLabs voice-session termination. NEVER OS SIGSTOP. Also triggerable by SMS command (owner-only Stage 1) | Wattson MB Part 13 (C14/B7.4) | Click → scope modal → confirm → status banner "STOPPED at hh:mm — resume requires owner" | Wattson MB Part 13; matrix Wattson kill-switch gap (P0) |
| Identity & brand panel | Graeham Watts · Intero Real Estate · DRE #01466876 — read-only from identity.json; brand-tripwire note ("blocks any output containing a blocklisted DRE"); brand vault colors editable, layout never | shared-references/identity.json (single source of truth) | View; edit colors only; DRE/brokerage/contact fields locked | Draft; Skills CLAUDE.md brand rule; matrix Platform settings gap |
| Autonomy matrix | Scope-matrix table: playbooks × steps with AUTONOMOUS / REVIEW_REQUIRED / ADVISORY badges; per-step promotion stats (days running, unmodified-approval %, incidents) | Wattson StepPermissionMode per playbook step; AutonomyLevel (0–3) account dial | Change a step's mode (tighten anytime; loosen only via promotion flow) | Wattson MB Part 8; matrix Wattson governance gap (P0) |
| Promotion flow | REVIEW_REQUIRED → AUTONOMOUS requires: ≥30 consecutive days, success_rate >95% (human approved WITHOUT modification), zero incidents trailing 30 days, explicit owner approval logged in Admin Console w/ timestamp | Promotion stats service | "Promote" button enabled only when all four criteria show green; confirmation logs to audit | Wattson MB Part 8 |
| Never-Autonomous list | Pinned read-only list: client-facing comms, financial categorization, contract-terms modification, MLS listing submission, spend above cap, Reddit posts, GBP review replies, voice price/commitment statements, voice sensitive topics, cloned voice w/o VoiceIdentity, testimonial w/o ReleaseRecord | Wattson MB Part 8 (permanent, no promotion path) | none (display only) | Wattson MB Part 8 |
| AutonomyLevel dial | Account-wide setting 0–3 | Wattson C18/B9 | Select level; explanatory copy per level | Wattson MB Part 8; matrix |
| Client-messaging auto-mode toggle | wattson_client_messaging_auto_mode_enabled (default false). Even ON: Bucket-1 locked transactional templates (documents-ready, inspection-scheduled, portal-updated, appointment-confirmed) may auto-send if compliance passes; Bucket-2 discretionary always REVIEW_REQUIRED | Wattson C22/B9.4 | Toggle + inline explanation of the two buckets | Wattson MB Part 8 |
| Spend envelope panel | spend_envelope_enabled + fields: max_daily_budget_increase_amount/pct, max_daily_budget_decrease_amount/pct, max_campaign_daily_budget, max_account_monthly_spend, bid_floor, bid_ceiling, performance_pause_auto_allowed. ALL default null/disabled — "not set = nothing autonomous" shown explicitly | PropReach/Wattson C15/B9.3 | Edit fields; save logs to audit | Wattson MB Part 8; matrix PropReach envelope gap (P0) |
| Gift settings | gift_budget_cap + gift_approval_mode (REVIEW_REQUIRED default / AUTO_WITHIN_BUDGET) | GiftProvider C22/B9.5 | Edit | Wattson MB Part 8 |
| Limits & meters panel | Live usage vs caps: email 200/user/day · SMS 100/user/day · voice 120 min/user/day · API calls 5000/user/day · MLS queries 500/user/day (Stage 1 defaults); budget caps: LLM $10/user/day · voice API $15/user/day · ads default $50/day (envelope-gated). Circuit breakers auto-pause the offending playbook + alert — never silently degrade | Wattson MB Part 13 rate limits + budget caps; ChannelPolicy (limits live there, not hardcoded — C21) | View meters; edit within plan bounds; breaker events link to the paused playbook | Wattson MB Part 13; draft (draft shows weekly meter examples — build shows the per-day canonical caps) |
| Calling hours & voice panel | calling_hours 09:00–20:00 local (enforced via ComplianceProvider), max_call_duration 10 min hard cutoff, max_calls_per_number_per_day 2; voice-identity (VoiceIdentity signing/revocation status); AI-disclosure tokens rendered read-only from identity config | Wattson MB Parts 7 & 13 | Edit hours within legal bounds; revoke voice identity (confirmation) | Wattson MB; matrix voice-ops gap |
| Integrations health grid | Connector cards: MLS, GHL, Meta, Google, DocuSign, Stripe, TikTok, Plaid, etc. — connected / degraded / disconnected states; each card shows what breaks downstream if it disconnects + a repair task; expiring OAuth shows countdown ("TikTok renew 6d") | Tool Connector Layer (typed provider adapters, OAuth preferred) | Reconnect (OAuth flow), view downstream impact, create repair task | Draft; matrix Platform settings gap; Wattson MB architecture #4 |
| Channel registry | Channels table: SMS (Twilio primary / Sinch backup), Email, GHL Task, In-App, Comment-to-DM (GHL primary / ManyChat backup, PHASED), Voice — each with launch status and gate requirements | Wattson MB Part 16 channel registry | View; enable/disable per channel where allowed | Wattson MB channel registry table |
| Sequences & templates registry | Approved copy library with versions and approval status; a sequence missing approved copy shows BLOCKED — never improvises | PropFlow sequences/templates records | Open template editor; version history; approve new versions (routes through Approvals) | Draft; matrix PropFlow composer gap |
| Lead Sources panel | All intake paths (DM, QR, ad click, landing page, IDX form, open-house form, phone, manual import) with connection health/auth status | PropFlow /approved-leads intake config | View health; repair | Matrix PropFlow lead-inbox gap |
| Notification preferences | One interrupt tier ONLY (escrow deadline, hot-lead handoff, expiring-unseen approvals) pushes in real time; everything else batches to the morning brief. Per-channel prefs (push/email/SMS/in-app) | NotificationProvider config (B3.4) | Edit channel per notification class; cannot demote interrupt-tier safety items [BEST GUESS: escrow/handoff interrupts are non-disableable] | Draft; matrix notification-center gap |
| Notification Center (bell feed) | In-app feed = the Event Ledger, filtered to the user's notification classes; grouped by day; unread badge | Event Ledger (C39) via NotificationProvider IN_APP | Click item → deep link to originating screen; mark read; filter by module | Draft ("Bell feed = the ledger, filtered") |
| Data-retention display | Read-only policy display: RetentionClass table, mls_retention_expires_at handling, post-expiry tombstone-hash rule (delete/crypto-shred full body, PII, transcripts) | Platform retention services (V0 §14.8); no module hardcodes retention | View only | V0 §14; matrix Platform settings gap |
| Delegation panel (link) | Per-lane approval delegation grants (shared with Tab 13) | Admin Console delegation records | Grant/revoke; audit-logged | Wattson MB Part 3 |
| Solo-mode toggle | solo_mode: team-routed tasks fall back to owner, rate limits adjust to single-person throughput, approval queues consolidate into one daily review session, handwritten-note queue owner-handled or skipped with logged reason | Wattson MB Part 11 | Toggle per account | Wattson MB Part 11 |
| Billing / plan panel | Plan tier, metered-scan wallet (zoning area scans), usage | Stripe + billing service | View; manage payment (external) | Draft screen-14 inventory row; matrix PropSearch metered-scan item (P2) |

## States

- **Default:** overview card grid; degraded integrations surface a warn chip on the overview card.
- **Loading:** cards render with skeleton meters; never fabricate meter values — meters show "—" until real data arrives.
- **Empty/first-run:** unset envelope fields display "not set — nothing autonomous"; unconnected integrations show setup CTAs (mirrors onboarding Tab 23 steps).
- **Error/degraded (fail-closed):** meter service down → editing disabled ("can't verify current usage — limits locked"); integration API down → card shows DEGRADED + downstream-impact list + repair task; if the policy service is unreachable, autonomy-matrix edits are disabled (no permission changes without verified state).
- **Emergency-stopped:** global red banner across the entire app; Settings shows stop scope, who triggered, when; resume is owner-only with confirmation.
- **Permission-limited:** non-owner sees Identity (read-only), their own notification prefs, and nothing else by default; delegated admins see granted panels; kill switch and promotion approval strictly owner.
- **Mobile:** single-column; matrix table h-scrolls; emergency stop persistent in header.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| Identity fields (name, brokerage, DRE 01466876, phone, email, website, markets) | read-only strings | shared-references/identity.json |
| StepPermissionMode | AUTONOMOUS · REVIEW_REQUIRED · ADVISORY_ONLY per playbook step | Wattson playbook registry |
| AutonomyLevel | 0 · 1 · 2 · 3 | Account config (C18) |
| Promotion stats | days_running, success_rate (unmodified-approval %), incidents_30d, owner_signoff timestamp | Promotion stats service / audit log |
| Rate limits | email 200/d, SMS 100/d, voice 120 min/d, API 5000/d, MLS 500/d (Stage 1 defaults) + live usage counters | ChannelPolicy (C21) |
| Budget caps | LLM $10/d, voice $15/d, ads $50/d default (configurable) + spend to date | Wattson Part 13 |
| Spend envelope fields | 9 nullable fields as listed above | C15/B9.3 config |
| gift_budget_cap, gift_approval_mode | currency, enum | GiftProvider config |
| calling_hours, max_call_duration, max_calls_per_number_per_day | 09:00–20:00 local, 10 min, 2 | Wattson Part 13 / ComplianceProvider |
| Connector status | connected · degraded · disconnected + expiry date + downstream-impact list | Tool Connector Layer |
| Channel rows | provider primary/backup, launch status (LAUNCH-REAL/PHASED), gate | Channel registry (Part 16) |
| Template records | id, version, approval status, BLOCKED flag | Sequences registry |
| Notification classes | interrupt-tier vs batched; per-channel matrix | NotificationProvider config |
| RetentionClass policy rows | class → retention duration → post-expiry behavior | Platform retention services (V0 §14.8) |
| solo_mode | boolean | Playbook config (Part 11) |

## Rules & compliance

- **Identity is locked:** DRE/brokerage/contact read-only from identity.json; the brand tripwire blocks any output containing a blocklisted DRE (the known-bad legacy DRE on the identity.json blocklist is banned — never render it anywhere, including in examples).
- **Loosening permissions requires the promotion flow** (all four criteria + logged owner sign-off); tightening is always instant. Never-Autonomous items have no promotion UI at all.
- **No invented spend defaults:** envelope fields start null; UI must state that null = nothing autonomous.
- **Circuit breakers pause + alert, never silently degrade** (draft rule, backed by Part 13 failure handling: halt, log, notify owner, retry ≤3 only if configured).
- **Rate limits live in ChannelPolicy, not hardcoded** (C21) — the UI edits policy records, not module constants.
- **Kill switch:** <5s, Temporal-owned, no SIGSTOP; resume owner-only.
- **No module may hardcode DNC, calling-hours, AI-disclosure, Fair Housing, consent, retention, pixel, or rate-limit rules outside the shared services** (V0 §14) — this screen is the window onto those services, not a second copy.
- Every change here writes to the immutable audit log with who/when/before/after.

## Cross-links

- **In:** every screen's ⚙ link and bell icon; Approvals Tab 13 (delegation, promotion proposals, envelope links from spend cards); degraded-state banners app-wide; onboarding Tab 23 (writes initial values: personality dial, connections, budget tier).
- **Out:** Admin Console (audit log browser, cost/COGS dashboard — Wattson MB; separate P1 screen), Approvals Tab 13, template editor, OAuth provider flows, Voice Ops screen (voice identity), Billing.
- **Ledger events:** emits SETTINGS_CHANGED-class audit entries [BEST GUESS name], EMERGENCY_STOP_TRIGGERED/RESUMED [BEST GUESS], PROMOTION_APPROVED [BEST GUESS]; consumes the full Event Ledger for the bell feed, NOTIFICATION_* events, connector health events, breaker-pause events.

## Open decisions

- [DECIDE] Whether Admin Console (audit browser, cost dashboard, observability) is a section here or a separate screen — interim: separate P1 screen per the matrix; this screen links to it.
- [DECIDE] Which notification classes are non-disableable — interim: escrow deadlines, hot-lead handoffs, and expiring-unseen approvals cannot be turned off.
- [DECIDE] Plan-tier bounds on editable rate limits — interim: Stage 1 defaults shown as ceilings; PlanTier is never used as a permission value (Part 8) so tiers bound quantities only.
- [DECIDE] SMS kill-switch command UX (owner-only Stage 1) — interim: documented in the emergency-stop confirmation modal ("you can also text STOP-ALL to your Wattson number"); exact keyword TBD.
