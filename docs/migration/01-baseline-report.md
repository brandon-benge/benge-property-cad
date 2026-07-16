# Prompt 01 preservation and baseline report

- Result: **PASS with preserved legacy defects**
- Plan contract: `repo-split-v1`
- Prompt scope: `docs/migration-prompts/01-preserve-and-baseline.md` only
- Execution profile: `docs/migration-prompts/00-execution-profile.md`
- Starting commit: `df58179d506e52dd6cb771afd7b5b719a086cfc3`
- Starting branch: `main`
- Baseline capture time: 2026-07-16 13:29-13:37 EDT

Prompt 01 changed no product source, dependency, workflow, viewer, agent, remote, or
generated-file policy. The only repository additions are this report, the reviewed
semantic fixture, and its standalone generator/verifier. Existing user-owned
deletions and backup/planning paths were preserved.

## Starting repository state

The initial `git status --short --branch` was:

```text
## main...origin/main [ahead 1]
 D .agents/.DS_Store
 D .agents/README.md
 D .agents/agents/general-contractor.md
 D .agents/agents/python-cad-architect.md
 D .agents/agents/save.md
 D .agents/skills/general-contractor/SKILL.md
 D .agents/skills/general-contractor/agents/openai.yaml
 D .agents/skills/python-cad-architect/SKILL.md
 D .agents/skills/python-cad-architect/agents/openai.yaml
 D .agents/skills/save/SKILL.md
 D .agents/skills/save/agents/openai.yaml
 D AGENTS.md
?? .back_agents/
?? BENGE_PROPERTY_CAD_REPOSITORY_MIGRATION_PLAN.md
?? REPO_SPLIT_PROMPT_PLAN.md
?? back_AGENTS.md
```

There were no staged changes and no tags. The only configured remote was:

```text
origin  https://github.com/brandon-benge/benge_freecad_project.git (fetch)
origin  https://github.com/brandon-benge/benge_freecad_project.git (push)
```

No remote operation was performed.

## Local pre-migration tag

Created the local annotated tag:

```text
pre-migration-benge-baseline-df58179
```

It dereferences to the untouched starting commit
`df58179d506e52dd6cb771afd7b5b719a086cfc3`. The tag was not pushed.

## External preservation bundle

The authorized external bundle is:

```text
/Users/brandonbenge/Desktop/Houses Folder/Dreaming of Yard and House Updates/benge-property-cad-migration-preservation/20260716T132948-0400-benge-preservation/
```

It is outside Git and contains:

- `full-worktree.tar.gz`: every present non-`.git` path, including tracked,
  ignored, non-ignored untracked, caches, virtual environments, generated output,
  `.back_agents/`, `back_AGENTS.md`, migration plans, modes, and symlinks;
- `repository.bundle`: all Git refs and reachable history;
- `git-metadata.tar.gz`: the complete `.git` directory, including the index,
  configuration, refs, reflogs, and annotated baseline tag;
- `worktree.patch`: the complete unstaged `git diff --binary`;
- `staged.patch`: the complete staged binary diff (correctly zero bytes);
- `metadata/`: starting HEAD/branch/status/remotes/tags, index modes, tracked and
  deleted manifests, separate ignored and non-ignored untracked manifests, all
  present paths, regular-file SHA-256 values, path modes/sizes, symlink modes,
  targets and broken/resolved state, host/tool versions, dependency versions,
  lock checksums, archive listing, bundle verification, and reconstruction proof;
- `SHA256SUMS`: SHA-256 for every other file in the bundle.

Preserved inventory counts:

| Class | Count |
| --- | ---: |
| Tracked paths | 166 |
| Tracked deletions | 12 |
| Non-ignored untracked paths | 14 |
| Ignored untracked files | 40,138 |
| Present paths excluding `.git` | 44,517 |
| Present regular files excluding `.git` | 40,272 |
| Symlinks | 34 |

Important bundle hashes:

| File | SHA-256 |
| --- | --- |
| `full-worktree.tar.gz` | `1c807ac43e5dfde12bac812075673e6adc8d453c1890430caf23ba94aa8e4859` |
| `repository.bundle` | `63b09a82d181cf232149cfd3f81bc77915f6d8a683632d8886686d7a04a8a5e0` |
| `git-metadata.tar.gz` | `92d53d9a066516e42d92caec70f48f910c090c11f09b062d0af02e6ce9c60e76` |
| `worktree.patch` | `73907cebc8f2fb72cf404fad000dd515ebcbf543bcb169c25325889921e4f51c` |
| `staged.patch` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `SHA256SUMS` | `598999f889cb6fcfae947af62fe60efef5ab4b17ede08408f1f9308974f1f4e5` |

