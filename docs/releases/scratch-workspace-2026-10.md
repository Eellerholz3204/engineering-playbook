# First playbook patch: agent scratch workspaces

Retired 2026-10-20: this release is a recoverable draft. These are historical
instructions; use the [portable feature](agent-scratch-workspaces-portable-v1.md)
for new scratch adoption. Existing applied changes are not undone.

Patch ID: `scratch-workspace-2026-10`

Framework version: **3.2.1 → 3.3.0**

Release tag: `playbook-patch-scratch-workspace-2026-10`

This patch adds external agent scratch workspaces, rules for keeping temporary
diagnostics and tooling fixes out of consumer projects, and governance startup and
ownership guidance. It also installs the framework patch tooling and related
framework updates from the target snapshot. It preserves project source, tests,
documents and existing AGENTS.md instructions. Nothing is automatically deleted.

## Downloads

Download these two release assets into your **Downloads** folder:

- [scratch-workspace-2026-10.zip](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-scratch-workspace-2026-10/scratch-workspace-2026-10.zip)
- [scratch-workspace-2026-10.zip.sha256](https://github.com/Eellerholz3204/engineering-playbook/releases/download/playbook-patch-scratch-workspace-2026-10/scratch-workspace-2026-10.zip.sha256)

Choose the named patch ZIP, **not** GitHub's automatically generated "Source code"
archives. Keep the patch ZIP intact; Repository Builder reads it directly.

ZIP SHA-256:

```text
02953297c36b7d0da5398b182e0efebe8d8f08a4abb66170ccdb3059ccc2c253
```

These are the exact bytes of the verified local `scratch-workspace-patch-rc2.zip`
candidate, renamed for publication. The checksum sidecar names the published file.

## Compatibility and source identities

- Base: playbook 3.2.1 from `builder-v0.1.0`, commit
  `7b22dd7dcad44826c32cf7c98d76b93b6f01cc43`.
- Target: playbook 3.3.0, commit
  `dae80da38d4adb9b6db700fef16e45e5afa140e3`.
- The annotated release tag points to that exact target commit. This release does
  not include the later Builder dropdown changes or rebuild the desktop app.

The installed framework files must match the patch's exact baseline or already
match its target. A matching version number alone is insufficient. Local framework
edits, incompatible installations or missing baseline files block application;
there is no force option. Preview before applying to every repository.

## Apply with Repository Builder

Use the current source-launched Builder with patch support. Older packaged Builder
0.1.0 downloads do not provide this update screen; use a current source checkout or
the CLI described below. This patch does **not** upgrade the Builder application.

1. Open **Patch existing repository**, then click **Refresh lists**.
2. Select the existing repository and `scratch-workspace-2026-10` patch. Use
   **Browse patch ZIPs…** if it is outside Downloads.
3. Paste the SHA-256 above into **Release SHA-256**.
4. Choose **Preview patch** and review changes, conflicts and manual follow-up.
5. Choose **Apply patch** only after accepting that review. Keep the reported
   external backup location until the upgrade is accepted.

For CLI bootstrapping, download/extract the source at this release tag to a separate
tools folder, or use a trusted current checkout. Python 3.11+ and PowerShell are
required. Run its `scripts/playbook_patch.py preview` and `apply` commands with
`--bundle`, `--repo` and `--sha256` as shown in the
[tagged patch guide](https://github.com/Eellerholz3204/engineering-playbook/blob/playbook-patch-scratch-workspace-2026-10/PATCH_RELEASES.md).
Do not overwrite the consumer project with the source archive.

## Required follow-up and recovery

Existing AGENTS.md and project documents are preserved, not automatically reconciled.
Merge the suggested `AGENTS.blocks.md` from the external backup folder into AGENTS.md
without deleting local rules. Review any changed project templates called out by
preview. Run the installed governance verifier and the project's required checks,
then review the diff under the project's normal change process.

After instruction reconciliation, create or resolve a task workspace from the
consumer repository when needed:

```powershell
./engineering-playbook/scripts/initialize_agent_workspace.ps1 `
  -RepositoryPath (Get-Location).Path -TaskId 'my-task'
```

Backups, transaction records and suggested instruction blocks remain outside the
project. Reapplying the same target is a no-op. Caught write failures attempt rollback;
an abrupt interruption or concurrent edits may need manual recovery using retained
backups and the transaction journal. See the tagged patch guide for recovery details.

Publication does not apply this patch to any repository, create consumer commits or
PRs, remove existing tests or clean up historical agent artifacts.

## Verification

All 30 tests in the exact target source snapshot passed from a fresh Git export.
The candidate's baseline hashes and complete target payload matched the committed
snapshots above, including all 80 framework checksums. A fresh repository generated
from the released 3.2.1 source passed preview, apply, project-content preservation,
reapply and governance verification after explicit instruction reconciliation.
Archive contents matched the allowlist; no local runtime or scratch files were added.
