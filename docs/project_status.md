# Project status

## GOV-015 — 2026-10-20, patch-choice deduplication

Implemented content-based display grouping for local, cached and published copies.
The previous selected-local exception reproduced the reported two-choice display.
The picker now retains that source/key but shows one entry with the matching
published title and notes. Renamed byte-identical copies also merge; distinct or
unverifiable contents remain separate. Preview/Apply validation is unchanged.

All 15 focused UI tests and the real feature CLI/Builder preview/apply contract pass.
Live public-feed desktop verification reproduced a selected cached ZIP and confirmed
one compatible choice, published notes, separate preview/apply, preserved custom
instructions and unchanged framework version on a disposable project. Screenshot
inspection passed. All 59 tests passed from the clean staged-file export in 195.603
seconds, with no skips, including actual PowerShell generation and packaging.
All 82 checksums validate; export and working framework bytes match. Delivery:
IMPLEMENTED. Versions remain framework 3.3.1 / Builder 0.1.0 on the existing tracked
`codex/governance-context-loading` branch. Commit/push closure follows.
No release, real consumer, desktop binary or architecture decision changes.
Restart source-launched Builder and Check for patches to load the corrected picker.
No next implementation milestone is accepted.

## GOV-014 — 2026-10-20, portable patch published; older choices retired

The [portable scratch feature](releases/agent-scratch-workspaces-portable-v1.md)
is published from exact source `9ef4b37`. All 57 tests passed from that clean export
in 180.910 seconds. Published ZIP and sidecar match the verified candidate and GitHub
digests. Builder's live Check for patches, automatic verified download and preview
passed on a disposable custom 3.2.0 project with one compatible choice and no writes.

The original, early-330 and legacy-Metis releases are recoverable drafts; their
tags, asset identities and notes are unchanged. Their exact local cache entries
were moved to external `portable-patch-publication/retired-cache/` scratch.
Restart source-launched Builder, select the repository, Check for patches and
Preview the portable choice. Applying still requires the user's separate action.
Existing consumer installations and the packaged app release are unchanged.
Versions remain framework 3.3.1 / Builder 0.1.0; this installs only scratch feature v1.
Final publication records and refreshed documentation checksums are complete;
all 82 checksums and whitespace checks pass. This closure uses the same tracked
branch. No new PR, merge or next implementation milestone is authorized.

## GOV-013 — 2026-10-20, portable scratch feature implemented

Implemented a fixed schema-2 additive recipe alongside unchanged schema-1 snapshot
patches. One bundle covers catalog schema 1 / 3.0.1 and schema 2 / 3.2.0, 3.2.1,
3.3.0, 3.3.1. Only the helper, namespaced policy/feature receipt and an append-only
marked AGENTS.md section are installed. Custom instructions retain every original
byte and their authority; semantic conflicts still need explicit reconciliation.
Framework VERSION, manifests, project configuration, workflows and documents stay
unchanged. Feature-local conflicts block; unrelated framework changes do not.

Read-only inspection of 15 normal installed repositories found all compatible.
Application, byte-preservation and repeat-application checks passed on disposable
copies of those installations, including all nine primary Metis checkouts and
older 3.0.1/3.2.0 consumers. Hidden historical checkouts and excluded athena_dbt were
not audited. No real consumer was changed. These are migration contract checks,
not execution of each consumer's entire product suite or semantic approval of rules.

Ten focused contracts passed, including CLI/Builder round-trip, verified download
cache, supported families, missing AGENTS/config, encoding preservation, modified
feature/block refusal, archive scope, stale preview, rollback and Windows junctions.
Actual Flet desktop rendering/preview/apply through the app-owned test harness passed;
expanded instruction preview and unchanged-version success screenshots were inspected.
Native Windows input automation lost its target window; no delivery depends on it.
All diagnostics/screenshots/candidate assets remain outside the source checkout.
All 57 tests passed from the final clean tracked-file export in 243.062 seconds,
without skips. Actual PowerShell generation, UI round-trips, both patch formats and
relocated packaging passed. All 82 checksums passed; exported framework bytes equal
the working source, and the candidate manifest/payload match the final recipe.
The final read-only/disposable-copy audit again passed for all 15 installations.
Implementation `9ef4b378301489c86c3866b30dd3aa2e3bd9f398` was pushed to
`origin/codex/governance-context-loading`; remote HEAD matched and the checkpoint
tree was clean. This documentation-only closure follows on the same branch.

