# 19 · Distribution Board + Content Flow

**Purpose.** The channels × content publishing matrix and the closed-loop "Content Flow" board: where each locked asset came from, where it went, what it did, and the one-click next move. Auto-publish stays visibly OFF until the 7-item seam checklist is green; per-platform AI-disclosure holds are shown explicitly; each parent long-form expands into its ~15-asset family.

**Primary users.** Agent/owner (daily glance + one-click actions); content team (Peter/John-class roles) for scheduling and manual pushes.

**Entry points.** Left-nav "Distribution"; from Content Review & Approve (approved lock lands here queued); from Command Center content queue; from Campaign Manager (asset "went to" links); from a listing record ("Launch kit" chip); Wattson ("what went out this week?").

**Exit points.** "Push to ad" → Campaign Manager wizard prefilled (Screen 18); "Create funnel" → Funnel Page Builder; "Autopsy hook" → Attribution hook-autopsy browser (31); asset name → Content Review/lock detail; Connections → Settings > Integrations; derivative rows → Video Studio (32) render jobs; revoke → downstream-object revocation checklist.

## Layout

**Desktop.**
- **Header:** "Distribution" + week label + scheduled count; nav: `Connections`, `Asset families`.
- **Zone 1 — publish matrix:** table, rows = assets (parent + expandable derivatives), columns = channels (YouTube, Instagram, Facebook, TikTok, GBP, Email; LinkedIn column appears when connected). Cells = status chips.
- **Zone 2 — 2-up panels:** Connection health · Auto-publish seam checklist.
- **Zone 3 — Content Flow board** (brand-highlighted, per draft): table Came from → Asset (lock) → Went to → 7-day results → Verdict → Do next (one-click buttons); totals strip; listing→ad 3-click-path explainer with per-listing "Launch kit: ready / running / skipped" chips.
- **Sticky:** manual "Push now" button bar appears when items are queued and auto-publish is OFF.

**Mobile (375px).** Matrix scrolls horizontally inside its own container (never the page); Content Flow rows become stacked cards (source badge, lock id, channel chips, results line, verdict badge, action buttons full-width). Seam checklist and connection health stack.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Publish matrix cell chip | per channel per asset: published / posted / N reels live / sched <day> / HOLD: manual AI label / — (not targeted) / FAILED | DistributionPayload per channel (channel enum: instagram, instagram_reels, facebook, youtube, youtube_shorts, tiktok, gbp, linkedin, email, web, print, paid) + publish job status | click → payload detail (caption, alt text, disclosure flag, short link, UTM); reschedule; retry failed | PropCast MB Part 7 DistributionPayload; draft s19 |
| Parent-row expander "(+14 derivatives ▸)" | expands asset family: 20–30 auto-clipped Shorts candidates, only highest-rated published; cross-posts; SEO blog post; GBP square cuts (~15 assets/parent target) | Omnipresence Distribution stage + Production Asset Registry | expand/collapse; per-derivative status | PropCast MB "Omnipresence Distribution"; matrix asset-family item |
| Per-platform metadata A/B tab | title/thumbnail variant pairs {content_id, content_lock_id, lock_hash, approved_version_id, platform, variant_id, field, text} | A/B variant log | view pairing; winner marked from ledger joins | PropCast MB Part 10 metadata automation |
| AI-disclosure HOLD chip | names the platform lacking programmatic labeling (e.g. TikTok via Buffer relay) and that the item is HELD in QC until manually labeled | AI Disclosure Per Platform map | "Mark manually labeled" → releases with audit note [BEST GUESS on release mechanics] | PropCast MB Part 5 hard rule + Part 10 |
| Connection health panel | per channel: ✓ connected / token-expiry warning ("TikTok token expires in 6d — renew") / ○ not connected; relay fallback armed (Buffer for TikTok interim) | OAuth token store + relay config | Renew → OAuth flow; connect | draft s19; PropCast MB Part 10 relay rule |
| Seam checklist panel | the 7 items verbatim: (1) PropReach stores content_lock_id/approved_version_id/lock_hash, (2) PropFlow stores lock id on engagement/video/reply/lead events, (3) shortener maps every short link to lock id, (4) attribution rows carry lock id, (5) revocation finds every downstream object by lock id, (6) kill switches block by tenant/agent/channel/lock, (7) programmatic AI disclosure or held. Shows N/7 green; auto-publish toggle rendered LOCKED-OFF until 7/7 | seam-status service | read-only; each item links to admin seam-status panel | PropCast MB Part 16 seam checklist; matrix + draft (draft shows 5/7 with rollback + human-pause SLA missing — draft's two missing items are its own naming; canonical list is the 7 above, keep the draft's presentation but source labels from Part 16) |
| Auto-publish OFF banner | "Auto-publish OFF — everything queues for the manual push button"; manual export allowed only for lock-tied payloads | seam status | Push now (per item / per day batch) | PropCast MB Part 16 |
| Content Flow row | Came from (🏠 listing / 📰 news signal / 🔁 evergreen) → asset + lock id (CL-xxxx) + version → channels reached → 7-day results (views, shares, clicks, leads — Day 1/2/3/5/7 decision-window checkpoints) → verdict badge → next-action buttons | Event Ledger + platform-lane checkpoint metrics | row click → attribution drill (31) | draft s19 Content Flow; PropCast MB platform metrics schedule |
| Verdict badge | WINNER (top 10% engagement) / UNDERPERFORMER / GAP | QC monitoring WINNER/UNDERPERFORMER thresholds | — | PropCast MB Part 16 QC dashboard; draft "threshold: top-10%" |
| ⚡ Push to ad button | winner auto-nominates for spend; nomination lands in Approvals with budget suggestion — button prefills campaign wizard | escalation logic | → Screen 18 wizard | draft s19; PropCast MB Escalation Ladder (~10+ shares auto-promotes card→video→ads) |
| Autopsy hook button | opens hook-autopsy log for the piece | learning layer | → Screen 31 | matrix "hook autopsy log" |
| Kill escalation button | stops the escalation ladder for an underperformer | escalation state | confirm | PropCast MB Escalation Ladder |
| Sequel from comments | creates a concept brief from N unanswered comment questions | comment ingestion [BEST GUESS: count from CommentDmProvider] | → concept flow | draft s19 |
| GAP row | listing with no funnel/kit detected ("742 Hurlingame has NO funnel page yet") + ⚡ Create funnel now | launch-kit coverage check | → Funnel builder | draft s19 |
| Launch-kit chip per new listing | "Launch kit: ready / running / skipped" so nothing slips; 3-click path: listing live → kit auto-generates (creative from listing photos + funnel page + budget from farm CPL history + farm-segment audience) → ONE approval card ships all | UPCOMING_OWN_LISTING_DETECTED / LISTING_LIVE_FROM_IDX events + kit generator | chip → kit detail / approval card | draft s19; PropReach MB §10.1 |
| Weekly totals strip | assets out → views → site sessions → leads, organic vs paid split | ledger aggregates | — | draft s19 |
| Revoke action (per published asset) | "stop that campaign": downstream-object checklist (posts, ads, links, QRs, DM flows, pages) with per-object stop status, found by content_lock_id | revocation service | confirm → per-object progress | matrix ContentLock/revocation item; seam item 5 |
| Lock badge | CL-id + version on every asset; post-approval edit = new version + new compliance pass + new lock (never edit in place) | ContentLock | click → lock/version history | PropCast MB Part 5; matrix correction #9 |
| News-queue link chip | headline cards awaiting approval with broad-vs-local geo framing toggle and escalation-ladder indicator (P1; entry point lives here) | News-to-Post engine | → news queue | matrix News-to-Post item |
| Empty state | "Nothing scheduled this week — approved content lands here automatically" | — | link to content queue | [BEST GUESS] |

