# Prompt 09: coordinate canonical GitHub and local repository identity

## Objective

After local verification is frozen, establish the canonical
`benge-property-cad` remote and local checkout identity without changing the
verified design content.

## Required authority questions

At the start of this stage, ask the owner to confirm all of the following:

1. May Codex push the verified local commits and annotated tags?
2. May Codex rename the GitHub repository to `benge-property-cad`, update
   `origin`, and verify the old URL redirect?
3. May Codex update repository/Pages settings and protected environments needed
   by the already-reviewed workflows?
4. Is an authenticated GitHub connector or `gh` CLI available with that scope?
5. Has the tooling repository been renamed to `python-cad-tools`, and what exact
   canonical URL/commit/tag must downstream evidence reference?

Do not proceed on inferred or partial authority. A no/absent credential leaves
this prompt externally blocked without invalidating Prompt 08's local evidence.

## Work

1. Read the plan, profile, this prompt, Prompt 08 report, and exact remote state.
2. Reverify clean source/tag identities before any remote mutation.
3. Push only reviewed checkpoint commits/tags authorized by the owner.
4. Rename the GitHub repository, update and verify `origin`, test the old remote
   redirect, and record repository settings/Pages base identity.
5. Stop active processes, then rename or freshly clone the local directory to
   `benge-property-cad` from its parent. Prove no active configuration embeds the
   old absolute path.
6. Re-run local boundary, identity, clean-install, test, build, site, and browser
   smoke gates from the renamed path.
7. Record exact commands/results in
   `docs/migration/09-canonical-identity-report.md` and checkpoint any necessary
   URL/config corrections locally before pushing them with explicit authority.

## Constraints

- Do not publish tooling artifacts or alter the tooling repository.
- Do not begin registry verification or Pages deployment.
- Never expose credentials in source, logs, reports, or tool output.

## Gate and checkpoint

The canonical remote/local identity exists, redirects and settings are verified,
the same source passes from the renamed path, and evidence records exact remote
and commit identities. Create/push only the authorized focused checkpoint and
stop.
