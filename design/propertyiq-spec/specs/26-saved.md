# 26 · Saved searches & properties (consumer)

**Purpose.** The consumer retention + alert engine: saved prompts re-run continuously and message on new matches (consent-gated, sent by PropFlow); saved homes carry notes, custom rent assumptions, strategy tags, and assumption overrides for underwriting. Both feed compliant audience segments to the agent's PropReach side — this screen is the raw material for alerts, audiences, and pipeline.

**Primary users.** Signed-in consumers (buyers, investors, homeowners watching an address). Secondary: the agent viewing a contact's saved items via PropFlow contact detail (read-only mirror, separate surface).

**Entry points.** "Save" heart on result cards / property detail; save-search inline bar on Screen 02 (incl. "Alert me when one appears" zero-result path and the "Watch this" lens closers on Screen 01); alert emails/SMS deep links ("2 new matches"); Screen 01 returning-visitor "Welcome back" card; account nav "Your saved items".

**Exit points.** Saved-search card → Screen 02 pre-filled results (or its "N new" delta view); Edit prompt → Screen 01 input state with prompt loaded; saved property → Screen 03 property detail; "re-run underwrite →" → underwriting workspace with saved assumption_overrides applied; Alert settings → notification preferences; compare from saved homes → compare screen.

## Layout

Desktop:
- **Header:** avatar + "Your saved items" + summary subtitle ("2 searches · 5 homes · alerts: instant"); nav: Alert settings.
- **Main:** two-column grid — column style shared card layout: **Saved searches** section (cards: prompt text, live match count, delta line, cadence chips, Edit prompt) and **Saved properties** section (cards: address, strategy tag badge, note, saved assumptions summary, re-run underwrite link). [BEST GUESS: sections stacked with headers rather than interleaved, searches first, since the draft shows one of each in a 2-col grid without headers — deepen to labeled sections as counts grow.]
- **Per-search delta line:** "41 matches · 2 new since yesterday · 1 price cut on a saved home".
- **Empty-state hero** when nothing saved (see States).
- Footer: standard consumer site footer.

Mobile (375px): single column; searches first; cadence chips wrap; per-card swipe actions (delete/edit) [BEST GUESS]; alert settings behind the header link.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Summary header | Counts of searches/homes + global alert mode | SavedSearch list + SavedPropertyRecord list | Alert settings link | Draft S26 |
| Saved-search card | Quoted prompt, live match count, new-since delta, price-cut cross-note | SearchRecord (persisted saved variant) re-run continuously; delta vs last visit | tap card → Screen 02; "See the 2 new" delta view | Draft S26; matrix gap "Saved searches/properties … alerts basis" |
| Cadence chips | Instant alerts / Daily digest (selected state visible) | saved-search alert preference | tap switches cadence; change routes through consent-gated PropFlow messaging | Draft S26; MB 29 (PropSearch owns no channel) |
| Edit prompt | Reopens the prompt for modification | query_text + parsed_filters | edits re-parse (same S1 parser rules), preserves the saved-search id [BEST GUESS] | Draft S26 |
| Delete/pause search | Remove or mute a saved search | — | confirm; pausing stops alerts, keeps the record [BEST GUESS] | standard save pattern (matrix: "standard save patterns") |
| Saved-property card | Address + "saved · strategy: house-hack" tag + user note + assumptions summary | SavedPropertyRecord (notes, custom_rent_estimate_monthly, assumption_overrides, investor_strategy, source_search_id) | tap → property detail; inline note edit | Draft S26; MB 10.7 |
| Strategy tag badge | InvestorStrategy label (BUY_HOLD / BRRRR / FLIP / HOUSE_HACK …) | SavedPropertyRecord.investor_strategy | change via badge menu | MB 10.7 / enums |
| Note field | Free-text user note ("ask about the sub-panel") | SavedPropertyRecord.notes | inline edit, autosave | Draft S26; MB 10.7 |
| Assumptions summary | "20% down, self-manage" + custom rent estimate | assumption_overrides + custom_rent_estimate_monthly | tap → assumptions drawer (same editor as underwriting) | Draft S26; MB 10.7/19.4 |
| Re-run underwrite link | Launches underwriting with saved overrides | UnderwriteRunRecord pipeline | → underwriting workspace; emits UNDERWRITE_RUN on completion | Draft S26; MB 19/25.1 |
| Price-change / status badges on saved homes | Price cut, pending, sold, back-on-market since save | IDX refresh (webhook/poll, stale >24h flagged) | tap → detail | Draft S26 delta line; MB 14.3 |
| Alert settings panel | Per-search cadence, channel (email/SMS), global mute, quiet hours | consumer notification prefs; SMS requires granted consent snapshot | consent-gated toggles; SMS toggle disabled until consent granted with explanation | matrix corrections (consent model); MB PropFlowContactConsentSnapshot |
| Empty state | "Nothing saved yet" + explain alerts + one-tap example searches for their market | filter-URL presets | tap fires a real search | [BEST GUESS] consistent with S1 never-dead-end principle |
| Compare-from-saved | Select saved homes into the compare tray | compare state | persists, URL-addressable | Draft S2 tray ("persists across pages & sessions") |

