# 31 · Attribution & Analytics

**Purpose.** The ledger-driven proof layer: views → site sessions → leads → pipeline GCI per ContentLock, closed-deal traces, the hook-autopsy browser, the AEO/LLM-citation tab, and the Monday proof-email mirror. Every number comes from the Event Ledger; multi-touch models are labeled reporting assumptions, nulls render as "unknown" — never fabricated (correlation ≠ causation, rule C42).

**Primary users.** Agent/owner (the ROI receipt that drives renewal); team lead for content decisions; admin for model-weight configuration.

**Entry points.** Left-nav "Results"; Content Flow row drill (19); Campaign "Report" (18); Command Center stat tiles; Monday proof email links; Wattson ("what made money this month?"); QR-label analytics from Creative Library (30).

**Exit points.** Piece row → lock/version detail + Content Flow row; campaign slice → Campaign Manager (18); hook autopsy → concept/swipe-file (Video Studio 32 hook library); AEO cited page → SEO console; "Weekly proof email" → email mirror view + send settings; closed-deal trace → transaction record (PropClose) + contact record (PropFlow).

## Layout

**Desktop.**
- **Header:** "Results" + time-window picker (30 days default) + model switcher labeled "model: position-based (assumption, switchable)" per draft — canonical options FIRST_TOUCH / LAST_TOUCH / LINEAR_DECAY_REPORTING; nav: `Weekly proof email`, `Hook autopsies`.
- **Zone 1 — funnel stat row:** Content views → Site sessions → Leads → Pipeline GCI (4 stat tiles, per draft).
- **Zone 2 — per-piece table:** Piece (ContentLock id) | Views | Leads | Pipeline | Note (autopsy insight / QR-label detail / drove-N-valuations); closed-deal trace rows.
- **Zone 3 — 2-up panels:** AEO / AI citations · Monday proof email mirror.
- **Tabs above zone 2 [BEST GUESS as organization]:** Content · Campaigns (paid) · Deals · Hook autopsies · AEO.
- **Drill-down drawer:** click a piece → lock-level detail: per-checkpoint metrics (Day 1/2/3/5/7, 14, 30…), per-platform splits, variant A/B pairs, degradation-rung indicator per event batch.

