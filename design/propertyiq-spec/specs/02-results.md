# 02 · Results

**Purpose.** The split map/list results surface where a parsed search becomes explorable inventory: explainable "Matches N of M" intelligence strips with honest misses, all-in monthly cost at card level, the six lenses carried through as active filters, a sticky conversational refine dock, and the save-search capture that feeds alerts, audiences, and the agent's pipeline. Curated indexed versions of this page are also the organic-traffic landing surface.

**Primary users.** Consumers (buyer/investor/cautious/homeowner personas), anonymous or signed-in; Google visitors landing on curated slug pages; the agent demoing.

**Entry points.** Screen 01 search submit / pills / lens flows / signals rows; curated indexed slug pages (`/{city}/homes-under-{price}` etc., via IDXFilterUrlRecord); saved-search "See the N new" from Screens 01/26 and alert messages (sent by PropFlow); community-page preset links; PropReach ad + QR destinations; shared/compare URLs (URL-addressable state).

**Exit points.** Card click → Screen 03 property detail; Compare tray → compare screen; save-search flow → Screen 26 (+ optional owner-address step → owner report/seller-signal); "re-run underwrite"/investor actions → underwriting workspace; browse-block preset chips → sibling curated pages; neighborhood cross-link cards → community pages; Edit search → Screen 01 state.

## Layout

Desktop:
- **Header:** avatar + the query text echoed as the subtitle; nav: Edit search · Save.
- **Lens chip bar:** same six lenses as Screen 01 (mental model carries through); active lenses show their parameter inline (tap to edit); activating a new lens runs its one-question flow in place; lens-specific sub-toggles (fire/flood/quake, transit/walk, price-cut window) appear contextually inside the active lens only.
- **Split view:** left = interactive map (overlay tag naming active overlays, price pins, cluster bubbles, legend); right = results column: result-head (count · labeled sort · freshness stamp · List/Grid/Table/Map-only view switch), cards, inline save-search bar (after 60s or 8 cards), browse-block preset chips (end of list), sticky floating refine dock (pinned above compare tray), compare tray (bottom, dark).
- **Below results (curated pages only):** dated intro paragraph (AI-citation block), slug-minting library block, browse nearby searches, neighborhood cross-link cards, footer.