## States
- **Default:** populated sections with live counts and deltas.
- **Loading:** skeleton cards; counts fill progressively; stale IDX data (>24h) shows freshness warning instead of fake "live" counts.
- **Empty:** teaching empty state with example searches (never a dead end).
- **Error/degraded (fail closed):** saved-search re-run failure → card shows last-known results with "as of {date}" stamp, no fabricated deltas; rent/AVM missing on a saved home → those chips suppressed (`MISSING_RENT_ESTIMATE`/`MISSING_AVM`); ScoringService down → any fit ordering disappears, deterministic sort remains; alert channel blocked (consent unknown/denied, DNC) → cadence chip shows "alerts paused — verify your contact preferences" rather than silently not sending.
- **Permission-limited:** page requires sign-in (it's the account surface); an anonymous user who saved via localStorage sees a soft account prompt to sync across devices ("save across devices?" — never before first save, per S2 card rule).
- **Mobile:** single column, swipe actions, cadence chips as bottom sheet on small widths [BEST GUESS].

## Data fields
- Saved search: query_text, ParsedSearchFilters, result_count (live), new_since_last_visit count, alert cadence (INSTANT/DAILY/WEEKLY [BEST GUESS naming]), channel prefs, created/updated timestamps, map layer state (saved per saved-search — Draft S2).
- Saved property (SavedPropertyRecord, MB 10.7): saved_property_id, property_id, listing_id?, notes, custom_rent_estimate_monthly, assumption_overrides (UnderwritingAssumptionOverrides), investor_strategy, source_search_id, created/updated_at.
- Deltas: new matches, price cuts ($ amount), status changes — all sourced from IDX refresh, formatted with as-of dates.
- Consent snapshot (read-only, from PropFlow): sms/voice/ai_video/marketing_personalized consent + dnc_status — governs which alert channels are offered.

## Rules & compliance
- **PropSearch owns no outbound channel (MB 29):** all alert sends go through PropFlow with ComplianceProvider checks; unknown consent = blocked with a visible reason (matrix correction: "draft has no consent model — every outbound surface must run the compliance check").
- **School firewall (§16.4):** school data must never be used in saved-search alert logic or ranking of alert results — a saved school-boundary filter re-runs as the user's own filter only; alert copy avoids school characterizations and carries §16.3 disclaimers when school facts render.
- Saved searches/properties/underwrite runs feed PropSearchAudienceSegmentSupply (MB 22.2) with prohibited_inputs_removed (protected class, school data, sensitive life events, demographics) — the consumer is not shown this, but deletion of a saved item must propagate to segment criteria.
- Sensitive-topic content in a saved prompt → human_handoff_required; that topic never drives alerts, routing, or audiences.
- Retention per MB 26.3 tables; MLS-derived display honors mls_retention_expires_at and `MLS_RETENTION_EXPIRED` suppression.
- Notes/assumptions are the user's own data; never surfaced to ads; agent visibility via PropFlow follows platform privacy rules.
- No fabricated numbers anywhere: missing AVM/rent/mortgage-balance renders "unavailable" states, never estimates without provenance.

## Cross-links
In: Screens 01/02 save affordances, alert deep links (PropFlow-sent), returning-visitor card, property-detail save. Out: Screen 02 (pre-filled/delta), Screen 01 (edit prompt), Screen 03 detail, underwriting workspace, compare screen, alert settings.
Ledger/events: consumes IDX refresh (listing changes); underwrite launches emit UNDERWRITE_RUN; equity-related saved-address flows emit EQUITY_CARD_CREATED; saved-item activity logs to the event ledger as engagement signals (feeds lead heat + seller signals, agent-side); segment supply objects flow to PropReach (requires_propreach_preflight: true). PropSearch never emits LEAD_CAPTURED/PIPELINE_MOVED etc. (MB 25.3).

## Open decisions
- [DECIDE] Alert cadence enum + digest send times — interim: INSTANT/DAILY/WEEKLY, daily digest at 8am local, delivered by PropFlow inside its consent + quiet-hour rules.
- [DECIDE] Whether editing a saved prompt versions the search or mutates in place — interim: mutate in place, keep search_id, log the change (alerts continuity beats history here).
- [DECIDE] Anonymous-save sync mechanism — interim: localStorage saves migrate into the account on first sign-in; soft prompt after first save only.
- [DECIDE] Agent-side mirror of this screen — interim: read-only "saved activity" panel on the PropFlow contact detail (separate screen spec), no consumer-facing indication.
