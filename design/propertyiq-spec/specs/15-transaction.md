# 15 · Transaction Workspace (PropClose staff)

**Purpose:** The single staff-facing workspace for one live transaction — timeline-first, task-driven, document-safe. Everything a TC or agent needs to move a deal from contract to close lives here; every automation that touches the deal terminates in a review card here or in the Global Approvals Inbox. The cross-deal Kanban (TransactionBoardCard, PropClose §7.4) is the index; this screen is what a card opens into.

**Primary users:** Agent (Graeham-persona), Transaction Coordinator, brokerage admin (read/compliance). TC Wattson operates behind it via redacted context only.

**Entry points:** Command Center transaction card click-through · cross-deal Kanban board card · Global Approvals Inbox item ("open transaction") · Wattson chat deep link · PIPELINE_MOVED auto-creation toast ("New transaction created — open") · disclosure auto-pull report link (Wattson MLS playbook).

**Exit points:** Client portal ↗ (opens Screen 25 as the client sees it) · Close wizard (13-step flow, ends in DEAL_CLOSED + portal→HOMEOWNER) · Security review queue (wire quarantine) · Global Approvals Inbox (Screen 13) · CRM contact record (Screen 14) for any party with a contact_id · Offer Analyzer / Disclosure Analyzer sub-views (tabs on this screen) · back to Kanban index.

## Layout

**Desktop:**
- **Header bar:** avatar + deal title ("42 Cedar St — buyer side · $1,315,000"), subtitle (client name · Day N of M · closes {date}), right nav: "Client portal ↗", "Close wizard". Deal health chip (green/yellow/red, goes stale-grey if the underlying human update is unconfirmed — Sisu/Trackxi pattern per draft Screen 15 note).
- **Stage stepper (full width):** 7 canonical stages (CONTRACT_PENDING → INSPECTION_PERIOD → APPRAISAL → LOAN_COMMITMENT → FINAL_WALKTHROUGH → CLEAR_TO_CLOSE → CLOSED, PropClose §6.2 TransactionStage). Completed = filled brand; current-at-risk = red with deadline chip ("loan due Thu ⚠ T-2"); future = muted. Draft labels these in plain English (Open / EMD / Inspection / Appraisal / Contingencies / Docs & signing / Close) — keep plain-English labels mapped 1:1 to the enum.
- **Tab row under stepper:** Tasks (count) · Parties (count) · Documents (count) · Offers · Disclosures (⚑ flag count) · Timeline · Activity.
- **Main (left, ~60%):** the active tab's content. Default = Tasks: priority-ordered action cards.
- **Right rail (~40%):** context cards — Documents intake summary, Disclosures flags, Client portal status. Persist across tabs.
- **No footer.** Sticky: header + stepper + tab row stay pinned on scroll.

