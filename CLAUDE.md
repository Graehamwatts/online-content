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

For a full pass on a specific piece of text or file (53-pattern scan, a 0-100 AI-tell score, or a named voice like `casual`/`professional`/`technical`/`warm`/`blunt`), invoke the `humanizer` skill (`Documents\Skills LLMS\Claude\Skills\skills\humanizer\`) directly. Upgraded 2026-08-19 from a 29-pattern base to Aboudjem/humanizer-skill (MIT), 53 patterns + voice profiles + scoring; same skill name, so nothing else needs to change to pick it up.

## 📬 2026-06-13 — Scheduled reports SEND, never just draft

**Standing rule (Graeham, 2026-06-13):** every recurring report / brief / reminder task must **actually send** its email so it lands in the inbox — do NOT leave Gmail drafts. Default recipients for internal reports are **Graeham (`graehamwatts@gmail.com`) + Adrian (`graehamwattsclientcare@gmail.com`)**, plus any task-specific recipients (John, Peter, Ellie, Maria) as TO/CC per that task's SKILL.md. This overrides any "draft only" wording inside an individual SKILL.md.

- **Send mechanism:** Gmail connector's *send* action (not draft); fallback = SMTP via `skills/switchy-engine/scripts/send_email.py` using the app password at `Documents\Skills LLMS\Claude\Skills\gmail-app-password.txt` (read at send time, never print). For GitHub-Action tasks, SMTP via repo secrets `GMAIL_USERNAME` + `GMAIL_APP_PASSWORD` + `BRIEF_RECIPIENTS` on `online-content`.
- **Daily Attribution Brief** now emails Graeham + Adrian every weekday 7:15 AM PT (GitHub Action `daily-attribution-brief.yml` — email step added + verified 2026-06-13). It both publishes the dashboard AND sends.
- **Exception — client-facing content stays review-first:** anything that goes to an actual client (CMA client section, listing emails) is still SENT to Graeham + Adrian for review, who forward to the client. "Send not draft" means internal reports reach the inbox; it does NOT mean auto-emailing clients.

## ⚡ 2026-06-09 architecture update — ONE skills folder, junctions everywhere

There is now exactly ONE physical copy of the skills toolkit: `Documents\Skills LLMS\Claude\Skills\skills\`. Everything else is a Windows directory junction pointing at it:

- `C:\Users\Graeham Watts\.claude\skills` → junction → `Documents\Skills LLMS\Claude\Skills\skills` (what Claude Code loads). Editing a skill in Documents is instantly live in Claude Code.
- Cowork's plugin cache `AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\...\skills` is a **REAL COPY, mirrored one-way** from Documents by the auto-push hook (robocopy /MIR). **⚠️ NEVER make the Cowork cache a junction** — tried 2026-06-09; Cowork's server reconciler deleted 63 skill files in Documents THROUGH the junction (twice) before it was caught. The cache must stay a disposable copy so Cowork can only trash its own copy. Its manifest.json was scrubbed of zombie/duplicate entries the same day.

**Consequences:** never "sync" skills by hand-copying folders; the hook mirrors the cache automatically at session end. If a zombie skill (video-script-creation-engine, social-media-analyzer, html-email, video-prompt-builder, github-skill-sync, graeham-*) reappears in the cache, run `Documents\Skills LLMS\Claude\Scheduled\FINAL-FIX-zombie-skills.ps1` — the quarterly-skills-audit scheduled task also checks for this. The auto-push hook has a WIPE GUARD: a mass deletion (>20 files) in the Skills repo is restored from git instead of being committed.

**Auto-push on session end:** a Claude Code `SessionEnd` hook (`~/.claude/hooks/auto-push-repos.ps1`, registered in `~/.claude/settings.json`) auto-commits and pushes BOTH the Skills and Online Content repos whenever a session ends, with the brand tripwire (02015066 block) enforced before any Skills push. Log: `~/.claude/auto-push.log`. Sessions no longer need to push manually — but pushing manually is still fine.

**Scheduled tasks migrated to Claude Code (2026-06-09):** the 14 real recurring tasks were registered in Claude Code's scheduler (`~/.claude/scheduled-tasks/`, visible in the app sidebar). Each registered task is a thin wrapper that reads its canonical SKILL.md from `Documents\Skills LLMS\Claude\Scheduled\<task>\SKILL.md` — keep editing those files as the source of truth. The Cowork-side copies of these tasks must be toggled OFF in Cowork's UI to avoid double-fires. `daily-attribution-brief` was NOT registered — it self-runs as a GitHub Actions cron on the online-content repo.

## Tokens & push map — quick reference

Master token doc: `C:\Users\Graeham Watts\Documents\Obsidian GitHub Credentials\README - Where my tokens live.txt`

| What | Local working copy | GitHub repo (push target) | Token file (read at push time only) |
|---|---|---|---|
| **Skills** (toolkit) | `Documents\Skills LLMS\Claude\Skills\` | `Graehamwatts/skills` | `Documents\Skills LLMS\Claude\Skills\github-token.txt` |
| **Online Content** (published HTML) | `Documents\Skills LLMS\Claude\Online Content\` | `Graehamwatts/online-content` → `graehamwatts.github.io/online-content/` | `Documents\Skills LLMS\Claude\Online Content\github-token.txt` *(same token as Skills)* |
| **Obsidian vault** (Property OS "second brain") | `Documents\Obsidian\` | `Graehamwatts/property-os` | `Documents\Obsidian GitHub Credentials\Obsidian Vault, GitHub token.txt` *(separate token; working copy at `Documents\Skills LLMS\Claude\Scheduled\property-os-daily-backup\github-pat.txt`)* |
| **PropCast** | `Documents\Skills LLMS\Claude\PropCast\` | (PropCast automation) | `Documents\Skills LLMS\Claude\PropCast\propcast-token-pat.txt` |

- **Skills + Online Content share ONE token.** The **Obsidian vault uses its own separate token.** Don't move any token file — automation reads them from these exact paths.
- Token files are gitignored / kept out of synced folders. If one leaks or lands in a repo, rotate it (steps in the master token doc above).

## GitHub publishing — push directly with git (do NOT use Composio)

Pushing to GitHub is done **directly with `git`** using the token in `github-token.txt`. Composio is not used in this workspace (it was an old approach) — do not reach for it.

Pattern:
- Owner: `Graehamwatts` · Branch: `main` · token from the `github-token.txt` inside the relevant clone
- `PAT=$(cat github-token.txt | tr -d '[:space:]')`
- `git push "https://${PAT}@github.com/Graehamwatts/<repo>.git" HEAD:main`

**Reliability tip (Windows mount):** the `Documents/Skills LLMS/Claude/...` folder is a Windows mount where git sometimes cannot unlink its own lock/temp files, leaving `.git/*.lock` behind. The robust way to push is to **clone the repo fresh into the sandbox (`/tmp`), copy in the changed files from Documents, commit, and push** — a clean filesystem, no lock cruft left in the Documents clone.

**Before pushing ANY file:** run the brand integrity check — block `02015066` (the wrong DRE); the only valid DRE is `01466876`. Keep `.github/workflows/` files out of routine commits (token is `repo` scope, not `workflow`).

## Deprecated skills — DO NOT USE

Cowork's server can re-register these names in the plugin cache even after cleanup (cache last swept 2026-07-28; re-run `Scheduled/FINAL-FIX-zombie-skills.ps1` if one resurfaces — watch for a stale DRE like `02015066`, which is always wrong). If one appears, don't invoke it — use the replacement instead.

| Deprecated | Use instead |
|---|---|
| `video-script-creation-engine` | `content-creation-engine` |
| `social-media-analyzer` | `content-calendar` |
| `video-prompt-builder` | `cinematic-hooks` |
| `html-email` | direct git publish to `online-content` |
| `github-skill-sync` | direct git push |

**Source of truth is always `Documents/Skills LLMS/Claude/Skills/skills/<name>/SKILL.md`**, never the Cowork cache — re-read from there before executing any skill, even one already loaded, since your loaded context may be stale.

## Folder layout

Workspace root: `Documents/Skills LLMS/Claude/`. Contains clones of the `skills` and `online-content` repos (run `ls` for current structure — skill count and subfolder names drift, don't trust a hardcoded list here), plus Cowork-managed dirs (`Artifacts/`, `Scheduled/`, `Projects/`, `Content/` — do not touch). The Obsidian vault is a SIBLING at `C:\Users\Graeham Watts\Documents\Obsidian\`, not nested here — see the `obsidian-vault` skill for its internal layout.

## Two repos, one token

There are two GitHub repos: **`Graehamwatts/skills`** (toolkit) and **`Graehamwatts/online-content`** (published HTML — emails, newsletters, dashboards). The same Personal Access Token works for both, stored in `github-token.txt` inside each clone (gitignored).

**Critical placement rule:** skills go to `Skills/`, published HTML content goes to `Online Content/`. Never put emails/newsletters/dashboards in `Skills/`. Skills are tools that PRODUCE online content; the outputs go to the other repo.

(A third repo, **`Graehamwatts/property-os`**, holds the Obsidian vault backup and uses its own separate token — see the token map at the top.)

## Obsidian vault & its GitHub push

- **Vault (local):** `C:\Users\Graeham Watts\Documents\Obsidian\` — a SIBLING of `Documents\Skills LLMS\Claude\`, **NOT** inside it. Verified as the real vault root (has the `.obsidian` config). Top folders: `01 Team & Agents`, `02 Daily Notes`, `03 Listings`, `04 Clients`, `05 Marketing`, `AI Library`, `Content Intelligence`, `Instagram Saves`, `PropIQ` (renamed from `Prop OS` 2026-06-09), `PropertyCast`, `_Templates`, `rules`. Plain markdown — no token needed to read/write locally.
- **GitHub credentials (local):** `C:\Users\Graeham Watts\Documents\Obsidian GitHub Credentials\` — a SIBLING too, OUTSIDE every repo. Contains `Obsidian Vault, GitHub token.txt` (the PAT) and `README - Where my tokens live.txt` (Graeham's own token-location map — treat that README as the source of truth for where each token lives).
- **Vault → GitHub:** the vault is pushed to the **`Graehamwatts/property-os`** repo using the separate **`Obsidian Vault`** token (see token map up top) — via the `property-os-daily-backup` scheduled task (nightly ~11:09 PM) and the `property-os-sync` skill. This is a DIFFERENT token from the shared skills/content one.
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

```bash
# In whichever repo you modified:
git add <files>
git commit -m "Clear, specific message"
PAT=$(cat github-token.txt | tr -d '[:space:]')
git push "https://${PAT}@github.com/Graehamwatts/<repo>.git" main
```

There is no auto-push. Every change requires an explicit push before the session ends.

## Working with git from Cowork sessions

The Documents folder is a Windows mount. Two gotchas:

1. **File mode noise:** Without `core.filemode false`, git treats every Windows-side file copy as "modified." Both clones already have this set. Don't undo it.

2. **`git status` cache staleness:** The `Write` tool sometimes preserves file mtimes in a way git doesn't detect. If `git status` shows clean when you know you edited a file, write the file via bash (`cat > file <<EOF ... EOF`) instead — that updates mtime properly. Or run `git update-index --really-refresh` to force git to re-stat.

## Don't go looking elsewhere

Old workspace location `C:\Users\Graeham Watts\skills\` is **deprecated** as of 2026-05-04. It was 70+ commits behind GitHub at migration time. If a future session lands there: stop, switch workspace to `Documents/Skills LLMS/Claude/`, and tell Graeham.

## Keeping local and remote in sync

All changes go through `git` directly. When you push from a fresh sandbox clone (the robust method above), the `Documents/Skills LLMS/Claude/...` clone falls behind — run `git pull` there to catch up when needed. If a leftover `.git/*.lock` from a flaky mount operation blocks git, delete it (`rm -f .git/*.lock`) and retry.
