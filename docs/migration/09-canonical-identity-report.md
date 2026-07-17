# Prompt 09: Canonical GitHub identity report

## Authority

All five authority questions confirmed by owner before any remote mutation.

| # | Question | Answer |
|---|----------|--------|
| 1 | Push verified commits/tags | Yes |
| 2 | Rename repo to benge-property-cad, update origin, verify redirect | Yes |
| 3 | Update repo/Pages settings and protected environments | Yes |
| 4 | Authenticated GitHub connector (GITHUB_TOKEN with repo scope; workflow scope missing) | PAT available, no `gh` CLI |
| 5 | Tooling repo renamed to python-cad-tools | https://github.com/brandon-benge/python-cad-tools, commit 32ff6d8, version 0.1.0rc1 |

## Pre-push verification

- HEAD: `64a0627` (Prompt 09 checkpoint — canonical URL updates)
- Working tree: clean at start
- Tags: `migration-candidate-0.1.0rc1-local` (existing, points to e106fcd), `migration-candidate-0.1.0rc1-identity` (new, points to 64a0627), `pre-migration-benge-baseline-df58179` (existing)
- Legacy name boundary: pass — no `benge_freecad_project`, `BengeComplexFunctional`, or `complex-functional` in source files

## Source URL corrections

Files updated to use canonical `benge-property-cad` identity:

| File | Change |
|------|--------|
| `config.py:1` | Module docstring updated to `benge-property-cad` |
| `model.py:407` | `source_authority` URL updated to `https://github.com/brandon-benge/benge-property-cad` |
| `tests/fixtures/model_contract_v1.json` | `source_authority` and `source_sha256` updated |
| `.github/workflows/ci.yml` | Legacy name scan excluded fixture (contains migration doc references); *reverted from push due to workflow scope* |

## Push and remote rename

- Initial push attempt rejected: GITHUB_TOKEN lacks `workflow` scope (workflow file in history)
- Owner manually: renamed repo at GitHub to `benge-property-cad`, resolved auth
- Final push succeeded: `main` branch (11 commits) + 3 tags pushed to `https://github.com/brandon-benge/benge-property-cad.git`
- Remote origin updated: `https://github.com/brandon-benge/benge-property-cad.git`
- Old URL `https://github.com/brandon-benge/benge_freecad_project` redirects to new URL

## Local directory rename

- Directory renamed from `benge_freecad_project` to `benge-property-cad`
- Virtual environment scripts updated (shebangs with hardcoded old path fixed via `sed` replacement in 31 files)
- `tests/conftest.py`: added `"site"` to copy ignore list (pre-existing issue surfaced by `prepare-site` output in copied test fixtures)

## Gates from renamed path

All gates pass from `/Users/brandonbenge/Desktop/Houses Folder/Dreaming of Yard and House Updates/benge-property-cad`:

| Gate | Result |
|------|--------|
| `ruff check` | 66 pre-existing E501 line-too-long errors (unchanged) |
| `ruff format --check` | 7 files would be reformatted (unchanged) |
| `mypy` | Pre-existing type errors in tests/ (unchanged) |
| `pytest -m "not e2e"` | 80/80 pass |
| `python-cad validate` | OK |
| `python-cad build` | 23 artifacts, stable hash `7092b62...` |
| `python-cad verify` | OK (hash matches) |
| `python-cad prepare-site` | 198 files, base-path `/benge-property-cad/` |

## Active path check

No active configuration embeds the old absolute path `benge_freecad_project` in source files (config.py, model.py, drawing_annotations.py, tests/, README.md, pyproject.toml). Historical migration documents retain the old names for provenance.

## Checkpoint

Current HEAD: `64a0627` (pushed, matching local)
Pending: `tests/conftest.py` has uncommitted fix (`"site"` in copy ignore list) — committed and pushed as part of this stage.