**Mobile (375px):** header collapses to address + health chip; stepper becomes a horizontal scroll strip; tabs become a swipeable segmented control; right-rail cards stack below the main list. Primary action buttons full-width. Re-cascade acknowledgment and wire banners always render above the fold of the Tasks tab.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Deal title + side + value | Address, BUY/SELL/DUAL, deal_value | TransactionRecord (§6.5) | none | §6.5 |
| Day counter "Day 11 of 21 · closes Jul 25" | contract_date → close_date_target elapsed | TransactionRecord | hover: date provenance (source doc pinned) | §6.5 + draft Screen 15 (intake provenance) |
| Deal health chip | green/yellow/red from ledger facts + structured human updates; stale-grey if unconfirmed | ledger events + human status updates | click: contributing facts popover | draft Screen 15; non-scoring rule §14 (workflow flag only, never a score) |
| 7-stage stepper | current_stage with per-stage completion + at-risk state | TransactionRecord.current_stage; TransactionDeadline | click stage: filters Timeline tab | §6.2, §7.2 |
| Deadline chips T-7/T-3/T-1 | next deadline with alert offset state | TransactionDeadline.alert_offsets_days [7,3,1] default | click: opens deadline detail (rule source, extension lineage) | §7.3 rule 4 |
| AT_RISK badge | fires when no progress after 70% of contingency window elapsed | TransactionDeadline.at_risk_evaluation | click: shows evaluation facts + one-click remediation task | §7.3 rule 5 |
| Timeline-anomaly badge | stage duration > 2σ above tenant historical median (same side+stage) | TransactionRecord.timeline_anomaly_flag | operational review flag only — links to review task | §7.3 rule 6 |
| **Tasks tab** — task cards | title, description, due, owner lane (CLIENT/TC/AGENT/EXTERNAL/APPROVAL/DOCUMENT_GAP/DEADLINE_RISK/BOOKING_REQUEST/SECURITY_REVIEW), status | TransactionTask (§6.8) | open, complete, reassign; "not your court" grey state for TC-owned | §6.8; draft Screen 15 |
| 29-task checklist | full canonical checklist per side, grouped by stage | TransactionTask templates | check off; gaps auto-create DOCUMENT_GAP tasks | matrix per_page (29-task checklist); [BEST GUESS] grouping by stage |
| CR pre-filled form button ("Open CR-1") | contingency-removal draft prepared by Wattson, human sends | OfficialFormProvider (§8.3) | opens form review; if provider unconfigured → OFFICIAL_FORM_PROVIDER_NOT_CONFIGURED blocking state | §8.3 fail-closed |
| Signature cards ("Your signatures — 2") | DocuSign envelopes pending for the staff user | DocumentVersion.docusign_envelope_id, SignatureStatus | "Sign" → DocuSign; status PENDING/SIGNED/VOIDED/DECLINED | §6.9 |
| **Re-cascade diff banner** | "lender slipped 2 days → close Jul 25→27. 7 tasks re-derived, 2 now overdue, buyer notification drafted" | relative-date task chaining engine | "Review diff & accept" — NOTHING moves until acknowledged | draft Screen 15 (locked decision) |
| **Wire quarantine banner** | wire doc received, quarantined pending 6-gate security review; never exposed to portal | HIGH_SECURITY_WIRE doc + §13.4 gates | "Security review →" opens the security review queue; SECURITY_REVIEW task auto-created | §13.4 |
| Wattson nudge annotations | "Wattson nudged lender 8:10am, escalates to you 2pm" | Wattson task catalog via one-approval architecture | none (informational); escalation creates AGENT_ACTION task | §10.3–10.4 |
| **Parties tab** | 12 roles (BUYER…OTHER), contact/org/email/phone, portal_access_allowed toggle, document_access_scope per security class | TransactionParty (§6.6) | scoped invite (sends magic link via NotificationProvider — REVIEW_REQUIRED); edit scope | §6.6, §11.1 |
| **Documents tab** — doc list | type (21 DocumentTypes), security class badge (PUBLIC_MARKETING…HIGH_SECURITY_WIRE), version count, signature status, classification confidence | TransactionDocument (§6.9) | open (access logged), upload version, review classification, thread notes on doc | §6.9, §8.5–8.6 |
| 6 intake pathways card | DocuSign webhook, manual upload, email forward (per-transaction address e.g. `42cedar@docs.propertyiq.app`), client portal upload, GHL attachment, Drive link | DocumentSource enum | copy email address; view intake log | §6.2 DocumentSource, §8.2; draft Screen 15 |
| Classification review queue chip | "1 in classification review" — docs where human_confirmed=false or confidence low | DocumentClassification | confirm/re-classify; detected_sensitive_topic → human_handoff_required | §6.9 |
| Document state machine chips | needed → uploaded → in-review → approved/returned; returned jumps to top of Today | doc status + task linkage | approve/return with threaded note | draft Screen 15 (locked decision) |
| Submission gates panel | per-brokerage required-doc gate before stage advance | brokerage config | blocked stage advance names missing docs | draft Screen 15 (SkySlope pattern); [BEST GUESS] gate config lives in brokerage admin settings |
| **Offers tab** | multi-offer ranking matrix, net sheet, seller presentation export | offer records + offer-analyzer skill logic | side-by-side compare, strongest-offer highlights, export (client send = REVIEW_REQUIRED via Outbox) | matrix gap "Offer analysis tab" |
| **Disclosures tab** | disclosed-vs-found cross-reference table grouped by severity; flag count in tab label | disclosure-analyzer output over DISCLOSURE_TDS/SPQ/AVID + INSPECTION_REPORT docs | open flag detail; "credit-request draft ready → your review" (never auto-sent) | matrix gap "disclosure analyzer + credit-request drafting"; draft Screen 15 |
| Disclosure auto-pull report | on offer accepted, Wattson pulls disclosure package + red-flag summary | Wattson MLS playbook | attach to transaction; review | matrix (Wattson MLS playbook surfaces) |
| **Timeline tab** | all TransactionDeadlines: type, due date, status (8 DeadlineStatus values), rule source, extension lineage; human-approval state for the generated timeline | TransactionDeadline (§6.7); DeadlineRuleProvider + RegionProfile | approve generated timeline (mandatory before client-facing, §7.3 rule 3); mark complete/waive; request extension (Wattson drafts, human approves — §7.3 rule 7) | §7.3 |
| Drop-the-contract intake | drag a contract PDF → Wattson extracts parties/financials/dates (incl. relative dates computed against state rules + holidays) → mandatory human review of EVERY date, source doc pinned as provenance | Wattson extraction (redacted layer §10.2) + DeadlineRuleProvider | confirm/edit each extracted date before binding | draft Screen 15 (locked decision) |
| **Activity tab** | append-only activity log: milestones, stage moves, task events, approval decisions | Event Ledger (TRANSACTION_MILESTONE etc.) | filter by type; sensitive/security events NOT shown here (separate security audit log, §13.5) | §13.5, §15 |
| Right-rail: portal status card | client views this week, milestone video watch counts, next weekly update draft date (review-first), Homeowner-Hub-at-close note | PORTAL_VIEWED events; WeeklyListingUpdateEmbed | link to portal preview | §9.6; draft Screen 15 |
| Close wizard button | launches the 13-step close flow: validate close_date, deal_value, commission entry (manual, §12.4), compile source_facts, case-study facts (nullable, never fabricated), emit events, archive, portal→HOMEOWNER | §12.3 checklist | step-by-step wizard; human confirmation required before archive marked complete (§8.7) | §12.3, §12.4, §8.7 |
| Empty states | new transaction: stepper at stage 1, task list seeded from checklist template, docs empty with intake instructions | — | — | [BEST GUESS] |

