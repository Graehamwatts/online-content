# 32 · Video Studio + Production Asset Registry

**Purpose** — The machine room behind the shoot pipeline and the content engine: render job queues (HeyGen-class avatar, Remotion alpha motion-graphics, Higgsfield-class b-roll), the clip lifecycle from PLANNED to published, the file-match reviewer that enforces system-assigned shot-ID naming ("humans never name files"), the avatar/voice asset library, the 90/10 authenticity meter, QC holds, and the swipe-file/hook library.

**Primary users** — Agent; editor and videographer roles (scoped lanes); marketing coordinator; internal ops (QC).

**Entry points** — Command Center production alerts; Content Review (Tab 16) approve → render jobs appear here; Shoot pipeline / LISTING_PLAN view (call sheet clips); notification "2 need file-match review"; Wattson ("what's rendering?").

**Exit points** — READY renders → Distribution Board (Tab 19) as DistributionPayloads; QC holds → Approvals/Review Queue; failed renders → retry/route to manual; clip status → LISTING_PLAN view; hooks/autopsy → Attribution (Tab 31); avatar-look gaps → next shoot's call sheet.

## Layout

**Desktop**
- **Header**: "Video studio · 3 rendering · 2 need file-match review · 14 published this month"; nav: Avatar looks / Swipe file.
- **Two-column main.** Left: Render queue, File-match review (warning-styled), Clip lifecycle per active shoot. Right: Avatar & voice assets, 90/10 meter, Swipe file/hook library.
- **QC strip** (below when items exist): audio/video QC queues + AI-disclosure manual-hold items.

**Mobile (375px)** — Single column, priority order: file-match review (actionable) → render queue → QC holds → clip lifecycle → assets/meter/swipe collapsed accordions. File-match confirm works as a full-screen compare sheet (thumbnail vs. candidate shot spec, Confirm / Relabel buttons).

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Render queue | Jobs with engine (HeyGen avatar / Remotion alpha / Higgsfield b-roll), state QUEUED / RUNNING / READY / FAILED, elapsed time, artifact links | Render child activities on CreativeProductionRun; Redis render queue (bounded workers, idempotency keys, backoff, per-provider rate limits) | Open job → logs/artifact; retry FAILED; cancel | matrix gap "Video Studio: HeyGen render queue…" P1 + design_note (state enum verbatim); Master Brain Part 13 render contract |
| Remotion render detail | GitHub-Actions run URL + logs; output formats PNG-sequence (primary) / ProRes 4444 / WebM VP9 alpha + manifest.json (frame count, duration, resolution, source git SHA) | remotion-alpha-video-render playbook | Open workflow run; download artifact | Master Brain Part 11 §Motion Graphics Render Layer |
| Avatar engine log | Which engine actually rendered (premium engine explicitly requested; vendor may fall back) | render API response | Read-only per job | Master Brain Part 11 §Engine Selection |
| First-frame QC gate items | B-roll stills awaiting/failing first-frame QC (malformed faces/text, wrong location, lighting, artifacts) — regenerate the cheap still, not the video | b-roll generation pipeline | Approve still / regenerate | Master Brain Part 11 §B-Roll |
| B-roll coverage indicator | Per video: shots vs. floor (~1 distinct shot per 3–5s non-talking-head; short-form 8–14, long-form 40+) with source routes [AI]/[STOCK]/[MAP]/[FILM] | shot plan | Expand shot list | Master Brain Part 11 (floors verbatim) |
| File-match review card | Videographer upload without shot-ID → best-guess match (e.g. "IMG_4471.mov → VID-BEECH-KIT-02, 87% visual match") → Confirm or Relabel | Production Asset Registry (platform service, Spec Part F) | Confirm match / pick other clip_id / mark new | draft s32 (inherited); Intelligence Engine "humans never name files" |
| Clip lifecycle board (per shoot) | Per clip_id: PLANNED / SHOT / INGESTED / MATCHED / MISSING; rollup "23 planned → 21 uploaded → 19 matched"; assembly progress per finished video; product page fills as pieces finish | Production Asset Registry + assembly jobs | Filter by shoot/video; open clip | Intelligence Engine LISTING_PLAN view (status enum verbatim); draft s32 |
| Missing-clip alerts | MISSING clips flagged back to the shoot owner | registry | Create pickup task | Intelligence Engine registry |
| Avatar & voice assets library | Avatar looks (e.g. porch/office/car) each consented + signed, supported engines, usage contexts; voice clone version; per-render AI-disclosure note | avatar library + voice-identity records | Add look (requires consent/signature flow), retire look | draft s32; matrix Wattson gap "voice-identity signing/revocation" |
| Avatar-opportunity chips | Queued videos needing a look that doesn't exist → flagged + slotted onto the most convenient upcoming shoot | avatar-opportunity scan (monthly) | Accept slot → call sheet | Intelligence Engine Part 12 §Avatar-Opportunity Detection |
| 90/10 meter | Real-footage : avatar ratio this month (e.g. 84:16); policy: ≥10% genuinely personal from the agent's own camera, avatar capped at 90%; alert threshold as it climbs [BEST GUESS: draft's 25% early-warning line is a UI convention; the hard rule is the 90 cap] | 90/10 content classifier | Hover → per-piece classification | Master Brain Part 5 hard rule + glossary (verbatim); draft s32 |
| QC dashboard queues | Audio QC + video QC with WINNER/UNDERPERFORMER thresholds; render issues can fail render QA but cannot alter locked copy | QC pipeline | Pass/fail; fail → re-render from same lock | matrix gap "QC dashboard" P1; Master Brain render QA rule |
| AI-disclosure manual holds | Videos HELD because the target platform lacks programmatic AI labeling (e.g. TikTok via Buffer) — shows exactly which platform + manual step | AI Disclosure Per Platform table | Mark manually labeled → release | Master Brain Part 10 (verbatim hold rule); matrix design_note |
| Audio prep status | Text-normalization applied (no em-dashes in spoken lines, terminal periods, spelled-out numbers, break-tags only) — shown as a pre-render check | SSML pipeline + pronunciation dictionary | View normalized script | Master Brain Part 11 §Audio Prep |
| Swipe file / hook library | Saved hooks scored by autopsy results; top patterns surfaced (e.g. "specific-dollar-number opens") | hook-autopsy log + performance ledger joins | Browse/filter; send hook to concept engine | draft s32; Master Brain Part 10 A/B variant logging |
| Editor lane view | Assembly instructions per finished video: which clip_ids in what order with which overlays (role-scoped) | Call Sheet editor lane + registry | Mark assembled → upload master | Intelligence Engine Hybrid Production (role-split) |
| Published this month stat | Count of READY_FOR_PROPREACH → published pieces | ledger | Click → Distribution | draft s32 header |

