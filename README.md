<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code Multi-Agent System

**9 specialized AI agents + 3 productivity tools — all for Claude Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?style=flat-square&logo=rust)](https://www.rust-lang.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/claude-code-multi-agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-9-green?style=flat-square)](#agent-roster)
[![Tools](https://img.shields.io/badge/Tools-3-informational?style=flat-square)](#tools)

**[한국어 README](README.ko.md)** · **[Setup Guide](docs/SETUP.md)** · **[Cheatsheet](docs/AGENT-CHEATSHEET.md)** · **[Integration](docs/INTEGRATION.md)** · **[Contributing](docs/CONTRIBUTING.md)**

</div>

---

## What is this?

A drop-in enhancement for **Claude Code** that gives you:

1. **9 specialized sub-agents** — each laser-focused on one job (design, code, review, test, security…)
2. **`snippet`** — personal prompt manager; your best prompts one command away
3. **`claude-handoff`** — save full session context and resume it in the next conversation
4. **`claude-cost`** — estimate and track Claude API spend before you run a prompt

All three tools ship as Python CLIs, as Claude Code slash commands (`/snippet`, `/handoff`, `/cost`), and as a single compiled **Rust binary** (`claude-tools`).

Instead of one Claude instance doing everything, each task is routed to the agent best suited for it.

```
You                     Orchestrator
 │                           │
 └──► "Add OAuth login" ──► ├──► planner       (architecture)
                             ├──► database-expert (schema)
                             ├──► implementer   (code)
                             ├──► reviewer      (code review)
                             └──► tester        (tests)
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

> **Why separate agents?**  
> Each agent carries only the context relevant to its role. No contamination between "design mode" and "implementation mode." Parallel execution (planner + security-auditor simultaneously) cuts wall-clock time.

---

## Quick Start

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude   # authenticate on first run
```

### 2. Install the agents

```powershell
# Windows
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
bash setup-agents.sh
```

### 3. Verify

```
claude
/agents          # → 9 agents listed
```

---

## Using the Agents

### Full feature pipeline

```
Use the orchestrator to implement OAuth 2.0 login with Google.
Requirements:
- JWT token issuance
- Integrate with existing email login

Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### Quick review

```
Have the reviewer subagent review src/api/auth.ts
Focus on security vulnerabilities and error handling.
```

### Parallel tasks (saves time)

```
Run these in parallel:
1. Have planner design the notification module
2. Have database-expert design the schema
3. Have security-auditor review the requirements
Then have implementer execute the combined plan.
```

> See [AGENT-CHEATSHEET.md](docs/AGENT-CHEATSHEET.md) for 20+ ready-to-use prompts.

---

## Tools

Three productivity tools that fill the gaps Claude Code doesn't cover out of the box.

### Install all tools (one command)

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1
```

```bash
# macOS / Linux
bash tools/install-tools.sh
```

Installs:
- Slash commands `/snippet`, `/handoff`, `/cost` into `~/.claude/commands/`
- 20 built-in snippets from `snippets/defaults.json`
- Shell functions `snippet`, `claude-handoff`, `claude-cost` in your profile

> Or use the compiled Rust binary — see [Rust binary](#rust-binary-claude-tools) below.

---

### Tool 1 — `snippet` — Personal Prompt Manager

Save your best Claude prompts by name and recall them in one command, from the terminal or inside Claude Code.

**Terminal**

```bash
snippet list                          # all snippets
snippet list --tag pipeline           # filter by tag
snippet save myfix "Fix {{BUG}} in {{FILE}}" --tags bug
snippet run myfix --var BUG="null ref" --var FILE="auth.ts"
snippet run full-pipeline | claude    # pipe directly to Claude

snippet search security
snippet show code-review
snippet cp code-review my-review
snippet delete my-review --force
snippet stats
snippet export my-backup.json
snippet import snippets/defaults.json
```

**Inside Claude Code**

```
/snippet list
/snippet run full-pipeline
/snippet search security
/snippet show db-schema
```

**Template variables** — any `{{VARIABLE}}` becomes a fill-in-the-blank:

```bash
snippet run new-feature \
  --var FEATURE="user notifications" \
  --var LANG="TypeScript" \
  --var REQUIREMENTS="real-time push, email digest"
```

**Built-in snippets (20)**

| Name | Tags | Purpose |
|------|------|---------|
| `full-pipeline` | pipeline | Full orchestrator pipeline with template vars |
| `new-feature` | pipeline, feature | Design + implement from scratch |
| `fix-bug` | bug | Fix + regression test |
| `hotfix` | bug, urgent | Emergency production fix |
| `code-review` | review | File-level code review |
| `pr-review` | review, pr | Diff review before merge |
| `security-audit` | security | OWASP Top 10 audit |
| `parallel-design` | parallel | Design, schema, security in parallel |
| `db-schema` | database | Schema + index strategy + migration |
| `db-migrate` | database, migration | Migration with rollback plan |
| `performance` | performance | Bottleneck analysis |
| `write-tests` | test | Comprehensive test suite |
| `write-docs` | docs | README + JSDoc update |
| `refactor` | refactor | Safe refactor with test verification |
| `explain` | explain | Explain unfamiliar code |
| `api-review` | review, api | REST API design review |
| `nextjs-feature` | nextjs, frontend | Next.js 15 App Router feature |
| `fastapi-endpoint` | fastapi, backend | FastAPI endpoint with tests |
| `context-reset` | meta | Compact context + list next steps |
| `cost-check` | meta | Session cost estimate |

---

### Tool 2 — `claude-handoff` — Session Continuity

Save the full context of a Claude Code session (git state, open tasks, a summary note) to a markdown file. Load it back in the next session — no more "what were we doing again?"

**Terminal**

```bash
claude-handoff save                    # prompts for a note, saves context
claude-handoff save --note "finished auth, next: write tests"
claude-handoff load | claude           # load most recent handoff into Claude
claude-handoff list                    # list saved handoffs
claude-handoff show --id 20250101-120000
claude-handoff clean --days 30 --force # delete old handoffs
```

**Inside Claude Code**

```
/handoff save
/handoff load
/handoff list
```

**What a handoff captures:**

- Current git branch, last 5 commits, working-tree status, diff stat
- Remote URL and repo root
- Contents of `TODO.md` / `TASKS.md` if present
- Your summary note
- A ready-to-paste **Resume Prompt** for the next session

**Resume workflow:**

```bash
# End of session
claude-handoff save --note "Completed OAuth flow; next: email verification"

# Start of next session
claude-handoff load | claude
```

---

### Tool 3 — `claude-cost` — Cost Estimator & Tracker

Know what a prompt will cost before you run it. Track actual spend from session logs. Set a monthly budget.

**Terminal**

```bash
# Estimate cost for a snippet across all 9 agents
claude-cost estimate --snippet full-pipeline --agents 9

# Estimate any prompt text
claude-cost estimate "Refactor the entire auth module"

# Cost history for the last 7 days
claude-cost history

# Monthly summary
claude-cost month

# Per-agent breakdown
claude-cost agents

# Set a monthly budget (shows % used in estimates)
claude-cost set-budget 20.00
```

**Inside Claude Code**

```
/cost estimate full-pipeline
/cost history
/cost month
/cost agents
```

**Model pricing used**

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|-----------------|
| Opus | $15.00 | $75.00 |
| Sonnet | $3.00 | $15.00 |
| Haiku | $0.25 | $1.25 |

---

### Rust binary — `claude-tools`

All three tools + a live cost monitor compiled into one zero-dependency binary — no Python required.

```bash
cd rust
cargo build --release

# Use
./target/release/claude-tools snippet list
./target/release/claude-tools handoff save --note "done"
./target/release/claude-tools cost estimate --snippet full-pipeline
./target/release/claude-tools watch              # live cost monitor
./target/release/claude-tools watch --interval 5 # refresh every 5s
```

**Or install globally:**

```bash
cargo install --path rust/claude-tools

claude-tools snippet list
claude-tools handoff load | claude
claude-tools cost month
claude-tools watch   # real-time token + cost stream
```

> See [INTEGRATION.md](docs/INTEGRATION.md) for how `claude-tools` connects with **claw-code**, the Rust-based Claude CLI harness.

---

## Repository Layout

```
Claudecode-Agent/
├── agents/                       ← agent definitions (copied to ~/.claude/agents/)
│   ├── 00-orchestrator.md
│   ├── 01-planner.md
│   ├── 02-implementer.md
│   ├── 03-reviewer.md
│   ├── 04-tester.md
│   ├── 05-security-auditor.md
│   ├── 06-performance-optimizer.md
│   ├── 07-database-expert.md
│   └── 08-documenter.md
├── .claude/
│   └── commands/
│       ├── snippet.md            ← /snippet slash command
│       ├── handoff.md            ← /handoff slash command
│       └── cost.md               ← /cost slash command
├── snippets/
│   └── defaults.json             ← 20 built-in prompt templates
├── tools/
│   ├── snippet.py                ← prompt manager CLI (Python 3.8+, stdlib only)
│   ├── claude-handoff.py         ← session continuity CLI
│   ├── claude-cost.py            ← cost estimator CLI
│   ├── install-tools.ps1         ← Windows one-shot installer (all 3 tools)
│   └── install-tools.sh          ← macOS / Linux one-shot installer
├── rust/
│   ├── Cargo.toml                ← workspace root
│   └── claude-tools/             ← Rust binary (snippet + handoff + cost + watch)
│       ├── Cargo.toml
│       └── src/
│           ├── main.rs
│           ├── snippet.rs
│           ├── handoff.rs
│           ├── cost.rs
│           ├── watch.rs          ← real-time live cost monitor (NEW)
│           └── colors.rs
├── docs/
│   ├── SETUP.md                  ← full environment setup
│   ├── SETUP.ko.md
│   ├── AGENT-CHEATSHEET.md       ← ready-to-use prompt examples
│   ├── AGENT-CHEATSHEET.ko.md
│   ├── INTEGRATION.md            ← claw-code + Rust integration guide
│   ├── INTEGRATION.ko.md
│   ├── CONTRIBUTING.md           ← contribution guide
│   ├── CONTRIBUTING.ko.md
│   ├── CLAUDE.md                 ← personal coding guidelines
│   └── CLAUDE.ko.md
├── setup-agents.ps1              ← Windows agent installer
└── setup-agents.sh               ← macOS / Linux agent installer
```

---

## Full Documentation

| Document | EN | KO |
|----------|----|-----|
| Setup Guide | [SETUP.md](docs/SETUP.md) | [SETUP.ko.md](docs/SETUP.ko.md) |
| Agent Cheatsheet | [AGENT-CHEATSHEET.md](docs/AGENT-CHEATSHEET.md) | [AGENT-CHEATSHEET.ko.md](docs/AGENT-CHEATSHEET.ko.md) |
| Integration (claw-code + Rust) | [INTEGRATION.md](docs/INTEGRATION.md) | [INTEGRATION.ko.md](docs/INTEGRATION.ko.md) |
| Contributing Guide | [CONTRIBUTING.md](docs/CONTRIBUTING.md) | [CONTRIBUTING.ko.md](docs/CONTRIBUTING.ko.md) |
| Coding Guidelines | [CLAUDE.md](docs/CLAUDE.md) | [CLAUDE.ko.md](docs/CLAUDE.ko.md) |
| README | [README.md](README.md) | [README.ko.md](README.ko.md) |

---

## Context Cost Tips

| Situation | Command |
|-----------|---------|
| After finishing a step | `/compact` |
| Switching to a completely different task | `/clear` |
| Reference a specific file | `@src/auth.ts review this` |
| Check spend | `/cost` |
| Watch live cost in a second terminal | `claude-tools watch` |

---

## Troubleshooting

**Agents not showing in `/agents`**
```bash
ls ~/.claude/agents/*.md   # files must be present
# Restart Claude Code
```

**Agent Teams not working**
```powershell
# Windows
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","User")
# Should print: 1
```
```bash
# macOS / Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS   # should print 1
```

**MCP connection error (-32000)**
```bash
docker ps   # verify GitHub MCP container is running
# Then inside Claude Code:
/mcp        # reconnect
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

- **New agent idea?** → open a [Feature Request](https://github.com/BcKmini/Claudecode-Agent/issues/new?template=feature_request.md)
- **Bug?** → open a [Bug Report](https://github.com/BcKmini/Claudecode-Agent/issues/new?template=bug_report.md)
- **New snippet idea?** → add it to `snippets/defaults.json` and send a PR

---

## License

[MIT](LICENSE)