Mobile (375px): map collapses behind a floating "Map" pill; cards full-width; lens bar horizontal scroll; refine dock docks above the Map pill, collapsible to a pill; compare tray condenses to a count button; table view horizontally scrollable.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Query echo header | The active prompt as subtitle | SearchRecord.query_text | Edit search returns to input state | Draft S2 |
| Lens chip bar | Active lenses w/ inline parameters + inactive lenses | SearchRecord.parsed_filters | tap active = edit param; tap inactive = one-question flow; sub-toggles contextual | Draft S2 chips note |
| Map + pins | Price pins, hot pin state, cluster bubbles >40 pins | IDXListingRecord positions | card hover ↔ pin highlight (120ms, bidirectional); pin click → mini-card popover → detail; zoom expands clusters | Draft S2 map interactions |
| Overlay tag + legend | Names active overlays; ONE heatmap at a time with its own persistent legend | active lens layers | layer state saved per saved-search | Draft S2 note (Zillow/First Street pattern) |
| Draw-a-boundary tool | Freehand + polygon draw becomes a location chip | map UI → geo filter | draw → chip added, search re-runs | Draft S2 map interactions |
| "Search as I move the map" toggle | Re-query on pan/zoom | user pref, remembered | toggle | Draft S2 |
| Result head | "47 matches · Sorted by: Best match ▾ · data as of 6 min ago" | result_count, sort_mode, IDX freshness | sort menu; view switch | Draft S2; MB SearchSortMode |
| Sort menu | Best match (default, labeled) · Price ↑↓ · Newest · $/sqft · Rent yield · Match-miss count | SearchSortMode enum (USER_SELECTED_* / SCORING_SERVICE_INVESTOR_FIT / DEFAULT_DETERMINISTIC) | select re-orders | Draft S2; MB 8/10.6 |
| View switch | List / Grid (photo-forward) / Table (investor: sortable price, $/mo, yield, cap, DOM, zoning upside) / Map-only | — | Table columns follow pinned "what matters to me" dimensions | Draft S2 sort & views |
| Result card | Photo carousel → price → all-in $/mo → facts → intelligence strip → badges → compare/save/hide (locked order) | SearchResultRecord + deterministic_preview_metrics | hover arrows, dots, lazy-load; heart save; hide with visible undo (teaches ranker) | Draft S2 card anatomy |
| All-in monthly cost | $/mo incl. taxes+insurance+HOA at card level | CashflowEstimateSnapshot deterministic math | tap → breakdown [BEST GUESS: popover with line items] | Draft S2 note (differentiator) |
| Intelligence strip | "Matches 5 of 5 ▾" + why one-liner incl. honest misses ("miss: busier street than you asked for") | criteria checklist vs parsed_filters; ordering from ScoringService only | tap expands checklist | Draft S2 note + expanded state |
| Expanded checklist | Per-criterion ✓/miss with evidence + source date; each criterion editable in place | source_facts (SourceFact[]) per result | edit link re-runs; "closest miss to add" hint | Draft S2 expanded state |
| Badges | New (2d), Low fire risk, Rent est. $/mo, Yield %, HOA $/mo, ADU potential — relative-to-market framing | rent/risk/zoning/HOA data with provenance | tappable → badge converts to a filter (capability-discovery rule) | Draft S2 + S1 discovery rule |
| Compare checkbox + tray | Persistent tray: thumbnails, ✕ remove, + add, "Compare N →" | selection state | persists across pages & sessions; URL-addressable; "text the link to a spouse" | Draft S2 compare tray |
| Save-search inline bar | "Want these updates?" + Instant/Daily/Weekly chips; appears once after 60s or 8 cards, never a popup, dismiss remembered forever | — | choose cadence → email capture → SavedSearch created | Draft S2 |
| Save flow step 2 (dual capture) | Optional "Own a home now?" address question → instant value + equity-in-budget | AVM/EquityCard pipeline | skippable one-liner, never blocks save; answer → seller signal in Command Center + owner report page auto-created | Draft S2 (Real Geeks dual-capture) |
| Refine dock (chat) | Sticky floating conversational refinement with structured suggestion buttons in replies | NL parser (same rules as S1) | send → filters mutate with explicit delta narration ("6 homes removed, 41 remain") + counter-offer chips | Draft S2 refine dock |
| New-match live pill | "1 new match" injects at top, never reflows scroll | IDX webhook/poll | tap reveals | Draft S2 states |
| New-since-last-visit accent | Subtle top accent bar on new cards | saved-search delta | — | Draft S2 |
| Browse-block preset chips | One-tap sibling curated searches with live counts | IDXFilterUrlRecord library | navigate; end-of-list + footer only, never above results; clicks pixel-tracked → retargeting segments | Draft S2 |
| Curated-page intro | Dated stats paragraph, refreshed daily (AI-citation) | MarketDataSnapshot + live counts | curated indexed pages only; dynamic results skip it | Draft S2 |
| Slug-minting block | How prompts become indexed pages; example slugs | filter-URL library + prompt-parse logs | agent-facing explanation; pages auto-retire (410) after 90 days of zero inventory | Draft S2 |
| Neighborhood cross-links | Per-neighborhood match counts + medians | results aggregation | → community pages | Draft S2 |
| Zero-after-lenses recovery | "Your lenses filtered out all 47" + which lens did it + relax chips + live-count preset escape hatches + "Watch for new matches" | relaxation logic | one tap always lands on live inventory | Draft S2 dead-end recovery |
| Entry-landing variant | H1 matches query, dated intro, preset rendered as normal editable chips | IDXFilterUrlRecord | visitor is IN the real search, not a brochure | Draft S2 entry-point block |

## States
- **Default:** list view, Best-match sort (explicitly labeled), lenses from the parse active.
- **Loading:** skeleton cards; `progressive_loading` — SearchStatus PENDING→PARSING→RUNNING→PARTIAL→COMPLETE; PARTIAL renders available rows with a loading tail.
- **Empty (hard zero):** Screen 01 State-4 relaxer pattern inline. **Filtered-to-zero by lenses:** dedicated recovery card naming the responsible lens + preset escape hatches (never ends the session).
- **Error/degraded (fail closed):** ScoringService unavailable → `SCORING_SERVICE_UNAVAILABLE`: "Best match" sort disappears from the menu, falls back to DEFAULT_DETERMINISTIC/user sorts, match-count strips downgrade to deterministic criteria checklists only, no fabricated score. Rent estimate missing → `MISSING_RENT_ESTIMATE`: yield badges suppressed, never guessed. Zoning low confidence → cautious language or suppressed ADU badge (17.2). Risk provider down → risk badges/layer hidden with "score unavailable". IDX stale >24h → freshness warning. FAILED search → retry card.
- **Permission-limited:** anonymous = full search; detailed sold comps require authenticated + authorized session (`SOLD_COMPS_AUTH_REQUIRED`) — public pages show aggregates only. IDX license restrictions (`IDX_LICENSE_RESTRICTS_DISPLAY`) suppress restricted fields per listing.
- **Live-update:** "1 new match" pill; no scroll reflow.
- **Mobile:** map pill, docked refine chat, condensed tray (see Layout).