Branch remains `codex/governance-context-loading`; versions remain framework 3.3.1 /
Builder 0.1.0. ADR GOV-013 records the additive write boundary. The candidate is local
and unreleased; existing releases and app binaries are unchanged. Restart the current
source Builder and Browse to the local ZIP to preview. Publication, consumer apply
and PR merge remain separate decisions; no next milestone is accepted.

## GOV-012 — 2026-10-20, compatibility selection implemented

Builder now classifies patches for the selected repository using existing full
archive/checksum validation and read-only file comparison. Compatible patches sort
first; incompatible choices are hidden unless Show all is enabled or explicitly
selected. Already-applied and failed checks remain visible. Progress, stop-after-
current-check and refresh/retry are supported. Scans never establish Apply approval;
Preview rechecks current files, updating labels/counts if a prior result is stale.

All 47 tests passed from the final clean tracked-file export in 161.019 seconds,
including actual PowerShell generation, UI plan round-trip and packaging. All 81
checksums and staged whitespace checks passed. Real desktop checks used all three
published releases: correct classification/filtering, separate disposable apply,
same-target receipt distinction and offline refresh passed. Independent disposable
fixtures for all three released baselines each selected only their matching patch.
Scans made no project writes. Temporary QA scripts/screenshots stayed outside Git.

Unreleased source change; version labels remain framework 3.3.1 / Builder 0.1.0.
No published release, real consumer repository or desktop binary is changed.
Branch: `codex/governance-context-loading`; ADR GOV-012 records the interaction policy.
Implementation commit `b8b940dc4e337b73a31d34350acfc1bd840ba985` was pushed and
matched remote HEAD, with a clean checkpoint working tree. This documentation-only
closure follows. No next accepted milestone remains; source-launched
Builder users restart to load the update.

## GOV-011 — 2026-10-19, legacy migration published and verified

