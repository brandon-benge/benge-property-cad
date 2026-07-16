# Owner-authorized execution profile

This file records decisions made after
`BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md`. It is binding for prompts in
this directory and overrides conflicting sequencing or authority assumptions in
that plan.

## Scope and local-first terminal condition

- Work only in this Benge repository unless a prompt explicitly performs
  read-only inspection of frozen `python-cad-tools` distribution artifacts.
- Do not modify the `python-cad-tools` source checkout or installed
  site-packages.
- Complete and fully test all locally executable work before any push, remote
  rename, registry operation, release, CI run, or Pages deployment.
- The first execution sequence ends after Prompt 08 freezes a passing local
  compatibility report against the immutable local tooling candidate.
- Prompts 09-11 are separately authorized remote/registry stages. Each must ask
  its listed authority questions at that time and must not infer permission from
  completion of the local sequence.

## Git and repository operations

- Work on the current branch; do not create or switch branches unless the owner
  explicitly changes this profile.
- Create local, focused checkpoint commits and local annotated tags when the
  applicable prompt requires them.
- Never push commits or tags, rename a GitHub repository, change `origin`, create
  releases, run remote workflows, alter Pages settings, or deploy without the
  stage-specific authorization required by Prompts 09-11.
- Use the canonical future identities `benge-property-cad`, `Benge Property CAD`,
  `Benge Property`, and `BengeProperty` in active metadata and source as soon as
  the relevant local prompt migrates them. The local checkout directory may
  retain its legacy name through Prompt 08.
- Preserve unrelated user changes and never reset them.

## Tooling candidate boundary

- Prompt 02 may begin only after the tooling repository completes its local
  Prompt 08 and supplies an immutable `python-cad-tools==0.1.0rc1` wheel, sdist,
  checksums, provenance, and generic verification report.
- Consume only frozen distribution artifacts. Never use an editable install,
  source path, sibling import, VCS dependency, patched wheel, or copied tooling
  implementation.
- A failure in public tooling behavior is recorded as an upstream requirement.
  Do not implement a downstream framework fork or weaken the project contract.

## Preserved AI-workflow backups

- `.back_agents/` and `back_AGENTS.md` are not final project content. The owner
  has a separate backup in the tooling checkout and authorizes their eventual
  deletion here.
- Prompt 01 must nevertheless include their current bytes and deletion state in
  the verified Benge preservation bundle before any deletion.
- Prompt 06 creates active Benge-specific governance without treating the backup
  files as active policy. Prompt 07 deletes the backup-only paths after all
  relevant content has been reconciled and verified.

## Preservation location

Prompt 01 is authorized to create a timestamped bundle beneath:

```text
/Users/brandonbenge/Desktop/Houses Folder/Dreaming of Yard and House Updates/benge-property-cad-migration-preservation/
```

The bundle remains outside Git. It must include and verify the complete dirty
worktree, binary diffs, untracked inventory, metadata, and checksums required by
the migration plan.

## Platforms and locks

- Run every gate available on the current macOS arm64 host with Python 3.12 and
  3.13 where required.
- Never fabricate Ubuntu results, native lock contents, environment headers, or
  browser evidence. Prepare CI-native generation and verification for unavailable
  cells and list them as untested until an authorized remote run executes them.
- Do not claim the final migration complete until every advertised cell has real
  evidence as required by the plan.

## Checkpoint discipline

Every implementation prompt must:

1. read the complete migration plan, this profile, the current prompt, and the
   preceding checkpoint report when applicable;
2. record starting `HEAD` and `git status --short`;
3. preserve unrelated changes and never reset them;
4. modify only its stated scope;
5. run its full locally applicable gate and record commands/results in its
   report under `docs/migration/`;
6. stage only reviewed task-owned paths;
7. create one focused local checkpoint commit after the gate passes;
8. report the commit hash and remaining worktree status; and
9. stop without beginning the next prompt.

If a prompt cannot reach its gate, leave an evidence-backed failure report and
do not create a misleading passing checkpoint. A verifier prompt never repairs
failures in the same run.
