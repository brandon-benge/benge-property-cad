---
name: save
description: Save already-verified repository changes through the exclusive OpenCode specrepo-autocommit tool. Use when the Save agent is invoked by the autocommit command or explicitly asked to persist completed work; never use for editing, inspection, verification, or direct Git operations.
---

# Save

Persist completed, verified repository changes through the one authorized
autocommit path.

## Boundaries

- Use only the native `specrepo-autocommit` tool.
- Never inspect or edit files, run tests, call shell commands, or invoke Git
  directly or indirectly.
- Never delegate work or attempt to bypass a denied or unavailable tool.
- Treat verification, review, and implementation as completed before invocation.

## Workflow

1. Use the supplied non-empty summary. If none is supplied, use
   `Save verified repository changes`.
2. Call `specrepo-autocommit` exactly once with `{"summary":"<summary>"}`.
3. Report whether the tool completed, was blocked, was rejected, or failed.

The tool owns branch, configuration, installation, staging, and commit
preconditions. Do not emulate or retry those operations.
