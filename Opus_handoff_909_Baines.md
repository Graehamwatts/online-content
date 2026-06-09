# Handoff — Build the 909 Baines St CMA (3 Shorebreeze is DONE)

Paste this into a fresh chat to build the second listing CMA with a clean context window. 3 Shorebreeze Ct is finished and live; 909 Baines is a full from-scratch pull.

## STATUS
### 3 Shorebreeze Ct — COMPLETE and published
- Live: https://graehamwatts.github.io/online-content/cmas/CMA_3_Shorebreeze.html
- Saved to cmas/, cma/, cma-reports/ (all identical, 39,474 bytes).
- Working data archived at `Documents/Claude/Online Content/cma/_workdata_3_Shorebreeze.md`.
- Recommended list $1,325,000 to $1,375,000. BMR/foreclosure resale-restriction flagged as the #1 pre-list item (confirm with title + City of EPA).
- **Use the published 3 Shorebreeze HTML as the structural template for 909 Baines** — it already has the two improvements below baked in.

### 909 Baines St, East Palo Alto 94303 — NOT STARTED
Full pull needed: subject (Realist tax + MLS history), sold comps (EPA SFR last 6 mo), Active+Pending+Contingent competition, per-comp reduction detail on the top 5 sold comps, and the 5-year Matrix Stats trend.

### Emails — NOT STARTED (do after 909 Baines)
Pull each client's email from GoHighLevel (GHL MCP was NOT connected in the last session — connect it first), draft seller-facing emails for BOTH properties (DRAFTS ONLY, do not send), and return both live GitHub URLs. Emails are forwardable, second-person, lead with the market read, link to the hosted CMA.

## TWO IMPROVEMENTS TO APPLY (Graeham approved, now in the 3 Shorebreeze file)
1. **Estimated days-on-market per pricing tier.** Add a DOM range to each of Conservative / Competitive / Stretch, grounded in the reduction data (priced at/under market sold in 8 to 15 days; priced above sat 35+ days and usually cut). Print the caveat: small sample (5 closest comps + actives), spring-seasonality-dependent, directional ranges not guarantees.
2. **Sorted horizontal-bar DOM chart (replaces the old dual-axis domVsCut).** One bar per comp, bar length = days on market, sorted fastest to slowest, color = pricing outcome (green sold over asking no cut, gold sold at ask no cut, red required a cut). Outcome text baked into each y-axis label and the tooltip. Exact pattern (copy from the 3 Shorebreeze file, `domVsCut` block): single dataset, `type:'bar'`, `indexAxis:'y'`, `backgroundColor` array per bar, legend hidden, tooltip pulls from a parallel `domOutcome[]` array.

## CRITICAL GOTCHAS LEARNED THIS SESSION (read before building)
- **File host/VM sync bug (ROOT CAUSE FOUND).** When the Edit tool SHORTENS an HTML file, the bash mount keeps the old byte length and pads the tail with NULL bytes (`\x00`) after `</html>`. That junk made bash reads look truncated and got published once. **Fastest fix:** after ANY Edit, strip the nulls in bash before publishing: `python3 -c "s=open(F,'rb').read().rstrip(b'\x00').rstrip()+b'\n'; open(F,'wb').write(s)"`, then assert it ends with `</html>` and has no `\x00`. **Always** before publishing: verify ends with `</html>`, `node --check` the inline `<script>`, and (after publish) re-verify the LIVE page with `Chart.getChart(id)` for every canvas ID. Writing to a FRESH filename also sidesteps it (new files read clean).
- **Publishing WORKS from sandbox bash.** `curl`/python `urllib` to `api.github.com` returns HTTP 200 from the sandbox (the old "proxy blocks it" note is wrong for this environment). Token at `Documents/Claude/Online Content/github-token.txt` (40-char PAT). PUT to `https://api.github.com/repos/Graehamwatts/online-content/contents/cmas/CMA_909_Baines.html` with base64 content, branch main, and the existing `sha` if updating. No browser chunking, no Composio needed.
- **MLS access (Matrix).** Drive the Mac Studio Chrome (deviceId 09e3283f). Graeham logs into MLSListings manually. Do NOT click the REALIST top-nav (single-session logout). Get subject specs from Matrix Tax + History tabs.
- **Matrix workflow that worked:** Residential Search → set Status (Sold, or Active+Pending+Contingent), Property Type = Single Family Home, City = East Palo Alto (type "East Palo" in the City filter and click the autocomplete), Sale Date range for the 6-mo sold pull. For a single comp's reductions: clear the top search box, UNCHECK "Include other criteria," type the MLS#, Enter, open the listing → the Listing tab shows Orig Price / List Price / Sale Price / DOM (Orig = List means 0 reductions). For the 5-yr trend: top-nav STATS → pick preset "Sale Prices Over Time" → set City + Single Family Home → Customize tab → Time Frame "Past 5 Years", Statistic "Sale Price, Average" then re-run with "Sale Price to List Price Ratio", Group By Month → Data tab gives the monthly table.
- **Context discipline on Matrix.** `get_page_text` and `find` on a 250-row Matrix results page are ~200k tokens and will blow the window. Read row data from ZOOMED screenshots instead. NOTE: `javascript_tool` that returns scraped MLS rows gets "[BLOCKED: Cookie/query string data]" — don't rely on it for extracting results; use zoom screenshots. (JS is fine for clicking and for non-data checks.)

## LOCKED RULES (from skill + original kickoff)
- Voice: second person ("you/your"), forwardable to the seller as-is.
- NO em-dashes anywhere in published HTML. Scan with `grep -c "—"` (and en-dash "–") before publishing; both must be 0.
- Pricing tiers are RANGES, not single numbers (Conservative / Competitive / Stretch), each now with a DOM estimate.
- Lead with market context, never commission math.
- 5 required Chart.js canvases: trendPrice, trendLS, priceJourney, domVsCut (sorted bars), priceDom. Real MLS data only.
- Price-reduction history table for top sold comps.
- Submarket awareness: east-of-101 (Area 322) vs west-of-101. Flag cross-boundary comps; never anchor on west-side outliers.
- Three Paths Forward (Listing): Sell+Redeploy / Prep+Timing for top of range / Hold+Rent for long-term holders. Do NOT recommend "wait for rates to drop."
- Pre-List Prep section OPTIONAL — fold into Path B by default.
- Run narrative through the `humanizer` skill before publishing. Avoid "straightforward." DRE #01466876 ONLY (the wrong DRE must never appear; verify `grep -o -E "DRE #?[0-9]{8}"` shows only 01466876).
- Contact footer: Graeham Watts, Intero Real Estate, DRE #01466876, 650-308-4727, graehamwatts@gmail.com, www.graehamwatts.com. Nav logo URL is in the 3 Shorebreeze file.

## SAVE LOCATIONS (all three, local) + filename
- `Documents/Claude/Online Content/cmas/`  ← primary, this is what publishes
- `Documents/Claude/Online Content/cma/`
- `Documents/Claude/Online Content/cma-reports/`
- Filename: `CMA_909_Baines.html`

## ORDER OF WORK
Pull 909 Baines (subject → comps → active/pending → reductions → 5yr trend, saving to a `_workdata_909_Baines.md` as you go) → build from the 3 Shorebreeze template → humanize → verify (em-dash + DRE + node --check + ends-with-</html> + math) → publish via sandbox curl → verify live with Chart.getChart → Graeham reviews → then draft both seller emails and return the two live URLs.
