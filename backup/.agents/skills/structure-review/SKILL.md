---
name: structure-review
description: Review structural layout, supports, load paths, spans, and structural clarity in FreeCAD project designs.
---

# Structure Review Skill

Use when asked to review or improve structural aspects of a FreeCAD project.


Baseline competency: use this skill with strong FreeCAD and Python knowledge, including the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Workflow:

1. Inspect project-owned design sources such as `model.py`, `config.py`, `params.yaml`, README/design notes, and generated model context if available.
2. Identify structural elements, supports, spans, load paths, and unclear assumptions.
3. Flag missing dimensions, labels, or builder-facing structural notes.
4. Recommend changes only in project-owned files. Do not edit `.tools/` or managed shims/launchers.
5. Clearly separate conceptual observations from items requiring professional structural review.
