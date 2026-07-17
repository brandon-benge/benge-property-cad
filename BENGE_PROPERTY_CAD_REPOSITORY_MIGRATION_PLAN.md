# `benge-property-cad` Repository Migration and Verification Plan

- Status: execution-ready architecture plan
- Plan contract: `repo-split-v1`
- Current checkout name: `benge_freecad_project` (legacy only)
- Required repository name: `benge-property-cad`
- Required project metadata name: `benge-property-cad`
- Required tooling dependency: `python-cad-tools`
- Required tooling import namespace: `python_cad_tools`
- Required tooling command: `python-cad`
- Required initial stable tooling pin: `python-cad-tools==0.1.0`

## 1. Authority, objective, and terminal condition

This file is the implementation authority for the Benge design repository. An
agent executing it may edit only this repository. It must not modify the
`python-cad-tools` source repository or installed site-packages. If a public
capability is missing, the agent records a reproducible upstream requirement
and waits for a new candidate package; it does not create a local framework fork.

The objective is a deliberately small, property-specific repository in which
the authoritative editable design is easy for an AI agent to understand:

- `config.py` owns property dimensions, materials, and design parameters;
- `model.py` owns geometry composition and semantic metadata;
- `drawing_annotations.py` owns project-specific drawing intent through a
  public, format-neutral package contract;
- `tests/` owns all Benge-specific expectations;
- a small set of repository policy, dependency, CI, and documentation files
  makes the project reproducible.

The repository must consume a versioned registry package. It must not contain a
copied `.tools` implementation, root build launcher, start script, viewer source,
framework tests, framework agent roles, or legacy macro backups in its active head.

This migration is complete only when an AI verification agent has created a
fresh checkout containing this repository alone, installed the exact stable
registry dependency without editable/path/VCS tricks, and executed lint, typing,
all tests, complete CAD build, independent artifact verification, deterministic
comparison, packaged-site preparation, HTTP checks, and browser E2E. The agent
must produce a machine-readable compatibility report. The last step is never a
request for the user to test, open a file, or inspect a browser manually.

The repository owner may authorize credentials, registry access, GitHub rename,
Pages permissions, or a license choice. Those are authority inputs; the AI still
executes and records every technical verification.

## 2. Audit verdict and corrections to the combined plan

The two-repository split is feasible and recommended. `config.py`, `model.py`,
and the Benge test expectations already depend on reusable tooling mainly through
imports, so a normal installed package is the correct boundary. The combined
plan was directionally sound but is not detailed enough to execute. This plan
makes these corrections binding:

1. The repository is renamed to `benge-property-cad`, not “backyard” or a generic
   “CAD project.” “Property” covers the existing house mass, yard, decks, pool,
   and planned house updates without implying construction-document authority.
2. `project_tests/` remains Benge-owned but is renamed to conventional `tests/`.
   No Benge test moves into the tooling package.
3. Repository/product identity is migrated once to `Benge Property`; existing
   `complex.*` element IDs remain unchanged as opaque stable identifiers. They
   must not be silently rewritten during infrastructure renaming.
4. The primary annotation boundary is a format-neutral drawing provider. Direct
   SVG/DXF mutation is removed so SVG, DXF, and PDF describe the same annotation
   intent and so exporter structure is not a downstream dependency.
5. The project keeps its own `pyproject.toml`, native locks, README, AGENTS policy, CI,
   and Pages workflow. These cannot be moved into or overwritten by a wheel.
6. Viewer implementation moves upstream, but this repository retains a thin
   deployment workflow invoking installed `python-cad prepare-site`.
7. Legacy `backup/` is project history, never reusable source. Preserve it in a
   pre-migration tag/archive, prove recoverability, then remove it from the active
   head to reduce agent context.
8. Current agent-file moves and broken symlinks are user changes. Reconcile them
   deliberately; never reset or blindly copy the broken state.
9. Tests must inspect final post-annotation bytes and every manifest hash. A
   semantic hash alone is not artifact integrity.
10. Every terminal gate is AI-run in an isolated environment, including browser
    behavior and deployed Pages smoke tests when authorization permits.

## 3. Evidence from the current repository

### 3.1 Actual dependency boundary

| File | Current coupling | Audited conclusion |
| --- | --- | --- |
| `config.py` | Imports `FOOT` and `INCH` from `.tools` through `python_cad_tools.units` | Keep the import spelling; resolve it from an installed package |
| `model.py` | Imports context, elements, geometry, and units from `python_cad_tools` | These must be documented public modules with packaged types |
| `model.py` | Imports `drawing_annotations` only for an `atexit` side effect | Remove entirely; configuration loads the annotation provider |
| `drawing_annotations.py` | Uses a global project-relative `generated/`, root `build.py` subprocess, and `atexit` | Replace with a pure format-neutral provider; no artifact/global/process lifecycle coupling |
| `project_tests/test_benge_project.py` | Calls `build_project`, imports a private IFC helper, and asserts Benge identities/files | Rename/split under `tests/`; use public inspection API plus independently declared test libraries where needed |
| root `build.py` | Adds `.tools` to `sys.path` and delegates | Delete after installed CLI/API gates pass |
| `start.sh` | Synchronizes copied locks, builds, installs npm, prepares source viewer, starts Vite | Delete after packaged site/serve gates pass |
| `viewer/` | Reads generated artifacts/manifests only | Delete downstream source; use packaged model-free viewer shell |

Neither ordinary design editing nor the final project needs to read tooling
implementation, `start.sh`, or viewer source. Agents still need the documented
public package API and generated validation evidence.

### 3.2 Confirmed annotation/build defects

- `model.py` import registers an `atexit` callback. Programmatic
  `build_project()` returns before annotations are applied.
- The package exports, hashes, writes manifests, and promotes output first. The
  callback then mutates final plan SVG and DXF.
- The current plan SVG and plan DXF fail the size/SHA-256 values recorded in
  `generated/manifests/build-manifest.json`; the other recorded drawing files
  matched during this audit.
- A callback failure cannot turn the already successful build into a failure.
- Importing model code or exiting a failed/validate-only process can mutate a
  pre-existing `generated/` directory.
- `drawing_annotations.py --rebuild` invokes a child build that annotates at
  child exit and then annotates again in the parent. DXF semantic entities may
  be deduplicated, but repeated serialization is not byte-idempotent.
- SVG behavior relies on sheet `A-101`, the first two SVG group positions, and a
  particular Y-flip transform. DXF behavior guesses the sheet from “plan” in the
  filename and relies on renderer layers/linetypes. None is a public contract.
- Malformed/unexpected SVG, missing `ezdxf`, or unreadable DXF can return false
  silently while the build still appears successful.
- The section cut, elevation points, and 6-by-7-foot door schedule are duplicated
  literals rather than values derived from config/model metadata.
- Only SVG and DXF receive annotations; the PDF sheet set does not.

The target design must not merely move this mutation earlier. It must express
project drawing intent through a typed package API so every drawing renderer is
consistent and required annotation errors fail the build transaction.

### 3.3 Tests and CI are currently insufficient

- The single project test checks 236 elements, selected IDs, output reconciliation,
  and conceptual notices, but it never asserts the new section callout, elevation
  markers, schedule, or final manifest hashes.
- It imports `python_cad_tools.exporters.ifc.property_value`, which is exporter
  implementation rather than a documented project API.
- It hardcodes old fixture commit `76b8d75...` and Benge fixture identity.
- Pytest/mypy work through `.tools` path injection.
- CI installs `.tools/requirements/dev.lock`, lints neither
  `drawing_annotations.py` nor all intended tests explicitly, uses only Python
  3.13, and assumes pytest creates output before its determinism comparison.
- The semantic build hash covers design/paths/selection, not final artifact bytes,
  so it cannot detect the confirmed annotation corruption.
- Pages CI requires the copied viewer and Node in this design repository.
- The current project virtual environment passed the one pytest test, but it did
  not contain `ruff`; this proves that a clean development-install gate is needed.

