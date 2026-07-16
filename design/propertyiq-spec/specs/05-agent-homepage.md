# 05 · Agent Homepage (consumer-facing site, per-agent instance)

**Purpose** — The public front door of each agent's white-labeled PropertyIQ instance. Seller-first: NAR data shows 66% of sellers arrive by referral and use the site to *validate* the agent, so the page leads with dual capture (home value + search), then automated farm proof. It is also the link-equity hub for the whole instance (every community page, listing page, and curated search inherits authority from here).

**Primary users** — Consumers (sellers validating a referral, buyers, nosey neighbors); secondarily the agent (section reorder/hide via CMS-lite controls) and crawlers/LLMs (SEO/AEO surface).

**Entry points** — Direct/referral traffic, GBP profile link, postcard QR codes (switchy short links), email signatures, PropReach ad landing fallback, organic search for "{agent name}" and "{market} real estate agent", internal links from community/listing/sold pages.

**Exit points** — Home-value widget → instant AVM range page + lead intake (`/approved-leads`, source-tagged) → CRM (Screen 14) + AI text-back; NL search box → Screen 1/2 (search/results); lens chips → 6 guided-flow + feature-explainer pages; farm map & Just-Sold cards → sold pages / Screen 10 seller-report capture; neighborhood cards + areas-served links + footer mesh → Screen 6 community pages; "monthly report" links → report-subscribe capture; listings → Screen 3 property detail; reviews → GBP; "Work with me"/call/book → contact & booking (PropFlow slots, Screen 21 booking settings); PropCast content cards → content/video pages; sticky CTA bar → value / search / call.

## Layout

Desktop: single-column **section stack** inside the branded site chrome (header: avatar, agent name + tagline, nav Search·Communities·Sell·Reviews·Contact). Sections in default order: 1 Hero → 2 Farm proof → 3 Just Sold → 4 Explore the farm → 5 Featured listings → 6 Reviews → 7 Meet the agent + video → 8 Latest content → 8b FAQ → 8c Areas served → 9 SEO text block → SEO footer → sticky CTA bar → "Powered by PropertyIQ" + Equal Housing footer. Agents may **reorder/hide sections, never redesign** (locked template; brand vault variables only). Valuation capture must sit in the first viewport — below-fold widgets lose 60–70% of submissions (draft research note).

