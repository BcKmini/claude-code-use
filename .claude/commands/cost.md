---
description: Estimate or track Claude Code session costs. Usage: /cost [estimate <snippet>|history|month|agents]
---

Run the appropriate `claude-cost` command based on: $ARGUMENTS

**Handling rules:**

`estimate <name>` or `estimate <prompt text>`:
- Check if the argument matches a snippet name in `~/.claude/snippets.json`
- If it matches a snippet, run: `python tools/claude-cost.py estimate --snippet <name>`
- Otherwise treat it as a prompt string: `python tools/claude-cost.py estimate "<text>"`
- Display the cost breakdown table

`history`:
- Run: `python tools/claude-cost.py history`

`month`:
- Run: `python tools/claude-cost.py month`

`agents`:
- Run: `python tools/claude-cost.py agents`

empty / no args:
- Run: `python tools/claude-cost.py month`
- Show monthly summary as a quick overview

If Python is unavailable, try the compiled binary: `claude-tools cost <subcommand>`

If neither is available, print:
"claude-cost is not installed. Run: bash tools/install-tools.sh"