### 3.4 Current naming and repository hygiene defects

- `pyproject.toml` still declares generic `python-cad-project`.
- `config.py` uses artifact/project name `BengeComplexFunctional`.
- `model.py` uses model ID `functional.benge_complex`, source module
  `functional.benge_complex.model`, tag `complex-functional`, “fixture role,” and
  translated-snapshot metadata.
- The README, workflow labels, artifact names, source URLs, and Pages path use
  legacy repository identities.
- `backup/` contains project-specific legacy FreeCAD/macro history and must not
  move upstream.
- `.agents/` and `AGENTS.md` are currently deleted while `.back_agents/` and
  `back_AGENTS.md` are untracked. `.claude/agents`, `.claude/skills`,
  `.codex/agents`, `.codex/skills`, `.opencode/agents`, `.opencode/skills`, and
  `CLAUDE.md` are consequently broken symlinks.
- The shared `python-cad-architect` role currently grants one agent authority over
  both project design and managed tooling, defeating the desired duty split.

Baseline commit at audit time: `21f828d31bd6b1563be20212acd811c4355ce40d`.
The worktree is dirty with user-owned agent changes and the new planning files.
Preserve all of it during implementation.

## 4. Feasibility review

| Change | Feasibility | Prerequisite or risk |
| --- | --- | --- |
| Installed package imports | High | A tested `python-cad-tools` wheel with public typed modules |
| Remove `.tools`/launchers | High | CLI/API parity and clean-wheel Benge build first |
| Keep Benge tests downstream | High | Replace private imports and expand test layers |
| Format-neutral annotations | High after package API | Requires package drawing primitives/styles/provider contract |
| Equivalent SVG/DXF/PDF annotations | High | Package renderers need compound callout/marker/table support and semantic tests |
| Cross-run byte determinism | Conditional on tooling spike | STEP/IFC/GLB/SVG/DXF/PDF metadata and ordering must be canonical upstream; no downstream semantic-only waiver |
| Package viewer delivery | High | Model-free static assets in wheel; Python site builder; no downstream Node |
| Exact registry dependency | High | Registry authority and binary dependency availability on claimed platforms |
| Repository identity migration | High | Update metadata/filenames/tests/Pages deliberately; preserve element IDs |
| Remove `backup/` from active head | High | Create immutable tag/archive and verify recovery first |
| Reduce normal agent read scope | High | Minimal tree and narrow local AGENTS rules |
| In-process project-code sandbox | Not feasible | Treat project source as trusted; do not claim filesystem sandboxing |

The final wheel has heavy compiled/transitive CAD dependencies. Clean installs
must pass on every advertised Python/OS combination. A private registry must
proxy/mirror public dependencies or CI must be configured with an authorized
secondary index. The dependency string remains `python-cad-tools==0.1.0`; index
URLs and credentials never appear in source.

## 5. Canonical naming and identity migration

### 5.1 Infrastructure identity

| Concern | Required value |
| --- | --- |
| GitHub repository slug | `benge-property-cad` |
| PEP 621 project name | `benge-property-cad` |
| Human project title | `Benge Property CAD` |
| Tooling distribution | `python-cad-tools` |
| Tooling import | `python_cad_tools` |
| Tooling command | `python-cad` |
| Configuration table | `[tool.python-cad]` |
| Pages base path | `/benge-property-cad/` |
| CI artifact name | `benge-property-cad-generated` |
| Test directory | `tests/` |
| Design agent role | `benge-design-maintainer` |
| Read-only review role | `benge-artifact-reviewer` |

### 5.2 CAD/model identity

Perform one explicit, tested migration:

| Current | Required target |
| --- | --- |
| `PROJECT_NAME = "BengeComplexFunctional"` | Separate display name `Benge Property` and artifact stem `BengeProperty` |
| Model ID `functional.benge_complex` | `benge.property` |
| Source module `functional.benge_complex.model` | `model` |
| Tag `complex-functional` | `benge-property` |
| Fixture/snapshot/source-commit metadata | Real project authority metadata plus build-provided Git revision |
| Output `BengeComplexFunctional.*` | `BengeProperty.*` |

Existing element IDs beginning with `complex.` remain unchanged in this
migration. They are treated as stable opaque identifiers even though their prefix
is historical. Renaming 236 element IDs would be a separate design migration
requiring an explicit mapping and downstream-consumer review. Add a test that
proves the pre-split element-ID set is preserved exactly while model/artifact
identity changes intentionally.

Serialized identifier policy is explicit:

| Class | Migration rule |
| --- | --- |
| 236 element IDs `complex.*` | MUST remain byte-for-byte identical |
| Material IDs `material.complex.*` | MUST remain byte-for-byte identical |
| IFC product GlobalIds and element-derived material/property relationship IDs | MUST remain because they derive from preserved element IDs |
| Model ID/name/artifact stem/source module/project tag | MUST migrate exactly as the table above |
| IFC project/site/building/storey and aggregate relationship GlobalIds | MUST migrate once because their deterministic inputs change from `functional.benge_complex.*` to `benge.property.*`; old/new inputs and observed IDs are recorded in the golden |
| Output paths/filenames | MUST migrate from `BengeComplexFunctional` to `BengeProperty` expectations |
| Annotation IDs | New canonical IDs are introduced in Section 11.3 and MUST remain thereafter |
| Run timestamp/host, staging names, lock ownership, viewer cache entries | MAY regenerate and are marked volatile/non-authoritative |

The golden contract stores the MUST-remain sets and intentional old-to-new
model/spatial identity mapping. An executor may not decide these classes ad hoc.

Legacy names may remain only in immutable history and migration documents,
including `REPO_SPLIT_PROMPT_PLAN.md` and this audit section. Active source,
configuration, tests, CI, current docs, manifests, and generated names must pass
an allowlisted legacy-name scan.

## 6. Strict ownership boundary

### 6.1 This repository owns

- property dimensions, layouts, material choices, and project design parameters;
- all geometry composition and stable semantic element IDs;
- project IFC mapping/exclusion intent and project metadata;
- section/elevation/schedule annotation content and locations;
- Benge-specific unit, model, annotation, build, artifact, and site expectations;
- exact tool-package pin and four reproducible native development locks;
- project README, warnings, agent policy, CI, Pages deployment, and ignored outputs;
- generated artifacts only as disposable local/CI products.

### 6.2 `python-cad-tools` owns

- units/types, geometry helpers, design model contracts, build contexts;
- config loading, CLI, locking, staging, recoverable transactional promotion, and clean behavior;
- neutral drawing primitives/styles and all SVG/DXF/PDF rendering;
- STEP/IFC/GLB/drawing/quantity exporters and validators;
- manifest schemas, hashes, artifact verification APIs;
- viewer source, compiled model-free shell, site preparation, and serving;
- package release/dependency policy and generic tests.

### 6.3 Prohibited coupling

- No `.tools`, `build.py`, `start.sh`, `viewer/`, submodule, subtree, copied
  package file, or copied framework test remains in the final active tree.
- No editable, relative path, sibling checkout, direct VCS, or unpinned tooling
  dependency is permitted in final `pyproject.toml` or any lock.
- No `PYTHONPATH`, pytest `pythonpath`, mypy path to tooling source, or import from
  an exporter/private module is permitted.
- Project source never patches site-packages or reaches into the tooling repository.
- Tool releases never overwrite project tests, workflows, docs, locks, or agents.
- Generated output is never edited as design authority.

## 7. Separation of duties for agents

