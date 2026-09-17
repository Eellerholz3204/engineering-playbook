# Contributing

Clone the repository, create a Python 3.11 virtual environment, and install
`requirements-builder.txt`. Start the UI with `python -m repository_builder`.
Keep project types, capability descriptions, and template mappings in `playbook.json`.

Run `python -m unittest discover -s tests -v` before proposing changes. The suite
creates disposable repositories and requires PowerShell, Git, and Python on PATH.
Desktop render checks are available through `python -m tests.render_builder`.

Update documentation and manifest checksums when changing framework-managed files.
Refresh the checksums with `python scripts/update_checksums.py`.
Build instructions and distribution verification are in `packaging/README.md`.
Do not commit local environments, generated releases, logs, credentials, or editor
connection settings. Keep changes focused and explain the resulting behavior and
validation in the pull request.
