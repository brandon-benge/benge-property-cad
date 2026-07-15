# Installed Python CAD Project Instructions

## Hard boundary: managed tooling

Do not edit files under `.tools/`, managed root `build.py`, the root `install.py` and `update_tools.py` compatibility launchers, managed `.agents/`, or tool-registration links/configuration. These files come from the upstream template through `.tools/update_tools.py` and must not contain project-specific changes. This applies to every assistant and any subagent it invokes.

If a requested change appears to require managed tooling, stop and explain that it belongs upstream. Do not patch managed files as a project workaround.

## Project-owned source

Project-specific design and workflow work belongs in:

- `model.py` and optional project component modules;
- `config.py`;
- `params.yaml`;
- `README.md`;
- project-specific tests or validation extensions;
- `pyproject.toml` and `.gitignore` when project dependencies or policy change.

Python design source is authoritative. Generated files are disposable build products and must never be edited as design inputs.

## Build and verification

- Keep geometry parametric and use the managed `python_cad_tools` API.
- Preserve stable semantic IDs or document intentional migrations.
- Create geometry and metadata together; assign intentional IFC mappings or exclusions.
- Run `python build.py` after changes and review the regenerated validation reports and manifests.
- The default build must remain FreeCAD-independent.
- Use `python build.py --include-fcstd` only when optional compatibility output is explicitly required and FreeCADCmd is installed.

Managed updates replace only manifest-declared paths and preserve project-owned source. Use `python .tools/update_tools.py`; the root `python update_tools.py` command remains a compatibility alias. Use `--force-guidance` only to restore the upstream managed agent/guidance defaults.
