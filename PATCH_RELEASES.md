# Playbook patches for existing repositories

A patch is a reviewed ZIP with a unique patch ID, integrity hashes and release
summary. Two formats are supported: a portable additive scratch feature (schema 2)
and an exact framework snapshot upgrade (schema 1). Neither updates the installed
Builder application, publishes releases, creates PRs or changes project source/tests.

## Portable scratch-workspace feature

Use this instead of preparing a different full-framework upgrade for each repository.
One ZIP supports catalog schema 1 / playbook 3.0.1 and schema 2 / playbook 3.2.0,
3.2.1, 3.3.0 and 3.3.1. VERSION must agree with the catalog. Compatibility checks
the feature's destinations, not unrelated framework files or the repository name.
Unknown catalog/version combinations still require review before support is added.

The fixed recipe:

- Adds `engineering-playbook/scripts/initialize_agent_workspace.ps1` if absent.
  Reuses an equivalent installed helper without rewriting it.
- Adds `engineering-playbook/features/agent-scratch-workspace/POLICY.md` from the
  source's canonical scratch policy, plus `feature.json` describing this feature.
- Appends one marked scratch section to root `AGENTS.md` (or creates that file
  when absent). Every existing byte, including custom instructions and encoding,
  is retained. Preview displays the section before Apply.
- Leaves VERSION, playbook.json, SHA256SUMS.txt, governance asset pins, project
  configuration, workflows, project documents, source and tests unchanged.

This is **scratch support, not a framework version upgrade**. The feature receipt
uses normalized UTF-8 component hashes (BOM removed, CRLF converted to LF); its
AGENTS.md hash covers only the marked section. Original framework manifests retain
their original meaning. No copied updater or tooling tests are installed.

Existing feature files must be absent or equivalent in content. UTF-8 BOM and CRLF
differences alone are harmless and are not rewritten. A different existing helper,
policy, receipt or edited/duplicate/incomplete marked section blocks application.
Unrecognized instruction encoding or an unclosed fenced block requires explicit
reconciliation. There is no force option. Custom instructions elsewhere do not
block the mechanical append, but **Compatible is not semantic approval**: review
the new section against local rules. Conflicting instructions remain a human/project
owner decision. The new section expressly retains existing organizational authority.

Build from the trusted current source with refreshed checksums:

```powershell
python scripts/update_checksums.py
python -m unittest discover -s tests -v
python scripts/playbook_patch.py build-scratch `
  --target . `
  --output C:\releases\agent-scratch-workspaces.zip `
  --patch-id agent-scratch-workspaces-portable-v1 `
  --summary 'Add external agent scratch workspaces while preserving custom instructions and the installed framework version.'
```

The ZIP and sidecar must be outside the source snapshot; existing artifacts are
never overwritten. The artifact-only workflow defaults to `scratch-feature` and
needs no base_ref. For a full snapshot upgrade choose `snapshot` and supply base_ref.
Review and test disposable copies before separate release authorization. Published
assets use the existing fixed feed and checksum/download trust rules.

Use current source-launched Builder (restart it) or current trusted CLI: old
schema-1 readers reject this format safely. Select the additive scratch patch,
Preview, expand the AGENTS.md section and review changes, then separately Apply.
Builder pins the inspected inputs; if they change before Apply, preview again.
Afterward invoke the installed helper for each task and follow the repository's
normal verification/review process. Reapplying a complete feature is a no-op.
Already scratch-enabled full-snapshot installations may still add this dedicated
feature policy/receipt/section; the existing helper and prior instructions remain.

