# Current milestone

GOV-004: external agent workspaces and artifact ownership. Accepted by Eric's
2026-10-16 request to implement the agreed scratch-space approach in the playbook
and Repository Builder. Previous GOV-003 implementation is retained in the ledger.

Scope: external task workspace helper, automatic creation for every new repository
profile, installed ownership/promotion rules, Builder review explanation, retained
configuration compatibility, preservation on reconciliation and packaged resources.
Temporary diagnostics remain outside project deliverables; maintained generator
behavior and its focused regression coverage belong in this source repository.

Verification: actual generation across all profiles and available PowerShell
editions; task isolation, resume and no-write previews; invalid destination checks;
UI save/import round-trip and desktop review; reconciliation preservation; packaged
allowlist generation with refreshed checksums; full required test suite; diff check.

Checkpoint: update project documents and manifests, commit only milestone changes,
push to the current tracked branch and verify remote state. No new PR is required.
No downstream rollout, test deletion, automatic cleanup, merge or packaged release
is included. There is no next accepted implementation milestone; stop after closure.

Delivery: IMPLEMENTED. All 22 tests passed from a fresh tracked-file export without
local ignored artifacts. Actual desktop render/creation and Windows PowerShell 5.1
creation passed; all 76 packaged checksums passed. Commit/push closure is recorded
in the milestone ledger. No next accepted implementation milestone remains.
