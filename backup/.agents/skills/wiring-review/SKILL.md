---
name: wiring-review
description: Review electrical planning intent, routing, placement, and needed builder/electrician outputs.
---

# Wiring Review Skill

Use when asked to review or improve wiring/electrical planning for a FreeCAD project.


Baseline competency: use this skill with strong FreeCAD and Python knowledge, including the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Workflow:

1. Inspect project-owned design sources such as `model.py`, `config.py`, `params.yaml`, README/design notes, and generated model context if available.
2. Identify outlets, switches, lighting zones, conduit/routing assumptions, service areas, and access constraints.
3. Flag conflicts with water, structure, clearances, or inaccessible routes.
4. Recommend builder/electrician-facing outputs such as wiring diagrams, fixture schedules, labels, and notes.
5. Recommend changes only in project-owned files. Do not edit `.tools/` or managed shims/launchers.
