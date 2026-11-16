# Automation environment design and staged secret cutover

Updated 16 November 2026 after Gemini review. This PR can merge after re-review
without changing existing dashboard/state publication or moving secrets.

## Environment selection in this PR

- `schedule` jobs use `service-automation-scheduled`: only the main branch is
  deployable, no required reviewers, admin bypass disabled. This includes the
  four active schedules and the already-disabled Monday CRM report if re-enabled.
- `workflow_dispatch` jobs use `service-automation`: only main, reviewer
  Graehamwatts, admin bypass disabled, **prevent_self_review=false**. Both actor
  and triggering actor must be Graehamwatts. The owner can explicitly approve
  their own dispatched run. This is a deliberate human confirmation gate, not
  separation of duties; one owner cannot provide two independent identities.
- Postcard concurrency includes event type. A manual run waiting for approval
  cannot hold the scheduled-run lock. Scheduled runs still serialize together.

The manual self-review setting changes explicitly from true to false to remove
the one-owner approval deadlock. Schedules no longer request human approval.
Neither environment contains secrets yet. The main ruleset still blocks deletion
and force pushes; CODEOWNERS review is **not enforced**. We do not claim that
main-scoping alone makes unattended service secrets safe from repository writers.

## Existing secrets remain a known risk

Seven repository-scoped service secrets remain available to repository writers.
They have not been read, copied, deleted or moved. The environment declarations
alone cannot stop a writer adding an environment-free workflow on another branch.
The separately coordinated migration is documented in
[SECURITY-PUBLISHER-CUTOVER.md](SECURITY-PUBLISHER-CUTOVER.md). Its review and
publication requirements are gates for **that later cutover**, not this fix PR.

`POSTCARD_RECIPIENTS` is referenced but absent from repository and both service
environment secret lists. The postcard scripts currently fall back to the same
built-in recipients as before. No new recipient choice is made by this PR. The
owner must explicitly provision/confirm it through the later secure prompt; do
not silently substitute BRIEF_RECIPIENTS or paste addresses/credentials into chat.

Keep the default workflow token at its existing write setting until the secret
plan is ready. Before this PR merges, the Friday publisher still inherits write
permission. After merge all ten workflows declare permissions explicitly, which
removes that particular token-default dependency; the coordinated cutover still
must verify other publishers before changing the default. PR-review approval
by the token remains disabled.

## Public output and retired templates

Reminder and generator markers store recipient counts, never recipient lists.
Recipient addresses are not printed in service success/dry-run messages. No
existing marker recipient fields were found in the current checkout. Generator
mode stays paused as in the first PR revision; removing the known marker leak
alone does not authorize model-generated content publication.

The three old workflow templates are inert YAML documents with no jobs/triggers.
The retired daily script no longer exports untrusted source labels in its
single-line subject output. History is retained; see the implementation report
for historical exposure inventory. New automation requires a fresh review.

Run offline checks with Python and PyYAML:
`python -m unittest discover -s tests -p test_workflow_security.py`.
