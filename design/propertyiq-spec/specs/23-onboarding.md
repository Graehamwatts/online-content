# 23 · Onboarding Wizard

**Purpose** The first-run flow that makes every other screen possible: it captures the agent's profile, tone (AI Personality Dial with the blocking hard-ceiling acknowledgement), voice/avatar assets, sphere, farm geography, budget tier, and platform connections, then scans the brand vault and deploys. Target set in the draft: "producing by day one, branded in under 10 minutes."

**Primary users** New agent/tenant owner (Graeham-persona) on first login. Also re-enterable per-step from Settings (each step becomes a Settings panel after completion).

**Entry points** First login after account creation (forced — no other screen unlocks content generation until the personality-dial acknowledgement is captured, per PropCast Master Brain "Onboarding Capture"); Settings > Voice & Tone / Strategy deep-links back into individual steps; Wattson can deep-link a user to an incomplete step.

**Exit points** Step 8 "Deploy" → Command Center (Screen 1) with the first Monday-style briefing queued. "Skip voice/avatar" → continues wizard but flags account as static-videos-only. Abandon → resume banner on next login at the last incomplete step.

## Layout
- **Header (all steps):** avatar chip, "Welcome to PropertyIQ", step label ("Step 3 of 8 — your AI's personality"), progress dots (●●●○○○○○) right-aligned. Matches draft markup.
- **Main:** single centered column, max-width 640px, one decision per screen. Back / Continue buttons bottom-left; Continue is primary (ink button) and disabled until the step's required fields validate.
- **Footer note:** small grey line listing remaining steps (as in draft: "Remaining steps: 4 voice/avatar clone (or skip → static videos) · 5 sphere import + analysis report · 6 farm + listing-focus commitment + budget tier · 7 platform connections (OAuth) · 8 brand vault scan → 3 previews → deploy").
- **Mobile (375px):** identical single-column flow; sliders become full-width touch targets ≥44px; progress dots collapse to "3/8"; the example-rewrite card stacks below the sliders. The wizard is the one flow that must be fully phone-completable (agents onboard from their phone).