## States
- **Default:** Tasks tab, priority-ordered.
- **Loading:** skeleton stepper + card placeholders; target <1s record load (draft Screen 14 KPI applied here too — [BEST GUESS]).
- **Empty:** freshly auto-created transaction shows seeded checklist + "forward docs to {address}@docs.propertyiq.app" card.
- **Creation failure (fail-closed):** missing contact_id/property_id → NO transaction; a PropFlow human review task is created instead (§7.1). Duplicate → opens existing transaction.
- **Error/degraded:** OfficialFormProvider unconfigured → form actions disabled with OFFICIAL_FORM_PROVIDER_NOT_CONFIGURED. ESign provider down → signature cards show retry + manual-upload fallback. Wire gates not all true → quarantine (never partial display). ScoringService down → any displayed score disappears entirely (no local computation, §14).
- **Permission-limited:** brokerage admin sees read-only + compliance surfaces; parties without document_access_scope for a class never see those docs listed; staff access to portal data is STAFF_SESSION.
- **Mobile:** as in Layout; re-cascade and wire banners never collapsed.

## Data fields
TransactionRecord: transaction_id, side, status (6 values), current_stage (7), contract_date, close_date_target, close_date, deal_value, commission_gross_estimate/actual (USD MoneyAmount), at_risk_flag, timeline_anomaly_flag, next_deadline_id, attribution set (originating_content_id, campaign_id, lead_source, capture/conversion_source — display-only, nullable, never inferred). PropertySnapshot: MLS whitelist fields only (mls_listing_id, listing_status, list/close price, beds, baths, property_type, city, zip, mls_retention_expires_at). Deadlines: type, label, due_date (ISO), region_code, status, alert_offsets_days, at_risk_evaluation. Tasks: type, title, due, status (7 values). Documents: type, security_class, version, sha256, signature_status, retention_class (TRANSACTION_7Y default). Every record carries tenant_id + source_facts[] with verification_status.

