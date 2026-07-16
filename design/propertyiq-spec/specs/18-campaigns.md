# 18 · Campaign Manager (PropReach)

**Purpose.** The owner-facing paid-media surface: every campaign walks a 10-state machine and a 12-step preflight, the owner approves plain-language bundles (never acts like a media buyer), and nothing spends autonomously outside an explicitly configured spend envelope. Blocked campaigns always name the exact rule violated and offer the compliant alternative.

**Primary users.** Agent/owner (Graeham-class solo agent); team admin for spend settings. Wattson may draft campaigns conversationally but never bypasses gates (PropReach MB §7.7).

**Entry points.** Left-nav "Campaigns"; "Push to ad" buttons on Distribution board (Screen 19) and Content Flow winners; "Generate ads" panel on listing detail; Wattson intent ("boost the ADU video"); Approvals inbox card deep-links back here; weekly report "manage campaign" links.

**Exit points.** Approve → Global Approvals Inbox (approval card); campaign report → Attribution screen (31); audience chip → Audience Builder (30); creative chip → Creative Library (30); landing destination link → Funnel Page Builder; Spend settings → Settings > Spend Envelope; Manual channels tab (in-screen); blocked-state "Apply fix" re-runs preflight in place.

## Layout

**Desktop.**
- **Header:** screen title + live rollup ("3 live · $412 spent this month · envelope $300/mo per campaign" — per draft), actions: `+ New campaign`, `Manual channels`, `Spend settings`.
- **Main (single column, card list):** one row-card per campaign, sorted ACTIVE → PENDING_APPROVAL → PREFLIGHT_BLOCKED → SCHEDULED → PAUSED → DRAFT → COMPLETED/FAILED/ARCHIVED (archived collapsed). Blocked cards get warn styling with the named rule + alternative inline.
- **Below the list, 3-up info panels** (per draft): Preflight explainer, Spend envelope summary, Manual channels summary.
- **Right drawer:** campaign detail opens as a slide-over (state timeline, preflight result, performance snapshot, UTM/lock identity, platform refs).
- **Wizard:** full-screen modal stepper for `+ New campaign` (steps mirror preflight order — matrix item, PropReach §7.5).

