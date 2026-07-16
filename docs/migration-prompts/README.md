# Benge Property CAD migration prompt sequence

This directory divides `BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md` into
bounded prompts that can be executed and reviewed in separate Codex turns.
`00-execution-profile.md` records the owner's later local-first decisions and
overrides conflicting sequencing or authority assumptions in the original plan.

## How to execute a stage

Start a fresh Codex turn for each numbered prompt and say:

```text
Execute docs/migration-prompts/NN-<name>.md. Follow
docs/migration-prompts/00-execution-profile.md where it overrides
BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md. Do not begin the next prompt.
```

Run prompts in order. Each prompt owns one report, one gate, and at most one
focused checkpoint commit. A later prompt must not begin while its predecessor's
gate is failing.

## Sequence and decision points

| Prompt | Scope | Owner input required at start |
| --- | --- | --- |
| 01 | Preserve dirty checkout, baseline, tag, semantic golden | Only if preservation/golden assumptions fail |
| 02 | Verify immutable local tooling candidate | Exact tooling Prompt 08 bundle path |
| 03 | Canonical identity, installed dependency, native locks | Only for public-contract or ID-preservation conflict |
| 04 | Model imports and neutral annotations | Only for missing upstream primitive or design contradiction |
| 05 | Complete Benge tests, artifacts, site, browser | Approval before changing reviewed design golden |
| 06 | Project governance, CI, Pages definitions | Only for governance-policy conflict |
| 07 | Delete vendored/legacy/backup paths | Approval for any deletion outside the explicit disposition map |
| 08 | Independent local compatibility verification | Only if local candidate access/platform scope changes |
| 09 | GitHub/local canonical rename | Push, rename, settings, credentials, tooling canonical identity |
| 10 | Published prerelease and remote CI | Registry/provenance access, CI authority, native lock generation |
| 11 | Stable package and live Pages | Stable hashes, publication/license status, push/CI/Pages authority |

## Local-first stopping point

The currently authorized sequence is Prompts 01-08. It produces a clean,
minimal Benge repository plus immutable local compatibility evidence without
remote mutation. Prompt 02 intentionally waits for the sibling tooling migration
to finish its own Prompt 08 local release candidate.

Prompts 09-11 are prepared now so their questions are asked at the correct time.
They are not pre-authorized by this file and must not run merely because Prompt
08 passes.

## Final outcome

Only Prompt 11 can satisfy the original plan's complete terminal condition. A
passing Prompt 08 is a meaningful local milestone, not a claim that registry,
cross-platform CI, repository rename, or live Pages verification has occurred.
