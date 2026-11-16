# Service automation hardening cutover

Prepared 16 November 2026. Merge only after independent second-family review.

All service jobs request the `service-automation` environment. Configure it with
Graehamwatts approval, no self-approval, no admin bypass and only main allowed.
Approval is required on scheduled runs too; an owner must approve each run.

**The environment declaration alone does not contain repository secrets.**
Existing repository secrets remain available to workflows that omit the environment.
Using the private credential store, populate the environment with the seven existing
service secret names, validate availability without printing values, then delete the
repository-scoped equivalents in a coordinated cutover. GitHub cannot export secret
values. Never copy them through logs, files, prompts or this PR.

After merging, change the default workflow token to read-only. Write access is explicit
only for content-committing jobs and the postcard issue fallback. Checkout retains its
credential only for jobs that push. Changing the default before merge breaks current
Friday dashboard pushes.

Main can safely reject force pushes and deletion now. Requiring PRs for all main writes
also blocks scheduled dashboard/state commits and the PC's session-end auto-push.
Migrate those publishers to reviewed PRs before requiring PRs and CODEOWNERS review.
CODEOWNERS is advisory until that requirement is enabled.

Generation is deliberately paused: its existing output would publish recipient data.
Only postcard state markers are staged. Restore generation only after a private-output
change is reviewed. Credential repair and rotation require a separate secure operation.
No live email, CRM or n8n requests are needed for the local security tests.

Run tests with Python 3 and PyYAML:
`python -m unittest discover -s tests -p test_workflow_security.py`.
