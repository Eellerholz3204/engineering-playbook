# Development Workflow

## Startup

Before changing anything:

1. Read `engineering-playbook/REPOSITORY_CONTRACT.md`.
2. Read `engineering-playbook/DOCUMENTATION_REQUIREMENTS.md`.
3. Read `docs/product_vision.md` and `docs/domain_map.md`.
4. Read `docs/project_status.md`, `docs/roadmap.md`, and `docs/architecture_decisions.md`.
5. Read `docs/milestone_details.md` and `docs/releases/unreleased.md`.
6. Read `docs/current_milestone.md` when present.
7. Inspect branch, HEAD, version, tags, working tree, tests, and relevant runtime state.
8. Treat verified state as authoritative when documentation is stale.
9. Preserve unrelated work and identify pre-existing changes.

## Milestone discipline

- Complete one bounded milestone.
- Treat its boundary as a verification, documentation, commit, and push checkpoint; close the milestone before beginning another.
- Do not silently expand scope.
- Keep accepted architecture stable unless a genuine defect is demonstrated.
- Prefer the smallest compatible correction.
- Preserve immutable evidence and business history.
- Do not allow orchestration layers or consoles to acquire business logic.
- Authorization to implement a milestone includes staging, committing, and pushing its verified repository changes to the current tracked branch.
- Never include unrelated work in a milestone commit.
- Tagging, releases, publishing, destructive cleanup, external-system mutation, and consequential business decisions require explicit authorization.

## Milestone continuation

The end of a milestone is a documentation and verification boundary, not necessarily the
end of an agent work session.

After completing a milestone, the agent must:

1. Run the required focused and full verification.
2. Synchronize status, roadmap, milestone ledger, decisions, and unreleased notes.
3. Record the completed milestone outcome and final repository state.
4. Read the next milestone from the repository's current documentation.
5. Evaluate the human-review and authorization gates before continuing.

The agent should continue automatically into the next documented milestone when all of
the following are true:

- the next objective and checkpoint boundary are explicit and unambiguous;
- the next milestone is `ACCEPTED` and has delivery status `NEXT` or `SEQUENCED`;
- no human-review gate is declared or reached;
- no release, semantic approval, architecture acceptance, consequential decision,
  external mutation, destructive action, or new credential/permission is required;
- required inputs and compatible upstream interfaces are available;
- the preceding milestone is genuinely complete rather than merely paused.

Accepted committed milestones carry standing implementation authority through the documented queue. Each milestone remains bounded by its documented scope and genuine human authorization gates.

The agent must stop and request human review only when the milestone declares a genuine human-review gate, the next committed milestone is missing or ambiguous, verification cannot be repaired safely, a blocker prevents meaningful progress, a required human decision is identified, or new authority is needed. At that point the agent prepares a concise review packet with
the decision requested, evidence, recommendation, alternatives, and consequences.

When connected Gmail is configured as the human-review channel, the agent sends the review
request to the authenticated account using recipient `me`. The subject includes the
repository and milestone identifier so the thread can be found deterministically. The
agent then monitors that thread for the human reply and does not continue past the gate
until the decision is recorded in project documentation.

The review request asks the human to reply with one of:

- `APPROVE` plus any conditions, authorizing the documented next step only;
- `REVISE:` followed by requested changes, returning the current milestone to active work;
- `STOP`, ending automatic continuation.

The agent reads the latest reply in thread context, records its message identity,
timestamp, decision, conditions, and affected milestone, and preserves the email as review
evidence without copying sensitive body content unnecessarily. Free-form replies may be
interpreted only when the decision is unambiguous. Otherwise the agent requests
clarification and remains stopped. Email approval never expands authority beyond the
specific decision and milestone described in the review request.

## AI and human responsibilities

AI may implement, analyze, test, extract, summarize, propose, document, and verify.

Humans decide product direction, organizational knowledge, architecture acceptance, workflow disposition, employment or other consequential business decisions, and release authorization.

## Completion

Before closing each milestone:

1. Update all affected project documentation.
2. Update `docs/releases/unreleased.md` with implemented work only.
3. Record an ADR when a lasting architectural decision changed.
4. Run focused verification.
5. Run the complete verification suite.
6. Stage only milestone-owned changes, commit them, push to the tracked branch, and verify remote state.
7. Record changed files, verification, limitations, documentation updates, ADR status, commit, remote state, and the next committed milestone.
8. Continue to the next committed milestone when eligible; otherwise report the exact blocker, review, or authorization gate and stop.
