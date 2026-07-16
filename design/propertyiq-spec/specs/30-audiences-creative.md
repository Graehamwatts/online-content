# 30 · Audience Builder + Creative Library (PropReach)

**Purpose.** The two governed inventories every campaign draws from. Audiences: every segment carries its compliance evidence — raw vs after-compliance counts, attestation trail, match-size preflight — and nothing uploads without passing. Creatives: governed assets with release/legal/fatigue/compliance states, persuasion metadata, and the generators (listing-to-ads, QR packs, case-study recycling).

**Primary users.** Agent/owner; marketing/content team member for creative curation. Sharon-class list manager for farm lists [BEST GUESS on role].

**Entry points.** Left-nav "Audiences & creative"; campaign wizard step 4 (audience picker) and step 8 (creative picker) open focused pickers of this screen; PropSearch "save as segment" (`+ From PropSearch`); listing detail "Generate ads"; Creative Library links from Content Flow assets.

**Exit points.** "Use in campaign" → Campaign Manager wizard (18); attestation modal → Approvals record; blocked purchased list → consent-capture task (PropFlow review queue); LEGAL_BLOCKED template → request-legal-approval flow → Approvals; QR pack → print/export + scan analytics on Attribution (31); fatigue rotation → variant request to PropCast (CONTENT_VARIANT_CREATED).

## Layout

**Desktop.** Header: counts ("6 segments · 34 released assets"), actions `+ Segment`, `+ From PropSearch`. Two-column split (per draft): **left = Audiences** (segment cards stacked; blocked items warn-styled), **right = Creative** (governed asset grid with status badges + Generators panel). Asset click → right-side detail drawer (release status, license flags, personalization level, performance history, lock lineage). Segment click → detail drawer (membership counts, compliance trail, sources, suppressions).

