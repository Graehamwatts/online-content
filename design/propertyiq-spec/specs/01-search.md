# 01 · Search entry page

**Purpose.** The public, agent-branded front door of PropSearch: one natural-language input that also handles addresses, filters, and research questions, wrapped in a page that teaches the six differentiating "lenses" and captures anonymous visitors into saved searches and homeowner signals. It is simultaneously the SEO homepage for the agent's market and the top of the lead funnel.

**Primary users.** Anonymous consumers (buyers, homeowners, investors) arriving from Google, ads, postcards/QRs, and social; returning signed-in consumers; the agent when demoing.

**Entry points.** Direct domain (`https://{agentdomain}/search`, canonical), organic Google (WebSite+SearchAction schema), community-page links, curated "popular search" slug pages, Switchy short links/QRs from postcards & signs (UTM-carrying), PropReach ad destinations, nav "Search" from every consumer screen.

**Exit points.** Every search/pill/lens/signal-row/address → Screen 02 Results (POST /api/propsearch/search); address detection → property report card → Screen 03 property detail / owner report; "See what it's worth" → owner/equity capture flow; classic-search link → filter-panel variant of Screen 02; community-page links → community screens; "Alert me" / save actions → Screen 26 Saved (after capture); footer links → sell page, about, every community page.

## Layout

Desktop (top → bottom):
- **Site header (sticky):** agent avatar + name + brokerage (from identity.json brand vault), nav: Search · Communities · Sell · About; quiet ES/EN language toggle; market ticker strip beneath header (median · actives · DOM, links to community pages).
- **Hero:** ambient 3D farm-map demo behind the H1 (cycles one lens every 4s: commute isochrone → school boundaries → ADU parcels amber; pauses on interaction; respects `prefers-reduced-motion`; paints as static composite first, hydrates after idle; if live map misses 1.5s the static frame stays). H1 `"{Market}, already mapped."` (market auto-fills per agent). Sub-line explaining plain-English capability.
- **The ONE primary input** (prompt bar) with mic button + Search. Address mode / prompt mode / question mode are detections, not separate boxes.
- Trust line: "Live MLS data · no sign-up to search · your info is never sold to other agents" (links to privacy-promise page); homeowner hook line "Own a home here? See what it's worth →".
- **Lens chip row:** exactly six named lenses (Commute, School Boundaries, ADU Check, Yield Engine, Risk Lens, Market Signals) + "Explore map" chip. Live counts per market; counts under 10 hide, chips never disappear.
- **Parsed-as chip row** (post-parse): each parsed filter as an editable/removable chip.
- **Example pill row:** four persona pills (investor / buyer / cautious / market), never two from the same lens, rotated per visit, localized with live data; each fires a real search instantly.
- **Two-up card row:** "Any address is a query" explainer card · "This week in {market}" signals card (auto-generated weekly; rows deep-link to pre-filled searches).
- "Prefer filters? Use classic search" link.
- **Below-the-fold SEO block:** one prose paragraph (city + homes-for-sale keywords + neighborhood internal links, never a keyword wall); "Popular searches" curated indexed slug chips; trust row (MLS-direct badge, review stars); footer: "Powered by PropertyIQ" + "MLS data updated N min ago" freshness stamp; footer links to every community page + sell page.

