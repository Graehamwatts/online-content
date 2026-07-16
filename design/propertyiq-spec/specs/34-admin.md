# 34 · Admin Console (PropertyIQ ops / broker tier)

**Purpose** The trust machinery for the platform team and (Stage 3) broker tier: kill switches, live rate/budget meters, the immutable append-only audit log, per-tenant cost/COGS, seam status, evaluation metrics, and the migration console. Agents rarely see this; the owner and platform team live here. (Wattson Master Brain Parts 10/12/13; List A #32/#33/#34/#37.)

**Primary users** Stage 1: owner only. Stage 3: RBAC roles Owner/Admin/Agent/TC/Reviewer/Compliance (List A #34) — most panels Owner/Admin; Compliance role gets the audit log + eval dashboard read access [role mapping BEST GUESS beyond "owner-only Stage 1"].

**Entry points** Left nav "Admin" (role-gated); "⏻ Emergency stop" link in the Settings header (Screen 21) jumps here to the kill-switch panel; cost/margin alerts and incident notifications deep-link to their panels; SMS kill command exists independent of the UI (owner-only Stage 1).

**Exit points** Audit-log rows → the originating record (contact, playbook run, content lock); cost tiles → per-tenant drill-down; seam panel → Distribution Board seam checklist; migration console actions → feature-flag change records; eval metrics → promotion workflow in Settings > Autonomy.

## Layout
- **Header:** "PQ" avatar (platform, not agent), "Admin", subtitle "Tenant: graehamwatts · plan: Pro" (tenant switcher for platform staff), nav right: red "⏻ Kill switch" always visible.
- **Main (desktop): 2-column card grid** per draft: Kill switches (red-bordered, top-left) · Audit log · Cost/COGS · Seams & evaluation. Extended panels below [matrix requires them]: Rate limits & budget caps with live meters · Migration console · Incident/observability view · Token-budget circuit breakers.
- **Mobile (375px):** single column, kill switch pinned first; meters render as horizontal bars; audit log becomes a search-first list. Admin is desktop-primary; mobile is emergency-access mode (kill switch + incidents) [BEST GUESS].
- **Sticky:** kill-switch button in header on every scroll position.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Kill-switch panel | Scope selector global / tenant / user / module; <5s propagation from trigger to halt; mechanism = Temporal workflow cancel/pause + connector.stop() on every active connector + emergency policy flag (blocks new step admission at the Guardrail Engine) + active ElevenLabs voice-session termination; NO OS SIGSTOP; last test drill date shown; resume ONLY by explicit re-enable, never auto | Emergency Controls (Wattson Part 13) | select scope → confirm modal (typed confirmation [BEST GUESS]) → halt; re-enable is a separate explicit action, logged | Wattson Brain C14/B7.4; draft s34 |
| SMS-command note | Kill switch also triggerable by SMS command (owner-only Stage 1) — display registered number/status | Emergency Controls config | manage number | Wattson Brain Part 13 |
| Rate-limit meters | Live usage vs Stage 1 defaults: email 200/user/day · SMS 100/user/day · voice 120 min/user/day · API calls 5,000/user/day · MLS queries 500/user/day; policy-based, scoped global/tenant/user/plan/channel/region (List A #33) | policy store + usage counters | edit limits (policy write, logged); breach → the offending playbook auto-pauses + alert, never silent degrade | Wattson Brain Part 13; Screen 21 draft ("circuit breakers auto-pause the offending playbook, alert, never silently degrade") |
| Budget caps | Per user/day defaults: LLM $10 · voice API $15 · ads configurable default $50 (also gated by the spend envelope, Part 8 — envelope itself edits in Settings, cap shown here); call cutoffs: max duration 10 min, 2 calls/number/day, hours 09:00–20:00 | budget policy | edit, logged | Wattson Brain Part 13 |
| Token-budget circuit breakers | LLM spend meter + breaker state per tenant (the $600/day Fugu incident is the design rationale — draft cost tile note) | cost pipeline | configure thresholds | matrix "token budget circuit breakers"; draft s34 |
| Audit log browser | Append-only, immutable; every action with capability + policy snapshot **at decision time**; tenant_id on every entry; filter by contact / playbook / day / user / event type; exportable for E&O or DRE inquiries | Audit Log (immutable store) | filter, search, export (export action itself logged); row → provenance detail (who/what/why, correlation_id) | Wattson Brain Parts 4/10; matrix; draft s34 |
| Cost / COGS dashboard | Per-tenant monthly split (draft example: $38 LLM · $6 voice · $11 render · $9 data = $64 vs $199 plan) vs COGS model bands (LLM $20–40, compute $10–20, broker $3–8, storage $2–5, monitoring $5–10, voice $50–300 = $90–380/user/mo); margin-floor alert at 60% [draft number — matches "alert at 60% margin floor"]; voice metered separately (largest variable cost) | cost pipeline per tenant | trend lines per user; drill per module; alert config | Wattson Brain Part 12; draft s34 |
| SEO cost-elimination tile | vendor_cost_before $400/mo vs $0 after + monthly SearchAtlas/OTTO + compute costs; net savings; OTTO project count vs plan limit (Starter=1, Pro=4 concurrent) with warn-before-exceed | SearchAtlasOttoAdapter | link to SEO console | Wattson Brain Part 6 (lines 203/233) |
| ISA comparison tile | Human ISA $15–25/hr vs Wattson ~$0.05–0.15/min 24/7 | static model + usage | none | Wattson Brain Parts 7/12 |
| Seam status panel | Auto-publish seam checklist progress (e.g. 5/7), voice SLA state, per-platform AI-disclosure hold status | Distribution/seam registry | row → Distribution Board | draft s34; matrix (7-item auto-publish seam checklist) |
| Evaluation metrics dashboard | approval-unmodified rate (draft: 93%), hallucination flags, complaint count, incident count per step — the same stats that gate autonomy promotion (30 days + ≥95% unmodified + 0 incidents, per Screen 21) | eval pipeline / ApprovalRecord stats | filter per playbook/step; link to promotion workflow | draft s34 + s21; matrix "evaluation metrics dashboard" |
| Observability / incident view | OpenTelemetry tracing + Sentry/Datadog-style monitoring + incident-severity workflow; failure-handling record (halt + escalate, retry only if step.on_failure==retry and <3) | observability stack (List A #37) | open incident, assign, resolve | Wattson Brain Part 13 |
| Migration console | Feature flags, dry-run, rollback for the GHL→PropFlow (and similar) migrations; source-of-truth indicator (GHL now → PropFlow after explicit approved migration) | migration/flag service | toggle flag (confirm + log), run dry-run, rollback | matrix Platform settings gap; Wattson Brain C8/B8 |
| Approval-delegation panel | Owner delegates approval rights to named users (a team member's instance can never approve its own REVIEW_REQUIRED output) | Admin Console config | add/remove delegate, logged with timestamp | Wattson Brain Part 3 line 47 / line 301 |
| Mode-promotion log | Owner-approved autonomy promotions with timestamps ("explicit owner approval logged in Admin Console with timestamp") | Admin config log | view history | Wattson Brain line 301 |
| Tenant switcher | Platform staff only: pick tenant; all panels re-scope | tenant registry | switch (logged) | draft header; multi-tenant isolation rules |
| Kill-drill record | Last kill-switch test drill date + result (draft: "last test drill Jul 1 ✓") | drill log | schedule drill | draft s34 |

## States
- **Default:** all green — meters under caps, no incidents, seams progressing.
- **Loading:** meters/log paginate with skeletons; audit log search is server-side.
- **Empty:** new tenant → zeroed meters, empty log with "actions will appear here with their policy snapshots."
- **Error/degraded (fail-closed):** cost pipeline stale → tiles show "as of [timestamp]," never silently stale; audit-log store unreachable → banner + WRITE-blocking posture (if actions can't be audited, gated actions pause) [BEST GUESS consistent with fail-closed doctrine]; kill switch is designed to work when everything else is down (independent path).
- **Kill active:** whole console shows a persistent red state banner with scope + who triggered + re-enable control.
- **Permission-limited:** non-owner Stage 1 → no access; Stage 3 role-scoped panels; every config write logged with actor.
- **Mobile:** emergency mode (kill switch, incidents, meters read-only).

## Data fields
Kill state {scope, triggered_by, at, mechanism results}, drill log, rate-limit policies {channel, scope, limit, window} + usage counters, budget caps + spend, token-breaker thresholds/state, audit entries {tenant_id, actor, action, capability snapshot, policy snapshot, correlation_id, timestamp} (append-only), cost lines per tenant per category, margin %, seam checklist items + status, eval stats {unmodified-approval rate, hallucination flags, complaints, incidents} per step, incidents {severity, trace, state}, feature flags {name, state, dry-run results, rollback point}, delegates list, plan tier + limits.

## Rules & compliance
- Kill switch: <5s halt; Temporal owns workflow state (SIGSTOP forbidden); resume only by explicit re-enable.
- Audit log is append-only and immutable; entries carry capability + policy snapshot at decision time; exportable for E&O/DRE inquiries; every admin write is itself an audit entry.
- Rate limits/budget caps live in policy (ChannelPolicy etc.), never hardcoded; breaches pause the offending playbook and alert — no silent degradation.
- Self-approval prohibition and delegation flow enforced here.
- Tenant isolation: no cross-tenant data in any panel; tenant switch is a logged privileged action.
- No default numeric spend-envelope limits invented — owner-set only (envelope in Settings; this console shows caps/meters).

## Cross-links
In: Settings emergency-stop link, margin/breach alerts, incident notifications, Voice Ops (usage meters link), SEO console (cost tile). Out: Distribution Board (seams), Settings > Autonomy (promotion workflow), originating records from audit rows, Billing/plan. Emits: kill/enable events, policy-change events, export events, promotion approvals — all into the audit log itself; consumes every module's events as the log's content plus NOTIFICATION_* and COMPLIANCE_BLOCKED streams for incident correlation.

## Open decisions
- [DECIDE] Broker-tier (Stage 3) panel subset for the Compliance role — interim: audit log + eval dashboard read-only, no controls.
- [DECIDE] Margin-floor alert threshold — draft says 60%; keep 60% as interim until pricing/metering (List B voice-overage item) is resolved.
- [DECIDE] Visual design: the Brain explicitly defers Admin Console visual/UI (incl. light/dark, colors) to a separate design track (List A #34) — interim: inherit the platform design system, no bespoke theme.
- [BEST GUESS] Audit-unavailable write-blocking posture; typed confirmation on global kill; mobile emergency-mode scope.
