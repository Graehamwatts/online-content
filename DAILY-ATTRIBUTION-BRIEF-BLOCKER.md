# Daily Attribution Brief — Execution Blocker

**Status**: ❌ **BLOCKED** — Token scope limitation  
**Date**: 2026-06-30 (Tuesday, 7:23 AM PDT)  
**Scheduled Task**: `daily-attribution-brief` (Mon–Fri, 7:15 AM PT)

---

## What Failed

The autonomous daily attribution brief task attempted to:

1. **Deploy workflow** → Create `.github/workflows/daily-attribution-brief.yml` in `Graehamwatts/online-content` repo
2. **Trigger GitHub Action** → Run the workflow to pull GHL data via PIT
3. **Generate HTML brief** → Aggregate leads, opportunities, wins, and source attribution
4. **Email brief** → Send to graehamwatts@gmail.com with dashboard link

**Result**: Step 1 failed. Steps 2–4 were blocked as a result.

---

## The Blocker

The GitHub Personal Access Token (PAT) in `github-token.txt` has **`repo` scope only**.

GitHub's API refuses to create or update workflow files (`.github/workflows/*.yml`) without explicit `workflow` scope. The error:

```
refusing to allow a Personal Access Token to create or update workflow `.github/workflows/daily-attribution-brief.yml` without `workflow` scope
```

### Why This Matters

The workflow file is the vehicle for running the data pull and email generation outside the Cowork sandbox. The Cowork sandbox cannot:
- Call `services.leadconnectorhq.com` (blocked by proxy allowlist)
- Send email directly

The workflow bypasses both restrictions by:
- Running on GitHub's network (can reach GHL)
- Using GitHub Actions' built-in email tooling or calling Gmail API with repo Secrets

---

## How to Unblock

### Option A: Create a New Token with Workflow Scope (Recommended)

1. Go to **GitHub Settings → Developer Settings → Personal access tokens (classic)**
2. Click **Generate new token**
3. Name it: `gh-workflow-deploy` or similar
4. Grant these scopes:
   - ✓ `repo` (full control of private repositories)
   - ✓ `workflow` (update GitHub Action workflows)
5. Copy the new token
6. Store it at: `C:\Users\Graeham Watts\Documents\GitHub Credentials\pat-workflow-scope.txt`
7. Add it to the `Graehamwatts/online-content` repo Secrets as `WORKFLOW_DEPLOY_PAT`

### Option B: Use the New Token to Deploy the Workflow

Once you have the new token:

```bash
cd C:\Users\Graeham Watts\Documents\Claude\Online Content

PAT=$(cat "path/to/new/token/pat-workflow-scope.txt" | tr -d '[:space:]')

git add ".github/workflows/daily-attribution-brief.yml"
git commit -m "chore: add daily-attribution-brief workflow"
git push "https://${PAT}@github.com/Graehamwatts/online-content.git" HEAD:main
```

### Option C: Update the Existing Token (Not Recommended)

If you can't create a new token, you can regenerate the existing `github-token.txt` with `workflow` scope — but this will affect all scripts that use it. Only do this if you're confident it won't break other automations.

---

## What's Ready

✓ **Template prepared**: `.github/workflows/daily-attribution-brief.yml` (locally in your cloned repo)  
✓ **Failure report generated**: `dashboards/attribution/2026-06-29-daily-FAILED.html` (pushed to GitHub)  
✓ **GHL credentials in place**: `ghl-pit.txt` with valid PIT token and Location ID  

**What's NOT deployed**: The workflow file itself (blocked by token scope).

---

## Next Steps (for you or the next bot run)

1. Create the new PAT with `workflow` scope (manually, or ask Claude to do it via a different auth channel)
2. Push the workflow file using the new token
3. Re-run this task (`daily-attribution-brief`) — it will now succeed

Or, if you prefer manual execution until this is fixed:

```bash
node scripts/ghl-daily-brief.js
```

(Once you've created this helper script — it's not in the repo yet, but the workflow file shows the exact Node.js code needed.)

---

## Failure Report

A detailed failure report is saved at:  
**`dashboards/attribution/2026-06-29-daily-FAILED.html`**

This is viewable in your browser or at:  
**`https://graehamwatts.github.io/online-content/dashboards/attribution/2026-06-29-daily-FAILED.html`**

---

## Schedule Impact

- **Today's brief**: ❌ Not generated (GHL pull blocked)
- **Tomorrow's (Fri) brief**: ❌ Will fail for the same reason unless unblocked
- **Monday's brief**: ❌ Will fail for the same reason unless unblocked

The task will keep running but fail silently until the token scope is fixed.

---

**Escalation**: This is not a data or credential issue — it's purely a GitHub API permission issue. The fix is administrative (grant `workflow` scope to the PAT) and requires about 5 minutes of manual work.
