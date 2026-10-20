# Unreleased

GOV-011 publication accounting: the framework through `f6013bc` is published as
[scratch-workspace-legacy-metis-2026-10](scratch-workspace-legacy-metis-2026-10.md),
the exact-baseline legacy Metis 3.2.1-to-3.3.1 migration. It includes the current
framework/Builder source, but does not update installed desktop binaries. Both
previous patch releases remain unchanged; their historical accounting follows.

Publication accounting: the framework snapshot through `dae80da` is now distributed
as [scratch-workspace-2026-10](scratch-workspace-2026-10.md), the first 3.2.1-to-3.3.0
patch. The source implementation history below also covers Builder features awaiting
a separate packaged app release. The later dropdown changes are not in this patch;
no new desktop installer has been published.

The same target framework is also published as
[scratch-workspace-early-330-2026-10](scratch-workspace-early-330-2026-10.md) for
the exact early-3.3.0 baseline `7dc6467`. It is an alternate-baseline patch, not a
new target snapshot or desktop release. The original 3.2.1 patch remains unchanged.

## Added

- Portable schema-2 scratch feature patches and `build-scratch` CLI/workflow support.
  One additive recipe supports reviewed 3.0.1/3.2.0/3.2.1/3.3.0/3.3.1 catalog families,
  installs the helper/policy/feature receipt and appends a previewable marked AGENTS.md
  section. Existing bytes and custom authority are preserved. Modified feature
  destinations block; unrelated framework edits do not. BOM/CRLF equivalence is
  read-only. Framework versions/manifests/configuration stay unchanged.
- Builder labels additive features distinctly, shows the appended instructions and
  pins inspected inputs through Apply. Existing snapshot releases/readers retain
  their format; old readers safely reject schema 2. This is unreleased source and
  a local candidate, not publication or application to real consumers.

- Repository-aware patch compatibility labels, compatible-first ordering and Show all
  filtering. Repository selection and explicit discovery/refresh check actual files,
  with verified external downloads, progress and stop/retry. Failed checks remain
  visible; classification never grants Apply approval. Preview revalidates current
  files. This Builder source change is not in the published patch releases.

- Publisher-only `--base-additions` pins for separately adopted legacy governance
  files; emitted patches retain exact version-1 matching and all preservation rules.
- Framework 3.3.1 retains the access/identity startup and documentation requirements
  from the reviewed legacy Metis installation. No project identity facts are bundled.
  The dedicated legacy patch is published and download-back verified; prior releases
  and packaged Builder binaries remain unchanged.

- Explicit **Patch blocked** explanation and disabled primary action for conflicting
  previews; changing selection or refreshing resets the review gate. Conflicts can
  indicate a different baseline, not necessarily local edits or corruption.

- One patch selector for published releases and local ZIPs, readable release names,
  purpose descriptions and expandable release notes. Preview downloads and verifies
  published patches automatically; local previews use available sidecars/cache pins.
  Removed the separate download selector/action and manual SHA-256 entry. Apply
  still requires a separate action and rechecks the previewed bytes.

- Explicit in-app checking and downloading of published stable playbook patches,
  with checksum/archive validation, an external persistent cache, offline selection
  and clear network failure states. Preview/apply remain separate user actions.

- Searchable existing-repository and patch dropdowns with bounded local discovery,
  Browse fallback, session choices, full paths and Refresh. Changing inputs clears
  prior preview state; changing patches clears the old expected checksum.

- Build offline framework patch ZIPs/checksums from explicit base/target snapshots,
  with CLI preview/apply and a Builder **Patch existing repository** flow.
- Validate every framework file, reject local conflicts and untrusted archive paths,
  preserve project content, and record installed version/patch identity in existing
  configuration. Keep recoverable backups and instruction merge blocks in scratch.
- Artifact-only GitHub Actions patch packaging workflow and release/application guide.
- Product coverage for patch integrity, preservation, repeated apply, failure recovery,
  real generator output, CLI and Builder preview/apply; scratch paths support Unicode.

- External agent scratch space for every new repository profile, with a reusable
  PowerShell helper for task isolation, resume, no-write preview and local overrides.
- Builder review explanation and creation-output workspace location; saved plans
  remain compatible and do not contain machine-specific scratch paths.
- Installed blocker ownership and artifact-promotion rules: temporary diagnostics
  stay external, reusable tool fixes stay with their owner, and project tests protect
  maintained behavior. Clean project verification must not depend on scratch.
- Focused generator, UI round-trip, preservation and packaged-resource verification
  for the scratch-space behavior; no downstream test removal or automatic cleanup.

- Automatic AGENTS.md startup instructions for all generated repositories.
- Selectable Metis governance capability and cross-repository context loading.
- Read-only verification of entry points, required paths and source asset drift.
- Regression coverage for generation, missing context and preserving local rules.
- Central model and reasoning-effort routing policy with task tiers and escalation
  triggers; generated AGENTS.md receives the compact rule.
- Model-routing policy now resides in mandatory installed governance context, and
  generated AGENTS.md references the installed path.