| Agent role | Writable scope | Required behavior | Forbidden behavior |
| --- | --- | --- | --- |
| `benge-design-maintainer` | `config.py`, `model.py`, `drawing_annotations.py`, `tests/` | Uses public installed API, preserves IDs, builds and runs full affected matrix | Reads/patches tooling source/site-packages or edits generated bytes/operations files |
| `benge-project-operations` | `pyproject.toml`, locks, README, AGENTS/agent integration, `.github`, `.gitignore`, migration docs | Dependency/identity/CI/Pages/governance maintenance and exact package upgrades | Changes CAD geometry/IDs or tooling implementation |
| `benge-artifact-reviewer` | None | Reviews generated geometry/manifests/drawings/site and reports domain issues | Reads or edits source; certifies professional engineering/code compliance |
| `cad-compatibility-verifier` | None in source; temporary environments/reports only | Installs exact artifact, runs complete cross-repo and browser matrix | Fixes failures in the same verification run or asks user to test |
| `save` (orthogonal role) | Already verified diff only | Persists exact approved changes | Implements, inspects, tests, or weakens verification |

The old shared `python-cad-architect` identity is retired. The tooling repository
has separate tooling/viewer/release roles and no authority here.

Normal design-agent read scope is intentionally small:

1. Read `AGENTS.md`.
2. Read only the affected design source file(s) and corresponding test(s).
3. Read `pyproject.toml` only for package contract/dependency tasks.
4. Read generated manifests/artifacts only for validation or domain review.
5. Do not inspect locks, CI, migration documents, or package internals unless the
   request specifically concerns them.

## 8. Required final active tree and file descriptions

```text
benge-property-cad/
├── .github/workflows/
│   ├── ci.yml
│   └── pages.yml
├── .gitignore
├── AGENTS.md
├── .agents/
│   ├── agents/{benge-design-maintainer,benge-project-operations,benge-artifact-reviewer,cad-compatibility-verifier,save}.md
│   └── skills/<same-id>/{SKILL.md,agents/openai.yaml}
├── .claude/{agents,skills} -> ../.agents/...
├── .codex/{agents,skills} -> ../.agents/...
├── .opencode/{agents,skills} -> ../.agents/...
├── .opencode/{commands,tools}/
├── CLAUDE.md -> AGENTS.md
├── opencode.jsonc
├── README.md
├── pyproject.toml
├── requirements/
│   └── locks/
│       ├── dev-py312-ubuntu-x86_64.lock
│       ├── dev-py313-ubuntu-x86_64.lock
│       ├── dev-py312-macos-arm64.lock
│       └── dev-py313-macos-arm64.lock
├── config.py
├── model.py
├── drawing_annotations.py
├── tests/
│   ├── fixtures/
│   │   └── model_contract_v1.json
│   ├── test_config_contract.py
│   ├── test_model_contract.py
│   ├── test_drawing_annotations.py
│   ├── test_build_end_to_end.py
│   └── test_viewer_e2e.py
├── generated/
│   └── .gitkeep
├── REPO_SPLIT_PROMPT_PLAN.md
└── BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md
```

These agent/tool integration files are retained and rewritten as project-specific
governance. Every symlink is tested. Broken links, `.back_agents`,
`back_AGENTS.md`, copied tooling roles, caches, Node modules, and backup agent
trees are not part of the target.

Exact link targets are identical for `.claude`, `.codex`, and `.opencode`:
`agents -> ../.agents/agents` and `skills -> ../.agents/skills` from each tool
directory; root `CLAUDE.md -> AGENTS.md`. No target is absolute or resolves
outside the repository, and CI checks `readlink` plus resolved existence/type.

| Path | Owner | Required description |
| --- | --- | --- |
| `config.py` | `benge-design-maintainer` | Typed property dimensions/materials/identity/openings/annotation facts and tested invariants |
| `model.py` | `benge-design-maintainer` | Complete property `DesignModel`, geometry/materials/metadata/stable IDs/IFC intent; no lifecycle side effects |
| `drawing_annotations.py` | `benge-design-maintainer` | Pure neutral `build_annotations` provider with the four canonical annotation IDs |
| `tests/fixtures/model_contract_v1.json` | `benge-design-maintainer` | Reviewed pre-split ID/material/bounds/quantity golden and intentional identity migration map |
| `tests/test_config_contract.py` | `benge-design-maintainer` | Parameter units/ranges/relationships and single-source annotation facts |
| `tests/test_model_contract.py` | `benge-design-maintainer` | In-memory identity, exact golden reconciliation, geometry/material/IFC validation |
| `tests/test_drawing_annotations.py` | `benge-design-maintainer` | Provider IDs/cardinality/content and renderer annotation-manifest reconciliation |
| `tests/test_build_end_to_end.py` | `benge-design-maintainer` | Public API/CLI success, independent all-format parsing/hashes, stable determinism, provider rollback |
| `tests/test_viewer_e2e.py` | `benge-design-maintainer`; verifier executes read-only | Python Playwright Benge success flow, health/readiness, non-root base, known selection/downloads, failure artifacts |
| `pyproject.toml`, `requirements/locks/*.lock` | `benge-project-operations` | Project identity, exact pin, strict config, test tools, four native reproducible hashed matrix locks |
| `AGENTS.md`, `.agents/**`, tool views | `benge-project-operations` | Narrow project roles/public boundary; valid links and no upstream authority |
| `README.md` | `benge-project-operations` | Property purpose, conceptual limitations, clean commands, package upgrade procedure |
| `.github/workflows/ci.yml`, `pages.yml` | `benge-project-operations` | Clean package CI and thin package-driven deployment |
| `.gitignore`, `generated/.gitkeep` | `benge-project-operations` | Ignore disposable state; builder stages/hashes the zero-byte anchor on every build and `clean` preserves/recreates it |
| migration plan files | `benge-project-operations` | Historical planning; excluded from active-name scan and normal agent context |

## 9. Current-file disposition

| Current path | Final action and owner |
| --- | --- |
| `config.py`, `model.py` | Retain here; migrate imports/identity/metadata intentionally |
| `drawing_annotations.py` | Retain intent here; rewrite against public neutral drawing API |
| `project_tests/test_benge_project.py` | Split/rename into `tests/`; retain all Benge assertions and strengthen them |
| `.tools/**` | Delete after candidate-wheel tests pass with `.tools` physically absent |
| root `build.py` | Delete after `python-cad build` and public API parity pass |
| `start.sh` | Delete after installed `prepare-site`/`serve` and browser gates pass |
| `viewer/**` | Delete downstream after package viewer gate; source/tests remain upstream only |
| `.github/workflows/build-design.yml` | Rewrite/rename to project-owned `ci.yml` |
| `.github/workflows/pages.yml` | Retain ownership but rewrite to package commands and no Node/viewer source |
| `README.md`, `pyproject.toml`, `.gitignore`, `AGENTS.md` | Keep independent Benge versions; never treat as files moved upstream |
| `backup/**` | Tag/archive and remove from active head; never copy upstream |
| `.back_agents/**`, `back_AGENTS.md`, deleted `.agents/**`, broken links | `benge-project-operations` reconciles into the exact target agent tree, tests every link, removes backups |
| `opencode.jsonc`, `.opencode/{commands,tools}`, `.claude/**`, `.codex/**`, `CLAUDE.md` | Retain only the rewritten exact target governance/link paths; remove cross-boundary permissions |
| `.opencode/node_modules`, Python/test caches, generated artifacts | Ignore/remove as disposable local state |
| `REPO_SPLIT_PROMPT_PLAN.md` | Preserve unchanged as the original audit input/migration history |

Before removal, the AI must tag current HEAD and separately capture dirty/untracked
state, because a tag cannot contain it. Create a full-worktree archive outside
the repository, `git diff --binary`, untracked-file manifest, and SHA-256; extract
and compare it in a temporary directory. After reconciliation, an authorized
preservation commit/branch may supersede the external archive. Legacy files do
not remain in the active head merely for recoverability.

## 10. Dependency and project configuration contract

Target `pyproject.toml` intent:

```toml
[project]
name = "benge-property-cad"
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = [
  "python-cad-tools==0.1.0",
]

[tool.python-cad]
schema-version = 1
config = "config"
model = "model:build_model"
drawing-annotations = "drawing_annotations:build_annotations"
source-inputs = ["pyproject.toml", "config.py", "model.py", "drawing_annotations.py"]
output-directory = "generated"
default-formats = ["step", "ifc", "glb", "drawings", "quantities"]

[tool.setuptools]
py-modules = []
```

