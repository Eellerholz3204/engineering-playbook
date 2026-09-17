# Prompt Patterns

## Reconcile an existing project

```text
Read engineering-playbook/DEVELOPMENT_WORKFLOW.md and reconcile the installed Engineering Playbook with the verified repository state. Preserve project-owned documentation and source code. Complete the reconciliation checkpoint, commit and push it, then continue through the committed milestone queue unless genuine human input or authorization is required.
```

## Standard continuation

```text
Read engineering-playbook/DEVELOPMENT_WORKFLOW.md and continue through the committed milestone queue.
```

## Explicit bounded milestone

```text
Follow engineering-playbook/DEVELOPMENT_WORKFLOW.md.
Read all documents required by engineering-playbook/DOCUMENTATION_REQUIREMENTS.md.
Complete docs/current_milestone.md as one bounded checkpoint.
Run verification, update documentation, commit, push, and continue to the next committed milestone.
Stop only for a genuine blocker or required human input, feedback, credentials, or authorization.
Do not tag, release, publish, modify external systems, or perform destructive cleanup unless explicitly authorized.
```

## Release

```text
Follow engineering-playbook/DEVELOPMENT_WORKFLOW.md and engineering-playbook/RELEASE_PROCESS.md. Perform only explicitly authorized release actions. Verify version, commit, annotated tag, branch push, tag push, remote state, and final clean working tree.
```
