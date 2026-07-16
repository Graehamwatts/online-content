# 16 · Content Review & Approve (PropCast)

**Purpose** — The single creative decision surface for PropCast. Finalists from the Showrunner Gauntlet arrive here; the agent picks a direction, optionally steers conversationally, and the chosen concept builds the full container bundle (video + landing page + lead magnet PDF + comment-DM flow) which ships as ONE approval card. Per the Master Brain there are exactly two governed decisions in the whole pipeline: backlog approval (Monday briefing, Tab 12) and exact-version approval (here → ContentLock).

**Primary users** — Agent (Graeham); Wattson can steer on the agent's behalf via governed intents (ASK_WHY / APPROVE / REJECT / REQUEST_HUMAN_REVIEW), but approval itself is always human.

**Entry points** — Content queue item in Command Center; Monday briefing backlog item reaching AGENT_REVIEW; Wattson deep-link ("review the ADU piece"); notification ("3 finalists ready"); pipeline strip on any run in FINALISTS_BUILT/AGENT_REVIEW state; Approvals inbox (Tab 13) back-link.

**Exit points** — Choose + Approve → Approvals inbox (Tab 13) one-approval card → ContentLock mint → render → Distribution Board (Tab 19). "⚡ Create funnel" → Funnel Builder (Tab 17). Reject/defer → backlog. Element edit → element edit modal (stays on screen). History → ContentLock version history. ZERO_FINALISTS → manual creative review task.

## Layout

**Desktop**
- **Header**: run title ("Review: {topic} — pick a direction"), gauntlet summary line ("3 finalists survived · 12 generated, 9 culled"), nav: Backlog / History. Brief context pinned top-right: which signal/listing triggered this run and which backlog slot it fills (per ~37-iteration draft decision).
- **Main, zone 1 — Finalist cards**: 3-up grid (3–5 cards; fewer allowed, never padded). Selected card gets brand border + soft fill.
- **Main, zone 2 — Steering panel**: full-width chat input + Regenerate button, insufficient_finalists footnote.
- **Main, zone 3 — Pipeline strip**: always-visible 7-step position indicator (Signal/brief → Gauntlet → Pick & steer → Bundle build → One-approval/Lock → Distribute ~15 assets → Measure/autopsy).
- **Main, zone 4 (post-choice) — Container bundle preview**: four-quadrant (video thumb + first 15s / landing page preview / lead-magnet PDF page 1 / DM flow summary), each quadrant click-to-edit; single "Approve all → Lock" action routes through Approvals.

