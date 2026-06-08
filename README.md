<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code Multi-Agent System

**9 specialized AI agents + 5 productivity tools — all for Claude Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?style=flat-square&logo=rust)](https://www.rust-lang.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/Claudecode-Agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-9-green?style=flat-square)](#agent-roster)
[![Tools](https://img.shields.io/badge/Tools-5-informational?style=flat-square)](#tools)

**[한국어 README](README.ko.md)** · **[Setup Guide](docs/SETUP.md)** · **[Cheatsheet](docs/AGENT-CHEATSHEET.md)** · **[Integration](docs/INTEGRATION.md)** · **[Contributing](docs/CONTRIBUTING.md)**

</div>

---

## What is this?

A drop-in enhancement for **Claude Code** that gives you:

1. **9 specialized sub-agents** — each laser-focused on one job (design, code, review, test, security…)
2. **`snippet`** — personal prompt manager; your best prompts one command away
3. **`claude-handoff`** — save full session context and resume it in the next conversation
4. **`claude-cost`** — estimate and track Claude API spend before you run a prompt
5. **`claude-review-diff`** — generate a structured code review prompt from your git diff
6. **`claude-remind`** — surface incomplete TODO items at session start

All tools ship as Python CLIs, as Claude Code slash commands, and as a single compiled **Rust binary** (`claude-tools`).

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

## Quick Start

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude   # authenticate on first run
```

### 2. Clone and install

```powershell
# Windows
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
bash setup-agents.sh
```

### 3. Install tools (one command)

```bash
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

> Each agent carries only the context relevant to its role. Parallel execution (planner + security-auditor simultaneously) cuts wall-clock time.

> See [AGENT-CHEATSHEET.md](docs/AGENT-CHEATSHEET.md) for 20+ ready-to-use prompts.

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
│   └── 08-documenter.md
│
├── .claude/commands/                 ← slash commands → ~/.claude/commands/
│   ├── snippet.md
│   ├── handoff.md
│   ├── cost.md
│   ├── review-diff.md                ← NEW /review-diff
│   └── remind.md                     ← NEW /remind
│
├── snippets/
│   └── defaults.json                 ← 20 built-in prompt templates
│
├── tools/
│   ├── snippet.py                    ← prompt manager CLI
│   ├── claude-handoff.py             ← session continuity CLI
│   ├── claude-cost.py                ← cost estimator CLI
│   ├── claude-review-diff.py         ← NEW code review from diff CLI
│   ├── claude-remind.py              ← NEW session reminder CLI
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