## States

- **Default / Loading:** matrix skeleton rows; chips grey until statuses resolve.
- **Empty:** empty state above.
- **Error/degraded (fail-closed):** channel API down → column header shows degraded badge; scheduled cells hold (never silently skip); publish failures surface FAILED chip + failure alert; disclosure-unlabelable platforms HOLD (hard rule, no exception); if the seam-status service itself is unreachable, auto-publish renders OFF (fail closed). Metrics missing on a platform → results show partial with "metrics unavailable on <platform>", never fabricated.
- **Permission-limited:** content-team role can schedule/push; only owner/approver sees Push-to-ad (spend) and Revoke; connections admin-only.
- **Mobile:** stacked cards per Layout.

## Data fields

DistributionPayload: payload_id, tenant/agent ids, content_id, content_lock_id, approved_version_id, lock_hash, channel, asset_urls[], thumbnail_url, caption, alt_text, ai_disclosure_flag (always true), disclaimer_refs[], short_link (link.propertyiq.app), utm block. Flow metrics: views, shares, clicks→site sessions→leads per piece (nullable → "unknown"); verdict; checkpoint day. Connection: token expiry ISO date rendered as "in Nd". Totals: counts + $ paid spend (USD).

## Rules & compliance

- **AI disclosure is mandatory** per platform via API parameter; no programmatic support → HELD (PropCast MB Part 5 — no exceptions).
- **Auto-publish gate:** OFF until the exact-identity chain (7 seams) is proven; manual export only with lock-tied payloads (Part 16).
- **Every payload requires content_lock_id** — reject handoffs without it (Part 5 build rule).
- **Email routing rule:** email column links to the agent's blog post embedding the video, never directly to YouTube (PropCast MB).
- **iPhone safe zones / no paywalled text reproduction** enforced upstream but violations surface here as compliance holds.
- **Escalation to paid** routes through PropReach preflight — the ⚡ button never launches spend directly; nomination → Approvals.
- **Fair-housing:** no channel targeting exists on this board (organic); listing-kit ad legs inherit Screen 18 rules.

## Cross-links

In: Content Review & Approve (approved locks), Command Center, listing records, News queue. Out: Campaign Manager (18), Funnel builder, Attribution (31), Video Studio (32), Settings > Integrations, Approvals inbox (ad nominations, manual-label confirmations). **Ledger:** emits CONTENT_PUBLISHED (per channel publish), LINK_SCANNED consumed for QR/shortlink joins; consumes FOOTAGE_UPLOADED / ASSET_MATCHED (derivative readiness), LISTING_LIVE_FROM_IDX (launch-kit chips), CONTENT_VIEWED / ORGANIC_VIDEO_VIEWED (flow results). All rows carry content_lock_id.

## Open decisions

- [DECIDE] Relay vendor: interim = Buffer for TikTok (~$6/mo/channel-set, no programmatic TikTok AI label → those items always HOLD) until direct TikTok API approval; UI shows relay badge per channel, vendor-agnostic.
- [DECIDE] Draft's seam list wording (rollback, human-pause SLA) vs canonical Part 16 seven: interim = render the canonical 7, keep draft's "5/7 green" presentation style.
- [DECIDE] "Sequel from comments" question-count source: interim = comment-DM ingestion count [BEST GUESS]; feature degrades to hidden when CommentDmProvider absent.
- [DECIDE] Whether News queue is a lane on this board or its own screen (matrix says P2 separate): interim = entry chip here, dedicated screen later — board layout unaffected.
