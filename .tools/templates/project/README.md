# Python CAD Project

This project uses `model.py` and `config.py` as its authoritative design source. One headless build generates exact STEP, IFC4, GLB, conceptual SVG/DXF/PDF drawings, quantities, validation reports, and manifests without FreeCAD or Blender.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r .tools/requirements/runtime.lock
python build.py
```

On Windows, use the executables under `.venv\Scripts`.

Edit project dimensions and materials in `config.py` and build shared elements in `model.py`. Preserve stable semantic IDs. Do not edit `.tools/`, managed root launchers, or files under `generated/`.

Useful commands:

```bash
python build.py --format step
python build.py --format ifc --format quantities
python build.py --validate-only
python build.py --clean
python .tools/update_tools.py
```

The updater implementation lives under `.tools/`; `python update_tools.py` is a compatibility alias. Both commands refresh only manifest-declared managed paths. They preserve `model.py`, `config.py`, this README, project tests, and unknown files. Managed-tool fixes must be made in the upstream template repository, not in this installed project.

`generated/` is ignored by Git except for `.gitkeep`. CI should upload generated artifacts instead of committing them.

FCStd is optional and truthful: `--include-fcstd` requires FreeCADCmd, creates a compatibility import from shared STEP, and is never the design authority.

Conceptual drawings are not for construction or permitting. This project does not provide engineering, code, permit, survey, or licensed-trade approval.
