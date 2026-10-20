# Agent scratch workspaces — portable feature

Add external agent scratch workspaces and clear artifact-ownership rules without
replacing custom instructions or upgrading the whole framework. One patch supports
the reviewed installation families, including older Metis repositories. Temporary
diagnostics and tooling experiments stay outside the project; maintained product
code and tests remain with their owner.

Patch ID: `agent-scratch-workspaces-portable-v1`

Release tag: `playbook-patch-agent-scratch-workspaces-portable-v1`

## Use in Repository Builder

Restart the current source-launched Repository Builder, choose **Patch existing
repository**, select your repository, then **Check for patches**. Choose
**agent scratch workspaces (portable; preserves custom instructions)** and
**Preview patch**. Builder downloads and verifies it automatically; there is no
checksum to type. Expand the AGENTS.md section and review it before choosing
**Apply patch**. Checking, downloading and previewing never modify the repository.

This replaces the three older exact-baseline scratch patches in the published
selection. Those releases are retired to drafts, not repackaged or applied in reverse.
Their tags/assets and historical records are retained for recovery. Existing
installations remain unchanged until you explicitly apply a patch.

## Compatibility and preservation

Supported catalog/version pairs: schema 1 with playbook 3.0.1; schema 2 with
playbook 3.2.0, 3.2.1, 3.3.0 or 3.3.1. VERSION must agree with the catalog.
Compatibility checks only the feature destinations, not unrelated framework files
or repository names. Unknown catalog/version pairs require review.

The patch adds the workspace helper when absent, a namespaced policy and feature
receipt, and one clearly marked AGENTS.md section. Every existing instruction byte
is retained; custom project/organizational rules retain their authority. If AGENTS.md
is absent, the patch creates it with only this feature's instructions. It does not
establish any other missing governance entry points.

Framework VERSION, catalogs, checksums, project configuration, custom workflows,
source, tests and project documents stay unchanged. No tests or existing artifacts
are removed. The updater does not stage, commit, push, open PRs or execute ZIP code.
An existing equivalent helper is reused without changing its BOM or line endings.
Modified helper/policy/receipt files or edited/duplicate/incomplete marked sections
block rather than being overwritten. Compatible means structurally safe to add,
not semantic approval of custom rules: reconcile contradictory instructions explicitly.

This installs **scratch feature v1**, not a new framework version or desktop app.
It requires the schema-2 reader in current trusted source at `9ef4b37` or later.
Older packaged Builder 0.1.0 distributions cannot read this format; the source
launcher or trusted current CLI is required. Previously scratch-enabled repositories
may still add the dedicated policy/receipt/section, retaining their existing helper.

## Recovery and verification

Apply stores original changed files and a transaction journal in external scratch.
It rechecks the ZIP and repository inputs; changed inputs require a new preview.
Caught failures attempt rollback without overwriting concurrent edits. Interrupted
operations require journal/file review. Keep the backup until the change is accepted.
Reapplying a complete feature is a no-op. Invoke the installed helper for each task
and follow the project's normal verification and review process.

The implementation passed all 57 tests from a clean export, including actual
PowerShell generation, UI round-trips, both patch formats, packaging, archive/link
safety, instruction preservation, stale-input checks and rollback. The same artifact
passed read-only compatibility and disposable-copy apply/preservation/reapply checks
for all 15 audited installations. No real consumer application was part of publication.

## Artifact identity

- Exact source: `9ef4b378301489c86c3866b30dd3aa2e3bd9f398` (GOV-013).
- Schema 2, fixed `agent-scratch-workspace` feature version 1.
- ZIP: `agent-scratch-workspaces-portable-v1.zip`.
- ZIP SHA-256: `8ec723e90b79e792bb6e7ba0afa1d5ec7087e7305931484d7b3a9f0bbbb48b3e`.
- ZIP bytes are unchanged from the verified candidate; only its download filename
  and matching checksum-sidecar filename field have changed.
- The annotated release tag points to the exact implementation source, not a moving branch.

If needed, keep the [ZIP](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-agent-scratch-workspaces-portable-v1/agent-scratch-workspaces-portable-v1.zip)
and [checksum sidecar](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-agent-scratch-workspaces-portable-v1/agent-scratch-workspaces-portable-v1.zip.sha256)
together and Browse to the ZIP without extracting it. Do not use GitHub's generated
source archives as patches. Checksums establish integrity, not an independent
publisher signature. Use the trusted configured publisher.