## Data fields
- Per card: list_price ($X,XXX,XXX), address, beds/baths, sqft, all-in monthly (sum: PITI at current-rate assumption + taxes + insurance + HOA) [BEST GUESS on the exact PITI assumption surface — deterministic per MB 14.4 allowed-metrics; assumption visible in the breakdown popover], rent_estimate_monthly (+ comp-count provenance), gross yield/cap_rate/cash_on_cash/DSCR (investor mode), DOM, HOA $/mo, risk scores 1–10 with provenance, new-listing age, criteria checklist with per-fact source + as-of date.
- Result envelope: SearchResultRecord (sort_position, deterministic_preview_metrics, scoring_service_output nullable, source_facts, compliance_flags, manual_review_flags).
- Sort: SearchSortMode values only; sort_position is never a locally computed score (MB 10.6).
- Save-search capture: email (+ optional cadence INSTANT/DAILY/WEEKLY [BEST GUESS enum naming], optional owner address); lead submission goes through PropFlow `/approved-leads` with lead_source "IDX", capture_source "IDX_FORM".

## Rules & compliance
- PropSearch computes only the MB 14.4 allowed deterministic metrics locally; investor_fit/opportunity/motivated-seller/lead scores must come from ScoringService or not appear at all.
- School data: never in default ranking, never in saved-search alert logic, never in audiences (§16.4); school-filtered results carry §16.3 disclaimers; school-page retargeting pools merge into the general buyer audience only, never used for ad targeting.
- No crime layer. One heatmap at a time. Facts-not-characterizations wording (MB 16.1).
- Dynamic result pages `noindex, follow`; curated pages indexed with ItemList schema, real paginated URLs (`?page=2`, self-canonical), caps 250/market & 5000 global, auto-retire 410 after 90 days empty.
- Tracking: Meta Pixel + CAPI + GA4 on-page; internal clicks carry click-source attribute; Switchy short links reserved for OFF-site surfaces only.
- Save/alert messaging is sent by PropFlow with ComplianceProvider checks + consent; PropSearch owns no outbound channel (MB 29). Imported/unknown consent blocks outreach.
- Hide/save signals may feed re-ranking but never protected-class or school-derived features.
- MLS-derived fields passed to GHL/PropFlow limited to the 14.6 whitelist with mls_retention_expires_at.

## Cross-links
In: Screen 01, curated slugs, alerts (PropFlow-sent), ads/QRs, community pages, shared compare URLs. Out: Screen 03 detail, compare screen, underwriting workspace, Screen 26 Saved, community pages, sibling curated pages.
Ledger: search itself is a SearchRecord (no canonical event); saved-search creation feeds PropSearchAudienceSegmentSupply (SAVED_SEARCH basis) to PropReach; lead capture events (LEAD_CAPTURED) emitted by PropFlow only; page visits log to the event ledger for lead heat + seller signals; owner-address step triggers EQUITY_CARD_CREATED downstream.

## Open decisions
- [DECIDE] All-in monthly rate assumption source — interim: current conforming 30-yr average refreshed daily, shown in the breakdown popover with as-of date; never silent.
- [DECIDE] Alert cadence enum + quiet hours — interim: INSTANT/DAILY/WEEKLY delivered by PropFlow within its consent + compliance gates; PropSearch stores the preference on the saved search.
- [DECIDE] "Hide teaches the ranker" feature set — interim: hide events feed only deterministic re-ranking heuristics (price band, street type), pending ScoringService personalization definition (`PROPSEARCH_INVESTOR_FIT_NOT_DEFINED` guard).
- [DECIDE] Compare-link sharing auth — interim: unlisted URL-addressable compare state, read-only, no PII embedded.