**Mobile (375px)** — Finalist cards become a horizontally swipeable card stack with the hook-score badge always visible; pipeline strip collapses to "step 3 of 7" chip that expands on tap; steering input docks above the keyboard; quad preview becomes a vertical 4-card scroll with a sticky Approve bar.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Finalist card (×3–5) | Hook line, hook/craft score badge, 15s video preview, angle + tone description, Choose button | PropCast Intelligence Engine: CreativeFinalist records on CreativeProductionRun | Play preview; Choose; expand full script | Intelligence Engine Part 17 §Finalists; matrix gap "Finalist review (3-5 concept cards)" P0 |
| Craft score badge | 0–5 craft score (finalists below 3 never appear); comedic pieces also carry a joke score ≥3 | Finalist scoring rubric | Hover → rubric meaning (3 publishable, 4 strong, 5 excellent) | Intelligence Engine §Finalists and the 0-5 Scorer |
| Hook score | Numeric hook score shown on card header (draft shows e.g. 8.7) | Gauntlet scoring [BEST GUESS: hook score display scale is the draft's convention; canonical rubric is 0-5 craft/joke — dev should render the canonical scores and treat the 8.7-style number as a legacy draft artifact or a 0-10 composite, decision below] | — | draft s16 + Intelligence Engine |
| Tone chip + "why this tone?" popover | FLOAT tone rationale referencing the agent's Personality Dial (e.g. "matches your dial 6/10 humor, 3/10 edge") with Accept / Adjust / Lock actions | AgentTasteProfile + per-piece tone recommendation (runs pre-gauntlet when tone_mode=FLOAT) | Open popover; Accept/Adjust/Lock tone | Intelligence Engine §tone_mode FLOAT; matrix design_note |
| Choose button | Selects the concept; triggers bundle build (FORGED → DESIGN_QA) | Run state machine | Click → zone 4 populates | Run state machine, Intelligence Engine |
| Steering input | Free-text conversational regeneration ("make A less salesy") — facts & compliance preserved, only creative moves | RegenerationSteeringTurn records | Type + Regenerate → REGEN_REQUESTED → new drafts | Intelligence Engine §conversational regeneration |
| insufficient_finalists state | If <3 qualify, screen shows fewer + insufficient_finalists_reason (which gates culled what); never pads | Gauntlet stage_6_finalist_selection | Read-only explanation | Intelligence Engine stage 6 (verbatim rule) |
| ZERO_FINALISTS state | Zero qualify → run status ZERO_FINALISTS or MANUAL_REVIEW_REQUIRED; screen offers "send to manual creative review" | Run state machine | Route to review task | Intelligence Engine state machine |
| Pipeline strip | 7 stages with current position highlighted; "Distribute" note explains per-platform variant explosion (9:16/1:1/16:9, captions, per-platform hooks/metadata, previewable per platform before lock) | CreativeProductionRun.status | Hover stage → status detail | draft s16 (inherited decision); Master Brain Part 10 metadata automation |
| Brief context pin | Which signal/listing triggered this and which backlog slot it fills | SynthesisBacklogItem + CreativeKernelBrief | Click → source signal / canvas brief (Tab 36) | draft s16 |
| Quad container preview (post-choice) | Video thumb + first 15s / landing page preview / PDF first page / DM flow summary (keyword, DM copy, CRM tag) | Container step outputs; DM flow per container-type matrix | Click any quadrant → element-specific edit modal | Master Brain Part 9 §One-Approval UX (verbatim) |
| Element edit modals | Edit ONE element without touching the underlying tool (agent never touches DM tool, page host, PDF generator, CRM fields) | Locked-draft fields | Edit → new draft → re-runs Gate 2 before lock | Master Brain Part 9 |
| Compliance chip (expandable) | Shows exactly which rules ran: Fair Housing, DRE line, no-fabricated-stats/claims check, AI-disclosure platform map | ComplianceResult on run | Expand → per-rule pass/fail | draft s16 (inherited); Master Brain Part 5 gates |
| ContentLock note / History link | Approve mints ContentLock v1; any post-approval edit = new approved_version_id + new compliance pass + new lock (never mutate) | ContentLock records | History → version list with lock_hash, diff | Master Brain Part 5; matrix correction #10 |
| Approve all → Approvals | Single button; the bundle lands in Approvals (Tab 13) as one card | ApprovalRecord | Click → route to Tab 13 | matrix gap "one-approval content review" P0; draft s16 footer |
| ⚡ Create funnel button | Lives on the content object (as on every content object system-wide) | ContentLock lineage | Click → Tab 17 pre-filled | draft s17 easy-button decision (inherited) |
| Reject / Defer actions | Return item to backlog with reason (logged as TasteFeedbackEvent) | TasteFeedbackEvent | Click + optional reason | Intelligence Engine feedback loops |
| Revoke (History view) | On any published version: "stop that campaign" finds and stops every downstream object with per-object checklist (posts, ads, links, QRs, DM flows, pages) | ContentLock + DistributionPayload graph | Confirm → downstream stop statuses | matrix gap "ContentLock/version history, revocation" P1 |

## States

- **Default**: 3–5 finalist cards, steering panel, pipeline strip.
- **Loading**: run in SPARKS_GENERATED/CULLED → skeleton cards + "gauntlet running: 25-spark batches, culling" progress line; regen shows REGEN_DRAFTING spinner on affected cards only.
- **Empty**: no runs awaiting review → "Nothing to review — next briefing Monday" + link to backlog.
- **Fewer-than-3**: insufficient_finalists_reason panel replaces missing cards (never padded).
- **Zero**: ZERO_FINALISTS explanation + manual-review routing.
- **Error/degraded (fail-closed)**: BLOCKED/TIMED_OUT runs show the typed reason (LLM timeout, budget cap, kill switch) — no silent retry; COMPLIANCE_FAILED shows failing rule(s) and the run cannot be approved; if ComplianceResult is unavailable the Approve button is disabled with "compliance check unavailable — cannot ship" (nothing public ships unlocked).
- **Permission-limited**: team roles (editor/coordinator) can view + comment + steer if granted; only the agent (or a role with approval permission per StepPermissionMode) sees an enabled Approve.
- **Mobile**: swipe stack per Layout.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| run_id, status | uuid, enum (24-state machine CREATED…READY_FOR_PROPREACH) | CreativeProductionRun |
| finalist: hook, point, structure, format plan, CTA, tone | text/struct | CreativeFinalist |
| craft_score, joke_score | int 0–5 | Finalist scoring |
| tone recommendation + rationale | struct (FLOAT output) | Per-piece tone rec / AgentTasteProfile |
| gauntlet stats | ints (generated, culled, survivors) + cull reasons enum | Gauntlet run record |
| steering turns | RegenerationSteeringTurn[] (idempotency-keyed) | Intelligence Engine |
| container previews | video URL/thumb, page preview URL, PDF page-1 image, DM {keyword, dm_copy, crm_tag} | Container step outputs |
| compliance result | per-rule pass/fail/needs_review | ComplianceResult |
| lock identity | content_id, content_lock_id, lock_hash (sha256), approved_version_id | ContentLock |
| brief lineage | brief.sources[] (canvas node ids where applicable) | CreativeKernelBrief |

## Rules & compliance

- Two-decision law: backlog approval + exact-version approval only; nothing public renders/distributes until the approved version passed deterministic compliance AND locked.
- Post-approval edit of anything (incl. container copy, metadata, captions) = new approved_version_id → Gate 2 rerun → new ContentLock. No exceptions.
- Steering preserves facts and compliance context — the regen layer can never unlock blocked content.
- Hard-ceiling (Personality Dial) violations are rejected regardless of score ("funny is not a defense").
- No-pad rule: never fabricate finalists to reach a count.
- Fair Housing + no-fabricated-stats + DRE line + AI-disclosure map all surfaced in the compliance chip; AI-disclosure-unlabelable platforms produce QC holds downstream (Tab 32/19), noted on the card.
- Kill switches and token-budget circuit breakers can BLOCK a run mid-review; UI shows the typed reason.

## Cross-links

In: Command Center content queue, Monday briefing (Tab 12), Ideation Canvas brief (Tab 36), Wattson, notifications. Out: Approvals (Tab 13), Funnel Builder (Tab 17), Distribution Board (Tab 19), Video Studio render queue (Tab 32), Attribution (Tab 31).
Ledger events: consumes ComplianceResult, run states; emits TasteFeedbackEvent (approve/reject/edit/steer/finalist choice), APPROVAL_DECIDED (via Tab 13), ContentLock creation; downstream LEAD_CAPTURED/LINK_SCANNED carry this lock identity.

## Open decisions

- **[DECIDE] Hook-score display scale**: draft shows 8.7-style numbers; canonical rubric is 0–5 craft + 0–5 joke. Interim design: render craft/joke 0–5 as the badge; treat any composite 0–10 as internal ranking only.
- **[DECIDE] Where the quad preview lives**: same screen zone 4 (interim, as specced) vs. only inside the Approvals card. Interim: both — zone 4 is the working preview, Tab 13 card is the governed decision record.
- **[DECIDE] Preview render vendor for the 15s clip** (HeyGen-class avatar + Remotion overlays per Part 11): UI is vendor-agnostic; player consumes an MP4/WebM URL either way.
- **[BEST GUESS] Steering-turn limit per run**: unbounded in spec but budget-capped; UI shows remaining budget only when the circuit breaker is near.
