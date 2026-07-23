# 28 · Prospecting Hub (MLS playbooks + Predictive Seller)

**Purpose** One screen of ranked opportunity lists produced by the MLS-Enabled playbooks and the Predictive Seller workflow. Every row ends in a drafted action that routes to review — never an auto-send. Every score is explainable: click it and see the contributing facts.

**Primary users** Agent. Wattson runs the playbooks (personas per registry, permission REVIEW_REQUIRED); ISA/team may work review queues per role routing.

**Entry points** App nav "Prospecting"; Wattson chat intents ("show me motivated sellers in Redwood City", "what's my open house route this Saturday?", "find expired listings I should target"); morning brief links; Predictive Seller run-complete notification; map screen seller-propensity layer → candidate card.

**Exit points** Every row's draft → Approvals/Outbox (review-gated); candidate → CRM contact record (14) or consent-capture task; buyer match → buyer's contact record + tour-invite approval; route → calendar sync; expired-outreach approved → held until legal re-list window then Outbox; disclosure auto-pull → Transaction Workspace (15).

## Layout
Desktop: **Header** — farm identity ("Farm: Friendly Acres + EPA"), run cadence note ("runs nightly" for the aggregate; each playbook shows its own cadence), nav links Predictive runs / Buyer matches. **Main** — 2-column card grid of opportunity lanes: Predictive Seller (last run summary), DOM anomalies & price cuts, Expired/off-market, Buyer matches (reverse prospecting), full-width Weekend open-house route. Each lane card expands to its full ranked table below the grid (candidates table, anomaly table, etc.). A **run launcher** button on the Predictive Seller lane (MONTHLY_REFRESH / ON_DEMAND_PROPERTY).
Mobile (375px): lanes stack vertically as summary cards; tables become swipeable row cards; route card becomes a map-first view with tap-to-navigate; approvals via bottom sheet.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Predictive Seller lane | Last run date, HIGH/WARMING counts, top candidate teaser ("318 Hurlingame 87 — owned 14y, 71% equity, valuation ×2") | PredictiveSellerRun §14.6 + candidates §14.7 (ScoringService context PROPFLOW_PREDICTIVE_SELLER) | "Open candidates table"; run launcher (run_type MONTHLY_REFRESH / ON_DEMAND_PROPERTY / ENGAGEMENT_FACT_CHANGED) | PF MB 14.6–14.7 |
| Candidates table | Sortable rows: address, owner (redacted per rules), likelihood_to_list_score, tier (HIGH/MID/LOW), estimated_list_window (0-6/6-12/12+ months), data_quality_confidence, recommended_next_step | PredictiveSellerCandidate §14.7 | Row expand → explainability card: input_facts (ownership_years, estimated_equity_pct, recent_permit_last_12m, agent_marketing_engagement) + source_facts; NO raw owner names/mailing addresses — absentee/corporate/owner-occupied badges only | PF MB 14.7; matrix correction #12 |
| Tier-routed action buttons | Per recommended_next_step: CREATE_REVIEW_TASK, PAST_CLIENT_WARM_EQUITY_TOUCH, CONSENT_CAPTURE_REQUIRED, CONTENT_NURTURE_IF_CONSENTED, MONITOR_ONLY, HUMAN_HANDOFF_REQUIRED | §14.8 routing | HIGH tier → review task, **never auto-outreach**; unknown consent → consent-capture task, not a send | PF MB 14.8; matrix correction #2 |
| Engagement-fact chip | agent_marketing_engagement true/false with the rule (≥1 high-intent OR ≥2 low-intent actions in trailing 90d) | AgentMarketingEngagementFact §14.4 | Hover → which actions counted | PF MB 14.4 |
| DOM anomalies lane | Listings sitting >150% of market-average DOM for that geo + property type, motivated-seller score, price-cut history | MLS Playbook 6 (Days-on-Market Anomalies) | Row → draft buyer-opportunity pitch in Approvals; MLS data purged from session after run | Playbook Library MLS-6 |
| Price-reduction alerts | Drops in territory cross-referenced with active buyer criteria; context-aware framing ("dropped 5% after 21 days — likely motivated") | MLS Playbook 7 | Approve → send to matched buyer; logged in GHL; listing data purged after send | Playbook Library MLS-7 |
| Expired/off-market lane | Expired/withdrawn/cancelled (last 12 months) + pre-MLS; owner-on-title verified via public records; intent classification: (a) relisting soon (b) withdrew—issues (c) sold off-market (d) not selling; ranked; draft outreach for top 10 | MLS Playbooks 3 + 10 (weekly runs) | Categories (a)/(b) get drafts → agent approval; expired drafts **hold for the legal re-list window** before eligible to send; FSBO door-knock notes drafted | Playbook Library MLS-3/10; draft §28 (re-list window inherited) |
| Buyer Match lane | New MLS listings matched to each active buyer's saved criteria; background run every 2–4 hours | MLS Playbook 4 (Buyer Match Engine) | High-fit match → drafted personalized email → agent approval → send; tour-invite drafts land in Approvals | Playbook Library MLS-4 |
| Territory monitor feed | New listings, price changes, status changes in territory — digest or real-time per preference; status changes feed attribution; new listings feed Content Calendar | MLS Playbook 5 (Active Listing Monitor) + MLS-13 (Pending→Sold Attribution: sale price, DOM, list-to-sale ratio → event ledger) | Preference toggle digest/real-time; item → listing detail | Playbook Library MLS-5, MLS-13 |
| Open-house route card | Weekend plan: own opens + competitor opens worth walking, route-ordered by geography + time with drive times; per-buyer personalized open-house lists | MLS Playbook 12 (Fridays for weekend; daily for weekday opens) | One-tap calendar sync; per-buyer lists require agent approval before sending | Playbook Library MLS-12; draft §28 |
| Score explainability popover | Contributing facts for ANY score on screen | source_facts on candidate/anomaly records | Click score → facts; math never shown/computed locally (lives in Scoring Master Sheet) | PF MB 14.2; draft §28 note |
| Run history | Past PredictiveSellerRun rows: status (REQUESTED/RUNNING/COMPLETED/FAILED), requested_by, failure_reason | §14.6 | Open a past run's candidates (append-only snapshots, SCORING_SNAPSHOT_24M retention) | PF MB 14.6, 14.9 |
| Disclosure auto-pull tile (contextual) | On offer accepted: MLS disclosure package pulled → Disclosure Analyzer → red-flag summary + credit-request draft | MLS Playbook 8 | Opens in Transaction Workspace disclosures tab | Playbook Library MLS-8; matrix Wattson gap |
| Empty/held badges | Per-lane "held: MLS compliance gate" when the MLS connector/compliance layer (CDP #11) is not green | OpenClaw framework-level MLS enforcement | — | Playbook Library (compliance enforced at framework level, built FIRST) |

### PropMatch extension — Buyer Match lane (Graeham, 2026-07-22 — logged, not yet scoped)

Extends the Buyer Match lane row above (MLS Playbook 4). Source: Graeham's PropMatch reverse-prospecting concept, captured 2026-07-22 after Jason Pantana's AiM "Summer Surge #1 — AI Heat Sheets Agent". Four extension points:

- **(a) Buy-box distilled from ALL PropFlow contact notes**, not saved criteria only — a running per-contact profile, re-distilled as notes accrue (more notes = sharper matches), with high/medium/low confidence tiers.
- **(b) Multimodal listing read** — the buy-box is compared against listing photos + description, not just beds/baths/price metadata.
- **(c) Zoneomics feasibility checks on shortlisted matches only** (cost control) — ADU/garage-conversion potential becomes an explicit match reason ("small backyard, but the garage converts — and this contact doesn't care about losing the garage"), subject to the existing zoning confidence gates + mandatory disclaimer in the PropSearch Master Brain §17.
- **(d) Outreach drafted in the contact's format** — text, email, GIF, personalized video — always into the agent approval queue; nothing auto-sends (Fair Housing + permission-based marketing, same posture as every other lane on this screen).

Urgency overlay: Pantana's Heat Score (portal saves ÷ days on market — a call-list prioritizer, NOT a sell-probability predictor). Possible v2: a true will-it-sell-fast predictor from pricing-vs-comps. Full spec: AI-Library `sources/new-2026-07/propiq-feature-reverse-prospecting-engine_2026-07-22.md`.

## States
- **Default**: lanes with last-run summaries.
- **Loading**: per-lane skeletons; a RUNNING run shows progress on its lane.
- **Empty**: "No candidates above threshold this run" / "No anomalies in territory" — with last-run timestamp; never pad with low-confidence rows.
- **Error/degraded (fail-closed)**: ScoringService down → Predictive Seller lane shows "score unavailable — run deferred"; deterministic lanes (DOM, price cuts) still render since they're facts, but their motivation *scores* disappear; MLS connector down/unlicensed → all MLS lanes replaced by "MLS access unavailable" (no cached listing display — session-purge rule); run FAILED → failure_reason shown + retry.
- **Permission-limited**: outreach approval restricted to approver roles; candidate PII (owner_name_redacted) stays redacted for non-agent roles.
- **Mobile**: as in Layout; approvals via bottom sheets.

## Data fields
PredictiveSellerRun: run id, region_profile_id, farm_geo_code (3-letter registry code), requested_by, run_type, score_version, status, timestamps, failure_reason. Candidate: full §14.7 schema (input_facts, source_coverage, source_facts, scoring_output incl. manual_review_flags + ineligible_reason, recommended_next_step). DOM row: address, DOM, market-avg DOM, ratio, reduction history, motivation score. Price-cut row: listing, % cut, days-at-price, matched buyers. Expired row: listing, status type, off-market date, owner-on-title (bool), intent class, rank, draft ref. Buyer match: buyer, listing, fit rank, draft ref. Route: stops (address, window), ordered times, drive times.

## Rules & compliance
- **Never auto-send**: a score alone never triggers outreach (§14.8); every drafted action terminates in a review queue.
- Sensitive-topic firewall (§14.3): divorce/probate/distress/etc. can only produce human_handoff_required — no score change, no tag, no audience inclusion, no priority bump; the future_life_event_signal hook stays disabled.
- Fair Housing: schools never used as a ranking factor (MLS-1 step 3); no protected-class inputs; ownership signals shown as badges only, never raw owner mailing data.
- MLS data purged from session after each playbook response (every MLS playbook); only aggregates retained (MLS-13); no MLS data through AI providers without ZDR-equivalent contract; MLS compliance enforced at framework level (CDP #11) before any playbook runs.
- Unknown consent/DNC → consent-capture task, never a send (matrix correction #2).
- Draft copy comes from approved templates/registries; missing copy → task, not invention.
- Scoring formula/thresholds live only in the PropertyIQ Scoring Master Sheet; UI displays returned outputs only.

## Cross-links
In: Wattson chat/voice intents, morning brief, map seller-propensity layer, buyer saved-criteria (CRM), farm audience definitions. Out: Approvals/Outbox (all drafts), CRM contact record (14), Past Client OS equity touches (27), Transaction Workspace disclosures (15), Content Calendar (new-listing + market-update feeds), Calendar (route sync). **Emits**: PredictiveSellerRun events, review tasks (PropFlowTask CREATE_REVIEW_TASK / SENSITIVE_TOPIC_HANDOFF), ledger attribution points (pending→sold), scoring snapshots. **Consumes**: MLS RESO Web API data (via compliance layer), ScoringService outputs, buyer criteria, engagement facts from Event Ledger.

## Open decisions
- [DECIDE] Buyer Match run frequency setting: spec says "every 2–4 hours" — interim default 3h, tenant-configurable within 2–4h band, with the cost-runaway guardrail (usage meter vs MLS API budget) surfaced on the lane [BEST GUESS on the 3h midpoint].
- [DECIDE] "Runs nightly" header vs per-playbook cadences (weekly expired, 2–4h buyer match, hourly territory monitor, Friday routes): interim — header drops the single "nightly" claim; each lane shows its own cadence chip.
- [DECIDE] Legal re-list window length for expired outreach: jurisdiction/MLS-rule dependent — interim design shows a "holds until {date} (MLS re-list rule)" chip with the date computed by the compliance layer, no hardcoded day count.
- [DECIDE] Predictive Seller monthly refresh day + HIGH-tier threshold: both live in the Scoring Master Sheet — UI reads returned tier only; run scheduling default = monthly per §14.6 run_type.