The [portable feature release](https://github.com/Eellerholz3204/engineering-playbook/releases/tag/playbook-patch-agent-scratch-workspaces-portable-v1)
is published and available through Builder's **Check for patches**. The three older
exact-baseline releases are retired to recoverable drafts; their tags/assets are
retained, but they no longer appear in the public feed. Their locally cached copies
were archived outside Builder discovery. Restart Builder to clear session choices.
Already-applied patches are not undone. See the
[release notes](docs/releases/agent-scratch-workspaces-portable-v1.md).

## Prepare an exact snapshot patch release

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

### Legacy installations with separately adopted governance

Some older catalogs omit governance files installed later. A publisher may pass
`--base-additions reviewed-baseline.json` to `build`: this JSON object maps each
additional framework-relative path to its reviewed, exact SHA-256. The original
base catalog/checksums must still validate. Each additional file must exist, match
its pin, be outside the base allowlist and belong to the target allowlist. There
is no directory scan, baseline override, text normalization or consumer force mode.
The resulting ZIP uses the existing version-1 format and works with existing
patch-capable Builders. Review policy differences before building; exact pins do
not establish that replacing a local policy is appropriate.

Historically, the reviewed **metis-engineering-playbook** installation used
**agent scratch workspaces (legacy Metis 3.2.1 to 3.3.1)**. That retired patch preserved the reusable
access/identity requirements in the new framework and leaves project documents,
AGENTS.md and unknown files untouched. This baseline includes 51 catalog files plus
five adopted governance files, with their historical BOM/line-ending bytes. Other
3.2.1 installations are not automatically compatible. See the
[historical migration notes](docs/releases/scratch-workspace-legacy-metis-2026-10.md).
For new scratch adoption, select the portable feature instead.

### Select and review a patch

To obtain a patch directly, choose **Patch existing repository**, then **Check for
patches**. Choose an **Existing repository**. Builder checks local and discovered
published patches against that repository's actual framework files, downloading and
verifying published ZIPs into the external cache as needed. Choosing the repository
first also works: **Check for patches** checks newly discovered releases for it.
No network discovery runs just from opening the screen.

The single **Patch** selector labels and ranks results:

- **Compatible**: supported file contents; select and preview before applying.
- **Already applied**: framework matches the target, even if another patch delivered
  it. Preview can still show receipt or instruction reconciliation.
- **Not compatible**: different starting files or local changes.
- **Unable to check**: download, checksum, archive or repository inspection failed;
  select it to read the reason. This is not a compatibility verdict.

Compatible choices sort first. Incompatible ones are hidden until **Show all patches**
is enabled, except an explicitly selected patch remains visible with its explanation.
Failed checks and already-applied patches stay visible. A sole compatible choice is
selected only when no explicit patch selection exists; the repository is never chosen
automatically. If none fits, Builder reports that instead of recommending a version
number match. A version label or release title is not a compatibility test.

Checks run one patch at a time with progress. **Stop checking** stops after the
current check; remaining patches are marked **Not checked**. **Refresh lists**
rechecks current files and retries failures without refreshing the online catalog.
Changing repositories discards previous compatibility results. Results are advisory
snapshots: **Preview patch** revalidates the selected ZIP and current repository,
and only its separate **Apply patch** action can write files. Classification never
creates a reviewed/apply-ready transaction.

Published releases and local ZIPs share this list.
Published patches show their readable release name, purpose and expandable release
notes before download. Without a target repository, a sole available release may
be selected, but it is not yet classified. Existing selections are preserved.
Builder checks the public `Eellerholz3204/engineering-playbook` GitHub releases,
excluding drafts, prereleases and releases without a patch ZIP/checksum pair.
No sign-in is required and no network check runs just from opening Builder.

Compatibility checking and Preview download published ZIPs as needed and validate their checksums
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
authenticity. Download integrity alone does not establish repository compatibility.

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

An incompatible preview shows **Patch blocked** with the conflict count and a
disabled primary action. This can be a different framework revision, not necessarily
user edits or corruption. Select the patch for the installed baseline; after an
explicit reconciliation outside Builder, use **Refresh lists** and preview again.
There is no force-apply option. Source-launched Builder needs a restart to load
this status UI; it is not an update to previously packaged desktop binaries.

Historically, early 3.3.0 installations matching source revision `7dc6467` used
**agent scratch workspaces (early 3.3.0 repositories)**.
See its [historical notes](docs/releases/scratch-workspace-early-330-2026-10.md).
Both snapshots use the historical 3.3.0 version label; exact content checks, not
that label alone, determine compatibility. That retired bundle has the same verified
target framework as the first patch and a different reviewed starting snapshot.
Use the portable feature for new scratch adoption.

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

For schema-1 snapshot patches, every managed file must match the declared base or already match the target. A local
edit, missing base file, incompatible snapshot or unexpected file at an added path
blocks replacement. There is no force option. Preserve the local change and resolve
its ownership before retrying, or use a separately reviewed migration. Unknown files
outside the framework allowlist are preserved. File deletion, catalog schema changes
and removal of profiles/capabilities are not supported patch operations.

## Snapshot patches: what changes and what remains for review

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
