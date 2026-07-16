# 29 · Voice Ops (Wattson)

**Purpose** The 24/7 phone layer's control surface: inbound calls answered by the AI in the agent's cloned voice with live streaming transcripts, an outbound queue that is permanently review-gated, hard escalation to the human in ~10 seconds with the transcript-so-far, and the voice-identity + calling-hours + usage-meter settings. (Wattson Master Brain Part 7 + Part 13 + Part 14.)

**Primary users** Agent/owner (primary); CRM coordinator as escalation backup (Wattson routing table: voice_escalation → owner primary, coordinator backup). Solo mode: everything routes to the owner.

**Entry points** Left nav "Voice"; escalation push notification / full-screen alert (phone rings within ~10s); morning-brief "after-hours calls" summary links; contact timeline call entries; Prospecting/Past-Client screens' call actions.

**Exit points** "Take over now" → live call joins on the agent's phone; transcript row → contact detail timeline; booking created → Calendar screen (BOOKING_REQUESTED → confirm queue); Settings link → calling hours/voice identity panels; missed escalation → voicemail + top of Today queue (Command Center).

## Layout
- **Header:** avatar chip, "Voice", subtitle "Calling hours 9–7 · after-hours = AI answer + morning summary" (display note: enforced hours are 09:00–20:00 local per Brain C10; render actual configured hours), nav: Settings. Add a live-call indicator dot when any call is active.
- **Main (desktop, single column of stacked cards per draft):** (1) LIVE call card (green-bordered, top) when a call is in progress; (2) Escalation protocol card; (3) Outbound queue card; (4) inbound call log table (add below the draft's cards — the matrix requires an "inbound 24/7 answering log"); (5) footer disclosure note.
- **Right rail (desktop, ≥1100px) [BEST GUESS]:** usage meters (voice minutes vs cap, calls-per-number), voice-identity status card, calling-hours summary.
- **Mobile (375px):** LIVE card first and sticky; escalation alerts take over the full screen (this is primarily a phone moment); log becomes a card list; meters collapse into a single strip.
- **Sticky:** live-call banner persists across the whole app while a call is live [BEST GUESS], since escalation is time-critical.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| LIVE inbound call card | "● LIVE — inbound, unknown number (postcard callback)" + streaming transcript excerpt in italics | ElevenLabs Agents webhook → real-time transcript stream (retention class VOICE_TRANSCRIPT_24M) | **Take over now** (agent's phone bridges in; AI goes silent the moment the human joins); **Let AI finish + book** (AI may offer only pre-approved slots in neutral language → creates booking_request_task, emits BOOKING_REQUESTED, unless auto-book into pre-approved slots explicitly enabled) | Wattson Brain Part 7; draft s29 |
| Caller attribution chip | Source guess for unknown numbers (e.g. "postcard callback") from campaign phone-number mapping | attribution/ledger | click → source detail | draft s29; [BEST GUESS on mechanism] |
| Escalation protocol card | Trigger list + behavior summary: caller asks for a human, pricing negotiation, distress signals → phone rings within ~10s with transcript-so-far on screen; missed → voicemail + immediate SMS + GHL task + top of Today queue | EscalationTrigger config (read-only display) | expand to full trigger list | Wattson Brain Part 7 + Part 14; draft s29 |
| Escalation alert modal (event, not resident) | Full-screen: caller, context-so-far transcript, Answer / Send to voicemail | live call session | answer bridges call | matrix: "escalation alert modal shows context-so-far before pickup" |
| Hard-escalation trigger display | The sensitive-topic firewall list: divorce/separation/legal proceedings; death/estate/probate; financial distress/bankruptcy/foreclosure; explicit human request; anger signals; any mention of legal action. On these the ONLY automated output is human_handoff_required=true — no score change, no field write, no audience inclusion, no automated outreach | ComplianceProvider / firewall config (read-only) | none | Wattson Brain C1/B1.8 |
| Outbound queue card | REVIEW_REQUIRED queue — always; permanent, no trust-promotion path for outbound client-facing AI calls (List A #17). Rows: purpose + contact + draft script (e.g. "Torres confirm-consult reminder", "Henderson rotation call assist — AI dials + briefs you, you talk") | Wattson task queue | Approve (dials within calling hours), Edit script, Reject; per-row DNC/consent pre-check result shown BEFORE approve enables | Wattson Brain Part 7; draft s29 |
| Pre-call compliance chip (per outbound row) | Result of ComplianceProvider.check_outbound_contact(): dnc_status, voice_consent_status, calling-hour check (daily DNC scrub) | ComplianceProvider | blocked rows show the exact failing check; approve disabled | Wattson Brain C9/B6.4 |
| Inbound call log table | All calls: time, caller, direction, duration, outcome (qualified/booked/escalated/voicemail), transcript link, disclosure-played ✓ (logged on every CALL_PLACED/CALL_RECEIVED) | CALL_RECEIVED/CALL_PLACED/CALL_COMPLETED events + transcripts | row → transcript viewer; search transcripts; filter after-hours | Wattson Brain Part 7 events; matrix "inbound 24/7 answering log" |
| Transcript viewer (drawer) | Full transcript with escalation point marked; audio playback | Audit Log transcript stream, VOICE_TRANSCRIPT_24M | play, copy, jump-to contact timeline | Wattson Brain Part 7 |
| Usage meters | voice minutes vs cap (Stage 1 defaults: 120 min/user/day rate limit; voice_api_spend $15/user/day budget cap; draft shows a monthly display "12/60 min this month" — render both daily caps and the plan's monthly meter), calls-per-number 2/day, max call duration 10 min hard cutoff | rate-limit/budget policy + usage counters | click → Settings limits panel | Wattson Brain Part 13; draft s29 |
| Voice identity card | Signed VoiceIdentity status: clone type PVC, provider ElevenLabs (voice ID shown), consent signed date, allowed use, fallback voice, **Revoke** action | VoiceIdentity record | Revoke (confirm modal; falls back to fallback voice / disables AI calling) | Wattson Brain Part 7, List A #19; matrix "voice-identity signing/revocation" |
| Calling-hours settings (via Settings) | outbound 09:00–20:00 local default, configurable per account/region (RegionProfile/AccountSettings override); inbound 24/7 allowed toggle; call-cutoff settings | ComplianceProvider-enforced config | edit (REVIEW: owner-only) | Wattson Brain C10/B6.2 |
| Disclosure footer | "Every call opens with the signed AI disclosure ('Hi, this is Wattson, an AI assistant calling on behalf of [agent_name], [DRE_number], [brokerage_name].') — tokens rendered read-only from identity config; omission forbidden" | mandatory tokens: agent_name, brokerage_name, DRE_number, region, ai_disclosure_phrase, region_required_language | none — read-only by design | Wattson Brain C21/B6.3; draft s29 |
| After-hours summary chip | Count of overnight AI-answered calls feeding the morning brief | call log | click → filtered log | draft s29 header |
| Cost comparison tile [BEST GUESS placement] | "Human ISA $15–25/hr vs Wattson ~$0.05–0.15/min 24/7" — Brain says this lives on the Admin Console; here show only the tenant's own voice cost this month | Admin cost dashboard | link to Admin (if role permits) | Wattson Brain Part 7/12 |
| Empty state | "No calls yet — your AI answers 24/7 at [number]. Forward your line or publish this number." | — | copy number | [BEST GUESS] |

## States
- **Default:** no live call → log + queue; live call → LIVE card pinned.
- **Loading:** transcript stream connecting → skeleton lines with "connecting to live transcript…".
- **Empty:** see empty-state row; outbound queue empty → "nothing waiting for review."
- **Error/degraded (fail-closed):** ElevenLabs/VoiceAgentProvider down → banner "AI answering unavailable — calls route straight to your phone/voicemail," outbound approvals disabled (never dial without the disclosure-capable agent); ComplianceProvider unreachable → ALL outbound blocked with reason (fail closed), inbound answering may continue [BEST GUESS: inbound is lead-initiated exception but disclosure still renders from cached tokens — if tokens unavailable, disable AI answering entirely].
- **Kill switch active:** red banner; active voice sessions terminated (<5s), queue frozen (Wattson Brain Part 13).
- **Permission-limited:** Stage 1 owner-only for settings/revocation; coordinator sees log + escalation backup alerts only [role split BEST GUESS from routing table].
- **Mobile:** escalation modal is the primary experience; everything else read-mostly.

## Data fields
Caller number/contact_id, direction, started/ended, duration (≤10 min hard cutoff), outcome enum, disclosure_played (bool, logged), transcript (VOICE_TRANSCRIPT_24M retention), escalation trigger type + timestamp, booking_request payload, dnc_status, voice_consent_status, VoiceIdentity {consent, allowed_use, provider_voice_id (pilot Pa3vOYQHHpLJn1Tf7hnP), revocation_path, fallback_voice}, voice settings (stability 0.50, similarity 0.80, style 0.00, speaker_boost true, rate 0.90–0.93 — read-only display in Settings), meters (email 200/d, sms 100/d context; voice 120 min/d; calls/number 2/d).

## Rules & compliance
- Disclosure opener immutable at agent-config level; never omitted; logged per call.
- Outbound client-facing AI calls: StepPermissionMode = REVIEW_REQUIRED, **permanent** (List A #17). Inbound lead-initiated: regulated-autonomy exception — approved scripts, disclosure, hard escalation, 24/7.
- DNC + consent + calling-hours check before ANY outbound dial; blocks emit DNC_BLOCK / COMPLIANCE_BLOCKED.
- Sensitive-topic firewall: hard escalation only; no other automated output.
- Voice agent must never negotiate price or make commitments (Never-Autonomous List); may offer pre-approved slots only.
- No cloned voice without signed VoiceIdentity; revocation immediately effective.
- Calling hours enforced at the routing layer via ComplianceProvider, not in the UI.

## Cross-links
In: Command Center Today queue, escalation push, contact timeline, Prospecting drafted call scripts, Past Client OS call assist. Out: contact detail (transcripts attach to timeline), Calendar (BOOKING_REQUESTED→BOOKING_CONFIRMED via PropFlow), Settings (hours/limits), Admin Console (cost, kill switch). Events emitted/consumed: CALL_PLACED, CALL_RECEIVED, CALL_COMPLETED (transcript_retention_class), BOOKING_REQUESTED; consumes DNC_BLOCK / COMPLIANCE_BLOCKED from the compliance layer; escalations create GHL/PropFlow tasks + SMS notifications.

## Open decisions
- [DECIDE] Voicemail drop content for missed escalations (AI-voiced vs pre-recorded human) — interim: pre-recorded human greeting, since AI voicemail content is client-facing REVIEW territory.
- [DECIDE] Whether coordinators can approve outbound queue items — interim NO: a team member's instance can never approve REVIEW_REQUIRED output; approval routes to the owner or an Admin-Console-delegated approver.
- [DECIDE] Monthly voice metering/overage display (Brain: base covers ~first $30/mo of voice, overage cost+20% is a List B open item) — interim: show the meter and "overage billing TBD" label, no invented rates.
- [BEST GUESS] Live-call banner persistence app-wide; right-rail layout; caller-source attribution via per-campaign phone numbers.
