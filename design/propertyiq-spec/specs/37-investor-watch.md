# 37 · Investor Watch + Metered Scans

**Purpose.** Two P2, honest-by-design surfaces sharing one screen: (1) the Investor Video Monitoring dashboard (Master Brain §21) — non-predictive market signals extracted from public investor content via PropCast's VideoIntelligenceService, with an explicit degraded state when v1 pattern queries aren't live; (2) the metered zoning area-scan flow (§17.7) — draw an area, get a price quote reflecting actual API cost, pay, scan, cache. Both surfaces never fabricate: no synthesized trends, no charge without a quote, no double-charge without a cached-result warning.

**Primary users.** Agent (Graeham) and team analysts. Investor-persona subscribers for the watch dashboard [BEST GUESS: v1 is agent-facing only; consumer exposure unscoped]. No client-facing output ships from this screen directly.

**Entry points.**
- Global nav / PropSearch section → "Investor watch".
- Weekly brief email/notification (Friday aggregation, §21.5) → deep link to that week's patterns.
- Map screen → "Scan this area" after drawing a polygon on a zoning-capability filter layer (§17.7) → lands on the quote modal here (or inline on the map — see Open decisions).
- Billing screen → scan history row → cached scan results.

**Exit points.**
- Signal card → source video URL (external, public content).
- Deep-dive request → REVIEW_REQUIRED approval item (Approvals inbox / Screen 24 lane) — never auto-runs (§25/§30: "Investor monitoring deep dive = REVIEW_REQUIRED").
- Watchlist editor → saves customized source list.
- "Run scan" → payment flow (Stripe per platform integrations [BEST GUESS]) → cached results open on the map screen as a filter layer.
- Billing & scans nav → Billing/usage screen with full scan history.
- Cached scan "reopen" → map layer render, no charge.

## Layout

**Desktop (two-column grid, 1fr/1fr — matches draft):**
- **Header (sitehead):** "Investor watch" · subtitle "Watchlist: N channels · weekly brief Fridays". Right nav: **Billing & scans**.
- **Left column — This week's patterns:**
  1. Pattern summary card: sentiment lines, strategy-shift callouts, deep-dive queue status.
  2. Signal feed: individual `InvestorMonitoringSignal` cards, filterable by geo_tag / topic_tag / strategy / signal_type / sentiment.
  3. Watchlist manager card: source list with add/remove.
- **Right column — Area scans (metered):**
  1. Scan launcher card: "Draw an area → quote → run → cached" with link to map draw tool.
  2. Pending quote card(s): area name, parcel count, quoted price, Run scan button.
  3. Scan history list: date, area, layer type (ADU / SB9 / garage conversion), price paid, cached badge, reopen action.
- **Footer notes (both columns):** honesty microcopy — degraded-state note (left), re-run-warning note (right). Inherited verbatim intent from draft.