## Rules & compliance
- **Fail-closed everywhere:** no contact/property → no transaction; no form provider → no forms; wire gates (all 6: legal_review_approved, wire_protocol_approved, ComplianceProfile.allows_wire_instruction_portal, feature_flag, security_audit_logging, OTP/MFA) → quarantine + SECURITY_REVIEW task + WIRE_INSTRUCTIONS_EVENT; no wire details via email/SMS/Wattson ever (§13.4).
- **Non-scoring:** deadline/risk flags are workflow state only — never update scoring, outreach priority, sensitive CRM fields, or ad audiences (§7.3 rule 8, §14).
- **Wattson boundary:** enforceWattsonBoundary blocks send_legal_document, commit_to_deadline, wire actions, raw-sensitive views at the API layer; not disableable (§10.5). One-approval batch cards, not per-micro-step popups (§10.3).
- **Sends:** PropClose never sends directly — NotificationProvider only, ComplianceProvider.check_outbound_contact() first, four consent statuses + evidence fields (§11.1–11.2). Client-facing anything routes review-first (Outbox, Screen 24).
- **PII:** masked in UI by default; reveal requires explicit action + OTP/MFA + security-audit log entry (§13.3). No raw PII/wire/doc bodies in app logs or Event Ledger.
- **MLS:** whitelist fields only; no embeddings/vector stores/AI training on MLS data (§13.6). No school data on this screen (§13.7). Imagery via ImageryProvider/Mapbox with attribution (§13.8).
- **Retention:** TRANSACTION_7Y (exceeds CA DRE 3-year minimum); SECURITY_AUDIT_7Y for wire/access logs; crypto-shred + tombstone after expiry (§13.2, §8.5).
- Timeline generated from CA RPA-style defaults must be human-approved before it becomes client-facing (§7.3 rule 3).

## Cross-links
**In:** Command Center cards, Kanban index, Approvals Inbox, Wattson chat, PIPELINE_MOVED (consumed). **Out:** Client portal (25), CRM contact (14), Security review queue, Outbox (24), Approvals Inbox (13), Underwriter (22, from property context). **Emits:** TRANSACTION_MILESTONE (12 milestone types), CLOSING_DETECTED, DEAL_CLOSED (with case_study_facts), CASE_STUDY_FACTS_AVAILABLE, REFERRAL_CLOSED, PORTAL_VIEWED (portal side), DNC_BLOCK; security log: WIRE_INSTRUCTIONS_EVENT, DOCUMENT_ACCESS_EVENT, SECURITY_ACCESS_EVENT. **Consumes:** PIPELINE_MOVED, NOTIFICATION_QUEUED/SENT/FAILED, DEAL_CLOSED (portal conversion trigger).

## Open decisions
- [DECIDE] E-sign vendor: assume DocuSign (only direct v1 vendor integration per §16); UI shows generic "signature envelope" so vendor is swappable behind ESignProvider.
- [DECIDE] Per-transaction email address format: interim design `{street-slug}@docs.propertyiq.app` as shown in draft; collision handling appends a 4-char hash. [BEST GUESS]
- [DECIDE] 29-task checklist source template: matrix cites 29; interim = CA buyer-side/seller-side template pair maintained in brokerage config, editable per deal. [BEST GUESS]
- [DECIDE] Deal-health chip formula: interim = rule list (deadline states + doc gaps + unconfirmed human updates), rendered as workflow flags; must never be presented as a score (§14).
- [DECIDE] Offer tab computation home: offer ranking math runs in the offer-analyzer service (skills library), not PropClose-local, to respect non-scoring; PropClose displays results. [BEST GUESS]
