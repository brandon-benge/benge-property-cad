# Two-Repository Split: Prompt and Migration Plan

## Decision

Split the repositories, but make the split around an installed, documented
`python_cad_tools` package rather than around a copied `.tools/` directory.

The intended dependency direction is one-way:

```text
benge_freecad_project
  config.py
  model.py
  drawing_annotations.py
  project_tests/
          |
          | imports a versioned public API and invokes its CLI
          v
freecad_macro_project_template
  python_cad_tools package
  exporters and validation
  build/serve CLI
  viewer source and packaged viewer assets
  framework tests and release automation
```

Design agents working in `benge_freecad_project` should not need to inspect the
package implementation. They will still import and execute the installed
package. The package must therefore provide a stable public API, concise
authoring documentation, type information, and useful errors.

## What the current repository proves

The split is viable, with two current couplings that must be removed first.

| Project file | Current dependency | Target |
| --- | --- | --- |
| `config.py` | `python_cad_tools.units` from `.tools/` | Same public import from an installed package |
| `model.py` | `context`, `elements`, `geometry`, and `units` from `.tools/python_cad_tools` | Same concepts through a documented public package API |
| `model.py` | Imports `drawing_annotations` only to register an `atexit` callback | Declare an explicit package-supported post-build hook |
| `drawing_annotations.py` | Reads and modifies generated SVG/DXF; `--rebuild` invokes root `build.py` | Receive the staging output path from the hook; use the package CLI for standalone rebuilds |
| `project_tests/test_benge_project.py` | Calls `build_project` and checks Benge-specific IDs, counts, filenames, and output reconciliation | Keep in Benge; use stable public build/inspection APIs |
| `build.py` | Adds `.tools` to `sys.path` and delegates to the package CLI | Remove from Benge after the installed CLI is available |
| `start.sh` | Synchronizes `.tools` dependencies, builds, prepares viewer assets, starts Vite | Replace with a packaged `python-cad serve` command |
| `viewer/` | Reads only generated artifacts, not project Python | Own its source in the template/package repository; ship its built static assets with the package |

The current `project_tests/` belongs in `benge_freecad_project`: its assertions
are about the Benge model, not the reusable framework. The template repository
should own unit/integration tests for units, geometry, exporters, validation,
CLI behavior, packaging, and the viewer. It may use a generic fixture, but it
should not carry a live duplicate of the Benge model as framework source of
truth. A downstream compatibility test can build a released or checked-out
Benge project without copying that project into the template repository.

## Important defect to fix during the split

`drawing_annotations.py` currently edits artifacts from an `atexit` handler.
The framework writes `build-manifest.json` and its artifact hashes before that
handler runs. As a result, the current annotated plan SVG and DXF do not match
the SHA-256 values recorded in the build manifest.

The package build order must become:

1. Load and validate the project model.
2. Export into a staging directory.
3. Run declared project post-processors against that staging directory.
4. Validate the final artifacts.
5. Write artifact hashes and manifests last.
6. Atomically promote staging to `generated/`.

Post-processors must not use `atexit`, mutate already-promoted output, or rely
on a root `build.py` file.

## Target ownership

### `benge_freecad_project`

Project-owned design source:

- `config.py`
- `model.py`
- `drawing_annotations.py`
- `project_tests/`

Minimal repository support files also remain here:

- `pyproject.toml`, containing the pinned tool-package dependency and project
  test/lint configuration
- a dependency lock file if reproducible installs are required
- `AGENTS.md`, with the narrow design-agent boundary and public commands
- `.gitignore`
- a short project `README.md`
- project CI workflow(s)
- `generated/.gitkeep`, only if the empty output directory is useful

Generated artifacts are disposable outputs, not design-agent context.

This means “everything else goes to the template repository” applies to shared
implementation and product source. It cannot include Benge's own package
declaration, agent boundary, project CI, or basic repository documentation.

### `freecad_macro_project_template`

Reusable product source:

- installable `python_cad_tools` package
- build orchestration, CLI, model contracts, units, geometry, validation,
  manifests, exporters, and compatibility adapters
- generic package unit and integration tests
- viewer TypeScript source and tests
- prebuilt viewer assets included as Python package data
- `python-cad build`, `python-cad clean`, and `python-cad serve` commands
- package documentation and a minimal example project
- wheel/sdist build, release, and registry publishing workflows
- optional legacy installer/updater compatibility during a deprecation window

The package should use a normal source layout such as
`src/python_cad_tools/`, not `.tools/python_cad_tools/`. The repository may keep
the historical name, but the recommended distribution name is
`python-cad-tools`, matching the existing import namespace. If the distribution
must instead be named `freecad-macro-project-template`, document clearly that
its Python import remains `python_cad_tools` and use that one name consistently
in dependency declarations and releases.

