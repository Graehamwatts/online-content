# Daily Attribution Brief — Execution Blocker (FINAL — Jul 13, 2026)

**Status**: Task is functionally redundant. Not a token problem — never verify
against `.claude-credentials/ghl-pit.txt` again, see why below.

> This supersedes both prior versions of this doc (2026-06-30 and 2026-07-03).
> Both were wrong in different ways. This version was verified against the
> actual GitHub Actions run history and the live `command_center.py` source,
> not a local file guess.

---

## The real, final root cause (verified Jul 13, 2026)

Two independent things are true at once, and prior runs conflated them:

1. **`.github/workflows/daily-attribution-brief.yml` has a genuine YAML bug.**
   The embedded Node script writes raw HTML starting at column 1 inside a
   `run: |` block scalar, which terminates the block early. GitHub's parser
   confirms this — the workflow shows up with no name in the Actions API and
   rejects `workflow_dispatch` with a 422 ("Workflow does not have
   'workflow_dispatch' trigger"). A fix requires a `workflow`-scope PAT to
   push to `.github/workflows/`; the repo's PAT is `repo`-scope only, by
   design (see main CLAUDE.md). Only Graeham can mint that token or edit the
   file in the GitHub UI directly.

2. **The `GHL_PIT` GitHub secret has been valid the whole time.** Every prior
   "401 — token is a placeholder" diagnosis (Jun 29 – Jul 7) was reading
   `.claude-credentials/ghl-pit.txt`, a local file that this task's design
   happens to check — never the real secret. Proof: `scripts/command_center.py`
   uses the same `GHL_PIT` secret and has run successfully every business day,
   including Jul 13 (run `29266632202`), pulling live GHL data. **Do not
   diagnose this task's data pipeline against the local placeholder file
   again — check Actions run history against the `GHL_PIT` secret instead.**

## Why it doesn't matter anyway

`scripts/command_center.py` line 6: *"Replaces the retired Daily Attribution
Brief."* Morning Command Center (`.github/workflows/morning-command-center.yml`,
cron `0 14 * * 1-5`) already pulls the same GHL data every weekday morning,
includes a "Lead sources · last N days" section, and emails
`BRIEF_RECIPIENTS`. This task (`daily-attribution-brief`) has not delivered
anything Command Center doesn't already cover since at least early July.

## What's genuinely missing (the actual gap, not a bug)

Command Center's Jul 13 pull shows every lead in the last 7 days tagged
**"Unknown"** source — 8/8. That's an upstream tagging gap (web forms / ad
UTMs / GHL workflow triggers not stamping a source field onto new contacts),
not a pull or delivery failure. Fixing it is a GHL configuration task, not an
automation task.

## Recommendation (not yet actioned — Graeham's call)

Retire the `daily-attribution-brief` scheduled task. If the one thing it
offered that Command Center doesn't — day-over-day / same-weekday-last-week
lead comparison — is still wanted, add that single cut into
`command_center.py` instead. No new workflow, no new token needed.

---

**Bottom line**: This was never a live blocker. It was a redundant task
running against a local file that was never the real credential, layered on
top of a syntax bug in its own delivery pipeline, while a separate working
system already did the job. Retiring the task, not fixing the token, is the
actual fix.
