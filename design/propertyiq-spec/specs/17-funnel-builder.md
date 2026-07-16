# 17 · Funnel Page & Lead-Magnet Builder (PropCast/PropReach)

**Purpose** — Builds the owned capture layer behind every piece of content: pick a container from the container-type matrix (13 rows in the current build: keyword → landing page → lead-magnet PDF), the page + PDF + DM flow generate together from real data, the agent edits slots, and publishing routes through Approvals. Also home of the system-wide "⚡ Create funnel" easy button and the UTM auto-scheme.

**Primary users** — Agent; marketing coordinator role (edit); Wattson (proposes funnels via recommendations — e.g. "3 listings have no funnel yet").

**Entry points** — "⚡ Create funnel" on ANY content object anywhere (video, script, listing, carousel, news card) — opens the builder pre-filled; "My pages" nav; Content Review bundle build (Tab 16) when a piece's container needs manual editing; Wattson recommendation card one-click create; Campaign Manager (Tab 18) "landing destination missing" fix path.

**Exit points** — Publish → Approvals (Tab 13) → hosted at agent subdomain (Cloudflare Pages/Vercel); Attach to campaign → Campaign Manager (Tab 18); "⚡ Create content for this page" (reverse button) → content engine; page's SEO handoff → SEO console; leads captured → PropFlow CRM contact records.

## Layout

