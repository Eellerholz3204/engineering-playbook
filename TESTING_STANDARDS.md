# Testing Standards

Select focused verification appropriate to the repository profile: unit tests,
persistence and service integration tests, CLI tests, dbt model and data tests,
bounded-context verifiers, contract tests, migration tests, and security regressions.

Test deterministic identity, ordering independence, immutable history, snapshot fidelity, round-trip reconstruction, malformed records, duplicate identities, relationship integrity, path traversal, credential patterns, unsafe files, historical defect regressions, and reconciliation safety.

Architecture tests should enforce the repository's declared dependency direction and
prevent business logic from migrating into orchestration, persistence, transport, UI, or
other non-owning layers.

Do not weaken verification merely to make a milestone pass.

## Maintained tests versus scratch diagnostics

A permanent test must protect supported project behavior, a contract or a maintained
development workflow. Add the smallest useful regression coverage for a real defect;
an agent discovering it is not a reason to exclude it. A blocker alone is not a
reason to add a test. One-off probes, environment troubleshooting and tests of agent
workarounds run explicitly in the external task workspace described in
`GOVERNANCE_CONTEXT.md`. Reusable tool tests belong in that tool's owning repository.

Keep scratch outside project test discovery and CI. Required checks must pass with
declared dependencies from a clean checkout without scratch fixtures, helpers,
imports or hidden patches. Do not copy a tool's suite into each consumer. Review
existing tests by behavior and ownership before retiring them; test count and agent
origin alone are not removal criteria.
