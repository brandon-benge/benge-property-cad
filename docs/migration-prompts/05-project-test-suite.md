# Prompt 05: rebuild the Benge project test suite

## Objective

Replace the monolithic legacy project test with independent Benge-owned config,
model, annotation, full-build, artifact, CLI, site, and browser contracts.

## Work

1. Read the plan, profile, this prompt, prior reports, and installed public
   contracts. Record starting state in
   `docs/migration/05-project-tests-report.md`.
2. Rename `project_tests/` to conventional `tests/` and split coverage into the
   exact target files from Section 8. Retain every still-valid Benge assertion.
3. Replace exporter/private imports with public inspection APIs or explicitly
   declared direct parser dependencies. Remove the old fixture commit assertion.
4. Make every test use a copied project and temporary output. No test may depend
   on ordering or repository-root generated state.
5. Implement the complete Sections 12.1-12.7 config, model, annotation,
   programmatic API, CLI, artifact reconciliation, rollback, and determinism
   coverage, including paths containing spaces and final byte/hash checks.
6. Independently parse and reconcile STEP, IFC, GLB, SVG, DXF, PDF, JSON, CSV,
   quantities, stable IDs, bounds, schemas, manifest inventory, sizes, and
   SHA-256 values.
7. Implement `tests/test_viewer_e2e.py` with the explicit prepared-site/base-path
   pytest options, server lifecycle, HTTP checks, stable selectors, browser
   console/network capture, selection, metadata, quantities, units, visibility,
   camera, downloads, and `design_build_hash` checks.
8. Exercise site preparation and serving with downstream Node/viewer source
   unavailable, root and `/benge-property-cad/` paths, and strict destination
   safety.
9. Run Ruff, mypy, the complete local Python 3.12/3.13 suite, CLI flows, two
   clean deterministic builds, HTTP checks, and Playwright Chromium E2E.

## Constraints

- Do not copy generic framework tests downstream.
- Do not import package-private/exporter modules or tooling source.
- Do not edit package code or weaken stable-byte, rollback, browser, or parser
  assertions to accommodate a candidate defect.
- Do not require the user to inspect CAD files or a browser manually.

## Clarification and stop gates

If a final-byte, parser, transactional, site, or browser failure reproduces in
the package's generic fixture, file an upstream requirement and ask for a new
candidate. If it occurs only for Benge content, isolate whether the project
assumption or public contract is wrong before asking. Ask the owner before
changing the reviewed golden or advertised model/design intent.

## Gate and checkpoint

All Benge tests pass independently against the installed frozen candidate on
local Python 3.12 and 3.13, repository-root generated output remains absent,
Node is not used downstream, and automated browser evidence is clean. Create
the focused checkpoint and stop.
