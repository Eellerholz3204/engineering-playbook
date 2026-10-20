# Project status

## GOV-006 — 2026-10-19

Builder's patch screen now has searchable repository and patch dropdowns, Browse
fallbacks, selected full paths and Refresh. Discovery is local and nonrecursive:
installed projects in the creation parent folder and ~/source/repos; patch ZIPs in
Downloads, Builder dist and ZIP folders browsed this session. Session choices are
not persisted. Display metadata does not establish patch trust or compatibility.
Searching, selection changes and Refresh invalidate preview; patch changes clear
the expected checksum. The input controls remain stable while filtering.

Versions remain playbook 3.3.0 and Builder 0.1.0. Branch:
`codex/governance-context-loading`; the implementation starts from committed HEAD
`c27ebf47b05b9f97a3dd8f3e6608d2281ba4f065`. Only GOV-006 files changed at this
checkpoint; delivery identity will be recorded after commit/push verification.
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
