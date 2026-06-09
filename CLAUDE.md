# Cowork Workspace — Graeham's Setup

This is Graeham Watts's main Cowork workspace. Read this file FIRST in any session before doing repo work.

## Tokens & push map — quick reference

Master token doc: `C:\Users\Graeham Watts\Documents\Obsidian GitHub Credentials\README - Where my tokens live.txt`

| What | Local working copy | GitHub repo (push target) | Token file (read at push time only) |
|---|---|---|---|
| **Skills** (toolkit) | `Documents\Claude\Skills\` | `Graehamwatts/skills` | `Documents\Claude\Skills\github-token.txt` |
| **Online Content** (published HTML) | `Documents\Claude\Online Content\` | `Graehamwatts/online-content` → `graehamwatts.github.io/online-content/` | `Documents\Claude\Online Content\github-token.txt` *(same token as Skills)* |
| **Obsidian vault** (Property OS "second brain") | `Documents\Obsidian\` | `Graehamwatts/property-os` | `Documents\Obsidian GitHub Credentials\Obsidian Vault, GitHub token.txt` *(separate token; working copy at `Documents\Claude\Scheduled\property-os-daily-backup\github-pat.txt`)* |
| **PropCast** | `Documents\Claude\PropCast\` | (PropCast automation) | `Documents\Claude\PropCast\propcast-token-pat.txt` |

- **Skills + Online Content share ONE token.** The **Obsidian vault uses its own separate token.** Don't move any token file — automation reads them from these exact paths.
- Token files are gitignored / kept out of synced folders. If one leaks or lands in a repo, rotate it (steps in the master token doc above).

## GitHub publishing — push directly with git (do NOT use Composio)

Pushing to GitHub is done **directly with `git`** using the token in `github-token.txt`. Composio is not used in this workspace (it was an old approach) — do not reach for it.

Pattern:
- Owner: `Graehamwatts` · Branch: `main` · token from the `github-token.txt` inside the relevant clone
- `PAT=$(cat github-token.txt | tr -d '[:space:]')`
- `git push "https://${PAT}@github.com/Graehamwatts/<repo>.git" HEAD:main`

**Reliability tip (Windows mount):** the `Documents/Claude/...` folder is a Windows mount where git sometimes cannot unlink its own lock/temp files, leaving `.git/*.lock` behind. The robust way to push is to **clone the repo fresh into the sandbox (`/tmp`), copy in the changed files from Documents, commit, and push** — a clean filesystem, no lock cruft left in the Documents clone.

**Before pushing ANY file:** run the brand integrity check — block `02015066` (the wrong DRE); the only valid DRE is `01466876`. Keep `.github/workflows/` files out of routine commits (token is `repo` scope, not `workflow`).

## Deprecated skills — DO NOT USE

These skill names may appear in the available skills list because Cowork's server still registers them, but they are **deprecated** and must never be invoked. If you see one of these names, ignore it and use the replacement.

| Deprecated skill | Use instead | Why |
|---|---|---|
| `video-script-creation-engine` | `content-creation-engine` | Absorbed April 2026 per skill-deprecation-protocol |
| `social-media-analyzer` | `content-calendar` | Absorbed May 2026 |
| `video-prompt-builder` | `cinematic-hooks` | Consolidated |
| `html-email` | Publish HTML to the `online-content` repo via direct git | Replaced by direct git publishing |
| `github-skill-sync` | Direct git push from the `Documents/Claude/Skills` clone | Replaced by direct git push |

**Enforcement rule:** If the user asks you to use a deprecated skill by name, do NOT invoke it. Politely redirect to the replacement and explain the change in one sentence.

**Authoritative source of truth for skills:** `Documents/Claude/Skills/skills/` (this folder, synced to `Graehamwatts/skills` on GitHub). Cowork maintains an internal cache at `C:\Users\<user>\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\<org>\<account>\skills` that often contains stale or deprecated skill content due to upstream server sync. **Trust the Documents folder, not the cache.**

## CRITICAL: Always read skills from Documents, never from cache

**Before executing any skill, you MUST read the canonical SKILL.md from `Documents/Claude/Skills/skills/<skill-name>/SKILL.md` and use that as the authoritative source.** Your loaded skill list and any skill content Cowork has injected into your context may be a stale cached version. The Documents version is the source of truth.

This applies even when you "have" the skill loaded already — re-read the Documents version at the start of any task that uses a skill. Same for skill references and assets (use `Documents/Claude/Skills/skills/<skill-name>/references/<file>` not the cached version).

If the Documents version differs from what you appear to "know" about the skill, **trust the Documents version**. The cache is not the source of truth.

## Folder layout

```
Documents/Claude/                      ← THIS folder = your workspace root
├── Skills/                            ← clone of github.com/Graehamwatts/skills
│   ├── skills/                        (64 skill folders — the toolkit)
│   ├── assets/, docs/, scripts/
│   ├── github-token.txt               (gitignored — never commits)
│   └── .git/
│
├── Online Content/                    ← clone of github.com/Graehamwatts/online-content
│   ├── emails/                        (published HTML emails)
│   ├── dashboards/                    (weekly calendars)
│   ├── github-token.txt               (gitignored)
│   └── .git/
│
├── Obsidian/                          ← ACTUALLY at C:\Users\Graeham Watts\Documents\Obsidian\ (sibling, NOT inside Claude)
│   ├── 01 Team & Agents/, 02 Daily Notes/, 03 Listings/, 04 Clients/, 05 Marketing/
│   ├── AI Library/, Content Intelligence/, Instagram Saves/, Prop OS/, PropertyCast/
│   └── _Templates/, rules/            (full map: the `obsidian-vault` skill)
│
├── Artifacts/                         (Cowork-managed — DO NOT TOUCH)
├── Scheduled/                         (Cowork-managed — your scheduled tasks)
├── Projects/, Content/                (Cowork-managed — DO NOT TOUCH)
└── weekly-listing-update.skill        (a packaged .skill file — stray, safe to delete)
```

## Two repos, one token

There are two GitHub repos: **`Graehamwatts/skills`** (toolkit) and **`Graehamwatts/online-content`** (published HTML — emails, newsletters, dashboards). The same Personal Access Token works for both, stored in `github-token.txt` inside each clone (gitignored).

**Critical placement rule:** skills go to `Skills/`, published HTML content goes to `Online Content/`. Never put emails/newsletters/dashboards in `Skills/`. Skills are tools that PRODUCE online content; the outputs go to the other repo.

(A third repo, **`Graehamwatts/property-os`**, holds the Obsidian vault backup and uses its own separate token — see the token map at the top.)

## Obsidian vault & its GitHub push

- **Vault (local):** `C:\Users\Graeham Watts\Documents\Obsidian\` — a SIBLING of `Documents\Claude\`, **NOT** inside it. Verified as the real vault root (has the `.obsidian` config). Top folders: `01 Team & Agents`, `02 Daily Notes`, `03 Listings`, `04 Clients`, `05 Marketing`, `AI Library`, `Content Intelligence`, `Instagram Saves`, `Prop OS`, `PropertyCast`, `_Temp