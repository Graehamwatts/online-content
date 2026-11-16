# Cowork Workspace — Graeham's Setup

This is Graeham Watts's main Cowork workspace. Read this file FIRST in any session before doing repo work.

## 📍 WHERE MY SYSTEMS LIVE — canonical location map (added 2026-06-17)

**Purpose:** so Claude never has to ask "where is X" and Graeham never re-explains locations. When a system below is named, use THIS path/repo as the source of truth. This map is auto-loaded every session (no tool, no build, no tokens wasted).

| System | Canonical location | Notes |
|---|---|---|
| **Skills toolkit** | `Documents\Skills LLMS\Claude\Skills\skills\` → repo `Graehamwatts/skills` | the 60+ skill folders |
| **Published content** (CMAs, offers, newsletters, dashboards) | `Documents\Skills LLMS\Claude\Online Content\` → repo `Graehamwatts/online-content` | PUBLIC GitHub Pages — client-facing URLs |
| **Obsidian vault** ("second brain") | `Documents\Obsidian\` → repo `Graehamwatts/property-os` | plain markdown |
| **PropIQ — master brains / specs (SOURCE OF TRUTH)** | `Documents\PropIQ\PropIQ\` — local `.docx` Master Brains | overall `PropIQ master Brain V0.docx` + per-module (Mgmt, Search, PropCast, PropClose, PropFlow CRM, PropReach, Wattson). Naming = **PropertyIQ** ("PropOS" retired) |
| **PropIQ — Obsidian mirror** | `Documents\Obsidian\PropIQ\` | a *reflection* of the local masters — must stay **identical** to the local `.docx` files; never treat as the source |
| **PropIQ — code + backups** | GitHub `PropCast/PropIQ` repo (dev/stg/prod), managed by Mehmood/QuestLab | the running app + backup of the system |
| **PropCast** | `Documents\Skills LLMS\Claude\PropCast\` | automation |
| **AI Library** | `Documents\Skills LLMS\Claude\AI-Library\` | private AiM cross-reference |
| **Finance master** | Google Sheet "Finances 2026 — MASTER (Auto)" | NEVER create new finance sheets |

> ⚠️ Separate, NOT "the PropIQ system": `Documents\LLC's\PropIQ\` (legal) and `Documents\property & Personal info\PropIQ statements\` (financial).

## ✍️ Writing rules (always on) — 2026-08-19

Applies to everything you write for Graeham: CMAs, emails, listing copy, newsletters, chat replies, anything client-facing or public. This is the baseline; it does not require invoking a skill.

- No em dashes. Use commas, colons, or hyphens.
- Vary sentence length. Follow a long sentence with a short one. Fragments are fine.
- Cut AI vocabulary: delve, leverage, tapestry, testament, underscore, multifaceted, realm, seamless, robust, "it's worth noting", "in today's landscape", "and that matters" style tail-hedges.
- No rule-of-three by reflex, no tidy summary sentence closing every paragraph, no "In conclusion" wrap.
- State facts, not their significance. Delete "this represents / underscores / highlights."
- Prefer active voice and a named actor over agentless passive.
- Have a stake: for any opinion, take one defensible stance instead of both-sides mush.
- Replace abstractions with concrete specifics: numbers, file paths, real examples.
- Match length to need. A one-line answer deserves one line; don't pad a report section just because more detail is available. If you're unsure whether something needs explaining or trimming, err toward trimming and let Graeham ask for more.