## Public contract required before removing `.tools/`

The template/package agent must explicitly support and document:

- `BuildContext`
- `DesignElement`, `DesignModel`, `Dimensions`, `IfcMapping`, `MaterialSpec`,
  and `Placement`
- length types, constants, conversion, and formatting used by design source
- the supported geometry constructors used by `model.py`
- a programmatic build function for project tests
- a CLI that builds the current directory without a copied launcher
- a project post-processor protocol
- supported artifact-inspection helpers needed by downstream tests
- compatibility/version policy for serialized manifests and semantic IDs

Recommended project configuration:

```toml
[project]
dependencies = [
  "python-cad-tools==<released-version>",
  "ezdxf>=1.4,<2", # direct runtime import in drawing_annotations.py
]

[tool.python-cad]
model = "model:build_model"
postprocessors = ["drawing_annotations:annotate_all"]
output-directory = "generated"
```

The exact TOML keys can change, but hook discovery must be declarative and
documented. A suitable hook contract is conceptually:

```python
def annotate_all(context: ArtifactPostprocessContext) -> list[Path]: ...
```

The context should identify the project directory, staging output directory,
selected formats, and model metadata. The package should reject paths outside
staging and recalculate/validate manifests after hooks finish.

## Agent boundary after migration

The Benge `AGENTS.md` should tell design agents:

- Default editable scope is `config.py`, `model.py`,
  `drawing_annotations.py`, and `project_tests/`.
- Read `pyproject.toml` only when dependency or hook configuration matters.
- Use the documented public `python_cad_tools` API; do not inspect or patch
  site-packages during normal design work.
- Run `python-cad build` and the Benge test suite after design changes.
- Preserve stable semantic IDs and intentional IFC mappings/exclusions.
- Treat `generated/` as disposable output.
- If a required capability is missing from the public API, report it as an
  upstream template/package request instead of creating a local infrastructure
  workaround.

Package maintainers and template agents may read and edit package internals.
Viewer agents should work only in the template repository unless a Benge issue
is proven to be malformed generated data.

## Ordered implementation prompts

Run these prompts in order. Do not let two agents edit the same repository at
the same time. Both current worktrees contain uncommitted agent-instruction
moves; preserve and reconcile those user changes rather than resetting them.

### Prompt 1 — Template/package agent: create the distributable boundary

> Work only in `freecad_macro_project_template`. Convert the reusable tooling
> into an installable, versioned Python distribution using
> `src/python_cad_tools/`. Preserve the public import namespace
> `python_cad_tools`. Add wheel and sdist configuration, package type
> information, console entry points, and package documentation. Implement
> `python-cad build`, `python-cad clean`, and a programmatic public build API
> that operate on a project directory without requiring a copied `.tools/`
> tree or root `build.py`. Keep current exporters and default
> FreeCAD-independent behavior. Do not alter the sibling Benge repository.
> Add tests that install the built wheel into a clean environment and build a
> minimal external fixture using only installed APIs. Preserve all unrelated
> uncommitted user changes. Stop with a release-ready change and a migration
> report; do not publish yet.

Acceptance criteria:

- A wheel and sdist build successfully.
- A clean virtual environment can import `python_cad_tools` without path hacks.
- No test configuration needs `pythonpath = [".tools", ...]`.
- The minimal external fixture builds through both CLI and public Python API.
- Unit/integration tests exercise installed code, not the vendored copy.

### Prompt 2 — Template/package agent: add safe project hooks and viewer delivery

> Continue in `freecad_macro_project_template`. Add a documented,
> declaratively configured artifact post-processor API. Run hooks inside the
> staging directory after export and before artifact validation, manifest
> hashing, and atomic promotion. Add failure handling and path-safety tests.
> Then make the viewer usable by downstream projects without copying viewer
> source: build the static viewer in this repository, include the production
> assets in the Python distribution, and implement `python-cad serve` (and, if
> useful for Pages, `python-cad prepare-site`) against a project's generated
> directory. Keep TypeScript source and viewer tests only here. Do not modify
> the Benge repository and do not publish.

Acceptance criteria:

- A test post-processor visibly changes a staged artifact.
- The final build manifest records the changed artifact's correct size/hash.
- A failed hook cannot partially replace the previous `generated/` directory.
- Hook code receives paths/context explicitly and needs no `atexit` behavior.
- The installed wheel can serve or prepare the viewer with no downstream
  `viewer/` checkout and no `start.sh`.

### Prompt 3 — Template/package agent: separate framework and downstream tests

