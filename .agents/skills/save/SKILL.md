---
name: save
description: Commit already-verified repository changes through specrepo-autocommit using the OpenCode tool or its command-line fallback, only after the user explicitly asks to commit or save the changes to Git. Use from OpenCode, Claude, or OpenAI environments, but never trigger from inferred intent, task completion, approval, or a generic request to continue.
---

# Save

Use this skill from any agent only when the current user message explicitly
asks to commit the changes to Git. Accept clear equivalents such as "commit
this," "save these changes to Git," or "run autocommit."

Do not use this skill when the user merely asks to implement, finish, verify,
save a file, prepare changes, or says the work looks good. Never infer Git
persistence from task completion or prior preferences. If Git commit intent is
ambiguous, do not invoke the tool.

Before invocation, require completed implementation and applicable checks plus
a concise summary. Prefer the `specrepo-autocommit` tool when it is available;
call it exactly once with the summary and
`userExplicitlyRequestedGitCommit: true`.

When OpenCode tools are not available, run this exactly once from the
repository root:

```bash
python3 .opencode/tools/specrepo-autocommit.py "SUMMARY OF VERIFIED CHANGES"
```

Replace the placeholder with the concise summary. The command-line fallback is
subject to the same explicit Git-commit requirement. Do not invoke Git directly
or retry the tool or fallback automatically. Report its result.
