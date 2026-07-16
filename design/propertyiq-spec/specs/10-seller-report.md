# 10 · Seller Report / Owner Page (permanent per-owner live page)

**Purpose:** A permanent, per-owner live web page — not a report, not an email attachment. The monthly email teases exactly one delta ("W.I.N. — what's important now") and links here; the page carries the full story; every interaction (scenario click, check-in tap, chip toggle) writes a ledger signal that feeds the seller-propensity score shown in the agent's Command Center. Per the applied spec merge (matrix correction #8), this page and the PropClose Weekly Seller Dashboard are ONE artifact on ONE durable URL: homeowner mode (this spec) → listing-performance mode when they list → in-contract portal (Screen 25) → back to Homeowner Hub at close.

**Primary users:** Homeowner (past client, farm owner, sphere contact). Secondary: the agent (preview + propensity signals downstream).

**Entry points:** Monthly teaser email (one delta + link, review-first send policy) · postcard/farming QR (marketing short link, link.propertyiq.app — allowed here because this page is not auth-sensitive; sensitive portal auth links stay off the shortener) · Homeowner Hub equity card "see your full page" · agent-sent direct link · annual CMA follow-up.

**Exit points:** "Get my precise valuation (free)" → CMA request → agent task + Outbox-reviewed reply · "run it in the underwriter" → Underwriting Workspace (Screen 22) consumer-safe view · ADU concept link → zoning/ADU visual (licensing-safe imagery only) · comps map · Friendly Acres market guide (community page) · check-in taps (stay on page, self-segment).

## Layout

**Desktop:**
- **Header:** agent avatar + name + "Home value report" + nav: "Update my info", "Monthly tracking: ON".
- **Title block:** address H1; meta line: "Your home's live page · updated {date} · permanent link, refreshed monthly · Market temperature: {Buyer's/Neutral/Seller's}" (gauge computed from inventory, DOM, sale-to-list — Homebot pattern).
- **Buyer-demand hero (full width, brand border):** "14 buyers in our network are looking for a home like yours" + criteria line + the W.I.N. single monthly insight chip.
- **Equity Explorer (full width):** 3 scenario cards — Build the ADU (unique, zoning-data-powered) / Move up / Buy an investment — plus purchasing-power and short-term-rental micro-stats.
- **Two-column grid (1.3fr / 1fr):**
  - Left: valuation card (range, confidence, as-of date, delta vs last year, AVM-spread framing, best-time-to-list chip, range slider graphic) · "Tune your value" chips · "The 8 sales behind this number" comps card.
  - Right rail: "Want the real number?" CTA card (ink border, primary button) · 1-tap check-in card · Move math card · "If you sold at $X" net-sheet card · ADU hidden-value card · Rate & PMI watch · "Your neighborhood right now" · "How this reaches the owner" explainer.
- **Footer:** "Powered by PropertyIQ" + licensed identity block (agent name, DRE 01466876, brokerage — brand-locked).