**Mobile (375px).** Tabs "Audiences" / "Creative" replace the split. Cards full-width; drawers become full-screen sheets; generators collapse to an action list.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Segment card | name, source_type (GEOGRAPHIC / FIRST_PARTY_CONTACTS / OWNED_ENGAGEMENT / WEBSITE_VISITORS / PROPCAST_ENGAGEMENT / GOOGLE_CUSTOM_SEGMENT / PURCHASED_LIST_SEED / PROPSEARCH_SEGMENT), targeting_method, platform_targets, geo codes + market level; counts line: "Raw 412 → after compliance 388 (24 suppressed: DNC/opt-out/in-escrow)"; attestation ✓; match preflight "388 ≥ 100 ✓" | AudienceSegment | open drawer; Use in campaign; refresh; archive | PropReach MB §8.2, §8.3; draft s30 |
| Compliance trail (drawer) | compliance_check_id, audience_list_service_check_id, source_facts[], contains_imported_or_purchased_contacts, imported_contacts_defaulted_to_unknown_consent, raw_member_file_retention_policy (DO_NOT_STORE / TEMPORARY_SECURE_PROCESSING — raw member files are not kept) | AudienceSegment | read-only audit view | MB §8.3 |
| Attestation modal | required for Meta housing Customer List uploads: attestation_text, protected_data_not_used checkbox, attested_by/at, platform; upload hard-blocks without it | CustomerListAttestation | sign → logged; visible on card as ✓ | MB §8.4, §6.1 |
| Match-size preflight badge | Google/YouTube Customer Match: <100 matched = BLOCK upload; <500 = WARN + fallback recommendations (owned engagement, website retargeting, compliant custom segment, owner-approved list growth) | AudienceListService (GOOGLE_CUSTOMER_MATCH_MIN=100, WARN_IF_UNDER=500) | view fallback options | MB §8.5 |
| Retargeting source builder | allowed sources only: LINK_SCANNED, PAGE_VIEWED, CONTENT_VIEWED, ORGANIC_VIDEO_VIEWED, FORM_STARTED-without-LEAD_CAPTURED (windowed), owned landing pages, PropCast engagement — with GPC/DNT/opt-out respected note | event ledger sources | pick sources + window | MB §8.6 |
| Purchased-list consent wall card | blocked state citing the exact rule: no documented opt-in → direct-mail only, never digital upload; consent defaults unknown; DNC/consent/opt-out/ComplianceProfile must pass before any outreach eligibility; first-party-origin platform rules | ComplianceProfile + list import | view rule; route to consent-capture tasks | MB §8.9, §2.5; draft s30 |
| PropSearch segment picker | import saved-search/filter cohorts as segments; refresh cadence ("refreshes nightly") | PROPSEARCH_SEGMENT supply | import; schedule refresh | MB §8.2; draft s30 |
| Suppression settings | pre-upload membership filtering (never platform exclusions for Meta housing); reporting-only "don't spend against" recommendations | suppression config | edit lists | MB §8.7 |
| Google competitor-intent segment builder | Display/YouTube only; requires 5–10 related URLs/terms; "intent approximation — never claims a named person visited Zillow/Redfin/etc."; forbidden-inputs list enforced | segment config | build; honesty label non-removable | MB §8.8 |
| List Builder import | matching order: exact address → exact phone → exact email → probabilistic = human review only; phone/email conflict → review task, never auto-merge; net-new contacts via /approved-leads | GHL-now contacts + imports | upload; review conflicts | MB §8.10 |
| Creative asset tile | thumbnail, asset_type (VIDEO/IMAGE/CAROUSEL/COPY/PDF/LANDING_PAGE_VARIANT/AD_VARIANT), status badge: ACTIVE / TESTING / FATIGUE_FLAGGED / RETIRED / LEGAL_BLOCKED / COMPLIANCE_BLOCKED / DRAFT_ONLY; personalization chip (AREA_LEVEL / CONTACT_PII / PROPERTY_SPECIFIC / OWNER_SPECIFIC); AI-generated flag + disclosure-required | CreativeAsset | open drawer; use in campaign (RELEASED/ACTIVE only) | MB §9.2; draft s30 |
| Asset drawer | asset_url/sha256, originating_content_id + variant_id lineage, allowed_platforms, campaign_objectives, release_record_ids, license_flags (provider MAPBOX/GOOGLE_EARTH/ZILLOW/IDX/MLS/CLIENT_OWNED/MANUAL_RELEASE; status APPROVED/BLOCKED/LEGAL_APPROVAL_REQUIRED/ATTRIBUTION_REQUIRED/RETENTION_LIMITED), compliance_check_id, legal approval status, copy metadata (awareness_stage, lever, framework, failure_audit_result) | CreativeAsset + copy_variant_metadata | request legal approval; request variant | MB §9.2, §9.3, §18.7 |
| Fatigue flag + rotation card | "freq 4.1 → rotation suggested"; deterministic from frequency/CTR/conv-rate; alert hints Meta ~3.0 imp/person/wk, YouTube ~2.0 (account-configurable, not hard gates); never auto-pauses spend unless envelope allows | platform facts | accept rotation → variant request; dismiss | MB §9.5; draft s30 |
| ReleaseRecord gate indicator | client face/voice/name/testimonial assets show release status (release_id, scope, signed_at, expires_at); missing → hard-blocked from ads | ReleaseRecord | view evidence_url; request release | MB §9.6, §10.6 |
| Zestimate template lock | LEGAL_BLOCKED until human legal approval logged; third-party attribution required; safe generic fallback concept offered ("online estimates can miss local context") | template config | request legal approval | MB §11.4; draft s30 |
| ADU claim-ladder chip | L-affirmative (confidence ≥0.80 + jurisdiction covered) / cautious (0.60–0.80) / suppressed (<0.60 or uncovered); shows zoning_source + last_checked | Zoneomics fields via PropSearch | view ladder rationale | MB §11.5; draft "claim-ladder L2 (permitted-use verified)" |
| Listing-to-ads generator | template picker: LISTING_SELLER_AD / LISTING_BRAND_AD / LISTING_POSTCARD / CASE_STUDY_SELLER_AD / CASE_STUDY_TESTIMONIAL_AD; per-template rules enforced (GEOGRAPHIC_ONLY default, HOUSING category, current sourced listing status) | listing events + templates | generate → draft assets → campaign | MB §10.1, §10.2 |
| QR pack builder | labeled codes (sign, flyer, postcard, mailer — per-label scan analytics); every destination minted via link.propertyiq.app; scan emits LINK_SCANNED (scan_type=QR); print QR use = REVIEW_REQUIRED; room-level scans framed as low-cost experiment | Owned Link Shortener | create pack; export print files → Approvals | MB §10.3, §10.4; matrix |
| Case-study recycler | post-close ad candidates from DEAL_CLOSED case_study_facts (list_price/close_price/dom/offer_count all nullable — omit missing, never fabricate); testimonial variant hard-blocked without ReleaseRecord scope=advertising | DEAL_CLOSED + CASE_STUDY_FACTS_AVAILABLE | generate; review facts + sources | MB §10.5, §10.6 |
| Personalized-creative gate banner | CONTACT_PII/OWNER_SPECIFIC assets require marketing_personalized_consent_status=granted; failure → area-level fallback (no name/address/home-specific claim) | ComplianceProfile | view gate result | MB §11.2, §11.7 |
| Mapbox imagery badge | licensed-imagery assets carry non-removable attribution ("© Mapbox © OpenStreetMap"); Google Earth blocked v1; no map tiles into AI render pipelines | license_flags | read-only | MB §11.6 |
| Empty states | Audiences: "No segments — start from your farm geography or a PropSearch search." Creative: "Approved content and generated ads land here." | — | CTAs | [BEST GUESS] |

