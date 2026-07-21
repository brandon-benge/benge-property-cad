# Benge Property CAD

Parametric CAD model of the Benge property, built with the published
`python-cad-tools` package. The editable design lives in `config.py`, `model.py`,
and `drawing_annotations.py`; tests live in `tests/`.

A headless build produces STEP, IFC4, GLB, conceptual SVG/DXF/PDF drawings,
quantity reports, validation reports, and manifests. FreeCAD and Blender are not
required.

## Requirements

- Python 3.12 or 3.13
- A platform matching one of the lockfiles in `requirements/locks/`

## Setup

Create a virtual environment and install the lockfile for your platform and
Python version. For example, on Apple silicon with Python 3.13:

```bash
python3.13 -m venv .venv
.venv/bin/pip install --require-hashes \
  -r requirements/locks/dev-macos-arm64-py313.lock
```

Available lockfiles cover Python 3.12 and 3.13 on macOS arm64 and Ubuntu
x86_64. Each lock records exact transitive versions and hashes.

## Build and inspect the model

```bash
.venv/bin/python-cad validate --project-root .
.venv/bin/python-cad build --project-root .
.venv/bin/python-cad verify --project-root .
```

To inspect the result in the interactive viewer:

```bash
.venv/bin/python-cad serve --project-root . --port 8080
```

Open the URL printed in the terminal, typically
`http://127.0.0.1:8080/`. The viewer supports orbit controls, element
selection, measurement, and downloads of generated formats.

Generated files are written to `generated/`. They are disposable build evidence
and are ignored by Git except for `.gitkeep`; edit the authoritative Python
source instead.

## Edit the design

- Change dimensions and materials in `config.py`.
- Compose shared geometry and metadata in `model.py`.
- Maintain drawing labels and dimensions in `drawing_annotations.py`.
- Preserve stable semantic IDs, including existing `complex.*` IDs.
- Update geometry, metadata, and tests together.

Use only documented public APIs from the installed `python-cad-tools` package.

## Development checks

```bash
.venv/bin/ruff check config.py model.py drawing_annotations.py tests/
.venv/bin/ruff format --check config.py model.py drawing_annotations.py tests/
.venv/bin/mypy config.py model.py drawing_annotations.py tests/
.venv/bin/python -m pytest -q
```

Additional project commands:

```text
python-cad clean --project-root PATH
python-cad prepare-site --project-root PATH --destination PATH --base-path PATH
```

CI runs the applicable static analysis, tests, build, verification, and site
checks with the native lockfile for its environment.

## Dependency updates

The project currently allows `python-cad-tools>=0.1.4,<0.2`. When upgrading the
package, regenerate all four native lockfiles, confirm that they contain no
local path or source-checkout references, and rerun the full verification
matrix. This repository must consume the published PyPI package; do not vendor,
patch, or install `python-cad-tools` from a local checkout.

## Limitations

Generated drawings are conceptual and are not suitable for construction or
permitting. This project does not provide engineering, code, permit, survey, or
licensed-trade approval.

## Agent governance

See `AGENTS.md` for repository boundaries, responsibilities, writable scope,
and verification expectations for the four project roles:

- `file-design-maintainer`
- `file-artifact-reviewer`
- `cad-compatibility-verifier`
- `save`
