# Prompt 11: stable pin, final registry matrix, and Pages deployment

## Objective

Verify the frozen stable tooling bytes before and after publication, deploy the
same verified Benge build, and produce the final compatibility report.

## Required authority questions

At the start of this stage, ask the owner to confirm:

1. What exact frozen `python-cad-tools==0.1.0` wheel/sdist filenames, hashes,
   source revision, and tooling T8 report are authoritative?
2. Has the license/publication decision been resolved, and may the tooling owner
   publish those exact bytes without rebuilding?
3. May Codex update and push the stable project pin/locks and run all protected
   CI jobs?
4. May Codex enable/configure GitHub Pages, use the protected Pages environment,
   deploy, and run automated postdeployment HTTP/browser checks?
5. What canonical live Pages URL must be verified?

Missing authority marks this stage `EXTERNALLY_BLOCKED` after all independent
local/staged gates; it never becomes a request for the user to test manually.

## Work

1. Read the plan, profile, this prompt, all prior compatibility/provenance
   reports, and exact stable handoff.
2. Stage `python-cad-tools==0.1.0` and native locks, then run the complete clean
   matrix against the local frozen stable bytes through Section 10's
   checksum-verified wheel-only procedure before publication.
3. Return the passing prepublication report to the tooling owner. Require the
   published registry wheel/sdist hashes to be byte-identical to that handoff.
4. Resolve stable from the registry with no cache/local fallback, regenerate and
   verify all four native locks, and rerun the full local/CI matrix.
5. Verify canonical repository identity, active-name scans, required workflow
   jobs, same-commit/package/lock evidence, and the no-skip aggregate.
6. Build and verify artifacts, prepare the non-root site, deploy only the
   certified site directory, and automatically poll/test the live Pages URL.
7. Run postdeployment HTTP and Playwright checks for exact
   `design_build_hash == stable_artifact_set_hash`, GLB/download hashes, clean
   console/network state, and known element selection.
8. Generate and archive the final Section 15 compatibility report with every
   revision, distribution artifact, schema, hash, command, platform, browser,
   and Pages result.
9. If nominal `0.1.0` fails, follow Section 17 incident policy; do not overwrite
   or silently retain known-bad artifacts.

## Constraints

- Never rebuild published stable bytes, patch site-packages, expose credentials,
  skip required cells, or hand verification to the user.
- Do not call the migration complete while registry, CI, or supported Pages
  evidence is missing.

## Gate and checkpoint

The exact stable package passes before and after publication on all claimed
cells; canonical CI and Pages deploy the same certified commit/package/locks;
the live automated browser gate passes; and the final machine-readable report is
archived. Commit/push final evidence only with explicit authority and report the
terminal status as complete or `EXTERNALLY_BLOCKED`.
