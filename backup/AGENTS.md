# Repository Agent Instructions

## Hard Boundary: Managed Tooling

Do not edit files under `.tools/`.

The `.tools/` directory is managed template tooling. It is updated by `update_tools.py` from the upstream template and must not contain project-specific changes. This applies to all agents, skills, and assistants, including Claude, Codex, OpenCode, and any subagents they spawn.

If a requested change appears to require editing `.tools/`, stop and explain that the change belongs upstream in the template tooling, not in this project repository. Do not patch `.tools/` as a workaround.

## Editable Project Files

Project-specific work belongs in:

- `model.py`
- `config.py`
- `params.yaml`
- `README.md`
- `.agents/`
- `.claude/`
- `.codex/`
- `.opencode/`

Generated FreeCAD files such as `*.FCStd` are project outputs. Do not treat them as managed tooling.

## Compatibility Shims

Root files `build.py`, `helpers.py`, `macro_actions.py`, and the root `*.FCMacro` files are managed launchers/shims. Do not add project-specific behavior there. If they need a tooling change, treat it the same as `.tools/`: stop and route the change upstream.

## FreeCAD Project Work

All agents are expected to be competent with FreeCAD and Python. Domain agents should understand the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow before making recommendations.

For geometry/modeling changes:

- Prefer editing `model.py` and `config.py`.
- Keep geometry parametric.
- Use existing helper APIs instead of duplicating geometry boilerplate.
- Preserve rebuildability through `Build.FCMacro`.

For workflow/config changes:

- Prefer editing `params.yaml` through `ConfigureParams.FCMacro` behavior.
- `InitRepo.FCMacro` must not prompt. Configuration must happen before init.
- `Build.FCMacro` must respect `autocommit_override`.

## Updates

Use `update_tools.py` to refresh managed tooling. The updater must preserve project-owned files and only replace managed paths listed in `.tools/manifest.json`.
