# 24 · Universal Review Queue / Outbox

**Purpose:** Everything client-facing that a HUMAN must send, in typed lanes — plus the compliance flags and sensitive-topic handoffs where automation stops entirely. Distinct from Approvals (Tab 13): Approvals governs whether an automation may execute; the Outbox holds finished client-facing artifacts pending the review-first human forward (Graeham's standing rule: client-facing content is sent to Graeham + Adrian for review, who forward to the client — never auto-emailed to clients).

**Primary users:** Agent/owner; Adrian-class reviewer (client-care) as a second recipient of review-first sends. Delegated staff may work specific lanes if granted (same per-lane delegation model as Tab 13).

**Entry points:**
- Left-nav / top-bar "Outbox" entry with pending badge ("5 pending sends · 2 flags").
- Deep links from: Past Client OS (Tab 27 — 6-month CMAs land here for review), CMA Builder (publish → Outbox), Weekly Seller Dashboard pipeline (Monday doorway email), Newsletter builder ("Approve all 3 → Outbox"), Prospecting Hub (draft outreach), transaction milestones (crew packets, seller reports).
- Push: sensitive-topic handoff is an interrupt-tier alert that lands the user here.

**Exit points:**
- Review & send → send flow (Gmail/SMTP via NotificationProvider) → item moves to Published archive with hosted URL; ledger send events emitted.
- Preview ×N → per-segment preview overlay (newsletters) → back or approve.
- Edit → owning builder screen (CMA builder, newsletter editor, composer) → re-enters queue.
- Sensitive-topic handoff card → opens the contact's conversation (CRM Tab 14) with automation suspended; resolving it is a human action logged on the contact.
- Fair-housing flag → approve suggested rewrite (re-queues the send) or edit or discard.
- "Published archive" nav → archive of everything sent, each with its copyable permanent hosted URL (matrix: "every published report gets a copyable permanent URL").

## Layout

**Desktop:**
- **Header:** avatar · "Outbox & review" · "5 pending sends · 2 flags" · nav: Published archive. Add lane filter chips: All / CMAs / Seller reports / Newsletters / Crew packets / Prospecting drafts / Flags [BEST GUESS chip set — derived from matrix lane list: "seller reports, crew packets, newsletters, CMAs, sensitive-topic handoffs, Fair-Housing flags, duplicate reviews"].
- **Main (single column):** pending-send rows first (compact rows: lane badge · title · context line · primary action button), then flag cards visually distinct: sensitive-topic = crit-red bordered card, compliance/fair-housing = warn-amber bordered card. Duplicate-review conflict cards (from lead intake) render as side-by-side contact candidates with Merge / Keep separate (matrix PropFlow gap — no auto-merge).
- **Sticky:** header + chips. No rails/footer.

**Mobile (375px):** rows become full-width cards; Review & send opens a full-screen preview with the send button pinned bottom; flags pinned to the top of the list regardless of filter (safety first).

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| Header counts | Pending sends + flags | Outbox queue aggregate | none | Draft Screen 24 |
| Lane chips | Filter by artifact type | OutboxItem.lane | Filter | Matrix "typed lanes" [BEST GUESS exact chip set] |
| CMA row | e.g. "Torres CMA — 318 Hurlingame · hosted URL ready · due today (promised 24h) · sends to YOU + Adrian for forward, per review-first rule" | cma-generator pipeline output; hosted URL on online-content | Review & send → full preview → send | Draft; CMA skill review-first rule; Past Client OS 6-mo CMA cadence |
| Seller-report row | "Weekly seller dashboard email — Monday doorway email · showing feedback verbatim included (N entries)" | PropClose Weekly Seller Dashboard artifact (durable URL, week navigator, verbatim feedback) | Review & send | Draft; matrix correction #8 (seller report = live weekly dashboard, doorway email review-first) |
| Newsletter row | "Farm letter — 3 segment variants · owners/buyers/investors previews · scheduled Thu 8am pending approval" | Newsletter builder per-segment outputs | Preview ×3 (segment-switcher overlay) → approve schedule / edit | Draft; matrix newsletter gap (per-segment preview, approval gate) |
| Crew-packet row | Pre-shoot packets to videographer/editor/agent, pending after the Listing-Plan Card cleared | Wattson listing playbooks (Part 9: team-facing sends REVIEW_REQUIRED, never AUTONOMOUS, fire only after the one-approval card) | Review & send per recipient | Wattson MB Part 9; matrix correction #1 (NOTHING_DISPATCHES_UNTIL_APPROVED) |
| Prospecting-draft rows | Expired/off-market/DOM-anomaly outreach drafts; drafts never auto-send | Wattson MLS playbooks | Review & send / edit / discard | Matrix Wattson MLS gap |
| Sensitive-topic handoff card | "🛑 lead mentioned divorce in reply — All automation suspended on this contact. Conversation-so-far attached; this is yours from here. (Same rule for estate, illness, financial distress.)" | Compliance layer: human_handoff_required=true (C1/B1.8); topic list: divorce, probate/estate, health, religion, disability, family status, protected class, regulated financial distress | Open conversation (CRM); mark handled (logged); NO automated actions offered | Wattson MB C1/B1.8; V0 §13.7; draft |
| "No automation will touch this contact" notice | Explicit statement on every sensitive card | Compliance flag | none | Matrix Platform review-queue gap |
| Fair-housing flag card | "⚑ draft GBP reply used 'family-friendly neighborhood' · Blocked pre-send · suggested rewrite: 'close to parks and schools'" | ComplianceProvider needs_review result | Approve rewrite / Edit / Discard | Draft; V0 Fair Housing/FEHA gates |
| Duplicate-review card | Two candidate contacts side-by-side with field diffs | PropFlow intake dedupe queue (no auto-merge) | Merge / Keep separate | Matrix PropFlow lead-inbox gap |
| Review & send flow | Full artifact preview (hosted URL iframe or HTML email render) + recipients (defaults: Graeham + Adrian for client-facing; task-specific recipients per artifact) + send button | NotificationProvider (EMAIL); recipients from artifact config | Confirm send; compliance check runs pre-send and blocks with reason on failure | Standing review-first rule; NotificationProvider contract (B3.4) |
| Published archive | Every sent/published artifact: type, recipient, sent date, permanent hosted URL (copy button), open tracking where available (CMA opens feed propensity — Tab 27) | online-content hosted URLs + ledger send events | Search/filter, copy URL, open artifact | Matrix skills-library Outbox gap; draft Tab 27 CMA open-tracking |
| Empty state | "Outbox clear — nothing waiting on you" + count of items expected this week [BEST GUESS copy] | queue | none | pattern parity with Tab 13 |

## States

- **Default:** pending sends sorted by due date (promised-by first, e.g. "due today (promised 24h)"); flags pinned top.
- **Loading:** skeleton rows; badges last.
- **Empty:** clear-state message; archive still reachable.
- **Error/degraded (fail-closed):** send pipeline (SMTP/Gmail/NotificationProvider) unreachable → send buttons disabled with banner "Send channel down — nothing queued will go out"; nothing silently queues. ComplianceProvider down → all sends blocked (compliance must pass pre-send), flags remain visible.
- **Permission-limited:** delegate sees granted lanes only; sensitive-topic cards visible ONLY to the owner (and explicitly-granted humans) — [BEST GUESS: owner-only default, since the spec's intent is a personal human takeover].
- **Mobile:** flags always pinned; full-screen preview before any send (no one-tap blind sends).

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| lane | enum: CMA · SELLER_REPORT · NEWSLETTER · CREW_PACKET · PROSPECTING_DRAFT · SENSITIVE_HANDOFF · COMPLIANCE_FLAG · DUPLICATE_REVIEW [BEST GUESS names] | OutboxItem |
| title / context line | strings (property, client, cadence context) | Owning module |
| due / promised-by | timestamp + human label | Artifact SLA (e.g., CMA 24h promise) |
| hosted_url | permanent URL (online-content repo pattern) | Publishing pipeline |
| recipients | to/cc list; default Graeham + Adrian for client-facing | Artifact config + standing rule |
| compliance_result | pass / blocked+reason / needs_review+suggested rewrite | ComplianceProvider |
| handoff payload | contact_id, trigger phrase, conversation-so-far attachment, human_handoff_required=true | Compliance layer (C1) |
| duplicate candidates | two contact records + field-level diff | PropFlow dedupe queue |
| send events | NOTIFICATION_QUEUED / NOTIFICATION_SENT / NOTIFICATION_FAILED | NotificationProvider (B3.4) |
| open tracking | opens count per hosted URL (feeds seller-signal flags) | Ledger PORTAL_VIEWED / page-view events |

## Rules & compliance

- **Review-first rule (overrides everything):** client-facing artifacts are never auto-sent to clients; they send to Graeham + Adrian who forward. Internal reports send directly (that's the scheduled-reports rule, not this screen's).
- **Sensitive-topic firewall (C1/B1.8):** detection sets human_handoff_required=true ONLY — no score change, no field write, no audience inclusion, no automated outreach, no priority change. The card offers zero automated actions.
- **Fair-housing:** blocked pre-send with the specific phrase flagged and a compliant rewrite offered; school-data steering rules apply to any community content passing through (V0 C11).
- **Pre-send compliance gate:** every outbound runs ComplianceProvider.check_outbound_contact() (consent, DNC, quiet hours, CAN-SPAM unsubscribe for email); blocked sends show the reason inline — never fail silently, never improvise (matrix correction #11).
- **No auto-merge:** duplicate contacts always require the human decision.
- **Crew packets:** dispatch only after the Listing-Plan Card approval (Tab 13) cleared — this queue is the second (send) gate, not a bypass.
- **Fail-closed:** channel down = nothing sends; compliance unknown = blocked.

## Cross-links

- **In:** Past Client OS (Tab 27) CMA batches, CMA Builder, PropClose seller-dashboard pipeline, Newsletter builder, Wattson listing playbooks (crew packets), Prospecting Hub drafts, PropFlow intake (dupes), compliance layer (flags/handoffs).
- **Out:** CRM contact detail (Tab 14 — handoff conversations, duplicate resolution), Published archive, Approvals (Tab 13 — upstream gate), Settings (Tab 21 — send-channel health when degraded).
- **Ledger events:** emits NOTIFICATION_QUEUED/SENT/FAILED, artifact-published events (hosted URL), handoff-resolved log entries [BEST GUESS event name]; consumes compliance results, human_handoff_required flags, artifact-ready events, PORTAL_VIEWED opens.

## Open decisions

- [DECIDE] Exact lane taxonomy and whether duplicate-review lives here vs. a CRM-local queue — interim: here, per the matrix's "typed lanes" list which includes duplicate reviews.
- [DECIDE] Sensitive-handoff visibility (owner-only vs. any delegated human) — interim: owner-only.
- [DECIDE] Whether the Published archive is a tab of this screen or its own screen — interim: a view within this screen (nav link), since the matrix pairs "Outbox + published-content archive."
- [DECIDE] Scheduled-send support (newsletter "Thu 8am pending approval") — interim: approving arms the schedule; the send still fires through the compliance gate at send time.
