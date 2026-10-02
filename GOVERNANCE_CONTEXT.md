# Governance context loading

Before proposing discovery or changing code, load the governing context. Repeat
this process when the task crosses a repository boundary or its scope changes;
after context compaction, re-read any source needed to resolve uncertainty.

1. Read the repository's `AGENTS.md`, installed `DEVELOPMENT_WORKFLOW.md`,
   `REPOSITORY_CONTRACT.md`, and `DOCUMENTATION_REQUIREMENTS.md`.
2. Read project-owned product vision, domain map, architecture decisions, current
   status, roadmap, milestone ledger, unreleased notes, and current milestone
   when present. Follow any explicitly documented equivalent paths.
3. Follow the domain map's organizational governance and producer/consumer
   references. Read each affected repository's own installed workflow and required
   documents. A central playbook does not replace local responsibilities or state.
4. Follow accepted decisions to their contracts, registries, source definitions,
   implementation and completed evidence. Read access/identity, security and
   operations records and their canonical artifacts before using a runtime.
5. Reconcile documentation with branches, commits, modified/untracked files,
   selected versions and verified runtime evidence. Preserve unrelated work.
   Distinguish proposed, implemented, released, deployed and active states.
6. Before edits, give a brief context check: intended outcome; responsible owners
   and dependency direction; accepted decisions and constraints; implementation
   and evidence to reuse; actual gaps and authority to proceed. Reference sources
   and exact versions where relevant. This is not another approval gate.
7. Continue authorized work. Ask only for an actual unresolved decision or missing
   access, identifying the source and the dependent action. Do not ask the user to
   restate documented decisions or repeat completed discovery without evidence of
   a gap or contradiction.
8. Keep decisions, corrections, verification and next steps in the existing owning
   project documents. Preserve historical evidence and mark superseded guidance.
   Chat, temporary notes and a generated summary are not governance authorities.

## Startup entry point and verification

Every generated repository receives a project-owned `AGENTS.md` that invokes this
procedure. Organizational capability packs add scoped instructions there. Keep
these entry points small; read linked evidence as needed rather than copying all
repositories into the prompt. Missing mandatory context must be reported before
work that depends on it; independent authorized work may continue.

Run `python engineering-playbook/scripts/verify_governance_context.py --repo .`
to check entry points and required local document paths. For Metis, add `--metis`
and, if the central checkout is not a sibling, `--metis-root PATH`. Add
`--source PATH` to compare the installed governance assets to a reviewed playbook
source. In isolated CI use `--local-only` to skip external checkout availability;
run the full check locally before dependent work. The bundled asset manifest
detects local instruction/procedure drift without changing older framework files.
These structural checks cannot prove that an agent read or understood
the documents. Record any project-specific path mappings in the domain map.

The installer preserves existing AGENTS.md files and reports required manual
reconciliation. Reconcile the generated blocks without deleting local rules.
This procedure grants no release, deployment or external-mutation authority.

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
