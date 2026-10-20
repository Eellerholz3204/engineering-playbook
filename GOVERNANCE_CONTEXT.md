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

## Agent scratch space and project ownership

Work performed to complete a task is not automatically a project deliverable.
Classify blockers and supporting artifacts before choosing where to fix or keep them:

| Work | Owner and destination |
|---|---|
| Experiments, one-off reproduction scripts, diagnostic tests, temporary fixtures, logs, working notes and local environment workarounds | External agent task workspace |
| Reusable agent tooling, launcher fixes and their maintained tests | The repository that owns the tooling |
| Supported product behavior, project contracts and maintained build/development workflows | The project repository |

New repositories receive an external workspace automatically. From a generated
repository, resolve or create a separate folder for the current task:

```powershell
$agentScratch = & ./engineering-playbook/scripts/initialize_agent_workspace.ps1 `
    -RepositoryPath (Get-Location).Path -TaskId 'task-123'
```

In this framework source repository use `./scripts/initialize_agent_workspace.ps1`.
The default on Windows is `%LOCALAPPDATA%\AgentWorkspaces\<checkout-name>-<path-hash>\<task-id>`.
The checkout's absolute path identifies its workspace; separate clones/worktrees
and moved checkouts get separate locations. No absolute scratch path is committed.
Use a unique task ID for concurrent work; repeat the same ID to resume it. The
generator creates the `default` task folder. Fresh clones create their workspace
on first helper invocation. Scratch is local and is not shared by Git.

Set `ENGINEERING_PLAYBOOK_SCRATCH_ROOT` to an external absolute directory when a
different location is needed (including isolated tests). The helper rejects
overlapping checkout paths and directory links in the scratch path. `-ResolveOnly`
prints the location without creating it; `-WhatIf` also makes no changes. If the
workspace is unavailable, report the cause; do not silently put scratch in the
project's source, tests, or documentation directories.

### Handling blockers

Diagnose in scratch first. A local environment workaround can unblock authorized
work without becoming a project change. Fix a project defect in the project;
route a reusable tool defect to its owning repository with focused tests there.
Do not create tooling-only PRs in consumer projects, copy tool tests into every
consumer, or turn each blocker into a new project milestone. Cross-repository
changes still require applicable authority; a blocker does not expand scope.
Record only durable project impact and unresolved dependencies in project docs.

### Promoting artifacts and tests

Before staging a helper, test, fixture, report or document, identify the maintained
project requirement, supported contract or development workflow it protects, and
its owning repository. Keep the smallest useful artifact and regression coverage.
Checks that only prove a temporary diagnostic or agent workaround belong in scratch.
Discovery by an agent does not disqualify a real product regression test.
Do not remove existing tests just because of their age, count, or agent origin;
review their supported behavior and ownership before moving or retiring them.

Project builds, required tests and CI must work from a clean checkout with declared
dependencies and no scratch files, hidden patches or local absolute-path imports.
Run scratch diagnostics explicitly; do not add scratch to test discovery, package
inputs, CI jobs or release artifacts. At the checkpoint, inspect the staged diff
for accidental agent artifacts and verify that project success does not depend on
the scratch environment. A passing diagnostic is not a substitute for project checks.

Scratch notes may contain task state and reproduction commands, but are not an
authority for project decisions or required evidence. Promote durable decisions
to existing owning documents and required retained evidence to an approved project
or artifact store. Do not retain secrets or sensitive copied data in scratch.
No automatic cleanup runs: review task folders for needed evidence, then remove
only explicitly selected completed task folders under normal deletion authority.

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
