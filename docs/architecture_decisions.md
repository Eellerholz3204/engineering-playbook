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

## GOV-005 — Explicit patch bundles for existing repositories

Status: ACCEPTED under Eric's 2026-10-16 patch-delivery request.

Context: reconciliation copies the current framework but has no standalone patch
identity, preflight baseline/conflict report or release artifact for existing repos.
Playbook versions alone cannot distinguish historical same-version source changes.

Decision: package an allowlisted target framework snapshot with exact before/after
SHA-256 maps, a patch ID and summary. Build an offline ZIP and checksum sidecar from
two reviewed snapshots. Preview is read-only. Apply verifies the reviewed ZIP digest,
validates all payloads and installed files, and stops before replacement on conflicts.
Only framework files and version/last-patch metadata in an existing project config
are written. Unknown project metadata is preserved. AGENTS.md, project documents,
source and tests are never replaced; proposed instruction blocks stay in scratch.

The same Python engine serves CLI and Builder. Bundle code is not executed. Backups,
transaction evidence and merge guidance live in external scratch. File replacements
are atomic individually; caught write failures attempt rollback without overwriting
concurrent edits. Abrupt process/machine termination requires inspection and recovery
using the retained journal/backups. Updates create no commits or PRs in consumers.

Rationale: content baselines avoid unsafe same-version overwrite, while a complete
small framework payload is independently verifiable and requires no network during
preview/apply. Patch removal/migration and automatic project-file reconciliation
remain out of scope. Release trust comes from the reviewed publisher/checksum, not
the fact that an archive contains hashes.

Consequences: artifacts can be built locally or through an artifact-only workflow;
publication and downstream application remain explicit. A changed instruction block
can leave governance verification pending manual reconciliation even after a clean
framework apply. Existing packaged Builder binaries need a later rebuild to expose
the new UI; the CLI supports bootstrapping from the current trusted source checkout.
