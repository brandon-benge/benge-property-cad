# Prompt 10: verify the published tooling prerelease

## Objective

Replace the local candidate source with registry-resolved
`python-cad-tools==0.1.0rc1` and prove the complete Benge matrix against the
published immutable artifacts.

## Required authority questions

At the start of this stage, ask the owner:

1. Which authorized Python registry/index hosts the prerelease, and is access
   configured through standard pip credentials outside source?
2. Has the exact certified wheel/sdist been published without rebuilding, and
   what provenance/attestation proves its hashes?
3. May Codex run the repository's remote CI workflows and retrieve their
   artifacts/logs?
4. May Codex regenerate and commit all four native locks using their real native
   CI cells?

Stop if the release is absent, licensing/publication authority remains
unresolved, hashes differ, credentials are unavailable, or any platform cell
would need fabricated evidence.

## Work

1. Read the plan, profile, this prompt, local candidate report, canonical-identity
   report, registry provenance, and current workflow definitions.
2. Resolve/download the prerelease with caches and local fallbacks disabled;
   require wheel/sdist hashes to match the frozen certified handoff.
3. Regenerate each native lock only in its named Python/OS/architecture cell.
   Scan locks for paths, URLs, editable/VCS sources, extra tool hashes, and
   incorrect candidate hashes.
4. Run the complete clean project static/test/build/verify/determinism/site/HTTP/
   browser matrix locally and through every authorized CI cell.
5. Produce the same-commit prerelease compatibility report and archive job,
   lock, package, browser, and artifact evidence.
6. Report package failures upstream; never patch the installed distribution or
   reuse a failed immutable prerelease version.

## Constraints

- Do not deploy Pages or change to a stable pin.
- Do not add registry URLs/tokens to source or logs.
- Do not weaken or skip required cells.

## Gate and checkpoint

All native locks and complete local/CI cells pass against registry artifacts
whose hashes exactly match the frozen candidate. Commit/push the reviewed lock
and compatibility evidence only with explicit authority, then stop.
