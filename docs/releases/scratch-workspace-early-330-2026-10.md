# Agent scratch workspaces for early 3.3.0 repositories

Patch ID: `scratch-workspace-early-330-2026-10`

Framework version: **early 3.3.0 to scratch-enabled 3.3.0**

Release tag: `playbook-patch-scratch-workspace-early-330-2026-10`

This patch adds external agent scratch workspaces, rules for keeping temporary
diagnostics and tooling fixes out of project repositories, and the reusable framework
patch updater. It supports early 3.3.0 installations that predate scratch workspaces.
It preserves project source, tests, documents and existing AGENTS.md instructions.
Nothing is automatically deleted. Review and merge the suggested agent instructions
after applying so agents know to use the new workspace.

## Which patch to select

In the source-launched Repository Builder, choose **Patch existing repository**,
then **Check for patches**. Select **agent scratch workspaces (early 3.3.0 repositories)**
and the repository to update. **Preview patch** downloads and verifies the ZIP
automatically. Review the changes and required follow-up, then choose **Apply patch**.
Checking, downloading and previewing do not change project files.

Use this release when the installed framework matches the early 3.3.0 source revision
below. The original **agent scratch workspaces (3.2.1 to 3.3.0)** patch is for a different
starting snapshot. A version label alone cannot select the correct patch: the older
and newer framework revisions both historically carry version 3.3.0. Builder checks
the actual contents and blocks incompatible or locally modified files; there is no
force option. Do not overwrite conflicts to make a patch apply.

## Compatibility and immutable source identities

- Base: `7dc6467b7c0482a048fe755dfea31356c56c3f72`, early playbook 3.3.0.
- Target: `dae80da38d4adb9b6db700fef16e45e5afa140e3`, scratch-enabled playbook 3.3.0.
- The annotated release tag points to that target, not the later Builder UI changes.
- The target payload is identical to the first scratch-workspace patch; only the
  starting snapshot, patch identity and summary differ. The original release is unchanged.

This is an alternate-baseline framework patch, not a new framework implementation
or desktop app release. It does not install the latest Builder UI or change Builder's
version. Restart a current source-launched Builder for the new **Patch blocked** UI;
older packaged apps require a separately built app update or the trusted source CLI.

## Download manually when needed

- [Patch ZIP](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-scratch-workspace-early-330-2026-10/scratch-workspace-early-330-2026-10.zip)
- [Checksum sidecar](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-scratch-workspace-early-330-2026-10/scratch-workspace-early-330-2026-10.zip.sha256)

Keep both files together; do not extract the ZIP. Browse to the ZIP in Builder if
online discovery is unavailable. Builder reads the checksum sidecar automatically.
Use the named patch asset, not GitHub's generated Source code archives.

ZIP SHA-256: `d08de17db25022f1f6384e2e7b29ca8c5acf14ae204e058aa1e7e044afb1144f`.

## Preserved content, follow-up and recovery

The updater changes only allowlisted framework files under `engineering-playbook/`
and the installed-version/last-patch receipt in existing `.engineering-playbook.json`.
Existing project fields, source, tests, documentation and AGENTS.md are preserved.
It creates no consumer commits or pull requests and executes no code from the ZIP.

Apply stores backups, a transaction journal and suggested `AGENTS.blocks.md` in
external agent scratch. Merge those blocks into AGENTS.md explicitly without removing
project or Metis instructions. Review any changed project templates in the existing
owning documents; run the installed governance verifier and required project checks.
The framework update alone does not complete this instruction reconciliation.

Retain backups until the update and instruction review are accepted. Interrupted
updates require journal/file inspection; do not force an overwrite or delete backups.
See [patch delivery and recovery](https://github.com/Eellerholz3204/engineering-playbook/blob/dae80da38d4adb9b6db700fef16e45e5afa140e3/PATCH_RELEASES.md)
for the CLI, conflict rules and recovery procedure. Reapplying the same target and
receipt is a no-op. Cleanup and application to real repositories remain explicit.

## Verification

The target snapshot passed all 30 tests from a fresh Git export. The candidate's
76-file baseline and 81-file target were checked against the exact source snapshots;
its target payload matches the first patch byte-for-byte. A disposable repository
generated from the early baseline passed preview, application, project preservation,
repeated application and governance verification after explicit instruction merge.
These checks do not authorize or replace verification in a real consuming project.