**Mobile (375px).** Stat tiles 2×2 grid; table becomes stacked piece cards (lock id, three numbers, note); tabs scroll horizontally; drawer = full sheet.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Funnel stat tiles | 48.2K views → 2,140 sessions → 19 leads → $66K pipeline GCI (window-scoped) | Event Ledger aggregates (CONTENT_VIEWED, PAGE_VIEWED, LEAD_CAPTURED, PIPELINE_MOVED × deal value) | window picker recalculates | draft s31; PropCast MB attribution part |
| Model switcher | FIRST_TOUCH / LAST_TOUCH / LINEAR_DECAY_REPORTING; decay weights displayed and labeled "reporting assumptions, not proof of causation" — defaults paid click 0.4, organic content view 0.3, SEO page view 0.2, direct outreach 0.1 (admin-configurable) | AttributionModel config | switch recomputes report views only | PropReach MB §14.9 |
| Model-honesty banner | "Reporting assumption — never feeds lead_score, content score, outreach priority, or audience eligibility" | static rule | — | MB §14.9 |
| Per-piece row | title + ContentLock id (CL-xxxx), views, leads, pipeline $, note column (e.g. "hook autopsy: dollar-number open beat question-open 2.3×", "QR-label attribution: 31 scans, sign-QR 0 (rotate)") | nightly sync sheet → native ledger queries; append-only one row per content_lock_id per day | click → drill drawer; note → autopsy/QR detail | draft s31; PropCast MB nightly sync |
| Lock-level drill drawer | exact-identity metrics per checkpoint ladder (Day 1,2,3,5,7 all platforms; +14/30 Meta/TikTok; YT through Day 365); per-platform availability notes; variant A/B pairs with winners; first-party lane (never expires) vs platform lane distinction | platform metrics collection + owned-link/GA4/Rybbit/GSC/CRM | expand checkpoints; re-poll request (tracker re-open trigger) | PropCast MB metrics schedule |
| Degradation-rung indicator | per row/event batch: exact lock identity → content_id roll-up → campaign/platform level; stepped-down rows labeled, never fabricated | attribution degradation ladder | tooltip explains rung | PropCast MB ladder; matrix "degradation ladder (exact→content_id→campaign)" |
| Six CRM attribution fields panel (contact drill) | the attribution story on any captured lead: propcast content_id + lock identity + platform/source + lead-magnet/capture fields populated at capture moment [BEST GUESS on exact six field names — MB table cell not in converted text; use content_id, content_lock_id, approved_version_id, capture platform, lead magnet, capture_source until verified against the docx master] | CRM custom fields via webhook/API write-back | view on lead drill | PropCast MB "CRM Field Mapping" (six fields canonical anchor) |
| Closed-deal trace row | "first touch: postcard (Torres path) · community page organic (Kim path)" + full chain view per deal: every ledger touch in order with channel, date, identity rung | ledger trace by contact_id + DEAL_CLOSED | open full-chain timeline | draft s31; PropCast MB weekly email "content-to-deal highlight" |
| Campaigns (paid) tab | weekly-report schema surfaced: spend by platform/market-level/objective, CPL avg + splits, pipeline impact, top campaigns by ROI, top content by paid lift, assisted conversions, view-through conversions for Display/YT remarketing (blended context), creative health list, budget recommendations (review-required) | PropReachWeeklyReport + CampaignPerformanceSnapshot | recommendation → Approvals; campaign → 18 | PropReach MB §21.5, §21.6 |
| Impression-honesty note | ad impressions shown campaign/audience-level; contact-level only when identity_scope=CONTACT_DETERMINISTIC; never "this person saw your ad" | AD_IMPRESSION identity_scope | tooltip | PropReach MB §14.6 |
| Hook autopsy browser (tab) | per-piece hook pattern results extended to titles/thumbnails; ranked patterns (e.g. "specific-dollar-number opens top this quarter"); feeds swipe file | A/B pair log + learning layer | filter by pattern/format/geo; save to swipe file | PropCast MB Part 10 A/B logging; matrix "hook autopsy log"; draft s32 swipe file |
| AEO / AI citations panel | citations count by engine (ChatGPT / Perplexity / AI Overviews), cited page, self-reported "asked ChatGPT" leads | LLM_CITATION_DETECTED events + lead-source self-report | click → cited page in SEO console | draft s31; PropReach MB §17.4 consumed events |
| Monday proof email mirror | exactly the weekly email: top 3 pieces by CRM contacts created (not views), pipeline moves attributed, content-to-deal highlight ("this week's [address] deal was first touched by [video] on [date], locked as [lock id]"), one model-generated insight; sends Monday 7:00 AM, send-not-draft | weekly performance email job | view past emails; recipient settings | PropCast MB weekly email; draft s31; scheduled-reports send policy |
| QR-label analytics | per-label scan counts (sign/flyer/postcard/mailer) with rotate recommendations | LINK_SCANNED scan_type=QR by label | → Creative Library pack | PropReach MB §10.3–10.4; draft s31 |
| Calibration proposal cards | feedback-loop proposals surface as confirm/decline cards — never silently applied | learning layer | confirm/decline | matrix "feedback-loop calibration proposals (never silent)" |
| Lead feedback prompts | mark converted/junk to improve platform optimization | campaign leads | per-lead action | PropReach MB §21.6 |
| Null rendering | any missing metric renders "unknown" / "—" with reason (tracking blocked, platform metrics unavailable) | — | — | matrix; rule C42 |

## States