Mobile (375px): header collapses to avatar + hamburger; hero demo replaced by static composite; input full-width, 16px+ font (prevents iOS zoom); mic prominent; lens chip row becomes horizontal scroll with the last chip half-cut ("there's more →" affordance); two-up cards stack full-width; chips 44px touch targets.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Agent header/brand | Name, brokerage, DRE-bearing footer | identity.json brand vault (read-only) | nav links | Draft S1; CLAUDE.md brand rule |
| ES/EN toggle | Full-UI language switch (not just prompts) | user pref (localStorage/profile) | tap toggles | Draft S1 guardrail 2 (EPA farm requirement) |
| Market ticker | median · actives · DOM | MarketDataSnapshot (daily refresh top markets) | rows link to community pages | Draft S1 inventory; MB 10.8, freshness table |
| Ambient hero demo | Cycles 3 lens visualizations | Mapbox imagery (primary; Google Earth blocked for marketing) + zoning/school/commute layers | pauses on interaction; reduced-motion static | Draft S1; MB 12.6, MAPBOX_LICENSE flag |
| H1 + sub | Market-specific brand headline | brand vault market name | — | Draft S1 SEO spec |
| Primary prompt input | NL query / address / question, cycling typed-out placeholder (4 prompts, 2.5s hold, instrumented rotation) | — | type, voice mic, Enter/Search → POST /api/propsearch/search | Draft S1 State 1; MB 24.1 |
| Typing suggestions | Full-prompt completions ranked first, places demoted below divider | prompt-completion service + geocoder | tap fills & fires | Draft S1 State 2 |
| Parsed-as chips | Deterministic parse echo, each editable/removable | SearchRecord.parsed_filters (ParsedSearchFilters) | ✕ removes filter, tap edits; re-runs search | Draft S1 State 3; MB 10.5/14.2 |
| One clarifying question card | Max ONE structured tap-question before results | parser (asks when required facts missing) | tap answer → becomes chip | Draft S1 State 3; MB 14.2 |
| Zero-results relaxer | Names the weakest constraint + relax options + "Alert me" | search engine relaxation logic | tap option re-runs; alert = saved-search capture | Draft S1 State 4 |
| Lens chips ×6 | Each opens a one-question guided flow, swaps example pills, shows live count | per-lens counts from IDX/zoning/market data | tap → guided flow (table below draft, S1 lens-flow spec) | Draft S1 lens table |
| Commute lens flow | Work address + mode + minutes slider (default 30 @ 8am) → isochrone | routing/isochrone provider [BEST GUESS: Mapbox routing] | "Save this commute" persists to profile | Draft S1 lens table |
| Schools lens flow | Boundary-scoped school search or map boundary tap, colored by rating | LocalDataRecord (third-party school provider) | results limited to attendance boundary | Draft S1; MB 16.2–16.4 |
| ADU Check flow | Address eligibility verdict (max size + zoning cite) OR browse ADU-eligible listings | ZoningLookupRecord (Zoneomics, confidence-gated) | "Email me new ADU-eligible" = saved search | Draft S1; MB 17.2 gates |
| Yield Engine flow | Budget + cash-flow-vs-appreciation → investor mode grid | CashflowEstimateSnapshot deterministic preview metrics | "Watch this strategy" alert | Draft S1; MB 14.4 |
| Risk Lens flow | fire/flood toggles applied to current/last search | risk data provider with "how we compute this" provenance [BEST GUESS: First Street-class provider — UI unaffected by vendor] | overlay + 1–10 scores on cards | Draft S1 |
| Market Signals flow | Signals feed pre-filtered to the farm (price cuts, back-on-market, DOM outliers, new ADU-eligible) | IDX change detection + MarketDataSnapshot | each row = pre-filled search + one-tap watch | Draft S1 |
| Address-as-query card | Explains the report-card flow; "Save this address" homeowner hook | PropertyRecord + AVM/rent/zoning/risk | paste address → "Get the report card?" | Draft S1 |
| This-week signals card | 2–4 live signal rows with counts | signals engine, weekly auto-gen | deep-link to pre-filled searches | Draft S1 |
| Example pills ×4 | Persona-localized live-data prompts | pill ruleset + live counts | fire real search instantly, no wall | Draft S1 pill rules |
| Classic search link | Filter-first fallback (price/beds/baths/city — same engine) | — | opens filter panel | Draft S1 |
| Popular-search chips | Curated indexed slug pages | IDXFilterUrlRecord (INDEX_ALLOWED) | navigate to curated results page | Draft S1/S2; MB 15 |
| SEO prose block | One paragraph, neighborhood internal links | auto-written from live data | — | Draft S1 SEO |
| Trust row | MLS-direct badge, no-signup claim, Google review stars | review source [BEST GUESS: GBP API] | — | Draft S1 inventory |
| Freshness stamp | "MLS data updated N min ago" | IDX refresh timestamp | — | Draft S1; MB 14.3 |
| Returning-visitor hero swap | "Welcome back — since Tuesday: N new matches / price cut / open house" + See-the-new / Resume buttons | saved searches + saved properties deltas | one tap into Screen 02/26 | Draft S1 State 5 |
| Voice mic | Voice input to the prompt | device speech API | — | Draft S1 |