`shasum -a 256 -c SHA256SUMS` passed after the bundle was frozen.

### Reconstruction proof

The verification created a temporary `git clone --no-checkout` from
`repository.bundle`, populated its index with `git read-tree HEAD`, and extracted
`full-worktree.tar.gz` without checking out tracked content. It then regenerated
and byte-compared all of the following against the source capture:

```text
PASS present-paths.txt
PASS present-file-sha256.txt
PASS present-regular-modes-sizes.tsv
PASS present-directory-modes.tsv
PASS present-symlink-modes.tsv
PASS symlinks.tsv
PASS status-worktree.txt
PASS deleted-tracked-paths.txt
PASS untracked-nonignored-paths.txt
PASS untracked-ignored-paths.txt
PASS worktree.patch
PASS staged.patch
```

The reconstructed HEAD and branch were `df58179...` and `main`. This proves path
presence/absence, contents, regular-file and directory modes, symlink modes and
targets, broken-link state, tracked deletion state, ignored/untracked state,
staging state, and Git status are recoverable. The temporary verification clone
was removed after evidence was written into the bundle.

## Host and dependency baseline

| Item | Observed value |
| --- | --- |
| Host | macOS 26.5.2 build 25F84, Darwin 25.5.0, arm64 |
| Git | 2.50.1 (Apple Git-155) |
| Default `python3` | CPython 3.13.6 |
| Available `python3.12` | CPython 3.12.9 |
| Available `python3.13` | CPython 3.13.6 |
| Project virtual environment | CPython 3.13.6, pip 25.2 |
| Node / npm | 24.10.0 / 11.6.0 |
| FreeCAD / FreeCADCmd | not available |
| build123d | 0.11.1 |
| ifcopenshell | 0.8.5 |
| trimesh | 4.12.2 |
| numpy | 2.5.1 |
| ezdxf | 1.4.4 |
| reportlab | 4.5.1 |
| pypdf | 6.14.2 |
| pytest | 8.4.2 |
| Ruff / mypy in project environment | not installed |
| Legacy copied tooling | present under `.tools/python_cad_tools` |

The current CI advertises only Python 3.13. The Python 3.12 interpreter exists,
but this legacy checkout has no Python-3.12 environment/lock execution gate; no
3.12 pass is claimed.

## Baseline command matrix

All commands used the current files and existing project environment. Expected
legacy failures were recorded, not repaired.

| Area | Command | Exit/result |
| --- | --- | --- |
| Lint | `PATH="$PWD/.venv/bin:$PATH" ruff check model.py config.py project_tests` | 127; `ruff` not installed |
| Type | `PATH="$PWD/.venv/bin:$PATH" mypy` | 127; `mypy` not installed |
| Project test | `PATH="$PWD/.venv/bin:$PATH" pytest -q` | 0; 1 passed in 18.12 s |
| Validation | `PATH="$PWD/.venv/bin:$PATH" python build.py --validate-only` | 0; model validation passed, but the atexit callback still rewrote plan SVG/DXF |
| Build | `PATH="$PWD/.venv/bin:$PATH" python build.py` | 0; 22 generated paths reported |
| Current determinism check | read manifest `semantic_hash`, build, read again, `diff` | 0; both `8fae3c13894febbcdddbb3cb9fdfe134211b8afddff4df4a5a72dfa804d61f43` |
| Viewer prepare | `npm run prepare-model` in `viewer/` | 0; 21 artifacts prepared |
| Viewer unit tests | `npm test` in `viewer/` | 0; 8 files, 23 tests passed |
| Viewer model check | `npm run test:model` in `viewer/` | 0; 237 meshes, 236 selectable stable IDs |
| Viewer production build | `VITE_BASE_PATH=/benge_freecad_project/ npm run build` in `viewer/` | 0; TypeScript and Vite passed, with a large-chunk warning |
| Golden generator | `PYTHONPATH="$PWD/.tools:$PWD" .venv/bin/python tests/verify_model_contract_v1.py --write` | 0 |
| Golden verifier | `PYTHONPATH="$PWD/.tools:$PWD" .venv/bin/python tests/verify_model_contract_v1.py` | 0; PASS |

The current build/test/viewer success does not override the missing lint/type
tools or the artifact-integrity and byte-determinism defects below.

## Semantic golden

`tests/fixtures/model_contract_v1.json` is generated from the untouched in-memory
model and checked against valid baseline STEP, IFC, design-manifest, and quantity
output. It deliberately does not depend on final SVG/DXF drawing bytes.

