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
