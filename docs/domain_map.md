# Repository Builder domain map

`playbook.json` owns the profile/capability catalog and packaged resource list.
`repository_builder` presents creation plans; PowerShell scripts validate and create
repositories. Templates provide project-owned starting documents. Framework files
are installed under `engineering-playbook/`. In this source repository they live
at the root. Metis-specific instructions are an optional capability that refers
to `metis-engineering-playbook/docs/contract_agent_workflow.md`; that repository
continues to own Metis governance and project semantics.

`GOVERNANCE_CONTEXT.md` owns scratch, blocker classification and artifact-promotion
policy. `scripts/initialize_agent_workspace.ps1` owns external task-folder resolution
and creation; the shared repository generator calls it for every profile. Builder
explains the behavior without implementing a second path resolver. Scratch is local
execution state outside version control, not project authority or a build dependency.

`repository_builder/patching.py` owns patch snapshot validation, preview, application
and recovery. `scripts/playbook_patch.py` and `repository_builder/patch_ui.py` are
CLI/UI adapters. `.github/workflows/playbook-patch.yml` prepares artifacts for review;
it owns no publication or downstream Git authority. Patch baselines are content
hashes of reviewed framework snapshots, not inferred from a version label alone.