Reviewed values include:

| Contract value | Baseline |
| --- | --- |
| Model ID / name | `functional.benge_complex` / `BengeComplexFunctional` |
| Element IDs | 236 sorted unique `complex.*` IDs |
| Material IDs | 28 sorted unique `material.complex.*` IDs |
| Model bounds (mm) | `[-304.8, -15544.8, -2438.4, 12801.6, 304.8, 4470.4]` |
| Quantity element count | 236 |
| Total area (mm²) | 985,443,674.902338 |
| Total volume (mm³) | 115,439,941,583.0713 |
| Total mass (kg) | 123,849.416815 |

The fixture includes selected bounds for the house mass, fireplace masonry,
hot-tub placeholder and platform, outdoor-kitchen cabinet run, pool water, roof
cover, and first lower-front tread. It includes quantity totals grouped by every
category and every material.

The identity map explicitly requires:

- model ID `functional.benge_complex` to become `benge.property`;
- display/artifact identity `BengeComplexFunctional` to become
  `Benge Property` / `BengeProperty`;
- source module and tag to become `model` and `benge-property`;
- all element and material IDs, and element-derived IFC product IDs, to remain;
- IFC project/site/building/storey and three aggregate relationship GlobalIds to
  migrate once when the deterministic model-ID input changes.

All seven legacy IFC spatial/aggregate GlobalIds are recorded. The target
observation is intentionally `null`: Prompt 01 cannot change source identity and
the execution profile forbids fabricating candidate output. The later canonical
identity build must observe and verify those target IDs.

The standalone verifier suppresses only registration of the known legacy atexit
callback while loading the model, so semantic inspection itself cannot mutate
generated drawings. It validates fixture ordering, uniqueness, counts, internal
quantity reconciliation, selected/whole-model bounds, source hashes, model
metadata, and legacy IFC observations.

## Generated artifact baseline and defects

The manifest inventories these 21 non-manifest artifacts:

```text
.gitkeep
drawings/dxf/BengeComplexFunctional_front.dxf
drawings/dxf/BengeComplexFunctional_plan.dxf
drawings/dxf/BengeComplexFunctional_section.dxf
drawings/dxf/BengeComplexFunctional_side.dxf
drawings/pdf/BengeComplexFunctional_Conceptual_Drawings.pdf
drawings/svg/BengeComplexFunctional_front.svg
drawings/svg/BengeComplexFunctional_plan.svg
drawings/svg/BengeComplexFunctional_section.svg
drawings/svg/BengeComplexFunctional_side.svg
glb/BengeComplexFunctional.glb
glb/manifest.json
ifc/BengeComplexFunctional.ifc
ifc/validation.json
manifests/design-elements.json
quantities/materials.csv
quantities/quantities.csv
quantities/quantities.json
quantities/summary.md
step/BengeComplexFunctional.step
step/validation.json
```

Independent size/SHA-256 reconciliation checked all 21 entries and found exactly
two post-build mismatches after the final validate-only run:

| Path | Manifest size / actual | Manifest SHA-256 / actual SHA-256 |
| --- | --- | --- |
| `drawings/dxf/BengeComplexFunctional_plan.dxf` | 118,434 / 123,883 | `ba26e6df26f125c439072e7dbeba97620faa1431e3c00a98897ddc1db7f290ec` / `39912d1315c9f1e28c52d7dd0abcd781e4d4ca948af6783a94c0bc5e45adddcd` |
| `drawings/svg/BengeComplexFunctional_plan.svg` | 56,167 / 60,203 | `4353130f5b7a51ea00ae2d1f41706cbf4fbe7fbca6e52b683ba01624b7b51a63` / `5b8d61921eacbf915251ae3a72a8d6b9d91aeffe0e9f699367b11b0972c8666a` |

These are defect evidence, not golden hashes. The manifest is written before the
atexit annotation callback mutates those final files.

The current semantic-only determinism check passes while stable bytes do not.
Two successive successful full builds produced:

