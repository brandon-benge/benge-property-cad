# tools/

Infrastructure (per `tools/reconcile-infrastructure`'s own definition:
everything except `config.py`, `model.py`, `drawing_annotations.py`,
`models/**/*.py`, and `generated/`), so this directory is meant to be kept in
sync with this repository's sister projects rather than authored per-project
— though that sync is a manual, on-demand run of the tool below, not
automatic; a sister repo can carry an extra script here until it's rerun,
which is currently true of `test-with-cad-override` (see below).

- **`reconcile-infrastructure <path-to-file-template-cad-checkout>`** —
  overwrites every tracked infrastructure file in this repo with the
  template's live committed version, and removes any infrastructure file the
  template no longer has. Never touches the four customer-owned CAD-authoring
  paths or `generated/`. Invoked by `run-git-opencode-audit` before every
  OpenCode edit loop so the AI always works against an up-to-date template.
- **`run-git-opencode-audit`** — the entry point `.github/workflows/opencode.yml`
  invokes when the repository owner opens an issue or comments `/oc`/`/opencode`.
  Drives one full Git-triggered OpenCode transaction: validates the
  provider/model, runs `opencode` through `run-with-inactivity-watchdog`,
  writes a schema-validated audit run under `.makeitours/audit/v1/<run_id>/`,
  and commits/pushes only on success. On failure it leaves history untouched
  and writes redacted evidence for the workflow to upload instead. Not meant
  to run outside that workflow.
- **`run-with-inactivity-watchdog <inactivity_seconds> <command> [args...]`**
  — internal helper `run-git-opencode-audit` uses to run `opencode` itself:
  streams output live while writing a redacted, size-bounded copy for the
  audit trail, and kills the whole process group (exit 124, like GNU
  `timeout`) if it goes quiet for `inactivity_seconds`. Not meant to be
  invoked directly.
- **`test-with-cad-override [command...]`** — present in this checkout but
  **untracked**: `.gitignore`'s `tools/*` rule has no `!tools/README.md`-style
  exception for it, so a fresh clone of this repository will not have it, and
  it is not shared with `file-template-cad`. A manual, human/agent-run
  developer tool: runs this project's tests (or an arbitrary command) against
  a locally-built `python-cad-tools` wheel, installed into a disposable venv
  deleted on exit, via `PYTHON_CAD_TOOLS_OVERRIDE_WHEEL=path/to/wheel`. Not
  invoked by CI. Per this repository's own `AGENTS.md`, the only sanctioned
  way to test a local override wheel without touching `pyproject.toml`, the
  committed lockfiles, or the project's own `.venv`.

If this directory is removed or restructured, this file no longer applies.
