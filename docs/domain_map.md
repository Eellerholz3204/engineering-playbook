# Repository Builder domain map

`playbook.json` owns the profile/capability catalog and packaged resource list.
`repository_builder` presents creation plans; PowerShell scripts validate and create
repositories. Templates provide project-owned starting documents. Framework files
are installed under `engineering-playbook/`. In this source repository they live
at the root. Metis-specific instructions are an optional capability that refers
to `metis-engineering-playbook/docs/contract_agent_workflow.md`; that repository
continues to own Metis governance and project semantics.
