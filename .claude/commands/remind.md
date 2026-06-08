# /remind — Session Start Task Reminder

Surface incomplete checklist items from TODO.md / TASKS.md / CLAUDE.md and pipe them into Claude as a session-start prompt.

## Usage

```
/remind                      # scan all task files, print resume prompt
/remind --quiet              # show count only
/remind --file TODO.md       # scan a specific file
/remind | claude             # pipe directly into Claude to resume
```

## What it scans

Looks for unchecked markdown checkboxes (`- [ ]`) in:

- `TODO.md`
- `TASKS.md`
- `CLAUDE.md`
- `.claude/CLAUDE.md`

## Example output

```
You are resuming a development session.

## Project: myapp
Branch: `feat/oauth`

## Pending Tasks (3 incomplete)

- [ ] Add email verification endpoint  (TODO.md)
- [ ] Write integration tests for auth  (TODO.md)
- [ ] Update API docs  (TASKS.md)

## Instructions
Acknowledge these pending tasks. Ask which one to work on first...
```

## Typical workflow

```bash
# End of session — save handoff
claude-handoff save --note "OAuth done, email verification next"

# Start of next session — remind + load handoff
claude-remind | claude
# or
claude-handoff load | claude
```

## Tool

Runs `python tools/claude-remind.py` (or `claude-remind` if installed globally).

Install: `make install-tools`
