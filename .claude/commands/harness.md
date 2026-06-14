# /harness — AI Harness Designer

Design an AI harness for automating a specific workflow.

## Usage

```
/harness design <task description>
/harness validate <agent-file.md>
/harness types
```

---

## What is a Harness? (하네스란?)

**Agent = Model + Harness**

A harness is the controlled environment that makes an AI model behave predictably on a specific task.
The tighter the harness, the higher the accuracy for specialist tasks.

Three types:
| Type | Best for | Example |
|------|----------|---------|
| **Tight** | Well-defined, repeatable, high-stakes | Slow query fixer, diff generator |
| **Loose** | Exploratory, open-ended | General Claude Code chat |
| **Adaptive** | Multi-step workflows | Full dev pipeline |

---

## /harness design

```
/harness design {{TASK_DESCRIPTION}}
```

Invokes `harness-designer` agent to produce a full harness specification:
- Specialist agent definitions (persona, input/output contracts)
- Pipeline stage map
- Context isolation strategy
- Human oversight checkpoints
- Estimated token cost

**Example:**
```
/harness design automate slow query detection and patch generation for a Spring Boot / JPA service
```

---

## /harness validate

```
/harness validate {{AGENT_FILE}}
```

Reviews an existing agent `.md` file and checks:
- [ ] Role is clearly scoped (not too broad)
- [ ] Output format is constrained
- [ ] Forbidden actions are listed
- [ ] Tools are minimal (only what's needed)
- [ ] Human oversight point is defined

---

## /harness types

Prints a quick reference of all three harness types with examples and trade-offs.

---

*Powered by `harness-designer` (agent 09) — see `agents/09-harness-designer.md`*
*Inspired by: Musinsa Tech Blog — AI Specialist + Harness-controlled Pipeline*
