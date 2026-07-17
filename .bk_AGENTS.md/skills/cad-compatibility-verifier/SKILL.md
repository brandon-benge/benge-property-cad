---
name: cad-compatibility-verifier
description: Independent read-only verification of complete CAD toolchain compatibility.
---

# CAD Compatibility Verifier Skill

As an independent read-only verifier, install the exact tool package from the
authorized source and run the complete test, build, verify, site, and browser
matrix. Produce a machine-readable compatibility report.

## Verification sequence

1. Create a fresh archive/clone of the repository alone.
2. Create clean Python environments matching matrix cells.
3. Install the exact matching lock from the authorized registry.
4. Assert `importlib.metadata.version("python-cad-tools")` equals the project pin.
5. Assert `python_cad_tools.__file__` is under that environment's `site-packages`.
6. Run static checks: ruff, mypy.
7. Run all tests: pytest.
8. Run complete build: `python-cad validate`, `build`, `verify`.
9. Run site preparation and browser E2E.
10. Emit the compatibility report.
