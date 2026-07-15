# Benge Backyard Python CAD Project

This project is the live Python-first translation of the original Benge FreeCAD backyard concept. `model.py` and `config.py` are the authoritative design source. The reusable build system, exporters, validation, tests, and project policy are managed under `.tools/` by the `freecad_macro_project_template`.

The translated source is based on `brandon-benge/benge_freecad_project` commit `76b8d75c88d606611a82d135a45fc9be7ce840fb`. It models 236 semantic elements covering:

- upper and lower decks, deck boards, beams, joists, ledgers, and support posts;
- roof structure, fascia, rafters, posts, and covered-deck fan;
- fireplace, TV, sliding door, outdoor kitchen, and hot-tub platform;
- stairs, handrails, posts, guards, and skirting;
- pool patio and a sloped 5-foot-to-8-foot pool volume.

## Setup and build

```bash
python3 -m venv .venv
.venv/bin/pip install -r .tools/requirements/runtime.lock
.venv/bin/python build.py
```

The default build writes retained results under `generated/`:

```text
generated/
├── drawings/     # conceptual SVG, DXF, and four-page vector PDF
├── glb/          # glTF scene and validation manifest
├── ifc/          # IFC4 model and IfcOpenShell validation
├── manifests/    # stable design IDs, hashes, versions, and build metadata
├── quantities/   # geometry-derived JSON, CSV, and Markdown schedules
└── step/         # exact BREP assembly and reload validation
```

Focused commands:

```bash
.venv/bin/python build.py --validate-only
.venv/bin/python build.py --format step
.venv/bin/python build.py --format ifc --format quantities
.venv/bin/python build.py --clean
```

`--clean` removes rebuildable files under `generated/` but preserves `generated/.gitkeep`. Generated files are ignored by Git.

## Functional test

The project-owned functional test builds the live root `model.py` and `config.py`, parses every output format, and reconciles the 236 stable IDs across STEP, IFC, GLB, quantities, manifests, and drawings:

```bash
.venv/bin/pytest -q
```

Unlike the template’s isolated regression fixture, this test writes to this project’s persistent `generated/` directory. Its results remain available after pytest exits. The GitHub Actions workflow at `.github/workflows/build-design.yml` runs the same test and uploads `generated/` as `benge-backyard-generated`.

## Project ownership

Project-specific edits belong in `model.py`, `config.py`, `params.yaml`, this README, or project-specific tests. Do not edit `.tools/`, managed root launchers, managed agent definitions, or generated files as design inputs.

Refresh the managed template layer with:

```bash
.venv/bin/python .tools/update_tools.py
```

The root `update_tools.py` is a compatibility alias. The updater preserves project-owned source and replaces only manifest-declared managed paths.

## Original-project backup

The complete original project is preserved under `backup/`, including its historical Git metadata, FreeCAD files, macros, source, tools, and agent configuration. The rewrite does not read from or modify that directory during normal builds. `backup/` is ignored by the new project’s Git configuration so it cannot be accidentally committed as part of the translated project.

The generated drawings are conceptual and not for construction or permitting. This project does not provide engineering, code, permit, survey, or licensed-trade approval.