## States
- **Default (first visit):** full teaching layout, ambient demo, cycling placeholder.
- **Loading:** skeleton ≤400ms then progressive card fill; search fires with `progressive_loading: true` (MB 24.1) and transitions to Screen 02.
- **Returning visitor (40%+ of traffic):** hero demo + lens education suppressed (localStorage anonymous / profile signed-in); last search pre-loaded in the bar; signals strip filtered to their saved areas; lens chips shrink to one quiet row; welcome-back delta card. Tutorial never shows twice.
- **Empty/zero-results:** never a dead end — relaxation card names WHICH constraint and why + "Alert me" saved-search conversion (State 4).
- **Error/degraded (fail closed):** IDX feed stale >24h → freshness stamp turns warning ("data as of …"), no fabricated counts; lens counts unavailable → count hidden, chip stays; ambient map failure → static composite; risk/zoning provider down → those lenses open with "temporarily unavailable" note, never fake data. Sensitive-topic text in a query → `HUMAN_HANDOFF_REQUIRED`: topic excluded from parse/scoring/routing, gentle generic response, agent notified.
- **Permission-limited:** anonymous users get everything (no sign-up to search); detailed sold comps require authenticated + MLS-authorized session (MB freshness table).
- **Thin-market mode:** signals strip leans on solds + market stats, lens counts under 10 hidden, pills avoid volume promises.
- **Mobile:** per Layout; the one-question flows render as bottom sheets [BEST GUESS].

## Data fields
- Query: `query_text`, ParsedSearchFilters (city/state/zip/geo_code, min/max_price, min_beds/baths, property_types, listing_statuses, investor_strategy, min_rent_estimate_monthly, min_cap_rate, min_cash_on_cash_return, max_monthly_cash_needed, min_dscr, adu_interest, zoning_required, school_boundary_user_filter {user_entered: true}, exclude_protected_class_inputs: true). Source of truth: SearchRecord (MB 10.5).
- Attribution captured silently on every entry: content_id (only if real PropCast piece), originating_content_id, campaign_id, asset_id, anonymous_visitor_id, session_id, lead_source, capture_source, conversion_source, capture_provider (MB 7.2/24.1 UTM rules).
- Ticker/signal numbers: MarketDataSnapshot fields; counts formatted as integers; money as $X.XXM/$XXXK.
- Freshness timestamps per data type per MB 14.3 table.

## Rules & compliance
- Parser forbidden behaviors (MB 14.2): never infer protected class, family status, or sensitive life events; no MLS embeddings/vector search; no persistent AI memory of MLS content; no local scoring. Sensitive topic → human_handoff_required, topic never used downstream.
- School lens: user-entered only; §16.3 boundary + rating disclaimers + equal-service note shown in the flow; school data never in default ranking, alerts, audiences (§16.4 firewall).
- Zoning claims obey 17.2 gates (≥0.80 affirmative / 0.60–0.80 cautious / else suppress) + zoning disclaimer.
- No crime layer anywhere (fair housing). Wording rules: facts with attribution, never characterizations ("great schools", "family-friendly" forbidden — MB 16.1).
- "Never sold to other agents" claim must be contractually true platform-wide before ship (draft guardrail 3).
- Brand identity fields read-only from identity.json; DRE 01466876 only.
- Dynamic results noindex; only curated filter-URL pages indexed (caps: 250/market, 5000 global).

## Cross-links
In: ads/postcards/QRs (Switchy, UTM), community pages, curated slugs, PropReach destinations. Out: Screen 02 Results, Screen 03 property detail/report card, owner-value flow, community pages, Screen 26 Saved (via alert/save capture).
Ledger: emits nothing directly (search itself creates SearchRecord, not a canonical event); address report card may trigger EQUITY_CARD_CREATED downstream; IDX form leads submit via PropFlow `/approved-leads` (PropFlow emits LEAD_CAPTURED — PropSearch must never emit it, MB 25.3). Analytics events on every state transition; parse-abandon rate = north-star input metric.

## Open decisions
- [DECIDE] Isochrone/routing vendor — interim: Mapbox routing (already primary imagery vendor); UI unaffected.
- [DECIDE] Risk-data vendor — interim: First Street-class API; card copy shows provider attribution slot either way.
- [DECIDE] Review-stars source — interim: Google Business Profile rating, cached daily.
- [DECIDE] Voice input implementation — interim: native Web Speech API with server fallback; mic hidden where unsupported.
- [DECIDE] Placeholder-rotation experiment plumbing — interim: simple weighted rotation logged to analytics; formal A/B later.
