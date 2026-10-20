# Current milestone

GOV-006: selectable existing repositories and patch bundles. ACCEPTED, IMPLEMENTED
under Eric's 2026-10-19 request for dropdowns instead of manually named paths.

Scope: searchable dropdowns with bounded local discovery, Browse fallback, session
choices, full selected paths, refresh/empty states and preview invalidation.
Preserve the GOV-005 patch engine, trust checks and explicit preview/apply boundary.
No persistent registry, network catalog, publication, binary rebuild or downstream
repository update is included. Existing ownership/dependency decisions are unchanged;
no new ADR is required for this UI adapter change.

Verification: focused UI discovery, browse, search and refresh checks; desktop
rendering; full generator, UI round-trip, patch and packaging suite; refreshed
framework checksums and clean-export verification.

Checkpoint: update project records, review/stage only this milestone, commit and
push the tracked branch and verify remote state. Report completion in this chat.
No next implementation milestone is accepted; publication and rollout still require
separate authorization. GOV-005 historical closure follows.

Delivery: all 32 tests passed, including the final implementation in a fresh
tracked-file export. Desktop discovery, preview and application to a disposable
repository passed. All 80 checksums and staged whitespace checks passed. Two focused
UI cases cover discovery/filtering, refresh, Browse/cancel and session reuse.
Temporary screenshots and verification scripts remain outside the repository.

## Previous milestone

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