**Mobile (375px).** Header collapses to title + kebab (New / Manual / Spend). Campaign cards stack full-width; per-card metrics wrap to two lines; Pause/Report become a card-tap detail sheet. Wizard becomes full-screen sequential steps. 3-up panels stack vertically.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Rollup strip | live count, month spend, envelope cap | PropReach CampaignPerformanceSnapshot aggregate + SpendEnvelope | none | draft s18 header |
| Campaign card | name, status badge (10 states), platform chip (`Meta · Special Ad Category ✓`), spend vs cap, reach/clicks/leads/CPL vs benchmark, pending-recommendation note | PropReachCampaign + CampaignPerformanceSnapshot | click → detail drawer; Pause; Report | MB §7.2, §18.4, §18.6; draft s18 |
| Status badge | one of DRAFT / PREFLIGHT_BLOCKED / PENDING_APPROVAL / APPROVED / SCHEDULED / ACTIVE / PAUSED / COMPLETED / ARCHIVED / FAILED | CampaignStatus enum | filter by status via header chips [BEST GUESS: filter chips] | MB §7.2 |
| Pause button | manual pause (CampaignPauseType=MANUAL) | AdPlatformProvider | confirm dialog | MB §18.1 |
| Safety-pause banner | when auto-paused: reason from CampaignSafetyPauseReason (DEAD_LINK, BROKEN_LANDING_PAGE, AD_POLICY_VIOLATION, COMPLIANCE_BLOCK, TRACKING_DESTINATION_FAILURE, MALWARE_SECURITY_RISK) + repair CTA | campaign record | "Fix & resume" re-runs preflight | MB §2.6, §18.1; matrix "safety auto-pause reason banners" |
| Blocked card | names the hard block verbatim (e.g. "umbrella geo at LEAD_GEN violates market-level rule — Meta housing: no zip targeting") + compliant alternative with projected impact + `Apply fix` | CampaignPreflightResult.hard_blocks | Apply fix mutates draft + re-preflights | MB §5.3 hard block, §6.1; draft s18 |
| New-campaign wizard | steps mirror 12-step preflight: (1) objective (AUTHORITY/LEAD_GEN/RETARGETING/ACTIVE_LISTING/SERVICE_CAMPAIGN) → (2) promoted item (content_id / asset_id / approved_exception_type: GOOGLE_LSA, CHATGPT_ADS, RETARGETING, SERVICE_CAMPAIGN, ACTIVE_LISTING) → (3) geo with market-level badges (PRIMARY_MARKET/ADJACENT_MARKET/UMBRELLA_AWARENESS; umbrella+LEAD_GEN hard-blocked in-step) → (4) targeting method (GEOGRAPHIC_ONLY / CUSTOM_AUDIENCE, picker from Screen 30) → (5) Conversion Event Advisor → (6) volume-vs-qualified intake (CampaignGoalPreference) → (7) budget + envelope check → (8) preflight run → submit for approval | CampaignPreflightRequest / CampaignIntakeAnswers | step navigation; inline blocks | MB §7.3, §7.5, §7.6, §7.7, §5.3 |
| Preflight checklist panel | live 12 checks with pass/fail/pending: naming ✓, content/exception ✓, ScoringService (≥7.0 gate) , ComplianceProvider.check(), RegionProfile, ChannelPolicy, audience/list preflight, creative/legal/release, link & tracking, spend approval/envelope, owner approval, Event Ledger readiness | CampaignPreflightResult | expand each check for detail; failed check links to fix surface | MB §7.5, §2.2 |
| Conversion Event Advisor card | recommended_event (AD_CLICK / LEAD_FORM_SUBMIT / CMA_REQUEST / BOOKING_REQUEST / PHONE_CALL / QUALIFIED_FORM_SUBMIT), supported_by_funnel, warning_messages (e.g. spam-call warning for PHONE_CALL), owner_explanation, source facts | ConversionEventRecommendation | accept / override with warning | MB §7.6, §6.2 |
| Approval bundle preview | mirrors CampaignApprovalBundle: what's promoted (thumbnail), eligibility (score or exception + reason), platform mix %, market level + geo codes, audience type, budget request, landing destination, compliance summary, approvals required, expected-outcome range with guarantee_disclaimer and estimate_basis (ACCOUNT_HISTORY / MARKET_BENCHMARK / UNKNOWN) | CampaignApprovalBundle | "Send to Approvals" → PENDING_APPROVAL | MB §7.1, §7.4 |
| Spend envelope panel | all SpendEnvelope fields; **empty = nothing autonomous** (fields default null, ad_spend_change_mode=REVIEW_REQUIRED) | SpendEnvelope on CampaignBudgetRequest / tenant settings | edit → Settings > Spend Envelope | MB §2.6, §18.3; matrix "not set = nothing autonomous" |
| Recommendations queue chip | pending budget recommendations ("+$10/day — in Approvals") with rationale_source_facts | PropReachWeeklyReport.budget_recommendations | click → Approvals card | MB §21.5, §21.6 |
| Search-term recommendations | Google served-terms → add keyword / add negative / revise copy, approval-required | AdPlatformProvider search-term reports | approve/dismiss per row | MB §21.3 |
| Manual channels tab — ChatGPT Ads | plan builder: campaign spec (objective CLICKS/REACH/CONVERSIONS, ad groups with moment_id + context_hint ≤ housing-intent-only, ads: title ≤24 chars, copy ≤48 chars, hosted square image 640–1200px, landing via link.propertyiq.app), downloadable campaign_workbook.xlsx / context-hints-to-paste.docx / setup-checklist.docx, "I launched this" confirmation → CAMPAIGN_LAUNCHED with manual_channel=true | ChatGptAdsCampaignSpec | download pack; confirm launch; edit spec | MB §15.2–15.5 |
| Manual channels tab — Google LSA | lead inbox: rows with lead_status (NEW/ACCEPTED/DISPUTED/CREDITED/INVALID/CONVERTED), caller/email, call recording link (retention VOICE_TRANSCRIPT_24M), dispute action + credited tracking; Google Guaranteed status; setup checklist | GoogleLsaLeadRecord | dispute / accept / mark converted; leads route to /approved-leads | MB §16.3, §16.4 |
| Budget anomaly alert | banner when spend deviates [BEST GUESS: >20% vs daily cap trajectory — threshold not in MB, admin-configurable] | performance snapshots | dismiss / open report | matrix "budget anomaly alerts" |
| Report button | opens campaign slice of Attribution screen (31) + weekly report mirror | PropReachWeeklyReport | navigate | MB §21.5 |
| Lead feedback prompt | mark leads converted/junk so platform conversion corrections improve optimization | campaign leads | per-lead toggle | MB §21.6 |
| Empty state | "No campaigns yet — winners on your Distribution board auto-nominate here" + New campaign CTA | — | CTA | draft s19 nomination loop |

## States

