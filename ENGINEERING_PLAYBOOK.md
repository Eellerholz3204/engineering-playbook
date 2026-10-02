# Engineering Playbook v3

## Purpose

This playbook defines a reusable architecture and engineering framework for software repositories. It separates stable engineering laws from project-specific choices and preserves enough version-controlled context that work can continue without reconstructing earlier conversations.

## Authority model

1. Humans own product direction, architecture acceptance, organizational knowledge, workflow decisions, and business decisions.
2. AI assists through analysis, extraction, implementation, testing, documentation, and proposals.
3. LLM output is never authoritative merely because it was generated.
4. Verified repository and runtime state override stale documentation.
5. Project documentation must be corrected when verified state and documentation diverge.

## Model and reasoning-effort routing

Choose the least expensive available model and reasoning effort that can reliably
meet the task's governance, correctness, and verification requirements. Classify by
the work actually being performed; escalate if its scope or uncertainty changes.

| Work | Minimum routing |
|---|---|
| Routine mechanical work (for example, status checks, merges, polling, downloads, or hash checks) | Efficient tier, low effort |
| Narrow implementation with clear requirements and acceptance tests | Efficient tier, medium effort |
| Cross-repository contracts, statistical semantics, governance decisions, production authority, or final governance/release review | Governed-judgment tier, medium effort |
| Ambiguous architecture, security-sensitive judgment, conflicting evidence, or unresolved ownership | Governed-judgment tier, high effort |

Escalate to the governed-judgment tier when work encounters contract or schema
semantics, activation/readiness authority, statistical-method judgment, production
permissions or destructive operations, unclear ownership, conflicting evidence, or
repeated non-mechanical failures. Do not guess through a trigger; identify the
uncertainty and resolve it using the applicable governance sources. Repository
instructions may set a higher minimum for their work, but may not lower these
central minimums. These tiers describe capabilities, not fixed model names or
versions; any current model mapping is operational guidance and may change.

## Core architectural laws

- AI assists; humans decide.
- Organizational knowledge is human-curated, versioned, and frozen before authoritative use.
- LLMs may propose organizational knowledge but never become its authoritative source.
- Evidence is immutable.
- Business history is immutable or append-only.
- Document Processing is separate from Evidence Intake.
- Evidence Profiles are separate from Evaluation.
- Evaluation is deterministic once authoritative inputs and policies are selected.
- Ranking is separate from Evaluation.
- Operator Workflows orchestrate domains but do not own business data.
- The Operator Console orchestrates workflows and contains no business logic.
- Workspaces are operational surfaces and projections, not authoritative stores.
- Historical decisions reference immutable snapshots of the knowledge and evidence used.

## Ownership boundaries

### Playbook-managed

Everything under `engineering-playbook/` is governed by the installed playbook manifest. Immutable entries may be refreshed during reconciliation.

### Project-owned

Everything under `docs/`, project `scripts/`, source directories, and project configuration is owned by the project. Existing project-owned files are preserved during reconciliation.

### Generated

Generated outputs must be reproducible, clearly identified, and regenerated rather than hand-edited.

## Standard lifecycle

```text
Read repository contract
Verify actual state
Select one bounded milestone
Implement
Run focused verification
Run full verification
Synchronize project documentation
Record results and final repository state
Evaluate the human-review and authorization gates
Continue to the next documented milestone when eligible, otherwise stop
```

Milestones remain independently bounded even when an agent proceeds through several in
one work session. Completion, verification, and documentation may not be deferred until
the end of the multi-milestone run.

## Extension rule

The playbook defines patterns and document requirements. Each project records its concrete domain model, architectural decisions, operational surfaces, milestones, and implementation choices in project-owned documentation.
