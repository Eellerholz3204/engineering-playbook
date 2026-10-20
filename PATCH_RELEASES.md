# Playbook patches for existing repositories

A patch is a reviewed ZIP containing an allowlisted target framework snapshot,
the exact base/target file hashes, a unique patch ID and a release summary. It can
deliver scratch-space rules and future framework improvements to repositories that
already contain `engineering-playbook/`. It does not update the installed Builder
application, publish releases, create PRs or change project source/tests.

## Prepare a patch release

Use the trusted current source checkout with Python 3.11 or newer. Choose a reviewed
base snapshot that matches the repositories being updated and a tested target
snapshot. These may be extracted source releases or separate checkouts. Do not edit
the base. Both snapshots must have valid `playbook.json`, `VERSION` and complete
`SHA256SUMS.txt` files. Refresh target checksums after intentional framework changes:

```powershell
python scripts/update_checksums.py
python -m unittest discover -s tests -v
python scripts/playbook_patch.py build `
  --base C:\releases\previous-playbook `
  --target . `
  --output C:\releases\scratch-workspace-patch.zip `
  --patch-id scratch-workspace-2026-10 `
  --summary 'Add external agent scratch spaces and project artifact ownership rules.'
```

Write outputs outside both source snapshots. The builder creates the ZIP and
`.zip.sha256` sidecar without overwriting an existing artifact. The complete small
framework payload permits offline verification; only differing files are replaced.
Patch identity includes the ZIP hash, so same-version source revisions remain
distinguishable. Do not reuse a patch ID for different released content.

The **Build playbook patch** GitHub Actions workflow accepts the previous released
commit/tag, patch ID and summary. The selected workflow ref is the target. It tests
the target and uploads the ZIP/checksum as review artifacts, with read-only repository
permissions. It does not create a tag or GitHub release.

Before publishing, apply the candidate to a disposable repository generated from
the selected base. Review the diff and manual reconciliation report, verify project
preservation and run the required project checks. Then follow `RELEASE_PROCESS.md`
with explicit release authorization. Attach the ZIP and checksum to the approved
GitHub release, stating the patch ID, base/target versions, exact source commits,
summary and required instruction/document reconciliation. A new supported base
requires its own tested bundle; a matching version label alone is insufficient.

## Preview and apply in Repository Builder

To obtain a patch directly, choose **Patch existing repository**, then **Check for
patches**. Choose an **Existing repository** and an entry in the single **Patch**
selector, then **Preview patch**. Published releases and local ZIPs share this list.
Published patches show their readable release name, purpose and expandable release
notes before download. A sole available patch is selected after checking; a target
repository is never selected automatically. Existing selections are preserved.
Builder checks the public `Eellerholz3204/engineering-playbook` GitHub releases,
excluding drafts, prereleases and releases without a patch ZIP/checksum pair.
No sign-in is required and no network check runs just from opening Builder.

Preview downloads the selected published ZIP as needed and validates its checksum
and full archive automatically. There is no manual SHA-256 field. Downloads are retained outside projects
under `%LOCALAPPDATA%\RepositoryBuilder\patches\<sha256>\` (or `~/.cache` when local
application data is unavailable). Completed downloads appear in the same patch list
on later launches and can be previewed offline. Selecting a cached ZIP restores its
pinned expected hash; preview still verifies the file. Damaged cache entries are
reported, not silently overwritten. No automatic cache cleanup runs.

Network requests use HTTPS, GitHub/CDN redirect restrictions, size limits, 30-second
request timeouts and a maximum of five 100-release pages. Connection failures, rate
limits or oversized catalogs leave Browse/local preview available. Only the fixed
publisher is supported; checksums protect integrity, not independent publisher
authenticity. Downloading never applies a patch or determines project compatibility.

Use the searchable **Existing repository** and **Patch** dropdowns.
Repository discovery checks immediate children of the creation screen's parent
folder and `~/source/repos` for an installed `engineering-playbook/playbook.json`.
Patch discovery checks Downloads, Builder's `dist` folder and ZIP folders browsed
this session. It reads patch IDs and base/target versions for display; discovery
does not establish authenticity or compatibility. No recursive disk scan runs.

Use **Browse repositories…** or **Browse patch ZIPs…** for other locations, and
**Refresh lists** to rescan local files. Browsed choices remain available until
Builder exits; no paths or selection history are written into project files.
Local paths appear below the dropdowns; published choices show download status.
Searching, changing selections or refreshing requires a new preview. For local ZIPs,
Builder automatically uses the cache's pinned checksum or an adjacent `.zip.sha256`
file. An invalid sidecar blocks preview. Without either, archive integrity is still
checked, but publisher authenticity must be established by obtaining the ZIP from
a trusted source. Local selections show the manifest summary; published release
notes are available after an online check. Notes are informational, not executed.

Review changed files, conflicts and manual follow-up, then choose **Apply patch**.
Apply rechecks the exact ZIP digest captured internally during preview. Download
and preview never apply the patch or change project files.

This UI is available in the source-based Builder after restart; older packaged
Builder downloads require a separately built app update. They can be bootstrapped
using the trusted current source checkout and CLI below.

## Preview and apply from the command line

Run the updater from a trusted current checkout or reviewed installation. Python
3.11+ and PowerShell are required by the CLI; the packaged Builder bundles Python.
The updater never runs scripts or code contained in a patch ZIP.

```powershell
python scripts/playbook_patch.py preview `
  --bundle C:\releases\scratch-workspace-patch.zip `
  --repo C:\repos\ExistingProject

