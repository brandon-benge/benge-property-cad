# Prompt 08: freeze local Benge compatibility evidence

## Objective

Independently verify the minimal Benge repository against the exact immutable
local tooling candidate and freeze a machine-readable local compatibility report.

## Work

1. Begin from the checkpointed current branch and require a clean worktree. Read
   the plan, profile, this prompt, all prior reports, and candidate provenance.
   Record source/tag/artifact/lock/tool identities.
2. Act as `cad-compatibility-verifier`: do not repair source during this run. If
   a defect is found, report it, return it to the owning earlier prompt for a new
   focused commit, and restart this verification from the beginning.
3. Create fresh project-only archives/checkouts in paths containing spaces with
   no sibling tooling source on `sys.path`.
4. Install exact path-free hashed locks and the certified candidate non-editably
   on local Python 3.12 and 3.13 with caches disabled. Verify import provenance,
   package version/build information, and `pip check`.
5. Run all Sections 12-14 locally applicable static, model, annotation, CLI,
   full-format, manifest/hash, parser, determinism, rollback/recovery, clean,
   site, HTTP, and Playwright gates.
6. Perform the disposable one-dimension-change simulation and prove ordinary
   design work touches only project-owned design/test files.
7. Generate the Section 15 compatibility JSON automatically with exact commands,
   exit codes, durations, hashes, schemas, stable IDs, annotations, browser
   evidence, and explicit unsupported/pending remote platform features.
8. Store reports outside source where appropriate and commit only the stable
   machine-readable/reference evidence that does not falsify source cleanliness.
9. Create a local annotated Benge migration-candidate tag only after all locally
   executable gates pass. Do not push it.

## Constraints

- Do not fix failures while acting as verifier.
- Do not publish, push, rename, contact a registry, run remote CI, or deploy.
- Do not claim Ubuntu, GitHub, registry, or live Pages gates passed locally.
- Do not ask the user to inspect CAD output or browser behavior manually.

## Clarification and stop gates

Ask the owner only if a clean verifier environment cannot access the already
authorized local candidate bundle, or if completing the local matrix requires a
new platform claim. Candidate/project failures are routed to their owning prompt
with evidence rather than resolved by clarification.

## Gate and checkpoint

The gate passes when the exact candidate and clean Benge source produce a fully
passing local compatibility report on both native Python versions, with only
truthfully enumerated remote/platform gates pending. Create the focused report
checkpoint and local annotated tag, then stop. Do not begin Prompt 09.