Rules:

- The release-candidate branch may temporarily pin `0.1.0rc1` from a registry
  or install an exact local wheel in an isolated test command. Final active
  metadata and all four native locks pin `0.1.0` from the selected registry.
- No private index URL, token, local path, sibling path, editable flag, or VCS
  reference is committed. CI uses standard authorized pip index configuration.
- Each lock includes exact transitive versions and hashes and is regenerated only
  for an explicit dependency task.
- Run documented `python_cad_tools.artifacts` verification and also independently
  recompute inventory/size/SHA with stdlib plus parse STEP/IFC/GLB/SVG/DXF/PDF
  using direct libraries declared in the development group. Package verification
  is not its own independent oracle; never rely accidentally on transitive imports.
- Remove pytest `pythonpath=[".tools", "."]` and mypy `mypy_path=[".tools"]`.
- Mypy covers `config.py`, `model.py`, `drawing_annotations.py`, and `tests/`.
- Do not globally ignore missing package imports; the wheel must ship `py.typed`.
- The declared source-input list is authoritative and path-safe. Any future
  project component/data module is added explicitly; the build fails if a loaded
  project-root source input is undeclared.

This is a source-run application repository, not a publishable/importable Benge
library. Configure setuptools with no packages or `py-modules` so flat
`config.py` and `model.py` are not accidentally distributed. `pip install .` is
not the setup command. Development dependencies are the `dev` optional group in
`pyproject.toml`: `pytest`, `ruff`, `mypy`, `pip-tools`, Python `playwright`,
`build123d` for STEP reload, `ifcopenshell` for IFC, `trimesh` for GLB,
`ezdxf` for DXF, and `pypdf` for PDF; stdlib ElementTree parses SVG. Supported
version ranges align with the tool package. One universal lock is not assumed:
the four Section 8 locks cover CPython 3.12/3.13 on Ubuntu x86_64 and macOS
arm64, and each records its exact native resolution/hashes.

The reproducibility mechanism is `pip-tools`. Each lock is generated natively in
its named cell with the same pinned pip-tools version. Its header records Python
full version, OS, architecture, pip, and pip-tools versions plus these commands,
where `$LOCK_PATH` is the matching matrix file:

```text
python -m piptools compile --extra dev --generate-hashes --resolver=backtracking \
  --output-file $LOCK_PATH pyproject.toml
python -m pip install --require-hashes -r $LOCK_PATH
python -m pip check
python -m playwright install chromium
```

One reviewed dependency change uses a protected manual `lock-maintenance` job in
`ci.yml` to regenerate all four native locks together. Ordinary CI never
regenerates them; each job installs only its matching lock and
records that lock's SHA-256. A new platform/architecture is unsupported until it
has its own native lock and passing matrix.

Before a candidate exists in the registry, the only permitted exception is a
checksum-verified, ephemeral wheel source outside the repository. The verifier
places only the exact frozen T6a or T8 wheel in a temporary directory, verifies
its handoff SHA-256, converts that directory to an absolute `file:` URI, and in
each native cell performs this resolution/download/offline-install sequence:

```text
PIP_FIND_LINKS=$CANDIDATE_WHEEL_DIR_URI PIP_NO_CACHE_DIR=1 \
  python -m piptools compile --extra dev --generate-hashes --resolver=backtracking \
  --output-file $LOCK_PATH pyproject.toml
PIP_FIND_LINKS=$CANDIDATE_WHEEL_DIR_URI PIP_NO_CACHE_DIR=1 \
  python -m pip download --require-hashes --only-binary=:all: \
  --requirement $LOCK_PATH --dest $WHEELHOUSE
PIP_NO_INDEX=1 PIP_FIND_LINKS=$WHEELHOUSE_URI PIP_NO_CACHE_DIR=1 \
  python -m pip install --require-hashes --only-binary=:all: \
  --requirement $LOCK_PATH
```

The authorized index is enabled only during compile/download so transitive
dependencies can resolve. Immediately after compile, a mechanical lock parser
requires the `python-cad-tools` stanza to contain the exact candidate version and
exactly the frozen wheel SHA-256—no additional tool hash—so index precedence can
never substitute a same-name/version archive. After download, the verifier
requires exactly one normalized `python-cad-tools` archive in the wheelhouse with
that filename/hash and checks every wheelhouse file against an allowed lock hash;
the actual installation is then index-disabled. Absence of a binary wheel for a
claimed cell blocks that platform. The sdist is checksum-verified and exercised
by the tooling sdist-to-wheel gate but is not placed in this wheel-only directory.
The generated lock may contain only normalized distribution names, exact
versions, markers, and hashes: it must contain no `file:`, absolute/relative
candidate path, `--find-links`, editable, or VCS source. A mechanical scan proves
that condition before commit; the candidate directory and wheelhouse are removed
after evidence is captured.
After publication, unset `PIP_FIND_LINKS`, regenerate from the registry with
cache disabled, require the downloaded wheel/sdist hashes to match the certified
handoff, and rerun the full matrix. This procedure is identical for the local
`0.1.0rc1` gate and B9's prepublication `0.1.0` gate.

Ubuntu browser CI uses Playwright's `--with-deps chromium` setup; macOS uses
`chromium`. Lock generation is an explicit dependency-maintenance task and never
runs implicitly in ordinary CI.

The project documents and CI use one exact installed command contract:

```text
python-cad validate --project-root PATH [--format FORMAT ...]
python-cad build --project-root PATH [--format FORMAT ...]
python-cad verify --project-root PATH
python-cad clean --project-root PATH
python-cad prepare-site --project-root PATH --destination PATH --base-path PATH
python-cad serve --project-root PATH --host 127.0.0.1 --port PORT [--build]
```

`serve` verifies existing output by default; `--build` is explicit. The only
project-specific public environment setting is optional
`PYTHON_CAD_PROJECT_ROOT`; logging may use `PYTHON_CAD_LOG_LEVEL`. Standard
`NO_COLOR`, `SOURCE_DATE_EPOCH`, and pip index settings remain standard. Host,
port, output, destination, formats, and base path are CLI/TOML values, not custom
environment variables.

Expected exit codes are part of the package contract and project tests: `0`
success, `1` unexpected internal error, `2` usage/configuration, `3` model or
neutral-annotation validation, `4` dependency/export/build failure, `5`
schema/integrity verification, `6` unsafe path/active lock/recovery refusal,
`7` site/server failure, and `130` clean interrupt shutdown.

The project expects the package's exact initial JSON contract:

| File/document | Required schema identity |
| --- | --- |
| `generated/manifests/design-manifest.json` | `urn:python-cad-tools:schema:design-manifest:1` |
| `generated/manifests/build-manifest.json` | `urn:python-cad-tools:schema:build-manifest:1` |
| `generated/manifests/run-metadata.json` | `urn:python-cad-tools:schema:run-metadata:1` |
| `generated/glb/manifest.json` | `urn:python-cad-tools:schema:glb-manifest:1` |
| `generated/step/validation.json` | `urn:python-cad-tools:schema:step-validation:1` |
| `generated/ifc/validation.json` | `urn:python-cad-tools:schema:ifc-validation:1` |
| `generated/quantities/quantities.json` | `urn:python-cad-tools:schema:quantities:1` |
| `generated/drawings/annotation-manifest.json` | `urn:python-cad-tools:schema:drawing-annotations:1` |
| prepared-site `download-manifest.json` | `urn:python-cad-tools:schema:download-manifest:2` |
| prepared-site `site-metadata.json` | `urn:python-cad-tools:schema:site-metadata:1` |
| packaged `build-info.json` | `urn:python-cad-tools:schema:package-build-info:1` |

