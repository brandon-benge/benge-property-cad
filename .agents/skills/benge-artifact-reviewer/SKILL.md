---
name: benge-artifact-reviewer
description: Read-only review of generated CAD artifacts, manifests, and drawings.
---

# Benge Artifact Reviewer Skill

Review generated project outputs only. Cover all design, site, structural,
plumbing, and electrical concerns visible in the artifacts.

## Evidence boundary

Read only outputs under `generated/`, including:
- build and design-element manifests
- STEP, IFC, and GLB validation reports
- SVG, DXF, and PDF drawing sheets
- quantity JSON, CSV, and Markdown summaries

## Review workflow

1. Inventory the generated artifact set.
2. Check the build manifest and validation reports.
3. Reconcile stable IDs, dimensions, materials across formats.
4. Review plans, elevations, sections, labels, schedules.
5. Classify findings as blocker, important, or advisory.

## Delegate changes

When a finding requires source changes, call `benge-design-maintainer` with
affected artifacts, observed problem, desired output, and acceptance evidence.

After delegation, review regenerated outputs and close each finding.
