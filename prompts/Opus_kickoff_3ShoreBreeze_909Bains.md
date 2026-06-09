# Opus 4.8 Kickoff Prompt — Two Upcoming Listing CMAs

Hi Claude. I need you to run two listing CMAs back-to-back for two upcoming properties I have. Both are listing-side CMAs (I'm the seller's agent). Use the `cma-generator` skill and follow it exactly.

## The two properties

1. **3 Shore Breeze Court, East Palo Alto, CA**
2. **909 Bains Street, East Palo Alto, CA**

For each one: pull subject specs from MLS + Realist, pull active + pending + sold comps in the same submarket (last 6 months), pull MLS Matrix Stats trend data for the EPA SFR cohort, build the CMA following the canonical Listing-mode template, save locally to all three folders, and push to GitHub.

## Skills folder

`C:\Users\Graeham Watts\Documents\Claude\Skills`

The `cma-generator` skill at `C:\Users\Graeham Watts\Documents\Claude\Skills\skills\cma-generator\SKILL.md` has the full methodology and rules. **Read it first.** It will point you to:
- `references/dashboard_template.html` — canonical Listing-mode template (1030 Bradley reference example)
- `references/buyer_mode_template.html` — canonical Buyer-mode template (1430 Chilco reference)
- `references/past_client_mode.md` — past-client mode rules
- `references/branding.md`, `references/charts.md`, `references/github_publishing.md`

These two CMAs are Listing mode, so follow `dashboard_template.html` structure.

## Locked rules from the skill (do not skip)

- **Voice:** second person ("you", "your"). Speak directly to the seller. Forwardable as-is.
- **No em-dashes** anywhere in published HTML. Run final scan for `&mdash;` and `—`.
- **Pricing tiers are RANGES** not single numbers (Conservative / Competitive / Ambitious).
- **Lead with market context** (rates, cycle, trend), never commission math.
- **5 required Chart.js canvases:** `trendPrice`, `trendLS`, `priceJourney`, `domVsCut`, `priceDom`.
- **Real MLS data for trend charts** (monthly, Matrix Stats, 5+ years). Don't smooth or invent.
- **Price-reduction history table** for top sold comps. Click into each, pull Original List, Final List, Sold, # Reductions, DOM.
- **Submarket awareness:** east-of-101 vs west-of-101 in EPA matters. Flag any cross-boundary comp.
- **Three Paths Forward** for Listing mode: Sell+Redeploy / Prep+Timing for top of range / Hold+Rent for long-term investors.
- **Pre-List Prep section is OPTIONAL** — do NOT include by default.
- **Capital deployment framing:** quantify the opportunity cost of holding vs redeploying.

## File save locations (LOCAL)

Save each CMA to all three folders so the existing workflow stays consistent:
- `C:\Users\Graeham Watts\Documents\Claude\Online Content\cma\`
- `C:\Users\Graeham Watts\Documents\Claude\Online Content\cma-reports\`
- `C:\Users\Graeham Watts\Documents\Claude\Online Content\cmas\`

Filename pattern: `CMA_[street_number]_[street_name_underscored].html` (no special characters).

(If you also see `C:\Users\Graeham Watts\Documents\Claude\Skills\online_content_files\`, that's an older path. The current canonical local folder is the `Documents\Claude\Online Content` directory above.)

## GitHub publishing

Personal Access Token is at `C:\Users\Graeham Watts\Documents\Claude\Online Content\github-token.txt`. Use it to push via the GitHub Contents API:

- **Repo:** `Graehamwatts/online-content`
- **Path on repo:** `cmas/CMA_[address].html`
- **Method:** PUT to `https://api.github.com/repos/Graehamwatts/online-content/contents/cmas/[filename]`
- **Body:** JSON with `message`, base64-encoded `content`, `branch: main`, and `sha` if updating an existing file
- **Live URL pattern:** `https://graehamwatts.github.io/online-content/cmas/CMA_[address].html` (Pages deploys in 1-2 min)

The sandbox bash environment has direct network access to api.github.com — you can `curl` it directly from the bash tool. No browser relay needed.

## MLS access

Drive **Mac Studio Chrome** for MLS pulls. Connect via the Chrome extension MCP, list connected browsers, ask me to pick which one (the Mac Studio is the one named "chrome" on macOS). I'll need to log in to MLSListings manually the first time — don't enter passwords on my behalf.

MLSListings Matrix is at `https://matrix.mlslistings.com/Matrix/Home.aspx`. Realist is reachable via the REALIST link in Matrix's top nav. Both work after a single SSO login.

## Workflow for each property

1. Use AskUserQuestion at the start to confirm: client first name, occupancy status, any prior listing history, condition known or unknown.
2. Pull subject specs from Realist (sale history, owner, year built, sqft, lot, AVM, prior deed transfers).
3. Pull cohort comps from Matrix (Active + Pending + Sold, last 6 months, same submarket, similar size range).
4. Click into the top 4-5 sold comps to capture Original List, Final List, Sold, DOM for the price-reduction history table.
5. Pull EPA SFR trend data from Matrix Stats (monthly granularity, Sale Price Avg + L/S Ratio, Jan of 5 years back to current month).
6. Build the HTML following `dashboard_template.html` section order exactly.
7. Run final em-dash scan, save to all 3 local folders, push to GitHub via the Contents API.
8. Show me the live URL and present the file.

## Do NOT

- Send any client emails yet. I'll tell you when. Drafts only if I explicitly ask.
- Include the Pre-List Prep section by default.
- Use single-number pricing — always ranges.
- Include any em-dashes in the published HTML.
- Anchor pricing on cross-boundary comps without flagging them as different submarket.
- Recommend "wait for rates to drop" — frame Path C as long-term real estate hold investors only.

## Order of work

Start with **3 Shore Breeze Court**. After that one is published and I've reviewed it, we'll do 909 Bains Street. Use AskUserQuestion at the start of each to gather the client context I have on hand.

Let's go.