All fields are snake_case. The legacy `design-elements.json` name becomes
`design-manifest.json`. The download manifest uses schema version 2 because the
old viewer already labeled a different camelCase format as version 1. Package
version and document schema versions are independent.
Quantities v1 is an object envelope with `records`; it is not the legacy
top-level array. Project loaders/tests and the viewer consume `records`.

The exact supported import paths used here are:

```python
from python_cad_tools.build import (
    BuildOptions, BuildResult, ValidationOptions, ValidationReport,
    build_project, validate_project,
)
from python_cad_tools.context import BuildContext, DrawingContext
from python_cad_tools.elements import (
    DesignElement, DesignModel, Dimensions, IfcMapping, MaterialSpec, Placement,
)
from python_cad_tools.geometry import box, cylinder_between, prism_between, sloped_pool
from python_cad_tools.units import FOOT, INCH, MM, Length, mm, to_mm
from python_cad_tools.drawings import (
    DrawingAnnotationSet, ElevationMarker, SectionCallout, SheetAnnotations,
    Table, TableRow,
)
from python_cad_tools.artifacts import get_package_build_info, verify_build_output
```

`DesignModel` has distinct `id`, human `name`, and validated `artifact_stem`.
`BuildOptions`/`BuildResult`, `ValidationOptions`/`ValidationReport`, drawing
context/catalog/coordinates, annotation compound types, artifact records/hashes,
public errors, and numeric exit codes are the exact v1 definitions in the tooling
plan; downstream code does not choose an “equivalent” type or alternate module path.

## 11. Source refactor contract

### 11.1 `config.py`

- Rename live display/artifact identity to `Benge Property`/`BengeProperty`.
- Preserve typed unit values from installed `python_cad_tools.units`.
- Add any currently duplicated design facts, including sliding-door height,
  section cut position/view direction, elevation marker positions/directions/sheet
  references, schedule mark/type/bounds-relative placement, and other project
  annotation inputs.
- Keep only property-specific values. Renderer styles/default sheet mechanics
  belong upstream.
- Add explicit invariants in tests: positive dimensions, deck/stair relationships,
  pool depths, valid RGB ranges, opening dimensions, and marker/sheet references.

### 11.2 `model.py`

- Remove `import drawing_annotations` and every lifecycle side effect.
- Import only documented `python_cad_tools` modules/symbols.
- Set model ID `benge.property`, display `Benge Property`, artifact stem
  `BengeProperty`, source module `model`, and tag `benge-property` using the
  package's supported fields.
- Replace fixture/snapshot metadata with real design-authority metadata. Git
  revision/dirty state comes from the build context/manifest, not a hardcoded commit.
- Preserve the complete existing `complex.*` element-ID set and intentional IFC
  mappings unless a separate design change explicitly alters them.
- Derive door geometry and annotation facts from the same config constants.
- Keep generated files out of source authority.

### 11.3 `drawing_annotations.py`

Required public signature:

```python
def build_annotations(context: DrawingContext) -> DrawingAnnotationSet:
    ...
```

Required behavior:

- return provider ID `benge.property.annotations`, stable annotation IDs, and
  format-neutral sheet primitives;
- reference sheets/views by typed ID, never output filename;
- derive all dimensions/labels/positions from config/model metadata;
- express the plan section callout, A-201/A-202 elevation markers, and opening
  schedule once;
- let package renderers produce equivalent SVG, DXF, and PDF semantics;
- raise a typed error for invalid required context/sheet/annotation data;
- have no globals tied to `generated/`, file writes, XML parsing, `ezdxf`,
  subprocess, `sys.argv`, `atexit`, stdout-driven success, or standalone rebuild;
- be deterministic and semantically idempotent.

The v1 project IDs/content are exact:

| Annotation ID | Sheet | Required normalized content |
| --- | --- | --- |
| `benge.annotation.section.a301` | `A-101` | one section cut at configured X `4000 mm`, from plan `min_y` to `max_y`, `view_direction="right"`, two right-pointing directional ends, and two visible `A-301` labels referencing section sheet `A-301` |
| `benge.annotation.elevation.a201` | `A-101` | one configured marker at `(5500 mm, 1600 mm)`, direction `down`, reference `A-201` |
| `benge.annotation.elevation.a202` | `A-101` | one configured marker at `(13500 mm, -3500 mm)`, direction `left`, reference `A-202` |
| `benge.annotation.schedule.openings` | `A-101` | position `(min_x + 0.04 * (max_x - min_x), min_y + 1400 mm)`, title `DOOR & WINDOW SCHEDULE`, columns `("Opening", "Type", "Width", "Height")`, and `TableRow(id="SD-01", cells=("SD-01", "Sliding Glass Door", "6'-0\" (1,829 mm)", "7'-0\" (2,134 mm)"))`; numeric cells are formatted from configured 6-by-7-foot values, never independent literals |

Compound renderer entities use deterministic child suffixes beneath the parent
ID. The package's annotation manifest records parent/child cardinality, sheet,
normalized labels/table rows, SVG `data-annotation-id`, DXF XDATA identity, and
PDF page/text presence. Current red/black details become package style tokens;
the project does not hardcode renderer colors/lineweights.

The package owns annotation visual styles and artifact validation. The project
owns the content and exact property positions.

## 12. Complete Benge test design

All tests use temporary output directories. No test relies on another test or
on repository-root generated state.

### 12.1 Config contract

- all length parameters have expected dimensions and positive/allowed values;
- deck elevations/thicknesses, joist/beam/post sizes, roof relationships, stair
  riser/tread values, pool shallow/deep order, and clearances are valid;
- RGB tuples have three finite values in `[0, 1]`;
- sliding door width/height and annotation schedule values have one source;
- annotation coordinates are in intended property bounds and sheet references exist;
- human display name and safe artifact stem are exact.

### 12.2 In-memory model contract

- model ID/name/artifact stem/source metadata use canonical identity;
- no fatal package validation issues;
- exactly the intended 236-element baseline unless a design change explicitly
  updates the reviewed `model_contract_v1.json` golden;
- every pre-split `complex.*` element ID from that golden is present exactly once,
  with no silent rename;
- required house, fireplace, hot tub, kitchen, pool, roof, stair, and platform IDs exist;
- categories, material IDs/densities, colors, placements, dimensions, tags,
  parentage, visibility, and export format sets obey project expectations;
- every physical element has intentional IFC mapping or exclusion;
- model bounds and selected component bounds match tested design intent;
- source/model import registers no `atexit` behavior and writes no files.

### 12.3 Annotation contract

- provider returns one deterministic set with stable IDs;
- A-101 contains the exact four IDs/cardinalities/content in Section 11.3;
- schedule values equal config/model opening values;
- non-target sheets remain free of plan-only content;
- all annotation bounds fit or intentionally expand the viewport;
- invalid/missing sheet or malformed project data fails strictly;
- builds with the indivisible `drawings` bundle selected or omitted behave
  correctly; SVG/DXF/PDF are not independently selectable v1 subformats;
- rendered SVG has expected semantic data attributes and parses;
- rendered DXF has expected annotation layer/entities and passes audit;
- rendered PDF and the annotation sidecar expose equivalent callout/marker/
  schedule text on the correct page, reconciled to SVG attributes and DXF XDATA;
- one build contains no duplicate semantic annotation IDs/entities.

### 12.4 Programmatic end-to-end build

- first call documented `validate_project(ValidationOptions(...))`, assert a
  successful `ValidationReport`, and prove it creates/touches no output;
- then call documented `build_project(BuildOptions(...))` and inspect its
  `BuildResult` against a copied temporary project;
- annotations are complete before the function returns;
- selected formats and full default formats behave as documented;
- build result paths point only to promoted final output;
- no import from exporter/private modules occurs.

### 12.5 CLI end-to-end

- run from repository root and from a copied path containing spaces;
- exercise default build, repeated `--format`, validate, verify, clean, prepare-site,
  serve, and one Benge-specific invalid annotation/config case;
