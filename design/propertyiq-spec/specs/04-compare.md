# 04 · Compare

**Purpose** — Side-by-side decision surface for 2–4 properties, built as an "open lane" no portal will copy (draft rationale: portals monetize search sessions, not decision quality). Pins a baseline property, renders every other column as +/− deltas against it, computes a weighted-priority verdict from the user's own stated priorities, and converts the comparison into an agent-branded client deliverable logged to the CRM.

**Primary users** — Consumers/investors mid-decision; the agent preparing or sending a comparison to a client.

**Entry points**
- Card checkboxes on results (Screen 2) → compare tray → "Compare N →"
- Multi-select map pins (Screen 2 map mode)
- "Compare with 3 similar actives" auto-seed link on any property detail (Screen 3)
- Direct URL — compare sets are URL-addressable and persist (draft s4)
- Saved Properties screen ("Add from saved")
- A client-received comparison link (read-only variant)

**Exit points**
- "← Back to results" (originating search preserved: "From '3bd under $1.4M…' search")
- Column property name/photo → that Property detail (Screen 3)
- "Send comparison to client →" → Universal Review Queue / Outbox (client-facing send is review-first), logged to PropFlow contact timeline
- Add-column "+" → saved list picker / results picker / address lookup
- Row-level deep links (e.g. Zoning row → detail zoning section; underwriting metrics → Underwriting Workspace with that property)

## Layout

**Desktop**
- **Site header**: agent avatar, "Compare · N properties" + originating-search subtitle, "← Back to results".
- **Verdict card** (top, brand-left-bordered): "Verdict for your priorities: {property}" headline + 2–3 sentence tradeoff narrative + the flip condition ("If lot size mattered more than quiet, this flips"). Below it: **weight sliders row** ("Your weights: Quiet street ▮▮▮▮▮ · Schools ▮▮▮▮▯ · Price ▮▮▮▯▯ · Lot/upside ▮▮▯▯▯ — drag to re-weight; verdict recomputes live").
- **Controls row**: chips "Differences only (N same attributes hidden)" (default ON) / "All details"; right-aligned primary button "Send comparison to client →" with the caption "renders as your branded page + tradeoff narrative, logged to CRM".
- **Comparison table** (own `overflow-x:auto` container, sticky first column):
  - Header row: photo + address per column. Column 1 = 📌 pinned baseline with "Best fit · baseline" badge and a 3px brand top border. Other columns labeled "(deltas vs. pinned)". Last column = dashed "+ Add from saved (N), results, or any address" slot (only when < 4 properties).
  - Data rows in draft order: Price · Match (your prompt) · All-in monthly (PITI+ins+HOA) · Sqft/Lot/$-sqft · Commute · Schools (assigned) · Rent (yield offset) · Risk (fire/flood/quake /10) · Zoning & upside · DOM / negotiation read · Deal rating (ScoringService) · AI pros/cons.
  - Winner cell per row gets the `win` highlight; favorable deltas green.
  - Footnote row: fail-closed + column-cap rules text.

