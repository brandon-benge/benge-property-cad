# Prompt 06: rewrite governance, CI, and Pages workflows

## Objective

Create narrow project-owned agent governance and complete local-first CI/Pages
definitions that use only installed tooling and immutable dependency evidence.

## Work

1. Read the plan, profile, this prompt, prior reports, current backup agent
   content, and current workflow/config files. Record starting state in
   `docs/migration/06-governance-ci-report.md`.
2. Create the exact active `AGENTS.md`, `.agents/agents/**`, and
   `.agents/skills/**` Benge roles from Sections 7-8 with narrow project/tooling
   authority boundaries.
3. Repair `.claude`, `.codex`, `.opencode`, and `CLAUDE.md` using the exact
   relative link targets in Section 8. Test raw targets, resolved types, and
   repository containment.
4. Reconcile useful user content from `.back_agents/` and `back_AGENTS.md` into
   the new project-specific policy without copying cross-boundary tooling
   authority. Leave backups untouched for Prompt 07 deletion.
5. Replace the old build workflow with `.github/workflows/ci.yml` implementing
   the stable job IDs, least privileges, pinned actions, native lock selection,
   immutable candidate evidence, complete test/build/site/browser gates, report,
   and no-skip aggregate in Section 14.1.
6. Rewrite `.github/workflows/pages.yml` as the thin same-commit, certified-wheel,
   package-command deployment flow in Section 14.2. It must not use downstream
   Node or viewer source.
7. Ensure workflows distinguish currently generated local macOS locks from
   pending CI-native Ubuntu locks and never treat placeholder/missing locks as
   passing evidence.
8. Add static workflow-policy, action-pin, permissions, symlink, active-name,
   dependency-boundary, and target-tree tests runnable locally without contacting
   GitHub.
9. Update README and project governance documentation with clean installed
   commands, conceptual limitations, exact candidate upgrade procedure, and the
   local-first/remote-deferred status.

## Constraints

- Do not run or push workflows, alter remote settings, or deploy Pages.
- Do not delete backup agent paths in this prompt.
- Do not grant a project agent authority to edit package source/site-packages.
- Do not fabricate action results, Ubuntu locks, attestations, or Pages evidence.

## Clarification and stop gates

No remote authority is needed for this prompt. Ask the owner only if preserving
some backup agent behavior would conflict with the strict separation-of-duties
contract, or if a chosen third-party action cannot be pinned and verified
without network access. Record unavailable remote-only gates as pending rather
than weakening workflow policy.

## Gate and checkpoint

All active governance links resolve, local workflow syntax/policy checks pass,
CI/Pages definitions implement the required interfaces, README commands match
the installed CLI, and no remote action occurred. Create the focused checkpoint
and stop.
