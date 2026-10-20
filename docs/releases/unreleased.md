# Unreleased

## Added

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
