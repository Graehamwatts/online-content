# Morning Command Center — archived 2026-07-29

Graeham asked to stop this and shelve it rather than delete outright. Files moved here, untouched, in case we want it back:

- `morning-command-center.yml` — was `.github/workflows/morning-command-center.yml` (GitHub Action, weekdays 7am PT)
- `command_center.py` — was `scripts/command_center.py` (the script the workflow ran)

It had already been disabled via `gh workflow disable` on 2026-07-29 before this move, so no more emails were going out. Moving the `.yml` out of `.github/workflows/` removes it from GitHub Actions entirely (GitHub only reads workflow files from that exact path), so this is now fully off — nothing left to re-enable by accident.

Not touched: `dashboards/command-center/` — the daily-generated HTML history the workflow used to publish (28 files as of this archive date). Left in place since it's just historical published output, not part of the running automation. Safe to delete separately later if wanted.

**To bring it back:** move both files back to their original paths (`git mv` in reverse) and re-enable with `gh workflow enable "Morning Command Center" --repo Graehamwatts/online-content`.

**To delete for good:** just delete this `archive/morning-command-center/` folder.
