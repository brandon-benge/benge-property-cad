# Benge Backyard FreeCAD Project

This project generates a conceptual FreeCAD model for the backyard/deck layout.

## Included geometry

- Blue-gray house mass
- Upper covered deck: **24'-6" × 16'** with 5½" deck boards, joists, beams, and support posts
- Lower hot-tub deck: **15' × 19'** with perpendicular 5½" deck boards, joists, beams, and support posts
- Upper deck approximately 8 ft above pool level
- Lower deck approximately 4 ft above pool level
- Diagonal upper stair run starting closer to the house
- Wide landing integrated into the lower deck
- Straight lower run from the landing to pool level
- Full-length cover over the upper deck with fascia, rafters, roof support posts, and large ceiling fan
- Brick fireplace/TV wall with right-side electric fireplace insert and TV above
- Outdoor kitchen with cabinet run, countertop, sink, faucet, grill, and cabinet doors
- Hot-tub placeholder
- 34' × 12' pool, sloped from 5' deep to 8' deep, with 4' paver border
- Railings

## Project layout

- `config.py` — editable dimensions and colors
- `helpers.py` — common geometry utilities
- `model.py` — deck, stairs, roof, pool, railings, and feature geometry
- `build.py` — rebuild function with automatic module reloading
- `BengeBackyard.FCMacro` — build-only FreeCAD launcher macro
- `Build.FCMacro` — rebuilds, then versions with autocommit if available, else git if available, else only rebuilds
- `Revert.FCMacro` — reverts the latest git commit, pushes the revert upstream, then rebuilds; shows an error if git/repo support is unavailable
- `InitRepo.FCMacro` — prompts for Autocommit, Git, or Nothing version management; installs required tools for the selected mode, creates a private GitHub repo when versioning is enabled, commits everything, pushes, then rebuilds
- `macro_actions.py` — shared git/autocommit helpers used by the macros

## Initial setup

1. Extract the project to a permanent folder (moving the folder later requires re-adding the macro).
2. Open FreeCAD.
3. Choose **Macro → Macros…** → **Add existing macro**.
4. Select `BengeBackyard.FCMacro`.
5. Run the macro.
6. The project creates and saves `BengeBackyard.FCStd` in the same folder.
7. Press **0** for axonometric view and then **V, F** to fit the model.

## Daily development workflow

```
Edit a Python file (config.py, helpers.py, or model.py)
  → Save
  → Run Build.FCMacro
  → Review updated model
```

No FreeCAD restart is needed between edits. Successful rebuilds remove FreeCAD's timestamped `.FCBak` backup files from the project folder.

`InitRepo.FCMacro` asks how to manage versions and rollback:

- **Autocommit** installs/checks git, GitHub CLI (`gh`), and autocommit in `.macro_venvs/autocommit`, keeping autocommit dependencies out of FreeCAD's Python environment. It can also download `params.yaml` from `langchain_autocommit`, set `AUTOCOMMIT_PARAMS` to that file, and store `OPENCODE_API_KEY` for autocommit's LLM API key.
- **Git** installs/checks git and GitHub CLI (`gh`) only.
- **Nothing** only rebuilds the model and does not configure version management.

Automatic installs for git and `gh` use Homebrew on macOS and `winget` on Windows when a tool is missing. `gh` must still be authenticated with `gh auth login`.

Autocommit is launched without CLI arguments. It reads configuration from environment variables:

- `AUTOCOMMIT_PARAMS` points to the downloaded params file, stored locally at `.autocommit/params.yaml` when configured.
- `OPENCODE_API_KEY` is used by autocommit as the LLM API key.

Both values are persisted in `.macro_env`, which is ignored by git. If `AUTOCOMMIT_PARAMS` is not set, `Build.FCMacro` emits a runtime warning before running autocommit.

## Python console workflow

### First run

```python
import sys
sys.path.insert(0, "/path/to/benge_freecad_project")

import build
build.rebuild()
```

### Subsequent runs (after editing a file)

```python
build.rebuild()
```

The `rebuild()` function internally reloads `config`, `helpers`, and `model`, so a second `importlib.reload(build)` is not required.

## Edit dimensions

Open `config.py`. Dimensions are expressed in millimeters, but the file uses helpers:

```python
UPPER_DECK_WIDTH = 24.5 * FOOT
LOWER_DECK_DEPTH = 19 * FOOT
```

After editing, run either macro or `build.rebuild()` in the Python console.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Model does not appear after macro | View not refreshed | Press **0** (axonometric) then **V, F** (fit all) |
| `ImportError: No module named build` | Python path is wrong | Check the macro's `PROJECT_DIR` or your `sys.path.insert` path |
| Macro cannot import `build` | Project folder was moved | Re-add the macro in FreeCAD, or update `sys.path` |
| Stale geometry visible | Macro did not complete | Run `Build.FCMacro` again; check the Python console for tracebacks |
| A Python exception occurs | See traceback in FreeCAD Python console | The rebuild function prints the full traceback; fix the reported error in the source file |
| `BengeBackyard.FCStd` cannot be saved | File is locked / permissions | Close the file in FreeCAD's document tab, ensure the project folder is writable |
| `GeneratedModel` persists with old objects | Rebuild did not clean properly | Run `build.rebuild()` from the Python console and check for errors |

## Important limitation

This is a conceptual planning model, not permit-ready structural engineering. Footings, beams, joists, connectors, ledger attachment, roof loads, hot-tub loads, guards, handrails, and stair geometry require review against local code and by qualified professionals.
