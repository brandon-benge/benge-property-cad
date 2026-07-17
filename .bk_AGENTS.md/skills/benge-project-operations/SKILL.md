---
name: benge-project-operations
description: Repository and project operations maintenance — dependencies, locks, CI/Pages workflows, agent governance, symlinks, .gitignore, README, and migration docs.
---

# Benge Project Operations Skill

Maintain the project's dependency declaration, reproducible native locks,
CI/Pages workflows, agent governance, symlinks, .gitignore, README, and
migration documentation.

## Authority

- Edit `pyproject.toml`, requirements/locks, README, AGENTS.md, `.agents/**`,
  `.claude/**`, `.codex/**`, `.opencode/**`, `opencode.jsonc`, `CLAUDE.md`,
  `.github/workflows/*`, `.gitignore`, and migration docs.
- Update dependency pin and regenerate all native locks together.
- Change project identity metadata.
- Create and test symlinks for agent tool integration.

## Boundaries

- Do not change CAD geometry, element IDs, model structure, or annotation content.
- Do not edit `config.py`, `model.py`, `drawing_annotations.py`.
- Do not edit tooling source or site-packages.
- Do not invoke Git or `specrepo-autocommit`.
