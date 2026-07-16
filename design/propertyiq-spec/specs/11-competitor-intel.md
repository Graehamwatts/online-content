# 11 · Competitor & Channel Intelligence

**Purpose.** The analysis layer for competing agents: one profile screen that fuses MLS production data, official-API channel monitoring (YouTube/Instagram/GBP/website), and SearchAtlas keyword-gap data into a gap matrix and a living, tracked counter-plan. Every insight terminates in a counter-move action — the no-dead-end-alerts rule.

**Primary users.** The agent. Read-only for team members without strategy permission. Never client-facing; insights are for the agent's strategy and are never republished (draft compliance rail).

**Entry points.**
- Click a competing agent anywhere: farm watch card (Command Center), a map pin's listing agent, a listing page's agent attribution (draft note).
- "Watch list (N)" nav within this screen (up to ~5 agents per farm).
- Monday briefing / Command Center farm-watch card links when the weekly refresh detects changes.
- SEO Console keyword-gap tab links to the matching competitor profile.

**Exit points.**
- Gap-matrix "Move" links: PropCast counter-series brief; SEO Console (OTTO gap plan); PropCast drafts queue; open-lane content brief.
- "Queue the counter-plan" → creates the plan object; content items → PropCast gauntlet → Approvals; ads/postcards → PropReach campaign wizard / direct-mail flow (all approval-gated downstream).
- Counter-series episode approval → Global Approvals Inbox.
- Postcard action → farming/direct-mail flow; HIGH-tier predictive-seller owners route to a **review task, never auto-outreach** (matrix correction #2).
- "← Farm watch" back to Command Center.

## Layout

**Desktop.**
- **Header (site strip):** competitor avatar/initials (crit color), name + brokerage, meta line ("Competitor profile · watching since {month} · farm overlap: {area}"), nav: "← Farm watch" · "Watch list (N)".
- **Row 1 — stat row (5 tiles):** Farm listings (12mo), Avg sale-to-list (with "yours:" comparator), Avg DOM (comparator), Price accuracy vs model, Est. ad activity.
- **Row 2 — two-column grid:** left = **Channels card** (YouTube / Instagram / GBP / Website rows); right = **Gap matrix** table (Territory | Her | You | Move).
- **Row 3 — Wattson's summary card** (brand-soft): plain-English read + three action columns (This week / This month / Watch & measure) + living-plan footnote.
- **Row 4 — Counter-plan bar:** one-line strategy + "Queue the counter-plan" button.
- **Footer — compliance rail** (small, always visible): official-API/public-data-only boundary, storage limits, watch-list cap, weekly refresh.

**Mobile (375px).** Stat row becomes a 2-up grid then 1 (ad activity last). Channels card above gap matrix, stacked. Gap matrix scrolls horizontally in its own container. Wattson summary columns stack vertically (This week first). Counter-plan button full-width sticky at bottom.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Header identity | Competitor name, brokerage, watch-since date, farm overlap area | watch-list record + MLS agent data | back link; watch-list switcher | Draft Screen 11 |
| Watch list nav | Count of watched agents (cap ~5 per farm) | watch-list store | open list; add/remove agent; add disabled at cap with explanation | Draft compliance rail |
| Farm listings stat | Competitor listings in the farm, 12mo + trend note ("3 of last 5 new") | MLS/IDX production data | click → listing list | Draft |
| Sale-to-list stat | Competitor avg vs yours | MLS closed data | tooltip: sample size + window | Draft |
| DOM stat | Competitor avg DOM vs yours | MLS | tooltip | Draft |
| Price-accuracy stat | List vs model delta ("−3.1% vs model — tends to underprice") | MLS + valuation model | tooltip: per-listing breakdown; becomes a seller-presentation talking point in the summary | Draft |
| Ad-activity stat | Estimated paid activity per platform ("Meta: active · 2 listing campaigns") | **Meta Ad Library API only** (official, free); Google/TikTok ad libraries OFF until legally approved | click → minimal-record ad list (hash/URL/excerpt/summary) | PropReach MB §13.3/13.4; PropCast MB API table |
| Channels card header | "Official APIs & public data only (no scraping; store hash/URL/excerpt, never full copies)" | — | none — the boundary is stated on-screen | Matrix correction #5; PR §13.4 |
| YouTube row | Subs, cadence, avg views, top series | YouTube Data API (official, free) — full 90-day set, normalized for channel age/subscribers, 7-day view velocity noted | expand → recent videos (metadata only) | PropCast MB Demand/Supply layer |
| Instagram row | Followers, cadence, reels avg, format insight ("listing reels outperform talking-head 4:1") | official/legal-access path; normalize by creator size, account age, recency; saves+shares weighted 10× over likes | expand | PropCast MB supply intelligence; **[DECIDE] IG access path** (see Open decisions) |
| GBP row | Review count + rating vs yours, posting cadence | GBP/Places public data | link to SEO Console local grid | Draft |
| Website row | Platform/template, key ranking ("#2 for {keyword}"), content-absence insight ("no ADU/investor content") | SearchAtlas rank + site crawl of public pages | link to SEO Console gap tab | Draft |
| Gap matrix table | Territory rows: content lanes, SEO keywords, reviews, unclaimed lanes; columns Her / You / Move | fusion of the three engines | every Move cell is an action link (counter-series brief, OTTO gap plan, queued drafts, open-lane brief, "hold" states) — **no row without a Move** | Draft; no-dead-end-alerts rule |
| Format-gap classification | Gap rows tagged with the 7-type gap code: VOLUME_GAP, QUALITY_GAP, GEO_GAP, FORMAT_GAP, RECENCY_GAP, ANGLE_GAP, DEPTH_GAP | PropCast supply-intelligence classifier | tag chip filters the matrix | PropCast MB "7-type competitor gap classification" |
| Wattson summary | Plain-English strategic read; explicitly avoids survivorship-bias copying ("you don't need to out-post her — own the unclaimed lanes") | Wattson over fused data | regenerate; cite-sources expander [BEST GUESS] | Draft; PropCast MB Part on survivorship bias |
| This week / This month / Watch & measure columns | Concrete tracked actions with completion state (✓ / pending / in Approvals) | plan object + ledger completion tracking | each action deep-links to its module | Draft ("strategy with a scoreboard, not a memo") |
| Living-plan footnote | Re-scored monthly; plan auto-updates; changes land in Monday briefing; farm-share metric (e.g. 20% → target 30%) | monthly re-score job | none | Draft |
| Counter-plan bar | One-line plan + effort estimate + **Queue the counter-plan** button | Wattson plan generator | queue → creates plan; all outbound items route to gauntlet/Approvals/review tasks — button queues work, never sends anything | Draft; matrix corrections #1/#2 |
| Compliance rail | Public-data-only, no scraping behind logins, never republished, cap ~5 agents, weekly refresh, changes → farm-watch card | — | none | Draft |
| Empty state (new watch) | "Collecting data — first full profile after the next weekly refresh"; MLS stats appear first | — | — | [BEST GUESS] |
| Degraded state | Per-engine unavailability chips (see States) | — | — | PR §13.2 fail-closed pattern |

## States

- **Default:** full profile as drafted.
- **Loading:** skeleton stat tiles; channels card rows shimmer.
- **Empty:** newly-watched agent → partial profile (MLS stats render as soon as available; channel rows show "first refresh pending"). No watched agents → intro card + "watch an agent from farm watch or any listing."
- **Error/degraded (fail-closed):**
  - VideoIntelligence v1 unavailable → pattern/format insights (e.g. "reels outperform 4:1", format-gap tags) disappear and a chip says "pattern analysis unavailable"; a manual-review flag is logged; MLS and rank data remain. **Never fabricate pattern data** (PR §13.2; matrix PropSearch note "never fabricated data").
  - Rank API down → SEO rows show "rank data unavailable."
  - Ad Library unreachable → ad-activity tile shows "unknown," not last-known-as-current.
  - Any comparator missing ("yours:") renders as "—", never 0.
- **Permission-limited:** read-only; "Queue the counter-plan" and Move actions hidden; watch-list editing disabled.
- **Mobile:** per Layout.
- **Stale:** all channel data carries an as-of date; if a weekly refresh is missed, a stale banner shows the last refresh date.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| competitor_agent_id, name, brokerage, DRE (display only) | ids/strings | MLS agent record |
| watch_since, farm_overlap_area | date; geo label | watch-list record |
| farm_listings_12mo, sale_to_list_pct, avg_dom, price_accuracy_delta | numbers with sample window | MLS/IDX closed + active data |
| own comparators (your sale-to-list, DOM, review count, farm share) | numbers | own MLS production + GBP + farm analytics |
| ad activity | platform + status + campaign count | Meta Ad Library API (minimal records) |
| Competitor-ad record | source, ad_library_url, content_hash, short_excerpt, analysis_summary, created_at — **and nothing more** | COMPETITOR_AD_ANALYZED storage-allowed list (PR §13.4) |
| Channel metrics | subs/followers, cadence, avg views, top series; normalized scores | YouTube Data API / IG path / GBP; PropCast normalization layer |
| Gap row | territory, her_status, your_status, gap_type (7-enum), move_action(ref), move_status | fusion layer + plan object |
| SEO gap keywords | keyword, her rank, your rank, volume | SearchAtlas rank API (shared with Screen 20) |
| Counter-plan | plan_id, actions[] (module ref, due bucket, completion), farm-share metric + target, rescore_date | plan store + ledger |
| Refresh metadata | last_refresh_at (weekly), next_rescore (monthly) | scheduler |

## Rules & compliance

- **Official APIs or manual review only — no scraping** of competitor channels; the design labels monitoring "official-API monitoring" and shows the legal-access-first boundary on-screen (matrix correction #5). Google/TikTok ad-library scraping is off-limits until legally approved (PR §13.3). No data from behind logins.
- **Minimal storage:** competitor content stored only as content_hash, url, basic_metadata, short_excerpt, ai_summary, created_at, source. Forbidden: full bodies, full comment threads, third-party PII beyond minimal public metadata (PR §13.4). Retention per REDDIT_MINIMAL_24M-class policy for competitor-ad minimal records.
- **Never republish** competitor insights; agent-strategy use only.
- **No auto-outreach:** counter-plan postcard/outreach items targeting owners route through review tasks; Predictive-Seller HIGH-tier candidates can NEVER auto-outreach; unknown consent/DNC produces consent-capture tasks, not sends (matrix correction #2). Counter-series content goes through PropCast's ContentLock + one-approval flow (correction #9); nothing dispatches from this screen.
- **No implied surveillance of named people:** never claim or imply a named contact visited a competitor site or watched competitor videos (PR §8.8, §12 school rules). Competitor-intent custom segments (if a plan action creates one) are Display/YouTube-only intent approximation with the forbidden-inputs list — handled in PropReach, linked from here.
- **No protected-class/steering inputs** anywhere in gap analysis or plan actions (school quality, family status, etc. — PR forbidden-segment list).
- **Survivorship-bias guard:** channel analysis uses the full 90-day competitor output (not just hits), normalized for creator size/account age/recency; saves+shares weighted 10× over likes (PropCast MB). Wattson's summary must reason from gaps, not "copy their winners."
- **Fail closed** on missing engines (see States) — no fabricated patterns or ratings.
- Watch list capped at ~5 agents per farm; weekly refresh; monthly re-score.

## Cross-links

- **In:** Command Center farm-watch card; map pins; listing pages; Monday briefing; SEO Console keyword-gap tab.
- **Out:** PropCast (counter-series brief, ADU/open-lane drafts, gauntlet); SEO Console Screen 20 (OTTO gap plan, local grid); PropReach (campaign wizard, competitor-intent segment); direct-mail/farming flow (review-gated); Global Approvals Inbox (all content/campaign approvals); Ideation Canvas (COMPETITOR_VIDEO nodes, P2).
- **Ledger events consumed:** `COMPETITOR_AD_ANALYZED`, `VIDEO_INTELLIGENCE_PATTERNS_UPDATED`, MLS listing events for farm stats, plan-action completion events.
- **Ledger events emitted:** [BEST GUESS] `COUNTER_PLAN_QUEUED` / plan-action state changes as ledger rows (completion "tracked from the ledger" per draft); review-task creation events for outreach items.

## Open decisions

- **[DECIDE] Instagram data path:** the legacy PropCast pipeline used Apify scraping; the PropReach legal-access-first rule and matrix correction #5 mandate official-API/manual-review. Interim design: label the row "official/public data" and populate from the IG Graph API where OAuth-accessible (own + business-discovery metadata) with manual-review fallback; UI unaffected by which compliant path wins.
- **[DECIDE] Valuation model for price-accuracy:** interim = the platform's own AVM midpoint at list date; shown as "vs model" with tooltip disclosure.
- **[DECIDE] Farm-share metric definition:** interim = listings taken by agent ÷ total farm listings, trailing 12mo ([BEST GUESS]); targets user-set (the 20%→30% figure in the draft is example data, not a spec number).
- **[DECIDE] Watch-list cap exact number:** draft says "~5 per farm" — interim hard cap 5 with an admin override.
- **[DECIDE] Wattson summary regeneration cost controls:** interim = regenerate on weekly refresh + on-demand button, rate-limited [BEST GUESS].
