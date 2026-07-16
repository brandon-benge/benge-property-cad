# Prompt 02: intake and verify the local tooling candidate

## Objective

Verify the immutable generic `python-cad-tools==0.1.0rc1` handoff before any
Benge source migration depends on it.

## Prerequisite and required question

Before acting, locate the tooling Prompt 08 report and candidate bundle. If they
are absent, ask the owner for the exact bundle path and stop. Do not build a
candidate from tooling source or substitute the temporary artifacts mentioned
in the tooling Prompt 02 report.

## Work

1. Read the complete Benge plan, execution profile, this prompt, the Benge
   Prompt 01 report, and the tooling candidate's final report/provenance.
2. Record starting `HEAD`, status, candidate filenames, sizes, hashes, source
   revision, tool lock hashes, and claimed platforms in
   `docs/migration/02-candidate-intake-report.md`.
3. Verify the wheel, sdist, checksum file, provenance, report, and bundle hashes
   before executing any candidate code.
4. Inspect wheel/sdist metadata and contents for the exact distribution,
   `0.1.0rc1` version, public modules, `py.typed`, schemas, generic scaffold,
   viewer shell, build information, and forbidden project/backup/source content.
5. In disposable environments outside both checkouts, install the wheel
   non-editably on local Python 3.12 and 3.13 using the checksum-verified,
   wheel-only procedure from Section 10. Disable source-tree fallbacks and prove
   imports resolve under that environment's `site-packages`.
6. Run `pip check`, public symbol/type probes, CLI version/help, packaged generic
   fixture build/verify, prepare-site/serve, and the locally applicable generic
   browser smoke test described by the handoff.
7. Exercise the sdist-to-wheel evidence without rebuilding or altering the
   frozen handoff artifacts. Record discrepancies.
8. Store only a small machine-readable candidate reference (filenames, hashes,
   source revision, report path) in the repository; do not copy distributions
   into Git.

## Constraints

- Do not edit Benge design source or project dependency metadata yet.
- Do not inspect or patch tooling source or site-packages.
- Do not publish, push, rename, or access a registry.
- Do not serialize the candidate directory into project metadata or locks.

## Clarification and stop gates

Ask the owner for a replacement immutable candidate only if hashes/provenance do
not verify or a required generic gate fails. Report the exact reproducer and
stop. Ask whether to reduce platform claims only if a binary dependency is
unavailable on local Python 3.12 or 3.13; do not silently skip it.

## Gate and checkpoint

The gate requires clean, non-editable local verification of the exact handoff on
both locally available Python versions with no tooling checkout on `sys.path`.
Commit the intake report and candidate-reference evidence, create one focused
checkpoint, and stop.