## States

- **Default**: queues + lifecycle + assets as above.
- **Loading**: per-panel skeletons; render queue polls job states.
- **Empty**: "No renders queued — approved content appears here automatically"; file-match empty = "all uploads matched"; no active shoot = lifecycle panel hidden.
- **Error/degraded (fail-closed)**: render provider down → jobs stay QUEUED with provider-status banner, no silent retry storms (typed BLOCKED reasons, idempotency keys on retry); registry unreachable → file-match disabled with "matching unavailable — uploads held" (uploads never auto-guessed without the reviewer); 90/10 breach → publishing of further avatar content hard-blocked with explanation; disclosure-hold items cannot be released to distribution until marked.
- **Permission-limited**: videographer sees only upload + own shot list; editor sees assembly lane + file-match; agent/coordinator see all; QC pass/fail limited to QC-permitted roles.
- **Mobile**: single-column per Layout; file-match compare sheet is the primary mobile job.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| render job | {job_id, engine, state, started_at, elapsed, artifact_url, workflow_run_url, engine_rendered, content_lock_id} | render queue / provider webhooks |
| clip | {clip_id (system-assigned, e.g. VID-BEECH-KIT-02), shoot_id, status enum, source route, feeds content_id[]} | Production Asset Registry (Spec Part F) |
| upload match | {file_name, candidate clip_id, match_confidence %, decided_by} | registry matcher |
| avatar look | {look_id, name, consent + signature record, supported_engines[], trained_at} | avatar library |
| voice clone | {version, provider, signed identity, revocation status} | voice-identity records |
| 90/10 | monthly ratio + per-piece classification (PERSONAL vs AVATAR/AI) | 90/10 classifier |
| QC item | {type audio/video, thresholds, result, hold_reason (incl. AI_DISCLOSURE_MANUAL)} | QC pipeline |
| hook entry | {hook text, source content_id, autopsy scores, platform, variant A/B pair ids} | hook-autopsy log / Event Ledger |
| render manifest | frame count, duration, resolution, git SHA | Remotion artifact manifest.json |

## Rules & compliance

- Everything here executes AFTER ContentLock inside the governed run — render issues fail render QA but can never alter locked copy; a fix that changes copy = new version + new lock.
- Humans never name files: clip_ids are system-assigned at call-sheet time; file-match review is the only human step in naming.
- 90/10 hard rule: avatar/AI content capped; avatar-source captures hard-blocked from exceeding personal-content rules.
- AI disclosure per platform is non-negotiable (Part 5): unlabelable platform ⇒ HELD in QC, flagged for manual disclosure.
- CA AI disclosure hard-coded as line 1 of every personalized-video script and frame 1 of every asset (personalized renders passing through this queue).
- Avatar looks and voice clones require recorded consent/signing; revocation kills future renders using that identity.
- Kill switches / cost circuit breakers can pause the whole render layer; UI shows scope + reason.
- MLS footage/data in clips follows MLS hard rules (no AI training, no public exposure beyond permitted use).

## Cross-links

In: Tab 16 (approved runs → renders), shoot pipeline/call sheets (clips), Tab 12 briefing (production routes), Wattson. Out: Tab 19 Distribution (READY payloads incl. thumbnail + container fields), Tab 31 Attribution (autopsy/A-B data), Approvals/Review Queue (QC + disclosure holds), Admin (cost meters).
Ledger: consumes ContentLock identity on every job; emits render/QC state events and FALLBACK logs (120s personalized-video fail-safe); performance joins feed the swipe file.

## Open decisions

- **[DECIDE] Avatar/video vendor set**: assume HeyGen-class avatar API + Remotion (locked pipeline) + Higgsfield-class b-roll; personalized-video vendor is BHuman-primary behind a swappable adapter (BHUMAN | GANAI | TAVUS | HEYGEN_REMOTION). UI is adapter-agnostic — engine is a label on the job.
- **[DECIDE] Whether personalized-video (PropFlow-triggered) jobs share this queue or a separate lane. Interim: same queue, separate "Personalized" filter chip — they share the render contract and the Redis queue.
- **[BEST GUESS] 90/10 alert threshold**: warn at avatar share >25% of the month early (draft convention) with the hard block only at the cap.
- **[BEST GUESS] Swipe file size/scoring display**: list sorted by autopsy composite; exact score formula lives in the learning layer, UI shows rank + supporting metrics.
