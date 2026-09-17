# Release Process

Before release:

1. Verify branch, HEAD, remote state, version, and working tree.
2. Confirm the milestone and project documentation are complete.
3. Confirm `docs/releases/unreleased.md` reflects implemented changes.
4. Run the complete verification suite.
5. Audit security and runtime artifacts.
6. Determine the semantic version.
7. Prepare release notes.

When explicitly authorized:

1. Update version references and release documents.
2. Run verification again.
3. Stage only the intended scope.
4. Commit.
5. Create an annotated tag.
6. Push the branch.
7. Push the tag.
8. Verify remote branch and tag.
9. Confirm the final working tree is clean.

A release is incomplete until all intended remote operations are verified.
