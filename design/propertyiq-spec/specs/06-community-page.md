# 06 · Community Page (programmatic SEO template, `/{city}/{neighborhood}/`)

**Purpose** — The ranking engine of every agent instance: a templated, data-fed neighborhood guide combining editorial narrative + exhaustive live market data + internal-link mesh + FAQ schema. Generated per `/{city}/{neighborhood}`; only data, photos, and brand vary per agent. It doubles as the highest-converting seller-capture surface (in-page valuation module, 2–5% conversion per draft research).

**Primary users** — Consumers researching an area (buyers, sellers, owners); crawlers + LLMs (AI-citation/AEO target); the agent reviews editorial blocks; SEO Console (Screen 20) tunes variable slots.

**Entry points** — Organic search ("{neighborhood} homes for sale", "{neighborhood} statistics/prices", "{address} sold" via sold-page backlinks), homepage areas-served/footer/neighborhood cards, sibling-neighborhood mesh links, GBP posts, listing-page breadcrumbs, related-searches chips, monthly farm letter links.

**Exit points** — Listings → Screen 3 detail; "See all N homes" + related-searches chips → filter-URL curated results (Screen 2); school buttons → address-lookup flow / school-filtered search; valuation module + "instant home value" links → value capture → CRM; "monthly market report" → subscribe capture; ask-this-page box → NL answer flow (same engine as Screen 1); sibling/parent links → other community pages; sold links → permanent sold pages; "Ask about this neighborhood" → contact.

## Layout

Desktop: branded site chrome (header + "Search this area" nav) → breadcrumb (State › County › City › Neighborhood) → H1 + freshness line → hero 6-stat grid → sections in order: 30-second editorial read → Living in {hood} → Housing stock & costs → Getting around → Market trends by property type (table + 3 chart cards) → Neighborhood facts (6 stats) → Proprietary data-engine stats (6 tiles) → Ask-this-page box → Schools table + address buttons + disclaimer → Commute/climate/lifestyle cards → Homes for sale (live cards + CTAs) → Parks & dining editorial → Buying/selling service paragraph → Recently-sold hub block → Related searches chips → FAQ (schema) → Nearby neighborhoods mesh → Seller-valuation capture module (brand-bordered) → E-E-A-T authored-by block → footer (schema note + Powered by PropertyIQ).