- assert stable exit codes and useful messages;
- verify no root build launcher or sibling source is used. Generic CLI/path/lock
  fault matrices remain exclusively in `python-cad-tools` tests.

### 12.6 Final artifact reconciliation

- validate build/design/run schema IDs/versions and exact installed producer version;
- verify final validation status and expected model count;
- every manifest-listed regular file exists and matches recorded size/SHA-256;
- zero-byte `generated/.gitkeep` is an explicit nonvolatile inventory entry, and
  clean/build never leave its tracked deletion;
- artifact inventory follows the schema's explicit self-hash/volatile exclusions;
- whole-run `artifact_set_hash`, cross-run `stable_artifact_set_hash`, design
  semantic hash, source-set hash, selected formats, source revision, exact
  configured provider import string/provider ID, and canonical record ordering
  independently reproduce the package schema;
- STEP reload has expected solids/bounds/units;
- IFC4 parses/validates and reconciles stable IDs/GlobalIds;
- GLB nodes/extras/stable IDs/bounds reconcile;
- `quantities.json`, `quantities.csv`, `materials.csv`, and `summary.md` exist,
  parse as applicable, and quantities cover physical IDs with positive exact
  volumes and expected totals;
- four SVG and four DXF sheets plus one four-page PDF exist under `BengeProperty` names;
- the drawing annotation manifest reconciles all four canonical annotation IDs;
- SVG, DXF, and PDF parse and contain conceptual disclaimer plus equivalent annotations;
- cross-format physical ID sets and bounds agree where the format represents them.

### 12.7 Failure rollback/recovery and determinism

- begin with a known-good generated tree and record its recursive hash;
- use a disposable Benge provider fixture with a required annotation failure;
- failed command is nonzero, prior tree is byte-for-byte unchanged, and no staging/
  unsafe backup/journal remains; no lock is held afterward, while a documented
  persistent lock file is allowed;
- two clean builds have identical stable IDs, design semantic hash, artifact path
  set, and `stable_artifact_set_hash`; each build's whole-run
  `artifact_set_hash` is verified but may differ with volatile run metadata;
- compare the exact bytes and SHA-256 of every inventoried nonvolatile artifact,
  including STEP/IFC/GLB/SVG/DXF/PDF/JSON and `.gitkeep`, separately from the
  volatile `run-metadata.json` record; `build-manifest.json` is the documented
  self-excluded envelope, so compare its canonical stable projection after
  removing exactly its volatile record and whole-run `artifact_set_hash`. DXF
  handle/header metadata and all other format metadata must already be
  canonicalized by the package. A stable-byte mismatch is a release failure,
  not permission to weaken this test to semantic equivalence;
- generic exporter failures and crash points at each promotion rename/journal
  state remain tooling-owned tests.

### 12.8 Packaged viewer/site

- `python-cad prepare-site` runs with downstream `viewer/` absent and Node unavailable;
- every copied artifact was manifest-authorized and hash-verified;
- independently validate download-manifest v2/site-metadata v1 fields, canonical
  ordering, `artifacts/<source_path>` mapping, MIME/size/SHA, shell/artifact
  collision absence, and complete managed inventory; every build artifact record
  is copied or is exactly the allowed run-metadata/`.gitkeep` omission;
- it writes `site-metadata.json` with `design_build_hash` exactly equal to the
  build manifest's `stable_artifact_set_hash`, and the viewer, health endpoint,
  cache, report, and deployed smoke test all expose that same value;
- an empty temporary site destination succeeds, while an unmarked nonempty
  destination and symlink destination fail without changing any existing byte;
  the exhaustive root/home/project/output/foreign-marker/path-race matrix remains
  tooling-owned;
- site works at `/benge-property-cad/`, not only `/`;
- `python-cad serve --port 0` is started and terminated automatically; the test
  parses the documented `READY <url>` line and verifies `/healthz` reports the
  installed tool version and current `design_build_hash`; it terminates with
  SIGINT, accepts documented exit `130`, and verifies ephemeral cleanup;
- HTTP checks cover health, HTML, JS/CSS, download manifest, GLB, one drawing,
  and one downloadable artifact with expected MIME/hash;
- Playwright/Chromium loads with no page/console/network errors, selects a known
  stable ID, displays metadata/quantities, switches units, exercises visibility/
  camera/download controls, and observes the current `design_build_hash`;
- the harness uses package-stable `data-testid` selectors for model-loaded,
  canvas, properties, units, downloads, and `design_build_hash`; it waits at most 30 seconds;
- Python Playwright, its Chromium install, trace, screenshot, console log, and
  network log are owned by `tests/test_viewer_e2e.py` and matching dev lock. “No Node”
  means no downstream Node/npm/Vite build; Playwright's managed driver/browser is
  an explicit test dependency;
- generic same-URL service-worker refresh and offline failure injection remain
  tooling tests; this downstream test verifies one real Benge success bundle and
  the non-root Pages base path.

## 13. Boundary and clean-environment gates

The AI verifier must run mechanical boundary checks excluding Git history,
migration plans, and explicitly archived migration reports:

- no active `.tools`, root `build.py`, `start.sh`, `viewer/`, `backup/`, or broken symlink;
- no `benge_freecad_project`, `freecad_macro_project_template`,
  `python-cad-project`, `BengeComplexFunctional`, `functional.benge_complex`,
  `complex-functional`, `BENGE_FUNCTIONAL_OUTPUT`, or
  `python-cad-artifact-viewer` in active source/config/tests/docs/CI;
- no `.tools` Python path, editable/path/VCS dependency, sibling import, private
  exporter import, or custom registry credential variable;
- no generated artifacts except `.gitkeep` are tracked;
- no framework source or viewer source is copied into the project;
- all remaining agent/tool links resolve and grant only project-appropriate scope.

Clean-install verification:

1. Create a fresh archive/clone of this repository alone in a path with spaces.
2. Create clean Python 3.12 and 3.13 environments with caches disabled.
3. Install the exact matching Python/OS/architecture lock from the authorized
   registry; record its SHA-256 and run `pip check`.
4. Assert `importlib.metadata.version("python-cad-tools")` equals the project pin.
5. From outside both repositories, assert `python_cad_tools.__file__` is under
   that environment's `site-packages`.
6. Run static checks, all tests, complete build/verify/site/browser matrix.
7. Repeat supported operating-system CI cells.

No sibling tooling checkout may exist on `sys.path` during this gate.

## 14. CI and Pages workflows

### 14.1 `.github/workflows/ci.yml`

Required job IDs are stable workflow interfaces:

1. `locked-install` is the four-cell Python 3.12/3.13, Ubuntu x86_64/macOS
   arm64 matrix; each cell installs only its matching hashed lock and runs
   `pip check`.
2. `static-analysis` runs Ruff lint/format and mypy over all source/tests.
3. `model-annotation` runs config, model, golden-ID, and annotation tests.
4. `full-build-verify` runs all-format build plus independent artifact/schema/
   hash reconciliation on both Ubuntu Python versions and the claimed macOS cells.
5. `determinism-recovery` runs stable-byte, provider failure, and transactional
   rollback/recovery gates.
6. `site-browser-e2e` runs Node-free site preparation, HTTP, and Playwright.
7. `boundary-governance` runs legacy-name, dependency-boundary, wheel provenance,
   ignored-output, and broken-link checks.
8. `compatibility-report` depends on all preceding jobs, verifies their exact
   design commit/tool wheel SHA/native-lock SHA evidence, and uploads generated
   artifacts, prepared site, JUnit/logs, and the signed/attested report.
9. `required-gate` is a no-skip aggregate that succeeds only if every required
   matrix cell and `compatibility-report` succeeded for the same commit and wheel
   hash. Branch protection and Pages require this exact job.

If Windows is advertised, add a passing Windows clean-install/build/verify lane
first. Do not claim untested platform support.

All workflows declare least-privilege permissions, pin third-party actions to
reviewed full commit SHAs, use protected environments for registry/Pages writes,
and never execute untrusted pull-request code with deployment credentials.