Mobile (375px): same stack, hero cards stack vertically (value card first), lens chips wrap to horizontal scroll row, stat grids collapse 2-up, section CTAs are replaced by the sticky bottom CTA bar (one-ask-per-viewport rule — the sticky bar never stacks with section CTAs), nav collapses to hamburger, hero aerial image served at mobile crop.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Site header (avatar, name, nav) | Agent identity + top nav | Brand vault / identity config (name, DRE 01466876, brokerage) | Nav links | Draft s5; brand-vault flow (Screen 8/23) |
| Hero H1 + subhead | Keyword-bearing headline: market + value prop + farm proof ("14 homes sold in this neighborhood") | Brand vault + farm sales stats (MLS) | Agent-editable, keyword-guided | Draft s5 §1 |
| Hero background | Soft aerial photo of the FARM itself, dimmed 88%, brand-tinted | ImageryProvider (farm aerial) | none | Draft s5 §1 note |
| Home-value capture card (primary, brand-bordered) | Address input → instant AVM range; "precise valuation from {agent} in 24h" | AVMProvider → AVMSnapshot; lead → `/approved-leads` | Submit → value page + lead created + instant AI text-back (consent-gated) + CRM source tag `homepage_value` | Draft s5 §1; PropFlow intake; matrix correction (consent) |
| NL search card | "3bd, good schools, 30 min to Palo Alto…" → Screen 1 flow, no sign-up | SearchRecord / parser | Submit → results (Screen 2) | Draft s5 §1 |
| Six lens chips | Commute Lens · School Boundaries · ADU Check · Yield Engine · Risk Lens · Market Signals — ONE canonical capability pattern site-wide | Feature registry; ADU count from Zoneomics | Each deep-links into guided flow AND its indexable feature-explainer page (6 pages) | Draft s5 §1 |
| Farm proof section | "By the numbers": interactive map of every farm sale (sold + active pins) + 4 stats: homes sold (14), volume ($19.4M), sale-to-list (103%), DOM vs area (9 vs 12) | MLS via IDXProvider; agent production records; auto-updated | "Get your street's numbers →" → value capture; map pins → sold/listing pages | Draft s5 §2 |
| Just Sold cards (3+) | Auto-generated nosey-neighbor cards: sold price, street, list price, days, offers | MLS closed data; auto-generated on each closing | Card → permanent sold page; "Curious what yours would get?" → value capture | Draft s5 §3 |
| Explore-the-farm neighborhood cards | Photo, name, median, active count, "monthly report" link | Community-page data engine (Screen 6) | Card → community page; report link → subscribe capture (email consent) | Draft s5 §4 |
| Featured listings (3) | Price, address, beds/baths + one-line intelligence strip (all-in monthly / ADU / vs-comps) | IDXDisplayCache + intelligence engines | Card → Screen 3 detail | Draft s5 §5 |
| Reviews strip | Star aggregate (e.g. 4.9★), one seller-story quote, "62 Google reviews →" | GBP API (live-pulled) | Link → GBP reviews | Draft s5 §6 |
| Meet-the-agent + video | Bio, years, brokerage, DRE (locked from identity.json), "Work with me" CTA, 16:9 intro video | Brand vault; video auto-fed from PropCast avatar pipeline | CTA → contact/booking; video play | Draft s5 §7; brand tripwire |
| Latest content cards | 2 videos + farm-letter subscribe | PropCast published content (ContentLock'd versions only) | Play / subscribe | Draft s5 §8; ContentLock rule (matrix correction #10) |
| FAQ block (FAQPage schema) | 3+ agent-market Q&As; commission answer is agent-editable + compliance-checked | Templated from farm data; ComplianceProvider pass on edits | Expand/collapse | Draft s5 §8b |
| Areas-served geo paragraph | Every neighborhood name = link into its guide; "Se habla español"; mirrors LocalBusiness areaServed schema | Farm config | Links → community pages | Draft s5 §8c |
| SEO text block | ~120-word templated crawlable body copy (agent, brokerage, city keywords, neighborhood links, feature keywords), auto-generated from brand vault + farm config, agent-editable | Brand vault + farm config | Edit via CMS-lite (compliance-checked) | Draft s5 §9 |
| SEO footer (4 columns) | Neighborhoods / Popular searches / Market data / Work with me link lists | Filter-URL library (links never 404) + community index | Links | Draft s5 footer; PropSearch MB §15 |
| Sticky CTA bar | Appears once hero scrolls away: Get my home's value · Search homes · 📞 Call | — | 3 CTAs; replaces section CTAs on mobile | Draft s5 |
| Footer strip | "Powered by PropertyIQ" + "Equal Housing Opportunity" | Platform | none | Draft s5 |
| Behavior-triggered soft prompts | Repeat-visit / save behavior soft capture (no hard gate on organic) | Visitor session events | Dismissible prompt | Draft s3 lead policy, applies site-wide |
| CMS-lite section controls (agent view) | Reorder / hide sections; edit variable slots | Instance config | Drag-reorder, toggle | Draft s5 note ("agents reorder/hide, never redesign") |
| OTTO SEO layer | Title/meta/heading tuning through template variable slots only; changes route via SEO Console preview+approve (Screen 20) | SearchAtlas/OTTO via SeoProvider | Not user-visible; audit trail in SEO console | Matrix gap (SEO console); PropSearch MB §12.12 |

## States

- **Default**: all sections populated from live data.
- **Loading**: static-rendered shell (sections are server-rendered); widgets (map, value input) lazy-load — LCP budget < 2.5s (draft SEO spec).
- **Empty/new agent**: farm-proof and Just-Sold sections auto-hide until ≥1 closed sale exists (never show zeros); reviews strip hides below a review threshold [BEST GUESS: hide if < 5 reviews]; featured listings falls back to farm actives if the agent has no own listings [BEST GUESS].
- **Degraded (fail-closed)**: AVM unavailable → value card keeps address capture but promises "valuation from {agent} in 24h" only, never a fabricated instant number (matrix correction #7); GBP unreachable → reviews strip hides; PropCast feed empty → content section hides; farm map tile failure → stat tiles remain, map placeholder with retry.
- **Permission-limited**: consumers see everything (public page); CMS-lite controls only for the owning agent/team roles.
- **Mobile**: as in Layout; sticky CTA bar is the sole persistent ask.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| Agent name, brokerage, DRE, phone, email, markets | text; DRE always 01466876 for Graeham's instance | identity.json / brand vault (read-only on page) |
| Farm stats: homes sold, volume, sale-to-list %, DOM | int, $abbrev, %, days | MLS closed data + agent production, auto-refresh [BEST GUESS: nightly] |
| Just-sold card: address, sold $, list $, DOM, offer count | MLS whitelist fields only | IDXListingRecord (closed) |
| Neighborhood card: name, median $, active count | from community data engine | MarketDataSnapshot per neighborhood |
| Listing card: price, address, bd/ba, intelligence line | MLS + computed | IDXDisplayCache + CashflowEstimateSnapshot |
| Review aggregate + quote | float 1 decimal + text | GBP API |
| Value-capture lead: address, contact info (progressive) | address first; contact on step 2 | LeadIntake `/approved-leads`, source tag `homepage_*` per widget |
| Schema payloads | RealEstateAgent + LocalBusiness (NAP, DRE, areaServed, stars), WebSite + SearchAction, FAQPage | Rendered from brand vault + farm config |

## Rules & compliance

- **Brand tripwire**: DRE renders only from identity.json; the known-bad legacy DRE is blocklisted repo-wide (see identity.json blocklist).
- **Consent**: every form submission creates a contact with captured-consent evidence for the channel used; instant AI text-back fires only with SMS consent capture at the form (checkbox + TCPA language) — imported/unknown consent blocks outreach (matrix correction #11). [BEST GUESS: form includes an explicit "text me my value" opt-in line.]
- **Fair housing**: no crime data anywhere; no demographic characterizations in editorial slots; Equal Housing Opportunity mark in footer; lens set excludes any steering lens.
- **No hard lead gate on organic traffic** — behavior-triggered soft prompts only; hard gates reserved for PPC and agent-configurable (draft s3 policy).
- **Compliance pass on agent-editable text** (FAQ, hero H1, SEO block) before publish — ComplianceProvider, fail-closed to previous approved version.
- **AVM display honesty**: instant value always shows range + confidence + as-of date, or "estimate unavailable" (matrix correction #7).
- **PropCast content**: only ContentLock-approved versions render; a revoked lock removes the card (matrix gap: revocation checklist).
- Uniqueness across agent instances: hero/editorial variable slots must differ per agent enough to pass the platform uniqueness validator (shared with Screen 6) [BEST GUESS: same validator applies to homepage editorial blocks].

## Cross-links

In: GBP, postcards/QR, ads, community pages, sold pages, email signatures. Out: Screens 1/2 (search), 3 (detail), 6 (community), 10 (seller report capture path), sold pages, contact/booking. **Ledger events emitted**: PAGE_VIEWED, VALUATION_REQUESTED, SEARCH_SUBMITTED, LEAD_CREATED (with source tag), REPORT_SUBSCRIBED, CTA_CLICKED, CONTENT_PLAYED — all attribution-keyed for Screen 31. **Consumed**: content-published (PropCast), listing-closed (MLS) to refresh Just Sold, review updates (GBP).

## Open decisions

- [DECIDE] Instant AVM range shown pre-contact vs after contact capture. Interim: show range instantly with confidence + as-of date (trust-first, matches "no sign-up required" search promise); precise valuation is the contact hook.
- [DECIDE] AI text-back vendor/path (GHL interim vs PropFlow native). Interim: route through PropFlow messaging with ComplianceProvider pre-send check; UI unaffected.
- [DECIDE] Review source beyond GBP (Zillow reviews?). Interim: GBP only — one live source, honest count.
- [DECIDE] Section-stack CMS editing surface (in-app vs onboarding-only). Interim: simple reorder/hide panel in Settings > Website [BEST GUESS].
- [DECIDE] "Se habla español" / multilingual toggle per agent. Interim: brand-vault boolean flag rendering the line + multilingual NL search chip.
