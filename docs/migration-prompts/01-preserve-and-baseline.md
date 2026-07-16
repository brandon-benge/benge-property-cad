# Prompt 01: preserve and baseline the Benge repository

## Objective

Create a recoverable safety baseline and reviewed semantic golden for the dirty
legacy Benge checkout without changing product behavior.

## Work

1. Read the complete migration plan, the execution profile, and this prompt.
2. Record current `HEAD`, branch, status, remotes, tags, host/tool versions, and
   relevant CAD dependencies in `docs/migration/01-baseline-report.md`.
3. Preserve every current tracked, deleted, ignored, and untracked path,
   especially `.back_agents/`, `back_AGENTS.md`, both migration plans, generated
   output, caches, and the current agent/symlink state.
4. Create the authorized timestamped external bundle with a full-worktree
   archive, `git diff --binary`, staged diff, complete ignored/non-ignored
   untracked manifests, repository metadata, and SHA-256 checksums.
5. Extract the archive into a temporary no-checkout clone and prove paths,
   content, modes, symlink targets, deleted-state metadata, and Git status can be
   reconstructed. Record the exact bundle location and verification evidence.
6. Create a local annotated pre-migration tag on the untouched starting `HEAD`.
   Do not push it.
7. Run the current project lint, type, test, build, viewer, artifact, and
   determinism checks exactly as they exist. Record failures without repairing
   them and preserve the known post-build SVG/DXF hash mismatch as defect
   evidence rather than a golden.
8. Generate `tests/fixtures/model_contract_v1.json` from the valid pre-split
   semantic model: sorted 236 element IDs, material IDs, selected bounds,
   quantity aggregates, and the intentional model/spatial identifier migration
   mapping required by Sections 5 and 16 B0.
9. Add a focused test or standalone verifier proving the golden was generated
   from the baseline model and is internally consistent, without depending on
   corrupted final drawing hashes.
10. Record active legacy names, private imports, path injection, lifecycle side
    effects, tree sizes, and representative output hashes for later removal.

## Constraints

- Do not change source behavior, dependencies, workflows, viewers, agents, or
  remote state.
- Do not delete `.back_agents/` or `back_AGENTS.md` in this prompt.
- Do not inspect or modify tooling source. Existing installed/copied tooling may
  be used only to reproduce the current Benge baseline.
- Do not clean caches or generated files until they are inventoried and archived.

## Clarification and stop gates

Ask the owner only if the authorized preservation parent cannot be written, the
starting commit cannot be tagged locally, the current semantic model cannot be
loaded sufficiently to produce a trustworthy golden, or the observed element
set differs from the plan's 236-element premise. Preserve evidence before
asking. Ordinary documented baseline failures do not block the preservation
checkpoint.

## Gate and checkpoint

The gate passes when the dirty state is checksum-verifiably recoverable, the
starting commit has a local annotated tag, the semantic golden is reviewed and
validated, and all baseline results are recorded without lost user changes.
Commit only the report, golden, and narrowly required golden-validation support.
Stop after reporting the checkpoint hash and remaining status.
