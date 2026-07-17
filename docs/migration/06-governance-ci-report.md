# Prompt 06: Governance, CI, and Pages Report

## Starting Git State

- **Date**: 2026-07-16
- **Branch**: `main`
- **HEAD**: `6c5e020 feat(migration): rebuild Benge project test suite (Prompt 05)`
- **Working tree**: dirty (deleted `.agents/`, `AGENTS.md`, `.opencode/`, `opencode.jsonc`; untracked backup agent files and migration plans)

### Working tree changes
- Deleted: `.agents/` (all agent/skill definitions), `.opencode/` (agents/skills/commands/tools), `AGENTS.md`, `opencode.jsonc`
- Untracked: `.back_agents/`, `.back_opencode/`, `back_AGENTS.md`, `back_opencode.jsonc` (user backups), plus migration plan files

### Current symlinks (all broken)
- `.claude/agents -> ../.agents/agents` (target deleted)
- `.claude/skills -> ../.agents/skills` (target deleted)
- `.codex/agents -> ../.agents/agents` (target deleted)
- `.codex/skills -> ../.agents/skills` (target deleted)
- `CLAUDE.md -> AGENTS.md` (target deleted)
- `.opencode/` does not exist

### Backup content available
| Path | Content |
|------|---------|
| `.back_agents/` | Full agent/skill trees (python-cad-architect, general-contractor, save) |
| `back_AGENTS.md` | Old root AGENTS.md with cross-boundary python-cad-architect role |
| `back_opencode.jsonc` | Full opencode config with general-contractor/python-cad-architect/save agents |

### Current workflow files
| File | Status |
|------|--------|
| `.github/workflows/build-design.yml` | Old build workflow with legacy lock paths, ruff/mypy/pytest, no matrix, uses ubuntu-latest |
| `.github/workflows/pages.yml` | Old Pages workflow with Node/viewer build, uses viewer/ source |

### Current lock files
| File | Status |
|------|--------|
| `requirements/dev-macos-arm64-py312.lock` | Real macOS lock |
| `requirements/dev-macos-arm64-py313.lock` | Real macOS lock |
| `requirements/dev-ubuntu-x86_64-py312.lock` | Placeholder (PENDING) |
| `requirements/dev-ubuntu-x86_64-py313.lock` | Placeholder (PENDING) |
| `requirements/runtime-macos-arm64-py312.lock` | Real macOS lock |
| `requirements/runtime-macos-arm64-py313.lock` | Real macOS lock |
| `requirements/runtime-ubuntu-x86_64-py312.lock` | Placeholder (PENDING) |
| `requirements/runtime-ubuntu-x86_64-py313.lock` | Placeholder (PENDING) |

### Current test state (75 collected)
- `test_config_contract.py`: 8 tests
- `test_model_contract.py`: 13 tests
- `test_drawing_annotations.py`: 13 tests
- `test_build_end_to_end.py`: 25 tests
- `test_viewer_e2e.py`: 16 tests

### Current lint state
- Ruff: 66 E501 (line too long) errors in `model.py` — pre-existing
- Ruff format: 2 files would be reformatted (tests/test_model_contract.py, tests/test_viewer_e2e.py)
- Mypy: clean (3 source files)

### Requirements/locks currently flat in `requirements/`, need `requirements/locks/` per Section 8.

## Target State (Section 8)

- `.agents/agents/{benge-design-maintainer,benge-project-operations,benge-artifact-reviewer,cad-compatibility-verifier,save}.md`
- `.agents/skills/<same-id>/{SKILL.md,agents/openai.yaml}`
- `.claude/{agents,skills} -> ../.agents/{agents,skills}`
- `.codex/{agents,skills} -> ../.agents/{agents,skills}`
- `.opencode/{agents,skills} -> ../.agents/{agents,skills}`
- `.opencode/{commands,tools}/`
- `CLAUDE.md -> AGENTS.md`
- `opencode.jsonc` — Benge-specific project agent configuration
- `AGENTS.md` — narrow project roles (Section 7)
- `.github/workflows/ci.yml` — 9-job matrix with Section 14.1 interfaces
- `.github/workflows/pages.yml` — thin package-deployment flow (Section 14.2)
- `requirements/locks/` — four named native locks per Section 8 naming
