# Project status

## GOV-004 — 2026-10-16

External agent workspaces and artifact ownership are implemented in the playbook
and source-launched Repository Builder. All seven profiles create scratch outside
the checkout; installed guidance and a helper support fresh clones and separate
tasks. Existing project documents and AGENTS.md remain preserved on reconciliation.

Versions remain playbook 3.3.0 and Builder 0.1.0 (unreleased source changes).
Branch: `codex/governance-context-loading`; baseline HEAD: `7dc6467`.
The working tree contains only GOV-004 changes before closure. Verification: all
22 tests passed both locally and from a fresh tracked-file export with no ignored
artifacts; actual desktop creation/render and Windows PowerShell 5.1 creation passed;
packaged allowlist generation and all 76 checksums passed. Commit/push evidence is
recorded at milestone closure. No packaged binary was rebuilt or published.
No next implementation milestone or downstream cleanup is authorized.

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
