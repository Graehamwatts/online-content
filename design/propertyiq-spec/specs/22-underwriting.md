# 22 · Underwriting Workspace

**Purpose.** The full "Underwrite this deal" surface for one selected property: a deterministic pro forma (income → expenses → NOI → debt → DSCR → cash-on-cash → IRR → equity multiple), an editable assumption pack with California verify-per-deal flags, ADU/BRRRR/Flip strategy overlays, three 5×5 sensitivity grids, Excel + memo exports, and run history. It is the heart of PropSearch (Master Brain §19) and the screen the investor persona pays for. No LLM anywhere in the math (§19.2, §12.8).

**Primary users.** Agent (Graeham), team analysts, investor clients working with the agent (agent-driven in v1; the workspace itself is agent-facing, outputs are what clients see).

**Entry points.**
- Property detail page (Tab: property detail / Screen 22's launcher) — "Underwrite this deal" button (§19.1: heavy model runs on one selected property, never inline on search rows).
- Zoning & Investment Intelligence panel (§17.6) — "add to underwrite as scenario" on an affirmative zoning answer (draft decision: zoning Q&A and deal math are ONE surface).
- Compare screen — "underwrite" action per compared property [BEST GUESS, consistent with draft cross-links].
- Run history list (this screen's own header nav) — reopen a prior `UnderwriteRunRecord`.
- Saved Properties screen — saved property row → "Underwrite" (matrix: saved properties carry custom assumptions + strategy tags).

**Exit points.**
- "Export Excel" → generates `UNDERWRITING_XLSX` asset (formula-driven, §20.1) → download + stored in Asset Gallery (Screen: asset gallery).
- "Client memo (review-gated)" → generates `UNDERWRITING_MEMO_PDF` → routes to Universal Review Queue / Outbox (Screen 24). Never sends directly (§30 approval table: "Underwriting memo sent to client = REVIEW_REQUIRED by sending module").
- "Render concept on parcel 🛰" (ADU tile) → ADU visual flow (§17.4): plan-view overlay (Mapbox, allowed) or AERIAL_ADU (license-gated, REVIEW_REQUIRED for marketing).
- Back to property detail; Run history drawer; assumption source-fact click-through → source panel.
- Segment supply: a run can be included in a PropReach audience segment (basis `UNDERWRITE_RUN`, §22.2) — via the Audiences screen, not from here (link only).

## Layout

**Desktop (two-column, 1.4fr / 1fr — matches draft ~37-iteration layout):**
- **Header (sitehead):** property address ("Underwrite: 742 Hurlingame Ave"), run badge ("Run 3 · assumptions edited"), rent-confidence chip ("Rentometer rent HIGH confidence" — RentEstimateProvider is Rentometer, per build state). Right nav: **Run history · Export Excel · Client memo (review-gated)**.
- **Main column (left):**
  1. Headline stat row: NOI (yr 1), Cap rate, DSCR (with under-1.0 warning inline), 5-yr IRR.
  2. Strategy overlays card — chip toggles: Buy & hold (default on), + ADU, BRRRR, Flip; one-line impact readout ("ADU overlay flips DSCR to 1.14…").
  3. Sensitivity grid card — one grid visible (5×5 heatmap), tabs/label for the other two; mandatory bear row pinned.
  4. "This lot, answered (Zoneomics)" panel — 4 tiles (ADU / SB-9 / garage conversion / dims) + free-text lot question input + disclaimer line. (Inherited draft decision — deepened below.)
  5. 5-year pro forma & exits table — NOI / cash flow / equity per year, exit scenarios line.
- **Right rail:** Assumption pack card — every editable assumption with source badge; verify-per-deal ⚠ badges; the **acknowledgement checkbox** ("I've reviewed the N flagged assumptions — required before export/memo"). Sticky on scroll.
- **Footer:** none; export actions live in header.

**Mobile (375px):** single column, order = header (address + run chip) → headline stats (2×2 grid) → assumption pack (collapsed accordion, "Edit assumptions (3 flagged)") → strategy chips (horizontal scroll) → sensitivity grid (horizontal-scroll container, `overflow-x`) → zoning panel (tiles stack) → pro forma table (horizontal scroll) → sticky bottom bar with "Export" (disabled until acknowledgement) and "Recalculate". Acknowledgement checkbox surfaces inside the export sheet.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Address + run header | Property, run number, edit state | `UnderwriteRunRecord` (§10.14) | Click address → property detail | §10.14 |
| Rent confidence chip | Rent estimate + confidence (HIGH/MED/LOW) | `RentEstimateSnapshot` (§10.9, Rentometer via RentEstimateProvider §12.3) | Click → source facts popover | §12.3 |
| NOI stat tile | Year-1 NOI | `deterministic_output.valuation.noi_year1` | Click → income/expense breakdown drawer (GPR, EGI,每 OpEx line) | §19.5, §19.8 |
| Cap rate tile | going_in_cap; implied value + GRM + expense ratio in drawer | `valuation` block | Same drawer | §19.5 |
| DSCR tile | NOI / annual debt service; red warning when <1.0 | `debt.dscr` | Click → debt drawer incl. full amortization schedule table (`AmortizationRow[]`) | §19.5, §19.8 |
| IRR tile | levered_irr over hold_years; equity multiple secondary | `returns` block | If IRR non-computable → shows "—" + manual-review flag chip (§19.5: return null + flag, never fake) | §19.5 |
| Strategy overlay chips | BUY_HOLD / ADU_UPSIDE / BRRRR / FLIP (from `InvestorStrategy` enum §8) | overlay outputs (`ADUOverlayOutput`, `BRRRROverlayOutput`, `FlipOverlayOutput` §19.8) | Toggle → live recalc; ADU chip disabled + tooltip when zoning gate = SUPPRESS (§19.6 "only when the zoning gate permits display") | §19.6 |
| Overlay impact line | Deterministic delta readout (DSCR/IRR shift) | computed from overlay outputs | none | §19.6, draft |
| Sensitivity grids (3 tabs) | 5×5 heatmaps: appreciation×rent_growth→IRR; exit_cap×hold_years→IRR+EM; interest_rate×ltv→CoC+DSCR | `sensitivity` block (§19.7/19.8) | Live recalculation on assumption edit; cell click pins scenario; tab switch | §19.7 |
| Bear row | 0%-appreciation row always present, visually pinned/bold | grid 1 | none — cannot be hidden | §19.7 |
| Zoneomics lot panel | 4 answer tiles: ADU, SB9 split, garage conversion, dimensional detail (FAR/height/coverage used-vs-allowed) | `ZoningLookupRecord` (§10.11) + Zoneomics v3 `controls`/`plu`/`capacity` (§17.5) | Tile click → sourced answer detail; affirmative answers show "add to underwrite as scenario" | §17.1–17.5, draft |
| Lot question input | Free-text zoning question ("can I add a second story?") | ZoningProvider (§12.5), NL parse | Submit → sourced, confidence-gated answer; claim level AFFIRMATIVE / CAUTIOUS_DISCLAIMERED / SUPPRESS (§8) | §17.2, draft |
| Zoning disclaimer line | Verbatim §17.3 disclaimer, always under the panel | static | none | §17.3 |
| ADU render link | "Render concept on parcel" → plan-view overlay (Mapbox attribution required) or photoreal AERIAL_ADU (license + review gates) | ImageryProvider §12.6, §17.4 | Opens asset request flow; AERIAL_ADU marketing use = REVIEW_REQUIRED | §17.4, §30 |
| 5-yr pro forma table | NOI / cash flow / equity per year; overlay-on year annotated | projection loop (§19.5) | Row hover → assumptions driving it; "every number traces to a clickable assumption" (draft) | §19.5, draft |
| Exit scenarios line | Sell-at-exit IRR/EM; BRRRR refi cash-out + kept cash flow | §19.5 exit math + §19.6 BRRRR overlay | Click → exit assumptions | §19.5–19.6 |
| Assumption pack card | Every assumption w/ value + source badge (`assumption_source_facts`) | `UnderwritingAssumptions` defaults (§19.4): vacancy 5%, mgmt 8% of EGI, maint 6% of EGI, reserves $275/unit/mo, hold 5 yrs, selling cost 6% + tax/insurance/HOA/utilities/landscaping/trash/other income + growth/cap-rate set | Inline edit any field → `assumption_overrides` (§19.3) → recalc; edited fields marked "edited" | §19.3–19.4 |
| Verify-per-deal ⚠ badges | CA flags: Prop-13 reassessment/Mello-Roos/supplemental bill; transfer tax by jurisdiction; rent control (AB 1482 + EPA/Mountain View local) | `verify_per_deal_flags` (§19.4) | Hover → explanation; counted into acknowledgement | §19.4 |
| Forecast-risk badge on appreciation | "forecast 72/100 elevated risk" next to appreciation assumption | PROPSEARCH_MARKET_FORECAST (§12.13) | Hidden entirely when ScoringService/forecast unavailable (fail closed) | §12.13, draft |
| Acknowledgement checkbox | "I've reviewed the N flagged assumptions" — blocks Export Excel + memo until checked | local run state; logged onto the run | Check → enables exports; state persisted per run | draft (inherited); flag basis §19.4. [BEST GUESS: acknowledgement stored as metadata on UnderwriteRunRecord] |
| Export Excel button | Creates `UNDERWRITING_XLSX` (formula-driven model) | `CreatePropSearchAssetRequest` (§20.3), use_case INTERNAL_ANALYSIS or CLIENT_FACING_REPORT | Disabled pre-acknowledgement; returns `asset_id` (never content_id, §20.3) | §20, §4.1 |
| Client memo button | Creates `UNDERWRITING_MEMO_PDF`; label "review-gated" | §19.9, §20.1 | Routes to Outbox (Screen 24); memo may include ScoringService investor-fit; buy/hold/pass label ONLY from ScoringService or explicit human selection, else memo prints "Manual review required before making an investment decision." | §19.9, §30 |
| Run history nav | Prior runs list: run #, date, strategy, headline IRR/DSCR, edited-assumptions diff | `UnderwriteRunRecord` per run (immutable; new run per recalc-and-save) | Open run read-only; "duplicate as new run" | §10.14, matrix ("run history") |
| Investor-fit score chip (optional) | PROPSEARCH_INVESTOR_FIT output when available | ScoringService (§12.10), `scoring_service_output` | Click → decomposed contributing factors (explainability rule); absent when unavailable — no local score ever | §12.10, corrections list |
| Manual-review flag chips | e.g. ASSUMPTION_VERIFY_PER_DEAL, SCORING_SERVICE_UNAVAILABLE, ZONEOMICS_LOW_CONFIDENCE | `manual_review_flags` (§10.14, enum §30) | Hover → meaning + what's suppressed | §30 |
| Save to Saved Properties | Persist property + custom assumptions + strategy tag | `SavedPropertyRecord` (§10.7) | Save/unsave; feeds alerts + audience segments | §10.7, matrix gap "Saved searches/properties" |

## States

- **Default:** completed run displayed, live-recalc enabled on assumption edits (recalc is deterministic + local-fast; a saved recalculation creates a new run record with new `idempotency_key` [BEST GUESS on save-vs-scratch mechanics]).
- **Loading:** skeleton stat tiles + "Running deterministic model…" — pipeline order per §19.5. Zoning panel loads independently (30-day cache TTL, §12.5); stale cache (>30d or jurisdiction update) triggers silent refresh with spinner on the panel only.
- **Empty (first run):** assumption pack pre-filled from defaults (§19.4) + region context; user confirms financing (LTV/rate/term — required fields of `FinancingAssumptions` §19.3) → "Run underwrite" primary button. Rent estimate required: if RentEstimateSnapshot missing, run blocked with "Rent estimate unavailable — cannot underwrite" (forbidden to guess rent, §19.2).
- **Error/degraded (fail-closed, §30):**
  - ScoringService down → investor-fit chip and forecast-risk badge disappear (`SCORING_SERVICE_UNAVAILABLE` / `PROPSEARCH_MARKET_FORECAST_NOT_DEFINED`); deterministic metrics remain. No buy/hold/pass anywhere.
  - Zoneomics low confidence / jurisdiction not covered → tiles show "Needs verification" or panel collapses to "Zoning data unavailable for this jurisdiction"; ADU overlay chip disabled; AERIAL_ADU suppressed (§17.4).
  - IRR non-computable → null + manual review flag, tile shows em-dash (§19.5).
  - HOSTED_RENDER_FAILED on export → toast + retry; run data unaffected.
- **Permission-limited:** viewer-role team members see the run read-only, exports hidden [BEST GUESS — Master Brain defines tenant/app-user security §11.3 but not per-role UW permissions].
- **Mobile:** as in Layout; grids and tables scroll horizontally inside their own containers.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| price, beds, baths, sqft, unit_mix, property_type | USD int, ints, `UnitMix[]` | `UnderwriteRequest` ← PropertyRecord/IDXListingRecord |
| rent_estimate (+confidence, as-of) | $/mo, enum, ISO date | `RentEstimateSnapshot` §10.9 |
| avm_value (optional) | USD + confidence + as_of_date | `AVMSnapshot` §10.10 |
| financing: ltv (0–1), rate (nominal annual), amort_term_years, points, closing_costs, rehab_budget | decimals/USD | `FinancingAssumptions` §19.3 |
| strategy, hold_years | enum §8, int (default 5) | request |
| all 21 override fields (vacancy_pct … refi_costs) | per §19.3 `UnderwritingAssumptionOverrides` | run record input |
| Outputs: gpr, egi, per-line opex, total_opex, expense_ratio, noi_year1, going_in_cap, implied_value, GRM, loan_amount, monthly_pi, annual_debt_service, mortgage_constant, amortization rows, dscr, CFBT yr1, total_cash_in, CoC, levered_irr, equity_multiple, net_proceeds | per `UnderwriteDeterministicOutput` §19.8 | deterministic engine only |
| Overlay fields: adu_rent/cost/incremental_noi/value_uplift/zoning_claim_level; arv/refi_ltv/new_loan/cash_out; flip profit/annualized_return | §19.8 | overlays §19.6 |
| sensitivity grids | `SensitivityGrid` cells | §19.7 |
| assumption_warnings, verify_per_deal_flags, manual_review_flags, source_facts, compliance_flags | string[]/enums | §19.4, §19.8, §10.14 |
| memo_asset_id, spreadsheet_asset_id | asset_id strings | §10.14 (asset_id never content_id) |

## Rules & compliance

- **LLM boundary (§12.8, §19.2):** LLM allowed only for NL input parsing, memo drafting from already-computed metrics, clarification, formatting. Forbidden for any arithmetic, amortization, NOI, cap rate, IRR, local scoring/ranking, MLS embeddings.
- **Buy/hold/pass rule (§19.9):** label only from ScoringService or explicit human selection; otherwise the fixed sentence "Manual review required before making an investment decision."
- **Bear-case rule (§19.7):** 0%-appreciation row always shown.
- **Acknowledgement gate:** exports + memo blocked until flagged assumptions acknowledged (draft decision; flags per §19.4).
- **Client sends:** memo to client = REVIEW_REQUIRED via Outbox (§30). Equity-card use downstream requires consent gates (§18.3) — surfaced on the consuming screens, linked from here.
- **Zoning:** claim gate (AFFIRMATIVE / CAUTIOUS_DISCLAIMERED / SUPPRESS) on every claim; verbatim §17.3 disclaimer; Mapbox attribution on plan overlays; no Mapbox/Google tiles as AI-render input; AERIAL_ADU marketing = REVIEW_REQUIRED.
- **No guessing:** rent, mortgage balance, forecast scores — missing data blocks or degrades, never fabricates.
- **Fair housing:** no protected-class or family-status framing in memo text; memo compliance pass before send [per platform ComplianceProvider rule in corrections list].

## Cross-links

- **In:** property detail, zoning panel (§17.6), compare screen, saved properties, run history.
- **Out:** Outbox/Review Queue (memo), Asset Gallery (XLSX/memo/proforma-card assets), ADU visual flow, Audiences (segment basis UNDERWRITE_RUN), property detail.
- **Ledger events emitted:** `UNDERWRITE_RUN` (module PROPSEARCH, property_id required, contact_id/content_id/campaign_id nullable — §28), `GENERATED_ASSET_CREATED` on each export. Emits nothing else (four-event rule §28).
- **Consumes:** PropertyRecord/IDX facts, RentEstimateSnapshot, AVMSnapshot, ZoningLookupRecord, RegionProfile, ScoringService outputs.

## Open decisions

- **[DECIDE] Recalc-vs-run granularity:** interim design — slider/field edits recalc live in-session; "Save run" persists an immutable `UnderwriteRunRecord`; run history shows saved runs only.
- **[DECIDE] Acknowledgement persistence:** interim — stored per run in run metadata; re-acknowledge after any flagged-assumption edit.
- **[DECIDE] Client-visible underwriting (portal embed):** `PORTAL_EMBED` use_case exists (§20.3) but no portal UW view is specced; interim — memo PDF is the only client artifact.
- **[DECIDE] Draft grid labels ("rent × rate", "price × rehab") differ from §19.7's canonical three grids; interim — build the three canonical grids (appreciation×rent_growth, exit_cap×hold_years, rate×LTV) and treat the draft labels as illustrative, correcting the visual.
- **[BEST GUESS] Team-role read-only behavior** pending platform RBAC spec.
