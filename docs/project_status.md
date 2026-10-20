# Project status

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
