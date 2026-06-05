[← Back to README](../README.md)

**[한국어](AGENT-CHEATSHEET.ko.md)** · **English**

# Claude Code Multi-Agent Cheatsheet

Ready-to-use prompts for every situation. Copy and paste directly.

---

## Quick Start

```
/agents   # list available agents

# Full pipeline (most common)
Use the orchestrator to [describe your task]
```

---

## Prompts by Situation

### New Feature (Full Pipeline)
```
Use the orchestrator to implement [feature name].
Requirements:
- [requirement 1]
- [requirement 2]
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### Bug Fix
```
Use the orchestrator to fix the bug where [describe the bug].
The issue seems to be in [file/module].
After fixing, have reviewer verify and tester add regression tests.
```

### Code Review Only
```
Have the reviewer subagent review src/[file path].
Focus on security and error handling.
```

### Security Audit
```
Have security-auditor do a full OWASP audit of src/api/
Report all findings by severity.
```

### Performance Analysis
```
Have performance-optimizer analyze [file/feature].
The symptom is: [describe the slow part]
```

### Database Work
```
Have database-expert design the schema for [feature].
Requirements:
- [requirement]
Include migration files and index strategy.
```

### Documentation
```
Have documenter update README.md and add JSDoc to src/api/
Make it clear enough for a new developer to onboard in 30 minutes.
```

---

## Parallel Execution (Save Time)

```
Run these in parallel:
1. Have planner design the auth module
2. Have database-expert design the user schema
3. Have security-auditor review current auth requirements
Then have implementer execute the combined plan.
```

---

## Agent Teams Mode

Open 3 terminals side by side:

**Terminal 1 (Team lead)**
```bash
claude --model claude-opus-4-5
> Start an agent team. You are the team lead.
> Task: [big task]
> Spawn: implementer, reviewer, tester as teammates
```

**Terminal 2 (Monitoring)**
```bash
watch -n 1 cat .claude/team-tasks.md
```

**Terminal 3 (Additional instructions)**
```bash
claude --agent reviewer "re-check src/auth after implementer changes"
```

---

## Context Management (Cost Control)

| Situation | Command |
|-----------|---------|
| After finishing a step | `/compact` |
| Starting a completely different task | `/clear` |
| Check spend | `/cost` |
| Live cost monitor | `claude-tools watch` |
| Reference a specific file | `@src/auth/login.ts review this file` |

---

## Per-Agent Models & Cost

```
Opus   -> orchestrator, planner, security-auditor   (complex reasoning)
Sonnet -> implementer, reviewer, tester,             (execution-focused)
          performance-optimizer, database-expert
Haiku  -> documenter                                 (simple/repetitive, lowest cost)
```

---

## Troubleshooting

**Agents not showing**
```
/agents
```
Check that `.md` files exist in `~/.claude/agents/`.

**Agent going out of scope**
```
Have reviewer ONLY review src/auth.ts.
Do NOT suggest changes to other files.
```