**Mobile (375px):** single column: header → pattern summary → signal feed (cards stack) → watchlist (collapsed accordion) → scans section (launcher, quotes, history). Quote modal becomes a bottom sheet; map drawing happens on the map screen and returns here.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Weekly patterns card | Aggregated read: e.g. "Sentiment on Bay Area multifamily: cooling (3 of 6 tracked)"; "2 channels pivoting ADU-value-add" | Weekly aggregation over `InvestorMonitoringSignal` (§10.18); cadence weekly (§21.5) | Click line → contributing signal cards | §21.5–21.6, draft |
| Signal cards | One public-content signal: platform icon (YOUTUBE / PODCAST_VIDEO / PUBLIC_TIKTOK_APPROVED_SOURCE / OTHER), pattern_summary (short excerpt only), sentiment_label (BULLISH/BEARISH/NEUTRAL/MIXED/UNKNOWN), signal_type chip (CAP_RATE_DISCUSSION / SUBMARKET_SENTIMENT / STRATEGY_PATTERN / OFF_MARKET_STRATEGY_PATTERN / ADU_DISCUSSION / OTHER), geo/topic/strategy tags, source_window dates, extraction-confidence (labeled "extraction confidence — not a score") | `InvestorMonitoringSignal` §10.18 via `PropSearchVideoPatternQuery` (§12.11, mode SMART_SAMPLING) | Open source URL; tag click filters feed | §10.18, §12.11 |
| Non-prediction disclaimer | Persistent line: "Content-discussion signals — not predictions, not investment advice, not scores" | static | none | §21.6, §10.18 |
| Geo filter | User-selected geography filter over nationally-monitored sources | geo_tag extraction, hybrid scoping | Select market → refilter | §21.4 |
| Watchlist manager | Source list (v1 seed: BiggerPockets, Pace Morby, Codie Sanchez, Dion Talk, investor podcast networks, owner-approved Bay Area channels) with add/remove; each row shows access basis (public/API-approved) | watchlist config record [BEST GUESS: tenant-level settings record — no typed record in Brain] | Add source (must be public/approved-API; TikTok ad-library scraping blocked; owner personal accounts never used for auth — enforced with inline rejection reasons) | §21.3 |
| Refresh cadence note | "New content checked daily · dashboard aggregates weekly" | static per §21.5 | none | §21.5 |
| Deep-dive request button | Request per-video/topic deep dive → creates REVIEW_REQUIRED approval item; queue status shown ("deep-dive queued: …") | `InvestorMonitoringMode = DEEP_DIVE_REVIEW_REQUIRED` (§8); action PROPSEARCH_QUERY_INVESTOR_MONITORING (§30 action registry) | Request → routes to Approvals; status chip PENDING/APPROVED/DONE | §21.5, §30 |
| Weekly brief subscription | "Weekly brief Fridays" indicator; toggle destination [BEST GUESS: goes through report catalog / internal email, review-first if ever client-facing] | Report requirements §23 | Toggle on/off | §21.5, §23 |
| Degraded-state banner | Full-panel replacement: "Video ingestion/report records available; pattern dashboard unavailable" when only v0 exists | `PropSearchVideoPatternResponse.available_capability = V0_INGEST_ONLY`; flag VIDEO_INTELLIGENCE_V1_UNAVAILABLE | none — no synthesized data, safe workflows continue | §21.2, §12.11 |
| Scan launcher | Explains draw→quote→pay→cache flow; "Draw area" deep-links to map polygon tool | — | Opens map draw mode for layer type ADU / SB9_LOT_SPLIT / GARAGE_CONVERSION | §17.7 |
| Quote card/modal | Area name, parcel count (e.g. "1,240 parcels"), layer type, quoted price reflecting actual API cost, expiry [BEST GUESS: quotes expire, e.g. 7 days — pricing pass with Mehmood/Sami pending] | metered-scan quote service [DECIDE — billing design pass not yet scoped, §17.7] | "Run scan" → payment confirm → scan executes; cancel | §17.7 |
| Cached-result warning | On re-running an identical/overlapping polygon: "You have a cached result from ⟨date⟩ — reopen free, or re-run for $N" | scan cache keyed by polygon + layer type | Choose reopen (free) vs re-run (new charge — §17.7 "re-running the same area is a new charge") | §17.7, draft |
| Scan history rows | Date, area label, layer type, parcels, price paid, cached badge, reopen link | scan/billing records [BEST GUESS shape] | Reopen → map layer from cache; receipt link | §17.7, draft |
| Billing & scans nav | Links to Billing screen (payment method, scan invoices, usage) | billing provider | navigate | matrix gap ("billing/usage screen with scan history") |
| Per-property zoning note | Microcopy: "Per-property zoning facts are always free on property detail — scans are for area-wide layers only" | static | none | §17.7 (no separate charge for property detail facts) |
| Empty-state (no signals this window) | "No signals matched your filters this window" + widen-window suggestion | query result | adjust filters | [BEST GUESS, standard pattern] |

## States

- **Default:** v1 available, this week's aggregation + signal feed populated; ≥1 cached scan in history.
- **Loading:** skeleton cards per column; scans column loads independently of the monitoring column (different services — a VideoIntelligence outage must not hide scan history).
- **Empty:** first visit — watchlist card front-and-center with seed list preloaded and "monitoring begins after first daily check"; scans column shows launcher only.
- **Degraded (fail-closed):**
  - VideoIntelligence v0-only → left column collapses to the §21.2 banner verbatim; `manual_review_flag = VIDEO_INTELLIGENCE_V1_UNAVAILABLE`; watchlist still editable; scans unaffected. Never fabricated pattern data.
  - Quote service unavailable → "Scan pricing unavailable — try again later"; Run buttons disabled; no scan can run unquoted.
  - Payment failure → scan not run, no partial charge, quote retained.
  - Scan job failure post-payment → status FAILED with auto-credit/retry [DECIDE — billing pass].
