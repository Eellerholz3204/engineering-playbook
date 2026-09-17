# Repository Contract

Every governed repository must be independently understandable and continuable from version-controlled material.

## Framework location

The installed framework lives under:

```text
engineering-playbook/
```

Project documentation lives under:

```text
docs/
```

The framework governs the project but does not describe it.

## Required project documents

- `docs/product_vision.md`
- `docs/domain_map.md`
- `docs/project_status.md`
- `docs/roadmap.md`
- `docs/architecture_decisions.md`
- `docs/milestone_details.md`
- `docs/releases/unreleased.md`
- `docs/current_milestone.md` when active work is authorized

Projects may rename domain-specific workspace documents when the generic pattern has a different project term, but the mapping must be explicit in `docs/domain_map.md`.

Repository profiles add type-specific documents. Capability packs add optional documents
such as operator consoles, workspaces, document processing, service operations, and AI
governance. Optional documents become governed project documents when selected.

## Required operating documents

- `engineering-playbook/DEVELOPMENT_WORKFLOW.md`
- `engineering-playbook/DOCUMENTATION_REQUIREMENTS.md`
- `engineering-playbook/playbook.json`

## Precedence

1. Verified repository and runtime state.
2. Accepted architecture decisions and frozen organizational knowledge.
3. Current project documentation.
4. Planning documents.
5. Conversation context.

When these disagree, preserve evidence of the discrepancy and reconcile documentation during the current bounded milestone.

## Authorization boundary

Staging, committing, tagging, pushing, releasing, deleting, rewriting history, changing external systems, and destructive cleanup require explicit human authorization.

Completing one milestone does not authorize the next. Agents may automatically continue
only when the next documented milestone remains inside standing authorization and has no
human-review or authorization gate. Milestone closure, verification, and documentation
remain mandatory even during continuous work.
