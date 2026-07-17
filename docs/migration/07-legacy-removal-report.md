# Prompt 07: Legacy Content Removal Report

## Result: PASS

**Date**: 2026-07-16
**Starting HEAD**: `c90357a feat(migration): rewrite governance, CI, and Pages workflows (Prompt 06)`
**Preservation bundle**: `../benge-property-cad-migration-preservation/20260716T132948-0400-benge-preservation/` (verified: all SHA-256 matching)

## Starting State

### Current tree before removal (35 top-level entries)

| Path | Status | Disposition |
|------|--------|-------------|
| `.tools/` | Vendored tooling source | DELETE |
| `build.py` | Root build launcher | DELETE |
| `start.sh` | Root start launcher | DELETE |
| `viewer/` | Downstream viewer (Vite/TypeScript/Node) | DELETE |
| `backup/` | Legacy FreeCAD macros/tools | DELETE |
| `.back_agents/` | Owner backup of agent configs | DELETE |
| `back_AGENTS.md` | Owner backup of old AGENTS.md | DELETE |
| `back_opencode.jsonc` | Owner backup of opencode config | DELETE |
| `.back_opencode/` | Owner backup of opencode directory | DELETE |
| `__pycache__/` | Python cache | DELETE |
| `.mypy_cache/` | Mypy type cache | DELETE |
| `.pytest_cache/` | Pytest cache | DELETE |
| `.ruff_cache/` | Ruff cache | DELETE |
| `generated/*` (except .gitkeep) | Build output | CLEAN |

### Legacy file hashes (archived in preservation bundle)

- `back_AGENTS.md`: `fbc3dfd7486c80f0a7603d414c39cf77d3dddd0835e6f4e1fdaae6211c6b0e8f`
- `back_opencode.jsonc`: `fece8bf147ed7df2e9209858d2db8b86369cfa67734e767233a0be78392a8815`

### Pre-removal parity check (with legacy files present)

| Check | Result | Detail |
|-------|--------|--------|
| Ruff check | Pre-existing 66 E501 errors | model.py line-length only |
| Ruff format | 7 files would reformat | Pre-existing |
| Mypy | 38 errors | Pre-existing in tests/ with None-flow |
| pytest (unit) | 35/35 pass | config/model_contract/drawing |
| pytest (build) | 25/25 pass | test_build_end_to_end |
| pytest (non-e2e) | 80/80 pass | All except viewer_e2e |
| `python-cad validate` | OK | `design_semantic_hash: 1b378a3...` |
| `python-cad build` | OK | 23 artifacts, `stable_hash: f33c8d9...` |
| `python-cad verify` | OK | Same stable hash |
| `python-cad prepare-site` | OK | 198 files |

## Actions Taken

### 1. Git removal of tracked paths

```text
git rm -r .tools/ build.py start.sh viewer/ backup/ .back_agents/
  back_AGENTS.md back_opencode.jsonc .back_opencode/
```

Removed 130+ tracked files across the prohibited paths.

### 2. Working tree deletion

Removed same paths from disk (if not already removed by `git rm -r`).

### 3. Cache cleanup

Removed `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`.

### 4. Generated output cleanup

Cleaned all build artifacts from `generated/` (`.gitkeep` preserved).

### 5. `.gitignore` update

Added patterns: `.tools/`, `viewer/`, `backup/`, `.back_agents/`, `.back_opencode/`,
`back_AGENTS.md`, `back_opencode.jsonc`, `build.py`, `start.sh`, `site/`,
`.opencode/node_modules/`

## Boundary Scan Results (Section 13)

### Prohibited paths
- `.tools/` — absent
- `build.py` — absent
- `start.sh` — absent
- `viewer/` — absent
- `backup/` — absent
- `.back_agents/` — absent
- `back_AGENTS.md` — absent
- `back_opencode.jsonc` — absent
- `.back_opencode/` — absent

### Symlinks (all valid)
| Link | Target | Status |
|------|--------|--------|
| `.claude/agents` | `../.agents/agents` | OK |
| `.claude/skills` | `../.agents/skills` | OK |
| `.codex/agents` | `../.agents/agents` | OK |
| `.codex/skills` | `../.agents/skills` | OK |
| `.opencode/agents` | `../.agents/agents` | OK |
| `.opencode/skills` | `../.agents/skills` | OK |
| `CLAUDE.md` | `AGENTS.md` | OK |

### Legacy name scan (migration docs allowlisted)
All 8 legacy names absent from active source/config/tests/CI.

### Other boundary checks
- No `.tools` Python path in active source
- No editable/path/VCS dependency in `pyproject.toml`
- No private exporter imports
- No tracked generated artifacts except `generated/.gitkeep`
- No framework/viewer source copied in project
- No `node_modules` or Node dependencies
- No sibling checkout reliance
- Zero untracked non-ignored files

## Post-Removal Full Suite Results

| Check | Result | Detail |
|-------|--------|--------|
| Ruff check | 66 E501 errors | Unchanged from pre-removal |
| Ruff format | 7 files | Unchanged from pre-removal |
| Mypy | 38 errors | Unchanged from pre-removal |
| pytest (non-e2e) | 80/80 pass | Same as pre-removal |
| `python-cad validate` | OK | Same hash |
| `python-cad build` | OK | 23 artifacts, `f33c8d9...` (identical) |
| `python-cad verify` | OK | `stable_artifact_set_hash` unchanged |
| `python-cad prepare-site` | OK | 198 files, same hash |

All results are byte-for-byte identical to the pre-removal run.

## Final Active Tree

```text
./
├── .agents/
│   ├── agents/{benge-design-maintainer,benge-project-operations,
│   │          benge-artifact-reviewer,cad-compatibility-verifier,save}.md
│   └── skills/<same-id>/{SKILL.md,agents/openai.yaml}
├── .claude/{agents,skills} -> ../.agents/{agents,skills}
├── .codex/{agents,skills} -> ../.agents/{agents,skills}
├── .opencode/{agents,skills} -> ../.agents/{agents,skills}
├── .opencode/{commands,tools}/
├── .github/workflows/{ci.yml,pages.yml}
├── .gitignore
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md
├── opencode.jsonc
├── README.md
├── pyproject.toml
├── requirements/{locks/*.lock, dev-*-*-*.lock, runtime-*-*-*.lock}
├── config.py
├── model.py
├── drawing_annotations.py
├── tests/{conftest.py, fixtures/, test_*.py}
├── generated/.gitkeep
├── BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md
├── REPO_SPLIT_PROMPT_PLAN.md
└── docs/migration/{*-report.md, candidate-reference.json}
    └── docs/migration-prompts/*.md
```

## Checkpoint Gate Status

- [x] Preservation bundle verified (SHA-256 all OK, reconstruction PASS)
- [x] Pre-removal parity confirmed (identical build/verify/site results)
- [x] `.tools/` removed
- [x] `build.py` removed
- [x] `start.sh` removed
- [x] `viewer/` removed
- [x] `backup/` removed
- [x] `.back_agents/` and `back_AGENTS.md` removed (hashes archived)
- [x] `back_opencode.jsonc` and `.back_opencode/` removed
- [x] Caches cleaned; `.gitignore` updated
- [x] Boundary scan — all 8 prohibited path checks pass
- [x] Symlink audit — all 7 links valid
- [x] Legacy name scan — 8 names absent from active source
- [x] No tracked generated artifacts except `.gitkeep`
- [x] Full suite passes with identical results to pre-removal run
