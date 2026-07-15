---
name: architect-review
description: Review what builder-facing drawings, schedules, quantities, details, and outputs are needed.
---

# Architect Review Skill

Use when asked what designs and outputs are needed for actual builders to price, plan, and execute the work.


Baseline competency: use this skill with strong FreeCAD and Python knowledge, including the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Workflow:

1. Inspect project-owned design sources such as `model.py`, `config.py`, `params.yaml`, README/design notes, and generated model context if available.
2. Determine the current design maturity: concept, layout, construction planning, or builder-ready package.
3. Identify missing outputs: plans, elevations, sections, details, dimensions, schedules, quantities, BOM/cut lists, notes, reference views, and exported sheets.
4. Recommend a prioritized builder package that can be produced from or added to the FreeCAD model.
5. Recommend changes only in project-owned files. Do not edit `.tools/` or managed shims/launchers.
