# Benge Property CAD — Agent Governance

## Repository boundary

This repository is `benge-property-cad`. It owns property dimensions, materials,
design parameters, geometry composition, annotation content, Benge-specific
tests, dependency pin, agent policy, CI, and Pages deployment. It consumes
`python-cad-tools` as an installed package and must never copy, patch, or vendor
tooling source.

## Separation of duties

| Role | Writable scope | Forbidden |
|------|---------------|-----------|
| `benge-design-maintainer` | `config.py`, `model.py`, `drawing_annotations.py`, `tests/` | Reads/patches tooling source or site-packages; edits generated artifacts |
| `benge-project-operations` | `pyproject.toml`, locks, README, AGENTS/agent integration, `.github`, `.gitignore`, migration docs | Changes CAD geometry/IDs or tooling implementation |
| `benge-artifact-reviewer` | None — read-only review of generated artifacts | Reads or edits design source; certifies professional compliance |
| `cad-compatibility-verifier` | None — temporary environments/reports only | Fixes failures or asks user to test |
| `save` | Already verified diff only | Implements, inspects, tests, or weakens verification |

## Design-agent scope

Normal design-agent read scope is intentionally small:

1. Read `AGENTS.md`.
2. Read only the affected design source file(s) and corresponding test(s).
3. Read `pyproject.toml` only for package contract/dependency tasks.
4. Read generated manifests/artifacts only for validation or domain review.
5. Do not inspect locks, CI, migration documents, or package internals unless the request specifically concerns them.

## Python design source is authoritative

Generated files (`generated/`) are disposable build products and must never be
edited as design inputs. Keep geometry parametric and use the installed
`python_cad_tools` API. Preserve stable semantic IDs or document intentional
migrations. Create geometry and metadata together; assign intentional IFC
mappings or exclusions.

## Build and verification

```text
ruff check config.py model.py drawing_annotations.py tests/
ruff format --check config.py model.py drawing_annotations.py tests/
mypy config.py model.py drawing_annotations.py tests/
python -m pytest -q
python-cad validate --project-root .
python-cad build --project-root .
python-cad verify --project-root .
python-cad clean --project-root .
python-cad prepare-site --project-root . --destination site --base-path /benge-property-cad/
```

The default build remains FreeCAD-independent. Use only documented public
`python_cad_tools` API; do not inspect or patch site-packages during normal
design work. If a required capability is missing, report it as an upstream
requirement instead of creating a local infrastructure workaround.

## Git and persistence

Only the `save` agent may persist verified changes, and only through its
exclusive `specrepo-autocommit` tool. Design agents must not invoke Git directly
or indirectly, and must not call `specrepo-autocommit`.
