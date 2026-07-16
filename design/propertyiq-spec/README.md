# PropertyIQ Front-End Design Spec

**For:** Ramsha / QuestLab dev team · **Owner:** Graeham Watts · **Generated:** 2026-07-15

Two artifacts, use them together:

1. **[The interactive wireframe](https://graehamwatts.github.io/online-content/design/propertyiq-spec/wireframe.html)** — 37 clickable screens showing layout, hierarchy, and general look. Colors/fonts are placeholders (brand-vault theming demo via the dots top-right; system palette candidates via the 🎨 picker).
2. **The per-screen spec sheets below** — the exhaustive detail behind each screen: every element with its data source, all states (incl. fail-closed), data fields, compliance rules, cross-links/ledger events, and open decisions. Numbers come from the Master Brains; anything invented is marked **[BEST GUESS]**; undecided vendor/tech choices are marked **[DECIDE]** with an interim design.

Read the wireframe tab first, then its spec sheet. The spec is the contract; the wireframe is the picture.

| # | Screen spec |
|---|---|
| 01 | [01 · Search entry page](specs/01-search.md) |
| 02 | [02 · Results](specs/02-results.md) |
| 03 | [03 · Property detail](specs/03-property-detail.md) |
| 04 | [04 · Compare](specs/04-compare.md) |
| 05 | [05 · Agent Homepage (consumer-facing site, per-agent instance)](specs/05-agent-homepage.md) |
| 06 | [06 · Community Page (programmatic SEO template, `/{city}/{neighborhood}/`)](specs/06-community-page.md) |
| 07 | [07 · Mobile Patterns (375px system-wide adaptation spec)](specs/07-mobile.md) |
| 08 | [08 · System Map / Brand-Vault Flow](specs/08-system-map.md) |
| 09 | [09 · Command Center (Today queue + Map mode)](specs/09-command-center.md) |
| 10 | [10 · Seller Report / Owner Page (permanent per-owner live page)](specs/10-seller-report.md) |
| 11 | [11 · Competitor & Channel Intelligence](specs/11-competitor-intel.md) |
| 13 | [13 · Global Approvals Inbox](specs/13-approvals.md) |
| 14 | [14 · CRM (Contacts + Pipelines)](specs/14-crm.md) |
| 15 | [15 · Transaction Workspace (PropClose staff)](specs/15-transaction.md) |
| 16 | [16 · Content Review & Approve (PropCast)](specs/16-content-review.md) |
| 17 | [17 · Funnel Page & Lead-Magnet Builder (PropCast/PropReach)](specs/17-funnel-builder.md) |
| 18 | [18 · Campaign Manager (PropReach)](specs/18-campaigns.md) |
| 19 | [19 · Distribution Board + Content Flow](specs/19-distribution.md) |
| 20 | [20 · SEO Console (SearchAtlas / OTTO)](specs/20-seo-console.md) |
| 21 | [21 · Settings Suite & Notifications](specs/21-settings.md) |
| 22 | [22 · Underwriting Workspace](specs/22-underwriting.md) |
| 23 | [23 · Onboarding Wizard](specs/23-onboarding.md) |
| 24 | [24 · Universal Review Queue / Outbox](specs/24-outbox.md) |
| 25 | [25 · Client Portal / Homeowner Hub](specs/25-client-portal.md) |
| 26 | [26 · Saved searches & properties (consumer)](specs/26-saved.md) |
| 27 | [27 · Past Client OS](specs/27-past-clients.md) |
| 28 | [28 · Prospecting Hub (MLS playbooks + Predictive Seller)](specs/28-prospecting.md) |
| 29 | [29 · Voice Ops (Wattson)](specs/29-voice-ops.md) |
| 30 | [30 · Audience Builder + Creative Library (PropReach)](specs/30-audiences-creative.md) |
| 31 | [31 · Attribution & Analytics](specs/31-attribution.md) |
| 32 | [32 · Video Studio + Production Asset Registry](specs/32-video-studio.md) |
| 33 | [33 · Newsletter Builder + Direct Mail](specs/33-newsletter-mail.md) |
| 34 | [34 · Admin Console (PropertyIQ ops / broker tier)](specs/34-admin.md) |
| 35 | [35 · Management Module — Concept Overview (its own app shell)](specs/35-management.md) |
| 36 | [36 · Ideation Canvas + News-to-Post Queue (PropCast, P2)](specs/36-canvas-news.md) |
| 37 | [37 · Investor Watch + Metered Scans](specs/37-investor-watch.md) |

**Note:** Tab 12 (capability matrix) is a project-management view, not a build screen — no spec sheet. Source of truth for capabilities: the PropertyIQ Capability Matrix (2026-07-15) in Graeham's vault.
