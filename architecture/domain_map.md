# Domain Map Pattern

A project domain map identifies bounded contexts, ownership, authoritative state, relationships, and dependency direction.

For each context document:

- purpose and business responsibility;
- owned aggregates and history;
- commands and outputs;
- upstream and downstream contexts;
- organizational knowledge consumed;
- evidence consumed or produced;
- deterministic services;
- workflows and projections;
- prohibited responsibilities.

Explicitly distinguish domain contexts from Document Processing, workflows, workspaces, consoles, reporting, and infrastructure adapters.
