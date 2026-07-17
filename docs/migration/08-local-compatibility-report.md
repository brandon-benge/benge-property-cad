# Prompt 08: Local Compatibility Verification Report

## Result: PASS

**Verifier**: `cad-compatibility-verifier`
**Date**: 2026-07-16
**Starting HEAD**: `e106fcd fix(migration): add .gitkeep to .opencode/commands and .opencode/tools for git tracking`
**Tag**: `migration-candidate-0.1.0rc1-local`

## Verification Environment

- **OS**: macOS arm64 25.5.0 (Darwin)
- **Python 3.12.9**: Fresh venv at `/tmp/test space/benge-property-cad/.venv312/`
- **Python 3.13.6**: Fresh venv at `/tmp/test space/benge-property-cad/.venv313/`
- **Candidate**: `python-cad-tools-0.1.0rc1-py3-none-any.whl` (SHA `fbc30d4...`)
- **Install method**: `PIP_FIND_LINKS=file:///tmp/python-cad-tools-0.1.0rc1-candidate` with `--require-hashes`
- **Checkout method**: `git archive HEAD` extracted to `/tmp/test space/benge-property-cad/`

## Static Analysis

| Tool | Result | Note |
|------|--------|------|
| Ruff check | 66 E501 errors | Pre-existing, model.py line-length only |
| Ruff format | 7 files would reformat | Pre-existing |
| Mypy | 37-38 errors | Pre-existing, None-flow in tests |

## Test Results (both Python 3.12 and 3.13)

| Test file | Status | Count |
|-----------|--------|-------|
| Config contract | PASS | 8 tests |
| Model contract | PASS | 13 tests |
| Drawing annotations | PASS | 13 tests |
| Build end-to-end | PASS | 25 tests |
| Workflow policy | PASS | 20 tests (previously failed `test_opencode_directories_exist` — fixed) |
| Viewer E2E | ERROR (pre-existing) | ScopeMismatch in fixture |

## CLI Build Pipeline (both Python 3.12 and 3.13)

| Command | Status | Detail |
|---------|--------|--------|
| `python-cad validate` | OK | `design_semantic_hash: 7058c126...` |
| `python-cad clean` | OK | Clean succeeded |
| `python-cad build` | OK | 23 artifacts, `stable_hash: a28125b...` |
| `python-cad verify` | OK | All artifacts match recorded hashes |
| `python-cad prepare-site` | OK | 198 files, `design_build_hash == stable_hash` |

## Determinism

- Python 3.12 and 3.13 produce **identical** `stable_artifact_set_hash`: `a28125b...`
- Two builds on the same Python version produce identical hashes
- All 23 artifacts byte-for-byte identical across both runs

## One-Dimension Change Simulation

- Changed `DECK_BOARD_THICKNESS` from `1.25 * INCH` to `1.3 * INCH` in `config.py`
- Only `config.py` differed between baseline and changed checkout
- Build succeeded with 22 artifacts and different `stable_hash`
- Proves ordinary design work touches only project-owned files

## Defect Found and Fixed

- `test_opencode_directories_exist` failed in fresh `git archive` checkout because `.opencode/commands/` and `.opencode/tools/` are empty directories not tracked by git
- Fix: added `.gitkeep` to both directories (commit `e106fcd`)

## Compatibility Report

Machine-readable report: `docs/migration/08-compatibility-report.json`

## Tag

Created annotated tag: `migration-candidate-0.1.0rc1-local`

## Pending Items (explicitly unsupported in this local run)

- Ubuntu x86_64 platform verification
- GitHub CI matrix execution
- Registry-based installation
- Pages deployment
- Playwright viewer E2E browser tests
- Windows platform support