| Artifact | Build A SHA-256 | Build B SHA-256 | Stable? |
| --- | --- | --- | --- |
| STEP | `1f9cb0f11248b3b5cafe15e93a11a8982b3764121c1620f039949ad67cfc75be` | `b39dab1de2ed8cd139c5f5e3c7cac18901476e98ebcc840a1bf9039c0ba3b916` | no |
| IFC | `bd8f3707803e3654196cbb6f88676dbcbdd483e30918e3230802d3e4683922c3` | `f21c4adc3a3de3f2bcf00f83422c90daf5c58e41bb2f2351ac659fc48edff133` | no |
| GLB | `9846eb14a8edaf40ff38fd1a520a875fd4f2cd1ddaf9f4d3f5b7997a3f57bdbd` | same | yes |
| Plan SVG after annotation | `5b8d61921eacbf915251ae3a72a8d6b9d91aeffe0e9f699367b11b0972c8666a` | same | yes, but not manifest-valid |
| Plan DXF after annotation | `80f890e16f476bae19ad296d793980361d2899cc209dc66e4a55fc8b4e878ecc` | `1d2c4f494159c6b3bccf04744b5331adf4e28578329c35706139e07bff7665ab` | no and not manifest-valid |
| PDF | `d010973cfb731a4b015abe7a795be1c2e0f12a286c9dcf10f0ec675b0b3cf11f` | same | yes |
| Quantities JSON | `e1ebb4e8c328da7f20d0a6e70fa806a9998c283ee4a1001f6fd9e9e09875b98e` | same | yes |
| Design-elements JSON | `3e113be0c424ae291e57f5e3cceeed73118c9fdfd83febc20a826fd0eaac1876` | same | yes |

Running `--validate-only` then changed the already-generated plan DXF again to
`39912d...` without rebuilding artifacts. This confirms validation/import
lifecycle side effects. The final representative hashes are the actual hashes in
the mismatch table plus Build B's STEP/IFC and the stable values above; none of
the corrupted/mutable drawing hashes is a golden contract.

## Legacy coupling and lifecycle inventory

Active legacy identity remains in `config.py`, `model.py`, `pyproject.toml`,
`project_tests/test_benge_project.py`, viewer metadata/docs, and the copied
`.tools` template. Migration-only fixture/report/verifier references are
historical evidence and must remain allowlisted later.

Specific boundary and lifecycle debt:

- `build.py` inserts `.tools` into `sys.path`;
- `start.sh` sets `PYTHONPATH` to `.tools`;
- `pyproject.toml` sets pytest `pythonpath = [".tools", "."]` and mypy
  `mypy_path = [".tools"]`;
- `project_tests/test_benge_project.py` imports private
  `python_cad_tools.exporters.ifc.property_value`;
- `model.py` imports `drawing_annotations` solely for lifecycle registration;
- `drawing_annotations.py` imports `atexit` and `subprocess`, mutates global
  `generated/` SVG/DXF paths, invokes `build.py`, guesses DXF identity from file
  names, and registers `annotate_all` at exit;
- the root contains copied `.tools`, root launcher, `start.sh`, viewer source,
  backup history, caches, and agent backups that later prompts must remove only
  after candidate parity succeeds.

Current large-tree sizes (KiB from `du -sk`) were:

| Path | KiB |
| --- | ---: |
| `.venv` | 867,548 |
| `viewer` | 218,368 |
| `.opencode/node_modules` | 62,012 |
| `.mypy_cache` | 25,752 |
| `generated` | 5,980 |
| `backup` | 476 |
| `.tools` | 408 |
| `.back_agents` | 52 |
| `docs` | 56 |
| `project_tests` | 32 |

The full checkout occupied about 1.1 GiB before Prompt 01 additions.

## Agent and symlink state

The preservation bundle records all 34 symlinks. The six active tool-view links
plus `CLAUDE.md` are broken because `.agents/` and `AGENTS.md` are deleted:

```text
.claude/agents -> ../.agents/agents
.claude/skills -> ../.agents/skills
.codex/agents -> ../.agents/agents
.codex/skills -> ../.agents/skills
.opencode/agents -> ../.agents/agents
.opencode/skills -> ../.agents/skills
CLAUDE.md -> AGENTS.md
```

The corresponding `.back_agents/` and `back_AGENTS.md` bytes, all deleted source
paths, and this broken/resolved state are in the verified external bundle. They
were not deleted or reconciled in Prompt 01.

## Gate conclusion

Prompt 01's gate passes:

- the complete dirty state is checksum-verifiably recoverable;
- the untouched starting HEAD has a local annotated tag;
- the 236-element semantic golden is generated, reviewed, internally consistent,
  and independently verified without trusting corrupted drawing hashes;
- current checks and all baseline failures/side effects are recorded;
- no pre-existing user change was reset, deleted, staged, or overwritten.

The missing Ruff/mypy executables, known manifest mismatches, lifecycle mutation,
and byte nondeterminism are baseline defects for later authorized prompts. They do
not block the preservation checkpoint and were not repaired here.