- **Permission-limited:** deep-dive requests and paid scans restricted to owner/admin roles [BEST GUESS]; viewers see dashboard read-only, no Run scan.
- **Mobile:** single column per Layout; quote confirm as bottom sheet with explicit price restated on the confirm button ("Pay $19 & run scan").

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| investor_monitoring_signal_id, tenant_id | ids | `InvestorMonitoringSignal` §10.18 |
| source_video_url, source_platform, content_hash | url, enum, hash | §10.18 (minimal storage: hash, URL, basic metadata, short excerpt/summary, timestamp, source — never full transcripts/comment threads/3rd-party PII, §21.3) |
| geo_tag, topic_tag, strategy | strings / InvestorStrategy enum | §10.18 |
| signal_type, sentiment_label | enums §8/§10.18 | §10.18 |
| pattern_summary | short text | §10.18 |
| confidence | 0–1, labeled extraction confidence | §10.18 |
| source_window.start_at/end_at | ISO datetimes | §10.18 |
| retention_class | "REDDIT_MINIMAL_24M" (24-month minimal retention) | §10.18 |
| available_capability | V0_INGEST_ONLY / V1_PATTERN_QUERY | `PropSearchVideoPatternResponse` §12.11 |
| Scan: polygon geometry, layer_type (ADU/SB9/garage), parcel_count, quote_amount (USD), quote_created_at/expires_at, paid_at, status (QUOTED/PAID/RUNNING/CACHED/FAILED), cache key, result asset/layer ref | [BEST GUESS shapes — §17.7 defines mechanic, not records] | metered-scan billing design pass (pending) |

## Rules & compliance

- **Availability gate (§21.2):** dashboard requires VideoIntelligenceService v1 pattern queries; v0 → banner + flag, never fabricated data.
- **Non-prediction rule (§21.6, §10.18):** signals are read-only market-intelligence summaries — not predictions, not investment advice, not ScoringService inputs, not protected-targeting inputs, not property-specific off-market lead claims. UI must never render them as leads or scores.
- **Source legality (§21.3):** public or approved-API access only; no TikTok ad-library scraping; owner's personal accounts never used for scraping/auth; minimal storage posture.
- **Deep dive = REVIEW_REQUIRED (§21.5, §30):** user request routes through approvals; SMART_SAMPLING is the only autonomous mode.
- **Feedback loop (§21.7):** no Event Ledger event for saved/shared/acted-upon feedback in v1 — internal operational tuning only; UI must not promise "improves your recommendations."
- **Metered scan honesty (§17.7):** quote before charge, always; cached results reusable free; identical-area re-run warns before charging again; per-property zoning facts never metered.
- **Quiet compliance:** signals carry source_facts; excerpts stay short (copyright posture per minimal-storage rule).

## Cross-links

- **In:** global nav, Friday weekly brief link, map draw tool (scan flow), Billing screen.
- **Out:** external source videos; Approvals inbox (deep-dive REVIEW_REQUIRED items); map screen (cached scan layers, zoning-capability filter layers §17.7); Billing screen; watchlist settings.
- **Ledger events:** monitoring emits none of PropSearch's four events by itself (query action PROPSEARCH_QUERY_INVESTOR_MONITORING emits none, §30); §21.7 forbids an unregistered feedback event. Scans: `GENERATED_ASSET_CREATED` only if a generated asset is created (per PropSearchZoningLookupWorkflow rule); payment events belong to the billing provider, not the PropSearch ledger [BEST GUESS].
- **Consumes:** VideoIntelligenceService (PropCast-owned), ZoningProvider/Zoneomics (scans), ScoringService not used here (deliberately — signals are never scoring inputs).

## Open decisions

- **[DECIDE] Metered-scan billing implementation** (§17.7 flags it explicitly: "mechanic approved, implementation isn't scoped — needs its own product/billing design pass with Mehmood/Sami"). Interim design: Stripe one-off charges, quote = parcel_count × per-parcel API cost + margin, quotes expire in 7 days, failed scans auto-credit. UI above is unaffected by the pricing formula chosen.
- **[DECIDE] Where the quote modal lives:** interim — drawing happens on the map screen; the quote modal renders there, and this screen holds the launcher, pending quotes, and history. One quote object, two surfaces.
- **[DECIDE] Weekly brief delivery channel:** interim — in-app notification + internal email (send-not-draft per workspace rule); becomes a §23 report type if client-facing later.
- **[DECIDE] Consumer/investor-subscriber access to the watch dashboard:** interim — agent/team only in v1.
- **[BEST GUESS] Watchlist config record shape** — no typed record exists in the Master Brain; assume tenant-level settings entity with per-source access-basis metadata.
- **[BEST GUESS] Draft's deep-dive example ("transcript + claims check")** must respect §21.3 storage limits — deep-dive output stores summary + excerpt, not a retained full transcript where not licensed; interim design renders the deep-dive report ephemeral/linked rather than stored verbatim.
