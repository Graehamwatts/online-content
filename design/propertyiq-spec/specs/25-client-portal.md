# 25 · Client Portal / Homeowner Hub

**Purpose:** The one durable, agent-branded URL a client keeps for the whole relationship: LISTING (weekly seller dashboard / owner page, Screen 10) → TRANSACTION mode (this screen's primary view) → HOMEOWNER HUB at close. It exists to reduce client anxiety and "where are we?" calls — simple enough for a stressed buyer or seller to use without instructions (PropClose §9.1). Hosted at portal.propertyiq.app (§9.2).

**Primary users:** Buyer/seller clients (contact_ids on the PortalRecord). Staff view the same data inside the PropClose admin app (STAFF_SESSION), never through client links.

**Entry points:** Magic-link email/SMS invite (sent via NotificationProvider, consent-checked) · returning direct URL (re-issues magic link) · milestone notification links · Monday doorway email (listing mode) · QR/short links are FORBIDDEN for auth — sensitive portal links never use link.propertyiq.app (§9.2).

**Exit points:** DocuSign signing ceremony (after OTP step-up) · document download (step-up if sensitive) · message thread (routes to PropFlow inbox) · referral CTA → PropFlow referral intake (homeowner mode) · underwriter/equity deep links (homeowner mode) · nothing exits to staff surfaces.

## Layout

**Desktop:**
- **Header:** agent avatar + agent name (branding_ref resolved from identity config — pilot: Graeham Watts, DRE 01466876, Intero Real Estate, §9.3), context subtitle ("Your home purchase · 42 Cedar St"), nav: Messages (badge), Docs.
- **Hero card:** progress statement ("You're on day 11 of 21 — on track for keys July 25 🔑") + a 6-segment client-language stage strip (Offer accepted / Deposit in / Inspection / Loan — this week / Signing / Keys!). Client-friendly labels map to the 7 canonical stages; current stage outlined, complete filled.
- **Three-card row:** "Your to-dos" (client tasks) · "From {agent}" (milestone video/messages) · "Documents" (shared count, signature needs, wire warning).
- **Below (12 sections as enabled):** status, tasks, docs, upload, messages, milestones, showing feedback, weekly update embed, settings — per transaction_sections_enabled (§6.11 PortalSection enum).
- **Footer:** licensed identity block (agent name, DRE, brokerage — exact brand-lock match) + "Powered by PropertyIQ".

**Mobile (375px):** single column; hero stage strip horizontally scrollable; to-dos first (action bias); sticky bottom bar: Messages · Docs · To-dos. Everything tap-target ≥44px; zero instructions needed.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Magic-link login | passwordless entry; link consumed once, expiring | PortalAccessGrant (auth_method MAGIC_LINK, issued/expires/consumed_at, ip_hash, ua_hash, risk_flags) | request new link; risk_flags may force step-up | §6.11, §9.4 |
| OTP/MFA step-up modal | re-verifies before ANY sensitive action: signing, downloading sensitive docs, wire-related info, security/personal settings changes | PortalAuthLevel MAGIC_LINK→OTP_VERIFIED/MFA_VERIFIED | enter code; failure locks action, never degrades | §9.4 |
| Agent-branded header/footer | name, photo, DRE, brokerage exactly from identity configuration | branding_ref → identity.json (pilot DRE 01466876) | none — read-only, brand-locked | §9.3 |
| Stage strip (TRANSACTION_STATUS) | client-language progress: 6 segments incl. "Keys!" | TransactionRecord.current_stage mapped | none | §9.5; draft Screen 25 |
| Day/close counter | "day 11 of 21 — keys July 25" | contract_date, close_date_target | none; re-cascade updates only after staff acknowledgment (Screen 15) | §6.5 |
| MY_TASKS card | client to-dos ("upload insurance quote", "confirm walkthrough time — 2 taps") | TransactionTask where assigned_to_contact_id, type CLIENT_ACTION | complete inline; booking confirm = 2-tap (BOOKING_REQUEST_TASK, no AI auto-booking §11.6) | §6.8, §11.6 |
| DOCUMENTS section | docs shared with this contact per DocumentAccessPolicy; signature-needed badges | TransactionDocument filtered by allowed_contact_ids + security class scope | view (DOCUMENT_ACCESS_EVENT logged), download if download_allowed, watermark if watermark_required; sensitive = OTP step-up first | §6.9, §8.6, §13.3 |
| UPLOAD section | client uploads docs into intake pathway CLIENT_PORTAL_UPLOAD | DocumentSource | drag/tap upload → classification queue on staff side | §8.2 |
| MESSAGES section | thread with the agent; routes to PropFlow conversation layer | PortalMessageToPropFlow (capture_source PORTAL, capture_provider PROPERTYIQ_FORM) | send text + attach shared docs; sensitive-topic content → human_handoff_required only, no automation | §11.5 |
| MILESTONES section | milestone feed ("Deposit is in") + personalized video ("From Graeham" 0:48, watched ✓) | TRANSACTION_MILESTONE events; PropFlow personalized-video system | play (watch tracked); AI video gated on ai_video consent + REVIEW_REQUIRED default + non-removable CA AI disclosure frame one | §15.5; matrix correction #3 |
| **Wire-safety warning** | permanent notice: "wire details are NEVER posted here — verified callback only, beware lookalike emails" | static, always-on in Documents card | none | §13.4; draft Screen 25 |
| SHOWING_FEEDBACK section (sell side) | verbatim showing feedback | WeeklyListingUpdateEmbed payload | none | §9.5, §9.6 |
| WEEKLY_LISTING_UPDATE embed (sell side / listing mode) | PropCast-produced weekly seller dashboard (Screen 10 in listing-performance mode) | WeeklyListingUpdateEmbed (weekly_listing_update.v1) | authenticated view only; emits PORTAL_VIEWED; if unavailable → section hidden + staff task, never stale/fabricated | §9.6 |
| SETTINGS section | contact prefs, notification channels; security changes = step-up | PortalRecord, consent fields | edit (OTP for security items) | §9.4, §9.5 |
| DocuSign signing entry | "2 need signatures" | SignatureStatus PENDING | step-up → signing ceremony | §6.9, §9.4 |
| **Homeowner Hub (post-close mode):** close summary | what closed, when | TransactionRecord post-DEAL_CLOSED | none | §9.7 |
| Home anniversary card | anniversary from close_date/home_anniversary_date | close fields (synced to PropFlow §12.3 step 13) | none | §9.7 |
| Equity card | PropSearch EQUITY_CARD, labeled ESTIMATE; requires known mortgage balance else manual-entry prompt (MISSING_MORTGAGE_BALANCE) — never fabricated | PropSearch (PropClose computes nothing locally) | update-my-info | §9.7; matrix correction #7 |
| Annual CMA surface | CMA delivery when PropFlow/PropSearch exposes it | PropFlow/PropSearch | view/request | §9.7 |
| Referral CTA | routes to PropFlow referral intake | PropFlow | tap → referral form | §9.7 |
| Past-client touch log | display if PropFlow exposes it (cadence owned by PropFlow/Wattson, never PropClose) | PropFlow | none | §9.7 |
| "Same link forever" note | tells client this page becomes the Homeowner Hub at close | static | none | draft Screen 25 |
| Access status handling | INVITED/ACTIVE/SUSPENDED/ARCHIVED | PortalRecord.access_status | SUSPENDED/ARCHIVED → polite closed-door page with agent contact | §6.11 |

## States
- **Default (TRANSACTION mode):** hero + three cards + enabled sections.
- **Listing mode (pre-contract, sell side):** the portal surface IS the Screen 10 owner/seller page — one artifact, one URL (matrix correction #8).
- **Homeowner mode (post-close):** flips automatically on DEAL_CLOSED (§9.7); homeowner_sections_enabled control visibility.
- **Loading:** branded skeleton; hero renders first.
- **Empty:** newly invited client sees hero + "nothing needed from you right now."
- **Error/degraded (fail-closed):** weekly-update embed unavailable → section hidden + staff task; equity without mortgage balance → "estimate unavailable" + manual-entry prompt; document service down → list without download; wire info → never rendered under any failure.
- **Permission-limited:** every doc filtered by per_document_permissions; sections not in *_sections_enabled don't render at all; multiple contacts on one portal each see their own task/doc scope.
- **Auth-expired:** consumed/expired magic link → "send me a new link" screen.
- **Mobile:** per Layout.

## Data fields
PortalRecord: portal_id, mode (TRANSACTION|HOMEOWNER), branding_ref, portal_url, access_status, magic_link_enabled=true, sensitive_actions_require_otp_mfa=true, sections enabled arrays, per_document_permissions. PortalAccessGrant: auth_method, auth_level, issued/expires/consumed_at, ip_hash, user_agent_hash, risk_flags. Client-visible transaction fields: stage (mapped label), dates, client tasks, shared docs (title, type label, signature state), milestones, messages. Homeowner: close summary, anniversary date, equity estimate (labeled, ranged), CMA link, referral link. No raw MLS data, no scores, no wire data, no other parties' PII — ever.

## Rules & compliance
- Two-tier auth invariant: magic_link_enabled=true and sensitive_actions_require_otp_mfa=true are hard-coded true on the record (§6.11).
- **No ad pixels** in authenticated transaction portal v1; owned-page analytics only with ComplianceProvider pass + GPC/DNT/opt-out respected (§13.10). Attribution via canonical PORTAL_VIEWED only.
- Brand lock: footer/emails/invites/doc notices show licensed identity exactly (pilot DRE 01466876, Intero) (§9.3). The identity.json-blocklisted legacy DRE must never appear.
- No Zillow/Zestimate-branded or -referencing template anywhere in PropClose v1 (§9.7).
- No school data in v1; future embed must follow the PropSearch factual-display model with no steering/CTA inside the block (§13.7; matrix correction #4).
- Sold comps: public = aggregates only; detail requires authenticated session (§13.6).
- All portal messages with sensitive topics: human_handoff_required=true, no automation (§11.5).
- Every sensitive view/download/sign → security audit log (SECURITY_AUDIT_7Y), not the marketing ledger (§13.5).
- Client-facing sends (invites, weekly updates) are review-first per the workspace-wide send policy; PropClose sends only via NotificationProvider after ComplianceProvider.check_outbound_contact() (§11.1–11.2).

## Cross-links
**In:** invites from Transaction Workspace (15) Parties tab; Monday doorway email (listing mode); milestone notifications. **Out:** PropFlow inbox (messages), PropFlow referral intake, PropSearch equity/CMA surfaces, DocuSign. **Emits:** PORTAL_VIEWED, PAGE_VIEWED (embed renderer, privacy-checked), DOCUMENT_ACCESS_EVENT + SECURITY_ACCESS_EVENT (security log), PortalMessageToPropFlow. **Consumes:** DEAL_CLOSED (mode flip), TRANSACTION_MILESTONE, WeeklyListingUpdateEmbed.

## Open decisions
- [DECIDE] OTP delivery channel: interim = SMS if sms_consent granted, else email; configurable via ComplianceProfile security policy (§9.4 says defaults are configurable). [BEST GUESS]
- [DECIDE] Magic-link TTL: launch default 7 days for invites / 15 minutes for re-auth links. [BEST GUESS — §9.4 defers to security policy]
- [DECIDE] Milestone video vendor: assume HeyGen-class avatar API (LipDub/BeHuman candidates) — UI unaffected by vendor choice; consent + disclosure gating fixed regardless.
- [DECIDE] Multiple-transaction clients: interim = one portal per transaction, with the homeowner hub of the primary residence as the durable long-term URL. [BEST GUESS]
