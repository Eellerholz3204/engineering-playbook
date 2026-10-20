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

## GOV-006 — Repository and patch dropdowns, 2026-10-19

Accepted under Eric's request to replace manually named repository/ZIP paths with
dropdowns. Implemented searchable selectors with bounded local discovery, patch
ID/version labels, selected full paths, Browse, Refresh, empty-state guidance and
session choices. Search and selection changes invalidate prior review; changing
patches clears the old expected checksum. Stable input controls retain the filtering
subtree. Existing preview/apply and patch integrity policy remain in their owner.

Verification: all 32 tests passed in the working checkout and in tracked-file
exports; the final export passed in 144.260 seconds. Two focused UI tests cover
discovery, ignored non-patch ZIPs, empty/missing locations, Browse/cancel, session
reuse, refresh, filtering and disabled busy controls. Existing actual PowerShell
generation, UI plan round-trip, patch application/preservation and relocated package
checks passed. All 80 framework checksums and staged whitespace checks passed.
Desktop screenshots were inspected; discovery, preview and disposable apply passed.
Temporary scripts, screenshots and exports stayed in external task scratch.

Updated patch/application guidance, current milestone, roadmap, project status and
unreleased notes. No lasting architecture change or new ADR. Delivery: IMPLEMENTED.
No real downstream repository, prior candidate ZIP or packaged Builder binary was
changed; no patch publication or automatic network discovery is included. Source
launcher users restart Builder. No next implementation milestone is accepted.

Closure evidence: implementation commit
`3c63f68833df17c3a10b06cbe18b9f9cc60aa572` was pushed to
`origin/codex/governance-context-loading`. `git ls-remote` matched that exact HEAD
and the implementation checkpoint working tree was clean. This documentation-only
record follows on the same branch. Existing PR #1 remains the review vehicle;
no new PR was created.

## GOV-007 — First framework patch publication, 2026-10-19

Explicitly authorized by Eric after reviewing the local candidate and publication
gap. Scope: publish that exact candidate under a dedicated annotated source tag,
with ZIP/checksum assets, complete compatibility instructions and download-back
verification. No downstream apply, cleanup, binary rebuild or PR merge is included.

Prepared `scratch-workspace-2026-10.zip`, retaining the GOV-005 candidate's exact
SHA-256 `02953297c36b7d0da5398b182e0efebe8d8f08a4abb66170ccdb3059ccc2c253`.
Base commit `7b22dd7dcad44826c32cf7c98d76b93b6f01cc43` (3.2.1) and target
`dae80da38d4adb9b6db700fef16e45e5afa140e3` (3.3.0) were exported freshly.
Candidate baseline hashes and every payload byte matched those snapshots. All 30
target tests passed in 140.859 seconds; all 80 framework checksums passed. A fresh
3.2.1-generated repository passed preview, apply, preserved project content, no-op
reapply and governance checks after explicit instruction merge. Archive allowlist
and credential-pattern audit passed. One-release diagnostics stayed in scratch.

Release notes are in `docs/releases/scratch-workspace-2026-10.md`. No architecture
decision changed. Publication and remote verification are pending at this checkpoint.

