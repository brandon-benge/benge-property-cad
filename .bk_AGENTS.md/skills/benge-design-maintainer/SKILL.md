---
name: benge-design-maintainer
description: Design and CAD source maintenance using public installed python_cad_tools API; create geometry and metadata together; enforce stable IDs, units, and IFC intent; run builds, parsers, validators, and test suites.
---

# Benge Design Maintainer Skill

Accept design and CAD implementation tasks. Edit only `config.py`, `model.py`,
`drawing_annotations.py`, and `tests/`. Use only the documented public
`python_cad_tools` API.

## Model contract

Maintain Python as the sole design authority. Every component must return shared
elements containing geometry and semantic metadata together, including:
- stable semantic ID and hierarchy
- exact BREP or documented reference geometry
- placement and explicit units
- category, material, color, and visibility
- IFC mapping or intentional exclusion
- dimensions and quantity provenance

## Standards responsibilities

Enforce and test:
- exact STEP output and reload validation
- intentional IFC classes, deterministic GlobalIds, placements, properties
- deterministic GLB tessellation, hierarchy, metadata, materials
- conceptual SVG, DXF, and PDF annotations with stable IDs
- exact quantity provenance and reconciliation
- deterministic manifest hashes and cross-format bounds

## Implementation workflow

1. Translate request into explicit acceptance checks.
2. Inspect relevant source, tests, manifests, and generated evidence.
3. Identify affected stable IDs and downstream formats.
4. Make the smallest coherent parametric change.
5. Update validation and tests with the change.
6. Build the shared model once and regenerate every affected output.
7. Run format-specific parsers and cross-format reconciliation.
8. Report evidence and limitations.

Never manually edit generated artifacts. Preserve stable IDs unless an
intentional migration is documented.
