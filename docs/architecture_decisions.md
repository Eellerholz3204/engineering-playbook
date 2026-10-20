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

## GOV-008 — Explicit public patch discovery and validated local cache

Status: ACCEPTED under Eric's 2026-10-19 in-app patch download request.

Context: local-only selectors still require users to find and download the correct
release assets manually. The existing public patch publisher and verification engine
provide a bounded source and validation contract.

Decision: add a read-only standard-library HTTP adapter for the fixed public
Eellerholz3204/engineering-playbook repository. Check only on user action; list stable
published `playbook-patch-*` releases containing a ZIP and matching `.zip.sha256`.
Construct canonical publisher asset URLs rather than trusting arbitrary response URLs.
Require HTTPS and allowlisted GitHub/CDN redirects, size limits, bounded pagination
and request timeouts. Do not acquire or send credentials. Rate limits and offline
errors leave the manual/local workflow available.

Verify the release checksum, GitHub asset digest when supplied, and the complete
patch archive before exposing a download. Publish the verified ZIP/checksum pair
atomically in a content-addressed cache under local application data, outside the
checkout and selected consumer repository. Retain downloads for offline use, pin
preview to the cached content hash and reject damaged entries without overwriting
them. No automatic cache cleanup runs. Partial staging is temporary and discarded.

Rationale: users can obtain official patches without command-line tools, credentials,
or manual file management, while downloads remain separate from application. TLS
and the configured publisher establish source trust; checksums detect corruption,
not an independently signed publisher identity. A compromised publisher remains a
trust boundary. Version labels are not sufficient for consumer compatibility.

Consequences: browsing/downloading does not apply patches or execute payload code.
Existing preview, baseline checks, explicit Apply and backup/recovery remain required.
No automatic update scheduler, arbitrary feed URLs, private releases, prereleases,
desktop self-update or publication changes are included.

## GOV-011 — Reviewed legacy baseline additions

Status: ACCEPTED under Eric's legacy migration implementation/publication approval.

Context: the older Metis 3.2.1 catalog contains 51 framework files, while five
governance files were installed additively. Treating these as absent additions
blocks a safe upgrade; forcing replacement would discard reviewed local policy.

Decision: extend publisher-side build with an explicit JSON path/SHA-256 map for
reviewed supplemental base files. Validate the original snapshot unchanged, reject
base overrides and paths outside the target allowlist, and verify every supplied
pin against exact bytes. Emit the existing version-1 before/after format. Do not
normalize consumer files or infer ownership from directory contents. Integrate the
reusable access/identity requirements into the target framework before migration.

Rationale: legacy adoption can be represented by the existing content-hash contract
without changing consumer trust, conflict handling, rollback or project preservation.

Consequences: releases remain specific to audited bytes, including BOM/line endings.
Other baselines need independent review. Publisher recipes contain hashes only,
not project documents or credentials. Missing project configuration stays missing;
Metis instructions must still be preserved/reconciled manually. Existing releases
remain immutable. This supersedes no prior application or publication boundaries.

## GOV-012 — Advisory repository-specific patch classification

Status: ACCEPTED under Eric's 2026-10-20 compatibility-selection implementation request.

Context: release names/version labels cannot determine which exact baseline matches
a selected repository. Repeated manual preview attempts make supported patches hard
to find, even though the existing patch engine can safely inspect them.

Decision: on repository selection, Browse, explicit Refresh or successful online
discovery, validate available patches with the existing downloader and inspection
engine. No startup network discovery. Download only into the existing external cache,
one patch at a time; allow stopping after the current bounded check. Rank compatible
results first; hide incompatible choices unless Show all or explicitly selected.
Distinguish inspection/download failure from incompatibility. Identical target files
count as Already applied even if a different patch receipt is recorded.

Results are advisory and session-only. Repository changes invalidate classifications;
refresh retries/rechecks. Do not infer compatibility from names or semantic versions.
Do not silently change an explicit selection. Classification does not set a reviewed
transaction: Preview independently verifies current bytes, and Apply retains its
existing digest/conflict/recovery checks. No new publisher, patch format or write
authority is introduced; ADRs GOV-005/GOV-008 remain in force.

Consequences: selecting a repository after discovering releases can download multiple
ZIPs. Progress and unknown/error states remain visible, cached checks work offline,
and files changed externally may stale a label until refresh/preview. Application,
instruction reconciliation and real consumer Git operations remain explicit.
