# Agent scratch workspaces for legacy Metis repositories

This patch adds external agent scratch workspaces to the older Metis framework,
keeps temporary diagnostics and tooling work out of project history, and preserves
the access/identity requirements already adopted by metis-engineering-playbook.
Project source, tests, documents and AGENTS.md remain untouched. Nothing is
automatically deleted. Agent instructions still require explicit reconciliation.

Patch ID: `scratch-workspace-legacy-metis-2026-10`

Framework version: **legacy Metis 3.2.1 to 3.3.1**

Release tag: `playbook-patch-scratch-workspace-legacy-metis-2026-10`

## Select this patch in Repository Builder

Choose **Patch existing repository**, then **Check for patches**. Select
**metis-engineering-playbook** and **agent scratch workspaces (legacy Metis 3.2.1 to 3.3.1)**.
Choose **Preview patch** to download and verify the ZIP automatically. Review the
changes and follow-up before choosing **Apply patch**. Checking, downloading and
previewing do not change project files. There is no checksum to type.

This release is for the audited older installation with a 51-file catalog and five
separately adopted governance files. The original 3.2.1 and early-3.3.0 patches
target different baselines; they remain unchanged. A version label alone does not
establish compatibility. Unrecognized content still produces **Patch blocked**;
do not overwrite local changes to make the patch apply.

## What changes

- Install the external task-workspace helper and scratch/artifact ownership rules.
- Keep exploratory tests, logs and local tooling workarounds outside project repos;
  keep maintained product code and tests with their actual owner.
- Retain the access/identity startup reading and documentation requirements in the
  updated reusable framework. No project-specific identity facts are included.
- Bring the allowlisted framework to 3.3.1, including current patch tooling.
  This does not replace the installed desktop application or change Builder 0.1.0.

## Exact baseline and target

- Baseline provenance: committed framework content in metis-engineering-playbook
  at `1dfdd6c3b22dea347284c7e4ec757d89d5233429`, verified against the installed files.
- Baseline identity: exact installed-byte hashes of all 56 managed files in the
  ZIP's `patch.json`, including historical BOM/mixed Windows line endings. The
  original catalog/checksum snapshot validates unchanged. A text-normalized Git
  archive or differently encoded clone is not necessarily this same byte baseline.
- [Reviewed supplemental pins](https://github.com/Eellerholz3204/engineering-playbook/blob/f6013bc5ce4b0df0103847f8d7b63ecdd5c233de/docs/releases/scratch-workspace-legacy-metis-2026-10-baseline.json)
  identify the five governance files outside the older catalog. Publisher builds
  supply this file with `--base-additions` and the audited installed-framework export
  as `--base`; no consumer hashing or conflict rules are relaxed.
- Target: `f6013bc5ce4b0df0103847f8d7b63ecdd5c233de`, playbook 3.3.1, 82 allowlisted files.
  The annotated release tag points to this exact implementation commit.
- Existing version-1 patch readers accept this bundle; no new patch format is required.

## Preserved content and required follow-up

Only changed allowlisted files under `engineering-playbook/` are replaced. Project
source, tests, documents, AGENTS.md and unknown files are preserved byte-for-byte.
The updater never stages, commits, pushes or opens a consumer PR, and never executes
code from the ZIP. Existing project configuration retains local fields and receives
version/patch metadata; absent `.engineering-playbook.json` stays absent.

After applying, explicitly reconcile both installed `templates/agents.md` and
`templates/metis_agents.md` into the root AGENTS.md without removing local rules.
The paths are relative to `engineering-playbook/`. With no project configuration,
the updater cannot infer selected capabilities, so its backup's suggested blocks
alone must not be treated as the complete Metis instruction set. Review changed
templates against existing project documents; do not replace those documents.

Then run the installed governance verifier with `--metis` and the project's required
checks. A successful framework apply does not complete instruction reconciliation.
Existing uncommitted project work should remain separate in the normal review process.

Apply retains original replaced files, a transaction journal and suggested instruction
blocks in external scratch. Keep backups until the update is accepted. Interrupted
updates require journal/file inspection; reapplying an exact completed target is a
no-op. See [patch delivery and recovery](https://github.com/Eellerholz3204/engineering-playbook/blob/f6013bc5ce4b0df0103847f8d7b63ecdd5c233de/PATCH_RELEASES.md).

## Manual download if needed

- [Patch ZIP](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-scratch-workspace-legacy-metis-2026-10/scratch-workspace-legacy-metis-2026-10.zip)
- [Checksum sidecar](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-scratch-workspace-legacy-metis-2026-10/scratch-workspace-legacy-metis-2026-10.zip.sha256)

Keep both files together and browse to the ZIP without extracting it. Builder reads
the sidecar automatically. Do not use GitHub's generated Source code archives.

ZIP SHA-256: `d63068f7072bd70c6f988dafc459d0b4e764259571afc57b493f76deeeb4bc93`.

## Verification

All 43 tests passed from a clean tracked-file export, including actual PowerShell
generation, UI plan round-trip, packaging, legacy baseline validation and recovery.
The candidate matched the exact base/target hashes. Desktop application to a
disposable legacy fixture preserved project/identity/unknown files, did not create
missing configuration, and passed repeat application and reconciled governance.
Read-only preview against the named repository reported zero conflicts and 61
changes. No real consumer application was performed as part of publication.
