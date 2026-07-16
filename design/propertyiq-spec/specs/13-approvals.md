# 13 · Global Approvals Inbox

**Purpose:** The single surface where every automation across all modules terminates for human sign-off. One card per logical unit of work (One-Approval UX, Wattson Master Brain Part 8 — a hard architectural principle). Nothing consequential ships anywhere in PropertyIQ without passing through here; expired items default to NOT shipping (fail-closed).

**Primary users:** Agent/owner (Graeham-class user). Secondarily: delegated approvers — a TC or assistant granted per-lane approval rights (never global; a team member's Wattson instance can never approve its own REVIEW_REQUIRED output — Part 3).

**Entry points:**
- Persistent ✓ icon in the top bar of every agent screen; badge = pending count (matrix P0 #1: "Persistent approvals icon in top bar + dedicated Approvals screen").
- Deep links from: Command Center content queue, Monday Briefing backlog actions, PropReach campaign wizard ("Publish → Approvals"), Funnel builder (Tab 17), SEO console deploy flows (Tab 20), Distribution Board nominations, Prospecting drafts, Voice Ops outbound queue.
- The single interrupt-tier push notification when an unseen item is about to expire (draft depth spec).
- Mobile app: Approvals is a first-class bottom-nav destination (draft: "approvals are the #1 phone task").

**Exit points:**
- Approve → item dispatches via its owning module; mints ContentLock for content items; emits ledger events; card moves to History.
- Edit → element-specific edit modal (content) or inline editor (messages) → new version → NEW compliance pass → NEW lock → card re-enters queue as v(n+1) (draft rule, matrix correction #10).
- Reject w/ reason → halt group, log rejection reason, notify owner (Part 8 on_reject contract).
- Defer → card re-queues; expiry clock keeps running.
- View diff (SEO) → diff preview overlay → Deploy or back.
- History link → searchable decision log. Delegation link → delegation settings panel. Emergency: kill switch reachable via Settings (Tab 21) — not duplicated here, but the top bar is shared.

## Layout

**Desktop:**
- **Header (sitehead):** avatar · "Approvals" · summary line "N pending · oldest expires in Xh" · lane filter chips: All / Content / Messages / Spend / SEO (+ Gifts, Postcards, Video as counts require — chips show live counts, e.g. "All (7)") · right nav: History, Delegation.
- **Main (single column, card stack):** cards sorted oldest-expiry-first (SLA rule). The highest-stakes bundle card (e.g., a PropCast one-approval content bundle) renders emphasized (brand border + brand-soft background). Below the stack: an overflow line ("Also in queue: gift, postcard proof, milestone video") when >5 card types, then the depth-spec info panel is design documentation only — not shipped UI.
- **No left/right rails, no footer.** Sticky: header with lane chips stays pinned on scroll.

**Mobile (375px):**
- Entire inbox = swipe cards: swipe right = approve, left = reject (with reason sheet), down = defer (draft depth spec). Tap = expand full card. Lane chips scroll horizontally under the header. Batch buttons collapse into a per-lane action sheet.

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| ✓ top-bar icon + badge | Pending approval count, app-wide | Platform · ApprovalRecord count where status=PENDING | Click → this screen | Matrix gap "Global Approvals Inbox"; draft note |
| Header summary | "7 pending · oldest expires in 9h" | ApprovalRecord aggregate (min expires_at) | none | Draft Screen 13 |
| Lane filter chips | All / Content / Messages / Spend / SEO / Gifts / Postcards / Video, each with live count | ApprovalRecord.lane | Click filters card stack; state persists per session | Draft; matrix "grouped by type (content, campaign, spend, message, gift, SEO deploy)" |
| One-approval bundle card | Logical unit of work: title, module badge, ContentLock version badge, compliance ✓/✗ chip, expiry countdown | Wattson approval_group bundle {group_id, outputs[], recommended_action, correlation_id, expires_at (default 48h)} — Part 8 | Expand; per-element preview click | Wattson MB Part 8 |
| Bundle quad preview | Content bundles: Video (0:15 preview) · Landing page (URL + gate) · Lead magnet PDF (title, page count) · DM flow (keyword + follow-up) | PropCast content bundle assets | Click any quadrant → element-specific edit modal | PropCast one-approval screen (matrix P0); draft |
| "Approve all N → ships" button | Approves the whole bundle atomically; on_approve executes all outputs atomically | Wattson Part 8 on_approve | Click → 5-min undo window starts → dispatch | Part 8; draft depth spec (undo) |
| "Edit an element" button | Opens the clicked element's edit modal | Owning module editor | Any edit → new version → new compliance pass → new lock | Draft inline rule; matrix correction #10 |
| "Reject w/ reason" button | Halts group; reason required (text field) | Wattson Part 8 on_reject | Modal with reason textarea; logs + notifies owner | Part 8 |
| Message card | Outbound message (SMS/email/DM) with full text, recipient, provenance badge ("requested by Wattson"), consent status line ("consent ✓ SMS · quiet-hours ok") | PropFlow/Wattson Bucket-2 message draft; ComplianceProvider.check_outbound_contact() result | Send / Edit / Reject / Defer | Wattson C22 two-bucket model; matrix Wattson gap (provenance); draft |
| Spend card | Budget change request: amount, campaign, rationale with source facts, envelope remaining ("within your spend envelope ($300/mo remaining: $178)") | PropReach recommendation + spend envelope config (Part 8 / C15) | Approve / Defer / Reject | Part 8 spend envelope; matrix PropReach spend gap |
| SEO deploy card | OTTO change set summary, freeze-flag note, "applies through template variable slots only" | SeoProvider otto_preview_deployment payload | View diff (diff overlay) / Deploy / Reject | Wattson MB Part 6 (deploy gated behind preview+approval, per-project freeze flag) |
| Gift card | Gift description, amount vs gift_budget_cap ("$45 — under $50 cap") | GiftProvider record; gift_approval_mode default REVIEW_REQUIRED | Approve / Reject | Wattson C22/B9.5; draft overflow line. [BEST GUESS] $50 cap is an example value — cap is owner-configured, no default invented |
| Postcard proof card | Farm postcard proof image + drop date | Direct Mail (farming-postcard pipeline) | Approve proof / Edit / Reject | Draft overflow line; skills-library matrix item |
| Milestone video card | Personalized video preview + gate checklist (consent, lead_score≥50, high-intent action, AI disclosure frame-1) | PropFlow personalized video record | Approve / Reject; gate failures shown, card blocked if any gate fails | Matrix correction #3 |
| Expiry countdown chip | Time remaining; amber at 12h left, red at 3h | ApprovalRecord.expires_at | none; drives sort | Draft depth spec. [BEST GUESS] 12h/3h thresholds inherited from draft iteration, not a Master Brain number |
| Per-lane batch button | "Approve all 3 compliant content items" — per lane only, never global approve-all; disabled when the lane has mixed compliance states | Lane aggregate | Click → batch approve → single undo window | Draft depth spec |
| Undo toast | 5-minute undo before dispatch (except hard-deadline items, which say so); undo re-queues, never deletes | Dispatch scheduler | Click Undo → card returns to queue | Draft depth spec [BEST GUESS on 5-min duration — draft decision, no MB number] |
| Delegation panel | "TC can approve: docs, scheduling · Assistant: content" as chips; grant/revoke per lane | Admin Console delegation records (Part 3: owner delegates approval rights in Admin Console) | Add/remove lane grants; every delegated approval logs who + provenance | Wattson MB Part 3; draft depth spec |
| History view | Searchable decisions log: approved/edited/rejected/expired with before/after diffs ("the E&O answer file") | Immutable audit log (Admin Console) | Search, filter by lane/decision/date, open diff | Draft depth spec; Wattson audit-log requirement |
| Volume-guard banner | If a playbook floods the queue (>10 items/day for 3 days), Wattson proposes promoting its reliable steps to autonomous | Wattson promotion stats (Part 8 criteria) | "Review promotion" → Settings Tab 21 autonomy matrix | Draft depth spec [BEST GUESS on 10/day×3d trigger]; promotion criteria = MB Part 8 (30 days, >95% unmodified, 0 incidents, explicit owner sign-off) |
| Empty state | "Nothing needs your sign-off ✓" + next scheduled generation time | Scheduler | none | Draft depth spec |
| Expired-item handling | Expired = safe default: nothing ships; item moves to History as EXPIRED | ApprovalRecord lifecycle | Re-request generation from History | Matrix gap (48h expiry); draft note |

## States

- **Default:** card stack sorted oldest-expiry-first; lane chips with counts.
- **Loading:** skeleton cards (3); header counts render last (no fabricated counts).
- **Empty:** "Nothing needs your sign-off ✓" + next generation time.
- **Error/degraded (fail-closed):** if ApprovalRecord service unreachable → full-screen degraded notice, all approve buttons disabled ("Can't verify queue state — nothing will ship until this recovers"). If ComplianceProvider is down, message/content cards show compliance UNKNOWN and their Approve buttons are disabled (compliance must pass before send — V0 §14 rules; nothing improvises).
- **Permission-limited (delegate view):** delegate sees ONLY their granted lanes; all other lanes hidden (not greyed). Cards they approve are stamped with their identity + provenance. A delegate never sees the Delegation panel.
- **Mixed-compliance lane:** batch button disabled with reason tooltip.
- **Mobile:** swipe-card mode as above; reject always requires the reason sheet (no blind left-swipe dispatch of a rejection without reason).

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| group_id, correlation_id | string ids | Wattson approval bundle (Part 8) |
| lane | enum: CONTENT · CAMPAIGN · SPEND · MESSAGE · GIFT · SEO_DEPLOY · POSTCARD · VIDEO [BEST GUESS enum names; set derived from matrix grouping list] | ApprovalRecord |
| outputs[] | step_output payloads w/ previews | Owning module |
| recommended_action | string | Wattson |
| expires_at | timestamp, default now+48h | Part 8 bundle contract |
| status | PENDING · APPROVED · REJECTED · DEFERRED · EXPIRED · UNDONE [BEST GUESS enum] | ApprovalRecord lifecycle |
| compliance_result | pass / block / needs_review + reason | ComplianceProvider |
| content_lock_version | "ContentLock v2" | PropCast lock registry |
| provenance | requested_by (Wattson / playbook id / user), approved_by, approved_at | Audit log |
| consent snapshot (message cards) | channel consent status + DNC + quiet-hours check | ComplianceProvider.check_outbound_contact() |
| envelope remaining (spend cards) | currency, from spend envelope config | PropReach + Part 8 envelope |
| rejection_reason | required text | ApprovalRecord |

## Rules & compliance

- **Fail-closed everywhere:** expired = nothing ships; compliance-unknown = approve disabled; missing approved copy = BLOCKED state, never invented.
- **Never-Autonomous List** items (any client-facing comm, Reddit posts, GBP review replies, voice price/commitment, cloned voice w/o VoiceIdentity, testimonial w/o ReleaseRecord, spend above cap, contract terms, MLS submission, financial categorization) ALWAYS arrive here — no promotion path exists (MB Part 8).
- Approve = atomic execution of the bundle; any post-approval edit = new version → new compliance pass → new ContentLock (two governed decisions total: Monday backlog approval + per-piece version approval).
- Delegation is per-lane, never global; delegated approvals log identity; self-approval by the producing instance is forbidden (Part 3).
- Sensitive-topic items never appear here as approvables — they route to the Outbox/Review Queue (Tab 24) as human handoffs with automation suspended (C1/B1.8).
- Fair-housing/compliance blocks show the specific rule and a compliant alternative (Wattson refusal pattern).
- One interrupt-tier push only: expiring-unseen items (all else batches to the morning brief — Tab 21 notification model).

## Cross-links

- **In:** every module's terminal automation step; top-bar icon on all ~26 screens; Monday Briefing (Tab 12) backlog approval; Funnel builder publish; SEO console deploys; Distribution Board ad nominations; Prospecting draft outreach; Voice Ops outbound queue.
- **Out:** Distribution Board (Tab 18, post-approval shipping), Settings Tab 21 (delegation, autonomy promotion, spend envelope), Outbox Tab 24 (client-facing sends that a human must forward), owning-module detail screens (edit modals).
- **Ledger events emitted:** APPROVAL_GRANTED / APPROVAL_REJECTED / APPROVAL_EXPIRED [BEST GUESS names], SEO_PAGE_PUBLISHED (with approval_id, by owning module), NOTIFICATION_QUEUED/SENT for dispatches, ContentLock mint events. **Consumes:** approval_group completion events, compliance results, promotion-stat aggregates.

## Open decisions

- [DECIDE] Amber/red expiry thresholds (12h/3h) and the undo-window length (5 min) — interim design keeps draft values; not Master Brain numbers.
- [DECIDE] Volume-guard trigger (>10 items/day for 3 days) — interim design keeps the draft heuristic; promotion criteria themselves are locked by MB Part 8.
- [DECIDE] Lane enum finalization (does POSTCARD fold into CONTENT?) — interim: separate lanes per matrix grouping list.
- [DECIDE] Whether History lives here or in Admin Console audit browser — interim: lightweight History here, deep-links into the Admin Console immutable log for full audit.
