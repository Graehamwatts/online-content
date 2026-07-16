# 03 · Property detail

**Purpose** — The single-property page: the consumer/investor decision surface and the platform's SEO workhorse. It renders the licensed IDX listing plus PropertyIQ's intelligence layers (match reasoning, monthly cost, investment snapshot, zoning/ADU, climate, price history, comparables, neighborhood), and it is the launch point for underwriting, compare, save, and agent contact. Sold listings never die — the page persists as a "sold" page with a home-value CTA (Zillow's organic moat pattern; ~37 iterations of the draft confirm this).

**Primary users** — Consumers (buyers/sellers browsing the agent's site), investors/serious buyers, the agent themself (reviewing intelligence before a client conversation). Anonymous visitors see the full page — no hard gate on organic traffic (draft decision from Ylopo data: soft behavior-triggered prompts only; hard gates reserved for PPC and agent-configurable).

**Entry points**
- Results list/map card click (Screen 2) — "← Back to 47 results" preserved
- Compare table column header click (Screen 4)
- Filter-URL landing pages and "homes like this" internal links (Brain §15)
- Organic search (canonical URL `/{city}/{address-slug}/{mls-id}`), social OG cards, QR codes/short links minted on filter URLs
- Saved Properties screen, alerts emails
- LISTING_LIVE_FROM_IDX-driven links from PropCast/PropReach content

**Exit points**
- Explore tiles → in-page anchor sections (sticky nav)
- "Run the numbers →" / Investment tile → Underwriting Workspace (Screen 22) with `property_id` + any saved assumption overrides
- "Area guide →" / neighborhood teaser link → Community page; breadcrumbs → city/community pages
- "See comps →" → comparables section; comp rows link to other listing detail pages
- Compare affordance → Compare (Screen 4) auto-seeded "compare with 3 similar actives"
- Agent card "Ask about this home" / "Book a tour" → lead capture → PropFlow intake (PropSearch itself never emits LEAD_CAPTURED — the form posts to the PropFlow intake endpoint; Brain §25.3)
- Save → SavedPropertyRecord; Share → OG-carded URL
- Sold-page CTA "What's my home worth" → home-value capture flow (homepage widget flow)

## Layout

**Desktop**
- **Site header**: agent avatar + name, "← Back to N results" context line, Save / Share actions. Agent-branded (identity.json), "Powered by PropertyIQ" footer credit lives in the right-rail card.
- **Breadcrumbs**: California › City › Neighborhood › Address — BreadcrumbList schema; links pass authority up to community + city pages.
- **Gallery**: hero photo + 4 tiles ("+ N photos" opens full carousel; arrows on hover, dots, lazy-load). LCP budget: hero renders < 2s.
- **Sticky in-page nav**: Overview · Why it matched · Commute · Schools · Investment · Zoning & upside · Climate & risk · Price history · Comparables · Neighborhood. Highlights active section on scroll.
- **Two-column body** (confirmed layout, draft v2): left = content sections in order below; right = **sticky agent contact card** that follows scroll (Redfin/Zillow convention).
  1. Bold stat card: price ($1,289,000 style), all-in $/mo, beds/baths/sqft/lot, badge row (New (2d), −4% vs comps, Matches 5 of 5)
  2. Address line
  3. Stat row: Match score · Est. rent · DOM · vs. comps
  4. **Explore tile grid** (9 tiles): Commute, Schools, Investment, Zoning & upside, Climate & risk, Price history, Comparables, Neighborhood, Why it matched — each tile = icon, bold label, one-line data teaser, "→" link to its section
  5. About this home (listing remarks / AI-drafted body text)
  6. Why this matched your search (match reasoning card)
  7. Monthly cost module with Buyer/Investor toggle (editable)
  8. Investment snapshot
  9. Zoning & Investment Intelligence panel (approved 2026-07-08 Zoneomics/Reventure plan)
  10. Climate & risk badges
  11. Price & tax history (server-rendered prose + table)
  12. Neighborhood teaser (2 sentences + link)

**Mobile (375px)**
- Single column, same section order. Gallery becomes a swipeable full-width carousel with photo counter.
- Sticky agent card becomes a **sticky bottom bar** (Ask about this home · Book a tour), per draft note.
- Sticky section nav becomes a horizontally scrollable chip row under the gallery.
- Explore tiles stack 2-up. Stat rows wrap 2×2. Compare tables inside Comparables scroll horizontally in their own container.
- Card actions (save/compare/hide) — visible heart + long-press sheet (no hover states on mobile; inherited from Screen 2 rules).

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| Breadcrumbs | State › City › Neighborhood › Address | PropSearch PropertyRecord geo fields | Click → community/city pages | Draft per-page SEO spec; Brain §15 |
| Photo gallery | Licensed listing photos | IDXListingRecord / IDXDisplayCacheRecord (Brain §10.3–10.4) | Carousel, lightbox, lazy-load | Draft s3; Brain §26.5 MLS/IDX boundary |
| Price + all-in $/mo stat card | List price, estimated all-in monthly | IDXListingRecord.list_price; CashflowPreviewMetrics (Brain §24.4) | None; monthly figure links to Monthly cost module | Draft s3 |
| Facts row | Beds / baths / sqft / lot | IDXListingRecord | — | Draft s3 |
| Badge row | New (Nd) · −X% vs comps · Matches N of N | DOM from IDX; comps delta from AVM/comp model; match count from SearchResultRecord | Hover/tap explains | Draft s3 |
| Match score stat + "Why it matched" card | e.g. 96/100 with factual reasoning tied to the user's own prompt criteria | SearchResultRecord (Brain §10.6); parsed criteria from SearchRecord | Tile → section; each claim carries its fact | Draft s3. Note: ranking/match scoring must NOT run locally (Brain §14.2 forbids local scoring) — score comes from ScoringService/search service; hidden for visitors with no active search context |
| Est. rent stat | Monthly rent estimate + confidence | RentEstimateSnapshot (Rentometer; Brain §10.9) | Links to Investment section | Draft s3; build-state memory (Rentometer, not RentCast) |
| Explore tiles (9) | Teaser + deep link per intelligence domain | See per-section sources | Click → anchor scroll | Draft s3 |
| About this home | MLS remarks first when licensed for display; where thin, AI-drafted paragraph from listing facts + intelligence data, clearly agent-attributed | IDXListingRecord.remarks; generated copy pipeline | Read only | Draft s3; Brain §26.5; fair-housing wording rules §16.1 |
| Commute section | Drive times to user-set destinations at chosen hour | LocalDataProvider (Brain §12.7); routing provider [BEST GUESS: Mapbox directions, consistent with the Mapbox imagery position §12.6] | Edit destination/time | Draft s3 |
| Schools section | Assigned schools, third-party ratings, boundaries | LocalDataRecord (Brain §10.12, §16) | User-initiated expand; sortable school list; provider/district links | Brain §16.2–16.4 — see Rules |
| Monthly cost module | PITI + tax + insurance + HOA, all editable (rate, down %, taxes); Buyer/Investor toggle swaps to cash flow / cap rate / rent yield | CashflowPreviewMetrics via POST /cashflow/preview (Brain §24.4); defaults from assumption pack §19.4 | Live-updating inputs; toggle | Draft s3 (BuyAbility rationale); Brain §14.4 deterministic metrics |
| Investment snapshot | Cap rate, cash flow @20% down, 5-yr appreciation est., rent confidence | CashflowPreviewMetrics; appreciation from MarketDataSnapshot (Brain §10.8) [BEST GUESS: forecast figure labeled "est." with as-of date] | "Run the numbers →" → Underwriting Workspace | Draft s3; Brain §19 |
| Zoning & Investment Intelligence panel | Development-upside card ("Builds up to 3 units · 1 built today"), ZIP market forecast score (0–100 meter + risk label), Permitted-by-right grid (ADU / garage conversion / SB-9), ordinance source link | ZoningLookupRecord (Zoneomics, Brain §10.11, §17); forecast score from the 2026-07-08 Reventure-inspired scoring build | Expand zoning details (FAR/height/setbacks) | Draft s3 (approved 2026-07-08 panel); Brain §17 |
| "Ask anything about this lot" box | NL zoning Q&A with suggested chips (garage conversion, ADU, SB-9, "Show ADU concept 🛰") | ZoningProvider Q&A (Brain §17.1); ADU visuals §17.4 | Free-text ask; chip taps; ADU concept renders plan-view parcel overlay | Draft s3; Brain §17.2–17.4 |
| Zoning disclaimer line | Verbatim third-party/verify-with-jurisdiction text | Static (Brain §17.3) | — | Brain §17.3 (verbatim, non-removable) |
| Owner-signal badge | Owner-occupied / Absentee / Corporate ONLY | PropertyDataProvider (Brain §12.2) | — | Matrix correction #12: never raw owner names/mailing addresses |
| Overlay warning | Historic/restrictive overlay note, shown only when applicable | ZoningLookupRecord | — | Draft s3 |
| Climate & risk badges | Fire/Flood/Quake scores + insurance est. | LocalDataProvider risk feed [BEST GUESS: third-party risk provider (First Street–class); provider attribution required per facts-not-characterizations] | Tile → section | Draft s3 |
| Price & tax history | Server-rendered prose + table: list date/price, last sale, assessed value, taxes | PropertyRecord + county data via PropertyDataProvider | Read only; never JS-only (SEO) | Draft s3 |
| Comparables section | 8 comps, model value ($1.34M style) | AVMSnapshot (Brain §10.10) + comp set | Comp rows link to their listing pages | Draft s3; AVM display rules (confidence, range, as-of date — matrix correction #7) |
| Neighborhood teaser | 2-sentence crawlable teaser + "Read the full guide →" | Community-page content store | Link to community page | Draft s3 |
| Sticky agent card | Avatar, name, brokerage + DRE (from identity.json), response-time line, Ask about this home, Book a tour, Powered by PropertyIQ | Tenant identity config (locked) | Buttons open lead form / booking flow → PropFlow intake; booking uses pre-approved slots (Screen: Calendar) | Draft s3; Skills CLAUDE.md brand rule |
| Save (header + card heart) | Creates/updates SavedPropertyRecord (notes, custom rent, assumption overrides, strategy tag) | SavedPropertyRecord (Brain §10.7) | Save/unsave; save opens optional notes/strategy sheet | Matrix gap "Saved searches/properties P0" |
| Share | Copies canonical URL; OG/Twitter card with hero photo | — | Native share on mobile | Draft SEO spec |
| Compare affordance | Adds to compare tray; "Compare with 3 similar actives" auto-seed link | Compare set (Screen 4) | Checkbox/button; tray pill on mobile | Draft s4 note |
| Soft lead prompts | Behavior-triggered (repeat visit, photo-binge, save) non-blocking prompt | Session behavior signals | Dismissible; agent-configurable; hard gate only on PPC entry | Draft s3 lead policy |
| Sold-page variant | "Sold for $X on {date}" banner, gallery retained per MLS display rules, what's-my-home-worth CTA | IDX sold record; AVM | CTA → home-value flow | Draft s3 + SEO canonical rule |
| Compliance flags (hidden plumbing) | compliance_flags array on the detail API gates what renders | PropertyDetailApiResponse (Brain §24.3) | — | Brain §24.3 |

## States

- **Default**: full page as above; anonymous OK.
- **Loading**: gallery + stat-card skeletons render immediately (LCP < 2s budget); intelligence sections stream in independently — each section has its own skeleton so a slow provider never blocks the page.
- **Empty / partial data (fail-closed per section)**:
  - AVM missing → comps section shows "estimate unavailable" — never a fabricated number; always confidence + range + as-of date when present (matrix correction #7).
  - Rent estimate missing → Investment snapshot hides rent-derived metrics, shows "rent estimate unavailable" + manual_review_flag.
  - Zoning below confidence/coverage gate → claim suppressed entirely ("Zoning answer unavailable for this parcel"), never guessed (Brain §17.2); ADU visuals suppressed or internal-only (§17.4).
  - ScoringService down → match score and any investor-fit score/rank hidden; deterministic metrics remain (Brain §12.10 failure behavior).
  - Mortgage balance unknown (sold/homeowner contexts) → equity = null + MISSING_MORTGAGE_BALANCE prompt, never guessed (Brain §18.2).
  - No active search context → "Why it matched" tile + section hidden (nothing to match against).
- **Error/degraded**: IDX feed stale beyond freshness rules → banner "Listing data as of {timestamp}"; if display license revoked, licensed fields/photos are removed (IDXDisplayCacheRecord governs) and the page falls back to public-record facts.
- **Permission-limited**: restricted MLS fields never render beyond license (Brain §26.5). Agent-only chrome (e.g. "Generate ads" panel, PropReach P1) hidden from consumers.
- **Sold/off-market**: permanent sold page state (above).
- **Mobile**: layout variations per Layout section; sticky bottom agent bar replaces right rail.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| list_price / close_price | USD int | IDXListingRecord |
| beds, baths, property_type, sqft, lot_sqft, year_built | int/float/enum | IDXListingRecord / PropertyRecord |
| address, city, zip, geo_code, neighborhood | strings | PropertyRecord (+ PropertyAliasRecord for canonical URL survival across relists) |
| days_on_market, listing_status | int / enum | IDXListingRecord |
| all_in_monthly, P&I, taxes+insurance, HOA | USD/mo, editable inputs (rate %, down %, tax) | CashflowPreviewMetrics; defaults §19.4 assumption pack |
| rent_estimate_monthly + confidence | USD/mo + High/Med/Low | RentEstimateSnapshot |
| cap_rate, monthly_cash_flow, cash_on_cash, DSCR, GRM, expense_ratio, NOI | % / USD | CashflowPreviewMetrics (deterministic-only list, Brain §14.4) |
| match score + per-criterion pass/miss | 0–100 + list | SearchResultRecord (service-computed, never local) |
| avm_value, confidence, range, as_of_date | USD, %, range, date | AVMSnapshot |
| zoning: max_units, units_built, by-right list, FAR, height, setbacks, claim_level, confidence, coverage, ordinance citation | typed | ZoningLookupRecord |
| market forecast score (ZIP) | 0–100 + risk label | 2026-07-08 scoring build [BEST GUESS: stored as MarketDataSnapshot extension] |
| fire/flood/quake scores, insurance_est | n/10, USD/yr | LocalDataProvider risk feed |
| school: name, assigned boundary, rating, provider, methodology link | typed | LocalDataRecord |
| price/tax history rows | date + USD table | PropertyRecord/county |
| owner signal | enum: owner-occupied / absentee / corporate | PropertyDataProvider |
| saved: notes, custom_rent_estimate_monthly, assumption_overrides, investor_strategy | per §10.7 | SavedPropertyRecord |
| lead form: name, contact, message, source/UTM tags | strings | Posts to PropFlow intake; PropSearch capture fields §7.2–7.3 |

## Rules & compliance

- **Fair housing / facts-not-characterizations** (Brain §16.1): all prose uses allowed wording; forbidden: "great schools", "family-friendly", "safe", "best/declining neighborhood". AI-drafted "About this home" copy must pass the same filter.
- **School module** (Brain §16.2–16.4): user-initiated or neutrally placed; identical for every user on the same property; third-party attribution + methodology link; all three verbatim disclaimers (boundary, rating, equal-service); never feeds ranking, alerts, audiences, scoring, or lead capture. **No conversion CTA inside the schools block** (matrix correction #4 — CTA sits outside it).
- **Zoning** (Brain §17): confidence/coverage gates suppress below-threshold claims; verbatim disclaimer always shown; ADU plan-view overlay uses Mapbox with attribution; photorealistic ADU concept only with client-owned/licensed aerial imagery and marketing use is REVIEW_REQUIRED.
- **Scoring**: no local formulas/weights/ranking (Brain §12.10, §14.4); fail closed.
- **AVM/equity**: confidence + range + as-of always; "estimate unavailable" over fabrication; equity needs known mortgage balance (Brain §18).
- **MLS/IDX boundary** (Brain §26.5): display only what the license allows; retention expiry honored; only the §14.6 whitelist fields flow to PropFlow/GHL.
- **Sensitive topics**: NL inputs (zoning Q&A, lead messages) that hit sensitive topics set human_handoff_required; never used for scoring/routing (Brain §14.2, §26.6).
- **Owner privacy**: badges only, never names/mailing addresses (matrix correction #12).
- **Lead policy**: no hard gate on organic; soft prompts behavior-triggered; hard gate PPC-only and agent-configurable (draft decision — do not contradict).
- **Consent**: any outbound follow-up from a captured lead runs ComplianceProvider checks in PropFlow — this page only captures with source attribution (§7.2–7.3 UTM rules).
- **Brand**: agent identity fields (name, brokerage, DRE #01466876 for Graeham's tenant) render read-only from identity.json; the known-bad legacy DRE on the identity.json blocklist is banned.

## Cross-links

- **In**: Results (S2), Compare (S4), filter-URL pages (S: Filter-URL library), community/city pages, saved properties, external organic/social/QR.
- **Out**: Underwriting Workspace (S22), Compare (S4), Community page, Calendar/booking, PropFlow lead intake, CMA/home-value flow (sold pages).
- **Emits** (via services): PROPERTY_VIEWED-class analytics [BEST GUESS: page-view events at content/campaign attribution level per the impression-honesty rule], UNDERWRITE_RUN (when launched from here and run), GENERATED_ASSET_CREATED (ADU visuals), ZONING_LOOKUP events. Must NOT emit LEAD_CAPTURED/AD_* etc. (Brain §25.3) — PropFlow emits lead events.
- **Consumes**: LISTING_LIVE_FROM_IDX freshness, AVM/rent/zoning snapshots, SearchResultRecord match context.

## Open decisions

- **[DECIDE] Risk-data vendor**: interim design assumes a First Street-class API with per-hazard 1–10 scores + insurance estimate; UI unaffected by vendor choice — badges + section layout stay identical.
- **[DECIDE] Commute routing provider**: assume Mapbox Directions (aligned with the §12.6 Mapbox imagery position); tile copy and editable destination UX unchanged either way.
- **[DECIDE] 5-yr appreciation figure**: shown as "est." from MarketDataSnapshot; if the Reventure-inspired forecast build lands ZIP-level only, show ZIP figure with "(ZIP)" label rather than a property-level claim.
- **[DECIDE] Soft-prompt trigger thresholds** (repeat-visit count, photo-binge depth): agent-configurable in Settings; interim defaults [BEST GUESS] 2nd visit or 10+ photos or first save.
- **[DECIDE] Match-score availability for anonymous users**: interim — score renders only when a session search context exists; otherwise the tile/section is absent (fail-quiet, not a locked teaser).