## Step sequence (8 steps, per draft screen 23 note — do not reorder)
1. **Profile** — agent identity capture (5-7 questions per matrix gap item): name, brokerage, DRE, markets, niche, years, team-or-solo. DRE/brokerage fields validate against identity.json-style brand record and become read-only afterwards (brand tripwire).
2. **Brand voice capture** — writing samples / "how do you talk" prompts (precedes the dial, per Brain: dial step comes "after brand voice capture and before first content generation").
3. **AI Personality Dial** (the draft's rendered step) — see element inventory.
4. **Voice & avatar clone** — or skip → static videos.
5. **Sphere import + analysis report** — Instagram OAuth + contact import; generates the sphere analysis report (PropCast Group 1 deliverable).
6. **Farm + listing-focus commitment + budget tier** — geo tiers, the Market Read Layer's "budget-not-mix" logic and listing-focus commitment.
7. **Platform connections (OAuth)** — YT/IG(Business acct linked to FB Page — a tenant onboarding requirement per Brain Part 10 metrics rule)/FB/TikTok/GBP/LinkedIn/GHL/MLS.
8. **Brand vault scan → 3 previews → deploy** — reuses Tab 8's brand-vault flow; shows 3 branded content previews before Deploy.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Progress dots + step label | Position in the 8-step flow | wizard state | none (dots not clickable forward; back allowed) | draft s23 |
| Humor slider | humor_amount 0–5, pilot_default 2 (draft shows a 0–10 render — normalize to the Brain's 0–5 scale; keep the visual style) | AgentTasteProfile.humor_amount | drag; live example rewrite updates | PropCast Brain "Onboarding Capture" |
| Edge slider | edge_level 0–5, pilot_default 3 | AgentTasteProfile.edge_level | drag; example rewrite updates; worked example copy at each slider level (matrix design note) | PropCast Brain; matrix gap #4 |
| tone_mode toggle | LOCKED / FLOAT, pilot_default FLOAT, with one-line explanations ("FLOAT = per-piece recommendation inside hard limits") | AgentTasteProfile.tone_mode | toggle | PropCast Brain |
| Example rewrite card | Live sample copy at the current dial setting (draft: the "garage did not get the memo" ADU line at 6/3) — edge_level_examples_market keyed to the agent's market (pilot: east_palo_alto) | client-side template + dial values | updates on drag | PropCast Brain; draft s23 |
| Hard-ceiling acknowledgement checkbox | "I understand the hard ceiling: no politics, no punching down, facts never bent for a joke — content generation unlocks when checked." BLOCKING: Continue disabled and ALL content generation platform-wide disabled until checked. | hard_ceiling_acknowledged (must_equal true) + capture of acknowledged_at / acknowledged_by / policy_id personality_hard_ceiling_v1 / policy_version | check; hover/expand shows the full hard-ceiling list (never crude/sexual/mean/at client-buyer-seller expense/mocking home/Fair-Housing-adjacent/protected-class/who-lives-where/schools-as-proxy/demographic assumptions) | PropCast Brain "The Hard Ceiling" + matrix: "blocking acknowledgement checkbox — no generation until checked" |
| Voice clone recorder (step 4) | Record/upload voice sample → ElevenLabs PVC clone; requires signed VoiceIdentity authorization (consent, allowed use, provider ID, revocation path, fallback voice) before any cloned voice is used | VoiceIdentity record; ElevenLabs Agents | record, review consent text, sign, or Skip | Wattson Brain Part 7, List A #19 |
| Avatar clone setup (step 4) | Upload footage / book capture for avatar looks; [BEST GUESS] vendor HeyGen-class (LipDub/BeHuman candidates) — UI unaffected by vendor choice | avatar asset registry | upload or Skip | matrix gap #4; [DECIDE] |
| Skip-voice notice | "Skip → static videos" consequence banner | wizard flag | click Skip | draft s23 footer |
| Sphere import (step 5) | Instagram OAuth + CSV/GHL contact import; imported contacts default to unknown consent (blocks outreach until captured) | PropFlow contact intake | connect, upload | matrix corrections (consent model); PropCast Group 1 |
| Sphere analysis report | Generated report card shown in-wizard ("your sphere: N owners, M likely movers…") | PropCast sphere pipeline | view; emailed copy | PropCast Group 1 deliverable |
| Farm/geo picker (step 6) | Tier-1/tier-2 geography selection on a mini-map | geo config | draw/select | matrix gap #4 ("geo tiers") |
| Listing-focus commitment | Commitment selector consumed by the Market Read Layer (budget-not-mix logic) | strategy config | select | PropCast Brain Stage 2 |
| Budget tier selector | Plan/content budget tier cards | PlanTier / tenant config | select | matrix gap #4 |
| City Guide "Local Business Partner" slot | Optional: one merchant deal/coupon per city guide, filled during onboarding, stays until updated | City Guide container config | fill or skip | PropCast Brain line ~758 |
| OAuth connection cards (step 7) | Per-platform connect buttons with connected/failed state; IG requires Business Account linked to a FB Page (hard requirement called out inline) | integrations registry | click → OAuth popup | PropCast Brain Part 10; Screen 21 integrations |
| Brand vault scan (step 8) | Scans site/social for brand colors/logo → 3 branded previews → Deploy | brand vault (Tab 8 flow) | approve a preview set, Deploy | draft s23 note |
| Back / Continue buttons | Navigation; Continue disabled until step valid | — | click | draft s23 |

## States
- **Default:** step renders with pilot defaults pre-filled (humor 2, edge 3, FLOAT).
- **Loading:** sphere analysis and brand-vault scan are async — show progress card with "this takes ~2 min" and allow continuing other steps [BEST GUESS: parallelizable steps 5 and 8 scans].
- **Empty:** no writing samples in step 2 → offer "answer 5 quick questions instead."
- **Error/degraded (fail-closed):** OAuth failure → card shows retry + "what breaks without this" (mirrors Screen 21 integration cards); voice-clone provider down → offer Skip path, never fake a clone; acknowledgement missing on an existing/imported profile → generation stays blocked platform-wide and a resume banner appears.
- **Permission-limited:** only the tenant owner runs onboarding; team members invited later see a trimmed profile-only flow [BEST GUESS].
- **Mobile:** see Layout.
- **Re-entry:** dial changes after onboarding are future-only: create a new profile_version; in-flight drafts keep their version; locked content never mutates (Brain rule — surface this as an info note when editing later from Settings).

## Data fields
| Field | Format | Source of truth |
|---|---|---|
| humor_amount, edge_level | int 0–5 | AgentTasteProfile (versioned, profile_version) |
| tone_mode | enum LOCKED/FLOAT | AgentTasteProfile |
| hard_ceiling_acknowledged / _at / _by / policy_id / policy_version | bool + timestamps + ids (policy_id = personality_hard_ceiling_v1) | AgentTasteProfile |
| VoiceIdentity | signed authorization record: consent, allowed use, ElevenLabs voice ID, revocation path, fallback voice | Wattson voice config |
| Agent profile | name, DRE, brokerage, markets, niche | tenant identity record (locked post-onboarding, identity.json-equivalent) |
| Sphere contacts | contact records, consent = unknown by default | PropFlow (GHL now → PropFlow after migration) |
| Farm geo, listing-focus, budget tier | geo polygons/ids, enum, tier | strategy config |
| OAuth tokens | per platform | integrations registry |

## Rules & compliance
- **No generation before acknowledgement** — the single hard gate of this screen; enforced server-side (missing hard_ceiling_acknowledged=true is a deterministic block per the Brain's gate table).
- Hard ceiling text rendered verbatim from personality_hard_ceiling_v1, never paraphrased-only.
- DRE/brokerage locked from the brand record; blocklisted DRE values rejected (brand tripwire).
- Voice cloning gated on signed VoiceIdentity authorization (Never-Autonomous adjacent, List A #19).
- Imported contacts: unknown consent blocks outreach; wizard must not promise "we'll start messaging your sphere."
- Default tone presets stored in schema even though the preset UI is deferred (MVP 0 rule).

## Cross-links
In: first login; Settings deep-links. Out: Command Center (deploy), Settings > Voice & Tone (dial), Settings > Integrations (step 7 cards), Brand vault (Tab 8), Video Studio (avatar/voice assets, Screen 32), Past Client OS / CRM (sphere import results). Ledger events: profile created, AgentTasteProfile v1 written, VOICE identity signed, OAUTH_CONNECTED per platform, sphere report generated [event names BEST GUESS except AgentTasteProfile semantics].

## Open decisions
- [DECIDE] Avatar-clone vendor: assume HeyGen-class avatar API (LipDub/BeHuman candidates) — UI unaffected by vendor choice.
- [DECIDE] Slider scale display: Brain is 0–5; draft renders /10. Interim design: 0–5 with labeled stops, keep the draft's visual style.
- [DECIDE] Whether step 2 (brand voice) and step 5 (sphere) can be deferred with "finish later"; interim: steps 1–3 mandatory, 4–8 skippable with consequence banners, since only the dial gates generation.
- [BEST GUESS] "5-7 questions" profile content — exact question list to be finalized from the onboarding form implementation (PropCast Group 1).
