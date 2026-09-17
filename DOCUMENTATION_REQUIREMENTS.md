# Documentation Requirements

## Framework versus project documentation

Files under `engineering-playbook/` define reusable rules and patterns. Files under `docs/` describe the actual project. Do not copy project facts into framework files or treat generic templates as verified project state.

## Required project architecture documents

### `docs/product_vision.md`

Define the problem, users, outcomes, guiding principles, AI authority boundaries, non-goals, success measures, and product scope.

### `docs/domain_map.md`

Define bounded contexts, ownership, authoritative state, integrations, dependencies, and the distinction among domain services, workflows, workspaces, projections, and UI.

## Profile and capability documents

Repository profiles install documents appropriate to the implementation type. A dbt data
product documents its contract, data quality, lineage, provenance, publication, and
compatibility. A Python service documents its service contract, deployment, operations,
security, and privacy.

Capability packs may add operator-console, workspace, document-processing, service-
operations, or AI-governance documents. Do not install or maintain a capability document
for a repository that does not implement that capability.

## Decision and delivery terminology

Track product or architecture decisions independently from delivery. Decision statuses are
`PROPOSED`, `ACCEPTED`, `REJECTED`, and `DEFERRED_DECISION`. Delivery statuses for
accepted work are `CURRENT`, `NEXT`, `SEQUENCED`, `BLOCKED`, `IMPLEMENTED`, and
`REMOVED`.

Do not call accepted work deferred. Describe work excluded from the active milestone as
“not in this milestone; remains committed,” and record its priority, dependencies,
acceptance criteria, and target milestone when known. `NEXT` and `SEQUENCED` work remains
mandatory unless an explicit superseding decision removes it.
## Required project state documents

### `docs/project_status.md`

Keep current version, branch, committed HEAD, working-tree status, capabilities, verification, runtime identifiers, limitations, and next milestone synchronized.

### `docs/roadmap.md`

Preserve completed history and record only genuine planned milestones.

### `docs/architecture_decisions.md`

Add an ADR only for a lasting architectural decision. Include status, context, decision, rationale, consequences, and supersession when applicable.

### `docs/milestone_details.md`

Maintain an append-only milestone ledger with identifier, name, scope, commit when known, verification, outcome, and status.

### `docs/releases/unreleased.md`

Record implemented changes under Added, Changed, Fixed, or Security. Use Deferred Decision only for genuinely undecided, non-committed work. Never represent planned work as completed.

### `docs/current_milestone.md`

Define the authorized objective, scope, constraints, verification, documentation updates,
checkpoint boundary, genuine human-review gate, notification channel, and continuation policy. Name the
next milestone when automatic continuation is allowed.

## Reconciliation

When templates evolve:

- install missing project documents;
- preserve existing project documents;
- report that human reconciliation is required;
- never overwrite project content automatically;
- refresh immutable framework files from the installed playbook source.

## End-of-milestone report

Record implementation changes, documentation changes, ADR status, verification results,
limitations, recommended next milestone, and final Git status at every milestone boundary,
including when the agent continues automatically.
