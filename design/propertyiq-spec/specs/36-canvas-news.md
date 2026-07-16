# 36 · Ideation Canvas + News-to-Post Queue (PropCast, P2)

**Purpose** — Two ideation surfaces on one screen. The Canvas is the Monday briefing's visual ideation layer: heterogeneous sources dropped as nodes, briefs generated against any selected set, full lineage from source to output — the canvas state IS the saved brief object. The News queue is the approval surface for the News-to-Post engine: rendered headline cards with the geo-broadening framing toggle and the engagement escalation ladder (card → video → paid ads).

**Primary users** — Agent; multiplayer role owners on the canvas (content lead, editor, marketing coordinator); news queue approval is agent (or approval-permitted role).

**Entry points** — Briefing (Tab 12) "open canvas"; "My canvases" nav; news notification ("3 pending"); Wattson ("add this voice note to the canvas"); voice-note capture; content object "send to canvas".

**Exit points** — Generate brief → content engine (CreativeKernelBrief → gauntlet → Tab 16); news card approve → staged post (approval queue → distribution); escalated stories → video queue (Tab 16/32) and ad-spend recommendation → Approvals (Tab 13); node click-through → source records (listing, GSC cluster, competitor summary).

## Layout

**Desktop**
- **Header**: "Ideation · Canvas: {name} · News queue: n pending"; nav: My canvases.
- **Main left (~55%)**: infinite pannable canvas surface — typed nodes, selection marquee, comment pins anchored to nodes, "Generate brief from n selected →" action docked bottom-left, lineage badge top-right.
- **Main right (~45%)**: News queue — pending headline cards (framing toggle + rendered static preview + approve), escalation-ladder panel showing per-story ladder position.

