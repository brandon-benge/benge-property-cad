---
name: site-layout-review
description: Review site placement, grading, drainage, access, utilities, and yard constraints.
---

# Site Layout Review Skill

Use when asked to review or improve site placement or yard layout for a FreeCAD project.


Baseline competency: use this skill with strong FreeCAD and Python knowledge, including the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Workflow:

1. Inspect project-owned design sources such as `model.py`, `config.py`, `params.yaml`, README/design notes, and generated model context if available.
2. Identify placement references, access paths, drainage direction, grading assumptions, utilities, fences, trees, and staging constraints.
3. Flag missing measurements, property references, grade information, and utility assumptions.
4. Recommend builder-facing outputs such as site plans, offsets, reference points, access diagrams, and staging notes.
5. Recommend changes only in project-owned files. Do not edit `.tools/` or managed shims/launchers.
