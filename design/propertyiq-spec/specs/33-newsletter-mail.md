# 33 · Newsletter Builder + Direct Mail

**Purpose** The two recurring paper/inbox machines on one screen: (1) the per-segment personalized newsletter builder — 3-layer/two-axis personalization, section editor, per-segment preview switching, approval gate into the Outbox; (2) the direct-mail postcard composer — monthly farming postcards with the option-picker queue, mail-date calendar, one-card-one-goal-one-QR rule, locked contact block, and print-spec output. (Skills library: newsletter-generator + farming-postcard, per capability matrix; PropCast Master Brain CRM-email rules.)

**Primary users** Agent/owner (approves); content team members may edit sections (role-scoped) [BEST GUESS]. Recipients are the CRM database segments and the farm mailing list — never edited here, only referenced.

**Entry points** Left nav "Newsletter & mail"; Command Center briefing card ("farm letter due Thu"); scheduled option-picker email/notification 7 days before the 1st and 15th (farming-postcard preview cadence — server-side reminder on the 8th/24th per the cron-gap fix); Past Client OS cadence board (newsletter touch rows); Outbox items link back here for edits.

**Exit points** "Approve all 3 → Outbox" → Universal Review Queue (Screen 24) as a pending send; postcard "pick" → print-spec PDF generated + Outbox/vendor handoff; Archive link → published-content archive; QR labels → attribution dashboard (Screen 31) scan analytics; segment chips → Audience Builder (Screen 30) definitions.

