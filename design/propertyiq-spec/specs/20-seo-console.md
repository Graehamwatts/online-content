# 20 · SEO Console (SearchAtlas / OTTO)

**Purpose.** The single place where automated SEO becomes reviewable and auditable: site connections, audits/issues, OTTO-proposed changes shown as diffs, an approval-gated deploy flow, freeze flags, GBP posts/review replies, instant indexing, filter-URL handoff, and a client-shareable work summary. It exists because OTTO can mutate live sites — the console is the safety harness (PropReach Master Brain §17: "SEO pages are destinations and attribution surfaces; live SEO changes always preview first and always get human approval").

**Primary users.** The agent (Graeham persona) — daily/weekly review. Secondarily an admin/team member with SEO permission. Read-only "work summary" view is client-shareable (exported, not a login).

**Entry points.**
- Left-nav "SEO" item in the agent console shell.
- Command Center cards: `PAGE_ORGANIC_TRAFFIC_SPIKE`, `LLM_CITATION_DETECTED` events deep-link here.
- Competitor Intel (Screen 11) "OTTO: gap plan →" links into the Competitor keyword-gap tab.
- PropSearch Filter-URL library "Submit to SEO" routes into the deploy preview flow here (matrix P1 gap item).
- Global Approvals Inbox: an SEO-deploy approval card deep-links back to its diff here.
- Weekly SEO report email (Mondays) links to the Report tab.

**Exit points.**
- "Approve & deploy" → Global Approvals Inbox (`SEO_DEPLOYMENT` ApprovalRecord) → on approval, `deployOnPageFixes`/`deploySchema` executes → change-log entry.
- Gap keyword "create brief" → PropCast briefing/gauntlet (NOT a generic writer).
- GBP queue items → Approvals Inbox.
- Work summary "export" → client-shareable PDF/URL (routes through Outbox review-first rule if emailed to a client).
- Site connection wizard → Settings/Integrations on failure.

## Layout

