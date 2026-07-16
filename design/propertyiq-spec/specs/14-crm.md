# 14 · CRM (Contacts + Pipelines)

**Purpose** The working CRM: pipeline boards (New Leads 12-day sprint, Buyer, Seller, Past), the contact record with evidence-labeled timeline and consent panel, smart lists with a dialer work mode, and the four-panel conversation inbox. Every action is a ledger event; consent gates every outbound.

**Primary users** Agent (Graeham), team members (ISA/coordinator roles via role-based task queues). Wattson writes here only via governed actions (`WATTSON_REVIEWED_ACTION`).

**Entry points** Left app nav "CRM"; deep links from Today queue cards, Approvals items, Prospecting rows ("Open contact"), Past Client OS names, seller-report/valuation viewer alerts, lead-intake notifications, global search.

**Exit points** Contact → Transaction Workspace (Screen 15) when moved to UNDER_CONTRACT; → Past Client OS (27) on close; → Prospecting (28) via "why this score" → candidate card; → Approvals inbox for any Bucket-2 message; → Calendar for bookings; composer send → contact timeline.

## Layout
Desktop: **Left rail** (150px) — CRM sub-nav: Conversations (badge = unread), Contacts (count), Opportunities (active), Calendar, Cadences, Automations, Reporting; below it pinned **smart lists** with live counts ("No touch 30d (7)", "Valuation viewers (4)", "Hot investors (3)"). **Main** — top toolbar (pipeline selector, aggregate badge "46 opportunities · $1.9M GCI potential", advanced filters, sort, bulk actions, Board/List toggle, dedupe-reviewed Import, search); below it the kanban board (one column per stage) or virtualized list; an expanded contact record renders inline below the board when a card is opened (bordered panel, not a modal). **Contact record** is three-zone (Attio pattern): pinned header/action bar → stage Path ribbon → two columns (timeline left 1.5fr, context cards right 1fr, collapsible). **Inbox view** is four-panel (GHL pattern): conversation list | thread | contact context | composer.
Mobile (375px): sub-nav collapses to a bottom tab bar (Conversations / Contacts / Boards / Calendar); boards become horizontally swipeable single columns; contact record becomes full-screen with sticky action bar at bottom; work mode becomes the dialer flow (one contact per screen, swipe to advance). Density toggle (36–40px rows) desktop-only.
Performance is a product KPI (draft §14, inherited): lists <500ms, record open <1s, virtualized timelines.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Pipeline selector | NEW_LEADS / BUYER / SELLER / PAST_BUYERS / PAST_SELLERS / LOST (investor pipeline = GHL interim, shown as external link chip) | PropFlow §11.1 PipelineId | Switch board | PF MB 11.1 |
| Kanban board / list toggle | Same collection rendered as board, list, or grid | PropFlowActivity + contact records ("collections" primitive) | Drag card = PipelineMoveRequest → PIPELINE_MOVED event; column headers aggregate count + $ volume | PF MB 11.4; draft §14 Attio card |
| 12-day sprint counter chip | "Day 9/12" per New Leads card; warn ≥ day 9, critical day 11+ | NewLeadStageId + lead created_at | Day 12 unresolved → forced disposition dialog (qualify / long-nurture / archive) creating DAY_12_REVIEW task | PF MB 11.2 |
| Card micro-stats row | 📞 💬 ✉ 👁 ☑ 📅 live counts + last-touch age | PropFlowActivity counts | Click an icon → timeline filtered to that channel | Draft §14 (GHL pattern) |
| Neglect watchdog column/widget | Leads past stage-tuned inactivity threshold | Temporal watchdog (runs every 6h) → NEGLECT_FOLLOW_UP tasks | Click → Today queue task | PF MB 11.5 (thresholds configurable per account; exact defaults [BEST GUESS: 48h hot / 7d warm / 30d nurture] — table blank in converted doc) |
| Smart lists (left rail) | Saved ledger queries with live counts | Event Ledger queries | Click → list; "Work mode" button starts dialer session (contact 1 opens, log inline, keystroke advances) | Draft §14 FUB card |
| Contact header | Name, property, in-CRM-since, source chain (e.g. "farm postcard → valuation page") | Contact record + Attribution Mirror §5.5 | — | PF MB 5.3/5.5 |
| Pinned action bar | Call / Text / Email / Note / Task buttons | — | Each opens an INLINE composer below it, never a modal; call opens live notepad + outcome picker (connected/vm/bad number); outcome = ledger event feeding Today ranking | Draft §14 (locked decision) |
| Score badges | Seller propensity (e.g. 87) + lead score, "why?" affordance | ScoringService mirror §5.6 | Click → explainability card (contributing source_facts) | PF MB 5.6, 14.7; matrix gap "score badges with explain-on-click" |
| Stage Path ribbon | Chevron stages with current highlighted | BuyerSellerStageId §11.3 | Click stage = PipelineMoveRequest; stage guidance line below is Wattson-generated from THIS record (key fields known/unknown) | Draft §14 (Salesforce Path, made live) |
| Timeline | Append-only activity, every entry labeled by evidence: DETERMINISTIC / INFERRED / ANONYMOUS_STITCHED / CAMPAIGN-LEVEL / HUMAN | PropFlowActivity §11.7 + stitch-on-capture §10.7 | Filter by channel; ad entries only campaign/audience-level (impression honesty — never "she saw it") | PF MB 11.7, 10.7; matrix PropFlow gap #1 |
| Consent panel | 4 channels (SMS, voice, ai_video, marketing_personalized) each with status + evidence (date, source, text, proof URL); DNC badge + last scrub date | ContactConsentMirror §5.4 | Hover/expand evidence; "not asked" states show Wattson's plan to ask | PF MB 5.4 |
| Equity card | Equity % with provenance ("balance from her statement, not guessed") | Financial Mirror §5.7 | Missing mortgage balance → MISSING_MORTGAGE_BALANCE manual-entry prompt, never fabricated | PF MB 5.7; matrix correction #7 |
| MLS whitelist panel | Which MLS data this contact may be shown | MLS Whitelist Mirror §5.8 | Read-only | PF MB 5.8 |
| Referral section (skinny) | Edges in/out, grade | ReferralEdge §19.2 | Refer button → link/create referee; link to Referrals dashboard | PF MB 19.3/19.4 |
| Tasks tab | Open PropFlowTask items typed by reason (NEGLECT_FOLLOW_UP, DAY_12_REVIEW, DUPLICATE_REVIEW, SENSITIVE_TOPIC_HANDOFF, …) | PF MB 11.6 | Complete/cancel; priority badges | PF MB 11.6 |
| Composer (shared everywhere) | Channel tabs, merge-field templates, "Wattson draft", SMS segment counter | MessagingProvider §9.7 + PipelineSequenceRegistry | **Consent gate IS the send-button state**: missing consent/DNC/compliance fail = disabled with reason shown; Bucket-2 messages route to review queue | PF MB 17.3, 22.2; draft §14 |
| Lead inbox + intake outcomes | New accepted leads with dedupe_result | /approved-leads §10.3–10.4, LEAD_CAPTURED | — | PF MB 10 |
| Duplicate-review queue | REVIEW_REQUIRED_PHONE_EMAIL_CONFLICT and probabilistic matches, side-by-side candidate contacts | Identity resolution §10.5 | Merge / keep-separate buttons; NEVER auto-merge in v1 | PF MB 10.5 |
| Import button | "Import (dedupe-reviewed)" | — | CSV import → every row through identity resolution; imported contacts default unknown consent (blocks outreach) | PF MB 5.4, 10.5 |
| Cadences nav item | Sequence/template registry with approval status | PipelineSequenceRegistry | Missing approved rows render as blocking state — copy is loaded, never invented | PF MB 11.2, 13.5 |
| Emergency stop | Wattson pause control (surface in Automations) | §17.4 (Temporal cancel/pause + connector.stop) | Confirmation; also lives in Admin | PF MB 17.4 |
| Wattson audit link | Per-action audit records on the contact | WattsonActionAuditView §17.5 | Filter by playbook/outcome | PF MB 17.5 |