> Continue in `freecad_macro_project_template`. Classify all tests by
> ownership. Keep framework unit/integration, packaging, CLI, exporter, and
> viewer tests here. Replace the copied live Benge fixture with a small generic
> contract fixture wherever it is testing framework behavior. If a realistic
> downstream compatibility check is still valuable, make it an explicit
> optional CI job that checks out a versioned Benge revision; do not duplicate
> Benge source in this repository. Expose or document any artifact-inspection
> helper that a downstream project legitimately needs so downstream tests do
> not import unstable exporter internals.

Acceptance criteria:

- Framework tests contain no authoritative copy of Benge's `model.py` or
  `config.py`.
- Template tests can run without the sibling repository.
- Optional downstream testing is clearly marked and versioned.
- Public versus private Python APIs are documented.

### Prompt 4 — Release agent: publish a migration release

> In `freecad_macro_project_template`, verify the package in clean Python 3.12
> and 3.13 environments, run Python and viewer checks, build wheel/sdist, and
> verify their contents. Publish a prerelease to the chosen private registry
> or TestPyPI only after credentials and destination are explicitly confirmed.
> Record the exact package name and version for the Benge migration. Do not
> change the Benge repository.

Do not proceed to Prompt 5 until an installable version or locally verified
wheel is available.

### Prompt 5 — Benge design agent: consume the package

> Work only in `benge_freecad_project`. Replace `.tools` path injection and
> duplicated framework dependencies with the exact released
> `python-cad-tools` dependency version (or an exact local wheel during the
> prerelease trial). Keep `config.py`, `model.py`, and
> `drawing_annotations.py` project-owned. Convert drawing annotation
> integration from import-time `atexit` registration to the package's declared
> post-build hook. Make annotation functions operate on the staging output path
> supplied by the framework. Remove the `--rebuild` dependency on root
> `build.py`; document the package CLI instead. Keep and strengthen
> `project_tests/` as Benge-specific end-to-end tests. Preserve unrelated
> uncommitted user changes and do not edit the sibling template repository.

Acceptance criteria:

- `config.py` and `model.py` import only installed package APIs plus project
  modules.
- `model.py` has no annotation side-effect import.
- Annotation output is complete before `build_project` returns.
- Tests verify expected Benge IDs/counts and actual annotation elements.
- Tests verify every manifest artifact size and SHA-256 after annotation.
- No Benge test imports an explicitly private package module.
- The build works with `.tools/` temporarily renamed or absent.

### Prompt 6 — Benge repository cleanup agent

> Continue in `benge_freecad_project` only after Prompt 5 passes. Remove
> vendored managed implementation: `.tools/`, root `build.py`, `start.sh`, and
> `viewer/`. Remove updater/installer-specific guidance and old copied-tool
> manifests. Keep the minimal repository support files listed in this plan.
> Update CI to install the pinned package, run lint/type/tests, build through
> `python-cad build`, verify deterministic semantic output, and prepare the
> packaged viewer only when deployment is requested. Add a narrow `AGENTS.md`
> that prevents normal design agents from reading package internals. Do not
> edit the template repository.

Acceptance criteria:

- No `.tools`, root build launcher, start script, or viewer source remains.
- `rg` finds no `.tools` path references in active source/configuration/docs.
- A fresh clone plus dependency installation can test, build, and serve/view.
- CI and local documented commands are identical where practical.
- Only Benge-specific tests remain under `project_tests/`.

### Prompt 7 — Cross-repository release verification

> Verify both repositories without changing their ownership boundary. In a
> clean environment, install the exact released tool package, check out the
> Benge repository, run its tests and full build, verify all manifest hashes,
> and smoke-test packaged viewer preparation/serving. Confirm that changing a
> Benge dimension requires touching only Benge-owned files and that changing an
> exporter requires touching only the template/package repository. Produce a
> short compatibility report containing the Benge revision, package version,
> Python version, and semantic build hash.

## Verification checklist

Template/package repository:

```text
ruff check src tests
mypy src/python_cad_tools
pytest
python -m build
install wheel in a clean environment
build the external minimal fixture
npm ci && npm test && npm run build   # in viewer source directory
```

Benge repository:

```text
install the exact declared dependency set in a clean environment
ruff check config.py model.py drawing_annotations.py project_tests
mypy
pytest -q
python-cad build
verify every build-manifest artifact hash
python-cad serve                      # smoke test only
```

## Final definition of done

- Design agents can make ordinary CAD changes without reading `.tools`,
  `build.py`, `start.sh`, viewer source, exporter internals, or package source.
- Benge source depends only on an installed, pinned, documented public API.
- `project_tests/` verifies the Benge design; template tests verify the tool.
- Annotations participate transactionally in the build and manifests describe
  the final bytes.
- The viewer is maintained once, in the template/package repository.
- A package release can upgrade Benge through one explicit dependency-version
  change and a compatibility test run.
