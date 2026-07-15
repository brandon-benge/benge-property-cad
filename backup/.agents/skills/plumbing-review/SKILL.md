---
name: plumbing-review
description: Review plumbing routing, fixture placement, access, slope assumptions, and needed builder/plumber outputs.
---

# Plumbing Review Skill

Use when asked to review or improve plumbing planning for a FreeCAD project.


Baseline competency: use this skill with strong FreeCAD and Python knowledge, including the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Workflow:

1. Inspect project-owned design sources such as `model.py`, `config.py`, `params.yaml`, README/design notes, and generated model context if available.
2. Identify fixtures, supply routes, drain routes, slope assumptions, cleanouts, access panels, and exposure risks.
3. Flag likely conflicts with structure, electrical routes, access, or freezing conditions.
4. Recommend builder/plumber-facing outputs such as routing diagrams, fixture schedules, notes, and access details.
5. Recommend changes only in project-owned files. Do not edit `.tools/` or managed shims/launchers.
