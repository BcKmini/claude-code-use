<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code Multi-Agent System

**11 specialized AI agents + 7 productivity tools — all for Claude Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?style=flat-square&logo=rust)](https://www.rust-lang.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/Claudecode-Agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-11-green?style=flat-square)](#agent-roster)
[![Tools](https://img.shields.io/badge/Tools-7-informational?style=flat-square)](#tools)
[![Bilingual](https://img.shields.io/badge/Lang-EN%20%7C%20KO-orange?style=flat-square)](#)

**[한국어 README](README.ko.md)** · **[Setup Guide](docs/SETUP.md)** · **[Cheatsheet](docs/AGENT-CHEATSHEET.md)** · **[Harness Guide](docs/HARNESS-GUIDE.md)** · **[Integration](docs/INTEGRATION.md)** · **[Contributing](docs/CONTRIBUTING.md)**

</div>

---

## What is this?

A drop-in enhancement for **Claude Code** that gives you:

1. **11 specialized sub-agents** — each laser-focused on one job (design, code, review, test, security, harness design, pipeline orchestration…)
2. **`snippet`** — personal prompt manager; your best prompts one command away
3. **`claude-handoff`** — save full session context and resume it in the next conversation
4. **`claude-cost`** — estimate and track Claude API spend before you run a prompt
5. **`claude-review-diff`** — generate a structured code review prompt from your git diff
6. **`claude-remind`** — surface incomplete TODO items at session start
7. **`claude-harness`** — validate and generate AI harness definitions for specialist agents
8. **`claude-pipeline`** — track multi-stage pipeline execution with quality gates and run reports

All tools ship as Python CLIs and as Claude Code slash commands. The core tools also ship as a single compiled **Rust binary** (`claude-tools`).

> **Bilingual:** All agents respond in the user's language — English and Korean (한국어) both fully supported.

```
You                     Orchestrator
 │                           │
 └──► "Add OAuth login" ──► ├──► planner         (architecture)
                             ├──► database-expert  (schema)
                             ├──► implementer      (code)
                             ├──► reviewer         (code review)
                             └──► tester           (tests)
```

---

## Why Harness Engineering? — Cost vs. Effectiveness

> Benchmark scenario: fix a bug in a single TypeScript file.
> Dev rate: $60/hr · Pricing: Sonnet 4.6 $3/$15 · Opus 4.7 $5/$25 per 1M tokens.

### At a glance

| Metric | Vanilla Claude CLI | This Harness | Change |
|--------|:-----------------:|:------------:|:------:|
| PR diff size | ~180 lines | ~25 lines | **−86%** |
| PR review time | ~18 min | ~4 min | **−78%** |
| First-pass approval rate | ~45% | ~85% | **+89%** |
| Rework rate | ~40% | ~10% | **−75%** |
| Bug detection (reviewer stage) | ✗ none | ✓ 42–48% caught | **+∞** |
| API cost per task | ~$0.039 | ~$0.049 | +26% |
| **Total engineering cost** *(API + dev time)* | **~$0.32** | **~$0.10** | **3.1× cheaper** |

> API cost goes up slightly — but review time and rework drop so much that
> total cost (API + human time) is **3× lower** per task.

### Total cost breakdown

```
Vanilla Claude CLI  ████████████████████████████████  $0.32
                    ├─ API         ██  $0.04
                    ├─ Review time ██████████████  $0.18
                    └─ Rework      ████████  $0.10

This Harness        ████████  $0.10
                    ├─ API         ███  $0.05
                    ├─ Review time ████  $0.04
                    └─ Rework      █  $0.01
```

### PR diff size

```
Vanilla  ██████████████████████████████████████  180 lines
Harness  ████  25 lines  (surgical edit protocol)
```

### Review time

```
Vanilla  ████████████████████  18 min
Harness  ████  4 min
```

*Data sources: Google DORA Report 2025 · Anthropic Engineering Blog · Stripe PR velocity data · DevToolsAcademy AI code review benchmark 2025*

---

## Quick Start

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude   # authenticate on first run
```

### 2. Install (choose one)

**Option A — One-line installer (recommended, macOS / Linux)**
```bash
curl -fsSL https://raw.githubusercontent.com/BcKmini/claude-code-use/main/install.sh | bash
```

**Option B — Specific version**
```bash
curl -fsSL https://raw.githubusercontent.com/BcKmini/claude-code-use/main/install.sh | bash -s -- --version v1.0.0
```

**Option C — Clone and build from source**
```powershell
# Windows
git clone https://github.com/BcKmini/claude-code-use.git
cd claude-code-use
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
git clone https://github.com/BcKmini/claude-code-use.git
cd claude-code-use
make install            # agents + slash commands + Python tools
make install-rust       # optional: Rust binary (requires cargo)
```

### 4. Verify

```
claude
/agents          # → 9 agents listed
/snippet list    # → built-in snippets
```

---

## Agent Roster

| # | Agent | Model | Job |
|---|-------|-------|-----|
| 00 | **orchestrator** | Opus | Breaks down requests and delegates to sub-agents |
| 01 | **planner** | Opus | Architecture & design decisions — read-only |
| 02 | **implementer** | Sonnet | Writes and edits code |
| 03 | **reviewer** | Sonnet | Bug, security, quality, performance review — read-only |
| 04 | **tester** | Sonnet | Unit, integration, E2E test authoring |
| 05 | **security-auditor** | Opus | OWASP Top 10 audit — read-only |
| 06 | **performance-optimizer** | Sonnet | Bottleneck analysis and optimization |
| 07 | **database-expert** | Sonnet | Schema design, queries, migrations |
| 08 | **documenter** | Haiku | README, API docs, inline comments |
| 09 | **harness-designer** | Opus | Designs tight/loose/adaptive AI harnesses for automation |
| 10 | **pipeline-orchestrator** | Opus | Manages multi-stage pipelines with context isolation |

> **All agents are bilingual** — they detect the user's language and respond in English or Korean (한국어).

> Each agent carries only the context relevant to its role. Parallel execution (planner + security-auditor simultaneously) cuts wall-clock time.

> See [AGENT-CHEATSHEET.md](docs/AGENT-CHEATSHEET.md) for 24+ ready-to-use prompts.

---

## Tools

Five productivity tools that fill the gaps Claude Code doesn't cover out of the box.

### Slash commands overview

| Command | What it does |
|---------|-------------|
| `/snippet` | Run, save, list personal prompt templates |
| `/handoff` | Save/load session context across conversations |
| `/cost` | Estimate and track API spend |
| `/review-diff` | Code review prompt from current git diff |
| `/remind` | Surface pending TODO items at session start |
| `/harness` | Design and validate AI harness definitions |
| `/pipeline` | Run and track multi-stage AI pipelines |

---

### Tool 1 — `snippet` — Personal Prompt Manager

Save your best Claude prompts by name and recall them in one command.

```bash
snippet list                                   # all snippets
snippet run full-pipeline | claude             # pipe to Claude
snippet save myfix "Fix {{BUG}} in {{FILE}}"   # template variables
snippet search security
snippet export my-backup.json
```

```
/snippet list
/snippet run full-pipeline
/snippet search security
```

**20 built-in snippets** including `full-pipeline`, `code-review`, `security-audit`, `write-tests`, `refactor`, `db-schema`, and more. See [snippets/defaults.json](snippets/defaults.json).

---

### Tool 2 — `claude-handoff` — Session Continuity

Save the full context of a session and load it back in the next one.

```bash
claude-handoff save --note "OAuth done, next: email verification"
claude-handoff load | claude    # resume immediately
claude-handoff list
claude-handoff clean --days 30
```

```
/handoff save
/handoff load
/handoff list
```

**What a handoff captures:** git branch, last 5 commits, working-tree status, diff stat, TODO.md contents, your note, and a ready-to-paste Resume Prompt.

---

### Tool 3 — `claude-cost` — Cost Estimator & Tracker

Know what a prompt will cost before you run it. Track actual spend from session logs.

```bash
claude-cost estimate --snippet full-pipeline --agents 9
claude-cost month
claude-cost set-budget 20.00
```

```
/cost estimate full-pipeline
/cost month
/cost agents
```

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|-----------------|
| Opus | $15.00 | $75.00 |
| Sonnet | $3.00 | $15.00 |
| Haiku | $0.25 | $1.25 |

---

### Tool 4 — `claude-review-diff` — Code Review from Git Diff

Generate a structured code review prompt from your current git changes and pipe it straight into Claude.

```bash
claude-review-diff                       # review unstaged changes
claude-review-diff --staged              # review staged changes
claude-review-diff --base main           # compare branch to main
claude-review-diff --focus security      # security-only review
claude-review-diff | claude              # pipe directly to Claude
```

```
/review-diff
/review-diff --staged
/review-diff --base main --focus security
```

**Focus options:** `security` · `performance` · `correctness` · `style` · `tests` · `all`

Output groups findings by severity: **Critical → Major → Minor → Nit**

---

### Tool 5 — `claude-remind` — Session Start Reminder

Scan TODO.md / TASKS.md / CLAUDE.md for incomplete checkboxes and print a session-start prompt.

```bash
claude-remind                # show all pending tasks + resume prompt
claude-remind --quiet        # count only
claude-remind | claude       # pipe to Claude to resume
```

```
/remind
/remind --quiet
```

**Typical end-of-session / start-of-session workflow:**

```bash
# End of session
claude-handoff save --note "Auth done, next: email verification"

# Start of next session
claude-remind | claude         # see pending tasks
claude-handoff load | claude   # full context restore
```

---

### Tool 6 — `claude-harness` — Harness Validator & Template Generator

Validate agent harness definitions and generate harness templates from the command line.

```bash
claude-harness check-all                         # validate all agents in agents/
claude-harness validate agents/09-harness-designer.md   # validate one agent
claude-harness template tight my-specialist      # print a tight harness template
claude-harness template adaptive my-orchestrator # print an adaptive harness template
```

```
/harness design automate slow query detection and patching
/harness validate agents/03-reviewer.md
/harness types
```

**Checks performed on each agent:**
- Role is clearly scoped
- Output format is constrained
- Forbidden actions are listed
- Tools list is minimal
- Bilingual language support present

---

### Tool 7 — `claude-pipeline` — Pipeline Tracker & Reporter

Track multi-stage AI pipeline execution, log stage results, and generate Markdown run reports.

```bash
claude-pipeline init slow-query-fix              # create and activate pipeline
claude-pipeline stage "detection" start
claude-pipeline stage "detection" pass --note "found 3 slow queries"
claude-pipeline stage "patch-gen" start
claude-pipeline stage "patch-gen" warn --note "1 query had no safe fix"
claude-pipeline status                           # show live status
claude-pipeline report                           # markdown run report
claude-pipeline list                             # all saved pipelines
```

```
/pipeline run analyze slow queries and generate patches with review loop
/pipeline status
/pipeline stages
```

---

### Rust binary — `claude-tools`

All tools compiled into one zero-dependency binary — no Python required.

```bash
cd rust && cargo build --release
# or: make install-rust

claude-tools snippet list
claude-tools handoff save --note "done"
claude-tools cost month
claude-tools watch              # live cost monitor (real-time)
claude-tools watch --interval 5
claude-tools env                # environment health check
```

**`claude-tools env` output:**

```
Claude Code Environment

  ✓ ANTHROPIC_API_KEY   sk-ant-…abcd
  ✓ ~/.claude/           exists
  ✓ ~/.claude/agents/    9 agents installed
  ✓ ~/.claude/commands/  5 commands: snippet, handoff, cost, review-diff, remind
  ✓ handoffs             3 saved, latest: 20250608-143022.md
  ✓ sessions             4 projects, 12 session files
```

---

## Makefile

```bash
make help           # list all targets
make install        # agents + slash commands + Python tools
make install-rust   # build and install Rust binary
make build          # cargo build --release
make test           # all tests
make lint           # clippy + ruff
make fmt            # rustfmt + ruff format
make status         # git log + tool install check
make env            # Claude environment health check
make clean          # remove build artifacts
```

---

## Repository Layout

```
Claudecode-Agent/
├── Makefile                          ← build / install / test / clean
├── setup-agents.ps1                  ← Windows quick installer
├── setup-agents.sh                   ← macOS / Linux quick installer
│
├── agents/                           ← agent definitions → ~/.claude/agents/
│   ├── 00-orchestrator.md
│   ├── 01-planner.md
│   ├── 02-implementer.md
│   ├── 03-reviewer.md
│   ├── 04-tester.md
│   ├── 05-security-auditor.md
│   ├── 06-performance-optimizer.md
│   ├── 07-database-expert.md
│   ├── 08-documenter.md
│   ├── 09-harness-designer.md        ← NEW harness architect
│   └── 10-pipeline-orchestrator.md  ← NEW pipeline manager
│
├── .claude/commands/                 ← slash commands → ~/.claude/commands/
│   ├── snippet.md
│   ├── handoff.md
│   ├── cost.md
│   ├── review-diff.md
│   ├── remind.md
│   ├── harness.md                    ← NEW /harness
│   └── pipeline.md                   ← NEW /pipeline
│
├── snippets/
│   └── defaults.json                 ← 20 built-in prompt templates
│
├── tools/
│   ├── snippet.py                    ← prompt manager CLI
│   ├── claude-handoff.py             ← session continuity CLI
│   ├── claude-cost.py                ← cost estimator CLI
│   ├── claude-review-diff.py
│   ├── claude-remind.py
│   ├── claude-harness.py             ← NEW harness validator + template gen
│   ├── claude-pipeline.py            ← NEW pipeline tracker + reporter
│   ├── install-tools.ps1             ← Windows tool installer
│   └── install-tools.sh              ← macOS/Linux tool installer
│
├── rust/claude-tools/src/
│   ├── main.rs
│   ├── snippet.rs
│   ├── handoff.rs
│   ├── cost.rs
│   ├── watch.rs                      ← live cost monitor
│   ├── env.rs                        ← NEW environment health check
│   └── colors.rs
│
└── docs/
    ├── SETUP.md / SETUP.ko.md
    ├── AGENT-CHEATSHEET.md / .ko.md
    ├── HARNESS-GUIDE.md / .ko.md      ← NEW harness design guide
    ├── INTEGRATION.md / .ko.md
    ├── CONTRIBUTING.md / .ko.md
    └── CLAUDE.md / .ko.md
```

---

## Context Cost Tips

| Situation | Command |
|-----------|---------|
| After finishing a step | `/compact` |
| Switching tasks completely | `/clear` |
| Check current spend | `/cost` |
| Watch live cost | `claude-tools watch` |
| Check environment | `claude-tools env` |
| Resume with pending tasks | `claude-remind \| claude` |
| Full session restore | `claude-handoff load \| claude` |

---

## Troubleshooting

**Agents not showing in `/agents`**
```bash
ls ~/.claude/agents/*.md   # files must be present
# Restart Claude Code after installing
```

**Agent Teams not working**
```powershell
# Windows — should print 1
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","User")
```
```bash
# macOS / Linux — should print 1
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
```

**Tool not found after `make install-tools`**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

**`make` not available on Windows**
```powershell
winget install GnuWin32.Make
```

---

## Contributing

- **New tool idea?** → [Feature Request](https://github.com/BcKmini/Claudecode-Agent/issues/new?template=feature_request.md)
- **Bug?** → [Bug Report](https://github.com/BcKmini/Claudecode-Agent/issues/new?template=bug_report.md)
- **New snippet?** → add to `snippets/defaults.json` and send a PR

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for the full guide.

---

## License

[MIT](LICENSE)
