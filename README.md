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
- `BengeBackyard.FCMacro` — FreeCAD launcher macro
- `RebuildBengeBackyard.FCMacro` — shortcut macro for daily re-run

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
  → Run RebuildBengeBackyard.FCMacro
  → Review updated model
```

No FreeCAD restart is needed between edits.

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
| Stale geometry visible | Macro did not complete | Run `RebuildBengeBackyard.FCMacro` again; check the Python console for tracebacks |
| A Python exception occurs | See traceback in FreeCAD Python console | The rebuild function prints the full traceback; fix the reported error in the source file |
| `BengeBackyard.FCStd` cannot be saved | File is locked / permissions | Close the file in FreeCAD's document tab, ensure the project folder is writable |
| `GeneratedModel` persists with old objects | Rebuild did not clean properly | Run `build.rebuild()` from the Python console and check for errors |

## Important limitation

This is a conceptual planning model, not permit-ready structural engineering. Footings, beams, joists, connectors, ledger attachment, roof loads, hot-tub loads, guards, handrails, and stair geometry require review against local code and by qualified professionals.
