---
name: buildability-review
description: Review whether the design can be built practically, clearly, and in a sensible construction sequence.
---

# Buildability Review Skill

Use when asked to review whether a FreeCAD design is practical for builders to construct.


Baseline competency: use this skill with strong FreeCAD and Python knowledge, including the FreeCAD document/object model, `Part` geometry, placements, recompute/save behavior, Python module reloading, and the project-owned `model.py` / `config.py` workflow.

Workflow:

1. Inspect project-owned design sources such as `model.py`, `config.py`, `params.yaml`, README/design notes, and generated model context if available.
2. Identify assembly sequence, repeated parts, material assumptions, access constraints, and tolerances.
3. Flag missing labels, dimensions, cut lists, quantities, and construction notes.
4. Recommend simplifications that improve fabrication, transport, and installation.
5. Recommend changes only in project-owned files. Do not edit `.tools/` or managed shims/launchers.