Mobile (375px): single column; stat grids 2-up; the trends table and schools table scroll horizontally inside `overflow-x` containers; chart cards stack; sticky bottom CTA [BEST GUESS: "Get home value · Search this area" bar mirroring homepage pattern]; valuation module stays near end but a compact inline value link appears after the hero stats.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Breadcrumb | CA › San Mateo County › Redwood City › Friendly Acres; BreadcrumbList schema | Geo hierarchy config | Links up the mesh | Draft s6 |
| H1 + freshness line | "{Hood}, {City}, CA — Neighborhood Guide & Market Statistics" · "Live data, updated daily · {month year}" | Template + render timestamp | none | Draft s6 SEO spec |
| Hero 6-stat grid | Median sale (12mo) + YoY, $/sqft, homes for sale, median DOM (vs national), sale-to-list, months of supply | MarketDataSnapshot (MLS), daily re-render | Hover defs [BEST GUESS] | Draft s6 |
| 30-second read (editorial) | AI-drafted-from-data summary + quoted agent voice line | LLM draft over snapshots; agent-reviewed before publish | Agent edit in review flow | Draft s6 (E-E-A-T) |
| "Living in {hood}" prose | ~150-word templated editorial from POI/geo data, unique per neighborhood per agent | LocalDataProvider + LLM; agent-reviewed | — | Draft s6 |
| Housing stock & costs prose | Stock description + price bands + ADU-by-right % + upzoned-lot count; numbers re-render monthly | MLS + Zoneomics (ZoningLookupRecord) | — | Draft s6 |
| Getting around prose | Drive times, Caltrain, walk score | Commute engine (same as property-page commute layer) + LocalDataProvider | — | Draft s6 |
| Trends-by-type table | SFH/TH/Condo: median, $/sqft, sold count, DOM, sale-to-list, YoY | MarketDataSnapshot per type | Horiz-scroll on mobile | Draft s6 (julianalee data-depth play) |
| 3 chart cards | 5-yr price trend, inventory & DOM, recent-sales heat map | MarketDataSnapshot series; map from closed MLS | Chart interactions [BEST GUESS: hover values only] | Draft s6 |
| Neighborhood facts grid | Home count, median year built, median lot, own-vs-rent, median rent (3bd), walk/bike | PropertyRecord aggregate + RentEstimateSnapshot + LocalData | — | Draft s6 |
| Proprietary data-engine grid | ADU-eligible %, development-upside lots, gross rent yield vs Peninsula avg, 8am commutes, market forecast /100 + risk label, hazard profile | Zoneomics, RentEstimate, ScoringService forecast, FEMA/CAL FIRE | Forecast tile click → contributing facts [BEST GUESS, mirrors map-pin explainability rule] | Draft s6 ("uncopyable SEO/AEO blocks") |
| Ask-this-page box | NL Q&A scoped to the neighborhood; zoning answers cite municipal code; school answers carry disclaimer | Same parser/answer engine as Screen 1 + LocalDataProvider | Submit → answer inline | Draft s6 |
| Schools table | School, grades, type, rating, distance; each school links its page | LocalDataProvider SchoolDataResponse (third-party ratings, attributed) | Row links | Draft s6; PropSearch MB §16 |
| School action buttons | "Which schools serve a specific address?" + "Search homes assigned to {school}" — placed OUTSIDE the schools data module | User-initiated filter (school_boundary_user_filter) | Address lookup / filtered search | Matrix correction #4; MB §16.4 |
| School disclaimer | Verbatim: third-party sources, ratings/boundaries change, verify with district; equal-service note | Static template §16.3 | none, non-removable | MB §16.3 |
| Commute/climate/lifestyle cards | Hazard-zone map (FEMA/CAL FIRE objective data), drive-time map, parks/dining list — NO crime data | LocalDataProvider + hazard providers | Card → expanded map [BEST GUESS] | Draft s6 |
| Homes-for-sale cards + CTAs | Live listings; "See all N →" (filter URL) + "Get the monthly market report" | IDXDisplayCache; filter-URL library | Card → detail; CTAs | Draft s6 |
| Parks & dining editorial | Named local POIs, agent-reviewed | LocalDataProvider + LLM | — | Draft s6 |
| Buying/selling service paragraph | Long-tail targeting; instant-alert + instant-value capture links | Template + live DOM stat | 2 capture links | Draft s6 |
| Recently-sold hub block | 12-mo sold count/median + 3 recent sales, each address links its permanent sold page (loop closes back) | Closed MLS | Links | Draft s6 |
| Related-searches chips | 5+ curated query links rendered from the filter-URL library (never 404) | IDXFilterUrlRecord | Links → curated result pages | Draft s6; MB §15 |
| FAQ block | 3+ Q&As with hard numbers; FAQPage schema (~2.7× AI-citation rate) | Templated from snapshots | Expand/collapse | Draft s6 |
| Nearby-neighborhoods mesh | Sibling cards (name, median, actives) + "All {city} →" parent rollup | Community index | Links | Draft s6 |
| Seller-valuation module | "Own a home in {hood}?" address capture, brand-bordered | AVMProvider + lead intake, source tag `community_{hood}_value` | Submit → value flow + CRM | Draft s6 (highest-converting element) |
| E-E-A-T authored-by block | "Written & verified by {agent}" + sales-in-hood count + DRE + reviews link + first-person note (agent-authored once) + "Ask about this neighborhood" CTA | Brand vault + production records | CTA → contact | Draft s6 |
| Footer | Powered by PropertyIQ + schema/canonical note | Platform | — | Draft s6 |
| Uniqueness validator (publish gate) | Blocks publish if page too similar to other agents' instances (doorway-page risk) | Platform validator | Blocking state in publish flow with diff report [BEST GUESS on report format] | Draft s6 note |
| OTTO auto-SEO layer | Per-instance GSC-fed title/meta/heading tuning + internal-link suggestions through variable slots only, never raw HTML | SearchAtlas/OTTO via SeoProvider; approvals in Screen 20 | Change log visible in SEO Console | Draft s6 SEO spec; MB §12.12 |

## States

