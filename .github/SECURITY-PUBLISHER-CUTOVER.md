# Separate publisher / main-protection / secrets cutover plan

Not implemented by this PR. Do not enable a blanket main PR requirement while
current publishers push directly. Do not move repository secrets into the
unattended environment before the main publication controls are ready.

GitHub's branch PR requirement applies to a branch, not selected file paths.
CODEOWNERS identifies owners for .github/** and scripts/** but does not enforce
reviews on direct pushes. Public-repository push-path restrictions are not a
substitute for this coordinated plan.

1. Inventory all direct publishers, including the PC session hook, dashboard jobs,
   postcard state markers and manual tools. Preserve mail/watchdog cadence while
   choosing how unpublished state stays durable and avoids duplicate emails.
2. In a separately reviewed change, convert direct content/state publishers to
   branch + PR delivery. Define who approves and merges, and acceptable delay
   before Pages updates. This changes the owner's publication flow and requires
   explicit manager coordination; it is intentionally absent from this fix PR.
3. Prepare a main-wide PR rule with an owner code review for .github/** and
   scripts/**, stale review invalidation and no general writer bypass. With a
   sole owner, owner-authored PRs need an explicitly documented PR-only admin
   bypass after independent model-family review; never an always/direct-push
   bypass. Record that exception rather than pretending owners can approve their
   own GitHub PRs. Maintain the separate no-force/no-deletion ruleset.
4. Coordinate activation of the publisher changes and PR rule. Recheck all
   workflows and every repository file they execute, including local helpers and
   configuration, before granting the unattended environment credentials.
5. Using a secure owner-entry prompt, provision only needed secrets into each
   service environment, resolve the missing POSTCARD_RECIPIENTS explicitly,
   verify availability without printing values, then remove repository-scoped
   equivalents in the same controlled window. GitHub cannot export secret values.
6. Only once that plan is ready, set default_workflow_permissions=read, keeping
   can_approve_pull_request_reviews=false and explicit per-job write grants.
   Verify Pages, mail, CRM reports, n8n watchdog, marker persistence and manual
   owner approval. Never send a live message as a security test without authority.
7. Run the fleet lesson search immediately before each settings change, record
   before/after and read-back. Roll back by a reviewed additive change, never by
   force push. Stop if a live flow or unexpected account/billing action is needed.

Reference: GitHub rules and CODEOWNERS documentation:
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
