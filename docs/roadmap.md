# Roadmap

- GOV-001: governance context loading and adoption in the nine workspace Metis
  repositories - IMPLEMENTED locally; source and adoption PRs are open.
- GOV-002: central model and reasoning-effort routing - IMPLEMENTED locally on the
  source PR #1 branch; no downstream repositories are in scope.
- GOV-003: correct installed location for model-routing authority - IMPLEMENTED
  locally on source PR #1; no downstream repositories are in scope.
- Eric confirmed the rollout excludes Architecture Intelligence, legacy
  athena_dbt and the Terraform checkout on 2026-09-26.
- Packaged release: follow the existing build/release process when authorized.
- GOV-004: external agent workspaces and artifact ownership - ACCEPTED, IMPLEMENTED.
  Scope: new repository generation, Builder explanation, installed helper/rules,
  ownership-focused testing and documentation; no existing-repository cleanup.
- GOV-005: releaseable patches for existing repositories - ACCEPTED, IMPLEMENTED.
  Scope: bundle build, preview/apply, preservation and recovery, Builder UI and
  artifact-only workflow. Actual publication and downstream rollout are separate.
- GOV-006: repository and patch dropdowns - ACCEPTED, IMPLEMENTED. Bounded local
  discovery, Browse fallback and refreshed preview state; no downstream updates.
- GOV-007: publish the first framework patch - ACCEPTED, IMPLEMENTED. Existing verified
  3.2.1-to-3.3.0 candidate, annotated source tag and ZIP/checksum release assets;
  no downstream application or Builder binary release.
- GOV-008: in-app published patch discovery and downloads - ACCEPTED, IMPLEMENTED.
  Fixed public release source, external validated cache and explicit preview/apply.
- GOV-009: unified patch selection and readable patch information - ACCEPTED, IMPLEMENTED.
  Automatic verified download during Preview, no manual hash field, purpose and
  release notes; explicit Apply and existing trust boundaries remain unchanged.
- GOV-010: explicit blocked patch state and early-3.3.0-compatible patch publication -
  ACCEPTED, CURRENT. New alternate-baseline release to the existing verified target;
  no forced overwrite, first-release changes, real consumer apply or binary rebuild.