**Mobile (375px)** — Tabbed: [Canvas] / [News]. Canvas becomes a node LIST grouped by type with multi-select checkboxes + Generate button (full drag canvas is desktop-first; spec flags this as UI-heavy human dev lane); News cards full-width with framing toggle and swipe-to-approve.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Canvas node | Typed source: {source_id, type: LISTING \| NEWS \| COMPETITOR_VIDEO \| VOICE_NOTE \| DOC \| QUERY_CLUSTER, ref, extracted_summary}; pre-digested by existing ingestion (video-intelligence transcripts, Part 4 market read, GSC demand connector) | canvas/brief store + ingestion services | Drag/position; open source; select | Intelligence Engine §Ideation Canvas (type enum verbatim); matrix gap P2 |
| Add-node affordance | Add from: listing picker, news feed item, competitor video (official-API monitored), voice-note recorder, doc upload, GSC query cluster | respective ingestion services | Add → node appears pre-digested | Intelligence Engine |
| Selection + Generate brief | Marquee/multi-select; "Generate brief from n selected" runs generation against the selected node set | selected node set | Click → brief with brief.sources=[source_ids] → content engine | Intelligence Engine (verbatim) |
| Lineage badge | "Nodes keep lineage into every output" — lineage flows into content_id ancestry and the Event Ledger so attribution can trace which inputs produce winners | Event Ledger + content_id ancestry | Click → outputs generated from this canvas | Intelligence Engine; draft s36 |
| Multiplayer presence + comments | Agent + role owners share the canvas; comments anchor to nodes | canvas store | Comment threads per node | Intelligence Engine (multiplayer rule) |
| Canvas-as-brief | No separate brief document — saving is implicit; My canvases lists saved boards | canvas state = saved content-brief object | Rename, duplicate, archive | Intelligence Engine (verbatim) |
| Guardrail chips | Competitor/third-party nodes carry "inspiration-only" badge (no ingestion of copyrighted full text, Part 8 corpus rules); listing nodes carry MLS-rules badge | node metadata | Hover → rule text | Intelligence Engine guardrails; matrix correction #5 (official-API, hash/URL/excerpt/summary storage only) |
| News queue card | Rendered headline static (safe-zone enforced) + headline, source credit, cluster of related articles, framing toggle, Approve / Edit / Skip | News-to-Post engine output (staged, nothing self-publishes) | Approve → staged to distribution; edit → re-render + re-gate | Master Brain Part 13 §News-to-Post; matrix gap P1/P2 |
| Geo-framing toggle | Local (target-area framing, agent's farm data) vs Broad(er region); broadening computed per target area: below a density threshold (e.g. EPA or a single neighborhood) produce local AND broader-region content; self-sustaining areas local-only — decided per area, never assumed | geographic-broadening computation | Toggle previews both framings | Master Brain Part 13 (verbatim rule); draft s36 |
| Source-policy indicator | RSS-first, paywall-aware: free outlets (SFGATE, KQED, SFist, SocketSite, Patch, Palo Alto Online, city sites, Bay City News) for content; Google News RSS discovery-only; hard-paywalled (SF Chronicle) excluded; never reproduce paywalled text — summarize public facts + credit | news sourcing config | Hover → outlet policy | Master Brain Part 13 (verbatim) |
| Safe-zone preview | Static/carousel rendered inside iPhone safe zones (no critical text top ~13% / bottom UI band; 4:5 tiles inside center square for grid crop) | layout prompt emitter | Toggle safe-zone overlay | Master Brain Part 13 §Static and Carousel Post Rules |
| Escalation ladder panel | Per-story ladder position: static posted → shares vs threshold (~10+ shares auto-promotes) → video version queued → video clears benchmark → ad-spend recommendation lands in Approvals; reuses content_id for roll-up + lock identity per promoted variant | Event Ledger performance + escalation logic | Open story → each rung's object | Master Brain Part 13 §Escalation Ladder (threshold verbatim "roughly 10+ shares"); draft s36 shows 214-share example |
| Escalation notifications | "Last week's rate card crossed threshold — video auto-queued" | escalation events | Click → Tab 16/32 | matrix gap design_note ("share-threshold escalation shown as a ladder indicator") |
| GBP/blog draft cards | News engine also assembles GBP posts and blog drafts for approval alongside statics/carousels | News-to-Post output types | Approve per format | Master Brain Part 13 (formats verbatim) |
| Compliance footer per card | Fair Housing pass on all copy; source credit; framing never demographic | ComplianceResult | Expand | Master Brain Part 13 Strict Controls |
| My canvases list | Saved boards with name, node count, outputs generated, collaborators | canvas store | Open/archive | Intelligence Engine |

## States

- **Default**: active canvas + pending news cards.
- **Loading**: node pre-digestion runs async — new node shows "digesting…" until extracted_summary lands; news cards render server-side, queue shows count while rendering.
- **Empty**: canvas empty-state ("Drag in a listing, a news story, a voice note — generate a brief from any selection"); news queue empty ("No pending stories — sources checked continuously, RSS-first").
- **Error/degraded (fail-closed)**: ingestion service down for a node type → that add-affordance disabled with reason (never a node with fabricated summary); GSC connector stale → QUERY_CLUSTER nodes show as-of date + stale badge; escalation data unavailable → ladder shows "performance data unavailable" (never synthesized share counts); news source fetch failure → story skipped, logged — no card with unverified facts; approval always stages, nothing self-publishes even in degraded mode.
- **Permission-limited**: collaborators add nodes + comment; brief generation [BEST GUESS] any collaborator; news Approve restricted to approval-permitted roles; canvas visible only to invited role owners (tenant-scoped).
- **Mobile**: tabbed list variant per Layout.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| node | {source_id, type enum (6 values), ref, extracted_summary, position, added_by} | canvas/brief store |
| brief | {brief_id, sources[]=source_ids, generated_at, resulting content_id[]} | CreativeKernelBrief + ancestry |
| comment | {node_id anchor, author, text, ts} | canvas store |
| news story | {cluster of article refs, chosen angle, headline, source credit, outlet, framing (LOCAL/BROAD), formats[]} | News-to-Post engine |
| rendered asset | layout prompt (canvas, text, safe-zone anchor, font, contrast) + image | layout emitter (template-first; AI images for conceptual topics only) |
| ladder state | {story content_id, rung: STATIC→VIDEO→ADS, shares count, threshold, next action} | Event Ledger + escalation logic |
| geo decision | {target_area, density_class, broadening: LOCAL_AND_BROAD vs LOCAL_ONLY} | per-target-area computation |

## Rules & compliance

- Nothing self-publishes: every news output stages to an approval queue; promoted variants that spend money route to Approvals (Tab 13).
- Paywall law: never reproduce paywalled text; summarize public facts, credit the source; hard-paywalled outlets excluded from content.
- Copyright/corpus: competitor + third-party canvas sources are inspiration-only; storage limited to hash/URL/excerpt/summary; monitoring via official APIs or manual review — no scraping (matrix correction #5).
- MLS hard rules on listing nodes (no embeddings/AI training/public exposure).
- Safe zones are law on statics/carousels; visual styling stays configurable (open design decision — never hardcode colors/fonts).
- Fair Housing pass on all generated copy; geographic broadening is a market-density decision, never a demographic one.
- Escalated content carries content_id for roll-up + lock identity per locked/promoted variant; a promoted video goes through the full run → compliance → ContentLock path like everything else.
- Tenant isolation: canvases, briefs, news outputs all tenant-scoped.

## Cross-links

In: Briefing (Tab 12), voice notes, GSC demand connector, market read, competitor monitoring, listings. Out: content engine → Tab 16 (briefs), Tab 13 Approvals (ad-spend rungs), Tab 19 Distribution (approved statics/GBP posts), Tab 31 Attribution (lineage tracing), Tab 32 (escalated video renders).
Ledger: brief lineage → content_id ancestry; consumes share/engagement events for the ladder; emits approval + escalation events.

## Open decisions

- **[DECIDE] Build phase**: spec marks the Canvas P2 and "UI-heavy — human development lane; v1 can be a thin layer over existing ingestion plus brief storage." Interim design: ship v1 as the mobile-style node LIST + generate flow on all breakpoints; the drag canvas is the v2 desktop layer. Screen contract identical either way.
- **[DECIDE] Exact share threshold**: canonical is "roughly 10+ shares" — make it a configurable tenant setting defaulting to 10, surfaced next to the ladder.
- **[BEST GUESS] Real-time multiplayer transport** (presence/comments): standard collaborative-doc sync; no spec constraint — UI only needs presence avatars + node-anchored comments.
- **[BEST GUESS] News check cadence**: continuous RSS polling with the queue badge updating on new clusters; spec sets no interval.