For a full pass on a specific piece of text or file (55-pattern scan, a 0-100 AI-tell score, or a named voice like `casual`/`professional`/`technical`/`warm`/`blunt`), invoke the `humanizer` skill (`Documents\Skills LLMS\Claude\Skills\skills\humanizer\`) directly. Upgraded 2026-08-19 from a 29-pattern base to Aboudjem/humanizer-skill (MIT), then to v0.7.1 on 2026-09-07 (53→55 patterns, plus guardrails against flagging autistic/ADHD writers' naturally low-variance prose and non-native-English formal register as "AI," and an explicit no-fabrication rule); same skill name, so nothing else needs to change to pick it up. Check upstream (github.com/Aboudjem/humanizer-skill) periodically since it's actively maintained.

## 📬 2026-06-13 — Scheduled reports SEND, never just draft

**Standing rule (Graeham, 2026-06-13):** every recurring report / brief / reminder task must **actually send** its email so it lands in the inbox — do NOT leave Gmail drafts. Default recipients for internal reports are **Graeham (`graehamwatts@gmail.com`) + Adrian (`graehamwattsclientcare@gmail.com`)**, plus any task-specific recipients (John, Peter, Ellie, Maria) as TO/CC per that task's SKILL.md. This overrides any "draft only" wording inside an individual SKILL.md.

- **Daily Attribution Brief and morning-command-center are retired.** Their old workflow templates are neutralized historical notices. Do not copy or revive them; any replacement needs a fresh security review.
- **Exception — client-facing content stays review-first:** anything that goes to an actual client (CMA client section, listing emails) is still SENT to Graeham + Adrian for review, who forward to the client. "Send not draft" means internal reports reach the inbox; it does NOT mean auto-emailing clients.

## ⚡ 2026-06-09 architecture update — ONE skills folder, junctions everywhere

There is now exactly ONE physical copy of the skills toolkit: `Documents\Skills LLMS\Claude\Skills\skills\`. Everything else is a Windows directory junction pointing at it:

- `C:\Users\Graeham Watts\.claude\skills` → junction → `Documents\Skills LLMS\Claude\Skills\skills` (what Claude Code loads). Editing a skill in Documents is instantly live in Claude Code.
- Cowork's plugin cache `AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\...\skills` is a **REAL COPY, mirrored one-way** from Documents by the auto-push hook (robocopy /MIR). **⚠️ NEVER make the Cowork cache a junction** — tried 2026-06-09; Cowork's server reconciler deleted 63 skill files in Documents THROUGH the junction (twice) before it was caught. The cache must stay a disposable copy so Cowork can only trash its own copy. Its manifest.json was scrubbed of zombie/duplicate entries the same day.

**Consequences:** never "sync" skills by hand-copying folders; the hook mirrors the cache automatically at session end. If a zombie skill (video-script-creation-engine, social-media-analyzer, html-email, video-prompt-builder, github-skill-sync, graeham-*) reappears in the cache, run `Documents\Skills LLMS\Claude\Scheduled\FINAL-FIX-zombie-skills.ps1` — the quarterly-skills-audit scheduled task also checks for this. The auto-push hook has a WIPE GUARD: a mass deletion (>20 files) in the Skills repo is restored from git instead of being committed.

**Publishing:** push a reviewed branch using the authenticated Git helper. No session hook is authority to publish workflow or script edits. Existing dashboard/state publishers remain direct-push automation until the separately reviewed cutover.

**Scheduled tasks migrated to Claude Code (2026-06-09):** the 14 real recurring tasks were registered in Claude Code's scheduler (`~/.claude/scheduled-tasks/`, visible in the app sidebar). Each registered task is a thin wrapper that reads its canonical SKILL.md from `Documents\Skills LLMS\Claude\Scheduled\<task>\SKILL.md` — keep editing those files as the source of truth. The Cowork-side copies of these tasks must be toggled OFF in Cowork's UI to avoid double-fires. `daily-attribution-brief` was NOT registered — it self-runs as a GitHub Actions cron on the online-content repo.

## Credentials and publishing

Credentials belong in the approved private credential store. Never print or copy them into this public repository, logs, prompts or Git remote URLs. Use an authenticated Git credential helper. Workflow edits require a reviewed pull request. After the separate secret cutover, scheduled automation will use environment secrets. Until then, the existing repository secrets remain in place; see .github/SECURITY-CUTOVER.md.

## Deprecated skills — DO NOT USE

Cowork's server can re-register these names in the plugin cache even after cleanup. If one appears, don't invoke it — use the replacement instead.

| Deprecated | Use instead |
|---|---|
| `video-script-creation-engine` | `content-creation-engine` |
| `social-media-analyzer` | `content-calendar` |
| `video-prompt-builder` | `cinematic-hooks` |
| `html-email` | direct git publish to `online-content` |
| `github-skill-sync` | direct git push |
| `ghl-crm-audit` | `shared-references/integrations.md` §12 (GoHighLevel CRM) |

**Do NOT run `Scheduled/FINAL-FIX-zombie-skills.ps1`** (audited 2026-09-06). The `SessionEnd` auto-push hook already does the same job strictly better: it mirrors with robocopy `/MIR` (removes extras at *any* depth, not just a hardcoded top-level list), scrubs the manifest with an allowlist rather than a fixed denylist, and checks `LinkType` before touching the cache. The script has no junction guard, only sweeps top-level dirs, and rewrites `manifest.json` in a format the Cowork app rejects. Two sibling scripts in that folder, `PHASE2-graduate-junction.ps1` and `REDIRECT-CACHE.ps1`, were disabled 2026-09-06 because they create the forbidden cache junction; do not re-enable or "fix" their paths.

**Source of truth is always `Documents/Skills LLMS/Claude/Skills/skills/<name>/SKILL.md`**, never the Cowork cache — re-read from there before executing any skill, even one already loaded, since your loaded context may be stale.

## Folder layout

Workspace root: `Documents/Skills LLMS/Claude/`. Contains clones of the `skills` and `online-content` repos (run `ls` for current structure — skill count and subfolder names drift, don't trust a hardcoded list here), plus Cowork-managed dirs (`Artifacts/`, `Scheduled/`, `Projects/`, `Content/` — do not touch). The Obsidian vault is a SIBLING at `C:\Users\Graeham Watts\Documents\Obsidian\`, not nested here — see the `obsidian-vault` skill for its internal layout.

## Repository placement


**Critical placement rule:** skills go to `Skills/`, published HTML content goes to `Online Content/`. Never put emails/newsletters/dashboards in `Skills/`. Skills are tools that PRODUCE online content; the outputs go to the other repo.


## Obsidian vault & its GitHub push

- **Vault (local):** `C:\Users\Graeham Watts\Documents\Obsidian\` — a SIBLING of `Documents\Skills LLMS\Claude\`, **NOT** inside it. Verified as the real vault root (has the `.obsidian` config). Top folders: `01 Team & Agents`, `02 Daily Notes`, `03 Listings`, `04 Clients`, `05 Marketing`, `AI Library`, `Content Intelligence`, `Instagram Saves`, `PropIQ` (renamed from `Prop OS` 2026-06-09), `PropertyCast`, `_Templates`, `rules`. Plain markdown — no token needed to read/write locally.
- **Rule:** never commit either Obsidian folder into a repo. If a token ever lands in a synced/backed-up folder, rotate it.

## Mandatory session protocol

### At the START of any session that will touch repo files:

```bash
# Pull both repos to ensure local matches GitHub
cd "Documents/Skills LLMS/Claude/Skills"          && git pull origin main
cd "Documents/Skills LLMS/Claude/Online Content"  && git pull origin main
```

This is non-negotiable. Skipping the pull causes stale-workspace bugs (the kind that wasted hours on 2026-05-04).

### At the END of any session that modified repo files:

Use the authenticated Git credential helper to push a reviewed branch and open a pull request.

Check the remote branch before handoff; follow the current reviewed publishing procedure. This document does not configure or authorize a session-end push hook.

## Working with git from Cowork sessions

The Documents folder is a Windows mount. Two gotchas:

1. **File mode noise:** Without `core.filemode false`, git treats every Windows-side file copy as "modified." Both clones already have this set. Don't undo it.

2. **`git status` cache staleness:** The `Write` tool sometimes preserves file mtimes in a way git doesn't detect. If `git status` shows clean when you know you edited a file, write the file via bash (`cat > file <<EOF ... EOF`) instead — that updates mtime properly. Or run `git update-index --really-refresh` to force git to re-stat.

## Don't go looking elsewhere

Old workspace location `C:\Users\Graeham Watts\skills\` is **deprecated** as of 2026-05-04. It was 70+ commits behind GitHub at migration time. If a future session lands there: stop, switch workspace to `Documents/Skills LLMS/Claude/`, and tell Graeham.

## Keeping local and remote in sync

All changes go through `git` directly. When you push from a fresh sandbox clone (the robust method above), the `Documents/Skills LLMS/Claude/...` clone falls behind — run `git pull` there to catch up when needed. If a leftover `.git/*.lock` from a flaky mount operation blocks git, delete it (`rm -f .git/*.lock`) and retry.
