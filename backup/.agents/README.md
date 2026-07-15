# Shared Agent Assets

This directory contains project-local agent and skill definitions shared across Claude, Codex, and OpenCode through repo-local symlinks.

- `agents/` stores reusable agent definitions.
- `skills/` stores reusable skill/workflow definitions.

Tool-specific directories live at the repository root:

- `.claude/agents -> ../.agents/agents`
- `.claude/skills -> ../.agents/skills`
- `.codex/agents -> ../.agents/agents`
- `.codex/skills -> ../.agents/skills`
- `.opencode/agents -> ../.agents/agents`
- `.opencode/skills -> ../.agents/skills`

Keep this directory project-specific. Do not create links outside this repository.

The current mapping is one-to-one:

- `structure-review` agent and skill
- `wiring-review` agent and skill
- `plumbing-review` agent and skill
- `site-layout-review` agent and skill
- `buildability-review` agent and skill
- `architect-review` agent and skill