**Desktop.**
- **Header (site strip):** avatar + `SEO · {domain}` + status line ("GSC connected · OTTO active · weekly report Mondays") + tab nav: **Overview · Audits · Rank tracker · Keyword gap · Briefs · Backlinks · Local grid · GBP · Report · Change log · Settings**. A site-switcher dropdown if the tenant has >1 connected site; a plan-limit pill ("Projects 3/5") per the SearchAtlas active-project-count warning (§17.4).
- **Main (Overview tab, the draft's default):** two-column grid, 1.3fr / 1fr.
  - Left column: Pending-deploy card (diff preview), Issues (audit) card, Work-summary card.
  - Right column: Freeze-flags card, GBP queue card, Instant-indexing card, Filter-URL-handoff card.
- **Below the grid:** "Full console modules" panel — six module tiles (Rank tracker, Site audit, Competitor keyword gap, Content briefs, Backlinks & mentions, Local SEO grid), each a summary tile that opens its tab. This is the Search-Atlas-parity block already locked in the draft.
- **Footer note:** "All modules share one data layer (GSC + OTTO + rank API + ledger) · every module's 'fix' routes through the diff-preview → Approvals flow — nothing deploys silently." Keep verbatim in spirit; it is the governing rule.

**Mobile (375px).** Tabs collapse to a horizontal scroll chip row under the header. Cards stack single-column in this order: Pending deploy → Issues → GBP queue → Freeze flags → Work summary → Instant indexing → Filter-URL handoff → module tiles. Diff blocks scroll horizontally inside their own container (`overflow-x:auto`). Approve buttons full-width, sticky bottom bar when a deploy is selected.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Site header + status line | Domain, GSC connection, OTTO active, report cadence | SeoProvider project record + GSC OAuth status | Site switcher; click status → Settings tab | Draft Screen 20; PR §17.3 `connectSite` |
| Plan-limit pill | Active projects vs SearchAtlas plan limit; warns near limit | SearchAtlas account API | Tooltip; link to plan settings | PR §17.4 "active project-count warning" |
| **Pending deploy card** | Batch of proposed changes ("14 title/meta changes"), source badge ("from GSC query data"), diff preview (− old / + new, monospace, red/green) | `previewDeployment()` → SeoDeploymentPreview | "Approve & deploy" (creates SEO_DEPLOYMENT ApprovalRecord); "Review each" → per-change list with individual include/exclude checkboxes | PR §17.3/17.4; draft |
| Diff constraint note | "…all through template variable slots, layout untouchable" | template engine | none (informational) | Draft; brand-vault layout-locked rule |
| **Issues (audit) card** | Thin-vs-siblings pages (uniqueness validator), orphan pages, broken links, Core Web Vitals | `getAudit()` + `getIssues()` | Click issue class → Audits tab filtered; "auto-fix" issue types show a Fix button that generates a preview (never direct deploy) | PR §17.3; draft ("auto-fix via OTTO for 4 of 5 issue types — the 5th needs a human call") |
| **Work summary card** | Month-to-date: changes deployed, slugs minted, rank moves, AI-citation count | `exportWorkSummary()` + ledger | "Export client version" → shareable artifact | PR §17.3/17.4 "auditable work summary" |
| **Freeze flags card** | Frozen paths with reason + expiry ("/friendly-acres/ 🔒 A/B test until Aug 1") | per-project freeze flags | Add/remove freeze (path picker + reason + optional end date); OTTO skips frozen paths — enforced server-side, UI shows a lock on any proposed change touching a frozen path (change is auto-excluded from deploys) | PR §17.4 "per-project freeze-flag support"; draft |
| **GBP queue card** | Drafted GBP posts (weekly cadence: market stat / listing alert / community update) + drafted review replies | PropCast GBP engine + GBP API | Preview each; "Send to Approvals" — nothing posts directly from this card | PropCast MB Part re: GBP ("one GBP post weekly… GBP video weekly"); draft |
| Review-request cadence status | Reviews requested at close (+72h) and 1-year mark; target: top-3 GBP review count, recency <30 days | ledger + GBP API | link to Past Client OS trigger settings | PropCast MB review strategy |
| **Instant indexing card** | URLs submitted this week (new listings + slugs), avg index time | `requestIndexing()` results | "Submit URL" (manual add, requires approval_id — batches into the deploy approval) | PR §17.3; PropCast MB "instant indexing on publish so new pages are seen in hours" |
| **Filter-URL handoff card** | Slug usage vs caps ("61/250 market cap"), candidates awaiting mint from prompt logs | PropSearch filter-URL library | "Review candidates" → mint flow → routes back through preview+approve | Matrix PropSearch gap (250/market, 5000/global caps); draft |
| **Rank tracker tile/tab** | Tracked keywords, position, Δ, per-neighborhood groups, vs named competitors | rank API (SearchAtlas) | Sort/filter; keyword click → SERP snapshot; "add keyword"; competitor comparison toggle | Draft ("142 tracked · daily · vs 3 named competitors") |
| **Site audit tile/tab** | Health score, issue classes, CWV, schema validity per page | `getAudit()`/`getIssues()` | Per-issue Fix → preview; export | Draft ("Health 91/100 · schema valid 214/214") |
| **Competitor keyword gap tile/tab** | Keywords competitors rank for that you don't, filtered by volume × intent; top gap surfaced | rank API + competitor set (shared with Screen 11) | "Create brief" per keyword → Briefs tab → PropCast gauntlet | Draft; cross-link Screen 11 |
| **Content briefs tile/tab** | Auto-briefs (H2s, questions, entities, competitor coverage) queued into PropCast | brief generator | Open brief; "Send to PropCast gauntlet" (never a generic writer — voice + compliance stay in PropCast) | Draft ("routes into PropCast's gauntlet, NOT a generic writer") |
| **Backlinks & mentions tile/tab** | DR, referring domains, new/lost links, unlinked-mention finder with outreach drafts | backlink API | Outreach drafts → Outbox (human sends) | Draft |
| **Local SEO grid tile/tab** | GBP map-pack rank on a 5×5 geo-grid per keyword; weak quadrants highlighted | local rank grid API | Per-cell detail; "target plan" → GBP cadence + review-velocity suggestions (advisory) | Draft |
| **Report tab** | Weekly client-shareable report assembled from all panels | all module data + `exportWorkSummary` | Export PDF/URL; schedule (Mondays); email routes review-first | Draft footer note |
| **Change log tab** | Append-only list: every deployed change with approval_id, approver, timestamp, before/after, correlation_id | ledger + SeoDeploymentResult records | Filter by type/date/page; "revert" creates a NEW proposed change (never silent) [BEST GUESS: revert-as-new-proposal] | PR §17.4 "auditable work summary… no silent mutation" |
| **Settings tab / connection wizard** | Site connections: method = cloudflare (default for PropertyIQ-managed) / pixel (fallback) / wordpress (WP sites only); connection status PENDING/CONNECTED/FAILED; pixel snippet / worker config / plugin instructions | `connectSite()` | Add site (requires approval_id — connecting a site is itself approval-gated); auto-deploy toggles per low-risk change class [see Rules] | PR §17.3 connectSite signature; §17.4 method rules |
| Capability-probe banner | Warning if startup capability probe found missing MCP tools | MCP probe | "Retry probe"; degraded features greyed with explanation | PR §17.4 "capability probe at startup; dynamic tool discovery" |
| AI-citation counter | LLM citations detected (e.g. "6→9") | `LLM_CITATION_DETECTED` events | click → list of citing engines/queries | PR consumed events; draft work-summary |
| Empty state (no site) | "Connect your site to start" + wizard CTA | — | launches connection wizard | standard |
| Empty state (no pending) | "OTTO has nothing queued — next audit {date}" | — | — | standard |

## States

- **Default:** Overview as drafted.
- **Loading:** skeleton cards; diff block shows shimmer; never show stale rank data without an as-of date.
- **Empty:** no connected site → wizard; no pending deploys → quiet state; no gap keywords → "no competitor set defined — add competitors" (links to Screen 11 watch list).
- **Error/degraded (fail-closed):** if the SearchAtlas MCP capability probe fails or the token is invalid, all deploy/fix/indexing buttons disable with an inline reason ("OTTO connection degraded — read-only until reconnected"); read-only data (last audit, change log, ledger-sourced counters) stays visible with as-of timestamps. Rank API outage → tiles show "rank data unavailable" — never last-known values presented as current. No fabricated metrics, ever.
- **Permission-limited:** team member without SEO-deploy permission sees everything read-only; approve buttons hidden (approval happens in the Approvals Inbox anyway, scoped by delegation rules).
- **Mobile:** per Layout; diff and grids scroll inside their containers; the 5×5 local grid renders as a compact heatmap with tap-for-detail.
- **Frozen-path conflict:** any pending change touching a frozen path renders with a lock badge and is excluded from the batch approve; tooltip names the freeze reason.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| seo_project_id, tenant_id, domain | ids/string | SeoProvider project record |
| connection_status | PENDING / CONNECTED / FAILED | connectSite result |
| connection method | pixel / cloudflare / wordpress | connectSite input |
| Pending change | change_type, page_url, before, after, source (e.g. GSC query data) | SeoDeploymentPreview |
| approval_id, correlation_id | ids on every deploy/indexing call | ApprovalRecord / ledger |
| Audit health score, issue list | int /100; SeoIssue[] | getAudit/getIssues |
| CWV metrics | LCP seconds etc., pass/fail | audit provider |
| Freeze flag | path, reason, start, optional end | project freeze store |
| Keyword row | keyword, position (int), Δ, group, competitor positions | rank API, daily |
| Gap keyword | keyword, volume/mo, intent class, competitor, brief_status | rank API + brief queue |
| Backlink stats | DR, referring domains, new/lost | backlink API |
| Local grid cell | lat/lng cell, rank int, keyword | local grid API |
| Indexing record | url, submitted_at, indexed_at, avg index time | requestIndexing + GSC |
| Filter-URL usage | slugs used / 250 per market, / 5000 global; candidate list | PropSearch filter-URL library |
| Work summary | changes deployed, slugs minted, rank deltas, AI citations, time_window | exportWorkSummary + ledger |
| GBP queue item | type (post/review-reply), draft body, target, status | PropCast GBP engine |
| AI citations | count + per-event detail | LLM_CITATION_DETECTED events |

## Rules & compliance

- **Human approval before any live SEO deployment** — every deploy, schema injection, indexing request, and site connection carries an `approval_id`; the approve action creates an `SEO_DEPLOYMENT` ApprovalRecord in the Global Approvals Inbox (48h expiry, delegation per platform rules). **No silent mutation of a live site** (PR §17.4).
- **Preview before deployment** — a diff must exist before an approve button renders.
- **Freeze flags** — OTTO skips frozen paths; UI enforces exclusion from batches.
- **Auto-deploy for low-risk classes** (draft note "or enable auto for low-risk classes"): per-change-class toggle in Settings; [BEST GUESS] auto classes limited to title/meta template-slot changes and schema on noindex pages, promoted only after a track record, mirroring the autonomy-matrix promotion pattern (30 days / ≥95% unmodified approvals / 0 incidents) from the platform autonomy rules. Everything else stays REVIEW_REQUIRED.
- **Layout untouchable** — changes flow through template variable slots only; brand vault layout is locked.
- **GBP posts and review replies never publish directly** — they route to Approvals; review replies are client-facing text and honor the fair-housing lint (e.g. the "family-friendly" block pattern from Screen 24).
- **Content briefs route into PropCast's gauntlet** for voice + compliance — the console never publishes prose itself.
- **Capability probe + dynamic tool discovery** at startup; degraded = read-only, fail closed.
- **Secrets:** SEARCHATLAS_TOKEN (MCP Bearer) and SEARCHATLAS_REST_API_KEY are distinct and never interchangeable (PR §17.2) — surface only connection status in UI, never key material.
- **Plan-limit warning** before creating projects past the SearchAtlas limit.
- **Attribution honesty:** SEO page views feed reporting-only attribution (default weight 0.2, labeled "reporting assumption, not proof of causation" — PR LINEAR_DECAY_REPORTING); nothing here changes lead_score or Scoring Master outputs.
- Client-emailed reports follow the review-first rule (send to Graeham + Adrian, who forward).

## Cross-links

- **In:** left nav; Command Center event cards; Screen 11 gap-plan links; PropSearch filter-URL "Submit to SEO"; Approvals Inbox card back-links; weekly report email.
- **Out:** Global Approvals Inbox (deploys, GBP, connections); PropCast briefing/gauntlet (briefs); Outbox (outreach drafts, client report emails); Settings/Integrations (GSC/GBP OAuth); Screen 11 (competitor set management).
- **Ledger events consumed:** `SEO_PAGE_PUBLISHED`, `PAGE_ORGANIC_TRAFFIC_SPIKE`, `LLM_CITATION_DETECTED`.
- **Ledger events emitted:** deploy/indexing results with approval_id + correlation_id; [BEST GUESS] `SEO_DEPLOYMENT_EXECUTED`-class entries land as ledger rows via SeoDeploymentResult; `SEO_PAGE_PUBLISHED` when a new page/slug goes live.

## Open decisions

- **[DECIDE] Rank/backlink/local-grid data vendor:** assume SearchAtlas's own rank tracker, backlink index, and local grid (parity block says "Search Atlas parity") — UI unaffected if a second vendor (e.g. DataForSEO) backs any panel.
- **[DECIDE] Auto-deploy class list and promotion criteria:** interim = title/meta template-slot changes only, promoted per the platform autonomy-matrix thresholds ([BEST GUESS] stated above).
- **[DECIDE] Revert semantics:** interim = revert creates a new proposed change through the same preview→approve flow; no direct rollback button.
- **[DECIDE] Client-facing work-summary format:** interim = branded hosted URL + PDF export, assembled from the Report tab; delivered review-first.
- **[DECIDE] Evaluate-first outcome (PropCast MB Part 9):** if SearchAtlas falls short on schema injection or the attribution/UTM handoff, only that gap is built in-house — console UI treats SeoProvider as the abstraction either way.