**Desktop**
- **Header**: "New funnel page · Step 2 of 3 — container picked: {name}"; nav: My pages (n).
- **Optional hero panel** (first-run / from easy-button): the ⚡ explainer + UTM auto-scheme + closed-loop cards (as in draft — inherit, don't remove).
- **Left rail (≈40%)**: container matrix picker (13 rows, selected highlighted, each row shows keyword → gate → PDF), Mode panel (Branded / Unbranded toggle + footer note).
- **Main (≈60%)**: live page preview with dashed editable slots (headline, subhead, form/CTA), URL + "UTM auto" strip, PDF cover preview + pixel/footer status line, footer action bar (Publish → Approvals · Attach to campaign).

**Mobile (375px)** — Steps become a vertical wizard: 1) container list (full-width cards), 2) mode, 3) preview (page renders at true mobile width — this IS the visitor's view), 4) sticky Publish bar. Slot editing via bottom-sheet forms.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| ⚡ Create funnel (global button) | On every content object; engine picks matching container (listing video→tour gate, market video→report capture, ADU script→checklist magnet), pre-fills headline/geo/CTA from the content's own facts, inherits ContentLock lineage, opens builder filled for 30-second edit-and-publish | ContentLock + content facts | One click → this screen pre-filled | draft s17 easy-button (inherited ~37-iteration decision) |
| Reverse button | "⚡ Create content for this page" on any funnel page | funnel page record | Click → content engine brief | draft s17 |
| Container matrix picker | 13 selectable container templates; each row: content type/keyword intent → landing page style → lead magnet template (e.g. "what's my home worth in {area}" → valuation gate → Pricing Guide PDF; Listing tour gate; Open house RSVP; Buyer guide; ADU checklist; Relocation kit; Investor yield report; City Guide; …) | Container Type Matrix (Master Brain Part 9) — matrix is canonical; 13-row count per matrix JSON gap item | Select row → regenerates preview + PDF + DM keyword | Master Brain Part 9 §Container Type Matrix; matrix gap "13-row container matrix" P0 |
| Mode toggle | Branded / Unbranded (teaser ads): unbranded strips the agent hero for portal-style ad compliance; DRE/brokerage footer stays on BOTH, non-removable | campaign context | Toggle → preview swaps | draft s17 (inherited) |
| Headline slot | Auto-derived from the video title; one-click edit | container generation | Click → inline edit | Master Brain Part 9 §Landing Page (verbatim: "Headline auto-derived from the video title (one-click edit)") |
| Subhead slot | References topic + geography, auto-filled from live data ("East Palo Alto market data — updated {Month}") | Stage-2 signal data (MLS stats, news pull) via PropSearch data floor | Click → edit | Master Brain Part 9 |
| Hero video embed | YouTube or hosted MP4 of the parent content | ContentLock render artifact | Swap/remove | Master Brain Part 9 |
| Lead capture form / CTA section | Container-appropriate gate (address field for valuation; name+email+phone+buyer/agent toggle for disclosure gates) | container template | Edit CTA copy | Master Brain Part 9 + Listing Property Page section |
| Locked footer | Agent name · license number · brokerage · NAR Fair Housing logo — pulled from identity configuration, read-only | identity.json / tenant identity config | None (locked) | Master Brain Part 9 (verbatim); Skills CLAUDE.md brand rule |
| Lead magnet PDF preview | First-page preview; template per container matrix; auto-populated with real Stage-2 data; agent branding (headshot, license, brokerage) | PDF generator (ReportLab/WeasyPrint per MVP1) | Click → PDF slot editor | Master Brain Part 9 §Lead Magnet PDF |
| Local Business Partner slot | City Guide containers only: one merchant deal/coupon per guide per city, filled at onboarding, persists until updated | agent config | Edit slot | Master Brain Part 9 (City Guide rule) |
| Comment-DM flow summary | Keyword (auto-assigned per container type), DM copy ("Hey [first name]! Here's your [lead magnet] → [short link]" + 48h follow-up if unopened), CRM tag propcast_[content_type]_[geo] | CommentDmProvider config (staged: GHL messenger interim → ManyChat → native) | Edit DM copy (re-gates) | Master Brain Part 9 §Comment-DM Flow |
| Pixel/CAPI status line | Meta Pixel + GA4 (+ TikTok pixel) auto-injected — shown as status, not configurable | platform tracking config | Hover → pixel IDs | Master Brain Part 9; draft s17 |
| URL + UTM strip | propertyiq.app/f/{slug} (or agent subdomain) + "UTM auto" badge; scheme: utm_source={platform} · utm_medium={organic\|paid\|email\|print\|qr} · utm_campaign={contentlock-id} · utm_content={variant} · utm_term={audience-segment}; generated at publish per destination, enforced by distribution (a link can't ship without them) | owned link shortener + ledger mapping | Copy link | draft s17 UTM card (inherited); Master Brain Part 14 |
| Publish → Approvals | Publishes only through the approval gate; container copy is public-facing creative → drafted before Gate 2, frozen in ContentLock | ApprovalRecord + ContentLock | Click → Tab 13 card | Master Brain Part 9 container logic |
| Attach to campaign | Links page as a campaign's landing destination | PropReach campaign record | Picker | draft s17; PropReach preflight (landing page live ✓) |
| My pages list | All funnel pages: status (draft/pending approval/live), container type, leads captured, parent content, campaign links | funnel page records + ledger | Open/edit/duplicate/retire | matrix new_screens "Funnel Page & Lead Magnet Builder" |
| Waitlist mode indicator | Disclosure-gate pages before docs upload: page still captures requests; auto-delivers + notifies agent when docs land | listing page record | Read-only status | Master Brain Part 9 §Listing Property Page |
| Wattson recommendation surfaces | "Push these 2 to PropReach ads" (over-threshold organic) · "3 listings have no funnel yet" (one-click create) · "clicks but no leads — swap the magnet" | Wattson recommendations queue; ledger analytics | One-click apply (spend items route to Approvals) | draft s17 loop card (inherited) |
| Lifestyle/AEO container fields | City guides & lifestyle pages: FAQPage + LocalBusiness JSON-LD, visible last-updated timestamp, instant-indexing on publish, source attributions | AEO schema section; PropSearch data floor | Read-only compliance panel | Master Brain Part 9 §Lifestyle & Authority Containers / AEO Schema |

## States

- **Default**: 3-step wizard (container → mode → edit/preview).
- **Pre-filled (easy button)**: all slots filled; user lands directly on step 3.
- **Loading**: page + PDF generating together — skeleton preview with "generating from {content} facts".
- **Empty (My pages)**: "No funnel pages yet — every video/listing carries ⚡ Create funnel."
- **Error/degraded (fail-closed)**: data source missing (no MLS stat for subhead) → slot renders "data unavailable" and blocks publish until edited/removed — never a fabricated number; PDF generation failure → publish blocked with typed reason; hosting deploy failure post-approval → page status DEPLOY_FAILED with retry; identity config missing → hard block (footer cannot render → nothing publishes).
- **Pending approval**: page read-only with "In Approvals" banner + link.
- **Permission-limited**: coordinator can edit slots; only approval-permitted roles see Publish enabled; footer and pixels locked for everyone.
- **Mobile**: wizard variant per Layout.

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| container_type | enum (13 values per matrix) | Container Type Matrix, assigned at Stage 2 |
| page: slug/URL, headline, subhead, hero video URL, CTA copy, mode (BRANDED/UNBRANDED) | text/URL | funnel page record; container_copy frozen in ContentLock |
| footer identity | name, DRE #, brokerage, Fair Housing logo | identity config (read-only) |
| lead magnet | template id, generated PDF URL, data snapshot + as-of date | PDF generator + Stage-2 sources |
| DM flow | keyword, dm_copy, follow-up copy, crm_tag, source field propcast_organic_[platform] | CommentDmProvider config |
| tracking | pixel ids, GA4 id, short link, UTM set | platform config + link shortener mapping (stores lock identity) |
| lock identity | content_id, content_lock_id, lock_hash, approved_version_id | ContentLock |
| lead events | LEAD_CAPTURED / LINK_SCANNED / DOC_DOWNLOADED {content_id, content_lock_id, lock_hash, approved_version_id, contact_id, container_type, timestamp} | Event Ledger (PropFlow/Platform emitters) |

## Rules & compliance

- Container copy created after lock ⇒ new approved_version_id + Gate 2 rerun + new ContentLock; the container step may build from locked fields but may never invent new public-facing copy.
- Footer (agent name, license, brokerage, NAR logo) is locked on branded AND unbranded pages; DRE always from identity config — never hand-typed (the identity.json DRE blocklist applies).
- Fair Housing gate for lifestyle containers: facts not characterizations; no best/top/worst rankings; no school-quality/demographic proxies; source attribution on every data point; "verify with the source" disclaimer; uniform availability; one-time broker/legal sign-off on the template library.
- Honest gate copy — no dark patterns; pixel disclosure + DNT/Global Privacy Control respected (Part 5 hard rules).
- Routing rule: landing page serves search/paid traffic; comment-DM serves organic social — the builder wires both from one container.
- School/boundary data (lifestyle pages) is user-initiated, identical for all users, disclaimed — no conversion CTA inside the schools block (matrix correction #4).
- No fabricated stats: every data slot carries source + as-of date or renders unavailable.

## Cross-links

In: every content object (⚡), Tab 16 bundle, Tab 18 campaigns, Wattson recs, My pages. Out: Approvals (13), Campaign Manager (18), Distribution (19), SEO console (submit page/instant indexing), Attribution (31), PropFlow (captured leads), Switchy-style owned short links + QR packs.
Ledger: consumes content facts + lock identity; page traffic emits LEAD_CAPTURED, LINK_SCANNED, DOC_DOWNLOADED with full identity key set.

## Open decisions

- **[DECIDE] Canonical 13-row list**: Master Brain defines the matrix but the converted doc renders the table empty; draft names 7 (home value, listing tour gate, open house RSVP, buyer guide, ADU checklist, relocation kit, investor yield report) + city guide + lifestyle/authority + gated disclosure. Interim: build the picker data-driven from the matrix table in the source .docx; do not hardcode.
- **[DECIDE] Hosting**: Cloudflare Pages vs Vercel (spec allows either). UI unaffected — show host + deploy status generically.
- **[DECIDE] Programmatic-page vendor**: SearchAtlas evaluate-first rule — if it covers programmatic local pages/schema/indexing, PropCast orchestrates on top; builder UI must treat renderer as swappable.
- **[BEST GUESS] Slug editing**: allow slug edit pre-publish only; post-publish the URL is durable (matches durable-URL patterns elsewhere in the platform).
