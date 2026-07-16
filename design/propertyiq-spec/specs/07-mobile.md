# 07 · Mobile Patterns (375px system-wide adaptation spec)

**Purpose** — Not a separate product: the canonical 375px adaptation rules for the consumer surfaces (search/results, property detail, homepage, community pages) plus the shared mobile primitives every other screen's "mobile variations" section inherits. Draft's proven anchors: list-first results with a floating Map toggle (split view fails on small screens — Zillow's pattern), one-line intelligence strip compression, and the sticky agent contact bar on detail pages.

**Primary users** — Consumers on phones (majority of portal traffic); secondarily agents on the go (the agent-side mobile flows — Past Client call assistant, approvals — are specified on their own screens; this spec defines the shared primitives they reuse).

**Entry points** — Any mobile visit to the instance (responsive web, not a native app for v1 [BEST GUESS]); QR codes on postcards/signs deep-link to listing/community/value pages; SMS links from alerts and AI text-backs; GBP mobile taps.

**Exit points** — Same destinations as desktop counterparts; plus native handoffs: `tel:` call, SMS, calendar add on tour booking, share sheet on Save·Share.

## Layout

**Global chrome (consumer)**: compact header — agent avatar + name + "PropertyIQ" powered-by; no persistent nav bar (hamburger) [BEST GUESS]. One primary ask per viewport; sticky bottom bars replace section CTAs, never stack.

**Results (phone 1 in draft)**: search prompt input + Go → horizontally scrolling chip row (Commute · Schools · Fire · Yield · +More; active chips highlighted) → vertical card list (photo, price, address/bd-ba, one-line ⚡ intelligence strip: "96 match · 22 min commute · Elem 9/10") → floating "Map" pill toggle bottom-center. Map mode replaces the list full-screen with a bottom-sheet card peek on pin tap [BEST GUESS on sheet]; toggle returns to list.

**Property detail (phone 2 in draft)**: back header ("← {address}" + Save · Share) → edge-to-edge swipe gallery (~130px+ hero) → price + fact line → one-line intelligence strip → horizontally scrolling section chips (Overview · Commute · Schools · Investment) that jump-scroll/switch panels → key stat rows (e.g. Est. rent + yield) → **sticky bottom agent bar**: "Ask {agent}" (primary, brand) + "Book tour" (outline), always visible.

**Homepage & community**: per their own specs' mobile sections — this spec is their authority for the shared primitives below.

## Element inventory

| Element | What it shows/does | Data source | Interactions | Spec source |
|---|---|---|---|---|
| Compact branded header | Avatar, agent name, powered-by | Brand vault | Tap avatar → homepage | Draft s7 |
| NL search prompt (mobile) | Same parser as Screen 1; voice mic button for dictation | SearchRecord/parser | Type/voice → results; "Parsed as" chips echo the interpretation, editable | Draft s1 note (voice mic for mobile) |
| Horizontal chip row | Filter/lens chips, scrollable, on/off state, "+More" opens full filter sheet | Active filters | Tap toggles; +More → bottom-sheet filter panel [BEST GUESS] | Draft s7 |
| Result card (mcard) | Photo, price, address · bd/ba, one-line ⚡ intelligence strip | IDXDisplayCache + intelligence engines | Tap → detail; long-press/heart save [BEST GUESS: heart icon] | Draft s7 |
| Intelligence strip (compressed) | Desktop strip compresses to ONE line: match count/criteria, top honest highlight | Match engine ("Matches 5 of 5" framing from s2) | Tap expands full strip [BEST GUESS] | Draft s7 + s2 |
| Floating Map toggle | Bottom-center pill; switches list ↔ full-screen map | — | Tap; map obeys one-heatmap-at-a-time + legend rule | Draft s7 + s2 layer rule |
| Map pin bottom sheet | Pin tap → card peek with photo/price/strip; explainable layers (contributing facts on pin) | Same as cards; ScoringService for layers | Swipe up → detail | Draft s9 map rules; matrix correction #12 |
| Detail gallery | Edge-to-edge swipe photos | ImageryProvider/MLS | Swipe; tap → full-screen | Draft s7 |
| Save · Share | Save to saved properties (S26); native share sheet | SavedPropertyRecord | Save requires soft account/contact capture [BEST GUESS: deferred prompt on first save] | Draft s7 + s26 |
| Section chips (detail) | Overview/Commute/Schools/Investment in-page nav | — | Tap scrolls/switches | Draft s7 |
| Sticky agent bar | "Ask {agent}" + "Book tour", persistent on detail pages | Brand vault; booking slots (PropFlow) | Ask → chat/SMS lead flow (consent-gated); Book → slot picker (pre-approved slots, confirm queue) | Draft s7; matrix PropFlow booking gap |
| Sticky homepage CTA bar | Value · Search · Call — replaces section CTAs on mobile | — | 3 CTAs | Draft s5 |
| Behavior-triggered soft prompt (mobile) | Repeat-visit/photo-binge/save prompts, dismissible, no hard gate on organic | Session events | Dismiss or capture | Draft s3 lead policy |
| Bottom-sheet pattern (shared primitive) | All secondary panels (filters, pin peek, monthly-cost editor, ask-a-question) render as bottom sheets, never new pages | — | Drag to dismiss | [BEST GUESS — consistent primitive] |
| Compare (mobile) | 2-col swipeable cards, pinned baseline fixed left | Compare set (URL-addressable) | Horizontal swipe through candidates | Draft s4 note |
| Community tables (mobile) | Trends/schools tables scroll inside overflow-x containers | Screen 6 data | Horizontal in-container scroll only | Draft s6 / spec 06 |
| Voice input (mic) | Dictated NL search | Device speech → parser | Tap-to-talk | Draft s1 |
| Call/text deep links | tel:/sms: handoffs on all phone CTAs | identity.json phone | Native dialer | identity.json |
| Toast/inline notices | Blocked-send, consent, and fail-closed messages surface as inline notices (never silent) | ComplianceProvider | — | Matrix correction #11 |

## States

- **Default**: list-first results; detail with sticky bar.
- **Loading**: skeleton cards (photo + 2 lines); map toggle disabled until first page of results; LCP budget <2s on detail (draft s3), <2.5s homepage.
- **Empty**: zero-results never happens — engine relaxes the weakest constraint and *says which one* ("showing 2.9+ baths because 3+ returned nothing") (draft s1); saved/compare empty states carry a one-line explainer + primary action.
- **Error/degraded (fail-closed)**: map layers hide with "score unavailable" when ScoringService is down; intelligence strip drops any unavailable metric rather than fabricating; deal-rating labels disappear when ScoringService is unavailable, deterministic metrics remain (matrix correction #6); offline → cached last results with a stale banner [BEST GUESS].
- **Permission-limited**: anonymous users browse freely (no hard gate on organic); saves/alerts require contact capture; tour booking requires name+phone+consent line.
- **Orientation/small screens**: everything specified at 375px; wider phones get the same layout with more card image height; no horizontal page scroll ever.

## Data fields

Same records as the desktop counterparts (S1–S6): IDXDisplayCache listing fields (MLS whitelist), match score + criteria count, commute minutes, school ratings (attributed + disclaimed), all-in monthly cost, rent estimate + yield (RentEstimateSnapshot), AVM range + confidence + as-of, saved-property notes/tags, compare sets (URL-addressable, persistent). Mobile adds: device geolocation (opt-in, for "near me" search + commute origin) [BEST GUESS], voice transcript (transient, not stored beyond the SearchRecord parse).

## Rules & compliance

- All desktop compliance rules apply unchanged: schools firewall (§16), no crime data, AVM honesty, honest-miss framing, one-heatmap-plus-legend, brand tripwire (DRE 01466876 from identity.json).
- Consent: "Ask {agent}" SMS/chat flows capture channel consent before the first outbound message; unknown consent blocks with a visible reason (matrix correction #11).
- Ownership signals on map pins render as absentee/corporate/owner-occupied badges only — never raw owner names/addresses (matrix correction #12).
- Geolocation is opt-in per browser prompt, used only for the session, never stored to the contact without explicit save [BEST GUESS].
- Tap targets ≥44px; sticky bars respect safe-area insets; performance is a product KPI (lists <500ms warm, per Screen 14 note — applies to mobile lists too).

## Cross-links

This screen defines primitives consumed by: S1/S2 (search/results), S3 (detail), S4 (compare), S5 (homepage), S6 (community), S10 (seller report — already mobile-first as a live page), S25 (client portal), S26 (saved searches), S27 (Past Client mobile call assistant — reuses sticky-bar + bottom-sheet + voice-note primitives). **Ledger events**: identical to desktop counterparts plus MAP_TOGGLED, VOICE_SEARCH_USED, STICKY_CTA_TAPPED, TOUR_REQUESTED — all attribution-keyed.

## Open decisions

- [DECIDE] Native app vs responsive web for v1. Interim: responsive web + PWA install prompt; native app deferred — no spec section mandates native [BEST GUESS].
- [DECIDE] "Ask {agent}" channel (in-page chat vs SMS handoff vs Wattson-answered chat with agent escalation). Interim: in-page chat answered by the platform engine with agent escalation + consent capture before any outbound follow-up — keeps the compliance check server-side; UI unaffected by channel choice.
- [DECIDE] Save gating moment (first save vs third). Interim: soft prompt on first save, skippable once, required on second [BEST GUESS].
- [DECIDE] Map clustering + pin budget on mobile. Interim: cluster above 50 pins in viewport [BEST GUESS], legend always visible for the active layer.
- [DECIDE] Voice search vendor (device WebSpeech vs server ASR). Interim: WebSpeech API with server fallback — parser input is plain text either way; UI unaffected.
