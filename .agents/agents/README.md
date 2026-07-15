# Agents

The project exposes one user-facing agent and one internal implementation subagent:

- `general-contractor.md` maps to `../skills/general-contractor/`. It reviews generated artifacts, reports coordinated construction feedback, and delegates changes.
- `python-cad-architect.md` maps to `../skills/python-cad-architect/`. It is hidden from direct selection and is the only agent authorized to read or edit Python CAD source and tests.