**Mobile (375px):** single column, order: title → buyer-demand hero → valuation card → check-in (high on page; it's the self-segmentation engine) → equity explorer (cards stack) → net sheet → move math → ADU → rate watch → comps → neighborhood → CTA card sticky-ish near bottom. Tap targets ≥44px; the CTA button also renders as a sticky bottom bar. [BEST GUESS on mobile order — optimized for the check-in signal]

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Market temperature gauge | Buyer's/Neutral/Seller's from inventory, DOM, sale-to-list | MLS-derived aggregates (whitelist-safe, aggregate display) | none | draft Screen 10 (Homebot gauge) |
| **Buyer-demand hero** | "N buyers match your home" from active saved searches + buyer criteria in the agent network | PropSearch saved searches + PropFlow buyer criteria (aggregate count only, no buyer identity) | none; render only when N≥1, hide block if 0 | draft Screen 10 (Percy pattern); [BEST GUESS] hide-if-zero |
| W.I.N. insight chip | ONE insight per month ("you crossed 40% equity") — also the only thing the email teases | monthly delta engine over the page's own data | none | draft Screen 10 (locked: one insight, never a list) |
| Equity Explorer — ADU card | cash-out builds it, rent estimate, value-add range, "lot qualifies by right" | PropSearch zoning (Zoneomics fields) + rent estimate + AVM | click → ADU concept view (ledger signal) | draft Screen 10; zoning claim ladder |
| Equity Explorer — Move up | equity as down payment, payment-gap math at today's rates | AVM + mortgage balance + rate feed | click (ledger signal) | draft Screen 10 |
| Equity Explorer — Investment | cash-out down payment scenario + est. cash flow, link to underwriter | PropSearch underwriting quick calc | "run it in the underwriter →" | draft Screen 10 |
| Purchasing power stat | max next-home price (equity + income est., editable) | derived; income user-editable | edit → recompute | draft Screen 10 |
| Short-term rental stat | spare room monthly estimate (12-comp est.) | rent-comp source | none | draft Screen 10 |
| Valuation card | range + midpoint, confidence label, as-of date, YoY delta | AVM ensemble | none | draft Screen 10; matrix correction #7 (confidence/range/as-of mandatory) |
| AVM-spread framing | "Three models disagree by $110K (ours / Zestimate / CoreLogic)" — the CMA conversation starter | multiple AVM feeds | none | draft Screen 10. ⚠ Zestimate naming is fine on this PropSearch/PropCast-owned page but FORBIDDEN once the page runs inside PropClose v1 portal chrome (no Zestimate-referencing template, PropClose §9.7) — see Open decisions |
| Best-time-to-list chip | seasonal window + premium % for the neighborhood | historical sale seasonality | none | draft Screen 10 |
| Range slider graphic | visual of range + midpoint marker | AVM | none | draft Screen 10 |
| "Tune your value" chips | Kitchen remodeled / Bathrooms updated / New roof / ADU added / Needs work | owner input → SourceFact (HUMAN_CONFIRMED) | toggle → sharpen estimate + ledger signal | draft Screen 10 |
| Comps card | "The 8 sales behind this number" — recent solds, distance, recency | MLS data | "see all comps on map →" — detailed sold comps require authenticated session; public view shows aggregates | draft Screen 10; PropClose §13.6 posture |
| CTA card "Want the real number?" | agent credibility line + free precise valuation button | identity config + agent stats | submit → CMA request task; reply is review-first | draft Screen 10 |
| **1-tap check-in** | 3 buttons: Just tracking / Curious what I'd walk away with / Thinking about it in 6–12 months | owner tap | writes ledger signal → seller-signals tile / propensity via ScoringService | draft Screen 10 (Homebot check-in) |
| Move math card | current payment vs move-up payment, gap, gap trend, "we'll flag the month it loosens" | mortgage terms + rate feed | none | draft Screen 10 |
| Net sheet "If you sold at $X" | payoff est., selling costs est., equity walk-away | AVM midpoint + mortgage balance + cost model | none; requires known mortgage balance (else prompt — see States) | draft Screen 10; matrix correction #7 |
| ADU hidden-value card | "ADU by right" + comp value-add range + rent alternative | Zoneomics fields + comps | "See the concept on your lot →" | draft Screen 10; claim ladder §13.9 |
| Rate & PMI watch | PMI cancel eligibility + monthly saving + "Wattson drafts the lender letter" · refi check · renovation ROI lines | mortgage data + rate feed + ROI reference | letter draft → agent review task (never auto-sent) | draft Screen 10 |
| Neighborhood snapshot | actives, median DOM, sale-to-list + market-guide link | MLS aggregates | link to community page | draft Screen 10 |
| "How this reaches the owner" explainer | permanent-page model, monthly email tease, propensity note, printable branded CMA on request, spec-merge note | static | none | draft Screen 10 |
| Monthly tracking toggle | subscription state for the teaser email | consent/notification prefs | toggle OFF = suppress emails (consent-gated send) | draft header; §11.2 consent model |
| Update my info | owner edits mortgage balance, income, home facts | owner input → SourceFacts | form | draft header |
| **Listing-performance mode flip** (once listed) | page becomes the Weekly Seller Dashboard: week navigator, verbatim showing feedback, three-state offer banner, PORTAL_VIEWED tracking, review-first Monday doorway email | WeeklyListingUpdateEmbed (weekly_listing_update.v1, PropCast-produced) | week nav; authenticated access only in portal context | matrix correction #8; PropClose §9.6 |
| Email teaser (companion artifact) | one delta + link; never the full page in email | W.I.N. engine | review-first send | draft Screen 10 |

## States
- **Default:** full page as above.
- **Loading:** hero + valuation skeletons; page useful without JS beyond toggles. [BEST GUESS]
- **AVM unavailable / low data:** valuation card renders "estimate unavailable" — never a fabricated number; dependent cards (net sheet, purchasing power) hide (matrix correction #7).
- **Missing mortgage balance:** equity/net-sheet cards show a MISSING_MORTGAGE_BALANCE manual-entry prompt instead of numbers (matrix correction #7).
- **Zoning below thresholds:** jurisdiction_covered=false OR confidence<0.60 → ADU claims suppressed entirely; 0.60–0.79 → cautious disclaimered language; ≥0.80 + covered → affirmative "by right" claim (claim ladder).
- **Buyer-demand = 0:** hero hidden. ScoringService down: propensity signals still write to ledger; no score ever computed page-side.
- **Listing mode degraded:** if the weekly embed is unavailable → section hidden + staff task, never stale/fabricated content (§9.6).
- **Empty (new owner, no history):** valuation + neighborhood only; explorer cards appear as data arrives. [BEST GUESS]
- **Permission:** homeowner mode is link-addressable per owner; listing/in-contract modes require authenticated portal session (no public indexing, no_public_indexing=true on the embed).
- **Mobile:** per Layout.

## Data fields
Address; updated_at; market temperature (enum of 3); buyer-match count (int, aggregate); W.I.N. insight (string, 1/month); AVM range low/high, midpoint, confidence (label), as_of date, YoY delta; per-model AVM values (ours/others); best-list window + premium %; owner condition chips (bool each → SourceFact); comps (address, sold price, distance, recency); check-in selection (3-value enum + timestamp); current rate, payment, move-up payment, gap, gap delta; payoff est., selling-cost est., equity walk-away (all USD, all "est." labeled); zoning_confidence (0–1), jurisdiction_covered, zoning_source, zoning_last_checked_at; ADU value-add range, rent est.; PMI eligibility (bool), refi delta; actives, median DOM, sale-to-list; monthly-tracking consent state. Listing mode adds: reporting_period_start/end, showing_feedback_summary, seller_tasks[], market_activity_summary, offer-banner state (none/received/multiple — three-state per correction #8).

## Rules & compliance
- **Never fabricate:** AVM/equity numbers require real inputs; unknown → "unavailable" + entry prompt. All values labeled estimates.
- **Every displayed estimate carries confidence + range + as-of date** (matrix correction #7 — hard rule).
- **Propensity is ScoringService's job:** this page only emits ledger signals; no page-side scoring, thresholds, or tiers (non-scoring rule).
- **Zoning/ADU claim ladder** enforced per render (§13.9 thresholds above).
- **Outbound gating:** monthly teaser email is consent-gated (marketing consent + evidence) and review-first per the send policy; any agent outreach triggered by check-ins routes to review — never auto-outreach (matrix correction #2).
- **Brand lock:** identity from identity.json (DRE 01466876); the identity.json blocklist enforced.
- **MLS posture:** aggregate comps public; detailed solds authenticated; whitelist fields only; no vector/AI-training use of MLS data.
- **Imagery:** ImageryProvider/Mapbox with attribution; no Google satellite for client-facing marketing; ADU concept renders only from owned/licensed imagery — never provider map tiles (§13.8).
- **Analytics:** owned-page analytics with GPC/DNT/opt-out respect; in listing/portal modes: no ad pixels, PORTAL_VIEWED canonical event only (§13.10).
- **No school data on this page** (steering firewall).
- Fair-housing: value/demand framing is property-fact-based; no demographic language anywhere.

## Cross-links
**In:** monthly teaser email, farming postcards/QR, Homeowner Hub equity card, agent share, annual CMA touch. **Out:** CMA request (→ agent task + Outbox), Underwriting Workspace (22), community/market guide page, comps map, ADU concept view, Client Portal (25) when in-contract. **Emits:** ledger signals per interaction (scenario clicks, chip toggles, check-in taps — feed seller-propensity via ScoringService), PAGE_VIEWED (privacy-checked), PORTAL_VIEWED (listing/portal modes), CMA-request task event. **Consumes:** AVM feeds, ScoringService outputs (Command-Center side), WeeklyListingUpdateEmbed (listing mode), DEAL_CLOSED (mode transitions via portal lifecycle).

## Open decisions
- [DECIDE] Zestimate naming in the AVM-spread line: PropClose v1 forbids Zestimate-referencing templates in its portal (§9.7). Interim design: homeowner mode (PropSearch/PropCast-owned surface) shows "three independent estimates" with generic model labels ("Model A/B") unless legal clears third-party brand naming; the draft's explicit "Zestimate $1.41M" copy is treated as illustrative, not shipped copy.
- [DECIDE] AVM vendor mix: assume our model + 2 licensed third-party AVMs — UI unaffected by vendor choice. [BEST GUESS]
- [DECIDE] Buyer-match count threshold/staleness: interim = count from saved searches active in last 90 days, recomputed monthly with the page refresh. [BEST GUESS]
- [DECIDE] Page auth in homeowner mode: interim = unguessable per-owner URL, no login, no indexing, with OTP step-up added only if the page ever exposes exact mortgage balance the owner entered. [BEST GUESS — aligns with §9.4 sensitivity tiers]
- [DECIDE] "Wattson drafts the lender letter" (PMI): interim = draft lands as an agent review task + Outbox item; never sent client-direct. [BEST GUESS consistent with review-first policy]