### 14.2 `.github/workflows/pages.yml`

The project-owned workflow triggers only from a successful default-branch
`ci.yml` run whose `workflow_run.head_repository.full_name == github.repository`;
fork/untrusted runs cannot reach deployment credentials. It verifies that
`required-gate` and all named jobs above belong to
the exact `workflow_run.head_sha`, and that the compatibility report's stable
tool wheel SHA and native-lock SHA match the files it will install. A rerun from
a different commit/candidate is forbidden. `actions/checkout` must use
`ref: ${{ github.event.workflow_run.head_sha }}` (never the moving branch name),
and the job must require `git rev-parse HEAD` to equal that event SHA before any
install, test, build, or deployment step.

Its fixed Ubuntu x86_64/Python 3.13 predeploy sequence is:

```text
PIP_NO_CACHE_DIR=1 python -m pip download --require-hashes \
  --only-binary=:all: \
  -r requirements/locks/dev-py313-ubuntu-x86_64.lock \
  --dest $WHEELHOUSE
printf '%s  %s\n' "$CERTIFIED_TOOL_WHEEL_SHA256" \
  "$WHEELHOUSE/$CERTIFIED_TOOL_WHEEL_FILE" | sha256sum --check -
PIP_NO_INDEX=1 PIP_FIND_LINKS=$WHEELHOUSE_URI PIP_NO_CACHE_DIR=1 \
  python -m pip install --require-hashes --only-binary=:all: \
  -r requirements/locks/dev-py313-ubuntu-x86_64.lock
python -m pip check
python -m playwright install --with-deps chromium
python -m ruff check config.py model.py drawing_annotations.py tests
python -m ruff format --check config.py model.py drawing_annotations.py tests
python -m mypy config.py model.py drawing_annotations.py tests
python -m pytest -q
python-cad validate --project-root .
python-cad clean --project-root .
python-cad build --project-root .
python-cad verify --project-root .
python-cad prepare-site --project-root . --destination $EMPTY_STAGING \
  --base-path /benge-property-cad/
python -m pytest -q tests/test_viewer_e2e.py \
  --prepared-site $EMPTY_STAGING --base-path /benge-property-cad/
```

The certified filename/SHA variables come only from the already verified
same-commit compatibility report. Before install, the workflow also rejects any
normalized duplicate `python-cad-tools` archive and any wheelhouse file whose
hash is absent from the lock; the index-disabled installation is therefore the
certified package, not merely a matching version string.

`test_viewer_e2e.py` must implement those two explicit pytest options and must
serve/stop the supplied site itself. The workflow then re-verifies the prepared
site inventory/hash, uploads/deploys only that directory, and in a separate
automated postdeploy job polls the Pages URL and verifies HTML, exact
`design_build_hash == stable_artifact_set_hash`, GLB hash, browser console/network
state, and a known selectable element. Any fixed command, required job, matrix
cell, hash check, or postdeploy check that is skipped/cancelled blocks deployment.
Only the deploy job receives `pages: write`/`id-token: write`; predeploy and
postdeploy verification retain read-only permissions except the protected Pages
API operation itself.

It must not install Node, build viewer source, access `.tools`, or invoke root launchers.

## 15. AI-generated compatibility report

The final JSON report must contain:

- `plan_contract`;
- tooling repository revision/dirty flag read from packaged `build-info.json`
  and cross-checked against release attestation;
- exact distribution name/version;
- tested wheel and sdist filenames and SHA-256 values;
- design repository revision and dirty flag;
- Python version, OS/platform, and relevant dependency versions;
- project config contract version;
- every emitted document schema ID/version;
- model/design semantic hash, whole-run `artifact_set_hash`, and cross-run
  `stable_artifact_set_hash`;
- site `design_build_hash` and proof it equals `stable_artifact_set_hash`;
- element count and stable-ID preservation result;
- annotation SVG/DXF/PDF checks;
- manifest inventory/size/hash reconciliation result;
- full command, exit code, duration, and status matrix;
- site base path, HTTP results, browser console/network/selection result;
- Pages URL/result when deployment authority exists;
- explicit list of unsupported optional features/platforms rather than silent skips.

The report is generated by automation and archived as a CI/release artifact. It
is not manually authored proof.

## 16. Ordered implementation phases and agent prompts

Cross-repository handshake order is fixed:

```text
T0 + B0 baselines
  -> coordinated R0 remote renames
  -> tooling T1-T5
  -> tooling T6a frozen generic-tested rc candidate
  -> B1-B6 migration
  -> B7 + tooling T6b joint local verification
  -> tooling T7 rc publication
  -> B8 registry-rc verification
  -> tooling T8 frozen stable candidate
  -> B9 prepublish stable verification
  -> tooling publishes the same stable hashes
  -> B9 registry-stable + Pages verification
  -> final joint report
```

This ordering is a contract; no agent may create a circular prerequisite.

### Phase B0 — Preserve design history and capture baseline

Prompt:

> Work only in the current Benge checkout. Preserve all uncommitted user changes,
> especially deleted/moved agent files and planning documents. Record HEAD,
> status, remotes, environment versions, current test/build results, current
> element IDs/count/bounds/quantity summaries/artifact paths, and the known final
> plan SVG/DXF hash mismatches. Tag HEAD, then create the checksum-verified
> full-worktree archive, binary diff, and untracked manifest specified in Section
> 9; test extraction. Generate and review
> `tests/fixtures/model_contract_v1.json` from the valid semantic baseline with
> sorted 236 element IDs, material IDs, selected bounds/quantity aggregates, and
> intentional identifier migration mapping. Do not reset, edit the tooling repo,
> or treat corrupted final hashes as a valid golden.

Gate: recoverable legacy baseline plus explicit semantic golden and known-defect record.

### Phase R0 — Coordinate the canonical repository remote

Prompt:

> After both repositories have verified baselines and rename authority is
> available, rename this GitHub repository to `benge-property-cad`, update
> `origin`, repository URLs, and the current Pages/repository settings, and verify
> the old remote redirect. Coordinate with `cad-tools-maintainer`, which
> independently renames its repository to `python-cad-tools`; do not edit that
> checkout. After active processes stop, rename/reclone the local directory to
> `benge-property-cad` and prove no configuration embeds the legacy absolute path.
> A compatibility workflow may accept an explicit legacy URL/commit
> during local development, but prerelease publication is blocked until both
> canonical remotes exist.

Gate: canonical Benge remote exists before package prerelease compatibility jobs.
Missing authorization is an external blocker, never a request for user testing.

### Phase B1 — Wait for and verify the candidate package

Prompt:

> Obtain the exact `python-cad-tools==0.1.0rc1` wheel/sdist frozen by tooling Phase
> T6a. In a disposable clean environment outside both source trees,
> inspect its hash/content, use the checksum-verified ephemeral wheel-only
> `PIP_FIND_LINKS` procedure in Section 10, install non-editably, run `pip check`,
> import public symbols/types, and build the package's generic fixture. Prove no
> candidate URI/path was serialized into any native lock. Do not begin project migration
> against an editable checkout or incomplete package.

Gate: immutable candidate artifact passes generic clean-install verification.

### Phase B2 — Enforce project identity and dependency boundary

Prompt:

> Rename active project metadata to `benge-property-cad`, add strict
> `[tool.python-cad]`, pin the exact candidate, create all four reproducible native locks, and
> remove all `.tools` path configuration. Each rc lock resolves through the exact
> B1 ephemeral wheel source and contains only names/versions/hashes, never its
> location. Update active README/CI/agent wording.
> Migrate live model/artifact identity to `benge.property`/`Benge Property`/
> `BengeProperty` while preserving every `complex.*` element ID. Remove stale
> fixture/source-commit metadata. Do not yet delete legacy files needed for a
> controlled parity comparison.

Gate: in-memory model test proves exact element-ID preservation and intentional identity changes.

### Phase B3 — Migrate model imports and annotations

