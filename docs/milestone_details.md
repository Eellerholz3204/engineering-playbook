# Milestone ledger

## GOV-001 â€” Governance context loading, 2026-09-26

Implemented generic and Metis startup blocks, installed reading procedure, catalog
integration, instruction preservation and a read-only structural verifier.
Verification: all 18 generator, UI and packaging regression tests passed; the
Metis UI save/import round-trip also passed after its added assertion. Actual
PowerShell generation covers all seven profiles and the Metis option. Packaged
allowlist copy and all 75 checksums passed. Diff whitespace check passed.
Existing Metis rollout is additive; no project semantics or runtime are changed.

The nine existing Metis repositories adopted the v1 bundle locally; seven have
open PRs and two have no remote. Exact identities are maintained in the central
[Metis rollout ledger](https://github.com/metis-health-2023-KLL/metis-engineering-playbook/pull/255).
Hosted Codex Control CI exposed stricter import/line-length rules. The shared
checker was formatted at source, passed that repository's Ruff configuration
and passed its two focused regression tests before propagation.

## GOV-002 — Central model and reasoning-effort routing, 2026-10-02

Added a capability-based routing policy to the canonical playbook and a compact
rule to the generated generic AGENTS.md block. Routing sets minimum tiers by task
type, names escalation triggers, permits repository-specific higher minimums, and
does not bind the normative policy to transient model versions. Added generated
instruction regression assertions. No downstream repositories were edited.
Verification: all 18 unit/integration tests passed, including actual PowerShell
repository-generation coverage; all 75 framework checksums refreshed; `git diff
--check` passed. Commit and tracked-branch remote state are recorded at milestone
closure.

## GOV-003 — Installed model-routing authority, 2026-10-02

Moved the full model-routing policy into mandatory `GOVERNANCE_CONTEXT.md` and
changed generated AGENTS.md to reference its installed path. Kept a pointer in
`ENGINEERING_PLAYBOOK.md`; it is optional in some installed repositories. Added
regression assertions against generated root guidance and installed policy.
No downstream repositories were edited. Verification: all 18 tests passed, all
75 framework checksums refreshed, and `git diff --check` passed. Commit and
tracked-branch remote state are recorded at milestone closure.

## GOV-004 — External agent workspaces and artifact ownership, 2026-10-16

Implemented a shared external task-workspace helper, automatic creation for all
seven profiles and Builder's review explanation. Added installed startup rules,
blocker classification, artifact promotion, test ownership and scratch-independent
verification. Existing configuration fields and project-document preservation remain
unchanged. Governance bundle and framework checksums include the new helper.

Verification: all 22 tests passed locally and again from a fresh tracked-file export
without local ignored artifacts. Coverage includes actual PowerShell generation,
Windows PowerShell/PowerShell 7 helper lifecycle checks, invalid paths and directory
links, UI save/import followed by creation, reconciliation preservation and creation
from a relocated packaged allowlist. All 76 framework checksums passed. Desktop
screens rendered and creation completed; QA artifacts stayed in external scratch.
Additional Windows PowerShell 5.1 repository generation passed. Staged diff review
found no scratch artifacts or dependencies; `git diff --check` passed. ADR GOV-004
records the accepted ownership and workspace decision. Delivery: IMPLEMENTED.

Scope excludes downstream cleanup, test deletion, automatic scratch removal, merge,
binary rebuild and release. Next committed implementation milestone: none.

Closure evidence: implementation commit `05e28e4d7613e7efbb6724ed9a2292c0664c5f9c`
(`feat: isolate agent scratch work from project deliverables`) was pushed to
`origin/codex/governance-context-loading`. `git ls-remote` matched that exact HEAD;
the implementation checkpoint working tree was clean. This documentation-only
delivery record follows on the same branch. Existing PR #1 remains the review
vehicle; no new PR was created. No additional implementation milestone remains.

## GOV-005 — Patch delivery to existing repositories, 2026-10-16

Implemented offline ZIP/checksum production, read-only preview, conflict-checked
apply, per-file atomic replacement, external backups/journal and caught-failure
rollback. A shared engine serves CLI and Builder. It executes no bundle code and
performs no consumer Git operations. Existing project configuration retains local
fields while recording version/last-patch identity; project content and AGENTS.md
are preserved. Suggested instruction blocks stay with external backups for review.
Added the artifact-only GitHub Actions build workflow and PATCH_RELEASES.md guide.
ADR GOV-005 records the delivery, ownership and recovery boundaries.

Verification: eight focused patch tests passed; all 30 tests passed locally and
again from a fresh tracked-file export after the Unicode-path correction. Coverage
includes checksum/path tampering, duplicate entries, linked destinations, conflicts,
no-write preview, apply/reapply, injected write-failure rollback, metadata and project
preservation, CLI against actual generated repositories, and Builder preview/apply.
Existing all-profile PowerShell generation, UI save/import and packaging checks pass.
All 80 framework checksums and `git diff --check` passed.

An actual desktop upgrade used a disposable repository created by the released
`builder-v0.1.0` generator, base commit `7b22dd7dcad44826c32cf7c98d76b93b6f01cc43`
(playbook 3.2.1). The 3.3.0 target preserved project files and local instructions.
Governance verification correctly reported the preserved old instruction block,
then passed after the documented explicit merge in the disposable repository.
Desktop screenshots and diagnostic output stayed in external task scratch.

Candidate: `scratch-workspace-patch-rc2.zip`, patch ID `scratch-workspace-2026-10`.
ZIP SHA-256: `02953297c36b7d0da5398b182e0efebe8d8f08a4abb66170ccdb3059ccc2c253`.
The ZIP and checksum sidecar are prepared locally; publishing remains unauthorized.
This candidate targets the exact released 3.2.1 snapshot, not arbitrary modified
installations. Additional baselines need separately tested bundles or reconciliation.
The Actions workflow was not dispatched; its packaging command was verified locally.
No real downstream repositories, packaged app binaries, tags or releases changed.

Delivery: IMPLEMENTED. Implementation commit
`dae80da38d4adb9b6db700fef16e45e5afa140e3` was pushed to
`origin/codex/governance-context-loading`; `git ls-remote` matched that exact HEAD
and the implementation checkpoint working tree was clean. The candidate payload
was rechecked against the committed framework and matched exactly. This
documentation-only delivery record follows on the same branch. Existing PR #1
remains the review vehicle; no new PR was created.
Next accepted implementation milestone: none. Publication and rollout remain explicit.