python scripts/playbook_patch.py apply `
  --bundle C:\releases\scratch-workspace-patch.zip `
  --repo C:\repos\ExistingProject `
  --sha256 <reviewed-64-character-ZIP-checksum>
```

In an installed copy the entry point is
`engineering-playbook/scripts/playbook_patch.py`. Preview writes nothing and exits
2 for framework conflicts; invalid bundles or other failures exit 1. Apply requires
the reviewed ZIP checksum. Hashes detect corruption and content changes; obtain the
bundle and expected checksum from a trusted publisher because hashes are not signatures.

Every managed file must match the declared base or already match the target. A local
edit, missing base file, incompatible snapshot or unexpected file at an added path
blocks replacement. There is no force option. Preserve the local change and resolve
its ownership before retrying, or use a separately reviewed migration. Unknown files
outside the framework allowlist are preserved. File deletion, catalog schema changes
and removal of profiles/capabilities are not supported patch operations.

## What changes and what remains for review

The updater writes only changed files under `engineering-playbook/` and, when an
existing `.engineering-playbook.json` is present, its `playbook_version` and
`last_playbook_patch` receipt (ID and ZIP digest). Other configuration fields are
preserved. It creates no project configuration if one was absent.

AGENTS.md and project-owned documents are preserved byte-for-byte, including local
and organizational rules. Changed templates are reported. Suggested selected
governance blocks are saved as `AGENTS.blocks.md` beside the external backups; merge
them into AGENTS.md explicitly without deleting local instructions. If AGENTS.md is
missing, use those blocks to establish the startup entry point. Review project
template changes in their existing owning documents. A framework apply may succeed
while governance adoption remains pending this manual reconciliation.

After reconciling instructions, run the installed governance verifier and the
repository's required checks. Review the diff and use the normal project change
process. The updater does not initialize Git, stage, commit, push or open a PR.
Reapplying the same target and receipt is a no-op.

## Backups and recovery

Apply creates a unique external agent task folder through the trusted workspace
helper. It prints a backup path containing original replaced files, the original
project configuration when changed, a transaction journal and instruction blocks.
No logs, backup directories or diagnostic tests are added to the project.

The journal lists each changed path and before/after hash; `before: null` means the
file was newly added. Individual replacements are atomic. Caught failures attempt
to restore completed writes; concurrent edits are retained and reported for manual
recovery. The journal records `applied`, `rolled_back` or `recovery_required`.

An abrupt process or machine interruption can leave the journal at `prepared` and
some files updated. Stop other writers, inspect the journal and compare actual
hashes before acting. A retry can complete a mixture of exact base/target files.
For manual rollback, restore backed-up originals only after checking for newer edits;
remove a newly added file only when its current hash still matches the recorded
patch output. Review project metadata alongside framework files. Keep backups until
the patch and any instruction reconciliation are accepted. Cleanup is explicit.