Published a separately approved release for metis-engineering-playbook's older
3.2.1 installation: 51 checksummed files plus five later governance assets. The
baseline content matches committed framework at `1dfdd6c3b22dea347284c7e4ec757d89d5233429`
after read-only BOM/line-ending comparison; release pins retain exact installed
bytes. Unrelated consumer work remains untouched. Publisher build now accepts
reviewed additional baseline pins without changing consumer hash matching. Target
3.3.1 preserves access/identity startup and documentation requirements; Builder
remains 0.1.0. All 43 tests passed from the final clean export in 194.280 seconds,
including PowerShell generation, UI plan round-trip and packaging. All 81 checksums,
old-reader compatibility and final-artifact desktop/disposable preservation checks
passed. Real consumer read-only preview has zero conflicts and 61 changes.
The [legacy release](https://github.com/Eellerholz3204/engineering-playbook/releases/tag/playbook-patch-scratch-workspace-legacy-metis-2026-10)
was published at 2026-10-20 03:41:43 UTC (2026-10-19 local). Draft/public download-back,
notes/digests and live Builder discovery/download/read-only preview passed. Both
previous releases are unchanged. Implementation `f6013bc5ce4b0df0103847f8d7b63ecdd5c233de`
and release notes `bc757d7aa6bf834f92cf74404b2f3889229ed8a7` were pushed and verified;
the annotated remote tag resolves to the implementation. This documentation-only
closure follows. Delivery: IMPLEMENTED. No real consumer apply, binary release or
PR merge occurred; no next accepted milestone remains. Branch remains
`codex/governance-context-loading`; existing PR #1 remains the review vehicle.

## GOV-010 — 2026-10-19, published and verified

Implemented explicit Patch blocked messaging, conflict count/baseline explanation
and disabled primary action. The blocked state survives the end of the busy cycle;
selection changes or Refresh restore preview. Existing patch validation is unchanged.

Published `scratch-workspace-early-330-2026-10.zip` for the exact early 3.3.0 baseline
`7dc6467b7c0482a048fe755dfea31356c56c3f72` to the first patch's identical target
`dae80da38d4adb9b6db700fef16e45e5afa140e3`. All 76 installed framework files in
metis-ingestion-control-plane match this baseline; a read-only candidate preview
has zero conflicts and 22 changes. Its original framework is unchanged since the
initial repository commit, not a set of uncommitted local edits.

The artifact is 163112 bytes, SHA-256
`d08de17db25022f1f6384e2e7b29ca8c5acf14ae204e058aa1e7e044afb1144f`.
Target's 30 tests passed from a fresh Git export (135.958 seconds). Exact snapshot,
allowlist and payload audits passed. Desktop blocked/recovery, disposable generation,
upgrade, project preservation, reapply and instruction reconciliation passed. A
temporary QA path-length issue was resolved within scratch; no project workaround
was added. All 41 current tests passed from the final clean tracked-file export
in 137.019 seconds, including PowerShell generation, UI plan round-trip and relocated
packaging. All 81 current framework checksums and whitespace checks passed.
Implementation/release-preparation commit `b743aae37fb8c79a3bdda8676acec0617d396cc5`
was pushed and matched the tracked remote; the preparation checkpoint tree was clean.
This documentation-only closure follows on the same branch.

Versions remain playbook 3.3.0 and Builder 0.1.0. This redistributes a previously
reviewed target for a different baseline; the first release is unchanged. The new
[release](https://github.com/Eellerholz3204/engineering-playbook/releases/tag/playbook-patch-scratch-workspace-early-330-2026-10)
was published at 2026-10-20 03:18:12 UTC (2026-10-19 local), stable and not marked
Latest. Draft/public download bytes and notes matched the committed candidate;
Builder's live public discovery/download/read-only preview passed with zero conflicts
and 22 changes for the named repository. Annotated tag `83f8a292afde942b3e5e022f56c6efa14f722806`
resolves remotely to the exact target above. No real consumer apply, desktop
binary rebuild or PR merge is authorized. Existing ADRs GOV-005/GOV-008 apply; no new
ADR. Next implementation milestone: none. Branch: `codex/governance-context-loading`.

## GOV-009 — 2026-10-19

Builder now uses one Patch selector for published releases and local ZIPs. Published
choices show the release title without the generic prefix/ZIP filename, an overview
and expandable original release notes. Preview downloads and verifies the selected
patch automatically; cached choices can be previewed offline. There is no manual
SHA-256 field. Local sidecars are read automatically when present; the exact preview
digest remains pinned internally for separate Apply. Selection changes invalidate
review, and release identity changes invalidate cached remote mappings.

Versions remain playbook 3.3.0 and Builder 0.1.0 on
`codex/governance-context-loading`. Working-checkout verification: all 40 tests
passed (135.868 seconds); the final additional cache-identity assertion also passed.
Live desktop checks exercised published notes, unified selection, automatic download,
read-only preview, offline reuse and disposable application with project preservation.
Screenshots were inspected and retained in external scratch. All 81 framework
checksums passed. The final clean tracked-file export passed all 40 tests in
139.575 seconds, including all-profile PowerShell generation, UI plan round-trip
and relocated packaged resources. Staged whitespace checks passed. Delivery:
IMPLEMENTED. Implementation commit `f76734eeac4606ee6f8997b2531723eb0692c93f`
was pushed to the tracked branch; remote HEAD matched and the implementation
checkpoint working tree was clean. This documentation-only closure follows there.

Updated patch and Builder guides, milestone, roadmap and unreleased notes. Existing
ADRs GOV-005/GOV-008 remain unchanged; this is a UI orchestration refinement, not a
new publisher or application policy. No published patch/tag, real consumer project
or packaged binary changed. Restart the source-launched Builder to load the changes.
No next implementation milestone is accepted.

## GOV-008 — 2026-10-19

Builder now checks the fixed public playbook GitHub repository on explicit user
action and downloads selected stable patch ZIP/checksum pairs. HTTPS host limits,
bounded requests, checksum/digest comparison and full archive validation protect
downloads. A complete pair is exposed atomically in the external content-addressed
cache; later launches support offline selection with the expected hash restored.
Errors retain the manual/local workflow. Preview and Apply remain separate actions.
No credentials, startup polling, arbitrary feed URLs or consumer writes are added
to the downloader. ADR GOV-008 records source trust and cache ownership.

Versions remain playbook 3.3.0 and Builder 0.1.0. Branch:
`codex/governance-context-loading`; implementation commit:
`33c3e547ba79a58c8c69b57e6471fc4b39a7d099`. The implementation checkpoint
HEAD and remote branch matched that commit and the working tree was clean. This
documentation-only delivery record follows on the same branch.

Verification: all 38 tests passed locally and in the final clean tracked-file
export (136.717 seconds), including actual all-profile PowerShell generation,
UI configuration round-trip and relocated packaged resources. Five download
contract tests and a UI flow test cover filtering/pagination, network restrictions,
errors, interrupted/invalid downloads, cache reuse/tampering and preview gating.
The actual published scratch-workspace patch passed live discovery, download and
checksum selection, desktop rendering, preview and apply in a disposable repository
generated from the old release. All 81 framework checksums and diff checks passed.
Temporary QA scripts/screenshots remained outside the checkout.

Source-launched Builder users restart to load the change. No packaged binary,
published patch/tag, real consumer repository or PR merge changed. Cached downloads
are local and not automatically cleaned; private/prerelease feeds and automatic
application remain out of scope. No next implementation milestone is accepted.

## GOV-007 — 2026-10-19

The first framework patch is published. The existing
candidate is unchanged, with published filename `scratch-workspace-2026-10.zip` and
SHA-256 `02953297c36b7d0da5398b182e0efebe8d8f08a4abb66170ccdb3059ccc2c253`.
Base: `7b22dd7dcad44826c32cf7c98d76b93b6f01cc43` (3.2.1); target:
`dae80da38d4adb9b6db700fef16e45e5afa140e3` (3.3.0). No version bump is needed
to publish this already-versioned snapshot. Builder remains 0.1.0.

All 30 target-snapshot tests passed from a fresh Git export (140.859 seconds).
Candidate hashes/payload matched both committed snapshots; fresh old-generator
upgrade, preservation, reapply and post-reconciliation governance passed. All 80
framework checksums passed. The archive contains only its manifest and 81 allowlisted
framework files; a private-key/GitHub-token pattern scan found no matches. Release
notes describe exact compatibility, manual reconciliation and recovery requirements.

Release: [scratch-workspace-2026-10](https://github.com/Eellerholz3204/engineering-playbook/releases/tag/playbook-patch-scratch-workspace-2026-10),
published 2026-10-20 00:45:14 UTC (2026-10-19 local), not a draft or prerelease.
Both assets were downloaded through unauthenticated public URLs and matched the
local ZIP/checksum bytes. Published notes matched the committed release document.
The annotated tag object `5f1caf73ca4a97f44ba820ffcfb1d3ea98187292` resolves to
the exact target commit above and matched the remote tag.

Branch: `codex/governance-context-loading`; preparation commit
`76a7eb24d251a2898496a29b9c1f6742a48b5a47` was pushed and matched the remote.
The publication checkpoint working tree was clean; this documentation-only record
follows on the same branch. No new ADR, consumer changes, Builder binary rebuild
or PR merge occurred. No next implementation milestone is accepted.

## GOV-006 — 2026-10-19

Builder's patch screen now has searchable repository and patch dropdowns, Browse
fallbacks, selected full paths and Refresh. Discovery is local and nonrecursive:
installed projects in the creation parent folder and ~/source/repos; patch ZIPs in
Downloads, Builder dist and ZIP folders browsed this session. Session choices are
not persisted. Display metadata does not establish patch trust or compatibility.
Searching, selection changes and Refresh invalidate preview; patch changes clear
the expected checksum. The input controls remain stable while filtering.

Versions remain playbook 3.3.0 and Builder 0.1.0. Branch:
`codex/governance-context-loading`; implementation commit
`3c63f68833df17c3a10b06cbe18b9f9cc60aa572`. The implementation checkpoint HEAD
and remote branch matched that commit, with a clean working tree. This delivery
record is a documentation-only follow-up on the same branch.
All 32 tests passed, including the final code in a fresh tracked-file export with
declared dependencies and no ignored source artifacts. Actual desktop rendering,
discovered choices, preview and disposable apply passed. Existing PowerShell
generation, creation-plan round-trip, patch contracts and packaging passed; all 80
checksums were refreshed and validated. Staged whitespace checks passed.

No patch engine or architecture decision changed; no new ADR is needed. The
source-launched Builder picks this up after restart. Packaged binaries, the prior
patch candidate and real downstream repositories were not changed. No network
release catalog or persistent recent-location registry is included. No next
implementation milestone is accepted; publication and rollout remain separate.

## GOV-005 — 2026-10-16

Patch delivery is implemented: reviewed ZIP/checksum production, no-write
preview, conflict-checked apply, external backup/recovery and instruction merge
guidance, plus Builder UI and artifact-only CI packaging. Consumer source, tests,
AGENTS.md and project documents are preserved. Existing configuration retains local
fields and receives installed version/last-patch metadata. No consumer Git action runs.

Versions remain playbook 3.3.0 and Builder 0.1.0 (unreleased source changes).
Branch: `codex/governance-context-loading`; implementation commit: `dae80da`.
At the implementation checkpoint, HEAD and the remote branch both resolved to
`dae80da38d4adb9b6db700fef16e45e5afa140e3`, and the working tree was clean. This
delivery record is a documentation-only follow-up on the same branch.
Verification: eight focused patch tests and all 30 suite tests passed, with the final
suite run from a fresh tracked-file export free of ignored local artifacts.
An actual Builder desktop upgrade from `builder-v0.1.0` / playbook 3.2.1 to the
current framework preserved project content; governance passed after explicit
instruction reconciliation. Unicode scratch paths passed in the final suite. All 80
framework checksums and the packaged allowlist passed; staged diff review passed.
Candidate identity and commit/push delivery evidence are maintained in the ledger.

No patch is published or applied to real downstream repositories. A local candidate
ZIP demonstrates the released 3.2.1 baseline; different installed content requires
a matching bundle or explicit reconciliation. Existing Builder binaries remain
unchanged and need a separate rebuild to expose the patch UI. No next implementation
milestone is accepted; release publication and rollout require an explicit decision.

## GOV-004 — 2026-10-16

External agent workspaces and artifact ownership are implemented in the playbook
and source-launched Repository Builder. All seven profiles create scratch outside
the checkout; installed guidance and a helper support fresh clones and separate
tasks. Existing project documents and AGENTS.md remain preserved on reconciliation.

Versions remain playbook 3.3.0 and Builder 0.1.0 (unreleased source changes).
Branch: `codex/governance-context-loading`; implementation commit: `05e28e4`.
At the implementation checkpoint, HEAD and the remote branch both resolved to
`05e28e4d7613e7efbb6724ed9a2292c0664c5f9c`, and the working tree was clean. This
delivery record is a documentation-only follow-up on the same branch. Verification: all
22 tests passed both locally and from a fresh tracked-file export with no ignored
artifacts; actual desktop creation/render and Windows PowerShell 5.1 creation passed;
packaged allowlist generation and all 76 checksums passed. Commit/push evidence is
recorded in the ledger below GOV-004. No packaged binary was rebuilt or published.
At GOV-004 closure no next implementation milestone or downstream cleanup was
authorized; GOV-005 above records the subsequent patch-delivery request.

## Earlier milestones

GOV-001 implementation adds governance startup to Repo Builder and its PowerShell
generation paths. New repos receive AGENTS.md; selecting Metis governance adds
its canonical cross-repository context procedure. Existing instructions are
preserved and flagged for reconciliation. Verification results are recorded in
`docs/milestone_details.md`. Packaged releases require a separate build/release.

GOV-002 adds central model and reasoning-effort routing to the framework and
generated generic AGENTS.md. The policy defines capability tiers and escalation
triggers without binding normative guidance to transient model versions.
Governance review identified that the prior AGENTS.md reference targeted an
optional framework file. GOV-003 moves the normative policy to the mandatory
installed `GOVERNANCE_CONTEXT.md` and corrects that reference.
