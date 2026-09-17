# Architecture Principles

- Define explicit bounded contexts and ownership boundaries.
- Keep domain models independent of CLI, persistence, filesystem, cloud SDKs, reports, workspaces, workflows, and UI.
- Use strongly typed identities for important domain concepts.
- Capture mutable inputs as immutable snapshots when historical decisions depend on them.
- Preserve audit history through append-only records and explicit supersession.
- Generate deterministic identities from canonical, versioned encodings.
- Treat workspaces, reports, dashboards, and search indexes as projections.
- Preserve uncertainty in extraction, reconciliation, and inference.
- Retain provenance for every derived conclusion.
- Separate evidence acquisition, processing, profiling, evaluation, ranking, workflow, and final human decisions.
- Keep deterministic services free of hidden LLM calls.
- Prefer the smallest compatible correction when defects are discovered.