## States

- **Default / Loading:** skeleton cards/tiles; counts show dashes.
- **Empty:** per-column empty states above.
- **Error/degraded (fail-closed):** AudienceListService unreachable → uploads disabled with LIST_TOO_SMALL-style flag pending check (no upload without preflight); ComplianceProvider down → segment creation and asset release actions disabled, existing records read-only; Zoneomics fields stale/missing → ADU claims render suppressed; membership counts unknown → "counts pending", upload blocked.
- **Permission-limited:** attestation signing and legal-approval requests restricted to owner/admin; team can build drafts.
- **Mobile:** tabbed, per Layout.

## Data fields

AudienceSegment (full schema §8.3) incl. member_count_raw / member_count_after_compliance / estimated_matched_users (nullable → "pending"); CustomerListAttestation; CreativeAsset (full schema §9.2) incl. asset_sha256, ai_generated_or_ai_modified, ai_disclosure_required; LicenseFlag; ReleaseRecord (release_id, contact_id, clip_ids[], release_scope, evidence_url, signed_at, expires_at); Zoneomics: zoning_confidence (0–1, 2dp), jurisdiction_covered, zoning_source, zoning_last_checked_at; QR scan counts per label (int). Suppressed-count breakdown by reason (DNC / opt-out / in-escrow per draft).

## Rules & compliance

- **Attestation hard block** (§8.4); **match minimums** 100/500 (§8.5); **no platform exclusions for Meta housing** — filter membership pre-upload (§8.7).
- **Sensitive-topic firewall:** no divorce/probate/health/protected-class/etc. signals in any segment input or custom-segment term; forbidden-inputs list rendered in the competitor-segment builder (§8.8, §12.3).
- **School data never targets** — no school inputs to audiences (§12.1).
- **Copy Persuasion Standard** applies to every generated ad copy asset: one dominant lever, failure audit, hard line "persuasion never manipulation" (no fabricated urgency/scarcity, no "great schools", no family-status framing); override order Compliance > brand voice > copy diagnosis (§9.4).
- **ReleaseRecord absolute rule** (§9.6). **Zestimate legal lock** (§11.4). **ADU Zoneomics ladder** (§11.5). **Area-level fallback** on any failed gate (§11.7).
- **Raw member files never stored** beyond temporary secure processing (§8.3).

## Cross-links

In: PropSearch (segment supply, zoning facts, generated assets), PropCast (variants, engagement audiences), listing records, PropFlow/GHL contacts (read-only via adapter — PropReach never becomes contact system of record, §2.1). Out: Campaign Manager (18) pickers; Approvals (attestations, legal approvals, print QR); Attribution (31) per-label scan analytics; PropFlow review queue (consent-capture, merge conflicts). **Ledger:** consumes LINK_SCANNED, PAGE_VIEWED, CONTENT_VIEWED, ORGANIC_VIDEO_VIEWED, FORM_STARTED, DEAL_CLOSED, CASE_STUDY_FACTS_AVAILABLE, RELEASE_RECORD_CREATED; causes CONTENT_VARIANT_CREATED (via PropCast on variant request); audience/creative records carry compliance_check_ids for audit.

## Open decisions

- [DECIDE] Segment refresh cadence: interim = nightly for PROPSEARCH_SEGMENT (per draft), manual refresh elsewhere.
- [DECIDE] Whether the QR pack builder also lives on listing detail: interim = yes, same component, library is the archive.
- [DECIDE] Fatigue thresholds surfaced as editable account settings vs fixed hints: interim = editable in Settings, defaults Meta 3.0 / YT 2.0 per MB §9.5.
- [DECIDE] Personalized-video creative rows (BHUMAN primary / LIPDUB backup, HeyGen for broadcast — MB §11.1): interim = they appear as VIDEO assets with personalization=CONTACT_PII and the §11.3 gate chip; vendor choice does not affect UI.
