# Repository Builder agent instructions

This is the framework source repository. Begin with `DEVELOPMENT_WORKFLOW.md`,
`GOVERNANCE_CONTEXT.md`, `REPOSITORY_CONTRACT.md`, `DOCUMENTATION_REQUIREMENTS.md`
at the root and their required project documents. Installed repositories use the
`engineering-playbook/` prefix instead. Preserve existing project documents and
AGENTS.md instructions during installation. Exercise actual PowerShell generation,
UI plan round-trips and packaging tests when changing the catalog or installer.
Refresh bundle/checksum manifests with `python scripts/update_checksums.py`.