- **Default:** card list as above.
- **Loading:** skeleton cards; header rollup shows dashes, never zeros.
- **Empty:** empty-state card (above).
- **Error/degraded (fail-closed):** ScoringService down → content-backed campaigns show SCORE_UNAVAILABLE flag and cannot pass step 3 (scored path fails closed; exceptions still possible) — never a locally computed score. Platform OAuth expired → OAUTH_EXPIRED flag on card, launch disabled, repair CTA. Event Ledger write-readiness fails → step 12 blocks launch. Benchmarks unavailable → CPL shows raw value with "no benchmark", never invented.
- **Permission-limited:** non-admin sees campaigns read-only; approve actions hidden (approval authority per ApprovalRequirement); spend settings admin-only.
- **Mobile:** as Layout; wizard sequential; LSA inbox rows become cards.

## Data fields

PropReachCampaign: campaign_id, campaign_name, status, objective, platforms[], manual_channel, content_id / originating_content_id / asset_id / approved_exception_type (nullable), targeting_method, geo_codes[], geo_market_level, audience_ids[], housing_campaign, special_ad_categories[], budget (total_budget, daily_cap, dates, ad_spend_change_mode=REVIEW_REQUIRED, spend_envelope), approval_id, legal_approval_required/_id, compliance_check_id, utm {utm_campaign=content_id or NONE, utm_id=campaign_id, source, medium, content, term}, platform_campaign_refs[], source_facts[]. Performance: impressions, estimated_reach, clicks, spend, leads, cost_per_lead, conversion_rate, frequency, view_through_conversions, pipeline_contacts, closed_deals, deal_value, commission_gross_estimate/actual (all nullable — render "unknown" when null). Money as USD; dates ISO-8601 rendered locale-short.

## Rules & compliance

- **Score gate:** content-backed campaigns require content_performance_score ≥ 7.0 (PROPCAST_VIDEO_PERFORMANCE, Scoring Master Sheet); no local scores ever (MB §2.2).
- **Five exceptions** skip only the organic gate; all 12 preflight steps except the score check still run (MB §2.3, §4.3).
- **Meta housing deny-by-default:** special_ad_categories=["HOUSING"]; hard-block list (age/gender narrowing, ZIP targeting, detailed targeting, exclusions, Lookalikes, radius <15mi US, protected-class or proxy) rendered verbatim in block reasons (MB §6.1, §12.2).
- **Umbrella hard block:** UMBRELLA_AWARENESS cannot launch LEAD_GEN (MB §5.3). 60/30/10 allocation is a planning suggestion only — UI must never auto-shift money (MB §5.4).
- **Spend law:** ad_spend_change_mode defaults REVIEW_REQUIRED; autonomy only inside owner-set envelope; auto-pause for safety reasons only; performance pause requires performance_pause_auto_allowed=true (MB §2.6).
- **Sensitive-topic firewall:** no sensitive-topic signals in targeting/audience anywhere on this screen (MB §12.3). School data never in targeting (MB §12.1).
- **ChatGPT Ads copy** must carry agent name, DRE 01466876, Intero Real Estate from identity config (MB §15.3) — rendered read-only from identity.json.
- **Approval provenance:** Wattson-drafted campaigns show "requested by Wattson" on the approval card (matrix Wattson item).

## Cross-links

In: Distribution board (19) push-to-ad and launch-kit nominations; Creative Library (30) "use in campaign"; listing detail generate-ads; Wattson; Approvals inbox. Out: Approvals inbox (CAMPAIGN_LAUNCH, SPEND_CHANGE, LEGAL, MANUAL_CHANNEL_LAUNCH approvals), Audiences (30), Attribution (31), Funnel builder, Settings > Spend Envelope. **Ledger:** emits CAMPAIGN_LAUNCHED (manual_channel flag for ChatGPT/LSA), CAMPAIGN_PERFORMANCE_SIGNAL, COMPETITOR_AD_ANALYZED; consumes CONTENT_PUBLISHED, CONTENT_VARIANT_CREATED, LEAD_CAPTURED, PIPELINE_MOVED, DEAL_CLOSED, COMPLIANCE_BLOCKED, DNC_BLOCK. Campaigns carry content_lock_id alongside content_id (MB §14.5).

## Open decisions

- [DECIDE] Benchmark source for CPL comparison ("benchmark $62" in draft): interim design = tenant account history first, market benchmark labeled as hint, per MB §7.7 — never a promise. UI unaffected.
- [DECIDE] Budget-anomaly threshold: interim = admin-configurable %, default 20% [BEST GUESS].
- [DECIDE] Whether campaign detail is a drawer or its own route: interim = drawer with a permalink route for deep-links from Approvals/reports.
- [DECIDE] LSA integration depth (manual vs limited API): interim UI is manual-first (checklist + inbox), which also covers the API case when it lands.
