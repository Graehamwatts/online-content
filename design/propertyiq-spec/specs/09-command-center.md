# 09 · Command Center (Today queue + Map mode)

**Purpose.** The agent's single daily operating surface. The event ledger is the engine; "Today" is the interface: every system event (valuation run, tour request, cadence due, CMA promised, escrow deadline, content ready) flows into one ledger and renders as ONE ranked queue — calls first, promises second, cadences third, approvals last. The Map mode toggle (PropSearch Master Brain §17.7) overlays the farm with seller-propensity pins, market-forecast heat, and zoning-capability layers — every color explainable on click. No competitor combines the ranked ledger with the intelligence map; this is the demo screen.

**Primary users.** Solo agent (Graeham archetype) — owner role. Team variant: owner sees cross-team items; team members see only their own queue (Wattson Part 16: a member's instance can never approve its own REVIEW_REQUIRED output; approval routes to owner/delegate).

**Entry points.** Default landing screen after agent login · left-rail "Today" from any agent-console screen · morning-brief email "Start my day" deep link · push notification tap (queue item deep link) · Wattson answer chips ("Add to Today") from Map mode or any module.

**Exit points.** Every queue item deep-links to its owning module: Call → dialer overlay + contact record (PropFlow) · CMA draft → Universal Review Queue / CMA presentation screen · Escrow item → Transaction Workspace (PropClose, Tab: Transaction Workspace) · Content approve → Content Review & Approve screen (ContentLock flow) · Comms rows → unified inbox thread · Campaign card → Campaign Manager (PropReach) · Farm-watch actions → review-task creation (never direct send) · Map pin → property detail page or "Add to Today" · Left rail → Farm map, Leads & clients, Comms, Transactions, Content studio, Content calendar, Ads & funnels, Competitor intel, Playbooks, Reports, Settings · Top bar → ⌘K palette, notification center, Global Approvals Inbox icon.

## Layout

**Desktop (persistent chrome, per draft note line ~1354):** the 172px left rail is global across every agent-console screen; consumer pages never show it.

- **Header (sitehead):** avatar + "Command Center · {weekday, date} · {agent name}" · **Today / Map segmented toggle** (pill, actually switches views) · right nav: "Search anything (⌘K)" + 🔔 notification bell with count + **persistent Approvals inbox icon** (matrix gap #1: "Persistent approvals icon in top bar + dedicated Approvals screen" — P0; add it here even though the dedicated screen is its own tab).
- **Left rail (172px):** Today (active) · 🗺 Farm map · 👤 Leads & clients · 💬 Comms (badge) · 📋 Transactions (badge) · 🎬 Content studio · 📅 Content calendar · 📣 Ads & funnels · 🔎 Competitor intel · ⚙ Playbooks · 📈 Reports · footer: ⚙ Settings.
- **Wattson command bar** (full width under header, both modes): "Ask Wattson anything…" input + Ask button + helper line with ⌘K command grammar examples (`318 hurl cma`, `esc cedar`) and j/k/e/s/c keys. Matrix P0 gap: this surface must be app-wide (right-rail or ⌘K panel on EVERY screen), not Command-Center-only — Command Center hosts the always-visible instance.
- **Main column (Today mode), top→bottom:**
  1. Morning brief card (headline · overnight events · hard deadlines · first move · risk line) + "▶ Start my day" button.
  2. Triage strip (new leads gated before entering Today).
  3. KPI stat row ×6.
  4. Two-column grid: **left 1.4fr** = ranked Today queue; **right 1fr** = stacked cards (Farm watch · Content queue · Comms unified inbox · Campaigns · Site performance).
  5. Goal-pace + Day-close two-card row.
  6. Pipeline strip (6 stages) + expanded escrow lane (2 transaction cards with stage steppers).
  7. Week ahead (5-day strip + `<details>` full week calendar grid).
  8. Shoot-detected pipeline card (6-step, with Listing-Plan approval gate).
  9. This week's content calendar table.
  10. Playbooks card + Ads & funnels card (two-column).
- **Map mode (replaces main column):** header line · 3 chip groups (Intelligence layers / My business / Defend) · farm-pulse badge strip · map canvas with pins + pin-detail popover + legend/compliance label · "Defend this farm — Wattson's read" action card.
- **Footer:** "PropertyIQ · agent console."

**Mobile (375px).** Left rail collapses to a hamburger + bottom tab bar (Today · Map · Comms · Approvals · More) [BEST GUESS]. KPI row becomes a horizontal scroll of stat chips. Queue is the screen: full-width cards, primary action as full-width button, swipe right = done, swipe left = snooze [BEST GUESS, mirrors the j/k/e/s desktop grammar]. Right-rail cards stack below the queue behind an "Overview" accordion. "Start my day" enters a full-screen one-item-at-a-time guided flow (this is the native mobile pattern for guided mode). Map mode is full-bleed; chip groups become a bottom-sheet filter; pin popover becomes a bottom card. Week calendar is a vertical agenda list, not a grid. Wattson bar docks to bottom above the tab bar.

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| Today/Map segmented toggle | Switches main view | UI state | Click/tap; persists per session | Draft Screen 9 note ("toggle now actually switches views") |
| ⌘K search / command palette | Global search + typed command grammar (`318 hurl cma` → CMA draft; `esc cedar` → escrow) | Wattson Action Registry (Part 17) resolving to typed module_actions | Open ⌘K anywhere; type; Enter executes/queues governed action | Wattson MB Part 17 + matrix P0 gap (app-wide Wattson surface); draft line ~1364 |
| Notification bell 🔔 | Unread count; opens Notification Center feed | NotificationProvider events | Click → feed panel | Matrix P0 "Settings Suite + Notification Center"; draft header |
| Approvals inbox icon | Pending ApprovalRecord count; opens Global Approvals Inbox | ApprovalRecord (approval_group bundle: group_id, outputs[], recommended_action, correlation_id, expires_at default 48h) | Click → Approvals screen; badge shows count; items expire at expires_at | Wattson MB Part 8 One-Approval UX; matrix gap #1 (P0) |
| Wattson command bar | Free-text ask: answers from ledger, drafts comms, runs reports, queues actions for approval | Event Ledger + Action Registry; every utterance maps to a governed typed action | Ask → inline answer with source chips + intent buttons ASK_WHY / APPROVE / REJECT / REQUEST_HUMAN_REVIEW | Wattson MB Parts 1, 17; matrix Wattson P0 gap (intent buttons) |
| Morning brief card | Overnight summary, hard deadlines, "first move," risk callout | Ledger digest job (overnight window) | "Start my day" → guided mode (queue left, action center, client card right, complete→advance) | Draft ~1367–1379; guided mode = Lofty/HubSpot pattern |
| Monday briefing envelope | On Mondays the brief becomes the PropCast Monday weekly briefing: lead-never-buried headline, market-state card, ranked content backlog, ATTACK/HOLD/DEFEND posture, one clarifying question; backlog approval = governed decision #1 | PropCast briefing record | Approve backlog (one card) · answer the clarifying question · adjust posture | Matrix P0 gap: "Command Center morning brief should BE this envelope"; PropCast MB |
| Triage strip | "Triage: N new — nothing enters Today without your accept"; Wattson pre-sort suggestions (accept+call / nurture / merge duplicate) | PropFlow lead inbox; duplicate detection (no auto-merge) | One-tap accept / nurture / send-to-duplicate-review per lead | Draft ~1380–1383 (Linear Triage pattern); matrix PropFlow gap (lead inbox + dedupe review) |
| KPI stat row (6) | Needs you now · Unread comms · In escrow · New leads (7d) · Seller signals · AI handled | Ledger aggregates: queue, comms inbox, PropClose transactions, PropFlow leads, PropSearch valuation events, Wattson convo log | Each tile click-filters the queue or opens its module [BEST GUESS: tiles are filters] | Draft ~1384–1391 |
| Today queue (ranked list) | Single ranked to-do list; rank order fixed: calls → promises → cadences → approvals; colored urgency dot (crit/warn/soft) per row; each row = icon, title, context badge, one-line "why," ONE primary action button | Event Ledger items typed: seller-signal call (PropSearch), promised CMA (Wattson promise tracker), escrow deadline (PropClose), cadence touch (PropFlow), tour confirm (AI concierge), content approvals (PropCast) | Primary action per row (Call / Review draft / Open file / Edit & send / Confirm / Review N) · keyboard j/k navigate, e done, s snooze, c call · snooze re-queues | Draft ~1394–1425; ranking rule from Screen 9 note |
| "At risk — things that DIDN'T happen" row | Negative-space alerts (untouched hot lead 48h; listing showing-velocity −40% wk/wk → price-cut analysis suggestion) | Ledger absence-detection (neglect watchdog) | "Fix both" → opens drafted re-engage text (review task) + price-cut analysis | Draft ~1426–1430 (Gong pattern); matrix PropFlow neglect-watchdog gap; price-cut analysis → price-reduction skill |
| FYI line | No-action info (AI nurturing activity, auto-queued cadences) + "open full event ledger →" | Ledger low-priority events | Link → full Event Ledger browser (Attribution/Analytics screen) | Draft ~1431 |
| All-clear line | "Queue is finite" — N things running normally, streak counter, Wattson time-saved | Ledger | None (reassurance affordance) | Draft ~1432 |
| Farm watch card | New listing / price cut / sold events in farm; competitive-share line ("you 20% · J. Lee 3 of last 5"); each signal ends in one-click action chips (CMA the neighbors, Postcard the block, Just-listed nurture, Alert matching buyers, Door-knock note) | PropSearch farm feed + competitor intel (official-API/public monitoring only, hash/URL/excerpt storage) | Action chips create **review tasks** — consent/DNC checked first, nothing auto-sends; unknown consent → consent-capture task | Draft ~1436–1447; matrix correction #2 & #5 |
| Content queue card | PropCast items by status (ready / draft / goes-stale-Fri) + 4-wk performance micro-stats; ContentLock note | PropCast content items + ContentLock versions | "approve & post" → Content Review & Approve; approve mints ContentLock; post-approval edit = new version + new compliance pass + new lock | Draft ~1448–1457; matrix correction #9 |
| Comms unified inbox card | Split streams (Clients/Escrow/New leads/Vendors) w/ per-stream chips; SMS/email/voicemail rows; voicemail transcribed; grounded Wattson draft attached per convo | Comms service (SMS/email/VM ingestion), sync timestamp | Stream chips filter; "draft attached — 1 tap to send" opens draft for human send (client comms are Never-Autonomous — Wattson drafts, human sends) | Draft ~1458–1471; Wattson MB Part 8 Never-Autonomous List |
| Campaigns card (PropReach) | Postcard / listing ads / farm letter performance one-liners | PropReach campaign records + attribution events | Click → Campaign Manager | Draft ~1473–1479 |
| Site performance card | 30d visits, % organic, leads + conversion, top page + rank, AI citations (ChatGPT/Perplexity/AIO); Wattson surfaces OTTO wins here | GSC + analytics + AEO citation tracker; SEO console (OTTO) work summaries | Click → SEO Console / Reports | Draft ~1481–1488 + line 1098 |
| Goal pace card | GCI YTD vs goal, pace line, deals-behind read, Wattson's "why the queue is ranked this way" | Goal config (Settings) + closed-deal ledger | Edit goal → Settings | Draft ~1493–1499. Numbers shown ($118K/$250K/47%/54%) are demo data |
| Day close card | 5:30pm ritual: queue cleared, Wattson-handled count, streak, tomorrow's #1, explicit all-clear | Ledger end-of-day digest | Appears after configurable time [BEST GUESS: default 5:30pm local, Settings-editable] | Draft ~1501–1505 |
| Pipeline strip | 6 counts: Triage / Nurturing (AI) / Active buyers / Seller convos / In escrow ($) / Past clients on cadence + projected pipeline GCI | Same ledger as queue; PropFlow pipelines + PropClose | Stage click → CRM kanban (12-day New-Lead sprint boards live on the CRM screen, not here) | Draft ~1507–1517; matrix PropFlow P0 gap notes draft has "only a GCI strip" — the full kanban is Screen: CRM |
| Escrow transaction cards (×2) | Address/side/price, day X of Y badge, next-deadline badge, GCI, 7-segment stage stepper (Offer→EMD→Inspection→Appraisal→Loan→Docs→Close), waiting-on line, Wattson nudge/escalation note | PropClose TransactionRecord (7-stage stepper is the full workspace's; this is the compact mirror) | "Open file" → Transaction Workspace; signature chips → doc-sign flow | Draft ~1519–1555; matrix PropClose P0 gap (full workspace is its own screen) |
| Milestone-video strip (inside escrow card) | Personalized avatar milestone videos (EMD received, loan cleared, clear to close) w/ watch counts | PropCast render + PropClose milestones | Gates honored: requires ai_video consent + channel consent + lead_score≥50 + explicit high-intent action, defaults REVIEW_REQUIRED, non-removable CA AI disclosure on frame one | Matrix correction #3 (verbatim gates); draft ~1536 |
| Week ahead strip + full calendar | 5 highlighted days; expandable 7-day × time-slot grid; 2-way Google Calendar sync; every event links to client/escrow/content record; auto-held 9–10am call block sized to queue; prep packs attached; deadlines cannot be dragged — only escalated | Calendar sync + ledger deadlines | Expand details · (full build) drag-to-reschedule non-deadline events · event click → linked record | Draft ~1558–1608 |
| Shoot-detected pipeline card | 6 steps: 1 Analyze ✓ · 2 Shot list ✓ (named shot-IDs VID-*/DRN-*) · **3 YOUR approval — Listing-Plan Card (hard gate: NOTHING_DISPATCHES_UNTIL_APPROVED)** · 4 Call sheet → videographer (agent's own) · 5 Assembly map → editor (own, or PropertyIQ editor network upsell) · 6 Product page | Wattson listing-lifecycle playbooks (Part 9) + listing-launch-engine | Buttons: Review shot list (N) · Send call sheet (enabled ONLY post-approval) · Preview assembly map | Wattson MB Part 9 (Dashboard Alert card; pre-shoot emails REVIEW_REQUIRED, fire only after one-approval card clears); matrix correction #1 |
| Weekly content calendar table | IG/FB · YouTube · Email/GBP rows × Mon–Fri; status chips; amber gaps; competitor-intel gap topics injected | PropCast calendar (slots fill from shoot outputs, evergreen engine, market triggers) | Approve-all or per-item (both mint ContentLocks); "full calendar →" → Content Calendar screen | Draft ~1627–1638 |
| Playbooks card | Running automations w/ on/off state (new-listing-in-farm, listing-launch, CMA-promised, past-client cadence, escrow milestone videos, seller-signal escalation, expired/FSBO watch off); Wattson proposes new playbooks from patterns | Wattson Playbook Library records: trigger (ledger event) → steps → approval gates | Toggle per playbook; "library (24) →" → Playbook Library screen; pending-approval chips → Approvals | Draft ~1642–1653; Wattson Playbook Library NX |
| Ads & funnels card | Active campaigns w/ spend/reach/CPL; funnel-pages block (branded/unbranded per compliance, DRE footer on both, per-page UTM so ad→funnel→valuation→call reads end-to-end in ledger); "+ New funnel page" | PropReach + funnel builder + attribution ledger | Manage → Campaign Manager; + New funnel page → Funnel Builder (publish routes through Approvals) | Draft ~1655–1665; matrix P0 Funnel Builder |
| **MAP MODE** — layer chips | 3 groups: Intelligence (Seller propensity pins · Market forecast heat · ADU-eligible parcels *metered* · SB-9 eligible) / My business (Past clients · Active listings · Hot leads) / Defend (Competitor listings · Expiring 30d · FSBO · Absentee clusters) | PropSearch §17.7 layers; ScoringService keys PROPSEARCH_SELLER_PROPENSITY, PROPSEARCH_MARKET_FORECAST; Zoneomics capacity facts; PropFlow contact geo | Toggle chips; ADU/SB-9 area layers are metered: draw/select area → quoted price (actual API cost) → pay → scan runs → results cached; re-run = new charge | PropSearch MB §17.7 (verbatim mechanic) |
| Farm pulse badge strip | Actives · DOM · sale/list % · your trailing-12mo share w/ trend · threat line · opportunity line | PropSearch farm aggregates + competitor intel | None / links to Competitor Intel | Draft ~1692–1697 |
| Map canvas + pins | Color-coded propensity pins (🔴 high 🟠 warming ⚪ low), past-client ⌂ pins, your-listing pin, competitor pins, expiring pins | ScoringService rendering-ready values; PropSearch never defines formula/weights | Click pin → explain popover (decomposable score, never opaque color) | PropSearch MB §17.7 explainability rule |
| Pin-detail popover | Address, propensity badge, contributing facts (years owned, equity %, owner-occupancy, valuation runs, zoning capacity e.g. "ADU by right · builds to 3 units") | ScoringService factors + PropSearch facts + Zoneomics | "Add to Today" (creates ledger call/review task) · "Property page" | Draft ~1706–1717; §17.7 "do their own research rather than trust a color alone" |
| Map legend / compliance label | Pin/color legend + fail-closed + privacy rules text | — | — | Draft ~1720 (rules verbatim, see Rules below) |
| "Defend this farm" card | Wattson's spatial read + actions: 📬 Postcard the 5 · 🚪 Door-knock route · Add all to cadence | Wattson analysis over map layers | ALL outreach actions create review tasks; Predictive-Seller HIGH-tier candidates can NEVER auto-outreach | Draft ~1722–1730; matrix correction #2 |
| Heat-layer click | Area popover: what's driving the read (inventory, DOM, price-cut frequency, appreciation trend, current rate) | PROPSEARCH_MARKET_FORECAST area aggregate | Click area band → factor breakdown | PropSearch MB §17.7 |

## States

- **Default:** Today mode, queue populated, all cards live.
- **Loading:** skeleton rows in queue + shimmer cards; KPI tiles show "—". Map: basemap renders first, layers stream in with per-chip spinners [BEST GUESS].
- **Empty:** new account → morning brief becomes onboarding-completion checklist; queue shows "Nothing yet — Wattson is watching your farm and inbox" + links to connect channels/import sphere [BEST GUESS]. Mid-day cleared queue → the all-clear line is the hero (permission-to-stop ritual).
- **Error / degraded (fail-closed):**
  - ScoringService down or PROPSEARCH_MARKET_FORECAST unpublished → forecast gauge/heat layer HIDE with "score unavailable"; deterministic facts (inventory, DOM, price-cut count) still render; never stale colors (PropSearch MB §17.6/17.7 fail-closed + draft legend).
  - Seller-propensity layer unavailable → pins hide, "score unavailable" chip; business-layer pins (past clients, listings) remain.
  - Comms sync failure → banner "last synced Xm ago — no message silently dropped"; per-stream stale badges.
  - Ledger digest failure → morning brief shows raw event list instead of narrative [BEST GUESS].
  - Approval bundle past expires_at (48h default) → card marked expired, action halts, owner notified (Wattson MB Part 8).
  - Metered scan payment/API failure → no partial results; quote screen re-shown with error.
- **Permission-limited:** team member sees own queue only; approvals of their REVIEW_REQUIRED outputs route to owner/delegate — approve buttons render as "Sent to {owner} for approval" (Wattson MB Part 16). Reviewer/TC roles see transactions + approvals lanes only [BEST GUESS pending RBAC Stage 3 roles: Owner/Admin/Agent/TC/Reviewer/Compliance — Wattson MB #34].
- **Mobile:** see Layout; guided mode is full-screen; map chips in bottom sheet.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| Queue item | {type, rank, urgency(crit/warn/soft), title, context_badge, why_line, primary_action, entity_ref, correlation_id} | Event Ledger |
| ApprovalRecord bundle | group_id, outputs[], recommended_action, correlation_id, expires_at (default 48h) | Wattson Part 8 |
| KPI counts | integers + deltas | Ledger aggregates |
| GCI / goal | USD, % of goal, pace % | Settings goal + closed deals |
| Transaction card | address, side, price, day_n/day_total, stage[7], next_deadline, gci, waiting_on | PropClose TransactionRecord |
| Seller-propensity pin | property_id, score tier (high/warming/low), factors[] (years_owned, equity_pct, occupancy, valuation_run_count) | ScoringService PROPSEARCH_SELLER_PROPENSITY over PropSearch facts |
| Market-forecast area | score + drivers (inventory, DOM, price-cut freq, appreciation, rate) | ScoringService PROPSEARCH_MARKET_FORECAST |
| Zoning-capacity pin data | ADU-by-right, buildable units, built units | Zoneomics v3 parcel/capacity fields via PropSearch |
| Metered scan | area geometry, quoted_price (actual API cost), status, cached results | PropSearch §17.7 billing mechanic |
| Content item | content_id, version, ContentLock id, status, stale_at | PropCast |
| Farm-watch signal | event type (new/cut/sold), address, price/delta, listing agent + brokerage, model-delta % | PropSearch farm feed |
| Competitor intel | agent, brokerage, listing count trailing-5; storage = hash/URL/excerpt/summary only | Official-API/public monitoring (correction #5) |
| Playbook | id, trigger_event, steps[], StepPermissionMode per step, enabled | Wattson Playbook Library |
| Comms message | channel (sms/email/vm), stream, transcript, wattson_draft, source_chips | Comms service |
| Streak / time-saved | integer days · hours | Ledger [BEST GUESS on computation of "time saved"] |

## Rules & compliance

- **One-Approval UX (hard architectural principle):** related actions arrive as one card per unit of work; approvals batched at queue bottom, never outranking calls. Approve executes atomically; reject halts group + logs reason (Wattson MB Part 8).
- **Never-Autonomous List applies everywhere on this screen:** any client-facing communication (email/text/voice/DM), spend above cap, GBP review replies, cloned voice w/o VoiceIdentity, testimonial clips w/o ReleaseRecord. Wattson drafts; a human sends. "1 tap to send" buttons are the human send.
- **Outreach from farm watch / map / defend card:** creates review tasks only; consent + DNC checked first; unknown consent → consent-capture task, never a send; Predictive-Seller HIGH-tier can never auto-outreach (matrix corrections #2).
- **Shoot pipeline hard gate:** NOTHING_DISPATCHES_UNTIL_APPROVED — Listing-Plan Card approval precedes any role packet; pre-shoot emails are REVIEW_REQUIRED team sends (Wattson MB Part 9; correction #1). Videographer = agent's own; editors = as-a-service upsell.
- **Milestone videos:** ai_video consent + channel consent + lead_score≥50 + explicit high-intent action; default REVIEW_REQUIRED; non-removable CA AI disclosure frame one (correction #3).
- **ContentLock:** exactly two governed content decisions — Monday backlog approval + per-piece exact-version approval; any post-approval edit = new version → new compliance pass → new lock (correction #9).
- **Map explainability:** pins are decomposable scores, never opaque colors; fail-closed when ScoringService down ("score unavailable," never stale colors); owner signals show absentee/corporate/owner-occupied badges only — never names/addresses on the map layer (draft legend ~1720).
- **Metered scans:** draw → quote → pay → run; cached; re-run = new charge; no invented default prices (PropSearch §17.7).
- **Spend envelope:** null envelope = nothing autonomous on spend; ad_spend_change_mode defaults REVIEW_REQUIRED; auto-pause only for safety conditions (Wattson MB Part 8).
- **Promotion path:** REVIEW_REQUIRED→AUTONOMOUS needs ≥30 consecutive days, >95% unmodified-approval rate, zero incidents 30d, explicit owner approval logged in Admin Console. Show promotion stats on playbook steps [surface on Playbook Library screen; chip here].
- **Deadlines are immovable on the calendar** — escalate, never drag.

## Cross-links

- **In:** login default · morning email · notifications · every module's "back to Today."
- **Out:** Approvals Inbox (13) · CRM Contacts+Pipelines · Transaction Workspace · Content Review & Approve · Content Calendar · Campaign Manager · Funnel Builder · SEO Console · Competitor Intel (11) · Playbook Library · Reports/Attribution · Settings (21) · Property detail (3) · Seller report (10) · CMA presentation.
- **Ledger events consumed:** every event type (valuation_run, tour_requested, cadence_due, cma_promised, escrow_deadline, content_ready, campaign_metric, comms_received, competitor_listing, playbook_trigger…).
- **Ledger events emitted:** item_completed, item_snoozed, approval_granted/rejected, triage_accepted, review_task_created, consent_capture_task_created, add_to_today (from map), metered_scan_purchased, day_closed.

## Open decisions

- [DECIDE] Map provider: assume **Mapbox** (already referenced in PropIQ doc-rebuild corrections for imagery rules) — layer/pin design is provider-agnostic.
- [DECIDE] Heat-layer API pricing beyond membership — flagged open in §17.7 itself; interim: layer ships included, usage metered internally for pricing data.
- [DECIDE] Metered-scan billing UX (wallet vs per-charge) — matrix lists "Billing/metered-scan wallet" as unbuilt; interim: quote → one-tap charge to card on file, receipts in Settings→Billing.
- [DECIDE] "AI handled / time saved" computation — interim: count of Wattson-completed convo turns × average handling estimate, labeled "~".
- [DECIDE] Day-close trigger time — interim: 5:30pm local, Settings-editable.
- [DECIDE] Whether the Pipeline strip expands full kanban inline or always routes to CRM screen — interim: routes to CRM (kanban with 12-day sprint counters lives there per matrix).
- [DECIDE] Video vendor for milestone/avatar videos: assume HeyGen-class avatar API (LipDub/BeHuman candidates) — UI unaffected by vendor choice.
- [DECIDE] Mobile bottom-tab set — interim as listed [BEST GUESS].