## States
- **Default**: board with live counts; record collapsed.
- **Loading**: skeleton rows/cards; KPI budget — show cached counts instantly, hydrate.
- **Empty**: "No opportunities in this pipeline" + Add contact / Import; smart list empty = "0 match — criteria shown".
- **Error/degraded (fail-closed)**: ScoringService down → score badges disappear entirely (never stale/fabricated), deterministic fields remain; ComplianceProvider unreachable → all send buttons disabled with "compliance check unavailable — sends blocked" (fail-closed, PF MB 22.1); GHL sync degraded → banner "mirror stale as of {t}", writes queue.
- **Permission-limited**: team roles see role-routed task queues; Bucket-2 approvals only for users with approval rights; sensitive-topic contacts show "no automation will touch this contact" notice and hide automation controls.
- **Mobile**: dialer work mode; inline composers become bottom sheets.

## Data fields
Contact core (§5.3): name, phones/emails (normalized), address, geo_code, lead_source/capture_source/conversion_source/capture_provider, first/last/originating_content_id, campaign_id (Attribution Mirror §5.5 — six canonical attribution fields; legacy aliases import-only §6.3). Consent: 4 × {status, evidence_at/source/text/proof_url}, dnc_status, dnc_last_scrub_at. Scores: lead_score, likelihood_to_list_score, seller_likelihood_tier, data_quality_confidence (Scoring Mirror §5.6 — display only, formula in Scoring Master Sheet). Pipeline: pipeline_id, stage_id, move history (PIPELINE_MOVED events with mover identity). Task: PropFlowTask full schema §11.6. Activity: PropFlowActivity §11.7 incl. retention_class per entry. Money: est. GCI per opportunity (column aggregates).

