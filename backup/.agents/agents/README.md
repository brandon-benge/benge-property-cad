# Agents

Project-specific agents are domain/concern specific, not file specific.

All agents are expected to be competent with FreeCAD and Python. They should understand the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Current agents:

- `structure-review.md` maps to `../skills/structure-review/`
- `wiring-review.md` maps to `../skills/wiring-review/`
- `plumbing-review.md` maps to `../skills/plumbing-review/`
- `site-layout-review.md` maps to `../skills/site-layout-review/`
- `buildability-review.md` maps to `../skills/buildability-review/`
- `architect-review.md` maps to `../skills/architect-review/`

All agents must obey the root `AGENTS.md` instructions, especially the rule that `.tools/` and managed shims/launchers are not edited.
