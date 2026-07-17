---
name: save
description: Save already-verified repository changes through the exclusive specrepo-autocommit tool.
---

# Save Skill

Persist completed, verified repository changes through the one authorized
autocommit path.

## Workflow

1. Use the supplied non-empty summary. If none is supplied, use
   `Save verified repository changes`.
2. Call `specrepo-autocommit` exactly once with `{"summary":"<summary>"}`.
3. Report whether the tool completed, was blocked, was rejected, or failed.
