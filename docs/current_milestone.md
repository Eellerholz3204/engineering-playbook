# Current milestone

GOV-005: releaseable playbook patches for existing repositories. Accepted by Eric's
2026-10-16 request to provide a way to release patches to existing repos. GOV-004
remains implemented; its scope and verification are retained in the ledger.

Scope: local patch ZIP build/checksum tooling, explicit base/target snapshots,
no-write preview and conflict-checked apply, external backups with failure recovery,
installed-version receipt, preserved project documents/instructions, Builder's
existing-repository patch flow, and an artifact-only GitHub Actions build workflow.
Prepare and verify a local candidate patch demonstrating scratch-rule adoption.

Constraints: do not execute bundle code; do not force local edits, delete framework
files or change project source/tests. Preserve AGENTS.md and propose manual merges
in external scratch. Patch implementation and its behavior tests belong here.
No real downstream repo rollout, release publication, tag or merge is authorized.

Verification: package integrity/path validation, conflicts and no-write preview,
apply/reapply, preservation and metadata, injected write failure and rollback,
actual PowerShell generator output, UI creation-plan round-trip plus patch preview/
apply round-trip, desktop rendering, full suite and packaged allowlist checksums.

Checkpoint: update project docs, regenerate checksums, review/stage only GOV-005,
commit and push the current tracked branch, then verify remote state. No next
implementation milestone is accepted. Publishing the prepared artifact or applying
it to named downstream repositories is a separate scope decision.

Delivery: IMPLEMENTED. All 30 tests passed from a fresh tracked-file export, including
the patch contracts, existing generator/UI round-trips and packaged resource checks.
All 80 framework checksums passed. Actual desktop upgrade of a repository generated
from builder-v0.1.0 passed, including preservation and governance verification after
explicit instruction reconciliation. Candidate identity and closure are in the ledger.
