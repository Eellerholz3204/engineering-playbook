# Testing Standards

Select focused verification appropriate to the repository profile: unit tests,
persistence and service integration tests, CLI tests, dbt model and data tests,
bounded-context verifiers, contract tests, migration tests, and security regressions.

Test deterministic identity, ordering independence, immutable history, snapshot fidelity, round-trip reconstruction, malformed records, duplicate identities, relationship integrity, path traversal, credential patterns, unsafe files, historical defect regressions, and reconciliation safety.

Architecture tests should enforce the repository's declared dependency direction and
prevent business logic from migrating into orchestration, persistence, transport, UI, or
other non-owning layers.

Do not weaken verification merely to make a milestone pass.
