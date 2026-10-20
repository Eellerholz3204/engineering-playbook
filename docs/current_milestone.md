# Current milestone

GOV-009: one patch selector with automatic downloads and readable patch information.
ACCEPTED, IMPLEMENTED under Eric's request to remove duplicate patch selectors and
manual checksum entry and explain each patch in the available screen space.

Scope: unify published/local choices; download and verify as part of explicit
Preview; show friendly release titles, purpose and expandable release notes;
automatically read local sidecars/cache pins. Keep separate Apply, unchanged patch
engine, fixed publisher and external cache boundaries. Existing ADRs remain valid.
No published assets, real consumer repos, packaged binaries or PR merge are in scope.

Verification: focused UI/cache/notes contracts, real published patch desktop flow
using a disposable old-baseline repo, full suite including PowerShell generation,
UI plan round-trip and packaging, clean tracked-file export and refreshed checksums.
Checkpoint: synchronize project records, commit/push the tracked branch and verify
remote state. Report here; no next implementation milestone is authorized.

Delivery: all 40 tests passed locally and from the clean tracked-file export
(139.575 seconds). Actual PowerShell generation, UI plan round-trip, packaging,
live desktop published-patch download/notes, offline reuse and disposable apply
passed. All 81 checksums and staged whitespace checks passed. QA artifacts stayed
outside the checkout. Restart the source-launched Builder; no binary release or
real consumer change occurred. Commit/push closure is recorded in the ledger.

## Previous milestone: GOV-008

GOV-008: check for and download published patches in Repository Builder. ACCEPTED,
IMPLEMENTED under Eric's 2026-10-19 request to eliminate manual GitHub downloads.

Scope: explicit online check, published stable ZIP/checksum pair selection,
validated downloads to an external persistent cache, offline cached selection,
network/empty/error states, and unchanged explicit preview/apply. Use the fixed
public source Eellerholz3204/engineering-playbook without credentials or startup
network requests. No consumer application, published-asset changes, PR merge,
binary rebuild or new release is included. ADR GOV-008 records trust/cache boundaries.

Verification: focused network/discovery/cache/UI contracts, real release download,
desktop render/preview with a disposable old-baseline repo, complete generation,
UI plan round-trip and packaging suite from a clean export, and updated checksums.
Checkpoint: update project records, stage only owned changes, commit/push current
tracked branch and verify remote state. Report in this chat. No next milestone
or human decision beyond this scope is pending; downstream apply remains explicit.

Delivery: all 38 tests passed locally and in the final clean tracked-file export
(136.717 seconds). Live public release discovery/download, checksum selection,
desktop rendering, preview and disposable apply passed. All 81 framework checksums
and staged whitespace checks passed. No real downstream repository or published
release changed. Source-launched Builder users restart to load this feature;
packaged binaries still need a separate build/release.

## Previous milestone: GOV-007

GOV-007: publish the first framework patch. ACCEPTED, IMPLEMENTED under Eric's explicit
2026-10-19 approval to publish the prepared first patch release.

Scope: verify the existing candidate unchanged, retain exact baseline/target source
identities, publish a dedicated annotated tag and GitHub release with the ZIP,
checksum and instructions, download back the assets and verify remote identities.
Target remains playbook 3.3.0 at `dae80da`; no version bump or rebundling is needed.
No Builder binary rebuild, PR merge, downstream apply or cleanup is authorized.

Verification: complete target-snapshot suite from a clean Git export; candidate
payload and baseline against committed snapshots; disposable old-generator upgrade,
preservation, reapply and governance reconciliation; release asset and tag verification.
Checkpoint: commit/push release documentation on the existing tracked branch,
publish only after checks pass, then record publication evidence and final Git state.
Report in this chat. No new ADR or next implementation milestone is required.

Delivery: published `playbook-patch-scratch-workspace-2026-10` at
2026-10-20 00:45:14 UTC (2026-10-19 local). All 30 target-snapshot tests passed;
exact source/candidate checks and a disposable old-generator upgrade passed.
Both public downloads matched their expected checksums and published notes matched
the committed instructions. The annotated remote tag resolves to `dae80da`.
No downstream repositories were changed. See the release notes and ledger for
asset URLs, complete identities and publication evidence.

## Previous milestone: GOV-006

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
