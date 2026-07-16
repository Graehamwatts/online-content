# 08 · System Map / Brand-Vault Flow

**Purpose.** The "how it all fits together" screen — an internal/dev-and-sales artifact, not a consumer or daily-agent surface. Three sections: (A) the page mesh — every arrow is simultaneously a user path and an internal-link/SEO crawl path; (B) the brand-vault onboarding flow — how one locked layout becomes each agent's branded instance in under 3 minutes; (C) the full page inventory with design status — the honest checklist of what exists vs. what's next.

**Primary users.** Dev team (Ramsha's team building from specs) · product owner (Graeham) · sales/demo use (explaining the product architecture) · designers picking the next screen. Not shown to agents or consumers in production — this is a documentation/architecture view. [BEST GUESS: ships in the product as an internal "/system" route behind Admin role, and in the design draft as Tab 8.]

**Entry points.** Draft tab bar "8 · System map" · Onboarding Wizard step 8 links INTO flow B (the brand-vault scan is executed there; Tab 8 documents it) · Screen 23 (Onboarding wizard) references "brand vault (Tab 8 flow)" · Screen 21 Settings ("identity locked from the brand vault") references it · demo script.

**Exit points.** Mesh nodes link to their designed tabs (1–6, 9–11) · inventory Status column links to each tab or flags "next" · flow B step 5 "Evolve" → Settings→Brand (re-scan) and premium-template upsell · matrix tab (12) for the capability-level version of section C.

## Layout

**Desktop.** Single scrolling document page (no left rail — this is a draft/doc surface, wrapped in the standard tab chrome):
- Note banner: "Screen 8 — How the system fits together. Two diagrams…"
- **A · Page mesh:** 3-column × 3-row node grid: row 1 = Agent homepage (center, brand-highlighted); row 2 = Curated search pages · Community pages (brand-highlighted) · Results (dynamic); row 3 = Listing pages (center) · Lead capture (dashed brand border). Arrow labels between rows (↓ search prompt, ↓ footer links, ↔ neighborhoods, ↕ siblings, ↓ CTA). Caption paragraph under the grid.
- **B · Brand-vault flow:** horizontal 5-step pipeline (min-width 760px, overflow-x scroll): 1 Scan → 2 Sanity gate → 3 Preview ×3 → 4 Deploy (brand-highlighted) → 5 Evolve (dashed = ongoing). Caption: "the demo is the three dots in the top bar… Time-to-branded-instance target: under 3 minutes."
- **C · Page inventory:** 4-column table (Page/surface · Audience · SEO · Status) with green = designed, amber = named/scoped/not mocked; footer line with the recommended design order.

**Mobile (375px).** Mesh grid collapses to a single vertical column in flow order (homepage → curated/results → community → listings → lead capture) with down-arrows only [BEST GUESS]. Flow B keeps horizontal scroll (it already declares min-width 760px + overflow-x) or stacks vertically with step numbers [BEST GUESS: stack vertically]. Inventory table scrolls horizontally inside its own container.

## Element inventory

| Element | What it shows/does | Data source (module + record) | Interactions | Spec source |
|---|---|---|---|---|
| **A1 Agent homepage node** | "link-equity hub · embed widget"; center of mesh; brand-highlighted | Static diagram; refers to Tab 5 homepage (H1 auto-fills market name from brand vault) | Click → Tab 5 [BEST GUESS: nodes are links] | Draft ~1935; Tab 5 line ~314 |
| A2 Curated search pages node | "/homes-under-1.4m · indexed" — SEO slug pages | Tab 6 curated pages | Click → Tab 6 | Draft ~1939 |
| A3 Results (dynamic) node | "noindex · links out to everything" — crawl budget concentrates on ranking pages | Tab 2 results | Click → Tab 2 | Draft ~1943 |
| A4 Community pages node | "the ranking engine · FAQ schema"; brand-highlighted; ↕ siblings, ↓ listings, ↑ city rollup | Tab 6 community pages | Click → Tab 6 | Draft ~1947 |
| A5 Listing pages node | "breadcrumbs up · comps sideways · stays live when sold" | Tab 3 property detail + sold pages | Click → Tab 3 | Draft ~1951 |
| A6 Lead capture node | "Ask · Tour · Market report → PropFlow CRM" (dashed border = conversion endpoint) | PropFlow lead intake | Click → lead-capture flows (Tab 2/3 CTAs) | Draft ~1955 |
| A7 Arrow labels | Direction + meaning of each edge (user path AND internal link) | — | — | Draft ~1936–1952 |
| A8 Mesh caption | "Every page links up (breadcrumbs), sideways (siblings, comps), and down… A crawler — or a buyer — can enter anywhere and reach everywhere." Noindex rule for dynamic results | — | — | Draft ~1958 |
| **B1 Step 1 · Scan** | "Website + Google Business Profile → logo, colors, name, DRE, markets" — automated brand extraction | BrandVault record (scanned fields); GBP + site scrape of the AGENT'S OWN properties (agent authorizes at onboarding) | Runs from Onboarding Wizard step 8; re-runs from Settings on rebrand | Draft ~1964 |
| B2 Step 2 · Sanity gate | "Contrast check · mud detection · accessibility fix-ups" — auto-correction of extracted palettes | BrandVault candidate themes | Automatic; failures fall back to house default [BEST GUESS] | Draft ~1966 |
| B3 Step 3 · Preview ×3 | Three candidate themes: extracted · cleaned · house default — agent taps one | BrandVault candidates rendered over the locked layout | Tap to select; this IS the choice UI in onboarding | Draft ~1968 |
| B4 Step 4 · Deploy | "CSS variables only — layout locked · all pages themed at once" (brand-highlighted step) | BrandVault active theme → CSS variable set | One tap; every consumer + portal page rethemes | Draft ~1970. Same mechanism as OTTO constraint: changes apply through variable slots, never raw HTML (line ~1098) |
| B5 Step 5 · Evolve | "Manual tweaks · premium templates (upsell) · re-scan on rebrand" (dashed = ongoing) | BrandVault versions | → Settings→Brand; premium templates = paid | Draft ~1972 |
| B6 Flow caption | Demo = the three theme dots in the draft's top bar (same locked layout, different agent variables). **Target: branded instance < 3 minutes** | — | — | Draft ~1974 |
| **C Page-inventory table** | Full platform surface list w/ audience, SEO disposition, status | Design-draft status tracking (manually maintained) | Row/status links to tabs; amber rows are the backlog | Draft ~1977–1991 |
| C rows (verbatim content) | 1 Search entry/Results/Compare/Property detail/Sold (consumer; detail+sold+curated indexed; designed tabs 1–4) · 2 Agent homepage/Community/Feature explainers ×5/Curated slugs (indexed — the ranking engine; tabs 5–6) · 3 Seller report/Funnels branded+unbranded/Buyer portal (noindex; seller done tab 10, funnels+buyer portal next) · 4 Client escrow portal (noindex; needs own screen → now Tab 25) · 5 Command Center/Competitor intel/Playbook library/Content studio (tabs 9+11; playbook+content studio next) · 6 CMA/listing-presentation page (exists in cma-generator, needs PropertyIQ skin) · 7 Onboarding wizard/Settings/Billing wallet/Team view (flow specced, screens → Tabs 21/23) · 8 Agent profile/Blog hub/Legal pages (indexed, templated not drawn) | — | — | Draft ~1981–1988 |
| C footer | Legend (green/amber) + recommended next-design order: buyer portal → client escrow portal → CMA presentation → onboarding wizard | — | — | Draft ~1990. NOTE: superseded by Tab 12's "✅ COMPLETE 2026-07-15: all P0/P1/P2 designed" — update statuses when regenerating this tab |

## States

- **Default:** static document; all three sections rendered.
- **Loading:** n/a (static content); if node-status chips become live (pulling design-status from the matrix), show per-chip skeletons [BEST GUESS].
- **Empty:** n/a.
- **Error/degraded:** if inventory statuses are wired to the capability matrix and it's unreachable, show last-cached statuses with an as-of date — never blank the table [BEST GUESS, mirrors platform fail-closed style].
- **Permission-limited:** Admin/owner-only in product; not present in client or team-member navigation [BEST GUESS].
- **Mobile:** vertical mesh; stacked flow; scrolling table (see Layout).

## Data fields

| Field | Format | Source of truth |
|---|---|---|
| BrandVault scanned fields | logo (img), primary/secondary colors (hex), agent name, DRE number, brokerage, markets[] | Brand-vault scan of agent's site + GBP; DRE/brokerage ultimately from licensed identity record (identity.json pattern — single source of truth, locked in Settings) |
| Theme candidate | {id, label: extracted/cleaned/house-default, css_vars{}} | BrandVault |
| Active theme | css variable set + version + deployed_at | BrandVault |
| Time-to-branded-instance | target < 3 min (product KPI) | Draft B caption |
| Mesh node | {page, seo: indexed/noindex, tab_ref, status} | Design status table |
| Inventory row | page/surface · audience (Consumer/Client/Agent/Agent→client) · SEO · status (designed/specced/next) | Draft table |

## Rules & compliance

- **Layout locked; variables only.** Agent branding can NEVER change structure — deploy step and OTTO SEO changes both apply exclusively through CSS-variable/template slots so the compliant locked layout can't be broken (draft ~1970, ~1098).
- **Identity is locked, not editable prose:** name/DRE/brokerage flow from the brand vault into every surface (homepage H1, SEO block, funnel footers, Settings identity panel — Tabs 5/21/23/25 all reference "the same brand vault"). Matrix P0 "Settings Suite: Identity/brand (locked)."
- **DRE footer persists on branded AND unbranded funnel pages** (Tab 9 funnels block) — the unbranded toggle strips agent theming, never the license/compliance footer.
- **SEO discipline:** dynamic results stay noindexed; community pages + homepage carry ranking weight; curated slugs, listing, sold pages indexed (mesh + inventory columns). Lead-capture pages noindex.
- **Scan consent:** brand scan reads the agent's own website + GBP, authorized during onboarding — not third-party scraping [BEST GUESS framing; consistent with competitor-intel official-API/public-data rule].
- **Accessibility:** sanity gate enforces contrast/accessibility before any extracted palette can deploy (step 2).
- Fair-housing/consent gates don't attach to this screen directly (no consumer data displayed) — they live on the screens the mesh points to.

## Cross-links

- **In:** tab bar · Onboarding Wizard (23) step 8 executes flow B · Settings (21) brand panel → "re-scan" (flow B step 5) · Capability Matrix (12) is the deeper version of section C.
- **Out:** every mesh node → Tabs 1–6 · inventory rows → Tabs 9, 10, 11, 21, 23, 25 and the P0/P1 screens (13–37) · flow B → Settings→Brand, Billing (premium templates).
- **Ledger events:** emits BRAND_VAULT_SCANNED, THEME_DEPLOYED, THEME_RESCANNED [BEST GUESS names — pattern-consistent with the platform event ledger]; consumes design-status data only.

## Open decisions

- [DECIDE] Does Tab 8 ship in-product or remain a design-doc artifact? Interim: ships as Admin-only "/system" architecture page; the brand-vault FLOW ships for real inside Onboarding step 8 and Settings→Brand.
- [DECIDE] Brand-scan engine (own scraper vs third-party brand-extraction API). Interim: in-house scan of site + GBP (logo, palette via dominant-color extraction, name/DRE/markets via LLM extraction with human confirm on the preview step) — UI unaffected by choice.
- [DECIDE] Premium template pricing/tiering (step 5 upsell). Interim: design 2–3 premium templates behind a paywall chip; numbers TBD by product owner — no invented prices.
- [DECIDE] Whether section C statuses stay hand-maintained or bind live to the capability matrix JSON. Interim: bind to the matrix (Tab 12) so "done is a checklist, not a claim" stays true automatically; note that C's current amber statuses are stale vs. Tab 12's 2026-07-15 "all designed" banner and must be refreshed.
- [DECIDE] Re-scan on rebrand: auto-detect (periodic diff of agent site) vs manual button. Interim: manual "Re-scan my brand" in Settings; deploy still requires the preview-and-tap step (never silent retheme).