Publication closure: [release](https://github.com/Eellerholz3204/engineering-playbook/releases/tag/playbook-patch-scratch-workspace-2026-10)
published at 2026-10-20 00:45:14 UTC (2026-10-19 local). Published as a framework
patch, not a desktop app update; no Latest designation was requested. Release notes
match the committed document. Assets were uploaded in draft, downloaded/verified,
then published and downloaded again over unauthenticated public HTTPS URLs.

- ZIP: `scratch-workspace-2026-10.zip`, 163185 bytes, asset ID `657849251`;
  SHA-256 `02953297c36b7d0da5398b182e0efebe8d8f08a4abb66170ccdb3059ccc2c253`.
- Sidecar: `scratch-workspace-2026-10.zip.sha256`, 96 bytes, asset ID `657849257`;
  SHA-256 `352bfaf6d3d65ebfa2936d33c4b4d001f51fbce7bbf6db1693e5ddd521152ec4`.
- Annotated tag: `playbook-patch-scratch-workspace-2026-10`, object
  `5f1caf73ca4a97f44ba820ffcfb1d3ea98187292`, peeled commit
  `dae80da38d4adb9b6db700fef16e45e5afa140e3`; local and remote identities matched.

Preparation commit `76a7eb24d251a2898496a29b9c1f6742a48b5a47` was pushed to
`origin/codex/governance-context-loading` and matched the remote branch. The
publication checkpoint working tree was clean. This documentation-only closure
follows on that branch; existing PR #1 remains the review vehicle. No new PR,
consumer changes, binary rebuild or merge occurred. Delivery: IMPLEMENTED.
No next accepted implementation milestone remains; downstream adoption is separate.

## GOV-008 — In-app patch discovery and downloads, 2026-10-19

Implemented explicit Check for patches and Download selected patch actions using
the fixed public GitHub publisher. Published stable ZIP/checksum pairs are listed;
drafts, prereleases, unsafe names and incomplete pairs are excluded. Requests use
HTTPS redirect restrictions, limits/timeouts, no credentials and no startup polling.
Downloads compare publisher checksum and optional GitHub digest, validate the full
archive and expose a complete pair atomically in the external content-addressed
cache. Offline selection restores the pinned digest. Corrupt entries are retained
for review, not overwritten. Consumer compatibility remains the existing preview
engine's responsibility; nothing downloads or applies automatically.

Verification: all 38 tests passed locally and from the final clean tracked-file
export in 136.717 seconds. Five maintained download tests and one additional UI
flow test cover the public feed, error/bounds contracts, invalid/interrupted
downloads, safe cache placement/reuse/tampering, offline digest and preview gating.
Existing actual PowerShell generation across all profiles, UI save/import round-trip,
patch preservation/recovery and relocated package generation passed. All 81 framework
checksums and staged whitespace checks passed. Live GitHub discovery/download of
the published first patch, desktop screenshots, checksum autofill, preview and
disposable old-baseline application passed. No permanent tests require network.

Updated public patch guide, Builder guide, catalog/checksums, domain map, status,
roadmap, milestone and unreleased notes. ADR GOV-008 records accepted trust/cache
boundaries. One-off verification scripts/screenshots remain external. Delivery:
IMPLEMENTED. No published release/tag, real consumer repository or packaged binary
changed. No next implementation milestone is accepted.

Closure evidence: implementation commit
`33c3e547ba79a58c8c69b57e6471fc4b39a7d099` was pushed to
`origin/codex/governance-context-loading`. `git ls-remote` matched the exact HEAD
and the implementation checkpoint working tree was clean. This documentation-only
record follows on that branch; existing PR #1 remains the review vehicle. No new
PR was created and no additional implementation milestone is accepted.

## GOV-009 — Unified patch selection and readable patch information, 2026-10-19

Accepted under Eric's request to remove the confusing published/local selector
split and manual hash field, and use the screen to explain patch purpose. One
selector now supports published and local patches. Published names omit the generic
prefix and asset filename; bounded release notes supply an introductory overview
and expandable original notes as inert text. Local patches show their manifest
summary. Preview downloads and verifies as needed, with separate Apply pinned to
the exact reviewed file/digest. Cache reuse is offline and checked against pinned
identity; changing releases or selections cannot reuse stale review. Local checksum
sidecars are used automatically, invalid sidecars rejected and absent ones optional.

Verification: all 40 working-checkout tests passed in 135.868 seconds; the final
cache-identity regression assertion also passed. Focused coverage protects selection,
notes, automatic download, errors, cache deduplication, stale identity invalidation,
sidecar validation and explicit apply gating. Live desktop verification used the
published scratch-workspace patch and a disposable old-generator repository: release
purpose/notes rendered, Preview downloaded automatically without project writes,
cached preview worked offline and Apply preserved project content. Screenshots and
one-off diagnostics remain in external task scratch. All 81 checksums refreshed.
Final clean tracked-file export: all 40 tests passed in 139.575 seconds, including
actual all-profile PowerShell generation, UI plan round-trip, patch preservation
and relocated packaged resources. Framework snapshot/checksum validation and staged
whitespace checks passed. Delivery: IMPLEMENTED; commit/push closure follows.

Updated guides, status, roadmap, current milestone and unreleased notes. No new ADR;
GOV-005/GOV-008 ownership and trust boundaries are unchanged. No published asset,
real consumer repository, packaged binary or PR merge changed. No next accepted
implementation milestone remains.

Closure evidence: implementation commit
`f76734eeac4606ee6f8997b2531723eb0692c93f` was pushed to
`origin/codex/governance-context-loading`. `git ls-remote` matched that exact HEAD
and the implementation checkpoint working tree was clean. This documentation-only
record follows on the same branch. Existing PR #1 remains the review vehicle;
no new PR was created and no next implementation milestone is accepted.

## GOV-010 — Blocked patch state and early-3.3.0 patch, 2026-10-19

Eric explicitly approved both clear blocked-state UI and publication of a compatible
scratch-workspace patch for the earlier 3.3.0 baseline. The prior patch's ten conflicts
are a baseline mismatch: all 76 installed framework files in the named consumer match
source `7dc6467`, not the original patch's 3.2.1 baseline. No consumer edits are required
to diagnose it. Preserve the first release and do not apply to real repositories.

Implemented a prominent Patch blocked explanation and conflict count, disabled primary
action through busy-state completion, and selection/refresh recovery. Prepared new
patch ID `scratch-workspace-early-330-2026-10`, base
`7dc6467b7c0482a048fe755dfea31356c56c3f72`, target
`dae80da38d4adb9b6db700fef16e45e5afa140e3`. Target payload is identical to the first
release. Both source snapshots historically carry version 3.3.0; the distinct artifact
and exact hashes define compatibility. No new framework implementation is released.

Candidate ZIP: 163112 bytes, SHA-256
`d08de17db25022f1f6384e2e7b29ca8c5acf14ae204e058aa1e7e044afb1144f`.
Sidecar SHA-256: `cdc90934aea440cc8bed0caa6a10894a4487cbb03e7db901fb32ce6dafe71024`.
Target snapshot's 30 tests passed from a fresh Git export in 135.958 seconds. Exact
baseline/target/allowlist audit, original-target payload comparison and private-key/token
pattern audit passed. Candidate preview against the real named repository is read-only
and has zero conflicts/22 changes. Disposable old-generator desktop preview/apply,
project preservation, no-op reapply and governance after explicit instruction merge
passed. A long QA folder hit Windows path limits; repeating from a shorter temporary
folder passed without a product workaround. All diagnostics/screenshots remain external.

All 41 current tests passed from the final clean tracked-file export in 137.019
seconds, including PowerShell generation, UI plan round-trip and packaging. All 81
current framework checksums and whitespace checks passed. Publication closure follows.
Updated patch/Builder guides, release notes and owning project records. Existing ADRs GOV-005/GOV-008 remain
valid; no new ADR. No real consumer apply, binary release or PR merge. No next accepted
implementation milestone remains.

GOV-010 publication closure: [release](https://github.com/Eellerholz3204/engineering-playbook/releases/tag/playbook-patch-scratch-workspace-early-330-2026-10)
published at 2026-10-20 03:18:12 UTC (2026-10-19 local), not a draft/prerelease and
not marked Latest. Draft assets were downloaded and verified before publishing;
public assets were then downloaded through Builder's unauthenticated HTTPS adapter.
Both matched the exact local bytes and GitHub digests above. Published notes match
the committed release document. Live Builder discovery selected the friendly early
3.3.0 title, downloaded and previewed against the real named repository with zero
conflicts/22 changes, without applying. The first release's notes and digests remain
unchanged. The named consumer's working tree remained clean.

- ZIP asset ID `658132684`, 163112 bytes; sidecar asset ID `658132683`, 107 bytes.
- Annotated tag `playbook-patch-scratch-workspace-early-330-2026-10`, object
  `83f8a292afde942b3e5e022f56c6efa14f722806`, peeled target
  `dae80da38d4adb9b6db700fef16e45e5afa140e3`; local/remote identities matched.
- Implementation/preparation commit `b743aae37fb8c79a3bdda8676acec0617d396cc5`
  was pushed to `origin/codex/governance-context-loading`; remote HEAD matched and
  the preparation checkpoint tree was clean. This documentation-only closure follows.

Delivery: IMPLEMENTED. Existing PR #1 remains the review vehicle; no new PR, merge,
consumer write or desktop binary release occurred. No next implementation milestone
is accepted. Restart the source-launched Builder and select the early-3.3.0 patch;
real application and subsequent instruction reconciliation remain explicit.

## GOV-011 — Legacy Metis scratch migration

ACCEPTED, CURRENT under Eric's approval to implement and publish a compatible
migration after both earlier patches conflicted with metis-engineering-playbook.
The reviewed installation contains a valid 51-file 3.2.1 snapshot plus five later
governance files. All 56 files match committed content at
`1dfdd6c3b22dea347284c7e4ec757d89d5233429` after read-only encoding comparison;
exact installed bytes, not normalized hashes, define the patch baseline. Existing
consumer changes are outside the framework and are preserved without application.

Implemented publisher-only `--base-additions` with explicit exact pins, validated
base snapshot and target allowlist membership. No inferred ownership, base override,
new patch schema or relaxed consumer matching. Promoted the reusable access/identity
startup/documentation requirements into target framework 3.3.1; no project-specific
identity facts are copied. Builder remains 0.1.0. ADR GOV-011 records the extension.

Focused verification: all 10 patch tests passed (69.122 seconds), including CLI
legacy build, BOM/CRLF exact matching, rejection of unsafe/invalid/overriding pins,
preservation and no-op reapply. Candidate audit matched 56 base and 82 target files;
real consumer read-only preview has zero conflicts and 61 changes. Existing version-1
reader compatibility passed. Desktop disposable preview/apply preserved project,
identity and unknown files, created no absent configuration, and passed governance
after explicit generic/Metis instruction reconciliation. Screenshots and diagnostic
scripts remain external; no real consumer files changed. Full-suite verification
and release identity/publication closure follow below.

GOV-011 prepublication verification: all 43 tests passed from the final clean
tracked-file export in 194.280 seconds, including actual PowerShell generation,
UI plan round-trip and relocated packaging. The initial run exposed a Windows
default-decoding mistake in the new assertion; explicit UTF-8 fixed that test and
the complete final run passed. All 81 checksums and staged whitespace checks pass.
The final ZIP and earlier QA candidate have identical manifests/payloads, matching
the target source exactly. Final-artifact desktop verification and existing version-1
reader compatibility passed again; no real consumer apply occurred.

- Artifact: `scratch-workspace-legacy-metis-2026-10.zip`, 174097 bytes.
- ZIP SHA-256: `d63068f7072bd70c6f988dafc459d0b4e764259571afc57b493f76deeeb4bc93`.
- Sidecar: 110 bytes; SHA-256 `c9ec25c91a01ce980152f354ac139e66e54c93fa880473773fac2866ae31ee99`.
- Target: framework 3.3.1, 82 files; baseline: 56 files (51 catalog + five explicit pins).
- Published asset/tag identities will be recorded after download-back verification.
