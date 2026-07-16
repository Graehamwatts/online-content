# 35 · Management Module — Concept Overview (its own app shell)

**Purpose** Concept overview of PropertyIQ Management — per the spec a **separate product/app shell**, not a tab of the agent platform: a staff console plus three scoped portals (owner / tenant / vendor), with the Daily Review Card as the home hero. Enterprise-grade multi-entity management on a native double-entry GL (system of record), dial-governed Wattson autonomy, and "sell a building, the books do themselves" disposition. Sequenced after the agent platform; MVP = the owner's 47-property CSV-import portfolio (Phase 2). (PropIQ Management Master Brain — UPDATED, Part 1 locked 2026-06-23.)

**Primary users** Staff console: owner/PM staff (12 canonical RBAC roles per the Brain's RLS+RBAC model). Owner portal: property owners/investors. Tenant portal: tenants. Vendor portal: maintenance vendors. Each portal sees ONLY its scope.

**Entry points** Separate app URL/login (own shell; SSO from PropertyIQ for the owner) [BEST GUESS on SSO]; tenant portal via invite at lease activation; vendor portal via work-order dispatch link; owner portal via owner invite; PropClose DEAL_CLOSED event auto-triggers the disposition flow (system entry).

**Exit points** Daily Review decisions → their underlying records (work order, renewal, AR ladder, reconciliation); "Draft the disposition listing?" wedge prompt → PropClose; owner statement → owner portal + PDF; Wattson approval cards → the module's own approval inbox. Cross-app: hold-vs-sell recommendations link to PropSearch comps/underwriting (the Predictive Lifecycle Asset Manager wedge).

## Layout
- **Staff console header:** "M" avatar, "PropertyIQ Management", subtitle "37 units · Daily Review · [date]", nav: Owner portal / Tenant portal / Vendor portal (per draft — these are links to the scoped apps, not tabs).
- **Home hero:** the Daily Review Card (brand-bordered) — "N decisions, then you're done."
- **Stat strip below hero:** Occupancy · Rent collected (month) · Open work orders · Owner statements due.
- **Left nav (full app) [BEST GUESS from Brain surface list]:** Daily Review · Properties/Units · Entity map · Leasing · Renewals · Maintenance · Accounting (GL, AR/AP, bank feeds, reconciliation) · Owners & statements · Compliance/Notices · Fixed assets & dispositions · Reports · Settings.
- **Mobile (375px):** Daily Review Card is the entire above-fold experience; each decision is a swipeable card with approve/pick actions; stat strip beneath; portals are mobile-first by design (tenants pay/report from phones).

## Element inventory
| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Daily Review Card | The day's queued decisions (draft: 4). Examples: maintenance vendor-bid pick ($1,450 vs $1,720-with-warranty, autopilot-solicited); renewal approval (+4% with comps attached); AR late-tenant soft reminder with notice ladder shown; 2 unmatched bank-feed items with suggested matches | Wattson draft/triage layer over work orders, renewals, AR, reconciliation | per-row approve / pick / edit / defer; solo-mode consolidates all queues into this one daily session (Wattson Brain solo_mode) | draft s35; matrix "Daily Review Card as home hero" |
| Stat strip | Occupancy 97% · rent collected 94% $58.1K · open WOs 3 · statements due Aug 1 auto | GL + rent roll + WO store (generated, never hand-maintained) | tiles → module screens | draft s35 |
| Entity map | SIMPLE/ADVANCED projection of organizations → legal_entities → entity_ownerships → portfolios → properties → buildings → units; models land trusts, nominee trustee, cash-hub account; "invisibly simple for a solo owner" | core hierarchy schema (Module 1) | toggle SIMPLE/ADVANCED; click entity → its books | Mgmt Brain Part 1/Module 1 |
| Accounting area | Native double-entry GL as system of record: journal entries (sum(debit)=sum(credit) enforced), Schedule-E-aligned chart, cash vs accrual per accounting book, AR/AP sub-ledgers, owner distributions as equity movements, intercompany due-to/due-from | gl_accounts, journal_entries/lines, ar_charges, ap_bills | drill any statement line → journal → source event; QuickBooks export | Mgmt Brain Module 1 GL |
| Bank feeds & reconciliation | Plaid feed matching (ordered matching ending in suspense), Stripe clearing postings, BankReconciliation records; trust: three-way reconciliation (trust_beneficiaries, trust_reconciliations) | bank_transactions, bank_reconciliations | accept suggested match, split, send to suspense | Mgmt Brain Module 1 |
| Leasing funnel | Tour → application → screening → lease → move-in → renewals, entity-scoped, posting through the ledger; showing scheduler with the required Wattson cadence (schedule, 24-hr and several-hours reminders both sides, post-showing follow-up, host action prompt); portable ApplicationProfile + entity-scoped ListingApplication; applicant-paid screening (Stripe) via ScreeningAdapter (TransUnion SmartMove first); Plaid income verification + GPT-4o Vision doc ingestion with allowed/disallowed extraction categories | leasing module | manage showings, review applications; screening AI-assisted but **human-decided** | Mgmt Brain Module 2A |
| Adverse-action workflow | Automated FCRA adverse-action letters AFTER a human decline/conditional approval; includes CRA/provider info + dispute rights | screening module | triggered by human decision only | Mgmt Brain Module 2A (FCRA hard blocks) |
| Lease gen + e-sign + move-in | CA-compliant templates or uploaded counsel-approved lease; landlord name never guessed — derived from Module 1 title/entity model and snapshotted at signing; e-sign via adapter (DocuSign); deposit into trust-ready ledger; move-in inspection; activation creates AR rent schedule + tenant portal invite | Module 2B | generate/upload, send for signature, record inspection | Mgmt Brain Module 2B |
| Renewals pipeline | 120/90/60-day renewal calendar for every active lease with known end date; proposed terms with comps attached; Wattson runs it within the autonomy dial | renewal automation | approve/edit offers; non-renewal handling | Mgmt Brain Module 2B; draft Daily Review row |
| Maintenance autopilot + vendor portal | Report → triage → vendor bid solicitation (autopilot) → human pick → dispatch → invoice → AP posting; vendor portal scoped to assigned WOs | WO store + vendor portal | pick bid, approve invoice | draft s35; matrix Management row |
| Owner portal + statements + approval inbox | Owner-scoped: statements (generated artifacts from GL), distributions, approval inbox (e.g. repair over threshold), documents | owner portal (scoped RLS) | owner approves/declines | matrix Management row |
| Tenant portal | Ledger/balance, payments, maintenance requests, documents, renewal offers | tenant portal | pay, submit WO, sign | Mgmt Brain Module 2B §6 |
| Compliance rules engine surfaces | Parameterized, jurisdiction-aware rules seeded with California; notices/eviction tracking with the notice ladder | compliance engine | view applicable rules per property; generate notices (human-approved) | Mgmt Brain Part 1; draft AR row ("notice ladder shown") |
| Fixed assets + disposition tracker | Fixed-asset register, depreciation schedules; the 18 ordered disposition actions (validate sale packet → freeze cutoff → prorate → final depreciation → proceeds → selling costs → debt payoff → remove asset → clear accum. depreciation → book gain/loss → tax flags (§1231/§1250/§1245/1031/installment/related-party) for CPA → deposit settlement + notices → lease termination → close AR/AP → final statement → balance-sheet/consolidation update → audit-ready packet → archive SOLD) | disposition engine, triggered by PropClose DEAL_CLOSED | single Wattson approval card "Building sold — disposition packet ready" with Approve & Post / Edit Closing Statement Mapping / Send to CPA / Simulate Only / Reject-Hold | Mgmt Brain Part 1 Disposition spec |
| Wattson autonomy dial | Draft → Notify → Auto-within-limits → Full-auto, owner-set, with hard compliance gates; tier-mapped (Core=Draft, Professional=One-Approval, Portfolio/Enterprise=policy-bounded autonomy; basis/tax/distributions ALWAYS require approval) | agent_capabilities, autonomy_policies | set dial per capability | Mgmt Brain Part 1 |
| Copilots (4) | Owner / PM / tenant / vendor conversational copilots, each scoped to its portal's data | Wattson instances (scoped) | chat | matrix Management row; Mgmt Brain |
| CSV import (MVP) | Guided CSV + concierge migration first (AppFolio/Buildium/Yardi importers by demand); the 47-property pilot portfolio runs real data before live payments/trust | import pipeline | upload, map columns, dry-run preview | Mgmt Brain Part 1 Migration; Phase 2 |
| Lifecycle wedge prompt | Predictive Lifecycle Asset Manager: hold-vs-sell / repair-vs-dispose recommendations contextualized against live market data (e.g. "Unit 4 HVAC $6k vs sell at 22% IRR via PropClose — draft the disposition listing?") | PropSearch comps + PropClose + Mgmt data | accept → PropClose draft; decline logged | Mgmt Brain Part 1 "The wedge" |
| Pricing/tier badge | Core $99/mo (50 units, $1.50 overage) · Professional $199/150 (launch default) · Portfolio $499/400 · Enterprise $1,499/1,000 ($1.25) — determines Wattson tier features | plan record | upgrade flow | Mgmt Brain Part 1 Tiers |

## States
- **Default:** Daily Review with today's decisions; done state = "0 decisions — you're done" with the stat strip.
- **Loading:** ledger-derived stats compute server-side; show as-of timestamps.
- **Empty (new tenant):** CSV-import onboarding hero replaces the Daily Review until first properties exist.
- **Error/degraded (fail-closed):** Plaid feed down → reconciliation panel shows disconnected + no fabricated matches; posting engine rejects unbalanced entries (sum(debit)≠sum(credit) is a hard block); disposition exceptions (partial sale, seller financing, casualty proceeds, unreconciled bank/trust, locked period) route to human — never autopost; screening provider down → applications hold, no AI-only decisions ever.
- **Permission-limited:** RLS + RBAC everywhere; every tenant-owned table carries org_id; no cross-org joins; portals see only their scope ("Each portal sees only its scope" — draft footer).
- **Mobile:** Daily Review card-per-decision swipe flow; tenant/vendor portals mobile-first.

## Data fields
Org/entity/portfolio/property/building/unit hierarchy ids; lease {parties, term, rent schedule}; journal entries/lines with dimensions {entity, property, unit, lease, bank, owner}; AR charges/AP bills; bank transactions + reconciliation state; trust beneficiary balances (three-way); screening results (allowed categories only); renewal calendar dates (120/90/60); WO {status, bids, invoice}; fixed asset {cost basis, accumulated depreciation, NBV}; disposition packet {gross price, selling costs, basis, accum. depr., NBV, book gain, loan payoff, net cash, deposits, leases affected, tax flags, exceptions}; occupancy/collection rates (derived); plan tier + unit counts.

## Rules & compliance
- Native GL is the system of record; statements are generated artifacts, never hand-maintained state; JournalEntry idempotency unique(org_id, source_type, source_id, source_event_key).
- Rental decisions, legal filings, and tax treatment ALWAYS stay with a human (module-level invariant).
- FCRA: consent, permissible purpose, adverse action, and audit required; screening AI-assisted, human-decided; hard blocks on disallowed extraction categories.
- Disposition: human confirms closing date, statement mapping, basis/allocation, ambiguous classifications, loan-payoff mapping, deposit treatment, distributions, CPA tax review, and all exceptions; automation only after approval; basis/tax/distributions require approval at every tier.
- Lease landlord name derived from the entity/title model and snapshotted — never guessed.
- Wattson autonomy hook before every send (showing reminders etc.); all money posts through the ledger.
- Trust accounting architecture-ready with three-way reconciliation before live trust activation (Phase 5+).

## Cross-links
In: PropClose DEAL_CLOSED (disposition trigger); PropSearch market data (wedge); PropertyIQ SSO for the owner. Out: PropClose (disposition listing drafts), QuickBooks export, owner statements to owner portal, CPA packet export. Ledger events: this module IS a ledger — emits posting events per money event; consumes DEAL_CLOSED, Plaid/Stripe transaction feeds; Wattson approval cards flow through the module's approval inbox (kept separate from the agent platform's Approvals Inbox per the separate-shell decision).

## Open decisions
- [DECIDE] Whether this overview screen stays in the agent-platform design doc or moves wholly to its own design track — interim per matrix: "design as its own app," this tab remains the concept overview + hand-off pointer.
- [DECIDE] Daily Review decision-count cap per day and ordering logic — interim: severity order (money-risk → legal-clock → tenant experience), max ~7 [BEST GUESS].
- [DECIDE] Payments/screening vendor contracts (Stripe Connect, TransUnion SmartMove, DocuSign named as adapter-wrapped picks; the ~40% non-autonomous build is gated on vendor contracts, payments underwriting, FCRA/legal, CPA review) — UI unaffected by final vendor via adapters.
- [BEST GUESS] Left-nav grouping; SSO entry; copilot placement as a persistent panel per portal (mirrors the platform-wide Wattson surface rule).
