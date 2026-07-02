# Daily Attribution Brief — RESOLVED / OBSOLETE

**Status**: Not a blocker. This task is redundant.
**Corrected**: 2026-07-02 by the scheduled `daily-attribution-brief` run.

## The real finding
The Daily Attribution Brief was **retired and replaced by the Morning Command Center**
(`scripts/command_center.py` — its docstring: "Replaces the retired Daily Attribution Brief").
The Command Center runs every weekday via the already-deployed
`.github/workflows/morning-command-center.yml` (perfect run record, 8/8 business days
through 2026-07-01), pulls the same GoHighLevel data, includes a
"Lead sources · last 7 days" breakdown, and emails it to BRIEF_RECIPIENTS.

## Why the Jun 29–30 "token scope" blocker was a red herring
Deploying a *new* attribution workflow needs `workflow` token scope — but no new workflow
was ever needed, because the data pull already happens daily. Any additional attribution
cut (e.g. day-over-day by source) belongs inside `command_center.py`, which is a plain
script pushable with the existing `repo`-scope token. No admin/token fix required.

## Recommendation
Retire the `daily-attribution-brief` scheduled task (Cowork → Scheduled tasks). It only
duplicates the Command Center and emits false "BLOCKED" alerts 3×/week. If the day-over-day
source comparison is specifically wanted, fold it into `command_center.py`.

Prior-run artifact kept for history: `dashboards/attribution/2026-06-29-daily-FAILED.html`.
