# Architecture decisions

## GOV-001 — Governed startup entry points

Accepted by Eric's 2026-09-26 implementation request. Generate concise AGENTS.md
instructions invoking the installed procedure. Organizational packs append scoped
source references. Preserve existing instructions during installation and require
explicit reconciliation. Governance facts remain in their owning project records.
Structural checks detect missing paths and instruction drift but cannot establish
semantic understanding. This avoids a second copied governance authority.

## GOV-004 — External agent workspaces and artifact ownership

Status: ACCEPTED by Eric's 2026-10-16 implementation request.

Context: local blockers and exploratory tools were becoming permanent consumer
project PRs, tests and documents without a maintained project requirement.

Decision: create scratch outside the checkout using one PowerShell helper shared
by all generator entry points. Identify a checkout by its normalized absolute path
hash, with separate task folders. Default to local application data; permit an
external environment override, never a committed machine-specific path. Install
the helper and concise AGENTS.md instructions in every profile. Preserve existing
project documents and instructions during reconciliation.

The mandatory governance context defines blocker ownership, artifact promotion,
test relevance and retention. Temporary diagnostics stay in scratch; reusable
tool fixes live with their owner; maintained project behavior stays in the project.
Required project checks must pass independently of scratch. Existing tests are not
removed by count or provenance.

Rationale: external placement avoids accidental Git staging, test discovery and
packaging without proliferating ignore rules or per-profile implementations.

Consequences: scratch is machine-local, optional for ordinary project execution,
and created on demand in fresh clones. Moving a checkout creates a new identity.
No automatic cleanup or downstream migration is included. Packaged binaries need
a separate authorized rebuild/release to distribute this source change.