## Rules & compliance
- Consent before every send (§22.2); DNC (§22.3); required compliance route through ComplianceProvider (§22.1) — all fail closed.
- Two-bucket messaging (§17.3): locked transactional templates may auto-send; anything discretionary/Wattson-written = REVIEW_REQUIRED.
- Sensitive-topic firewall (§22.4/§14.3): detection produces ONLY human_handoff_required; no field writes, tags, scores, audience inclusion, or outreach-priority changes.
- Fair Housing/FEHA (§22.5): no protected-class fields anywhere in UI; pricing-floor qualifier (§13.8) is the only price-qualification pattern.
- Copy never invented: all sequence/drip/warm-sequence copy loads from PipelineSequenceRegistry; missing rows → tasks, not messages.
- Touch governance (§13.9): touch_ledger_lock prevents stacked touches across sprint/drips/PCOS/videos/voice — UI shows "held: touch lock" reason when a step is deferred.
- No auto-merge; imported contacts = unknown consent.

## Cross-links
In: Today queue, Approvals, Prospecting, Voice Ops (call logs → timeline), Seller report PORTAL_VIEWED alerts. Out: Transaction Workspace (15), Past Client OS (27), Prospecting (28), Referrals, Calendar, Approvals inbox. **Emits**: LEAD_CAPTURED, PIPELINE_MOVED, task/activity events, COMPLIANCE_BLOCK, REFERRAL_RECEIVED. **Consumes**: scoring snapshots, PAGE_VIEWED/CONTENT_VIEWED/LINK_SCANNED (warm sequence §13.7), booking events, stitch backfills.

## Open decisions
- [DECIDE] Neglect-threshold defaults: converted doc's table is blank. Interim: ship configurable per-account with [BEST GUESS] defaults 48h (New Leads/hot), 7d (active buyer/seller), 30d (nurture); watchdog cadence fixed at 6h per spec.
- [DECIDE] Investor pipeline: spec defers native build — interim design shows an "Investor (GHL interim)" chip that deep-links to GHL, plus review-task routing.
- [DECIDE] Board card fields: user-picked 3–5 fields per Attio pattern — interim default: name, sprint-day/stage-age, source, est. GCI, last touch.
- [DECIDE] Conversations inbox unification with Voice Ops transcripts — interim: voice transcripts render as timeline entries with a player link; full thread merge later.
