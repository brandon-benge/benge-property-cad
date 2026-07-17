# Prompt 02 — Candidate Intake Report

## Starting State

| Item | Value |
|------|-------|
| HEAD | `9e660a9 chore(migration): preserve Benge baseline` |
| Worktree | Dirty (D .agents/*, D AGENTS.md, ?? .back_agents/, ?? BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md, ?? REPO_SPLIT_PROMPT_PLAN.md, ?? back_AGENTS.md) |
| Remote | `origin https://github.com/brandon-benge/benge_freecad_project.git` |
| Bundles checked | None prior |

## Tooling Prompt 08 Report

- Path: `freecad_macro_project_template/docs/migration/08-local-rc-report.md`
- Source commit: `9e6b67a069cbbded512d98a710e8a8f9a0e74f5f` (clean)
- Distribution: `python-cad-tools==0.1.0rc1`
- Tag: `v0.1.0rc1`
- All gates PASS (lint, mypy, 102 unit tests, packaging, viewer, clean install 3.12/3.13, sdist rebuild, content audit)

## Candidate Bundle Verification

| Artifact | Filename | Size (B) | SHA-256 | Status |
|----------|----------|----------|---------|--------|
| Bundle | `python-cad-tools-0.1.0rc1-candidate/` | — | `2c93d0a42ba256056216d2469ae33763cfbfc3cb81f545534937381c63056a79` | Matches report |
| Wheel | `python_cad_tools-0.1.0rc1-py3-none-any.whl` | 1,030,163 | `fbc30d4adbe0be42e1315a90a6e0f93fc60d2037976523b9919fa487e9b23b49` | Matches SHA256SUMS, provenance, report |
| Sdist | `python_cad_tools-0.1.0rc1.tar.gz` | 931,088 | `c6b527b9321daf897689c503f229adf51b2fd5ffad3abf321e5978fa73034fb0` | Matches SHA256SUMS, provenance, report |
| SHA256SUMS | `SHA256SUMS` | 208 | `040f5158442945bad57614032f211f2a8b264afeac2831c85f4bf96eae6e714d` | Verified |
| Provenance | `provenance.json` | 633 | `75f2dd23c572ff9fd31dbc7e376521761ce824625c20364d1a0095fd448117f1` | Verified |

## Wheel Metadata

- Name: `python-cad-tools`
- Version: `0.1.0rc1`
- Requires-Python: `>=3.12,<3.14`
- Dependencies: `build123d>=0.11.1,<0.12`, `cadquery-ocp-novtk>=7.9.3.1.1,<7.10`, `ifcopenshell>=0.8.5,<0.9`, `trimesh>=4.12,<5`, `numpy>=2.3,<3`, `ezdxf>=1.4,<2`, `reportlab>=4.4,<5`, `pypdf>=6,<7`
- Extras: `dev` (build, twine, pytest, pytest-cov, ruff, mypy)
- Entry point: `python-cad = python_cad_tools.cli:main`
- `py.typed`: Present
- `build-info.json`: source_commit `32ff6d8`, viewer_shell_sha256 `5be46f14`
- Generator: setuptools 83.0.0, wheel 1.0, py3-none-any

## Wheel Contents

- 20 Python modules in `python_cad_tools/`
- 2 subpackages: `drawings/`, `exporters/` (with `drawings/` sub-subpackage)
- 10 JSON schemas in `schemas/`
- 7 scaffold templates in `templates/project/` (includes `.gitignore`)
- 175 viewer static files in `_viewer_static/`
- `py.typed` marker
- Forbidden content check: PASSED (no `.back_agents`, `back_AGENTS.md`, `.tools`, `generated/`, `node_modules/`)

## Python 3.13 Verification (macOS arm64, 3.13.6)

| Gate | Result | Detail |
|------|--------|--------|
| `pip check` | PASSED | No broken requirements |
| Public imports | PASSED | units, build, context, elements, drawings, geometry, artifacts, exceptions |
| CLI `--version` | PASSED | `python-cad 0.1.0rc1` |
| CLI `--help` | PASSED | 7 subcommands listed |
| `python-cad init` | PASSED | 9 files created |
| `python-cad build` | PASSED | 22 artifacts, `stable_artifact_set_hash: 54f6176bab81424a764a91a03ed15ea558e9addb323f789bd5468d3d3f2ba82c` |
| `python-cad verify` | PASSED | Same hash, 22 artifacts verified |
| `python-cad prepare-site` | PASSED | 198 files, `design_build_hash` matches |
| `python-cad serve` (health) | PASSED | `{"status":"ok","tool_version":"0.1.0rc1"}` |
| Browser smoke test (Playwright) | PASSED | Title: "Python CAD Tools Viewer", 0 errors, hash match |

## Python 3.12 Verification (macOS arm64, 3.12.9)

| Gate | Result | Detail |
|------|--------|--------|
| `pip check` | PASSED | No broken requirements |
| Public imports | PASSED | Same API surface as 3.13 |
| CLI `--version` | PASSED | `python-cad 0.1.0rc1` |
| `python-cad init` | PASSED | 9 files created |
| `python-cad build` | PASSED | 22 artifacts, identical `stable_artifact_set_hash: 54f6176bab81424a764a91a03ed15ea558e9addb323f789bd5468d3d3f2ba82c` |
| `python-cad verify` | PASSED | Same hash |
| `python-cad prepare-site` | PASSED | 198 files, identical hash |

## Sdist-to-Wheel Evidence

| Check | Result |
|-------|--------|
| File list comparison | IDENTICAL (235 files each) |
| `build-info.json` comparison | IDENTICAL (same source_commit `32ff6d8`, same viewer_shell `5be46f14`) |
| Note | Rebuilt wheel has different byte hash due to RECORD timestamps; content is functionally identical |

## Candidate Reference (Machine-Readable)

Stored in `docs/migration/candidate-reference.json`.

## Gate Verdict

**PASSED** — The immutable `python-cad-tools==0.1.0rc1` handoff is verified on both locally available Python versions (3.12 and 3.13, macOS arm64) with no tooling checkout on `sys.path`.

## Remaining Worktree Status (unchanged)

```
 D .agents/.DS_Store
 D .agents/README.md
 D .agents/agents/general-contractor.md
 D .agents/agents/python-cad-architect.md
 D .agents/agents/save.md
 D .agents/skills/general-contractor/SKILL.md
 D .agents/skills/general-contractor/agents/openai.yaml
 D .agents/skills/python-cad-architect/SKILL.md
 D .agents/skills/python-cad-architect/agents/openai.yaml
 D .agents/skills/save/SKILL.md
 D .agents/skills/save/agents/openai.yaml
 D AGENTS.md
?? .back_agents/
?? BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md
?? REPO_SPLIT_PROMPT_PLAN.md
?? back_AGENTS.md
```
