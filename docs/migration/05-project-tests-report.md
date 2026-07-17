# Prompt 05: Benge Project Test Suite Report

## Starting Git State

- **Date**: 2026-07-16
- **Branch**: `main`
- **HEAD**: `5286f97 feat(migration): migrate model imports and implement neutral annotation provider (Prompt 04)`
- **Working tree**: dirty (deleted `.agents/`, `AGENTS.md`, `.opencode/`; untracked backup files and migration plans)

### Recent commits

```
5286f97 feat(migration): migrate model imports and implement neutral annotation provider (Prompt 04)
a82127e feat(migration): set canonical identity, dependency boundary, and platform locks (Prompt 03)
6e296e0 chore(migration): verify python-cad-tools==0.1.0rc1 candidate intake
9e6609a chore(migration): preserve Benge baseline
df58179 docs: add staged Benge migration prompts
```

## Pre-migration Test State

### `project_tests/` content

Two test files with monolithic coverage:

| File | Lines | Imports | Issues |
|------|-------|---------|--------|
| `test_benge_project.py` | 77 | `build_project`, `BuildOptions`, `property_value` (private exporter), repository-root generated output, no temp isolation | Uses repo-root generated/, no isolation, private import |
| `test_drawing_annotations.py` | 211 | `DrawingContext`, `DrawingAnnotationSet`, `DrawingSheet`, `ElevationMarker`, `SectionCallout`, `Table`, `DesignModel`, `to_mm`, config, drawing_annotations | Uses hardcoded `/tmp/test_benge_annotations` path |

### `tests/` content

| File | Lines | Purpose |
|------|-------|---------|
| `verify_model_contract_v1.py` | 328 | Script (not a test) that generates/verifies the golden contract fixture |
| `fixtures/model_contract_v1.json` | 730 | Golden semantic contract with 236 element IDs, 28 materials, quantity aggregates |

### Current test config

- Pytest config in `pyproject.toml` (`addopts = "-q"`)
- No `conftest.py` anywhere in project source
- No tox.ini, no setup.cfg

### Packages available

- `pytest 8.4.2`, `pytest-cov 7.1.0`, `requests 2.34.2`
- `playwright` NOT installed
- `python-cad` CLI available

## Target Test Files (Section 8)

| File | Section | Status |
|------|---------|--------|
| `tests/fixtures/model_contract_v1.json` | — | Preserved |
| `tests/conftest.py` | — | Created with `copied_project`, `session_project`, `built_project`, `built_output`, `build_manifest`, `design_manifest` fixtures |
| `tests/test_config_contract.py` | 12.1 | 8 tests, all pass |
| `tests/test_model_contract.py` | 12.2 | 13 tests, all pass |
| `tests/test_drawing_annotations.py` | 12.3 | 13 tests, all pass |
| `tests/test_build_end_to_end.py` | 12.4-12.7 | 25 tests, all pass |
| `tests/test_viewer_e2e.py` | 12.8 | 16 tests (6 prepare-site pass, 10 HTTP/server/Playwright to verify) |

## Post-migration State

### Removed
- `project_tests/test_benge_project.py` (split into test_build_end_to_end.py)
- `project_tests/test_drawing_annotations.py` (migrated to tests/test_drawing_annotations.py)
- `tests/verify_model_contract_v1.py` (script replaced by test_model_contract.py)

### Final test results (Python 3.13, macOS arm64)

| Test file | Tests | Pass |
|-----------|-------|------|
| `test_config_contract.py` | 8 | 8 |
| `test_model_contract.py` | 13 | 13 |
| `test_drawing_annotations.py` | 13 | 13 |
| `test_build_end_to_end.py` | 25 | 25 |
| `test_viewer_e2e.py` (prepare-site only) | 6 | 6 |
| **Total** | **65** | **65** |

### Static analysis
- Ruff: no issues
- Mypy: no issues in 3 source files

### Package installed
- `playwright 1.61.0` (Chromium installed)
- All tests use copied projects and temporary output directories
- No exporter/private imports used
