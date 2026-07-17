# Shared Agent Assets

This directory contains the three canonical agent and skill definitions shared by Claude, Codex, and OpenCode through repository-local links.

- `general-contractor` is the user-facing, read-only primary agent. It reviews only generated project outputs, consolidating architectural-deliverable, buildability, structural, site, plumbing, and electrical feedback.
- `python-cad-architect` is the directly callable implementation agent. It is the only agent allowed to read or edit Python CAD source, managed CAD tooling, tests, or standards mappings, and it cannot use Git or autocommit.
- `save` is the hidden persistence subagent. It cannot inspect, edit, test, or use a shell; in OpenCode it is the exclusive caller of `specrepo-autocommit`.

The user may invoke the Python CAD Architect directly, and the General Contractor delegates every implementation or source-level investigation to it when coordinating output review. The `/autocommit` command invokes Save only after work is verified. The Save agent is not intended for direct user invocation.

Tool-specific directories link to these definitions:

- `.claude/agents -> ../.agents/agents`
- `.claude/skills -> ../.agents/skills`
- `.codex/agents -> ../.agents/agents`
- `.codex/skills -> ../.agents/skills`
- `.opencode/agents -> ../.agents/agents`
- `.opencode/skills -> ../.agents/skills`

These are repository-local links only. Do not create or update agent definitions outside this checkout as part of template maintenance.