## Layout
- **Header:** avatar chip, "Newsletter & mail", subtitle with next deadlines ("Farm letter Thu · postcard drop Aug 1"), nav: Archive.
- **Main (desktop): two equal columns** per draft — left = newsletter builder card, right = postcard composer card. Below [BEST GUESS extension]: full-width mail calendar strip (1st/15th drops, newsletter cadence) and the archive rail.
- **Mobile (375px):** stacked cards, newsletter first; segment chips scroll horizontally; the 3 postcard options become a swipeable carousel; approval buttons full-width sticky at card bottom.

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Newsletter issue header | Issue name + cadence ("July farm letter — 3-layer personalization") | newsletter build record | rename | draft s33; propiq-newsletter-build (3-layer/two-axis) |
| Segment chips | Owners (388) / Buyers (61) / Investors (24) — counts are AFTER-compliance counts from the audience layer | Audience segments (PropFlow/PropReach segment supply) | click switches the live preview to that segment's variant | draft s33; matrix "segment selector drives preview switching" |
| Per-segment preview pane | Rendered variant: owner variant leads with "your street's numbers" block (median + 2 recent solds), then ADU-rule change, then anniversary-equity module for applicable readers; buyer variant reorders new-inventory first — "same skeleton, three stories" | newsletter module library + local-intelligence feed (PropCast) | scroll; click a section → section editor | draft s33 |
| Section editor ("Edit sections") | Modular section list (market numbers, news module, equity module, listing module, CTA) with add/remove/reorder per the module-library model; per-section regenerate | module library; content pipeline | edit text (creates new version → new compliance pass), toggle per-segment inclusion | draft s33; matrix; ContentLock version rule (corrections list) |
| Personalization-layer indicator | Shows which of the 3 layers applied to the previewed reader class (segment story / geo data / per-reader modules like anniversary-equity) | personalization engine | hover explains each layer | propiq-newsletter-build |
| Compliance chip | Pass/needs_review from ComplianceProvider (Fair-Housing scan of copy; e.g. blocks "family-friendly neighborhood" class language) | ComplianceProvider | blocked → shows reason + suggested rewrite | matrix corrections (consent/compliance everywhere); Screen 24 pattern |
| "Approve all 3 → Outbox" button | One decision ships all segment variants to the Outbox as review-first sends (client-facing = review-first rule) | approval record | click → confirm → Outbox items created | draft s33 |
| Link policy note | Newsletter links go to the agent's blog/site, never directly to YouTube; thumbnail embedded as clickable image; utm_medium=newsletter carried for attribution roll-up | PropCast Brain CRM-email row | none | PropCast Brain lines 73/1613/1635 |
| Send audience note | Past-client segment runs monthly per Wattson Playbook Library (past-client-monthly-newsletter); seller weekly-listing-update embed is the weekly surface — this screen builds the monthly issue | Wattson Playbook Library | link to cadence board | PropCast Brain line 73 |
| Postcard drop header | "Aug 1 postcard — pick one of 3 options" | farming-postcard option cache | — | draft s33 |
| Option cards (3) | A · Just-sold proof / B · "41% of lots allow an ADU" / C · Home-value QR — previews of 3-5 hook options generated 7 days ahead; archetypes drawn from the 6 historical headline archetypes (equity, buyer-tagged, anti-Zillow, AI search, anti-Zestimate, neighbor envy) | farming-postcard skill option cache | click to pick; "regenerate options"; view full 6x4 preview front/back | draft s33; farming-postcard SKILL |
| Rules strip | Enforced constraints rendered inline: one goal · one QR (labeled e.g. AUG-PC for scan attribution) · locked contact block w/ DRE · audience = farm owners minus Do-Not-Mail (Sharon's list) · print-spec PDF on pick · mail calendar 8th/24th touchpoints server-side | postcard composer config | none (rules are non-editable) | draft s33 |
| Locked contact block preview | The brand-continuity contact strip (Intero + Graeham lockup, gold+black, DRE #01466876) — read-only from identity.json; brand tripwire blocks blocklisted DRE | identity.json / brand vault | none | farming-postcard skill; CLAUDE.md brand rule |
| QR label + router | QR minted through the owned link shortener with campaign label; CTA→landing-page router selection (which landing page the scan hits) | switchy-engine / link shortener; content_id + UTM | pick destination from approved pages | PropCast Brain line 810; farming-postcard |
| Audience count card | Farm owners count minus Do-Not-Mail suppressions, with suppression count shown | mail list + Do-Not-Mail list | click → list detail (read-only here) | draft s33 |
| Print-spec output | On pick: 6x4 print-ready PDF (Universal Mail Works specs) + order handoff | postcard render pipeline | download PDF; "send to printer" = review-required human step | farming-postcard skill |
| Mail calendar strip | 1st/15th drop dates, option-preview reminder dates (8th/24th), newsletter send dates; shipped/pending status per drop | schedule + archive | click a date → that drop's record | farming-postcard memory (server-side action); draft header |
| Archive | Past issues + postcards with sent date, audience size, scan/open stats | published-content archive + attribution ledger | open, duplicate-as-template | draft s33 nav; matrix "archive" |
| Option-picker queue state | If options were emailed and not yet picked: banner "3 options awaiting your pick for Aug 1" | option cache | pick from banner | matrix "option-picker queue" |

## States
- **Default:** current issue + next drop side by side.
- **Loading:** variant preview regenerating → skeleton with "personalizing for [segment]…".
- **Empty:** no issue in progress → "Start July letter" (pulls module suggestions from the local-intelligence feed); no postcard options yet → "Options generate 7 days before the 1st/15th — generate now" button.
- **Error/degraded (fail-closed):** local-intelligence feed unavailable → market-number sections render "data unavailable," never stale/fabricated numbers; compliance service down → Approve disabled with reason; mortgage/equity data missing for a reader → equity module drops out for that reader (no invented equity); Do-Not-Mail list unreachable → postcard pick blocked (never mail without suppression applied).
- **Permission-limited:** approve buttons owner-only (or delegated approver); team edits sections only [BEST GUESS].
- **Mobile:** see Layout; picking a postcard option from the reminder email deep-links to the carousel.

## Data fields
Issue id/name, segment ids + after-compliance counts, per-segment variant HTML, module list + versions, compliance result per variant, utm fields (content_id, utm_medium=newsletter), approval record (who/when), postcard option set {archetype, headline, art, goal, QR label, destination URL}, pick record, print-spec PDF URL, drop date, audience snapshot (count + suppression count), scan analytics per QR label, open/click stats per issue (feeds seller-signal flags, e.g. CMA-open propensity pattern from Screen 27).

## Rules & compliance
- Client-facing sends are review-first: everything exits via the Outbox to Graeham + Adrian pattern; nothing mails/emails directly from this screen.
- One card · one goal · one QR (hard composer constraint); locked contact block non-editable.
- Newsletter never links directly to YouTube (blog/site only).
- Fair-Housing scan on all copy; steering-adjacent language blocked pre-approval with rewrite suggestion.
- Do-Not-Mail suppression mandatory before any postcard pick finalizes; email sends respect consent/DNC via ComplianceProvider (imported contacts with unknown consent are excluded and shown as excluded).
- Any post-approval edit = new version → new compliance pass → new lock (ContentLock rule).
- Print QR usage is REVIEW_REQUIRED (PropReach QR rule).
- Numbers in market blocks trace to the data feed; no LLM-invented stats.

## Cross-links
In: Command Center briefing, cadence board (Screen 27), option-reminder notification, Audience Builder segments (Screen 30). Out: Outbox (Screen 24), Attribution (Screen 31 — QR scans, opens, utm roll-up), Published archive, switchy link/QR minting, landing pages (funnel-page builder for QR destinations). Emits: approval + version/lock events, MAIL_DROP scheduled/shipped [name BEST GUESS], NOTIFICATION_QUEUED for reminder emails; consumes: audience snapshots, local-intelligence feed, attribution scan events.

## Open decisions
- [DECIDE] Print vendor integration depth (Universal Mail Works API vs manual PDF handoff) — interim: generate print-spec PDF + a human "I sent this to print" confirmation (matches ChatGPT-Ads manual-channel pattern).
- [DECIDE] Whether newsletter cadence (monthly past-client + farm) is editable here or only in Playbook settings — interim: read-only here, edit in Settings/Playbooks.
- [BEST GUESS] Mail calendar strip and archive rail placement (draft shows only the two cards); segment-variant count fixed at the audience layer, not hardcoded to 3.
