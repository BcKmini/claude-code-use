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

## Harness Design & Pipeline (New)

### Design an AI Harness for a Workflow
```
Have harness-designer design a tight harness for the following task.

Task: [describe the automation task]
Domain: [e.g., Spring Boot/JPA, Python/FastAPI]
Expected output format: [e.g., unified diff, JSON report]

Deliver: specialist definitions, pipeline stages, context isolation plan,
human oversight checkpoints, token cost estimate.
```

### Run a Multi-Stage Pipeline
```
Have pipeline-orchestrator plan and execute a pipeline for:
[describe the workflow]

Use context isolation between stages.
Run independent stages in parallel.
Apply quality gates at every stage.
Produce a run report at the end.
```

### Context Isolation — Parallel Reconnaissance
```
Redesign this analysis to use parallel context-isolated agents:

Current: one agent reads everything and produces one report
Target: 4 agents, each answering ONE question in an isolated context

Questions to answer in parallel:
1. [question 1]
2. [question 2]
3. [question 3]
4. [question 4]

Then synthesize all 4 answers in a final stage.
```

### Multi-Perspective Review Loop
```
Set up a review loop for [artifact/file/diff].

Perspectives:
1. Correctness (logic errors, edge cases)
2. Security (OWASP top 10, injection, auth)
3. Performance (N+1 queries, missing index, O(n²))
4. Style (naming, complexity, maintainability)

Max iterations: 3
Early exit if: no new findings or no improvement vs. previous round.
```

### Validate All Agent Harnesses
```bash
claude-harness check-all   # validate all agents in agents/
```

### Pipeline Tracking Workflow
```bash
claude-pipeline init my-workflow
claude-pipeline stage "analysis" start
claude-pipeline stage "analysis" pass --note "found issues"
claude-pipeline stage "patch-gen" start
claude-pipeline report     # markdown run report
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

## Slash Commands — Tools

| Command | What it does | Example |
|---------|-------------|---------|
| `/snippet list` | Browse saved prompts | `/snippet list --tag security` |
| `/snippet run` | Execute a prompt template | `/snippet run full-pipeline` |
| `/handoff save` | Save session context | `/handoff save` |
| `/handoff load` | Restore last session | `/handoff load` |
| `/cost estimate` | Pre-run cost estimate | `/cost estimate full-pipeline` |
| `/cost month` | Monthly spend summary | `/cost month` |
| `/review-diff` | Code review from git diff | `/review-diff --focus security` |
| `/review-diff --staged` | Review staged changes | `/review-diff --staged` |
| `/review-diff --base main` | Compare branch to main | `/review-diff --base main` |
| `/remind` | Show pending TODO items | `/remind` |
| `/remind --quiet` | Count only | `/remind --quiet` |
| `/harness design` | Design an AI harness | `/harness design automate slow query analysis` |
| `/harness validate` | Validate agent harness | `/harness validate agents/03-reviewer.md` |
| `/pipeline run` | Run a multi-stage pipeline | `/pipeline run analyze and patch slow queries` |
| `/pipeline status` | Show pipeline run status | `/pipeline status` |

---

## Context Management (Cost Control)

| Situation | Command |
|-----------|---------|
| After finishing a step | `/compact` |
| Starting a completely different task | `/clear` |
| Check spend | `/cost` |
| Live cost monitor (second terminal) | `claude-tools watch` |
| Environment health check | `claude-tools env` |
| Resume with pending tasks | `claude-remind \| claude` |
| Full session restore | `claude-handoff load \| claude` |
| Reference a specific file | `@src/auth/login.ts review this file` |

---

## Session Workflow

```bash
# End of session
claude-handoff save --note "OAuth done, next: email verification"

# Start of next session (pick one or both)
claude-remind | claude          # see pending TODO items
claude-handoff load | claude    # full git context restore
```

---

## Per-Agent Models & Cost

```
Opus   -> orchestrator, planner, security-auditor,   (complex reasoning)
          harness-designer, pipeline-orchestrator
Sonnet -> implementer, reviewer, tester,             (execution-focused)
          performance-optimizer, database-expert
Haiku  -> documenter                                 (simple/repetitive, lowest cost)
```

---

## Surgical Code Changes (PR 가독성 최적화)

> These prompts enforce minimal diffs so PRs are fast to review.
> Based on Google/Stripe/Anthropic best practices: reviewable diffs ship 60% faster.

### Fix only one function
```
Have implementer fix ONLY the [function_name] function in [file path].
Do NOT modify any other functions, imports, or formatting in that file.
Use Edit tool — do not rewrite the whole file.
Diff target: under 30 lines changed.
```

### Minimal patch — bug fix
```
Bug is in [file:function_name].
Have implementer change ONLY what's necessary to fix this bug.
Constraint: diff must stay under 30 lines.
If broader refactoring would help but isn't strictly needed, list it separately — don't apply it now.
```

### Add a feature without touching existing code
```
Have implementer add [feature] to [file].
Scope boundary: new code only — do not reformat, rename, or reorganize existing code.
Existing functions must be left exactly as they are unless the feature requires changing them.
```

### Split a large change into atomic PRs
```
This change affects [N] files. Have orchestrator split into separate atomic implementer tasks:
Task 1: [change description] — files: [A, B only]
Task 2: [change description] — file: [C only]
Task 3: [change description] — file: [D only]
Each task should produce a diff under 150 lines.
Call implementer once per task, sequentially.
```

### Request a diff review before applying
```
Before implementing, have planner output:
1. Exact files to modify (with function names and line ranges)
2. Explicit "Do Not Touch" list
3. Estimated lines changed per file
I will approve the scope before implementer starts.
```

### Reviewer: check diff quality first
```
Have reviewer check [file or branch diff] for diff quality BEFORE correctness:
- Were only the requested functions/lines changed?
- Any formatting or rename noise?
- Total diff under 200 lines?
Flag DIFF_BLOAT if the scope is wider than the task required.
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

**Implementer rewrote the whole file instead of editing it**
```
Revert the change. Then:
Have implementer re-implement using Edit tool only.
Scope: modify ONLY [function_name] at [file:line_start–line_end].
Do not use Write on an existing file.
```

**Check full environment**
```bash
claude-tools env   # or: make env
```