Prompt:

> Change config/model imports to documented installed APIs, remove the annotation
> side-effect import, centralize duplicated door/annotation facts in config/model
> metadata, and rewrite `drawing_annotations.py` as pure
> `build_annotations(context)`. Express section, elevation, and schedule intent
> once and require equivalent SVG/DXF/PDF rendering. Remove globals, XML/ezdxf
> mutation, subprocess, CLI, `atexit`, filename guesses, and silent skips.

Gate: annotation unit/render tests pass and programmatic build returns only after
all three drawing formats contain valid equivalent annotations and correct hashes.

### Phase B4 — Rebuild the project test suite

Prompt:

> Rename `project_tests/` to `tests/` and split it into config, model, annotation,
> and full-build tests described in Section 12. Replace package-private imports
> with public artifact inspection or explicit direct test dependencies. Use only
> temporary output. Add all-format parsing, cross-format reconciliation, final
> hash checks, transaction failure, determinism, CLI path-with-spaces, and site
> tests. Remove the hardcoded old source commit assertion.

Gate: complete suite passes against the candidate wheel with repository-root
generated output absent.

### Phase B5 — Rewrite project CI, Pages, and agent governance

Prompt:

> Create project-owned `ci.yml` and thin `pages.yml` using only the exact package
> pin and installed commands. Add Node-free site and headless browser tests under
> `/benge-property-cad/`. Replace the cross-boundary architect with
> `benge-design-maintainer`, keep review read-only, and reconcile current agent
> moves/symlinks without losing user content. Verify every remaining integration
> link and permission boundary.

Gate: local CI-parity commands pass; workflow syntax/action checks and all links pass.

### Phase B6 — Remove legacy/vendored files

Prompt:

> After candidate parity is green, physically remove `.tools/`, root `build.py`,
> `start.sh`, downstream `viewer/`, `backup/`, obsolete updater/installer docs,
> stale copied workflows, caches, and redundant agent backups. Preserve only the
> verified legacy tag/archive. Update ignore rules. Run boundary and legacy-name
> scans with migration documents explicitly allowlisted.

Gate: minimal target tree, no broken links, and full suite passes with no sibling
tooling checkout or Node.

### Phase B7 — Local candidate end-to-end verification

Prompt:

> As an independent read-only verifier, create fresh project-only checkouts in
> paths with spaces, install the exact candidate wheel on all claimed Python/OS
> cells, and run every gate in Sections 12–14, including final artifact hashes,
> failure rollback/recovery, determinism, HTTP, Playwright, and a one-dimension change
> simulation in a disposable clone proving only design-owned files are involved.
> Emit the compatibility report and hand it to tooling Phase T6b. Do not repair
> failures in this verifier role.

Gate: immutable local-candidate report is fully passing.

### Phase B8 — Published prerelease verification

Prompt:

> Install `python-cad-tools==0.1.0rc1` from the authorized registry, with cache
> disabled and no local wheel/source fallback. Regenerate all four native locks
> from the registry, prove they contain no candidate source location, rerun the
> entire clean project test/build/verify/site/browser flow, and attach
> registry artifact hashes/provenance. Report failures upstream; never patch the
> installed package or ask the user to test.

Gate: published-prerelease report is fully passing.

### Phase B9 — Stable pin and final registry/deployment verification

Prompt:

> Receive the exact local `python-cad-tools==0.1.0` wheel/sdist hashes from tooling
> Phase T8. `benge-project-operations` stages the stable dependency metadata in a
> clean commit; `cad-compatibility-verifier` makes no source edits and runs the complete matrix
> against those local bytes through the Section 10 checksum-verified ephemeral
> wheel-only resolution procedure before publication; prove every native lock contains no
> local source location. Return the report so the tooling
> workflow can publish those same files without rebuilding. Then resolve
> `python-cad-tools==0.1.0` from the registry, regenerate/verify all four final
> native locks, require downloaded hashes to match the pretested artifacts, and
> rerun the full matrix. Update only the dependency pin/native locks and required
> compatibility metadata.
> Confirm the coordinated Phase R0 GitHub repository/remote/Pages identity,
> redirects, active URLs, and base paths, and rerun active-name checks. In new
> no-cache environments install stable from the registry and run the complete
> matrix. Live Pages is part of this repository's current supported flow: deploy,
> poll it, load it in the automated browser, verify `design_build_hash` and known selection,
> and terminate all local servers. If deployment authorization is unavailable,
> finish every local/staged gate but mark the migration `EXTERNALLY_BLOCKED`, not
> complete; the user supplies authorization only, never testing. Archive the final
> compatibility report.

Gate: stable package, renamed repo, CI, artifacts, local viewer, and deployed
viewer are AI-verified. No user test remains.

## 17. Failure ownership and escalation

| Failure | Owner | Required response |
| --- | --- | --- |
| Benge dimension/ID/material expectation | `benge-design-maintainer` | Fix here and rerun affected/full gates |
| Neutral annotation contains wrong Benge content | `benge-design-maintainer` | Fix provider/config here |
| Same neutral annotation renders differently by format | `cad-tools-maintainer` | File upstream reproducer; wait for new package; no local renderer workaround |
| Generic and Benge builds both fail | `cad-tools-maintainer` | Report candidate/version/evidence upstream |
| Benge-only package integration failure | `cad-compatibility-verifier` triages | Isolate public-contract vs project assumption before assigning |
| Manifest verifier detects mismatched bytes | Build/annotation pipeline | Never weaken or bypass verification |
| Viewer fails on valid generic and Benge bundles | `cad-viewer-maintainer` | Upstream release required |
| Registry/Pages credential missing | `benge-project-operations` records external authority blocker | User supplies authorization, not test labor |
| Published tooling rc fails | Tooling release/owning maintainer; Benge operations updates only the pin | Stop use, preserve evidence, accept only a new fully gated `rcN`; never patch locally or reuse the version |
| Published tooling stable fails | Tooling release/owning maintainer; Benge operations blocks deploy | Yank/mark/advisory plus incident and fully gated patch release; do not deploy/retain a known-bad pin |

Registry versions are immutable. If nominal `0.1.0rc1` fails, this plan repeats
B1–B8 against `0.1.0rc2` (and later `rcN` as necessary). If published `0.1.0`
fails, B9 stops Pages, records the incident, and repeats its complete local/
registry/deployment matrix against the upstream fully gated `0.1.1`; it never
asks for an overwrite or deletes provenance. The final pin/report names the first
fully passing non-yanked stable version and explains any nominal-version change.

## 18. Final definition of done

- Repository, project metadata, model display/artifact identity, CI artifacts,
  URLs, and Pages use `benge-property-cad`/`Benge Property`/`BengeProperty`.
- All pre-split `complex.*` element IDs remain stable and tested.
- Active authoritative source is limited to config, model, neutral annotations,
  and focused Benge tests plus minimal repo support.
- `tests/` contains only Benge-specific contracts; framework tests live upstream.
- The exact fully verified non-yanked stable dependency (`python-cad-tools==0.1.0`
  nominally, or its incident-policy patch) and all native locks install cleanly
  from the registry; no copied/path/editable tooling exists.
- No `.tools`, root build/start launcher, viewer source, legacy backup, stale
  updater docs, broken agent link, or cross-boundary agent authority remains.
- SVG, DXF, and PDF contain equivalent project annotations before the build
  completes; all formats validate.
- Every recorded final artifact size/SHA-256 and schema reconciles, and build
  failure plus injected promotion crashes preserve or recover prior valid output.
- Static, unit, model, annotation, CLI, full-format, determinism, failure,
  clean-clone, site, HTTP, browser, and CI/Pages gates pass on claimed platforms.
- A one-dimension disposable change proves normal CAD work touches only
  design-owned files and needs no package-source reading.
- The final AI-generated compatibility report records exact revisions, package
  artifacts, schemas, semantic/artifact hashes, commands, and browser results.
- No required testing or visual verification is handed back to the user.
