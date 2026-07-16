# Prompt 07: remove vendored and legacy content

## Objective

After installed replacements pass, reduce the active repository to the target
project tree and remove every prohibited copied framework/viewer/backup path.

## Work

1. Read the plan, profile, this prompt, prior reports, and preservation-bundle
   verification. Record starting state in
   `docs/migration/07-legacy-removal-report.md`.
2. Reconfirm the exact frozen candidate passes parity with `.tools`, root
   launchers, and downstream viewer source temporarily present.
3. Remove `.tools/`, root `build.py`, `start.sh`, `viewer/`, `backup/`, obsolete
   updater/installer docs, stale copied workflows, caches, generated artifacts,
   and every other prohibited path from Section 9.
4. Delete `.back_agents/` and `back_AGENTS.md` as owner-authorized backup-only
   content after verifying their archived hashes and confirming active policy
   contains the intended reconciled behavior.
5. Update `.gitignore`; retain only `generated/.gitkeep` and ensure clean/build
   preserve or recreate its zero-byte tracked state.
6. Run the complete boundary scan from Section 13, allowlisting only the two
   migration plan files and migration reports/prompts as historical control
   content.
7. Prove there are no broken/outside symlinks, private imports, path/editable/VCS
   dependencies, copied tooling/viewer implementation, tracked generated output,
   legacy active names, Node dependencies, or sibling checkout reliance.
8. Run the entire local static, test, build, verify, determinism, rollback, site,
   HTTP, and browser matrix with prohibited paths physically absent.
9. Record a complete before/after disposition map and final active-tree listing.

## Constraints

- Do not delete anything until its installed replacement and external
  preservation evidence are verified.
- Preserve Git history, local tags, migration plans, reports, and semantic golden.
- Do not modify tooling source, remote state, or registry state.
- Do not retain legacy implementation merely for convenience after parity passes.

## Clarification and stop gates

Ask the owner before deleting any path not explicitly covered by Sections 8-9
or this profile. If full gates fail only after a legacy path disappears, diagnose
the hidden coupling and stop; do not restore it as an undocumented dependency.
If the candidate lacks the replacement capability, request a new upstream
candidate.

## Gate and checkpoint

The exact target tree is present, backup-only agent paths are deleted, every
boundary/link/name check passes, and the complete local suite passes without a
sibling tooling checkout, vendored source, root launcher, downstream viewer, or
Node. Create the focused checkpoint and stop.