- **Default / Loading:** stat tiles skeleton; table shimmer. Never render 0 for unknown — loading ≠ zero.
- **Empty:** "No attributed activity in this window — attribution starts the moment your first tracked link goes out."
- **Error/degraded (fail-closed):** ledger query failure → screen-level error with retry, no cached fabrication; platform lane missing → first-party numbers shown with "platform metrics unavailable on <platform>"; GA4/Rybbit divergence → ledger wins, reconciliation note (GA4 is reconciliation only, MB §14.1); ScoringService/VideoIntelligence outage does not affect this screen except autopsy tab shows "pattern analysis unavailable" (never fabricated patterns, MB §13.2).
- **Permission-limited:** model-weight editing admin-only; team sees read-only; recommendation approvals owner-only.
- **Mobile:** per Layout.

## Data fields

Funnel: views, sessions, leads (int), pipeline GCI (USD). Piece rows: content_id (PC-YYYYMMDD-GEO-TYPE-hex format), content_lock_id, approved_version_id, lock_hash (drill only), per-metric nullable ints/moneys. Model weights: 0–1 floats summing 1.0, admin-editable. Weekly report: full PropReachWeeklyReport schema (§21.5). Deal trace: ordered events with event_type, timestamp, channel, identity rung. AEO: engine, count, cited URL, detected_at. Windows: TimeWindow ISO pairs; default 30 days [draft].

## Rules & compliance

- **Event Ledger is the attribution source of truth** from MVP0; GA4 secondary, Sheets export-only (PropReach MB §14.1, §2.4).
- **Reporting-only models:** LINEAR_DECAY must never change lead_score, content_performance_score, likelihood_to_list, outreach priority, audience eligibility, or Scoring Master outputs (§14.9).
- **Impression honesty** (§14.6) and **degradation ladder honesty** (PropCast MB): step down a rung, never fabricate.
- **Correlation ≠ causation (C42):** all lift/insight copy phrased as correlation; model switcher labeled assumption.
- **Contacts ranked by contacts-created, not views** in the proof email — vanity metrics never headline.
- **No sensitive-topic data** appears in any trace or insight; deal traces show channel-level touches, not inferred life events (§12.3).
- **Send-not-draft:** the Monday email actually sends (Graeham standing rule, CLAUDE.md 2026-06-13) to configured recipients.

## Cross-links

In: Distribution Content Flow (19), Campaign Manager (18), Creative Library QR packs (30), Command Center, SEO console (SEO_PAGE_PUBLISHED / PAGE_ORGANIC_TRAFFIC_SPIKE / LLM_CITATION_DETECTED), PropFlow contact records (six attribution fields), PropClose (DEAL_CLOSED + case-study facts). Out: hook autopsies → swipe file (32) and concept-forge inputs; budget recommendations → Approvals; cited pages → SEO console; traces → transaction/contact detail. **Ledger:** pure consumer — CONTENT_VIEWED, ORGANIC_VIDEO_VIEWED, PAGE_VIEWED, LINK_SCANNED, LEAD_CAPTURED, PIPELINE_MOVED, DEAL_CLOSED, CAMPAIGN_LAUNCHED, CAMPAIGN_PERFORMANCE_SIGNAL, LLM_CITATION_DETECTED; emits nothing except report-generated/email-sent audit records [BEST GUESS: REPORT_GENERATED-style audit entry — verify event name against Event Registry before build; never invent a new ledger event without registering it, C6].

## Open decisions

- [DECIDE] Draft header says "position-based" model while the canonical enum is FIRST_TOUCH/LAST_TOUCH/LINEAR_DECAY_REPORTING (Phase-3 sketch was 40/40/20): interim = ship the three canonical models; label LINEAR_DECAY's default weights in the switcher; "position-based" naming retired.
- [DECIDE] Exact six CRM attribution field names: interim set listed above [BEST GUESS] — confirm against the PropCast Master Brain docx table (the converted md dropped the table body) before schema freeze.
- [DECIDE] Dashboard tech: matrix results-dashboard memory says ECharts with dataZoom brush for trend lines — interim = adopt; UI contract unaffected.
- [DECIDE] Whether this screen is the "platform read-model cockpit" superset (propiq-results-dashboard memory) or PropReach-scoped: interim = one Results screen with Content/Campaigns/Deals tabs reading the shared ledger — no new attribution DB.
