[← Back to README](../README.md)

**[한국어](HARNESS-GUIDE.ko.md)** · **English**

# AI Harness Design Guide

How to design harnesses that make AI agents predictable, accurate, and safe.

> *Inspired by Musinsa Tech Blog: "AI Specialist + Harness-controlled Pipeline"*

---

## Core Philosophy: Agent = Model + Harness

A language model alone is a generalist — it can do anything, which means it might do the wrong thing. A **harness** is the controlled environment that shapes the model's behavior for a specific task.

> "This project's code is 99% written by Claude. The engineer's job is to design the harness."

The engineer's role in AI-powered workflows:
- Design the harness (system prompts, agent structure, stage definitions)
- Compose the team (concurrency limits, provider choice, max iterations)
- Add safety nets after failures
- Make the final judgment (approve / reject outputs)

---

## Three Harness Types

### 1. Tight Harness — Specialist

**When to use:** Well-defined, repeatable, high-stakes tasks.

```
Characteristics:
✓ Narrow role: "10-year Spring Boot/JPA expert"
✓ Constrained output: unified diff only, JSON schema, etc.
✓ Explicit forbidden actions
✓ Deterministic output validation
```

**Trade-off:** High accuracy on the specific task; useless outside its scope.

**Example agents in this project:** `security-auditor`, `database-expert`, `harness-designer`

---

### 2. Loose Harness — Generalist

**When to use:** Exploratory, open-ended, or conversational tasks.

```
Characteristics:
✓ Broad, flexible role
✓ Free-form output
✓ Human judgment at each step
```

**Trade-off:** Flexible but less predictable; requires active human steering.

**Example:** Claude Code itself in interactive mode.

---

### 3. Adaptive Harness — Orchestrator

**When to use:** Multi-step workflows that combine multiple specialists.

```
Characteristics:
✓ Coordinates specialist agents
✓ Routes based on previous stage outputs
✓ Manages context isolation between agents
✓ Handles failures per stage
```

**Trade-off:** Most powerful for complex automation; most complex to design.

**Example agents in this project:** `orchestrator`, `pipeline-orchestrator`

---

## Context Isolation: Preventing Context Rot

In long pipelines, accumulated context causes "Context Rot" — early errors contaminate later stages.

### The Rule
Each agent receives **only the context it needs** — nothing more.

```
❌ Bad: pass the full conversation history to every agent
✅ Good: pass only the validated output of the previous stage

❌ Bad: one agent reads everything and does everything
✅ Good: 4 parallel agents each read one thing and report one finding
```

### Pattern: Parallel Reconnaissance
```
Stage 2 — parallel, context-isolated:
  Agent A: analyze code structure      ← independent context window
  Agent B: collect DB metadata         ← independent context window
  Agent C: verify configuration        ← independent context window
  Agent D: analyze trade-offs          ← independent context window

Stage 3 — synthesize:
  receive only the 4 reports above (not their full sessions)
```

---

## Building a Tight Harness: Step by Step

### 1. Define the Problem Precisely
```
What is the single, repeatable task?
What does a perfect output look like? (this is your success criterion)
What are the failure modes?
What human oversight is required?
```

### 2. Write the Specialist Persona
```
You are a [N-year] expert in [specific domain].
You ONLY do [specific task]. Nothing else.
```

### 3. Define Input / Output Contracts
```
## Input Contract
[Exact format of what you receive]

## Output Contract
Output ONLY in the following format — nothing else:
[exact format: unified diff / JSON / structured markdown]
```

### 4. List Forbidden Actions
```
## Forbidden
- Never modify files outside [scope]
- Never add features not requested
- Never produce output outside the defined format
```

### 5. Add a Validation Layer
```
Static:  syntax check, schema conformance, format match
Dynamic: dry-run, EXPLAIN, test execution
Verdict: PASS | WARNING | MISMATCH | ERROR

Default: warn (don't block), unless the action is irreversible
```

### 6. Define Human Oversight Checkpoints
```
What does the AI decide autonomously?   → within the harness
What requires human approval?           → before applying
What is NEVER automated?               → final merge, production push
```

---

## Review Loop Pattern

A review loop runs multiple review agents in parallel, deduplicates findings, applies fixes, and iterates.

```
Round N:
  Spawn review agents in parallel:
    Agent 1: correctness review (isolated context)
    Agent 2: security review    (isolated context)
    Agent 3: performance review (isolated context)
    Agent 4: style review       (isolated context)
  
  Merge findings → deduplicate → fix → re-review

Early exit when:
  - All findings resolved
  - No improvement vs. previous round
  - Max iterations reached
```

**Multi-provider variant:** Run the same 4 perspectives with 2 AI providers (e.g., Claude + another model) → up to 8 parallel reviews → automatically merge duplicate findings.

---

## Skill System: Prompts as Files

Keep prompts version-controlled and composable:

```
skills/
  analyst/
    system.md     ← system prompt for the analyst specialist
    user.md       ← user prompt template
  reviewer/
    system.md
    user.md
  shared/
    checklist.md  ← shared partial, included in multiple skills
```

Benefits:
- Version-controlled prompt history
- Reuse shared checklists across agents
- Swap prompts without changing code
- Circular reference detection and depth limits

---

## What NOT to Automate

Intentionally preserve human judgment for:

| Decision | Why |
|----------|-----|
| Which slow queries to analyze | Business context beyond metrics |
| Whether to apply a suggested patch | Technical + business trade-off |
| Final PR merge | Accountability |
| Production deployment | Irreversible, high blast radius |

---

## Using the Tools

```bash
# Validate all agent harness definitions
claude-harness check-all

# Validate a single agent
claude-harness validate agents/09-harness-designer.md

# Generate a tight harness template
claude-harness template tight my-specialist > agents/11-my-specialist.md

# Track pipeline execution
claude-pipeline init my-workflow
claude-pipeline stage "analysis" start
claude-pipeline stage "analysis" pass --note "found 3 issues"
claude-pipeline stage "patch-gen" start
claude-pipeline report
```

---

## Quick Reference

| Harness Type | Best for | Accuracy | Flexibility |
|---|---|---|---|
| Tight (Specialist) | Defined, repeatable tasks | ★★★★★ | ★☆☆☆☆ |
| Loose (Generalist) | Exploration, conversation | ★★★☆☆ | ★★★★★ |
| Adaptive (Orchestrator) | Multi-step automation | ★★★★☆ | ★★★★☆ |

---

*See also:*
- *[`agents/09-harness-designer.md`](../agents/09-harness-designer.md) — agent for designing harnesses*
- *[`agents/10-pipeline-orchestrator.md`](../agents/10-pipeline-orchestrator.md) — agent for running pipelines*
- *[`tools/claude-harness.py`](../tools/claude-harness.py) — CLI harness validator*
- *[`tools/claude-pipeline.py`](../tools/claude-pipeline.py) — CLI pipeline tracker*
