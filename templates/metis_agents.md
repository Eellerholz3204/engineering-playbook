<!-- BEGIN METIS GOVERNANCE CONTEXT v1 -->
## Metis governance sources

This repository participates in Metis. Locate the existing
`metis-engineering-playbook` checkout and read `docs/contract_agent_workflow.md`,
including its required context and reuse procedure. Use the repository identity
and domain map to locate it; a sibling checkout is a convenience, not authority.
If unavailable, report the missing source before dependent work.

Read the central product vision, domain map, data platform architecture, accepted
architecture decisions, current status/milestone, roadmap and reference data,
then the corresponding documents of affected producer and consumer repositories.
Follow links to exact contracts, registry versions, approvals and completed proof.
For CDM consumers, read the released Metis dictionary in `metis-data-contracts`
and M-016/M-017 completion evidence in the central `docs/reference_data.md`.
Reuse completed validation and existing common measure stages. Establish measure
ownership from the domain maps before implementing a consumer or publisher.

Use existing normal checkouts, feature branches and pull requests. Create a new
worktree or clone for isolation only when Eric explicitly requests it. Preserve
committed, modified and untracked work; never silently stash, reset or clean it.
Do not switch a shared checkout's branch while another task is using it.
Keep durable decisions in the prescribed owning project documents. Agent work
runs only during an active session; do not promise work after yielding.
<!-- END METIS GOVERNANCE CONTEXT v1 -->