- **Default**: fully populated, "updated {date}" visible.
- **Loading**: server-rendered (static shell is the norm); charts/maps lazy-load below fold.
- **Empty/sparse-data neighborhood**: sections with insufficient data auto-hide rather than render thin content (e.g. <3 sales in 12mo hides trends-by-type rows [BEST GUESS: per-row suppression with "insufficient sales to report" note]); page is not generated at all below a data floor [BEST GUESS threshold — flag to product].
- **Degraded (fail-closed)**: ScoringService down → forecast tile hidden ("score unavailable"), never a stale/fabricated score (matrix correction #12 pattern); Zoneomics stale beyond 30-day cache → ADU/upzone tiles show "verify — data refresh pending" [derived from MB 30-day zoning cache rule]; school provider down → schools section hides with the disclaimer block retained off; AVM down → valuation module keeps capture, drops instant promise.
- **Unpublished/blocked**: uniqueness-validator failure blocks publish; page stays on last approved version.
- **Permission-limited**: public read; editorial edit + publish restricted to agent/team; OTTO deploys gated by Screen 20 approval (freeze flag per page respected).
- **Mobile**: per Layout; tables scroll in-container, page never scrolls horizontally.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| All market stats (median, $/sqft, DOM, sale-to-list, supply, YoY) | currency/int/%/months, as-of date | MarketDataSnapshot (MLS), daily re-render |
| ADU-by-right %, upzoned lot count | %, int | ZoningLookupRecord (Zoneomics, 30-day cache) |
| Gross rent yield, median rent | %, $/mo | RentEstimateSnapshot (Rentometer) |
| Forecast score | 0–100 + risk label | ScoringService (fail-closed) |
| Hazard profile | categorical (fire/flood/quake) | FEMA / CAL FIRE objective data |
| Schools: name, grades, type, rating, distance | third-party attributed | SchoolDataResponse (`school_data_used_for_default_ranking: false`, `..._ad_targeting: false`) |
| Commute times | minutes at 8am | Commute engine |
| POIs (parks, dining) | named list | LocalDataRecord |
| Listings / solds | MLS whitelist fields | IDXDisplayCache / closed records |
| Editorial blocks | text, agent-reviewed flag + review timestamp | LLM draft + agent approval record |
| Canonical URL, schema payloads | `/{city}/{neighborhood}/`; Place + Dataset + FAQPage + BreadcrumbList + ItemList | Template engine |
| Sitemap entries | per-type sitemaps with lastmod; WebP images + image sitemap | Instance sitemap generator |

## Rules & compliance

- **Schools firewall (MB §16)**: school data user-initiated in behavior, identical for all users, never feeds ranking/scoring/targeting/lead capture; conversion CTAs sit OUTSIDE the schools module; verbatim §16.3 disclaimer + equal-service note non-removable; school ratings never a default ranking input.
- **Fair housing**: no crime data (hazard/climate is the compliant substitute); no demographic steering language in editorial; ComplianceProvider pass on all agent-edited prose.
- **Filter-URL governance (MB §15)**: every curated link is server-rendered, canonicalized, compliance-checked, MLS-license compliant; indexable caps 250/market and 5,000/global; dynamic long-tail = NOINDEX unless approved; "Submit to SEO" routes through the OTTO preview+approve flow (Screen 20).
- **AVM honesty**: instant values show range/confidence/as-of or "estimate unavailable" (matrix correction #7).
- **Doorway-page defense**: uniqueness validator is a hard publish gate; rollout farm-first (~15–30 neighborhoods), never metro-wide bulk.
- **Data attribution**: every local-data fact carries source attribution (MB §16 local data floor).
- **Freshness**: stats re-render daily with visible updated-date; editorial numbers monthly.

## Cross-links

In: homepage (§4, 8c, footer), sibling/parent community pages, sold pages, listing breadcrumbs, GBP posts, ads/QR destinations. Out: listing detail (S3), curated filter-URL results (S2), sold pages, city rollup `/{city}/`, school pages, contact/value capture (→ CRM S14). **Ledger events emitted**: PAGE_VIEWED, VALUATION_REQUESTED, REPORT_SUBSCRIBED, NL_QUESTION_ASKED, ALERT_CREATED, LEAD_CREATED (source `community_{slug}_*`), FILTER_URL_CLICKED. **Consumed**: daily MarketDataSnapshot renders, listing/closing events, OTTO deploy approvals (S20), agent editorial approvals.

## Open decisions

- [DECIDE] Page-generation data floor (min sales/actives before a neighborhood page exists). Interim: generate only for farm-configured neighborhoods with ≥10 sales/12mo [BEST GUESS], expand on approval.
- [DECIDE] Uniqueness-validator threshold + scope (per-metro vs global). Interim: block publish when cross-instance similarity exceeds the platform default; show side-by-side diff of offending blocks [BEST GUESS].
- [DECIDE] Ask-this-page answer engine gating (anonymous vs soft-capture after N questions). Interim: anonymous, mirroring the no-hard-gate organic policy; behavior-triggered soft prompt after 3 questions [BEST GUESS].
- [DECIDE] Chart library/interactivity level. Interim: static-rendered SVG with hover values (performance budget first); ECharts reserved for agent-side analytics (per results-dashboard memory).
- [DECIDE] Walk/bike score licensing (Walk Score API vs computed). Interim: display only if licensed provider connected; tile hides otherwise (fail-closed).
