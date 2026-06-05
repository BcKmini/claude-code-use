---
description: Save or load a session handoff document. Usage: /handoff [save|load|list]
---

Run the appropriate `claude-handoff` command based on: $ARGUMENTS

**Handling rules:**

`save` or empty:
- Use the Bash tool to run: `python tools/claude-handoff.py save`
- If that fails (tools/ not in path), try: `claude-handoff save`
- After saving, confirm the handoff ID and remind how to resume: `claude-handoff load | claude`

`load`:
- Read the file at `~/.claude/handoffs/` — pick the most recent `.md` file
- Display its full contents so the current session understands the prior context
- Then ask: "Ready to continue. What should we work on?"

`list`:
- Use the Bash tool to run: `python tools/claude-handoff.py list`
- Display the results

If neither Python nor the binary is available, print:
"claude-handoff is not installed. Run: bash tools/install-tools.sh"
