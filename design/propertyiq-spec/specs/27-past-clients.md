# 27 · Past Client OS

**Purpose** The machine that keeps every closed client (112 enrolled today) warm for life: a canonical touch cadence spread across the year, a 13-week call rotation with a morning queue, the year heatmap, the voice-note call-logging loop, and suppression flags. Nothing lapses silently and nothing client-facing sends without review.

**Primary users** Agent (call queue, approvals), team (Sharon handwritten-note lists, Adrian briefing — interim workflow owners), Wattson (CRM_WATTSON persona, REVIEW_REQUIRED).

**Entry points** App nav "Past clients"; morning push notification (call queue); Today queue PAST_CLIENT_TOUCH tasks; automatic enrollment at close (from Transaction Workspace close wizard); contact record "Past client" chip.

**Exit points** Tap-to-call → phone dialer + voice-note logger; Review buttons → Outbox/Approvals (equity notes, CMAs, gifts); referral capture ("brother might sell") → Lead Triage/CRM; heatmap client → contact record (14); gift approval → gift queue; CMA link → hosted CMA URL.

## Layout
Desktop: **Header** — enrolled count, rotation health, touches this week; nav tabs **Today / Year heatmap / Referrals** (the spec's three v1 views §20.5: Today/This-Week board, year-at-a-glance heatmap, rotation balancer). **Main, two columns**: left (1.3fr) = today's action cards (rotation calls with context card, anniversary/birthday bundles, suppression summary); right (1fr) = 13-week rotation balancer bar chart + referral tracker card. **Below full-width**: Cadence board — every client × every touch in Week/Month/Year/By-person views with touch-type filter chips; beneath it Template-library card and Auto-CMA engine status card.
Mobile (375px): the **call-assistant flow is the primary mobile surface** — morning queue as swipeable cards (context card → Tap-to-call → hold-mic voice note → transcribed summary → one-tap confirm). Balancer and cadence board collapse to vertically stacked, horizontally scrollable strips. Heatmap = pinch-zoomable full-screen view.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Rotation call card | Client due this week (rotation wk N of 13) + context card: bought year, equity delta, life details from last notes ("deck project — ask how it turned out") | PastClientRecord §20.2 (call_rotation_week, last_relationship_call_at) + timeline notes | Tap-to-call; after-call voice-note loop | PF MB 20.2, 20.6 |
| Voice-note logging loop | Hold mic → speak outcome → transcribe/summarize → read-back → one-tap confirm → call log written, last_relationship_call_at stamped; mentions of new people become referral leads in Triage | Conversational Call Assistant §20.6 (WPB-PCOS-conversational-call-assistant) | Confirm / edit / re-record; unlogged call → end-of-day reminder, then next-day follow-up until complete | PF MB 20.6; Playbook Library registry |
| Anniversary/birthday bundle card | e.g. "Nguyen home anniversary Thu — equity note drafted + gift suggestion under cap" — avatar video + note + gift as ONE bundle, one approval | PastClientTouch §20.4 (BIRTHDAY_TOUCH, CLOSING_HOME_ANNIVERSARY_TOUCH) + GiftProvider §9.15 | "Review both/all" → Approvals; gift default REVIEW_REQUIRED | PF MB 20.4, 19.8; draft §27 |
| Suppression card | Active suppressions with reason: in-escrow (no marketing touches), sensitive-topic hold, requested-space window with auto-resume date | Touch governance §13.9 + sensitive firewall §22.4 | Sensitive holds resume only on explicit agent clearance; timed holds auto-resume | Draft §27 (inherited); PF MB 22.4 |
| 13-week rotation balancer | Bar per week (clients assigned); light weeks flagged | call_rotation_week distribution | Balancer proposes rebalancing ("pull 5 forward from week 5") — agent accepts/declines; never silent | PF MB 20.5; draft §27 |
| Touch-mix legend | Per person/year: 4 quarterly calls, monthly newsletter (12), market digest every 2 months, CMA/equity touch every 6 months, birthday, home anniversary, handwritten-note prompts | Canonical Cadence §20.3 table (owners: WPB-PCOS-quarterly-call, -monthly-newsletter, -bimonthly-market-touch, -annual-cma-email, -birthday-touch, -anniversary-video, -handwritten-note) | — | PF MB 20.3 + Playbook Library cadence table. Note: draft's "2 handwritten notes" count is [BEST GUESS] — spec says prompts fire on referral/close/milestone/annual moment, not a fixed 2 |
| Referral tracker card | New edges, thank-yous queued (review-gated), A-grade referrer count, YTD referral GCI | ReferralEdge §19.2, ReferrerGradeSettings §19.5 | Open Referrals dashboard (left-to-right referrer→referee list; force-graph is out of scope v1) | PF MB 19.4, 19.5 |
| Cadence board | Clients × week grid, every scheduled touch as a cell; Week/Month/Year/By-person toggle; filter chips (calls, notes, gifts, videos, CMAs, custom) | next_touch_schedule (PastClientTouch[]) | Cell click → touch detail (status SCHEDULED/DUE/OVERDUE/COMPLETED/CANCELLED, permission mode, template); suppressed rows render greyed with reason | PF MB 20.4; draft §27 |
| Template library + build-your-own | Stock touch templates + plain-English custom cadences ("pool clients: pool-service reminder each May") → Wattson builds template, applies to matching clients, **shows first instance before it ever runs** | PipelineSequenceRegistry + CUSTOM touch_type | Create/edit; approval required before first run | Draft §27 (locked decision); PF MB 20.4 CUSTOM |
| Auto-CMA engine status | Generated/sent/in-Outbox counts, next batch due, opens ×N → seller-signal flags | cma-generator pipeline (WPB-PCOS-annual-cma-email); hosted URL per client owner page | Open Outbox items; opens feed propensity (agent_marketing_engagement fact §14.4) | Draft §27; PF MB 14.4 |
| Year heatmap tab | Every client's touch position/coverage for the year at a glance | touch_history + next_touch_schedule | Click client → record; gaps visually flagged | PF MB 20.5 |
| Morning push | Daily call queue + handwritten-note prompts + CMA touches for review, via NotificationProvider | §20.6 morning workflow | Deep-links into this screen | PF MB 20.6 |
| Enrollment banner (contextual) | New close auto-enrolled: status active, anniversary set, rotation week assigned, touches scheduled, referral grade carried | §20.7, idempotency {transaction_id, contact_id, close_date} | Review/adjust rotation week | PF MB 20.7 |

## States
- **Default**: today's cards + balancer.
- **Loading**: skeleton cards; heatmap renders progressively.
- **Empty**: no clients enrolled → "Past Client OS activates automatically at your first close" + manual-enroll action; no touches today → "Nothing due — next: {touch, date}".
- **Error/degraded (fail-closed)**: transcription unavailable → voice note saved as audio + manual-log form, task stays open until logged; cma-generator failure → touch flips to review task, never a fabricated CMA; ComplianceProvider down → all outbound touches (newsletter/digest/video) held with reason; equity unknown → equity line renders "estimate unavailable"/prompts mortgage-balance entry, never guessed.
- **Permission-limited**: handwritten-note lists routable to a team member; gift approvals restricted to approver role; sensitive-suppressed clients hidden from team queues.
- **Mobile**: call-assistant flow as above.

## Data fields
PastClientRecord §20.2: past_client_status, past_client_os_active, close_date, home_anniversary_date, birthday, primary_address, geo_code, referral_grade (A/B/C), call_rotation_week (1–13), last_relationship_call_at, last_cma_equity_touch_at, last_market_update_at, last_newsletter_at, next_touch_schedule[], touch_history[]. PastClientTouch §20.4: touch_type (14 canonical types incl. POSTCARD, POP_BY_PROMPT, HOLIDAY_GIFT_PROMPT, CLIENT_APPRECIATION_EVENT_INVITE, CHARITABLE_DONATION_PROMPT, E_CARD, CUSTOM), due_at, fixed_date, status, step_permission_mode, template_id. TouchHistory: completed_by (HUMAN_USER/WATTSON_REVIEWED_ACTION/SYSTEM), outcome_summary, next_action. Gift: budget cap from ReferrerGradeSettings-adjacent gift settings ($45 in draft = example value, cap is a tenant setting §19.8).

## Rules & compliance
- Every outbound touch passes ComplianceProvider + channel consent + DNC (§22.1–22.3); touch_ledger_lock prevents collisions with sprint/drip/video touches (§13.9) — collision suppressions shown on the calendar.
- Client-facing content (CMAs, newsletters, equity notes) is review-first: lands in Outbox for agent review, never auto-sends to the client (Bucket 2, §17.3).
- Gifts: default REVIEW_REQUIRED; AUTO_WITHIN_BUDGET only with a configured cap + approved vendor; no vendor → manual one-click task (§19.8).
- Sensitive-topic hold: only human clearance resumes; no automation touches the contact (§22.4).
- Wattson receives only structured, minimized contact context in the call assistant (§20.6).
- Board priority order: overdue → due today → due this week → referral_grade → past-client value (§20.5).
- AI-generated anniversary videos carry the ai_video consent gate + non-removable CA AI disclosure (§21.7; matrix correction #3).

## Cross-links
In: close wizard (15) enrollment, Today queue, morning push, CRM contact chip. Out: CRM record (14), Referrals dashboard, Outbox/Approvals, gift queue, hosted CMA URLs, Prospecting (equity-touch opens feed seller propensity). **Emits**: PAST_CLIENT_TOUCH activities, touch-completion history, REFERRAL_RECEIVED (from call notes), CMA sent/opened events. **Consumes**: DEAL_CLOSED/closing detection (§18.2), PORTAL/CMA view events, suppression flags, scoring facts.

## Open decisions
- [DECIDE] Interim vs Temporal cadence owner: current N8N/interim crons (Daily Call Email Mon–Fri 10:00, anniversary batch 24th, CMA weekly digest Mon, bimonthly market update, birthday 24th, Sharon weekly notes, Adrian briefing) migrate to Temporal cron per Playbook Library — UI shows owner-agnostic status; interim design assumes Temporal names.
- [DECIDE] Handwritten-note annual count: interim = prompt-driven (referral/close/milestone/annual), surfaced as ~2/yr in the mix legend [BEST GUESS].
- [DECIDE] Rotation size math: 112 clients / 13 weeks ≈ 8–9 calls/week (draft says "~22-client weekly rotation" in the interim workflow — that figure includes multi-touch weeks). Interim: balancer displays actual per-week counts, no hardcoded target.
- [DECIDE] Gift vendor: assume GiftProvider-abstracted vendor (Handwrytten/Loop-&-Tie-class) — UI unaffected by vendor choice.
