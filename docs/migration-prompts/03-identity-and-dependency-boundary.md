# Prompt 03: project identity and installed dependency boundary

## Objective

Migrate active project identity and configuration to the canonical Benge values
while preserving every stable design identifier and consuming only the frozen
installed tooling candidate.

## Work

1. Read the plan, execution profile, this prompt, and reports 01-02. Record
   starting Git state in `docs/migration/03-identity-boundary-report.md`.
2. Update `pyproject.toml` to `benge-property-cad`, the strict
   `[tool.python-cad]` schema, exact `python-cad-tools==0.1.0rc1` migration pin,
   complete dev dependencies, Ruff/mypy/pytest configuration, and no package
   discovery for the flat project modules.
3. Remove `.tools`/`PYTHONPATH`/mypy path injection and all editable, sibling,
   VCS, private-index, or relative-path dependency behavior from active config.
4. Resolve native macOS arm64 Python 3.12 and 3.13 hashed locks through the exact
   verified candidate wheel using Section 10. Mechanically prove the locks
   contain only names, versions, markers, and hashes—not the candidate path.
5. Add CI-native definitions/placeholders for Ubuntu locks, but do not fabricate
   their contents. Leave unavailable lock cells explicitly pending in the report.
6. Migrate active config/model identity to model ID `benge.property`, display
   `Benge Property`, artifact stem `BengeProperty`, source module `model`, tag
   `benge-property`, and project title `Benge Property CAD`.
7. Replace fixture/snapshot authority metadata with real project authority and
   build-provided Git revision. Preserve the exact golden `complex.*` element
   IDs, `material.complex.*` IDs, and required derived IFC identities.
8. Update focused in-memory tests for the intentional old-to-new model/spatial
   mapping and unchanged stable-ID sets. Retain controlled legacy launchers only
   where still needed for later parity; do not delete them yet.
9. Update active README/workflow/agent wording only as needed for this identity
   boundary, while leaving the full governance rewrite to Prompt 06.

## Constraints

- Do not rewrite the annotation implementation yet.
- Do not delete `.tools`, build/start launchers, viewer source, backup history,
  or backup agent files until their replacement gates pass.
- Do not create fake Ubuntu locks or claim cross-platform success.
- Do not change any `complex.*` element ID to make naming look cleaner.

## Clarification and stop gates

Ask the owner if the candidate's public API cannot express the required model
identity, if exact stable-ID preservation fails, or if native lock resolution
cannot bind to the verified wheel hash. Those are contract decisions, not
reasons to add a local workaround. Ubuntu lock generation remains deferred
without asking until Prompt 09 authorizes remote CI.

## Gate and checkpoint

The installed-candidate model loads without source-path tricks; canonical model
identity is exact; the golden stable-ID sets are unchanged; local native locks
are reproducible and path-free; and focused lint/type/tests pass. Create the
focused checkpoint and stop.