**Mobile (375px)**
- Verdict card full-width; weights become tappable slider chips in a horizontal scroll row.
- Table becomes **2-column swipeable cards**: pinned baseline fixed as the left column, remaining properties swiped through on the right (draft s4). Row labels render as section headers inside each card pair.
- "Send to client" as a sticky bottom button. Add-property via a "+" chip opening a bottom sheet.

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| Header context line | "Compare · N properties · From '{search}'" | SearchRecord (Brain §10.5) via compare-set origin | Back to results | Draft s4 |
| Verdict card | Winner for the user's weighted priorities + tradeoff narrative + flip condition | Weighted composition of per-row facts; weights from the user's search priorities (SearchRecord parsed criteria) | Recomputes live on slider drag | Draft s4. Fail-closed: verdict requires ScoringService/verdict service availability — see States |
| Weight sliders | Priority weights (quiet street, schools, price, lot/upside — derived from the user's prompt criteria, not a fixed list) | User session / SavedSearch | Drag; live recompute; winner flip is visible | Draft s4 |
| Differences-only toggle | Hides rows where all columns match ("N same attributes hidden") | Client-side over row data | Chip toggle; "All details" shows everything | Draft s4 (NN/g pattern) |
| Send comparison to client → | Renders the comparison as an agent-branded hosted page + tradeoff narrative; send goes review-first | HostedRenderProvider (Brain §12.9) → GeneratedAssetRef; logged to PropFlow contact timeline | Opens client-picker → lands in Outbox/Review Queue, never auto-sends | Draft s4; matrix "Universal Review Queue P0"; scheduled-reports client-facing exception |
| Pinned baseline column | Column 1, brand border, 📌 + "Best fit · baseline" badge | Compare set state | Any column's ⋮ menu → "Pin as baseline" re-anchors deltas [BEST GUESS on the affordance; the pin behavior itself is draft-specified] | Draft s4 |
| Delta cells | +/− vs pinned (e.g. "+$61,000", "−$470/mo", "+4 min") | Computed client-side from deterministic per-property facts | Hover/tap shows the absolute value | Draft s4 |
| Add-property slot | Dashed "+" column: add from saved (count shown), results, or any address | SavedPropertyRecord list; search; address lookup → PropertyRecord | Opens picker; at 4 columns, adding a 5th replaces the weakest match with an **undo toast** | Draft s4 |
| Price row | List price / deltas | IDXListingRecord | Winner highlight | Draft s4 |
| Match row | "5 of 5" vs "4 of 5 · miss: busier street" | SearchResultRecord per property (service-computed) | Tap miss → explanation | Draft s4 |
| All-in monthly row | PITI+ins+HOA, deltas | CashflowPreviewMetrics (Brain §24.4) using the same editable assumptions as detail's Monthly cost module | Tap → assumption popover [BEST GUESS: shared assumption edit applies to all columns for honest comparison] | Draft s4 |
| Sqft/Lot/$-sqft row | Absolute + deltas; n/a for condos | IDXListingRecord | — | Draft s4 |
| Commute row | Minutes to the user's destination at their hour, deltas | LocalDataProvider routing | Destination inherited from search context | Draft s4 |
| Schools row | Assigned school + third-party rating per column | LocalDataRecord (Brain §16) | Tap → detail schools section | Draft s4; §16 display rules apply (attribution + disclaimers reachable) |
| Rent row | Rent estimate + yield, deltas | RentEstimateSnapshot + CashflowPreviewMetrics | — | Draft s4 |
| Risk row | fire/flood/quake n/10 triplet | Risk feed (same source as detail) | — | Draft s4 |
| Zoning & upside row | "ADU by right · builds to 3 (1 built)" / "at max units" / "Condo — n/a" | ZoningLookupRecord (Brain §17) | Tap → detail zoning panel | Draft s4; §17 gates: suppressed claims render "unavailable" |
| DOM / negotiation read row | "6d · multiple offers likely", "19d · seller leverage" | IDX DOM (deterministic) + negotiation-read label | — | Draft s4. Negotiation-read label is an inference — must come from ScoringService or be rule-based-and-labeled; [BEST GUESS] v1 ships a deterministic DOM-banded label with an info tooltip |
| Deal rating row | "Good — 4% under model" / "At model" | ScoringService + AVM model value | — | Draft s4 + draft QA line 2056: **ScoringService-only, fail-closed** — row disappears when unavailable (matrix correction #6) |
| AI pros/cons row | 2–3 pros/cons per column, fact-anchored (e.g. "roof 2009 (disclosure)") | Generated from listing facts + intelligence data only | — | Draft s4; every claim must trace to a SourceFact; fair-housing wording rules §16.1 |
| Fail-closed footnote | "Rows render only when data is confirmed for every column (or marked 'not disclosed')" | — | — | Draft s4 (NN/g consistency rule) |
| Column ⋮ menu | Remove, pin as baseline, open detail | — | — | [BEST GUESS] standard affordance |
| Read-only client view | The sent comparison as a branded hosted page: verdict narrative + table, agent card footer, no edit controls | GeneratedAssetRef hosted URL | PORTAL-view tracking on open [BEST GUESS: view event at asset level] | Draft s4 "branded page"; identity.json footer |

## States

- **Default**: 2–4 properties, differences-only ON, baseline = best match from the originating search.
- **Loading**: table skeleton with header photos first; rows appear as each data domain confirms across all columns.
- **Empty**: 0–1 properties → explainer state: "Pick at least 2 homes to compare" + entry-point hints (checkboxes on results, map multi-select) + saved-properties shortcut.
- **Row fail-closed**: a row renders ONLY when data is confirmed for every column or explicitly marked "not disclosed" — a row with a silent hole never renders (draft s4). Zoning claims below the §17.2 gate show "unavailable"; the whole row still renders only if every column has a value or an explicit unavailable marker.
- **Deal rating unavailable**: ScoringService down or unpublished → the Deal rating row AND any buy/hold/pass framing disappear entirely; deterministic metrics rows remain; manual_review_flag set (Brain §12.10; matrix correction #6).
- **Verdict degraded**: verdict/weights require the scoring seam; when unavailable, the verdict card collapses to "Verdict unavailable — compare the facts below" (no locally-computed winner; Brain §14.2 forbids local ranking).
- **Column cap**: max 4; adding a 5th replaces the weakest match with an undo toast.
- **Stale compare set**: a property goes pending/sold → column stays with a status badge ("In contract" / "Sold {date}") rather than vanishing; deltas still computed against last-known facts with as-of note.
- **Permission-limited**: client read-only view has no sliders/edit/add; agent-only actions (send to client) hidden from consumer sessions [BEST GUESS: consumers get "Share" instead, minting the same hosted page without CRM logging].
- **Mobile**: 2-col swipeable cards, pinned baseline fixed; horizontal scroll confined to the table container.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| compare_set: property_ids[], pinned_property_id, source_search_id, weights{} | URL-addressable, persisted | Compare-set record [BEST GUESS: stored per app_user like SavedPropertyRecord, §10.7 pattern] |
| list_price + delta | USD / signed USD | IDXListingRecord |
| match count + misses | "N of 5" + miss labels | SearchResultRecord |
| all_in_monthly + delta | USD/mo | CashflowPreviewMetrics (shared assumptions) |
| sqft, lot_sqft, price_per_sqft | int / USD | IDXListingRecord (computed $/sqft is deterministic) |
| commute_minutes + delta | min | LocalDataProvider |
| school assigned + rating + provider | name, n/10, attribution | LocalDataRecord |
| rent_estimate_monthly, yield | USD/mo, % | RentEstimateSnapshot / CashflowPreviewMetrics |
| risk triplet | n/10 ×3 | risk feed |
| zoning summary: adu_allowed, max_units, units_built, claim_level | typed | ZoningLookupRecord |
| DOM, negotiation label | int d + label | IDX; labeled rule-band (interim) |
| deal_rating | label + % vs model | ScoringService + AVMSnapshot |
| pros/cons | 2–3 strings each, SourceFact-anchored | generation pipeline over listing facts |
| weights | per-criterion 0–5 | user session; seeded from parsed search priorities |
| sent deliverable: asset_id, hosted URL, recipient contact_id, sent_at | GeneratedAssetRef | Brain §10.16, §20; PropFlow timeline entry |

## Rules & compliance

- **No local scoring/ranking** (Brain §14.2, §12.10): deal rating, match scores, investor-fit, and the weighted verdict all come from ScoringService/search services. Deterministic metrics (price, $/sqft, deltas, cashflow math per §14.4) MAY be computed locally.
- **Fail closed** on deal rating and verdict (matrix correction #6); on any row with unconfirmed data (draft NN/g rule); on zoning claims below gate (§17.2).
- **Schools**: same data for every user; attribution + disclaimers reachable from the row; school data never feeds the verdict weighting algorithm's defaults — "Schools" appears as a weight ONLY because the user explicitly asked for it in their search (user-initiated, §16.4 allowed path). If the user's prompt didn't mention schools, the schools weight slider does not appear by default.
- **Fair housing wording** (§16.1) in verdict narrative and pros/cons: facts, never characterizations ("feeds Roy Cloud, rated 9/10 by {Provider}" — never "better schools" without the rating attribution; never "safe/family-friendly").
- **Client send is review-first**: "Send to client" creates a draft in the Universal Review Queue/Outbox; nothing client-facing auto-sends (workspace standing rule + matrix Outbox P0). Send also requires the contact's channel consent via ComplianceProvider (matrix correction: no consent model bypass).
- **MLS/IDX boundary** (§26.5): the hosted client page displays only license-permitted fields/photos; sold columns follow sold-display rules.
- **Zoning disclaimer** (§17.3) appears on the client deliverable when the zoning row is included.
- **Brand**: hosted deliverable footer from identity.json (DRE 01466876 for Graeham's tenant); the identity.json blocklist enforced.
- **Attribution**: hosted-page opens tracked at asset level; compare events carry search_id/property_id keys; PropSearch does not emit LEAD_* events (§25.3).

## Cross-links

- **In**: Results (S2) checkboxes + map multi-select, Property detail (S3) auto-seed, Saved Properties, direct URLs, client link (read-only).
- **Out**: Property detail (S3) per column, Underwriting Workspace (S22) from investment rows, Outbox/Review Queue (send flow), PropFlow contact timeline (logged deliverable).
- **Emits**: GENERATED_ASSET_CREATED (hosted comparison page, Brain §25.1); compare-set analytics events [BEST GUESS: COMPARE_VIEWED-class at asset/search level]; the send itself is logged by PropFlow when the human approves.
- **Consumes**: SearchResultRecord match context, all per-property snapshots (AVM, rent, zoning, local data, cashflow), ScoringService outputs.

## Open decisions

- **[DECIDE] Verdict computation seam**: the weighted verdict is an inference. Interim design: ScoringService gains a `PROPSEARCH_COMPARE_VERDICT` context taking the deterministic row facts + user weights; until published, the verdict card runs degraded (facts only) — the UI is built for both states.
- **[DECIDE] Negotiation-read labels**: interim = deterministic DOM bands with an ℹ tooltip ("19+ days on market in this area typically means seller leverage — based on DOM only"); upgrade path = ScoringService label.
- **[DECIDE] Compare-set persistence scope**: interim = per app_user record + shareable URL token (SavedPropertyRecord pattern); anonymous sessions get URL-state only.
- **[DECIDE] Weakest-match replacement rule** at the 4-column cap: interim = lowest match score is replaced (with undo toast); if match scores unavailable, replace oldest-added.
- **[DECIDE] Consumer "Share" variant**: interim = consumers can mint the same hosted page unbranded-send-free (no CRM log, no client picker); agent send remains the review-gated path.
- **[DECIDE] Shared vs per-column financing assumptions**: interim = ONE shared assumption set across columns (honest apples-to-apples), editable from the all-in-monthly row; per-column overrides deferred to the Underwriting Workspace.
